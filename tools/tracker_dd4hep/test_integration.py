import unittest
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from aperture import enlarge_pixel_aperture
from export import rename_materials


class IntegrationGuards(unittest.TestCase):
    def test_default_source_export_assembles_balanced_pixels_and_fixed_strips(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, '-B', str(root/'tools/tracker_dd4hep/export.py'), '--output', directory], check=True, capture_output=True)
            actual = json.loads((Path(directory)/'expected.json').read_text())
            # Preserve established strip counts while integrating the added
            # donor2 disk pair and the source-level balanced placement config.
            self.assertEqual(actual['pixel_config'], 'detector/config/pixel-detector-balanced.json')
            self.assertEqual({c['name']:c['counts'].get('sensitive') for c in actual['components']},
                             dict(beam=None,pixel=12410,short_barrel=8064,short_endcap=4320,long_barrel=13968,long_endcap=7488))
            self.assertEqual(actual['config']['pixel_passive_aperture_mm'],28.8)
            self.assertEqual(actual['beam']['config']['inner_radius_mm'],27)
            self.assertEqual(actual['beam']['config']['wall_mm'],0.8)
            barrel = next(e for e in actual['components'] if e['name']=='pixel')['provenance']['placement']
            self.assertEqual(barrel['pixel_barrel_radii_mm'],[31.5,57,96,182])

    def test_all_material_attributes_are_translated(self):
        node = ET.fromstring(
            '<detector><core material="Foam" tube_material="Titanium" coolant_material="CO2" name="CO2" /></detector>'
        )
        rename_materials(node, {x: "pixel_" + x for x in ("Foam", "Titanium", "CO2")})
        core = node[0]
        self.assertEqual(
            core.attrib,
            dict(
                material="pixel_Foam",
                tube_material="pixel_Titanium",
                coolant_material="pixel_CO2",
                name="CO2",
            ),
        )

    def test_aperture_preserves_non_filler_inventory(self):
        node = ET.fromstring(
            '<lccdd><detectors><detector name="PixelEndcapPositive"><part name="test" shape="sector" rmin="27*mm" rmax="50*mm" angle="1*rad" dz="1*mm" material="pixel_Core" /></detector></detectors></lccdd>'
        )
        volume = (50**2 - 27**2) / 2
        entities = [
            dict(
                name="test",
                material="pixel_Core",
                volume_mm3=volume,
                mass_g=volume * 0.55 / 1000,
            )
        ]
        recipes = {
            "pixel_Core": dict(volume_fractions={"Foam": 0.9, "Copper": 0.1}),
            "pixel_Foam": dict(density_g_cm3=0.5),
            "pixel_Copper": dict(density_g_cm3=1.0),
        }
        materials = ET.Element("materials")
        actions = enlarge_pixel_aperture(node, materials, entities, recipes, 28.8)
        revised = entities[0]
        recipe = recipes[revised["material"]]
        copper_mass = revised["mass_g"] * recipe["composition"]["pixel_Copper"]
        self.assertAlmostEqual(copper_mass, volume * 0.1 / 1000)
        self.assertGreater(actions[0]["removed_mass_g"], 0)
        with self.assertRaises(ValueError):
            enlarge_pixel_aperture(node, materials, entities, recipes, float("nan"))


if __name__ == "__main__":
    unittest.main()
