"""Isolated physical four-family board staggering; native factories unchanged.

PROTOTYPE TEST ONLY. Carrier seams, support, absorber, cooling and layer planes
are inherited. Full barrel slabs shift 48 mm axially away from their bays;
short slabs use the prospectively specified 24-mm feasibility adaptation.
Tangential half-phase uses real narrow edge boards and complete ASIC stacks.
"""
import argparse
from collections import Counter, defaultdict
import copy
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

from angular_sample import ROOT, save, sha
from untiled_geometry import EXPECTED, canonical, location, mm, number, pose, primitive_volume, wafer_volume

HARDWARE = ROOT / "tools/calorimeter_hardware"
if str(HARDWARE) not in sys.path:
    sys.path.insert(0, str(HARDWARE))
from barrel_layout import build as barrel_layout
from edge_layout import (area, contains, intersect, pack, pad_mask, rectangle,
                         build as edge_layout)
from edge_export import hardware as edge_hardware, encode_geometry

PHASES = ((0., 0.), (48., 0.), (0., 48.), (48., 48.))
SHORT_AXIAL_PHASE_MM = 24.
NARROW_IDS = 700
ENDCAP_ID_BLOCK = 256


def set_width(node, width):
    if node.get("kind") != "xtru":
        raise ValueError("Expected rectangular extruded board film")
    vertices = node.findall("vertex")
    if len(vertices) != 4:
        raise ValueError("Expected rectangular board film")
    old = [number(v.get("x")) for v in vertices]
    center = (min(old) + max(old)) / 2
    if abs(center) > 1e-8:
        raise ValueError("Original film is not centred")
    for vertex, x in zip(vertices, old):
        vertex.set("x", mm(math.copysign(width / 2, x)))


def half_board(original):
    """46x94 PCB, 42x90 wafer, 40x88 active; two complete ASIC stacks."""
    result = ET.Element("board", name="half_tangent")
    widths = dict(active=40., guard=42., bias_PI=42., bias_Cu=42., glue=42.,
                  pad=40., PCB_G10=46., PCB_Cu=46.)
    for source in original.findall("piece"):
        suffix = source.get("name").removeprefix("square_")
        match = re.fullmatch(r"a([0-3])_(.+)", suffix)
        if match and int(match[1]) >= 2:
            continue
        piece = copy.deepcopy(source)
        piece.set("name", "half_" + suffix)
        if match:
            piece.set("x", "0*mm")
        else:
            if suffix not in widths:
                raise ValueError(f"Unexpected full-board constituent {suffix}")
            set_width(piece, widths[suffix])
            if suffix == "guard":
                cut, = piece.findall("cut")
                set_width(cut, 40.)
        result.append(piece)
    if len(result.findall("piece")) != 16:
        raise ValueError("Narrow board must contain eight films and two four-part ASIC stacks")
    return result


def tangent_boards(columns, half_phase):
    """Return (u, family, column) at exactly the retained outer PCB span."""
    if columns < 2 or columns > 8:
        raise ValueError("Unsupported original barrel column count")
    centers = [(j - (columns - 1) / 2) * 96. for j in range(columns)]
    if not half_phase:
        return [(u, "square", j) for j, u in enumerate(centers)]
    edge = 48. * columns - 24.
    return [(-edge, "half_tangent", 0)] + [(u + 48., "square", j) for j, u in enumerate(centers[:-1])] + [(edge, "half_tangent", 1)]


def panel_rows(panel, axial_phase):
    amount = (SHORT_AXIAL_PHASE_MM if panel["kind"] == "short" else axial_phase) if axial_phase else 0.
    rows = [z - panel["bay_sign"] * amount for z in panel["row_centers_mm"]]
    cavity = panel["length_mm"] / 2 - 5.
    edge_clearances, bay_clearances = [], []
    for z in rows:
        edge_clearances.append(cavity - abs(z - panel["center_mm"]) - 47.)
        bay_clearances.append(abs(z - panel["bay_center_mm"]) - 47. - 20.)
    if min(edge_clearances) < -1e-8 or min(bay_clearances) < 2 - 1e-8:
        raise ValueError("Shifted barrel board violates frame/bay clearance")
    return rows, amount, min(edge_clearances), min(bay_clearances)


