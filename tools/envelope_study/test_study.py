"""Analytic fixtures only; these test dimensions are not detector parameters."""
import math
import unittest
import study

class EnvelopeStudyTests(unittest.TestCase):
    def setUp(self):
        self.barrel = dict(id='test_barrel', r_min_m=1., r_max_m=2., z_min_m=0., z_max_m=3., classification='NODD DESIGN CHOICE', rationale='test fixture only')
        self.endcap = dict(id='test_endcap', r_min_m=.5, r_max_m=2., z_min_m=4., z_max_m=5., classification='NODD DESIGN CHOICE', rationale='test fixture only')

    def test_transverse_ray_misses_endcap(self):
        self.assertEqual(study.ray_interval(self.barrel, 0), (1.,2.))
        self.assertIsNone(study.ray_interval(self.endcap, 0))

    def test_diagonal_and_mirror(self):
        eta = math.asinh(1.)
        lo, hi = study.ray_interval(self.barrel, eta)
        self.assertAlmostEqual(lo, math.sqrt(2.))
        self.assertAlmostEqual(hi, 2*math.sqrt(2.))
        self.assertEqual(study.ray_interval(self.barrel,-eta), (lo,hi))

    def test_forward_hole(self):
        self.assertIsNone(study.ray_interval(self.endcap, 4.))

    def test_tangent_zero_path(self):
        r = dict(self.barrel, z_min_m=2.,z_max_m=3.)
        self.assertIsNone(study.ray_interval(r, math.asinh(1.)))

    def test_positive_overlap_not_boundary_contact(self):
        b=dict(self.barrel,id='test_touching',r_min_m=2.,r_max_m=3.)
        d={'proposal':'test', 'regions':[self.barrel,b], 'study':{'eta_samples':[0]}}
        self.assertEqual(study.report(d)['rectangle_overlaps'],[])
        b['r_min_m']=1.5
        self.assertEqual(len(study.report(d)['rectangle_overlaps']),1)

    def test_reject_bad_units_and_unexplained_dimensions(self):
        d={'units':'mm','regions':[self.barrel], 'reflection_symmetry':'z -> -z', 'study':{'eta_samples':[0]}}
        with self.assertRaises(ValueError): study.validate(d)
        d['units']='m';d['regions'][0]['r_max_m']=float('nan')
        with self.assertRaises(ValueError): study.validate(d)

    def test_reject_nonfinite_eta_and_boolean_coordinates(self):
        d={'units':'m','reflection_symmetry':'z -> -z','regions':[self.barrel], 'study':{'eta_samples':[float('nan')]}}
        with self.assertRaises(ValueError): study.validate(d)
        d['study']['eta_samples']=[0];d['regions'][0]['r_min_m']=False
        with self.assertRaises(ValueError): study.validate(d)

    def test_extreme_eta_no_overflow(self):
        self.assertIsNone(study.ray_interval(self.barrel, 1000.))

if __name__ == '__main__': unittest.main()
