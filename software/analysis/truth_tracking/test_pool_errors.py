import unittest
import numpy as np
from pool_errors import moments


class PoolErrorsTests(unittest.TestCase):
    def test_total_mixture_includes_between_cluster_mean_variation(self):
        result = moments([-3., -1., 3., 5.])
        self.assertEqual(result['entries'], 4)
        self.assertEqual(result['mean_mm'], 1.)
        self.assertAlmostEqual(result['sigma_mm'], np.sqrt(10.))
        self.assertAlmostEqual(result['uncentered_rms_mm'], np.sqrt(11.))

    def test_missing_and_degenerate_training_rejected(self):
        for values in ([], [1.], [1., 1.], [0., np.nan]):
            with self.assertRaises(ValueError):
                moments(values)


if __name__ == '__main__':
    unittest.main()
