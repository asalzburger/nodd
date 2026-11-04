import math
import unittest

import numpy as np

from pull_histograms import bound_pulls, common_edges, histogram


class PullDistributionControls(unittest.TestCase):
    def test_truth_minus_fit_sign_wrapped_phi_and_time(self):
        truth = np.array([[1., 0., math.pi - .01, 1., .1, 0.]])
        fitted = np.array([[-1., .4, -math.pi + .01, .8, .12, .4]])
        covariance = np.diag([4., .04, .0001, .01, .0001, 4.])[None]
        values, flags = bound_pulls(fitted, truth, covariance)
        np.testing.assert_allclose(values, [[1., -2., -2., 2., -2., -.2]], atol=1e-12)
        self.assertTrue(flags["valid_covariance"][0])

    def test_bad_six_parameter_covariance_keeps_missing_pull_explicit(self):
        truth = np.array([[0., 0., 0., 1., .1, 0.]])
        bad = np.eye(6)[None]
        bad[0, 0, 5] = bad[0, 5, 0] = 2
        values, flags = bound_pulls(truth, truth, bad)
        self.assertFalse(flags["valid_covariance"][0])
        self.assertTrue(np.all(np.isnan(values)))

    def test_common_edges_retain_extreme_tails_and_missing_entries(self):
        arrays = [np.array([-1e6, -5., 0., 5., 1e6, np.nan]), np.array([2e7])]
        edges = common_edges(arrays, 5., .1, 16)
        for values in arrays:
            result = histogram(values, edges, 5.)
            self.assertEqual(result["underflow"] + result["overflow"], 0)
            self.assertEqual(sum(result["counts"]), result["entries"])
        self.assertEqual(histogram(arrays[0], edges, 5.)["outside_core"], 2)
        self.assertEqual(histogram(arrays[0], edges, 5.)["nonfinite"], 1)

    def test_variable_bin_density_integrates_to_all_finite_entries(self):
        edges = np.array([0., 1., 3.])
        result = histogram([.5, 1.5, 2.5], edges, 5.)
        np.testing.assert_array_equal(result["counts"], [1, 2])
        density = np.asarray(result["counts"]) / result["entries"] / np.diff(edges)
        np.testing.assert_allclose(density, [1/3, 1/3])
        self.assertAlmostEqual(float(np.sum(density * np.diff(edges))), 1.)


if __name__ == "__main__":
    unittest.main()
