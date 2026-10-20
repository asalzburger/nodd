"""Bounded positive/adverse checks for unsigned DES040 barrel outlines."""
import copy
import json
import unittest

import numpy as np

from . import barrel_overlap as b
from . import geometry as g
from . import layout


class BarrelOverlapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(b.DEFAULT_CONFIG.read_text())
        cls.source = b.ROOT/cls.config['base_geometry']
        cls.baseline = json.loads(cls.source.read_text())
        cls.original = copy.deepcopy(cls.baseline)
        cls.geometry, cls.controls = b.build(cls.baseline, cls.config)
        cls.barrels = [p for p in cls.geometry['panels'] if p['kind'] == 'barrel']

    def test_pinned_geometry_and_fixed_interfaces_preserved(self):
        self.assertEqual(b.digest(self.source), self.config['base_geometry_sha256'])
        self.assertEqual(self.baseline, self.original)
        self.assertEqual(b.fixed_interfaces(self.geometry), b.fixed_interfaces(self.baseline))
        self.assertTrue(self.controls['fixed_interfaces_retained'])
        self.assertEqual(len(self.geometry['supports']['members']), 484)
        self.assertEqual([p for p in self.geometry['panels'] if p['kind'] == 'endcap'],
                         [p for p in self.baseline['panels'] if p['kind'] == 'endcap'])
        self.assertEqual(self.controls['counts']['endcap'], {'1': 72, '2': 72, '3': 48})

    def test_build_is_deterministic(self):
        geometry, controls = b.build(self.baseline, self.config)
        self.assertEqual(geometry, self.geometry)
        self.assertEqual(controls, self.controls)

    def test_whole_volume_and_uncached_actual_orientation_audits(self):
        self.assertEqual(self.controls['panel_panel_conflicts'], [])
        audit = self.controls['independent_controls']
        self.assertTrue(audit['passed'])
        self.assertEqual(audit['adaptive_audit_count'], len(self.barrels))
        self.assertTrue(all(p['clear'] for p in audit['actual_orientation_uncached_coil_audits']))
        self.assertFalse(audit['occupied_coil_fixture']['clear'])
        self.assertEqual(audit['occupied_coil_fixture']['reason'], 'occupied volume witness')
        self.assertFalse(audit['occupied_support_fixture']['clear'])
        self.assertTrue(audit['duplicate_panel_conflict'])
        self.assertTrue(audit['widened_without_stagger_conflict'])
        self.assertFalse(audit['changed_radius_cache_key_collision'])
        for p in self.barrels:
            self.assertTrue(p['coil_certificate']['clear'])
            self.assertTrue(p['support_certificate']['clear'])
            self.assertEqual(p['support_certificate']['total_members'], 484)
            self.assertEqual(p['support_certificate']['required_clearance_m'], .05)
        self.assertEqual(self.controls['coil_certificate_cache']['historical_certificates_loaded'], 0)

    def test_actual_apothems_corner_cap_z_extents_and_size_policy(self):
        for p in self.barrels:
            facet = int(p['id'].split('/')[1][1:])
            radius = [5.2, 6.7, 8.2][p['station']-1]
            if p['station'] == 3 and facet % 2:
                radius = 8.75
            self.assertAlmostEqual(np.linalg.norm(np.asarray(p['origin_m'])[:2]), radius)
            self.assertLess(np.linalg.norm(g.vertices3(p)[:, :2], axis=1).max(), 9.4)
            self.assertLessEqual(abs(g.vertices3(p)[:, 2]).max(), [6.4456, 9.2, 12.5][p['station']-1]+1e-10)
            self.assertGreaterEqual(g.polygon_area(p['vertices_m']), .25-1e-10)
            self.assertGreaterEqual(np.ptp(np.asarray(p['vertices_m'])[:, 1]), .5-1e-10)
            self.assertLessEqual(np.ptp(np.asarray(p['vertices_m'])[:, 1]), 4.+1e-10)
        envelope = self.controls['envelope']
        self.assertAlmostEqual(envelope['maximum_corner_radius_after_m'], 9.099797510275206)
        self.assertAlmostEqual(envelope['maximum_corner_radius_growth_m'], .586448168947723)
        self.assertEqual(self.controls['counts']['barrel'], {'1': 96, '2': 168, '3': 432})
        self.assertEqual(self.controls['barrel_count_reduction'], 360)
        self.assertEqual(self.controls['dimensions_after']['3']['dimension_family_count'], 9)
        self.assertEqual(self.controls['dimensions_after']['2']['tangent_width_below_half_m_count'], 48)
        self.assertEqual(self.controls['dimensions_after']['3']['tangent_width_below_half_m_count'], 96)

    def test_angular_overlap_derivation_and_actual_finite_faces(self):
        d = self.controls['stagger']
        c = self.geometry['configuration']['chambers']
        self.assertAlmostEqual(d['odd_half_width_m'], 1.3439920862902566)
        self.assertAlmostEqual(d['derived_full_depth_border_overlap_deg'], .1)
        # Test actual finite full-depth footprints on either side of each0.1deg
        # common angular interval. These templates eliminate only z interruptions.
        even = layout._barrel('TEST/even', 3, 0., 8.2, -1., 1.,
                             -d['even_half_width_m'], d['even_half_width_m'], c)
        odd = layout._barrel('TEST/odd', 3, 15., 8.75, -1., 1.,
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
        self.assertAlmostEqual(self.controls['stagger_volume_checks']['separating_plane_gap_m'], .0696252773064927)
        self.assertEqual(self.controls['stagger_volume_checks']['checked_adjacent_template_pairs'], 24)

    def test_z_merges_certify_the_whole_union_and_never_increase_length_cap(self):
        merge = self.controls['max_z_seam_merging']
        self.assertEqual(merge['accepted'], 264)
        self.assertEqual(merge['before'], 960)
        self.assertEqual(merge['after'], 696)
        combined = [p for p in self.barrels if 'merged_from' in p]
        self.assertTrue(combined)
        self.assertEqual(sum(len(p['merged_from'])-1 for p in combined), merge['accepted'])
        for p in combined:
            self.assertTrue(p['coil_certificate']['clear'])
            self.assertTrue(p['support_certificate']['clear'])
            self.assertLessEqual(p['compartment']['z_m'][1]-p['compartment']['z_m'][0], 4.+1e-10)

    def test_c12_cache_key_uses_actual_solid_radius_and_magnetic_configuration(self):
        c = self.geometry['configuration']['chambers']
        m = self.baseline['magnetic_configuration']
        p = layout._barrel('same-id', 3, 15., 8.2, -1, 1, -.9, .9, c)
        moved = layout._barrel('same-id', 3, 15., 8.75, -1, 1, -.9, .9, c)
        self.assertNotEqual(b.coil_cache_key(p, m, c), b.coil_cache_key(moved, m, c))
        rotated = layout._barrel('different-id', 3, 45., 8.2, -1, 1, -.9, .9, c)
        self.assertEqual(b.coil_cache_key(p, m, c), b.coil_cache_key(rotated, m, c))
        altered = copy.deepcopy(m)
        altered['coil_groups']['barrel']['half_r_m'] += .01
        self.assertNotEqual(b.coil_cache_key(p, m, c), b.coil_cache_key(p, altered, c))
        resized = layout._barrel('same-id', 3, 15., 8.2, -1, 1, -.91, .91, c)
        self.assertNotEqual(b.coil_cache_key(p, m, c), b.coil_cache_key(resized, m, c))

    def test_fixed_clearances_sources_and_stations_cannot_be_weakened(self):
        for key in ('coil_clearance_m', 'support_clearance_m'):
            config = copy.deepcopy(self.config)
            config[key] = .049
            with self.assertRaisesRegex(ValueError, 'fixed50mm'):
                b.build(self.baseline, config)
        config = copy.deepcopy(self.config)
        config['neighbor_clearance_m'] = .019
        with self.assertRaisesRegex(ValueError, 'fixed20mm'):
            b.build(self.baseline, config)
        for key in ('supports', 'magnetic_configuration', 'panels'):
            base = copy.deepcopy(self.baseline)
            if key == 'supports':
                base[key]['members'][0]['depth_m'] += .001
            elif key == 'magnetic_configuration':
                base[key]['coil_groups']['barrel']['center_r_m'] += .001
            else:
                next(p for p in base[key] if p['kind'] == 'endcap')['depth_m'] += .001
            with self.assertRaisesRegex(ValueError, 'fingerprint changed'):
                b.build(base, self.config)
        base = copy.deepcopy(self.baseline)
        base['configuration']['chambers']['barrel_half_z_m'][0] += .001
        with self.assertRaisesRegex(ValueError, 'fixed barrel station'):
            b.build(base, self.config)


if __name__ == '__main__':
    unittest.main()
