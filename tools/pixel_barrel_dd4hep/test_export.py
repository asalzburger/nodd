"""Pinning, inventory and material-conservation controls; no DD4hep required."""

import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export as generator
from materials import Materials


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = generator.read(
            generator.ROOT / "detector/config/pixel-barrel.json"
        )
        cls.temp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.temp.name)
        cls.expected = generator.export(cls.config, cls.path / "nominal")
        cls.support = generator.read(generator.ROOT / cls.config["support_config"])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_baseline_transform_inventory_and_frozen_pin(self):
        counts = self.expected["counts"]
        self.assertEqual(
            {
                k: counts[k]
                for k in [
                    "layer",
                    "stave",
                    "module",
                    "sensitive",
                    "ring",
                    "foot",
                    "cooling_tube",
                ]
            },
            dict(
                layer=4,
                stave=82,
                module=3050,
                sensitive=6794,
                ring=24,
                foot=492,
                cooling_tube=164,
            ),
        )
        layout = generator.load_layout(self.support)
        patches = {
            p["id"]: p
            for p in layout["modules"]
            if p["subsystem"] == "pixel" and p["region"] == "barrel"
        }
        for e in self.expected["entities"]:
            if e["role"] == "sensitive":
                p = patches[e["ids"]["sensor"]]
                self.assertEqual(e["center_mm"], p["center_mm"])
                self.assertEqual(e["normal"], p["n"])
        changed = copy.deepcopy(self.config)
        changed["input_sha256"][self.config["support_config"]] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Pinned baseline"):
            generator.export(changed, self.path / "stale")

    def test_translated_stave_frame_and_rotated_module_stack(self):
        root = ET.parse(self.path / "nominal/pixel-barrel.xml").getroot()
        layout = generator.load_layout(self.support)
        bodies = {b["module_id"]: b for b in layout["bodies"]}
        value = lambda node, key: float(node.get(key).split("*")[0])
        for stave in root.findall(".//stave"):
            phi, radius, offset = (value(stave, key) for key in ("phi", "radius", "offset_u"))
            n = [math.cos(phi), math.sin(phi), 0.]
            u = [-math.sin(phi), math.cos(phi), 0.]
            first = stave.find("module")
            b = bodies[int(first.get("id"))]
            for j in range(2):
                self.assertAlmostEqual(n[j], b['n'][j], places=12)
                self.assertAlmostEqual(radius*n[j]+offset*u[j], b['center_mm'][j], places=10)
            span = self.support['passive_stave_z_mm'][b['layer_id']]
            self.assertAlmostEqual(value(stave, 'length'),span[1]-span[0])
            for module in stave.findall('module'):
                sensor=module.find('sensor')
                self.assertAlmostEqual(value(sensor,'length'),20.4 if b['family']=='single' else 40.6)
                for patch in sensor.findall('patch'):
                    self.assertAlmostEqual(value(patch,'width'),19.2)
                    self.assertAlmostEqual(value(patch,'length'),20.)
                for die in module.findall('die'):
                    self.assertAlmostEqual(value(die,'width'),21.)
                    self.assertAlmostEqual(value(die,'length'),20.)
                    # No ASIC periphery is allowed to consume the z clearance.
                    self.assertLessEqual(abs(value(die,'v'))+value(die,'length')/2,value(sensor,'length')/2+1e-10)

    def test_retained_pr29_configuration_still_exports(self):
        old=generator.read(generator.ROOT/'detector/config/pixel-barrel-pr29.json')
        expected=generator.export(old,self.path/'pr29')
        self.assertEqual(expected['counts']['module'],2750)
        self.assertEqual(expected['counts']['sensitive'],6206)

    def test_configured_readout_fields_cannot_overflow(self):
        config = copy.deepcopy(self.config)
        config["module"]["pixel_pitch_mm"] = 0.025
        with self.assertRaisesRegex(ValueError, "Pixel pitch overflows"):
            generator.export(config, self.path / "pitch-overflow")
        config = copy.deepcopy(self.config)
        config["system_id"] = 32
        with self.assertRaisesRegex(ValueError, "system_id"):
            generator.export(config, self.path / "id-overflow")

    def test_material_volume_to_mass_conversion_and_invalid_fractions(self):
        m = Materials(self.config, self.support)
        m.effective("fixture", {"Copper": 2.0, "Polyimide": 3.0}, 10.0)
        recipe = m.recipes["fixture"]
        density = (2 * 8.96 + 3 * 1.42 + 5 * 0.0012) / 10
        self.assertAlmostEqual(recipe["density_g_cm3"], density)
        self.assertAlmostEqual(
            recipe["composition"]["Copper"], 2 * 8.96 / (density * 10)
        )
        with self.assertRaises(ValueError):
            m.effective("overfill", {"Copper": 11.0}, 10.0)
        bad = copy.deepcopy(self.config)
        bad["cable_volume_fractions"]["Copper"] = 0.8
        with self.assertRaises(ValueError):
            generator.export(bad, self.path / "bad")

    def test_material_change_keeps_geometry_identifiers_and_non_air_inventory(self):
        high = copy.deepcopy(self.config)
        high["cable_volume_fractions"] = {"Copper": 0.2, "Polyimide": 0.4, "Air": 0.4}
        e = generator.export(high, self.path / "high")
        self.assertEqual(self.expected["counts"], e["counts"])
        for a, b in zip(self.expected["entities"], e["entities"]):
            self.assertEqual(
                (a["name"], a["role"], a["center_mm"], a.get("ids")),
                (b["name"], b["role"], b["center_mm"], b.get("ids")),
            )
            self.assertEqual(a.get("volume_mm3"), b.get("volume_mm3"))
            if a["role"] in ["cable", "service_cell"]:
                self.assertGreater(b["mass_g"], a["mass_g"])
            else:
                self.assertEqual(a.get("mass_g"), b.get("mass_g"))
        self.assertEqual(self.expected["service_accounting"], e["service_accounting"])
        root = ET.parse(self.path / "nominal/pixel-barrel.xml").getroot()
        for volume in root.findall(".//service"):
            ri = float(volume.get("rmin").split("*")[0])
            ro = float(volume.get("rmax").split("*")[0])
            length = float(volume.get("length").split("*")[0])
            phi = float(volume.get("phi_width").split("*")[0])
            expected = next(
                x for x in self.expected["entities"] if x["name"] == volume.get("name")
            )
            self.assertAlmostEqual(
                (ro * ro - ri * ri) * phi / 2 * length, expected["volume_mm3"], places=6
            )

    def test_service_conservation_and_disjoint_partition(self):
        cells = json.loads((self.path / "nominal/service-cells.json").read_text())
        source = self.expected["service_accounting"]["source_reference"]
        self.assertAlmostEqual(
            sum(c["constituent_volumes_mm3"]["Titanium"] for c in cells),
            source["Ti_volume_mm3"],
            places=6,
        )
        self.assertAlmostEqual(
            sum(c["constituent_volumes_mm3"]["CO2"] for c in cells),
            source["full_liquid_volume_mm3"],
            places=6,
        )
        for c in cells:
            self.assertLess(sum(c["constituent_volumes_mm3"].values()), c["volume_mm3"])
        for i, a in enumerate(cells):
            for b in cells[i + 1 :]:
                if a["z"] == b["z"] and a["phi"] == b["phi"]:
                    self.assertLessEqual(
                        min(a["rmax"], b["rmax"]), max(a["rmin"], b["rmin"])
                    )


if __name__ == "__main__":
    unittest.main()
