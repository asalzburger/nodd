#!/usr/bin/env python3
"""SS-P1 portable read-only exact-Git-object PhysVal checker. Requires numpy only.
All review evidence is read with git show REV:PATH. Output is restricted to
/private/tmp/pr90-SS-P1-*. Primary ray, SAT, event and SVG tests import no nODD helper.
"""
import argparse,collections,csv,hashlib,io,json,math,pathlib,re,subprocess,sys,tarfile,time,zipfile,xml.etree.ElementTree as ET
import numpy as np
REV='11ec9bb670bca2b882929d1d2b4ef7d9da534da6'
SCOPE='docs/validation/DES-040/sketched-stagger-2026-10-20/'
BASE='docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json'
REPO=pathlib.Path('/Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout')
CACHE={}; RESULT={'assignment':'SS-P1','revision':REV,'checks':{},'findings':[],'limits':['No new native engine, field solve, simulation, reconstruction or installed-dependency verification.','Independent numerical implementation shares the declared prism/coil representation and design choices; it cannot qualify absent material or services.']}
def raw(p,rev=REV):
 k=(rev,p)
 if k not in CACHE:CACHE[k]=subprocess.check_output(['git','-C',str(REPO),'show',rev+':'+p])
 return CACHE[k]
def js(p,rev=REV):return json.loads(raw(p,rev))
def sha(b):return hashlib.sha256(b).hexdigest()
def record(name,data):RESULT['checks'][name]=data;print(name,json.dumps(data)[:400],flush=True)
def eq(a,b,name,atol=2e-11):
 a,b=np.asarray(a),np.asarray(b)
 assert a.shape==b.shape,(name,a.shape,b.shape)
 assert np.array_equal(np.isfinite(a),np.isfinite(b)),name+' finite mask'
 finite=np.isfinite(a)&np.isfinite(b)
 residual=float(np.max(np.abs(a[finite]-b[finite]))) if finite.any() else 0.
 assert residual<atol,(name,residual)
 return residual
def vertices(p):
 v=np.asarray(p['vertices_m']);h=p['depth_m']/2
 return np.concatenate([np.c_[v,np.full(4,z)] for z in [-h,h]])@np.asarray(p['basis']).T+p['origin_m']
def poly(p):
 v=np.asarray(p['vertices_m']);e=np.roll(v,-1,axis=0)-v
 n=np.c_[e[:,1],-e[:,0]];n/=np.linalg.norm(n,axis=1)[:,None]
 return n,np.sum(n*v,axis=1)
def body_planes(p):
 q=np.asarray(p['basis']);o=np.asarray(p['origin_m']);n,b=poly(p);w=n@q[:,:2].T
 return np.r_[w,q[:,2][None],-q[:,2][None]],np.r_[b+w@o,q[:,2]@o+p['depth_m']/2,-q[:,2]@o+p['depth_m']/2]
def dot(d,a):return d[:,0]*a[0]+d[:,1]*a[1]+d[:,2]*a[2]
def full_depth(p,d,border):
 # Independent oriented-edge cross products at BOTH depth faces.
 q=np.asarray(p['basis']);o=np.asarray(p['origin_m']);v=np.asarray(p['vertices_m']);e=np.roll(v,-1,axis=0)-v
 den=dot(d,q[:,2]);project=o@q;h=p['depth_m']/2
 good=np.abs(den)>1e-12
 t0=np.divide(project[2]-h,den,out=np.zeros(len(d)),where=good)
 t1=np.divide(project[2]+h,den,out=np.zeros(len(d)),where=good)
 good&=(t0>0)&(t1>0)
 ix=np.flatnonzero(good)
 ans=np.full(len(d),np.inf)
 if not len(ix):return ans
 dx=dot(d[ix],q[:,0]);dy=dot(d[ix],q[:,1]);ok=np.ones(len(ix),bool)
 for t in [t0[ix],t1[ix]]:
  xx=t*dx-project[0];yy=t*dy-project[1]
  for a,edge in zip(v,e):
   ok&=edge[0]*(yy-a[1])-edge[1]*(xx-a[0]) >= border*np.linalg.norm(edge)-1e-12*np.linalg.norm(edge)
 ans[ix[ok]]=(t0[ix[ok]]+t1[ix[ok]])/2
 return ans
def distances(panels,d,border):
 ans=np.full((len(d),3),np.inf);bar=ans.copy()
 for p in panels:
  v=full_depth(p,d,border);s=p['station']-1
  ans[:,s]=np.minimum(ans[:,s],v)
  if p['kind']=='barrel':bar[:,s]=np.minimum(bar[:,s],v)
 return ans,bar
def summary(before,after):
 delta=after.astype(int)-before.astype(int)
 return {'before_count':int(before.sum()),'after_count':int(after.sum()),'before_fraction':float(before.mean()),'after_fraction':float(after.mean()),'gains':int((delta==1).sum()),'losses':int((delta==-1).sum()),'delta_percentage_points':float(100*delta.mean()),'paired_sampling_standard_error_pp':float(100*np.std(delta,ddof=1)/np.sqrt(len(delta))),'quarter_deltas_pp':[float(100*x.mean()) for x in np.array_split(delta,4)]}
