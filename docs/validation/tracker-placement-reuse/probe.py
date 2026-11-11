"""Characterize unchanged tracker DDG4 startup in a fresh, task-local process."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


def mapping_interval(lines):
    begin = end = count = None
    for elapsed, line in lines:
        if "Populating Geant4 volume manager" in line:
            if begin is not None:
                raise ValueError("Repeated mapping start")
            begin = elapsed
        match = re.search(r"populated with (\d+) sensitive path entries", line)
        if match:
            if end is not None or begin is None:
                raise ValueError("Unpaired mapping completion")
            end, count = elapsed, int(match[1])
    if begin is None or end is None or end < begin:
        raise ValueError("Missing or invalid DDG4 mapping interval")
    return dict(sensitive_paths=count, mapping_seconds=end-begin)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("compact", type=Path)
    parser.add_argument("library_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--native-timing", type=Path, required=True)
    parser.add_argument("--ddg4-library", type=Path, required=True)
    parser.add_argument("--expected-sensors", type=int, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    here = Path(__file__).resolve().parent
    repo = here.parents[2]
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    libraries = [args.library_dir.resolve() / ("lib" + name + suffix) for name in (
        "nODDBeamPipe", "nODDPixelBarrel", "nODDShortStripBarrel",
        "nODDShortStripEndcap", "nODDLongStrip")]
    macro = output / "probe.mac"
    macro.write_text("/gun/particle geantino\n/gun/energy 10 GeV\n/gun/position 0 0 0 mm\n"
                     "/gun/direction 1 0 0\n/run/beamOn 1\n"
                     "/control/echo TRACKER_PROBE_DONE\n")
    env = os.environ.copy()
    # Explicitly prohibit the existing profiler's optional couple-cache experiment.
    env.pop("MATERIAL_REUSE_STATIC_COUPLES", None)
    for key in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        env[key] = str(args.library_dir.resolve()) + os.pathsep + env.get(key, "")
    env.update(TRACKER_PROBE_OUTPUT=str(output), TRACKER_PROBE_REPO=str(repo),
               DYLD_INSERT_LIBRARIES=os.pathsep.join(str(p.resolve()) for p in
                   (args.ddg4_library, args.native_timing)),
               MATERIAL_NATIVE_TIMING=str(output / "native-phases.jsonl"))
    ddsim = shutil.which("ddsim")
    if not ddsim:
        raise RuntimeError("ddsim is unavailable in the activated runtime")
    command = [sys.executable, "-u", ddsim, "--compactFile", str(args.compact.resolve()),
               "--steeringFile", str(here / "steering.py"), "--runType", "run",
               "--enableG4Gun", "--macroFile", str(macro), "--numberOfThreads", "1",
               "--random.seed", "130001", "--physics.list", "FTFP_BERT",
               "--physics.rangecut", "0.7", "--part.userParticleHandler", "",
               "--outputConfig.forceEDM4HEP", "--outputFile", str(output / "unused.root")]
    provenance = dict(command=command, source_commit=subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True).strip(),
        sha256={str(p.relative_to(repo)) if p.is_relative_to(repo) else str(p): sha(p)
                for p in [args.compact.resolve(), args.compact.resolve().parent / "materials.xml",
                          *libraries, args.ddg4_library.resolve(), args.native_timing.resolve(), Path(__file__).resolve(),
                          here / "steering.py", repo / "tools/material_recording_profile/inventory.hpp"]})
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    lines = []
    started = time.monotonic()
    with (output / "probe.log").open("w", buffering=1) as log:
        with subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, errors="replace") as child:
            for line in child.stdout:
                elapsed = time.monotonic() - started
                log.write(f"[{elapsed:10.3f}] {line}")
                lines.append((elapsed, line))
            code = child.wait()
    if code or not any(line.strip() == "TRACKER_PROBE_DONE" for _, line in lines):
        raise RuntimeError(f"Probe failed (exit {code}); inspect {output / 'probe.log'}")
    result = mapping_interval(lines)
    if result["sensitive_paths"] != args.expected_sensors:
        raise RuntimeError("DDG4 sensitive path count disagrees with supplied baseline inventory")
    phases = [json.loads(line) for line in (output / "native-phases.jsonl").read_text().splitlines()]
    required = {"g4_initialize", "g4_close_geometry_voxelization", "g4_update_couple_table",
                "g4_event_transport_and_recording"}
    if not required.issubset({phase["name"] for phase in phases}):
        raise RuntimeError("Native phase instrumentation is incomplete")
    inventory = json.loads((output / "inventory.json").read_text())
    if inventory["geant4"]["expanded_nodes_including_world"] <= args.expected_sensors:
        raise RuntimeError("Native inventory is incomplete")
    result.update(wall_including_inventory_seconds=time.monotonic()-started,
                  expected_sensitive_paths=args.expected_sensors, exit_code=code)
    (output / "timing.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
