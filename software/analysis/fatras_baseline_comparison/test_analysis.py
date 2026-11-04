"""Scientific guards for attrition, tails and paired resolution statistics."""
import copy
import unittest

import numpy as np

import analyze
from run_native import campaign


class ResolutionStatistics(unittest.TestCase):
    def test_full_tails_retained_beside_core_width(self):
        x=np.concatenate([np.linspace(-1,1,200),[-1000,1000,np.nan]])
        stats=analyze.summary(x,bootstrap=12,rng=np.random.default_rng(1))
        self.assertEqual((stats['entries'],stats['nonfinite']),(202,1))
        self.assertGreater(stats['std'],10*stats['width68'])
        self.assertGreater(stats['rms'],10*stats['width68'])
        self.assertGreater(stats['width68_se'],0)
        self.assertIsNone(analyze.summary(np.arange(29))['width68'])

    def test_primary_ratio_keeps_each_baselines_finite_fit_population(self):
        old=np.linspace(-1,1,200);current=old*2;current[:60]=np.nan
        result=analyze.paired_ratio(old,current,replicates=20,rng=np.random.default_rng(2))
        self.assertEqual((result['old_finite'],result['current_finite'],result['common_finite']),(200,140,140))
        self.assertLess(result['ratio'],1.6)
        self.assertAlmostEqual(result['common_fit_ratio'],2.)
        self.assertEqual(result['valid_bootstraps'],20)
        self.assertLess(result['ratio_bootstrap95'][0],result['ratio_bootstrap95'][1])
        self.assertIsNone(analyze.paired_ratio(np.ones(40),np.arange(40),replicates=2)['ratio'])

    def test_missing_fits_remain_in_generated_denominator(self):
        case={key:np.array(value) for key,value in {
            'selected':[1,1,1],'attempts':[1,1,1],'fitted':[1,1,0],
            'has_parameters':[1,1,0],'finite_fit':[1,0,0],'valid_covariance':[1,0,0],
            'native_match':[1,0,0],'wrong_charge':[1,1,0],
            'created':[10,9,8],'used':[9,5,0]}.items()}
        for key in ('selected','attempts','fitted','has_parameters','finite_fit','valid_covariance','native_match','wrong_charge'):
            case[key]=case[key].astype(bool)
        case['values']={p:{'residual':np.array([.1,np.nan,np.nan]),'pull':np.array([.5,np.nan,np.nan])}
                        for p in analyze.PARAMETERS}
        result=analyze.summarize_case(case,np.ones(3,dtype=bool),0,np.random.default_rng(1))
        self.assertEqual(result['counts']['generated'],3)
        self.assertEqual(result['counts']['fit_failures'],1)
        self.assertEqual(result['counts']['nonfinite_fits'],1)
        self.assertEqual(result['counts']['wrong_charge'],1)
        self.assertAlmostEqual(result['counts']['finite_fit_fraction']['value'],1/3)

    def test_response_and_field_contracts_cannot_drift(self):
        source='software/running/nodd_truth_tracking.py'
        report={'outcome':'completed','simulation':'fatras','events':20000,'pt_GeV':5,'threads':1,
            'campaign':campaign('current'),'scientific_input_revision':'326fed57a3c3aa75466756f47cee2e69d5d22b9b',
            'executed_source_sha256':{source:analyze.sha(analyze.ROOT/source)}}
        analyze.check_contract(report,'current',5)
        for key,value in [('field_Bz_T',2.),('seed',228),('phi_range_rad',[0,np.pi])]:
            bad=copy.deepcopy(report);bad['campaign'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):analyze.check_contract(bad,'current',5)
        bad=copy.deepcopy(report);bad['campaign']['digitization']['short_strip_pitch_mm']=[.075,.5]
        with self.assertRaisesRegex(ValueError,'readout'):analyze.check_contract(bad,'current',5)
        bad=copy.deepcopy(report);bad['events']=100
        with self.assertRaises(ValueError):analyze.check_contract(bad,'current',5)


if __name__=='__main__':unittest.main()
