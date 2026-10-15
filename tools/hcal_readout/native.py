"""Independent DD4hep/ROOT audit of the DES036 isolated physical module.

Reads persisted native shapes, materials, placements and cell encodings. ROOT
navigation checks the actual cooling bores, not just the declared service graph.
No electrical, optical, radiation or thermal qualification is implied.
"""
import argparse
from array import array
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def capacity(shape, unit):
    kind = str(shape.ClassName())
    if kind == "TGeoBBox":
        return 8 * shape.GetDX() * shape.GetDY() * shape.GetDZ() / unit**3
    if kind in ("TGeoTube", "TGeoTubeSeg"):
        fraction = 1 if kind == "TGeoTube" else (shape.GetPhi2() - shape.GetPhi1()) / 360
        return 2 * math.pi * (shape.GetRmax()**2 - shape.GetRmin()**2) * shape.GetDz() * fraction / unit**3
    if kind == "TGeoCompositeShape":
        boolean = shape.GetBoolNode()
        if str(boolean.ClassName()) != "TGeoSubtraction":
            raise ValueError("unsupported native Boolean operation")
        return capacity(boolean.GetLeftShape(), unit) - capacity(boolean.GetRightShape(), unit)
    raise ValueError("unsupported native shape " + kind)


def dimension_errors(shape, part, unit):
    """Check primitive dimensions and every actual Boolean cutter transform."""
    errors = []

    def primitive(native, kind, dims):
        if kind == "box" and str(native.ClassName()) == "TGeoBBox":
            values = dict(sx=2 * native.GetDX() / unit, sy=2 * native.GetDY() / unit, sz=2 * native.GetDZ() / unit)
        elif kind == "tube" and str(native.ClassName()) in ("TGeoTube", "TGeoTubeSeg"):
            values = dict(rmin=native.GetRmin() / unit, rmax=native.GetRmax() / unit, length=2 * native.GetDz() / unit)
            if str(native.ClassName()) == "TGeoTubeSeg" and abs(native.GetPhi2() - native.GetPhi1() - 360) > 1e-10:
                errors.append("incomplete cylinder")
        else:
            errors.append("primitive type")
            return
        if any(abs(values[k] - v) > 1e-7 for k, v in dims.items()):
            errors.append("primitive dimension")

    for cut in reversed(part["cuts"]):
        if str(shape.ClassName()) != "TGeoCompositeShape":
            errors.append("missing cutter")
            return errors
        boolean = shape.GetBoolNode()
        primitive(boolean.GetRightShape(), cut["kind"], cut["dimensions_mm"])
        matrix = boolean.GetRightMatrix()
        for axis in range(3):
            if abs(matrix.GetTranslation()[axis] / unit - cut["center_mm"][axis]) > 1e-7:
                errors.append("cutter translation")
            for local in range(3):
                if abs(matrix.GetRotationMatrix()[axis * 3 + local] - cut["frame"][local][axis]) > 1e-10:
                    errors.append("cutter rotation")
        shape = boolean.GetLeftShape()
    primitive(shape, part["shape_kind"], part["dimensions_mm"])
    return errors


def elemental_fractions(name, recipes, atoms):
    if name in atoms:
        return {int(atoms[name]["Z"]): 1.0}
    recipe = recipes[name]
    weights = {
        k: value * atoms[k]["A"] if recipe["basis"] == "atom_count" else value
        for k, value in recipe["composition"].items()
    }
    norm = sum(weights.values())
    result = defaultdict(float)
    for child, value in weights.items():
        for z, fraction in elemental_fractions(child, recipes, atoms).items():
            result[z] += value / norm * fraction
    return result


