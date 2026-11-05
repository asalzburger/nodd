import copy
import json
import math
import unittest

from design import CONFIG, build, common_unit, core, determinant, encode, frame, ray, transform, validate, water_ports


class BarrelDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=build()

    def test_depth_amendment_and_polygon_corner(self):
        s=self.data['summary']
        self.assertAlmostEqual(s['total_depth_mm'],1558)
        self.assertAlmostEqual(s['depth_amendment_mm'],62.1)
        self.assertAlmostEqual(s['corner_radius_mm'],4158/math.cos(math.pi/16))
        self.assertGreater(s['ecal_egress_extra_clearance_mm'],15)

    def test_old_envelope_rejected(self):
        c=json.loads(CONFIG.read_text());c['proposed_outer_apothem_mm']=4095.9
        with self.assertRaisesRegex(ValueError,'depth/envelope'):
            build(c)

    def test_matched_column_counts_and_bounded_phases(self):
        for layer in self.data['layers']:
            self.assertEqual(layer['carrier_count_per_sector'],len(layer['columns_mm'])*33)
            self.assertLessEqual(abs(layer['tangent_phase_mm']),max(0,layer['centred_edge_margin_mm']-1)+1e-8)
        self.assertTrue(any(abs(p['requested_tangent_phase_mm'])>abs(p['tangent_phase_mm']) for p in self.data['layers']))

    def test_axial_flange_intrusion_rejected(self):
        c=json.loads(CONFIG.read_text());c['axial_phases_mm'][0]=250
        with self.assertRaisesRegex(ValueError,'axial phase'):
            build(c)

    def test_collector_reservation_not_hidden(self):
        c=json.loads(CONFIG.read_text());c['row_collector_gap_mm']=1
        with self.assertRaisesRegex(ValueError,'collector'):
            build(c)

    def test_identifier_round_trips_and_capacity(self):
        for sector,layer,carrier,mid,sensor in ((0,0,0,0,0),(15,35,131,1,35)):
            cid=encode(sector,layer,carrier,mid,sensor)
            self.assertEqual([(cid>>shift)&mask for shift,mask in ((10,15),(14,63),(20,4095),(32,3),(34,63))],
                             [sector,layer,carrier,mid,sensor])
        for args in ((16,0,0),(0,64,0),(0,0,4096)):
            with self.assertRaises(ValueError):encode(*args)

    def test_duplicate_placement_rejected(self):
        d=dict(self.data);d['placements']=self.data['placements']+[self.data['placements'][0]]
        with self.assertRaisesRegex(ValueError,'duplicate'):
            validate(d)

    def test_improper_frame_rejected(self):
        d=dict(self.data);p=copy.deepcopy(d['placements'][0]);p['frame'][0]=[-v for v in p['frame'][0]]
        d['placements']=[p]+d['placements'][1:]
        with self.assertRaisesRegex(ValueError,'improper'):
            validate(d)

    def test_corrupt_origin_and_row_identity_rejected(self):
        for key in ('origin_mm','carrier'):
            d=dict(self.data);p=copy.deepcopy(d['placements'][0]);d['placements']=[p]+d['placements'][1:]
            if key=='origin_mm':p[key][0]+=1
            else:p[key]+=1
            with self.assertRaises(ValueError):validate(d)

    def test_paid_channels_and_mass_ownership(self):
        d=dict(self.data);d['summary']=dict(d['summary']);d['summary']['powered_channels']=d['summary']['tiles']
        with self.assertRaisesRegex(ValueError,'powered'):
            validate(d)
        d['summary']=dict(self.data['summary']);d['summary']['material_mass_g']+=100
        with self.assertRaisesRegex(ValueError,'mass ownership'):
            validate(d)

    def test_core_mask_keeps_physical_tile_and_board_gaps(self):
        c=self.data['common']['config']
        self.assertTrue(core(18,3,c))
        self.assertFalse(core(0,3,c))
        self.assertFalse(core(33,3,c))
        self.assertFalse(core(18,100,c))

    def test_midplane_adverse_control_and_staggered_recovery(self):
        self.assertEqual(ray(self.data,0,0,'aligned_midplane_gap')['active_planes'],0)
        self.assertGreater(ray(self.data,0,0,'staggered')['active_planes'],0)

    def test_steel_normal_path_and_sector_seam(self):
        self.assertAlmostEqual(ray(self.data,0,0)['steel_path_mm'],36*30)
        self.assertAlmostEqual(ray(self.data,0,math.pi/16)['steel_path_mm'],0)
        self.assertEqual(ray(self.data,2,0)['active_planes'],0)

    def test_proper_basis_and_transformed_common_ports(self):
        for phi in (0,.3,math.pi):
            basis=frame(phi);self.assertAlmostEqual(determinant(basis),1)
            self.assertAlmostEqual(sum(v*v for v in basis[0]),1)
            p=transform([0,0,0],basis,[0,120,8.5])
            self.assertAlmostEqual(p[2],120)
        for p in self.data['placements'][::7000]:
            ports=water_ports(p,self.data['common'])
            self.assertEqual(len(ports),4)
            for world,local in zip(ports,self.data['common']['cooling_handoffs']):
                self.assertAlmostEqual(world['centre_mm'][2],p['local_xy_mm'][1]+local['centre_mm'][1])
                self.assertEqual(world['direction'],[0,0,local['direction'][1]])

    def test_direct_global_tile_centres_agree_with_lookup(self):
        # Start from the independent common-module channel map and actual global
        # placement, then reconstruct an IP ray; no grid inverse is reused here.
        for p in self.data['placements'][::7000]:
            for tile in common_unit()['channel_map'][::7]:
                point=transform(p['origin_mm'],p['frame'],tile['tile_center_mm'])
                r=math.hypot(point[0],point[1])
                result=ray(self.data,math.asinh(point[2]/r),math.atan2(point[1],point[0]))
                self.assertIn(p['layer'],result['layers'])


if __name__=='__main__':unittest.main()
