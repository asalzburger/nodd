"""Paired statistics controls independent of native ACTS dependencies."""
import unittest

import numpy as np

from analyze import basic, paired_widths


class PairedStatisticsTest(unittest.TestCase):
    def test_same_event_rescaling_has_exact_paired_ratio(self):
        x=np.random.default_rng(582).normal(size=600)
        factors=np.array([1,2,3,4])
        result=paired_widths(factors[:,None]*x,replicates=80)
        for mode in result:
            for expected,case in zip(factors,mode['cases']):
                self.assertAlmostEqual(case['ratio_to_baseline'],expected)
                self.assertAlmostEqual(case['ratio_se'],0,places=12)

    def test_attrition_is_visible_and_common_sample_is_separate(self):
        x=np.linspace(-3,3,300)
        values=np.tile(x,(4,1))
        values[1,:100]=np.nan
        result=paired_widths(values,replicates=80)
        all_success,common=result
        self.assertEqual(all_success['cases'][1]['entries'],200)
        self.assertEqual(common['generated_or_common_events'],200)
        self.assertNotAlmostEqual(all_success['cases'][1]['ratio_to_baseline'],1)
        self.assertAlmostEqual(common['cases'][1]['ratio_to_baseline'],1)
        self.assertAlmostEqual(common['cases'][1]['ratio_se'],0)

    def test_undefined_small_sample_and_uncut_tail(self):
        result=paired_widths(np.ones((4,29)),replicates=8)
        self.assertIsNone(result[0]['cases'][0]['width68'])
        self.assertIsNone(result[0]['cases'][0]['ratio_to_baseline'])
        x=np.r_[np.linspace(-1,1,100),1000]
        stats=basic(x)
        self.assertEqual(stats['entries'],101)
        self.assertGreater(stats['std'],50)
        self.assertLess(stats['width68'],1)


if __name__=='__main__':unittest.main()
