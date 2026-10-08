import unittest
import xml.etree.ElementTree as ET
from aperture import enlarge_pixel_aperture
from export import rename_materials


class IntegrationGuards(unittest.TestCase):
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
