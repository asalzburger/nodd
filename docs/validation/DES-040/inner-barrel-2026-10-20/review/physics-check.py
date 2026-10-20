#!/usr/bin/env python3
"""Independent IB-P1 finite-artifact audit. Git blobs only; no repository imports.

NumPy is used for linear algebra and the declared iid bank. Geometry is derived
directly from convex halfspaces, SAT axes and exact straight-leg bounds.
"""
import argparse, copy, hashlib, io, json, math, platform, re, struct, subprocess, tarfile, time
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np

PIN='94d474906660619587b66e850019f0f0fb8e03bd'
BASE='docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json'
SCOPE='docs/validation/DES-040/inner-barrel-2026-10-20/'
HCAL='0e8530d56d171f38c9d53d3c60c8b48803680bbd'

def normals(p):
    v=np.asarray(p,float); e=np.roll(v,-1,axis=0)-v
    n=np.column_stack((e[:,1],-e[:,0])); return n/np.linalg.norm(n,axis=1)[:,None]

def expanded(body,gap):
    p=copy.deepcopy(body);v=np.asarray(p['vertices_m']);n=normals(v)
    b=np.einsum('ij,ij->i',n,v)+gap
    p['vertices_m']=[np.linalg.solve(n[[i-1,i]],b[[i-1,i]]).tolist() for i in range(len(v))]
    p['depth_m']+=2*gap;return p

def prism(body):
    v=np.asarray(body['vertices_m']);q=np.asarray(body['basis']);o=np.asarray(body['origin_m']);h=body['depth_m']/2
    points=np.concatenate([np.column_stack((v,np.full(len(v),z)))@q.T+o for z in [-h,h]])
    face=np.concatenate([np.column_stack((normals(v),np.zeros(len(v))))@q.T,q[:,2][None,:]])
    edges=np.concatenate([(np.roll(points[:len(v)],-1,axis=0)-points[:len(v)]),q[:,2][None,:]])
    return dict(id=body['id'],p=points,n=face,e=edges,lo=points.min(axis=0),hi=points.max(axis=0))

def intersect(a,b):
    if np.any(a['hi']<b['lo']-1e-10) or np.any(b['hi']<a['lo']-1e-10):return False
    axes=np.concatenate([a['n'],b['n'],np.cross(a['e'][:,None,:],b['e'][None,:,:]).reshape(-1,3)])
    axes=axes[np.linalg.norm(axes,axis=1)>1e-12];axes/=np.linalg.norm(axes,axis=1)[:,None]
    x=a['p']@axes.T;y=b['p']@axes.T
    return not np.any((x.max(axis=0)<y.min(axis=0)-1e-10)|(y.max(axis=0)<x.min(axis=0)-1e-10))

def contains(body,point):
    x=(np.asarray(point)-body['origin_m'])@np.asarray(body['basis'])
    v=np.asarray(body['vertices_m']);return bool(abs(x[2])<body['depth_m']/2 and np.all(np.einsum('ij,ij->i',normals(v),x[:2]-v)<0))

def section(body,z=1.):
    p=prism(body)['p'];k=len(body['vertices_m']);out=[]
    for i,j in [(i,(i+1)%k) for i in range(k)]+[(k+i,k+(i+1)%k) for i in range(k)]+[(i,k+i) for i in range(k)]:
        a,b=p[i],p[j]
        if a[2]==z:out.append(a[:2])
        if (a[2]-z)*(b[2]-z)<0:out.append((a+(z-a[2])/(b[2]-a[2])*(b-a))[:2])
    if not out:return None
    out=np.unique(np.round(out,11),axis=0);c=out.mean(axis=0)
    return out[np.argsort(np.arctan2(out[:,1]-c[1],out[:,0]-c[0]))]

def same_poly(a,b,tol=1e-9):
    a=np.asarray(a);b=np.asarray(b)
    return a.shape==b.shape and max(min(np.linalg.norm(x-b,axis=1)) for x in a)<=tol

