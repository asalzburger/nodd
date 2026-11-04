"""Independent finite-ray and distance controls for the survey geometry."""
import unittest
import numpy as np
from survey import ray_crossings, choose_carriers, segment_distance, nearest_indices, pixel_after_rule


class SurveyControls(unittest.TestCase):
    def setUp(self):
        self.portals=[{'rz_segment_mm':[[10,-20],[10,20]]},
                      {'rz_segment_mm':[[0,30],[12,30]]},
                      {'rz_segment_mm':[[0,15],[20,15]]}]

    def test_pixel_orientation_and_strict_majority(self):
        self.assertTrue(pixel_after_rule(True,10,6))
        self.assertFalse(pixel_after_rule(False,10,9))
        self.assertFalse(pixel_after_rule(True,10,5))
        self.assertFalse(pixel_after_rule(True,0,0))

    def test_finite_bounds_exclude_infinite_disc_intersection(self):
        t,i=ray_crossings(np.array([.6,0,.8]),self.portals)
        np.testing.assert_array_equal(i,[0,2])
        np.testing.assert_allclose(t,[10/.6,15/.8])

    def test_flight_before_after_and_missing_candidate(self):
        target,distance=choose_carriers(np.array([3.,15.,31.]),np.array([False,True,True]),np.array([10.,20.]),np.array([5,7]))
        np.testing.assert_array_equal(target,[-1,7,-1]);self.assertEqual(distance[1],5)

    def test_coincident_counts_on_both_sides(self):
        target,_=choose_carriers(np.array([10.,10.]),np.array([False,True]),np.array([10.]),np.array([5]))
        np.testing.assert_array_equal(target,[5,5])

    def test_finite_segment_endpoint_distance(self):
        d=segment_distance(np.array([13.,13.]),np.array([0.,24.]),self.portals[0])
        np.testing.assert_allclose(d,[3,5])

    def test_nearest_sensitive_crossing_not_next_hit_only(self):
        np.testing.assert_array_equal(nearest_indices(np.array([10.,20.]),np.array([9.,14.,16.,23.])),[0,0,1,1])


if __name__=='__main__':unittest.main()
