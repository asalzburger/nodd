import copy
import math
import unittest

from compact_prototype import configs
from services import budget


class CompactTests(unittest.TestCase):
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
