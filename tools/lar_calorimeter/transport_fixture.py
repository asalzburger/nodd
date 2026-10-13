"""Small barrel transport fixture: two complete adjacent physical periods.

This proves saved sensitive hits/readout machinery, not whole-barrel transport.
"""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from barrel_geometry import point_on_gap, sha

def fixture(compact,expected,output):
    r=json.loads(expected.read_text());tree=ET.parse(compact);d=tree.getroot().find('detectors/detector')
    for node in list(d):
        if node.tag=='piece' or (node.tag=='replica' and int(node.get('plane')) not in (0,1)):d.remove(node)
    ET.indent(tree);tree.write(output,encoding='utf-8',xml_declaration=True)
    piece=next(p for p in r['pieces'] if p.get('gap')==0 and p['layer']==5)
    a=piece['clip_annulus_mm'];point=point_on_gap(piece,(a['rmin']+a['rmax'])/2)+[0.]
    normal=piece['lower_face'][0]+[0.]
    metadata=dict(scope='Two retained full physical periods, no cryostat/services; muon begins inside layer5 gap. No full assembly/response result.',
        position_mm=point,direction=normal,compact_sha256=sha(compact),expected_sha256=sha(expected),fixture_sha256=sha(output),selector_sha256=sha(__file__))
    output.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n');return metadata

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compact',type=Path,required=True);p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(fixture(a.compact,a.expected,a.output)))
