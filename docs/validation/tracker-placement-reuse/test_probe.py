"""Parser controls: fail closed when DDG4 startup evidence is incomplete."""
import unittest
from probe import mapping_interval
from recipe_counts import recipe
import xml.etree.ElementTree as ET


class MappingIntervalTests(unittest.TestCase):
    def test_measures_only_mapping(self):
        fixture_count = 3
        result = mapping_interval([(1., "unrelated"), (2., "Populating Geant4 volume manager"),
                                   (5., f"populated with {fixture_count} sensitive path entries"),
                                   (9., "unrelated")])
        self.assertEqual(result, dict(sensitive_paths=fixture_count, mapping_seconds=3.))

    def test_incomplete_or_ambiguous_evidence(self):
        start = (2., "Populating Geant4 volume manager")
        end = (5., "populated with 3 sensitive path entries")
        for lines in ([], [start], [end], [start, start, end], [start, end, end],
                      [start, (1., end[1])]):
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                mapping_interval(lines)

    def test_recipe_keeps_child_ids_material_and_cuts(self):
        # Explicit fixture values, unrelated to detector parameters.
        first = ET.fromstring('<module name="a" id="1" z="2*mm"><piece name="x" '
                              'sensor="3" material="A"><cut sx="4*mm"/></piece></module>')
        other = ET.fromstring(ET.tostring(first))
        other.set("name", "b")
        other.set("id", "9")
        other.set("z", "8*mm")
        other[0].set("name", "y")
        outer = {"name", "id", "z"}
        self.assertEqual(recipe(first, outer), recipe(other, outer))
        for target, attr, value in ((other[0], "sensor", "5"), (other[0], "material", "B"),
                                    (other[0][0], "sx", "6*mm")):
            before = target.get(attr)
            target.set(attr, value)
            self.assertNotEqual(recipe(first, outer), recipe(other, outer))
            target.set(attr, before)


if __name__ == "__main__":
    unittest.main()
