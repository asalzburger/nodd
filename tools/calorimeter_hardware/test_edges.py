"""Physical mask/ASIC/readout controls and forward-aperture negative controls."""
import copy
import json
import math
import unittest
from pathlib import Path

from edge_layout import ROOT, area, build, circle_intersection_area, contains, intersect, rectangle


class EdgeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report,cls.layouts,_=build()

    def test_physical_board_and_guard_containment(self):
        for layout in self.layouts.values():
            for m in layout['modules']:
                self.assertTrue(all(contains(m['board'],*v) for v in m['sensor']))
                self.assertTrue(all(contains(m['sensor'],*v) for v in m['active']))
                self.assertGreater(area(m['sensor']),area(m['active']))
                self.assertLessEqual(max(v[0] for v in m['sensor'])-min(v[0] for v in m['sensor']),90+1e-7)
                self.assertLessEqual(max(v[1] for v in m['sensor'])-min(v[1] for v in m['sensor']),90+1e-7)

    def test_boards_do_not_overlap(self):
        for layout in self.layouts.values():
            boxes=[]
            for m in layout['modules']:
                p=[[x+m['center_mm'][0],y+m['center_mm'][1]] for x,y in m['board']];boxes.append((p,[min(v[i] for v in p) for i in (0,1)],[max(v[i] for v in p) for i in (0,1)]))
            for i,(p,lo,hi) in enumerate(boxes):
                for q,lo2,hi2 in boxes[i+1:]:
                    if all(min(a,b)>max(c,d)+1e-7 for a,b,c,d in zip(hi,hi2,lo,lo2)):self.assertLess(area(intersect(p,q)),1e-6)

    def test_electrodes_partition_and_reference_points(self):
        for m in self.layouts['edges']['modules']:
            members=set();count=0
            for g in m['pads']:
                self.assertGreaterEqual(g['area_mm2'],.2*5.5**2-1e-7)
                self.assertTrue(any(contains(p,*g['reference_mm']) for p in g['polygons']))
                for p in g['polygons']:self.assertTrue(all(contains(m['active'],*v) for v in p))
                for q in g['members']:
                    self.assertNotIn(tuple(q),members);members.add(tuple(q));count+=1
            self.assertAlmostEqual(sum(g['area_mm2'] for g in m['pads']),area(m['active']),places=6)
            self.assertEqual(len(members),count)

    def test_packages_fit_and_channel_capacity(self):
        for m in self.layouts['edges']['modules']:
            self.assertGreaterEqual(64*len(m['asics']),len(m['pads']))
            self.assertLess(64*(len(m['asics'])-1),len(m['pads']))
            for x,y in m['asics']:self.assertTrue(all(contains(m['board'],*v) for v in rectangle(x-5.5,y-6.5,11,13)))
            for i,(x,y) in enumerate(m['asics']):
                for u,v in m['asics'][i+1:]:self.assertTrue(abs(x-u)>=11-1e-8 or abs(y-v)>=13-1e-8)

    def test_same_squares_survive_edge_addition(self):
        a={tuple(m['grid']):m for m in self.layouts['squares']['modules']};b={tuple(m['grid']):m for m in self.layouts['edges']['modules'] if m['full']}
        self.assertEqual(set(a),set(b))
        for grid in a:
            for key in ('index','center_mm','board','sensor','active','asics'):
                self.assertEqual(a[grid][key],b[grid][key],f'{grid}: {key}')
            self.assertEqual([g['key'] for g in a[grid]['pads']],[g['key'] for g in b[grid]['pads']])
        self.assertGreater(self.report['summary']['edges']['active_face_fraction'],self.report['summary']['squares']['active_face_fraction'])

    def test_forward_aperture_and_actual_cracks(self):
        r=self.report['eta4_front_radius_mm'];c=self.report['config'];self.assertLess(math.sqrt(2)*(c['inner_square_apothem_mm']+c['inner_support_mm']),r)
        self.assertFalse(self.layouts['edges']['hit'](r,0))
        self.assertTrue(self.layouts['edges']['hit'](r/math.sqrt(2),r/math.sqrt(2)))
        self.assertGreater(300,r)

    def test_circle_area_reference_cases(self):
        self.assertAlmostEqual(circle_intersection_area(rectangle(-2,-2,4,4),1),math.pi,places=10)
        self.assertAlmostEqual(circle_intersection_area(rectangle(-.1,-.1,.2,.2),1),.04,places=10)
        self.assertAlmostEqual(circle_intersection_area(rectangle(2,2,1,1),1),0,places=10)


if __name__=='__main__':unittest.main()
