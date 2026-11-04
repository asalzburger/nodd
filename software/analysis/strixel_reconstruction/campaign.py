#!/usr/bin/env python3
"""Explicit sequential launch/check/resume for the 80-case DES042 prototype."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import runtime


def scheduling_policy():
    """Use retained baseline timings only to order independent subprocesses."""
    estimates = {}
    for simulation, particle, unused_seed in runtime.POPULATIONS:
        for pt in runtime.PTS:
            directory = ("tracker-reconstruction/validation/selected" if
                (simulation, particle) == ("fatras", "muon") else
                f"tracker-reconstruction-species/{simulation}/{particle}")
            relative = f"docs/validation/{directory}/pt{pt:g}/summary.json.gz"
            path = runtime.ROOT / relative
            pinned = subprocess.check_output(["git", "show", runtime.INPUT_REVISION + ":" + relative], cwd=runtime.ROOT)
            digest = runtime.sha256(path)
            if digest != hashlib.sha256(pinned).hexdigest():
                raise ValueError("Frozen scheduling evidence changed: " + relative)
            with gzip.open(path, "rt") as stream:
                reference = json.load(stream)
            seconds = reference["sequencer_seconds"] / reference["events"]
            if not math.isfinite(seconds) or seconds <= 0:
                raise ValueError("Invalid frozen scheduling timing: " + relative)
            estimates[f"{simulation}-{particle}-pt{pt:g}"] = {
                "seconds_per_event": seconds, "reference": relative, "sha256": digest}
    return {"name": "Descending frozen per-event sequencer time; case ID ascending breaks ties",
            "input_revision": runtime.INPUT_REVISION, "estimates": estimates,
            "scope": "Scheduling only; no physics, event identity or native thread change; historical times are not an ETA"}


def ordered(cases, policy):
    def key(case):
        identity = f"{case['simulation']}-{case['particle']}-pt{case['pt_GeV']:g}"
        return (-policy["estimates"][identity]["seconds_per_event"], case["case_id"])
    return sorted(cases, key=key)


def plan(events, supplier, native_runtime, write_root, jobs=1):
    policy = scheduling_policy()
    cases = runtime.cases(events)
    return {"schema_version": 1, "status": "PROTOTYPE", "input_revision": runtime.INPUT_REVISION,
        "profile": runtime.PROFILE, "threads": 1, "max_parallel_processes": jobs, "events_per_case": events,
        "supplier_root": str(supplier), "runtime_root": str(native_runtime), "write_root": write_root,
        "cases": cases, "scheduling_policy": policy,
        "launch_order": [case["case_id"] for case in ordered(cases, policy)],
        "launcher_sha256": {str(Path(__file__).resolve()): runtime.sha256(__file__),
                            str(Path(runtime.__file__).resolve()): runtime.sha256(runtime.__file__)}}


def status(directory, case):
    path = directory / case["case_id"] / "run-report.json"
    if not path.exists():
        return "absent" if not path.parent.exists() else "incomplete"
    try:
        report = json.loads(path.read_text())
        if report.get("outcome") != "completed":
            return report.get("outcome", "incomplete")
        for name in ("case_id", "events", "seed", "pt_GeV", "pitch_mm", "simulation", "particle"):
            if report.get(name) != case[name]:
                return "configuration-mismatch"
        for name, digest in report["output_sha256"].items():
            target = path.parent / name
            if not target.is_file() or runtime.sha256(target) != digest:
                return "output-mismatch"
        return "completed"
    except (OSError, ValueError, KeyError, TypeError):
        return "invalid-report"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("launch", "resume", "check", "list"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events", type=int, default=1000)
    parser.add_argument("--case", action="append", help="Exact case ID; repeat to select multiple smoke/pilot cases")
    parser.add_argument("--supplier-root", type=Path, default=runtime.ROOT.parent / "nodd-gen3-material-mapping")
    parser.add_argument("--runtime-root", type=Path, default=runtime.ROOT.parent / "nodd-software-layout")
    parser.add_argument("--write-root", action="store_true")
    parser.add_argument("--jobs", type=int, default=1, help="Independent one-thread native processes (default 1)")
    args = parser.parse_args()
    directory = args.output.resolve()
    if args.jobs <= 0:
        parser.error("--jobs must be a positive integer")
    expected = plan(args.events, args.supplier_root.resolve(), args.runtime_root.resolve(), args.write_root, args.jobs)
    selected = [c for c in expected["cases"] if not args.case or c["case_id"] in args.case]
    if args.case and set(args.case) != {c["case_id"] for c in selected}:
        parser.error("Unknown case ID")
    if args.action == "list":
        print(json.dumps(selected, indent=2)); return
    manifest = directory / "campaign-plan.json"
    if args.action == "launch":
        if directory.exists() and any(directory.iterdir()):
            parser.error("launch requires a fresh empty campaign output directory")
        directory.mkdir(parents=True, exist_ok=True)
        with manifest.open("x") as stream:
            stream.write(json.dumps(expected, indent=2, sort_keys=True) + "\n")
    else:
        if not manifest.exists() or json.loads(manifest.read_text()) != expected:
            parser.error("Stored campaign plan differs; use its exact events, suppliers, ROOT option and source bytes")
    if args.action == "check":
        states = {c["case_id"]: status(directory, c) for c in selected}
        print(json.dumps(states, indent=2))
        parser.exit(0 if all(s == "completed" for s in states.values()) else 1)
    # One case per subprocess, one ACTS thread. Refuse prior failed/interrupted
    # directories; recovery requires a fresh campaign directory, preserving evidence.
    pending = []
    for case in ordered(selected, expected["scheduling_policy"]):
        state = status(directory, case)
        if state == "completed" and args.action == "resume":
            print(case["case_id"] + ": verified completed, skipped", flush=True); continue
        if state != "absent":
            parser.error(case["case_id"] + ": " + state + "; preserve it and use a fresh campaign directory")
        pending.append(case)

    def launch(case):
        command = [sys.executable, "-B", str(Path(runtime.__file__).resolve()), "--case", case["case_id"],
            "--events", str(args.events), "--output", str(directory / case["case_id"]),
            "--supplier-root", expected["supplier_root"], "--runtime-root", expected["runtime_root"]]
        if args.write_root:
            command.append("--write-root")
        log = directory / (case["case_id"] + ".log")
        started = time.monotonic()
        print("Launching " + case["case_id"], flush=True)
        with log.open("x") as stream:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=False)
        if result.returncode or status(directory, case) != "completed":
            raise RuntimeError(f"{case['case_id']} failed; retained {log}")
        print(f"Completed {case['case_id']} in {time.monotonic()-started:.1f}s", flush=True)

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(launch, case) for case in pending]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as error:
                # Running native cases finish normally; never interrupt a
                # persistent Geant4 event loop. Unstarted cases stay absent.
                for queued in futures:
                    queued.cancel()
                parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
