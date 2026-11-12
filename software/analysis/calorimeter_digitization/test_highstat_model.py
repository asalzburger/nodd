import unittest
import json
import numpy as np
from highstat_model import fit, quantile, restore


class CalibrationControls(unittest.TestCase):
    def data(self):
        rng = np.random.default_rng(81); n = 1800
        feature = rng.uniform(0, 1, (n, 10)); energy = rng.uniform(10, 80, n)
        response = .012 * (.6 + feature[:, 1] + .2 * np.maximum(feature[:, 3] - .5, 0))
        signal = response * energy; valid = np.ones(n, dtype=bool)
        signal[::100] = 0; response[::100] = 0; valid[::100] = False
        role = np.arange(n) % 3
        return dict(features=feature, signal=signal, energy=energy, response=response,
                    region=(feature[:, 0] > .5).astype(int), valid_axis=valid), role

    def test_weighted_quantiles_match_explicit_duplicates(self):
        x = np.array([9., 3., 0., 8., 1.]); w = np.array([3, 0, 2, 1, 4])
        q = np.linspace(0, 1, 101)
        np.testing.assert_allclose(quantile(x, w, q), np.quantile(np.repeat(x, w), q))

    def test_closure_only_changes_scale_and_keeps_zeros(self):
        data, role = self.data(); model = fit(data, role, 'spline')
        p = model.infer(data['features'], data['signal'], data['region'], data['valid_axis'])
        closed = p['energy'][role == 2] / data['energy'][role == 2]
        self.assertAlmostEqual(closed.mean(), 1, places=12)
        before = p['pre_energy'] / data['energy']; after = p['energy'] / data['energy']
        self.assertAlmostEqual(before.std(ddof=1)/before.mean(), after.std(ddof=1)/after.mean(), places=12)
        self.assertTrue(np.all(p['energy'][data['signal'] == 0] == 0))
        self.assertTrue(np.all((p['gain'] >= .5) & (p['gain'] <= 3)))

    def test_closure_labels_do_not_change_response_coefficients(self):
        data, role = self.data(); first = fit(data, role, 'spline')
        other = {k:v.copy() for k,v in data.items()}
        other['energy'][role == 2] *= 1.1; other['response'][role == 2] /= 1.1
        second = fit(other, role, 'spline')
        for a,b in zip(first.models, second.models):
            self.assertEqual(a.record(), b.record())
        self.assertAlmostEqual(second.closure / first.closure, 1.1, places=12)

    def test_observable_only_inference_and_serialized_roundtrip(self):
        for kind in ('original','spline'):
            data, role = self.data(); model = fit(data, role, kind)
            result = model.infer(data['features'], data['signal'], data['region'], data['valid_axis'])
            data['energy'] *= 4; data['response'] /= 4
            serialized=json.loads(json.dumps(model.record(),allow_nan=False))
            repeat = restore(serialized).infer(data['features'], data['signal'], data['region'], data['valid_axis'])
            for key in result:np.testing.assert_array_equal(result[key], repeat[key])

    def test_constant_features_produce_no_duplicate_knots(self):
        data, role = self.data(); data['features'][:, 2] = 0
        model = fit(data, role, 'spline')
        for m in model.models:
            self.assertEqual(m.basis.knots[2], [])
            for knots in m.basis.knots:self.assertEqual(len(knots), len(set(knots)))

    def test_bootstrap_refit_matches_explicit_duplicate_populations(self):
        data,role=self.data();count=np.random.default_rng(182).integers(0,4,len(role))
        repeated={k:np.repeat(v,count,axis=0) for k,v in data.items()}
        repeated_role=np.repeat(role,count)
        for kind in ('original','spline'):
            weighted=fit(data,role,kind,count);explicit=fit(repeated,repeated_role,kind)
            self.assertAlmostEqual(weighted.closure,explicit.closure,places=10)
            for a,b in zip(weighted.models,explicit.models):
                self.assertEqual((a.regularization,a.knot_count),(b.regularization,b.knot_count))
                np.testing.assert_allclose(a.coefficient,b.coefficient,rtol=1e-8,atol=1e-9)
            a=weighted.infer(data['features'],data['signal'],data['region'],data['valid_axis'])
            b=explicit.infer(data['features'],data['signal'],data['region'],data['valid_axis'])
            np.testing.assert_allclose(a['energy'],b['energy'],rtol=1e-9,atol=1e-9)


if __name__ == '__main__':unittest.main()
