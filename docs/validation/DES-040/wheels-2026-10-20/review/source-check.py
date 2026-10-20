#!/usr/bin/env python3
"""Read-only checks of frozen wheel source/inputs. No repository imports or ACTS.
Uses git show, Python stdlib and NumPy. Subject functions are isolated with AST
for controls; independent expectations and geometry SAT are implemented here.
"""
import argparse, ast, hashlib, io, itertools, json, math, subprocess, tempfile
from pathlib import Path
import numpy as np
REV='22a3f8c113a276b1321adeb9b994107594eb3c7d'
D='docs/validation/DES-040/wheels-2026-10-20/'

def main(repo, revision):
    hashes={}; cache={}
    def raw(p):
        if p not in cache:
            cache[p]=subprocess.check_output(['git','-C',str(repo),'show',revision+':'+p]);hashes[p]=hashlib.sha256(cache[p]).hexdigest()
        return cache[p]
    def obj(p): return json.loads(raw(p))
    def functions(p,names,ns=None):
        env={'np':np,'math':math,'Path':Path,'json':json,'hashlib':hashlib};env.update(ns or {})
        tree=ast.parse(raw(p).decode());nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.Assign)) and (getattr(n,'name',None) in names)]
        assert len(nodes)==len(names),(p,names)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),p,'exec'),env);return env
    conf=obj('tools/muon_layout/wheels-config.json'); g=obj(D+'candidate/geometry.json');base=obj('docs/validation/DES-040/geometry.json')
    mag=obj(D+'magnetic/configuration.json'); energy=obj(D+'magnetic/energy.json'); cold=obj(D+'magnetic/cold.json'); geomctrl=obj(D+'candidate/geometry-controls.json')
    panels=g['panels']; members=g['supports']['members']; source=mag['configuration']; oldsource=mag['baseline_configuration']
    # Independently assemble vertices, face normals, edge directions and conservative
    # face-offset prism envelopes; then use full convex polyhedron SAT.
    def poly(body,margin=0):
        v=np.asarray(body['vertices_m'],float);Q=np.asarray(body['basis'],float);O=np.asarray(body['origin_m']);h=body['depth_m']/2+margin
        edges=np.roll(v,-1,axis=0)-v;n=np.c_[edges[:,1],-edges[:,0]];n/=np.linalg.norm(n,axis=1)[:,None];b=(n*v).sum(axis=1)
        if margin:v=np.array([np.linalg.solve(np.vstack((n[i-1],n[i])),[b[i-1]+margin,b[i]+margin]) for i in range(4)])
        vertices=np.vstack([np.c_[v,np.full(4,z)] for z in [-h,h]])@Q.T+O
        normals=np.vstack((n@Q[:,:2].T,Q[:,2],-Q[:,2]));ed=np.vstack((vertices[1:4]-vertices[:3],vertices[0]-vertices[3],vertices[4]-vertices[0]))
        return vertices,normals,ed,vertices.min(axis=0),vertices.max(axis=0)
    def overlap(a,b):
        if np.any(a[4]<b[3]-1e-10) or np.any(b[4]<a[3]-1e-10):return False
        axes=np.vstack((a[1],b[1],np.cross(a[2][:,None],b[2][None,:]).reshape(-1,3)));norm=np.linalg.norm(axes,axis=1);axes=axes[norm>1e-12]/norm[norm>1e-12,None]
        x,y=a[0]@axes.T,b[0]@axes.T
        return not np.any((x.max(0)<y.min(0)-1e-10)|(y.max(0)<x.min(0)-1e-10))
    pp=[poly(p) for p in panels];bounds=np.array([[p[3],p[4]] for p in pp]);panel_conflicts=[];pairtests=0
    for i,p in enumerate(pp):
        near=np.flatnonzero(((bounds[i+1:,0]<=p[4]+1e-10)&(bounds[i+1:,1]>=p[3]-1e-10)).all(axis=1))+i+1
        for j in near:
            pairtests+=1
            if overlap(p,pp[j]):panel_conflicts.append([panels[i]['id'],panels[j]['id']])
    mm=[poly(m,.05) for m in members];mb=np.array([[m[3],m[4]] for m in mm]);support_conflicts=[];supporttests=0
    for i,p in enumerate(pp):
        near=np.flatnonzero(((mb[:,0]<=p[4]+1e-10)&(mb[:,1]>=p[3]-1e-10)).all(axis=1))
        for j in near:
            supporttests+=1
            if overlap(p,mm[j]):support_conflicts.append([panels[i]['id'],members[j]['id']])
    assert not panel_conflicts and not support_conflicts
    wheels=[p for p in panels if p.get('whole_sector')];assert len(wheels)==72
    assert all(len(p['vertices_m'])==4 and p['depth_m']==.5 for p in wheels)
    dims={}
    for name in ['inner_wheel','outer_wheel']:
        group=[p for p in wheels if p['wheel']==name];spec=conf[name];assert len(group)==2*spec['sectors']
        p=group[0];v=np.array(p['vertices_m']);u0,u1=v[:,0].min(),v[:,0].max();w0=abs(v[v[:,0]==u0,1]).max();w1=abs(v[v[:,0]==u1,1]).max()
        assert abs(u0-.7)<1e-12 and abs(math.hypot(u1,w1)-spec['outer_radius_m'])<1e-12
        dims[name]={'count':len(group),'base_distance_m':u1-u0,'bases_m':[2*w0,2*w1],'outer_corner_m':math.hypot(u1,w1)}
    # Whole inner wheel supporting planes and independent SAT to 12 inflated BT leg boxes.
    bt=source['coil_groups']['barrel'];btboxes=[]
    for k in range(12):
        a=math.radians(bt['phi_offset_deg']+30*k);c,s=math.cos(a),math.sin(a);Q=np.array([[c,-s,0],[s,c,0],[0,0,1]])
        btboxes.append(poly({'vertices_m':[[-.30,-.35],[.30,-.35],[.30,.35],[-.30,.35]],'basis':Q,'origin_m':np.array([c,s,0])*4.6,'depth_m':24.2}))
    for p in wheels:
        if p['station']==1:
            assert abs(p['origin_m'][2])+.25+.05<7.05
            assert not any(overlap(poly(p),b) for b in btboxes)
        else:assert abs(p['origin_m'][2])-.25>12.05+.05
    old={p['id']:p for p in base['panels']};middle=[p for p in panels if p['kind']=='endcap' and p['station']==2]
    assert len(middle)==216
    keys=('origin_m','basis','vertices_m','depth_m')
    assert all(all(p[k]==old[p['id']][k] for k in keys) for p in middle)
    oldmembers={m['id']:m for m in base['supports']['members']};changed=[m for m in members if m!=oldmembers[m['id']]]
    assert len(changed)==48 and all('-front/LUG' in m['id'] for m in changed)
    assert all(abs(m['depth_m']-.6)<1e-12 for m in changed)
    b3=[p for p in panels if p['kind']=='barrel' and p['station']==3]
    def inside(p,x):
        v=np.asarray(p['vertices_m']);q=np.asarray(p['basis']);l=(np.asarray(x)-p['origin_m'])@q;e=np.roll(v,-1,axis=0)-v;n=np.c_[e[:,1],-e[:,0]];return (n@l[:2] <= (n*v).sum(axis=1)+1e-12).all() and abs(l[2])<=p['depth_m']/2+1e-12
    assert not any(inside(p,[8.2,0,11.7]) for p in b3)
    # All accepted finite-volume certificates are conservative proofs, not samples.
    assert all(p['coil_certificate']['clear'] and p['support_certificate']['clear'] for p in panels)
    assert g['validation']['unresolved_cells_accepted']==0
    # Independent graph reachability checks recorded physical-contact edges;
    # individual material contact construction is reviewed in support.py.
    graph={}
    for a,b in g['supports']['graph']['edges']:graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
    reached=set();pending=[x['id'] for x in g['supports']['ground']]
    while pending:
        node=pending.pop()
        if node in reached:continue
        reached.add(node);pending.extend(graph.get(node,set())-reached)
    assert set(g['supports']['case_ids'])<=reached and all(m['id'] in reached for m in members)
    oldc=obj('tools/muon_layout/acts/config.json');newc=obj('tools/muon_layout/wheels_acts/config.json')
    numerical_keys=['active_border_m','max_step_m','surface_tolerance_m','rk_tolerance_m','path_limit_m','max_steps','navigation_mode']
    assert all(oldc[k]==newc[k] for k in numerical_keys)
    # Current and complete-energy arithmetic without rerunning the energy solver.
    for name,coil in source['coil_groups'].items():
        assert coil['ampere_turns_per_coil']==oldsource['coil_groups'][name]['ampere_turns_per_coil']==mag['currents_Aturn'][name]
        if name.startswith('endcap'):assert abs(coil['center_z_m'])==9.5 and coil['half_z_m']==2.2
    mat=np.asarray(energy['selected']['coupling_integral_J']);assert abs(mat.sum()/2-energy['toroid_energy_J'])<1e-5
    assert abs(energy['complete_energy_J']-energy['toroid_energy_J']-energy['solenoid_self_energy_J'])<1e-5
    assert abs(energy['complete_energy_J']/cold['complete_cold_volume_m3']/1e6-30)<1e-8
    assert all(source['pack'][k]<source['cold'][k]<source['warm'][k] for k in ['normal_m','tangent_m'])
    summed={}
    for name,coil in source['coil_groups'].items():
        perimeter=4*(coil['half_r_m']+coil['half_z_m'])+(2*math.pi-8)*coil['corner_radius_m']
        summed[name]=12*perimeter*source['cold']['normal_m']*source['cold']['tangent_m']
        assert abs(summed[name]-cold['groups'][name]['summed_sleeve_volume_m3'])<1e-8
    # Isolate reviewed subject functions; no execution/import of repository modules.
    original=functions('tools/muon_layout/acts/prepare.py',{'entrance','directions'})
    c=obj('tools/muon_layout/wheels_acts/config.json');c.pop('systems')
    prep=functions('tools/muon_layout/wheels_acts/prepare.py',{'primaries'}, {'original_directions':original['directions'],'entrance':original['entrance']})
    prim=prep['primaries'](c);size=23088;assert len(prim['track_id'])==230880
    sph=prim['sample'][:size]==1;caps=np.isin(prim['sample'][:size],[2,3]);cut=c['endcap_abs_eta_min'];mu0=math.tanh(cut)
    assert abs(prim['solid_angle_weight_sr'][:size][sph].sum()-4*math.pi)<1e-12
    assert abs(prim['solid_angle_weight_sr'][:size][caps].sum()-4*math.pi*(1-mu0))<1e-12
    baselinec=dict(c,entrance={'radius_m':4.35,'half_z_m':6.5,'forward_offset_m':1e-5});bank=original['directions'](baselinec)
    assert np.array_equal(prim['direction'][:14896],bank['direction'])
    # Entrances lie strictly after HCAL and before the inner wheel, all original directions retained.
    launch=prim['start_m'][:size];assert np.max(abs(launch[:,2]))<6.4956
    # Validate exact subject variant reverse transformations and engine identity.
    cpp=raw('tools/muon_layout/acts/propagate.cpp');varianttext=raw('tools/muon_layout/wheels_acts/variant.py').decode();env={'__name__':'frozen_review_subject','__file__':'variant.py'};exec(compile(varianttext,'variant.py','exec'),env)
    assert hashlib.sha256(cpp).hexdigest()==env['BASE_SHA256']
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);src=td/'base.cpp';dst=td/'variant.cpp';src.write_bytes(cpp)
        # Supply real frozen generator bytes so the generator's self-hash can be evaluated.
        vf=td/'variant.py';vf.write_text(varianttext);env['__file__']=str(vf);r=env['generate'](src,dst);generated=dst.read_text();restored=generated
        for ch in reversed(r['transformations']):assert restored.count(ch['new'])==ch['occurrences'];restored=restored.replace(ch['new'],ch['old'])
        assert restored.encode()==cpp
    # Exact paired interval and independent stratum-SE checks over all Boolean input combinations.
    an=functions('tools/muon_layout/wheels_acts/analyze.py',{'sampling_error','availability'})
    pair=functions('tools/muon_layout/wheels_acts/compare.py',{'paired_metric'}, {'sampling_error':an['sampling_error']})['paired_metric']
    tested=0
    for pb,pa,ib,ia in itertools.product([False,True],repeat=4):
        got=pair(np.array([pb,pb]),np.array([pa,pa]),[ib,ib],[ia,ia],[.4,.6],[1,1])
        before=[1] if pb else [0,1] if ib else [0];after=[1] if pa else [0,1] if ia else [0]
        outcomes=[a-b for a in after for b in before]
        assert abs(got['change_lower_fraction']-min(outcomes))<1e-12 and abs(got['change_upper_fraction']-max(outcomes))<1e-12;tested+=1
    v=np.array([0.,1.,0.,1.,1.,1.]);w=np.array([.1,.1,.1,.2,.2,.2]);banks=np.array([2,2,2,3,3,3])
    expected=math.sqrt((1/3)**2*np.var(v[:3],ddof=1)/3+(2/3)**2*np.var(v[3:],ddof=1)/3)
    assert abs(an['sampling_error'](v,w,banks)-expected)<1e-14
    # Literal counters: contiguous same-chamber opposite large faces required;
    # duplicate roots/reentries and side entries cannot manufacture stations.
    counters=functions('tools/muon_layout/acts/analyze.py',{'count_events'})['count_events']
    dt=np.dtype([(k,'f8') for k in ['panel_index','face_index','x_m','y_m','z_m','path_m','dx','dy','dz']])
    cat={(p,k):{'normal':np.array([-1,0,0] if k==0 else [0,0,(-1 if k==4 else 1)]),'large':k>=4,'plane':k,'station':1} for p in [0,1] for k in [0,4,5]}
    def ev(p,k,path):return (p,k,0,0,path,path,.1,0,1)
    fixtures=[([ev(0,4,1),ev(0,5,2)],2,1),([ev(0,0,1),ev(0,5,2)],1,0),([ev(0,4,1),ev(0,4,1),ev(0,5,2)],2,1),([ev(0,4,1),ev(0,5,2),ev(0,4,3),ev(0,5,4)],2,1),([ev(0,4,1),ev(1,5,2)],2,0)]
    for rows,nf,ns in fixtures:
        e=np.array(rows,dtype=dt);z=counters(e,cat,np.ones(len(e),bool),2e-8);assert z['outer_unique_faces']==nf and z['outer_paired_stations']==ns
    # Inspect actual serialized map inputs without importing either field reader.
    maps={}
    for tag in ['baseline-extended','candidate']:
        with np.load(io.BytesIO(raw(D+'magnetic/'+tag+'-map.npz')),allow_pickle=False) as f:maps[tag]={k:f[k] for k in f.files}
    with np.load(io.BytesIO(raw('docs/validation/DES-039/joint-field.npz')),allow_pickle=False) as f:oldmap={k:f[k] for k in f.files}
    bmap=maps['baseline-extended'];zi=np.searchsorted(bmap['z_m'],oldmap['z_m'])
    parity={k:bool(np.array_equal(oldmap[k],bmap[k][:,zi],equal_nan=True)) for k in ['B_total_cyl_T','valid_field','inside_toroid_warm_reservation']}
    assert all(parity.values())
    def stencil(f,points):
        a=np.arctan2(points[:,1],points[:,0]);coordinates=[np.hypot(points[:,0],points[:,1]),points[:,2],np.degrees(a)%30]
        inds=[];good=np.ones(len(points),bool)
        for ax,x in zip(['r_m','z_m','phi_deg'],coordinates):
            grid=f[ax];good&=(x>=grid[0])&(x<=grid[-1]);inds.append(np.clip(np.searchsorted(grid,x,side='right')-1,0,len(grid)-2))
        for offset in itertools.product([0,1],repeat=3):good&=f['valid_field'][tuple(k+j for k,j in zip(inds,offset))]
        return good
    mapchecks={}
    soldata=obj('tools/toroid_prototype/solenoid-input.json')['sources'][1]['content'];sp=soldata['result']
    rng=np.random.default_rng(20021)
    for tag,f in maps.items():
        config=source if tag=='candidate' else oldsource
        assert f['z_m'][0]==-14.3125 and f['z_m'][-1]==14.3125
        assert np.isfinite(f['B_total_cyl_T'][f['valid_field']]).all()
        assert np.isnan(f['B_total_cyl_T'][~f['valid_field']]).all()
        assert np.array_equal(f['B_total_cyl_T'][:,:,0],f['B_total_cyl_T'][:,:,-1],equal_nan=True)
        good=stencil(f,launch);assert good.all()
        ids=[rng.integers(0,len(f[k]),4096) for k in ['r_m','z_m','phi_deg']];rr,zz,ph=[f[k][i] for k,i in zip(['r_m','z_m','phi_deg'],ids)];ph=np.radians(ph);xyz=np.c_[rr*np.cos(ph),rr*np.sin(ph),zz]
        occupied=np.zeros(len(xyz),bool)
        for group in config['coil_groups'].values():
            rho=group['corner_radius_m']
            for k in range(12):
                angle=math.radians(group['phi_offset_deg']+30*k);cs,sn=math.cos(angle),math.sin(angle);u=xyz[:,0]*cs+xyz[:,1]*sn;v=-xyz[:,0]*sn+xyz[:,1]*cs
                q=np.abs(np.c_[u-group['center_r_m'],zz-group['center_z_m']])-np.array([group['half_r_m']-rho,group['half_z_m']-rho]);sd=np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(q.max(axis=1),0)-rho
                occupied|=(abs(sd)<=.1+.1+1e-12)&(abs(v)<=.15+.1+1e-12)
        dr=np.maximum.reduce([sp['cold_inner_radius_m']-rr,rr-sp['winding_outer_radius_m'],np.zeros(len(rr))]);dz=np.maximum(abs(zz)-soldata['configuration']['cold_mass_length_m']/2,0)
        expected=(np.hypot(dr,dz)>.1)&~occupied
        assert np.array_equal(expected,f['valid_field'][tuple(ids)])
        mapchecks[tag]={'shape':list(f['B_total_cyl_T'].shape),'valid_launch_stencils':int(good.sum()),'launch_points':len(good),'independent_mask_nodes':len(rr),'mask_node_mismatches':int(np.count_nonzero(expected!=f['valid_field'][tuple(ids)])),'C12_endpoint_exact':True}
    # Independent IID solid-angle check of the wheel diagnostic. This is an
    # independent sampling cross-check, not a replacement for its analytic result.
    gapchecks={};rng=np.random.default_rng(20022);N=200000;mu=rng.uniform(0,1,N);phi=rng.uniform(0,2*np.pi,N);tan=np.sqrt(1-mu*mu)/mu;ux,uy=np.cos(phi)*tan,np.sin(phi)*tan
    for name in ['inner_wheel','outer_wheel']:
        spec=conf[name];z=spec['abs_z_m'];ideal=(tan*(z-.25)>=.7)&(tan*(z+.25)<=spec['outer_radius_m']);hit=np.zeros(N,bool)
        for body in wheels:
            if body['wheel']!=name or body['side']!=1:continue
            v=np.asarray(body['vertices_m']);Q=np.asarray(body['basis']);ed=np.roll(v,-1,axis=0)-v;n=np.c_[ed[:,1],-ed[:,0]];n/=np.linalg.norm(n,axis=1)[:,None];bb=(n*v).sum(axis=1)
            one=np.ones(N,bool)
            for facez in [z-.25,z+.25]:
                xy=np.c_[facez*ux,facez*uy]@Q[:2,:2];one&=(xy@n.T<=bb+1e-12).all(axis=1)
            hit|=one
        m=int(ideal.sum());loss=float(np.mean(~hit[ideal]));expected=geomctrl['straight_wheel_gap_diagnostic']['wheels'][name]['envelope_gap_fraction_within_ideal_annulus'];se=math.sqrt(loss*(1-loss)/m)
        assert abs(loss-expected)<5*se
        gapchecks[name]={'iid_rays':N,'ideal_annulus_rays':m,'loss_fraction':loss,'sampling_SE':se,'analytic_loss':expected,'deviation_in_SE':(loss-expected)/se}

    source_reconciliation=[]
    for path,expected_hash in geomctrl['sources'].items():
        actual=hashlib.sha256(raw(path)).hexdigest()
        source_reconciliation.append({'path':path,'executed_generation_sha256':expected_hash,'frozen_sha256':actual,'same':expected_hash==actual})
    # Explicit geometry-source counters and independent arithmetic are retained;
    # serialized field parity/launch masks are inspected in a second bounded step.
    return {'revision':revision,'source_sha256':hashes,'geometry':{'panels':len(panels),'counts':{kind:{str(j):sum(p['kind']==kind and p['station']==j for p in panels) for j in [1,2,3]} for kind in ['barrel','endcap']},'panel_pair_SAT_tests':pairtests,'panel_conflicts':panel_conflicts,'panel_support_expanded_SAT_tests':supporttests,'support_conflicts':support_conflicts,'wheels':dims,'middle_exact_retained':len(middle),'front_lugs_changed':len(changed),'B3_BT_return_witness_excluded':True,'ground_reachable_cases':len(g['supports']['case_ids']),'ground_reachable_members':len(members)},'magnetics':{'retained_currents_Aturn':mag['currents_Aturn'],'complete_energy_J':energy['complete_energy_J'],'cold_volume_m3':cold['complete_cold_volume_m3'],'cold_cross_section_m':source['cold'],'summed_sleeve_volumes_m3':summed,'last_energy_change_relative':energy['convergence_comparisons'][-1]['relative_energy_change']},'sampling':{'directions_per_case':size,'tracks_per_system':len(prim['track_id']),'sphere_directions':int(sph.sum()),'precision_cap_directions':int(caps.sum()),'endcap_sphere_directions':int(np.count_nonzero(sph&(abs(prim['eta_pos'][:size])>=cut))),'original_direction_bank_identical':True,'sphere_weight_sr':float(prim['solid_angle_weight_sr'][:size][sph].sum()),'caps_weight_sr':float(prim['solid_angle_weight_sr'][:size][caps].sum()),'fixed_endcap_abs_eta_min':cut,'new_entrance_crossover_abs_eta':math.asinh(6.4684/4.35)},'native_variant':{'base_cpp_sha256':hashlib.sha256(cpp).hexdigest(),'generated_cpp_sha256':r['generated_source_sha256'],'transformation_count':len(r['transformations']),'reverse_restored_exact':True,'inherited_numerical_settings_unchanged':{k:newc[k] for k in numerical_keys}},'geometry_generation_source_reconciliation':source_reconciliation,'serialized_maps':{'baseline_old_node_parity':parity,'systems':mapchecks},'wheel_gap_IID_crosscheck':gapchecks,'postprocessing_controls':{'paired_boolean_cases':tested,'stratified_SE_checked':True,'literal_counter_fixtures':len(fixtures)},'limits':['No ACTS/native gate execution or candidate energy solver rerun','Source subject functions are isolated from immutable git bytes; no repository implementation imports','SAT covers actual panels/support envelopes; coil certificate algorithm reviewed, wheel boxes independently checked; all-volume barrel coil certificates not independently regenerated','Future native acquisition and result artifacts require a separate frozen W-P3 assessment']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--revision',default=REV);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=main(a.repo,a.revision);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))
