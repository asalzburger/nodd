#!/usr/bin/env python3
"""Project saved ODD ECAL endcap SimHits; no digitization or transport run."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ODD_PIN = "d70556f33b1c36abdf101a07ad8cf57eb56fbdf1"
SOURCE_FILES = ("xml/detectors/CalorimeterECal.xml", "xml/OpenDataDetectorEnvelopes.xml",
                "factory/calorimeter/ODDPolyhedraEndcapCalorimeter_geo.cpp")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def mm(value):
    match = re.fullmatch(r"\s*([0-9.]+)\s*\*\s*(mm|cm|m)\s*", value)
    if not match:
        raise ValueError(f"Unsupported dimensional expression: {value}")
    return float(match[1]) * {"mm": 1, "cm": 10, "m": 1000}[match[2]]


def geometry(source):
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != ODD_PIN:
        raise ValueError(f"Requires ODD {ODD_PIN}, got {revision}")
    subprocess.run(["git", "-C", str(source), "diff", "--quiet", "HEAD", "--", *SOURCE_FILES], check=True)
    envelope = ET.parse(source / SOURCE_FILES[1]).getroot()
    constants = {c.attrib["name"]: c.attrib["value"] for c in envelope.findall("./define/constant")}
    xml = ET.parse(source / SOURCE_FILES[0]).getroot()
    calorimeter = xml.find("./detectors/detector[@name='ECalEndcap']")
    layer = calorimeter.find("layer")
    slices = layer.findall("slice")
    sensitive = [i for i, s in enumerate(slices) if s.get("sensitive") == "yes"]
    if len(sensitive) != 1:
        raise ValueError("Expected one sensitive silicon slice per layer")
    index = sensitive[0]
    n = int(constants["ecal_e_symmetry"])
    outer = mm(constants["ecal_e_outer_radius"])
    pitch = mm(xml.find("./define/constant[@name='ECal_cell_size']").get("value"))
    return dict(modules=n, layers=int(layer.get("repeat")), inner_apothem_mm=mm(constants["ecal_e_inner_radius"]),
                outer_radius_mm=outer, outer_apothem_mm=outer * math.cos(math.pi / n),
                gap_per_module_edge_mm=mm(calorimeter.get("gap")), pitch_mm=pitch,
                zmin_mm=mm(constants["ecal_e_min_z"]),
                layer_thickness_mm=sum(mm(s.get("thickness")) for s in slices),
                sensitive_depth_mm=sum(mm(s.get("thickness")) for s in slices[:index]) + mm(slices[index].get("thickness")) / 2,
                sensitive_slice=index + 1,
                encoding=xml.find("./readouts/readout[@name='ECalEndcapCollection']/id").text.strip(),
                source_revision=revision, source_sha256={name: sha256(source / name) for name in SOURCE_FILES})


def fields(encoding):
    offset = 0
    result = []
    for item in encoding.split(","):
        parts = item.split(":")
        name = parts[0]
        if len(parts) == 3:
            offset = int(parts[1])
        width = int(parts[-1])
        result.append((name, offset, abs(width), width < 0))
        offset += abs(width)
    return result


def decode(cell, specification):
    result = {}
    for name, offset, width, signed in specification:
        value = (cell >> offset) & ((1 << width) - 1)
        if signed and value >= (1 << (width - 1)):
            value -= 1 << width
        result[name] = value
    return result


def basis(g, stored_module):
    # From the pinned factory's placeStaves and positive-endcap placement.
    # Factory modules1..16 occupy a four-bit stored field, so16 is encoded0.
    physical = stored_module or g["modules"]
    phi = 2 * math.pi / g["modules"] * (2 - physical) - math.pi / 2
    radial = (math.cos(phi), math.sin(phi))
    tangent = (-math.sin(phi), math.cos(phi))
    return radial, tangent


def centre(g, module, u, v):
    radial, tangent = basis(g, module)
    radius = (g["inner_apothem_mm"] + g["outer_apothem_mm"]) / 2 + v * g["pitch_mm"]
    return [radius * radial[i] + u * g["pitch_mm"] * tangent[i] for i in range(2)]


def module_outline(g, module):
    radial, tangent = basis(g, module)
    result = []
    for radius, sign in ((g["inner_apothem_mm"], -1), (g["outer_apothem_mm"], -1),
                         (g["outer_apothem_mm"], 1), (g["inner_apothem_mm"], 1)):
        half_width = radius * math.tan(math.pi / g["modules"]) - g["gap_per_module_edge_mm"]
        result.append([radius * radial[i] + sign * half_width * tangent[i] for i in range(2)])
    return result


def extract(args):
    from podio import root_io
    import ROOT
    g = geometry(args.odd_source.resolve())
    manifest = json.loads(args.manifest.read_text())
    if manifest["odd_revision"] != ODD_PIN:
        raise ValueError("Simulation/geometry source pin mismatch")
    samples = [s for s in manifest["samples"] if s["particle"] == args.particle and s["energy_GeV"] == args.energy and s["eta"] == args.eta]
    if len(samples) != 1:
        raise ValueError("Need exactly one matching saved sample")
    sample = samples[0]
    path = Path(sample["path"])
    if sample["exit_code"] != 0 or sha256(path) != sample["sha256"]:
        raise ValueError("Failed or changed input sample")
    if not all(math.isfinite(x) and x > 0 for x in (args.overview_bin_mm, args.zoom_width_mm)):
        raise ValueError("Display bin/window dimensions must be positive")
    if not 0 <= args.layer <= g["layers"]:
        raise ValueError("Layer must be0 (automatic) or a valid one-based sensitive layer")
    half = math.ceil((g["outer_radius_mm"] + g["pitch_mm"]) / args.overview_bin_mm) * args.overview_bin_mm
    bins = round(2 * half / args.overview_bin_mm)
    overview = [0] * (bins * bins)
    by_layer = defaultdict(Counter)
    totals = Counter()
    worst = [0., 0., 0.]
    specification = fields(g["encoding"])
    for frame in root_io.Reader(str(path)).get("events"):
        totals["events"] += 1
        seen = set()
        for hit in frame.get("ECalEndcapCollection"):
            cell = int(hit.getCellID())
            if cell in seen:
                raise ValueError("Repeated cell ID within one simulated event")
            seen.add(cell)
            identity = decode(cell, specification)
            if identity["barrel"] != 1:
                totals["other_endcap_entries"] += 1
                continue
            point = hit.getPosition()
            observed = (float(point.x), float(point.y), float(point.z))
            if not all(math.isfinite(x) for x in (*observed, hit.getEnergy())) or hit.getEnergy() < 0:
                raise ValueError("Invalid stored SimHit")
            layer, module, u, v = (identity[k] for k in ("layer", "module", "x", "z"))
            if not 1 <= layer <= g["layers"] or not 0 <= module < g["modules"] or identity["slice"] != g["sensitive_slice"]:
                raise ValueError("Unexpected sensitive identity")
            expected = centre(g, module, u, v) + [g["zmin_mm"] + g["sensitive_depth_mm"] + (layer - 1) * g["layer_thickness_mm"]]
            for i in range(3):
                delta = abs(observed[i] - expected[i])
                worst[i] = max(worst[i], delta)
                if delta > 4 * 2**-23 * max(1., abs(expected[i])):
                    raise ValueError("CellID/source placement disagrees with stored cell centre")
            ix, iy = (math.floor((observed[i] + half) / args.overview_bin_mm) for i in range(2))
            if not (0 <= ix < bins and 0 <= iy < bins):
                raise ValueError("Hit centre outside overview display bins")
            overview[iy * bins + ix] += 1
            by_layer[layer][module, u, v] += 1
            totals["positive_endcap_entries"] += 1
    if totals["events"] != sample["requested_events"]:
        raise ValueError("Event count differs from generator manifest")
    chosen = args.layer or max(by_layer, key=lambda k: (sum(by_layer[k].values()), -k))
    if not by_layer[chosen]:
        raise ValueError("Chosen sensitive layer has no stored hits")
    counts = by_layer[chosen]
    seed = max(sorted(counts), key=counts.__getitem__)
    zoom_centre = centre(g, *seed)
    window = [zoom_centre[0] - args.zoom_width_mm / 2, zoom_centre[0] + args.zoom_width_mm / 2,
              zoom_centre[1] - args.zoom_width_mm / 2, zoom_centre[1] + args.zoom_width_mm / 2]
    selected = []
    for (module, u, v), count in sorted(counts.items()):
        x, y = centre(g, module, u, v)
        if window[0] - g["pitch_mm"] <= x <= window[1] + g["pitch_mm"] and window[2] - g["pitch_mm"] <= y <= window[3] + g["pitch_mm"]:
            if count > totals["events"]:
                raise ValueError("Per-cell occupancy exceeds event count")
            selected.append([module, u, v, count])
    result = dict(schema_version=1, status="PROTOTYPE raw SimHit projection; no digitization or new transport",
                  collection="ECalEndcapCollection", side="+z (stored barrel field1)", geometry=g,
                  input_sha256=sample["sha256"], manifest_sha256=sha256(args.manifest),
                  sample={k: sample[k] for k in ("particle", "energy_GeV", "eta", "phi_rad", "requested_events", "seed")},
                  script_sha256=sha256(Path(__file__)), ROOT_version=ROOT.gROOT.GetVersion(), totals=dict(totals),
                  position_validation=dict(method="All selected stored global cell centres compared to pinned factory/ID grid", maximum_residual_mm=worst,
                                           tolerance="4 * float32 epsilon * max(1mm, absolute expected coordinate), per component"),
                  overview=dict(bin_width_mm=args.overview_bin_mm, x_edges_mm=[-half + i * args.overview_bin_mm for i in range(bins + 1)],
                                y_edges_mm=[-half + i * args.overview_bin_mm for i in range(bins + 1)],
                                counts_y_then_x=overview, normalization="Stored positive-endcap SimHit entries summed over all48 layers and all events"),
                  zoom=dict(layer=chosen, layer_policy="Requested layer" if args.layer else "Largest total SimHit-entry count; tie chooses lowest layer",
                            total_layer_entries=sum(counts.values()), window_xy_mm=window,
                            cell_bins_module_localx_localz_count=selected,
                            normalization="One per-cell occupancy count per event; all events retained", glyph="Nominal readout cells clipped to the source silicon-module trapezoid"),
                  limitations=["Fixed-phi gun illuminates a shower patch; uncolored cells are not evidence of dead channels or inefficiency.",
                               f"Module outlines are geometry guides; left display bins{args.overview_bin_mm:g}mm are distinct from local{g['pitch_mm']:g}mm readout cells.",
                               "Cell centres, not contribution step positions. Stored four-bit module0 corresponds to factory module16.",
                               "No explicit wafer tiling beyond the ODD wedge-shaped sensitive module; no digitization, calibration or full Marlin study."])
    assert sum(overview) == totals["positive_endcap_entries"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(json.dumps(dict(events=totals["events"], positive_entries=totals["positive_endcap_entries"], layer=chosen,
                          layer_entries=sum(counts.values()), zoom_cells=len(selected), maximum_residual_mm=worst)))


def plot(args):
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "nodd-endcap-xy-matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, LogNorm
    from matplotlib.patches import Polygon, Rectangle
    import numpy as np
    data = json.loads(args.input.read_text())
    g, overview, zoom = data["geometry"], data["overview"], data["zoom"]
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 7.2))
    fig.subplots_adjust(left=.075, right=.925, bottom=.27, top=.80, wspace=.40)
    cmap = LinearSegmentedColormap.from_list("ECAL", ["#ffffdd", "#cccc00", "#666600"])
    polygons = {}
    for module in range(g["modules"]):
        points = module_outline(g, module)
        polygons[module] = points
        for axis in axes:
            axis.add_patch(Polygon(points, closed=True, facecolor="#fafafa", edgecolor="#999999", linewidth=.7, zorder=0))
        radial, _ = basis(g, module)
        axes[0].text(1310 * radial[0], 1310 * radial[1], str(module), ha="center", va="center", fontsize=8,
                     color="#444444", bbox=dict(facecolor="white", edgecolor="none", alpha=.8, pad=1.3), zorder=5)
    xe, ye = overview["x_edges_mm"], overview["y_edges_mm"]
    values = np.asarray(overview["counts_y_then_x"]).reshape((len(ye) - 1, len(xe) - 1))
    left = axes[0].pcolormesh(xe, ye, np.ma.masked_equal(values, 0), cmap=cmap, norm=LogNorm(1, max(2, values.max())), shading="flat", zorder=2)
    for points in polygons.values():
        axes[0].add_patch(Polygon(points, closed=True, fill=False, edgecolor="#999999", linewidth=.6, zorder=4))
    axes[0].set(xlim=(-1550, 1550), ylim=(-1550, 1550), title=f"All {g['layers']} sensitive layers · {overview['bin_width_mm']:g} mm display bins")
    window = zoom["window_xy_mm"]
    axes[0].add_patch(Rectangle((window[0], window[2]), window[1] - window[0], window[3] - window[2], fill=False, edgecolor="#111111", linewidth=1.3, zorder=6))
    maximum = max(c[3] for c in zoom["cell_bins_module_localx_localz_count"])
    norm = LogNorm(1, max(2, maximum))
    visible_modules = set()
    for module, u, v, count in zoom["cell_bins_module_localx_localz_count"]:
        visible_modules.add(module)
        x, y = centre(g, module, u, v)
        radial, tangent = basis(g, module)
        position = (x, y)
        corners = [[position[i] + g["pitch_mm"] / 2 * (su * tangent[i] + sv * radial[i]) for i in range(2)]
                   for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        patch = Polygon(corners, closed=True, facecolor=cmap(norm(count)), edgecolor="#888833", linewidth=.3, zorder=3)
        patch.set_clip_path(Polygon(polygons[module], closed=True, transform=axes[1].transData))
        axes[1].add_patch(patch)
        patch.set_clip_box(axes[1].bbox)
    axes[1].set(xlim=window[:2], ylim=window[2:], title=f"Layer {zoom['layer']} · actual {g['pitch_mm']:g} mm readout-cell bins")
    for axis in axes:
        axis.set_aspect("equal")
        axis.set(xlabel="Global x [mm]", ylabel="Global y [mm]")
        axis.spines[["top", "right"]].set_visible(False)
        axis.tick_params(labelsize=9)
    fig.colorbar(left, ax=axes[0], fraction=.045, pad=.03, label="SimHit entries / projected bin")
    fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=axes[1], fraction=.045, pad=.03, label="Events with a hit / readout cell")
    sample = data["sample"]
    particle = {"e-": "electrons", "gamma": "photons", "mu-": "muons"}.get(sample["particle"], sample["particle"])
    fig.suptitle(f"ODD Si–W ECAL endcap (+z) · sensitive-hit x–y projection\n{sample['energy_GeV']:g} GeV {particle}, η={sample['eta']:g}, φ={sample['phi_rad']:g} rad · {data['totals']['events']} saved events · raw SimHits", fontsize=12, y=.97)
    fig.text(.075, .14, f"Grey boundaries: {g['modules']} silicon-module wedges; labels are stored module IDs. Zoom crosses modules {', '.join(map(str, sorted(visible_modules)))}.\n"
             f"Readout segmentation: local x/z grid, {g['pitch_mm']:g} × {g['pitch_mm']:g} mm². Zoom cells are clipped to the module footprint.", fontsize=9)
    fig.text(.075, .035, "Fixed-φ illumination; uncolored regions are unhit in this sample, not disabled channels. Cell centres, not particle step positions.\n"
             "No digitization or new transport run. ODD has virtual readout cells in silicon wedges; this is not a wafer-tiling model.", fontsize=8.5)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    ex = sub.add_parser("extract")
    ex.add_argument("--manifest", type=Path, required=True)
    ex.add_argument("--odd-source", type=Path, required=True)
    ex.add_argument("--particle", default="e-")
    ex.add_argument("--energy", type=float, default=50)
    ex.add_argument("--eta", type=float, default=2)
    ex.add_argument("--layer", type=int, default=0)
    ex.add_argument("--overview-bin-mm", type=float, default=20)
    ex.add_argument("--zoom-width-mm", type=float, default=140)
    ex.add_argument("--output", type=Path, required=True)
    pl = sub.add_parser("plot")
    pl.add_argument("--input", type=Path, required=True)
    pl.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    (extract if args.mode == "extract" else plot)(args)


if __name__ == "__main__":
    main()
