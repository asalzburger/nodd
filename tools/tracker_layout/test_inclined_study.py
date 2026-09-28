"""Analytic fixture checks for unsigned inclined row envelopes and face accounting."""
import copy
import json
import math
from pathlib import Path
import unittest

from inclined_study import (candidate_c, ring_intersection, summarize, crossings,
                            validate_ring, area_ledger)


class InclinedControls(unittest.TestCase):
    def setUp(self):
        n=math.sqrt(.5)
        self.ring=dict(id='fixture',kind='inclined_ring',subsystem='long_strip',
            r0_m=1.,z0_m=1.,r1_m=1.2,z1_m=.8,r2_m=.8,z2_m=1.2,
            normal_r=n,normal_z=n,x0_percent=2.,sigma_rphi_m=1e-5,sigma_second_m=1e-3)

    def test_origin_normal_incidence_and_area(self):
        h=ring_intersection(self.ring,math.asinh(1),0,10,0)
        for a,b in zip(h,(1,1,math.sqrt(2),2)): self.assertAlmostEqual(a,b)
        area=area_ledger({'layers':[self.ring]})
        expected=math.pi*2*math.hypot(.4,.4)
        self.assertAlmostEqual(area['reference_area_m2']['long_strip'],expected)
        self.assertAlmostEqual(area['silicon_face_area_m2']['long_strip'],2*expected)

    def test_straight_displaced_vertex_closed_form(self):
        eta,zv=.7,.15
        s=math.sinh(eta)
        expected_r=(2-zv)/(1+s)
        hit=ring_intersection(self.ring,eta,zv,10,0)
        self.assertAlmostEqual(hit[0],expected_r)
        self.assertAlmostEqual(hit[1],zv+s*expected_r)
        self.assertAlmostEqual(hit[3],2*math.cosh(eta)/(math.sqrt(.5)*(1+s)))

    def test_helix_plane_equation_mirror_and_field_sign(self):
        h=ring_intersection(self.ring,math.asinh(1),.1,1,3)
        self.assertAlmostEqual(h[0]+h[1],2,places=12)
        mirrored=dict(self.ring,normal_z=-self.ring['normal_z'],z0_m=-1,z1_m=-.8,z2_m=-1.2)
        other=ring_intersection(mirrored,-math.asinh(1),-.1,1,-3)
        for i in (0,2,3): self.assertAlmostEqual(h[i],other[i])
        self.assertAlmostEqual(h[1],-other[1])

    def test_edges_misses_and_material_for_two_faces(self):
        self.assertIsNone(ring_intersection(self.ring,0,0,10,0))
        self.assertIsNone(ring_intersection(self.ring,4,0,10,0))
        for r,z in [(1.2,.8),(.8,1.2)]:
            self.assertAlmostEqual(ring_intersection(self.ring,math.asinh(z/r),0,10,0)[0],r)
        one=summarize([(self.ring,(1,1,1,2))])
        self.assertEqual(one['stations'],1)
        self.assertEqual(one['long_strip_scalar_faces'],2)
        self.assertEqual(one['local_material_percent'],2)
        other=dict(self.ring,id='fixture-2',station_group='fixture')
        two=summarize([(self.ring,(1,1,1,2)),(other,(1,1,1,2))])
        self.assertEqual(two['stations'],1)
        self.assertEqual(two['module_crossings'],2)
        self.assertEqual(two['silicon_face_crossings'],4)
        self.assertEqual(two['physical_scalar_coordinates'],4)
        self.assertEqual(two['grouped_station_coordinates'],2)
        self.assertEqual(two['local_material_percent'],4)

    def test_invalid_ring_rejected(self):
        host=dict(r_min_m=.025,r_max_m=2,abs_z_max_m=3)
        validate_ring(self.ring,host)
        for change in ({'normal_r':2},{'r1_m':1.3},{'x0_percent':-1},{'r0_m':float('nan')}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_ring(dict(self.ring,**change),host)

    def test_c_retains_pixels_disks_and_double_sided_barrel_counts(self):
        root=Path(__file__).resolve().parents[2]
        base=json.loads((root/'docs/design/DES-006-layouts.json').read_text())
        config=json.loads((root/'docs/design/DES-006-inclined-layouts.json').read_text())
        a=base['candidates'][0]; c=candidate_c(a,config['recipe'])
        for l in c['layers']:
            if l['kind']=='inclined_ring': validate_ring(l,base['host'])
        unchanged=[l for l in c['layers'] if l['subsystem']=='pixel' or l['kind']=='disc']
        original=[l for l in a['layers'] if l['subsystem']=='pixel' or l['kind']=='disc']
        for x,y in zip(original,unchanged):
            clean=copy.deepcopy(y);clean.pop('station_group');clean['id']='A'+clean['id'][1:]
            self.assertEqual(x,clean)
        row=summarize(crossings(c,0,0,10,3))
        self.assertEqual((row['stations'],row['silicon_face_crossings'],row['long_strip_scalar_faces']),(10,12,4))


if __name__=='__main__': unittest.main()
