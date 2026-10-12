"""Export DES028 prototypes; no link to production CMake or detector entry point."""
import argparse,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from model import ROOT,build,sha

def write(path,node):ET.indent(node,space='  ');ET.ElementTree(node).write(path,encoding='utf-8',xml_declaration=True)

def compact(units,out,mode='units',placements=None,extra=None):
    doc=ET.Element('lccdd');ET.SubElement(doc,'info',name='CalorimeterPrototype',title='isolated hardware prototypes',author='nODD',version='0.1',status='prototype')
    ET.SubElement(ET.SubElement(doc,'includes'),'gdmlFile',ref='materials.xml')
    defs=ET.SubElement(doc,'define')
    for k,v in dict(world_x=6000,world_y=6000,world_z=8000).items():ET.SubElement(defs,'constant',name=k,value=f'{v}*mm')
    readouts=ET.SubElement(doc,'readouts');dets=ET.SubElement(doc,'detectors')
    for u in units:
        name=u['name'].upper();ro=ET.SubElement(readouts,'readout',name=name+'Hits');p=u['cell_pitch_mm'];offset=u['cell_offset_mm']
        ET.SubElement(ro,'segmentation',type='CartesianGridXY',grid_size_x=f'{p}*mm',grid_size_y=f'{p}*mm',offset_x=f'{offset}*mm',offset_y=f'{offset}*mm')
        ET.SubElement(ro,'id').text='system:8,side:2,sector:5,layer:6,cassette:12,sensor:8,x:-9,y:-9'
        d=ET.SubElement(dets,'detector',name=name,id=str(u['system_id']),type='nODDCalorimeterPrototype',readout=name+'Hits',mode=mode)
        ET.SubElement(d,'sensitive',type='calorimeter')
        for p in u['parts']:
            e=ET.SubElement(d,'piece',name=p['name'],role=p['role'],material=p['material'],kind=p['shape_kind'],owner=p['owner'])
            for k,v in zip(('x','y','z'),p['center_mm']):e.set(k,f'{v:.17g}*mm')
            for i in range(3):
                for j in range(3):e.set(f'a{i}{j}',format(p['frame'][j][i],'.17g'))
            for k,v in p['dimensions_mm'].items():e.set(k,f'{v:.17g}*mm')
            if 'sensor' in p:e.set('sensor',str(p['sensor']))
            for cut in p['cuts']:
                node=ET.SubElement(e,'cut',kind=cut['kind'])
                for k,v in zip(('x','y','z'),cut['center_mm']):node.set(k,f'{v:.17g}*mm')
                for k,v in cut['dimensions_mm'].items():node.set(k,f'{v:.17g}*mm')
        if mode=='units':ET.SubElement(d,'placement',x=f'{-400 if name=="ECAL" else 400}*mm',y='0*mm',z='0*mm',side='0',sector='0',layer='0',cassette='0')
    write(out/'calorimeter.xml',doc)

def export(out):
    out.mkdir(parents=True,exist_ok=True);report,m=build();write(out/'materials.xml',m.root);compact(report['units'],out)
    report['execution']=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)))
    report['source_sha256'].update({str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),ROOT/'prototypes/calorimeter/Calorimeter.cpp')})
    (out/'expected.json').write_text(json.dumps(report,indent=2)+'\n')
    for u in report['units']:print(u['name'],u['sensitive_count'],'active elements',u['channels'],'channels',round(u['mass_g'],3),'g',round(u['power']['total_heat_W'],3),'W')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);export(p.parse_args().output)
