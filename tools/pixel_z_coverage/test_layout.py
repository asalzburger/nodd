"""Physical and preservation checks for the isolated DES-013 replacement."""
import copy
import json
import math
from pathlib import Path
import unittest

from layout import ROOT, barrel, build, load, row_centres, shape


class LayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads(Path(__file__).with_name('config.json').read_text())
        cls.baseline=load(cls.config)
        cls.models=cls.baseline['metadata']['models']

    def test_hash_guard(self):
        with self.assertRaises(ValueError):load(dict(self.config,baseline_sha256='wrong'))

    def test_unchanged_detector_and_identifiers(self):
        for case in self.config['cases'][1:]:
            with self.subTest(case=case['id']):
                layout=build(self.baseline,case)
                self.assertEqual(layout['layers'],self.baseline['layers'])
                for field in ('modules','bodies'):
                    self.assertEqual([v for v in layout[field] if not barrel(v)],
                                     [v for v in self.baseline[field] if not barrel(v)])
                ids=[p['id'] for p in layout['modules']]
                self.assertEqual(len(ids),len(set(ids)))
                mids=[b['module_id'] for b in layout['bodies']]
                self.assertEqual(len(mids),len(set(mids)))
                owners={b['module_id']:b for b in layout['bodies']}
                for p in layout['modules']:
                    if not barrel(p):continue
                    self.assertAlmostEqual(p['active_area_mm2'],384.)
                    b=owners[p['module_id']]
                    for axis in ('u','v'):
                        delta=sum((p['center_mm'][i]-b['center_mm'][i])*b[axis][i] for i in range(3))
                        self.assertLessEqual(abs(delta)+p['half_'+axis+'_mm'],b['half_'+axis+'_mm']+1e-9)

    def test_rotates_periphery_and_keeps_readout_dead_seam(self):
        c=self.config['cases'][1]
        single=shape('single',self.models,c)
        self.assertAlmostEqual(single['offset_phi'],-.9)
        self.assertEqual(single['active_z'],20.)
        quad=shape('quad',self.models,c)
        points=sorted(set(v for u,v,hu,hv in quad['patches']))
        self.assertAlmostEqual(points[1]-points[0]-20.,.2)
        self.assertAlmostEqual(quad['body_phi'],44.2)
        self.assertAlmostEqual(quad['body_z'],43.2)

    def test_packing_clearance_endpoints_and_chip_centred_phase(self):
        for case in self.config['cases'][2:]:
            for family in ('single','quad'):
                s=shape(family,self.models,case)
                centres=row_centres(-550,550,s,case)
                self.assertGreaterEqual(centres[0]-s['body_z']/2,-550-1e-9)
                self.assertLessEqual(centres[-1]+s['body_z']/2,550+1e-9)
                for a,b in zip(centres,centres[1:]):self.assertAlmostEqual(b-a-s['body_z'],case['gap_mm'])
                if case['phase']=='chip':
                    self.assertLess(min(abs(c+v) for c in centres for u,v,hu,hv in s['patches']),1e-9)
                # Adding a row at either end must violate the specified envelope.
                pitch=s['body_z']+case['gap_mm']
                if case['phase']=='chip':
                    self.assertLess(centres[0]-pitch-s['body_z']/2,-550)
                    self.assertGreater(centres[-1]+pitch+s['body_z']/2,550)

    def test_no_mutation(self):
        before=copy.deepcopy(self.baseline)
        build(self.baseline,self.config['cases'][4])
        self.assertEqual(self.baseline,before)

    def test_rejects_zero_clearance(self):
        with self.assertRaises(ValueError):shape('single',self.models,dict(self.config['cases'][4],gap_mm=0))

if __name__=='__main__':unittest.main()
