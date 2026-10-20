#!/usr/bin/env python3
"""BO-P1 exact-revision read-only artifact audit. Requires NumPy; never imports repo code.

python3 -B /private/tmp/pr90-BO-P1-check.py --repo REPO --revision FULL_SHA --output RESULT.json
Only RESULT.json is written. Inputs are read with git show, including binary artifacts.
The recorded native trajectory is audited; no ACTS, field solve, or response study runs.
"""
import argparse, collections, csv, hashlib, io, itertools, json, math, re, struct, subprocess, time, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np

S = 'docs/validation/DES-040/barrel-overlap-2026-10-20'
B = 'docs/validation/DES-040/refined-wheels-2026-10-20/candidate/geometry.json'

def sha(b): return hashlib.sha256(b).hexdigest()
def fp(x): return sha(json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())
def corners(p):
    v=np.asarray(p['vertices_m']); h=p['depth_m']/2
    return np.array([[x,y,z] for z in (-h,h) for x,y in v])@np.asarray(p['basis']).T+p['origin_m']
def polyplanes(v):
    v=np.asarray(v); e=np.roll(v,-1,axis=0)-v; n=np.c_[e[:,1],-e[:,0]]
    n/=np.linalg.norm(n,axis=1)[:,None]
    return n,np.einsum('ij,ij->i',n,v)
def planes(p):
    q=np.asarray(p['basis']); o=np.asarray(p['origin_m']); n,b=polyplanes(p['vertices_m'])
    w=n@q[:,:2].T; n3=np.vstack((w,q[:,2],-q[:,2]))
    return n3,np.r_[b+w@o,q[:,2]@o+p['depth_m']/2,-q[:,2]@o+p['depth_m']/2]
def area(p):
    v=np.asarray(p['vertices_m']); w=np.roll(v,-1,axis=0); return float((v[:,0]*w[:,1]-v[:,1]*w[:,0]).sum()/2)
def inside(p, xyz, border=0):
    loc=(xyz-np.asarray(p['origin_m']))@np.asarray(p['basis']); n,b=polyplanes(p['vertices_m'])
    return (loc[:,:2]@n.T<=b-border+1e-10).all(axis=1)&(abs(loc[:,2])<=p['depth_m']/2+1e-10)
def full_depth(panels,d,border):
    """Independent barrel rectangle calculation: intersect both radial faces.

    Work in physical tangent/z ranges from actual geometry. No midplane/proxy
    function from the implementation is called. Same chamber must contain both ends.
    """
    ans=np.zeros((len(d),3),bool)
    for p in panels:
        if p['kind']!='barrel': continue
        q=np.asarray(p['basis']); o=np.asarray(p['origin_m']); v=np.asarray(p['vertices_m'])
        dn=d[:,0]*q[0,2]+d[:,1]*q[1,2]+d[:,2]*q[2,2]
        dt=d[:,0]*q[0,0]+d[:,1]*q[1,0]+d[:,2]*q[2,0]
        dz=d[:,0]*q[0,1]+d[:,1]*q[1,1]+d[:,2]*q[2,1]
        good=dn>1e-12
        for offset in (-p['depth_m']/2,p['depth_m']/2):
            distance=np.divide(o@q[:,2]+offset,dn,out=np.full(len(d),np.inf),where=abs(dn)>1e-12)
            tx=distance*dt-o@q[:,0]; zz=distance*dz-o@q[:,1]
            good &= (distance>0)&(tx>=v[:,0].min()+border-1e-12)&(tx<=v[:,0].max()-border+1e-12)&(zz>=v[:,1].min()+border-1e-12)&(zz<=v[:,1].max()-border+1e-12)
        ans[:,p['station']-1]|=good
    return ans
def bank(n):
    r=np.random.default_rng(906320); mu=r.uniform(0,np.tanh(1.),n); ph=r.uniform(0,2*np.pi,n)
    d=np.c_[np.sqrt(1-mu*mu)*np.cos(ph),np.sqrt(1-mu*mu)*np.sin(ph),mu]
    return np.r_[d,d*[1,1,-1]]
