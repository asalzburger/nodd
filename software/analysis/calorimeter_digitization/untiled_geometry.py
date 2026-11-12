"""Isolated untiled-silicon control for the exact retained PR133 compact.

This is a PROTOTYPE geometry intervention, not a production detector change.
Original carrier boundaries and all nonintersecting passive material are kept.
Only original active/guard wafers are replaced; intersecting support is cut out
at the new 0.5-mm silicon planes. The unchanged native factories read this XML.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
EXPECTED = {
    "detector.xml": "411dc035120b663fb19d3000ee8a5984bfc9f7a6c31423b01539b47dc4384159",
    "materials.xml": "5091f0cbc2444b6ef481c2293ec99375e5eada82a84ab03be7a50f3b8375cee1",
    "particles.HEPEvt": "44bf93acf342ccfd9f461423ea12992ab1cab9046f84841ff8853ed763aad389",
    "truth-input.jsonl": "b53199a644e659eb6efdd4684b824c6b85f66e0968686b0af3482e93b56c30b1",
}
IDENTITY = ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
# local wafer u,v,w -> carrier x,y,z = w,u,v (normal is radial).
BARREL_FRAME = ((0., 0., 1.), (1., 0., 0.), (0., 1., 0.))
# cutter x,y,z -> wafer u,v,w = x,-z,y.
CUTTER_FRAME = ((1., 0., 0.), (0., 0., -1.), (0., 1., 0.))
TANGENT = math.tan(math.pi / 16)
SEAM_MM = 1.
THICKNESS_MM = .5
EPS = 1e-8


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def number(value):
    """Accept only the literal numeric units in the frozen compact."""
    text = str(value)
    if text.endswith("*mm"):
        text = text[:-3]
    result = float(text)
    if not math.isfinite(result):
        raise ValueError("Nonfinite geometry literal")
    return result


def mm(value):
    return f"{value:.17g}*mm"


def close(a, b):
    if abs(a - b) > EPS:
        raise ValueError(f"Unsupported source dimension: {a} != {b}")


def rotation(node):
    return tuple(tuple(number(node.get(f"a{i}{j}", str(IDENTITY[i][j]))) for j in range(3)) for i in range(3))


def location(node):
    return tuple(number(node.get(k, "0")) for k in ("x", "y", "z"))


def pose(node, xyz=(0., 0., 0.), frame=IDENTITY):
    node.attrib.update({k: mm(v) for k, v in zip(("x", "y", "z"), xyz)})
    node.attrib.update({f"a{i}{j}": f"{frame[i][j]:.17g}" for i in range(3) for j in range(3)})
    return node


def polygon(node):
    return [(number(v.get("x")), number(v.get("y"))) for v in node.findall("vertex")]


def area(points):
    if len(points) < 3:
        return 0.
    return abs(sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(points, points[1:] + points[:1]))) / 2


def signed_area(points):
    return sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(points, points[1:] + points[:1])) / 2


def intersection(subject, clip):
    """Convex polygon intersection; cutters/parts in this control are convex."""
    output = list(subject)
    clip = list(clip)
    if signed_area(clip) < 0:
        clip.reverse()
    for a, b in zip(clip, clip[1:] + clip[:1]):
        before, output = output, []
        if not before:
            break
        cross = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        previous, cp = before[-1], cross(before[-1])
        for current in before:
            cc = cross(current)
            if (cc >= -EPS) != (cp >= -EPS):
                t = cp / (cp - cc)
                output.append(tuple(previous[k] + t * (current[k] - previous[k]) for k in (0, 1)))
            if cc >= -EPS:
                output.append(current)
            previous, cp = current, cc
    return output


def prism(parent, tag, points, depth, xyz=(0., 0., 0.), frame=IDENTITY, **attributes):
    node = pose(ET.SubElement(parent, tag, kind="xtru", depth=mm(depth), **attributes), xyz, frame)
    for x, y in points:
        ET.SubElement(node, "vertex", x=mm(x), y=mm(y))
    return node


def wedge(low, high):
    return [(low, -low * TANGENT + SEAM_MM), (high, -high * TANGENT + SEAM_MM),
            (high, high * TANGENT - SEAM_MM), (low, low * TANGENT - SEAM_MM)]


def primitive_volume(node):
    kind = node.get("kind")
    if kind == "xtru":
        return area(polygon(node)) * number(node.get("depth"))
    if kind == "box":
        return math.prod(number(node.get(k)) for k in ("sx", "sy", "sz"))
    if kind == "tube":
        return math.pi * (number(node.get("rmax")) ** 2 - number(node.get("rmin")) ** 2) * number(node.get("length"))
    raise ValueError(f"Unsupported primitive {kind}")


def wafer_volume(node):
    if node.get("kind") != "xtru":
        raise ValueError("Expected original extruded silicon wafer")
    value = primitive_volume(node)
    for cut in node.findall("cut"):
        if location(cut) != (0., 0., 0.) or rotation(cut) != IDENTITY or cut.findall("cut"):
            raise ValueError("Unsupported wafer cut")
        close(number(cut.get("depth")), number(node.get("depth")))
        close(area(intersection(polygon(node), polygon(cut))), area(polygon(cut)))
        value -= primitive_volume(cut)
    if value <= 0:
        raise ValueError("Nonpositive original wafer volume")
    return value


def bounds(node):
    kind = node.get("kind")
    if kind == "xtru":
        depth = number(node.get("depth")) / 2
        points = [(x, y, z) for x, y in polygon(node) for z in (-depth, depth)]
    else:
        if kind == "box":
            half = [number(node.get(k)) / 2 for k in ("sx", "sy", "sz")]
        elif kind == "tube":
            half = [number(node.get("rmax")), number(node.get("rmax")), number(node.get("length")) / 2]
        else:
            raise ValueError(f"Unsupported source shape {kind}")
        points = [(x, y, z) for x in (-half[0], half[0]) for y in (-half[1], half[1]) for z in (-half[2], half[2])]
    xyz, frame = location(node), rotation(node)
    transformed = [tuple(xyz[i] + sum(frame[i][j] * p[j] for j in range(3)) for i in range(3)) for p in points]
    return [(min(p[i] for p in transformed), max(p[i] for p in transformed)) for i in range(3)]


def canonical(node):
    return node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(), tuple(canonical(child) for child in node)


def barrel_slab(template, layer, center, silicon):
    """Exact carrier-clipped wafer with local axes tangent, beam, radial."""
    halfwidth = (center + THICKNESS_MM / 2) * TANGENT - SEAM_MM
    piece = pose(ET.SubElement(template, "piece", name=f"untiled_barrel_l{layer}", role="sensitive", material=silicon,
                       kind="box", sx=mm(2 * halfwidth), sy="7800*mm", sz="0.5*mm"))
    # Numerical cutter extensions are outside the physical slab. Sloped
    # Boolean faces reproduce the exact original carrier boundary through
    # the radial thickness, rather than approximating it by a rectangle.
    wlow, whigh, outside = -1., 1., halfwidth + 1.
    lowline = lambda w: (center + w) * TANGENT - SEAM_MM
    positive = [(lowline(wlow), wlow), (outside, wlow), (outside, whigh), (lowline(whigh), whigh)]
    negative = [(-outside, wlow), (-lowline(wlow), wlow), (-lowline(whigh), whigh), (-outside, whigh)]
    for cutter in (positive, negative):
        prism(piece, "cut", cutter, 7802., frame=CUTTER_FRAME)
    return piece


def cut_intersections(piece, slabs):
    """Subtract exact carrier-coordinate axial prisms; report removed material.

    A slab has an XY convex polygon and axial z interval. Untouched primitives
    are returned verbatim. Frozen intersecting supports are identity-oriented
    extruded polygons with at most one through-hole; reject a broader model.
    """
    box = bounds(piece)
    xyz = location(piece)
    original_cuts = list(piece.findall("cut"))
    changed = []
    for slab in slabs:
        points, zlow, zhigh = slab["polygon"], *slab["z_interval_mm"]
        xy = [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(2)]
        depth = min(box[2][1], zhigh) - max(box[2][0], zlow)
        if depth <= EPS or any(min(box[i][1], xy[i][1]) - max(box[i][0], xy[i][0]) <= EPS for i in range(2)):
            continue
        if piece.get("kind") != "xtru" or rotation(piece) != IDENTITY:
            raise ValueError(f"Unsupported intersecting passive: {piece.get('name')}")
        body = [(x + xyz[0], y + xyz[1]) for x, y in polygon(piece)]
        overlap = intersection(body, points)
        cut_area = area(overlap)
        if cut_area <= EPS:
            continue
        if len(original_cuts) > 1:
            raise ValueError("Unsupported multiply cut intersecting support")
        for old in original_cuts:
            if old.get("kind") != "xtru" or rotation(old) != IDENTITY:
                raise ValueError("Unsupported existing passive cut")
            cb = bounds(old)
            if xyz[2] + cb[2][0] > max(box[2][0], zlow) + EPS or xyz[2] + cb[2][1] < min(box[2][1], zhigh) - EPS:
                raise ValueError("Existing support cut does not span slab intersection")
            cx, cy, _ = location(old)
            hole = [(x + xyz[0] + cx, y + xyz[1] + cy) for x, y in polygon(old)]
            cut_area -= area(intersection(overlap, hole))
        if cut_area <= EPS:
            continue
        local_points = [(x - xyz[0], y - xyz[1]) for x, y in points]
        prism(piece, "cut", local_points, zhigh - zlow, (0., 0., (zlow + zhigh) / 2 - xyz[2]))
        changed.append(dict(layer=slab["layer"], volume_mm3=cut_area * depth))
    return changed


def transform(tree):
    root = tree.getroot()
    if root.find("fields") is not None:
        raise ValueError("Expected zero-field source")
    detectors = {d.get("name"): d for d in root.findall("./detectors/detector")}
    if set(detectors) != {"BARREL", "EDGE"}:
        raise ValueError("Expected exact ECAL-only source")
    report = dict(status="PROTOTYPE / UNTILED CONTROL", thickness_mm=THICKNESS_MM,
                  carrier_half_seam_mm=SEAM_MM, virtual_pitch_mm=5.5,
                  factories_unchanged=True, original_replica_transforms_preserved=True,
                  removed_wafers=[], added_slabs=[], passive_subtractions=[])
    replicas_before = {name: [canonical(p) for p in d.findall("replica")] for name, d in detectors.items()}
    envelopes_before = {name: canonical(d.find("wedge_envelope")) for name, d in detectors.items()}
    for ro in root.findall("./readouts/readout"):
        if ro.findtext("id") != "system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6":
            raise ValueError("Unexpected original cell encoding")
        ro.find("segmentation").attrib.clear()
        ro.find("segmentation").attrib.update(type="CartesianGridXY", grid_size_x="5.5*mm", grid_size_y="5.5*mm", offset_x="2.75*mm", offset_y="2.75*mm")
        ro.find("id").text = "system:8,side:2,sector:4,layer:6,module:10,x:-12,y:-12"
    barrel = detectors["BARREL"]
    if barrel.get("type") != "nODDEcalBarrelPrototype" or barrel.get("id") != "8":
        raise ValueError("Unexpected barrel factory")
    original_board, = barrel.findall("board")
    removed = [p for p in original_board.findall("piece") if p.get("role") in ("sensitive", "sensor_edge")]
    if {p.get("name") for p in removed} != {"square_active", "square_guard"}:
        raise ValueError("Unexpected barrel wafer topology")
    original_wafer_volume = sum(wafer_volume(p) for p in removed)
    silicon = removed[0].get("material")
    for p in removed:
        close(number(p.get("depth")), THICKNESS_MM)
        close(location(p)[2], .6)
        original_board.remove(p)
    for p in original_board.findall("piece"):
        low, high = bounds(p)[2]
        if min(high, .85) - max(low, .35) > EPS:
            raise ValueError("A retained board passive overlaps silicon plane")
    barrel_slabs = []
    layer_regions = [r for r in barrel.findall("region") if r.get("name") != "barrel_frame"]
    if len(layer_regions) != 48:
        raise ValueError("Expected 48 barrel sampling layers")
    for layer, region in enumerate(layer_regions):
        if region.get("name") != f"barrel_layer{layer}":
            raise ValueError("Unexpected barrel layer ordering")
        instances = region.findall("board_instance")
        if not instances or any(b.get("template") != "square" for b in instances):
            raise ValueError("Unexpected original barrel modules")
        base = location(instances[0])[0]
        if any(abs(location(b)[0] - base) > EPS or abs(rotation(b)[0][2] - 1) > EPS for b in instances):
            raise ValueError("Noncoplanar barrel wafer instances")
        center = base + .6
        close(center, 1702.5 + layer * 10.9)
        carrier = wedge(center - THICKNESS_MM / 2, center + THICKNESS_MM / 2)
        slab = dict(layer=layer, polygon=carrier, z_interval_mm=[-3900., 3900.])
        barrel_slabs.append(slab)
        board_name = f"untiled_layer{layer}"
        template = ET.SubElement(barrel, "board", name=board_name)
        barrel_slab(template, layer, center, silicon)
        instance = pose(ET.SubElement(region, "board_instance", template=board_name, module="0"), (center, 0., 0.), BARREL_FRAME)
        report["removed_wafers"].append(dict(detector="BARREL", layer=layer, physical_wafer_pairs=len(instances) * 16,
            material=silicon, volume_mm3=original_wafer_volume * len(instances) * 16))
        report["added_slabs"].append(dict(detector="BARREL", layer=layer, physical_slabs=16, material=silicon,
            plane_center_mm=center, normal="carrier radial x", area_mm2=(2 * (center * TANGENT - SEAM_MM)) * 7800. * 16,
            volume_mm3=area(carrier) * 7800. * 16, local_frame=[list(row) for row in rotation(instance)]))
    for region in barrel.findall("region"):
        for piece in region.findall("piece"):
            old = canonical(piece)
            cuts = cut_intersections(piece, barrel_slabs)
            if cuts:
                report["passive_subtractions"].append(dict(detector="BARREL", region=region.get("name"), piece=piece.get("name"),
                     material=piece.get("material"), physical_replicas=16, cuts=cuts, volume_mm3=sum(c["volume_mm3"] for c in cuts) * 16))
            elif canonical(piece) != old:
                raise AssertionError("Unintersecting passive was modified")
    edge = detectors["EDGE"]
    if edge.get("type") != "nODDEcalEdgePrototype" or edge.get("id") != "9":
        raise ValueError("Unexpected endcap factory")
    layer_region, = [r for r in edge.findall("region") if r.get("name") == "edge_layer"]
    removed = [p for p in layer_region.findall("piece") if p.get("role") in ("sensitive", "sensor_edge")]
    if len(removed) != 224 or sum(p.get("role") == "sensitive" for p in removed) != 112:
        raise ValueError("Unexpected original endcap wafer inventory")
    silicon = next(p.get("material") for p in removed if p.get("role") == "sensitive")
    for p in removed:
        close(number(p.get("depth")), THICKNESS_MM)
        close(location(p)[2], 2.5)
        layer_region.remove(p)
    report["removed_wafers"].append(dict(detector="EDGE", physical_wafer_pairs=112 * 48 * 32,
        material=silicon, volume_mm3=sum(wafer_volume(p) for p in removed) * 48 * 32))
    carrier = wedge(100., 2223.2)
    prism(layer_region, "piece", carrier, THICKNESS_MM, (0., 0., 2.5), name="untiled_endcap_silicon",
          role="sensitive", material=silicon, module="0")
    edge_slabs = [dict(layer=i, polygon=carrier, z_interval_mm=[2.25 + i * 10.9, 2.75 + i * 10.9]) for i in range(48)]
    for region in edge.findall("region"):
        if region.get("name") == "edge_layer":
            for piece in region.findall("piece"):
                if piece.get("name") == "untiled_endcap_silicon":
                    continue
                if min(bounds(piece)[2][1], 2.75) - max(bounds(piece)[2][0], 2.25) > EPS:
                    raise ValueError(f"Retained endcap layer passive intersects Si: {piece.get('name')}")
        elif region.get("name") == "edge_frame":
            for piece in region.findall("piece"):
                cuts = cut_intersections(piece, edge_slabs)
                if cuts:
                    report["passive_subtractions"].append(dict(detector="EDGE", region=region.get("name"), piece=piece.get("name"),
                         material=piece.get("material"), physical_replicas=32, cuts=cuts, volume_mm3=sum(c["volume_mm3"] for c in cuts) * 32))
        else:
            raise ValueError("Unexpected endcap region")
    report["added_slabs"].append(dict(detector="EDGE", physical_slabs=48 * 32, material=silicon,
        plane_center_mm=2.5, layer_pitch_mm=10.9, normal="local endcap z", carrier_polygon_mm=carrier,
        area_mm2=area(carrier) * 48 * 32, volume_mm3=area(carrier) * THICKNESS_MM * 48 * 32))
    for name, detector in detectors.items():
        if [canonical(p) for p in detector.findall("replica")] != replicas_before[name] or canonical(detector.find("wedge_envelope")) != envelopes_before[name]:
            raise AssertionError("Original sector/layer placements or navigation envelope changed")
    report["physical_sensitive_slabs"] = sum(p["physical_slabs"] for p in report["added_slabs"])
    report["passive_subtraction_count"] = sum(len(p["cuts"]) for p in report["passive_subtractions"])
    if report["physical_sensitive_slabs"] != 2304:
        raise AssertionError("Unexpected full sampling-plane count")
    return report


def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    for name, expected in EXPECTED.items():
        if sha(source / name) != expected:
            raise ValueError(f"Unsupported source hash: {name}")
    manifest = json.loads((source / "sample.json").read_text())
    if manifest["events"] != 10000 or manifest["input_sha256"] != EXPECTED["particles.HEPEvt"] or manifest["truth_sha256"] != EXPECTED["truth-input.jsonl"]:
        raise ValueError("Expected retained 10k angular input manifest")
    tree = ET.parse(source / "detector.xml")
    report = transform(tree)
    densities = {}
    for material in ET.parse(source / "materials.xml").findall(".//material"):
        density = material.find("D")
        if density is not None:
            if density.get("unit") != "g/cm3":
                raise ValueError("Unsupported density units")
            densities[material.get("name")] = number(density.get("value"))
    totals = {}
    for category, sign in (("removed_wafers", -1), ("added_slabs", 1), ("passive_subtractions", -1)):
        for item in report[category]:
            item["mass_g"] = item["volume_mm3"] * densities[item["material"]] / 1000
            total = totals.setdefault(item["material"], dict(volume_delta_mm3=0., mass_delta_g=0.))
            total["volume_delta_mm3"] += sign * item["volume_mm3"]
            total["mass_delta_g"] += sign * item["mass_g"]
    report["material_changes"] = totals
    report["input_source_hashes"] = {name: sha(source / name) for name in EXPECTED}
    report["input_manifest_sha256"] = sha(source / "sample.json")
    report["geometry_transform_sha256"] = sha(__file__)
    report["geometry_transform_revision"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    report["checks"] = dict(original_sector_layer_transforms="unchanged", inherited_carrier_seam="unchanged 1 mm half gap",
        passive_changes="only exact intersections with new silicon planes", active_guard_wafers="replaced; other board films retained",
        sensitive_counts=2304, existing_factories="unchanged", primary_files="byte-identical copy",
        native_overlap_validation="required separately before transport", cell_position_note="virtual Cartesian cell centres can lie beyond clipped physical edge bins")
    output.mkdir(parents=True, exist_ok=False)
    for name in ("materials.xml", "particles.HEPEvt", "truth-input.jsonl"):
        shutil.copyfile(source / name, output / name)
    tree.find("info").set("title", "PROTOTYPE untiled silicon control; retained PR133 carrier faces")
    ET.indent(tree)
    tree.write(output / "detector.xml", encoding="utf-8", xml_declaration=True)
    manifest["hashes"] = {name: sha(output / name) for name in ("detector.xml", "materials.xml")}
    manifest["geometry_source"] = "PROTOTYPE untiled control: continuous full-carrier 0.5 mm Si; inherited sector seams preserved; intersecting support subtracted"
    manifest["control"] = {"type": "untiled-silicon", "original_source_revision": manifest["source_revision"],
        "original_sample_manifest_sha256": report["input_manifest_sha256"],
        "geometry_transform_sha256": report["geometry_transform_sha256"], "geometry_transform_revision": report["geometry_transform_revision"]}
    manifest["source_revision"] = report["geometry_transform_revision"]
    report["output_hashes"] = {name: sha(output / name) for name in EXPECTED}
    for name in ("particles.HEPEvt", "truth-input.jsonl", "materials.xml"):
        if report["input_source_hashes"][name] != report["output_hashes"][name]:
            raise AssertionError("Preserved source bytes differ")
    (output / "sample.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    (output / "geometry-audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(output=str(output), physical_sensitive_slabs=2304, material_changes=totals,
                         detector_sha256=report["output_hashes"]["detector.xml"]), indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.output)
