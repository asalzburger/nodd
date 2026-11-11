"""Controls for broad-spectrum response widths and sector/edge binning."""
import math
import unittest
import numpy as np
from angular_analyze import ETA_EDGES, PHI_EDGES, PERIOD, bin_index, folded_phi, fractional_width


class AngularResponseTests(unittest.TestCase):
    def test_beam_energy_spread_is_removed(self):
        energy=np.array([10.,20.,40.,80.]);signal=.02*energy
        self.assertGreater(fractional_width(signal),.8)
        self.assertAlmostEqual(fractional_width(signal/energy),0.,places=14)

    def test_no_hit_event_remains_a_physical_zero(self):
        self.assertAlmostEqual(fractional_width([0,.02,.02,.02]),2/3)
        self.assertIsNone(fractional_width([0,0]))

    def test_sector_centre_and_seam_phase(self):
        np.testing.assert_allclose(folded_phi(np.arange(16)*PERIOD),0,atol=1e-14)
        self.assertAlmostEqual(float(folded_phi(PERIOD/2)),-PERIOD/2)
        self.assertEqual(int(bin_index([0],PHI_EDGES)[0]),5)

    def test_signed_phase_is_preserved(self):
        self.assertAlmostEqual(float(folded_phi(-.1)),-.1)
        self.assertAlmostEqual(float(folded_phi(.1)),.1)

    def test_last_eta_boundary_is_included(self):
        np.testing.assert_array_equal(bin_index([0,.3,3],ETA_EDGES),[0,1,9])


if __name__=="__main__":unittest.main()