def mask_table(segmentation, profiles):
    """Write every physical local active mask and clipped edge electrode."""
    polygons, cells = [], []
    for identifier, profile in sorted(profiles.items()):
        poly = profile["active"]
        polygons += [identifier, len(poly)] + [v for p in poly for v in p]
        if profile.get("full", False):
            continue
        pads = profile.get("pads") or pad_mask(poly, 5.5, .2 * 5.5**2)
        for electrode in pads:
            for raw in electrode["members"]:
                cells += [identifier, *raw, *electrode["key"], *electrode["reference_mm"], *electrode["bbox_mm"]]
    segmentation.attrib.update(type="nODDEdgeGrid", grid_size_x="5.5*mm", grid_size_y="5.5*mm", offset_x="2.75*mm", offset_y="2.75*mm",
                              sensor_polygons_mm=" ".join(f"{v:.17g}" for v in polygons))
    if cells:
        segmentation.set("cell_table_mm", " ".join(f"{v:.17g}" for v in cells))
    else:
        segmentation.attrib.pop("cell_table_mm", None)


def part_volume(piece):
    if piece.findall("cut"):
        return wafer_volume(piece)
    return primitive_volume(piece)


def material_board(parts, copies):
    result = defaultdict(float)
    for piece in parts:
        result[piece.get("material")] += part_volume(piece) * copies
    return result


def add_material(total, values, sign=1.):
    for key, value in values.items():
        total[key] += sign * value


def validate_modules(modules, *, channels_limit=None):
    """Physical containment, disjoint boards, finite masks and readout capacity."""
    boxes = []
    for module in modules:
        if not 0 <= module["index"] < 1024:
            raise ValueError("Module does not fit ten-bit field")
        for inner, outer in (("sensor", "board"), ("active", "sensor")):
            if not all(contains(module[outer], *p) for p in module[inner]):
                raise ValueError("PCB/wafer/active containment failed")
        if len(module["pads"]) > 64 * len(module["asics"]):
            raise ValueError("ASIC channel capacity insufficient")
        for x, y in module["asics"]:
            if not all(contains(module["board"], *v) for v in rectangle(x - 5.5, y - 6.5, 11., 13.)):
                raise ValueError("ASIC/package clearance outside PCB")
        for i, (x, y) in enumerate(module["asics"]):
            if any(abs(x - u) < 11 - 1e-8 and abs(y - v) < 13 - 1e-8 for u, v in module["asics"][i + 1:]):
                raise ValueError("ASIC packages overlap")
        for electrode in module["pads"]:
            if electrode["area_mm2"] < .2 * 5.5**2 - 1e-8:
                raise ValueError("Undersized readout electrode")
        if abs(sum(p["area_mm2"] for p in module["pads"]) - area(module["active"])) > 1e-6:
            raise ValueError("Readout pads do not partition active mask")
        cx, cy = module["center_mm"]
        board = [[x + cx, y + cy] for x, y in module["board"]]
        boxes.append((board, [min(p[k] for p in board) for k in (0, 1)], [max(p[k] for p in board) for k in (0, 1)]))
    if len({m["index"] for m in modules}) != len(modules):
        raise ValueError("Repeated physical module ID")
    for i, (board, lo, hi) in enumerate(boxes):
        for other, lo2, hi2 in boxes[i + 1:]:
            if all(min(hi[k], hi2[k]) - max(lo[k], lo2[k]) > 1e-7 for k in (0, 1)) and area(intersect(board, other)) > 1e-6:
                raise ValueError("Physical PCBs overlap")
    if channels_limit is not None and sum(len(m["pads"]) for m in modules) > channels_limit:
        raise ValueError("Existing interface channel capacity exceeded")


