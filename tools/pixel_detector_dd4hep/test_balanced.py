"""Source-level DES040 integration against the preserved explicit reference."""

import copy
import importlib.util
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("balanced_combined", HERE / "export.py")
combined = importlib.util.module_from_spec(spec)
spec.loader.exec_module(combined)
ROOT = combined.ROOT


def number(node, key):
    return float(node.get(key).split("*")[0])


class BalancedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.tmp.name)
        cls.config = combined.read(ROOT / "detector/config/pixel-detector-balanced.json")
        cls.actual = combined.export(cls.config, cls.folder / "balanced")
        cls.reference = combined.export(combined.read(ROOT / "detector/config/pixel-detector-trimmed.json"), cls.folder / "reference")
        cls.xml = ET.parse(cls.folder / "balanced/pixel-detector.xml").getroot()
        cls.oldxml = ET.parse(cls.folder / "reference/pixel-detector.xml").getroot()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_default_cli_and_human_selected_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, "-B", str(HERE / "export.py"), "--output", directory], check=True, capture_output=True)
            actual = combined.read(Path(directory) / "expected.json")
        self.assertEqual(actual["counts"]["sensitive"], 12410)
        self.assertEqual(actual["counts"]["module"], 5666)
        self.assertEqual(actual["counts"]["disc"], 20)
        selected = combined.read(ROOT / "docs/design/inputs/DES-040-balanced-selection.json")["parameters"]
        placement = actual["provenance"]["placement"]
        self.assertEqual(placement["pixel_barrel_radii_mm"], [31.5, 57, 96, 182])
        self.assertEqual(placement["pixel_barrel_staves"], [12, 22, 18, 30])
        self.assertEqual(placement["pixel_disks_abs_z_mm"], selected["pixel_disks_abs_z_mm"])
        self.assertEqual(placement["additional_pixel_disk"], selected["additional_pixel_disk"])

    def test_every_sensitive_identity_and_rigid_transform(self):
        old = {tuple(e["ids"].values()): e for e in self.reference["entities"] if e["role"] == "sensitive"}
        seen, sources = set(), set()
        datums = [615, 865, 1115, 1333, 1565, 1780, 2090, 2440, 3070, 950]
        reference_z = [615, 795, 1046, 1333, 1645, 1977, 2328, 2692, 3070]
        for e in self.actual["entities"]:
            if e["role"] != "sensitive":
                continue
            key = tuple(e["ids"].values())
            self.assertNotIn(key, seen)
            seen.add(key)
            system, layer = e["ids"]["system"], e["ids"]["layer"]
            donor = 2 if layer == 10 else layer
            oldkey = tuple(dict(e["ids"], layer=donor).values())
            source = old[oldkey]
            if system == 1:
                delta = [-2.5, -3, -10, 0][layer-1]
                stave = self.oldxml.find(f'./detectors/detector[@id="1"]/layer[@id="{layer}"]/stave[@id="{e["ids"]["stave"]}"]')
                phi = number(stave, "phi")
                expected = [source["center_mm"][0]+delta*math.cos(phi), source["center_mm"][1]+delta*math.sin(phi), source["center_mm"][2]]
                self.assertEqual(e["size_mm"], source["size_mm"])
            else:
                side = -1 if system == 2 else 1
                expected = [*source["center_mm"][:2], source["center_mm"][2]+side*(datums[layer-1]-reference_z[donor-1])]
                for field in ("size_mm", "normal", "u", "v", "template_patch_id"):
                    self.assertEqual(e[field], source[field])
                self.assertNotIn(e["source_patch_id"], sources)
                sources.add(e["source_patch_id"])
            self.assertLess(math.dist(e["center_mm"], expected), 1.e-8)
        self.assertEqual(len(seen), 12410)
        self.assertEqual(len(sources), 5616)

    def test_local_units_and_global_cells_are_preserved(self):
        for system in (2, 3):
            det = self.xml.find(f'./detectors/detector[@id="{system}"]')
            before = self.oldxml.find(f'./detectors/detector[@id="{system}"]')
            self.assertEqual([int(d.get("id")) for d in det.findall("disc")], list(range(1, 11)))
            for identity in range(1, 11):
                donor = 2 if identity == 10 else identity
                actual = det.find(f'disc[@id="{identity}"]')
                old = before.find(f'disc[@id="{donor}"]')
                # Module local transforms and every material shape/dimension are
                # generated from the original donor, independent of new datum.
                for a, b in zip(actual.iter(), old.iter()):
                    self.assertEqual(a.tag, b.tag)
                    for key in set(a.attrib) | set(b.attrib):
                        if key in ("name", "material", "vis") or a is actual and key in ("id", "z"):
                            continue
                        self.assertEqual(a.get(key), b.get(key), (identity, a.tag, key))
                self.assertEqual(len(list(actual.iter())), len(list(old.iter())))
            for part in before.findall("part"):
                if part.get("name").startswith(("trunk", "bypass", "rear", "carrier", "flange")):
                    self.assertEqual(part.attrib, det.find(f'part[@name="{part.get("name")}"]').attrib)
            for identity, z in enumerate([615,865,1115,1333,1565,1780,2090,2440,3070,950], 1):
                label = "P" if system == 3 else "N"
                sign = 1 if system == 3 else -1
                collectors = [p for p in det.findall("part") if p.get("name").startswith(f"collector{label}{identity}_")]
                self.assertEqual(len(collectors), 3)
                for p in collectors:
                    self.assertAlmostEqual(number(p, "z"), sign*(z+36.7))
            self.assertEqual(len(det.findall("part[@shape='sector']")), len(before.findall("part[@shape='sector']"))+15)

    def test_inventory_is_explicit_and_reference_materials_unchanged(self):
        for name, recipe in self.reference["materials"].items():
            self.assertEqual(recipe, self.actual["materials"][name], name)
        for label in ("N", "P"):
            a = self.actual["service_accounting"]["endcap"]["transport_"+label]
            self.assertTrue(a["global_inventory_reference"])
            self.assertEqual(a["flange_necks"], self.reference["service_accounting"]["endcap"]["transport_"+label]["flange_necks"])
            audit = next(q for q in self.actual["provenance"]["endcap_placement_audit"] if q["side"] == (1 if label=="P" else -1))
            reference_rails = sum(e["volume_mm3"] for e in self.reference["entities"] if e["role"]=="rail" and e["name"].startswith("rail"+label+"_"))
            self.assertAlmostEqual(audit["rail_volume_mm3_before"],reference_rails,places=6)
            self.assertAlmostEqual(audit["CFRP_rail_volume_change_mm3"],-229.824,places=6)
            self.assertEqual(audit["added_disc"]["donor_layer"],2)
            self.assertEqual(len(audit["added_collector_cells"]),1)
            # Standalone aperture is27mm; integrated tracker subsequently
            # applies the existing28.8mm amendment and audits its removed filler.
            collector_volume = 3*math.radians(90)*(190**2-27**2)*50/2
            self.assertAlmostEqual(audit["added_collector_cells"][0]["capacity_mm3"],collector_volume,places=5)
        self.assertEqual(self.actual["counts"]["cable"], self.reference["counts"]["cable"])
        for role in ("cable", "service_cell"):
            a = {e["name"]: e for e in self.actual["entities"] if e["role"] == role}
            b = {e["name"]: e for e in self.reference["entities"] if e["role"] == role}
            self.assertEqual(a, b)

    def test_invalid_identity_and_allocation_fail(self):
        for extra in ({"layer_id":2}, {"donor_layer":11}, {"abs_z_mm":4000}, {"abs_z_mm":865}):
            cfg = copy.deepcopy(self.config)
            cfg["placement"]["additional_pixel_disk"].update(extra)
            with self.assertRaises(ValueError):
                combined.export(cfg, self.folder / "invalid")
        cfg = copy.deepcopy(self.config)
        cfg["placement"]["pixel_barrel_staves"][0] = 14
        with self.assertRaisesRegex(ValueError,"stave counts"):
            combined.export(cfg,self.folder / "changed-count")


if __name__ == "__main__":
    unittest.main()
