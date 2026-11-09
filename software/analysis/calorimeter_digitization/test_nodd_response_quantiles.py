"""Controls for exact event quantiles and closed-artifact binding."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import nodd_response_quantiles as q


class QuantileControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'diagnostics.jsonl'
        self.events = [dict(index=i, identity=[7, i], raw_GeV=x,
                            modes={'off': {'energy_GeV': x}, 'on': {'energy_GeV': x}})
                       for i, x in enumerate([0., 1., 3., 8.])]
        self.path.write_text(''.join(json.dumps(e)+'\n' for e in self.events))
        self.row = dict(kind='showers', geometry='nodd', diagnostics=str(self.path),
            sample=dict(kind='showers', geometry='nodd', particle='e-', energy_GeV=5, eta=0,
                        actual_run_number=7, requested_events=4, sha256='raw-input'),
            receipt=dict(exit_code=0, output_sha256=q.sha(self.path), identity={'input_sha256': 'raw-input'}))
        stats = dict(n=4, mean=3., SD=float(np.std([0., 1., 3., 8.], ddof=1)), zero_count=1)
        self.population = dict(geometry='nodd', particle='e-', momentum_GeV=5, eta=0, n=4,
            input_sha256='raw-input', native_output_sha256=q.sha(self.path),
            stages={s: {'energy_GeV': copy.deepcopy(stats)} for s in q.STAGES})

    def test_zeros_and_linear_quantiles(self):
        x = q.checked_totals(self.row, self.population)
        np.testing.assert_array_equal(x[:, 0], [0, 1, 3, 8])
        # Independent order-statistic interpolation, including both endpoints.
        ordered = [0., 1., 3., 8.]
        expected = []
        for p in q.PROBABILITIES:
            rank = p*3
            lo = int(rank)
            hi = min(lo+1, 3)
            expected.append(ordered[lo]+(rank-lo)*(ordered[hi]-ordered[lo]))
        np.testing.assert_allclose(np.quantile(x[:, 0], q.PROBABILITIES, method='linear'), expected, atol=1e-15)

    def test_changed_output_rejected(self):
        self.path.write_text(self.path.read_text()+'\n')
        with self.assertRaisesRegex(ValueError, 'Changed population'):
            q.checked_totals(self.row, self.population)

    def test_wrong_population_or_closed_moments_rejected(self):
        for field, value in [('eta', 2), ('input_sha256', 'other')]:
            altered = copy.deepcopy(self.population); altered[field] = value
            with self.assertRaises(ValueError): q.checked_totals(self.row, altered)
        altered = copy.deepcopy(self.population); altered['stages']['on']['energy_GeV']['zero_count'] = 0
        with self.assertRaisesRegex(ValueError, 'closed moments'): q.checked_totals(self.row, altered)

    def test_reordered_identity_rejected_even_with_updated_hash(self):
        self.events[0]['identity'] = [7, 1]
        self.path.write_text(''.join(json.dumps(e)+'\n' for e in self.events))
        self.row['receipt']['output_sha256'] = self.population['native_output_sha256'] = q.sha(self.path)
        with self.assertRaisesRegex(ValueError, 'event order'): q.checked_totals(self.row, self.population)


if __name__ == '__main__':
    unittest.main()
