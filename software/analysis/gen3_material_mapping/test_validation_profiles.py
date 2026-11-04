"""Scientific normalization controls independent of detector-specific values."""
import unittest
import numpy as np
from export_validation import profile


class ProfileControls(unittest.TestCase):
    def test_zero_contributions_count_in_mean_and_sem(self):
        p=profile(np.array([.2,.4,.8]),np.array([0.,0.,3.]),np.array([0.,1.]))
        self.assertEqual(p['counts'],[3]);np.testing.assert_allclose(p['mean'],[1.]);np.testing.assert_allclose(p['variance'],[2/3])

    def test_empty_bins_explicit_and_range_not_silently_clipped(self):
        p=profile(np.array([.5]),np.array([2.]),np.array([0.,1.,2.]))
        self.assertEqual(p['empty_bins'],[1])
        with self.assertRaises(ValueError):profile(np.array([2.1]),np.array([2.]),np.array([0.,1.,2.]))


if __name__=='__main__':unittest.main()
