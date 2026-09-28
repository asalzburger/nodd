"""Independent physics controls; NumPy tests skip when optional dependency is absent."""

import importlib.util
import math
import unittest

from covariance_control import crossed_measurements, transverse_covariance


class IntersectionControls(unittest.TestCase):
    def test_vertex_reflection_and_disk_aperture(self):
        # Synthetic test dimensions: a forward annulus straddles the eta=4 ray.
        layers = [{"id": str(sign), "kind": "disc", "z_m": sign * 3.0,
                   "r_min_m": 0.1, "r_max_m": 0.12, "sigma_rphi_m": 1e-5}
                  for sign in (-1, 1)]
        candidate = {"layers": layers}
        positive = crossed_measurements(candidate, 4.0, 0.15)
        negative = crossed_measurements(candidate, -4.0, -0.15)
        self.assertEqual(len(positive), 1)
        self.assertEqual(len(negative), 1)
        self.assertAlmostEqual(positive[0]["r_m"], 2.85 / math.sinh(4))
        self.assertAlmostEqual(positive[0]["r_m"], negative[0]["r_m"])
        self.assertEqual(crossed_measurements(candidate, 0.0, 0.0), [])
        self.assertEqual(crossed_measurements(candidate, 4.0, 0.5), [])


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy is optional for documentation-only checks")
class CovarianceControls(unittest.TestCase):
    def test_three_point_second_difference(self):
        # At synthetic radii 1,2,3 m, kappa=y1-2*y2+y3 exactly.
        # Independent unit-variance measurements therefore give Var(kappa)=6.
        measurements = [{"r_m": r, "sigma_rphi_m": 1.0} for r in (1.0, 2.0, 3.0)]
        result = transverse_covariance(measurements)
        self.assertAlmostEqual(result["sigma_kappa_per_m"], math.sqrt(6), places=12)
        self.assertEqual(result["information_rank"], 3)

    def test_precision_scaling_and_missing_lever_arm(self):
        measurements = [{"r_m": r, "sigma_rphi_m": 1e-5} for r in (0.1, 0.2, 0.3, 0.4)]
        nominal = transverse_covariance(measurements)
        coarser = transverse_covariance([
            {**m, "sigma_rphi_m": 2 * m["sigma_rphi_m"]} for m in measurements
        ])
        self.assertAlmostEqual(coarser["sigma_kappa_per_m"] / nominal["sigma_kappa_per_m"], 2)
        with self.assertRaisesRegex(ValueError, "rank deficient"):
            transverse_covariance([{"r_m": 0.1, "sigma_rphi_m": 1e-5}] * 4)


if __name__ == "__main__":
    unittest.main()
