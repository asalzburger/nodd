"""PROTOTYPE allocation checks, not physical detector acceptance."""
import copy
import json
from pathlib import Path
import unittest

from muon_layouts import assemble
from envelope_study.study import ray_interval

ROOT = Path(__file__).resolve().parents[2]


class SteppedEndcapTests(unittest.TestCase):
    def setUp(self):
        self.baseline = json.loads((ROOT/'docs/design/DES-003-envelopes.json').read_text())
        self.options = json.loads((ROOT/'tools/magnetic_study/muon-layouts.json').read_text())['options']

    def test_all_candidates_reclaim_space_without_intersections(self):
        original = copy.deepcopy(self.baseline)
        for option in self.options:
            with self.subTest(candidate=option['id']):
                _, regions = assemble(self.baseline, option)
                front = regions['muon_endcap_inner']
                barrel = regions['muon_barrel']
                self.assertLess(front['z_min_m'], barrel['z_max_m'])
                self.assertLess(front['r_max_m'], barrel['r_min_m'])
                for eta in (3., 3.5):
                    self.assertIsNotNone(ray_interval(front, eta))
        self.assertEqual(original, self.baseline)

    def test_barrel_length_is_not_an_endcap_front_constraint(self):
        option = copy.deepcopy(self.options[0])
        # Test fixture only: shorten barrel independently, leaving a transition gap.
        option['overrides']['muon_barrel']['z_max_m'] = 7.0
        _, regions = assemble(self.baseline, option)
        self.assertEqual(regions['muon_endcap_inner']['z_min_m'], 6.35)
        self.assertEqual(regions['muon_endcap_outer']['z_min_m'], 7.2)

    def test_collision_with_calorimeter_is_rejected(self):
        option = copy.deepcopy(self.options[0])
        option['endcap_sections'][0]['z_min_m'] = 6.0
        with self.assertRaises(ValueError):
            assemble(self.baseline, option)

    def test_collision_with_barrel_and_duplicate_sections_are_rejected(self):
        for mutation in ('collision', 'duplicate'):
            option = copy.deepcopy(self.options[0])
            if mutation == 'collision':
                option['endcap_sections'][0]['r_max_m'] = 4.5
            else:
                option['endcap_sections'].append(copy.deepcopy(option['endcap_sections'][0]))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                assemble(self.baseline, option)


if __name__ == '__main__':
    unittest.main()
