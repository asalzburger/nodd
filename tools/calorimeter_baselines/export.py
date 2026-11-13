#!/usr/bin/env python3
"""Select a working baseline and compose its maintained tracker and ECAL stage."""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OPTIONS = {
    "LAYOUT-001": (("siw-barrel", "tools/calorimeter_hardware/barrel_export.py", "calorimeter.xml", {8: 8}),
                   ("siw-endcaps", "tools/calorimeter_hardware/edge_export.py", "calorimeter.xml", {8: 9})),
    "LAYOUT-002": (("lar-barrel", "tools/lar_calorimeter/barrel_export.py", "barrel.xml", {10: 10}),
                   ("lar-endcaps", "tools/lar_calorimeter/endcap_export.py", "endcaps.xml", {11: 11})),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def signature(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple(signature(child) for child in node))


def write(path, node):
    ET.indent(node, space="  ")
    ET.ElementTree(node).write(path, encoding="utf-8", xml_declaration=True)


def compose(components, output, layout):
    """Namespace recipes together with their references; reject ambiguous roots."""
    if layout not in OPTIONS:
        raise ValueError("Unknown baseline: " + layout)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    doc = ET.Element("lccdd")
    ET.SubElement(doc, "info", name=layout + "TrackerECAL", title="Working tracker and ECAL baseline stage",
                  author="nODD", version="0.1", status="prototype")
    ET.SubElement(ET.SubElement(doc, "includes"), "gdmlFile", ref="materials.xml")
    sections = {name: ET.SubElement(doc, name) for name in ("define", "display", "readouts", "detectors")}
    material_doc = ET.Element("materials")
    material_seen = {}
    section_seen = {name: {} for name in sections}
    system_ids = set()
    world = {}
    records = []
    ecal_placement = {}
    for tag, compact, mapping in components:
        compact = Path(compact)
        source = ET.parse(compact).getroot()
        if source.tag != "lccdd" or source.find("fields") is not None:
            raise ValueError("Unsupported compact scope: " + tag)
        includes = source.findall("includes/gdmlFile")
        if len(includes) != 1 or includes[0].get("ref") != "materials.xml" or len(source.find("includes")) != 1:
            raise ValueError("Unexpected component includes: " + tag)
        materials = compact.parent / "materials.xml"
        recipes = ET.parse(materials).getroot()
        if recipes.tag != "materials":
            raise ValueError("Expected standalone material definitions: " + tag)
        names = {node.get("name"): (node.get("name") if tag == "tracker"
                                    else tag.replace("-", "_") + "_" + node.get("name"))
                 for node in recipes}
        for node in recipes:
            node = deepcopy(node)
            node.set("name", names[node.get("name")])
            for child in node.iter():
                if child.get("ref") in names:
                    child.set("ref", names[child.get("ref")])
            key = (node.tag, node.get("name"))
            sig = signature(node)
            if key in material_seen:
                if material_seen[key] != sig:
                    raise ValueError("Conflicting shared material/element: " + str(key))
            else:
                material_seen[key] = sig
                material_doc.append(node)
        transformed = source
        if tag != "tracker":
            periods = transformed.findall("detectors/detector/period/period_envelope") + transformed.findall("detectors/detector/wheel/period_envelope")
            wedges = transformed.findall("detectors/detector/wedge_envelope")
            if periods and not wedges and {node.get("policy") for node in periods} == {"real-periods-v1"}:
                policy, envelopes = "real-periods-v1", len(periods)
            elif wedges and not periods:
                policy, envelopes = "real-wedges", len(wedges)
            else:
                policy, envelopes = "legacy-or-unrecognized", len(periods) + len(wedges)
            ecal_placement[tag] = dict(policy=policy, reusable_envelopes=envelopes)
        for node in transformed.iter():
            for attr, value in list(node.attrib.items()):
                if (attr == "material" or attr.endswith("_material")) and value in names:
                    node.set(attr, names[value])
        root_map = []
        for node in transformed.findall("detectors/detector"):
            old = int(node.get("id"))
            if old not in mapping:
                raise ValueError("Unmapped detector system: " + tag + "/" + str(old))
            new = mapping[old]
            if not 0 <= new < 256 or new in system_ids:
                raise ValueError("Duplicate/out-of-range integrated system ID: " + str(new))
            system_ids.add(new)
            node.set("id", str(new))
            root_map.append(dict(name=node.get("name"), source_system_id=old, integrated_system_id=new))
        for section in sections:
            for node in transformed.findall(section + "/*"):
                name = node.get("name")
                if section == "define" and name in ("world_x", "world_y", "world_z"):
                    value = node.get("value", "")
                    if not value.endswith("*mm"):
                        raise ValueError("World dimension requires explicit mm")
                    world[name] = max(world.get(name, 0), float(value[:-3]))
                    continue
                if not name:
                    raise ValueError("Unnamed compact entry: " + tag + "/" + section)
                sig = signature(node) if section == "define" else True
                if name in section_seen[section]:
                    if section != "define" or section_seen[section][name] != sig:
                        raise ValueError("Duplicate/conflicting compact entry: " + section + "/" + name)
                else:
                    section_seen[section][name] = sig
                    sections[section].append(node)
        records.append(dict(component=tag, compact=str(compact.resolve()), compact_sha256=sha(compact),
                            materials_sha256=sha(materials), system_mapping=root_map))
    if set(world) != {"world_x", "world_y", "world_z"}:
        raise ValueError("Incomplete world dimensions")
    for name, value in sorted(world.items()):
        ET.SubElement(sections["define"], "constant", name=name, value=f"{value:.17g}*mm")
    write(output / "materials.xml", material_doc)
    write(output / "detector.xml", doc)
    report = dict(layout=layout, status="DRAFT / PROTOTYPE; native integration audit pending",
                  constructed=["supplied tracker component", "ECAL barrel", "ECAL endcaps"],
                  design_only={"solenoid": "DES026 allocation; no field installed",
                               "HCAL": "DES035-038 design options; LAr regional adaptation pending",
                               "FCAL": "Merged DES039 ROOT geometry; DD4hep/readout integration pending"},
                  digitization="Issue114 EDM4hep I/O and explicit-failure algorithm skeletons; no physical response",
                  reserved_future_system_ids={"FCAL": 12, "HCAL_barrel": 13, "HCAL_endcaps": 14},
                  components=records, system_ids=sorted(system_ids), exporter_sha256=sha(__file__),
                  ecal_placement=ecal_placement,
                  compact_sha256=sha(output / "detector.xml"), materials_sha256=sha(output / "materials.xml"))
    (output / "baseline.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def export(layout, output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    tracker = output / "components/tracker"
    subprocess.run([sys.executable, "-B", str(ROOT / "tools/tracker_dd4hep/export.py"),
                    "--output", str(tracker)], check=True, cwd=ROOT)
    tracker_compact = tracker / "tracker.xml"
    components = [("tracker", tracker_compact, {i: i for i in range(0, 8)})]
    for tag, script, filename, mapping in OPTIONS[layout]:
        directory = output / "components" / tag
        command = [sys.executable, "-B", str(ROOT / script), "--output", str(directory)]
        if layout == "LAYOUT-001":
            command.append("--real-wedges")
        else:
            service = "barrel_services.py" if tag == "lar-barrel" else "endcap_services.py"
            command += ["--services", str(ROOT / "tools/lar_calorimeter" / service), "--real-periods"]
        subprocess.run(command, check=True, cwd=ROOT)
        components.append((tag, directory / filename, mapping))
    report = compose(components, output, layout)
    policy, expected_counts = (("real-wedges", {"siw-barrel": 1, "siw-endcaps": 1}) if layout == "LAYOUT-001"
                               else ("real-periods-v1", {"lar-barrel": 1, "lar-endcaps": 3}))
    expected_placement = {tag: dict(policy=policy, reusable_envelopes=count) for tag, count in expected_counts.items()}
    if report["ecal_placement"] != expected_placement:
        raise ValueError("Maintained ECAL export did not produce the selected reusable placement hierarchy")
    config = json.loads((ROOT / "detector/config/tracker.json").read_text())
    report["tracker_generation"] = dict(
        status="Fresh maintained DES043 export in this invocation; reuse is unsupported",
        producer_sha256=sha(ROOT / "tools/tracker_dd4hep/export.py"),
        config_sha256={p: sha(ROOT / p) for p in ("detector/config/tracker.json", config["pixel_config"], config["short_strip_config"], config["strixel_selection"])},
        expected_sha256=sha(tracker / "expected.json"), compact_sha256=sha(tracker_compact),
        materials_sha256=sha(tracker / "materials.xml"))
    (output / "baseline.json").write_text(json.dumps(report, indent=2) + "\n")
    print(layout, "systems", report["system_ids"], "->", output / "detector.xml")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", choices=OPTIONS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export(args.layout, args.output)
