#!/usr/bin/env python3
"""Survey recorded material and propose finite Gen3 portal carriers; no map is installed."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import awkward as ak
import numpy as np
import uproot


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def nearest_indices(sorted_values, values):
    k = np.searchsorted(sorted_values, values)
    a = np.clip(k - 1, 0, len(sorted_values) - 1)
    b = np.clip(k, 0, len(sorted_values) - 1)
    return np.where(abs(values - sorted_values[a]) <= abs(values - sorted_values[b]), a, b)


def segment_distance(r, z, portal):
    a, b = np.asarray(portal['rz_segment_mm'], dtype=float)
    dr, dz = b - a
    t = np.clip(((r-a[0])*dr+(z-a[1])*dz)/(dr*dr+dz*dz), 0, 1)
    return np.hypot(r-a[0]-t*dr, z-a[1]-t*dz)


def ray_crossings(direction, portals):
    """Positive flight lengths from the origin, respecting finite portal bounds."""
    transverse = np.hypot(*direction[:2])
    result = []
    for i, p in enumerate(portals):
        (r1, z1), (r2, z2) = p['rz_segment_mm']
        if abs(r1-r2) < 1e-8:
            t = r1/transverse if transverse > 0 else -1
            valid = min(z1,z2)-1e-6 <= t*direction[2] <= max(z1,z2)+1e-6
        else:
            t = z1/direction[2] if direction[2] != 0 else -1
            valid = min(r1,r2)-1e-6 <= t*transverse <= max(r1,r2)+1e-6
        if valid and t >= 0:
            result.append((t, i))
    result.sort()
    return np.asarray([t for t,i in result]), np.asarray([i for t,i in result], dtype=np.int32)


def choose_carriers(s, after, crossing_s, crossing_id):
    # Coincident crossings count as both before and after. Ties use sorted
    # catalogue index, preserving deterministic native IDs.
    lo = np.searchsorted(crossing_s, s+1e-6, side='right')-1
    hi = np.searchsorted(crossing_s, s-1e-6, side='left')
    k = np.where(after, hi, lo)
    valid = (k >= 0) & (k < len(crossing_s))
    out = np.full(len(s), -1, dtype=np.int32)
    distance = np.full(len(s), np.inf)
    out[valid] = crossing_id[k[valid]]
    distance[valid] = abs(crossing_s[k[valid]]-s[valid])
    return out, distance


def pixel_after_rule(inward_facing, total_X0, downstream_X0):
    return bool(inward_facing and total_X0 > 0 and downstream_X0 > .5*total_X0)


def native_groups(geometry):
    groups = defaultdict(list)
    lookup = {}
    for sensor in geometry['sensors']:
        key = (sensor['ids']['system'], sensor['ids']['layer'])
        groups[key].append(sensor)
    out = []
    for index, (key, sensors) in enumerate(sorted(groups.items())):
        centers = np.array([s['center_mm'] for s in sensors])
        normals = np.array([s['normal'] for s in sensors])
        r = np.hypot(centers[:,0], centers[:,1])
        dot = np.sum(centers*normals,axis=1)/np.linalg.norm(centers,axis=1)
        sy, layer = key
        levels = {}
        for s in sensors:
            # Endcap normals are exactly axial in the supplied native geometry.
            z = round(s['center_mm'][2],6)
            levels.setdefault(z, set()).add(int(np.sign(s['normal'][2])))
            pieces = s['source_path'].strip('/').split('/')
            lookup[(pieces[1], pieces[2])] = index
        out.append({'index':index, 'system':sy,'layer':layer,'sensors':len(sensors),
                    'r_range_mm':[float(r.min()),float(r.max())],
                    'z_range_mm':[float(centers[:,2].min()),float(centers[:,2].max())],
                    'support_dot_outgoing_range':[float(dot.min()),float(dot.max())],
                    'z_levels':[[z,next(iter(signs)) if len(signs)==1 else 0] for z,signs in sorted(levels.items())]})
        if sy == 1 and not np.all(dot > 0):
            raise ValueError('Pixel barrel support direction is not consistently outward')
        if sy in (2,3) and not np.allclose(abs(normals[:,2]),1):
            raise ValueError('Expected axial pixel endcap normals')
    return out, lookup


def clusters(r, z, category, weight, mask, distance):
    """Connected occupied 20 mm r x 50 mm z cells, separately per component."""
    result=[]
    for component in (2,4,6):
        m=mask & (category==component)
        if not np.any(m):
            continue
        cells=np.stack([np.floor(r[m]/20).astype(int),np.floor(z[m]/50).astype(int)],axis=1)
        unique, inverse=np.unique(cells,axis=0,return_inverse=True)
        counts=np.bincount(inverse); budgets=np.bincount(inverse,weights=weight[m])
        maxima=np.zeros(len(unique));np.maximum.at(maxima,inverse,distance[m])
        todo={tuple(cell):i for i,cell in enumerate(unique)}
        while todo:
            seed=next(iter(todo)); stack=[seed]; ids=[]; coords=[]
            while stack:
                point=stack.pop()
                if point not in todo: continue
                ids.append(todo.pop(point));coords.append(point)
                for dr,dz in ((0,1),(0,-1),(1,0),(-1,0)):
                    neighbor=(point[0]+dr,point[1]+dz)
                    if neighbor in todo: stack.append(neighbor)
            a=np.array(coords)
            result.append({'component':{2:'pixel',4:'short_strip',6:'long_strip'}[component],
                           'steps':int(counts[ids].sum()),'sum_X0':float(budgets[ids].sum()),
                           'r_min_mm':int(a[:,0].min()*20),'r_max_mm':int((a[:,0].max()+1)*20),
                           'z_min_mm':int(a[:,1].min()*50),'z_max_mm':int((a[:,1].max()+1)*50),
                           'max_nearest_portal_mm':float(maxima[ids].max()),'occupied_cells':len(ids)})
    return sorted(result,key=lambda c:-c['sum_X0'])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('input','labels','geometry','output'):
        ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--near-mm',type=float,default=10.)
    ap.add_argument('--scatter-stride',type=int,default=40)
    args=ap.parse_args()
    if args.near_mm<=0 or args.scatter_stride<=0:ap.error('Positive proximity and stride required')
    args.output.mkdir(parents=True,exist_ok=True)
    geometry=json.loads(args.geometry.read_text());portals=geometry['portals']
    groups,lookup=native_groups(geometry)
    with Path(str(args.labels)+'.regions.csv').open() as stream:
        regions={int(a['region_id']):a['path'] for a in csv.DictReader(stream)}
    region_group=np.full(max(regions)+1,-1,dtype=np.int32)
    for key,path in regions.items():
        pieces=path.strip('/').split('/')
        if len(pieces)>2:
            # TGeo adds exactly one placement-copy suffix to the native name.
            region_group[key]=lookup.get((pieces[1].rsplit('_',1)[0],pieces[2].rsplit('_',1)[0]),-1)
    source=uproot.open(args.input)['material_tracks'];labels=uproot.open(args.labels)['categorized_steps']
    assert source.num_entries==labels.num_entries==100000
    fields=['v_x','v_y','v_z','v_px','v_py','v_pz','mat_x','mat_y','mat_z','mat_dx','mat_dy','mat_dz','mat_step_length','mat_X0','mat_L0','t_X0','t_L0']
    store=defaultdict(list);offsets=[0];directions=[];max_ray_residual=0.;max_dir_residual=0.;closure=[0.,0.]
    for first in range(0,source.num_entries,5000):
        a=source.arrays(fields,entry_start=first,entry_stop=first+5000)
        b=labels.arrays(entry_start=first,entry_stop=first+5000)
        n=ak.to_numpy(ak.num(a.mat_x));np.testing.assert_array_equal(n,ak.to_numpy(ak.num(b.category)));np.testing.assert_array_equal(n,ak.to_numpy(ak.num(b.region)))
        vertex=np.array([ak.to_numpy(a[k]) for k in ('v_x','v_y','v_z')]).T
        assert np.all(vertex==0),'Origin-ray survey requires zero starting vertices'
        d=np.array([ak.to_numpy(a[k]) for k in ('v_px','v_py','v_pz')]).T.astype(float);d/=np.linalg.norm(d,axis=1)[:,None]
        direction=np.repeat(d,n,axis=0);directions.extend(d)
        flat=lambda v:ak.to_numpy(ak.flatten(v)).astype(float)
        length=flat(a.mat_step_length)
        pos=np.stack([flat(a['mat_'+axis])+.5*length*flat(a['mat_d'+axis]) for axis in 'xyz'],axis=1)
        stepdir=np.stack([flat(a['mat_d'+axis]) for axis in 'xyz'],axis=1)
        max_dir_residual=max(max_dir_residual,float(np.linalg.norm(stepdir-direction,axis=1).max()))
        s=np.sum(pos*direction,axis=1)
        max_ray_residual=max(max_ray_residual,float(np.linalg.norm(pos-s[:,None]*direction,axis=1).max()))
        w=length/flat(a.mat_X0);l=length/flat(a.mat_L0)
        for iq,values in enumerate((w,l)):
            totals=np.add.reduceat(values,np.r_[0,np.cumsum(n)[:-1]])
            np.testing.assert_allclose(totals,ak.to_numpy(a[['t_X0','t_L0'][iq]]),rtol=6e-6,atol=2e-6)
            closure[iq]=max(closure[iq],float(abs(totals-ak.to_numpy(a[['t_X0','t_L0'][iq]])).max()))
        c=ak.to_numpy(ak.flatten(b.category)).astype(np.int8);reg=ak.to_numpy(ak.flatten(b.region)).astype(np.int32)
        assert np.all((c>=0)&(reg>=0));g=region_group[reg]
        for name,value in [('r',np.hypot(pos[:,0],pos[:,1])),('z',pos[:,2]),('s',s),('X0',w),('L0',l),('category',c),('region',reg),('group',g)]:store[name].append(value)
        offsets.extend(offsets[-1]+np.cumsum(n))
        print('READ',first+len(n),flush=True)
    data={k:np.concatenate(v) for k,v in store.items()};del store
    if max_ray_residual>.01 or max_dir_residual>1e-5:raise ValueError('Non-straight recording incompatible with origin-ray method')
    r,z,s,w,c,group=[data[k] for k in ('r','z','s','X0','category','group')]
    classification=json.loads(Path(str(args.labels)+'.json').read_text())
    assert classification['tracks']==source.num_entries and classification['steps']==len(s)
    assert classification['unassigned_steps']==classification['density_mismatches']==0
    expected_counts=[v['steps'] for v in classification['components'].values()]
    np.testing.assert_array_equal(np.bincount(c,minlength=8),expected_counts)
    passive=(c>0)&(c%2==0)
    ref=np.full(len(s),np.nan);inward=np.zeros(len(s),dtype=bool)
    support_stats=np.zeros((len(groups),2,2)) # group, inward, [total,after]
    # Associate passive pixel steps only with silicon actually crossed by the
    # same ray in the same native layer. Missing crossings remain unresolved.
    for begin,end,d in zip(offsets[:-1],offsets[1:],directions):
        cc=c[begin:end];gg=group[begin:end];ss=s[begin:end];zz=z[begin:end]
        assert np.all(np.diff(ss)>=-1e-3),'Material steps are not flight ordered'
        for gi in np.unique(gg[cc==3]):
            if gi<0:raise ValueError('Sensitive pixel layer missing native association')
            hits=np.flatnonzero((cc==3)&(gg==gi));points=np.flatnonzero((cc==2)&(gg==gi))
            if not len(points):continue
            hit=hits[nearest_indices(ss[hits],ss[points])]
            info=groups[gi]
            if info['system']==1:face=np.ones(len(hit),dtype=bool)
            else:
                levels=np.array(info['z_levels']);j=nearest_indices(levels[:,0],zz[hit])
                normal=levels[j,1]
                assert np.all(normal!=0),'Ambiguous native face normal'
                face=normal*d[2]>0
            inds=begin+points;ref[inds]=ss[hit];inward[inds]=face
            for f in (False,True):
                ii=inds[face==f];support_stats[gi,int(f),0]+=w[ii].sum()
                support_stats[gi,int(f),1]+=w[ii[s[ii]>ref[ii]]].sum()
    after=np.zeros(len(s),dtype=bool)
    linked=(c==2)&np.isfinite(ref)
    for gi in range(len(groups)):
        for f in (False,True):
            total,behind=support_stats[gi,int(f)]
            fraction=behind/total if total else None
            if pixel_after_rule(f,total,behind):after[(group==gi)&linked&inward]=True
        groups[gi]['passive_pixel_crossing_association']=[{'inward_facing':bool(f),'sum_X0':float(support_stats[gi,f,0]),'after_sensor_fraction_X0':float(support_stats[gi,f,1]/support_stats[gi,f,0]) if support_stats[gi,f,0] else None,'proposal':'after' if pixel_after_rule(f,*support_stats[gi,f]) else 'before'} for f in (0,1)]
    target=np.full(len(s),-1,dtype=np.int32);flight=np.full(len(s),np.nan)
    for begin,end,d in zip(offsets[:-1],offsets[1:],directions):
        t,ids=ray_crossings(d,portals);indices=begin+np.flatnonzero(passive[begin:end])
        target[indices],flight[indices]=choose_carriers(s[indices],after[indices],t,ids)
    print('ASSIGNED',flush=True)
    near=np.full(len(s),np.inf);selected=np.full(len(s),np.nan)
    for i,p in enumerate(portals):
        dist=segment_distance(r,z,p);np.minimum(near,dist,out=near)
        mm=(target==i);selected[mm]=dist[mm]
    print('DISTANCES',flush=True)
    flags=passive&(near>args.near_mm)
    selected_far=passive&((target<0)|(selected>args.near_mm))
    assignments=[]
    for i,p in enumerate(portals):
        m=(target==i)
        if not np.any(m):continue
        assignments.append({'surface_id':p['surface_id'],'geometry_id':p['geometry_id'],'steps':int(m.sum()),'sum_X0':float(w[m].sum()),'after_steps':int((m&after).sum()),'before_steps':int((m&~after).sum()),'selected_far_steps':int((m&selected_far).sum()),'near_selected_steps':int((m&~selected_far).sum()),'near_selected_sum_X0':float(w[m&~selected_far].sum()),'flight_distance_max_mm':float(flight[m].max()),'flight_distance_p50_mm':float(np.median(flight[m]))})
    flag_clusters=clusters(r,z,c,w,flags,near)
    for index,item in enumerate(flag_clusters,1):item['id']=f'F{index:03d}';item['mean_X0_per_generated_geantino']=item['sum_X0']/source.num_entries
    # Flag exact native component/child regions in addition to coarse connected
    # r-z clusters. Fit possible new carriers to ALL passive samples in each
    # flagged region, avoiding a tail-only estimate of the material location.
    remote_regions=[]
    # One grouping pass avoids rescanning all 17M steps for each native child.
    ordering=np.argsort(data['region'],kind='stable')
    ordered_regions=data['region'][ordering]
    for reg in np.unique(data['region'][flags]):
        lo,hi=np.searchsorted(ordered_regions,[reg,reg+1]);indices=ordering[lo:hi]
        indices=indices[passive[indices]];remote=indices[flags[indices]]
        ww=w[indices];rr=r[indices];zz=z[indices];total=ww.sum()
        rmean=float(np.average(rr,weights=ww));zmean=float(np.average(zz,weights=ww))
        rstd=float(np.sqrt(np.average((rr-rmean)**2,weights=ww)))
        zstd=float(np.sqrt(np.average((zz-zmean)**2,weights=ww)))
        shape='cylinder' if rstd<zstd else 'disc'
        width=min(rstd,zstd)
        remote_regions.append({'region_id':int(reg),'path':regions[int(reg)],'steps':len(indices),'flagged_steps':len(remote),
             'sum_X0':float(total),'remote_sum_X0':float(w[remote].sum()),'r_range_mm':[float(rr.min()),float(rr.max())],
             'z_range_mm':[float(zz.min()),float(zz.max())],'weighted_r_mm':rmean,'weighted_z_mm':zmean,
             'r_rms_mm':rstd,'z_rms_mm':zstd,'within_near_of_fit_fraction_X0':float(ww[abs((rr-rmean) if shape=='cylinder' else (zz-zmean))<=args.near_mm].sum()/total),'suggested_new_surface':shape if width<=args.near_mm else 'segment region first',
             'fit_status':'geometric proposal only; native volume/link insertion and held-out material replay NOT RUN'})
    remote_regions.sort(key=lambda item:-item['remote_sum_X0'])
    layer_carriers=[]
    for gi,info in enumerate(groups):
        for policy in (False,True):
            m=passive&(group==gi)&(after==policy)&~selected_far
            ids=np.unique(target[m]);counts=[{'surface_id':portals[int(i)]['surface_id'],'geometry_id':portals[int(i)]['geometry_id'],
                'steps':int(np.count_nonzero(m&(target==i))),'sum_X0':float(w[m&(target==i)].sum())} for i in ids]
            if counts:layer_carriers.append({'system':info['system'],'layer':info['layer'],'policy':'after' if policy else 'before','carriers':counts})
    sum_passive=w[passive].sum()
    summary={'schema_version':1,'status':'DRAFT first-step surface proposal; no material map installed',
             'tracks':source.num_entries,'steps':len(s),'passive_tracker_steps':int(passive.sum()),'passive_tracker_mean_X0':float(sum_passive/source.num_entries),
             'native_sensor_steps_retained':int((c%2==1).sum()),'beam_pipe_steps_retained':int((c==0).sum()),
             'near_threshold_mm':args.near_mm,'scatter_stride':args.scatter_stride,
             'pixel_passive_linked_steps':int(linked.sum()),'pixel_passive_unresolved_steps':int(((c==2)&~linked).sum()),
             'pixel_passive_unresolved_fraction_X0':float(w[(c==2)&~linked].sum()/w[c==2].sum()),
             'after_steps':int((passive&after).sum()),'before_steps':int((passive&~after).sum()),
             'no_directional_carrier_steps':int((passive&(target<0)).sum()),
             'selected_carrier_far_steps':int(selected_far.sum()),'selected_carrier_far_fraction_X0':float(w[selected_far].sum()/sum_passive),
             'far_from_any_portal_steps':int(flags.sum()),'far_from_any_portal_fraction_X0':float(w[flags].sum()/sum_passive),
             'threshold_sensitivity':[{'mm':a,'steps':int((passive&(near>a)).sum()),'fraction_passive_X0':float(w[passive&(near>a)].sum()/sum_passive)} for a in (5,10,20)],
             'checks':{'max_origin_ray_residual_mm':max_ray_residual,'max_step_direction_residual':max_dir_residual,'max_track_closure_absolute':dict(zip(('X0','L0'),closure)),'all_steps_labelled':True,'finite_portal_intersections':True},
             'groups':groups,'assignments':assignments,'layer_carriers':layer_carriers,'remote_regions':remote_regions,'flag_clusters':flag_clusters,
             'provenance':{'recording_sha256':sha(args.input),'labels_sha256':sha(args.labels),'classification_sha256':sha(str(args.labels)+'.json'),'geometry_sha256':sha(args.geometry),'survey_sha256':sha(__file__),'recording_geometry_revision':None,'recording_seed':None}}
    (args.output/'survey.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    catalog={k:geometry[k] for k in ('portals','volumes','beampipe_portals','provenance','checks')}
    catalog['sensor_groups']=groups
    (args.output/'geometry-summary.json').write_text(json.dumps(catalog,indent=2,allow_nan=False)+'\n')
    if flag_clusters:
        with (args.output/'flag-clusters.csv').open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(flag_clusters[0]),lineterminator='\n');writer.writeheader();writer.writerows(flag_clusters)
    index=np.arange(0,len(s),args.scatter_stride)
    np.savez_compressed(args.output/'scatter.npz',r=r[index],z=z[index],category=c[index],flag=flags[index],target=target[index],after=after[index])
    rz_edges=(np.arange(-4050,4050.1,10),np.arange(0,1250.1,5))
    occupancy=np.histogram2d(z,r,bins=rz_edges)[0];budget=np.histogram2d(z,r,bins=rz_edges,weights=w)[0]/source.num_entries
    np.savez_compressed(args.output/'occupancy.npz',counts=occupancy,mean_X0=budget,z_edges=rz_edges[0],r_edges=rz_edges[1])
    print(json.dumps({k:v for k,v in summary.items() if k not in ('groups','assignments','layer_carriers','remote_regions','flag_clusters','provenance')}),flush=True)


if __name__=='__main__':main()
