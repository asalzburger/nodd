"""Regression guards for the real A/C1 interface, without fetching other branches."""
import copy
import json
import unittest

import compatibility
import study


class LayoutCompatibilityTest(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(study.INPUT.read_text())
        self.catalogue = json.loads(compatibility.CATALOGUE.read_text())

    def test_both_active_layouts_and_all_signed_disks_match(self):
        self.assertEqual(compatibility.contract(self.cfg, self.catalogue), [1430, 1800, 2120, 2450, 2730, 3120])
        self.assertEqual(self.cfg['inner_radius'], 710)
        self.assertEqual(self.cfg['outer_radius'], 1100)

    def test_previous_radius_and_short_strip_z_are_rejected(self):
        for key, value in [('inner_radius', 700), ('disk_z', 1320)]:
            with self.assertRaises(ValueError):
                compatibility.contract(dict(self.cfg, **{key: value}), self.catalogue)

    def test_drift_in_second_layout_and_negative_side_is_not_ignored(self):
        for candidate in self.catalogue['candidates']:
            bad = copy.deepcopy(self.catalogue)
            changed = next(c for c in bad['candidates'] if c['id'] == candidate['id'])
            next(l for l in changed['layers'] if l['kind'] == 'disc' and l['subsystem'] == 'long_strip' and l['z_m'] < 0)['r_min_m'] = .720
            with self.assertRaises(ValueError):
                compatibility.contract(self.cfg, bad)
        bad = copy.deepcopy(self.catalogue)
        bad['candidates'].pop()
        with self.assertRaises(ValueError):
            compatibility.contract(self.cfg, bad)

    def test_reflected_stack_and_vertex_give_identical_ray_factor(self):
        for z in compatibility.contract(self.cfg, self.catalogue):
            for vertex in self.cfg['vertex_z']:
                for level in (-12, -4, 4, 12):
                    for face in (-2.5, 2.5):
                        positive = (z+level+face-vertex)/(z-vertex)
                        negative = (-z-level-face+vertex)/(-z+vertex)
                        self.assertEqual(positive, negative)

    def test_interface_reservations_do_not_claim_clear_radial_corridor(self):
        candidate = next(c for c in self.cfg['candidates'] if c['id'] == 'square-long-6')
        result = study.evaluate(candidate, self.cfg, scan=True)
        interfaces = compatibility.interface_summary(result, self.cfg, self.catalogue)
        for layout in interfaces['layouts']:
            self.assertEqual(layout['ideal_active_band_gap_mm'], 10)
            self.assertLess(layout['body_radial_gap_to_short_strip_active_edge_mm'], 0)
            self.assertAlmostEqual(layout['short_long_trial_axial_envelope_gap_mm'], 18.85)
            self.assertAlmostEqual(layout['first_disk_body_to_ideal_barrel_end_mm'], 14.35)
            self.assertAlmostEqual(layout['last_disk_body_to_host_end_mm'], 14.35)
        self.assertGreater(interfaces['radial_host_residual_mm'], 0)


if __name__ == '__main__':
    unittest.main()
