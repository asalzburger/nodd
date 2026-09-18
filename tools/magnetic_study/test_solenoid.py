"""Independent identities for the isolated vacuum-field PROTOTYPE."""
import unittest
import numpy as np
from solenoid import Solenoid

class FieldTests(unittest.TestCase):
    def setUp(self): self.s=Solenoid(1.415,3.3)
    def test_axis_formula_and_normalization(self):
        self.assertAlmostEqual(float(self.s.axis(0)),3.,places=13)
        for z in [0,1,3.15,5,10]:
            br,bz=self.s.field(0,z)
            self.assertAlmostEqual(br,0,places=12)
            self.assertAlmostEqual(bz,float(self.s.axis(z)),places=11)
    def test_reflection_and_current_reversal(self):
        b=self.s.field(.7,2.)
        np.testing.assert_allclose(self.s.field(.7,-2.),b*[-1,1],atol=1e-12)
        np.testing.assert_allclose(Solenoid(1.415,3.3,-3).field(.7,2.),-b,atol=1e-12)
    def test_vacuum_maxwell(self):
        r,z,h=.7,1.8,1e-4
        b=self.s.field(r,z)
        dr=(self.s.field(r+h,z)-self.s.field(r-h,z))/(2*h)
        dz=(self.s.field(r,z+h)-self.s.field(r,z-h))/(2*h)
        self.assertLess(abs(dr[0]+b[0]/r+dz[1]),1e-7)
        self.assertLess(abs(dz[0]-dr[1]),1e-7)
    def test_quadrature_convergence(self):
        fine=Solenoid(1.415,3.3,3,192,256)
        for r,z in [(1.14,3.15),(.5,1.),(3.,4.),(6.,8.)]:
            reference=fine.field(r,z)
            self.assertLess(np.linalg.norm(self.s.field(r,z)-reference),
                            1e-6+1e-5*np.linalg.norm(reference))
    def test_far_field_dipole(self):
        # On axis the leading dipole term is mu0 NI R^2/(2 z^3).
        from solenoid import MU0
        z=1000.
        dipole=MU0*self.s.ni*self.s.radius**2/(2*z**3)
        self.assertLess(abs(float(self.s.axis(z))/dipole-1),3e-5)
    def test_guard_and_invalid_inputs(self):
        for r,z in [(1.415,0),(1.415,3.3),(-1,0),(0,float('nan'))]:
            with self.assertRaises(ValueError): self.s.field(r,z)
        with self.assertRaises(ValueError): Solenoid(0,1)

if __name__=='__main__': unittest.main()
