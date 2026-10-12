#!/usr/bin/env python3
"""Native ACTS edge and aligned-seam controls on every retained complete layout."""
import argparse
import gzip
import json
import math
from pathlib import Path

from layout import barrel
from acts_validate import validate


def probes(layout):
    tracks=[]
    for z in (-11.,0.,11.):
        for j in (0,4,8,12):
            tracks.append(dict(origin_mm=[.5,.5,z],eta=0.,phi=2*math.pi*(j+.3819660112501051)/16,
                               pt_GeV=1.,field_T=0.,charge=1,cohort='common_seam_probe'))
    lids=sorted({p['layer_id'] for p in layout['modules'] if barrel(p)})
    for lid in lids:
        p=min((p for p in layout['modules'] if barrel(p) and p['layer_id']==lid and p['col']==0),key=lambda p:abs(p['center_mm'][2]))
        x,y,z=p['center_mm'];phi=math.atan2(y-.5,x-.5)
        for sign in (-1,1):
            for delta in (-.001,.001):
                tracks.append(dict(origin_mm=[.5,.5,z+sign*(p['half_v_mm']+delta)],eta=0.,phi=phi,
                                   pt_GeV=1.,field_T=0.,charge=1,cohort='1um_z_edge_probe',
                                   target_patch_id=p['id'],target_expected_hit=delta<0))
    return tracks


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--acts-source',type=Path,required=True)
    a=p.parse_args();config=json.loads(Path(__file__).with_name('config.json').read_text())
    for c in config['cases']:
        directory=a.run/c['id'];layout=json.loads(gzip.decompress((directory/'layout.json.gz').read_bytes()));tracks=probes(layout)
        report=validate(layout,tracks,directory/'acts-seams',acts_source=a.acts_source)
        for row in report['per_track']:
            t=row['input']
            if 'target_patch_id' in t and (t['target_patch_id'] in row['observed_patch_hits'])!=t['target_expected_hit']:
                raise AssertionError('Native edge membership disagrees with explicitly constructed boundary')
        if not report['passed']:raise AssertionError('Native seam audit failed')
        print(c['id'],'seam/1um bounds controls PASS',len(tracks),flush=True)

if __name__=='__main__':main()