def barrel_transform(detector, readout, report):
    baseline, _ = barrel_layout()
    original, = detector.findall("board")
    narrow = half_board(original)
    detector.append(narrow)
    templates = {b.get("name"): b for b in detector.findall("board")}
    full_mask = rectangle(-44., -44., 88., 88.)
    half_mask = rectangle(-20., -44., 40., 88.)
    profiles = {}
    material_delta = defaultdict(float)
    layers = []
    for layer in baseline["layers"]:
        index = layer["index"]
        region, = [r for r in detector.findall("region") if r.get("name") == f"barrel_layer{index}"]
        before_passive = [canonical(p) for p in region.findall("piece")]
        original_instances = region.findall("board_instance")
        if len(original_instances) != len(layer["modules"]):
            raise ValueError("Retained barrel XML and source packing differ")
        add_material(material_delta, material_board(original.findall("piece"), len(original_instances) * 16), -1)
        for instance in original_instances:
            region.remove(instance)
        tangent, axial = PHASES[index % 4]
        modules, panels = [], []
        base = layer["front_mm"] + baseline["ecal"]["absorber_mm"]
        for panel in layer["panels"]:
            rows, actual, edge_clearance, bay_clearance = panel_rows(panel, axial)
            panel_modules = []
            for row, z in enumerate(rows, panel["first_row"]):
                for u, family, column in tangent_boards(layer["columns"], bool(tangent)):
                    module_id = row * 8 + column if family == "square" else NARROW_IDS + 2 * row + column
                    frame = ((0., 0., 1.), (1., 0., 0.), (0., 1., 0.)) if z >= 0 else ((0., 0., 1.), (-1., 0., 0.), (0., -1., 0.))
                    pose(ET.SubElement(region, "board_instance", template=family, module=str(module_id)), (base, u, z), frame)
                    profile = dict(active=full_mask if family == "square" else half_mask, full=family == "square")
                    if module_id in profiles and profiles[module_id] != profile:
                        raise ValueError("Module ID reused for a different local mask")
                    profiles[module_id] = profile
                    module = dict(index=module_id, row=row, center_mm=[u, z], family=family,
                                  channels=256 if family == "square" else 128, asics=4 if family == "square" else 2)
                    modules.append(module); panel_modules.append(module)
            interfaces = [x for x in layer["interfaces"] if x["panel"] == panel["index"]]
            channels = sum(m["channels"] for m in panel_modules)
            if channels != panel["board_rows"] * layer["columns"] * 256 or channels > len(interfaces) * 8192:
                raise ValueError("Barrel regrouping changed capacity or exceeds existing interfaces")
            # Interfaces stay physically unchanged; assign whole 64-channel
            # ASIC payloads to their existing 8192-channel capacities.
            allocation = []
            for module in panel_modules:
                for chip in range(module["asics"]):
                    allocation.append((module["index"], chip))
            groups = [allocation[i * 128:(i + 1) * 128] for i in range(len(interfaces))]
            if sum(map(len, groups)) != len(allocation):
                raise ValueError("ASIC-to-interface ownership incomplete")
            panels.append(dict(index=panel["index"], kind=panel["kind"], axial_shift_away_bay_mm=actual,
                 minimum_frame_clearance_mm=edge_clearance, minimum_bay_gap_mm=bay_clearance,
                 board_rows=len(rows), interface_assigned_channels=[64 * len(g) for g in groups]))
        counts = Counter(m["family"] for m in modules)
        for family, count in counts.items():
            add_material(material_delta, material_board(templates[family].findall("piece"), count * 16))
        if [canonical(p) for p in region.findall("piece")] != before_passive:
            raise AssertionError("Common barrel hardware changed")
        if max(m["index"] for m in modules) >= 1024:
            raise ValueError("Barrel module field overflow")
        layers.append(dict(layer=index, tangent_phase_mm=tangent, axial_full_phase_mm=axial,
                           retained_slab_phase_mm=layer["phase_mm"], panels=panels, modules=modules,
                           family_counts_per_sector=dict(counts), channels_per_sector=sum(m["channels"] for m in modules)))
    mask_table(readout.find("segmentation"), profiles)
    report["barrel"] = dict(layers=layers, module_mask_ids=len(profiles), narrow_ids_start=NARROW_IDS,
          active_area_delta_per_halfphased_row_mm2=-704., wafer_area_delta_per_halfphased_row_mm2=-540.,
          narrow_board_geometry_mm=dict(pcb=[46, 94], wafer=[42, 90], active=[40, 88]),
          short_axial_phase_mm=SHORT_AXIAL_PHASE_MM, half_board_asics=[[0, -22], [0, 22]],
          interfaces="Existing physical interfaces retained; 64-channel ASIC payloads regrouped within 8192-channel capacity",
          cooling="Original cold plates, tubes and water retained unchanged")
    return material_delta


