#!/usr/bin/env python3
"""Draw DES-011 prototype evidence from saved layouts without regenerating them."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

import numpy as np

if __package__:
    from .services_geometry import body_envelope
    from .views import (box_section, box_vertices, convex_hull, rectangle_vertices,
                        sensor_outlines, sensor_section)
else:
    from services_geometry import body_envelope
    from views import (box_section, box_vertices, convex_hull, rectangle_vertices,
                       sensor_outlines, sensor_section)


HERE = Path(__file__).resolve().parent
SUBSYSTEMS = ("pixel", "short_strip", "long_strip")
LABELS = dict(pixel="Pixels", short_strip="Short strips", long_strip="Long-strip pairs", total="Total")
COLOURS = dict(pixel="#0072b2", short_strip="#d89000", long_strip="#009e73", shared="#9c5799")
MODES = ("straight", "positive", "negative")
MODE_COLOURS = ("#343a40", "#0072b2", "#d55e00")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as stream:
            return json.load(stream)
    return json.loads(path.read_text())


def _save(fig, output, name, plt):
    for extension in ("png", "pdf"):
        fig.savefig(output / f"{name}.{extension}", dpi=170, bbox_inches="tight")
    plt.close(fig)


def _bypass(route):
    return route.get("role") in ("last_disc_bypass", "last_disc_bypass_turn")


def _positive(record):
    return record["z_max_mm"] > 0.


def _rz_groups(layout):
    # All-phi occupied envelopes, explicitly not a single meridional plane cut.
    groups = defaultdict(list)
    extents = {}
    for body in layout["bodies"]:
        extent = body_envelope(body)
        extents[body["module_id"]] = extent
        if _positive(extent):
            groups[body["layer_id"], body.get("row"), body.get("level")].append(extent)
    return [dict(r_min_mm=min(e["r_min_mm"] for e in values),
                 r_max_mm=max(e["r_max_mm"] for e in values),
                 z_min_mm=min(e["z_min_mm"] for e in values),
                 z_max_mm=max(e["z_max_mm"] for e in values))
            for values in groups.values()], extents


def _rz_draw(ax, groups, supports, routes, host, vessel):
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Rectangle

    def rectangle(record):
        z0 = max(0., record["z_min_mm"])
        return Rectangle((z0, record["r_min_mm"]), record["z_max_mm"]-z0,
                         record["r_max_mm"]-record["r_min_mm"])

    for records, colour, alpha in ((groups, "#666d75", .75), (supports, "#7ebdc1", .6)):
        ax.add_collection(PatchCollection([rectangle(r) for r in records if _positive(r)],
                                         facecolors=colour, edgecolors="none", alpha=alpha))
    for route in routes:
        if not _positive(route):
            continue
        patch = rectangle(route)
        colour = COLOURS.get(route["subsystem"], COLOURS["shared"])
        patch.set(facecolor=colour, edgecolor=colour, alpha=.27,
                  linewidth=1.1 if _bypass(route) else .45,
                  linestyle="--" if _bypass(route) else "-",
                  hatch="///" if _bypass(route) else None)
        ax.add_patch(patch)
    if host:
        ax.add_patch(Rectangle((0., host["r_min_m"]*1000.), host["abs_z_max_m"]*1000.,
                               (host["r_max_m"]-host["r_min_m"])*1000., fill=False,
                               edgecolor="#24282c", linestyle=":", linewidth=.9))
    if vessel:
        ax.add_patch(rectangle(vessel))
        ax.patches[-1].set(facecolor="#a990a5", edgecolor="#6b526c", alpha=.18)
    ax.set(xlabel="z [mm]", ylabel="r [mm]", aspect="equal")
    ax.grid(alpha=.13)


def routing_views(case_id, layout, services, vessel, output, plt):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    groups, extents = _rz_groups(layout)
    supports, routes = services["supports"], services["routes"]
    positive = [r for r in [*groups, *supports, *routes] if _positive(r)]
    if not positive:
        raise ValueError("No positive-side occupied geometry to draw")
    host = layout.get("metadata", {}).get("host")
    limits = [max(r["z_max_mm"] for r in positive), max(r["r_max_mm"] for r in positive)]
    if host:
        limits = [max(limits[0], host["abs_z_max_m"]*1000.), max(limits[1], host["r_max_m"]*1000.)]
    if vessel:
        limits = [max(limits[0], vessel["z_max_mm"]), max(limits[1], vessel["r_max_mm"])]
    fig = plt.figure(figsize=(16, 10), layout="constrained")
    grid = fig.add_gridspec(2, 3, height_ratios=(1.25, 1.))
    full = fig.add_subplot(grid[0, :])
    _rz_draw(full, groups, supports, routes, host, vessel)
    full.set(xlim=(0., limits[0]*1.02), ylim=(0., limits[1]*1.02),
             title="Positive-side occupied envelopes over all azimuths · bands reserve space, not solid material")
    bypasses = [r for r in routes if _positive(r) and _bypass(r)]
    if bypasses:
        route = max(bypasses, key=lambda r: (r["z_max_mm"]-r["z_min_mm"])*(r["r_max_mm"]-r["r_min_mm"]))
        full.annotate("Final-disc downstream bypass", xy=((route["z_min_mm"]+route["z_max_mm"])/2.,
                                                          (route["r_min_mm"]+route["r_max_mm"])/2.),
                      xytext=(-175, 30), textcoords="offset points", fontsize=9,
                      arrowprops=dict(arrowstyle="->", color="#694670"), color="#694670")
    metadata = []
    for column, sub in enumerate(SUBSYSTEMS):
        ax = fig.add_subplot(grid[1, column])
        barrel = [b for b in layout["bodies"] if b["subsystem"] == sub and b["region"] == "barrel"]
        discs = [l for l in layout["layers"] if l["subsystem"] == sub and l["kind"] in ("disc", "disk") and l["z_m"] > 0]
        if not barrel or not discs:
            ax.text(.5, .5, "No barrel/positive disc pair", ha="center", transform=ax.transAxes)
            ax.set_axis_off()
            continue
        first = min(discs, key=lambda l: l["z_m"])
        disc = [b for b in layout["bodies"] if b["layer_id"] == first["id"]]
        barrel_ids = {b["layer_id"] for b in barrel}
        barrel_extents = [extents[b["module_id"]] for b in barrel] + [s for s in supports if s["layer_id"] in barrel_ids]
        disc_extents = [extents[b["module_id"]] for b in disc] + [s for s in supports if s["layer_id"] == first["id"]]
        if not disc_extents:
            raise ValueError(f"First disc {first['id']} has no occupied geometry")
        barrel_end = max(e["z_max_mm"] for e in barrel_extents)
        disc_start = min(e["z_min_mm"] for e in disc_extents)
        disc_end = max(e["z_max_mm"] for e in disc_extents)
        padding = max(30., .4*(disc_end-barrel_end))
        r0 = min(e["r_min_mm"] for e in [*barrel_extents, *disc_extents])
        r1 = max(e["r_max_mm"] for e in [*barrel_extents, *disc_extents])
        _rz_draw(ax, groups, supports, routes, host, vessel)
        ax.set(xlim=(max(0., barrel_end-padding), disc_end+padding),
               ylim=(max(0., r0-20.), r1+20.), aspect="auto",
               title=f"{LABELS[sub]} · barrel / first disc\nOccupied z separation: {disc_start-barrel_end:.2f} mm")
        # Zoom panels show numerical scales but use independent axis aspect ratios.
        ax.annotate("", xy=(disc_start, (r0+r1)/2.), xytext=(barrel_end, (r0+r1)/2.),
                    arrowprops=dict(arrowstyle="<->", color="#aa3d44", linewidth=1))
        metadata.append(dict(subsystem=sub, first_disc_id=first["id"], barrel_occupied_end_mm=barrel_end,
                             first_disc_occupied_start_mm=disc_start, separation_mm=disc_start-barrel_end,
                             bounds_zr_mm=[*ax.get_xlim(), *ax.get_ylim()]))
    fig.suptitle(f"{case_id}\nDES-011 routing mockup · PROTOTYPE / no mechanical sign-off", fontsize=14)
    handles = [Patch(facecolor="#666d75", label="Occupied body envelope"),
               Patch(facecolor="#7ebdc1", label="Support reservation")]
    handles += [Patch(facecolor=c, alpha=.4, label=s.replace("_", " ")+" services") for s, c in COLOURS.items()]
    handles += [Patch(facecolor="none", hatch="///", linestyle="--", label="Final-disc bypass")]
    if host:
        handles.append(Line2D([], [], color="#24282c", linestyle=":", label="Tracker host boundary"))
    if vessel:
        handles.append(Patch(facecolor="#a990a5", alpha=.3, label="Vessel reservation"))
    fig.legend(handles=handles, loc="outside lower center", ncol=4, fontsize=9)
    _save(fig, output, "routing-rz", plt)
    return dict(barrel_first_disc=metadata, bypass_route_ids=[r["id"] for r in bypasses],
                note="Full view has equal scale; zooms have independently labelled axis scales. No reflection/symmetry assumption is made.")


def _annuli(ax, records, z0, z1, *, support=False):
    from matplotlib.patches import Wedge
    visible = []
    for record in records:
        if record["z_min_mm"] > z1 or record["z_max_mm"] < z0:
            continue
        colour = "#7ebdc1" if support else COLOURS.get(record["subsystem"], COLOURS["shared"])
        ax.add_patch(Wedge((0., 0.), record["r_max_mm"], 0., 360.,
                           width=record["r_max_mm"]-record["r_min_mm"], facecolor=colour,
                           edgecolor=colour, linewidth=.35, alpha=.25,
                           hatch="///" if _bypass(record) else None))
        visible.append(record["id"])
    return visible


def transverse_views(case_id, layout, services, output, plt):
    from matplotlib.collections import LineCollection, PolyCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    fig, axes = plt.subplots(3, 3, figsize=(15, 15), layout="constrained")
    sensors = sensor_outlines(layout)
    metadata = []
    for col, sub in enumerate(SUBSYSTEMS):
        bodies = [b for b in layout["bodies"] if b["subsystem"] == sub]
        outlines = [s for s in sensors if s["subsystem"] == sub]
        patches = [p for p in layout["modules"] if p["subsystem"] == sub]
        layers = [l for l in layout["layers"] if l["subsystem"] == sub]
        barrels = [l for l in layers if l["kind"] == "cylinder"]
        discs = sorted((l for l in layers if l["kind"] in ("disc", "disk") and l["z_m"] > 0), key=lambda l: l["z_m"])
        for row, ax in enumerate(axes[:, col]):
            if not barrels or not discs:
                ax.text(.5, .5, "No representative layer", ha="center", transform=ax.transAxes)
                ax.set_axis_off()
                continue
            if row == 0:
                chosen = [b for b in bodies if b["region"] == "barrel"]
                # A z=0 slice can sit in all even-row sensor seams. Choose the
                # nearest-positive row centre showing the most barrel layers,
                # without projecting modules that miss that actual plane.
                choices = [min((b for b in chosen if b["layer_id"] == layer["id"] and b["center_mm"][2] >= 0.),
                               key=lambda b: b["center_mm"][2]) for layer in barrels]
                def visible_layers(reference):
                    z = reference["center_mm"][2]
                    return len({b["layer_id"] for b in chosen if abs(b["center_mm"][2]-z) <=
                                abs(b["u"][2])*b["half_u_mm"] + abs(b["v"][2])*b["half_v_mm"] +
                                abs(b["n"][2])*b["half_w_mm"]})
                reference = max(choices, key=lambda b: (visible_layers(b), -b["center_mm"][2]))
                z0 = z1 = reference["center_mm"][2]
                selected_sensors = [s for s in outlines if s["region"] == "barrel"]
                selected_patches = [p for p in patches if p["region"] == "barrel"]
                body_polygons = [points for b in chosen if len(points := box_section(b, z0)) >= 3]
                sensor_polygons = [points for s in selected_sensors if len(points := sensor_section(s, z0)) >= 2]
                active_polygons = [points for p in selected_patches if len(points := sensor_section(p, z0)) >= 2]
                title = f"{LABELS[sub]} · actual barrel cut\nz = {z0:.2f} mm"
                layer_id = reference["layer_id"]
            else:
                layer = discs[0] if row == 1 else discs[-1]
                layer_id = layer["id"]
                chosen = [b for b in bodies if b["layer_id"] == layer_id]
                if not chosen:
                    raise ValueError(f"Cannot project empty endcap {layer_id}")
                vertices = [box_vertices(b) for b in chosen]
                z0, z1 = min(v[:, 2].min() for v in vertices), max(v[:, 2].max() for v in vertices)
                body_polygons = [convex_hull(v[:, :2]) for v in vertices]
                sensor_polygons = [rectangle_vertices(s)[:, :2] for s in outlines if s["layer_id"] == layer_id]
                active_polygons = [rectangle_vertices(p)[:, :2] for p in patches if p["layer_id"] == layer_id]
                title = f"{LABELS[sub]} · {'first' if row == 1 else 'final'} disc projection\nNominal z = {layer['z_m']*1000.:g} mm"
            route_ids = _annuli(ax, services["routes"], z0, z1)
            support_ids = _annuli(ax, services["supports"], z0, z1, support=True)
            ax.add_collection(PolyCollection(body_polygons, facecolors="#b7bec4", edgecolors="#626c74", linewidths=.35, alpha=.6))
            for polygons, colour, style, width in ((sensor_polygons, "#202d37", "dashed", .4),
                                                    (active_polygons, COLOURS[sub], "solid", .6)):
                ax.add_collection(LineCollection([np.concatenate((p, p[:1])) if len(p) > 2 else p for p in polygons],
                                                colors=colour, linestyles=style, linewidths=width))
            extent = max(np.max(np.abs(box_vertices(b)[:, :2])) for b in chosen)*1.10
            own_routes = [r["r_max_mm"] for r in services["routes"] if r["id"] in route_ids and r["subsystem"] == sub]
            extent = max([extent, *own_routes]) * 1.03
            ax.set(xlim=(-extent, extent), ylim=(-extent, extent), aspect="equal",
                   xlabel="x [mm]", ylabel="y [mm]", title=title)
            ax.grid(alpha=.12)
            metadata.append(dict(subsystem=sub, kind="barrel_section" if row == 0 else "endcap_projection",
                                 reference_layer_id=layer_id, z_extent_mm=[float(z0), float(z1)],
                                 body_polygons=len(body_polygons), physical_sensor_polygons=len(sensor_polygons),
                                 active_polygons=len(active_polygons), visible_route_ids=route_ids,
                                 visible_support_ids=support_ids))
    fig.suptitle(f"{case_id}\nPROTOTYPE · barrel planes are true cuts; discs project the complete staggered assembly\n"
                 "Annuli shown only where their z interval intersects the labelled cut/assembly extent", fontsize=13)
    fig.legend(handles=[Patch(facecolor="#b7bec4", label="Occupied body"),
                        Line2D([], [], color="#202d37", linestyle="--", label="Physical sensor"),
                        *[Line2D([], [], color=COLOURS[s], label=LABELS[s]+" active patch") for s in SUBSYSTEMS],
                        Patch(facecolor="#7ebdc1", alpha=.4, label="Support/service annuli (colour by owner)")],
               loc="outside lower center", ncol=3, fontsize=9)
    _save(fig, output, "transverse-sections", plt)
    return metadata


def comparison_views(case_ids, summaries, baseline, output, plt, validation=None):
    scopes = ("total", *SUBSYSTEMS)
    fig, axes = plt.subplots(5, 4, figsize=(17, 17), layout="constrained")
    labels, selected_count = [], 0
    for cid in case_ids:
        if cid == baseline:
            labels.append("B")
        else:
            selected_count += 1
            labels.append(f"S{selected_count}")
    definitions = ["Mean reached stations", "Fixed-reference missing stations [%]",
                   "p95 track maximum inter-station gap [mm]", "p95 origin/host-anchored maximum gap [mm]",
                   "Summed silicon area [m²]"]
    for col, scope in enumerate(scopes):
        for row in range(4):
            ax = axes[row, col]
            finite_values = []
            for mode, colour in zip(MODES, MODE_COLOURS):
                values = []
                for summary in summaries:
                    source = summary["coverage" if row == 0 else "spacing"][mode]
                    group = source["total"] if scope == "total" else source["per_subdetector"].get(scope)
                    if group is None:
                        value = None
                    elif row == 0:
                        value = group["stations"]["mean"]
                    elif row == 1:
                        value = group["missing_ideal_station_fraction"]
                        value = 100.*value if value is not None else None
                    else:
                        field = "max_inter_hit_gap_mm" if row == 2 else "max_boundary_gap_mm"
                        value = group["station_spacing"][field]["p95"]
                    values.append(np.nan if value is None else value)
                    if value is not None:
                        finite_values.append(value)
                ax.plot(range(len(case_ids)), values, marker="o", markersize=4, linewidth=1,
                        color=colour, label=mode)
            ax.set_xticks(range(len(case_ids)), labels)
            ax.grid(alpha=.18)
            ax.ticklabel_format(axis="y", style="plain", useOffset=False)
            if finite_values:
                low, high = min(finite_values), max(finite_values)
                # Display windows only: prevent root-level floating noise from
                # masquerading as a visible physical gap improvement.
                minimum_span = .1 if row < 2 else max(1., .01*(low+high)/2.)
                if high-low < minimum_span:
                    centre = (low+high)/2.
                    ax.set_ylim(max(0., centre-.55*minimum_span), centre+.55*minimum_span)
                elif ax.get_ylim()[0] < 0:
                    ax.set_ylim(bottom=0.)
            if row == 0:
                ax.set_title(LABELS[scope])
            if col == 0:
                ax.set_ylabel(definitions[row])
        ax = axes[4, col]
        x = np.arange(len(case_ids))
        for offset, key, colour, label in ((-.18, "sensor_area_m2", "#6b7785", "Physical silicon"),
                                         (.18, "active_area_m2", "#65a498", "Summed active silicon")):
            values = [s["summary"].get(scope, {}).get(key, np.nan) for s in summaries]
            ax.bar(x+offset, values, width=.36, color=colour, label=label)
        ax.set_xticks(x, labels)
        ax.grid(axis="y", alpha=.18)
        if col == 0:
            ax.set_ylabel(definitions[4])
    axes[0, 0].legend(fontsize=8)
    axes[4, 0].legend(fontsize=8)
    mapping = "\n".join(f"{short}: {cid}" + (" [DENSE COVERAGE FAIL]" if (validation or {}).get(cid) is False else "")
                        for short, cid in zip(labels, case_ids))
    fig.suptitle("DES-011 sampled layout comparison · PROTOTYPE\n"
                 "Coverage first; a spacing statistic alone is not an optimization score\n"
                 "Silicon areas sum sensors; projected overlaps count repeatedly, not as unique coverage\n"+mapping, fontsize=12)
    _save(fig, output, "comparison", plt)
    return dict(labels=dict(zip(labels, case_ids)), modes=list(MODES), scopes=list(scopes),
                missing_reference="Frozen original ideal-layer denominator from spacing report",
                area_definition="Sum over physical sensors/active islands; geometric overlaps count repeatedly, not unique covered area",
                gap_weighting="p95 across per-track maximum 3D arc gaps; null tracks excluded only from undefined inter-hit statistic")


def export(run, output, cases=None):
    run, output = Path(run), Path(output)
    study_path = run / "study.json"
    if not study_path.exists():
        study_path = run / "study.json.gz"
    study = read(study_path)
    baseline = study["baseline"]
    case_ids = list(dict.fromkeys(cases if cases is not None else [baseline, *study["selected"]]))
    if not case_ids or any(not isinstance(cid, str) or Path(cid).name != cid or cid in (".", "..") for cid in case_ids):
        raise ValueError("Cases must be nonempty simple case directory names")
    consumed = [study_path]
    summaries = []
    for cid in case_ids:
        path = run / "cases" / cid / "summary.json"
        summary = read(path)
        if summary["id"] != cid:
            raise ValueError("Case summary ID does not match its directory")
        summaries.append(summary)
        consumed.extend((path, path.with_name("layout.json.gz")))
    vessel = None
    if (envelopes_path := run / "envelopes.json").exists():
        envelopes = read(envelopes_path)
        if envelopes["units"] != "m":
            raise ValueError("Retained global envelopes must have explicit metre units")
        magnets = [r for r in envelopes["regions"] if r["id"] == "magnet"]
        if magnets:
            vessel = {key.removesuffix("_m")+"_mm": magnets[0][key]*1000.
                      for key in ("r_min_m", "r_max_m", "z_min_m", "z_max_m")}
        consumed.append(envelopes_path)
    input_hashes = {str(path.relative_to(run)): digest(path) for path in consumed}
    manifest_path = run / "artifacts.json"
    manifest_hash = None
    if manifest_path.exists():
        retained = read(manifest_path)["files"]
        for name, value in input_hashes.items():
            if retained.get(name) != value:
                raise RuntimeError("Retained artifact missing or hash mismatch: "+name)
        manifest_hash = digest(manifest_path)
    helper_hashes = {name: digest(HERE/name) for name in ("views.py", "geometry.py", "services_geometry.py")}
    for name, value in helper_hashes.items():
        expected = study.get("code_sha256", {}).get(name)
        if expected is not None and expected != value:
            raise RuntimeError("Geometry drawing helper differs from retained run: "+name)
    renderer_hash = digest(Path(__file__))
    output.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault("MPLCONFIGDIR", str(output / ".matplotlib-cache"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    details = {}
    for cid, summary in zip(case_ids, summaries):
        case_output = output / cid
        case_output.mkdir()
        with gzip.open(run / "cases" / cid / "layout.json.gz", "rt") as stream:
            layout = json.load(stream)
        details[cid] = dict(routing=routing_views(cid, layout, summary["services"], vessel, case_output, plt),
                            transverse=transverse_views(cid, layout, summary["services"], case_output, plt))
    comparison = comparison_views(case_ids, summaries, baseline, output, plt,
                                  study.get("holdout_coverage_passed"))
    if any(digest(run/name) != value for name, value in input_hashes.items()):
        raise RuntimeError("Retained inputs changed during rendering")
    if digest(Path(__file__)) != renderer_hash or any(digest(HERE/name) != value for name, value in helper_hashes.items()):
        raise RuntimeError("Renderer/helper source changed during rendering")
    artifacts = {str(p.relative_to(output)): digest(p) for p in sorted(output.rglob("*")) if p.suffix in (".png", ".pdf")}
    result = dict(schema_version=1, status="PROTOTYPE views; no new geometry or sign-off",
                  generated_utc=datetime.now(timezone.utc).isoformat(), run=str(run),
                  source_run_commit=study.get("source_commit"),
                  baseline=baseline, cases=case_ids, command=[sys.executable, *sys.argv],
                  input_sha256=input_hashes, retained_artifact_manifest_sha256=manifest_hash,
                  input_verification="matched retained manifest" if manifest_hash else "hashes captured; no retained manifest supplied",
                  renderer_sha256=renderer_hash, helper_sha256=helper_hashes,
                  python=platform.python_version(), numpy=np.__version__, matplotlib=matplotlib.__version__,
                  definitions=dict(body="Actual saved oriented boxes; r-z combines occupied extrema over azimuth",
                                   support="Saved finite annular keep-out, not structural material",
                                   service="Saved finite constant corridor/collector/bypass envelopes; no individual cable placement",
                                   xy="Exact barrel plane sections; full first/final positive-disc projections including stereo faces",
                                   vessel="Shown only if retained envelopes.json supplies the magnet reservation"),
                  details=details, comparison=comparison, files=artifacts)
    (output / "views.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", help="Case IDs; default is baseline plus every selected case")
    args = parser.parse_args()
    result = export(args.run, args.output, args.cases)
    print(json.dumps(dict(cases=result["cases"], artifacts=len(result["files"]), output=str(args.output))))


if __name__ == "__main__":
    main()
