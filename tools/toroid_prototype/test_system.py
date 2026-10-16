"""Independent observable controls for DES-039 (pure math; no ACTS runtime)."""
import math
import unittest
import numpy as np
from .system import (load_design,normalize_currents,toroid_sources,response_points,
                     signed_response,solenoid_sources,solenoid_parameters,ray)
from .field import evaluate

class SystemTests(unittest.TestCase):
    def test_uniform_field_unequal_station_interpolation(self):
        c=load_design()
        for eta in [0.,1.10,1.14,2.]:
            _,w,_,s=response_points(eta,15,c)
            self.assertAlmostEqual(sum(w),(s[1]-s[0])*(s[2]-s[1])/2,places=11)
            # Integrated angular Brownian noise: sigma_MS=theta0*a*b/(sqrt(3)*L).
            a,b=s[1]-s[0],s[2]-s[1]
            self.assertGreater(a*b,0)

    def test_current_normalization(self):
        c=load_design();n=normalize_currents(c);src=toroid_sources(c)
        for t in c['field_target'].values():
            got=signed_response(t['eta'],t['phi_deg'],c,src)['B_sag_T']
            self.assertAlmostEqual(got,t['sagitta_equivalent_B_T'],places=10)
        self.assertTrue(all(x>0 for x in n['currents_Aturn'].values()))

    def test_solenoid_analytic_axis(self):
        src,factor=solenoid_sources();c=solenoid_parameters()
        a,b,h=c['cold_inner_radius_m'],c['winding_outer_radius_m'],c['cold_mass_length_m']/2
        def end(u):return 0 if u==0 else u*(math.asinh(b/abs(u))-math.asinh(a/abs(u)))
        def axis(z):return end(z+h)-end(z-h)
        zz=np.array([0.,1.,3.,3.6,5.,8.,12.]);exact=3*np.array([axis(z) for z in zz])/axis(0)
        got=evaluate(np.column_stack((0*zz,0*zz,zz)),src)
        np.testing.assert_allclose(got[:,2],exact,rtol=2e-4,atol=2e-6)
        np.testing.assert_allclose(got[:,:2],0,atol=1e-12)
        self.assertLess(abs(factor-1),1e-4)

    def test_current_outside_ampere_circuit(self):
        c=load_design();normalize_currents(c);src=toroid_sources(c)
        ph=np.linspace(0,2*math.pi,360,endpoint=False)
        r=6.2;p=np.column_stack((r*np.cos(ph),r*np.sin(ph),0*ph))
        b=evaluate(p,src);bphi=-b[:,0]*np.sin(ph)+b[:,1]*np.cos(ph)
        expected=4e-7*math.pi*12*c['coil_groups']['barrel']['ampere_turns_per_coil']
        self.assertAlmostEqual(2*math.pi*r*bphi.mean()/expected,1.,places=4)

if __name__=='__main__':unittest.main()
