#!/usr/bin/env python3
"""Categorize an existing beam-pipe/tracker Geant4 material recording.

Run in the node's verified ROOT/DD4hep environment. No particles are simulated.
"""
import argparse
import ctypes
import hashlib
import json
import math
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


def audit_labels(path, recording, compact, factories, output):
    """Bind the bounded Geant4 CSG audit to the exact classification inputs."""
    audit = json.loads(path.read_text())
    if (audit['recording_sha256'] != sha(recording) or audit['compact_sha256'] != sha(compact) or
            audit['materials_sha256'] != sha(compact.with_name('materials.xml')) or
            sorted(f['sha256'] for f in audit['factories']) != sorted(sha(p) for p in factories)):
        raise ValueError('Geant4 audit input identities do not match this classification')
    if sha(path.with_name('lookups.json')) != audit['lookups_sha256']:
        raise ValueError('Geant4 audit lookup bytes changed')
    steps = audit['certified_steps']
    if len(steps) != audit['rows'] or not steps:
        raise ValueError('Incomplete Geant4 audit')
    target = output/'geant4-audited-labels.txt'
    lines = []
    for row in steps:
        if (row['category'] != 4 or 'ShortStripEndcap' not in row['path'] or
                any(c.isspace() for c in row['volume']) or row['track'] < 0 or row['step'] < 0):
            raise ValueError('Invalid bounded passive-endcap audit label')
        lines.append(f"{row['track']} {row['step']} {row['volume']}\n")
    target.write_text(''.join(lines))
    return str(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--compact", type=Path, required=True)
    parser.add_argument("--factory", type=Path, action="append", required=True,
                        help="Built detector library; repeat for each factory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--write-steps", action="store_true",
                        help="Also export per-step category/region labels for mapping studies")
    parser.add_argument("--limit", type=int, default=-1,
                        help="Diagnostic track limit; -1 means all tracks")
    parser.add_argument("--eta-max", type=float, default=4.5,
                        help="Symmetric profile support, aligned to 0.1 eta bins")
    parser.add_argument("--geant4-audit", type=Path,
                        help="Optional hash-bound native Geant4 audit for passive graphite CSG discrepancies")
    args = parser.parse_args()
    if args.limit == 0 or args.limit < -1:
        parser.error("--limit must be positive or -1")
    if (not math.isfinite(args.eta_max) or args.eta_max <= 0 or
            abs(10 * args.eta_max - round(10 * args.eta_max)) > 1e-9):
        parser.error("--eta-max must be positive and aligned to 0.1 bins")
    for path in [args.input, args.compact, *args.factory]:
        if not path.is_file():
            parser.error(f"Missing input: {path}")
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    audit = audit_labels(args.geant4_audit, args.input, args.compact, args.factory, output) if args.geant4_audit else ''
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
                    str(output / "classification-diagnostics.csv"), args.limit,
                    args.write_steps, args.eta_max, audit)
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
    if args.geant4_audit:
        files.append(("geant4_audit", args.geant4_audit))
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
