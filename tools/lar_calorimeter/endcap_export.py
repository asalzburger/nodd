"""Isolated DES033 turbine compact/export with explicit service parents."""
import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from barrel_export import pose, write, totals as passive_totals
from endcap_geometry import ROOT, build, sha


def shape(node,piece):
    node.set('kind',piece['shape_kind'])
    for key,value in piece.get('dimensions_mm',{}).items():node.set(key,f'{value:.17g}*mm')
    if piece['shape_kind'] in ('arb8','xtru'):
        if piece['shape_kind']=='arb8':node.set('half_z',f"{piece['half_z_mm']:.17g}*mm")
        else:node.set('depth',f"{piece['depth_mm']:.17g}*mm")
        for x,y in piece['vertices_mm']:ET.SubElement(node,'vertex',x=f'{x:.17g}*mm',y=f'{y:.17g}*mm')
    if 'clip_annulus_mm' in piece:
        a=piece['clip_annulus_mm'];depth=2*piece['half_z_mm'] if piece['shape_kind']=='arb8' else piece['depth_mm']
        ET.SubElement(node,'annulus',rmin=f"{a['rmin']:.17g}*mm",rmax=f"{a['rmax']:.17g}*mm",length=f'{depth:.17g}*mm')
    for cut in piece.get('cuts',[]):
        e=ET.SubElement(node,'cut');shape(e,cut);pose(e,cut)


def piece(parent,p):
    e=ET.SubElement(parent,'piece',name=p['name'],role=p['role'],material=p['material'])
    shape(e,p);pose(e,p)
    if p['role']=='sensitive':e.set('gap',str(p['gap']))
    if 'parent_name' in p:e.set('parent_name',p['parent_name'])


def totals(report):
    view=dict(pieces=[],replicas=[],passive=report['passive'],materials=report['materials'])
    passive_totals(view)
    values=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    for name,row in view['material_totals'].items():values[name].update(row)
    count=len(report['passive'])
    for wheel in report['wheels']:
        mult=sum(r['wheel']==wheel['wheel'] for r in report['replicas'])
        if mult!=2*wheel['periods']:raise ValueError('Missing physical wheel/side/period')
        count+=mult*len(wheel['pieces'])
        for p in wheel['pieces']:
            for key in ('volume_mm3','mass_g'):values[p['material']][key]+=mult*p[key]
    report['material_totals']=dict(values);report['mass_g']=sum(v['mass_g'] for v in values.values());report['physical_material_parts']=count


def compact(report,out):
    doc=ET.Element('lccdd');ET.SubElement(doc,'info',name='LAYOUT002LArEndcapPrototype',title='DES033 isolated turbine LAr endcaps',author='nODD',version='0.1',status='prototype')
    ET.SubElement(ET.SubElement(doc,'includes'),'gdmlFile',ref='materials.xml')
    define=ET.SubElement(doc,'define')
    for key,value in dict(world_x=6500,world_y=6500,world_z=report['envelopes']['warm_back_z_mm']+2000).items():ET.SubElement(define,'constant',name=key,value=f'{value:.17g}*mm')
    ro=report['readout'];readout=ET.SubElement(ET.SubElement(doc,'readouts'),'readout',name=ro['name'])
    table=[v for w in report['wheels'] for ref in w['reference_points'] for v in (w['wheel'],ref['rho'],ref['z'],*ref['position_mm'])]
    wheel_table=[v for w in report['wheels'] for v in (w['inner_radius_mm'],w['outer_radius_mm'],w['periods'],w['radial_bins'])]
    ET.SubElement(readout,'segmentation',type='nODDLArEndcapGrid',sampling_depth_mm=format(ro['sampling_depth_mm'],'.17g'),axial_bins=str(ro['axial_bins']),wheel_table_mm=' '.join(format(v,'.17g') for v in wheel_table),reference_table_mm=' '.join(format(v,'.17g') for v in table))
    ET.SubElement(readout,'id').text=ro['descriptor']
    d=ET.SubElement(ET.SubElement(doc,'detectors'),'detector',name='LArEndcaps',id=str(ro['system_id']),type='nODDLArEndcapPrototype',readout=ro['name']);ET.SubElement(d,'sensitive',type='calorimeter')
    for wheel in report['wheels']:
        e=ET.SubElement(d,'wheel',index=str(wheel['wheel']),name='TurbineWheel'+str(wheel['wheel']))
        for p in wheel['pieces']:piece(e,p)
    for r in report['replicas']:
        e=ET.SubElement(d,'replica',**{k:str(r[k]) for k in ('side','wheel','plane')});pose(e,r)
    for p in report['passive']:piece(d,p)
    write(out/'endcaps.xml',doc)


def export(out,services=None):
    out.mkdir(parents=True,exist_ok=True);report,m=build()
    if services:
        specification=importlib.util.spec_from_file_location('endcap_services',services);module=importlib.util.module_from_spec(specification);specification.loader.exec_module(module)
        result=module.augment(report,m)
        if result is not None:report=result
        report['source_sha256'][str(services.resolve().relative_to(ROOT))]=sha(services)
    report['materials']=m.recipes;totals(report);write(out/'materials.xml',m.root);compact(report,out)
    for p in (Path(__file__),ROOT/'tools/lar_calorimeter/barrel_export.py',ROOT/'prototypes/calorimeter/LArEndcap.cpp'):report['source_sha256'][str(p.relative_to(ROOT))]=sha(p)
    report['execution']=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)))
    report['artifact_sha256']={p.name:sha(p) for p in (out/'endcaps.xml',out/'materials.xml')}
    (out/'expected.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Exported',report['physical_sensitive_elements'],'raw IDs;',report['logical_channels'],'logical cells;',report['mass_g']/1e6,'t')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--services',type=Path)
    a=p.parse_args();export(a.output,a.services)