def svg_polygons(raw,groups):
    """Invert declared axes transforms and match actual vector path vertices."""
    root=ET.fromstring(raw);ns='{http://www.w3.org/2000/svg}';clips={c.attrib['id']:c.find(ns+'rect').attrib for c in root.findall('.//'+ns+'clipPath')};count=0
    for axis,expected,limits in groups:
        g=next(x for x in root.findall('.//'+ns+'g') if x.get('id')==axis)
        paths=[p for p in g.findall('./'+ns+'g/'+ns+'path') if p.get('clip-path') and any(s in p.get('style','') for s in ['#cdba9d','#e9941b','#a0a0a0','#0060fe','stroke: #c52626'])]
        assert len(paths)==len(expected),(axis,len(paths),len(expected))
        for path,wanted in zip(paths,expected):
            values=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',path.attrib['d'])]
            assert len(values)==8,(axis,path.attrib['d'])
            xy=np.array(values).reshape(4,2);key=re.search(r'#([^)]*)',path.attrib['clip-path'])[1];rect=clips[key];x,y,w,h=[float(rect[k]) for k in ['x','y','width','height']];(xmin,xmax),(ymin,ymax)=limits
            data=np.column_stack((xmin+(xy[:,0]-x)/w*(xmax-xmin),ymax-(xy[:,1]-y)/h*(ymax-ymin)))
            assert same_poly(data,wanted,1e-7),(axis,data,wanted)
            count+=1
    return count

def hit(body,rays,border):
    """Each ray must intersect both depth faces within this one inset polygon."""
    q=np.asarray(body['basis']);o=np.asarray(body['origin_m']);v=np.asarray(body['vertices_m']);n=normals(v)
    d=rays@q; start=-o@q; h=body['depth_m']/2
    good=np.ones(len(rays),bool)
    for z in [-h,h]:
        with np.errstate(divide='ignore',invalid='ignore'):t=(z-start[2])/d[:,2]
        good &= np.isfinite(t)&(t>0)
        # Only surviving directions require 2D halfspace checks.
        ids=np.flatnonzero(good);xy=start[:2]+t[ids,None]*d[ids,:2]
        for nn,vv in zip(n,v):
            good[ids] &= (xy-vv)@nn<=-border+1e-10
    return good

def bank(panels,rays,border):
    out=np.zeros((len(rays),3),bool)
    for p in panels:out[:,p['station']-1]|=hit(p,rays,border)
    return out

def hbody(ident,sec,a,b,hz,tangent,inset):
    ph=sec*math.pi/8;c,s=math.cos(ph),math.sin(ph)
    return dict(id=ident,origin_m=[0,0,0],basis=[[c,-s,0],[s,c,0],[0,0,1]],vertices_m=[[a,-a*tangent+inset],[b,-b*tangent+inset],[b,b*tangent-inset],[a,a*tangent-inset]],depth_m=2*hz)

