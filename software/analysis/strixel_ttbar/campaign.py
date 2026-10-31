#!/usr/bin/env python3
"""Repeatable, bounded DES042 ttbar+200 pileup campaign; no implicit retries."""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
PITCHES = (0.5, 1., 1.5, 2.)
SOURCES = ("software/analysis/strixel_ttbar/runtime.py",
           "software/analysis/strixel_ttbar/campaign.py",
           "software/source/ActsExamples/StrixelPileup/CMakeLists.txt",
           "software/source/ActsExamples/StrixelPileup/PythiaBinding.cpp",
           "software/source/ActsExamples/StrixelPileup/PileupAudit.cpp",
           "software/source/ActsExamples/StrixelPileupSafeFatras/CMakeLists.txt",
           "software/source/ActsExamples/StrixelPileupSafeFatras/Binding.cpp",
           "software/source/ActsExamples/StrixelPileupSafeFatras/TtbarSafeBetheHeitler.hpp",
           "software/source/ActsExamples/StrixelPileupSafeFatras/FailureAudit.hpp",
           "software/source/ActsExamples/StrixelPileupSafeFatras/test_energy_loss.cpp",
           "software/source/ActsExamples/StrixelPileupSafeFatras/test_failure_identity.cpp")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def source_identity(root=ROOT):
    names = list(SOURCES)
    directory = root / "software/source/ActsExamples/StrixelPileupSafeGbts"
    if directory.is_dir():
        names += [str(path.relative_to(root)) for path in sorted(directory.iterdir()) if path.is_file()]
    return {name: sha256(root / name) for name in names}


def plan(args):
    if args.events <= 0 or args.seed < 0 or args.jobs not in range(1, 5):
        raise ValueError("Require positive events, nonnegative seed and jobs1..4")
    result = {"schema_version": 1, "study_status": "PROTOTYPE", "events": args.events,
            "seed": args.seed, "pileup": 200, "pitches_mm": list(PITCHES),
            "jobs": args.jobs,
            "source_revision": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": source_identity(),
            "supplier_root": str(args.supplier_root.resolve()),
            "runtime_root": str(args.runtime_root.resolve()),
            "native_dir": str(args.native_dir.resolve()),
            "fatras_native_dir": str(args.fatras_native_dir.resolve()),
            "python": str(Path(sys.executable).resolve())}
    gbts = getattr(args, "gbts_native_dir", None)
    if gbts is not None:
        result["gbts_native_dir"] = str(gbts.resolve())
    shared = getattr(args, "sample", None)
    if shared is not None:
        directory = shared.resolve()
        original = json.loads((directory / "run-report.json").read_text())
        if original.get("kind") != "generate":
            raise ValueError("External sample must be a completed generation")
        revision = original.get("source_revision")
        if not isinstance(revision, str) or len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
            raise ValueError("External sample lacks its original source revision")
        report_check(directory, {**result, "source_revision": revision})
        result["shared_sample"] = {"directory": str(directory),
            "source_revision": revision,
            "report_sha256": sha256(directory / "run-report.json")}
    return result


def report_check(directory, expected, pitch=None):
    path = directory / "run-report.json"
    if not path.is_file():
        raise ValueError("Missing completed report: " + str(path))
    report = json.loads(path.read_text())
    for key in ("events", "seed", "source_revision"):
        if report.get(key) != expected[key]:
            raise ValueError("Report identity differs: " + str(path) + ":" + key)
    if report.get("outcome") != "completed":
        raise ValueError("Failed/incomplete case is preserved; choose a fresh campaign")
    if pitch is not None and report.get("pitch_mm") != pitch:
        raise ValueError("Wrong case pitch")
    outputs = report.get("output_sha256", {})
    if not outputs:
        raise ValueError("Missing output provenance")
    for name, digest in outputs.items():
        item = (directory / name).resolve()
        if not item.is_relative_to(directory.resolve()) or sha256(item) != digest:
            raise ValueError("Output hash differs: " + name)
    return report


def checked_sample(directory, expected):
    shared = expected.get("shared_sample")
    sample = Path(shared["directory"]) if shared else directory / "sample"
    original_expected = {**expected, "source_revision": shared["source_revision"]} if shared else expected
    report = report_check(sample, original_expected)
    if shared and (report.get("kind") != "generate" or
                   sha256(sample / "run-report.json") != shared["report_sha256"]):
        raise ValueError("External sample report changed")
    return sample, report


def verify(directory, expected):
    sample_directory, sample = checked_sample(directory, expected)
    sample_hash = sha256(sample_directory / "run-report.json")
    for pitch in PITCHES:
        case = report_check(directory / f"pitch{pitch:g}", expected, pitch)
        if case.get("sample_report_sha256") != sample_hash:
            raise ValueError("Reconstruction is bound to another sample")
    return {"status": "PASS", "events_per_pitch": expected["events"],
            "pitches_mm": list(PITCHES), "source_revision": expected["source_revision"],
            "sample_report_sha256": sample_hash,
            "sample_output_files": len(sample["output_sha256"])}


