"""Export shared logical cassettes/sectors and complete physical assemblies."""
import argparse,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from model import ROOT,sha
from assembly import inventory
from export import compact,write

def transform(node,p):
    for key,v in zip(('x','y','z'),p['center_mm']):node.set(key,f'{v:.17g}*mm')
    for i in range(3):
        for j in range(3):node.set(f'a{i}{j}',format(p['frame'][j][i],'.17g'))

def export(out):
    out.mkdir(parents=True,exist_ok=True);report,m=inventory();write(out/'materials.xml',m.root);compact(report['units'],out,mode='assemblies')
    tree=ET.parse(out/'calorimeter.xml')
    for detector,u in zip(tree.getroot().find('detectors'),report['units']):
        for p in list(detector.findall('piece')):
            if p.get('owner')=='sector':detector.remove(p)
        for r in report['regions']:
            if r['unit']!=u['name']:continue
            region=ET.SubElement(detector,'region',name=r['name'])
            for p in r['parts']:
                node=ET.SubElement(region,'passive',name=p['name'],role=p['role'],material=p['material'],kind='xtru',depth=f"{p['depth_mm']:.17g}*mm");transform(node,p)
                for x,y in p['vertices_mm']:ET.SubElement(node,'vertex',x=f'{x:.17g}*mm',y=f'{y:.17g}*mm')
            for p in r['placements']:
                node=ET.SubElement(region,'placement',layer=str(p['layer']),cassette=str(p['cassette']));transform(node,p)
        for p in report['replicas']:
            if p['unit']==u['name']:
                node=ET.SubElement(detector,'replica',region=p['region'],side=str(p['side']),sector=str(p['sector']));transform(node,p)
    write(out/'calorimeter.xml',tree.getroot())
    report['execution']=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)))
    for p in (Path(__file__),ROOT/'prototypes/calorimeter/Calorimeter.cpp',ROOT/'tools/calorimeter_hardware/export.py',ROOT/'tools/pixel_barrel_dd4hep/materials.py',ROOT/'detector/config/elements.json'):report['source_sha256'][str(p.relative_to(ROOT))]=sha(p)
    (out/'expected.json').write_text(json.dumps(report,indent=2)+'\n');print('Exported',sum(x['cassettes'] for x in report['summary']),'cassettes',report['mass_g']/1e6,'tonnes');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);export(p.parse_args().output)
