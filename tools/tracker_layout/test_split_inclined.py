"""Scope/regression checks for the C1/C2 ablation; no detector acceptance."""
import copy
import json
from pathlib import Path
import unittest

from inclined_study import crossings, summarize, area_ledger
from split_inclined import variants


class SplitControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[2]
        cls.a=json.loads((root/'docs/design/DES-006-layouts.json').read_text())['candidates'][0]
        cls.c=json.loads((root/'docs/design/DES-006-inclined-layouts.json').read_text())['candidate']
        _,cls.c1,cls.c2=variants(cls.a,cls.c)

    def test_c1_long_strips_exactly_baseline_with_two_faces(self):
        original=[l for l in self.a['layers'] if l['subsystem']=='long_strip']
        actual=[l for l in self.c1['layers'] if l['subsystem']=='long_strip']
        self.assertEqual(len(original),len(actual))
        for a,b in zip(original,actual):
            normalized=copy.deepcopy(b);normalized['id']='A'+b['id'][2:];normalized.pop('station_group')
            self.assertEqual(a,normalized)
        self.assertEqual(area_ledger(self.a)['silicon_face_area_m2']['long_strip'],
                         area_ledger(self.c1)['silicon_face_area_m2']['long_strip'])

    def test_c2_is_old_c_only_renamed_and_c1_keeps_short_strips(self):
        for a,b in zip(self.c['layers'],self.c2['layers']):
            normalized=copy.deepcopy(b)
            normalized['id']='C'+b['id'][2:]
            normalized['station_group']='C'+b['station_group'][2:]
            self.assertEqual(a,normalized)
        self.assertEqual(len(self.c['layers']),len(self.c2['layers']))
        for c in [self.c1,self.c2]:
            short=[l for l in c['layers'] if l['subsystem']=='short_strip']
            expected=[l for l in self.c['layers'] if l['subsystem']=='short_strip']
            self.assertEqual(len(short),len(expected))
            self.assertEqual(area_ledger(c)['reference_area_m2']['short_strip'],
                             area_ledger(self.c)['reference_area_m2']['short_strip'])
            self.assertEqual(len({l['id'] for l in c['layers']}),len(c['layers']))

    def test_increment_is_only_long_strip_material(self):
        for eta in [0,.5,.8,1.,1.2,1.5,2.,4.]:
            for zv in [-.15,0,.15]:
                h1=crossings(self.c1,eta,zv,1,4)
                h2=crossings(self.c2,eta,zv,1,4)
                hc=crossings(self.c,eta,zv,1,4)
                self.assertEqual(summarize(h2),summarize(hc))
                def long_x0(hits): return sum(h[3] for l,h in hits if l['subsystem']=='long_strip')
                self.assertAlmostEqual(summarize(h2)['local_material_percent']-summarize(h1)['local_material_percent'],long_x0(h2)-long_x0(h1))


if __name__=='__main__': unittest.main()