def launch_process(command, log):
    # Each ACTS case has its own subprocess and log; no shell interpolation.
    if shutil.disk_usage(log.parent).free < 5 * 1024**3:
        raise RuntimeError("Less than5GiB free; preserve outputs and restore capacity")
    with log.open("x") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                cwd=ROOT, check=False)
    if result.returncode:
        raise RuntimeError(f"Native command exited{result.returncode}; see {log}")


def execute(args):
    directory = args.output.resolve()
    expected = plan(args)
    path = directory / "campaign-plan.json"
    if args.action == "launch":
        if directory.exists() and any(directory.iterdir()):
            raise ValueError("Launch requires a fresh empty campaign directory")
        directory.mkdir(parents=True, exist_ok=True)
        write_json(path, expected)
    else:
        if not path.is_file() or json.loads(path.read_text()) != expected:
            raise ValueError("Campaign arguments, revision or source changed")
    if args.action == "check":
        result = verify(directory, expected)
        print(json.dumps(result), flush=True)
        return
    runtime = ROOT / "software/analysis/strixel_ttbar/runtime.py"
    common = ["--supplier-root", expected["supplier_root"],
              "--runtime-root", expected["runtime_root"],
              "--native-dir", expected["native_dir"],
              "--fatras-native-dir", expected["fatras_native_dir"]]
    if "shared_sample" in expected:
        sample, _ = checked_sample(directory, expected)
    else:
        sample = directory / "sample"
    if sample.exists() and any(sample.iterdir()):
        checked_sample(directory, expected)
    else:
        command = [sys.executable, "-B", str(runtime), "generate", "--events",
                   str(args.events), "--seed", str(args.seed), "--output", str(sample), *common]
        launch_process(command, directory / "sample.log")
        report_check(sample, expected)
        print(json.dumps({"sample": "completed", "events": args.events}), flush=True)
    pending = []
    for pitch in PITCHES:
        case = directory / f"pitch{pitch:g}"
        if case.exists() and any(case.iterdir()):
            report_check(case, expected, pitch)
        else:
            pending.append((pitch, case))
    # Submit at most jobs tasks, and submit new work only after success. Running
    # jobs finish after an error; partial evidence is never erased or retried.
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {}
        queue = iter(pending)
        def submit(item):
            pitch, case = item
            command = [sys.executable, "-B", str(runtime), "reconstruct", "--sample",
                       str(sample), "--pitch", f"{pitch:g}", "--output", str(case), *common]
            if "gbts_native_dir" in expected:
                command += ["--gbts-native-dir", expected["gbts_native_dir"]]
            futures[pool.submit(launch_process, command, directory / f"pitch{pitch:g}.log")] = (pitch, case)
        for _ in range(min(args.jobs, len(pending))):
            submit(next(queue))
        errors = []
        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            successes = 0
            for future in sorted(done, key=lambda f: futures[f][0]):
                pitch, case = futures.pop(future)
                try:
                    future.result()
                    report_check(case, expected, pitch)
                    print(json.dumps({"pitch_mm": pitch, "outcome": "completed"}), flush=True)
                    successes += 1
                except BaseException as error:
                    errors.append(f"pitch{pitch:g}: {type(error).__name__}: {error}")
            if errors:
                for other in futures:
                    other.cancel()
            else:
                for _ in range(successes):
                    item = next(queue, None)
                    if item is not None:
                        submit(item)
        if errors:
            raise RuntimeError("; ".join(errors))
    if source_identity() != expected["source_sha256"]:
        raise RuntimeError("Campaign source changed during execution")
    result = verify(directory, expected)
    write_json(directory / "campaign-check.json", result)
    print(json.dumps(result), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("launch", "resume", "check"))
    parser.add_argument("--events", type=int, default=100)
    parser.add_argument("--seed", type=int, default=153042)
    parser.add_argument("--jobs", type=int, default=1, choices=range(1, 5))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--supplier-root", type=Path, default=ROOT.parent / "nodd-gen3-material-mapping")
    parser.add_argument("--runtime-root", type=Path, default=ROOT.parent / "nodd-software-layout")
    parser.add_argument("--native-dir", type=Path, default=ROOT / "build/strixel-ttbar-native")
    parser.add_argument("--fatras-native-dir", type=Path, default=ROOT / "build/strixel-ttbar-safe-fatras")
    parser.add_argument("--gbts-native-dir", type=Path, default=ROOT / "build/strixel-ttbar-safe-gbts")
    parser.add_argument("--sample", type=Path,
                        help="Reuse a completed immutable external Fatras sample with its original generation revision")
    args = parser.parse_args()
    try:
        execute(args)
    except (ValueError, RuntimeError, OSError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
