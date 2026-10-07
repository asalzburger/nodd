#!/usr/bin/env python3
"""DES-020 longitudinal packing, measured from both exported compact models.

Exports go under ignored build/. Existing layouts/native evidence are read only.
The JSON report uses the standard library; drawing additionally needs Matplotlib.
"""
import argparse
from collections import defaultdict
import gzip
import json
import math
from pathlib import Path
import platform
import subprocess
import xml.etree.ElementTree as ET

from export import export
from model import ROOT, build, load, sha

HERE = Path(__file__).resolve().parent
CASES = (("tangential", "inputs.json", "layout.json.gz"),
         ("phi_tilted", "inputs-phi-tilted.json", "phi-tilted/layout.json.gz"))


def dim(node, key):
    return float(node.get(key).removesuffix("*mm"))


def interval(node, offset=0):
    center = dim(node, "v") + offset
    return [center - dim(node, "sy") / 2, center + dim(node, "sy") / 2]


def bounds(items):
    items = list(items)
    return [min(x[0] for x in items), max(x[1] for x in items)]


def union_length(items):
    merged = []
    for lo, hi in sorted(items):
        if not merged or lo > merged[-1][1]:
            merged.append([lo, hi])
        else:
            merged[-1][1] = max(merged[-1][1], hi)
    return sum(hi - lo for lo, hi in merged)


