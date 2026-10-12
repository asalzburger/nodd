"""Pinned ODD endcap face arithmetic; optional comparison with DES029 packing.

Run from the repository root. This interprets the inspected source equations;
it does not construct ODD in DD4hep or measure calorimeter efficiency.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from assembly import inventory

REVISION = "c167363f3d4ad1540a577af99071283caf54f3a6"
SOURCE_HASHES = {
    "xml/OpenDataDetectorEnvelopes.xml": "f6d7f905fc6abc1437b1953d365d6faeb6ad0f1fd92ba82f21c774bca6bf05a4",
    "xml/detectors/CalorimeterECal.xml": "b8d248a0b4afc49381b3d5211e99dea59ebc5920836f0dd2512ae79dd9cabbdd",
    "xml/detectors/CalorimeterHCal.xml": "f7ae7005d5b2f5cf78e59a652b6f94c85786ac41b426974753029168a326ce3c",
    "factory/calorimeter/ODDPolyhedraEndcapCalorimeter_geo.cpp": "03fba144f0f1afbcd8bc352115defe1199672af6882b9672098b5b78a6a021e0",
}


def mm_value(value):
    parts = value.split("*")
    if len(parts) == 1:
        return float(parts[0])
    return float(parts[0]) * {"mm": 1, "cm": 10, "m": 1000}[parts[1]]


def compare(source):
    revision = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    if revision != REVISION:
        raise ValueError("Use the inspected ODD revision " + REVISION)
    for relative, expected in SOURCE_HASHES.items():
        actual = hashlib.sha256((source / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("Source differs from inspected equations: " + relative)
    constants = {
        x.attrib["name"]: mm_value(x.attrib["value"])
        for x in ET.parse(source / "xml/OpenDataDetectorEnvelopes.xml").iter("constant")
        if x.attrib["name"].startswith(("ecal_e_", "hcal_e_"))
    }
    model, _ = inventory()
    result = {
        "status": "DRAFT source-derived face coverage; no new native ODD validation",
        "upstream_revision": REVISION,
        "upstream_main_verified_on": "2026-10-12",
        "verification": "Public GitLab main API and four raw files matched the clean pinned cache byte for byte.",
        "source_sha256": SOURCE_HASHES,
        "method_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "prototype_source_sha256": model["source_sha256"],
        "method": {
            "outer_apothem": "R_corner * cos(pi/N)",
            "face_area": "N * (R_apothem^2 - r_inner_apothem^2) * tan(pi/N)",
            "sensitive_area": "face_area - N * 2 * gap * (R_apothem - r_inner_apothem)",
            "front_aperture_eta": "asinh(z_front / r_boundary); geometric illustration, not efficiency or full-depth acceptance",
            "denominators": "ODD polygon face excluding aperture, before stave seams; nODD sector absorber face excluding aperture and separate structural frame. Different detector sizes and reference faces.",
        },
        "endcaps": [],
    }
    for kind, name, xml in (
        ("ecal", "ECalEndcap", "CalorimeterECal.xml"),
        ("hcal", "HCalEndcap", "CalorimeterHCal.xml"),
    ):
        detector = next(
            x for x in ET.parse(source / "xml/detectors" / xml).iter("detector")
            if x.attrib["name"] == name
        )
        n = int(constants[kind + "_e_symmetry"])
        r = constants[kind + "_e_inner_radius"]
        corner = constants[kind + "_e_outer_radius"]
        outer = corner * math.cos(math.pi / n)
        z = constants[kind + "_e_min_z"]
        gap = mm_value(detector.attrib["gap"])
        layer = detector.find("layer")
        repeat = int(layer.attrib["repeat"])
        sensitive = next(x for x in layer.findall("slice") if x.attrib.get("sensitive") == "yes")
        area = n * (outer * outer - r * r) * math.tan(math.pi / n)
        active = area - n * 2 * gap * (outer - r)
        # Independent trapezoid area checks the whole-face subtraction expression.
        trapezoid = ((r + outer) * math.tan(math.pi / n) - 2 * gap) * (outer - r)
        assert math.isclose(n * trapezoid, active, rel_tol=1e-12)
        assert 0 < active < area
        assert r * math.tan(math.pi / n) > gap
        region = next(x for x in model["regions"] if x["name"] == kind + "_endcap")
        unit = next(x for x in model["units"] if x["name"] == kind)
        first = min(
            p["center_mm"][0] + s["center_mm"][1] - s["dimensions_mm"]["sy"] / 2
            for p in region["placements"] if p["layer"] == 0
            for s in unit["parts"] if s["role"] == "sensitive"
        )
        result["endcaps"].append({
            "subsystem": kind,
            "sectors": n,
            "layers": repeat,
            "front_mm": z,
            "inner_apothem_mm": r,
            "outer_corner_mm": corner,
            "outer_apothem_mm": outer,
            "half_width_reduction_mm": gap,
            "seam_normal_width_mm": 2 * gap * math.cos(math.pi / n),
            "sensitive_material": sensitive.attrib["material"],
            "sensitive_thickness_mm": mm_value(sensitive.attrib["thickness"]),
            "stack_depth_mm": repeat * sum(mm_value(x.attrib["thickness"]) for x in layer.findall("slice")),
            "face_area_mm2": area,
            "sensitive_face_area_mm2": active,
            "sensitive_face_fraction": active / area,
            "front_aperture_eta_at_flat": math.asinh(z / r),
            "front_aperture_eta_at_corner": math.asinh(z / (r / math.cos(math.pi / n))),
            "prototype_active_plate_fraction": region["coverage"][0]["active_fraction"],
            "prototype_first_sensitive_radius_mm": first,
            "prototype_front_mm": region["front_mm"],
        })
    return result, model


def plot(result, model, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Polygon, Rectangle

    plt.rcParams["svg.hashsalt"] = "odd-endcap-comparison"
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.6), layout="constrained")
    for row, comparison in enumerate(result["endcaps"]):
        kind = comparison["subsystem"]
        ax = axes[row, 0]
        inner, outer = comparison["inner_apothem_mm"], comparison["outer_apothem_mm"]
        tangent, gap = math.tan(math.pi / comparison["sectors"]), comparison["half_width_reduction_mm"]
        for reduction, color in ((0, "#f0dcb5"), (gap, "#32885b")):
            ax.add_patch(Polygon([
                [inner / 1000, -(inner * tangent - reduction) / 1000],
                [outer / 1000, -(outer * tangent - reduction) / 1000],
                [outer / 1000, (outer * tangent - reduction) / 1000],
                [inner / 1000, (inner * tangent - reduction) / 1000],
            ], facecolor=color, edgecolor="#555", lw=.6))
        ax.set_title(f"ODD {kind.upper()}: {100 * comparison['sensitive_face_fraction']:.2f}% sensitive face", loc="left", fontsize=11)
        ax.text(.02, .96, f"Inner edge {inner:.0f} mm | front z = {comparison['front_mm']/1000:.2f} m", transform=ax.transAxes, va="top", fontsize=9)
        ax.set(xlim=(.2, outer / 1000 + .08), ylim=(-outer * tangent / 1000 - .12, outer * tangent / 1000 + .12))

        ax = axes[row, 1]
        region = next(x for x in model["regions"] if x["name"] == kind + "_endcap")
        unit = next(x for x in model["units"] if x["name"] == kind)
        plate = next(x for x in region["parts"] if x["role"] == "absorber")
        ax.add_patch(Polygon([[x / 1000, y / 1000] for x, y in plate["vertices_mm"]], facecolor="#f0dcb5", edgecolor="#555", lw=.6))
        for placement in region["placements"]:
            if placement["layer"] != 0:
                continue
            x, y, _ = placement["center_mm"]
            width, height = unit["width_mm"], unit["height_mm"]
            ax.add_patch(Rectangle(((x-height/2)/1000, (y-width/2)/1000), height/1000, width/1000, facecolor="#c5d0d7", edgecolor="#777", lw=.5))
            for part in unit["parts"]:
                if part["role"] != "sensitive":
                    continue
                sx, sy, _ = part["center_mm"]
                sw, sh = part["dimensions_mm"]["sx"], part["dimensions_mm"]["sy"]
                ax.add_patch(Rectangle(((x+sy-sh/2)/1000, (y-sx-sw/2)/1000), sh/1000, sw/1000, facecolor="#32885b", edgecolor="white", lw=.1))
        first = comparison["prototype_first_sensitive_radius_mm"]
        ax.axvline(first / 1000, color="#aa3333", linestyle="--", lw=.8)
        ax.set_title(f"nODD PR69 {kind.upper()}: {100 * comparison['prototype_active_plate_fraction']:.2f}% active plate", loc="left", fontsize=11)
        ax.text(.02, .96, f"First sensitive edge {first:.0f} mm | nominal hole 300 mm", transform=ax.transAxes, va="top", fontsize=9)
        outer = region["outer_apothem_mm"]
        ax.set(xlim=(.2, outer / 1000 + .08), ylim=(-outer * tangent / 1000 - .12, outer * tangent / 1000 + .12))
    for ax in axes.flat:
        ax.set_aspect("equal")
        ax.set_xlabel("radial coordinate [m]")
        ax.set_ylabel("tangential coordinate [m]")
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Endcap coverage: continuous ODD sheets and packaged nODD cassettes\nOne sector / one layer; physical dimensions differ between detectors", fontsize=13)
    fig.legend(handles=[Patch(facecolor="#32885b", label="Sensitive material"), Patch(facecolor="#f0dcb5", label="Face outside sensitive material"), Patch(facecolor="#c5d0d7", label="Cassette footprint")], loc="outside lower center", ncol=3, frameon=False)
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "odd-endcap-comparison.png", dpi=180)
    svg = output / "odd-endcap-comparison.svg"
    fig.savefig(svg, metadata={"Date": None})
    svg.write_text("\n".join(x.rstrip() for x in svg.read_text().splitlines()) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    result, model = compare(args.source_dir)
    Path("docs/validation/DES-029/odd-endcap-comparison.json").write_text(json.dumps(result, indent=2) + "\n")
    if args.plot:
        plot(result, model, Path("docs/design/figures/DES-029"))
    print([(x["subsystem"], x["sensitive_face_fraction"], x["front_aperture_eta_at_flat"]) for x in result["endcaps"]])
