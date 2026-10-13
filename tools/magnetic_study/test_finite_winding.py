"""Independent physical identities and rejection tests for the vacuum prototype."""
import math
import unittest
import numpy as np
from finite_winding import FiniteWinding
from solenoid import MU0, Solenoid


class FiniteWindingTests(unittest.TestCase):
    def setUp(self):
        self.model = FiniteWinding(1.34,1.44,3.3)

    def test_independent_axis_integral_including_end_planes(self):
        self.assertAlmostEqual(self.model.axis(0),3.,places=12)
        for z in (0.,1.,3.15,3.3,-3.3,5.,10.):
            np.testing.assert_allclose(self.model.field(0,z),[0,self.model.axis(z)],atol=1e-10,rtol=0)

    def test_reflection_and_current_reversal(self):
        b=self.model.field(.7,2.)
        np.testing.assert_allclose(self.model.field(.7,-2.),b*[-1,1],atol=1e-12)
        np.testing.assert_allclose(FiniteWinding(1.34,1.44,3.3,-3).field(.7,2.),-b,atol=1e-12)

    def test_vacuum_maxwell(self):
        r,z,step=.7,1.8,1e-4
        b=self.model.field(r,z)
        dr=(self.model.field(r+step,z)-self.model.field(r-step,z))/(2*step)
        dz=(self.model.field(r,z+step)-self.model.field(r,z-step))/(2*step)
        self.assertLess(abs(dr[0]+b[0]/r+dz[1]),1e-7)
        self.assertLess(abs(dz[0]-dr[1]),1e-7)

    def test_thin_winding_limit(self):
        # Synthetic shrinking pack, fixed central field: recover the old sheet.
        thin=FiniteWinding(1.415-5e-5,1.415+5e-5,3.3)
        sheet=Solenoid(1.415,3.3)
        for r,z in ((0,0),(.7,2),(1.14,3.15),(3,4)):
            np.testing.assert_allclose(thin.field(r,z),sheet.field(r,z),rtol=1e-7,atol=1e-9)

    def test_far_field_dipole(self):
        # m = pi * integral(J r^2 dr dz), not NI*pi*(mean radius)^2.
        s=self.model; z=1000.
        moment=math.pi*s.j*2*s.h*(s.b**3-s.a**3)/3
        expected=MU0*moment/(2*math.pi*z**3)
        self.assertLess(abs(s.axis(z)/expected-1),3e-5)

    def test_refinement_for_both_controls(self):
        for a,b,h in ((1.34,1.44,3.3),(4.4,4.6,6.5)):
            nominal=FiniteWinding(a,b,h)
            fine=FiniteWinding(a,b,h,nr=16,nz=192,nphi=256)
            for r,z in ((1.14,3.15),(.5,1.),(3.,4.),(6.,8.)):
                reference=fine.field(r,z)
                self.assertLess(np.linalg.norm(nominal.field(r,z)-reference),1e-6+1e-5*np.linalg.norm(reference))

    def test_excluded_winding_and_invalid_inputs(self):
        for r,z in ((1.34,0),(1.39,0),(1.44,0),(1.44,3.3),(1.5,0),(-1,0),(0,float('nan'))):
            with self.assertRaises(ValueError): self.model.field(r,z)
        for a,b,h in ((0,1,1),(2,1,1),(1,1,1),(1,2,0),(1,float('inf'),1)):
            with self.assertRaises(ValueError): FiniteWinding(a,b,h)
        for params in ({'nr':0},{'nr':2.5},{'nz':True},{'nphi':3},{'guard':-1}):
            with self.assertRaises(ValueError): FiniteWinding(1,2,3,**params)


if __name__ == '__main__': unittest.main()
