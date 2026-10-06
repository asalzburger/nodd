#!/usr/bin/env python3
"""Construct and audit the isolated PR #29 pixel-barrel DD4hep prototype.

Imports of DD4hep/ROOT are deliberately deferred: report comparison and its
negative controls are usable without the optional simulation installation.
"""

from __future__ import annotations

import argparse
from array import array
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ray_direction(eta, phi):
    """Unit vector for a straight track, using the usual collider eta."""
    return [
        math.cos(phi) / math.cosh(eta),
        math.sin(phi) / math.cosh(eta),
        math.tanh(eta),
    ]


def compare_sensors(observed, expected, tolerance_mm=1e-7):
    """Check physical identities and both signed plane normals and centres."""
    errors = []
    by_ids = {}
    for sensor in observed:
        key = tuple(sorted(sensor["ids"].items()))
        if key in by_ids:
            errors.append(f"duplicate sensitive identifier: {dict(key)}")
        by_ids[key] = sensor
    expected_keys = set()
    max_center = max_normal = 0.0
    for sensor in expected:
        key = tuple(sorted(sensor["ids"].items()))
        if key in expected_keys:
            errors.append(f"duplicate expected identifier: {dict(key)}")
        expected_keys.add(key)
        actual = by_ids.get(key)
        if actual is None:
            errors.append(f"missing sensitive identifier: {dict(key)}")
            continue
        center = math.dist(actual["center_mm"], sensor["center_mm"])
        normal = math.dist(actual["normal"], sensor.get("normal", sensor.get("n")))
        max_center, max_normal = max(max_center, center), max(max_normal, normal)
        if center > tolerance_mm:
            errors.append(f"sensitive centre mismatch {dict(key)}: {center:.9g} mm")
        if normal > 1e-9:
            errors.append(f"sensitive normal mismatch {dict(key)}: {normal:.9g}")
        for axis in ("u", "v"):
            if axis in sensor and math.dist(actual[axis], sensor[axis]) > 1e-9:
                errors.append(f"sensitive {axis} axis mismatch {dict(key)}")
        if (
            "size_mm" in sensor
            and math.dist(actual["size_mm"], sensor["size_mm"]) > tolerance_mm
        ):
            errors.append(f"sensitive dimensions mismatch {dict(key)}")
    for key in set(by_ids) - expected_keys:
        errors.append(f"unexpected sensitive identifier: {dict(key)}")
    return {
        "passed": not errors,
        "errors": errors,
        "maximum_center_residual_mm": max_center,
        "maximum_normal_residual": max_normal,
        "observed": len(observed),
        "expected": len(expected),
    }


def exclusive_volume(volume, child_volumes):
    """Subtract immediate non-assembly daughters, never granddaughters twice."""
    result = volume - sum(child_volumes)
    if result < -max(1e-9, abs(volume) * 1e-9):
        raise ValueError("daughter capacities exceed their mother capacity")
    return max(0.0, result)


