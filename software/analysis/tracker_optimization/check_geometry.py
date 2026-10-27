#!/usr/bin/env python3
"""Native ROOT/DD4hep overlap audit of a prepared study compact."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--compact",type=Path,required=True)
    p.add_argument("--library-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--tolerance-mm",type=float,default=1.e-5)
    args=p.parse_args()
    if args.output.exists():raise ValueError("Choose a new audit output")
    import ROOT
    import dd4hep
    ROOT.gROOT.SetBatch(True);ROOT.EnableImplicitMT(1)
    suffix=".dylib" if sys.platform=="darwin" else ".so"
    hashes={}
    for name in ("nODDBeamPipe","nODDPixelBarrel","nODDShortStripBarrel","nODDShortStripEndcap","nODDLongStrip"):
        path=(args.library_dir/("lib"+name+suffix)).resolve()
        if ROOT.gSystem.Load(str(path))<0:raise RuntimeError("Factory load failed")
        hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    detector=dd4hep.Detector.getInstance();start=time.monotonic()
    detector.fromXML(str(args.compact.resolve()))
    manager=detector.manager()
    manager.CheckOverlaps(args.tolerance_mm*dd4hep.mm)
    overlaps=[{"description":str(x.GetTitle()),"penetration_mm":float(x.GetOverlap())/dd4hep.mm}
              for x in manager.GetListOfOverlaps()]
    report={"schema_version":1,"status":"PASS" if not overlaps else "FAIL", "scope":"Full compact native ROOT overlap/extrusion check; not installation or service-capacity qualification",
        "source_revision":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "compact_sha256":hashlib.sha256(args.compact.read_bytes()).hexdigest(),
        "factory_sha256":hashes,"ROOT":ROOT.gROOT.GetVersion(),"tolerance_mm":args.tolerance_mm,
        "overlaps":overlaps,"wall_seconds":time.monotonic()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"overlaps":len(overlaps),"wall_seconds":report["wall_seconds"]}),flush=True)
    ROOT.DisableImplicitMT()
    # Explicit cleanup avoids ROOT/DD4hep singleton teardown after overlap workers.
    dd4hep.Detector.destroyInstance()
    if overlaps:raise SystemExit(1)


if __name__=="__main__":main()
