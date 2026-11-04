"""Scientific accounting and paired-comparison controls."""
import unittest
import numpy as np

from analyze import wilson, summarize, paired_comparison


def sample(n=100):
    x=np.linspace(-1,1,n)
    return {"event_id":np.arange(n), "eta":x.copy(), "phi":x.copy(), "pt":np.ones(n),
        "charge":np.ones(n), "created":np.full(n,10), "used":np.full(n,10),
        "incident_records":np.full(n,10), "proto":np.full(n,10),
        "fitted":np.ones(n,dtype=bool), "wrong_charge":np.zeros(n,dtype=bool),
        "valid_covariance":np.ones(n,dtype=bool),
        "values":{q:{"residual":x.copy(), "pull":x.copy()} for q in
                  ("d0","z0","pt_relative","q_over_pt_relative")}}


class Accounting(unittest.TestCase):
    def test_zero_hit_and_missing_fit_remain_in_denominator(self):
        c=sample(); c["created"][:10]=0; c["used"][:10]=0; c["fitted"][:10]=False
        for pair in c["values"].values():
            for data in pair.values(): data[:10]=np.nan
        r=summarize(c,np.ones(100,dtype=bool),np.random.default_rng(1),10)
        self.assertEqual(r["generated"],100)
        self.assertEqual(r["fit_tracks"],90)
        self.assertEqual(r["stages"]["created"]["ge10"]["value"],.9)
        self.assertEqual(r["quantities"]["d0"]["residual"]["entries"],90)

    def test_exact_scale_paired_bootstrap(self):
        a,b=sample(),sample()
        for pair in b["values"].values(): pair["residual"]*=.8
        result=paired_comparison(a,b,10)[0]["quantities"]["d0"]
        self.assertAlmostEqual(result["ratio"],.8)
        np.testing.assert_allclose(result["ratio_bootstrap95"],[.8,.8])

    def test_different_generated_truth_rejects_pairing(self):
        a,b=sample(),sample(); b["phi"][0]+=.001
        with self.assertRaisesRegex(ValueError,"identical generated phi"):
            paired_comparison(a,b,10)

    def test_acceptance_endpoint_in_pair_denominator(self):
        a,b=sample(),sample();a["eta"][-1]=b["eta"][-1]=4
        self.assertEqual(paired_comparison(a,b,10)[0]["generated"],100)

    def test_zero_width_is_unmeasurable_ratio(self):
        a,b=sample(),sample()
        for pair in a["values"].values(): pair["residual"][:]=0
        result=paired_comparison(a,b,10)[0]["quantities"]["d0"]
        self.assertIsNone(result["ratio"])
        self.assertIsNone(result["ratio_bootstrap95"])

    def test_interval_endpoints_and_empty_bins(self):
        self.assertEqual(wilson(0,0)["value"],None)
        self.assertAlmostEqual(wilson(0,10)["low"],0)
        self.assertAlmostEqual(wilson(10,10)["high"],1)
        self.assertLess(wilson(50,100)["low"],.5)
        self.assertGreater(wilson(50,100)["high"],.5)


if __name__=="__main__": unittest.main()
