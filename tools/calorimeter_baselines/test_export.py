"""Composition controls; source exporters retain their component geometry tests."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from export import compose, write


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def component(self, name, ident, density="2.3", world=6000):
        directory = self.root / name
        directory.mkdir()
        material = ET.fromstring(f'<materials><element name="Si" formula="Si" Z="14"><atom value="28"/></element>'
                                 f'<material name="Sensor"><D value="{density}" unit="g/cm3"/><fraction n="1" ref="Si"/></material></materials>')
        write(directory / "materials.xml", material)
        doc = ET.fromstring(f'<lccdd><includes><gdmlFile ref="materials.xml"/></includes>'
                            f'<define><constant name="world_x" value="{world}*mm"/><constant name="world_y" value="{world}*mm"/>'
                            f'<constant name="world_z" value="8000*mm"/></define>'
                            f'<readouts><readout name="{name}Hits"><id>system:8,layer:8</id></readout></readouts>'
                            f'<detectors><detector name="{name}" id="{ident}" type="TestFixture" readout="{name}Hits">'
                            f'<piece name="sensitive" material="Sensor" x="1*mm" cooling_material="Sensor"/></detector></detectors></lccdd>')
        write(directory / "component.xml", doc)
        return directory / "component.xml"

    def test_system_remap_namespaces_and_geometry_preservation(self):
        barrel = self.component("barrel", 8)
        endcap = self.component("endcap", 8, density="2.4", world=7000)
        before = {p: p.read_bytes() for c in (barrel, endcap) for p in (c, c.parent / "materials.xml")}
        report = compose([("barrel", barrel, {8: 8}), ("endcap", endcap, {8: 9})], self.root / "combined", "LAYOUT-001")
        doc = ET.parse(self.root / "combined/detector.xml")
        self.assertEqual(report["system_ids"], [8, 9])
        self.assertEqual([x.get("material") for x in doc.findall("detectors/detector/piece")], ["barrel_Sensor", "endcap_Sensor"])
        self.assertEqual([x.get("x") for x in doc.findall("detectors/detector/piece")], ["1*mm", "1*mm"])
        self.assertEqual([x.get("cooling_material") for x in doc.findall("detectors/detector/piece")], ["barrel_Sensor", "endcap_Sensor"])
        recipes = ET.parse(self.root / "combined/materials.xml")
        self.assertEqual([x.get("ref") for x in recipes.findall("material/fraction")], ["barrel_Si", "endcap_Si"])
        self.assertEqual(doc.find("define/constant[@name='world_x']").get("value"), "7000*mm")
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_duplicate_or_unmapped_ids_fail(self):
        a = self.component("a", 8)
        b = self.component("b", 8)
        for mapping in ({8: 8}, {}, {8: 256}):
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                compose([("a", a, {8: 8}), ("b", b, mapping)], self.root / "out", "LAYOUT-001")

    def test_conflicting_duplicate_component_materials_fail(self):
        a = self.component("a", 10)
        b = self.component("b", 11, density="3")
        for path in (a.parent / "materials.xml", b.parent / "materials.xml"):
            doc = ET.parse(path).getroot()
            doc.find("material").set("name", "Air")
            write(path, doc)
        with self.assertRaisesRegex(ValueError, "Conflicting shared"):
            compose([("same", a, {10: 10}), ("same", b, {11: 11})], self.root / "out", "LAYOUT-002")

    def test_unexpected_include_or_field_fails(self):
        a = self.component("a", 10)
        original = ET.parse(a).getroot()
        for tag in ("fields", "include"):
            doc = deepcopy(original)
            if tag == "fields":
                ET.SubElement(doc, tag)
            else:
                ET.SubElement(doc.find("includes"), "gdmlFile", ref="hidden.xml")
            write(a, doc)
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                compose([("a", a, {10: 10})], self.root / "out", "LAYOUT-002")


if __name__ == "__main__":
    unittest.main()
