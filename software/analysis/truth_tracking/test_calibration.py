import unittest
import numpy as np

from calibrate_errors import reconcile_table


class HitErrorCalibrationTests(unittest.TestCase):
    def fixture(self, sizes, residuals):
        return {"volume_id": np.ones(len(sizes), dtype=int),
                "clus_size_loc0": np.asarray(sizes),
                "rec_loc0": np.asarray(residuals), "true_loc0": np.zeros(len(sizes))}

    def table(self, values):
        return {"entries": [{"volume": 1, "value": [{"index": 0, "rms": values}]}]}

    def test_last_entry_pools_all_native_overflow_sizes(self):
        data = self.fixture([1, 1, 2, 2, 3, 3], [-1, 1, -2, 2, -8, 8])
        corrected, groups = reconcile_table(data, self.table([1., 2.]))
        self.assertEqual(corrected["entries"][0]["value"][0]["rms"][0], 1.)
        self.assertAlmostEqual(corrected["entries"][0]["value"][0]["rms"][1],
                               np.std([-2, 2, -8, 8]))
        self.assertEqual(groups[-1]["entries"], 4)
        self.assertTrue(groups[-1]["tail"])

    def test_unsupported_internal_size_merges_into_explicit_tail(self):
        data = self.fixture([1, 1, 3, 3, 4, 4], [-1, 1, -3, 3, -4, 4])
        corrected, groups = reconcile_table(data, self.table([1., float("nan"), 3., 4.]))
        self.assertEqual(len(corrected["entries"][0]["value"][0]["rms"]), 2)
        self.assertEqual(groups[-1]["unsupported_tail_merged_at"], 2)
        self.assertEqual(groups[-1]["entries"], 4)

    def test_centered_sd_is_distinct_from_bias_and_uncentered_rms(self):
        data = self.fixture([1, 1], [2., 4.])
        corrected, groups = reconcile_table(data, self.table([1.]))
        self.assertEqual(corrected["entries"][0]["value"][0]["rms"], [1.])
        self.assertEqual(groups[0]["mean_mm"], 3.)
        self.assertAlmostEqual(groups[0]["uncentered_rms_mm"], np.sqrt(10))

    def test_no_fake_error_for_unsupported_training(self):
        with self.assertRaises(ValueError):
            reconcile_table(self.fixture([1], [0.]), self.table([1.]))
        with self.assertRaises(ValueError):
            reconcile_table(self.fixture([1, 1], [0., 0.]), self.table([1.]))


if __name__ == "__main__":
    unittest.main()
