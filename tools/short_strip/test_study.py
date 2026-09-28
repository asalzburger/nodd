"""Independent geometry controls for unsigned DES-007 screening."""
import json
import math
import unittest
from pathlib import Path
import numpy as np
import study


class GeometryTest(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(Path(study.INPUT).read_text())

    def test_area_and_containment_controls(self):
        p = study.rectangle(10, 20, 4)
        self.assertEqual(study.area(p), 40)
        self.assertEqual(study.inside(p, np.array([15, 0, 15, 10]),
                                     np.array([0, 0, 3, 2])).tolist(), [True, False, False, True])
        self.assertAlmostEqual(study.area(study.rotate(p, .72)), 40)
        self.assertAlmostEqual(study.radial_extent(p)[0], 10)
        self.assertAlmostEqual(study.radial_extent(p)[1], math.sqrt(404))

    def test_collision_controls(self):
        p = study.rectangle(10, 20, 4)
        self.assertTrue(study.intersects(p, p+np.array([3, 1])))
        self.assertFalse(study.intersects(p, p+np.array([10, 0])))
        self.assertFalse(study.intersects(p, p+np.array([0, 8])))
        self.assertTrue(study.intersects(p, study.rotate(p, .05)))

    def test_shapes_identifiers_and_angular_search_bound(self):
        for c in self.cfg['candidates']:
            rings = study.layout(c, self.cfg)
            mods = study.modules(rings, self.cfg)
            self.assertEqual(len({(m['ring'], m['module']) for m in mods}), len(mods))
            for r in rings:
                p = r['active']
                # Check CCW convexity, not just unsigned area.
                d = np.roll(p, -1, axis=0)-p
                self.assertTrue(np.all(d[:, 0]*np.roll(d[:, 1], -1)-d[:, 1]*np.roll(d[:, 0], -1)>0))
                angles = np.abs(np.arctan2(p[:, 1], p[:, 0]))
                self.assertLess(angles.max(), 1.5*2*math.pi/r['count'])
                self.assertEqual(r['count'] % 2, 0)

    def test_fast_coverage_against_every_module(self):
        # Independent brute-force global-coordinate half-space intersection.
        # Includes non-zero vertex and all z-levels; no nearest-module shortcut.
        cfg = self.cfg
        nr, np_ = 37, 121
        radius = cfg['inner_radius']+(np.arange(nr)+.5)*(cfg['outer_radius']-cfg['inner_radius'])/nr
        phi = (np.arange(np_)+.5)*2*math.pi/np_
        xx = radius[:, None]*np.cos(phi)
        yy = radius[:, None]*np.sin(phi)
        for c in cfg['candidates']:
            rings = study.layout(c, cfg)
            mods = study.modules(rings, cfg)
            for vertex in (None, 150.0):
                hits = np.zeros((nr, np_), dtype=int)
                for m in mods:
                    factor = 1 if vertex is None else (cfg['disk_z']+m['z']-vertex)/(cfg['disk_z']-vertex)
                    # Global rotated polygons and point coordinates.
                    hits += study.inside(m['active'], xx*factor, yy*factor)
                result = study.sample(rings, cfg, nr, np_, vertex)
                self.assertEqual(result['uncovered_bins'], int((hits == 0).sum()))
                weights = np.broadcast_to(radius[:, None], hits.shape)
                self.assertAlmostEqual(result['mean_sensor_crossings'], float((weights*hits).sum()/weights.sum()))

    def test_baseline_channel_arithmetic(self):
        self.assertAlmostEqual(48*96/(.075*.5), 122880)
        self.assertEqual(round(48/.075), 640)
        self.assertEqual(round(96/.5), 192)

    def test_rejected_control_and_clearance(self):
        # Small grid suffices to expose large five-ring radial gaps.
        c = self.cfg['candidates'][-1]
        rings = study.layout(c, self.cfg)
        self.assertGreater(study.sample(rings, self.cfg, 100, 360)['uncovered_area_fraction'], .03)
        for c in self.cfg['candidates']:
            self.assertEqual(study.collisions(study.modules(study.layout(c, self.cfg), self.cfg)), [])


if __name__ == '__main__':
    unittest.main()
