"""Composition controls; source exporters retain their component geometry tests."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from export import compose, export as export_baseline, write


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

    def test_tracker_hardcoded_material_names_and_beam_id_preserved(self):
        tracker = self.component("beam", 0)
        report = compose([("tracker", tracker, {0: 0})], self.root / "out", "LAYOUT-001")
        doc = ET.parse(self.root / "out/detector.xml")
        self.assertEqual(report["system_ids"], [0])
        self.assertEqual(doc.find("detectors/detector/piece").get("material"), "Sensor")
        recipes = ET.parse(self.root / "out/materials.xml")
        self.assertIsNotNone(recipes.find("material[@name='Sensor']"))
        self.assertEqual(recipes.find("material/fraction").get("ref"), "Si")

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

    def baseline_fixture_backend(self, calls, *, omit_envelopes=False):
        """Replace expensive source generation, exercising real orchestration/composition.

        Fixture solids are intentionally not a native detector model. The
        regression checks option propagation, selected XML hierarchy and the
        manifest guard; component/native geometry controls remain separate.
        """
        def run(command, *, check, cwd):
            self.assertTrue(check)
            calls.append(command)
            script = Path(command[2])
            directory = Path(command[command.index("--output") + 1])
            directory.mkdir(parents=True, exist_ok=True)
            tracker = script.parent.name == "tracker_dd4hep"
            lar = script.parent.name == "lar_calorimeter"
            barrel = script.name == "barrel_export.py"
            ident = 0 if tracker else (10 if barrel else 11) if lar else 8
            fixture = self.component("fixture" + str(len(calls)), ident)
            tree = ET.parse(fixture)
            detector = tree.find("detectors/detector")
            if not omit_envelopes and "--real-periods" in command:
                for i in range(1 if barrel else 3):
                    parent = ET.SubElement(detector, "period" if barrel else "wheel", index=str(i))
                    ET.SubElement(parent, "period_envelope", policy="real-periods-v1")
            if not omit_envelopes and "--real-wedges" in command:
                ET.SubElement(detector, "wedge_envelope")
            filename = "tracker.xml" if tracker else ("barrel.xml" if barrel else "endcaps.xml") if lar else "calorimeter.xml"
            write(directory / filename, tree.getroot())
            (directory / "materials.xml").write_bytes((fixture.parent / "materials.xml").read_bytes())
            (directory / "expected.json").write_text('{"scope":"orchestration test fixture"}\n')
        return run

    def test_maintained_lar_export_selects_real_periods_with_services(self):
        calls = []
        with patch("export.subprocess.run", side_effect=self.baseline_fixture_backend(calls)):
            report = export_baseline("LAYOUT-002", self.root / "baseline")
        self.assertEqual(len(calls), 3)
        for command, service in zip(calls[1:], ("barrel_services.py", "endcap_services.py")):
            self.assertIn("--real-periods", command)
            self.assertNotIn("--real-wedges", command)
            self.assertEqual(Path(command[command.index("--services") + 1]).name, service)
        self.assertEqual(report["ecal_placement"], {
            "lar-barrel": {"policy": "real-periods-v1", "reusable_envelopes": 1},
            "lar-endcaps": {"policy": "real-periods-v1", "reusable_envelopes": 3}})
        doc = ET.parse(self.root / "baseline/detector.xml")
        self.assertEqual(len(doc.findall("detectors/detector/period/period_envelope")), 1)
        self.assertEqual(len(doc.findall("detectors/detector/wheel/period_envelope")), 3)
        self.assertEqual(report["system_ids"], [0, 10, 11])

    def test_maintained_siw_export_keeps_real_wedges(self):
        calls = []
        with patch("export.subprocess.run", side_effect=self.baseline_fixture_backend(calls)):
            report = export_baseline("LAYOUT-001", self.root / "baseline")
        for command in calls[1:]:
            self.assertIn("--real-wedges", command)
            self.assertNotIn("--real-periods", command)
            self.assertNotIn("--services", command)
        self.assertEqual(report["ecal_placement"], {
            "siw-barrel": {"policy": "real-wedges", "reusable_envelopes": 1},
            "siw-endcaps": {"policy": "real-wedges", "reusable_envelopes": 1}})
        self.assertEqual(report["system_ids"], [0, 8, 9])

    def test_maintained_export_rejects_missing_selected_hierarchy(self):
        calls = []
        with patch("export.subprocess.run", side_effect=self.baseline_fixture_backend(calls, omit_envelopes=True)):
            with self.assertRaisesRegex(ValueError, "selected reusable placement"):
                export_baseline("LAYOUT-002", self.root / "baseline")


if __name__ == "__main__":
    unittest.main()
