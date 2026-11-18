import copy
import math
import unittest

from compact_prototype import configs, RESTORED_SPEC
from barrel_geometry import ROOT
import json
from services import budget


class CompactTests(unittest.TestCase):
    def test_restored_sampling_boundaries_and_service_clearance(self):
        spec, barrel, endcap, service = configs(RESTORED_SPEC)
        self.assertEqual((barrel['lead_mm'], barrel['planes']), (1.8, 1248))
        self.assertEqual((barrel['sampling_inner_radius_mm'], barrel['sampling_outer_radius_mm']), (1772.8, 2350))
        self.assertEqual(barrel['inclination_deg'], 50.18)
        original=json.loads((ROOT/'tools/lar_calorimeter/barrel.json').read_text())
        def fractions(c):
            r0,r1=c['sampling_inner_radius_mm'],c['sampling_outer_radius_mm']
            angle=math.radians(c['inclination_deg']);t=0.;result=[0.]
            for length in c['segments_mm']:
                t+=length
                r=math.hypot(r0+t*math.cos(angle),t*math.sin(angle))
                result.append((r-r0)/(r1-r0))
            result[-1]=1.
            return result
        for a,b in zip(fractions(original),fractions(barrel)):
            self.assertAlmostEqual(a,b,places=12)
        corner=math.hypot(2350+105+35,360+75/2)
        self.assertGreater(service['nitrogen_pipe_radius_mm']-10-corner,15)
        self.assertAlmostEqual(2350+210+30+49+2.7,2641.7)
        self.assertEqual(endcap['sampling_depth_mm'],650)
        self.assertLess(budget(service)['bends']['100']['axial_s_bend_envelope_mm'],855)

    def test_reserved_clearance_and_sampling_similarity(self):
        spec, barrel, endcap, service = configs()
        self.assertEqual(barrel['warm_inner_radius_mm']-1640, 60)
        self.assertAlmostEqual(barrel['sampling_inner_radius_mm'], 1772.8)
        self.assertAlmostEqual(barrel['sampling_outer_radius_mm']/barrel['sampling_inner_radius_mm'],2578.3/2172.8)
        self.assertEqual(barrel['inclination_deg'],50.18)
        self.assertEqual(endcap['sampling_depth_mm'],650)
        self.assertEqual(endcap['cold_back_z_mm']-(endcap['sampling_front_z_mm']+endcap['sampling_depth_mm']),250)
        self.assertEqual(endcap['warm_front_z_mm']-barrel['warm_half_z_mm'],1000)
        # Independent worst flat-board corner and pipe annulus clearance.
        back=barrel['sampling_outer_radius_mm']
        corner=math.hypot(back+105+35,360+75/2)
        self.assertGreater(service['nitrogen_pipe_radius_mm']-10-corner,12)
        self.assertGreater(back+barrel['rear_bath_mm']-service['nitrogen_pipe_radius_mm']-10,2.9)

    def test_service_bends_fail_without_explicit_radius(self):
        _,_,_,service=configs()
        result=budget(service)
        self.assertLess(result['bends']['100']['axial_s_bend_envelope_mm'],1000)
        bad=copy.deepcopy(service);bad.pop('actual_bend_radii_mm')
        with self.assertRaisesRegex(ValueError,'outside chosen bend'):budget(bad)
        bad=copy.deepcopy(service);bad['actual_bend_radii_mm']['100']=399
        with self.assertRaisesRegex(ValueError,'below minimum'):budget(bad)


if __name__=='__main__':unittest.main()
