"""Audit actual ACTS boundary events; no trajectory or hit fabrication."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.muon_layout import geometry as geo
from tools.muon_layout.acts.prepare import configuration,save,sha

HIT_DTYPE=np.dtype([('track_id','i8'),('sequence','i4'),('panel_index','i4'),('face_index','i2'),
                   ('is_large','?'),('geometry_id','u8'),('x_m','f8'),('y_m','f8'),('z_m','f8'),
                   ('path_m','f8'),('dx','f8'),('dy','f8'),('dz','f8')])


def read_hits(path):
    def rows():
        with Path(path).open(newline='') as f:
            for row in csv.DictReader(f):
                yield tuple(int(row[k]) if HIT_DTYPE[k].kind in 'iu' else bool(int(row[k])) if HIT_DTYPE[k].kind=='b' else float(row[k]) for k in HIT_DTYPE.names)
    return np.fromiter(rows(),dtype=HIT_DTYPE)


def face_catalog(path,panels,tol=1e-7):
    """Match ACTS faces to independent source halfspaces and validate all IDs."""
    result={};ids=set();max_plane=0.;expected=6*len(panels)
    with Path(path).open(newline='') as f:
        for row in csv.DictReader(f):
            j,k=int(row['panel_index']),int(row['face_index']);ident=int(row['geometry_id'])
            if (j,k) in result or ident in ids:raise ValueError('duplicate native face/64-bit ID')
            body=panels[j];n,b=geo.planes3(body)
            centre=np.array([float(row[x+'_m']) for x in ['cx','cy','cz']]);normal=np.array([float(row[x]) for x in ['nx','ny','nz']])
            residual=abs(n@centre-b);which=int(np.argmin(residual));max_plane=max(max_plane,float(residual[which]))
            if residual[which]>tol or abs(abs(n[which]@normal)-1)>1e-9:raise ValueError('ACTS face differs from source plane')
            if not geo.contains(body,centre[None,:])[0]:raise ValueError('ACTS face centre outside source prism')
            large=which>=4
            if large!=bool(int(row['is_large'])):raise ValueError('native large-face classification differs')
            result[j,k]=dict(plane=which,normal=n[which],bound=b[which],large=large,id=ident,station=body['station'])
            ids.add(ident)
    if len(result)!=expected or len(ids)!=expected:raise ValueError('native face count mismatch')
    for j in range(len(panels)):
        if {x['plane'] for (p,_),x in result.items() if p==j}!=set(range(6)):raise ValueError('not six distinct source faces')
    return result,dict(native_faces=len(result),unique_64bit_ids=len(ids),max_plane_residual_m=max_plane)


def count_events(events,face_info,border_flags,tol=2e-6):
    """Literal unique faces and contiguous same-chamber paired station proxies.

    Face normals are outward source normals. Repeated reports at one root are
    numerical duplicates; later visits remain separate physical events.
    """
    large=set();active_large=set();paired=set();active_paired=set();visits={};seen_visits={}
    duplicates=0;reentries=0;side=0;orphans=0;touches=0;last={}
    keep=[]
    for i,event in enumerate(events):
        p,k=int(event['panel_index']),int(event['face_index']);key=(p,k);info=face_info[key]
        point=np.array([event[x+'_m'] for x in ['x','y','z']]);path=float(event['path_m'])
        old=last.get(key)
        if old is not None and abs(path-old[0])<=tol and np.linalg.norm(point-old[1])<=tol:
            duplicates+=1;continue
        last[key]=(path,point);keep.append(i)
        active=bool(border_flags[i]);is_large=info['large']
        if is_large:
            large.add(key)
            if active:active_large.add(key)
        else:side+=1
        direction=np.array([event[x] for x in ['dx','dy','dz']]);sense=float(direction@info['normal'])
        if abs(sense)<1e-10:touches+=1;continue
        if sense<0:
            if p in visits:orphans+=1
            if seen_visits.get(p,0):reentries+=1
            seen_visits[p]=seen_visits.get(p,0)+1
            visits[p]=(info['plane'],is_large,active)
        else:
            entry=visits.pop(p,None)
            if entry is None:orphans+=1;continue
            if entry[1] and is_large and entry[0]!=info['plane']:
                paired.add(info['station'])
                if entry[2] and active:active_paired.add(info['station'])
    return dict(outer_unique_faces=len(large),active_unique_faces=len(active_large),
                outer_paired_stations=len(paired),active_paired_stations=len(active_paired),
                numerical_duplicates=duplicates,reentries=reentries,side_events=side,
                orphan_transitions=orphans,open_visits=len(visits),tangent_events=touches,
                keep_indices=np.array(keep,dtype=int))


def _availability(passed,incomplete,weights):
    total=weights.sum();low=float(weights[passed].sum()/total)
    high=float(weights[passed|incomplete].sum()/total)
    n=len(passed)
    return dict(proven_lower_fraction=low,possible_upper_fraction=high,
                proven_tracks=int(passed.sum()),unqualified_below_threshold=int((incomplete&~passed).sum()),
                binomial_standard_error_lower=(float(np.sqrt(low*(1-low)/n))
                    if np.allclose(weights,weights[0],rtol=1e-12,atol=0) else None),
                scope='upper-lower is unfinished-event uncertainty, not a statistical confidence band')


def summarize(c,tracks):
    cases=[]
    for p in c['momentum_GeV']:
        for q in c['charge_e']:
            case=dict(momentum_GeV=p,charge=q,samples={})
            for kind,label in [(0,'eta_display'),(1,'full_sphere')]:
                take=(tracks['momentum_GeV']==p)&(tracks['charge']==q)&(tracks['sample']==kind)
                w=tracks['solid_angle_weight_sr'][take];bad=tracks['incomplete'][take]
                stats=dict(tracks=int(take.sum()),weight_sr=float(w.sum()),
                           incomplete_tracks=int(bad.sum()),statuses={str(k):int(v) for k,v in zip(*np.unique(tracks['status'][take],return_counts=True))})
                for field,threshold in [('outer_unique_faces',6),('active_unique_faces',6),('outer_paired_stations',3),('active_paired_stations',3)]:
                    stats[field]=_availability(tracks[field][take]>=threshold,bad,w)
                stats['orphan_transitions']=int(tracks['orphan_transitions'][take].sum())
                stats['reentries']=int(tracks['reentries'][take].sum())
                case['samples'][label]=stats
            cases.append(case)
    return cases


def analyze(work,run,output):
    c=configuration();work,run,output=Path(work),Path(run),Path(output);output.mkdir(parents=True,exist_ok=True)
    with np.load(work/'primaries.npz',allow_pickle=False) as f:data=dict(f)
    panels=json.loads((ROOT/c['geometry']).read_text())['panels'];catalog,geocheck=face_catalog(run/'geometry.csv',panels)
    hits=read_hits(run/'hits.csv');N=len(data['track_id'])
    status=np.full(N,'missing','U64');error=np.full(N,'','U256');steps=np.zeros(N,'i4');final=np.full((N,3),np.nan);path=np.zeros(N)
    native_corrections=np.zeros(N,'i4');guard_caps=np.zeros(N,'i4');parallel_ambiguities=np.zeros(N,'i4');min_guard=np.full(N,np.nan)
    seen=set()
    with (run/'tracks.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            i=int(row['track_id'])
            if i in seen or not 0<=i<N:raise ValueError('duplicate/unknown native track')
            seen.add(i);status[i]=row['status'];error[i]=row['error'];steps[i]=int(row['steps']);path[i]=float(row['path_m'])
            final[i]=[float(row[x+'_m']) for x in ['x','y','z']]
            native_corrections[i]=int(row['native_corrections']);guard_caps[i]=int(row['guard_caps']);parallel_ambiguities[i]=int(row['parallel_ambiguities'])
            if row['min_guard_m']:min_guard[i]=float(row['min_guard_m'])
    if len(seen)!=N:raise ValueError('generated track denominator not retained')
    if len(hits) and (np.any(np.diff(hits['track_id'])<0) or hits['track_id'].min()<0 or hits['track_id'].max()>=N):raise ValueError('unordered/unknown hit track')
    xyz=np.column_stack([hits[x+'_m'] for x in ['x','y','z']]);active=np.zeros(len(hits),bool)
    residual=np.zeros(len(hits));finite_excess=np.zeros(len(hits));station=np.zeros(len(hits),'i1')
    tol=max(10*c['surface_tolerance_m'],1e-5)
    for j,body in enumerate(panels):
        ids=np.flatnonzero(hits['panel_index']==j)
        if not len(ids):continue
        points=xyz[ids];n,b=geo.planes3(body);local=(points-body['origin_m'])@np.asarray(body['basis']);pn,pb=geo.polygon_planes(body['vertices_m'])
        active[ids]=(local[:,:2]@pn.T<=pb-c['active_border_m']+c['surface_tolerance_m']).all(axis=1)
        finite_excess[ids]=np.maximum(0,(points@n.T-b).max(axis=1));station[ids]=body['station']
        for face in range(6):
            ii=ids[hits['face_index'][ids]==face]
            if not len(ii):continue
            info=catalog[j,face];residual[ii]=abs(xyz[ii]@info['normal']-info['bound'])
            if not np.all(hits['geometry_id'][ii]==info['id']) or not np.all(hits['is_large'][ii]==info['large']):raise ValueError('native face ownership/ID changed')
    if not np.isfinite(xyz).all() or (len(hits) and max(residual.max(),finite_excess.max())>tol):raise ValueError('native boundary position/finite bounds failed')
    keys=['outer_unique_faces','active_unique_faces','outer_paired_stations','active_paired_stations','numerical_duplicates','reentries','side_events','orphan_transitions','open_visits','tangent_events']
    counters={k:np.zeros(N,'i4') for k in keys};offset=np.searchsorted(hits['track_id'],np.arange(N+1));clean=np.zeros(len(hits),bool)
    for i in range(N):
        lo,hi=offset[i:i+2];ev=hits[lo:hi]
        if len(ev)>1 and np.any(np.diff(ev['path_m'])< -2*tol):raise ValueError('nonmonotonic native path')
        value=count_events(ev,catalog,active[lo:hi],2*c['surface_tolerance_m'])
        for k in keys:counters[k][i]=value[k]
        clean[lo+value['keep_indices']]=True
    completed=np.isin(status,['completed','returned_to_entrance'])
    nav_uncertain=(counters['orphan_transitions']>0)|(completed&(counters['open_visits']>0))|(parallel_ambiguities>0)
    data.update(counters,status=status,error=error,steps=steps,final_position_m=final,path_m=path,
                native_corrections=native_corrections,guard_caps=guard_caps,parallel_ambiguities=parallel_ambiguities,min_guard_step_m=min_guard,
                navigation_unqualified=nav_uncertain,incomplete=(~completed)|nav_uncertain)
    np.savez_compressed(output/'tracks.npz',**data)
    h={k:hits[k] for k in hits.dtype.names};h.update(active=active,station=station,numerical_unique_event=clean,
                                                     plane_residual_m=residual,finite_excess_m=finite_excess)
    np.savez_compressed(output/'hits.npz',**h)
    summary=dict(configuration=c,cases=summarize(c,data),native_metadata=json.loads((run/'metadata.json').read_text()),
        audit=dict(**geocheck,tracks=N,raw_boundary_hits=len(hits),unique_crossing_events=int(clean.sum()),
                   max_plane_residual_m=float(residual.max()) if len(hits) else 0.,
                   max_finite_face_excess_m=float(finite_excess.max()) if len(hits) else 0.,
                   orphan_transitions=int(counters['orphan_transitions'].sum()),
                   parallel_tolerance_ambiguities=int(parallel_ambiguities.sum()),
                   navigation_unqualified_tracks=int(nav_uncertain.sum())),
        inputs=dict(geometry_sha256=c['geometry_sha256'],map_sha256=c['map_sha256'],primaries_sha256=sha(work/'primaries.npz'),
                    raw_hits_sha256=sha(run/'hits.csv'),raw_tracks_sha256=sha(run/'tracks.csv')),
        artifacts={name:sha(output/name) for name in ['tracks.npz','hits.npz']},
        scope='native ACTS vacuum boundary-event proxies; all failures remain in generated denominators; no efficiency or physical threshold certification')
    save(output/'summary.json',summary)
    print(json.dumps(summary['audit'],indent=2))
    return data,h,summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();analyze(a.work,a.run,a.output)
