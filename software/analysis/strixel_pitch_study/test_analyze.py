"""Paired statistics controls independent of native ACTS dependencies."""
import unittest

import numpy as np

from analyze import basic, paired_widths, verify_full_arrays, perigee_observables, QUANTITIES, validate_matrix, validate_comparison


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

    def test_full_array_replay_preserves_absent_fit_flags(self):
        truth=np.array([[0,0,.2,1.1,.1],[0,0,.2,1.1,.1]],dtype=float)
        fitted=truth.copy();fitted[1,:]=np.nan
        covariance=np.tile(np.eye(5),(2,1,1));covariance[1,:,:]=np.nan
        has=np.array([True,False])
        values,flags=perigee_observables(fitted,truth,covariance)
        self.assertTrue(flags['wrong_charge'][1])  # NaN comparison must be masked.
        a=dict(truth=truth,fitted=fitted,covariance=covariance,has_fitted_parameters=has)
        for q in QUANTITIES:
            for kind in ('residual','pull'):a[q+'_'+kind]=np.where(has,values[q][kind],np.nan)
        a.update({key:value&has for key,value in flags.items()})
        verify_full_arrays(a)
        a['wrong_charge'][1]=True
        with self.assertRaises(ValueError):verify_full_arrays(a)

    def test_incomplete_campaign_cannot_claim_production_matrix(self):
        reports=[dict(pt_GeV=pt,pitch_mm=p,requested_events=20000)
                 for pt in (1,10,100) for p in (.5,1,1.5,2)]
        validate_matrix(reports)
        with self.assertRaises(ValueError):validate_matrix(reports[:4])
        with self.assertRaises(ValueError):validate_matrix(reports+[reports[0]])
        validate_matrix(reports[:4],pilot=True)

    def test_missing_balanced_evidence_cannot_pass(self):
        for value in ({},{'selection.json':True},{'selection.json':True,'material-map.json':False}):
            with self.assertRaises(ValueError):validate_comparison(value)
        validate_comparison({'selection.json':True,'material-map.json':True})


if __name__=='__main__':unittest.main()