def endcap_transform(detector, readout, report):
    baseline, layouts, _ = edge_layout()
    config = baseline["config"]
    ecal = json.loads((HARDWARE / "cassettes.json").read_text())["ecal"]
    source, = [r for r in detector.findall("region") if r.get("name") == "edge_layer"]
    owned = [p for p in source.findall("piece") if re.match(r"edge_m\d+_", p.get("name", ""))]
    common = [p for p in source.findall("piece") if p not in owned]
    interface_count = sum(p.get("name", "").startswith("interface_") and p.get("role") == "interface" for p in common)
    if not interface_count:
        raise ValueError("No existing endcap interfaces")
    original_material = material_board(owned, 48 * 32)
    detector.remove(source)
    family_reports, profiles = [], {}
    material_delta = defaultdict(float)
    add_material(material_delta, original_material, -1)
    for phase, (tangent, radial) in enumerate(PHASES):
        layout = pack(config, ecal, baseline["outer_polygon_mm"], layouts["edges"]["phase_mm"] + radial, True,
                      tangent_phase_mm=tangent, inner_partial_row=bool(radial))
        raw_max = max(m["index"] for m in layout["modules"])
        if raw_max >= ENDCAP_ID_BLOCK:
            raise ValueError("Endcap phase family exceeds its ten-bit ID block")
        for module in layout["modules"]:
            module["index"] += phase * ENDCAP_ID_BLOCK
        validate_modules(layout["modules"], channels_limit=interface_count * 8192)
        hardware, _ = edge_hardware(baseline, layout)
        region = ET.SubElement(detector, "region", name=f"edge_layer_phase{phase}")
        for piece in common:
            region.append(copy.deepcopy(piece))
        pieces = []
        for part in hardware["layer_parts"]:
            if not re.match(r"edge_m\d+_", part["name"]):
                continue
            node = ET.SubElement(region, "piece", name=part["name"], role=part["role"], material="siw_endcaps_" + part["material"])
            encode_geometry(node, part)
            if "module" in part:
                node.set("module", str(part["module"]))
            pieces.append(node)
        add_material(material_delta, material_board(pieces, 12 * 32))
        for module in layout["modules"]:
            if module["index"] in profiles:
                raise ValueError("Duplicate endcap mask ID")
            profiles[module["index"]] = module
        family_reports.append(dict(phase=phase, tangent_phase_mm=tangent, radial_phase_mm=radial,
            module_id_offset=phase * ENDCAP_ID_BLOCK, modules=layout["modules"],
            channels_per_sector=sum(len(m["pads"]) for m in layout["modules"]),
            installed_asic_channels_per_sector=64 * sum(len(m["asics"]) for m in layout["modules"]),
            existing_interface_capacity_per_sector=interface_count * 8192,
            active_area_per_sector_mm2=layout["active_area_mm2"], rejected=layout["rejected"]))
        if [canonical(p) for p in region.findall("piece") if not re.match(r"edge_m\d+_", p.get("name", ""))] != [canonical(p) for p in common]:
            raise AssertionError("Endcap common passive geometry changed")
    for replica in detector.findall("replica"):
        if replica.get("region") == "edge_layer":
            replica.set("region", f"edge_layer_phase{int(replica.get('layer')) % 4}")
    mask_table(readout.find("segmentation"), profiles)
    report["endcap"] = dict(families=family_reports, layers_per_family=12,
                            original_radial_phase_mm=layouts["edges"]["phase_mm"], module_id_block=ENDCAP_ID_BLOCK,
                            common_hardware="Original absorber, skins, cooling, interfaces and support unchanged")
    return material_delta


