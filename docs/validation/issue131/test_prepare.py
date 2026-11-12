"""Small synthetic inputs test benchmark exclusions without native dependencies."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from run_pilot import prepare, sha


class PreparationTests(unittest.TestCase):
    def fixture(self, directory, *, fields=False, wedge=True):
        baseline = directory / "baseline"
        baseline.mkdir()
        root = ET.Element("lccdd")
        ET.SubElement(root, "info")
        if fields:
            ET.SubElement(root, "fields")
        detectors = ET.SubElement(root, "detectors")
        readouts = ET.SubElement(root, "readouts")
        for system in range(10):
            name = {8: "BARREL", 9: "EDGE"}.get(system, f"test_tracker_{system}")
            node = ET.SubElement(detectors, "detector", id=str(system), name=name)
            ET.SubElement(node, "test_component", material="test_material", size="1*mm")
            if system in (8, 9) and wedge:
                ET.SubElement(node, "wedge_envelope", material="test_material")
            ET.SubElement(readouts, "readout", name=name + "Hits")
        ET.ElementTree(root).write(baseline / "detector.xml")
        (baseline / "materials.xml").write_text('<materials name="test_fixture_only"/>')
        (baseline / "baseline.json").write_text(json.dumps({
            "compact_sha256": sha(baseline / "detector.xml"),
            "materials_sha256": sha(baseline / "materials.xml"),
        }))
        output = directory / "run"
        output.mkdir()
        return baseline, output

    def test_only_ecal_retained_without_changing_ecal_or_materials(self):
        with tempfile.TemporaryDirectory() as temporary:
            baseline, output = self.fixture(Path(temporary))
            before = ET.parse(baseline / "detector.xml").findall("detectors/detector")[-2:]
            samples = prepare(output, baseline)
            after = ET.parse(output / "detector.xml").findall("detectors/detector")
            self.assertEqual([ET.tostring(node) for node in after],
                             [ET.tostring(node) for node in before])
            self.assertEqual((output / "materials.xml").read_bytes(),
                             (baseline / "materials.xml").read_bytes())
            self.assertEqual(sum(sample["events"] for sample in samples), 100)
            self.assertEqual({node.get("name") for node in
                              ET.parse(output / "detector.xml").findall("readouts/readout")},
                             {"BARRELHits", "EDGEHits"})

    def test_field_and_legacy_hierarchy_are_rejected(self):
        for options in ({"fields": True}, {"wedge": False}):
            with self.subTest(options=options), tempfile.TemporaryDirectory() as temporary:
                baseline, output = self.fixture(Path(temporary), **options)
                with self.assertRaises(AssertionError):
                    prepare(output, baseline)

    def test_changed_input_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            baseline, output = self.fixture(Path(temporary))
            with (baseline / "materials.xml").open("a") as stream:
                stream.write("<!-- test corruption -->")
            with self.assertRaises(AssertionError):
                prepare(output, baseline)


if __name__ == "__main__":
    unittest.main()
