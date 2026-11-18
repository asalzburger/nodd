"""Guard conditional side egress without weakening the original bend checks."""
import copy
from pathlib import Path
import unittest
from compact_prototype import configs, RESTORED_SPEC
from services import budget

SPEC=Path(__file__).with_name('gap400-prototype.json')


class Gap400Tests(unittest.TestCase):
    def test_sampling_preserved_and_complete_endcap_translated(self):
        _,before_b,before_e,_=configs(RESTORED_SPEC)
        _,after_b,after_e,c= configs(SPEC)
        self.assertEqual(before_b,after_b)
        shifted={'sampling_front_z_mm','warm_front_z_mm','cold_front_z_mm','warm_back_z_mm','cold_back_z_mm'}
        self.assertEqual(set(before_e),set(after_e))
        for key in before_e:
            self.assertEqual(after_e[key],before_e[key]-600 if key in shifted else before_e[key],key)
        self.assertEqual((after_e['warm_front_z_mm'],after_e['warm_back_z_mm']),(4500,5660))
        self.assertEqual((c['hcal_barrel_half_z_mm'],c['hcal_endcap_front_z_mm']),(6260,6760))

    def test_400mm_without_explicit_route_policy_still_fails(self):
        _,_,_,c=configs(RESTORED_SPEC);c['front_service_gap_mm']=400
        with self.assertRaisesRegex(ValueError,'minimum bend allocation'):budget(c)

    def test_conditional_reservation_has_margins_but_constructs_no_route(self):
        _,_,_,c=configs(SPEC);r=budget(c);v=r['external_route_reservation']
        self.assertFalse(v['external_route_constructed'])
        self.assertEqual(v['endcap_to_hcal_axial_interval_mm'],1100)
        self.assertEqual(v['radial_exit_window_abs_z_mm'],[6260,6760])
        self.assertLess(max(v['mixed_utility_station_area_mm2'].values()),v['lanes']['utility']['area_mm2'])
        for bend in r['bends'].values():
            self.assertLess(bend['side_neck_required_axial_mm'],1000)
            self.assertLess(bend['rear_two_face_bound_mm'],500)

    def test_insufficient_neck_lane_or_coincident_utilities_fail(self):
        _,_,_,original=configs(SPEC)
        for key,value in [('side_neck_band_abs_z_mm',[3500,4000]),('utility_lane_mm',[1100,150]),('endcap_utility_sector',0),('actual_bend_radii_mm',{'80':400,'100':399})]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                c=copy.deepcopy(original);c[key]=value;budget(c)


if __name__=='__main__':unittest.main()