def measure(input_path, frozen_path, output):
    c = load(input_path)
    layout = build(c)
    frozen = json.loads(gzip.decompress(frozen_path.read_bytes()))
    # The new drawing cannot silently describe different rows or an axial tilt.
    for actual, old in zip(layout["modules"], frozen["modules"], strict=True):
        for key in ("name", "row", "layer", "stave", "center_mm", "v", "lift_mm", "half_v_mm"):
            if key == "center_mm":
                if actual[key][2] != old[key][2]:
                    raise ValueError("Frozen axial placement changed: " + actual["name"])
            elif actual[key] != old[key]:
                raise ValueError("Frozen axial contract changed: " + actual["name"])
    # The exporter, not a second hardcoded geometry, supplies component bounds.
    export(c, output, input_path)
    tree = ET.parse(output / "short-strip-barrel.xml")
    staves = tree.findall(".//stave")
    first = staves[0]
    rows = []
    for module in first.findall("module"):
        z, lift = dim(module, "z"), dim(module, "lift")
        pieces = module.findall("piece")
        active = next(p for p in pieces if p.get("role") == "sensitive")
        rows.append(dict(row=int(module.get("id")), center_z_mm=z, lift_mm=lift,
                         active_z_mm=interval(active, z),
                         sensor_z_mm=bounds(interval(p, z) for p in pieces
                                            if p.get("role") in ("sensitive", "guard")),
                         front_body_z_mm=bounds(interval(p, z) for p in pieces),
                         front_stack_w_mm=bounds([dim(p, "w") + lift - dim(p, "sz") / 2,
                                                 dim(p, "w") + lift + dim(p, "sz") / 2]
                                                for p in pieces)))
    signature = [(r["center_z_mm"], r["lift_mm"]) for r in rows]
    for stave in staves:
        if [(dim(m, "z"), dim(m, "lift")) for m in stave.findall("module")] != signature:
            raise ValueError("Nonuniform axial schedule: " + stave.get("name"))
    pieces = first.findall("piece")
    zones = defaultdict(list)
    for p in pieces:
        if p.get("kind") in ("box", "shoe"):
            zones[p.get("role")].append(interval(p))
        elif p.get("role") == "cooling_tube":
            zones["cooling_straight"].append([dim(p, "v") - dim(p, "length") / 2,
                                              dim(p, "v") + dim(p, "length") / 2])
        elif p.get("role") == "cooling_bend":
            # Exported half torus lies in local U,V. Verify its inward return.
            start = float(p.get("start").removesuffix("*rad"))
            angle = float(p.get("angle").removesuffix("*rad"))
            if not math.isclose(angle, math.pi) or not any(math.isclose(start, a) for a in (0, math.pi)):
                raise ValueError("Unsupported cooling bend arc")
            center, reach = dim(p, "v"), dim(p, "major") + dim(p, "rmax")
            zones["cooling_return"].append([center - reach, center + dim(p, "rmax")]
                                           if center > 0 else
                                           [center - dim(p, "rmax"), center + reach])
    pitch = rows[1]["center_z_mm"] - rows[0]["center_z_mm"]
    overlaps = [a["active_z_mm"][1] - b["active_z_mm"][0] for a, b in zip(rows, rows[1:])]
    body_overlaps = [a["front_body_z_mm"][1] - b["front_body_z_mm"][0]
                     for a, b in zip(rows, rows[1:])]
    pickup_length = dim(next(p for p in pieces if p.get("role") == "thermal_pickup"), "sy")
    active = bounds(r["active_z_mm"] for r in rows)
    front = bounds(r["front_body_z_mm"] for r in rows)
    support = bounds(zones["support"])
    board = next(x for x in zones["end_board"] if x[0] > 0)
    collector = c["collector_mm"][2:]
    # Rings are layer-level global cylinders: compact w is global z here.
    # Stave/module local v is global z only after the stave frame rotation.
    ring_intervals = [[dim(p, "w") - dim(p, "length") / 2,
                       dim(p, "w") + dim(p, "length") / 2]
                      for p in tree.findall(".//piece[@role='ring']")]
    half = len(rows) // 2
    low = next(r for r in rows if r["lift_mm"] == 0)
    high = next(r for r in rows if r["lift_mm"] > 0)
    active_intervals = [r["active_z_mm"] for r in rows]
    summed = sum(hi - lo for lo, hi in active_intervals)
    union = union_length(active_intervals)
    positive_return = next(x for x in zones["cooling_return"] if x[0] > 0)
    negative_return = next(x for x in zones["cooling_return"] if x[1] < 0)
    result = dict(staves=len(staves), modules=len(layout["modules"]), rows_per_stave=len(rows),
                  phi_tilt_deg=c.get("phi_tilt_deg", 0), axial_coordinate="V = global z",
                  row_pitch_mm=pitch, rows=rows,
                  adjacent_active_overlap_mm=[min(overlaps), max(overlaps)],
                  adjacent_front_body_overlap_mm=[min(body_overlaps), max(body_overlaps)],
                  active_span_mm=active, sensor_span_mm=bounds(r["sensor_z_mm"] for r in rows),
                  front_body_span_mm=front,
                  summed_active_length_mm=summed, active_union_length_mm=union,
                  redundant_projected_length_mm=summed - union,
                  redundancy_fraction_of_summed_length=(summed - union) / summed,
                  same_height_front_body_gap_mm=rows[2]["front_body_z_mm"][0] - rows[0]["front_body_z_mm"][1],
                  adjacent_front_stack_normal_gap_mm=high["front_stack_w_mm"][0] - low["front_stack_w_mm"][1],
                  pickup_length_mm=pickup_length,
                  pickup_neighbour_body_gap_mm=pitch - (rows[0]["front_body_z_mm"][1] -
                                                      rows[0]["front_body_z_mm"][0] + pickup_length) / 2,
                  central_active_overlap_z_mm=[rows[half]["active_z_mm"][0], rows[half-1]["active_z_mm"][1]],
                  half_stave_modules=half, support_span_mm=support,
                  bearing_centres_z_mm=sorted(set(dim(p, "w") for p in tree.findall(".//piece[@role='ring']"))),
                  bearing_intervals_z_mm=sorted(set(tuple(x) for x in ring_intervals)),
                  cooling_straight_z_mm=sorted(set(tuple(x) for x in zones["cooling_straight"])),
                  cooling_return_z_mm=sorted(zones["cooling_return"]),
                  cooling_central_envelope_gap_mm=positive_return[0] - negative_return[1],
                  end_board_positive_z_mm=board, collector_positive_z_mm=collector,
                  trunk_positive_z_mm=c["trunk_mm"][2:],
                  positive_end_gaps_mm=dict(active_to_support=support[1]-active[1],
                                           front_body_to_support=support[1]-front[1],
                                           support_to_board=board[0]-support[1],
                                           front_body_to_board=board[0]-front[1],
                                           board_to_collector=collector[0]-board[1]),
                  original_strip_disc_datum_mm=1295.5,
                  original_disc_inside_collector_mm=collector[1]-1295.5,
                  source_sha256={str(p.relative_to(ROOT)): sha(p) for p in
                                 (input_path, frozen_path, HERE/"model.py", HERE/"export.py",
                                  ROOT/"prototypes/short_strip_barrel/ShortStripBarrel.cpp")},
                  exported_compact_sha256=sha(output/"short-strip-barrel.xml"))
    return result, first


