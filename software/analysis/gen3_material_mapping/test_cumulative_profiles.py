"""Analytic controls for continuous and thin-surface cumulative material."""
import unittest
import numpy as np
from cumulative_profiles import cumulative_at, finalize, slice_indices


class CumulativeControls(unittest.TestCase):
    def test_partial_overlapping_and_zero_projection_steps(self):
        grid = np.array([0., 1., 2., 3., 4.])
        actual = cumulative_at(grid, [0, 0, 1], [1, 2, 2], [3, 4, 2], [4, 2, 3], 3, True)
        np.testing.assert_allclose(actual, [[0, 0, 2, 5, 6], [0, 0, 3, 3, 3], [0, 0, 0, 0, 0]])

    def test_thin_interaction_is_inclusive_and_not_spread_by_slab_length(self):
        actual = cumulative_at([0, 1, 2, 3], [0, 0], [1, 2.5], [1, 2.5], [2, 4], 1, False)
        np.testing.assert_array_equal(actual, [[0, 2, 2, 6]])

    def test_every_zero_ray_contributes_to_mean_and_correlated_prefix_sem(self):
        curves = cumulative_at([0, 1, 2], [0, 0], [.5, 1.5], [.5, 1.5], [1, 2], 3, False)
        p = finalize(3, curves.sum(axis=0), (curves * curves).sum(axis=0))
        np.testing.assert_allclose(p['mean'], [0, 1 / 3, 1])
        np.testing.assert_allclose(p['variance'], [0, 2 / 27, 2 / 3])

    def test_eta_slice_boundaries_and_folded_negative_rays(self):
        np.testing.assert_array_equal(slice_indices(np.array([0, -.49, .5, -.99, 1]), [0, .5, 1]), [0, 0, 1, 1, 1])
        with self.assertRaises(ValueError):
            slice_indices([1.1], [0, 1])

    def test_invalid_or_truncated_grid_fails_instead_of_losing_budget(self):
        for start, end, weight in [([1], [4], [2]), ([2], [1], [2]), ([1], [2], [-1])]:
            with self.assertRaises(ValueError):
                cumulative_at([0, 1, 2, 3], [0], start, end, weight, 1, True)

    def test_empty_ray_collection_and_empty_slice(self):
        self.assertEqual(cumulative_at([0, 1], [], [], [], [], 0, True).shape, (0, 2))
        with self.assertRaises(ValueError):
            finalize(0, np.zeros(2), np.zeros(2))

    def test_difference_arrays_match_direct_segment_integrals_for_unsorted_steps(self):
        rng = np.random.default_rng(100)
        owner = rng.integers(0, 4, 80)
        start = rng.uniform(0, 7, 80)
        end = start + rng.uniform(.001, 2, 80)
        weights = rng.uniform(0, 3, 80)
        grid = np.linspace(0, 10, 41)
        for distributed in (False, True):
            expected = np.zeros((5, len(grid)))
            for ray, a, b, w in zip(owner, start, end, weights):
                fraction = np.clip((grid - a) / (b - a), 0, 1) if distributed else (grid >= a)
                expected[ray] += w * fraction
            np.testing.assert_allclose(cumulative_at(grid, owner, start, end, weights, 5, distributed),
                                       expected, rtol=1.e-12, atol=1.e-11)


if __name__ == '__main__':
    unittest.main()
