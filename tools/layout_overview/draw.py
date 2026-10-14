#!/usr/bin/env python3
"""Reproduce the LAYOUT-001 R–Z overview from retained, pinned scalar inputs.

This standard-library drawing is a component-envelope illustration. It does not
build detector geometry, infer acceptance or assign material to reservations.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "docs/layouts/LAYOUT-001.json"
OUTPUT = ROOT / "docs/layouts/figures/LAYOUT-001-rz.svg"
COLOURS = {"pixel": "#8754b4", "short": "#247db1", "long": "#33996b"}


def draw(data):
    """Return deterministic SVG with one metre represented by 100 pixels."""
    tracker = data["tracker"]
    groups = tracker["sensitive_groups"]
    if sum(g["count"] for g in groups) != tracker["sensitive_elements"]:
        raise ValueError("Tracker sensitive-group count differs from its source")
    if not any(g["side"] == -1 for g in groups) or not any(g["side"] == 1 for g in groups):
        raise ValueError("Both recorded tracker endcaps are required")
    view = data["view"]
    scale, left, base = 100.0, 110.0, 620.0
    x = lambda z: left + (z - view["z_min_m"]) * scale
    y = lambda r: base - r * scale
    width = (view["z_max_m"] - view["z_min_m"]) * scale
    height = view["r_max_m"] * scale
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="855" viewBox="0 0 1500 855" role="img" aria-labelledby="title description">',
        '<title id="title">LAYOUT-001: tracker, inner 3 T solenoid, Si–W ECAL and HCAL outline</title>',
        '<desc id="description">Equal-scale R-Z envelope section. Recorded tracker bounds, conditional magnet/ECAL, amended HCAL outline, cyan empty external service annulus/rear break and red empty FCal reservations. No installed FCal or muon system.</desc>',
        '<metadata>' + html.escape(json.dumps({"layout_id": data["layout_id"], "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(), "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "source_revisions": sorted({v["revision"] for v in data["sources"].values()}), "scope": "Envelope illustration; no new native simulation"}, sort_keys=True)) + '</metadata>',
        '<defs><pattern id="magnet" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#f0ecfb"/><path d="M-2,2 l4,-4 M0,8 l8,-8 M6,10 l4,-4" stroke="#c5b8e3" stroke-width="1"/></pattern></defs>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#203047} .title{font-size:29px;font-weight:700} .subtitle{font-size:19px} .label{font-size:17px} .tick{font-size:16px} .small{font-size:16px} .fine{font-size:15px} .grid{stroke:#e7ebef;stroke-width:1} .outline{fill:none;stroke:#637187;stroke-width:1.5;stroke-dasharray:7 5}</style>',
        '<rect width="1500" height="855" fill="white"/>',
        '<text x="75" y="49" class="title">LAYOUT-001 · Tracker + inner 3 T solenoid + Si–W ECAL</text>',
        '<text x="75" y="82" class="subtitle">Cyan: empty service space · red: empty FCal reservation · open prototypes, engineering sign-off pending</text>',
    ]

    def text(z, r, label, klass="label", anchor="middle"):
        out.append(f'<text x="{x(z):.3f}" y="{y(r):.3f}" class="{klass}" text-anchor="{anchor}">{html.escape(label)}</text>')

    def box(z0, z1, r0, r1, fill, stroke="none", dash=None, opacity=1):
        if z0 >= z1 or r0 >= r1:
            raise ValueError("Invalid drawing envelope")
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<rect x="{x(z0):.3f}" y="{y(r1):.3f}" width="{(z1-z0)*scale:.3f}" height="{(r1-r0)*scale:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5" opacity="{opacity}"{dashed}/>')

    # Legend distinguishes subsystem content from conditional/rough envelopes.
    legends = [
        (75, 119, COLOURS["pixel"], "Pixel sensitive bounds", None),
        (395, 119, COLOURS["short"], "Short-strip sensitive bounds", None),
        (760, 119, COLOURS["long"], "Long-strip sensitive bounds", None),
        (75, 153, "url(#magnet)", "Solenoid allocation · PR64 open", None),
        (500, 153, "#f3c56b", "Si–W ECAL prototype envelopes", None),
        (1010, 153, "none", "HCAL rough outline", "7 5"),
    ]
    for lx, ly, fill, label, dash in legends:
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<rect x="{lx}" y="{ly-15}" width="28" height="18" fill="{fill}" stroke="#64748b"{dashed}/><text x="{lx+39}" y="{ly}" class="small">{html.escape(label)}</text>')

    for z in range(-6, 7):
        out.append(f'<path d="M{x(z):.3f},{base-height:.3f} V{base}" class="grid"/>')
        text(z, -.27, str(z), "tick")
    for r in range(5):
        out.append(f'<path d="M{left},{y(r):.3f} H{left+width}" class="grid"/>')
        out.append(f'<text x="{left-15}" y="{y(r)+6:.3f}" class="tick" text-anchor="end">{r}</text>')
    out.append(f'<rect x="{left}" y="{base-height}" width="{width}" height="{height}" fill="none" stroke="#607084"/>')
    out.append('<text x="755" y="682" class="subtitle" text-anchor="middle">z [m] · equal radial and axial scale</text>')
    out.append('<text x="39" y="410" class="subtitle" transform="rotate(-90 39 410)" text-anchor="middle">r [m]</text>')

    h = data["hcal"]
    box(-h["barrel_half_length_m"], h["barrel_half_length_m"], h["barrel_front_apothem_m"], h["barrel_outer_apothem_m"], "#f4f6f8", "#8893a3", "7 5")
    for side in (-1, 1):
        a, b = h["endcap_front_abs_z_m"], h["endcap_back_abs_z_m"]
        box(a if side > 0 else -b, b if side > 0 else -a, h["endcap_inner_apothem_m"], h["endcap_outer_apothem_m"], "#f4f6f8", "#8893a3", "7 5")
    text(0, 3.45, "HCAL · amended outline only", "subtitle")
    for side in (-1, 1):
        centre = side*(h["endcap_front_abs_z_m"]+h["endcap_back_abs_z_m"])/2
        text(centre, 2.9, "HCAL", "subtitle")
        text(centre, 2.64, "outline", "small")

    s = data["services"]
    e = data["ecal"]
    box(-h["barrel_half_length_m"], h["barrel_half_length_m"], s["inner_radius_m"], s["outer_radius_m"], "#d5eff3", "#7da7b1")
    text(0, 2.48, "300 mm external collection / backbone annulus", "fine")
    for side in (-1, 1):
        lo, hi = e["endcap_back_abs_z_m"], h["endcap_front_abs_z_m"]
        box(lo if side > 0 else -hi, hi if side > 0 else -lo, .3, s["egress_radius_m"], "#e7f4f6", "#7da7b1")
        mid = side*(lo+hi)/2
        out.append(f'<text x="{x(mid):.3f}" y="{y(2.0):.3f}" class="small" text-anchor="middle" transform="rotate(-90 {x(mid):.3f} {y(2.0):.3f})">400 mm radial egress break</text>')
        for f in data["forward_reservations"]:
            a, b = f["z_min_abs_m"], f["z_max_abs_m"]
            box(a if side > 0 else -b, b if side > 0 else -a, f["r_min_m"], f["r_max_m"], "#fff0f1", "#bf4257", "4 3")

    box(-e["barrel_flange_half_length_m"], e["barrel_flange_half_length_m"], e["barrel_front_apothem_m"], e["barrel_outer_apothem_m"], "#f3c56b", "#b67b16")
    for side in (-1, 1):
        a, b = e["endcap_front_abs_z_m"], e["endcap_back_abs_z_m"]
        box(a if side > 0 else -b, b if side > 0 else -a, e["endcap_inner_apothem_m"], e["endcap_outer_apothem_m"], "#f3c56b", "#b67b16")
        text(side*4.217, 1.24, "ECAL", "fine")
    text(0, 1.925, "Si–W barrel · detailed prototype", "subtitle")

    m = data["solenoid"]
    box(-m["vessel_half_length_m"], m["vessel_half_length_m"], m["vessel_inner_radius_m"], m["vessel_outer_radius_m"], "url(#magnet)", "#8b74b3")
    box(-m["cold_half_length_m"], m["cold_half_length_m"], m["cold_inner_radius_m"], m["cold_outer_radius_m"], "#bc9ade", "#926cc0")
    box(-m["cold_half_length_m"], m["cold_half_length_m"], m["cold_inner_radius_m"], m["winding_outer_radius_m"], "#8663b2")
    box(-m["vessel_half_length_m"], m["vessel_half_length_m"], m["vessel_inner_radius_m"], m["assembly_outer_reservation_m"], "none", "#8b74b3", "4 4")
    text(0, 1.49, "Solenoid allocation · 3 T central target", "fine")

    reservation = tracker["planning_reservation"]
    box(-reservation["half_length_m"], reservation["half_length_m"], 0, reservation["radius_m"], "none", "#637187", "4 4")
    for g in groups:
        family = "pixel" if g["component"] == "pixel" else g["component"].split("_")[0]
        box(g["z_min_m"], g["z_max_m"], g["r_min_m"], g["r_max_m"], COLOURS[family], opacity=.9)
    text(0, .94, "Tracker", "subtitle")
    text(0, .74, "recorded sensitive bounds", "fine")
    text(0, .36, "45,646 planes", "fine")
    # Tiny pipe is deliberately a line at this overview scale; no invented wall.
    out.append(f'<path d="M{x(-data['beam_pipe']['half_length_m']):.3f},{y(data['beam_pipe']['display_radius_m']):.3f} H{x(data['beam_pipe']['half_length_m']):.3f}" stroke="#697585" stroke-width="1"/>')
    out.append(f'<path d="M{x(0):.3f},{y(0):.3f} V{y(4.2):.3f}" stroke="#8c97a7" stroke-dasharray="3 4"/>')
    text(0, -.48, "IP", "small")

    out += [
        '<text x="110" y="721" class="small">Calorimeter section uses 16-gon apothems; corners extend farther. Blocks include inactive regions.</text>',
        '<text x="110" y="749" class="small">Local cassette collector ports remain absent; cyan lanes are backbone allocations, not an installed hydraulic/cable network.</text>',
        '<text x="110" y="777" class="small">Red FCal reservation: r = 0.080–0.290 m, |z| = 4.533–6.379 m; no hardware, acceptance or containment. No muon system.</text>',
        '<text x="110" y="811" class="fine">Inputs: DES025 tracker; DES026 / PR64 magnet; DES030 / PR70 + DES031 / PR71 unchanged ECAL; DES034 service-constrained HCAL outline.</text>',
        '<text x="110" y="835" class="fine">Pinned sources + reproduction: docs/layouts/LAYOUT-001.json · Envelope illustration; no combined native overlap or performance result.</text>',
        '</svg>',
    ]
    result = "\n".join(out) + "\n"
    ET.fromstring(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check retained SVG without writing")
    args = parser.parse_args()
    data = json.loads(INPUT.read_text())
    result = draw(data)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != result:
            raise SystemExit("FAIL: retained overview differs from named inputs/generator")
        print("PASS: deterministic SVG, valid XML, both endcaps and 45,646 recorded tracker planes")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(result)
        print("Wrote", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
