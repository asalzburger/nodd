"""Geometric/ID contracts and negative controls for the new standalone HCAL."""
import copy
import math
import unittest
import xml.etree.ElementTree as ET
from model import build,common,decode,encode,placements,transform,validate_config
from export import compact
from tempfile import TemporaryDirectory
from pathlib import Path


class HCALGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=build()

    def test_frozen_stack_and_unchanged_hardware(self):
        r=self.r;u,_=common()
        self.assertEqual(r['depth']['total_mm'],2590)
        self.assertEqual(r['depth']['steel_mm'],1800)
        self.assertEqual(len(u['parts']),394)
        self.assertEqual(len(r['unit_tile_map']),72)
        self.assertFalse(any(p['role']=='absorber_reference' for p in u['parts']))
        self.assertEqual(r['counts']['barrel_carriers'],181232)
        self.assertEqual(r['counts']['endcap_carriers'],110880)
        self.assertEqual(r['sensitive_tiles'],21032064)

    def test_depth_amendment_cannot_be_hidden(self):
        c=copy.deepcopy(self.r['config']);c['steel_mm']=29
        with self.assertRaisesRegex(ValueError,'closure'):validate_config(c)
        c=copy.deepcopy(self.r['config']);c['layers']=64
        with self.assertRaisesRegex(ValueError,'frozen'):validate_config(c)
        c=copy.deepcopy(self.r['config']);c['radial_handoff_mm']=5800
        with self.assertRaisesRegex(ValueError,'handoff'):validate_config(c)

    def test_all_carrier_ids_unique_and_capacity(self):
        ids=set();count=0
        for p in placements(self.r['config'],self.r['barrel_layers'],self.r['endcap_pattern']):
            self.assertNotIn(p['volume_id'],ids);ids.add(p['volume_id']);count+=1
            self.assertEqual({k:decode(p['volume_id'])[k] for k in ('system','side','sector','layer','carrier')},{k:p[k] for k in ('system','side','sector','layer','carrier')})
        self.assertEqual(count,self.r['counts']['carriers'])
        with self.assertRaisesRegex(ValueError,'capacity'):encode(13,0,16,0,0)
        with self.assertRaisesRegex(ValueError,'system and side'):encode(14,0,0,0,0)

    def test_both_endcaps_proper_frames_and_mirror_positions(self):
        e=self.r['endcap_pattern'];helper=__import__('model').endcap_helpers()
        samples=list(e['carriers'][i] for i in (0,len(e['carriers'])//2,-1))
        for phase in self.r['config']['endcap']['phases_deg']:
            a=helper.frame_for(phase,1);b=helper.frame_for(phase,2)
            self.assertAlmostEqual(helper.determinant(a),1)
            self.assertAlmostEqual(helper.determinant(b),1)
            for q in samples:
                x,y=helper.rotate_xy(q['center_xy_mm'],phase)
                for tile in self.r['unit_tile_map']:
                    p=transform(tile['tile_center_mm'],[x,y,6790],a)
                    n=transform(tile['tile_center_mm'],[x,-y,-6790],b)
                    self.assertAlmostEqual(p[0],n[0]);self.assertAlmostEqual(p[1],-n[1]);self.assertAlmostEqual(p[2],-n[2])

    def test_compact_retains_all_original_shapes_and_table(self):
        with TemporaryDirectory() as tmp:doc=compact(self.r,Path(tmp))
        for d in doc.findall('detectors/detector'):
            unit=d.find("template[@compound_tiles='true']")
            self.assertEqual(len(unit.findall('piece')),394)
            active=unit.findall('piece[@role="sensitive"]')
            self.assertEqual(len(active),72)
            for tile in active:
                self.assertEqual(len(tile.findall('shape/cut')),1)
            table=doc.find(f"readouts/readout[@name='{d.get('readout')}']/segmentation").get('tile_table_mm').split()
            self.assertEqual(len(table),72*5)
            self.assertEqual(list(map(float,table[:5])),[0,0,0,0,0])
            self.assertEqual(list(map(float,table[36*5:37*5])),[1,0,186,0,0])
            self.assertEqual({tuple(map(int,(table[i],table[i+1]))) for i in range(0,len(table),5)},{(m,s) for m in (0,1) for s in range(36)})
        self.assertIsNone(doc.find('fields'))
        self.assertEqual({int(d.get('id')) for d in doc.findall('detectors/detector')},{13,14})


if __name__=='__main__':unittest.main()