def check(args):
    import ROOT as R
    import dd4hep

    R.gROOT.SetBatch(True)
    R.EnableImplicitMT(1)
    R.gRandom.SetSeed(36)
    if R.gSystem.Load(str(args.library.resolve())) < 0:
        raise RuntimeError("failed to load isolated module factory")
    expected = json.loads(args.expected.read_text())
    parts = {p["name"]: p for p in expected["parts"]}
    if len(parts) != len(expected["parts"]):
        raise ValueError("nonunique expected part names")
    atoms = {a["name"]: a for a in json.loads((ROOT / "detector/config/elements.json").read_text())["elements"]}
    tracker = load_file("hcal_readout_ray_audit", ROOT / "tools/pixel_barrel_dd4hep/validate.py")
    errors, sensors, native_parts, seen_ids = [], {}, {}, set()
    totals = defaultdict(lambda: {"volume_mm3": 0.0, "mass_g": 0.0})
    counts, cells, checked_materials = Counter(), 0, {}
    unit = float(dd4hep.mm)
    detector = dd4hep.Detector.getInstance()
    try:
        detector.fromXML(str(args.compact.resolve()))
        manager = detector.manager()
        readout = detector.readout("HCALReadoutHits")
        decoder = readout.idSpec().decoder()

        def visit(node, parent, inherited, path):
            nonlocal cells
            matrix = R.TGeoHMatrix(parent)
            matrix.Multiply(node.GetMatrix())
            ids = dict(inherited)
            for pair in dd4hep.PlacedVolume(node).volIDs():
                ids[str(pair.first)] = int(pair.second)
            path += "/" + str(node.GetName())
            volume = node.GetVolume()
            name = str(volume.GetName())
            if name in parts:
                if name in native_parts:
                    errors.append("duplicate native part " + name)
                part = parts[name]
                material = volume.GetMaterial()
                material_name = str(material.GetName())
                measured_volume = capacity(volume.GetShape(), unit)
                errors.extend(problem + " " + name for problem in dimension_errors(volume.GetShape(), part, unit))
                mass = measured_volume * float(material.GetDensity()) / 1000
                if material_name != part["material"]:
                    errors.append("material " + name)
                if not math.isclose(measured_volume, part["volume_mm3"], rel_tol=1e-8, abs_tol=1e-7):
                    errors.append("capacity " + name)
                if not math.isclose(mass, part["mass_g"], rel_tol=1e-8, abs_tol=1e-7):
                    errors.append("mass " + name)
                origin, world = array("d", [0, 0, 0]), array("d", [0, 0, 0])
                matrix.LocalToMaster(origin, world)
                centre = [v / unit for v in world]
                rotation = matrix.GetRotationMatrix()
                for axis in range(3):
                    if abs(centre[axis] - part["center_mm"][axis]) > 1e-7:
                        errors.append("centre " + name)
                    for local in range(3):
                        if abs(rotation[3 * axis + local] - part["frame"][local][axis]) > 1e-10:
                            errors.append("rotation " + name)
                if material_name not in checked_materials:
                    wanted = elemental_fractions(material_name, expected["materials"], atoms)
                    actual = ({int(material.GetElement(i).Z()): float(material.GetWmixt()[i])
                               for i in range(material.GetNelements())} if material.IsMixture()
                              else {int(material.GetZ()): 1.0})
                    if max(abs(actual.get(z, 0) - wanted.get(z, 0)) for z in set(actual) | set(wanted)) > 1e-8:
                        errors.append("composition " + material_name)
                    checked_materials[material_name] = actual
                totals[material_name]["volume_mm3"] += measured_volume
                totals[material_name]["mass_g"] += mass
                counts[part["role"]] += 1
                native_parts[name] = {"centre_mm": centre, "volume_mm3": measured_volume, "mass_g": mass}
                is_sensitive = bool(dd4hep.Volume(volume).isSensitive())
                if is_sensitive != (part["role"] == "sensitive"):
                    errors.append("sensitivity " + name)
                if is_sensitive:
                    fields = R.std.vector("pair<string,int>")()
                    for key, value in ids.items():
                        fields.emplace_back(key, value)
                    vid = int(readout.idSpec().encode(fields))
                    if vid in seen_ids:
                        errors.append("duplicate sensitive ID")
                    seen_ids.add(vid)
                    for key, value in ids.items():
                        if int(decoder.get(vid, key)) != value:
                            errors.append("ID round trip " + key)
                    for key in ("module", "sensor"):
                        if ids.get(key) != part[key]:
                            errors.append("tile identity " + name)
                    for x, y in ((0, 0), (-14.8, -14.8), (-14.8, 14.8), (14.8, -14.8), (14.8, 14.8)):
                        point = dd4hep.Position(x * unit, y * unit, 0)
                        cid = int(readout.segmentation().cellID(point, point, vid))
                        back = readout.segmentation().position(cid)
                        if any(int(decoder.get(cid, key)) != 0 for key in ("x", "y")):
                            errors.append("one-cell tile encoding " + name)
                        if abs(back.x() / unit) > 1e-8 or abs(back.y() / unit) > 1e-8:
                            errors.append("tile position round trip " + name)
                        cells += 1
                    sensors[path] = {"ids": ids, "centre_mm": centre}
            for index in range(volume.GetNdaughters()):
                visit(volume.GetNode(index), matrix, ids, path)

        visit(manager.GetTopNode(), R.TGeoHMatrix(), {}, "")
        if set(native_parts) != set(parts):
            errors.append("native part inventory mismatch")
        if counts != Counter(p["role"] for p in parts.values()):
            errors.append("native role counts")
        for material, values in expected["material_totals"].items():
            for key in ("volume_mm3", "mass_g"):
                if not math.isclose(totals[material][key], values[key], rel_tol=1e-8, abs_tol=1e-6):
                    errors.append("constituent total " + material + " " + key)
        manager.CheckOverlaps(1e-5 * unit)
        overlaps = [{"description": str(o.GetTitle()), "penetration_mm": float(o.GetOverlap()) / unit}
                    for o in manager.GetListOfOverlaps()]
        if overlaps:
            errors.append("native overlaps " + str(len(overlaps)))
        active_parts = sorted((p for p in parts.values() if p["role"] == "sensitive"), key=lambda p: (p["module"], p["sensor"]))
        rays = []
        samples = [("first_tile", *active_parts[0]["center_mm"][:2], 1),
                   ("last_tile", *active_parts[-1]["center_mm"][:2], 1),
                   ("board_seam", 0, -87, 0), ("service_bay", 0, 100, 0)]
        for label, x, y, count in samples:
            ray = tracker.trace_ray(manager, dd4hep, [x, y, -35], [0, 0, 1], sensors, max_length_mm=55)
            ray["sample"] = label
            if ray["sensitive_crossings"] != count:
                errors.append("material/sensitive ray " + label)
            rays.append(ray)
        bore_rays = []
        for x in (-93, 93):
            ray = tracker.trace_ray(manager, dd4hep, [x, -121, 8.5], [0, 1, 0], sensors, max_length_mm=242)
            ray["sample"] = "coolant_bore_" + str(x)
            if not math.isclose(ray["material_path_mm"].get("Water", 0), 240, abs_tol=1e-6):
                errors.append("blocked/discontinuous water bore " + str(x))
            for material, distance in ray["material_path_mm"].items():
                if material != "Water" and distance > 1e-6:
                    errors.append("solid material in coolant bore " + material)
            bore_rays.append(ray)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        root_file = args.output.with_suffix(".root")
        manager.Export(str(root_file.resolve()))
        report = {
            "status": "FAIL" if errors else "PASS", "errors": errors,
            "scope": "Isolated common-module native geometry, constituent mass, placement, identifiers and actual bore navigation. No optical/electrical/thermal/hadronic qualification.",
            "execution": {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                          "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)),
                          "python": platform.python_version(), "ROOT": R.gROOT.GetVersion(),
                          "compact_sha256": sha(args.compact), "expected_sha256": sha(args.expected),
                          "factory_sha256": sha(ROOT / "prototypes/hcal_readout/Readout.cpp"),
                          "library_sha256": sha(args.library), "validator_sha256": sha(__file__),
                          "ray_helper_sha256": sha(ROOT / "tools/pixel_barrel_dd4hep/validate.py")},
            "physical_parts": len(native_parts), "counts": dict(counts),
            "sensitive_ids": len(seen_ids), "cell_probes": cells,
            "material_totals": dict(totals), "mass_g": sum(t["mass_g"] for t in totals.values()),
            "material_elemental_mass_fractions": checked_materials,
            "overlap_tolerance_mm": 1e-5, "overlaps": overlaps,
            "ROOT_overlap_seed": 36,
            "material_rays": rays, "coolant_bore_rays": bore_rays, "root_sha256": sha(root_file),
        }
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(report["status"], len(native_parts), "parts;", len(seen_ids), "sensitive IDs;", cells, "cell probes;", len(overlaps), "overlaps")
        for error in errors:
            print(error)
        return 1 if errors else 0
    finally:
        R.DisableImplicitMT()
        dd4hep.Detector.destroyInstance()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for key in ("compact", "expected", "library", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
    raise SystemExit(check(parser.parse_args()))
