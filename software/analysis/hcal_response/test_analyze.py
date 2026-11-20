"""Independent statistics/invalid-input checks for the published observable."""
import math
import statistics
import unittest

from analyze import categories, moments


class RawResponseContracts(unittest.TestCase):
    def test_nonfinite_directions_fail(self):
        for eta,phi in ((math.nan,0.),(0.,math.nan),(math.inf,0.),(0.,-math.inf)):
            with self.subTest(eta=eta,phi=phi), self.assertRaises(ValueError):
                categories([dict(eta=eta,phi=phi)])

    def test_out_of_range_azimuth_fails(self):
        for phi in (-math.pi-1e-6,math.pi,math.pi+1e-6):
            with self.subTest(phi=phi), self.assertRaises(ValueError):
                categories([dict(eta=0.,phi=phi)])
        self.assertEqual(len(categories([dict(eta=0.,phi=-math.pi)])["phi"]),1)

    def test_zero_response_events_remain_and_width_is_undefined(self):
        result = moments([0.,0.,0.])
        self.assertEqual((result["events"],result["zero_events"]),(3,3))
        self.assertEqual(result["mean_response"],0.)
        self.assertEqual(result["sample_sd"],0.)
        self.assertIsNone(result["fractional_width"])

    def test_sample_width_matches_independent_statistics(self):
        data = [0.,.013,.025,.018,.021,.032]
        result = moments(data)
        self.assertAlmostEqual(result["sample_sd"],statistics.stdev(data),places=15)
        self.assertAlmostEqual(result["fractional_width"],statistics.stdev(data)/statistics.mean(data),places=15)
        self.assertEqual(result["zero_events"],1)


if __name__ == '__main__': unittest.main()
