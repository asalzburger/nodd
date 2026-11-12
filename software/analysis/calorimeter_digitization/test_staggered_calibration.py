"""Scientific controls for held-out response fitting and multiplicity accounting."""
import unittest
import numpy as np

from staggered_calibration import CrossFit, folds, solve_model


def fixture():
    n = 600
    rng = np.random.default_rng(17)
    x = rng.uniform(-1, 1, (n, 2))
    response = .015 * (1 + .3*x[:, 0] - .1*x[:, 1])
    valid = np.ones(n, dtype=bool); valid[0] = False; response[0] = 0
    energy=np.linspace(10,80,n)
    return dict(event=np.arange(n), features=x, response=response, signal=response*energy,
                valid_axis=valid, region=np.arange(n) % 2, energy=energy)


class CalibrationControls(unittest.TestCase):
    def test_weighted_moments_match_explicit_fit(self):
        rng = np.random.default_rng(41)
        f = rng.normal(size=(100, 3)); z = np.column_stack([np.ones(100), f])
        y = .02 * (1 + .1*f[:, 0]); weight = rng.integers(1, 4, 100)
        actual = solve_model(z.T@(weight[:, None]*z), z.T@(weight*y), .01)
        repeated = np.repeat(np.arange(100), weight)
        zz, yy = z[repeated], y[repeated]
        expected = solve_model(zz.T@zz, zz.T@yy, .01)
        np.testing.assert_allclose(actual.coefficient, expected.coefficient, atol=1e-12)
        self.assertAlmostEqual(actual.response_scale, expected.response_scale)

    def test_own_outer_fold_labels_cannot_change_predictions(self):
        data = fixture(); first = CrossFit(data); predicted = first.predict()
        own = first.outer == 2
        changed = dict(data); changed['response'] = data['response'].copy()
        changed['response'][own] *= 5
        second = CrossFit(changed).predict()
        # Compare inferred gain, which may not depend on that held-out label.
        np.testing.assert_allclose(predicted['gain'][own], second['gain'][own], atol=0, rtol=0)

    def test_zero_fallback_and_gains_are_bounded(self):
        model = CrossFit(fixture()); result = model.predict(record=True)
        self.assertEqual(result['response'][0], 0)
        self.assertTrue(result['fallback'][0])
        self.assertTrue(np.all(result['gain'] >= .5))
        self.assertTrue(np.all(result['gain'] <= 3.))
        self.assertEqual(len(result['records']), 10)

    def test_full_inferred_energy_does_not_use_held_out_truth(self):
        data=fixture();first=CrossFit(data);own=first.outer==2
        changed=dict(data);changed['energy']=data['energy'].copy();changed['response']=data['response'].copy()
        changed['energy'][own]*=2;changed['response'][own]/=2
        for prior in ('uniform','inverse_energy'):
            a=first.predict(prior=prior);b=CrossFit(changed).predict(prior=prior)
            np.testing.assert_allclose(a['inferred_energy'][own],b['inferred_energy'][own],atol=0,rtol=0)

    def test_duplicate_multiplicities_keep_the_same_folds(self):
        data = fixture(); model = CrossFit(data)
        before = model.outer.copy(); counts = np.ones(len(before)); counts[10] = 8
        model.predict(counts)
        np.testing.assert_array_equal(model.outer, before)
        np.testing.assert_array_equal(before, folds(data['event'], 5, 1337000))


if __name__ == '__main__':
    unittest.main()