def clip(v,n,b):
    out=[]
    for a,c in zip(v,np.roll(v,-1,axis=0)):
        da,dc=np.dot(a,n)-b,np.dot(c,n)-b
        if da<=0:out.append(a)
        if da*dc<0:out.append(a+da/(da-dc)*(c-a))
    return np.asarray(out)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',required=True,type=Path);ap.add_argument('--revision',required=True);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();begin=time.monotonic()
    if a.revision!=PIN:raise ValueError('Bounded review revision must be '+PIN)
    evidence={}
    def read(path,rev=PIN):
        raw=subprocess.check_output(['git','-C',str(a.repo),'show',rev+':'+path]);evidence[rev+':'+path]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw));return raw
    def load(path,rev=PIN):return json.loads(read(path,rev))
    geo=load(BASE); conditional=load(SCOPE+'conditional-check.json');trialdoc=load(SCOPE+'conditional-B1-outlines.json');views=load(SCOPE+'views/views.json');iface=load(SCOPE+'interface-check.json');old=load(SCOPE+'unchanged-evidence.json')
    # Verify the declared source archive against both manifest and exact Git objects.
    manifest=load(SCOPE+'inputs/source-manifest.json');archive=tarfile.open(fileobj=io.BytesIO(read(SCOPE+'inputs/source-blobs.tar.gz')),mode='r:gz');members=archive.getnames();archive_checks=[]
    for loc,record in manifest.items():
        rev,path=loc.split(':',1);raw=read(path,rev);assert hashlib.sha256(raw).hexdigest()==record['sha256'] and len(raw)==record['bytes']
        names=[n for n in members if n.endswith('/'+path) or n==path]
        assert len(names)==1,(path,names)
        assert archive.extractfile(names[0]).read()==raw
        archive_checks.append(loc)
    for rec in conditional['sources']:
        rev,path=rec['locator'].split(':',1);raw=read(path,rev)
        assert hashlib.sha256(raw).hexdigest()==rec['sha256'] and len(raw)==rec['bytes']
    assert hashlib.sha256(read(SCOPE+'conditional-check.py')).hexdigest()==conditional['checker_sha256']
    # Historical preservation audit checks all identities, including OBJ/map/native files.
    preserved=[]
    inventory=subprocess.check_output(['git','-C',str(a.repo),'ls-tree','-r','--name-only',old['baseline_revision'],'--']+old['scope'],text=True).splitlines()
    assert set(inventory)=={rec['path'] for rec in old['files']},'Historical identity inventory incomplete'
    for rec in old['files']:
        p=rec['path'];before=read(p,old['baseline_revision']);now=read(p)
        assert before==now and hashlib.sha256(now).hexdigest()==rec['sha256'];preserved.append(p)
    assert len(preserved)==old['unchanged_files']==687
    cat=load('docs/validation/MUON-001/hcal-material.json');hc=load('tools/hcal_barrel/config.json',HCAL);hs=load('docs/validation/DES-037/summary.json',HCAL)
    assert cat['repo_head']==HCAL and hc==hs['config']
    for p in ['tools/hcal_barrel/config.json','tools/hcal_barrel/design.py','docs/validation/DES-037/summary.json']:
        assert hashlib.sha256(read(p,HCAL)).hexdigest()==cat['source_sha256'][p]
    mag=geo['magnetic_configuration'];c=geo['configuration']['chambers'];bt=mag['coil_groups']['barrel'];half=c['depth_m']/2;clear=c['coil_clearance_m'];Rmax=bt['center_r_m']-bt['half_r_m']-mag['warm']['normal_m']/2-clear-half
    b1=[p for p in geo['panels'] if p['kind']=='barrel' and p['station']==1];fixed=[p for p in geo['panels'] if p not in b1];new=trialdoc['panels'];assert len(b1)==96 and len(new)==144 and len(fixed)==792
    assert len(geo['supports']['members'])==484 and len(geo['panels'])==888
    source_fingerprint=hashlib.sha256(json.dumps(mag,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert all(p['coil_certificate']['clear'] and p['coil_certificate']['source_fingerprint']==source_fingerprint and p['support_certificate']['clear'] and p['support_certificate']['required_clearance_m']==.05 and p['support_certificate']['total_members']==484 for p in new)
    assert {x['id'] for x in conditional['checks']['actual_orientation_uncached_coil_audits']}=={p['id'] for p in new}
    moved=[]
    for p in b1:
        if round(p['compartment']['phi_deg']/15)%2==0:
            q=copy.deepcopy(p);ph=math.radians(p['compartment']['phi_deg']);q['origin_m']=[Rmax*math.cos(ph),Rmax*math.sin(ph),0];moved.append(q)
    tangent=math.tan(math.pi/16);hz=(hc['half_length_mm']-hc['end_flange_mm'])/1000;outer=hc['proposed_outer_apothem_mm']/1000;rear=outer-hc['back_cover_mm']/1000
    plates=[];covers=[]
    for sec in range(16):
        for lay in hs['layers']:
            r=lay['steel_front_mm']/1000
            plates.append(hbody(f'HCAL/S{sec:02d}/Steel{lay["layer"]:02d}',sec,r,r+hc['steel_mm']/1000,hz,tangent,(hc['sector_half_seam_mm']+hc['edge_rail_mm'])/1000))
        covers.append(hbody(f'HCAL/S{sec:02d}/RearCover',sec,rear,outer,hz,tangent,hc['sector_half_seam_mm']/1000))
    hsol=[prism(p) for p in plates+covers]
    actual_conflicts={p['id']:[q['id'] for q in hsol if intersect(prism(p),q)] for p in moved};assert len(actual_conflicts)==48 and all(actual_conflicts.values())
    width=max(abs(x) for p in b1 for x,z in p['vertices_m']);bounds=[]
    alpha_even=math.atan((width-.03)/(5.2+half));alpha_odd=math.radians(15.1)-alpha_even
    derived_odd_half=(5.75+half)*math.tan(alpha_odd)+.03
    assert abs(derived_odd_half-conditional['derivation']['odd_half_width_m'])<1e-12
    assert abs(math.degrees(alpha_even+alpha_odd)-15-.1)<1e-12
    for k in range(12):
        ph=k*math.pi/6;er=np.array([math.cos(ph),math.sin(ph)]);et=np.array([-er[1],er[0]]);best=-math.inf
        for p in covers:
            v=section(p);v=clip(v,et,width)
            if len(v):v=clip(v,-et,width)
            if len(v):best=max(best,float(np.max(v@er)))
        bounds.append(dict(phi_deg=k*30,cover_max_projected_r_m=best,minimum_B1_R_m=best+clear+half,missing_room_m=best+clear+half-Rmax,depth_room_m=bt['center_r_m']-bt['half_r_m']-mag['warm']['normal_m']/2-best-2*clear))
    p=next(p for p in moved if p['id']=='B1/F00/Z02');witnesses=[]
    for xyz,material in [([4.120,0,1],plates[35]),([4.153,0,1],covers[0])]:
        assert contains(p,xyz) and contains(material,xyz);witnesses.append(dict(point_m=xyz,panel=p['id'],material=material['id']))
    # Entire B1 prisms are axially remote from ECT and BT rounded returns.
    zmax=max(abs(v[1]) for p in new for v in p['vertices_m'])
    ect_zlo=min(abs(g['center_z_m'])-g['half_z_m']-mag['warm']['normal_m']/2-clear for name,g in mag['coil_groups'].items() if name!='barrel')
    assert zmax<ect_zlo and zmax<bt['half_z_m']-bt['corner_radius_m']-mag['warm']['normal_m']/2-clear
    # Therefore all B1/BT checks reduce exactly to 24 finite straight boxes.
    boxes=[]
    for k in range(12):
        for j,r in enumerate([bt['center_r_m']-bt['half_r_m'],bt['center_r_m']+bt['half_r_m']]):
            ph=k*math.pi/6;co,si=math.cos(ph),math.sin(ph);aa=mag['warm']['normal_m']/2;bb=mag['warm']['tangent_m']/2
            boxes.append(dict(id=f'BT/{k}/{j}',origin_m=[0,0,0],basis=[[co,-si,0],[si,co,0],[0,0,1]],vertices_m=[[r-aa,-bb],[r+aa,-bb],[r+aa,bb],[r-aa,bb]],depth_m=2*(bt['half_z_m']-bt['corner_radius_m'])))
    ns=[prism(p) for p in new];sup=[prism(expanded(p,.05)) for p in geo['supports']['members']];coil=[prism(expanded(p,.05)) for p in boxes]
    supconf=[[p['id'],q['id']] for p in ns for q in sup if intersect(p,q)];coilconf=[[p['id'],q['id']] for p in ns for q in coil if intersect(p,q)]
    assert not supconf and not coilconf
    alltrial=new+fixed;sol=[prism(p) for p in alltrial];pairconf=[]
    for i,p in enumerate(sol):
        for q in sol[i+1:]:
            if intersect(p,q):pairconf.append([p['id'],q['id']])
    assert not pairconf
    families=Counter((round(float(np.ptp(np.asarray(p['vertices_m'])[:,0])),12),round(float(np.ptp(np.asarray(p['vertices_m'])[:,1])),12)) for p in new)
    bnew={p['id']:p for p in new};retained=[]
    ident=lambda p:{k:p[k] for k in ['id','kind','origin_m','basis','vertices_m','depth_m','station','compartment','face']}
    for p in b1:
        if p['id'] in bnew and ident(p)==ident(bnew[p['id']]):retained.append(p['id'])
    assert len(retained)==48 and len(families)==4
    # Independent analytic 4-seed and continuous-z counterfactuals classify losses.
    seeds=[];full=[]
    for p in b1:
        q=copy.deepcopy(p);odd=round(q['compartment']['phi_deg']/15)%2
        if odd:
            ph=math.radians(q['compartment']['phi_deg']);q['origin_m']=[5.75*math.cos(ph),5.75*math.sin(ph),0]
            for v in q['vertices_m']:v[0]=math.copysign(derived_odd_half,v[0])
        seeds.append(q)
        if q['id'].endswith('Z00'):
            t=copy.deepcopy(q)
            for v in t['vertices_m']:v[1]=math.copysign(c['barrel_half_z_m'][0],v[1])
            # Z00 has all negative z; explicitly preserve vertex order.
            w=max(abs(v[0]) for v in t['vertices_m']);t['vertices_m']=[[-w,-c['barrel_half_z_m'][0]],[w,-c['barrel_half_z_m'][0]],[w,c['barrel_half_z_m'][0]],[-w,c['barrel_half_z_m'][0]]];full.append(t)
    assert len(seeds)==96 and len(full)==24
    assert all(not intersect(prism(expanded(p,.02)),prism(full[(i+1)%24])) for i,p in enumerate(full))
    # Verify ideal seeds themselves clear source coils; no-frame labels do not hide coil cuts.
    assert all(not intersect(prism(p),q) for p in seeds for q in coil)
    rng=np.random.default_rng(40087);mu=rng.uniform(-1,1,65536);phi=rng.uniform(0,2*math.pi,65536);rays=np.column_stack((np.sqrt(1-mu*mu)*np.cos(phi),np.sqrt(1-mu*mu)*np.sin(phi),mu));coverage={}
    for border in [0.,.03]:
        common=bank(fixed,rays,border);oldbar=bank(b1,rays,border)[:,0];newbar=bank(new,rays,border)[:,0];noframe=bank(seeds,rays,border)[:,0];noz=bank(full,rays,border)[:,0];before=common.copy();after=common.copy();before[:,0]|=oldbar;after[:,0]|=newbar;rec={}
        for name,oldmask,newmask in [('B1barrel',oldbar,newbar),('station1',before[:,0],after[:,0]),('three_station',before.all(axis=1),after.all(axis=1))]:
            delta=newmask.astype(int)-oldmask.astype(int);loss=oldmask&~newmask
            rr=dict(denominator=65536,before_count=int(oldmask.sum()),after_count=int(newmask.sum()),gains=int((delta==1).sum()),losses=int((delta==-1).sum()),delta_pp=float(delta.mean()*100),paired_SE_pp=float(delta.std(ddof=1)/math.sqrt(len(delta))*100),quarter_deltas_pp=[float(x.mean()*100) for x in np.array_split(delta,4)])
            claimed=conditional['coverage'][str(border)][name]
            for k in ['before_count','after_count','gains','losses']:assert rr[k]==claimed[k],(border,name,k,rr[k],claimed[k])
            assert abs(rr['paired_SE_pp']-claimed['paired_sampling_standard_error_pp'])<1e-12
            if name!='station1':
                rr['loss_classification']={}
                for cat,mask in [('frame_packing_loss',loss&noframe),('longitudinal_seed_seam_loss',loss&~noframe&noz),('finite_barrel_end_loss',loss&~noz)]:
                    ids=np.flatnonzero(mask);rr['loss_classification'][cat]=dict(count=len(ids),first_ids=ids[:5].tolist(),abs_eta_range=[float(np.abs(np.arctanh(mu[ids])).min()),float(np.abs(np.arctanh(mu[ids])).max())] if len(ids) else None)
                    assert len(ids)==conditional['coverage'][str(border)]['loss_localization'][name][cat]['count']
                assert sum(x['count'] for x in rr['loss_classification'].values())==rr['losses']
            rec[name]=rr
        coverage[str(border)]=rec
    # Actual displayed geometry and file identity, independently reconstructed.
    invalid=copy.deepcopy(b1)
    for p in invalid:
        p['id']='INVALID-BELOW/'+p['id'];facet=round(p['compartment']['phi_deg']/15)%24
        if facet%2==0:p['origin_m']=(np.asarray(p['origin_m'])*Rmax/5.2).tolist()
        else:
            for v in p['vertices_m']:v[0]=math.copysign(iface['angular_projection']['widened_intercoil_half_width_for_0p1deg_full_depth_overlap_m'],v[0])
    displayed=0
    for label,panels in [('current',b1),('invalid_below',invalid),('unselected_outward',new)]:
        actual={p['id']:section(p) for p in panels if section(p) is not None};assert len(actual)==24
        for rec in views['cuts'][label]:assert same_poly(actual[rec['id']],rec['xy_m']);displayed+=1
    for key,panels in [('hcal_steel',plates),('hcal_rear_covers',covers)]:
        actual={p['id']:section(p) for p in panels}
        for rec in views[key]:assert same_poly(actual[rec['id']],rec['xy_m']);displayed+=1
    for rec in views['warm_coils']:
        assert rec['group']=='barrel';p=boxes[rec['coil']*2+rec['interval']];assert same_poly(section(p),rec['xy_m']);displayed+=1
    for label,panels in [('Current selected B1',b1),('Unselected outward B1 · frame cuts retained',new)]:
        actual={p['id']:p['vertices_m'] for p in panels if abs(p['compartment']['phi_deg']-15)<1e-8}
        assert len(actual)==len(views['longitudinal'][label])
        for rec in views['longitudinal'][label]:assert same_poly(actual[rec['id']],rec['vertices_tangent_z_m']);displayed+=1
    for mapping,revision in [(views['source_sha256'],views['source_revision']),(views['input_sha256'],PIN)]:
        for p,sha in mapping.items():assert hashlib.sha256(read(p,revision)).hexdigest()==sha
    artifacts={};svg_count=0
    for name,sha in views['artifacts'].items():
        raw=read(SCOPE+'views/'+name);assert hashlib.sha256(raw).hexdigest()==sha
        if name.endswith('.png'):
            assert raw[:8]==b'\x89PNG\r\n\x1a\n';artifacts[name]=dict(sha256=sha,size=struct.unpack('>II',raw[16:24]))
        else:
            root=ET.fromstring(raw);artifacts[name]=dict(sha256=sha,path_count=len(root.findall('.//{http://www.w3.org/2000/svg}path')))
            if 'feasibility' in name:
                groups=[]
                for i,label in enumerate(['current','invalid_below','unselected_outward']):
                    polygons=[p['xy_m'] for key in ['hcal_steel','hcal_rear_covers','warm_coils'] for p in views[key]]+[p['xy_m'] for p in views['cuts'][label]]
                    groups.append(('axes_'+str(i+1),polygons,views['common_xy_limits_m']))
            else:
                groups=[('axes_'+str(i+1),[np.asarray(p['vertices_tangent_z_m'])[:,[1,0]] for p in views['longitudinal'][label]],[[-6.7,6.7],[-1.1,1.1]]) for i,label in enumerate(['Current selected B1','Unselected outward B1 · frame cuts retained'])]
            svg_count+=svg_polygons(raw,groups)
    # Basic independent negative controls, including distinct-station semantics.
    control=dict(duplicate_detected=intersect(ns[0],ns[0]),remote_separated=not intersect(ns[0],prism(dict(new[0],origin_m=[100,100,100]))),inside_steel_witness=contains(plates[35],[4.12,0,1]),three_panels_one_station_do_not_make_three=not bank([b1[2]]*3,np.array([[1.,0.,.2]]),0.).all(axis=1)[0])
    assert all(control.values())
    result=dict(assignment='IB-P1',role='PhysVal explicit-mandate fallback',reviewed_revision=PIN,hcal_revision=HCAL,status='Bounded independent artifact/geometry assessment; no human approval or alternative selected',input_dirty_content='Only paired journal dirty at initial check; no working-tree scientific bytes read',undercoil=dict(R_max_m=Rmax,HCAL_prism_count=len(hsol),moved_count=len(moved),all_moved_actual_material_intersections=actual_conflicts,plane_bounds=bounds,strict_interior_witnesses=witnesses),conditional=dict(active_count=888,conditional_count=len(alltrial),B1_count=len(new),fixed_count=len(fixed),retained_B1_count=len(retained),magnetic_source_fingerprint=source_fingerprint,dimension_families=[dict(tangent_width_m=k[0],z_length_m=k[1],count=v) for k,v in sorted(families.items())],pair_count=len(sol)*(len(sol)-1)//2,pair_conflicts=pairconf,support_pair_count=len(ns)*len(sup),support_conflicts=supconf,independent_exact_straight_coil_pair_count=len(ns)*len(coil),coil_conflicts=coilconf,full_z_adjacent20mm_checks=24,zmax_m=zmax,expanded_ECT_axial_start_m=ect_zlo,max_corner_radius_m=max(float(np.linalg.norm(v[:2])) for p in ns for v in p['p'])),coverage=dict(samples=65536,seed=40087,scope='iid full4pi, stationary IP rays; same cassette both depth faces; barrel/endcap OR within station then three distinct station IDs',results=coverage),artifact_audit=dict(display_polygons_rebuilt=displayed,actual_SVG_polygons_matched=svg_count,artifacts=artifacts,source_archive_records_matched=len(archive_checks),old_blob_identities_unchanged=len(preserved)),controls=control,sources=evidence,limits=['HCAL audit includes actual steel/cover subset; clear reduced subset would not certify full HCAL.','Clearance means finite source-model geometry with face-offset50mm guards; no manufacturing or engineered tolerance qualification.','Coverage Monte Carlo SE covers this geometric bank only, no detector model uncertainty; fixed quarters are diagnostics, not independent replications.','No transport, response, reconstructed efficiency, momentum resolution, nonlinear magnet/field solve, nativeACTS or dependency/source changes performed.','Geometry preservation of old native/maps/OBJ bytes does not rerun or newly validate their physics.'],runtime=dict(python=platform.python_version(),numpy=np.__version__,elapsed_s=time.monotonic()-begin),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:result[k] for k in ['assignment','reviewed_revision','conditional','coverage','artifact_audit','controls','runtime']},indent=2))

if __name__=='__main__':main()
