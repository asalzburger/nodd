"""Extract conservative sensitive-plane RZ bounds from a DES025 expected inventory.

No passive geometry is reconstructed. The software truth region is separately
carried as a proposed planning reservation, not a verified service enclosure.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def extract(path):
    j=json.loads(path.read_text())
    hashes=dict(j['assembly_source_hashes'])
    def collect(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if isinstance(v,str) and len(v)==64 and (ROOT/k).is_file():
                    if k in hashes and hashes[k]!=v:raise ValueError('conflicting source hash: '+k)
                    hashes[k]=v
                else:collect(v)
        elif isinstance(value,list):
            for v in value:collect(v)
    collect(j['components'])
    for name,h in hashes.items():
        if digest(ROOT/name)!=h:raise ValueError('tracker source changed: '+name)
    groups={}
    for e in j['entities']:
        if e['role']!='sensitive':continue
        c=e['center_mm']; n=e['normal']; size=e['size_mm']
        if 'u' in e:u,v=e['u'],e['v']
        elif n[2]==0:u,v=[-n[1],n[0],0],[0,0,1]
        else:raise ValueError('unsupported sensor axes')
        offsets=[[sum(sign*length*axis[k]/2 for sign,length,axis in zip(signs,size,(u,v,n)))
                  for k in range(3)] for signs in itertools.product((-1,1),repeat=3)]
        corners=[[c[k]+o[k] for k in range(3)] for o in offsets]
        # Triangle inequality: conservative lower radial bound; upper from corners.
        rlo=max(0,math.hypot(*c[:2])-max(math.hypot(*o[:2]) for o in offsets))
        rhi=max(math.hypot(*q[:2]) for q in corners)
        zs=[q[2] for q in corners]
        side=0 if abs(n[2])<.5 else (1 if c[2]>0 else -1)
        key=(e['component'],e['ids']['system'],e['ids']['layer'],side)
        row=groups.setdefault(key,dict(component=key[0],system=key[1],layer=key[2],side=side,
                                      count=0,r_min_m=float('inf'),r_max_m=0,
                                      z_min_m=float('inf'),z_max_m=-float('inf')))
        row['count']+=1
        row['r_min_m']=min(row['r_min_m'],rlo/1000)
        row['r_max_m']=max(row['r_max_m'],rhi/1000)
        row['z_min_m']=min(row['z_min_m'],min(zs)/1000)
        row['z_max_m']=max(row['z_max_m'],max(zs)/1000)
    return dict(status='DRAFT; illustration bounds only',
                source='DES-025 expected.json retained local export; native evidence remains historical',
                expected_sha256=digest(path), extract_sha256=digest(Path(__file__)),
                matched_repository_source_sha256=hashes,
                total_sensitive=sum(r['count'] for r in groups.values()),
                bound_convention='Conservative triangle-inequality radial minimum; sensor-corner radial maximum and z limits; grouped bounding boxes, not passive solids.',
                groups=[groups[k] for k in sorted(groups)])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--expected',type=Path,required=True)
    a=p.parse_args();out=extract(a.expected)
    target=ROOT/'docs/validation/DES-026/tracker-rz.json'
    target.write_text(json.dumps(out,indent=2)+'\n')
    print('Extracted',out['total_sensitive'],'sensors in',len(out['groups']),'groups;',len(out['matched_repository_source_sha256']),'source/input hashes match.')
