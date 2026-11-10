#!/usr/bin/env python3
"""Render PR115 nODD sensor tiles and pad-resolved raw-hit occupancy.

The geometry guide is separate from simulated coverage. No detector or
digitization settings are changed. Preparation needs only Python's stdlib;
plotting additionally needs Matplotlib and NumPy.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PR115_HEAD = "14898df4022363bb038577d170daaf5ed8cdc547"
ECAL = "#cccc00"
SQUARE = "#f2f2bf"
EDGE = "#dede66"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(args):
    expected = json.loads(args.expected.read_text())
    sources = expected["source_sha256"] | expected["layout_report"]["source_sha256"]
    for name, digest in sources.items():
        if sha(ROOT / name) != digest:
            raise ValueError(f"Current geometry source differs: {name}")
        pinned = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{PR115_HEAD}:{name}"])
        if hashlib.sha256(pinned).hexdigest() != digest:
            raise ValueError(f"Geometry source differs from PR115: {name}")
    modules = expected["modules"]
    if (len(modules), sum(m["full"] for m in modules)) != (112, 76):
        raise ValueError("Requires PR115's 76 square + 36 custom sensor wedge")
    report = expected["layout_report"]
    cassettes = json.loads((ROOT / "tools/calorimeter_hardware/cassettes.json").read_text())["ecal"]
    # Display choice: adjacent custom and square modules, not a geometry change.
    zoom_modules = [26, 27]
    output = dict(
        schema_version=1, status="PROTOTYPE geometry guide; not simulated coverage",
        geometry="PR115 tiled nODD Si-W endcap / DES030", pr115_head=PR115_HEAD,
        source_sha256=sources, expected_sha256=sha(args.expected),
        script_sha256=sha(__file__), units="mm",
        carriers=report["config"]["carriers"], layers=report["layers"],
        outer_polygon_mm=report["outer_polygon_mm"],
        inner_apothem_mm=report["config"]["inner_apothem_mm"],
        carrier_face_mm=report["carrier_face_mm"],
        front_mm=report["front_mm"], layer_pitch_mm=report["layer_pitch_mm"],
        pad_pitch_mm=cassettes["pitch_mm"], sensor_blank_mm=cassettes["sensor_outer_mm"],
        square_active_mm=cassettes["sensor_active_mm"],
        modules=[{k: m[k] for k in ("index", "center_mm", "board", "sensor", "active", "full", "family")} for m in modules],
        zoom=dict(module_ids=zoom_modules, window_xy_mm=[318, 424, -80, 49],
                  pads=[dict(module=m["index"], key=g["key"], polygons=g["polygons"],
                             reference_mm=g["reference_mm"], members=g["members"])
                        for m in modules if m["index"] in zoom_modules for g in m["pads"]]),
        description="One +z layer geometry; 16 repeated sectors. Each module is a sensor tile, not a wedge. True custom pad unions retained.",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, separators=(",", ":")) + "\n")
    print(json.dumps({"modules_per_wedge": len(modules), "zoom_pads": len(output["zoom"]["pads"]), "output_bytes": args.output.stat().st_size}))


def absolute(poly, module, angle=0):
    c, s = math.cos(angle), math.sin(angle)
    cx, cy = module["center_mm"]
    return [[c * (x + cx) - s * (y + cy), s * (x + cx) + c * (y + cy)] for x, y in poly]


def plot(args):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    from matplotlib.patches import Patch, Polygon, Rectangle
    import numpy as np

    data = json.loads(args.layout.read_text())
    hits = json.loads(args.hits.read_text()) if args.hits else None
    modules = {m["index"]: m for m in data["modules"]}
    # Per-pad hit bins are aggregated over events and selected fixture layers.
    bins = [] if hits is None else hits["bins"]
    if hits:
        if hits["geometry"]["source_sha256"] != data["source_sha256"]:
            raise ValueError("Hit and layout geometry source hashes differ")
        if sum(b["saved_hit_count"] for b in bins) != hits["saved_hits"]:
            raise ValueError("Raw-hit bin sum differs from declared total")
        if any(b["side"] != 1 or b["sector"] != 0 or b["layer"] not in (0, 1, 2)
               or b["module"] not in modules or not 0 < b["event_count"] <= hits["events"]
               or b["saved_hit_count"] < b["event_count"] for b in bins):
            raise ValueError("Unexpected raw-hit display scope/count")
    counts = {}
    for b in bins:
        key = (b["module"], *b["pad_key"])
        counts[key] = counts.get(key, 0) + b["saved_hit_count"]
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig = plt.figure(figsize=(16, 8.3), facecolor="white")
    gs = fig.add_gridspec(2, 3, width_ratios=[1.05, 1.48, .62], height_ratios=[1.15, 1],
                          left=.06, right=.945, bottom=.16, top=.84, wspace=.27, hspace=.48)
    full = fig.add_subplot(gs[:, 0])
    wedge = fig.add_subplot(gs[0, 1:])
    details = fig.add_subplot(gs[1, 1])
    close = fig.add_subplot(gs[1, 2])
    fig.suptitle("nODD tiled Si–W ECAL endcap — PR #115 baseline", x=.045, ha="left", y=.97, fontsize=20, weight="bold")
    subtitle = "16 wedge carriers × 112 sensor tiles per layer  |  76 square + 36 custom tiles per wedge  |  nominal 5.5 mm pads"
    fig.text(.045, .915, subtitle, fontsize=12)

    sensor_polys, sensor_colors = [], []
    for sector in range(data["carriers"]):
        for m in modules.values():
            sensor_polys.append(absolute(m["sensor"], m, sector * 2 * math.pi / data["carriers"]))
            sensor_colors.append(SQUARE if m["full"] else EDGE)
    full.add_collection(PolyCollection(sensor_polys, facecolors=sensor_colors, edgecolors="#55551b", linewidths=.18))
    full.add_patch(Polygon(data["outer_polygon_mm"], fill=False, edgecolor="#333333", linewidth=.8))
    for sector in range(data["carriers"]):
        a = sector * 2 * math.pi / data["carriers"]
        full.text(2320 * math.cos(a), 2320 * math.sin(a), str(sector), ha="center", va="center", fontsize=8, color="#555555")
    full.set(xlim=(-2500, 2500), ylim=(-2500, 2500), xlabel="global x [mm]", ylabel="global y [mm]", title="A  Full +z face: sensor outlines")
    full.set_aspect("equal")
    full.add_patch(Polygon(data["carrier_face_mm"], fill=False, edgecolor="black", linewidth=1.2))
    full.annotate("sector 0\nilluminated fixture", xy=(1650, 0), xytext=(650, -1350), fontsize=9,
                  arrowprops=dict(arrowstyle="->", color="black"))

    for kind, color, width in (("board", "#a6a6a6", .5), ("sensor", "#55551b", .7)):
        wedge.add_collection(PolyCollection([absolute(m[kind], m) for m in modules.values()],
                                            facecolors="none" if kind == "board" else [SQUARE if m["full"] else EDGE for m in modules.values()],
                                            edgecolors=color, linewidths=width))
    if hits:
        points = np.array([b["position_mm"][:2] for b in bins])
        wedge.scatter(points[:, 0], points[:, 1], s=5, c="#555500", linewidths=0, label="Raw Geant4 hit cell references", zorder=3)
    wedge.add_patch(Rectangle((318, -80), 106, 129, fill=False, edgecolor="black", linewidth=1.2))
    wedge.set(xlim=(90, 2170), ylim=(-430, 430), xlabel="global x [mm]", ylabel="global y [mm]",
              title="B  Sector 0: individual sensor modules and raw hits")
    wedge.set_aspect("equal")
    wedge.annotate("zoom C", xy=(370, -80), xytext=(600, -330), fontsize=10,
                   arrowprops=dict(arrowstyle="->"))

    cmap = LinearSegmentedColormap.from_list("ecal_hit_entries", ["#ffffe5", ECAL, "#666600"])
    maximum = max(counts.values(), default=1)
    norm = Normalize(vmin=0, vmax=maximum)
    pads = data["zoom"]["pads"]
    # Fill unhit pads white; retain polygon fragments of a merged electrode
    # with identical occupancy, and draw its physical union without internal seams.
    for ax in (details, close):
        for index in data["zoom"]["module_ids"]:
            m = modules[index]
            ax.add_patch(Polygon(absolute(m["board"], m), facecolor="#ededed", edgecolor="#888888", linewidth=.8))
            ax.add_patch(Polygon(absolute(m["sensor"], m), facecolor=EDGE if not m["full"] else SQUARE, edgecolor="#333333", linewidth=1))
        for pad in pads:
            m = modules[pad["module"]]
            count = counts.get((pad["module"], *pad["key"]), 0)
            polys = [absolute(p, m) for p in pad["polygons"]]
            ax.add_collection(PolyCollection(polys, facecolors=[cmap(norm(count)) if count else "white"], edgecolors="none"))
            # Cancel shared edges in the constituent polygons of a merged pad.
            segments = {}
            for p in polys:
                for u, v in zip(p, p[1:] + p[:1]):
                    key = tuple(sorted((tuple(round(a, 8) for a in u), tuple(round(a, 8) for a in v))))
                    segments[key] = segments.get(key, 0) + 1
            for (u, v), n in segments.items():
                if n % 2:
                    ax.plot([u[0], v[0]], [u[1], v[1]], color="#7f7f7f", lw=.35)
        ax.set_aspect("equal")
        ax.set(xlabel="global x [mm]", ylabel="global y [mm]")
    details.set(xlim=(318, 424), ylim=(-80, 49), title="C  Custom tile 26 + square tile 27")
    details.text(426, -62, "26\ncustom", va="center", fontsize=9)
    details.text(426, 0, "27\nsquare", va="center", fontsize=9)
    # A custom boundary close-up shows clipped and connected merged pads.
    close.set(xlim=(328, 358), ylim=(-67, -49), title="D  Custom edge pads")
    close.annotate("", xy=(332.5, -51), xytext=(338, -51), arrowprops=dict(arrowstyle="|-|", lw=.8))
    close.text(335.25, -49.5, "5.5 mm", ha="center", fontsize=8)
    close.annotate("Merged edge pad", xy=(340.86, -55.36), xytext=(345, -64.5),
                   ha="center", fontsize=8, arrowprops=dict(arrowstyle="->", lw=.8))
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, ax=close, fraction=.065, pad=.08)
    cbar.set_label("Raw hit entries / pad\n(sum of fixture layers)", fontsize=9)
    cbar.ax.tick_params(labelsize=8)
    fig.legend(handles=[Patch(facecolor=ECAL, edgecolor="#55551b", label="ECAL silicon"),
                        Patch(facecolor=SQUARE, edgecolor="#55551b", label="90 mm square sensor"),
                        Patch(facecolor=EDGE, edgecolor="#55551b", label="Custom edge sensor"),
                        Patch(facecolor="white", edgecolor="#7f7f7f", label="Unhit active pad")],
               loc="lower left", bbox_to_anchor=(.038, .065), ncol=4, frameon=False, fontsize=10)
    fixture = "Layout guide only; awaiting raw-hit fixture."
    if hits:
        fixture = f'{hits["events"]} simulated 10 GeV muons; +z sector 0, layers 0–2; stratified broad / tile 26 / tile 27 display illumination.'
    fig.text(.045, .043, fixture, fontsize=9)
    fig.text(.045, .017, "PROTOTYPE • Geometry outlines show all tiles; hits cover only the stated display fixture. No digitization or Marlin study. Unhit ≠ inactive.", fontsize=9, color="#555555")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160, metadata={"Software": "Matplotlib; tiled_endcap_xy.py"})
    plt.close(fig)
    print(json.dumps({"output": str(args.output), "sha256": sha(args.output), "hit_bins": len(bins)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--expected", type=Path, required=True)
    prep.add_argument("--output", type=Path, required=True)
    draw = commands.add_parser("plot")
    draw.add_argument("--layout", type=Path, required=True)
    draw.add_argument("--hits", type=Path)
    draw.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    (prepare if args.command == "prepare" else plot)(args)


if __name__ == "__main__":
    main()
