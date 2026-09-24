"""Independent limits, symmetries and fail-closed policy checks."""
import copy
import json
import math
import unittest
import numpy as np
from sizing import MU0, POLICY, ROOT, check_field, stored_energy, solve, validate_sized_winding


class SizingTests(unittest.TestCase):
    def test_field_hard_limit_and_polarity(self):
        for b in (0,1,4,5,-5):check_field(b)
        for b in (5.000001,-5.000001,float('nan'),float('inf')):
            with self.assertRaises(ValueError):check_field(b)
        self.assertAlmostEqual(stored_energy(1,1.1,4,-3),stored_energy(1,1.1,4,3))

    def test_energy_field_squared_and_geometric_scale(self):
        e=stored_energy(1,1.1,4,2)
        self.assertAlmostEqual(stored_energy(1,1.1,4,4)/e,4,places=10)
        self.assertAlmostEqual(stored_energy(2,2.2,8,2)/e,8,places=10)

    def test_independent_infinite_length_field_energy(self):
        # Infinite thick solenoid: B=mu0*J*t in bore, mu0*J*(b-r) in pack.
        # Compare U/L to exact radial B^2 volume integral as end effects vanish.
        a,b,length,b0=1.,1.2,20000.,2.
        j=b0/(MU0*(b-a))
        primitive=lambda r:b*b*r*r/2-2*b*r**3/3+r**4/4
        expected=math.pi*MU0*j*j*(a*a*(b-a)**2/2+primitive(b)-primitive(a))
        self.assertLess(abs(stored_energy(a,b,length,b0)/length/expected-1),2e-4)

    def test_analytic_axial_kernel_against_direct_integral(self):
        # Integrate separation before angular/radial integration, away from singularity.
        x,w=np.polynomial.legendre.leggauss(200)
        length,d=3.7,.28;s=(x+1)*length/2
        direct=np.sum(w*length/2*(length-s)/np.sqrt(d*d+s*s))
        analytic=length*math.asinh(length/d)-math.hypot(length,d)+d
        self.assertAlmostEqual(direct,analytic,places=11)

    def test_refinement_and_energy_volume_closure(self):
        for family in POLICY['families']:
            s=solve(family)
            self.assertLess(s['energy_density_relative_residual'],1e-8)
            e=stored_energy(s['cold_inner_radius_m'],s['winding_outer_radius_m'],s['cold_mass_length_m'],3,96,384)
            self.assertLess(abs(e/s['stored_energy_J']-1),5e-4)

    def test_current_inputs_and_tampered_geometry(self):
        for w in json.loads((ROOT/'tools/magnetic_study/windings.json').read_text())['windings']:
            validate_sized_winding(w)
            for key in ('cold_inner_radius_m','cold_outer_radius_m','vessel_outer_radius_m','vessel_length_m'):
                bad=copy.deepcopy(w);bad['sizing'][key]+=.1
                with self.assertRaises(ValueError):validate_sized_winding(bad)
            bad=copy.deepcopy(w);bad['central_field_T']=5.1
            with self.assertRaises(ValueError):validate_sized_winding(bad)


if __name__=='__main__':unittest.main()
