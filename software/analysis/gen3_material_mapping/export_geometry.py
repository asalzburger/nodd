#!/usr/bin/env python3
"""Export native Gen3 Tracker portals and sensor frames for a mapping proposal.

Run in the verified nODD ACTS/DD4hep runtime. This reads the caller's compact and
factories; it neither modifies geometry nor establishes the recording's unknown
geometry revision. Units are millimetres. R-z segments contain [r, z] pairs.
"""

import argparse
from collections import Counter, defaultdict
import ctypes
import hashlib
import importlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time


# Numerical checks for an exact axisymmetric representation, not detector clearances.
TRANSFORM_TOLERANCE = 1e-9
BOUNDS_TOLERANCE_MM = 1e-9
EXPECTED_SENSORS = 45646
EXPECTED_VOLUMES = 117


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_revision(directory):
    return subprocess.check_output(
        ["git", "-C", str(directory), "rev-parse", "HEAD"], text=True
    ).strip()


def axisymmetric_transform(encoded):
    """Decode a native transform, rejecting tilted or off-axis geometry."""
    translation = encoded.get("translation") or [0., 0., 0.]
    flat = encoded.get("rotation") or [1., 0., 0., 0., 1., 0., 0., 0., 1.]
    if len(translation) != 3 or len(flat) != 9:
        raise ValueError("Malformed transform")
    values = [*translation, *flat]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Non-finite transform")
    rotation = [flat[i:i + 3] for i in (0, 3, 6)]
    for i in range(3):
        for j in range(3):
            product = sum(rotation[k][i] * rotation[k][j] for k in range(3))
            if abs(product - (i == j)) > TRANSFORM_TOLERANCE:
                raise ValueError("Non-orthonormal transform")
    determinant = sum(
        rotation[0][i] * (rotation[1][(i + 1) % 3] * rotation[2][(i + 2) % 3]
                          - rotation[1][(i + 2) % 3] * rotation[2][(i + 1) % 3])
        for i in range(3)
    )
    if abs(determinant - 1.) > TRANSFORM_TOLERANCE:
        raise ValueError("Transform is not a proper rotation")
    if max(abs(translation[0]), abs(translation[1])) > BOUNDS_TOLERANCE_MM:
        raise ValueError("Off-axis cylinder/disc cannot be an exact r-z segment")
    if max(abs(rotation[0][2]), abs(rotation[1][2]),
           abs(rotation[2][0]), abs(rotation[2][1])) > TRANSFORM_TOLERANCE:
        raise ValueError("Tilted cylinder/disc cannot be an exact r-z segment")
    return {"translation_mm": translation, "rotation": rotation}


def check_full_phi(half_phi):
    if not math.isfinite(half_phi) or abs(half_phi - math.pi) > TRANSFORM_TOLERANCE:
        raise ValueError("Partial-phi geometry cannot be an exact full-phi r-z segment")


def surface_geometry(surface):
    """Return exact finite geometry for a native axisymmetric portal surface."""
    transform = axisymmetric_transform(surface["transform"])
    z = transform["translation_mm"][2]
    bounds = surface["bounds"]
    values = bounds["values"]
    if len(values) != 4 or not all(math.isfinite(value) for value in values):
        raise ValueError("Malformed or non-finite portal bounds")
    if surface["type"] == "CylinderSurface" and bounds["type"] == "CylinderBounds":
        radius, half_z, half_phi, _ = values
        check_full_phi(half_phi)
        if radius <= 0. or half_z <= 0.:
            raise ValueError("Invalid finite cylinder")
        shape = {"radius_mm": radius, "z_min_mm": z - half_z, "z_max_mm": z + half_z}
        segment = [[radius, z - half_z], [radius, z + half_z]]
        kind = "cylinder"
    elif surface["type"] == "DiscSurface" and bounds["type"] == "RadialBounds":
        r_min, r_max, half_phi, _ = values
        check_full_phi(half_phi)
        if r_min < 0. or r_max <= r_min:
            raise ValueError("Invalid finite disc")
        shape = {"z_mm": z, "r_min_mm": r_min, "r_max_mm": r_max}
        segment = [[r_min, z], [r_max, z]]
        kind = "disc"
    else:
        raise ValueError(f"Unsupported portal: {surface['type']}/{bounds['type']}")
    return {"type": kind, **shape, "bounds": bounds,
            "transform": transform, "rz_segment_mm": segment}


