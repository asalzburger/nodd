"""Native ACTS review assets and shape inventories for the DES040 wheel candidate.

Visualization/inventory only. No geometry, magnetic map, propagator or historical
artifact is changed. Run with the installed ACTS Python environment for matplotlib:
``python -B -m tools.muon_layout.wheels_artifacts``. Existing verified native
binaries are used; no build or dependency installation is performed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import zipfile

import numpy as np

from . import export_obj as old
from . import wheel_inventory as inventory
from .acts.prepare import export_geometry
from .geometry import vertices3, volume

ROOT = Path(__file__).resolve().parents[2]
REVISION = "a32558a419404dfe741182b6713ce1f31062fd37"
BASE = "docs/validation/DES-040/geometry.json"
SCOPE = ROOT / "docs/validation/DES-040/wheels-2026-10-20"
FINAL_GEOMETRY_SHA = "621b5cb9d45906b338251d527d932abd6b9aca86c84ffaa0918c7e535a17781f"
EXPECTED_PROPAGATOR = "397ca6d59d2798cd5ab53e1faa78bccf8250de6d324d2eafe9be14c39c7a005d"
EXPECTED_WRITER = "f4c9842fd7534b7adb64b086495c25092bc6d1e6022665dfbc621aeeb024ee62"
EXPECTED_CORE = "f4c040fa6c331fca6180dc75589fbc95ec30fc485c2edbefb891fda46cdf7088"
SOURCE_PATHS = ("tools/muon_layout/export_obj.py", "tools/muon_layout/wheel_inventory.py",
    "tools/muon_layout/obj_writer/writer.cpp", "tools/muon_layout/acts/prepare.py",
    "tools/muon_layout/geometry.py", "tools/toroid_prototype/geometry.py")
FRAME_SCOPE = ("Actual source support outer-prism reservations; hollow RHS cavities are omitted "
               "for review visibility. Separate members overlap at joints; these objects are "
               "neither material solids nor a mass union. Frame is outside the chamber-only ACTS world.")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def pinned(path):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", REVISION+":"+path])


def material_cleanup(path, colors):
    """Retain one byte-identical ACTS block per actual colour, including mono views."""
    raw = path.read_bytes()
    unique = {}
    for block in re.split(r"(?=^newmtl )", raw.decode(), flags=re.M):
        if not block.strip():
            continue
        name = block.splitlines()[0].split()[1]
        if name in unique and unique[name] != block:
            raise ValueError("conflicting native material definitions")
        unique[name] = block
    wanted = {"material_"+"_".join(map(str, c)) for c in colors}
    if set(unique) != wanted:
        raise ValueError("native material inventory differs from requested colours")
    path.write_text("".join(unique.values()))
    for color in colors:
        block = unique["material_"+"_".join(map(str, color))]
        kd = next(line.split()[1:] for line in block.splitlines() if line.startswith("Kd "))
        if not np.allclose(list(map(float, kd)), np.array(color)/256, atol=5.1e-7, rtol=0):
            raise ValueError("ACTS diffuse colour changed")
    return hashlib.sha256(raw).hexdigest()


def prism_objects(members):
    faces = ([3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4],
             [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7])
    result = []
    for p in members:
        v = vertices3(p)
        name = "frame_"+re.sub(r"[^A-Za-z0-9_.-]", "_", p["id"])
        result.append((name, old.GREY, [v[list(f)] for f in faces]))
    return result


def verify_obj(path, expected, prism_volumes):
    actual, vertex_count = old.read_obj(path)
    assert list(actual) == [o[0] for o in expected]
    maximum, max_volume_error, minimum_volume = 0., 0., float("inf")
    for name, color, polygons in expected:
        assert len(actual[name]) == len(polygons)
        edges, directed, signed_volume = Counter(), Counter(), 0.
        for (material, face), target in zip(actual[name], polygons):
            assert material == "material_"+"_".join(map(str, color))
            residual = float(abs(face-target).max())
            maximum = max(maximum, residual)
            assert residual < 1e-12
            ids = [tuple(np.round(v, 9)) for v in face]
            assert len(set(ids)) == 4
            for a, b in zip(ids, ids[1:]+ids[:1]):
                edges[tuple(sorted((a, b)))] += 1
                directed[a, b] += 1
            for j in (1, 2):
                signed_volume += np.dot(face[0], np.cross(face[j], face[j+1]))/6
        assert all(v == 2 for v in edges.values())
        assert all(directed[b, a] == count for (a, b), count in directed.items())
        assert signed_volume > 0
        minimum_volume = min(minimum_volume, signed_volume)
        if name in prism_volumes:
            max_volume_error = max(max_volume_error, abs(signed_volume-prism_volumes[name]))
    assert max_volume_error < 1e-10
    vertices = np.concatenate([np.concatenate(faces) for _, _, faces in expected])
    return {"objects": len(expected), "quad_faces": sum(len(o[2]) for o in expected),
            "roles": dict(Counter(name.split("_", 1)[0] for name, _, _ in expected)),
            "raw_obj_vertices": vertex_count, "all_objects_closed_and_outward_oriented": True,
            "welding_dimension_grid_m": 1e-9, "maximum_roundtrip_coordinate_error_m": maximum,
            "maximum_prism_volume_error_m3": max_volume_error,
            "minimum_positive_object_volume_m3": minimum_volume,
            "global_bounds_xyz_m": [vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()],
            "coordinates": "metres; right-handed Cartesian; beam along z"}


def preview(path, objects, label, frame=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    vertices = np.concatenate([np.concatenate(faces) for _, _, faces in objects])
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    span = np.maximum(hi-lo, .5)
    bounds = [lo-.035*span, hi+.035*span]
    fig = plt.figure(figsize=(13, 10))
    ax = fig.add_subplot(111, projection="3d")
    labels = []
    for color in (old.GREY, old.BLUE):
        selected = [(name, fs) for name, col, fs in objects if col == color]
        if not selected:
            continue
        faces = [face for _, fs in selected for face in fs]
        ax.add_collection3d(Poly3DCollection(faces, facecolors=np.array(color)/256,
            edgecolors="none", alpha=.28 if color == old.BLUE else .95, rasterized=True))
        role = f"{len(selected)} chamber envelopes" if color == old.BLUE else (
            "36 warm sweeps + support outer prisms" if frame else "36 toroid warm sweeps")
        labels.append(Patch(color=np.array(color)/256, label=role))
    ax.set(xlim=(bounds[0][0], bounds[1][0]), ylim=(bounds[0][1], bounds[1][1]),
           zlim=(bounds[0][2], bounds[1][2]), xlabel="x [m]", ylabel="y [m]", zlabel="z [m]")
    ax.set_box_aspect(span)
    ax.view_init(elev=18, azim=-48)
    ax.legend(handles=labels, loc="upper left")
    caption = "PROTOTYPE · frame outer reservations; cavities omitted" if frame else (
        "PROTOTYPE · blue chamber transparency is preview only")
    ax.set_title(label+"\n"+caption)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    assert np.all(vertices >= bounds[0]) and np.all(vertices <= bounds[1])
    return {"dynamic_display_bounds_xyz_m": [x.tolist() for x in bounds],
            "all_vertices_inside_display_bounds": True}


def bundle_zip(path, members):
    with zipfile.ZipFile(path, "w") as archive:
        for member in members:
            entry = zipfile.ZipInfo(member.name, date_time=(2026, 10, 20, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, member.read_bytes())
    with zipfile.ZipFile(path) as archive:
        assert archive.namelist() == [p.name for p in members]
        assert all(archive.read(p.name) == p.read_bytes() for p in members)
    return {"sha256": sha(path), "member_names": [p.name for p in members],
            "member_bytes_equal_to_siblings": True}


def common_inventory_limits(before, after):
    widths, heights = [], []
    for geometry in (before, after):
        for p in geometry["panels"]:
            if p["kind"] != "endcap":
                continue
            d = inventory.dimensions(p)
            widths.append(2*max(d["inner_base_m"]/2,
                               abs(d["outer_base_offset_m"])+d["outer_base_m"]/2))
            heights.append(d["radial_span_m"])
    return max(widths), max(heights)


def inventories(before_path, after_path, out):
    import matplotlib
    before, after = [json.loads(p.read_text()) for p in (before_path, after_path)]
    limits = common_inventory_limits(before, after)
    reports = {}
    for name, path, kind, label, scale in (
        ("before-endcap", before_path, "endcap", "Before wheel revision", limits),
        ("after-endcap", after_path, "endcap", "After wheel revision", limits),
        ("current-barrel", after_path, "barrel", "Current repacked barrel", None)):
        # The existing helper places captions below its axes. A tight save
        # includes their full extent for short sheets without editing it.
        with matplotlib.rc_context({"savefig.bbox": "tight", "savefig.pad_inches": .2}):
            reports[name] = inventory.write(path, out, kind, label, prefix=name, common_limits=scale)
    # Full-precision source dimensions in CSV complement the display-family CSV.
    maps = {}
    counts = {}
    for tag, geometry in (("before", before), ("after", after)):
        maps[tag] = {}
        rows = []
        for kind in ("barrel", "endcap"):
            report = inventory.inventory(geometry, kind)
            for entry in report["panels"]:
                maps[tag][entry["panel_id"]] = dict(entry, kind=kind)
                rows.append({"panel_id": entry["panel_id"], "shape_id": entry["shape_id"],
                    "kind": kind, "station": entry["station"], "side": entry["side"],
                    **entry["actual_dimensions_m"]})
        fields = list(dict.fromkeys(key for row in rows for key in row))
        with (out/f"{tag}-panels-unrounded.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fields, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        counts[tag] = {"total": len(geometry["panels"]),
            "by_kind": dict(Counter(p["kind"] for p in geometry["panels"])),
            "by_kind_station_side": dict(Counter(
                f"{p['kind']}/S{p['station']}/"+str(p.get("side", 0)) for p in geometry["panels"]))}
    bodies = {tag: {p["id"]: p for p in geometry["panels"]}
              for tag, geometry in (("before", before), ("after", after))}
    mapping = []
    for ident in sorted(set(maps["before"]) | set(maps["after"])):
        a, b = maps["before"].get(ident), maps["after"].get(ident)
        if a is None:
            status = "added"
        elif b is None:
            status = "removed"
        elif a["actual_dimensions_m"] != b["actual_dimensions_m"]:
            status = "same_id_changed_dimensions"
        elif any(bodies["before"][ident][key] != bodies["after"][ident][key]
                 for key in ("origin_m", "basis", "vertices_m", "depth_m")):
            status = "same_id_moved_or_rotated"
        else:
            status = "unchanged"
        mapping.append({"panel_id": ident, "status": status, "before": a, "after": b})
    change = {"status": "source shape/placement bookkeeping, not performance or manufacturability",
              "before_geometry_sha256": sha(before_path), "after_geometry_sha256": sha(after_path),
              "counts": counts, "shared_endcap_plot_limits_m": list(limits),
              "shape_families": {name: report["shape_families"] for name, report in reports.items()},
              "mapping_status_counts": dict(Counter(p["status"] for p in mapping)), "panels": mapping,
              "identity_scope": "Identical strings are compared literally; wholesale replacement wheels have new IDs. No fabricated one-to-one correspondence between different modules."}
    save(out/"comparison.json", change)
    with (out/"shape-change-mapping.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, ["panel_id", "status", "kind", "station", "side", "before_shape_id", "after_shape_id"], lineterminator="\n")
        writer.writeheader()
        for row in mapping:
            entry = row["after"] or row["before"]
            writer.writerow({"panel_id": row["panel_id"], "status": row["status"],
                **{k: entry[k] for k in ("kind", "station", "side")},
                "before_shape_id": row["before"]["shape_id"] if row["before"] else "",
                "after_shape_id": row["after"]["shape_id"] if row["after"] else ""})
    return change


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=Path, default=SCOPE/"candidate/geometry.json")
    parser.add_argument("--geometry-sha256", default=FINAL_GEOMETRY_SHA)
    parser.add_argument("--propagator", type=Path, default=ROOT/"reference/cache/pr90-wheels/build/nodd-muon-wheels-propagate")
    parser.add_argument("--writer", type=Path, default=ROOT/"reference/cache/pr90-obj/build/nodd-muon-obj")
    parser.add_argument("--acts-library", type=Path, default=Path("/Users/salzburg/Documents/work/installed/acts-nodd/lib/libActsCore.dylib"))
    args = parser.parse_args()
    out, inv = SCOPE/"obj-revised", SCOPE/"inventory-comparison"
    out.mkdir(parents=True, exist_ok=True); inv.mkdir(parents=True, exist_ok=True)
    work = out/"native-inspection"; work.mkdir(exist_ok=True)
    historical_paths = [ROOT/BASE, ROOT/"docs/validation/DES-039/results.json"]
    historical_paths += list((ROOT/"docs/validation/DES-040/obj").glob("*"))
    historical_hashes = {str(p.relative_to(ROOT)): sha(p) for p in historical_paths if p.is_file()}
    for path in SOURCE_PATHS + (BASE, "docs/validation/DES-039/results.json"):
        assert sha(ROOT/path) == hashlib.sha256(pinned(path)).hexdigest(), path
    assert sha(args.geometry) == args.geometry_sha256
    for path, expected in ((args.propagator, EXPECTED_PROPAGATOR), (args.writer, EXPECTED_WRITER), (args.acts_library, EXPECTED_CORE)):
        assert sha(path) == expected, path
    geometry = json.loads(args.geometry.read_text())
    panels = export_geometry({"geometry": str(args.geometry.relative_to(ROOT))}, work/"geometry.dat")
    vertices = np.concatenate([vertices3(p) for p in panels])
    assert (np.hypot(vertices[:, 0], vertices[:, 1]) < 9.1).all() and (abs(vertices[:, 2]) < 13.3).all()
    command = [str(args.propagator.resolve()), "--geometry", str(work/"geometry.dat"), "--field", "zero",
        "--inspect-only", "--output-dir", str(work), "--world-radius-m", "9.1", "--world-half-z-m", "13.3",
        "--entrance-radius-m", "4.35", "--entrance-half-z-m", "6.4684"]
    with (work/"inspection.log").open("w") as stream:
        subprocess.run(command, check=True, stdout=stream, stderr=subprocess.STDOUT)
    chamber_objects, native_error = old.chambers(work, panels)
    coil_objects = old.coils(geometry["magnetic_configuration"])
    members = geometry["supports"]["members"]
    frame_objects = prism_objects(members)
    prism_volumes = {o[0]: volume(p) for o, p in zip(chamber_objects, panels)}
    prism_volumes.update({o[0]: volume(p) for o, p in zip(frame_objects, members)})
    bundles = {
        "chambers-and-coils": (chamber_objects+coil_objects, "Revised chambers and toroid warm envelopes", False),
        "barrel-chambers": ([o for o,p in zip(chamber_objects, panels) if p["kind"] == "barrel"], "Current repacked barrel chambers", False),
        "positive-endcap-chambers": ([o for o,p in zip(chamber_objects, panels) if p["kind"] == "endcap" and p["side"] > 0], "Positive-endcap chamber envelopes · all three stations", False),
        "toroids-and-frame": (coil_objects+frame_objects, "Toroid warm envelopes and support outer prisms", True)}
    checks, assets = {}, {}
    component_members = []
    for name, (objects, label, frame) in bundles.items():
        input_path, obj = work/f"{name}-objects.txt", out/f"{name}.obj"
        old.write_input(input_path, objects)
        result = subprocess.run([str(args.writer.resolve()), str(input_path), str(obj)], check=True, capture_output=True, text=True)
        raw_mtl = material_cleanup(obj.with_suffix(".mtl"), {o[1] for o in objects})
        checks[name] = verify_obj(obj, objects, prism_volumes)
        checks[name].update(preview(out/f"{name}.png", objects, label, frame), raw_native_mtl_sha256=raw_mtl,
                            native_writer_stdout=result.stdout.strip())
        assets[name] = {p.name: sha(p) for p in (obj, obj.with_suffix(".mtl"), out/f"{name}.png")}
        if name != "chambers-and-coils":
            component_members.extend((obj, obj.with_suffix(".mtl")))
    zip_checks = {
        "chambers-and-coils.zip": bundle_zip(out/"chambers-and-coils.zip", [out/"chambers-and-coils.obj", out/"chambers-and-coils.mtl"]),
        "components.zip": bundle_zip(out/"components.zip", component_members)}
    change = inventories(ROOT/BASE, args.geometry, inv)
    source_hashes = {p: sha(ROOT/p) for p in SOURCE_PATHS+(
        "tools/muon_layout/wheels_artifacts.py", "tools/muon_layout/wheels.py", "tools/muon_layout/wheels-config.json")}
    report = {"status": "isolated PROTOTYPE visualization and source inventory; no response or engineering approval",
        "input_revision": REVISION, "execution_HEAD": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "source_files_worktree_sha256": source_hashes, "candidate_geometry_sha256": sha(args.geometry),
        "historical_geometry_sha256": sha(ROOT/BASE), "native_propagator_sha256": sha(args.propagator),
        "native_obj_writer_sha256": sha(args.writer), "acts_core_library_sha256": sha(args.acts_library),
        "native_inspection_command": command, "native_inspection_metadata": json.loads((work/"metadata.json").read_text()),
        "native_face_corner_sha256": sha(work/"geometry-corners.csv"), "native_face_sha256": sha(work/"geometry.csv"),
        "maximum_native_to_source_corner_error_m": native_error,
        "chamber_count": len(panels), "coil_count": len(coil_objects), "frame_outer_prism_count": len(members),
        "chambers_inside_native_world": True, "chamber_max_abs_z_m": float(abs(vertices[:, 2]).max()),
        "chamber_max_radius_m": float(np.hypot(vertices[:,0],vertices[:,1]).max()),
        "colors_rgb_8bit": {"chambers": old.BLUE, "coils_and_frame": old.GREY}, "native_material_rgb_divisor": 256,
        "material_processing": "Only deduplicate identical ACTS MTL blocks; sibling relative mtllib; no coordinate or colour changes.",
        "coil_representation": "36 separate analytic warm-sweep reservations, not a Boolean mass union; shortened ECT, retained BT and warm section.",
        "frame_representation": FRAME_SCOPE, "coil_arc_segments_per_quadrant": old.ARC_STEPS,
        "maximum_coil_chord_sagitta_m": max((g["corner_radius_m"]+geometry["magnetic_configuration"]["warm"]["normal_m"]/2)*(1-np.cos(np.pi/(4*old.ARC_STEPS))) for g in geometry["magnetic_configuration"]["coil_groups"].values()),
        "checks": checks, "zip_checks": zip_checks, "artifacts": assets,
        "inventory_counts": change["counts"], "inventory_families": change["shape_families"],
        "software": {"python": platform.python_version(), "numpy": np.__version__},
        "historical_artifact_hashes_unchanged": historical_hashes,
        "limits": ["Visual chamber envelopes contain no MDT internals or measured response.", FRAME_SCOPE,
            "No solenoid, HCAL, floor solid, tracks, world or entrance object is exported.",
            "Native chamber faces and analytic coil/frame reservations are distinct representations; colours are not materials."]}
    assert all(sha(ROOT/p) == digest for p, digest in historical_hashes.items())
    assert sha(args.geometry) == args.geometry_sha256
    save(out/"export.json", report)
    (out/"README.md").write_text(
        "# Revised wheel geometry: native ACTS OBJ\n\n"
        "Isolated PROTOTYPE. [Combined chambers and coils ZIP](chambers-and-coils.zip) contains a sibling OBJ/MTL pair. "
        "[Component ZIP](components.zip) contains barrel, positive endcap and toroids-plus-frame pairs. "
        "All paths in OBJ material references are relative; coordinates are metres, right-handed xyz, beam along z.\n\n"
        "Chambers are blue RGB(0,96,255); coils/frame are grey RGB(160,160,160). ACTS stores diffuse values divided by 256. "
        "Blue transparency is preview only. Native finite chamber vertices are exported at17-digit precision. "
        "Every object is checked closed and outward-oriented after 1 nm position welding. Warm coils use 64 chords per quadrant.\n\n"
        +FRAME_SCOPE+" No physical magnetic/material response, construction acceptance or mass follows.\n\n"
        "![Combined preview](chambers-and-coils.png)\n\n"
        "[Barrel](barrel-chambers.obj) · [Positive endcap](positive-endcap-chambers.obj) · [Toroids and frame](toroids-and-frame.obj). "
        "Each has a sibling MTL/PNG. [Exact source/native checks and hashes](export.json).\n\n"
        "Reproduce: `MPLCONFIGDIR=/private/tmp/pr90-wheels-matplotlib XDG_CACHE_HOME=/private/tmp/pr90-wheels-cache "
        "/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python -B -m tools.muon_layout.wheels_artifacts`. "
        "Existing native binary/library hashes are checked; no builds run.\n")
    (inv/"README.md").write_text(
        "# Before/after chamber shape inventory\n\n"
        "[Before endcap](before-endcap.md) · [After endcap](after-endcap.md) · [Current repacked barrel](current-barrel.md). "
        "Endcap shape sheets use identical metric limits, including the long whole-wheel trapezoids. "
        "All shapes use the same blue diffuse colour as the OBJ.\n\n"
        f"Before: {change['counts']['before']['total']} chambers. After: {change['counts']['after']['total']} chambers. "
        "The [comparison JSON](comparison.json) gives counts by station/hemisphere and every panel's intrinsic dimensions and ID status; "
        "[mapping CSV](shape-change-mapping.csv), before/after-panels-unrounded.csv retain the source identities and unrounded dimensions. "
        "Shape-family display grouping uses 1 nm dimensions; it is not a manufacturing tolerance. "
        "A new whole wheel is not paired artificially one-to-one with removed ordinary modules.\n\n"
        "This is source geometry bookkeeping, not reconstructed efficiency, MDT manufacturing or engineering acceptance. "
        "[Provenance](provenance.json). Reproduce with the wheels_artifacts command in ../obj-revised/README.md.\n")
    save(inv/"provenance.json", {"source_geometry_before_sha256": sha(ROOT/BASE), "source_geometry_after_sha256": sha(args.geometry),
        "generator_sha256": sha(__file__), "inventory_helper_sha256": sha(ROOT/"tools/muon_layout/wheel_inventory.py"),
        "input_revision": REVISION, "shared_endcap_limits_m": change["shared_endcap_plot_limits_m"],
        "artifacts_sha256": {p.name: sha(p) for p in sorted(inv.iterdir()) if p.is_file() and p.name != "provenance.json"}})
    print(json.dumps({"chambers": len(panels), "coils": len(coil_objects), "frame": len(members),
                      "native_corner_error_m": native_error, "inventories": change["shape_families"],
                      "output": str(out), "inventory_output": str(inv)}, indent=2))


if __name__ == "__main__":
    main()
