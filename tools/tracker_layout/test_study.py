"""Synthetic analytic controls; fixture values are not detector proposals."""
import copy
import json
import math
from pathlib import Path
import unittest

from study import intersection, sample, validate, KAPPA


class Controls(unittest.TestCase):
    def setUp(self):
        self.cylinder = dict(kind='cylinder', r_m=1., z_min_m=-2., z_max_m=2., x0_percent=1.)
        self.disc = dict(kind='disc', r_min_m=.2, r_max_m=1.5, z_m=1., x0_percent=1.)

    def test_zero_field_analytic_material(self):
        eta = math.asinh(1.)
        hit = intersection(self.cylinder, eta, 0., 10., 0.)
        self.assertAlmostEqual(hit[1], 1.)
        self.assertAlmostEqual(hit[2], math.sqrt(2.))
        self.assertAlmostEqual(hit[3], math.sqrt(2.))
        disk = intersection(self.disc, eta, 0., 10., 0.)
        self.assertAlmostEqual(disk[0], 1.)
        self.assertAlmostEqual(disk[3], math.sqrt(2.))

    def test_curvature_and_field_sign(self):
        eta = math.asinh(.5)
        pt = KAPPA  # fixture: radius1m at1T
        a = intersection(self.cylinder, eta, 0., pt, 1.)
        self.assertAlmostEqual(a[1], math.pi / 6.)
        self.assertEqual(a, intersection(self.cylinder, eta, 0., pt, -1.))
        self.assertIsNone(intersection(self.cylinder, eta, 0., pt / 3., 1.))

    def test_signed_vertex_reflection_and_hole(self):
        a = intersection(self.disc, 1., .15, 1., 3.)
        reflected = dict(self.disc, z_m=-1.)
        b = intersection(reflected, -1., -.15, 1., 3.)
        self.assertAlmostEqual(a[0], b[0])
        self.assertAlmostEqual(a[1], -b[1])
        self.assertIsNone(intersection(self.disc, -1., 0., 1., 3.))
        self.assertIsNone(intersection(self.disc, 4., 0., 1., 3.))
        self.assertIsNone(intersection(self.disc, 0., 0., 1., 3.))

    def test_effective_pair_counted_once(self):
        pair = dict(self.cylinder, id='fixture-pair', subsystem='long_strip')
        row = sample({'layers':[pair]}, 0., 0., 10., 3.)
        self.assertEqual(row['stations'], 1)
        self.assertEqual(row['long_strip_pair_stations'], 1)

    def test_contract_rejects_bad_bounds_and_numbers(self):
        path = Path(__file__).resolve().parents[2] / 'docs/design/DES-006-layouts.json'
        data = json.loads(path.read_text())
        validate(data)
        for key, val in [('r_m', 2.), ('sigma_rphi_m', float('nan')), ('x0_percent', -1.)]:
            bad = copy.deepcopy(data)
            bad['candidates'][0]['layers'][0][key] = val
            with self.assertRaises(ValueError):
                validate(bad)
        bad = copy.deepcopy(data)
        bad['candidates'][1]['id'] = bad['candidates'][0]['id']
        with self.assertRaises(ValueError):
            validate(bad)
        bad = copy.deepcopy(data)
        bad['scan']['eta_step'] = 0
        with self.assertRaises(ValueError):
            validate(bad)


if __name__ == '__main__':
    unittest.main()