def spacing(a):
 valid=np.isfinite(a).all(axis=1);ordered=valid&(a[:,1]>a[:,0])&(a[:,2]>a[:,1]);x=a[ordered];z=x[:,2]-x[:,0]
 return {'three_station_count':int(valid.sum()),'station_order_inversions':int((valid&~ordered).sum()),'ordered_count':int(ordered.sum()),'first_to_third_chord_m':np.quantile(z,[0,.05,.5,.95,1]).tolist(),'first_to_middle_chord_m':np.quantile(x[:,1]-x[:,0],[0,.05,.5,.95,1]).tolist(),'middle_to_third_chord_m':np.quantile(x[:,2]-x[:,1],[0,.05,.5,.95,1]).tolist(),'middle_fraction_of_total':np.quantile((x[:,1]-x[:,0])/z,[0,.05,.5,.95,1]).tolist()}
def compare_dict(actual,expected,where):
 for k,v in actual.items():
  if isinstance(v,dict):compare_dict(v,expected[k],where+'/'+k)
  elif isinstance(v,(list,float,int)):assert np.allclose(v,expected[k],atol=2e-11,rtol=1e-12),(where,k,v,expected[k])
  else:assert v==expected[k]
def template(station,facet,radius,width,z,phase):
 a=math.radians(phase+facet*15);c,s=math.cos(a),math.sin(a)
 return dict(id=f'TEMPLATE/B{station}/F{facet}',station=station,kind='barrel',origin_m=[radius*c,radius*s,0],basis=[[-s,0,c],[c,0,s],[0,1,0]],vertices_m=[[-width/2,-z],[width/2,-z],[width/2,z],[-width/2,z]],depth_m=.5)
def entry(p,d):
 n,b=body_planes(p);lo=np.zeros(len(d));hi=np.full(len(d),np.inf);good=np.ones(len(d),bool)
 for a,z in zip(n,b):
  den=dot(d,a);pos=den>1e-12;neg=den< -1e-12
  hi[pos]=np.minimum(hi[pos],z/den[pos]);lo[neg]=np.maximum(lo[neg],z/den[neg]);good&=~((~pos&~neg)&(z<0))
 return np.where(good&(hi>=lo)&(hi>=0),lo,np.inf)
def inside(p,xyz,border=0,tol=1e-12):
 q=np.asarray(p['basis']);x=(xyz-p['origin_m'])@q;v=np.asarray(p['vertices_m']);e=np.roll(v,-1,axis=0)-v
 ok=np.abs(x[:,2])<=p['depth_m']/2+tol
 for a,edge in zip(v,e):ok&=edge[0]*(x[:,1]-a[1])-edge[1]*(x[:,0]-a[0])>=border*np.linalg.norm(edge)-tol*np.linalg.norm(edge)
 return ok

def footprint_inside(p,xyz,border):
 x=(xyz-p['origin_m'])@np.asarray(p['basis']);v=np.asarray(p['vertices_m']);e=np.roll(v,-1,axis=0)-v
 return all(edge[0]*(x[1]-a[1])-edge[1]*(x[0]-a[0])>=border*np.linalg.norm(edge)-1e-12*np.linalg.norm(edge) for a,edge in zip(v,e))

def expand(p,margin):
 p=dict(p);n,b=poly(p);b=b+margin
 p['vertices_m']=[np.linalg.solve(np.array([n[i-1],n[i]]),[b[i-1],b[i]]).tolist() for i in range(4)];p['depth_m']+=2*margin
 return p

def sat(a,b):
 va,vb=vertices(a),vertices(b)
 if np.any(va.max(0)<vb.min(0)-1e-10) or np.any(vb.max(0)<va.min(0)-1e-10):return False
 # Face normals and pairwise edge cross products are a complete SAT axis set.
 na,_=body_planes(a);nb,_=body_planes(b)
 ea=np.r_[va[1:4]-va[:3],(va[0]-va[3])[None],(va[4]-va[0])[None]]
 eb=np.r_[vb[1:4]-vb[:3],(vb[0]-vb[3])[None],(vb[4]-vb[0])[None]]
 axes=np.r_[na,nb,np.cross(ea[:,None],eb[None,:]).reshape(-1,3)];axes=axes[np.linalg.norm(axes,axis=1)>1e-12]
 axes/=np.linalg.norm(axes,axis=1)[:,None];aa,bb=va@axes.T,vb@axes.T
 return not np.any((aa.max(0)<bb.min(0)-1e-10)|(bb.max(0)<aa.min(0)-1e-10))
def readrows(p):return list(csv.DictReader(io.StringIO(raw(p).decode())))

