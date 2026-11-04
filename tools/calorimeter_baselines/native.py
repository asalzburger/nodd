#!/usr/bin/env python3
"""Audit actual construction and complete overlaps for a composed baseline stage."""

import argparse
import json
from pathlib import Path
import subprocess

from export import ROOT, sha


def audit(directory, libraries, output):
    launch = dict(
        source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        source_dirty=bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)),
        native_auditor_sha256=sha(__file__), libraries={Path(p).name: sha(p) for p in libraries})
    import ROOT as R
    import dd4hep

    directory = Path(directory).resolve()
    record = json.loads((directory / "baseline.json").read_text())
    for name, key in (("detector.xml", "compact_sha256"), ("materials.xml", "materials_sha256")):
        if sha(directory / name) != record[key]:
            raise ValueError("Changed baseline artifact: " + name)
    if sha(Path(__file__).with_name("export.py")) != record["exporter_sha256"]:
        raise ValueError("Changed composition source; re-export baseline")
    R.gROOT.SetBatch(True)
    R.gRandom.SetSeed(114)  # Reproducible integration check, not a physics seed.
    for library in libraries:
        if R.gSystem.Load(str(Path(library).resolve())) < 0:
            raise RuntimeError("Cannot load geometry factory: " + str(library))
    detector = dd4hep.Detector.getInstance()
    try:
        detector.fromXML(str(directory / "detector.xml"))
        manager = detector.manager()
        top = manager.GetTopVolume()
        roots = [str(top.GetNode(i).GetVolume().GetName()) for i in range(top.GetNdaughters())]
        wanted = [m for c in record["components"] for m in c["system_mapping"]]
        # The unchanged beam-pipe factory places bore and wall directly in world;
        # its DetElement is attached to the wall rather than an Assembly.
        expected_roots = {m["name"] for m in wanted if m["name"] != "BeamPipe"}
        if any(m["name"] == "BeamPipe" for m in wanted):
            expected_roots.update(("BeamPipe_bore", "BeamPipe_wall"))
        if len(roots) != len(expected_roots) or set(roots) != expected_roots:
            raise ValueError("Unexpected constructed detector roots: " + str(roots))
        observed = {m["name"]: int(detector.detector(m["name"]).id()) for m in wanted}
        if observed != {m["name"]: m["integrated_system_id"] for m in wanted}:
            raise ValueError("Native root ID mapping differs from baseline manifest")
        manager.CheckOverlaps(1e-5 * float(dd4hep.mm))
        overlaps = [dict(description=str(x.GetTitle()), penetration_mm=float(x.GetOverlap()) / float(dd4hep.mm))
                    for x in manager.GetListOfOverlaps()]
        result = dict(status="FAIL" if overlaps else "PASS", layout=record["layout"],
                      **launch,
                      ROOT=R.gROOT.GetVersion(), baseline_manifest_sha256=sha(directory / "baseline.json"),
                      compact_sha256=record["compact_sha256"], materials_sha256=record["materials_sha256"],
                      native_systems=observed, overlap_tolerance_mm=1e-5, overlap_seed=114,
                      overlap_count=len(overlaps), overlaps=overlaps,
                      scope="Actual maintained tracker plus selected complete ECAL barrel/endcaps and local services; no HCAL/FCAL/solenoid/field or response qualification")
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n")
        print(result["status"], record["layout"], len(observed), "native systems;", len(overlaps), "overlaps")
        return bool(overlaps)
    finally:
        dd4hep.Detector.destroyInstance()
        # Match the maintained tracker validator: dispose the geometry while
        # ROOT's thread infrastructure is still alive, before interpreter exit.
        if R.gGeoManager:
            R.gGeoManager.Delete()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--library", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(audit(args.directory, args.library, args.output))
