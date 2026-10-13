"""Physical packing/ownership and adverse controls for the new barrel slabs."""
import copy
import math
import unittest
from barrel_layout import build, crossings
from barrel_export import hardware
from native_prism import native_capacity
from barrel_compare import intersects

class BarrelControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report,cls.base=build();cls.hw,_=hardware(cls.report,cls.base)
    def test_native_scaled_shifted_prism_is_rejected(self):
        class Prism:
            scale=1.;offset=0.;zoffset=0.;sections=2
            def ClassName(self):return 'TGeoXtru'
            def GetNz(self):return self.sections
            def GetNvert(self):return 4
            def GetX(self,i):return (0,2,2,0)[i]
            def GetY(self,i):return (0,0,2,2)[i]
            def GetZ(self,i):return (-5,5)[i]+self.zoffset
            def GetXOffset(self,i):return self.offset
            def GetYOffset(self,i):return 0.
            def GetScale(self,i):return self.scale
        p=Prism();self.assertAlmostEqual(native_capacity(p),40)
        for key,value in [('scale',2.),('offset',1.),('zoffset',2.),('sections',3)]:
            p=Prism();setattr(p,key,value)
            with self.assertRaises(ValueError):native_capacity(p)
    def test_finite_volume_boundary_and_parallel_miss(self):
        self.assertTrue(intersects([(9.5,10.5),(10.1,11.1),(-1,1)],[1,1,0]))
        self.assertFalse(intersects([(9.5,10.5),(10.6,11.6),(-1,1)],[1,1,0]))
        self.assertFalse(intersects([(9.5,10.5),(10.1,11.1),(1,2)],[1,1,0]))
    def test_retained_envelope_and_counts(self):
        r=self.report;self.assertEqual(len(r['layers']),48);self.assertEqual(r['summary']['sensors'],359904);self.assertEqual(r['summary']['channels'],92135424)
        self.assertAlmostEqual(r['envelopes']['ecal_barrel_outer_mm'],2223.2);self.assertAlmostEqual(r['envelopes']['hcal_barrel_front_mm'],2263.2)
        self.assertEqual([(len([p for p in r['layers'] if p['columns']==n])) for n in (6,7,8)],[18,22,8])
    def test_bays_and_frames_do_not_intersect_boards(self):
        for layer in self.report['layers']:
            panels=layer['panels'];self.assertAlmostEqual(panels[0]['center_mm']-panels[0]['length_mm']/2,-3880);self.assertAlmostEqual(panels[-1]['center_mm']+panels[-1]['length_mm']/2,3880)
            for left,right in zip(panels,panels[1:]):self.assertAlmostEqual(right['center_mm']-right['length_mm']/2-left['center_mm']-left['length_mm']/2,2)
            for p in panels:
                for z in p['row_centers_mm']:
                    self.assertLessEqual(abs(z-p['center_mm'])+47,p['length_mm']/2-5)
                    self.assertGreaterEqual(abs(z-p['bay_center_mm'])-47-20,2)
    def test_short_centering_is_rejected(self):
        c=copy.deepcopy(self.report['config']);c['short_panel_board_shift_mm']=1
        with self.assertRaisesRegex(ValueError,'board/bay'):build(c)
    def test_invalid_stagger_is_rejected(self):
        c=copy.deepcopy(self.report['config']);c['layer_panel_phases_mm']=[100]
        with self.assertRaisesRegex(ValueError,'panel phase'):build(c)
    def test_absorber_is_owned_once(self):
        for layer in self.hw['layers']:
            plates=[p for p in layer['parts'] if p['role']=='absorber'];self.assertEqual(len(plates),1);self.assertAlmostEqual(plates[0]['depth_mm'],7800)
        self.assertFalse(any(p['role']=='absorber' for p in self.hw['board_parts']+self.hw['frame_parts']))
    def test_cooling_void_and_filled_pipe_match(self):
        for layer in self.hw['layers']:
            plates=[p for p in layer['parts'] if p['role']=='spreader'];pipes=[p for p in layer['parts'] if p['role']=='pipe'];water=[p for p in layer['parts'] if p['role']=='water']
            void=sum(math.pi*q['dimensions_mm']['rmax']**2*q['dimensions_mm']['length'] for p in plates for q in p['cuts'])
            self.assertAlmostEqual(void,sum(p['volume_mm3'] for p in pipes+water),places=5)
            self.assertTrue(all(abs(max(v[0] for v in p['vertices_mm'])-min(v[0] for v in p['vertices_mm'])-3)<1e-8 for p in plates))
    def test_complete_lane_interface_ownership(self):
        for layer in self.report['layers']:
            self.assertEqual(sum(p['channels'] for p in layer['interfaces']),layer['channels'])
            for p in layer['panels']:
                lanes=[j for q in layer['interfaces'] if q['panel']==p['index'] for j in q['lanes']];self.assertEqual(sorted(lanes),list(range(layer['columns'])))
            self.assertTrue(all(q['channels']<=8192 for q in layer['interfaces']))
            self.assertLess(max(q['index'] for q in layer['modules']),1024)
    def test_real_cracks_and_stagger_control(self):
        self.assertEqual(len(crossings(self.report,0,0)),22)
        self.assertGreater(len(crossings(self.report,.25,.03)),0)
        c=copy.deepcopy(self.report['config']);c['layer_panel_phases_mm']=[0];control,_=build(c)
        self.assertEqual(len(crossings(control,.25,.03)),0)
        self.assertTrue(all(any(abs(z)<1e-8 for z in q['row_centers_mm']) for q in self.report['layers']))

if __name__=='__main__':unittest.main()
