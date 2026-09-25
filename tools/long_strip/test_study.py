"""Independent controls for the DES-008 analytical prototype."""
import json
import math
import unittest

import numpy as np
import study


class StereoStudyTest(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(study.INPUT.read_text())

    def test_geometry_controls(self):
        p = study.rectangle(-2, 2, 6)
        self.assertEqual(study.area(p), 24)
        self.assertAlmostEqual(study.area(study.rotate(p, .62)), 24)
        self.assertTrue(study.inside(p, 0, 0))
        self.assertFalse(study.inside(p, 3, 0))
        self.assertTrue(study.intersects(p, p+[1, 1]))
        self.assertFalse(study.intersects(p, p+[4, 0]))

    def test_rotation_about_module_centre_and_envelope(self):
        cfg = self.cfg
        c = cfg['candidates'][1]
        rings = study.layout(c, cfg)
        expected = c['width']*math.cos(.02)+c['height']*math.sin(.02)
        for r in rings:
            for sensor in r['sensors']:
                np.testing.assert_allclose(sensor.mean(axis=0), [r['radius'], 0], atol=1e-12)
                self.assertAlmostEqual(np.ptp(sensor[:, 1]), expected)
                self.assertTrue(study.inside(r['body'], sensor[:, 0], sensor[:, 1]).all())
        mods = study.modules(rings, cfg)
        self.assertEqual(len({(m['ring'], m['module'], side) for m in mods for side in (0, 1)}), 2*len(mods))

    def test_pair_coverage_against_global_brute_force(self):
        # Test-only small grid: full enumeration, global sensor polygons, no shortcut.
        cfg = self.cfg
        nr, nphi = 19, 71
        radius = cfg['inner_radius']+(np.arange(nr)+.5)*(cfg['outer_radius']-cfg['inner_radius'])/nr
        phi = (np.arange(nphi)+.5)*2*math.pi/nphi
        xx, yy = radius[:, None]*np.cos(phi), radius[:, None]*np.sin(phi)
        weights = np.broadcast_to(radius[:, None], xx.shape)
        for c in cfg['candidates']:
            rings = study.layout(c, cfg)
            for vertex in (None, 150.0):
                pairs = np.zeros(xx.shape, dtype=int)
                crossings = np.zeros_like(pairs)
                for ring in rings:
                    for j in range(ring['count']):
                        angle = ring['phase']+j*2*math.pi/ring['count']
                        z = (2*(ring['ring'] % 2)+j % 2-1.5)*cfg['level_spacing']
                        hits = []
                        for side, sign in enumerate((-1, 1)):
                            factor = 1 if vertex is None else (cfg['disk_z']+z+sign*cfg['separation']/2-vertex)/(cfg['disk_z']-vertex)
                            sensor = study.rotate(ring['sensors'][side], angle)
                            hit = study.inside(sensor, xx*factor, yy*factor)
                            if ring['rows'] == 2:
                                # Independently construct a rotated dead band in global coordinates.
                                seam = study.rectangle(-cfg['row_gap']/2, cfg['row_gap']/2, 1000)
                                seam = study.rotate(seam, sign*cfg['relative_stereo']/2)+[ring['radius'], 0]
                                seam = study.rotate(seam, angle)
                                hit &= ~study.inside(seam, xx*factor, yy*factor)
                            hits.append(hit)
                            crossings += hit
                        pairs += hits[0] & hits[1]
                got = study.sample(rings, cfg, nr, nphi, vertex)
                self.assertEqual(got['missing_pair_bins'], int((pairs == 0).sum()))
                self.assertAlmostEqual(got['mean_pairs'], (pairs*weights).sum()/weights.sum())
                self.assertAlmostEqual(got['mean_sensor_crossings'], (crossings*weights).sum()/weights.sum())

    def test_single_hit_and_unrelated_sides_do_not_count_as_pair(self):
        cfg = dict(self.cfg, relative_stereo=.08, separation=10, row_gap=0)
        c = cfg['candidates'][-1]
        got = study.sample(study.layout(c, cfg), cfg, 101, 363, 150)
        self.assertGreater(got['missing_pair_fraction'], got['no_sensor_fraction'])
        self.assertGreater(got['both_sides_but_no_same_module_pair_fraction'], 0)

    def test_z_collision_and_cooling_failures(self):
        p = study.rectangle(0, 4, 4)
        mods = [{'ring': 0, 'module': i, 'level': i, 'z': z, 'body': p} for i, z in enumerate((0, 6))]
        self.assertEqual(len(study.collisions(mods, self.cfg)), 1)
        mods[1]['z'] = 8
        self.assertEqual(study.collisions(mods, self.cfg), [])
        self.assertAlmostEqual(study.mechanical(self.cfg)['cooling_stack_residual_mm'], .7)
        self.assertFalse(study.mechanical(dict(self.cfg, separation=1.8))['cooling_stack_fits_fixture'])
        self.assertLess(study.mechanical(dict(self.cfg, separation=6.6))['adjacent_level_clearance_mm'], 0)

    def test_covariance_from_measurement_matrix(self):
        for angle in (.020, .040, .052, .080):
            # Measurement u = tangential*cos(a) +/- radial*sin(a).
            h = np.array([[math.cos(angle/2), math.sin(angle/2)],
                          [math.cos(angle/2), -math.sin(angle/2)]])
            cov = np.linalg.inv(h.T @ h)*(self.cfg['pitch']**2/12)
            r = study.resolution(self.cfg['pitch'], angle)
            self.assertAlmostEqual(r['sigma_across_mm']**2, cov[0, 0])
            self.assertAlmostEqual(r['sigma_along_mm']**2, cov[1, 1])
        self.assertEqual(study.resolution(.08, 0)['rank'], 1)
        self.assertIsNone(study.resolution(.08, 0)['sigma_along_mm'])

    def test_row_mask_is_applied_to_each_rotated_sensor(self):
        cfg = dict(self.cfg, relative_stereo=0)
        c = next(c for c in cfg['candidates'] if c['id'] == 'square-split-6')
        r = study.layout(c, cfg)[0]
        for side in (0, 1):
            self.assertFalse(study.active(r, cfg, r['radius'], 10, side))
            self.assertTrue(study.active(r, cfg, r['radius']+1, 10, side))
        cfg['row_gap'] = 0
        self.assertTrue(study.active(r, cfg, r['radius'], 10, 0))

    def test_physical_sensor_gap_and_bad_config(self):
        for field, value in [('separation', .1), ('pitch', 0), ('relative_stereo', -1), ('row_gap', -1)]:
            with self.assertRaises(ValueError):
                study.validate(dict(self.cfg, **{field: value}))

    def test_nominal_bodies_and_failed_control(self):
        for c in self.cfg['candidates']:
            rings = study.layout(c, self.cfg)
            collisions = study.collisions(study.modules(rings, self.cfg), self.cfg)
            if c['id'] == 'wide-14-mount-control':
                self.assertGreater(len(collisions), 0)
            else:
                self.assertEqual(collisions, [])
        c = self.cfg['candidates'][-1]
        got = study.sample(study.layout(c, self.cfg), self.cfg, 100, 360, 150)
        self.assertGreater(got['missing_pair_fraction'], 0)


if __name__ == '__main__':
    unittest.main()
