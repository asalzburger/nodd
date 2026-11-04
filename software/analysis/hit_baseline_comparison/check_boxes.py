#!/usr/bin/env python3
"""Independent finite-sensor ray intersections using native ACTS export bounds."""
import argparse
import json
from pathlib import Path

import numpy as np

from reduce import sha


def intersections(centers,axes,half,direction):
    origin=-np.einsum('sai,si->sa',axes,centers)
    local=axes@direction
    low=np.divide(-half-origin,local,out=np.full_like(local,-np.inf),where=abs(local)>1e-14)
    high=np.divide(half-origin,local,out=np.full_like(local,np.inf),where=abs(local)>1e-14)
    near=np.minimum(low,high).max(axis=1)
    far=np.maximum(low,high).min(axis=1)
    parallel=np.any((abs(local)<=1e-14)&(abs(origin)>half),axis=1)
    return (far>np.maximum(near,0))&(~parallel)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--hits',type=Path,required=True)
    ap.add_argument('--geometry',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--rays',type=int,default=256)
    args=ap.parse_args()
    data=np.genfromtxt(args.hits,delimiter=',',names=True,max_rows=args.rays)
    source=json.loads(args.geometry.read_text());s=source['sensors']
    centers=np.array([v['center_mm'] for v in s]);normals=np.array([v['normal'] for v in s])
    axes=np.stack([np.array([v['u'] for v in s]),np.array([v['v'] for v in s]),normals],axis=1)
    half=np.array([v['size_mm'] for v in s])/2
    systems=np.array([v['ids']['system'] for v in s])
    differences=[];plane_differences=[]
    for row in data:
        d=np.array([row[k] for k in ('dx','dy','dz')])
        finite=intersections(centers,axes,half,d)
        denom=normals@d
        t=np.divide(np.sum(normals*centers,axis=1),denom,out=np.full(len(s),np.inf),where=abs(denom)>1e-14)
        displacement=t[:,None]*d-centers
        plane=(t>0)&(abs(np.sum(displacement*axes[:,0],axis=1))<half[:,0])&(
            abs(np.sum(displacement*axes[:,1],axis=1))<half[:,1])
        actual=[int(row[k]) for k in ('pixel','short_strip','long_strip')]
        def counts(mask):
            return [int(np.count_nonzero(mask&np.isin(systems,ids))) for ids in ((1,2,3),(4,5),(6,7))]
        if counts(finite)!=actual:
            differences.append({'event':int(row['event_id']),'track':int(row['track_id']),
                                'finite_boxes':counts(finite),'geant4':actual})
        if counts(plane)!=actual:plane_differences.append(int(row['track_id']))
    report={'rays':len(data),'native_sensors':len(s),'finite_box_mismatches':differences,
        'zero_thickness_plane_mismatching_rays':len(plane_differences),
        'scope':'Finite sensitive-volume crossings include edge grazes that need not cross the sensor midplane; not ACTS plane-hit equivalence',
        'hits_sha256':sha(args.hits),'geometry_sha256':sha(args.geometry),'checker_sha256':sha(__file__)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    if differences:raise ValueError('Independent finite-box crossing counts differ')
    print(f"PASS: {len(data)} rays match finite sensor boxes; {len(plane_differences)} differ from zero-thickness planes")


if __name__=='__main__':main()
