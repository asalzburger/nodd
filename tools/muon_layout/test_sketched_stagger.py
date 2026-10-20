"""Focused physical/adverse checks for the updated-sketch outline prototype."""
import copy
import json
import unittest

import numpy as np

from . import geometry as g
from . import layout
from . import sketched_stagger as s


class SketchedStaggerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(s.DEFAULT_CONFIG.read_text())
        cls.source = s.ROOT/cls.config['base_geometry']
        cls.baseline = json.loads(cls.source.read_text())
        cls.original = copy.deepcopy(cls.baseline)
        cls.geometry, cls.controls = s.build(cls.baseline, cls.config)
        cls.changed = [p for p in cls.geometry['panels'] if p['kind'] == 'barrel' and p['station'] in (1, 2)]

    def test_pinned_input_immutable_fixed_solids_and_identifiers(self):
        self.assertEqual(s.digest(self.source), self.config['base_geometry_sha256'])
        self.assertEqual(self.config['input_revision'], 'a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f')
        self.assertEqual(self.baseline, self.original)
        self.assertEqual(s.fixed_interfaces(self.geometry), s.fixed_interfaces(self.baseline))
        self.assertTrue(self.controls['B3_retained_value_equal'])
        self.assertTrue(self.controls['endcaps_retained_value_equal'])
        self.assertEqual(self.controls['counts']['barrel'], {'1': 96, '2': 216, '3': 432})
        self.assertEqual(self.controls['counts']['endcap'], {'1': 72, '2': 72, '3': 48})
        self.assertEqual(self.controls['total_panels'], 936)
        self.assertEqual(len({p['id'] for p in self.geometry['panels']}), 936)
        self.assertEqual(self.controls['barrel_count_change'], 48)
        self.assertFalse(self.controls['count_reduction_required'])

    def test_determinism_including_fresh_certificates_and_no_frame_reference(self):
        geometry, controls = s.build(self.baseline, self.config)
        self.assertEqual(geometry, self.geometry)
        self.assertEqual(controls, self.controls)
        fixed_reference = lambda value: [p for p in value['without_support_panels']
            if p['kind'] == 'endcap' or p['station'] == 3]
        self.assertEqual(fixed_reference(geometry), fixed_reference(self.baseline))
        changed_reference = [p for p in geometry['without_support_panels']
            if p['kind'] == 'barrel' and p['station'] in (1, 2)]
        self.assertEqual(len(changed_reference), 360)
        self.assertTrue(all(p['coil_certificate']['clear'] for p in changed_reference))

    def test_actual_radii_phase_depth_extents_and_useful_sizes(self):
        for body in self.changed:
            facet = int(body['id'].split('/')[1][1:])
            expected_radius = 6.7 if body['station'] == 2 else (4.63 if facet % 2 else 5.2)
            expected_phase = facet*15+(7.5 if body['station'] == 2 else 0.)
            self.assertAlmostEqual(np.linalg.norm(np.asarray(body['origin_m'])[:2]), expected_radius)
            self.assertEqual(body['compartment']['phi_deg'], expected_phase)
            self.assertEqual(body['depth_m'], .5)
            self.assertLessEqual(abs(g.vertices3(body)[:, 2]).max(), [6.4456, 9.2][body['station']-1]+1e-10)
            self.assertGreaterEqual(g.polygon_area(body['vertices_m']), .25-1e-10)
            zspan = np.ptp(np.asarray(body['vertices_m'])[:, 1])
            self.assertGreaterEqual(zspan, .5-1e-10)
            self.assertLessEqual(zspan, 4.+1e-10)
        self.assertEqual(self.geometry['configuration']['chambers']['barrel_phase_deg'], [0., 7.5, 0.])
        self.assertAlmostEqual(self.controls['envelope']['maximum_corner_radius_growth_m'], 0.)
        self.assertEqual(self.controls['dimensions_after']['1']['dimension_family_count'], 2)
        self.assertEqual(self.controls['dimensions_after']['2']['dimension_family_count'], 4)
        self.assertEqual(self.controls['dimensions_after']['2']['tangent_width_below_half_m_count'], 48)
        # The48 B2 narrow fragments are allowed by the existing area/z policy;
        # no new universal tangential minimum is invented to reject them.
        self.assertGreaterEqual(self.controls['dimensions_after']['2']['minimum_area_m2'], .25)

    def test_full_depth_finite_overlap_and_physical_neighbor_separation(self):
        d = self.controls['stagger']
        c = self.geometry['configuration']['chambers']
        self.assertAlmostEqual(d['odd_half_width_m'], .776415147025806)
        self.assertAlmostEqual(d['derived_full_depth_border_overlap_deg'], .1)
        even = layout._barrel('TEST/even', 1, 0., 5.2, -1., 1.,
                             -d['even_half_width_m'], d['even_half_width_m'], c)
        odd = layout._barrel('TEST/odd', 1, 15., 4.63, -1., 1.,
                            -d['odd_half_width_m'], d['odd_half_width_m'], c)
        boundary = d['even_full_depth_border_half_angle_deg']
        phi = np.radians([boundary-.099, boundary-.001])
        rays = np.column_stack((np.cos(phi), np.sin(phi), np.zeros(2)))
        self.assertTrue(np.isfinite(g.midplane_hits(even, rays, .03, True)).all())
        self.assertTrue(np.isfinite(g.midplane_hits(odd, rays, .03, True)).all())
        phi = np.radians([boundary-.101, boundary+.001])
        rays = np.column_stack((np.cos(phi), np.sin(phi), np.zeros(2)))
        self.assertFalse(np.isfinite(g.midplane_hits(odd, rays[:1], .03, True)).any())
        self.assertFalse(np.isfinite(g.midplane_hits(even, rays[1:], .03, True)).any())
        self.assertFalse(g.intersects(even, odd, .02))
        neighbor = self.controls['stagger_volume_checks']
        self.assertEqual(neighbor['checked_adjacent_template_pairs'], 24)
        self.assertAlmostEqual(neighbor['separating_plane_gap_m'], .0353309407529947)
        # A15mm outward change crosses the physical20mm separation limit.
        adverse = dict(self.config, inner_odd_apothem_m=4.65)
        with self.assertRaisesRegex(ValueError, '20mm neighboring'):
            s.stagger_checks(c, adverse, s.stagger_dimensions(c, adverse))

    def test_fresh_whole_volume_interfaces_and_occupied_controls(self):
        self.assertEqual(self.controls['all_panel_pair_count'], 437580)
        self.assertEqual(self.controls['panel_panel_conflicts'], [])
        audit = self.controls['independent_controls']
        self.assertEqual(audit['adaptive_audit_count'], len(self.changed))
        self.assertTrue(all(p['clear'] for p in audit['actual_orientation_uncached_coil_audits']))
        self.assertFalse(audit['occupied_coil_fixture']['clear'])
        self.assertEqual(audit['occupied_coil_fixture']['reason'], 'occupied volume witness')
        self.assertFalse(audit['occupied_support_fixture']['clear'])
        self.assertTrue(audit['duplicate_panel_conflict'])
        self.assertTrue(audit['widened_without_stagger_conflict'])
        for body in self.changed:
            self.assertTrue(body['coil_certificate']['clear'])
            self.assertTrue(body['support_certificate']['clear'])
            self.assertEqual(body['support_certificate']['total_members'], 484)
            self.assertEqual(body['support_certificate']['required_clearance_m'], .05)
        self.assertEqual(self.controls['coil_certificate_cache']['historical_certificates_loaded'], 0)

    def test_installed_hcal_and_known_service_bounds_remain_distinct(self):
        bound = self.controls['hcal_and_known_service_bounds']
        self.assertTrue(bound['passed'])
        self.assertAlmostEqual(bound['minimum_known_service_clearance_lower_bound_m'], .055)
        self.assertAlmostEqual(bound['minimum_installed_hcal_clearance_lower_bound_m'], .14054)
        adverse = self.controls['independent_controls']['R4_60_service_clearance_diagnostic']
        self.assertFalse(adverse['passed'])
        self.assertAlmostEqual(adverse['minimum_known_service_clearance_lower_bound_m'], .025)
        self.assertGreater(adverse['minimum_installed_hcal_clearance_lower_bound_m'], .05)
        self.assertIn('Unimplemented external HCAL', bound['scope'])

    def test_actual_phase_radius_shape_and_sources_change_cache_key(self):
        c, m = self.geometry['configuration']['chambers'], self.baseline['magnetic_configuration']
        body = layout._barrel('same-id', 2, 7.5, 6.7, -1., 1., -.8, .8, c)
        key = s.coil_cache_key(body, m, c)
        for radius, phase, width in [(6.71, 7.5, .8), (6.7, 15., .8), (6.7, 7.5, .81)]:
            changed = layout._barrel('same-id', 2, phase, radius, -1., 1., -width, width, c)
            self.assertNotEqual(key, s.coil_cache_key(changed, m, c))
        altered = copy.deepcopy(m)
        altered['coil_groups']['barrel']['half_r_m'] += .01
        self.assertNotEqual(key, s.coil_cache_key(body, altered, c))
        altered = dict(c, coil_clearance_m=.051)
        self.assertNotEqual(key, s.coil_cache_key(body, m, altered))
        self.assertNotEqual(s.coil_cache_key(body, m, c, ('source', 'chambers', 'config-a')),
                            s.coil_cache_key(body, m, c, ('source', 'chambers', 'config-b')))
        self.assertFalse(self.controls['independent_controls']['changed_radius_cache_key_collision'])
        self.assertFalse(self.controls['independent_controls']['changed_phase_cache_key_collision'])

    def test_z_seam_merges_prove_complete_union_within_original_length_cap(self):
        merged = [p for p in self.changed if p.get('merged_from')]
        report = self.controls['max_z_seam_merging']
        self.assertEqual(sum(len(p['merged_from'])-1 for p in merged), report['accepted'])
        self.assertEqual(report['before'], 504)
        self.assertEqual(report['after'], 312)
        for body in merged:
            self.assertTrue(body['coil_certificate']['clear'])
            self.assertTrue(body['support_certificate']['clear'])
            self.assertLessEqual(np.ptp(np.asarray(body['vertices_m'])[:, 1]), 4.+1e-10)

    def test_no_source_or_clearance_exception_and_no_unrecorded_retuning(self):
        for key in ('coil_clearance_m', 'support_clearance_m', 'hcal_clearance_m'):
            config = dict(self.config, **{key: .049})
            with self.assertRaisesRegex(ValueError, 'fixed50mm'):
                s.build(self.baseline, config)
        for key in ('neighbor_clearance_m', 'gap_m'):
            with self.assertRaisesRegex(ValueError, 'fixed20mm'):
                s.build(self.baseline, dict(self.config, **{key: .019}))
        for key, value in [('inner_odd_apothem_m', 4.60), ('middle_barrel_phase_deg', 15.),
                           ('target_overlap_deg', .2), ('max_barrel_length_m', 6.)]:
            with self.assertRaisesRegex(ValueError, 'prototype choices changed'):
                s.build(self.baseline, dict(self.config, **{key: value}))
        for component in ('supports', 'magnetic_configuration', 'B3', 'endcap'):
            baseline = copy.deepcopy(self.baseline)
            if component == 'supports':
                baseline['supports']['members'][0]['depth_m'] += .001
            elif component == 'magnetic_configuration':
                baseline['magnetic_configuration']['coil_groups']['barrel']['center_r_m'] += .001
            else:
                panel = next(p for p in baseline['panels'] if (p['kind'] == 'endcap'
                    if component == 'endcap' else p['kind'] == 'barrel' and p['station'] == 3))
                panel['depth_m'] += .001
            with self.assertRaisesRegex(ValueError, 'fingerprint changed'):
                s.build(baseline, self.config)
        baseline = copy.deepcopy(self.baseline)
        baseline['configuration']['chambers']['min_span_m'] = .49
        with self.assertRaisesRegex(ValueError, 'policy fingerprint changed'):
            s.build(baseline, self.config)


if __name__ == '__main__':
    unittest.main()
