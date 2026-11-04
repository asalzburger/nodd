"""Checks of common support, additive means, conditional errors and palette."""
import copy
from pathlib import Path
import unittest

import numpy as np

from compare import COLORS, COMPONENTS, EDGES, assemble, crop, ratio


class ComparisonTests(unittest.TestCase):
    def fixtures(self, edges=EDGES):
        n = len(edges)-1
        q = {c: {'mean': np.full(n, i+1.).tolist(), 'variance': np.full(n, .02).tolist()}
             for i, c in enumerate(COMPONENTS)}
        q['total'] = {'mean': np.full(n, 36.).tolist(), 'variance': np.full(n, .5).tolist()}
        truth = {'axes': {'eta': {'edges': edges.tolist(), 'counts': [10]*n,
                 'quantities': {key: copy.deepcopy(q) for key in ('X0', 'L0')}}},
                 'classification': {'unassigned_steps': 0, 'density_mismatches': 0}, 'checks': {}}
        acts = {'axes': {'eta': {'edges': edges.tolist(), 'quantities': {
            key: {'counts': [12]*n, 'mean': [36.]*n, 'variance': [.36]*n} for key in ('X0', 'L0')}}}}
        return truth, acts

    def test_crop_keeps_bin_means_and_own_counts(self):
        truth, _ = self.fixtures(np.linspace(-4.5, 4.5, 91))
        g = truth['axes']['eta']; g['counts'] = list(range(1, 91))
        g['quantities']['X0']['total']['mean'] = list(range(90))
        cropped = crop(g)
        self.assertEqual(cropped['counts'], list(range(6, 86)))
        self.assertEqual(cropped['quantities']['X0']['total']['mean'], list(range(5, 85)))

    def test_crop_rejects_shifted_bins(self):
        truth, _ = self.fixtures(EDGES+.01)
        with self.assertRaises(ValueError):
            crop(truth['axes']['eta'])

    def test_ratio_is_conditional_not_combined_sem(self):
        actual = ratio({'mean': [4., 1.], 'variance': [.16, .04]},
                       {'mean': [2., 0.], 'variance': [99., 0.]})
        self.assertEqual(actual['mean'], [2., None])
        self.assertEqual(actual['variance'], [.04, None])
        self.assertEqual(actual['valid'], [True, False])

    def test_additive_closure_and_unresolved_classification_rejected(self):
        truth, acts = self.fixtures()
        result = assemble(truth, acts, truth, acts)
        self.assertEqual(result['baselines']['old']['selected_geant4_rays'], 800)
        self.assertEqual(result['summary']['X0']['total']['fractional_reduction'], 0.)
        broken = copy.deepcopy(truth)
        broken['axes']['eta']['quantities']['X0']['total']['mean'][0] += 1
        with self.assertRaises(AssertionError):
            assemble(broken, acts, truth, acts)
        truth['classification']['density_mismatches'] = 1
        with self.assertRaises(ValueError):
            assemble(truth, acts, truth, acts)

    def test_palette_matches_repository_and_alpha_contract(self):
        readme = Path(__file__).resolve().parents[3]/'README.md'
        content = readme.read_text().lower()
        for color in COLORS.values():
            self.assertIn(color, content)
        truth, acts = self.fixtures()
        result = assemble(truth, acts, truth, acts)
        self.assertEqual(result['passive_alpha'], .5)
        self.assertEqual(result['sensitive_alpha'], 1.)


if __name__ == '__main__':
    unittest.main()
