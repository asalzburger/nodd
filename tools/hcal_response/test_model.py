"""Geometric/ID contracts and negative controls for the new standalone HCAL."""
import copy
import math
import unittest
import xml.etree.ElementTree as ET
from model import build,common,decode,encode,placements,transform,validate_config,load
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
        self.assertEqual(r['counts']['barrel_common_carriers'],178224)
        self.assertEqual(r['counts']['barrel_edge_carriers'],90240)
        self.assertEqual(r['counts']['barrel_carriers'],268464)
        self.assertEqual(len(r['units']),101)
        self.assertEqual(r['counts']['endcap_carriers'],110880)
        self.assertEqual(r['sensitive_tiles'],23157216)

    def test_depth_amendment_cannot_be_hidden(self):
        c=copy.deepcopy(self.r['config']);c['steel_mm']=29
        with self.assertRaisesRegex(ValueError,'closure'):validate_config(c)
        c=copy.deepcopy(self.r['config']);c['layers']=64
        with self.assertRaisesRegex(ValueError,'frozen'):validate_config(c)
        c=copy.deepcopy(self.r['config']);c['radial_handoff_mm']=5800
        with self.assertRaisesRegex(ValueError,'handoff'):validate_config(c)
        c=copy.deepcopy(self.r['config'])
        corner=c['barrel']['outer_apothem_mm']/math.cos(math.pi/c['sectors'])
        c['radial_handoff_mm']=corner+69.9
        with self.assertRaisesRegex(ValueError,'service clearance'):validate_config(c)
        c['radial_handoff_mm']=corner+70
        self.assertEqual(validate_config(c),2590)

    def test_all_carrier_ids_unique_and_capacity(self):
        ids=set();count=0
        for p in placements(self.r['config'],self.r['barrel_layers'],self.r['endcap_pattern']):
            self.assertNotIn(p['volume_id'],ids);ids.add(p['volume_id']);count+=1
            self.assertEqual({k:decode(p['volume_id'])[k] for k in ('system','side','sector','layer','carrier','unit')},{k:p[k] for k in ('system','side','sector','layer','carrier','unit')})
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

    def test_compact_retains_original_and_new_physical_parts_and_explicit_tables(self):
        with TemporaryDirectory() as tmp:doc=compact(self.r,Path(tmp))
        for d in doc.findall('detectors/detector'):
            units=d.findall("template[@compound_tiles='true']")
            expected_ids=set(self.r['units']) if d.get('name')=='HCALBarrel' else {'0'}
            self.assertEqual({p.get('unit') for p in units},expected_ids)
            for unit in units:
                source=self.r['units'][unit.get('unit')]
                self.assertEqual(len(unit.findall('piece')),len(source['parts']))
                active=unit.findall('piece[@role="sensitive"]')
                self.assertEqual(len(active),source['sensitive_count'])
                for tile in active:self.assertEqual(len(tile.findall('shape/cut')),1)
            table=list(map(float,doc.find(f"readouts/readout[@name='{d.get('readout')}']/segmentation").get('tile_table_mm').split()))
            wanted={(int(uid),t['module'],t['sensor']) for uid in expected_ids for t in self.r['units'][uid]['channel_map']}
            self.assertEqual(len(table),len(wanted)*9)
            self.assertEqual({tuple(map(int,table[i:i+3])) for i in range(0,len(table),9)},wanted)
            self.assertEqual(table[:9],[0,0,0,0,0,0,29.7,29.7,3])
        self.assertIsNone(doc.find('fields'))
        self.assertEqual({int(d.get('id')) for d in doc.findall('detectors/detector')},{13,14})

    def test_every_edge_has_actual_small_border_and_finite_sector_clearance(self):
        t=math.tan(math.pi/16);b=self.r['config']['barrel']
        for layer in self.r['barrel_layers']:
            for edge in layer['edges']:
                unit=self.r['units'][str(edge['unit'])];w,h,d=unit['fixture']['carrier_size_mm']
                for radial in (0,d):
                    boundary=(layer['carrier_front_mm']+radial)*t-3
                    self.assertLessEqual(abs(edge['center_x_mm'])+w/2,boundary-.5+1e-8)
                core_outer=max(edge['side']*(edge['center_x_mm']+q['tile_center_mm'][0])+q['tile_size_mm'][0]/2 for q in unit['channel_map'])
                gap=(layer['carrier_front_mm']+2)*t-core_outer
                self.assertAlmostEqual(gap,self.r['edge_coverage']['core_plane_inactive_half_strip_mm'],places=7)
                for core in unit['channel_map']:
                    board=next(p for p in unit['parts'] if p['name']==f"m{core['module']}_pcb_G10")
                    self.assertLess(abs(core['tile_center_mm'][0]-board['center_mm'][0])+core['tile_size_mm'][0]/2,board['dimensions_mm']['sx']/2)
                    self.assertGreater(core['tile_size_mm'][0],7)
        self.assertEqual(sorted(u['fixture']['carrier_size_mm'][0] for k,u in self.r['units'].items() if k!='0'),sorted({e['width_mm'] for q in self.r['barrel_layers'] for e in q['edges']}))

    def test_edge_invalid_physical_extension_is_rejected(self):
        from edge_units import validate,column_count
        helper=load('_hcal_edge_test_builder','tools/hcal_readout/readout.py')
        unit=copy.deepcopy(self.r['units']['1'])
        unit['parts'][0]['center_mm'][0]=unit['fixture']['carrier_size_mm'][0]/2
        with self.assertRaisesRegex(ValueError,'outside carrier'):validate(unit,helper)
        with self.assertRaisesRegex(ValueError,'capacity'):column_count(400)
        self.assertEqual(encode(13,0,0,0,0,module=1,sensor=35,unit=100),encode(13,0,0,0,0,module=1,sensor=35)+(100<<42))

    def test_complete_material_ledger_exposes_guide_mass_increase(self):
        from model import regional_materials
        old=copy.deepcopy(self.r['config']);old['barrel']['edge_rail_mm']=20
        before=regional_materials(old);after=regional_materials(self.r['config'])
        self.assertAlmostEqual((after['Steel235']['mass_g']-before['Steel235']['mass_g'])/1e6,101.5732224,places=6)
        self.assertAlmostEqual((after['Aluminium']['mass_g']-before['Aluminium']['mass_g'])/1e6,-50.07495168,places=6)
        self.assertGreater(self.r['material_totals']['Steel235']['mass_g'],after['Steel235']['mass_g']-.01)


if __name__=='__main__':unittest.main()