def shape_capacity(shape):
    """Exact capacities for primitives and the two explicitly supported CSGs.

    ROOT estimates general composite capacity by sampling. Avoid that stochastic
    value: inspect the actual CSG graph and prove the restricted geometry before
    using an analytical expression. New CSG shapes require a new audit method.
    """
    if str(shape.ClassName()) != "TGeoCompositeShape":
        return float(shape.Capacity())
    node = shape.GetBoolNode()
    operation = str(node.ClassName())
    left, right = node.GetLeftShape(), node.GetRightShape()
    if not node.GetLeftMatrix().IsIdentity():
        raise ValueError("unsupported transformed left CSG operand")
    if (
        str(right.ClassName()) not in ("TGeoTube", "TGeoTubeSeg")
        or right.GetRmin() != 0
    ):
        raise ValueError(f"unsupported CSG right operand: {right.ClassName()}")
    if (
        str(right.ClassName()) == "TGeoTubeSeg"
        and abs(right.GetPhi2() - right.GetPhi1() - 360.0) > 1e-10
    ):
        raise ValueError("CSG audit requires a complete cylinder")
    matrix = node.GetRightMatrix()
    rotation = [float(matrix.GetRotationMatrix()[i]) for i in range(9)]
    # DES015 tongue: radial box with its circular-plate intersection removed.
    identity = [1.,0.,0.,0.,1.,0.,0.,0.,1.]
    if operation == "TGeoSubtraction" and str(left.ClassName()) == "TGeoBBox" and max(abs(a-b) for a,b in zip(rotation,identity)) < 1e-12:
        tx,ty,tz = [float(matrix.GetTranslation()[i]) for i in range(3)]
        a,b,c = float(left.GetDX()),float(left.GetDY()),float(left.GetDZ())
        radius = float(right.GetRmax())
        start,end = -tx-a,-tx+a
        if abs(ty)>1e-12 or abs(tz)>1e-12 or start<=0 or math.hypot(start,b)>=radius or end<=radius or right.GetDz()<c:
            raise ValueError("unsupported endcap tongue subtraction")
        return (2*b*end-b*math.sqrt(radius*radius-b*b)-radius*radius*math.asin(b/radius))*2*c
    expected_rotation = [1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0]
    if max(abs(a - b) for a, b in zip(rotation, expected_rotation)) > 1e-12:
        raise ValueError("unsupported CSG cylinder orientation")
    tx, ty, tz = [float(matrix.GetTranslation()[i]) for i in range(3)]
    radius, half_length = float(right.GetRmax()), float(right.GetDz())
    if operation == "TGeoIntersection" and str(left.ClassName()) == "TGeoBBox":
        a, b, c = float(left.GetDX()), float(left.GetDY()), float(left.GetDZ())
        back = -tz - c
        if (
            abs(tx) > 1e-12
            or abs(ty) > 1e-12
            or abs(b - half_length) > 1e-12
            or abs(-tz + c - radius) > 1e-10
            or back <= 0
            or math.hypot(a, back) >= radius
        ):
            raise ValueError("unsupported foot intersection dimensions")
        return (
            (
                a * math.sqrt(radius * radius - a * a)
                + radius * radius * math.asin(a / radius)
                - 2 * a * back
            )
            * 2
            * b
        )
    if operation == "TGeoSubtraction":
        base, holes = left, [(tx, ty, tz, radius, half_length)]
        while str(base.ClassName()) == "TGeoCompositeShape":
            nested = base.GetBoolNode()
            if str(nested.ClassName()) != "TGeoSubtraction":
                raise ValueError("unsupported nested CSG operation")
            # Recursive call verifies the nested transform, hole and containment.
            shape_capacity(base)
            hole, transform = nested.GetRightShape(), nested.GetRightMatrix()
            holes.append(
                (
                    *[float(transform.GetTranslation()[i]) for i in range(3)],
                    float(hole.GetRmax()),
                    float(hole.GetDz()),
                )
            )
            base = nested.GetLeftShape()
        if str(base.ClassName()) != "TGeoBBox":
            raise ValueError("unsupported CSG subtraction mother")
        for x, y, z, r, dz in holes:
            if (
                abs(x) + r > base.GetDX() + 1e-12
                or abs(y) + dz > base.GetDY() + 1e-12
                or abs(z) + r > base.GetDZ() + 1e-12
            ):
                raise ValueError("cooling hole extends outside foam")
        for i, first in enumerate(holes):
            for second in holes[i + 1 :]:
                if (
                    math.hypot(first[0] - second[0], first[2] - second[2])
                    < first[3] + second[3]
                ):
                    raise ValueError("cooling subtraction holes overlap")
        return float(base.Capacity()) - sum(
            math.pi * r * r * 2 * dz for x, y, z, r, dz in holes
        )
    raise ValueError(f"unsupported CSG capacity: {operation}")


