"""Directional selection controls independent of calorimeter response values."""
import unittest

import numpy as np

from raw_angular import coordinates


class SectorSelection(unittest.TestCase):
    def test_periodic_copies_share_bins_and_eta_keeps_full_population(self):
        # Explicit angles: central window is ±3.375 degrees for a 22.5° sector.
        phi = np.radians([0, 22.5, -22.5, 3, -3, 4, -4, 11.25])
        primaries = np.column_stack([np.ones(len(phi)), np.zeros(len(phi)), phi])
        edges, categories, metadata = coordinates(primaries, 15)
        np.testing.assert_equal(categories['phi'][:3], [7, 7, 7])
        self.assertTrue(np.all(categories['phi'][3:5] >= 0))
        np.testing.assert_equal(categories['phi'][5:], [-1, -1, -1])
        self.assertTrue(np.all(categories['eta'] >= 0))
        self.assertEqual((edges['phi'][0], edges['phi'][-1]), (-15, 15))
        self.assertAlmostEqual(metadata['half_width_deg'], 3.375)

    def test_invalid_sector_windows_fail(self):
        primaries = np.array([[1., 0., 0.]])
        for half in (0, -15, 51, float('nan')):
            with self.assertRaises(ValueError):
                coordinates(primaries, half)


if __name__ == '__main__':
    unittest.main()
