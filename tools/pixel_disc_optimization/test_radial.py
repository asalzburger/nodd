"""Independent radial-axis, shared-sensor, seam and acceptance controls."""
import math
import unittest

import numpy as np
from shapely.ops import unary_union

import radial
import study


class RadialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = radial.load_config()

    def test_rectangular_covariance_rotates_but_square_control_does_not(self):
        c0 = radial.covariance([25., 100.], 0.)
        c90 = radial.covariance([25., 100.], math.pi/2)
        self.assertAlmostEqual(c0[0][0], 25**2/12)
        self.assertAlmostEqual(c90[0][0], 100**2/12)
        self.assertAlmostEqual(radial.covariance([50., 50.], .7)[0][0], 50**2/12)
        self.assertAlmostEqual(radial.covariance([50., 50.], .7)[0][1], 0.)

    def test_datum_match_accepts_float_roundoff_but_rejects_changed_position(self):
        ds = [sign*z for z in self.cfg['positive_disc_datums_mm'] for sign in [-1., 1.]]
        ds[10] += 4.6e-13
        radial.check_datums(self.cfg, ds)
        ds[10] += 1e-5
        with self.assertRaises(ValueError):
            radial.check_datums(self.cfg, ds)

    def test_all_families_have_tangential_axes_and_preserve_inner_ring(self):
        for policy in self.cfg['policies']:
            modules, rings = radial.candidates(self.cfg, .5, .2, policy)
            inner = [m for m in modules if m['row']==0]
            self.assertEqual(len(inner), 18)
            self.assertTrue(all(m['family']=='single' for m in inner))
            for m in inner:
                self.assertAlmostEqual(np.linalg.norm(m['center_mm'][:2]), 41.15)
            for m in modules:
                c = np.asarray(m['center_mm'][:2]); u = np.asarray(m['u'][:2])
                self.assertAlmostEqual(np.dot(c, u), 0., places=10)
            self.assertEqual(sum(r['modules'] for r in rings), len(modules))

    def test_shared_sensor_is_counted_once_and_seam_is_inactive(self):
        cfg = dict(self.cfg, annulus_mm=[.1, 100.])
        for family, chips in [('double', 2), ('double-radial', 2), ('quad', 4)]:
            m = dict(family=family, module_id=200000, sensor_id=200000,
                     center_mm=[60., 0., 10.], u=[0., 1., 0.], v=[1., 0., 0.])
            patches = radial.active_patches([m], cfg)
            self.assertEqual(len(patches), chips)
            self.assertEqual(len({p['sensor_id'] for p in patches}), 1)
            self.assertEqual(len({p['id'] for p in patches}), chips)
            outlines = radial.project([m], cfg, 10., guard=.1)
            active = radial.project([m], cfg, 10.)
            self.assertEqual(len(outlines), 1)
            self.assertAlmostEqual(sum(p.area for p in active), chips*384)
            # Shared silicon at the centre does not imply active seam response.
            self.assertFalse(unary_union(active).covers(outlines[0].centroid))

    def test_whole_quad_is_coloured_as_one_assembly(self):
        raw, _ = radial.candidates(self.cfg, .3, .2, 'quad')
        placed = radial.stagger(raw, self.cfg, 615.2)
        patches = radial.active_patches(placed, self.cfg)
        for m in placed:
            same = [p for p in patches if p['module_id']==m['module_id']]
            self.assertTrue(all(p['center_mm'][2]==m['center_mm'][2] and p['level']==m['level'] for p in same))
        self.assertFalse(radial.body_screen(placed, self.cfg)['overlaps_or_insufficient_gap'])

    def test_guard_cannot_fill_an_active_seam(self):
        cfg = dict(self.cfg, annulus_mm=[59.95, 60.05], active_mm=[20., 19.2],
                   luminous_half_z_mm=0., certificate_max_depth=0)
        m = dict(family='double-radial', module_id=200000, sensor_id=200000,
                 center_mm=[60., 0., 10.], u=[0., 1., 0.], v=[1., 0., 0.])
        # Direct planar seam control independent of the ring generator.
        active = radial.project([m], cfg, 10.)
        from shapely.geometry import Point
        self.assertFalse(unary_union(active).covers(Point(60., 0.)))
        self.assertTrue(radial.project([m], cfg, 10., guard=.5)[0].covers(Point(60., 0.)))

    def test_larger_family_seams_are_detected_as_coverage_holes(self):
        raw, _ = radial.candidates(self.cfg, .3, .2, 'double')
        placed = radial.stagger(raw, self.cfg, 615.2)
        active = study.metrics(radial.project(placed, self.cfg, 615.2), self.cfg)
        self.assertGreater(active['uncovered_annulus_superset_mm2'], 1.)

    def test_service_chains_count_modules_and_chips_separately(self):
        raw, rings = radial.candidates(self.cfg, .3, .2, 'quad')
        services = radial.service_estimate(raw, rings, self.cfg, 210.)
        self.assertEqual(services['modules_per_disc'], len(raw))
        self.assertEqual(services['chips_per_disc'], len(radial.active_patches(raw, self.cfg)))
        self.assertGreater(services['chips_per_disc'], services['modules_per_disc'])
        self.assertGreater(services['power_chains'], 0)

    def test_selected_radial_fixture_covers_near_and_far_without_body_clashes(self):
        raw, _ = radial.candidates(self.cfg, .55, .1)
        for datum in [615.2, 3070.]:
            placed, row = radial.screen(raw, self.cfg, datum)
            self.assertTrue(row['endpoint_body_overlap_pass'])
            self.assertTrue(study.coverage_certificate(radial.active_patches(placed, self.cfg), self.cfg, datum)['passed'])
            self.assertTrue(radial.orientation_screen(placed, self.cfg)['passed'])

    def test_reflection_preserves_silicon_and_outward_body_periphery(self):
        raw, _ = radial.candidates(self.cfg, .55, .1)
        positive = radial.stagger(raw, self.cfg, 615.2)
        negative = [dict(m, center_mm=[*m['center_mm'][:2], -m['center_mm'][2]], u=[-x for x in m['u']]) for m in positive]
        for a, b in zip(positive, negative):
            self.assertAlmostEqual(radial.body_polygon(a, self.cfg).symmetric_difference(radial.body_polygon(b, self.cfg)).area, 0., places=8)
        self.assertAlmostEqual(unary_union(radial.project(positive, self.cfg, 615.2)).symmetric_difference(unary_union(radial.project(negative, self.cfg, -615.2))).area, 0., places=8)


if __name__ == '__main__':
    unittest.main()
