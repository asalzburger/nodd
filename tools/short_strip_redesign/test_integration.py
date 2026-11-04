"""Portable physical contract controls for the DES043 barrel adapter."""
import copy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from barrel_native import adapt
from integration import selection

ROOT=Path(__file__).resolve().parents[2]


class BarrelIntegration(unittest.TestCase):
    def fixture(self):
        c=json.loads((ROOT/'tools/short_strip_redesign/inputs.json').read_text())
        b=json.loads((ROOT/'tools/short_strip_barrel/inputs-phi-tilted.json').read_text())
        doc=ET.fromstring('<lccdd><readouts><readout><segmentation/></readout></readouts><detectors><detector><layer><stave name="test_stave" id="0" phi="0*rad" tilt="0.2617993877991494*rad" radius="260*mm"/></layer></detector></detectors></lccdd>')
        stave=doc.find('.//stave');entities=[]
        def add(parent,name,role,kind,point,dims,material='CarbonFoam'):
            ET.SubElement(parent,'piece',name=name,role=role,kind=kind,material=material,
                **{k:f'{v}*mm' for k,v in zip(('u','v','w'),point)},
                **{k:f'{v}'+('*rad' if k in ('start','angle') else '*mm') for k,v in dims.items()})
            entities.append(dict(name=name,role=role,material=material,center_mm=[0,0,0]))
        for label,w,t in [('front_skin',-1.375,.15),('front_glue',-1.5,.1),('core',-4.05,5),('back_skin',-6.725,.15)]:
            add(stave,'test_stave_'+label,'support','box',[0,0,w],dict(sx=52,sy=2420,sz=t))
        for side in (-1,1):
            for leg in (-1,1):
                add(stave,f'pipe{side}{leg}','cooling_tube','tube',[leg*12,side*613,-4.05],dict(rmin=1.11,rmax=1.25,length=1194),material='Titanium')
            add(stave,f'bend{side}','cooling_bend','torus',[0,side*16,-4.05],dict(rmin=1.11,rmax=1.25,major=12,start=math_pi if side>0 else 0,angle=math_pi),material='Titanium')
            add(stave,f'rail{side}','power_bus','box',[side*6.25,0,-7.05],dict(sx=12,sy=2420,sz=.2),material='Copper')
            module=ET.SubElement(stave,'module',name=f'module{side}',id=str(side+1),z=f'{side*128/3}*mm',lift=f'{1.5 if side>0 else 0}*mm')
            add(module,f'module{side}_active','sensitive','box',[0,0,0],dict(sx=48,sy=96,sz=.2),material='Silicon')
            add(module,f'module{side}_oldASIC','readout','box',[0,0,-.2],dict(sx=23.4,sy=23.4,sz=.15),material='Silicon')
            add(stave,f'old_pickup{side}','thermal_pickup','box',[10,side*128/3,-1],dict(sx=20,sy=64,sz=.4))
        names={'CarbonFoam','Titanium','Copper','Silicon','CFRP','Epoxy','Graphite','SignalFlex','BumpFixture'}
        expected=dict(entities=entities,materials={name:dict(density_g_cm3=1.) for name in names})
        return doc,expected,c,b

    def test_actual_barrel_windows_and_finite_straight_plus_bend_cuts(self):
        doc,e,c,b=self.fixture();adapt(doc,e,c,b,{})
        self.assertEqual(e['counts']['sensitive'],2)
        self.assertEqual(e['counts']['readout'],4)
        self.assertEqual(e['counts']['thermal_pickup'],4)
        self.assertNotIn('old_pickup',str(e))
        for node in doc.findall('.//piece'):
            if node.get('role')=='thermal_pickup':
                self.assertEqual({cut.get('kind') for cut in node.findall('cut')},{'tube','torus'})
                self.assertEqual(float(node.get('u')[:-3])**2,144.)
            if node.get('name')=='test_stave_back_skin':self.assertEqual(len(node.findall('cut')),0)
            if node.get('name')=='test_stave_front_skin':self.assertEqual(len(node.findall('cut')),4)
            if node.get('role')=='power_bus':self.assertEqual(node.get('sz'),'0.17*mm')
        bounded=[x for x in e['entities'] if x.get('cuts')]
        self.assertTrue(bounded)
        self.assertTrue(all('volume_mm3' not in x and 'mass_g' not in x and x['volume_bounds_mm3'][1]>0 for x in bounded))
        self.assertTrue(any(p['reason']=='Barrel titanium surface' for p in e['shape_probes']))
        self.assertEqual(len(doc.findall('.//piece[@role="readout"]')),4)

    def test_obsolete_offset_or_unselected_configuration_fails(self):
        doc,e,c,b=self.fixture();c['thermal']['barrel_pad_u_mm']=10.
        with self.assertRaisesRegex(ValueError,'saddle'):adapt(doc,e,c,b,{})
        s,c=selection()
        self.assertEqual(s['expected_combined_sensitive'],46682)
        self.assertEqual(c['thermal']['barrel_pad_mm'],[20,64])


math_pi=3.141592653589793
if __name__=='__main__':unittest.main()
