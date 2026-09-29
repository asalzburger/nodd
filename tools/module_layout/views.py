#!/usr/bin/env python3
"""PROTOTYPE: true barrel sections and labelled endcap-assembly projections."""

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import subprocess

import numpy as np

try:
    from .geometry import _shape
except ImportError:
    from geometry import _shape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SECTION_TOLERANCE_MM = 1e-9
SUBSYSTEMS = ("pixel", "short_strip", "long_strip")
LABELS = {"pixel": "Pixels", "short_strip": "Short strips", "long_strip": "Long-strip pairs"}
COLOURS = {"pixel": "#176fa8", "short_strip": "#ba6e18", "long_strip": "#287964"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def rectangle_vertices(record):
    c, u, v = (np.asarray(record[key], dtype=float) for key in ("center_mm", "u", "v"))
    return np.asarray([c + a * record["half_u_mm"] * u + b * record["half_v_mm"] * v
                       for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def box_vertices(body):
    c, u, v, n = (np.asarray(body[key], dtype=float) for key in ("center_mm", "u", "v", "n"))
    return np.asarray([c + a * body["half_u_mm"] * u + b * body["half_v_mm"] * v
                       + d * body["half_w_mm"] * n
                       for a, b, d in itertools.product((-1, 1), repeat=3)])


def _unique(points, tolerance=SECTION_TOLERANCE_MM):
    result = []
    for point in points:
        if not any(np.linalg.norm(point - other) <= tolerance for other in result):
            result.append(np.asarray(point))
    return np.asarray(result).reshape(-1, 2)


def _section(vertices, edges, z_mm):
    """Intersect an edge graph with z=z_mm; return ordered xy vertices."""
    if vertices[:, 2].min() > z_mm + SECTION_TOLERANCE_MM or vertices[:, 2].max() < z_mm - SECTION_TOLERANCE_MM:
        return np.empty((0, 2))
    points = []
    for ia, ib in edges:
        a, b = vertices[ia], vertices[ib]
        da, db = a[2] - z_mm, b[2] - z_mm
        if abs(da) <= SECTION_TOLERANCE_MM:
            points.append(a[:2])
        if abs(db) <= SECTION_TOLERANCE_MM:
            points.append(b[:2])
        if da * db < 0.:
            points.append((a + da / (da - db) * (b - a))[:2])
    points = _unique(points)
    if len(points) > 2:
        center = points.mean(axis=0)
        points = points[np.argsort(np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0]))]
    return points


def box_section(body, z_mm):
    return _section(box_vertices(body), [(i, j) for i in range(8) for j in range(i + 1, 8)
                                        if (i ^ j) in (1, 2, 4)], z_mm)


def sensor_section(sensor, z_mm):
    return _section(rectangle_vertices(sensor), [(0, 1), (1, 2), (2, 3), (3, 0)], z_mm)


def convex_hull(points):
    """Projected box silhouette, including the contribution of its thickness."""
    points = sorted(set(map(tuple, np.asarray(points, dtype=float))))
    if len(points) <= 2:
        return np.asarray(points).reshape(-1, 2)

    def turn(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    lower, upper = [], []
    for point in points:
        while len(lower) >= 2 and turn(lower[-2], lower[-1], point) <= 0.:
            lower.pop()
        lower.append(point)
    for point in reversed(points):
        while len(upper) >= 2 and turn(upper[-2], upper[-1], point) <= 0.:
            upper.pop()
        upper.append(point)
    return np.asarray(lower[:-1] + upper[:-1])


def sensor_outlines(layout):
    """Recover one conditional physical-sensor rectangle per sensor_id.

    Chip-active patch centres are symmetric around their physical sensor centre;
    the authoritative model's _shape function supplies its guard-inclusive size.
    These outlines are distinct from readout-chip silicon and trial body boxes.
    """
    groups = defaultdict(list)
    for patch in layout["modules"]:
        groups[patch["sensor_id"]].append(patch)
    result = []
    for patches in groups.values():
        first = patches[0]
        shape = _shape(first["family"], layout["metadata"]["models"])
        if not math.isclose(shape["sensor_u"] * shape["sensor_v"], first["sensor_area_mm2"], abs_tol=1e-8):
            raise AssertionError("Physical-sensor outline disagrees with retained sensor area")
        result.append(dict(first, center_mm=np.mean([p["center_mm"] for p in patches], axis=0).tolist(),
                           half_u_mm=shape["sensor_u"] / 2., half_v_mm=shape["sensor_v"] / 2.))
    return result


def load_case(run, case_id):
    # The study driver follows the repository's sibling-script import layout.
    from study import case_layout
    run = Path(run)
    metadata = read(run / "run.json")
    if digest(HERE / "geometry.py") != metadata["code_sha256"]["geometry.py"]:
        raise RuntimeError("Geometry code differs from the retained run; use the matching checkout or create a fresh run")
    cases = [case for case in metadata["cases"] if case["id"] == case_id]
    if len(cases) != 1:
        raise ValueError("Case must occur exactly once in the retained run")
    layout = case_layout(cases[0], read(run / "sensor_models.json"), run / "layouts.json")
    retained = read(run / case_id / "summary.json")["geometry"]
    for key in ("model_sha256", "layout_sha256"):
        if layout["metadata"][key] != retained[key]:
            raise RuntimeError(f"Regenerated geometry differs from retained evidence: {key}")
    if layout["metadata"]["summary"] != retained["summary"]:
        raise RuntimeError("Regenerated module/sensor counts or areas differ from retained evidence")
    return layout, metadata


def _at_slice(records, z_mm, kind):
    for record in records:
        extent = abs(record["u"][2]) * record["half_u_mm"] + abs(record["v"][2]) * record["half_v_mm"]
        if kind == "body":
            extent += abs(record["n"][2]) * record["half_w_mm"]
        if abs(record["center_mm"][2] - z_mm) <= extent + SECTION_TOLERANCE_MM:
            points = box_section(record, z_mm) if kind == "body" else sensor_section(record, z_mm)
            if len(points) >= 2:
                yield record, points


def _axes(ax, bounds):
    ax.set(xlim=bounds[:2], ylim=bounds[2:], xlabel="x [mm]", ylabel="y [mm]", aspect="equal")
    ax.grid(alpha=.15, linewidth=.5)
    ax.spines[["top", "right"]].set_visible(False)


def _section_panel(ax, bodies, sensors, patches, z_mm, bounds, normal_colour=None):
    from matplotlib.collections import PolyCollection, LineCollection
    body_sections = list(_at_slice(bodies, z_mm, "body"))
    sensor_sections = list(_at_slice(sensors, z_mm, "sensor"))
    active_sections = list(_at_slice(patches, z_mm, "sensor"))
    if body_sections:
        colours = [normal_colour(b) if normal_colour else "#c1c8cd" for b, _ in body_sections]
        ax.add_collection(PolyCollection([p for _, p in body_sections], facecolors=colours,
                                          edgecolors="#6e7981", linewidths=.45, alpha=.48))
    for sections, physical in ((sensor_sections, True), (active_sections, False)):
        segments = [np.concatenate([p, p[:1]]) if len(p) > 2 else p for _, p in sections]
        colours = ["#172832" if physical else COLOURS[m["subsystem"]] for m, _ in sections]
        ax.add_collection(LineCollection(segments, colors=colours, linewidths=.65 if physical else 1.25,
                                         linestyles="dashed" if physical else "solid"))
    _axes(ax, bounds)
    return dict(z_mm=float(z_mm), trial_bodies=len(body_sections), physical_sensors=len(sensor_sections),
                active_patches=len(active_sections),
                module_ids=[b["module_id"] for b, _ in body_sections],
                sensor_ids=[s["sensor_id"] for s, _ in sensor_sections])


def _adjacent_row_slice(bodies):
    """Select a distinct positive row after the row nearest z=0.

    Group by row before choosing: a peripheral ledge can move a central body
    centre slightly positive without making it an adjacent longitudinal row.
    """
    groups = defaultdict(list)
    for body in bodies:
        groups[body["row"]].append(body["center_mm"][2])
    centres = {row: float(np.median(values)) for row, values in groups.items()}
    central = min(centres, key=lambda row: (abs(centres[row]), row))
    positive = [z for row, z in centres.items() if row != central and z > SECTION_TOLERANCE_MM]
    return min(positive) if positive else centres[central]


def _save(fig, output, name, plt):
    fig.savefig(output / f"{name}.png", dpi=180)
    fig.savefig(output / f"{name}.pdf")
    plt.close(fig)


def barrel_views(layout, sensors, output, plt):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch, Circle
    from matplotlib.colors import Normalize
    from matplotlib.cm import ScalarMappable
    barrels = [layer for layer in layout["layers"] if layer["kind"] == "cylinder"]
    if not barrels:
        raise ValueError("A barrel section requires cylindrical layer definitions")
    bodies = [body for body in layout["bodies"] if body["region"] == "barrel"]
    patches = [patch for patch in layout["modules"] if patch["region"] == "barrel"]
    sensors = [sensor for sensor in sensors if sensor["region"] == "barrel"]
    innermost = min((layer for layer in barrels if layer["subsystem"] == "pixel"), key=lambda layer: layer["r_m"])
    second_z = _adjacent_row_slice([b for b in bodies if b["layer_id"] == innermost["id"]])
    slices = [0., second_z]
    fig, axes = plt.subplots(2, 4, figsize=(17, 9), layout="constrained")
    section_data = []
    for row, z in enumerate(slices):
        for col, sub in enumerate((None, *SUBSYSTEMS)):
            selected = bodies if sub is None else [b for b in bodies if b["subsystem"] == sub]
            selected_sensors = sensors if sub is None else [s for s in sensors if s["subsystem"] == sub]
            selected_patches = patches if sub is None else [p for p in patches if p["subsystem"] == sub]
            extent = max(math.hypot(*b["center_mm"][:2]) + b["half_u_mm"] + b["half_w_mm"] for b in selected) * 1.03
            entry = _section_panel(axes[row, col], selected, selected_sensors, selected_patches,
                                   z, [-extent, extent, -extent, extent])
            entry["scope"] = sub or "total"
            section_data.append(entry)
            axes[row, col].set_title(f"{LABELS[sub] if sub else 'All barrels'} · z = {z:.2f} mm\n"
                                     f"{entry['trial_bodies']} bodies / {entry['physical_sensors']} sensor cuts", fontsize=10)
    fig.suptitle(f"{layout['candidate']} / {layout['variant']} · actual transverse sections\n"
                 "PROTOTYPE · only geometry intersecting the labelled z plane is drawn", fontsize=14)
    fig.legend(handles=[Patch(facecolor="#c1c8cd", edgecolor="#6e7981", label="Trial occupied-body section"),
                        Line2D([], [], color="#172832", linestyle="--", label="Conditional physical-sensor cut"),
                        *[Line2D([], [], color=COLOURS[sub], linewidth=2, label=LABELS[sub] + " active cut") for sub in SUBSYSTEMS]],
               loc="outside lower center", ncol=3, frameon=False, fontsize=9)
    _save(fig, output, "barrel-sections", plt)

    fig, axes = plt.subplots(2, 3, figsize=(13, 9), layout="constrained")
    detail_data = []
    for col, sub in enumerate(SUBSYSTEMS):
        layer = min((layer for layer in barrels if layer["subsystem"] == sub), key=lambda layer: layer["r_m"])
        selected = [b for b in bodies if b["layer_id"] == layer["id"]]
        selected_sensors = [s for s in sensors if s["layer_id"] == layer["id"]]
        selected_patches = [p for p in patches if p["layer_id"] == layer["id"]]
        offsets = [b.get("normal_offset_mm", 0.) for b in selected]
        maximum = max(1., max(map(abs, offsets)))
        norm = Normalize(vmin=-maximum, vmax=maximum)
        cmap = plt.get_cmap("coolwarm")
        radius = layer["r_m"] * 1000.
        width = max(b["half_u_mm"] for b in selected) * 2.7
        bounds = [radius - width, radius + width, -width, width]
        for row, z in enumerate((0., _adjacent_row_slice(selected))):
            entry = _section_panel(axes[row, col], selected, selected_sensors, selected_patches, z, bounds,
                                   normal_colour=lambda b: cmap(norm(b.get("normal_offset_mm", 0.))))
            entry.update(layer_id=layer["id"], scope=sub, displayed_bounds_xy_mm=bounds)
            detail_data.append(entry)
            axes[row, col].add_patch(Circle((0., 0.), radius, facecolor="none", edgecolor="#8b9298",
                                           linestyle=":", linewidth=.8))
            axes[row, col].set_title(f"{LABELS[sub]} · {layer['id']}\nz = {z:.2f} mm", fontsize=11)
        fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=axes[:, col], shrink=.7,
                     label="Body displacement along nominal normal [mm]")
    fig.suptitle(f"{layout['candidate']} / {layout['variant']} · local barrel module sections\n"
                 "True cuts; empty seams remain empty · dotted line: nominal layer radius", fontsize=14)
    fig.legend(handles=[Patch(facecolor="#c1c8cd", edgecolor="#6e7981", label="Trial occupied body"),
                        Line2D([], [], color="#172832", linestyle="--", label="Physical sensor"),
                        Line2D([], [], color=COLOURS['pixel'], linewidth=2, label="Active readout cut (subsystem colour)")],
               loc="outside lower center", ncols=3, frameon=False, fontsize=9)
    _save(fig, output, "barrel-detail", plt)
    return dict(common_slices_mm=slices, section_panels=section_data, detail_panels=detail_data)


def endcap_views(layout, sensors, output, plt):
    from matplotlib.collections import PolyCollection
    from matplotlib.colors import Normalize
    from matplotlib.cm import ScalarMappable
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch, Circle
    fig, axes = plt.subplots(2, 3, figsize=(14, 10), layout="constrained")
    metadata = []
    for column, sub in enumerate(SUBSYSTEMS):
        candidates = [layer for layer in layout["layers"] if layer["kind"] == "disc"
                      and layer["subsystem"] == sub and layer["z_m"] > 0.]
        layer = min(candidates, key=lambda item: item["z_m"])
        nominal_z = layer["z_m"] * 1000.
        bodies = [b for b in layout["bodies"] if b["layer_id"] == layer["id"]]
        outlines = [s for s in sensors if s["layer_id"] == layer["id"]]
        patches = [p for p in layout["modules"] if p["layer_id"] == layer["id"]]
        body_offsets = {b["module_id"]: b["center_mm"][2] - nominal_z for b in bodies}
        maximum = max(1., max(map(abs, body_offsets.values())))
        norm, cmap = Normalize(vmin=-maximum, vmax=maximum), plt.get_cmap("coolwarm")
        body_polygons = [convex_hull(box_vertices(body)[:, :2]) for body in bodies]
        sensor_polygons = [rectangle_vertices(sensor)[:, :2] for sensor in outlines]
        active_polygons = [rectangle_vertices(patch)[:, :2] for patch in patches]
        active_colours = [cmap(norm(body_offsets[p["module_id"]])) for p in patches]
        middle_row = sorted({b["row"] for b in bodies})[len({b["row"] for b in bodies}) // 2]
        reference = min((b for b in bodies if b["row"] == middle_row),
                        key=lambda b: abs(math.atan2(b["center_mm"][1], b["center_mm"][0])))
        c = reference["center_mm"]
        zoom_width = 1.6 * max(reference["half_u_mm"], reference["half_v_mm"])
        full_width = max(np.max(np.abs(p)) for p in body_polygons) * 1.05
        for row, bounds in enumerate(([-full_width, full_width, -full_width, full_width],
                                     [c[0] - zoom_width, c[0] + zoom_width, c[1] - zoom_width, c[1] + zoom_width])):
            ax = axes[row, column]
            ax.add_collection(PolyCollection(body_polygons, facecolors="none", edgecolors="#8b949c", linewidths=.65))
            ax.add_collection(PolyCollection(active_polygons, facecolors=active_colours, edgecolors="none", alpha=.68))
            ax.add_collection(PolyCollection(sensor_polygons, facecolors="none", edgecolors="#26333d",
                                              linewidths=.55, linestyles="dashed"))
            for radius in (layer["r_min_m"] * 1000., layer["r_max_m"] * 1000.):
                ax.add_patch(Circle((0., 0.), radius, facecolor="none", edgecolor="#525d64", linewidth=.7, linestyle=":"))
            _axes(ax, bounds)
            ax.set_title(f"{LABELS[sub]} · {layer['id']}\n"
                         f"{'Full disc assembly' if row == 0 else 'Module-neighbour detail'} · nominal z = {nominal_z:g} mm", fontsize=10)
        fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=axes[:, column], shrink=.75,
                     label="Module-body centre z − nominal disc z [mm]")
        vertices = [box_vertices(b) for b in bodies]
        metadata.append(dict(subsystem=sub, layer_id=layer["id"], nominal_z_mm=nominal_z,
                             body_z_extent_mm=[float(min(p[:, 2].min() for p in vertices)),
                                               float(max(p[:, 2].max() for p in vertices))],
                             body_normal_z_offsets_mm=sorted(set(body_offsets.values())),
                             trial_bodies=len(bodies), physical_sensors=len(outlines), active_patches=len(patches),
                             reference_module_id=reference["module_id"],
                             note="Projection along z of one named nominal disc assembly, including every staggered normal level and both long-strip faces"))
    fig.suptitle(f"{layout['candidate']} / {layout['variant']} · endcap tiling\n"
                 "PROTOTYPE · separate reference disc per subsystem · projections along z, not planar cuts", fontsize=14)
    fig.legend(handles=[Line2D([], [], color="#8b949c", label="Trial occupied-body silhouette"),
                        Line2D([], [], color="#26333d", linestyle="--", label="Conditional physical sensor"),
                        Patch(facecolor=plt.get_cmap("coolwarm")(.8), alpha=.68, label="Active readout islands; colour = body z offset"),
                        Line2D([], [], color="#525d64", linestyle=":", label="Nominal active radial bounds")],
               loc="outside lower center", ncols=2, frameon=False, fontsize=9)
    _save(fig, output, "endcap-reference", plt)
    return metadata


def export(run, case_id, output):
    run, output = Path(run), Path(output)
    layout, retained = load_case(run, case_id)
    output.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault("MPLCONFIGDIR", str(output / ".mpl-cache"))
    os.environ.setdefault("XDG_CACHE_HOME", str(output / ".cache"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sensors = sensor_outlines(layout)
    barrel = barrel_views(layout, sensors, output, plt)
    endcaps = endcap_views(layout, sensors, output, plt)
    provenance = dict(status="PROTOTYPE geometric views; no new detector acceptance", case=case_id,
                      generated_utc=datetime.now(timezone.utc).isoformat(), run=str(run),
                      source_run_revision=retained["project_revision"],
                      export_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                      views_code_sha256=digest(__file__), geometry_code_sha256=digest(HERE / "geometry.py"),
                      retained_run_sha256=digest(run / "run.json"),
                      retained_summary_sha256=digest(run / case_id / "summary.json"),
                      retained_input_sha256={name: digest(run / name) for name in ("sensor_models.json", "layouts.json")},
                      model_sha256=layout["metadata"]["model_sha256"], python=platform.python_version(),
                      numpy=np.__version__, matplotlib=matplotlib.__version__, section_tolerance_mm=SECTION_TOLERANCE_MM,
                      definitions=dict(barrel="Exact z-plane cuts through oriented trial occupied boxes and finite sensor/readout rectangles",
                                       endcap="One positive nominal disc assembly per subsystem; projected silhouettes and all sensor faces, retaining staggered z offsets",
                                       physical_sensor="Conditional guard-inclusive sensor outline, each physical sensor once; not readout-chip silicon",
                                       trial_body="Occupied-box allowance from the same geometry fixture; not fabricated stave or service design"),
                      barrel=barrel, endcaps=endcaps,
                      files={p.name: digest(p) for p in sorted(output.iterdir()) if p.suffix in (".png", ".pdf")})
    (output / "views.json").write_text(json.dumps(provenance, indent=2, allow_nan=False) + "\n")
    return provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = export(args.run, args.case, args.output)
    print(json.dumps(dict(case=result["case"], output=str(args.output), files=list(result["files"]))))


if __name__ == "__main__":
    main()
