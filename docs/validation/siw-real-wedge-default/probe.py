"""Time the ECAL geometry from the maintained LAYOUT-001 compact and audit its IDs."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def run(baseline, library, output):
    output = output.resolve()
    output.mkdir(parents=True)
    compact = ET.parse(baseline / "detector.xml")
    detectors = compact.find("detectors")
    readouts = compact.find("readouts")
    for detector in list(detectors):
        if detector.get("id") not in ("8", "9"):
            detectors.remove(detector)
    active_readouts = {detector.get("readout") for detector in detectors}
    for readout in list(readouts):
        if readout.get("name") not in active_readouts:
            readouts.remove(readout)
    if {detector.get("id") for detector in detectors} != {"8", "9"}:
        raise ValueError("The source compact must include both Si-W components")
    if any(detector.find("wedge_envelope") is None for detector in detectors):
        raise ValueError("The maintained compact is missing a real Si-W wedge")
    compact.write(output / "detector.xml", encoding="utf-8", xml_declaration=True)
    shutil.copyfile(baseline / "materials.xml", output / "materials.xml")
    macro = output / "probe.mac"
    macro.write_text("/control/echo WEDGE_STARTUP_DONE\n")

    here = Path(__file__).resolve().parent
    env = os.environ.copy()
    for key in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        env[key] = str(library.resolve().parent) + os.pathsep + env.get(key, "")
    env.update(WEDGE_AUDIT_DIRECTORY=str(output), WEDGE_AUDIT_HEADER=str(here / "touchable_audit.hpp"))
    command = [
        sys.executable, "-u", shutil.which("ddsim"), "--compactFile", str(output / "detector.xml"),
        "--steeringFile", str(here / "steering.py"), "--runType", "run", "--enableG4Gun",
        "--macroFile", str(macro), "--numberOfEvents", "0", "--numberOfThreads", "1",
        "--random.seed", "22019999", "--physics.list", "FTFP_BERT", "--physics.rangecut", "0.7",
        "--part.userParticleHandler", "", "--outputConfig.forceEDM4HEP",
        "--outputFile", str(output / "unused.root"),
    ]
    started = time.monotonic()
    begin = end = count = None
    finished = False
    with (output / "probe.log").open("w", buffering=1) as log:
        with subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, errors="replace") as child:
            for line in child.stdout:
                elapsed = time.monotonic() - started
                log.write(f"[{elapsed:10.3f}] {line}")
                if "Populating Geant4 volume manager" in line:
                    begin = elapsed
                if match := re.search(r"populated with (\d+) sensitive path entries", line):
                    end, count = elapsed, int(match[1])
                if line.strip() == "WEDGE_STARTUP_DONE":
                    finished = True
            exit_code = child.wait()
    if exit_code or not finished or begin is None or end is None or count != 531936:
        raise RuntimeError(f"Unexpected probe completion, see {output / 'probe.log'}")
    ids, placements, imprints, center, axis = (output / "mapping-audit.tsv").read_text().split()
    if int(ids) != count:
        raise RuntimeError("Touchable audit count differs from DDG4 map count")
    result = dict(sensitive_paths=count, mapping_seconds=end-begin,
                  wall_including_native_audit_seconds=time.monotonic()-started,
                  geant4_physical_volume_objects=int(placements), assembly_imprints=int(imprints),
                  maximum_dd4hep_ddg4_center_delta_mm=float(center),
                  maximum_dd4hep_ddg4_axis_delta=float(axis))
    (output / "timing.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("library", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    run(args.baseline, args.library, args.output)
