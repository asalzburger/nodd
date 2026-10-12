#!/usr/bin/env python3
"""Compare validated old/new DD4hep assemblies on the same deterministic ray cohort."""
import argparse
import hashlib
import gzip
import sys
from collections import Counter
import json
from pathlib import Path


def compare(old_path, new_path):
    reports=[json.loads(p.read_text()) for p in (old_path,new_path)]
    old,new=reports
    if any(r['status']!='PASS' for r in reports):
        raise ValueError('Both assemblies must pass physical validation first')
    if any(old[k]!=new[k] for k in ('root_version','dd4hep_version','navigation_sampling')):
        raise ValueError('Control and candidate require matching runtime and sampling')
    if len(old['navigation'])!=len(new['navigation']):
        raise ValueError('Ray cohorts differ')
    rays=[]
    for a,b in zip(old['navigation'],new['navigation']):
        if any(a[k]!=b[k] for k in ('origin_mm','direction')):
            raise ValueError('Ray cohorts differ')
        rays.append(dict(origin_mm=a['origin_mm'],eta=a['eta'],phi_rad=a['phi_rad'],
            old_sensitive_crossings=a['sensitive_crossings'],new_sensitive_crossings=b['sensitive_crossings'],
            old_hits_by_layer=a['hits_by_layer'],new_hits_by_layer=b['hits_by_layer'],
            old_x_over_x0=a['x_over_x0'],new_x_over_x0=b['x_over_x0'],
            old_l_over_lambda=a['l_over_lambda'],new_l_over_lambda=b['l_over_lambda']))
    return dict(status='PASS: comparable validated inputs; geometry/material changes reported, not assumed invariant',
        report_sha256={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in zip(('old','new'),(old_path,new_path))},
        old_mass_g=old['mass_g'],new_mass_g=new['mass_g'],delta_mass_g=new['mass_g']-old['mass_g'],
        counts={k:dict(old=old['counts'].get(k,0),new=new['counts'].get(k,0)) for k in sorted(set(old['counts'])|set(new['counts']))},
        materials={k:dict(old_mass_g=old['materials'].get(k,{}).get('mass_g',0),new_mass_g=new['materials'].get(k,{}).get('mass_g',0)) for k in sorted(set(old['materials'])|set(new['materials']))},
        rays=rays,limitations='75 sparse navigation/material rays, not an acceptance or material-budget average. Different hits are expected after the human-selected packing change; use DES013 ACTS cohorts for coverage.')


def audit_source(report_path,layout_path,thickness):
    # Independent finite-plane oracle used in the ACTS layout studies. Imported
    # only for this optional check; ordinary report comparisons need no NumPy.
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'module_layout'))
    from intersections import SurfaceIndex
    import numpy as np
    layout=json.loads(gzip.decompress(layout_path.read_bytes()))
    layout['modules']=[p for p in layout['modules'] if p['subsystem']=='pixel' and p['region']=='barrel']
    index=SurfaceIndex(layout)
    report=json.loads(report_path.read_text());rays=[]
    for ray in report['navigation']:
        track=dict(origin_mm=ray['origin_mm'],eta=ray['eta'],phi=ray['phi_rad'],field_T=0.)
        hits=index.hits(track,host_radius_mm=300.,host_half_z_mm=650.,all_surfaces=True)
        def counts_of(indices):return dict(Counter(str(int(layout['modules'][i]['layer_id'].split('-B')[-1])) for i in indices))
        plane_counts=counts_of([i for i,_ in hits])
        # ROOT transports through finite silicon boxes; a grazing edge can be
        # entered even when its mid-plane crossing is just outside active bounds.
        delta=np.asarray(ray['origin_mm'])-index.centers
        near=np.full(len(index.modules),-np.inf);far=np.full(len(index.modules),np.inf)
        for axis,half in [(index.u,index.hu),(index.v,index.hv),(index.n,np.full(len(index.modules),thickness/2))]:
            offset=np.sum(delta*axis,axis=1);slope=axis@np.asarray(ray['direction'])
            parallel=np.abs(slope)<1e-14
            with np.errstate(divide='ignore',invalid='ignore'):
                a=(-half-offset)/slope;b=(half-offset)/slope
            low=np.where(parallel,-np.inf,np.minimum(a,b));high=np.where(parallel,np.inf,np.maximum(a,b))
            high=np.where(parallel & (np.abs(offset)>half),-np.inf,high)
            near=np.maximum(near,low);far=np.minimum(far,high)
        indices=np.flatnonzero((far>np.maximum(near,0)) & (near<ray['distance_mm']))
        counts=counts_of(indices)
        if counts!=ray['hits_by_layer']:
            raise ValueError(f'Finite-patch oracle differs from ROOT: {track}: {counts} != {ray["hits_by_layer"]}')
        rays.append(dict(track=track,hits_by_layer=counts,midplane_hits_by_layer=plane_counts,patch_ids=[layout['modules'][int(i)]['id'] for i in indices]))
    return dict(status='PASS',sensor_thickness_mm=thickness,method='Independent source OBB slab intersections; ideal mid-plane counts also retained to expose grazing edge clips',layout_sha256=hashlib.sha256(layout_path.read_bytes()).hexdigest(),
                oracle_sha256=hashlib.sha256((Path(__file__).resolve().parents[1]/'module_layout/intersections.py').read_bytes()).hexdigest(),rays=rays)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('old','new','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--old-layout',type=Path);p.add_argument('--new-layout',type=Path)
    p.add_argument('--sensor-thickness-mm',type=float)
    a=p.parse_args();result=compare(a.old,a.new)
    if (a.old_layout or a.new_layout) and (a.sensor_thickness_mm is None or a.sensor_thickness_mm<=0):p.error('Source audits require the configured positive --sensor-thickness-mm')
    for label,layout,report in [('old',a.old_layout,a.old),('new',a.new_layout,a.new)]:
        if layout:result[label+'_source_audit']=audit_source(report,layout,a.sensor_thickness_mm)
    result['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':main()