def draw(report, staves, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 10,
                         "svg.fonttype": "none", "svg.hashsalt": "DES-020-z-packing",
                         "axes.spines.top": False, "axes.spines.right": False})
    sensor, body, support, pickup, cooling, service = "#246aa0", "#727b87", "#4b6354", "#929188", "#b75479", "#c89945"
    fig = plt.figure(figsize=(15, 11.8), layout="constrained")
    grid = fig.add_gridspec(3, 2, height_ratios=[1, 1, 2.1])
    r = report["prototypes"]["tangential"]
    for i, key in enumerate(("tangential", "phi_tilted")):
        ax = fig.add_subplot(grid[i, :])
        q = report["prototypes"][key]
        ax.plot(q["support_span_mm"], [-1.3, -1.3], color=support, lw=1)
        for row in q["rows"]:
            lo, hi = row["front_body_z_mm"]
            ax.add_patch(Rectangle((lo, row["lift_mm"]-.12), hi-lo, .24,
                                   facecolor="none", edgecolor=body, lw=.65))
            lo, hi = row["active_z_mm"]
            ax.add_patch(Rectangle((lo, row["lift_mm"]-.1), hi-lo, .2,
                                   facecolor=sensor, edgecolor="none"))
        for z in q["bearing_centres_z_mm"]:
            ax.plot(z, .035, "^", transform=ax.get_xaxis_transform(), color=support, markersize=5)
        ax.axvline(0, color="#888888", ls=":", lw=.7)
        ax.text(0, 2.25, "28 rows / stave • 96 mm active • 85.333 mm pitch • 1.5 mm alternating lift", ha="center")
        ax.text(0, -.95, "cold-plate front face; bearing markers indicate z only", ha="center", va="bottom", fontsize=8, color=support)
        label = "(a) Tangential two-lane control" if i == 0 else "(b) Same-radius +15° phi-tilted alternative"
        ax.set(title=f"{label} — {q['staves']} staves / {q['modules']:,} modules; identical longitudinal schedule",
               xlim=(-1250, 1250), ylim=(-1.65, 2.7), yticks=[0, 1.5],
               ylabel="local N [mm]", xlabel="global z [mm] (= local V)")
        ax.set_xticks([-1200, -800, -400, 0, 400, 800, 1200])
    ax = fig.add_subplot(grid[2, 0])
    stave = staves["tangential"]
    # Projection onto V,N; both pickups and both pipe legs project to one band.
    colors = dict(sensitive=sensor, guard=body, readout="#7594b5", interconnect="#b1a17d",
                  module_passive=body, module_flex="#b08c4c", thermal_pickup=pickup,
                  core="#d8dfd2", support=support, power_bus="#ba772f", signal_bus="#ba772f")
    for p in stave.findall("piece"):
        if p.get("role") not in ("support", "core", "power_bus", "thermal_pickup"):
            continue
        lo, hi = interval(p)
        if hi < -125 or lo > 125:
            continue
        ax.add_patch(Rectangle((lo, dim(p, "w")-dim(p, "sz")/2), hi-lo, dim(p, "sz"),
                               facecolor=colors[p.get("role")], edgecolor="none"))
    for m in stave.findall("module"):
        z, lift = dim(m, "z"), dim(m, "lift")
        if abs(z) > 100:
            continue
        # Draw active silicon last so peripheral guards do not hide it in projection.
        for p in sorted(m.findall("piece"), key=lambda p: p.get("role") == "sensitive"):
            lo, hi = interval(p, z)
            ax.add_patch(Rectangle((lo, dim(p, "w")+lift-dim(p, "sz")/2), hi-lo, dim(p, "sz"),
                                   facecolor=colors[p.get("role")], edgecolor="none"))
    def dimension(axis, lo, hi, y, text):
        axis.annotate("", xy=(lo, y), xytext=(hi, y), arrowprops=dict(arrowstyle="|-|", color="#333333", lw=.8))
        axis.text((lo+hi)/2, y+.18, text, ha="center", va="bottom", fontsize=9)
    left, right = r["rows"][13:15]
    dimension(ax, left["center_z_mm"], right["center_z_mm"], 3.5, "centre pitch 85.333 mm")
    dimension(ax, *left["active_z_mm"], 5.0, "active length 96 mm")
    ax.annotate("active overlap 10.667 mm\nat z = −5.333…+5.333", xy=(0, .7), xytext=(25, 6.2),
                ha="center", fontsize=9, arrowprops=dict(arrowstyle="-", color="#555555"))
    ax.annotate("front-stack gap 0.5 mm", xy=(0, .35), xytext=(-100, 2.2), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="#555555"))
    ax.annotate("64 mm pickups\n1.833 mm to adjacent body", xy=(-7, -.9), xytext=(32, -2.8), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="#555555"))
    ax.text(-117, -5.0, "cooling lies in the core; independent ±z returns\nclosest swept envelopes z = ±2.75 mm", fontsize=9, color=cooling)
    ax.axvline(0, color="#888888", ls=":", lw=.7)
    ax.set(title="(c) Central seam — shared V,N projection", xlim=(-125, 125), ylim=(-8, 8),
           xlabel="z [mm]", ylabel="local normal depth N [mm]")
    ax.text(-117, -7.75, "Normal scale enlarged; projected layers are not a single u slice.", fontsize=8)
    ax = fig.add_subplot(grid[2, 1])
    zones = [("active silicon", r["rows"][-1]["active_z_mm"], sensor),
             ("die incl. guard", r["rows"][-1]["sensor_z_mm"], body),
             ("front body + flex", r["rows"][-1]["front_body_z_mm"], "#b08c4c"),
             ("cold plate / buses", [1100, r["support_span_mm"][1]], support),
             ("end board", r["end_board_positive_z_mm"], "#7594b5"),
             ("sector collector", r["collector_positive_z_mm"], service),
             ("trunk → 3500 mm", [r["trunk_positive_z_mm"][0], 1340], service)]
    for i, (label, (lo, hi), color) in enumerate(zones):
        y = 6-i
        ax.add_patch(Rectangle((lo, y-.23), hi-lo, .46, facecolor=color, edgecolor="none", alpha=.85))
        end = r["trunk_positive_z_mm"][1] if i == 6 else hi
        ax.text(hi+1.5, y, f"{end:g}" if i != 6 else "→", va="center", fontsize=9)
        if i >= 4:
            ax.text(lo-1.5, y, f"{lo:g}", ha="right", va="center", fontsize=8)
    for z in (1200, 1210, 1215, 1245, 1310):
        ax.axvline(z, color="#999999", lw=.6, ls=":", zorder=0)
    ax.axvline(1295.5, color="#b43e3e", ls="--", lw=1)
    ax.text(1295.5, -1.15, "old disc\n1295.5", color="#b43e3e", ha="center", fontsize=9)
    dimension(ax, 1203.5, 1215, 7.1, "body → board: 11.5 mm")
    dimension(ax, 1245, 1310, 8.2, "collector: 65 mm")
    ax.text(1121, -2.15, "support → board: 5 mm; support beyond active: 10 mm\nold disc lies inside collector by 14.5 mm\nnegative end is the mirrored axial allocation", fontsize=9)
    ax.set(title="(d) Positive barrel end — axial allocation", xlim=(1120, 1345), ylim=(-2.8, 9.2),
           yticks=range(7), yticklabels=[z[0] for z in reversed(zones)], xlabel="z [mm]")
    ax.text(1121, -2.65, "Rows are an envelope ledger, not radial positions or connected routing.", fontsize=8)
    fig.suptitle("nODD short-strip barrel — longitudinal packing of the DES-020 prototypes", fontsize=17)
    fig.supxlabel("Blue: active silicon; grey outline: 103 mm front body. DRAFT / PROTOTYPE • Projected overlap is not full-track hermeticity.", fontsize=10)
    output.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(output/f"DES-020-z-packing.{ext}", dpi=160, metadata={"Date": None} if ext == "svg" else None)
    plt.close(fig)
    p = output/"DES-020-z-packing.svg"
    p.write_text("\n".join(line.rstrip() for line in p.read_text().splitlines())+"\n")
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"build/short-strip-z-packing")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT/"build"):
        parser.error("Exports and generated evidence must stay in ignored build/.")
    output.mkdir(parents=True, exist_ok=True)
    report = dict(status="DRAFT / PROTOTYPE; axial accounting, not detector acceptance", date="2026-10-07",
                  classification="INFERENCE from unchanged DES-020 NODD DESIGN CHOICE inputs/compact solids",
                  execution_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  execution_dirty=bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)),
                  producer_sha256=sha(__file__), python_version=platform.python_version(), prototypes={},
                  limitations=["Envelope arithmetic and projected axial union do not establish track hermeticity or installation tolerances.",
                               "Native/coverage/engineering evidence remains historical and is not rerun or overwritten.",
                               "Original 1295.5 mm endcap datum is the PR49 control interface, not a claim about later PR51.",
                               "Sector cells and route waypoints do not qualify bends, connectors or hydraulic/electrical continuity."])
    staves = {}
    for key, input_name, frozen in CASES:
        report["prototypes"][key], staves[key] = measure(HERE/input_name, ROOT/"docs/validation/DES-020"/frozen, output/key)
    a, b = report["prototypes"].values()
    # Remove explicitly transverse/count/source fields; every axial result must match.
    excluded = {"staves", "modules", "phi_tilt_deg", "source_sha256", "exported_compact_sha256"}
    if {k:v for k,v in a.items() if k not in excluded} != {k:v for k,v in b.items() if k not in excluded}:
        raise ValueError("The prototypes have different axial packing")
    report["all_staves_match_frozen_axial_schedule"] = True
    report["identical_prototype_axial_packing"] = True
    if not args.report_only:
        report["matplotlib_version"] = draw(report, staves, output/"figures")
        report["figure_sha256"] = {str(p.name): sha(p) for p in sorted((output/"figures").glob("DES-020-z-packing.*"))}
    (output/"packing.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print("PASS: both exported models match every frozen axial row; packing is identical")


if __name__ == "__main__":
    main()
