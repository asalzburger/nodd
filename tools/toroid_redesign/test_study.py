"""Independent analytical controls for the issue105 schematic proposal."""
import copy
import math
import unittest

import numpy as np

from tools.toroid_redesign.study import axial_bounds, crossings, load, validate


class RedesignControls(unittest.TestCase):
    def test_complete_warm_axial_separation_and_negative_control(self):
        c = load()
        self.assertAlmostEqual(validate(c)['minimum_family_gap_m'], .8)
        for name in ('endcap_plus', 'endcap_minus'):
            self.assertGreater(axial_bounds(c, name)[1], axial_bounds(c, name)[0])
        c['coil_groups']['barrel']['half_z_m'] = 11.8
        with self.assertRaisesRegex(ValueError, 'interleave'):
            validate(c)
        c = load(); c['redesign']['winding_field_limit_T'] = 5
        with self.assertRaisesRegex(ValueError, 'policy'):
            validate(c)

    def test_full_depth_analytic_handoff_and_no_host_intersections(self):
        s = load()['stations']; h = s['outline_thickness_m']/2
        for i in range(3):
            r, z, length, outer = (s[k][i] for k in ('barrel_radii_m',
                'disk_abs_z_m', 'barrel_half_lengths_m', 'disk_outer_radii_m'))
            self.assertAlmostEqual(z-h-length, .05)
            self.assertGreaterEqual(length/(r+h), (z+h)/outer)
            self.assertLessEqual(s['disk_inner_radius_m'], (z-h)/math.sinh(3))
            if i < 2:
                self.assertLess(outer, s['barrel_radii_m'][i+1]-h)

    def test_coil_free_eta3_handoff_and_finite_aperture(self):
        c = load()
        eta = np.linspace(-3, 3, 1201)
        self.assertTrue(crossings(eta, 0, c, False)[0].all())
        cutoff = math.asinh((6.7456-.25)/.4)
        self.assertTrue(crossings([cutoff-1e-8], 0, c, False)[0][0, 0])
        self.assertFalse(crossings([cutoff+1e-8], 0, c, False)[0][0, 0])
        self.assertFalse(crossings([3.5], 0, c, False)[0][0, 0])

    def test_sector_and_hemisphere_symmetry(self):
        c = load()
        eta = np.array([.1, .7, 1.15, 1.7, 2.6, 3.0])
        phi = np.array([2., 7., 11., 15., 22., 28.])
        hits, p, _ = crossings(eta, phi, c)
        mirrored, q, _ = crossings(-eta, phi, c)
        np.testing.assert_array_equal(hits, mirrored)
        np.testing.assert_allclose(p[:, :, 2], -q[:, :, 2])
        np.testing.assert_array_equal(hits, crossings(eta, phi+30, c)[0])

    def test_whole_depth_and_coil_exclusion_negative_controls(self):
        c = load()
        # A ray through a barrel end-return centre cannot invent a B1 hit.
        end = c['coil_groups']['barrel']['half_z_m']
        eta = math.asinh(end/c['stations']['barrel_radii_m'][0])
        self.assertTrue(crossings([eta], 0, c, False)[0][0, 0])
        fixture = copy.deepcopy(c)
        fixture['stations']['disk_outer_radii_m'][0] = .8
        self.assertFalse(crossings([eta], 0, fixture, True)[0][0, 0])
        # Shortening barrels creates a real uninstrumented transition.
        control = copy.deepcopy(c)
        control['stations']['barrel_half_lengths_m'] = [5.7]*3
        eta = math.asinh(7./8.45)
        self.assertTrue(crossings([eta], 0, c, False)[0].all())
        self.assertFalse(crossings([eta], 0, control, False)[0].all())

    def test_usable_wheel_rescues_clipped_barrel_without_double_count(self):
        hits, points, kinds = crossings([.984375], [.0625], load())
        self.assertTrue(hits.all())
        self.assertEqual(kinds[0, 0], 2)
        self.assertAlmostEqual(points[0, 0, 2], 6.7456)
        self.assertEqual(int(hits.sum()), 3)

    def test_one_station_per_shell_and_strict_ordering(self):
        c = load()
        eta = np.linspace(0, 3, 601)
        hits, p, _ = crossings(eta, 7.5, c, False)
        self.assertEqual(hits.shape, (601, 3))
        self.assertTrue((np.diff(np.linalg.norm(p, axis=-1), axis=-1) > 0).all())


if __name__ == '__main__':
    unittest.main()
