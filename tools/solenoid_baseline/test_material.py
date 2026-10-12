"""Independent ray geometry and finite assembly material controls; fixtures only."""
import json
import math
from pathlib import Path
import unittest
from material import ROOT,enclosure,material_budget,part,ray_length,solids

class MaterialTests(unittest.TestCase):
    def test_fully_crossed_cylinder_analytic_path(self):
        p=part('fixture','cold_mass',1.,1.1,-10.,10.,.1)
        for eta in (-1.,0.,1.):
            self.assertAlmostEqual(ray_length(eta,p),.1*math.cosh(eta),places=12)

    def test_endcap_analytic_path(self):
        p=part('fixture','vessel',.1,5.,2.,2.05,.1)
        self.assertAlmostEqual(ray_length(1.,p),.05/math.tanh(1.),places=12)
        self.assertEqual(ray_length(0.,p),0)
        self.assertEqual(ray_length(-1.,p),0)

    def test_finite_edge_clipping_and_miss(self):
        p=part('fixture','cold_mass',1.,1.2,-2.,2.,.1)
        eta=math.asinh(2/1.1)
        expected=2/math.tanh(eta)-math.cosh(eta)
        self.assertAlmostEqual(ray_length(eta,p),expected,places=12)
        self.assertEqual(ray_length(3.,p),0)
        self.assertAlmostEqual(ray_length(0.,p,1.05),.05)

    def test_enclosure_corner_not_double_counted(self):
        parts=enclosure('fixture','vessel',1.,2.,3.,.1,.2,.1)
        # Ray enters inner wall then exits an annular cap; compare to outer minus
        # empty inner enclosure, independently as two ray intervals.
        eta=1.6
        total=sum(ray_length(eta,p) for p in parts)
        outer=part('whole','vessel',1.,2.,-3.,3.,.1)
        empty=part('void','vessel',1.1,1.9,-2.8,2.8,.1)
        self.assertAlmostEqual(total,ray_length(eta,outer)-ray_length(eta,empty),places=12)

    def test_real_scenarios_fit_symmetry_and_order(self):
        a=json.loads((ROOT/'tools/solenoid_baseline/material-assumptions.json').read_text())
        r=json.loads((ROOT/'docs/validation/DES-026/sizing.json').read_text())['result']
        scenarios=[solids(r,a,s) for s in a['scenarios']]
        for eta in (0.,.8,1.60,1.67,1.71,1.8,1.85,2.,4.):
            values=[material_budget(eta,p,r)['total'] for p in scenarios]
            self.assertLessEqual(values[0],values[1]+1e-12);self.assertLessEqual(values[1],values[2]+1e-12)
            self.assertAlmostEqual(values[1],material_budget(-eta,scenarios[1],r)['total'],places=12)
        self.assertEqual(material_budget(4.,scenarios[1],r)['total'],0)
        cold=(r['cold_outer_radius_m']-r['cold_inner_radius_m'])*a['atlas_cold_t_over_X0']/a['atlas_cold_thickness_m']
        ref=a['scenarios'][1]
        expected=cold+(2*ref['vessel_barrel_wall_m']+2*ref['shield_wall_m'])/a['aluminum_X0_m']
        self.assertAlmostEqual(material_budget(0.,scenarios[1],r)['total'],expected,places=12)

    def test_invalid_input_and_overlap(self):
        p=part('fixture','cold_mass',1.,1.1,-1.,1.,.1)
        for eta in (float('nan'),float('inf'),11.):
            with self.assertRaises(ValueError):ray_length(eta,p)
        with self.assertRaises(ValueError):enclosure('bad','vessel',1.,1.1,1.,.1,.1,.1)
        with self.assertRaises(ValueError):ray_length(0.,p,float('nan'))
        a=json.loads((ROOT/'tools/solenoid_baseline/material-assumptions.json').read_text())
        r=json.loads((ROOT/'docs/validation/DES-026/sizing.json').read_text())['result']
        with self.assertRaisesRegex(ValueError,'overlapping'):
            solids(r,dict(a,shield_inner_radius_m=1.35),a['scenarios'][1])
        with self.assertRaises(ValueError):
            solids(r,a,dict(a['scenarios'][1],cold_material_multiplier=float('nan')))

if __name__=='__main__':unittest.main()