def main(args):
 global REPO
 REPO=pathlib.Path(args.repo);start=time.time()
 g=js(SCOPE+'candidate/geometry.json');old=js(BASE);ctrl=js(SCOPE+'candidate/geometry-controls.json');art=js(SCOPE+'artifacts.json');vr=js(SCOPE+'native-validation/validation.json');view=js(SCOPE+'views/views.json');cfg=js('tools/muon_layout/sketched-stagger-config.json')
 RESULT['hashes']={p:sha(raw(p)) for p in [SCOPE+'README.md',SCOPE+'candidate/geometry.json',SCOPE+'native-validation/validation.json',SCOPE+'native-validation/full-sphere-inputs-and-distances.npz',SCOPE+'artifacts.json','tools/muon_layout/sketched_validation.py']}
 for report in [art,vr,view]:
  for p,h in report['source_sha256'].items():assert sha(raw(p))==h,(p,h)
  for p,h in report['source_sha256'].items():assert raw(p)==raw(p,'65cf2741bd697ddb8c4022a751f275b41f63241e'),p
 assert sha(raw(BASE))==cfg['base_geometry_sha256']==art['baseline_geometry_sha256']
 assert raw(BASE)==raw(BASE,cfg['input_revision'])
 assert sha(raw(SCOPE+'candidate/geometry.json'))==art['geometry_sha256']==vr['geometry_sha256']==view['after_geometry_sha256']
 assert g['magnetic_configuration']==old['magnetic_configuration'] and g['supports']==old['supports']
 for selection in [lambda p:p['kind']=='endcap',lambda p:p['kind']=='barrel' and p['station']==3]:assert [p for p in g['panels'] if selection(p)]==[p for p in old['panels'] if selection(p)]
 u=js(SCOPE+'unchanged-evidence.json')
 for x in u['files']:
  path=x['path'];a=raw(path);assert sha(a)==x['sha256'] and a==raw(path,u['baseline_revision']),path
  CACHE.pop((REV,path),None);CACHE.pop((u['baseline_revision'],path),None)
 assert len(u['files'])==709
 mf=js(SCOPE+'inputs/source-manifest.json');archive=tarfile.open(fileobj=io.BytesIO(raw(SCOPE+'inputs/source-blobs.tar.gz')))
 assert len(archive.getmembers())==20==len(mf['files'])
 for x in mf['files']:
  content=archive.extractfile(x['archive_path']).read();rev,p=x['locator'].split(':',1)
  assert sha(content)==x['sha256'] and len(content)==x['bytes'] and content==raw(p,rev),x['locator']
 record('identities',{'source_freeze':'65cf2741bd697ddb8c4022a751f275b41f63241e','source_hashes_match':True,'fixed_geometry_identical':True,'prior_files':709,'source_archive_blobs':20})
 panels=g['panels'];changed=[p for p in panels if p['kind']=='barrel' and p['station']<3];members=g['supports']['members']
 counts={k:dict(collections.Counter(str(p['station']) for p in panels if p['kind']==k)) for k in ['barrel','endcap']}
 families={str(s):len({tuple(np.round(np.ptp(np.asarray(p['vertices_m']),axis=0),12)) for p in panels if p['kind']=='barrel' and p['station']==s}) for s in [1,2,3]}
 assert len(panels)==936 and len(changed)==312 and len(members)==484 and counts==ctrl['counts']
 assert families=={'1':2,'2':4,'3':9}
 for p in changed:
  assert p['coil_certificate']['clear'] and p['coil_certificate']['source_fingerprint']==ctrl['coil_certificate_cache']['source_fingerprint']
  assert p['coil_certificate']['symmetry']=='fresh actual-orientation source proof; no historical or rotated proof reuse'
  assert p['support_certificate']['clear'] and p['support_certificate']['total_members']==484
 for p in panels:
  q=np.asarray(p['basis']);assert np.allclose(q.T@q,np.eye(3),atol=1e-12) and np.linalg.det(q)>.999999
  if p['kind']=='barrel' and p['station']==1:
   f=int(p['id'].split('/F')[1][:2]);assert abs(np.linalg.norm(p['origin_m'][:2])-(4.63 if f%2 else 5.2))<1e-12
  if p['kind']=='barrel' and p['station']==2:assert abs((p['compartment']['phi_deg']-7.5)%15)<1e-10
 vv=np.concatenate([vertices(p) for p in panels]);rr=np.hypot(vv[:,0],vv[:,1]);maxr=float(rr.max())
 assert maxr<9.1 and abs(vv[:,2]).max()<13.3
 record('inventory',{'counts':counts,'changed_panels':len(changed),'support_members':len(members),'barrel_families':families,'max_corner_radius_m':maxr,'world_radial_margin_m':9.1-maxr,'map_radial_margin_m':9.5-maxr})
 # Full-sphere retained bank independently regenerated.
 bank=np.load(io.BytesIO(raw(SCOPE+'native-validation/full-sphere-inputs-and-distances.npz')));d=bank['direction'];rng=np.random.default_rng(40088);mu=rng.uniform(-1,1,65536);phi=rng.uniform(0,2*np.pi,65536)
 fresh=np.c_[np.sqrt(1-mu*mu)*np.cos(phi),np.sqrt(1-mu*mu)*np.sin(phi),mu]
 assert np.array_equal(fresh,d) and np.array_equal(bank['eta'],np.arctanh(mu)) and np.array_equal(bank['phi_rad'],phi)
 assert np.max(abs(np.linalg.norm(d,axis=1)-1))<1e-14
 fixed=[p for p in panels if p['kind']!='barrel' or p['station']==3]
 noframe=[p for p in g['without_support_panels'] if p['kind']=='barrel' and p['station']<3]+fixed
 templates=[]
 for s in [1,2]:
  for f in range(24):
   r=4.63 if s==1 and f%2 else [5.2,6.7][s-1]
   h=(5.2-.25)*math.tan(math.pi/24)-.01
   a=math.atan((h-.03)/(5.2+.25));odd=(4.63+.25)*math.tan(math.radians(15.1)-a)+.03
   w=odd if s==1 and f%2 else ([5.2,6.7][s-1]-.25)*math.tan(math.pi/24)-.01
   templates.append(template(s,f,r,2*w,[6.4456,9.2][s-1],0 if s==1 else 7.5))
 primary={}
 for border,label in [(0,'outline'),(.03,'border30mm')]:
  out={};arr={};bars={};maxres=0
  for model,ps in [('before',old['panels']),('after',panels)]:
   arr[model],bars[model]=distances(ps,d,border)
   maxres=max(maxres,eq(arr[model],bank[label+'_'+model+'_station_distance_m'],label+model),eq(bars[model],bank[label+'_'+model+'_barrel_station_distance_m'],label+model+'barrel'))
  a,b=np.isfinite(arr['before']),np.isfinite(arr['after'])
  for k in [1,2,3]:out[f'at_least_{k}_stations']=summary(a.sum(1)>=k,b.sum(1)>=k)
  for s in range(3):out[f'station{s+1}']=summary(a[:,s],b[:,s])
  out['barrel_only']={f'B{s+1}':summary(np.isfinite(bars['before'][:,s]),np.isfinite(bars['after'][:,s])) for s in range(3)}
  mixed1=a.copy();mixed1[:,0]=b[:,0];mixed2=a.copy();mixed2[:,1]=b[:,1]
  out['three_station_component_controls']={'changed_B1_old_B2':summary(a.all(1),mixed1.all(1)),'old_B1_changed_B2':summary(a.all(1),mixed2.all(1))}
  loss=a.all(1)&~b.all(1);nf=np.isfinite(distances(noframe,d,border)[0]).all(1);tm=np.isfinite(distances(templates+fixed,d,border)[0]).all(1)
  masks={'fixed_frame_packing':loss&nf,'longitudinal_seams_and_packing':loss&~nf&tm,'finite_transverse_or_end_reach':loss&~tm}
  assert np.array_equal(np.sum(list(masks.values()),axis=0),loss.astype(int))
  out['loss_classes']={}
  for name,mask in masks.items():
   assert np.array_equal(mask,bank[label+'_loss_'+name]);ids=np.flatnonzero(mask)
   claimed=vr['full_sphere']['results'][label]['three_station_loss_localization'][name]
   assert ids.tolist()==claimed['direction_ids'] and len(ids)==claimed['count']
   out['loss_classes'][name]={'count':len(ids),'direction_ids_sha256':sha(ids.astype('<i8').tobytes())}
  common=a.all(1)&b.all(1)
  out['common_three_station_spacing']={k:spacing(x[common]) for k,x in arr.items()};out['spacing']={k:spacing(x) for k,x in arr.items()};out['barrel_only_spacing']={k:spacing(x) for k,x in bars.items()}
  cmp={k:v for k,v in out.items() if k not in ['loss_classes']};compare_dict(cmp,vr['full_sphere']['results'][label],label)
  out['archive_maximum_distance_residual_m']=maxres;primary[label]=out;record(label,{k:v for k,v in out.items() if k in ['at_least_3_stations','loss_classes','archive_maximum_distance_residual_m']})
 RESULT['primary']=primary
 # Entire entrance reserves: radial barrel planes, and axial first endcap face.
 barrel_min=min(np.linalg.norm(p['origin_m'][:2])-p['depth_m']/2 for p in panels if p['kind']=='barrel')
 endcap_min=min(abs(p['origin_m'][2])-p['depth_m']/2 for p in panels if p['kind']=='endcap')
 t=np.minimum(4.35/np.hypot(d[:,0],d[:,1]),6.4684/abs(d[:,2]));starts=(t+1e-5)[:,None]*d
 eq(starts,bank['start_m'],'starts');inside_ids=[p['id'] for p in panels if inside(p,starts).any()];assert not inside_ids
 first=np.minimum.reduce([entry(p,d) for p in panels]);finite=np.isfinite(first);gap=first[finite]-(t[finite]+1e-5)
 assert (gap>0).all()
 record('entrance',{'entire_radial_reserve_m':barrel_min-4.35-1e-5,'entire_axial_reserve_m':endcap_min-6.4684-1e-5,'inside_starts':0,'minimum_sampled_start_to_first_prism_entry_m':float(gap.min()),'R4_60_radial_reserve_m':4.60-.25-4.35-1e-5})
 # Independent full SAT against all actual support orientations and chamber pairs.
 bounds=np.array([[vertices(p).min(0),vertices(p).max(0)] for p in panels]);pair_broad=0;conflicts=[]
 for i,p in enumerate(panels):
  jj=np.flatnonzero(np.all(bounds[i,1]>=bounds[i+1:,0]-1e-10,axis=1)&np.all(bounds[i,0]<=bounds[i+1:,1]+1e-10,axis=1))+i+1
  pair_broad+=len(jj)
  for j in jj:
   if sat(p,panels[j]):conflicts.append([i,int(j)])
 assert not conflicts
 expanded=[expand(p,.05) for p in members];sb=np.array([[vertices(p).min(0),vertices(p).max(0)] for p in expanded]);n_support=0
 for p in changed:
  v=vertices(p);take=np.flatnonzero(np.all(v.max(0)>=sb[:,0]-1e-10,axis=1)&np.all(v.min(0)<=sb[:,1]+1e-10,axis=1));n_support+=len(take)
  assert not [members[j]['id'] for j in take if sat(p,expanded[j])],p['id']
 assert sat(changed[0],changed[0]) and sat(members[0],expanded[0])
 neighbor=[]
 for f in range(24):assert not sat(templates[f],expand(templates[(f+1)%24],.02));neighbor.append(f)
 def neighbor_gap(r):
  even=(5.2-.25)*math.tan(math.pi/24)-.01;ang=math.radians(15.1)-math.atan((even-.03)/5.45);odd=(r+.25)*math.tan(ang)+.03
  return 4.95-((r+.25)*math.cos(math.pi/12)+odd*math.sin(math.pi/12))
 assert neighbor_gap(4.65)<.02 and 4.60-.25-4.325<.05
 diagdir=np.array([[math.cos(math.pi/12),math.sin(math.pi/12),1/4.35]]);diagdir/=np.linalg.norm(diagdir,axis=1)[:,None]
 diagstart=diagdir*(4.35/np.hypot(diagdir[:,0],diagdir[:,1])+1e-5)[:,None]
 assert inside(template(1,1,4.60,2*odd,6.4456,0),diagstart)[0] and not inside(templates[1],diagstart)[0]
 record('independent_SAT',{'all_panel_pairs':len(panels)*(len(panels)-1)//2,'broad_phase_panel_pairs':pair_broad,'conflicts':conflicts,'support_pair_considerations':len(changed)*len(members),'support_exact_SAT_pairs':n_support,'neighbor_pairs':len(neighbor),'B1_gap_m':neighbor_gap(4.63),'R4_65_gap_m':neighbor_gap(4.65),'R4_60_service_gap_m':4.60-.25-4.325,'positive_duplicate_and_support_adverse_controls':True})
 native_checks(g,vr)
 artifact_checks(g,old,art,view)
 helper_interface_check(args)
 supplemental(g,old,vr)
 RESULT['findings']=[{'id':'SS-P1-F1','severity':'minor / non-blocking scope metadata','locator':REV+':'+SCOPE+'native-validation/validation.json#limits[0]','finding':'The top-level limit says geometric fractions use the restricted barrel bank, while this artifact now also contains a full_sphere result. The scoped full_sphere metadata and README are correct.','requested_correction':'Scope this sentence to geometric_bank; preserve original acquisition/source identities and all scientific arrays.'}]
 RESULT['passed_bounded_checks']=True
 RESULT['recommendation']='Scientific geometry claims supported within the stated prototype scope; clarify F1. No response, reconstruction, engineering or human acceptance.'
 RESULT['initial_checker_diagnostic']='An initial curved-border audit wrongly imposed 1e-12 depth membership on native roots with allowed O(10 nm) plane residual. Corrected to separate finite-face tolerance (1e-6 m) from footprint-only 30 mm border (1e-12 m); contiguous source-normal entry/exit pairing and zero-field analytic masks then agree. An input.dat count header was also corrected in the review parser.'
 RESULT['elapsed_seconds']=time.time()-start;RESULT['checker_sha256']=sha(pathlib.Path(__file__).read_bytes());RESULT['repo_files_changed']=[];RESULT['runtime']={'python':sys.version,'numpy':np.__version__}
 target=pathlib.Path(args.output);assert str(target).startswith('/private/tmp/pr90-SS-P1-');target.write_text(json.dumps(RESULT,indent=2,allow_nan=False)+'\n');print('WROTE',target,flush=True)

def native_checks(g,vr):
 out={};panels=g['panels']
 for name,inp in [('straight','straight-inputs.npz'),('curved-smoke','curved-inputs.npz')]:
  pre=SCOPE+'native-validation/'+name+'/';tracks=readrows(pre+'tracks.csv');hits=readrows(pre+'hits.csv');faces=readrows(pre+'geometry.csv');data=np.load(io.BytesIO(raw(SCOPE+'native-validation/'+inp)))
  assert [int(x['track_id']) for x in tracks]==list(range(len(data['track_id'])))
  statuses=dict(collections.Counter(x['status'] for x in tracks));assert statuses==vr['native_reports'][name]['statuses']
  assert len(faces)==len({x['geometry_id'] for x in faces})==5616
  fmap={};events=collections.defaultdict(list);max_plane=0.;max_source=0.
  for x in faces:
   i,f=int(x['panel_index']),int(x['face_index']);p=panels[i];n,b=body_planes(p)
   normal=np.array([float(x['n'+a]) for a in ['x','y','z']]);center=np.array([float(x['c'+a+'_m']) for a in ['x','y','z']])
   plane=int(np.argmin(abs(n@center-b)));residual=float(abs(n[plane]@center-b[plane]));max_source=max(max_source,residual)
   assert residual<1e-12 and abs(abs(normal@n[plane])-1)<1e-12 and inside(p,center[None])[0]
   assert bool(int(x['is_large']))==(plane>=4)
   fmap[i,f]=(x,plane,n[plane])
  assert all({fmap[i,k][1] for k in range(6)}==set(range(6)) for i in range(936))
  for row in hits:
   i,f,tid=int(row['panel_index']),int(row['face_index']),int(row['track_id']);p=panels[i];xyz=np.array([float(row[a+'_m']) for a in ['x','y','z']]);info,plane,normal=fmap[i,f]
   assert row['geometry_id']==info['geometry_id'] and inside(p,xyz[None],tol=1e-6)[0]
   center=np.array([float(info['c'+a+'_m']) for a in ['x','y','z']]);max_plane=max(max_plane,abs(normal@(xyz-center)))
   if p['kind']=='barrel':
    direction=np.array([float(row['d'+a]) for a in ['x','y','z']]);sense=float(direction@normal)
    # Border tests concern the footprint; the already audited curved depth-face
    # point may have the native solver's O(10 nm) plane residual.
    events[tid,i].append((plane,footprint_inside(p,xyz,.03),float(row['path_m']),sense))
  assert max_plane<1e-6
  masks=np.zeros((len(tracks),3),bool);borders=masks.copy();reentries=0
  for (tid,i),es in events.items():
   entered=None;previous_path=-np.inf
   for plane,active,path,sense in es:
    assert path>=previous_path-1e-10;previous_path=path
    if abs(sense)<1e-10:continue
    if sense<0:
     assert entered is None,('orphan entry',name,tid,i);entered=(plane,active)
    else:
     assert entered is not None,('orphan exit',name,tid,i)
     if entered[0]>=4 and plane>=4 and entered[0]!=plane:
      masks[tid,panels[i]['station']-1]=True
      if entered[1] and active:borders[tid,panels[i]['station']-1]=True
     entered=None
  rec={'tracks':len(tracks),'statuses':statuses,'raw_hits':len(hits),'native_faces':5616,'maximum_plane_residual_m':max_plane,'station_counts':masks.sum(0).tolist(),'border_station_counts':borders.sum(0).tolist(),'three_barrel_pairs':int(masks.all(1).sum()),'three_border_barrel_pairs':int(borders.all(1).sum()),'analytic_mismatches':None}
  for a,b in [('station_counts','station_paired_counts'),('border_station_counts','border_station_paired_counts'),('three_barrel_pairs','three_barrel_pairs'),('three_border_barrel_pairs','three_border_barrel_pairs')]:assert rec[a]==vr['native_reports'][name][b],(name,a,rec[a],vr['native_reports'][name][b])
  if name=='straight':
   prediction=distances(panels,data['direction'],0)[1];predborder=distances(panels,data['direction'],.03)[1]
   assert np.array_equal(masks,np.isfinite(prediction)) and np.array_equal(borders,np.isfinite(predborder));rec['analytic_mismatches']=0
  else:
   assert len(tracks)==256 and statuses=={'completed':197,'field_masked':59}
   assert np.array_equal(data['momentum_GeV'],np.repeat([5.,5.,100.,100.],64)) and np.array_equal(data['charge'],np.repeat([-1,1,-1,1],64))
  out[name]=rec
 record('native_retained_rows',out)

def artifact_checks(g,old,art,view):
 panels=g['panels'];out={}
 for name in ['obj/native-inspection','native-validation/straight','native-validation/curved-smoke']:
  rows=readrows(SCOPE+name+'/geometry-corners.csv');seen=collections.defaultdict(list)
  for r in rows:seen[int(r['panel_index'])].append([float(r[k+'_m']) for k in ['x','y','z']])
  assert len(seen)==936
  residual=0.
  for i,p in enumerate(panels):
   actual=np.array(seen[i]);want=vertices(p);dist=np.linalg.norm(actual[:,None]-want[None,:],axis=2);residual=max(residual,float(dist.min(1).max()),float(dist.min(0).max()))
  assert residual<1e-12;out[name]={'panels':len(seen),'corner_residual_m':residual}
 for name,files in art['obj_artifacts'].items():
  for p,h in files.items():assert sha(raw(SCOPE+'obj/'+p))==h,p
 for zname in art['zip_checks']:
  z=zipfile.ZipFile(io.BytesIO(raw(SCOPE+'obj/'+zname)));assert len(z.namelist())==(2 if zname=='chambers-and-coils.zip' else 6)
  for p in z.namelist():assert z.read(p)==raw(SCOPE+'obj/'+p)
 for p,h in view['artifacts'].items():assert sha(raw(SCOPE+'views/'+p))==h
 # Source polygons, independently from finite corners and exact z intersection.
 for model,label in [(old,'before'),(g,'after')]:
  pp={p['id']:p for p in model['panels']};want=[]
  for p in model['panels']:
   if p['kind']!='barrel':continue
   v=vertices(p);lo,hi=v[:,2].min(),v[:,2].max()
   if lo<=.5<=hi:want.append(p['id'])
  assert set(want)=={x['id'] for x in view['cuts'][label]}
  for x in view['cuts'][label]:
   v=vertices(pp[x['id']])[:,:2];unique=np.unique(np.round(v,10),axis=0);shown=np.asarray(x['xy_m'])
   assert len(unique)==4 and np.max(np.min(np.linalg.norm(unique[:,None]-shown[None,:],axis=2),axis=1))<2e-10
  for x in view['longitudinal'][label]:
   p=pp[x['id']];assert p['vertices_m']==x['vertices_tangent_z_m'] and abs(np.linalg.norm(p['origin_m'][:2])-x['radius_m'])<1e-12
 # Ensure actual SVG blue paths have geometry transforms matching retained input
 # polygons. matplotlib axes transforms are recoverable from subplot clip rects.
 svg=ET.fromstring(raw(SCOPE+'views/barrel-cross-sections.svg'));ns={'s':'http://www.w3.org/2000/svg'}
 clips={x.attrib['id']:x.find('s:rect',ns).attrib for x in svg.findall('.//s:clipPath',ns)};blue=[]
 for p in svg.findall('.//s:path',ns):
  if 'fill: #0060fe' not in p.attrib.get('style','') or 'clip-path' not in p.attrib:continue
  pts=np.array([float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?',p.attrib['d'])]).reshape(-1,2);blue.append((p,pts))
 # Count is stronger than a metadata hash: every full-view and zoom chamber path
 # must occur, including paths clipped outside zoom. Infer axis by clip x order.
 assert len(blue)==2*(len(view['cuts']['before'])+len(view['cuts']['after']))
 rects=sorted({p.attrib['clip-path'][5:-1] for p,_ in blue},key=lambda k:(float(clips[k]['y']),float(clips[k]['x'])))
 maxsvg=0.;counts=[]
 for axis,k in enumerate(rects):
  rec=clips[k];x,y,w,h=map(float,[rec[t] for t in ['x','y','width','height']]);label='before' if axis%2==0 else 'after';zoom=axis>=2
  xl,yl=([3.7,5.7],[-.3,3.1]) if zoom else (view['common_xy_limits_m'],view['common_xy_limits_m'])
  paths=[v for p,v in blue if p.attrib['clip-path'][5:-1]==k];shapes=view['cuts'][label];assert len(paths)==len(shapes)
  for v,s in zip(paths,shapes):
   q=np.asarray(s['xy_m']);expected=np.c_[x+(q[:,0]-xl[0])/(xl[1]-xl[0])*w,y+h-(q[:,1]-yl[0])/(yl[1]-yl[0])*h]
   residual=float(np.max(np.min(np.linalg.norm(v[:,None]-expected[None,:],axis=2),axis=1)));maxsvg=max(maxsvg,residual)
  counts.append(len(paths))
 assert maxsvg<2e-5,maxsvg
 out['actual_svg']={'blue_polygon_paths':len(blue),'axes_counts':counts,'max_path_pixel_residual':maxsvg};out['zip_identity']=True;out['source_view_polygons']=True
 record('artifacts',out)

def helper_interface_check(args):
 # Reuse the exact pinned SS-A1 checker mathematics; ONLY scratch path guards
 # and scratch directory prefixes are adapted to this assignment's owned paths.
 # The primary ray/SAT/event/SVG work above imports no helper mathematics.
 original=raw(SCOPE+'interface-check.py').decode()
 adapted=original.replace('/private/tmp/pr90-SS-A1-','/private/tmp/pr90-SS-P1-').replace("prefix='pr90-SS-A1-src-'","prefix='pr90-SS-P1-src-'")
 assert adapted!=original
 script=pathlib.Path('/private/tmp/pr90-SS-P1-interface-adapter.py');script.write_text(adapted)
 candidate=pathlib.Path('/private/tmp/pr90-SS-P1-candidate.json');candidate.write_bytes(raw(SCOPE+'candidate/geometry.json'))
 output='/private/tmp/pr90-SS-P1-interface-replayed.json'
 command=[sys.executable,'-B',str(script),'--repo',str(REPO),'--revision','a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f','--candidate',str(candidate),'--output',output]
 r=subprocess.run(command,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 data=json.loads(pathlib.Path(output).read_text());assert data['passed_bounded_checks']
 audit=data['candidate_audit'];assert audit['changed_barrel_count']==312 and len(audit['fresh_actual_orientation_coil'])==312 and not audit['all484_support_conflicts']
 record('pinned_interface_helper_replay',{'original_checker_sha256':sha(original.encode()),'adapter_sha256':sha(adapted.encode()),'adaptation':'scratch prefix only; mathematics unchanged','command':command,'results':output,'all_changed_uncached_coil_audits':312,'full_z_B1_templates':24,'full_z_B2_templates':24,'actual_HCAL_steel_cover_bodies':data['b1_full_z_template_checks']['actual_HCAL_steel_and_cover_count'],'passed':True,'independence_limit':'Pinned implementation coil-distance kernel reused; this is reproduction, not independent coil mathematics.'})

def supplemental(g,old,vr):
 # Exact field identity, complete native input rows, and retained central bank.
 assert sha(raw(vr['unchanged_field_source']))==vr['unchanged_field_npz_sha256']
 assert raw(vr['unchanged_field_source'])==raw(vr['unchanged_field_source'],'a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f')
 straight=np.load(io.BytesIO(raw(SCOPE+'native-validation/straight-inputs.npz')));rng=np.random.default_rng(906320);mu=rng.uniform(0,np.tanh(1),512);ph=rng.uniform(0,2*np.pi,512)
 first=np.c_[np.sqrt(1-mu*mu)*np.cos(ph),np.sqrt(1-mu*mu)*np.sin(ph),mu];directions=np.r_[first,first*[1,1,-1]]
 assert np.array_equal(directions,straight['direction'])
 assert np.all(straight['momentum_GeV']==100) and np.all(straight['charge']==1)
 for name in ['straight','curved-smoke']:
  data=np.load(io.BytesIO(raw(SCOPE+'native-validation/'+('straight-inputs.npz' if name=='straight' else 'curved-inputs.npz'))))
  rows=np.loadtxt(io.BytesIO(raw(SCOPE+'native-validation/'+name+'/input.dat')),skiprows=1)
  assert np.allclose(rows[:,0],data['track_id']) and np.allclose(rows[:,1],data['momentum_GeV']) and np.allclose(rows[:,2],data['charge'])
  eq(rows[:,3:6],data['start_m'],name+' input starts');eq(rows[:,6:9],data['direction'],name+' input directions')
 # Inventory CSV dimensions and JSON display families from actual source.
 for model,label in [(old,'before'),(g,'after')]:
  pp={p['id']:p for p in model['panels']};rows=readrows(SCOPE+'inventory/'+label+'-panels-unrounded.csv');assert set(x['panel_id'] for x in rows)==set(pp)
  for x in rows:
   p=pp[x['panel_id']];assert float(x['depth_m'])==p['depth_m']
   if p['kind']=='barrel':assert np.allclose([float(x['tangential_width_m']),float(x['longitudinal_length_m'])],np.ptp(p['vertices_m'],axis=0),rtol=0,atol=1e-12)
  inv=js(SCOPE+'inventory/'+label+'-barrel.json');assert sum(len(f['panel_ids']) for f in inv['families'])==sum(p['kind']=='barrel' for p in pp.values())
  for f in inv['families']:
   for ident in f['panel_ids']:
    p=pp[ident];key=np.rint(np.r_[np.ptp(p['vertices_m'],axis=0),p['depth_m']]/1e-9).astype(int)
    assert key.tolist()==f['dimension_grid_key']
 # All OBJ objects: closed edges, positive enclosed volume, declared material,
 # every blue corner versus actual finite source prism.
 objresults={};expected_names={'chamber_'+p['id'].replace('/','_'):p for p in g['panels']}
 for name in ['chambers-and-coils','barrel-chambers','positive-endcap-chambers','toroids-and-frame']:
  objects=[];verts=[];current=None;mtllib=[]
  for line in raw(SCOPE+'obj/'+name+'.obj').decode().splitlines():
   tok=line.split()
   if not tok:continue
   if tok[0]=='mtllib':mtllib.append(tok[1])
   elif tok[0]=='o':current={'name':tok[1],'faces':[],'materials':set()};objects.append(current)
   elif tok[0]=='v':verts.append(list(map(float,tok[1:4])))
   elif tok[0]=='usemtl':current['materials'].add(tok[1])
   elif tok[0]=='f':current['faces'].append([int(x.split('/')[0])-1 for x in tok[1:]])
  verts=np.array(verts);assert mtllib==[name+'.mtl'] and len(objects)==len({x['name'] for x in objects})
  mtl=raw(SCOPE+'obj/'+name+'.mtl').decode();declared=set(re.findall(r'^newmtl (\S+)',mtl,re.M));bluecount=0;residual=0.;volumes=[]
  for obj in objects:
   assert obj['materials']<=declared and len(obj['materials'])==1
   edges=collections.Counter();signed=0.;allv=[]
   for face in obj['faces']:
    q=verts[face];allv.extend(face)
    # Weld coordinates since native OBJ deliberately duplicates per-face verts.
    keys=[tuple(np.round(x,11)) for x in q]
    for a,b in zip(keys,keys[1:]+keys[:1]):edges[tuple(sorted([a,b]))]+=1
    for k in range(1,len(q)-1):signed+=float(q[0]@np.cross(q[k],q[k+1]))/6
   assert all(n==2 for n in edges.values()) and abs(signed)>1e-9,(name,obj['name'])
   volumes.append(abs(signed))
   if obj['name'] in expected_names:
    p=expected_names[obj['name']];want=vertices(p);actual=verts[allv];dist=np.linalg.norm(actual[:,None]-want[None,:],axis=2);residual=max(residual,float(dist.min(1).max()),float(dist.min(0).max()));bluecount+=1
    area=abs(np.sum(np.asarray(p['vertices_m'])[:,0]*np.roll(np.asarray(p['vertices_m'])[:,1],-1)-np.asarray(p['vertices_m'])[:,1]*np.roll(np.asarray(p['vertices_m'])[:,0],-1)))/2
    assert abs(abs(signed)-area*p['depth_m'])<1e-10
    assert obj['materials']=={'material_0_96_255'}
  assert residual<1e-12
  objresults[name]={'objects':len(objects),'blue_chambers':bluecount,'maximum_chamber_corner_residual_m':residual,'closed_all_objects':True,'materials':sorted(declared)}
 assert [objresults[x]['objects'] for x in ['chambers-and-coils','barrel-chambers','positive-endcap-chambers','toroids-and-frame']]==[972,744,96,520]
 record('inventory_OBJ_field_and_inputs',{'OBJ':objresults,'inventory_source_rows':936,'field_npz_sha256':vr['unchanged_field_npz_sha256'],'native_inputs_verified':True,'native_binary_verified_only_as_recorded_fingerprint':vr['native_binary_sha256']})

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--repo',default=str(REPO));ap.add_argument('--output',default='/private/tmp/pr90-SS-P1-results.json');args=ap.parse_args()
 try:main(args)
 except Exception as exc:
  RESULT['failure']={'type':type(exc).__name__,'message':str(exc)}
  pathlib.Path(args.output).write_text(json.dumps(RESULT,indent=2,allow_nan=False)+'\n');raise
