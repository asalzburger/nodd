import math
import unittest
import numpy as np

from metrics import (binomial_interval, interval_mask, perigee_observables,
                     statistics, validate_covariance, wrap_phi)


class PerformanceMetricsTests(unittest.TestCase):
    def test_phi_boundary_uses_shortest_difference(self):
        self.assertAlmostEqual(float(wrap_phi(-2 * math.pi + .002)), .002)
        fitted = np.array([[0., 0., -math.pi + .001, 1., .1]])
        truth = np.array([[0., 0., math.pi - .001, 1., .1]])
        result, _ = perigee_observables(fitted, truth, np.eye(5)[None])
        self.assertAlmostEqual(result["phi"]["residual"][0], .002)

    def test_pt_pull_includes_covariance_cross_term_and_charge_sign(self):
        # The two charge signs have equal physical covariance after sign change.
        fitted = np.array([[0., 0., 0., 1., .1], [0., 0., 0., 1., -.1]])
        truth = fitted.copy()
        truth[:, 4] *= 1.01
        cov = np.tile(np.diag([.01, .01, .001, .0004, .000001]), (2, 1, 1))
        cov[:, 3, 4] = [.00001, -.00001]
        cov[:, 4, 3] = cov[:, 3, 4]
        values, flags = perigee_observables(fitted, truth, cov)
        a = math.cos(1.) / .1
        b = -math.sin(1.) / .1 ** 2
        expected_variance = a * a * .0004 + b * b * .000001 + 2 * a * b * .00001
        expected_residual = math.sin(1.) * (1 / .1 - 1 / .101)
        np.testing.assert_allclose(values["pt_relative"]["pull"],
                                   expected_residual / math.sqrt(expected_variance))
        self.assertTrue(np.all(flags["valid_covariance"]))
        diagonal_only = a * a * .0004 + b * b * .000001
        self.assertGreater(abs(expected_variance - diagonal_only), 1.e-5)

    def test_invalid_covariance_is_counted_without_removing_residuals(self):
        fitted = np.array([[.1, 0., 0., 1., .1]])
        truth = np.array([[0., 0., 0., 1., .1]])
        covariance = np.eye(5)[None]
        covariance[0, 0, 0] = -1
        values, flags = perigee_observables(fitted, truth, covariance)
        self.assertFalse(flags["valid_covariance"][0])
        self.assertTrue(np.isnan(values["d0"]["pull"][0]))
        self.assertEqual(values["d0"]["residual"][0], .1)
        bad = np.eye(5)[None]
        bad[0, 3, 4] = bad[0, 4, 3] = 2
        self.assertFalse(validate_covariance(bad)[0])

    def test_statistics_do_not_clip_tails_or_turn_empty_bins_into_zero(self):
        values = np.array([-1., 0., 1., 20., np.nan])
        result = statistics(values, probability=.5, minimum_entries=3,
                            bootstrap_replicates=40)
        self.assertEqual(result["entries"], 4)
        self.assertEqual(result["nonfinite"], 1)
        self.assertEqual(result["mean"], 5.)
        self.assertAlmostEqual(result["rms"], math.sqrt(402 / 4))
        self.assertAlmostEqual(result["width68"], 3.)
        empty = statistics([], minimum_entries=3, bootstrap_replicates=40)
        self.assertIsNone(empty["std"])
        self.assertEqual(empty["status"], "undersampled")

    def test_eta_edges_partition_including_final_upper_edge(self):
        eta = np.array([-1., -.5, 0., .5, 1.])
        masks = [interval_mask(eta, a, b, final=(b == 1.))
                 for a, b in [(-1., 0.), (0., 1.)]]
        np.testing.assert_array_equal(np.sum(masks, axis=0), np.ones(5))
        np.testing.assert_array_equal(interval_mask(eta, .5, 1., final=True, absolute=True),
                                     [True, True, False, True, True])

    def test_wilson_preserves_empty_and_complete_denominators(self):
        self.assertIsNone(binomial_interval(0, 0)["value"])
        self.assertEqual(binomial_interval(10, 10)["value"], 1.)
        self.assertGreater(binomial_interval(0, 10)["high"], 0.)
        with self.assertRaises(ValueError):
            binomial_interval(11, 10)

    def test_event_bootstrap_is_reproducible(self):
        data = np.linspace(-1, 1, 100)
        first = statistics(data, bootstrap_replicates=20, rng=np.random.default_rng(12))
        second = statistics(data, bootstrap_replicates=20, rng=np.random.default_rng(12))
        self.assertEqual(first, second)
        self.assertGreater(first["width68_se"], 0)


if __name__ == "__main__":
    unittest.main()
