#!/usr/bin/env python3
"""Generate the centralized DES-024 passive pipe and vacuum bore."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def export(config, output):
    for key in ("inner_radius_mm", "wall_mm", "half_length_mm", "density_g_cm3", "vacuum_density_g_cm3"):
        if not math.isfinite(config[key]) or config[key] <= 0:
            raise ValueError("Positive finite " + key + " required")
    if config["system_id"] != 0:
        raise ValueError("Passive beampipe reserves system ID 0")
    ri, wall, hz = (config[k] for k in ("inner_radius_mm", "wall_mm", "half_length_mm"))
    sizes = config["world_half_size_mm"]
    if len(sizes) != 3 or any(not math.isfinite(v) or v <= 0 for v in sizes) or min(sizes[:2]) <= ri + wall or sizes[2] <= hz:
        raise ValueError("World must contain pipe with positive clearance")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    doc = ET.Element("lccdd")
    ET.SubElement(doc, "info", name="nODDBeamPipe", title="DES-024 straight Be pipe", author="nODD", version="0.1", status="prototype")
    ET.SubElement(ET.SubElement(doc, "includes"), "gdmlFile", ref="materials.xml")
    definitions = ET.SubElement(doc, "define")
    for axis, size in zip("xyz", sizes):
        ET.SubElement(definitions, "constant", name="world_" + axis, value=f"{size:.17g}*mm")
    display = ET.SubElement(doc, "display")
    ET.SubElement(display, "vis", name="BeamPipeVis", r="0.55", g="0.65", b="0.7", alpha="0.8", showDaughters="true", visible="true")
    ET.SubElement(display, "vis", name="BoreVis", visible="false")
    detector = ET.SubElement(ET.SubElement(doc, "detectors"), "detector", name="BeamPipe", id="0", type="nODDBeamPipe")
    ET.SubElement(detector, "dimensions", rmin=f"{ri:.17g}*mm", rmax=f"{ri+wall:.17g}*mm", half_length=f"{hz:.17g}*mm")
    materials = ET.Element("materials")
    # Complete pinned element table avoids ROOT sparse-Z mixture behavior.
    elements = json.loads((ROOT / "detector/config/elements.json").read_text())["elements"]
    for item in elements:
        e = ET.SubElement(materials, "element", name=item["name"], formula=item["name"], Z=str(item["Z"]))
        ET.SubElement(e, "atom", type="A", value=str(item["A"]), unit="g/mol")
    for name, density, composition in (("Beryllium", config["density_g_cm3"], {"Be": 1}), ("Vacuum", config["vacuum_density_g_cm3"], {"H": 1}), ("Air", 0.0012, {"N": .754, "O": .234, "Ar": .012})):
        material = ET.SubElement(materials, "material", name=name)
        ET.SubElement(material, "D", value=str(density), unit="g/cm3")
        for ref, fraction in composition.items():
            ET.SubElement(material, "fraction", n=str(fraction), ref=ref)
    for path, tree in ((output / "beampipe.xml", doc), (output / "materials.xml", materials)):
        ET.indent(tree, space="  ")
        ET.ElementTree(tree).write(path, encoding="utf-8", xml_declaration=True)
    volume = math.pi * ((ri + wall)**2 - ri**2) * 2 * hz
    expected = dict(config=config, outer_radius_mm=ri+wall, wall_volume_mm3=volume, wall_mass_g=volume*config["density_g_cm3"]/1000, sensitive_count=0,
                    config_sha256=hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest())
    (output / "expected.json").write_text(json.dumps(expected, indent=2) + "\n")
    return expected


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "detector/config/beampipe.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export(json.loads(args.config.read_text()), args.output)
