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

    def test_padding_keeps_every_event_once_in_the_same_full_sector_bins(self):
        phi = np.radians([-180, -14, -11.25, -7, 0, 7, 11.25, 14, 180])
        primaries = np.column_stack([np.ones(len(phi)), np.zeros(len(phi)), phi])
        edges, categories, metadata = coordinates(primaries, sector_padding_percent=15)
        plain_edges, plain_categories, _ = coordinates(primaries, 50)
        np.testing.assert_equal(edges['phi'], plain_edges['phi'])
        np.testing.assert_equal(categories['phi'], plain_categories['phi'])
        self.assertTrue(np.all(categories['phi'] >= 0))
        self.assertEqual(len(categories['phi']), len(phi))
        self.assertEqual(metadata['display_range_percent'], [-65, 65])
        self.assertEqual((edges['phi'][0], edges['phi'][-1]), (-50, 50))
        for padding in (-1, 51, float('nan')):
            with self.assertRaises(ValueError):
                coordinates(primaries, sector_padding_percent=padding)
        with self.assertRaises(ValueError):
            coordinates(primaries, 15, 15)


if __name__ == '__main__':
    unittest.main()
