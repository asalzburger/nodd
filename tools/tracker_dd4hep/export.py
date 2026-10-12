#!/usr/bin/env python3
"""Assemble maintained subsystem exports, preserving recipes and transforms."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from services import reconcile
from aperture import enlarge_pixel_aperture

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = (
    ("beam", "beampipe", "beampipe.xml"),
    ("pixel", "pixel_detector_dd4hep", "pixel-detector.xml"),
    ("short_barrel", "short_strip_barrel", "short-strip-barrel.xml"),
    ("short_endcap", "short_strip_endcap", "short-strip-endcap.xml"),
    ("long_barrel", "long_strip_barrel", "long-strip.xml"),
    ("long_endcap", "long_strip_endcap", "long-strip.xml"),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, tree):
    ET.indent(tree, space="  ")
    ET.ElementTree(tree).write(path, encoding="utf-8", xml_declaration=True)


def rename_materials(detector, names):
    """Include named cooling materials, not only the generic material field."""
    for node in detector.iter():
        for attribute, value in list(node.attrib.items()):
            if attribute == "material" or attribute.endswith("_material"):
                if value in names:
                    node.set(attribute, names[value])


def export(output, pixel_aperture_mm=None):
    config = json.loads((ROOT / "detector/config/tracker.json").read_text())
    if pixel_aperture_mm is None:
        pixel_aperture_mm = config["pixel_passive_aperture_mm"]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    doc = ET.Element("lccdd")
    ET.SubElement(
        doc,
        "info",
        name="nODDTracker",
        title="DES-025 BeamPipe + selected Tracker",
        author="nODD",
        version="0.1",
        status="prototype",
    )
    ET.SubElement(ET.SubElement(doc, "includes"), "gdmlFile", ref="materials.xml")
    sections = {
        name: ET.SubElement(doc, name)
        for name in ("define", "display", "readouts", "detectors")
    }
    matdoc = ET.Element("materials")
    element_names = set()
    recipes = {}
    entities = []
    provenance = {}
    components = []
    world = [0.0, 0.0, 0.0]
    for key, tool, filename in COMPONENTS:
        directory = output / "components" / key
        subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "tools" / tool / "export.py"),
                "--output",
                str(directory),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        xml = ET.parse(directory / filename).getroot()
        material = ET.parse(directory / "materials.xml").getroot()
        expected = json.loads((directory / "expected.json").read_text())
        local_recipes = expected.get("materials", expected.get("material_recipes", {}))
        # Beam and pixel have their own recipes; shared strip base materials are
        # reused only after exact recipe equality (including referenced names).
        names = {}
        for node in material.findall("material"):
            old = node.get("name")
            recipe = local_recipes.get(old)
            if key in ("beam",):
                new = old
            elif key == "pixel":
                new = old if old in ("Air", "Vacuum") else key + "_" + old
            elif old not in recipes or recipes[old] == recipe:
                new = old
            else:
                new = key + "_" + old
            names[old] = new
        for node in material:
            node = copy.deepcopy(node)
            if node.tag == "element":
                if node.get("name") not in element_names:
                    element_names.add(node.get("name"))
                    matdoc.append(node)
                continue
            old = node.get("name")
            new = names[old]
            if any(x.get("name") == new for x in matdoc.findall("material")):
                if old in local_recipes and new not in recipes:
                    recipes[new] = copy.deepcopy(local_recipes[old])
                continue
            node.set("name", new)
            for child in node:
                if child.get("ref") in names:
                    child.set("ref", names[child.get("ref")])
            matdoc.append(node)
            if old in local_recipes:
                recipe = copy.deepcopy(local_recipes[old])
                recipe["composition"] = {
                    names.get(k, k): v for k, v in recipe["composition"].items()
                }
                recipes[new] = recipe
        for node in xml.findall("./define/constant"):
            name = node.get("name")
            if name.startswith("world_"):
                axis = "xyz".index(name[-1])
                world[axis] = max(
                    world[axis], float(node.get("value").removesuffix("*mm"))
                )
            elif name.startswith("tracker_region_"):
                continue
            else:
                sections["define"].append(copy.deepcopy(node))
        for node in xml.findall("./display/*"):
            sections["display"].append(copy.deepcopy(node))
        for node in xml.findall("./readouts/*"):
            sections["readouts"].append(copy.deepcopy(node))
        for detector in xml.findall("./detectors/detector"):
            detector = copy.deepcopy(detector)
            rename_materials(detector, names)
            if key not in ("beam", "pixel"):
                old_id, new_id = config["system_translation"][key]
                if int(detector.get("id")) != old_id:
                    raise ValueError("Unexpected source system ID: " + key)
                detector.set("id", str(new_id))
            for node in detector.iter():
                # Preserve pixel template names/references; strip factory names
                # are labels only, physical/readout IDs remain untouched.
                if (
                    key not in ("pixel", "beam")
                    and node is not detector
                    and node.get("name")
                ):
                    node.set("name", key + "_" + node.get("name"))
            sections["detectors"].append(detector)
        for entity in expected.get("entities", []):
            entity = copy.deepcopy(entity)
            if "material" in entity:
                entity["material"] = names[entity["material"]]
            if key not in ("pixel", "beam"):
                entity["name"] = key + "_" + entity["name"]
            if key not in ("beam", "pixel") and "ids" in entity:
                entity["source_system_id"] = entity["ids"]["system"]
                old_id, new_id = config["system_translation"][key]
                if entity["ids"]["system"] != old_id:
                    raise ValueError("Unexpected sensitive source system ID: " + key)
                entity["ids"]["system"] = new_id
            if "constituent_volumes_mm3" in entity:
                entity["constituent_volumes_mm3"] = {
                    names.get(k, k): v
                    for k, v in entity["constituent_volumes_mm3"].items()
                }
            entity["component"] = key
            entities.append(entity)
        components.append(
            dict(
                name=key,
                counts=expected.get("counts", {}),
                provenance=expected.get("provenance", {}),
                material_names=names,
            )
        )
        provenance[key] = {
            name: sha(directory / name)
            for name in (filename, "materials.xml", "expected.json")
        }
    for axis, value in zip("xyz", world):
        ET.SubElement(
            sections["define"],
            "constant",
            name="world_" + axis,
            value=f"{value:.17g}*mm",
        )
    ET.SubElement(
        sections["define"],
        "constant",
        name="tracker_region_rmax",
        value=f"{config['tracker_region_rmax_mm']:.17g}*mm",
    )
    ET.SubElement(
        sections["define"],
        "constant",
        name="tracker_region_zmax",
        value=f"{config['tracker_region_zmax_mm']:.17g}*mm",
    )
    entities, reconciliation = reconcile(doc, matdoc, entities, recipes)
    aperture_amendment = (
        enlarge_pixel_aperture(doc, matdoc, entities, recipes, pixel_aperture_mm)
        if pixel_aperture_mm > 27
        else []
    )
    report = dict(
        status="DRAFT",
        config=config,
        pixel_aperture_amendment=aperture_amendment,
        service_reconciliation=reconciliation,
        entities=entities,
        materials=recipes,
        components=components,
        source_hashes=provenance,
        beam=json.loads((output / "components/beam/expected.json").read_text()),
        exporter_sha256=sha(Path(__file__)),
        assembly_source_hashes={
            str(p.relative_to(ROOT)): sha(p)
            for p in (
                Path(__file__),
                Path(__file__).with_name("services.py"),
                Path(__file__).with_name("aperture.py"),
                ROOT / "detector/config/tracker.json",
            )
        },
    )
    write(output / "tracker.xml", doc)
    write(output / "materials.xml", matdoc)
    (output / "expected.json").write_text(
        json.dumps(report, separators=(",", ":")) + "\n"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--pixel-aperture-mm",
        type=float,
        help="Explicit candidate amendment; no sensor change",
    )
    parser.add_argument(
        "--keep-pixel-aperture",
        action="store_true",
        help="Unamended control; overlaps the new pipe and must fail validation",
    )
    args = parser.parse_args()
    export(args.output, 27 if args.keep_pixel_aperture else args.pixel_aperture_mm)
