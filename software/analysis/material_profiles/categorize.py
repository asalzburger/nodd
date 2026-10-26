#!/usr/bin/env python3
"""Categorize an existing beam-pipe/tracker Geant4 material recording.

Run in the node's verified ROOT/DD4hep environment. No particles are simulated.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--compact", type=Path, required=True)
    parser.add_argument("--factory", type=Path, action="append", required=True,
                        help="Built detector library; repeat for each factory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=-1,
                        help="Diagnostic track limit; -1 means all tracks")
    args = parser.parse_args()
    if args.limit == 0 or args.limit < -1:
        parser.error("--limit must be positive or -1")
    for path in [args.input, args.compact, *args.factory]:
        if not path.is_file():
            parser.error(f"Missing input: {path}")
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    # Use the platform's library name and DD4hep's existing runtime search path.
    import sys
    ctypes.CDLL("libDDG4.dylib" if sys.platform == "darwin" else "libDDG4.so",
                mode=ctypes.RTLD_GLOBAL)
    import ROOT
    import dd4hep

    ROOT.gROOT.SetBatch(True)
    dd4hep.setPrintLevel(dd4hep.WARNING)
    for library in args.factory:
        library = library.resolve()
        os.environ["DD4HEP_LIBRARY_PATH"] = str(library.parent) + os.pathsep + os.environ.get("DD4HEP_LIBRARY_PATH", "")
        if ROOT.gSystem.Load(str(library)) < 0:
            raise RuntimeError(f"Failed to load {library.name}")
    detector = dd4hep.Detector.getInstance()
    start = time.monotonic()
    detector.fromCompact(str(args.compact.resolve()))
    if abs(float(dd4hep.mm) - .1) > 1e-15:
        raise RuntimeError("The classifier requires DD4hep's centimetre TGeo convention")
    code = Path(__file__).with_name("categorize.C")
    ROOT.gInterpreter.AddIncludePath(str(code.parent))
    # Importing dd4hep configures ROOT's include paths in the supported runtime.
    include = Path(dd4hep.__file__).resolve().parents[3] / "include"
    if (include / "DD4hep/Volumes.h").is_file():
        ROOT.gInterpreter.AddIncludePath(str(include))
    if not ROOT.gInterpreter.Declare(code.read_text()):
        raise RuntimeError("Could not compile categorize.C")
    ROOT.categorize(str(args.input.resolve()), str(output / "profiles.root"),
                    str(output / "classification-diagnostics.csv"), args.limit)
    report = json.loads((output / "profiles.root.json").read_text())
    if report["unassigned_steps"] or report["density_mismatches"]:
        raise RuntimeError("Classification incomplete; inspect diagnostics before plotting")
    repo = Path(__file__).resolve().parents[3]
    revision = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    files = [("recording", args.input), ("compact", args.compact),
             ("classifier", code), ("launcher", Path(__file__)),
             ("rounding_cell", code.with_name("rounding_cell.h")),
             *[("factory", p) for p in args.factory]]
    # Record sibling material XML if supplied by the standard tracker exporter.
    materials = args.compact.with_name("materials.xml")
    if materials.is_file():
        files.append(("materials", materials))
    provenance = {
        "analysis_source_revision": revision, "ROOT": ROOT.gROOT.GetVersion(),
        "DD4hep_mm": float(dd4hep.mm), "wall_seconds": time.monotonic() - start,
        "files": [{"role": role, "name": p.name, "sha256": sha(p)} for role, p in files],
        "geometry_provenance": "Explicit caller-supplied compact and factories; the recording contains no embedded geometry revision. Density agreement is checked at every step.",
        "position_convention": "Geant4 mat_x/y/z are pre-step positions. Lookup at position + 0.5 * length * direction; mat_s/e are synthetic symmetric positions.",
        "seed": None,
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")


if __name__ == "__main__":
    main()
