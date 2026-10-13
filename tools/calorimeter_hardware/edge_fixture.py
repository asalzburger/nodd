"""Small single-layer custom-module fixture for Geant4/readout smoke checks."""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from export import write


def fixture(directory):
    report=json.loads((directory/'expected.json').read_text());module=next(m for m in report['modules'] if not m['full'] and m['grid'][0]==0);pad=max(module['pads'],key=lambda q:q['area_mm2']);tree=ET.parse(directory/'calorimeter.xml');det=tree.getroot().find('detectors/detector')
    for region in list(det.findall('region')):
        if region.get('name')=='edge_frame':det.remove(region);continue
        for p in list(region.findall('piece')):
            if p.get('name').startswith('edge_m') and not p.get('name').startswith(f"edge_m{module['index']}_"):region.remove(p)
    for replica in list(det.findall('replica')):
        if replica.get('region')!='edge_layer' or replica.get('sector')!='0' or replica.get('layer')!='0':det.remove(replica)
    write(directory/'edge-fixture.xml',tree.getroot());x=module['center_mm'][0]+pad['reference_mm'][0];y=module['center_mm'][1]+pad['reference_mm'][1];z=report['layout_report']['front_mm']+2.5;norm=math.sqrt(x*x+y*y+z*z)
    directions={name:[x/norm,sign*y/norm,sign*z/norm] for name,sign in (('positive',1),('negative',-1))}
    result=dict(status='sparse Geant4 fixture, not full-detector transport',module=module['index'],family=module['family'],expected_cell_xy=pad['key'],target_mm=[x,y,z],directions=directions);(directory/'fixture.json').write_text(json.dumps(result,indent=2)+'\n');print(result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);fixture(p.parse_args().directory)