def physical_inventory(detector, dd4hep, ROOT, expected_entities):
    manager = detector.manager()
    unit = float(dd4hep.mm)
    counts, material = Counter(), defaultdict(
        lambda: {"volume_mm3": 0.0, "mass_g": 0.0}
    )
    sensors, nodes = [], []
    roles = {e["name"]: e["role"] for e in expected_entities}

    def visit(node, parent_matrix, inherited_ids, parent_path):
        volume = node.GetVolume()
        name = str(volume.GetName())
        path = parent_path + "/" + str(node.GetName())
        matrix = ROOT.TGeoHMatrix(parent_matrix)
        matrix.Multiply(node.GetMatrix())
        ids = dict(inherited_ids)
        placement = dd4hep.PlacedVolume(node)
        for field in placement.volIDs():
            ids[str(field.first)] = int(field.second)
        role = roles.get(name)
        if role:
            counts[role] += 1
        assembly = bool(volume.IsAssembly())
        children = [volume.GetNode(i) for i in range(volume.GetNdaughters())]
        item_info = {}
        if not assembly and name != str(manager.GetTopVolume().GetName()):
            capacity = shape_capacity(volume.GetShape()) / unit**3
            displaced = [
                shape_capacity(c.GetVolume().GetShape()) / unit**3
                for c in children
                if not c.GetVolume().IsAssembly()
            ]
            own_volume = exclusive_volume(capacity, displaced)
            substance = volume.GetMaterial()
            density = float(substance.GetDensity())
            item = material[str(substance.GetName())]
            item["volume_mm3"] += own_volume
            item["mass_g"] += own_volume * density / 1000.0
            item["density_g_cm3"] = density
            item["radiation_length_mm"] = float(substance.GetRadLen()) / unit
            item["interaction_length_mm"] = float(substance.GetIntLen()) / unit
            item_info.update(
                volume_mm3=own_volume,
                gross_volume_mm3=capacity,
                mass_g=own_volume * density / 1000.0,
                material=str(substance.GetName()),
            )
        origin, point = array("d", [0.0, 0.0, 0.0]), array("d", [0.0, 0.0, 0.0])
        vector, normal = array("d", [0.0, 0.0, 1.0]), array("d", [0.0, 0.0, 0.0])
        matrix.LocalToMaster(origin, point)
        matrix.LocalToMasterVect(vector, normal)
        if dd4hep.Volume(volume).isSensitive():
            sensors.append(
                {
                    "path": path,
                    "name": name,
                    "ids": ids,
                    "center_mm": [x / unit for x in point],
                    "normal": list(normal),
                    **{
                        axis: [float(matrix.GetRotationMatrix()[3*j+i]) for j in range(3)]
                        for i, axis in enumerate(("u", "v"))
                    },
                    "size_mm": [
                        2 * float(volume.GetShape().GetDX()) / unit,
                        2 * float(volume.GetShape().GetDY()) / unit,
                        2 * float(volume.GetShape().GetDZ()) / unit,
                    ],
                }
            )
        nodes.append(
            {
                "path": path,
                "name": name,
                "role": role,
                "ids": ids,
                "center_mm": [x / unit for x in point],
                "normal": list(normal),
                **item_info,
            }
        )
        for child in children:
            visit(child, matrix, ids, path)

    visit(manager.GetTopNode(), ROOT.TGeoHMatrix(), {}, "")
    return {
        "counts": dict(sorted(counts.items())),
        "materials": dict(sorted(material.items())),
        "sensors": sensors,
        "nodes": nodes,
        "physical_placements": len(nodes),
    }


def compare_entities(observed, expected, tolerance_mm=1e-7):
    errors = []
    lookup = defaultdict(list)
    for entity in observed:
        lookup[entity["name"]].append(entity)
    for entity in expected:
        found = lookup.get(entity["name"], [])
        if len(found) != 1:
            errors.append(
                f'{entity["name"]}: expected one physical placement, observed {len(found)}'
            )
            continue
        actual = found[0]
        if (
            "center_mm" in entity
            and math.dist(actual["center_mm"], entity["center_mm"]) > tolerance_mm
        ):
            errors.append(f'{entity["name"]}: centre differs from input')
        if "material" in entity and actual.get("material") != entity["material"]:
            errors.append(f'{entity["name"]}: material differs from input')
        if "ids" in entity and any(
            actual["ids"].get(k) != v for k, v in entity["ids"].items()
        ):
            errors.append(f'{entity["name"]}: physical IDs differ from input')
        for quantity in ("volume_mm3", "mass_g"):
            if quantity in entity and not math.isclose(
                actual.get(quantity, -1), entity[quantity], rel_tol=1e-6, abs_tol=1e-9
            ):
                errors.append(
                    f'{entity["name"]}: {quantity} differs from input: {actual.get(quantity)} vs {entity[quantity]}'
                )
    return {"passed": not errors, "errors": errors, "expected_entities": len(expected)}


