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

    def test_full_axial_depth_including_outer_back_corner(self):
        result = study.axial_depth(self.endcap, math.asinh(5./2.))
        self.assertTrue(result['full_axial_depth'])
        self.assertAlmostEqual(result['axial_fraction'], 1.)
        # Exact front inner corner also spans the axial allocation, but has no margin.
        self.assertTrue(study.axial_depth(self.endcap, math.asinh(4./.5))['full_axial_depth'])

    def test_partial_depth_is_not_full_and_forward_hole_is_miss(self):
        partial = study.axial_depth(self.endcap, math.asinh(4.5/2.))
        self.assertFalse(partial['full_axial_depth'])
        self.assertAlmostEqual(partial['axial_fraction'], .5)
        missed = study.axial_depth(self.endcap, 10.)
        self.assertEqual(missed['traversal'], 'miss')
        self.assertEqual(missed['axial_fraction'], 0.)

    def test_full_depth_threshold_both_sides(self):
        edge = math.asinh(4./.5)
        self.assertTrue(study.axial_depth(self.endcap, edge-1e-6)['full_axial_depth'])
        self.assertFalse(study.axial_depth(self.endcap, edge+1e-6)['full_axial_depth'])
        self.assertEqual(study.axial_depth(self.endcap, -edge), study.axial_depth(self.endcap, edge))

if __name__ == '__main__': unittest.main()