def volume_geometry(volume):
    transform = axisymmetric_transform(volume["transform"])
    bounds = volume["bounds"]
    values = bounds["values"]
    if bounds["kind"] != "Cylinder" or len(values) != 5:
        raise ValueError("Unsupported tracking volume bounds")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Non-finite tracking volume bounds")
    r_min, r_max, half_z, half_phi, _ = values
    check_full_phi(half_phi)
    if r_min < 0. or r_max <= r_min or half_z <= 0.:
        raise ValueError("Invalid finite tracking volume")
    z = transform["translation_mm"][2]
    return {"type": "cylinder", "r_min_mm": r_min, "r_max_mm": r_max,
            "z_min_mm": z - half_z, "z_max_mm": z + half_z,
            "bounds": bounds, "transform": transform}


def link_surface_ids(link):
    """All native child surface IDs used to partition a merged portal link."""
    if link is None:
        return set()
    result = {link["surface_id"]} if "surface_id" in link else set()
    for child in [*link.get("children", []), *link.get("artifact_links", [])]:
        result.update(link_surface_ids(child))
    return result


def sign(value):
    return "positive" if value > TRANSFORM_TOLERANCE else (
        "negative" if value < -TRANSFORM_TOLERANCE else "zero")


def summarize_sensors(sensors, volumes):
    groups = defaultdict(list)
    for index, sensor in enumerate(sensors):
        center = sensor["center_mm"]
        normal = sensor["normal"]
        if len(center) != 3 or len(normal) != 3 or not all(
                math.isfinite(value) for value in [*center, *normal]):
            raise ValueError("Malformed sensor center/normal")
        if abs(sum(value * value for value in normal) - 1.) > TRANSFORM_TOLERANCE:
            raise ValueError("Non-unit sensor normal")
        radius = math.hypot(center[0], center[1])
        distance = math.sqrt(sum(value * value for value in center))
        radial_dot = sum(normal[i] * center[i] for i in (0, 1)) / radius if radius else 0.
        origin_dot = sum(normal[i] * center[i] for i in range(3)) / distance if distance else 0.
        sensor["normal_radial_dot"] = radial_dot
        sensor["normal_origin_dot"] = origin_dot
        groups[(sensor["ids"]["system"], sensor["ids"]["layer"])].append(index)
    volumes_by_name = {volume["name"]: volume for volume in volumes}
    result = []
    for (system, layer), indices in sorted(groups.items()):
        name = f"System{system}Layer{layer}"
        volume = volumes_by_name.get(name)
        if volume is None:
            raise ValueError(f"Missing native layer volume {name}")
        selected = [sensors[index] for index in indices]
        result.append({
            "system": system, "layer": layer, "volume_name": name,
            "volume_id": volume["volume_id"], "count": len(indices),
            "sensor_indices": indices,
            "r_range_mm": [min(math.hypot(*s["center_mm"][:2]) for s in selected),
                           max(math.hypot(*s["center_mm"][:2]) for s in selected)],
            "z_range_mm": [min(s["center_mm"][2] for s in selected),
                           max(s["center_mm"][2] for s in selected)],
            "normal_radial_sign_counts": dict(Counter(sign(s["normal_radial_dot"]) for s in selected)),
            "normal_z_sign_counts": dict(Counter(sign(s["normal"][2]) for s in selected)),
            "normal_origin_sign_counts": dict(Counter(sign(s["normal_origin_dot"]) for s in selected)),
        })
    return result


