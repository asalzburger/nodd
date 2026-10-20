#!/usr/bin/env python3
"""Independent CR-P1 finite geometry/event audit; Python 3 + NumPy, no repo imports.
All evidence comes from git objects at --revision. No native propagation is run.
"""
import argparse,collections,csv,hashlib,io,json,math,platform,re,subprocess,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np

PREFIX='docs/validation/DES-040/refined-wheels-2026-10-20/'

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--revision',required=True);ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args();cache={};used={}
 rev=subprocess.check_output(['git','-C',str(a.repo),'rev-parse',a.revision+'^{commit}'],text=True).strip()
 def raw(path,revision=rev):
  key=(revision,path)
  if key not in cache:cache[key]=subprocess.check_output(['git','-C',str(a.repo),'show',revision+':'+path])
  if revision==rev:used[path]=hashlib.sha256(cache[key]).hexdigest()
  return cache[key]
 def js(path):return json.loads(raw(path))
 def rows(path):return list(csv.DictReader(io.StringIO(raw(path).decode())))
 def near(x,y,tol=1e-10):assert np.max(np.abs(np.asarray(x)-np.asarray(y)))<=tol,(x,y)
 def local(p):return np.array(p['vertices_m'],float)
 def corners(p):
  v=local(p);h=p['depth_m']/2
  return np.vstack([np.c_[v,np.full(4,z)] for z in [-h,h]])@np.array(p['basis']).T+np.array(p['origin_m'])
 def planes(p):
  v=local(p);e=np.roll(v,-1,axis=0)-v;n=np.c_[e[:,1],-e[:,0]];n/=np.linalg.norm(n,axis=1)[:,None]
  q=np.array(p['basis']);o=np.array(p['origin_m']);nn=n@q[:,:2].T
  return np.vstack([nn,q[:,2],-q[:,2]]),np.r_[np.sum(n*v,axis=1)+nn@o,q[:,2]@o+p['depth_m']/2,-q[:,2]@o+p['depth_m']/2]
 def expanded(p,delta):
  v=local(p);e=np.roll(v,-1,axis=0)-v;n=np.c_[e[:,1],-e[:,0]];n/=np.linalg.norm(n,axis=1)[:,None];b=np.sum(n*v,axis=1)+delta
  vv=[np.linalg.solve(n[[i-1,i]],b[[i-1,i]]) for i in range(4)]
  return dict(p,vertices_m=np.array(vv).tolist(),depth_m=p['depth_m']+2*delta)
 def solid(p):
  v=corners(p);n,_=planes(p);edges=np.vstack([v[1]-v[0],v[2]-v[1],v[3]-v[2],v[0]-v[3],v[4]-v[0]])
  return v,n,edges,v.min(axis=0),v.max(axis=0)
 def overlap(x,y):
  va,na,ea,alo,ahi=x;vb,nb,eb,blo,bhi=y
  if np.any(ahi<blo-1e-11) or np.any(bhi<alo-1e-11):return False
  axes=np.vstack([na,nb,np.cross(ea[:,None,:],eb[None,:,:]).reshape(-1,3)]);norm=np.linalg.norm(axes,axis=1);axes=axes[norm>1e-12]/norm[norm>1e-12,None]
  aa=va@axes.T;bb=vb@axes.T
  return not np.any((aa.max(axis=0)<bb.min(axis=0)-1e-11)|(bb.max(axis=0)<aa.min(axis=0)-1e-11))
 def box(identifier,lo,hi,angle,zc,zdepth):
  c,s=math.cos(angle),math.sin(angle)
  return dict(id=identifier,origin_m=[0,0,zc],basis=[[c,-s,0],[s,c,0],[0,0,1]],vertices_m=[[lo[0],lo[1]],[hi[0],lo[1]],[hi[0],hi[1]],[lo[0],hi[1]]],depth_m=zdepth)
 def dimensions(p):
  v=local(p);return [v[1,0]-v[0,0],v[3,1]-v[0,1],v[2,1]-v[1,1],((v[1,1]+v[2,1])-(v[0,1]+v[3,1]))/2,p['depth_m']]
 g=js(PREFIX+'candidate/geometry.json');cfg=js('tools/muon_layout/refined-wheels-config.json');base=js(cfg['base_geometry']);panels=g['panels'];ends=[p for p in panels if p['kind']=='endcap'];byid={p['id']:p for p in panels};mag=g['magnetic_configuration'];supports=g['supports']['members']
 out=dict(assignment='CR-P1',role='independent explicit-fallback PhysVal',reviewed_revision=rev,repo_files_changed=[],native_execution_rerun=False,runtime=dict(python=platform.python_version(),numpy=np.__version__))
 assert len(panels)==1248 and len(ends)==192 and len(supports)==484
 assert g['magnetic_configuration']==base['magnetic_configuration'] and g['supports']==base['supports']
 assert [p for p in panels if p['kind']=='barrel']==[p for p in base['panels'] if p['kind']=='barrel']
 counts=collections.Counter((p['station'],p['side']) for p in ends);families={str(s):len({tuple(np.rint(np.array(dimensions(p))*1e9).astype(int)) for p in ends if p['station']==s}) for s in [1,2,3]}
 assert dict(counts)=={(s,k):n for s,n in [(1,36),(2,36),(3,24)] for k in [-1,1]} and families=={'1':3,'2':3,'3':1}
 out['topology']=dict(total=1248,endcap=192,barrel=1056,per_end={str(s):counts[s,1] for s in [1,2,3]},dimension_families=families,baseline_barrel_support_magnet_equal=True)
 # Whole-volume SAT with independently reconstructed vertices/axes, no repo kernel.
 solids=[solid(p) for p in panels];ss=[solid(expanded(p,.05)) for p in supports];slo=np.array([x[3] for x in ss]);shi=np.array([x[4] for x in ss]);support_clashes=[];coil_clashes=[];support_tests=0;coil_tests=0
 for p in ends:
  x=solids[panels.index(p)];lo,hi=x[3:];nearidx=np.flatnonzero(((shi>=lo)&(slo<=hi)).all(axis=1))
  for i in nearidx:
   support_tests+=1
   if overlap(x,ss[i]):support_clashes.append([p['id'],supports[i]['id']])
  zlo,zhi=x[3][2],x[4][2]
  for name,cg in mag['coil_groups'].items():
   warm_a=mag['warm']['normal_m']/2;half_a=warm_a+.05;half_b=mag['warm']['tangent_m']/2+.05;zc=cg['center_z_m'];extent=cg['half_z_m']+half_a
   if zlo>zc+extent or zhi<zc-extent:continue
   # For every overlapping assembly the slab is wholly within its straight-leg span.
   assert max(abs(zlo-zc),abs(zhi-zc))<cg['half_z_m']-cg['corner_radius_m']-half_a
   for k in range(mag['folds']):
    angle=math.radians(cg['phi_offset_deg']+k*30)
    for sign in [-1,1]:
     r=cg['center_r_m']+sign*cg['half_r_m'];b=solid(box(name,[r-half_a,-half_b],[r+half_a,half_b],angle,zc,2*extent));coil_tests+=1
     if overlap(x,b):coil_clashes.append([p['id'],name,k,sign])
 assert not support_clashes and not coil_clashes
 pair_tests=0;pair_conflicts=[];plo=np.array([x[3] for x in solids]);phi=np.array([x[4] for x in solids])
 for j,x in enumerate(solids):
  for k in np.flatnonzero(((phi[j]>=plo[j+1:])&(plo[j]<=phi[j+1:])).all(axis=1))+j+1:
   pair_tests+=1
   if overlap(x,solids[k]):pair_conflicts.append([panels[j]['id'],panels[k]['id']])
 assert not pair_conflicts
 assert overlap(solids[1056],solids[1056]) and overlap(ss[0],ss[0])
 controls=js(PREFIX+'candidate/geometry-controls.json');ic=controls['independent_controls']
 assert ic['adaptive_audit_count']==len(ic['adaptive_probes'])==192 and all(p['clear'] for p in ic['adaptive_probes'])
 assert sum(p['cells'] for p in ic['adaptive_probes'])==ic['adaptive_cells']==343392
 for key in ['occupied_coil_fixture','incorrect_rotated_bound_fixture','nominal_eta_without_ECT_clearance_fixture','occupied_support_fixture']:assert not ic[key]['clear']
 assert ic['duplicate_panel_conflict']
 out['finite_volume']=dict(coil_box_tests=coil_tests,coil_conflicts=coil_clashes,support_broad_pairs=192*484,exact_expanded_support_tests=support_tests,support_conflicts=support_clashes,all_panel_broad_pairs=len(panels)*(len(panels)-1)//2,panel_SAT_tests=pair_tests,panel_conflicts=pair_conflicts,independent_duplicate_control_rejected=True,recorded_adaptive_audits=192,recorded_adaptive_cells=343392,recorded_adverse_controls_rejected=True,adaptive_kernel_not_rerun=True)
 # Actual affine side and physical normal seam, independently from world vertices.
 core=byid['EP1/REFINED/CORE/S00'];cv=corners(core)[:4,:2];m=(cv[1,1]-cv[0,1])/(cv[1,0]-cv[0,0]);inter=cv[0,1]-m*cv[0,0];seams=[]
 for fam in ['PRE_SLOT','POST_SLOT']:
  p=byid['EP1/REFINED/'+fam+'/S00'];v=corners(p)[[2,3],:2];dd=(m*v[:,0]+inter-v[:,1])/math.sqrt(1+m*m);near(dd,[.02,.02],2e-14);seams+=dd.tolist()
 bt=mag['coil_groups']['barrel'];r=bt['center_r_m']-bt['half_r_m'];aa=mag['warm']['normal_m']/2+.05;bb=mag['warm']['tangent_m']/2+.05;xl,xh=r-aa,r+aa
 area=24*(m*(xh*xh-xl*xl)/2+inter*(xh-xl)-bb*(xh-xl));near(area,controls['dimensions']['inner_wheel']['residual_affine_guard_area_beyond_BT_clearance_boxes_one_end_m2'])
 post=byid['EP1/REFINED/POST_SLOT/S00'];assert dimensions(post)[0]>.5
 out['inner_slot']=dict(actual_normal_seam_extrema_m=[min(seams),max(seams)],extra_localized_affine_area_one_end_m2=area,post_slot_span_m=dimensions(post)[0],classification='extra slot reservation beyond physical coil+50mm boxes; not wholly physically required')
 # Family near-face aperture centres/corners; tangent plane is a circumscribed hole.
 aperture={}
 for station,fams in [(1,['CORE','PRE_SLOT']),(2,['FULL','BT_LOW']),(3,['FULL'])]:
  zn=cfg['stations'][str(station)]['abs_z_m']-.25;nom=zn/math.sinh(3);aperture[str(station)]=dict(nearest_face_m=zn,nominal_R3_m=nom,families={})
  for fam in fams:
   p=byid[f'EP{station}/REFINED/{fam}/S00'];v=local(p);u=v[0,0];rr=np.linalg.norm(v[[0,3]],axis=1);assert u>=nom-1e-12
   aperture[str(station)]['families'][fam]=dict(apothem_m=u,corner_radius_m=rr.tolist(),centre_eta=math.asinh(zn/u),corner_eta=[math.asinh(zn/rad) for rad in rr])
 zn=9.25;radius=zn/math.sinh(3);ect=mag['coil_groups']['endcap_plus'];ri=ect['center_r_m']-ect['half_r_m'];lo=ri-.25;hi=ri+.25
 urange=[radius*math.cos(math.pi/12),radius];vmax=radius*math.sin(math.pi/12)
 assert lo<urange[0] and urange[1]<hi and vmax<.30
 assert abs(zn-ect['center_z_m'])<ect['half_z_m']-ect['corner_radius_m']-.25
 aperture['middle_eta3_continuous_warm_union_proof']=dict(nearest_ECT_leg_angle_bound_deg=15,u_range_m=urange,warm_u_range_m=[lo,hi],max_abs_v_m=vmax,warm_v_halfwidth_m=.30,entire_circle_occupied_before_clearance=True)
 aperture['uniform_eta3_requirement']='UNMET at fixed middle wheel and ECT';out['aperture']=aperture
 # Geometric relocation proof against actual retained supports and outer wheel.
 moved=[dict(p,origin_m=[0,0,12.35]) for p in ends if p['station']==2 and p['side']==1];rear=[];outer=[]
 for p in moved:
  x=solid(p)
  for i,y in enumerate(ss):
   if overlap(x,y):rear.append([p['id'],supports[i]['id']])
  for q in ends:
   if q['station']==3 and q['side']==1 and overlap(x,solids[panels.index(q)]):outer.append([p['id'],q['id']])
 assert rear and outer
 z1,z2,z3=6.7456,9.5,12.8;prod=(z2-z1)*(z3-z2);new=(12.35-z1)*(z3-12.35)
 out['moving_middle']=dict(trial_z_m=12.35,expanded_support_conflicts=len(rear),outer_chamber_conflicts=len(outer),examples=rear[:3]+outer[:3],centre_gaps_m=[z2-z1,z3-z2],span_m=z3-z1,chord_product_m2=prod,moved_chord_product_m2=new,ratio=new/prod,meaning='constant-curvature geometric factor only, no momentum resolution prediction')
 # Independent straight-ray check: evaluate both depth planes in the local polygon.
 def bank(n):
  rng=np.random.default_rng(906310);mu=rng.uniform(np.tanh(1.3),np.tanh(3),n);ph=rng.uniform(0,2*np.pi,n);d=np.c_[np.sqrt(1-mu*mu)*np.cos(ph),np.sqrt(1-mu*mu)*np.sin(ph),mu];return np.vstack([d,d*[1,1,-1]])
 def expected(plist,d,border):
  answer=np.zeros((len(d),3),bool)
  for p in plist:
   if p['kind']!='endcap':continue
   q=np.array(p['basis']);o=np.array(p['origin_m']);v=local(p);edge=np.roll(v,-1,axis=0)-v;n=np.c_[edge[:,1],-edge[:,0]];n/=np.linalg.norm(n,axis=1)[:,None];bb=np.sum(n*v,axis=1)-border;den=d@q[:,2];good=np.ones(len(d),bool)
   for s in [-1,1]:
    dist=(o@q[:,2]+s*p['depth_m']/2)/den;xy=(d*dist[:,None]-o)@q[:,:2];good&=(dist>0)&(xy@n.T<=bb+1e-12).all(axis=1)
   answer[:,p['station']-1]|=good
  return answer
 validation=js(PREFIX+'native-validation/validation.json');native={}
 for run,N in [('straight',1024),('curved-smoke',256)]:
  root=PREFIX+'native-validation/'+run+'/';trackrows=rows(root+'tracks.csv');assert [int(x['track_id']) for x in trackrows]==list(range(N));h=rows(root+'hits.csv');f=rows(root+'geometry.csv');assert len(f)==6*1248
  ids=set();catalog={};maxface=0.;planevis=collections.defaultdict(set)
  for row in f:
   j,k=int(row['panel_index']),int(row['face_index']);ident=int(row['geometry_id']);assert ident not in ids;ids.add(ident);n,b=planes(panels[j]);centre=np.array([float(row[x+'_m']) for x in ['cx','cy','cz']]);which=int(np.argmin(abs(n@centre-b)));res=abs(n[which]@centre-b[which]);maxface=max(maxface,res);assert res<1e-7;assert abs(abs(n[which]@np.array([float(row[x]) for x in ['nx','ny','nz']]))-1)<1e-9
   assert bool(int(row['is_large']))==(which>=4);catalog[j,k]=(which,n[which],b[which],ident);planevis[j].add(which)
  assert len(ids)==7488 and all(v==set(range(6)) for v in planevis.values())
  answer=np.zeros((N,3),bool);inset=answer.copy();visits={};last={};maxres=0.;maxexcess=0.;orphan=0;duplicates=0;prev=(-1,-1.);open_by_track=collections.Counter()
  for event in h:
   t=int(event['track_id']);j=int(event['panel_index']);k=int(event['face_index']);path=float(event['path_m']);assert (t,path)>=prev;prev=(t,path)
   which,n,b,ident=catalog[j,k];assert int(event['geometry_id'])==ident and bool(int(event['is_large']))==(which>=4);xyz=np.array([float(event[x+'_m']) for x in 'xyz']);direction=np.array([float(event[x]) for x in ['dx','dy','dz']]);nn,bbp=planes(panels[j]);maxres=max(maxres,abs(xyz@n-b));maxexcess=max(maxexcess,float(np.max(xyz@nn.T-bbp)));assert np.isfinite(xyz).all()
   if panels[j]['kind']!='endcap':continue
   key=t,j,k;old=last.get(key)
   if old is not None and abs(path-old[0])<2e-6 and np.linalg.norm(xyz-old[1])<2e-6:duplicates+=1;continue
   last[key]=(path,xyz);sense=direction@n
   if abs(sense)<1e-10:continue
   q=np.array(panels[j]['basis']);xy=(xyz-np.array(panels[j]['origin_m']))@q[:,:2];v=local(panels[j]);edge=np.roll(v,-1,axis=0)-v;pn=np.c_[edge[:,1],-edge[:,0]];pn/=np.linalg.norm(pn,axis=1)[:,None];active=bool((xy@pn.T<=np.sum(pn*v,axis=1)-.03+1e-12).all());vk=(t,j)
   if sense<0:
    if vk in visits:orphan+=1
    visits[vk]=(which,active)
   else:
    entry=visits.pop(vk,None)
    if entry is None:orphan+=1;continue
    if which>=4 and entry[0]>=4 and which!=entry[0]:
     answer[t,panels[j]['station']-1]=True
     if entry[1] and active:inset[t,panels[j]['station']-1]=True
  assert maxres<1e-6 and maxexcess<1e-6
  statuses=dict(collections.Counter(x['status'] for x in trackrows));r=dict(rows=N,statuses=statuses,raw_hits=len(h),native_faces=len(ids),max_face_centre_plane_residual_m=maxface,max_hit_plane_residual_m=maxres,max_finite_excess_m=maxexcess,station_paired_counts=answer.sum(axis=0).tolist(),border_station_paired_counts=inset.sum(axis=0).tolist(),three_endcap_pairs=int(answer.all(axis=1).sum()),three_border_endcap_pairs=int(inset.all(axis=1).sum()),endcap_orphan_transitions=orphan,endcap_open_visits=len(visits),deduplicated_endcap_events=duplicates)
  original=validation['native_reports'][run]
  for key in ['statuses','raw_hits','station_paired_counts','border_station_paired_counts','three_endcap_pairs','three_border_endcap_pairs']:assert r[key]==original[key],(run,key,r[key],original[key])
  npz=np.load(io.BytesIO(raw(PREFIX+'native-validation/'+('straight' if run=='straight' else 'curved')+'-inputs.npz')),allow_pickle=False)
  assert len(npz['track_id'])==N
  encoded=raw(root+'input.dat').decode().splitlines();assert int(encoded[0])==N
  actual=np.array([[float(x) for x in line.split()] for line in encoded[1:]])
  assert actual.shape==(N,9)
  near(actual[:,0],npz['track_id'],0);near(actual[:,1],npz['momentum_GeV'],0);near(actual[:,2],npz['charge'],0);near(actual[:,3:6],npz['start_m'],0);near(actual[:,6:9],npz['direction'],0)
  r['native_input_rows_equal_retained_NPZ']=True
  if run=='straight':
   maxray=0.
   for event in h:
    t=int(event['track_id']);point=np.array([float(event[x+'_m']) for x in 'xyz']);delta=point-npz['start_m'][t];direction=npz['direction'][t];maxray=max(maxray,float(np.linalg.norm(np.cross(delta,direction))))
   assert maxray<1e-7;r['max_straight_hit_distance_from_input_ray_m']=maxray
  if run=='straight':
   near(npz['direction'],bank(512));e=expected(panels,npz['direction'],0);b=expected(panels,npz['direction'],.03);r['analytic_outline_mismatches']=int(np.count_nonzero(answer!=e));r['analytic_border_mismatches']=int(np.count_nonzero(inset!=b));assert not r['analytic_outline_mismatches'] and not r['analytic_border_mismatches'];assert statuses=={'completed':1024} and orphan==0 and len(visits)==0
  else:assert statuses=={'completed':93,'field_masked':163};r['case_count']=len(set(zip(npz['momentum_GeV'].tolist(),npz['charge'].tolist())))
  native[run]=r
 out['raw_native_event_audit']=native
 d=bank(32768);geometric={}
 for label,plist in [('before',base['panels']),('refined',panels)]:
  for border,name in [(0,'outline'),(.03,'border30mm')]:
   ans=expected(plist,d,border);r=dict(station_counts=ans.sum(axis=0).tolist(),three_station_count=int(ans.all(axis=1).sum()));orig=validation['geometric_bank']['results'][label+'_'+name];assert r['station_counts']==orig['station_counts'] and r['three_station_count']==orig['three_station_count'];geometric[label+'_'+name]=r
 p0=geometric['before_outline']['three_station_count']/65536;p1=geometric['refined_outline']['three_station_count']/65536
 out['cap_bank']=dict(rows=65536,independent_directions=32768,mirrored=True,eta_range=[1.3,3],distribution='iid uniform cos(theta), full phi, restricted caps; no full-sphere or efficiency claim',results=geometric,three_pair_sampling_SE_percentage_points=[100*math.sqrt(x*(1-x)/32768) for x in [p0,p1]],SE_scope='unpaired marginal sampling SE only; mirrored rows do not double independent sample size; physical uncertainty not assessed')
 # Native corner equality, actual OBJ chamber vertices, ZIP byte identity and SVG polygons.
 nativecorner=rows(PREFIX+'obj/native-inspection/geometry-corners.csv');corner_error=0.
 for row in nativecorner:
  p=panels[int(row['panel_index'])];xyz=np.array([float(row[x+'_m']) for x in 'xyz']);corner_error=max(corner_error,float(np.min(np.linalg.norm(corners(p)-xyz,axis=1))))
 assert corner_error<1e-12
 objs={};objerr=0.
 lookup={'chamber_'+re.sub('[^A-Za-z0-9_]','_',p['id']):p for p in panels}
 for stem in ['chambers-and-coils','barrel-chambers','positive-endcap-chambers','toroids-and-frame']:
  text=raw(PREFIX+'obj/'+stem+'.obj').decode();objects={};current=None
  for line in text.splitlines():
   if line.startswith('o '):current=line[2:];objects[current]=[]
   elif line.startswith('v '):objects[current].append([float(v) for v in line.split()[1:]])
  chambercount=0
  for name,vv in objects.items():
   if name.startswith('chamber_'):
    assert name in lookup;chambercount+=1;v=np.array(vv);expectedv=corners(lookup[name]);err=float(np.linalg.norm(v[:,None,:]-expectedv[None,:,:],axis=2).min(axis=1).max());objerr=max(objerr,err);assert err<1e-12
  objs[stem]=dict(objects=len(objects),chamber_objects=chambercount)
 for zipname in ['chambers-and-coils.zip','components.zip']:
  z=zipfile.ZipFile(io.BytesIO(raw(PREFIX+'obj/'+zipname)))
  for member in z.namelist():assert z.read(member)==raw(PREFIX+'obj/'+member)
 inv=js(PREFIX+'inventory/after-endcap.json');assert inv['total_panels']==192 and inv['shape_families']==7 and set(x['panel_id'] for x in inv['panels'])=={p['id'] for p in ends}
 for fam in inv['families']:
  assert len(fam['panel_ids'])==fam['quantity']
  for id in fam['panel_ids']:near(dimensions(byid[id]),list(fam['dimensions_m'].values()),6e-10)
 sections=js(PREFIX+'xy-sections/sections.json');section_error=0.
 for sec in sections['sections']:
  assert len(sec['chambers'])==counts[sec['station'],1]
  for item in sec['chambers']:
   v=np.array(item['xy_m']);expectedv=corners(byid[item['id']])[:4,:2];section_error=max(section_error,float(np.linalg.norm(v[:,None,:]-expectedv[None,:,:],axis=2).min(axis=1).max()))
 assert section_error<8e-11
 svg=ET.fromstring(raw(PREFIX+'xy-sections/endcap-wheels-xy.svg'));ns={'s':'http://www.w3.org/2000/svg'};clips={el.get('id'):list(el)[0].attrib for el in svg.findall('s:defs/s:clipPath',ns)};svgcounts=[];svgerr=0.
 axes=[el for el in svg.findall('s:g/s:g',ns) if el.get('id','').startswith('axes_')]
 for sec,ax in zip(sections['sections'],axes):
  blue=[el for el in ax.iter() if el.tag.endswith('path') and 'fill: #0060fe' in el.get('style','')];svgcounts.append(len(blue));assert len(blue)==len(sec['chambers'])
  for path,item in zip(blue,sec['chambers']):
   clip=clips[path.get('clip-path')[5:-1]];x,y,w,h=[float(clip[k]) for k in ['x','y','width','height']];v=np.array([float(q) for q in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',path.get('d'))]).reshape(-1,2);v=np.c_[(v[:,0]-x)/w*20-10,10-(v[:,1]-y)/h*20];e=np.array(item['xy_m']);err=float(np.linalg.norm(v[:,None,:]-e[None,:,:],axis=2).min(axis=1).max());svgerr=max(svgerr,err)
 assert svgerr<1e-6
 artifacts=js(PREFIX+'artifacts.json')
 for path,sha in artifacts['source_sha256'].items():assert hashlib.sha256(raw(path)).hexdigest()==sha
 for mapping,folder in [('xy_artifacts','xy-sections/')]:
  for path,sha in artifacts[mapping].items():assert hashlib.sha256(raw(PREFIX+folder+path)).hexdigest()==sha
 for stem,items in artifacts['obj_artifacts'].items():
  for path,sha in items.items():assert hashlib.sha256(raw(PREFIX+'obj/'+path)).hexdigest()==sha
 for path,sha in validation['source_sha256'].items():assert hashlib.sha256(raw(path)).hexdigest()==sha
 assert hashlib.sha256(raw(PREFIX+'candidate/geometry.json')).hexdigest()==validation['geometry_sha256']==artifacts['geometry_sha256']
 out['artifact_consistency']=dict(max_native_corner_error_m=corner_error,max_OBJ_chamber_vertex_error_m=objerr,objects=objs,ZIP_members_byte_equal=True,inventory_families=7,max_section_source_corner_error_m=section_error,SVG_actual_blue_polygons=svgcounts,max_SVG_roundtrip_error_m=svgerr,manifest_source_figure_OBJ_hashes_match=True)
 unchanged=js(PREFIX+'unchanged-evidence.json');bad=[]
 for entry in unchanged['unchanged_files']:
  p=entry['path'];blob=subprocess.check_output(['git','-C',str(a.repo),'rev-parse',rev+':'+p],text=True).strip();oldblob=subprocess.check_output(['git','-C',str(a.repo),'rev-parse',unchanged['baseline_revision']+':'+p],text=True).strip()
  if blob!=entry['git_blob'] or blob!=oldblob or hashlib.sha256(raw(p)).hexdigest()!=entry['sha256']:bad.append(p)
 assert len(unchanged['unchanged_files'])==369 and not bad
 out['historical_integrity']=dict(baseline_revision=unchanged['baseline_revision'],all_369_blobs_and_SHA256_equal=True)
 out['acquisition_revision']=validation['source_revision'];out['export_revision']=artifacts['execution_revision'];out['evidence_SHA256']=used;out['passed']=True
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='evidence_SHA256'},indent=2))

if __name__=='__main__':main()
