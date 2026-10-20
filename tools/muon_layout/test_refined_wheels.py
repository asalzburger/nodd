"""Bounded full-volume and adverse controls for unsigned DES040 refinement."""
import copy
import json
import math
from pathlib import Path
import unittest

import numpy as np

from . import geometry as g
from . import refined_wheels as r
from .wheel_inventory import dimensions


class RefinedWheelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(r.DEFAULT_CONFIG.read_text())
        cls.source = r.ROOT/cls.config['base_geometry']
        cls.baseline = json.loads(cls.source.read_text())
        cls.geometry, cls.controls = r.build(cls.baseline, cls.config)
        cls.changed = [p for p in cls.geometry['panels'] if p['kind'] == 'endcap']

    def test_pinned_input_and_exact_preservation(self):
        self.assertEqual(r.digest(self.source), self.config['base_geometry_sha256'])
        self.assertEqual(self.geometry['supports'], self.baseline['supports'])
        self.assertEqual(self.geometry['magnetic_configuration'], self.baseline['magnetic_configuration'])
        self.assertEqual([p for p in self.geometry['panels'] if p['kind'] == 'barrel'],
                         [p for p in self.baseline['panels'] if p['kind'] == 'barrel'])
        self.assertEqual(self.controls['supports_retained_exact'], 484)
        self.assertEqual(self.controls['barrel_panels_retained_exact'], 1056)

    def test_actual_dimension_families_and_finite_bounds(self):
        self.assertEqual(self.controls['counts_both_ends'], {'1': 72, '2': 72, '3': 48})
        self.assertEqual(self.controls['dimension_families'], {'1': 3, '2': 3, '3': 1})
        self.assertEqual(len(self.geometry['panels']), 1248)
        for body in self.changed:
            v = g.vertices3(body)
            spec = self.config['stations'][str(body['station'])]
            self.assertEqual(np.asarray(body['vertices_m']).shape, (4, 2))
            self.assertEqual(body['depth_m'], .5)
            self.assertEqual(abs(body['origin_m'][2]), spec['abs_z_m'])
            self.assertLessEqual(float(np.linalg.norm(v[:, :2], axis=1).max()),
                                 spec['outer_radius_m']+1e-9)
            self.assertTrue(body['coil_certificate']['clear'])
            self.assertTrue(body['support_certificate']['clear'])
            self.assertEqual(body['support_certificate']['total_members'], 484)
            dimensions(body)  # Inventory/export contract: two constant-u bases.

    def test_independent_whole_volume_audits_and_adverse_fixtures(self):
        audit = self.controls['independent_controls']
        self.assertTrue(audit['passed'])
        self.assertEqual(audit['adaptive_audit_count'], 192)
        self.assertTrue(all(p['clear'] for p in audit['adaptive_probes']))
        for key in ('occupied_coil_fixture', 'incorrect_rotated_bound_fixture',
                    'nominal_eta_without_ECT_clearance_fixture', 'occupied_support_fixture'):
            self.assertFalse(audit[key]['clear'], key)
        self.assertEqual(audit['occupied_coil_fixture']['reason'], 'occupied volume witness')
        self.assertTrue(audit['duplicate_panel_conflict'])
        self.assertEqual(self.controls['panel_panel_conflicts'], [])
        self.assertEqual(self.controls['all_panel_pair_count'], 778128)

    def test_actual_filler_to_core_normal_seam_is20mm(self):
        d = self.geometry['refined_wheel_dimensions']['inner_wheel']['core']
        slope, intercept = d['seam_slope'], d['seam_intercept_m']
        for family in ('PRE_SLOT', 'POST_SLOT'):
            body = next(p for p in self.changed if p['side'] == 1 and p['station'] == 1
                        and p['family'] == family and p['id'].endswith('S00'))
            # This seam lies in the globalx/y frame of the BT leg at phi0.
            upper = np.asarray(body['vertices_m'])[[2, 3]]
            normal_distance = (slope*upper[:, 0]+intercept-upper[:, 1])/math.sqrt(1+slope*slope)
            np.testing.assert_allclose(normal_distance, .02, atol=1e-13, rtol=0)
            self.assertGreater(float(np.min(np.abs(upper[:, 1]))), 0)
        # The erroneous old half-offset would produce10mm and fails this metric.
        wrong_distance = (.01*math.sqrt(1+slope*slope))/math.sqrt(1+slope*slope)
        self.assertNotAlmostEqual(wrong_distance, self.config['seam_width_m'])
        slot = self.geometry['refined_wheel_dimensions']['inner_wheel']
        self.assertGreater(slot['residual_affine_guard_area_beyond_BT_clearance_boxes_one_end_m2'], 0)
        self.assertGreater(slot['filler_u_ranges_m']['POST_SLOT'][1]-
                           slot['filler_u_ranges_m']['POST_SLOT'][0], .5)

    def test_nominal_eta3_nearest_face_and_explicit_middle_loss(self):
        phi = np.linspace(0, 2*math.pi, 1009, endpoint=False)
        eta = self.config['eta_limit']+1e-6
        directions = np.column_stack((np.cos(phi)/math.cosh(eta),
                                      np.sin(phi)/math.cosh(eta), np.full(len(phi), math.tanh(eta))))
        for station in (1, 2, 3):
            spec = self.config['stations'][str(station)]
            nominal = (spec['abs_z_m']-.25)/math.sinh(3)
            self.assertAlmostEqual(self.controls['aperture'][str(station)]['nominal_eta3_radius_m'], nominal)
            for body in self.changed:
                if body['side'] != 1 or body['station'] != station:
                    continue
                self.assertFalse(np.isfinite(g.midplane_hits(body, directions, full_depth=True)).any())
        middle = self.geometry['refined_wheel_dimensions']['middle_wheel']
        self.assertGreater(middle['local_aperture_excess_m']['FULL'], 0)
        self.assertGreater(middle['local_aperture_excess_m']['BT_LOW'], .1)
        self.assertLess(middle['sector_centre_nearest_face_eta']['BT_LOW'], 2.9)
        self.assertIn('not achieved', middle['limitation'])
        # Nominaleta3 is an aperture target; a flat middle family still misses
        # some otherwise clear near-forward directions. Preserve that limitation.
        full = next(p for p in self.changed if p['station'] == 2 and p['side'] == 1 and p['family'] == 'FULL')
        self.assertGreater(min(v[0] for v in full['vertices_m']), middle['nominal_eta3_apothem_m'])

    def test_moving_fixed_station_or_weakening_interfaces_is_rejected(self):
        for key in ('coil_clearance_m', 'support_clearance_m'):
            config = copy.deepcopy(self.config)
            config[key] = .049
            with self.assertRaisesRegex(ValueError, 'fixed50mm'):
                r.build(self.baseline, config)
        config = copy.deepcopy(self.config)
        config['seam_width_m'] = .019
        with self.assertRaisesRegex(ValueError, 'fixed20mm'):
            r.build(self.baseline, config)
        config = copy.deepcopy(self.config)
        config['stations']['2']['abs_z_m'] += .1
        with self.assertRaisesRegex(ValueError, 'fixed station centres'):
            r.build(self.baseline, config)
        baseline = copy.deepcopy(self.baseline)
        baseline['supports']['members'].pop()
        with self.assertRaisesRegex(ValueError, 'every one of484'):
            r.build(baseline, self.config)


if __name__ == '__main__':
    unittest.main()
