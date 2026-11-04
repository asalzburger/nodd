import copy
import json
import math
import unittest
from barrel_geometry import build, ROOT
from barrel_services import augment
from barrel_export import totals
from services import budget

class ServiceTests(unittest.TestCase):
    def test_lane_bend_and_heat_negative_controls(self):
        b=budget();self.assertGreater(b['stations']['barrel']['ordinary_area_margin_mm2'],0)
        self.assertAlmostEqual(b['heat']['inferred_flow_kg_s'],200/120*1.07)
        for key,value in [('packing_fill',0),('front_service_gap_mm',100),('rear_service_gap_mm',100),('ordinary_lane_mm',[1,1]),('utility_lane_mm',[1,1])]:
            c=copy.deepcopy(b['config']);c[key]=value
            with self.assertRaises(ValueError):budget(c)
    def test_board_capacity_and_conserved_bath_mass(self):
        r,m=build();augment(r,m);totals(r)
        self.assertEqual(r['services']['physical_barrel']['board_envelopes'],5888)
        self.assertEqual(r['services']['physical_barrel']['capacity_channels'],3014656)
        self.assertEqual(r['services']['physical_barrel']['cooling_half_branches'],96)
        self.assertGreater(r['mass_g'],249e6)
        for key,value in [('board_radial_depth_mm',36),('barrel_ring_axial_width_mm',120),('barrel_ring_web_mm',30),('nitrogen_pipe_id_mm',16),('nitrogen_pipe_od_mm',22)]:
            c=copy.deepcopy(r['services']['config']);c[key]=value
            base,materials=build()
            with self.assertRaises(ValueError):augment(base,materials,c)
        roots={p['name']:p for p in r['passive']}
        for p in r['passive']:
            if p.get('parent_name') in ('rear_bath','end_bath_1','end_bath_-1'):
                parent=roots[p['parent_name']];d=parent['dimensions_mm']
                if p['shape_kind']=='box':
                    sx,sy,sz=[p['dimensions_mm'][k] for k in ('sx','sy','sz')]
                    corners=[]
                    for x in (-sx/2,sx/2):
                        for y in (-sy/2,sy/2):
                            point=[p['center_mm'][i]+p['frame'][0][i]*x+p['frame'][1][i]*y for i in range(3)]
                            corners.append(math.hypot(*point[:2]))
                    self.assertGreater(min(corners),d['rmin'])
                    self.assertLess(max(corners),d['rmax'])
                    self.assertLess(abs(p['center_mm'][2])+sz/2,d['length']/2)
                else:
                    q=p['dimensions_mm'];radius=math.hypot(*p['center_mm'][:2])
                    if radius:
                        self.assertGreater(radius-q['rmax'],d['rmin'])
                        self.assertLess(radius+q['rmax'],d['rmax'])
                    else:
                        self.assertGreater(q['rmin'],d['rmin']);self.assertLess(q['rmax'],d['rmax'])
                    self.assertLess(abs(p['center_mm'][2])+q['length']/2,d['length']/2)
        self.assertAlmostEqual(sum(x['mass_g'] for x in r['material_totals'].values()),r['mass_g'])
        altered=copy.deepcopy(r);next(p for p in altered['passive'] if p['name']=='rear_bath')['exclusive_volume_mm3']+=1e7
        with self.assertRaises(ValueError):totals(altered)

if __name__=='__main__':unittest.main()
