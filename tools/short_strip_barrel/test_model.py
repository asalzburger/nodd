import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from model import load,build,screen
spec=importlib.util.spec_from_file_location('ss_export',HERE/'export.py')
generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)


class BarrelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=load();cls.layout=build(cls.c)

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
