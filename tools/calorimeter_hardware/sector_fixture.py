"""Sparse transport fixture: sector0, all plates/frames, one cassette/layer.

Selection uses eta0.5 barrel / eta2 endcap and phi0.03. Both endcap signs remain.
This is a named test fixture, not a replacement detector configuration.
"""
import argparse,json,math,xml.etree.ElementTree as ET
from pathlib import Path
from export import write

def fixture(compact,expected,output):
    tree=ET.parse(compact);report=json.loads(expected.read_text())
    for detector in tree.getroot().find('detectors'):
        for replica in list(detector.findall('replica')):
            if replica.get('sector')!='0':detector.remove(replica)
        for region in detector.findall('region'):
            r=next(r for r in report['regions'] if r['name']==region.get('name'));selected=set()
            for layer in {p['layer'] for p in r['placements']}:
                sample=[p for p in r['placements'] if p['layer']==layer]
                def distance(p):
                    x,y,z=p['center_mm']
                    if r['kind']=='barrel':return (y-x*math.tan(.03))**2+(z-x*math.sinh(.5)/math.cos(.03))**2
                    return (x-z/math.sinh(2)*math.cos(.03))**2+(y-z/math.sinh(2)*math.sin(.03))**2
                p=min(sample,key=distance);selected.add((p['layer'],p['cassette']))
            for placement in list(region.findall('placement')):
                if (int(placement.get('layer')),int(placement.get('cassette'))) not in selected:region.remove(placement)
    write(output,tree.getroot())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compact',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();fixture(a.compact,a.expected,a.output)
