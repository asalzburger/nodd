"""Independent physical limits and interface rejection controls; fixture values only."""
import json
import math
from pathlib import Path
import unittest
import numpy as np
from model import MU0, axis_field, gauss, pack_current, solve, stored_energy, validate_config

ROOT = Path(__file__).resolve().parents[2]

class ModelTests(unittest.TestCase):
    def test_axis_normalization_symmetry_and_reversal(self):
        for a,b,L in ((1.,1.1,7.), (2.,2.4,4.)):
            self.assertAlmostEqual(axis_field(0,a,b,L,3),3,places=12)
            self.assertAlmostEqual(axis_field(2,a,b,L,3),axis_field(-2,a,b,L,3),places=12)
            self.assertAlmostEqual(axis_field(1,a,b,L,-3),-axis_field(1,a,b,L,3),places=12)

    def test_energy_field_and_length_scaling(self):
        u=stored_energy(1,1.1,7,3,24,96)
        self.assertAlmostEqual(stored_energy(1,1.1,7,1.5,24,96)/u,.25,places=12)
        self.assertAlmostEqual(stored_energy(2,2.2,14,3,24,96)/u,8,places=11)
        self.assertAlmostEqual(stored_energy(1,1.1,7,-3,24,96)/u,1,places=12)

    def test_analytic_axial_integral(self):
        x,w=gauss(128)
        L,d=4.,.7
        t=(x+1)*L/2
        direct=float(np.sum(w*L/2*(L-t)/np.sqrt(t*t+d*d)))
        analytic=L*math.asinh(L/d)-math.hypot(L,d)+d
        self.assertAlmostEqual(direct,analytic,places=11)

    def test_infinite_solenoid_energy_limit(self):
        # Independent B(r)=B0 in bore, B0*(b-r)/(b-a) in annulus, zero outside.
        a,b,L,B=1.,1.1,2000.,3.
        x,w=gauss(96); r=(a+b)/2+(b-a)*x/2
        annulus=float(np.sum(w*(b-a)/2*r*((b-r)/(b-a))**2))
        infinite_per_length=math.pi*B*B/MU0*(a*a/2+annulus)
        self.assertLess(abs(stored_energy(a,b,L,B,96,384)/L/infinite_per_length-1),.006)

    def test_baseline_root_refinement_and_clearances(self):
        c=json.loads((ROOT/'tools/solenoid_baseline/baseline.json').read_text())
        t=json.loads((ROOT/'detector/config/tracker.json').read_text())
        validate_config(c,t); r=solve(c)
        self.assertLess(r['energy_density_relative_residual'],1e-8)
        self.assertLess(r['relative_refinement'],5e-4)
        self.assertAlmostEqual(r['proposed_ecal_inner_radius_m'],1.70)
        self.assertAlmostEqual(r['proposed_ecal_endcap_front_m'],3.95)
        self.assertGreater(r['assembly_spare_radial_m'],0)
        for changes in ({'central_field_T':5.1},{'central_field_max_T':6},
                        {'cold_mass_length_m':6.6},{'vessel_inner_radius_m':1.2},
                        {'winding_radial_fraction_of_cold_mass':1.1},
                        {'outer_gap_scale':float('nan')}):
            with self.assertRaises(ValueError):validate_config(dict(c,**changes),t)
        with self.assertRaises(ValueError):solve(dict(c,assembly_outer_radius_m=1.4))

    def test_invalid_winding_and_quadrature(self):
        for args in ((0,1,4,3),(1,1,4,3),(1,2,0,3),(1,2,4,5.01),(1,2,4,float('nan'))):
            with self.assertRaises(ValueError):pack_current(*args)
        for n in (True,1,2.1):
            with self.assertRaises(ValueError):stored_energy(1,1.1,7,3,n,96)

if __name__ == '__main__':unittest.main()
