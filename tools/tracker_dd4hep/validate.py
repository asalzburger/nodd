#!/usr/bin/env python3
"""Audit actual combined geometry against independent component inventories."""

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "pixel_audit", ROOT_DIR / "tools/pixel_barrel_dd4hep/validate.py"
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def capacity(shape):
    if str(shape.ClassName()) == "TGeoCompositeShape":
        node = shape.GetBoolNode()
        if str(node.ClassName()) == "TGeoIntersection":
            return audit_original_capacity(shape)
        # Pixel tongue has a partial circular cut; retain its restricted audit.
        if (
            str(node.GetLeftShape().ClassName()) == "TGeoBBox"
            and str(node.GetRightShape().ClassName()) in ("TGeoTube", "TGeoTubeSeg")
            and node.GetRightShape().GetRmax() > 5
        ):
            try:
                return audit_original_capacity(shape)
            except ValueError:
                pass
        if str(node.ClassName()) != "TGeoSubtraction":
            raise ValueError("Unsupported assembled CSG")
        return capacity(node.GetLeftShape()) - capacity(node.GetRightShape())
    return float(shape.Capacity())


audit_original_capacity = audit.shape_capacity


def main():
    parser = argparse.ArgumentParser()
    for name in ("compact", "expected", "library_dir", "output"):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    args = parser.parse_args()
    import ROOT as R
    import dd4hep

    R.gROOT.SetBatch(True)
    R.EnableImplicitMT(1)
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    libs = [
        args.library_dir / f"lib{name}{suffix}"
        for name in (
            "nODDBeamPipe",
            "nODDPixelBarrel",
            "nODDShortStripBarrel",
            "nODDShortStripEndcap",
            "nODDLongStrip",
        )
    ]
    for lib in libs:
        if R.gSystem.Load(str(lib.resolve())) < 0:
            raise RuntimeError("Factory load failed: " + str(lib))
    expected = json.loads(args.expected.read_text())
    d = dd4hep.Detector.getInstance()
    d.fromXML(str(args.compact.resolve()))
    audit.shape_capacity = capacity
    inventory = audit.physical_inventory(d, dd4hep, R, expected["entities"])
    sensors = audit.compare_sensors(
        inventory["sensors"],
        [e for e in expected["entities"] if e["role"] == "sensitive"],
    )
    errors = list(sensors["errors"])
    packed = set()
    identifiers = []
    for system, readout in (
        (1, "PixelBarrelHits"),
        (2, "PixelEndcapHits"),
        (3, "PixelEndcapHits"),
        (4, "ShortStripBarrelHits"),
        (5, "ShortStripEndcapHits"),
        (6, "LongStripBarrelHits"),
        (7, "LongStripEndcapHits"),
    ):
        ro = d.readout(readout)
        checked = 0
        for s in inventory["sensors"]:
            if s["ids"]["system"] != system:
                continue
            fields = R.std.vector("pair<string,int>")()
            for key, value in s["ids"].items():
                fields.emplace_back(key, value)
            vid = int(ro.idSpec().encode(fields))
            if vid in packed:
                errors.append("Duplicate global volumeID")
            packed.add(vid)
            for key, value in s["ids"].items():
                if int(ro.idSpec().decoder().get(vid, key)) != value:
                    errors.append("Identifier decode mismatch")
            checked += 1
        identifiers.append(
            dict(system=system, readout=readout, sensitive_count=checked)
        )
    expected_materials = defaultdict(lambda: dict(volume_mm3=0.0, mass_g=0.0))
    for e in expected["entities"]:
        if "material" in e and "volume_mm3" in e:
            expected_materials[e["material"]]["volume_mm3"] += e["volume_mm3"]
            expected_materials[e["material"]]["mass_g"] += e["mass_g"]
    material_errors = []
    for name, values in expected_materials.items():
        actual = inventory["materials"].get(name, {})
        for key, value in values.items():
            if not math.isclose(actual.get(key, -1), value, rel_tol=1e-6, abs_tol=1e-6):
                material_errors.append(f"{name}: exclusive {key} mismatch")
    errors.extend(material_errors)
    import xml.etree.ElementTree as ET

    compact = ET.parse(args.compact).getroot()
    pipe_outer = expected["beam"]["outer_radius_mm"]
    apertures = [
        float(part.get("rmin").removesuffix("*mm"))
        for detector in compact.findall("./detectors/detector")
        if detector.get("name").startswith("PixelEndcap")
        for part in detector.iter("part")
        if part.get("shape") == "sector"
        and part.get("rmin")
        and float(part.get("rmin").removesuffix("*mm")) < 40
        and float(part.get("rmax").removesuffix("*mm")) > pipe_outer
    ]
    clearance = min(apertures) - pipe_outer
    if clearance < -1e-9:
        errors.append("Analytic pixel passive aperture intersects pipe")
    d.manager().CheckOverlaps(1e-5 * dd4hep.mm)
    overlaps = [
        dict(
            description=str(x.GetTitle()),
            penetration_mm=float(x.GetOverlap()) / dd4hep.mm,
        )
        for x in d.manager().GetListOfOverlaps()
    ]
    if overlaps:
        errors.append(f"{len(overlaps)} overlaps in full assembly")
    paths = {s["path"]: s for s in inventory["sensors"]}
    rays = []
    for eta in (-4, -3, -2, -1, 0, 1, 2, 3, 4):
        for phi in (0, 0.37, 1.11):
            ray = audit.trace_ray(
                d.manager(),
                dd4hep,
                [0, 0, 0],
                audit.ray_direction(eta, phi),
                paths,
                4100,
            )
            ray.update(eta=eta, phi=phi)
            rays.append(ray)
            if not math.isclose(
                ray["material_path_mm"].get("Beryllium", 0),
                expected["beam"]["config"]["wall_mm"] * math.cosh(eta),
                abs_tol=1e-7,
            ):
                errors.append("Pipe material path changed in assembly")
    report = dict(
        status="PASS" if not errors else "FAIL",
        errors=errors,
        sensitive_comparison=sensors,
        identifiers=identifiers,
        unique_volume_ids=len(packed),
        material_comparison=dict(
            passed=not material_errors,
            errors=material_errors,
            materials_checked=len(expected_materials),
        ),
        minimum_pixel_passive_clearance_mm=clearance,
        counts=inventory["counts"],
        physical_placements=inventory["physical_placements"],
        materials=inventory["materials"],
        overlaps=overlaps,
        navigation=rays,
        execution=dict(
            revision=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT_DIR, text=True
            ).strip(),
            dirty=True,
            root_version=R.gROOT.GetVersion(),
            hashes={
                str(p.name): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [args.compact, args.expected, Path(__file__), *libs]
            },
        ),
        limitations=[
            "No engineering sign-off; sparse straight rays are not acceptance or field navigation; Assembly uses explicitly reconciled service ownership; fixed packing limits remain unqualified."
        ],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    dd4hep.Detector.destroyInstance()
    if R.gGeoManager:
        R.gGeoManager.Delete()
    print(
        json.dumps(
            dict(
                status=report["status"],
                errors=errors[:8],
                overlaps=len(overlaps),
                sensors=len(packed),
            )
        )
    )
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
