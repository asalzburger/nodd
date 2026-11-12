"""Native overlap, sensitive placement and wide cell-address audit of the control."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

from angular_sample import ROOT, save, sha


def audit(args):
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    R.gRandom.SetSeed(135)
    if R.gSystem.Load(str(args.library.resolve())) < 0:
        raise RuntimeError("Geometry factory load failed")
    detector = dd4hep.Detector.getInstance()
    errors, seen, logical = [], set(), set()
    counts = Counter()
    cells = 0
    try:
        detector.fromXML(str((args.sample / "detector.xml").resolve()))
        manager = detector.manager()
        sensitive_descendants = {}

        def has_sensitive(volume):
            key = int(R.addressof(volume))
            if key not in sensitive_descendants:
                sensitive_descendants[key] = bool(dd4hep.Volume(volume).isSensitive()) or any(
                    has_sensitive(volume.GetNode(i).GetVolume()) for i in range(volume.GetNdaughters()))
            return sensitive_descendants[key]

        def visit(node, parent_ids):
            nonlocal cells
            volume = node.GetVolume()
            if not has_sensitive(volume):
                return
            ids = dict(parent_ids)
            for field in dd4hep.PlacedVolume(node).volIDs():
                ids[str(field.first)] = int(field.second)
            if dd4hep.Volume(volume).isSensitive():
                system = ids["system"]
                name = "BARRELHits" if system == 8 else "EDGEHits"
                counts[name] += 1
                if "Silicon" not in str(volume.GetMaterial().GetName()):
                    errors.append("Sensitive material is not silicon")
                readout = detector.readout(name)
                fields = R.std.vector("pair<string,int>")()
                for key, value in ids.items():
                    fields.emplace_back(key, value)
                vid = int(readout.idSpec().encode(fields))
                if vid in seen:
                    errors.append("Duplicate sensitive volume ID")
                seen.add(vid)
                decoder = readout.idSpec().decoder()
                for key, value in ids.items():
                    if int(decoder.get(vid, key)) != value:
                        errors.append("Volume ID roundtrip failed")
                logical_key = (system, str(volume.GetName()))
                if logical_key not in logical:
                    logical.add(logical_key)
                    segmentation = readout.segmentation()
                    # Deliberately exceeds all face extents: max actual barrel
                    # axial index is ~710. This verifies addressing capacity,
                    # not physical occupancy of these synthetic cell centres.
                    checked_ids = set()
                    for ix in (-1000, -711, -128, -1, 0, 127, 711, 1000):
                        for iy in (-1000, -711, -128, -1, 0, 127, 711, 1000):
                            point = dd4hep.Position((ix + .5) * 5.5 * dd4hep.mm,
                                                   (iy + .5) * 5.5 * dd4hep.mm, 0)
                            cid = int(segmentation.cellID(point, point, vid))
                            if cid in checked_ids:
                                errors.append("Aliased cell addresses")
                            checked_ids.add(cid)
                            if (int(decoder.get(cid, "x")), int(decoder.get(cid, "y"))) != (ix, iy):
                                errors.append("Wide cell ID roundtrip failed")
                            for key, value in ids.items():
                                if int(decoder.get(cid, key)) != value:
                                    errors.append("Cell ID corrupted parent fields")
                            back = segmentation.position(cid)
                            if abs(back.x() - point.x()) > 1e-8 * dd4hep.mm or abs(back.y() - point.y()) > 1e-8 * dd4hep.mm:
                                errors.append("Cell centre roundtrip failed")
                            cells += 1
            for i in range(volume.GetNdaughters()):
                visit(volume.GetNode(i), ids)

        visit(manager.GetTopNode(), {})
        if counts != Counter(BARRELHits=16 * 48, EDGEHits=32 * 48):
            errors.append("Expected one continuous sensitive sheet per layer/sector")
        print(f"Audited {sum(counts.values())} sensitive sheets; checking native overlaps", flush=True)
        manager.CheckOverlaps(1e-5 * float(dd4hep.mm))
        overlaps = [dict(description=str(item.GetTitle()),
                         penetration_mm=float(item.GetOverlap()) / float(dd4hep.mm))
                    for item in manager.GetListOfOverlaps()]
        if overlaps:
            errors.append(f"Native overlaps: {len(overlaps)}")
        result = dict(status="FAIL" if errors else "PASS", errors=errors,
                      source_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                      validator_sha256=sha(__file__), library_sha256=sha(args.library),
                      compact_sha256=sha(args.sample / "detector.xml"),
                      materials_sha256=sha(args.sample / "materials.xml"), ROOT=R.gROOT.GetVersion(),
                      physical_sensitive_sheets=dict(counts), unique_volume_ids=len(seen),
                      logical_sensitive_shapes=len(logical), synthetic_wide_cell_checks=cells,
                      overlap_tolerance_mm=1e-5, overlap_seed=135,
                      overlap_count=len(overlaps), overlaps=overlaps,
                      scope="Full native control geometry overlaps, physical sensitive sheets and virtual addressing; synthetic cells do not imply occupancy")
        if args.output.exists():
            raise ValueError("Refusing evidence overwrite")
        save(args.output, result)
        print(result["status"], len(overlaps), "native overlaps", flush=True)
        return bool(errors)
    finally:
        dd4hep.Detector.destroyInstance()
        if R.gGeoManager:
            R.gGeoManager.Delete()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(audit(parser.parse_args()))
