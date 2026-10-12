import math
import unittest
import xml.etree.ElementTree as ET
from services import reconcile


class SharedServices(unittest.TestCase):
    def fixture(self, payload=2):
        doc = ET.Element("lccdd")
        detectors = ET.SubElement(doc, "detectors")
        barrel = ET.SubElement(detectors, "detector", name="ShortStripBarrel")
        endcap = ET.SubElement(detectors, "detector", name="ShortStripEndcap")
        entities = []
        for parent, name, a, b in (
            (barrel, "short_barrel_trunk_0", 0, 10),
            (endcap, "short_endcap_trunk_0", 5, 10),
        ):
            ET.SubElement(
                parent,
                "piece",
                name=name,
                role="service_cell",
                kind="sector",
                material=name,
                u="0*mm",
                v="0*mm",
                w=f"{(a+b)/2}*mm",
                rmin="10*mm",
                rmax="11*mm",
                start="0*rad",
                angle="1*rad",
                length=f"{b-a}*mm",
            )
            entities.append(
                dict(
                    name=name,
                    role="service_cell",
                    material=name,
                    constituent_volumes_mm3={"Copper": payload},
                    volume_mm3=10.5 * (b - a),
                )
            )
        recipes = {"Copper": {"density_g_cm3": 8.96}, "Air": {"density_g_cm3": 0.0012}}
        return doc, ET.Element("materials"), entities, recipes

    def test_split_and_payload_conservation(self):
        doc, materials, entities, recipes = self.fixture()
        result, actions = reconcile(doc, materials, entities, recipes)
        self.assertEqual(len(result), 2)
        self.assertEqual([e["center_mm"][2] for e in result], [2.5, 7.5])
        self.assertAlmostEqual(
            sum(e["constituent_volumes_mm3"]["Copper"] for e in result), 4
        )
        self.assertAlmostEqual(sum(e["volume_mm3"] for e in result), 105)
        self.assertEqual(
            actions[-1]["payload_before_mm3"], actions[-1]["payload_after_mm3"]
        )
        for recipe in recipes.values():
            if "composition" in recipe:
                self.assertAlmostEqual(sum(recipe["composition"].values()), 1)

    def test_excess_payload_fails(self):
        with self.assertRaisesRegex(ValueError, "exceeds physical corridor"):
            reconcile(*self.fixture(1000))


if __name__ == "__main__":
    unittest.main()
