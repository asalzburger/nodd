"""Inventory-driven x-y section of DES-022, including the bearing connection.

This reads the retained inventory; it neither rebuilds nor changes geometry.
The section is inside a bearing ring, 0.25 mm from one potted bolt's centre.
All panels use equal x/y scales. Thin layers retain their physical coordinates.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Wedge, Patch, Rectangle, Arc
import numpy as np

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "svg.hashsalt": "DES022-xy", "axes.spines.top": False,
    "axes.spines.right": False,
})

COLOURS = {
    "core": "#d3bf90", "support": "#494949", "sensitive": "#27689e",
    "guard": "#a2c1d8", "pickup": "#777777", "spreader": "#777777",
    "module_glue": "#e7aa9d", "bus": "#c88336", "electronics": "#c88336",
    "flex": "#deb077", "cooling_tube": "#808995", "coolant": "#43abc1",
    "bearing_ring": "#735b96", "mount": "#735b96",
}
ORDER = {
    "bearing_ring": 0, "core": 1, "support": 2, "pickup": 3,
    "spreader": 4, "module_glue": 5, "guard": 6, "sensitive": 7,
    "bus": 8, "electronics": 9, "flex": 10, "mount": 11,
    "cooling_tube": 12, "coolant": 13,
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_polygon(vertices, edges, z):
    """Intersect a convex polyhedron with the stated global z plane."""
    points = []
    for i, j in edges:
        a, b = vertices[i], vertices[j]
        if abs(a[2] - z) < 1e-9:
            points.append(a[:2])
        if (a[2] - z) * (b[2] - z) < 0:
            points.append((a + (b-a) * (z-a[2]) / (b[2]-a[2]))[:2])
    if len(points) < 3:
        return None
    points = np.unique(np.round(points, 10), axis=0)
    if len(points) < 3:
        return None
    centre = points.mean(axis=0)
    angles = np.arctan2(points[:, 1]-centre[1], points[:, 0]-centre[0])
    return points[np.argsort(angles)]


def section(entity, z):
    """Return polygon/circle/annulus at z; reject unsupported intersected solids."""
    d = entity["dimensions_mm"]
    centre = np.array(entity["center_mm"])
    frame = np.array(entity["frame"])
    kind = entity["shape_kind"]
    if kind == "box":
        half = np.array([d["sx"], d["sy"], d["sz"]]) / 2
        if abs(centre[2]-z) > np.dot(half, abs(frame[:, 2])) + 1e-9:
            return None
        signs = np.array(list(itertools.product((-1, 1), repeat=3)))
        vertices = (signs * half) @ frame + centre
        edges = [(i, j) for i in range(8) for j in range(i+1, 8)
                 if np.count_nonzero(signs[i] != signs[j]) == 1]
        points = section_polygon(vertices, edges, z)
        return ("polygon", points) if points is not None else None
    if kind == "shoe":
        # Same ExtrudedPolygon as LongStrip.cpp, not a rectangular web proxy.
        a, b, k = d["sx"]/2, d["sz"]/2, d["slope"]
        xy = [(-a, -b-k*a), (a, -b+k*a), (a, b), (-a, b)]
        local = [[x, y, t] for t in (-d["sy"]/2, d["sy"]/2) for x, y in xy]
        vertices = np.array(local) @ frame + centre
        if z < vertices[:, 2].min() or z > vertices[:, 2].max():
            return None
        edges = [(i, (i+1) % 4) for i in range(4)]
        edges += [(i+4, (i+1) % 4+4) for i in range(4)]
        edges += [(i, i+4) for i in range(4)]
        return "polygon", section_polygon(vertices, edges, z)
    if kind == "tube":
        axial_z = abs(frame[2, 2])
        if abs(centre[2]-z) > axial_z*d["length"]/2 + d["rmax"]:
            return None
        if np.isclose(axial_z, 1):
            if abs(centre[2]-z) > d["length"]/2:
                return None
            return "annulus", (centre[:2], d["rmin"], d["rmax"])
        if np.isclose(axial_z, 0) and np.isclose(abs(frame[1, 2]), 1):
            # Transverse solid Ti pin: the section is a chord, not its projection.
            if d["rmin"] != 0:
                raise ValueError("Transverse hollow cylinder is unsupported")
            dz = z-centre[2]
            if abs(dz) >= d["rmax"]:
                return None
            chord = np.sqrt(d["rmax"]**2 - dz**2)
            points = np.array([centre[:2] + u*frame[0, :2] + n*frame[2, :2]
                               for u, n in ((-chord, -d["length"]/2),
                                            (chord, -d["length"]/2),
                                            (chord, d["length"]/2),
                                            (-chord, d["length"]/2))])
            return "polygon", points
        raise ValueError(f"Unsupported intersected cylinder: {entity['name']}")
    if kind == "torus" and abs(centre[2]-z) > d["major"]+d["rmax"]:
        return None
    if kind == "sector" and abs(centre[2]-z) > d["length"]/2:
        return None
    raise ValueError(f"Unsupported intersected solid: {entity['name']}")


def colour(e):
    if e["role"] == "mount":
        return {"CFRP": "#735b96", "Epoxy": "#e7aa9d", "Titanium": "#808995"}[e["material"]]
    return COLOURS[e["role"]]


def paint(ax, e, cut, alpha=1, overview=False):
    kind, data = cut
    kw = dict(facecolor=colour(e), edgecolor="none", alpha=alpha,
              zorder=ORDER[e["role"]])
    if kind == "polygon":
        ax.add_patch(Polygon(data, **kw))
        if e["role"] == "sensitive":
            ax.add_patch(Polygon(data, fill=False, edgecolor=colour(e),
                                 linewidth=.45 if overview else .65,
                                 alpha=alpha, zorder=ORDER[e["role"]]))
    else:
        centre, ri, ro = data
        if ri:
            ax.add_patch(Wedge(centre, ro, 0, 360, width=ro-ri, **kw))
        else:
            ax.add_patch(Circle(centre, ro, **kw))


def label(ax, text, xy, xytext, ha="left"):
    ax.annotate(text, xy=xy, xytext=xytext, ha=ha, va="center", fontsize=9,
                arrowprops=dict(arrowstyle="-", color="#444", lw=.8),
                bbox=dict(facecolor="white", edgecolor="none", alpha=.92, pad=2),
                zorder=30)


def polygon_at_y(points, y):
    """Leader target on the section centreline at a requested global y."""
    crossing = []
    for a, b in zip(points, np.roll(points, -1, axis=0)):
        if (a[1]-y) * (b[1]-y) < 0:
            crossing.append(a[0] + (b[0]-a[0]) * (y-a[1]) / (b[1]-a[1]))
    if len(crossing) != 2:
        raise ValueError("Leader target is outside its physical section")
    return np.mean(crossing), y


def run(inventory, output, receipt):
    raw = gzip.decompress(inventory.read_bytes()) if inventory.suffix == ".gz" else inventory.read_bytes()
    data = json.loads(raw)
    anchors = data["engineering"]["beam"]["recommended"]["anchors_z_mm"]
    station_z = next(z for z in anchors if z > 0)
    z = station_z + 2.75  # Drawing plane inside ring, just below +z bolt centre.
    sections = [(e, cut) for e in data["entities"] if (cut := section(e, z)) is not None]
    counts = dict(Counter(e["role"] for e, _ in sections))
    staves = data["layout"]["staves"]
    populations = [sum(s["layer"] == layer for s in staves) for layer in range(data["layers"])]
    rings = [e for e, _ in sections if e["role"] == "bearing_ring"]
    if counts["core"] != len(staves) or counts["sensitive"] != 2*len(staves) or len(rings) != data["layers"]:
        raise ValueError("Section does not show one complete sensor pair per stave and both rings")
    if counts["cooling_tube"] != 4*len(staves):
        raise ValueError("Expected four straight cooling legs per stave")
    pins = [e for e, _ in sections if e["role"] == "mount" and "_pin" in e["name"]]
    if len(pins) != len(staves):
        raise ValueError("Expected exactly one intersected bolt per stave")

    fig = plt.figure(figsize=(15, 10), facecolor="white")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.04, 1], height_ratios=[1, 1],
                           left=.07, right=.98, bottom=.17, top=.86, wspace=.25, hspace=.32)
    overview = fig.add_subplot(grid[:, 0])
    shingle = fig.add_subplot(grid[0, 1])
    mount = fig.add_subplot(grid[1, 1])
    for ax in (overview, shingle, mount):
        ax.set_aspect("equal")
        ax.set_xlabel("global x [mm]")
        ax.set_ylabel("global y [mm]")
        ax.tick_params(labelsize=9)
    for e, cut in sections:
        if e["role"] in ("core", "sensitive", "mount", "bearing_ring"):
            paint(overview, e, cut, overview=True)
    max_r = max(s["radius_mm"] for s in staves)
    extent = max_r + 80
    overview.set(xlim=(-extent, extent), ylim=(-extent, extent), title="(a) Both barrel layers and bearing rings")
    overview.plot(0, 0, "+", color="#333", ms=8)
    overview.text(0, 300, f"{populations[1]} staves · r = {max_r:g} mm", ha="center")
    overview.text(0, 130, f"{populations[0]} staves · r = {staves[0]['radius_mm']:g} mm", ha="center")
    overview.text(0, -60, "12° phi tilt", ha="center")
    overview.text(0, -250, "CFRP rings inside the sensor barrels", ha="center", color="#735b96", fontsize=9)

    near = {s["name"] for s in staves if s["layer"] == 0 and s["stave"] in (0, 1, populations[0]-1)}
    selected = [(e, cut) for e, cut in sections if e["role"] == "bearing_ring" and "_L0_" in e["name"]
                or any(e["name"].startswith(name+"_") for name in near)]
    # Draw native cuts by their contained material: pipe/CO2 replaces foam,
    # epoxy/Ti replaces potted foam, and active silicon fills the guard opening.
    for e, cut in sorted(selected, key=lambda pair: ORDER[pair[0]["role"]]):
        paint(shingle, e, cut, alpha=1 if e["name"].startswith("L0_S0_") or e["role"] == "bearing_ring" else .45)
        paint(mount, e, cut)
    shingle.set(xlim=(790, 864), ylim=(-81, 84), title="(b) Inner layer: three adjacent shingled staves")
    shingle.text(794, -72, "Equal x/y scale\nNeighbouring staves faded", fontsize=8, zorder=30)
    # Show the tilt relative to the local tangent at phi = 0.
    shingle.plot([840, 840], [0, 38], "--", color="#333", lw=.6, zorder=25)
    shingle.add_patch(Arc((840, 0), 60, 60, theta1=90, theta2=102, color="#333", lw=.8, zorder=25))
    shingle.text(835.5, 35, "12°", fontsize=9, zorder=30)
    overview.add_patch(Rectangle((790, -81), 74, 165, fill=False, ec="#333", lw=.8, zorder=25))
    mount.set(xlim=(790, 852), ylim=(35, 67), title="(c) Mounting edge: sandwich → shoe/web → ring")
    by_name = {e["name"]: (e, cut) for e, cut in selected}
    core_xy = polygon_at_y(by_name["L0_S0_core"][1][1], 39)
    si = next((e, cut) for e, cut in selected if e["role"] == "sensitive"
              and e["name"].startswith("L0_S0_") and e["ids"]["sensor"] == 0)
    si_xy = polygon_at_y(si[1][1], 45)
    pin = next(e for e, _ in selected if e["name"].startswith("L0_S0_")
               and e in pins)
    web = next(e for e, _ in selected if e["name"].startswith("L0_S0_")
               and e["shape_kind"] == "shoe")
    label(mount, "5 mm structural foam", core_xy, (849, 36), "right")
    label(mount, "Paired Si faces", si_xy, (849, 63), "right")
    label(mount, "Potted Ti fastener", pin["center_mm"][:2], (843, 58))
    label(mount, "CFRP tangent shoe/web", web["center_mm"][:2], (804, 64))
    label(mount, "3 mm CFRP bearing ring", (795, 51), (792, 39))
    label(mount, "Epoxy joint + Ti clamp", (825.65, 53.18), (813, 37))
    shingle.add_patch(Rectangle((790, 35), 62, 32, fill=False, ec="#333", lw=.8, zorder=25))

    fig.suptitle("nODD long-strip barrel — x-y section and module mounting", fontsize=17, y=.965)
    fig.text(.5, .91, f"DES-022 · DRAFT / PROTOTYPE · z = {z:.2f} mm · support station z = {station_z:.2f} mm",
             ha="center", fontsize=11, color="#555")
    legend = [Patch(fc=c, label=t) for c, t in (
        (COLOURS["sensitive"], "Active silicon"), (COLOURS["core"], "Structural foam"),
        (COLOURS["support"], "CFRP skins"), (COLOURS["mount"], "CFRP shoe / ring"),
        ("#e7aa9d", "Epoxy / potting"), ("#808995", "Ti pipes / fasteners"),
        (COLOURS["coolant"], "CO₂"), (COLOURS["bus"], "Bus / hybrid"))]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5, .079), ncol=4,
               frameon=False, fontsize=9)
    fig.text(.5, .06, "Exact inventory sections, not longitudinal projections. Thin skins / Si retain their physical coordinates; outlines aid visibility.", ha="center", fontsize=9)
    fig.text(.5, .038, f"{len(anchors)} stations/stave; centre fixes z, others slide. One of two bolts (z = station ±3 mm) intersects this plane.", ha="center", fontsize=9)
    fig.text(.5, .016, "No machined slots are claimed. End collectors are outside this section; ring stiffness, joints and torsion require qualification.", ha="center", fontsize=9)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".svg"), metadata={"Date": None})
    fig.savefig(output.with_suffix(".png"), dpi=180)
    plt.close(fig)
    svg = output.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
    root = Path(__file__).resolve().parents[2]
    evidence = {
        "status": "Drawing-only review addition; unchanged DES-022 DRAFT prototype",
        "inventory": str(inventory.resolve().relative_to(root)),
        "inventory_sha256": sha(inventory), "decoded_inventory_sha256": hashlib.sha256(raw).hexdigest(),
        "original_geometry_execution": data["provenance"]["execution"],
        "original_geometry_provenance": data["provenance"],
        "producer": str(Path(__file__).resolve().relative_to(root)), "producer_sha256": sha(Path(__file__)),
        "versions": {"matplotlib": matplotlib.__version__, "numpy": np.__version__},
        "section_z_mm": z, "station_z_mm": station_z, "section_entity_counts": counts,
        "layer_stave_counts": populations, "detailed_staves": sorted(near),
        "panels": ["Full barrel: core, Si, mounts and rings", "Three adjacent inner-layer staves: all intersected components", "Mounting-edge detail: all intersected components"],
        "outputs": {str(p.resolve().relative_to(root)): sha(p) for p in (output.with_suffix(".svg"), output.with_suffix(".png"))},
        "limitations": ["Equal-scale x-y sections, not CAD or new native validation.",
                        "Contained pipe/pot/pin materials and active silicon overpaint their corresponding host cuts; retained inventory dimensions/transforms are unchanged.",
                        "One of two longitudinally separated bolts intersects this plane; slot motion is nominal, not machined CAD.",
                        "Original coverage, material cost and engineering failures remain in the existing validation report."]}
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(evidence, indent=2)+"\n")
    print(json.dumps({"section_z_mm": z, "counts": counts, "figures": evidence["outputs"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Figure stem, without extension")
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    run(args.inventory, args.output, args.receipt)