def build_export(native, report, identifier_value):
    """Reduce native serialization without substituting generated layout outlines."""
    surfaces = {surface["surface_id"]: surface for surface in native["surfaces"]}
    portal_records = {portal["portal_id"]: portal for portal in native["portals"]}
    if len(surfaces) != len(native["surfaces"]) or len(portal_records) != len(native["portals"]):
        raise ValueError("Duplicate native table IDs")
    owners = defaultdict(list)
    volumes = []
    report_by_name = {volume["name"]: volume for volume in report["volumes"]}
    for volume in native["volumes"]:
        vid = volume["volume_id"]
        portal_surface_ids = []
        for portal_id in volume["portal_ids"]:
            sid = portal_records[portal_id]["surface_id"]
            owners[sid].append({"volume_id": vid, "volume_name": volume["name"],
                                "portal_id": portal_id})
            portal_surface_ids.append(sid)
        native_report = report_by_name[volume["name"]]
        if len(volume["surface_id"]) != native_report["surfaces"]:
            raise ValueError("Native surface count differs between independent exporters")
        if len(volume["portal_ids"]) != native_report["portals"]:
            raise ValueError("Native portal count differs between independent exporters")
        geometry_id = identifier_value(volume["geometry_id"])
        if geometry_id != native_report["geometry_id"]:
            raise ValueError("Native volume geometry IDs disagree")
        volumes.append({"volume_id": vid, "geometry_id": geometry_id,
                        "geometry_id_fields": volume["geometry_id"],
                        "name": volume["name"], "children": volume["children"],
                        "portal_surface_ids": portal_surface_ids,
                        "sensitive_surface_count": len(volume["surface_id"]),
                        **volume_geometry(volume)})
    portals_by_surface = defaultdict(list)
    link_ids = set()
    for portal in native["portals"]:
        portals_by_surface[portal["surface_id"]].append(portal)
        for direction in ("along_normal", "opposite_normal"):
            link_ids.update(link_surface_ids(portal[direction]))
    portals = []
    for sid, native_portals in sorted(portals_by_surface.items()):
        surface = surfaces[sid]
        portals.append({"surface_id": sid, "geometry_id": identifier_value(surface["geo_id"]),
                        "geometry_id_fields": surface["geo_id"],
                        "portal_ids": [p["portal_id"] for p in native_portals],
                        "owners": owners[sid], "material": surface.get("material"),
                        "links": [{"portal_id": p["portal_id"],
                                   "along_normal": p["along_normal"],
                                   "opposite_normal": p["opposite_normal"]} for p in native_portals],
                        **surface_geometry(surface)})
    link_surfaces = []
    for sid in sorted(link_ids - portals_by_surface.keys()):
        surface = surfaces[sid]
        link_surfaces.append({"surface_id": sid, "geometry_id": identifier_value(surface["geo_id"]),
                              "geometry_id_fields": surface["geo_id"],
                              "material": surface.get("material"), **surface_geometry(surface)})
    sensors = report["sensors"]
    if len({sensor["geometry_id"] for sensor in sensors}) != len(sensors):
        raise ValueError("Duplicate sensor geometry IDs")
    if len({sensor["source_path"] for sensor in sensors}) != len(sensors):
        raise ValueError("Duplicate source sensor paths")
    if sum(surface.get("sensitive", False) for surface in native["surfaces"]) != len(sensors):
        raise ValueError("Native sensitive surface counts disagree")
    native_sensors = {
        identifier_value(surface["geo_id"]): surface
        for surface in native["surfaces"] if surface.get("sensitive", False)
    }
    maximum_center_residual = 0.
    maximum_axis_residual = 0.
    for sensor in sensors:
        surface = native_sensors[sensor["geometry_id"]]
        transform = surface["transform"]
        translation = transform.get("translation") or [0., 0., 0.]
        rotation = transform.get("rotation") or [1., 0., 0., 0., 1., 0., 0., 0., 1.]
        maximum_center_residual = max(maximum_center_residual, max(
            abs(sensor["center_mm"][i] - translation[i]) for i in range(3)))
        for column, name in enumerate(("u", "v", "normal")):
            if name in sensor:
                maximum_axis_residual = max(maximum_axis_residual, max(
                    abs(sensor[name][i] - rotation[3 * i + column]) for i in range(3)))
    if maximum_center_residual > BOUNDS_TOLERANCE_MM or maximum_axis_residual > TRANSFORM_TOLERANCE:
        raise ValueError("Native sensor frame exports disagree")
    sensor_groups = summarize_sensors(sensors, volumes)
    return {"schema_version": 1, "status": "PROTOTYPE", "units": "mm",
            "coordinate_convention": "R-z segments contain [r, z] endpoints; matrices are row-major local-to-global rotations.",
            "portal_identity": "surface_id and portal_id are native converter traversal IDs valid for this exact export; geometry_id is the ACTS identifier. Shared objects are deduplicated by native identity, not rounded coordinates.",
            "normal_convention": "Sensor normals are signed global local-z axes from DD4hep Box coordinates. These axes alone do not identify a sensor's physical front or material side.",
            "root_volume_id": native["root_volume_id"],
            "portals": portals, "portal_link_surfaces": link_surfaces,
            "volumes": volumes, "sensors": sensors, "sensor_groups": sensor_groups,
            "beampipe_portals": report["beampipe_portals"],
            "checks": {"sensitive_surfaces": len(sensors), "volumes": len(volumes),
                       "unique_portals": len(native["portals"]),
                       "unique_portal_surfaces": len(portals),
                       "unique_portal_link_subsurfaces": len(link_surfaces),
                       "native_surface_table_size": len(surfaces),
                       "sensor_groups": len(sensor_groups),
                       "portal_owner_references": sum(len(p["owners"]) for p in portals),
                       "sensor_export_max_center_difference_mm": maximum_center_residual,
                       "sensor_export_max_axis_difference": maximum_axis_residual,
                       "unsupported_portals": 0,
                       "axisymmetry_rotation_tolerance": TRANSFORM_TOLERANCE,
                       "axisymmetry_translation_tolerance_mm": BOUNDS_TOLERANCE_MM}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodd-dir", type=Path, required=True,
                        help="Checkout supplying the native adapter and compact")
    parser.add_argument("--build-dir", type=Path, required=True,
                        help="DD4hep build directory, absolute or relative to --nodd-dir")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    nodd = args.nodd_dir.expanduser().resolve()
    build = args.build_dir.expanduser()
    build = (build if build.is_absolute() else nodd / build).resolve()
    detector_dir = build / "detector" if (build / "detector").is_dir() else build
    compact = detector_dir / "tracker/tracker.xml"
    if not compact.is_file():
        parser.error(f"Missing compact: {compact}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ctypes.CDLL("libDDG4.dylib" if sys.platform == "darwin" else "libDDG4.so",
                mode=ctypes.RTLD_GLOBAL)
    import ROOT
    import dd4hep
    import acts
    import acts.json
    from acts.examples.nodd import getNoddDetector

    start = time.monotonic()
    ROOT.gROOT.SetBatch(True)
    detector = getNoddDetector(nodd_dir=nodd, build_dir=build, logLevel=acts.logging.WARNING)
    report = json.loads(detector.geometryReport())
    converter = acts.json.TrackingGeometryJsonConverter(level=acts.logging.WARNING)
    context = detector.nominalGeometryContext()
    serialized = converter.toJson(context, detector.trackingGeometry())
    native = json.loads(serialized)
    # Use the requested output transiently for the native decoder check, then
    # replace it with the reduced export only after the full check succeeds.
    args.output.write_text(serialized + "\n")
    decoded = converter.fromFile(context, args.output.resolve())
    round_trip = json.loads(converter.toJson(context, decoded))
    if native != round_trip:
        raise RuntimeError("Native ACTS geometry JSON round trip changed payload")

    def identifier_value(encoded):
        return acts.GeometryIdentifier(**(encoded or {})).value

    result = build_export(native, report, identifier_value)
    if result["checks"]["sensitive_surfaces"] != EXPECTED_SENSORS:
        raise RuntimeError("Unexpected sensor count; this exporter targets the DES-025 prototype")
    if result["checks"]["volumes"] != EXPECTED_VOLUMES:
        raise RuntimeError("Unexpected volume count; this exporter targets the DES-025 prototype")
    result["checks"]["native_json_round_trip"] = "PASS: complete serialized payload identical"
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    files = [("compact", compact), ("materials", compact.with_name("materials.xml")),
             ("exporter", Path(__file__).resolve())]
    files += [("factory", detector_dir / f"lib{name}{suffix}") for name in (
        "nODDBeamPipe", "nODDPixelBarrel", "nODDShortStripBarrel",
        "nODDShortStripEndcap", "nODDLongStrip")]
    for module_name in ("acts", "acts.ActsPythonBindings", "acts.examples.nodd",
                        "acts.examples.ActsExamplesPythonBindingsNodd"):
        module = importlib.import_module(module_name)
        if module.__file__:
            files.append(("runtime_module", Path(module.__file__)))
    runtime_build = Path(importlib.import_module("acts.ActsPythonBindings").__file__).parents[2]
    for name in ("ActsCore", "ActsExamplesNodd", "ActsPluginDD4hep", "ActsPluginJson"):
        library = runtime_build / "lib" / f"lib{name}{suffix}"
        if library.is_file():
            files.append(("runtime_library", library))
    adapter_root = nodd / "software/source/ActsExamples/Nodd"
    for relative in ("src/DD4hepNoddDetector.cpp", "python/nodd.py", "python/Nodd.cpp"):
        files.append(("adapter_source", adapter_root / relative))
    analysis_repo = Path(__file__).resolve().parents[3]
    acts_source = nodd / "software/submodules/acts"
    result["provenance"] = {
        "analysis_source_revision": git_revision(analysis_repo),
        "native_adapter_checkout_revision": git_revision(nodd),
        "ACTS_source_revision": git_revision(acts_source),
        "native_adapter_dirty_paths": subprocess.check_output(
            ["git", "-C", str(nodd), "status", "--short", "--", "software/source/ActsExamples/Nodd"],
            text=True).splitlines(),
        "ACTS_source_dirty_paths": subprocess.check_output(
            ["git", "-C", str(acts_source), "status", "--short"], text=True).splitlines(),
        "recording_geometry_revision": None,
        "geometry_provenance": "Explicit caller-supplied native compact and factories. The material recording has no embedded geometry revision; this export does not assert identity with it.",
        "ROOT": ROOT.gROOT.GetVersion(), "DD4hep_mm": float(dd4hep.mm),
        "python": platform.python_version(), "platform": platform.platform(),
        "native_serialization_sha256": hashlib.sha256(serialized.encode()).hexdigest(),
        "files": [{"role": role, "name": path.name, "sha256": sha256(path)} for role, path in files],
        "wall_seconds": time.monotonic() - start,
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result["checks"], indent=2))
    print(f"Wrote {args.output} ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