def check_packed_identifiers(detector, ROOT, sensors, expected, dd4hep):
    packed_ids, errors = set(), []
    cells_checked = 0
    pitch = float(expected["readout_pitch_mm"])
    cell_ranges = set()
    readouts = expected.get("readouts_by_system", {"1": "PixelBarrelHits"})
    for sensor in sensors:
        readout_name = readouts.get(str(sensor["ids"]["system"]), expected["readout"])
        specification = detector.readout(readout_name).idSpec()
        decoder = specification.decoder()
        segmentation = detector.readout(readout_name).segmentation()
        fields = ROOT.std.vector("pair<string,int>")()
        for key, value in sorted(sensor["ids"].items()):
            fields.emplace_back(key, value)
        packed = int(specification.encode(fields))
        if packed in packed_ids:
            errors.append(f"duplicate encoded DD4hep VolumeID: {packed}")
        packed_ids.add(packed)
        for key, value in sensor["ids"].items():
            if int(decoder.get(packed, key)) != value:
                errors.append(f"VolumeID round-trip failure: {key}={value}")
        nx, ny = [round(sensor["size_mm"][axis] / pitch) for axis in (0, 1)]
        # Points just inside all four patch corners, plus the local origin.
        for ix, iy in (
            (-nx // 2, -ny // 2),
            (-nx // 2, ny // 2 - 1),
            (nx // 2 - 1, -ny // 2),
            (nx // 2 - 1, ny // 2 - 1),
            (0, 0),
        ):
            x = (
                0.0
                if ix == 0
                else math.copysign(sensor["size_mm"][0] / 2 - pitch * 1e-6, ix)
            )
            y = (
                0.0
                if iy == 0
                else math.copysign(sensor["size_mm"][1] / 2 - pitch * 1e-6, iy)
            )
            position = dd4hep.Position(x * float(dd4hep.mm), y * float(dd4hep.mm), 0.0)
            global_position = dd4hep.Position(
                *[c * float(dd4hep.mm) for c in sensor["center_mm"]]
            )
            cell_id = int(segmentation.cellID(position, global_position, packed))
            if (
                int(decoder.get(cell_id, "x")) != ix
                or int(decoder.get(cell_id, "y")) != iy
            ):
                errors.append(
                    f'{sensor["name"]}: incorrect cell indices at ({ix},{iy})'
                )
            returned = segmentation.position(cell_id)
            if math.hypot(
                returned.x() - (ix + 0.5) * pitch * float(dd4hep.mm),
                returned.y() - (iy + 0.5) * pitch * float(dd4hep.mm),
            ) > 1e-9 * float(dd4hep.mm):
                errors.append(f'{sensor["name"]}: cell centre round-trip mismatch')
            cells_checked += 1
        cell_ranges.add((nx, ny))
    return {
        "passed": not errors,
        "errors": errors,
        "unique_volume_ids": len(packed_ids),
        "readouts": sorted(set(readouts.values())),
        "pixel_cell_fields": "x,y remain zero for volume IDs",
        "cell_centres_checked": cells_checked,
        "patch_grids": sorted(cell_ranges),
        "pitch_mm": pitch,
    }


def trace_ray(
    manager, dd4hep, origin_mm, direction, sensitive_paths, max_length_mm=4000.0
):
    """Integrate actual ROOT navigation segments, with no fixed-step sampling."""
    unit = float(dd4hep.mm)
    manager.InitTrack(*[x * unit for x in origin_mm], *direction)
    navigator = manager.GetCurrentNavigator()
    distance = x0 = interaction = 0.0
    hits, materials, steps = set(), defaultdict(float), 0
    while not navigator.IsOutside() and distance < max_length_mm:
        node = navigator.GetCurrentNode()
        if not node:
            break
        path = str(navigator.GetPath())
        material = node.GetVolume().GetMaterial()
        is_world = str(node.GetVolume().GetName()) == str(
            manager.GetTopVolume().GetName()
        )
        navigator.FindNextBoundaryAndStep((max_length_mm - distance) * unit)
        length = float(navigator.GetStep()) / unit
        if not math.isfinite(length) or length < 0:
            raise RuntimeError(f"invalid ROOT navigation step: {length}")
        if length == 0:
            raise RuntimeError(f"zero ROOT navigation step at {path}")
        distance += length
        if path in sensitive_paths:
            hits.add(path)
        radiation = float(material.GetRadLen()) / unit
        nuclear = float(material.GetIntLen()) / unit
        if radiation > 0 and not is_world:
            x0 += length / radiation
        if nuclear > 0 and not is_world:
            interaction += length / nuclear
        if not is_world:
            materials[str(material.GetName())] += length
        steps += 1
        if steps > 100000:
            raise RuntimeError("ROOT navigation exceeded 100000 boundary steps")
    by_layer = Counter(sensitive_paths[path]["ids"].get("layer", -1) for path in hits)
    return {
        "origin_mm": origin_mm,
        "direction": direction,
        "distance_mm": distance,
        "x_over_x0": x0,
        "l_over_lambda": interaction,
        "sensitive_crossings": len(hits),
        "hits_by_layer": dict(sorted(by_layer.items())),
        "hits_by_detector_layer": dict(sorted(Counter(f"{sensitive_paths[path]['ids']['system']}:{sensitive_paths[path]['ids']['layer']}" for path in hits).items())),
        "crossed_layers": len(by_layer),
        "material_path_mm": dict(sorted(materials.items())),
        "boundary_steps": steps,
    }


def validate(args):
    import dd4hep
    import ROOT

    ROOT.gROOT.SetBatch(True)
    ROOT.gInterpreter.Declare(
        '#include "DD4hep/Version.h"\nnamespace nodd_validation { constexpr int major = DD4HEP_MAJOR_VERSION; constexpr int minor = DD4HEP_MINOR_VERSION; }'
    )
    if args.library and ROOT.gSystem.Load(str(args.library.resolve())) < 0:
        raise RuntimeError(f"could not load factory library: {args.library}")
    expected = json.loads(args.expected.read_text())
    detector = dd4hep.Detector.getInstance()
    detector.fromXML(str(args.compact.resolve()))
    manager = detector.manager()
    inventory = physical_inventory(detector, dd4hep, ROOT, expected["entities"])
    expected_sensors = [e for e in expected["entities"] if e["role"] == "sensitive"]
    comparison = compare_sensors(
        inventory["sensors"], expected_sensors, args.transform_tolerance_mm
    )
    entity_comparison = compare_entities(
        inventory["nodes"], expected["entities"], args.transform_tolerance_mm
    )
    identifiers = check_packed_identifiers(
        detector, ROOT, inventory["sensors"], expected, dd4hep
    )
    errors = comparison["errors"] + entity_comparison["errors"] + identifiers["errors"]
    for role, number in expected["counts"].items():
        if inventory["counts"].get(role, 0) != number:
            errors.append(
                f'{role}: expected {number}, observed {inventory["counts"].get(role, 0)}'
            )
    manager.CheckOverlaps(args.overlap_tolerance_mm * float(dd4hep.mm))
    overlaps = []
    for overlap in manager.GetListOfOverlaps():
        overlaps.append(
            {
                "name": str(overlap.GetName()),
                "description": str(overlap.GetTitle()),
                "penetration_mm": float(overlap.GetOverlap()) / float(dd4hep.mm),
            }
        )
    if overlaps:
        errors.append(f"ROOT found {len(overlaps)} overlaps/extrusions")
    sensor_paths = {x["path"]: x for x in inventory["sensors"]}
    rays = []
    # These are explicitly validation sample choices, not detector parameters.
    for origin in ([0.0, 0.0, 0.0], [1.0, 1.0, -150.0], [1.0, 1.0, 150.0]):
        for eta in (-2.0, -1.0, 0.0, 1.0, 2.0):
            for phi in (0.0, 0.37, 1.11, 2.29, 4.73):
                ray = trace_ray(
                    manager, dd4hep, origin, ray_direction(eta, phi), sensor_paths
                )
                ray.update(eta=eta, phi_rad=phi)
                rays.append(ray)
    if "readouts_by_system" in expected:
        # Exercise every endcap plane with an independently directed centre ray.
        targets = {}
        for s in expected_sensors:
            if s["ids"]["system"] != 1:
                targets.setdefault((s["ids"]["system"],s["ids"]["layer"]),s)
        for key,s in sorted(targets.items()):
            length=math.sqrt(sum(x*x for x in s["center_mm"]))
            ray=trace_ray(manager,dd4hep,[0.,0.,0.],[x/length for x in s["center_mm"]],sensor_paths)
            ray.update(target_detector_layer=list(key))
            rays.append(ray)
            if f"{key[0]}:{key[1]}" not in ray["hits_by_detector_layer"]:
                errors.append(f"targeted ray missed endcap plane {key}")
    if not any(r["sensitive_crossings"] for r in rays):
        errors.append(
            "none of the deterministic navigation rays crossed a sensitive volume"
        )
    expected_layers = {f"{s['ids']['system']}:{s['ids']['layer']}" for s in expected_sensors}
    crossed_layers = {layer for ray in rays for layer in ray["hits_by_detector_layer"]}
    if crossed_layers != expected_layers:
        errors.append(
            f"navigation did not exercise all pixel layers: {sorted(crossed_layers)} vs {sorted(expected_layers)}"
        )
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT_DIR, text=True
    ).strip()
    report = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "scope": "PROTOTYPE; DD4hep/ROOT construction and straight-ray navigation only",
        "commit": revision,
        "command": sys.argv,
        "python_version": platform.python_version(),
        "root_version": str(ROOT.gROOT.GetVersion()),
        "dd4hep_mm_in_root_units": float(dd4hep.mm),
        "dd4hep_version": f"{ROOT.nodd_validation.major}.{ROOT.nodd_validation.minor}",
        "compact_sha256": sha256(args.compact),
        "expected_sha256": sha256(args.expected),
        "library_sha256": sha256(args.library) if args.library else None,
        "validator_sha256": sha256(__file__),
        "world_material": {
            "name": str(manager.GetTopVolume().GetMaterial().GetName()),
            "density_g_cm3": float(manager.GetTopVolume().GetMaterial().GetDensity()),
        },
        "tolerances": {
            "overlap_mm": args.overlap_tolerance_mm,
            "sensitive_center_mm": args.transform_tolerance_mm,
            "normal": 1e-9,
        },
        "counts": inventory["counts"],
        "physical_placements": inventory["physical_placements"],
        "sensitive_comparison": comparison,
        "entity_comparison": entity_comparison,
        "packed_identifiers": identifiers,
        "input_provenance": expected.get("provenance", {}),
        "materials": inventory["materials"],
        "mass_g": sum(x["mass_g"] for x in inventory["materials"].values()),
        "overlaps": overlaps,
        "navigation": rays,
        "navigation_summary": {
            "layers_exercised": sorted(crossed_layers),
            "minimum_sensor_crossings": min(r["sensitive_crossings"] for r in rays),
            "maximum_sensor_crossings": max(r["sensitive_crossings"] for r in rays),
            "maximum_boundary_steps": max(r["boundary_steps"] for r in rays),
        },
        "navigation_sampling": f"{len(rays)} deterministic rays; base 75 rays plus one directed ray per endcap plane when present; no random seed",
        "material_accounting": "Exclusive volumes; world medium excluded. Primitive capacities and independently inspected curved-foot CSG have analytical capacities.",
        "limitations": [
            "No Geant4 transport, magnetic bending or ACTS conversion in this DD4hep-only test.",
            "Sparse deterministic rays are navigation checks, not a coverage or hermeticity claim.",
            "ROOT overlap tolerance is a proposed numerical tolerance, not an assembly clearance.",
        ],
    }
    # Destroy geometry while ROOT's thread mutexes are still alive. Deferring
    # its singleton to C++ static teardown crashes ROOT 6.40 after CheckOverlaps.
    dd4hep.Detector.destroyInstance()
    if ROOT.gGeoManager:
        ROOT.gGeoManager.Delete()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        f'{report["status"]}: {len(inventory["sensors"])} sensitive placements; {len(overlaps)} overlaps; {len(rays)} rays'
    )
    return 0 if not errors else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--library", type=Path)
    parser.add_argument("--overlap-tolerance-mm", type=float, default=1e-5)
    parser.add_argument("--transform-tolerance-mm", type=float, default=1e-7)
    args = parser.parse_args()
    if not all(
        math.isfinite(value) and value > 0
        for value in (args.overlap_tolerance_mm, args.transform_tolerance_mm)
    ):
        parser.error("tolerances must be finite and positive")
    return validate(args)


if __name__ == "__main__":
    raise SystemExit(main())