def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    for name, expected in EXPECTED.items():
        if sha(source / name) != expected:
            raise ValueError(f"Unsupported original tiled input hash: {name}")
    manifest = json.loads((source / "sample.json").read_text())
    if manifest["events"] != 10000:
        raise ValueError("Expected matched ten-thousand-event sample")
    tree = ET.parse(source / "detector.xml")
    detectors = {d.get("name"): d for d in tree.findall("./detectors/detector")}
    readouts = {r.get("name"): r for r in tree.findall("./readouts/readout")}
    if set(detectors) != {"BARREL", "EDGE"} or tree.find("fields") is not None:
        raise ValueError("Expected retained ECAL-only zero-field compact")
    for readout in readouts.values():
        if readout.findtext("id") != "system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6":
            raise ValueError("Unexpected baseline readout capacity")
    envelopes = {name: canonical(d.find("wedge_envelope")) for name, d in detectors.items()}
    replicas = {name: [{k: v for k, v in p.attrib.items() if k != "region"} for p in d.findall("replica")] for name, d in detectors.items()}
    report = dict(status="PROTOTYPE / PHYSICAL STAGGERING TEST", phases_mm=[list(p) for p in PHASES],
                  source_manifest_sha256=sha(source / "sample.json"), source_input_hashes={name: sha(source / name) for name in EXPECTED},
                  native_factory_changes=False, full_depth_carrier_seams="unchanged", layer_planes="unchanged")
    material_delta = barrel_transform(detectors["BARREL"], readouts["BARRELHits"], report)
    add_material(material_delta, endcap_transform(detectors["EDGE"], readouts["EDGEHits"], report))
    for name, detector in detectors.items():
        if canonical(detector.find("wedge_envelope")) != envelopes[name]:
            raise AssertionError("Navigation envelope changed")
        if [{k: v for k, v in p.attrib.items() if k != "region"} for p in detector.findall("replica")] != replicas[name]:
            raise AssertionError("Sector/layer transforms changed")
    densities = {m.get("name"): number(m.find("D").get("value")) for m in ET.parse(source / "materials.xml").findall(".//material") if m.find("D") is not None}
    report["material_changes"] = {name: dict(volume_delta_mm3=volume, mass_delta_g=volume * densities[name] / 1000) for name, volume in material_delta.items()}
    report["recipe_sha256"] = sha(__file__)
    report["edge_packer_sha256"] = sha(HARDWARE / "edge_layout.py")
    report["source_revision"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    output.mkdir(parents=True, exist_ok=False)
    for name in ("materials.xml", "particles.HEPEvt", "truth-input.jsonl"):
        shutil.copyfile(source / name, output / name)
    tree.find("info").set("title", "PROTOTYPE physical four-family board staggering; original carrier/support retained")
    ET.indent(tree)
    tree.write(output / "detector.xml", encoding="utf-8", xml_declaration=True)
    manifest["control"] = dict(type="physical-board-staggering", original_source_revision=manifest["source_revision"],
        original_sample_manifest_sha256=report["source_manifest_sha256"], phases_mm=report["phases_mm"],
        short_axial_phase_mm=SHORT_AXIAL_PHASE_MM, recipe_sha256=report["recipe_sha256"], edge_packer_sha256=report["edge_packer_sha256"])
    manifest["source_revision"] = report["source_revision"]
    manifest["geometry_source"] = "PROTOTYPE four physical board families; original support/absorber/cooling/planes/seams retained"
    manifest["hashes"] = {name: sha(output / name) for name in ("detector.xml", "materials.xml")}
    for name in ("materials.xml", "particles.HEPEvt", "truth-input.jsonl"):
        if sha(output / name) != EXPECTED[name]:
            raise AssertionError("Matched source bytes changed")
    report["output_compact_sha256"] = sha(output / "detector.xml")
    save(output / "sample.json", manifest)
    save(output / "geometry-audit.json", report)
    print(json.dumps(dict(output=str(output), compact_sha256=report["output_compact_sha256"],
                         barrel_physical_boards=sum(sum(q["family_counts_per_sector"].values()) for q in report["barrel"]["layers"]) * 16,
                         endcap_modules_per_family=[len(f["modules"]) for f in report["endcap"]["families"]],
                         material_changes=report["material_changes"]), indent=2), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.output)
