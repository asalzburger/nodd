"""Controls for correlated counterfactual uncertainty, including physical zeros."""
import unittest

import numpy as np

from untiled_compare import binned_moments, paired_bootstrap


class PairedComparisonTest(unittest.TestCase):
    def test_multiplicative_control_has_zero_width_difference(self):
        response = np.linspace(0, .03, 1000)
        categories = [np.arange(1000) % 10, (np.arange(1000) // 10) % 10]
        means, widths = paired_bootstrap([response, response * 2], categories, 50, 19)
        np.testing.assert_allclose(means[:, 1], means[:, 0] * 2, atol=0, rtol=1e-14)
        np.testing.assert_allclose(widths[:, 1], widths[:, 0], atol=1e-14)

    def test_binned_width_is_sample_sd_and_retains_zero(self):
        response = np.tile([0., 1., 2., 4.], 10)
        categories = np.repeat(np.arange(10), 4)
        means, widths = binned_moments(response, categories)
        np.testing.assert_allclose(means, np.mean([0., 1., 2., 4.]))
        np.testing.assert_allclose(widths, np.std([0., 1., 2., 4.], ddof=1) / means)


if __name__ == "__main__":
    unittest.main()
