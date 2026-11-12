"""Controls for paired weighted populations and undefined response bins."""
import unittest
import numpy as np
from staggered_results import interval, moments


class ReportControls(unittest.TestCase):
    def test_bootstrap_multiplicities_match_explicit_duplicates(self):
        values=np.array([0.,.5,1.,2.,4.,6.]);category=np.array([0,0,0,1,1,1]);counts=np.array([2,1,3,1,4,2])
        means,widths=moments(values,category,counts,2)
        for i in range(2):
            explicit=np.repeat(values[category==i],counts[category==i])
            self.assertAlmostEqual(means[i],explicit.mean())
            self.assertAlmostEqual(widths[i],explicit.std(ddof=1)/explicit.mean())

    def test_zero_and_empty_bins_remain_undefined(self):
        means,widths=moments(np.zeros(3),np.zeros(3,dtype=int),np.ones(3),2)
        self.assertEqual(means[0],0.)
        self.assertTrue(np.isnan(means[1]))
        self.assertTrue(np.isnan(widths).all())
        self.assertEqual(interval(widths),dict(ci95=None,bootstrap_undefined=2))


if __name__=='__main__':unittest.main()
