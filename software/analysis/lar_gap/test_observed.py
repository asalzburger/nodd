"""Adverse precision, accounting, identity, threshold and shared-bootstrap controls."""
from copy import deepcopy
import math
import unittest
import numpy as np

from observed_transport import collection_closure,f32,float32_cell_bounds,match_failures,event_identity
from observed_compare import summarize,variance_identity,TAIL_THRESHOLD


def fixture():
    failure=dict(run=0,event=0,track=1,parent=0,step=4,pdg=11,weight=1.,raw_volume=13,volume='w1_gap1_7',collection='LArEndcapHits',
        edep_MeV=.3,contribution_MeV=.3,reason='Hit outside turbine wheel/depth')
    for key in ('pre_global_mm','post_global_mm','mid_global_mm','pre_local_mm','post_local_mm','mid_local_mm'):failure[key]=[1.,2.,3.]
    row=dict(A_MeV=((.1+.2)+2.)+.3,U_MeV=.3,sensitive_callbacks=5,positive_steps=4,zero_steps=1,
        cells=[dict(cell=11,sum_MeV=.1+.2,steps=2),dict(cell=12,sum_MeV=2.,steps=1)],failures=[failure])
    hits={11:f32((.1+.2)/1000),12:f32(2./1000)}
    return row,hits


class PrecisionAndCoverage(unittest.TestCase):
    def test_native_and_saved_float32_closures_keep_rounding_residual(self):
        row,hits=fixture();result=collection_closure(row,hits)
        self.assertEqual(result['positive_steps'],4);self.assertEqual(result['failed_steps'],1)
        self.assertNotEqual(result['rounding_residual_GeV'],0.)
        self.assertLessEqual(abs(result['A_GeV']-result['H_GeV']-result['U_GeV']),result['saved_closure_bound_GeV'])

    def test_power_of_two_float32_cell_has_asymmetric_rounding_interval(self):
        lo,hi=float32_cell_bounds(1.)
        self.assertEqual(1.-lo,2**-25);self.assertEqual(hi-1.,2**-24)
        self.assertEqual(f32((lo+1.)/2),1.);self.assertEqual(f32((hi+1.)/2),1.)
        self.assertNotEqual(f32(math.nextafter(hi,math.inf)),1.)

    def test_wrong_rounding_missing_and_extra_saved_cells_fail(self):
        row,hits=fixture()
        for changed in ({11:hits[11]},{**hits,13:1.},{**hits,11:f32(hits[11]*1.01)}):
            with self.assertRaises(ValueError):collection_closure(row,changed)

    def test_missing_steps_failed_identity_and_energy_closure_fail(self):
        row,hits=fixture()
        for key,value in (('positive_steps',5),('sensitive_callbacks',6),('A_MeV',row['A_MeV']+.0001),('U_MeV',0.)):
            changed=deepcopy(row);changed[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):collection_closure(changed,hits)
        changed=deepcopy(row);changed['failures']*=2
        with self.assertRaises(ValueError):collection_closure(changed,hits)

    def test_nonunit_weight_nonpositive_and_modified_contributions_fail(self):
        row,hits=fixture()
        for key,value in (('weight',2.),('edep_MeV',0.),('contribution_MeV',.4)):
            changed=deepcopy(row);changed['failures'][0][key]=value
            with self.assertRaises(ValueError):collection_closure(changed,hits)

    def test_original_error_matching_uses_raw_identity_and_logger_precision(self):
        row,_=fixture();match_failures(row['failures'],[(13,'w1_gap1_7',[1.,2.,3.])])
        for logged in ([],[(14,'w1_gap1_7',[1.,2.,3.])],[(13,'w1_gap1_7',[1.00001,2.,3.])]):
            with self.assertRaises(ValueError):match_failures(row['failures'],logged)

    def test_duplicate_unexpected_event_and_unaudited_rounding_mode_fail(self):
        row=dict(run=0,event=0,rounding_mode='FE_TONEAREST');event_identity(row,set(),{0})
        for changed,seen in ((row,{0}),({**row,'event':1},set()),({**row,'run':1},set()),({**row,'rounding_mode':'FE_DOWNWARD'},set())):
            with self.assertRaises(ValueError):event_identity(changed,seen,{0})


class ObservedStatistics(unittest.TestCase):
    def data(self):
        rng=np.random.default_rng(92);n=3000
        primary=np.column_stack((rng.uniform(10,80,n),rng.uniform(-3,3,n),rng.uniform(-np.pi,np.pi,n)))
        s=rng.uniform(.05,.25,n);u=np.zeros(n);u[::37]=.01;h=s+2e-9
        values={name:dict(S=s.copy(),U=u.copy(),A=s+u,H=h.copy()) for name in ('standard','candidate')}
        bounds={v:np.full(n,1e-15) for v in values};failed={v:(u>0).astype(int) for v in values}
        return primary,values,bounds,failed

    def test_variance_identity_retains_saved_rounding_epsilon(self):
        _,values,_,_=self.data();v=values['standard'];r=variance_identity(v['A'],v['S'],v['U'],v['H'],np.full(len(v['A']),1e-15))
        self.assertAlmostEqual(r['mean_saved_minus_native_rounding'],2e-9,places=15)
        self.assertLessEqual(abs(r['variance_identity_residual']),r['variance_identity_bound'])
        self.assertAlmostEqual(r['observed_mean_A_minus_H'],r['predicted_mean_A_minus_H'],places=15)

    def test_four_series_share_bootstrap_covariance_and_original_threshold(self):
        p,v,b,f=self.data();r=summarize(p,v,b,f,replicates=20,seed=7)
        self.assertEqual(len(r['width_covariance_order']),84)
        covariance=np.array(r['width_covariance']);np.testing.assert_allclose(covariance,covariance.T)
        # Same two geometries have identically resampled principal widths.
        np.testing.assert_array_equal(covariance[:42,:42],covariance[42:,42:])
        for view in r['views'].values():
            self.assertEqual(view['common_tail']['threshold_R'],TAIL_THRESHOLD)
            for rows in view['candidate_minus_standard'].values():
                for row in rows:
                    for statistic in row.values():self.assertEqual(statistic['difference'],0.);self.assertEqual(statistic['ci95'],[0.,0.])
        self.assertNotEqual(r['missing']['standard']['global'][0]['mean_delta_U_over_E'],r['missing']['standard']['global'][0]['missing_fraction_sum_U_over_sum_A'])
        rng=np.random.default_rng(7);ratios=[]
        for _ in range(20):
            weights=np.bincount(rng.integers(len(p),size=len(p)),minlength=len(p))
            ratios.append(np.dot(weights,v['standard']['U']*p[:,0])/np.dot(weights,v['standard']['A']*p[:,0]))
        np.testing.assert_allclose(r['missing']['standard']['global'][0]['missing_fraction_bootstrap']['ci95'],np.quantile(ratios,[.025,.975]),rtol=1e-14)

    def test_replacing_frozen_threshold_and_broken_variance_identity_fail(self):
        p,v,b,f=self.data()
        with self.assertRaises(ValueError):summarize(p,v,b,f,replicates=2,threshold=.5*v['standard']['A'].mean())
        v['standard']['A'][0]+=.1
        with self.assertRaises(ValueError):variance_identity(v['standard']['A'],v['standard']['S'],v['standard']['U'],v['standard']['H'],b['standard'])


if __name__=='__main__':unittest.main()