def mesh(p):
    v=corners(p); n,_=planes(p); edges=np.vstack((v[1:4]-v[:3],v[0]-v[3],v[4]-v[0]))
    return (v,n,edges,v.min(axis=0),v.max(axis=0))
def conflict(a,b):
    av,an,ae,al,ah=a;bv,bn,be,bl,bh=b
    axes=np.vstack((an,bn,np.cross(ae[:,None,:],be[None,:,:]).reshape(-1,3)))
    size=np.linalg.norm(axes,axis=1); axes=axes[size>1e-12]/size[size>1e-12,None]
    pa=av@axes.T;pb=bv@axes.T
    return not np.any((pa.max(axis=0)<pb.min(axis=0)-1e-10)|(pb.max(axis=0)<pa.min(axis=0)-1e-10))
def expanded(p,margin):
    n,b=polyplanes(p['vertices_m']); b+=margin
    return dict(p,depth_m=p['depth_m']+2*margin,vertices_m=[np.linalg.solve(np.stack((n[i-1],n[i])),[b[i-1],b[i]]).tolist() for i in range(4)])

def run(args):
    started=time.time(); repo=Path(args.repo).resolve(); rev=args.revision
    if not re.fullmatch('[0-9a-f]{40}',rev): raise ValueError('A full commit SHA is required')
    checks=[]; inputs={}; errors=[]
    def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
    assert git('rev-parse',rev+'^{commit}').decode().strip()==rev
    def read(p,revision=rev):
        b=git('show',revision+':'+p)
        if revision==rev:inputs[p]=dict(sha256=sha(b),bytes=len(b))
        return b
    def js(p):return json.loads(read(p))
    def rows(p):return list(csv.DictReader(io.StringIO(read(p).decode())))
    def check(name,ok,details=None):
        checks.append(dict(name=name,passed=bool(ok),details=details))
        if not ok:errors.append(name)
    g=js(S+'/candidate/geometry.json'); base=js(B); c=js(S+'/candidate/geometry-controls.json')
    cfg=js('tools/muon_layout/barrel-overlap-config.json'); panels=g['panels']; bar=[p for p in panels if p['kind']=='barrel']
    artifacts=js(S+'/artifacts.json'); val=js(S+'/native-validation/validation.json'); views=js(S+'/views/views.json')
    check('fixed_magnetic_support_endcap_geometry',g['magnetic_configuration']==base['magnetic_configuration'] and g['supports']==base['supports'] and [p for p in panels if p['kind']=='endcap']==[p for p in base['panels'] if p['kind']=='endcap'])
    check('base_and_geometry_sha256',inputs[B]['sha256']==cfg['base_geometry_sha256']==artifacts['baseline_geometry_sha256'] and inputs[S+'/candidate/geometry.json']['sha256']==artifacts['geometry_sha256']==val['geometry_sha256'])
    fixed=dict(magnetic_configuration=fp(g['magnetic_configuration']),supports=fp(g['supports']),endcaps=fp([p for p in panels if p['kind']=='endcap']))
    check('fixed_interface_fingerprints',fixed==cfg['fixed_interface_sha256'],fixed)
    counts={kind:{str(st):sum(p['kind']==kind and p['station']==st for p in panels) for st in (1,2,3)} for kind in ('barrel','endcap')}
    check('actual_counts_and_unique_ids',len(panels)==888 and len({p['id'] for p in panels})==888 and len(bar)==696 and counts==c['counts'],counts)
    sizes={}; dims_before=0
    for st in (1,2,3):
        ps=[p for p in bar if p['station']==st]; spans=np.array([np.ptp(p['vertices_m'],axis=0) for p in ps]); families=collections.Counter(tuple(np.round(s,9)) for s in spans)
        prev=[p for p in base['panels'] if p['kind']=='barrel' and p['station']==st]
        dims_before+=len(set(tuple(np.round(np.ptp(p['vertices_m'],axis=0),9)) for p in prev))
        sizes[str(st)]=dict(count=len(ps),families=len(families),minimum_width_m=float(spans[:,0].min()),z_range_m=[float(spans[:,1].min()),float(spans[:,1].max())],below_half_m=int((spans[:,0]<.5-1e-10).sum()),minimum_area_m2=min(area(p) for p in ps))
        check('actual_size_policy_B'+str(st),len(families)==c['dimensions_after'][str(st)]['dimension_family_count'] and min(area(p) for p in ps)>=.25-1e-10 and spans[:,1].min()>=.5-1e-10 and spans[:,1].max()<=4+1e-10,sizes[str(st)])
    check('family_tradeoff_7_to_13',dims_before==7 and sum(v['families'] for v in sizes.values())==13)
    radii=[]; maxr=0.;maxz=collections.defaultdict(float)
    for p in bar:
        facet=int(p['id'].split('/')[1][1:]); expected=[5.2,6.7,8.2][p['station']-1]
        if p['station']==3 and facet%2:expected=8.75
        radii.append(abs(np.linalg.norm(np.asarray(p['origin_m'])[:2])-expected)<1e-10)
        co=corners(p);maxr=max(maxr,float(np.linalg.norm(co[:,:2],axis=1).max()));maxz[str(p['station'])]=max(maxz[str(p['station'])],float(abs(co[:,2]).max()))
    check('actual_stagger_and_z_bounds',all(radii) and all(maxz[str(st)]<=[6.4456,9.2,12.5][st-1]+1e-10 for st in (1,2,3)),dict(maximum_barrel_corner_radius_m=maxr,max_z_m=dict(maxz),native_world_margin_m=9.1-maxr,map_radial_margin_m=9.5-maxr))
    d=g['barrel_overlap_dimensions']; even=d['even_half_width_m'];odd=d['odd_half_width_m']
    overlap=math.degrees(math.atan((even-.03)/8.45)+math.atan((odd-.03)/9.))-15
    sep=8.5-8.45*math.cos(math.pi/12)-even*math.sin(math.pi/12)
    check('derived_full_depth_template_overlap_and_separation',abs(overlap-.1)<1e-12 and sep>.02 and abs(sep-c['stagger_volume_checks']['separating_plane_gap_m'])<1e-12,dict(projected_overlap_deg=overlap,separating_plane_gap_m=sep))
    # Independent final-prism SAT, including barrel/endcap interactions.
    mm=[mesh(p) for p in panels];lo=np.array([m[3] for m in mm]);hi=np.array([m[4] for m in mm]);tested=0;bad=[]
    for i in range(len(mm)):
        near=np.flatnonzero(((hi[i]>=lo[i+1:]-1e-10)&(hi[i+1:]>=lo[i]-1e-10)).all(axis=1))+i+1
        for j in near:
            tested+=1
            if conflict(mm[i],mm[j]):bad.append([panels[i]['id'],panels[j]['id']])
    check('all_393828_actual_panel_pairs_disjoint',not bad,dict(total_pairs=len(panels)*(len(panels)-1)//2,aabb_candidate_sat_tests=tested,conflicts=bad))
    sm=[mesh(expanded(p,.05)) for p in g['supports']['members']];sl=np.array([p[3] for p in sm]);sh=np.array([p[4] for p in sm]);bad=[];tested=0
    for p in bar:
        bm=mesh(p);near=np.flatnonzero(((bm[4]>=sl-1e-10)&(sh>=bm[3]-1e-10)).all(axis=1))
        for j in near:
            tested+=1
            if conflict(bm,sm[j]):bad.append([p['id'],g['supports']['members'][j]['id']])
    check('all_696x484_barrel_supports_50mm_clear',not bad,dict(candidate_sat_tests=tested,conflicts=bad))
    check('retained_whole_volume_certificates_and_merge_accounting',all(p['coil_certificate']['clear'] and p['support_certificate']['clear'] and p['support_certificate']['total_members']==484 for p in bar) and sum(len(p.get('merged_from',[p['id']]))-1 for p in bar)==264 and c['max_z_seam_merging']['accepted']==264 and c['coil_certificate_cache']['historical_certificates_loaded']==0)
    source_results={}
    for label,report,field,execution in [('geometry',c,'sources',None),('artifacts',artifacts,'source_sha256',artifacts['execution_revision']),('native',val,'source_sha256',val['source_revision']),('views',views,'source_sha256',None)]:
        mismatch=[]
        for p,h in report[field].items():
            if sha(read(p))!=h:mismatch.append(p)
            if execution and sha(read(p,execution))!=h:mismatch.append('execution:'+p)
        source_results[label]=dict(paths=len(report[field]),mismatches=mismatch,execution_revision=execution)
    check('all_recorded_executed_source_hashes_match_target_and_source_freeze',not any(v['mismatches'] for v in source_results.values()),source_results)
    check('exact_current_config_embedded',g['barrel_overlap_revision']==cfg)
    fieldpath=val['unchanged_field_source'];check('retained_field_npz_hash',sha(read(fieldpath))==val['unchanged_field_npz_sha256'])
    # Finite source planes and native corners from ACTS inspector.
    nc=rows(S+'/obj/native-inspection/geometry-corners.csv');nf=rows(S+'/obj/native-inspection/geometry.csv'); faceinfo={};corner_res=0.;plane_res=0.;ids=[]
    for row in nc:
        p=panels[int(row['panel_index'])];point=np.array([float(row[k+'_m']) for k in ('x','y','z')]);corner_res=max(corner_res,float(np.linalg.norm(corners(p)-point,axis=1).min()))
    for row in nf:
        idx,k=int(row['panel_index']),int(row['face_index']);n,b=planes(panels[idx]);pt=np.array([float(row[k+'_m']) for k in ('cx','cy','cz')]);normal=np.array([float(row[k]) for k in ('nx','ny','nz')]);which=int(np.argmin(abs(n@pt-b)));plane_res=max(plane_res,float(abs(n[which]@pt-b[which])))
        assert abs(abs(n[which]@normal)-1)<1e-9
        faceinfo[idx,k]=(n[which],b[which],which,int(row['geometry_id']))
        ids.append(int(row['geometry_id']))
    check('native_5328_unique_faces_21312_corners_match_finite_source',len(nf)==5328 and len(set(ids))==5328 and len(nc)==21312 and corner_res<1e-12 and plane_res<1e-12,dict(maximum_corner_residual_m=corner_res,maximum_face_plane_residual_m=plane_res))
    native={};straight_input=None;curved_input=None
    for label,filename,nt in [('straight','straight-inputs.npz',1024),('curved-smoke','curved-inputs.npz',256)]:
        dr=S+'/native-validation/'+label
        with np.load(io.BytesIO(read(S+'/native-validation/'+filename)),allow_pickle=False) as z: data=dict(z)
        track=rows(dr+'/tracks.csv');hit=rows(dr+'/hits.csv');meta=js(dr+'/metadata.json')
        inp=np.loadtxt(io.BytesIO(read(dr+'/input.dat')),skiprows=1)
        assert np.array_equal(inp[:,0].astype(int),data['track_id']) and np.allclose(inp[:,1],data['momentum_GeV'],atol=0,rtol=0) and np.array_equal(inp[:,2],data['charge']) and np.allclose(inp[:,3:6],data['start_m'],atol=0,rtol=0) and np.allclose(inp[:,6:9],data['direction'],atol=0,rtol=0)
        if label=='straight':straight_input=data
        else:curved_input=data
        assert len(track)==nt and [int(r['track_id']) for r in track]==list(range(nt))
        assert read(dr+'/geometry.csv')==read(S+'/obj/native-inspection/geometry.csv') and read(dr+'/geometry-corners.csv')==read(S+'/obj/native-inspection/geometry-corners.csv')
        out=np.zeros((nt,3),bool);border=np.zeros_like(out);visits={};last={};maxplane=0.;maxoutside=0.;duplicates=0;orphans=0;tangent=0
        for row in hit:
            tid,idx,face=[int(row[k]) for k in ('track_id','panel_index','face_index')];p=panels[idx];xyz=np.array([float(row[k+'_m']) for k in ('x','y','z')]);direction=np.array([float(row[k]) for k in ('dx','dy','dz')]);path=float(row['path_m']);normal,bound,which,ident=faceinfo[idx,face]
            assert int(row['geometry_id'])==ident and bool(int(row['is_large']))==(which>=4)
            nn,bb=planes(p);maxoutside=max(maxoutside,float((nn@xyz-bb).max()));maxplane=max(maxplane,abs(float(normal@xyz-bound)))
            local=(xyz-p['origin_m'])@np.asarray(p['basis']);pn,pb=polyplanes(p['vertices_m']);active=bool((pn@local[:2]<=pb-.03+1e-12).all())
            key=(tid,idx,face)
            if key in last and abs(path-last[key][0])<=2e-6 and np.linalg.norm(xyz-last[key][1])<=2e-6:duplicates+=1;continue
            last[key]=(path,xyz);sense=direction@normal
            if abs(sense)<1e-10:tangent+=1;continue
            visitkey=(tid,idx)
            if sense<0:
                if visitkey in visits:orphans+=1
                visits[visitkey]=(which,active)
            else:
                prior=visits.pop(visitkey,None)
                if prior is None:orphans+=1;continue
                if p['kind']=='barrel' and which>=4 and prior[0]>=4 and which!=prior[0]:
                    out[tid,p['station']-1]=True
                    if active and prior[1]:border[tid,p['station']-1]=True
        statuses=dict(collections.Counter(r['status'] for r in track));incomplete=[int(r['track_id']) for r in track if r['status']!='completed']
        actual=dict(tracks=nt,statuses=statuses,raw_hits=len(hit),station_paired_counts=out.sum(axis=0).tolist(),border_station_paired_counts=border.sum(axis=0).tolist(),three_barrel_pairs=int(out.all(axis=1).sum()),three_border_barrel_pairs=int(border.all(axis=1).sum()),incomplete_track_ids=incomplete)
        reported=val['native_reports'][label]
        check('actual_'+label+'_events_agree_with_report',all(actual[k]==reported[k] for k in actual) and maxplane<1e-6 and maxoutside<1e-6,dict(**actual,maximum_plane_residual_m=maxplane,maximum_outside_excess_m=maxoutside,duplicate_events=duplicates,orphan_events=orphans,open_visits=len(visits),tangent_events=tangent))
        if label=='straight':
            predict=full_depth(panels,data['direction'],0);predborder=full_depth(panels,data['direction'],.03)
            check('all_1024_zero_field_native_station_crossings_match_independent_rectangles',np.array_equal(out,predict) and np.array_equal(border,predborder),dict(outline_mismatches=int((out!=predict).sum()),border_mismatches=int((border!=predborder).sum())))
            check('straight_npz_matches_fixed_seed_bank',np.array_equal(data['direction'],bank(512)))
        else:check('all_59_field_masked_curved_rows_retained',statuses=={'completed':197,'field_masked':59} and len(incomplete)==59 and np.unique(data['momentum_GeV']).tolist()==[5.,100.] and np.unique(data['charge']).tolist()==[-1,1])
        native[label]=actual
    chosen=np.r_[np.arange(32),np.arange(512,544)]
    check('curved_preselection_charge_momentum_identity',np.array_equal(curved_input['direction'],np.tile(straight_input['direction'][chosen],(4,1))) and np.array_equal(curved_input['charge'],np.repeat([-1,1,-1,1],64)) and np.array_equal(curved_input['momentum_GeV'],np.repeat([5.,5.,100.,100.],64)))
    # The published 65,536 rows are 32,768 independent random directions plus reflection.
    d=bank(32768);banks={};summaries={}
    for label,model in [('before',base),('refined',g)]:
        for b,labelb in [(0,'outline'),(.03,'border30mm')]:
            f=full_depth(model['panels'],d,b);banks[label+'_'+labelb]=f
            sums=f.sum(axis=0).tolist();all3=f.all(axis=1);count=int(all3.sum());fraction=float(all3.mean())
            item=dict(station_counts=sums,three_station_count=count,three_station_fraction=fraction,binomial_sampling_se_percentage_points=100*math.sqrt(fraction*(1-fraction)/32768))
            summaries[label+'_'+labelb]=item;report=val['geometric_bank']['results'][label+'_'+labelb]
            check('recomputed_bank_'+label+'_'+labelb,sums==report['station_counts'] and count==report['three_station_count'] and fraction==report['three_station_fraction'] and np.array_equal(f[:32768],f[32768:]),item)
    paired={}
    for metric in ('outline','border30mm'):
        x=banks['before_'+metric][:32768].all(axis=1);y=banks['refined_'+metric][:32768].all(axis=1);diff=y.astype(float)-x.astype(float)
        lost=x&~y; fail=~banks['refined_'+metric][:32768];patterns=collections.Counter(','.join(str(k+1) for k in np.flatnonzero(fail[i])) for i in np.flatnonzero(lost))
        examples=[]
        for pattern in sorted(patterns):
            sample=next(i for i in np.flatnonzero(lost) if ','.join(str(k+1) for k in np.flatnonzero(fail[i]))==pattern); ray=d[sample];details=[];inset=0 if metric=='outline' else .03
            for st in (int(v) for v in pattern.split(',')):
                old=[p['id'] for p in base['panels'] if p['kind']=='barrel' and p['station']==st and full_depth([p],ray[None,:],inset)[0,st-1]]
                nearest=None
                for p in bar:
                    if p['station']!=st:continue
                    q=np.asarray(p['basis']);o=np.asarray(p['origin_m']);den=ray@q[:,2]
                    if den<=1e-12:continue
                    vv=np.asarray(p['vertices_m']);distance=(o@q[:,2]+np.array([-.25,.25]))/den
                    local=(distance[:,None]*ray-o)@q
                    bounds=[float(vv[:,0].min()+inset),float(vv[:,0].max()-inset),float(vv[:,1].min()+inset),float(vv[:,1].max()-inset)]
                    margins=np.array([local[:,0]-bounds[0],bounds[1]-local[:,0],local[:,1]-bounds[2],bounds[3]-local[:,1]])
                    score=float(margins.min())
                    if nearest is None or score>nearest['minimum_margin_m']:
                        nearest=dict(id=p['id'],minimum_margin_m=score,limiting_edge=['tangent_low','tangent_high','z_low','z_high'][int(np.argmin(margins)//2)],face_tangent_z_m=local[:,:2].tolist(),allowed_tangent_z_m=bounds)
                details.append(dict(station=st,before_matching_panel_ids=old,nearest_after_panel=nearest))
            examples.append(dict(sample_id=int(sample),eta_abs=float(np.arctanh(ray[2])),phi_deg=float(math.degrees(math.atan2(ray[1],ray[0]))%360),missing_station_pattern=pattern,source_details=details))
        paired[metric]=dict(gained=int((y&~x).sum()),lost=int(lost.sum()),unchanged=int((x==y).sum()),improvement_percentage_points=100*float(diff.mean()),paired_sampling_se_percentage_points=100*float(diff.std(ddof=1)/math.sqrt(32768)),lost_missing_station_counts=(fail&lost[:,None]).sum(axis=0).tolist(),lost_missing_station_patterns=dict(patterns),representative_lost_rays=examples)
    # Native OBJ: actual mesh memberships, source corners, closure and materials.
    expected_sets={'chambers-and-coils':(888,36,0),'barrel-chambers':(696,0,0),'positive-endcap-chambers':(96,0,0),'toroids-and-frame':(0,36,484)}
    object_reports={};chamber_lookup={'chamber_'+re.sub('[^A-Za-z0-9_.-]','_',p['id']):p for p in panels}
    frame_lookup={'frame_'+re.sub('[^A-Za-z0-9_.-]','_',p['id']):p for p in g['supports']['members']}
    def parseobj(blob):
        vertices=[];objects={};materials=set();mtllib=[];name=None
        for line in blob.decode().splitlines():
            parts=line.split()
            if not parts:continue
            if parts[0]=='v':vertices.append([float(x) for x in parts[1:]])
            elif parts[0]=='o':name=parts[1];assert name not in objects;objects[name]=[]
            elif parts[0]=='f':objects[name].append([int(x.split('/')[0])-1 for x in parts[1:]])
            elif parts[0]=='usemtl':materials.add(parts[1])
            elif parts[0]=='mtllib':mtllib.append(parts[1])
        return np.array(vertices),objects,materials,mtllib
    for name,expected in expected_sets.items():
        v,objects,mats,libs=parseobj(read(S+'/obj/'+name+'.obj'));countsobj=tuple(sum(k.startswith(prefix) for k in objects) for prefix in ('chamber_','coil_','frame_'));closed=True;positive=True;sourceerror=0.;prismvolumeerror=0.;quads=0
        for identifier,faces in objects.items():
            quads+=len(faces); vv=np.unique(np.concatenate(faces)); center=v[vv].mean(axis=0);edges=collections.Counter();volume=0.
            for face in faces:
                assert len(face)==4
                xyz=v[face];keys=[tuple(np.rint(point/1e-9).astype(np.int64)) for point in xyz]
                for a,b in zip(keys,keys[1:]+keys[:1]):edges[(a,b)]+=1
                # A racetrack has a hole: global centroid is outside its occupied
                # material. Its consistent closed orientation is instead checked
                # with reverse edge partners and positive signed volume below.
                cross=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])
                if not identifier.startswith('coil_'):positive &= float(cross@(xyz.mean(axis=0)-center))>0
                for i in (1,2):volume+=float((xyz[0]-center)@np.cross(xyz[i]-center,xyz[i+1]-center))/6
            closed &= all(n==1 and edges[(b,a)]==1 for (a,b),n in edges.items())
            positive &= volume>0
            p=chamber_lookup.get(identifier) or frame_lookup.get(identifier)
            assert identifier.startswith('coil_') or p is not None
            if p:
                co=corners(p);sourceerror=max(sourceerror,float(np.linalg.norm(v[vv,None,:]-co[None,:,:],axis=2).min(axis=1).max()));prismvolumeerror=max(prismvolumeerror,abs(volume-area(p)*p['depth_m']))
        mtl=read(S+'/obj/'+name+'.mtl').decode();defined=set(re.findall(r'^newmtl (\S+)',mtl,re.M))
        object_reports[name]=dict(objects=len(objects),roles=countsobj,quad_faces=quads,raw_vertices=len(v),closed=closed,outward=positive,maximum_source_corner_error_m=sourceerror,maximum_prism_volume_error_m3=prismvolumeerror)
        check('actual_mesh_'+name,countsobj==expected and closed and positive and sourceerror<1e-12 and prismvolumeerror<1e-10 and mats==defined and libs==[name+'.mtl'] and len(objects)==artifacts['checks'][name]['objects'],object_reports[name])
    for name,meta in artifacts['zip_checks'].items():
        raw=read(S+'/obj/'+name)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            check('actual_zip_'+name,sha(raw)==meta['sha256'] and z.namelist()==meta['member_names'] and all(z.read(p)==read(S+'/obj/'+p) for p in z.namelist()))
    hashbad=[];hashcount=0
    for bundle,files in artifacts['obj_artifacts'].items():
        for p,h in files.items():
            hashcount+=1
            if sha(read(S+'/obj/'+p))!=h:hashbad.append(p)
    for p,h in artifacts['barrel_view_artifacts'].items():
        hashcount+=1
        if sha(read(S+'/views/'+p))!=h:hashbad.append(p)
    check('actual_obj_preview_and_view_artifact_sha256',not hashbad,dict(paths=hashcount,mismatches=hashbad))
    view_counts={};rng=np.random.default_rng(906321);probes=rng.uniform(-10,10,(50000,2));xyz=np.c_[probes,np.full(len(probes),views['section_z_m'])]
    for label,model in [('before',base),('after',g)]:
        selected=[p for p in model['panels'] if p['kind']=='barrel' and corners(p)[:,2].min()-1e-12<=views['section_z_m']<=corners(p)[:,2].max()+1e-12]; recorded=views['cuts'][label];show=np.zeros(len(probes),bool);actual=np.zeros(len(probes),bool)
        expectedids={p['id'] for p in selected};error=0.
        for p in selected:actual|=inside(p,xyz)
        for cut in recorded:
            p=next(p for p in selected if p['id']==cut['id']);v=corners(p);v=v[np.argsort(v[:,2])[:4],:2];shown=np.asarray(cut['xy_m']);error=max(error,float(np.linalg.norm(shown[:,None,:]-v[None,:,:],axis=2).min(axis=1).max()));pn,pb=polyplanes(shown);show|=(probes@pn.T<=pb+1e-12).all(axis=1)
        chosen=[p for p in model['panels'] if p['kind']=='barrel' and abs((p['compartment']['phi_deg']-15+180)%360-180)<1e-8]
        long=views['longitudinal'][label];longmap={p['id']:p for p in long};longok={p['id'] for p in chosen}==set(longmap) and all(p['vertices_m']==longmap[p['id']]['vertices_tangent_z_m'] for p in chosen)
        view_counts[label]=dict(cuts=len(recorded),longitudinal=len(long),maximum_cut_corner_error_m=error,membership_mismatches=int((show!=actual).sum()))
        # draw.section_polygon explicitly rounds section vertices to 10 decimal
        # places. 1e-10 m accommodates that display encoding, not a physics gate.
        check('actual_view_source_membership_'+label,{p['id'] for p in recorded}==expectedids and error<1e-10 and np.array_equal(show,actual) and longok,view_counts[label])
    for p in ('barrel-cross-sections','longitudinal-packing'):
        png=read(S+'/views/'+p+'.png');svg=read(S+'/views/'+p+'.svg');root=ET.fromstring(svg);text=svg.decode()
        check('final_png_svg_'+p,png[:8]==b'\x89PNG\r\n\x1a\n' and 'DRAFT PROTOTYPE' in text,dict(png_dimensions=struct.unpack('>II',png[16:24]),svg_elements=sum(1 for _ in root.iter())))
    prior=js(S+'/prior-evidence-identity.json');oldrev=prior['baseline_revision'];mismatches=[];oldpaths={}
    for line in git('ls-tree','-r',oldrev).decode().splitlines():
        header,path=line.split('\t',1)
        if any(path.startswith(pref) for pref in prior['scope']):oldpaths[path]=header.split()[2]
    newtree={line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in git('ls-tree','-r',rev).decode().splitlines()}
    manifest={v['path']:v['sha256'] for v in prior['files']}
    for p,oid in oldpaths.items():
        if newtree.get(p)!=oid or sha(read(p))!=manifest.get(p):mismatches.append(p)
    check('all_449_prior_blob_identities_and_sha256',len(oldpaths)==449 and set(oldpaths)==set(manifest) and not mismatches,dict(baseline_revision=oldrev,paths=len(oldpaths),mismatches=mismatches))
    return dict(assignment='BO-P1',role='PhysVal explicit fallback',reviewed_revision=rev,passed=not errors,failed_checks=errors,checks=checks,geometric_bank=summaries,paired_sampling=paired,native=native,sizes=sizes,view_counts=view_counts,meshes=object_reports,inputs=inputs,runtime_seconds=time.time()-started,limits=['Artifact/source audit only; no ACTS rerun, field solve, response, material or reconstruction measurement.','Independent full-depth rectangle, convex SAT, finite event/mesh checks; retained adaptive coil certificate values inspected but coil distance kernel not independently rerun.','32768 iid directions plus mirrored partners; sampling errors are conditional MC precision and exclude design/response uncertainty.','No human engineering acceptance or design sign-off.'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True);p.add_argument('--revision',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=run(a);Path(a.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:result[k] for k in ('assignment','reviewed_revision','passed','failed_checks','runtime_seconds')},indent=2));raise SystemExit(0 if result['passed'] else 1)
