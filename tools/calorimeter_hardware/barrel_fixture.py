"""Three bounded one-board barrel fixtures for saved Geant4 hit checks."""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from export import write
from model import sha


def fixtures(directory):
    e=json.loads((directory/'expected.json').read_text());r=e['layout_report'];results=[]
    for name,layer,sector,target_z,seed in [('central',0,0,0,45),('positive',18,3,1000,46),('negative',47,11,-2000,47)]:
        q=r['layers'][layer];m=min(q['modules'],key=lambda m:abs(m['center_mm'][1]-target_z)+abs(m['center_mm'][0]));tree=ET.parse(directory/'calorimeter.xml');det=tree.getroot().find('detectors/detector');region_name=f'barrel_layer{layer}'
        for region in list(det.findall('region')):
            if region.get('name')!=region_name:det.remove(region);continue
            for node in list(region.findall('board_instance')):
                if int(node.get('module'))!=m['index']:region.remove(node)
        for node in list(det.findall('replica')):
            if node.get('region')!=region_name or int(node.get('sector'))!=sector:det.remove(node)
        path=directory/(name+'-fixture.xml');write(path,tree.getroot());sign=-1 if m['center_mm'][1]<0 else 1;local=[q['front_mm']+r['ecal']['absorber_mm']+r['ecal']['sensor_center_z_mm'],m['center_mm'][0]+sign*2.75,m['center_mm'][1]+sign*2.75];phi=sector*2*math.pi/16;point=[local[0]*math.cos(phi)-local[1]*math.sin(phi),local[0]*math.sin(phi)+local[1]*math.cos(phi),local[2]];norm=math.sqrt(sum(x*x for x in point));results.append(dict(name=name,layer=layer,sector=sector,module=m['index'],expected_cell_xy=[0,0],target_mm=point,direction=[x/norm for x in point],seed=seed,compact_sha256=sha(path)))
    output=dict(scope='Three single-board/single-layer material-retaining fixtures; not complete detector transport.',fixtures=results,selector_sha256=sha(__file__),full_compact_sha256=sha(directory/'calorimeter.xml'),expected_sha256=sha(directory/'expected.json'));(directory/'fixtures.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2));return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);fixtures(p.parse_args().directory)
