"""Meaningful profile normalization/covariance and finite-volume controls."""
import unittest
import numpy as np

from reduce import profile
from check_boxes import intersections


class HitProfiles(unittest.TestCase):
    def test_zeros_and_correlated_components(self):
        # Two bins, four rays each; components perfectly correlated in the first.
        eta=np.array([-.8]*4+[.8]*4)
        values=np.array([[0,0,0,0],[1,1,0,2],[2,2,0,4],[3,3,0,6],
                         [0,0,0,0],[2,0,0,2],[0,2,0,2],[0,0,2,2]])
        p=profile(eta,values,np.array([-1,0,1]))
        self.assertEqual(p['counts'],[4,4])
        self.assertEqual(p['quantities']['total']['mean'],[3,1.5])
        self.assertEqual(p['quantities']['pixel']['zero_count_rays'],[1,3])
        self.assertAlmostEqual(p['quantities']['total']['variance'][0],1.25)
        self.assertGreater(p['quantities']['total']['variance'][0],
                           sum(p['quantities'][q]['variance'][0] for q in ('pixel','short_strip','long_strip')))

    def test_incomplete_or_noninteger_samples_rejected(self):
        with self.assertRaises(ValueError):profile([1,1],np.zeros((2,4)),np.array([-1,0,1]))
        with self.assertRaises(ValueError):profile([-.5,-.5],np.ones((2,4))*.5,np.array([-1,0]))
        with self.assertRaises(AssertionError):profile([-.5,-.5],np.ones((2,4)),np.array([-1,0]))

    def test_two_placements_same_sensor_shape_and_edge_graze(self):
        # Same shape/orientation, two placed copies. Both must count separately.
        centers=np.array([[0,0,2.],[0,0,4.]])
        axes=np.tile(np.eye(3),(2,1,1));half=np.tile([1.,1.,.1],(2,1))
        np.testing.assert_array_equal(intersections(centers,axes,half,np.array([0.,0.,1.])),[True,True])
        # This ray enters the side after midplane, with a finite positive chord.
        center=np.array([[1.102,0.,2.]])
        self.assertTrue(intersections(center,axes[:1],half[:1],np.array([.05,0.,1.]))[0])
        self.assertGreater(abs(.05*2-center[0,0]),half[0,0])


if __name__=='__main__':unittest.main()
