"""Threshold, weighted bootstrap, event inclusion and paired-statistics controls."""
import unittest
import numpy as np

from compare import categories,statistics,weighted,summarize


class StatisticsControls(unittest.TestCase):
    def test_global_thresholds_do_not_become_bin_local_thresholds(self):
        r=np.array([0.,.1,.2,.3]);a=statistics(r,.15,.25)
        self.assertEqual((a['common_tail_events'],a['common_tail_denominator']),(2,4))
        self.assertEqual((a['own_global_tail_events'],a['own_global_tail_denominator']),(3,4))
        self.assertEqual(a['zero_events'],1)
        self.assertEqual(a['common_tail_threshold_R'],.15)

    def test_weighted_statistics_equal_explicit_whole_event_resampling(self):
        r=np.array([0.,1.,2.,4.]);cat=np.array([0,0,1,1]);w=np.array([1,2,2,3]);threshold=1.5
        actual=weighted(r,cat,w,2,threshold)
        for i in range(2):
            x=np.repeat(r[cat==i],w[cat==i]);expected=[x.mean(),x.std(ddof=1),x.std(ddof=1)/x.mean(),np.mean(x<threshold)]
            np.testing.assert_allclose(actual[i],expected,rtol=1e-14)

    def test_fine_transition_keeps_outside_events_in_other_projections(self):
        p=np.array([[20.,eta,0.] for eta in (0.,1.1,1.2,1.499,1.55,2.9)])
        cat=categories(p)
        self.assertEqual(cat['global'].tolist(),[0]*6)
        self.assertEqual(cat['fine_transition'].tolist(),[-1,0,2,7,9,-1])
        self.assertEqual(cat['broad_eta'].tolist(),[0,0,1,1,2,2])

    def fixture(self):
        n=3000;rng=np.random.default_rng(71)
        primary=np.column_stack((rng.uniform(10,80,n),rng.uniform(-3,3,n),rng.uniform(-np.pi,np.pi,n)))
        response=rng.uniform(.05,.25,n);response[::29]=0
        return primary,response

    def test_identical_variants_have_zero_paired_differences_and_full_covariance(self):
        p,r=self.fixture();a=summarize(p,dict(standard=r,candidate=r.copy()),replicates=30,seed=11)
        self.assertEqual(a['models']['standard']['global']['events'],3000)
        self.assertEqual(a['models']['standard']['global']['zero_events'],len(r[::29]))
        self.assertEqual(len(a['width_covariance_order']),42)
        np.testing.assert_allclose(np.array(a['width_covariance']),np.array(a['width_covariance']).T)
        for rows in a['candidate_minus_standard'].values():
            for row in rows:
                for result in row.values():self.assertEqual(result['difference'],0.);self.assertEqual(result['ci95'],[0.,0.])

    def test_scaled_candidate_keeps_common_cut_and_own_global_diagnostic(self):
        p,r=self.fixture();a=summarize(p,dict(standard=r,candidate=2*r),replicates=30,seed=11)
        threshold=.5*float(r.mean());self.assertEqual(a['common_tail']['threshold_R'],threshold)
        for name,model in a['models'].items():
            for projection in model['projections'].values():
                for row in projection['bins']:
                    self.assertEqual(row['common_tail_threshold_R'],threshold)
                    self.assertEqual(row['own_global_tail_threshold_R'],model['global_own_threshold_R'])
        self.assertAlmostEqual(a['models']['candidate']['global']['fractional_width'],a['models']['standard']['global']['fractional_width'])
        self.assertEqual(a['models']['candidate']['global']['own_global_tail_events'],a['models']['standard']['global']['own_global_tail_events'])
        self.assertLess(a['models']['candidate']['global']['common_tail_events'],a['models']['standard']['global']['common_tail_events'])
        self.assertGreater(a['candidate_minus_standard']['global'][0]['mean_response']['difference'],0)

    def test_nonfinite_negative_and_incomplete_responses_rejected(self):
        p,r=self.fixture()
        for bad in (r[:-1],np.full(len(r),np.nan),-r):
            with self.assertRaises(ValueError):summarize(p,dict(standard=r,candidate=bad),replicates=2)


class PercentileDrawingControls(unittest.TestCase):
    def test_estimate_outside_percentile_interval_does_not_move_either_endpoint(self):
        from compare import draw_percentile
        class Axes:
            def __init__(self):self.segments=[];self.points=[]
            def vlines(self,x,low,high,**kwargs):self.segments.append((np.asarray(x),np.asarray(low),np.asarray(high)))
            def plot(self,x,y,**kwargs):self.points.append((np.asarray(x),np.asarray(y),kwargs))
        ax=Axes();draw_percentile(ax,[1.,2.],[3.,-3.],[[0.,1.],[-1.,0.]],color='#cccc00',marker='o')
        np.testing.assert_array_equal(ax.segments[0][1],[0.,-1.]);np.testing.assert_array_equal(ax.segments[0][2],[1.,0.])
        np.testing.assert_array_equal(ax.points[-1][1],[3.,-3.])


if __name__=='__main__':unittest.main()
