import copy
import importlib.util
import json
import gzip
import math
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from model import load,build,screen,frame,foot_profile,ROOT,sha,INPUT,CONTROL_INPUT
spec=importlib.util.spec_from_file_location('ss_export',HERE/'export.py')
generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)


class BarrelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=load(CONTROL_INPUT);cls.layout=build(cls.c)

    def test_default_selects_retained_tilted_baseline(self):
        self.assertEqual(INPUT,HERE/'inputs-phi-tilted.json')
        baseline=build(load())
        retained=json.loads(gzip.decompress((ROOT/'docs/validation/DES-020/phi-tilted/layout.json.gz').read_bytes()))
        self.assert_snapshot(baseline,retained)
        self.assertEqual([x['staves'] for x in baseline['layers']],[44,56,80,108])
        self.assertEqual(len(baseline['modules']),8064)
        self.assertEqual(generator.INPUT,INPUT)

    def test_every_module_has_one_unambiguous_route(self):
        routed=[m for r in self.layout['routes'] for m in r['modules']]
        self.assertEqual(len(routed),len(set(routed)))
        self.assertEqual(set(routed),{m['name'] for m in self.layout['modules']})
        self.assertEqual(len(self.layout['routes']),2*len(self.layout['staves']))
        for r in self.layout['routes']:
            self.assertEqual(r['harnesses'],2)
            self.assertEqual(len(r['modules']),14)
            self.assertEqual(r['waypoints_rz_mm'][-1][1],r['side']*3500)

    def test_covariance_axes_and_repeated_readout(self):
        for m in self.layout['modules']:
            self.assertEqual(m['v'],[0,0,1])
            cross=[m['u'][1],-m['u'][0],0]
            for a,b in zip(cross,m['n']):self.assertAlmostEqual(a,b)
        result=screen(self.c,self.layout)
        self.assertEqual(result['channels_per_module'],122880)

    def test_tangential_control_matches_retained_placement(self):
        control=json.loads(gzip.decompress((ROOT/'docs/validation/DES-020/layout.json.gz').read_bytes()))
        self.assert_snapshot(self.layout,control)

    def assert_snapshot(self,actual,expected,path='layout'):
        """Exact structure/IDs; libm rounding envelope for serialized floats.

        Eight ULPs are machine precision (<=9.1e-13 mm at radius660 mm),
        far stricter than the established 1e-7 mm native transform gate.
        Comparing a macOS libm snapshot bit-for-bit fails on Linux despite
        unchanged geometry. This never regenerates or rounds the old artifact.
        """
        self.assertEqual(type(actual),type(expected),path)
        if isinstance(expected,dict):
            self.assertEqual(actual.keys(),expected.keys(),path)
            for key in expected:self.assert_snapshot(actual[key],expected[key],path+'.'+key)
        elif isinstance(expected,list):
            self.assertEqual(len(actual),len(expected),path)
            for i,(a,b) in enumerate(zip(actual,expected)):self.assert_snapshot(a,b,f'{path}[{i}]')
        elif isinstance(expected,float):
            self.assertLessEqual(abs(actual-expected),8*max(math.ulp(actual),math.ulp(expected)),path)
        else:self.assertEqual(actual,expected,path)

    def test_snapshot_distinguishes_roundoff_from_changed_placement(self):
        c=copy.deepcopy(self.layout)
        x=c['modules'][0]['center_mm'][0]
        c['modules'][0]['center_mm'][0]=math.nextafter(x,math.inf)
        self.assert_snapshot(c,self.layout)
        c['modules'][0]['center_mm'][0]=x+1e-8
        with self.assertRaises(AssertionError):self.assert_snapshot(c,self.layout)

    def test_phi_alternative_is_rotationally_repeated_with_signed_axes(self):
        c=load(HERE/'inputs-phi-tilted.json');layout=build(c)
        for layer in layout['layers']:
            staves=[s for s in layout['staves'] if s['layer']==layer['layer']]
            self.assertEqual({s['radius_mm'] for s in staves},{layer['nominal_radius_mm']})
            step=2*math.pi/len(staves)
            modules=[m for m in layout['modules'] if m['layer']==layer['layer']]
            for m in modules:
                a=modules[((m['stave']+1)%len(staves))*c['rows']+m['row']]
                for key in ('center_mm','u','n'):
                    x,y,z=m[key];rot=[math.cos(step)*x-math.sin(step)*y,math.sin(step)*x+math.cos(step)*y,z]
                    self.assertLess(math.dist(rot,a[key]),1e-9)
                er=[math.cos(m['phi_rad']),math.sin(m['phi_rad']),0]
                ep=[-er[1],er[0],0]
                self.assertAlmostEqual(sum(x*y for x,y in zip(m['n'],er)),math.cos(math.radians(15)))
                self.assertAlmostEqual(sum(x*y for x,y in zip(m['n'],ep)),math.sin(math.radians(15)))
        with tempfile.TemporaryDirectory() as t:
            inventory=generator.export(c,Path(t),HERE/'inputs-phi-tilted.json')
            self.assertEqual(inventory['provenance']['input_sha256'],sha(HERE/'inputs-phi-tilted.json'))

    def test_beveled_shoe_touches_ring_and_stave_without_penetration(self):
        c=load(HERE/'inputs-phi-tilted.json');tilt=math.radians(c['phi_tilt_deg'])
        for r in c['nominal_radii_mm']:
            shoe=foot_profile(c,r);mid=shoe['center_w_mm'];h=shoe['height_mm'];ring=r-17
            for u in (-c['foot_width_mm']/2,0,c['foot_width_mm']/2):
                point=frame(0,r,[c['foot_u_mm']+u,0,mid-h/2+shoe['bottom_slope']*u],tilt)
                self.assertGreaterEqual(math.hypot(*point[:2]),ring-1e-10)
                if u==0:self.assertAlmostEqual(math.hypot(*point[:2]),ring)
                self.assertAlmostEqual(mid+h/2,-6.8)
            self.assertEqual(c['foot_u_mm']-c['foot_width_mm']/2,13.5)
            self.assertEqual(c['foot_u_mm']+c['foot_width_mm']/2,15.5)

    def test_phi_input_rejects_mixed_lanes_or_unsupported_angle(self):
        for tilt,lane in ((15,12),(-15,0),(20,0)):
            c=copy.deepcopy(self.c);c.update(phi_tilt_deg=tilt,lane_step_mm=lane)
            with tempfile.TemporaryDirectory() as t:
                p=Path(t)/'bad.json';p.write_text(json.dumps(c))
                with self.assertRaisesRegex(ValueError,'Phi alternative'):load(p)

    def test_invalid_clearance_and_stale_sources_are_rejected(self):
        c=copy.deepcopy(self.c);c['pickup_mm'][1]=100
        with self.assertRaisesRegex(ValueError,'pickup'):build(c)
        c=copy.deepcopy(self.c);c['lane_step_mm']=2
        with self.assertRaisesRegex(ValueError,'Lane'):build(c)
        c=copy.deepcopy(self.c);c['input_sha256'][next(iter(c['input_sha256']))]='0'*64
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text(json.dumps(c))
            with self.assertRaisesRegex(ValueError,'Pinned'):load(p)

    def test_native_constituents_and_guards_are_disjoint(self):
        with tempfile.TemporaryDirectory() as t:
            expected=generator.export(self.c,Path(t))
            counts=expected['counts']
            self.assertEqual(counts['sensitive'],len(self.layout['modules']))
            self.assertEqual(counts['readout'],8*counts['sensitive'])
            self.assertEqual(counts['cooling_tube'],4*len(self.layout['staves']))
            self.assertEqual(counts['ring'],4*len(self.c['bearing_z_mm']))
            core=ET.parse(Path(t)/'short-strip-barrel.xml').find('.//piece[@role="core"]')
            self.assertEqual(len(core.findall('cut')),6)
            # Pipe envelope stays inside core and support width; two central U loops clear.
            self.assertLess(abs(self.c['tube_w_mm']+4.05)+self.c['tube_OD_mm']/2,2.5)
            self.assertLess(self.c['tube_offset_u_mm']+self.c['tube_OD_mm']/2,self.c['stave_width_mm']/2)
            self.assertGreater(self.c['loop_start_mm']-self.c['tube_offset_u_mm']-self.c['tube_OD_mm']/2,0)
            for e in expected['entities']:
                if 'volume_mm3' in e:self.assertGreater(e['volume_mm3'],0)

    def test_short_collector_rejected_and_adverse_budgets_retained(self):
        c=load(HERE/'inputs-30mm-control.json')
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError,'capacity'):generator.export(c,Path(t))
        s=screen(self.c,self.layout)
        self.assertTrue(s['packing'][0]['passed'])
        self.assertFalse(s['packing'][1]['passed'])
        self.assertFalse(s['packing'][2]['passed'])
        stress=[x for x in s['thermal_electrical_flow'] if x['load']=='channel_scaled_proxy']
        self.assertTrue(any(not x['thermal_passed'] for x in stress))


if __name__=='__main__':unittest.main()
