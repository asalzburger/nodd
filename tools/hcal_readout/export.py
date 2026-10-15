"""Deterministic DES036 export; absent from production entry points."""
import argparse
import json
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from readout import ROOT, build, sha


def write(path, node):
    ET.indent(node, space='  ')
    ET.ElementTree(node).write(path, encoding='utf-8', xml_declaration=True)


def pose(node, p):
    for key,value in zip(('x','y','z'),p['center_mm']): node.set(key,f'{value:.17g}*mm')
    for i in range(3):
        for j in range(3): node.set(f'a{i}{j}',format(p['frame'][j][i],'.17g'))
    for key,value in p['dimensions_mm'].items(): node.set(key,f'{value:.17g}*mm')


def compact(report, out):
    doc=ET.Element('lccdd')
    ET.SubElement(doc,'info',name='HCALReadoutPrototype',title='DES036 isolated common readout module',author='nODD',version='0.1',status='prototype')
    ET.SubElement(ET.SubElement(doc,'includes'),'gdmlFile',ref='materials.xml')
    defs=ET.SubElement(doc,'define')
    for key,value in dict(world_x=2000,world_y=2000,world_z=2000).items(): ET.SubElement(defs,'constant',name=key,value=f'{value}*mm')
    ro=ET.SubElement(ET.SubElement(doc,'readouts'),'readout',name='HCALReadoutHits')
    ET.SubElement(ro,'segmentation',type='CartesianGridXY',grid_size_x='30*mm',grid_size_y='30*mm',offset_x='0*mm',offset_y='0*mm')
    ET.SubElement(ro,'id').text=report['id_descriptor']
    detector=ET.SubElement(ET.SubElement(doc,'detectors'),'detector',name='HCALReadout',id='9',type='nODDHCALReadoutPrototype',readout='HCALReadoutHits')
    ET.SubElement(detector,'sensitive',type='calorimeter')
    for p in report['parts']:
        piece=ET.SubElement(detector,'piece',name=p['name'],role=p['role'],owner=p['owner'],material=p['material'],kind=p['shape_kind'])
        pose(piece,p)
        if 'sensor' in p:
            piece.set('module',str(p['module'])); piece.set('sensor',str(p['sensor']))
        for q in p['cuts']:
            node=ET.SubElement(piece,'cut',kind=q['kind']); pose(node,q)
    write(out/'readout.xml',doc)


def export(out, absorber=True):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    report,mat=build(absorber=absorber)
    write(out/'materials.xml',mat.root);compact(report,out)
    report['execution']=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)))
    for path in (Path(__file__),ROOT/'prototypes/hcal_readout/Readout.cpp',ROOT/'prototypes/hcal_readout/CMakeLists.txt'):
        report['source_sha256'][str(path.relative_to(ROOT))]=sha(path)
    report['export_sha256']={name:sha(out/name) for name in ('materials.xml','readout.xml')}
    (out/'expected.json').write_text(json.dumps(report,indent=2)+'\n')
    nominal=report['budgets']['power_scenarios'][0]
    print(f"DES036 PROTOTYPE: {len(report['parts'])} parts, 72 tiles, 156 powered channels; carrier/modules {report['carrier_and_modules_mass_g']:.6f} g; nominal heat {nominal['total_heat_W']:.6f} W")
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--no-absorber',action='store_true')
    a=p.parse_args();export(a.output,not a.no_absorber)
