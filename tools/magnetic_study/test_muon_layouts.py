"""PROTOTYPE allocation checks, not physical detector acceptance."""
import copy
import json
from pathlib import Path
import unittest

from muon_layouts import assemble, allocation_comparison
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

    def test_reallocation_preserves_interfaces_depths_and_sampled_paths(self):
        for option in self.options:
            if not option.get('inner_space_reallocated'):
                continue
            with self.subTest(candidate=option['id']):
                data, regions = assemble(self.baseline, option)
                comparison = allocation_comparison(self.baseline, data)
                self.assertTrue(comparison['tracker_and_service_bounds_preserved'])
                for family in ('ecal', 'hcal'):
                    self.assertEqual(comparison['families'][family]['decreased_path_samples'], 0)
                    self.assertEqual(comparison['families'][family]['new_miss_samples'], 0)
                for name, depth in comparison['nominal_depths_m'].items():
                    self.assertAlmostEqual(depth['candidate']-depth['baseline'],
                                           .4 if name == 'hcal_barrel' else 0.)
                self.assertAlmostEqual(comparison['interface_gaps_m']['tracker_services_to_ecal'], .06)
                self.assertAlmostEqual(comparison['interface_gaps_m']['ecal_to_hcal_barrel'], .10)
                baseline = {r['id']:r for r in self.baseline['regions']}
                for name in ('hcal_endcap', 'forward_calorimeter'):
                    self.assertEqual(regions[name], baseline[name])

    def test_old_ecal_endcap_radius_conflicts_with_inward_hcal(self):
        option = copy.deepcopy(next(o for o in self.options if o['id'] == 'MAG-03'))
        option['overrides']['ecal_endcap']['r_max_m'] = 2.06
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
