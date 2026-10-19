#!/usr/bin/env python3
"""Read-only DES040 checks, portable after copying into docs/validation/DES-040.

 python3 independent-spotchecks.py --root /path/to/checkout --git-root /path/to/checkout --output report.json
The root may be an immutable git-show snapshot. No layout/map/energy regeneration
or repository mutation occurs. Only an explicit --output path is written.
"""
from pathlib import Path
import argparse,hashlib,json,math,subprocess,sys,itertools,time
import numpy as np
sys.dont_write_bytecode=True
REV='8e93a131aa5f6d186f27a1a050221d5be50d0633'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def vv(body):
 p=np.asarray(body['vertices_m']);local=np.array([[x,y,z] for z in [-body['depth_m']/2,body['depth_m']/2] for x,y in p]);return local@np.asarray(body['basis']).T+body['origin_m']
def bounds(body):v=vv(body);return v.min(0),v.max(0)
def area(p):p=np.array(p);return .5*np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
def offset(body,margin):
 p=np.asarray(body['vertices_m']);e=np.roll(p,-1,axis=0)-p;n=np.column_stack((e[:,1],-e[:,0]));n/=np.linalg.norm(n,axis=1)[:,None];b=np.sum(n*p,axis=1)+margin
 out=dict(body);out['vertices_m']=[np.linalg.solve(np.array([n[j-1],n[j]]),[b[j-1],b[j]]).tolist() for j in range(4)];out['depth_m']=body['depth_m']+2*margin;return out
def independent_intersects(a,b,tol=1e-10):
 a,b=vv(a),vv(b);faces=[[0,1,2,3],[4,5,6,7]]+[[j,(j+1)%4,(j+1)%4+4,j+4] for j in range(4)]
 edges=[];axes=[]
 for v in [a,b]:
  ee=np.array([v[1]-v[0],v[2]-v[1],v[3]-v[2],v[0]-v[3],v[4]-v[0]]);edges.append(ee)
  axes.extend(np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]]) for f in faces)
 axes.extend(np.cross(edges[0][:,None,:],edges[1][None,:,:]).reshape(-1,3));axes=np.array(axes);norm=np.linalg.norm(axes,axis=1);axes=axes[norm>1e-12]/norm[norm>1e-12,None]
 aa,bb=a@axes.T,b@axes.T
 return not bool(np.any((aa.max(0)<bb.min(0)-tol)|(bb.max(0)<aa.min(0)-tol)))
def independent_hits(panels,d,border):
 distances={k:np.full((3,len(d)),np.inf) for k in ['outer','active','depth']}
 for body in panels:
  basis=np.array(body['basis']);origin=np.array(body['origin_m']);den=d@basis[:,2];t=np.divide(origin@basis[:,2],den,out=np.full(len(d),np.inf),where=abs(den)>1e-12);possible=np.flatnonzero(np.isfinite(t)&(t>0))
  if not len(possible):continue
  p=np.array(body['vertices_m']);e=np.roll(p,-1,axis=0)-p;length=np.linalg.norm(e,axis=1)
  def within(s):
   q=(s[:,None]*d[possible]-origin)@basis
   # Signed edge cross-product distance, independently from polygon_planes.
   cross=e[:,0][None,:]*(q[:,1,None]-p[:,1])-e[:,1][None,:]*(q[:,0,None]-p[:,0])
   return cross/length
  edge=within(t[possible]);outer=(edge>=-1e-12).all(1);active=(edge>=border-1e-12).all(1);depth=active.copy()
  for sign in [-1,1]:
   tf=t[possible]+sign*body['depth_m']/2/den[possible];depth&=(within(tf)>=border-1e-12).all(1)&(tf>0)
  for key,good in [('outer',outer),('active',active),('depth',depth)]:
   ids=possible[good];j=body['station']-1;distances[key][j,ids]=np.minimum(distances[key][j,ids],t[ids])
 return distances

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',required=True,type=Path);ap.add_argument('--git-root',type=Path);ap.add_argument('--revision',default=REV);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--rays',type=int,default=16384);args=ap.parse_args();start=time.monotonic();root=args.root.resolve();sys.path.insert(0,str(root))
 from tools.muon_layout import geometry as g
 from tools.muon_layout.coverage import panel_hits
 from tools.muon_layout.support import material_parts,build_supports
 from tools.toroid_prototype.geometry import coil_mask,group_mask
 folder=root/'docs/validation/DES-040';read=lambda name:json.loads((folder/name).read_text());G=read('geometry.json');R=read('results.json');checks=[]
 def add(name,**v):checks.append(dict(name=name,passed=True,**v))
 for path,h in R['inputs'].items():assert sha(root/path)==h,path
 for path,h in R['magnetic_inputs'].items():assert sha(root/path)==h,path
 for path,h in R['artifacts'].items():assert sha(folder/path)==h,path
 F=read('figures.json')
 for path,h in F['inputs'].items():assert sha(root/path)==h,path
 for path,h in F['outputs'].items():assert sha(folder/path)==h,path
 assert G['magnetic_configuration']==json.loads((root/'docs/validation/DES-039/results.json').read_text())['configuration']
 invariance=read('magnetic-invariance.json');assert invariance['file_count']==52 and invariance['all_unchanged']
 if args.git_root:
  for item in invariance['files']:
   values=[]
   for revision in [invariance['base_revision'],args.revision]:values.append(hashlib.sha256(subprocess.check_output(['git','-C',str(args.git_root),'show',revision+':'+item['path']])).hexdigest())
   assert values[0]==values[1]==item['base_sha256']==item['current_sha256'],item['path']
 add('generated_source_artifact_figure_hashes_and_magnetic_inheritance',input_files=len(R['inputs']),invariant_files_verified=52 if args.git_root else 0)
 P=G['panels'];assert len(P)==1560 and len({p['id'] for p in P})==1560;minimum_area=math.inf;minimum_long=math.inf;minimum_radial=math.inf
 all_samples=[]
 for p in P:
  q=np.array(p['basis']);poly=np.array(p['vertices_m']);assert np.allclose(q.T@q,np.eye(3),atol=1e-12) and np.linalg.det(q)>.999999999
  assert len(poly)==4 and area(poly)>=.25 and p['depth_m']==.5;minimum_area=min(minimum_area,float(area(poly)))
  if p['kind']=='barrel':
   assert np.allclose(poly,[[poly[:,0].min(),poly[:,1].min()],[poly[:,0].max(),poly[:,1].min()],[poly[:,0].max(),poly[:,1].max()],[poly[:,0].min(),poly[:,1].max()]])
   minimum_long=min(minimum_long,float(np.ptp(poly[:,1])));assert np.ptp(poly[:,1])>=.5-1e-12
  else:
   assert p['kind']=='endcap' and p['side'] in [-1,1];assert np.isclose(poly[0,0],poly[3,0]) and np.isclose(poly[1,0],poly[2,0]);minimum_radial=min(minimum_radial,float(np.ptp(poly[:,0])));assert np.ptp(poly[:,0])>=.5-1e-12
  assert p['coil_certificate']['clear'];v=vv(p);all_samples.extend(v);all_samples.append(v.mean(0));all_samples.extend((v[:4]+v[4:])/2)
 samples=np.array(all_samples);assert not coil_mask(samples,G['magnetic_configuration'],clearance=.05).any()
 rng=np.random.default_rng(40191);hard=np.argsort([p['coil_certificate']['cells'] for p in P])[-16:];ids=np.unique(np.r_[hard,rng.choice(len(P),32,False)])
 for i in ids:assert g.certify_coil_clear(P[i],G['magnetic_configuration'],clearance=.05,resolution=.02)['clear']
 add('actual_panel_shape_dimensions_all_sampled_volumes_and_bounded_certificate_recalculation',panels=len(P),minimum_area_m2=minimum_area,minimum_longitudinal_span_m=minimum_long,minimum_actual_trapezoid_radial_span_m=minimum_radial,coil_mask_points=len(samples),recomputed_full_volume_certificates=len(ids))
 # Complete broad phase using expanded support AABBs, followed by independent SAT.
 pb=np.array([bounds(p) for p in P]);panel_pairs=0
 for i,p in enumerate(P):
  near=np.flatnonzero(((pb[i,1]>=pb[i+1:,0])&(pb[i,0]<=pb[i+1:,1])).all(1))+i+1
  for k in near:panel_pairs+=1;assert not independent_intersects(p,P[k]),(p['id'],P[k]['id'])
 expanded=[offset(b,.05) for b in G['supports']['members']];sb=np.array([bounds(b) for b in expanded]);support_pairs=0
 for i,p in enumerate(P):
  near=np.flatnonzero(((sb[:,1]>=pb[i,0])&(sb[:,0]<=pb[i,1])).all(1))
  for k in near:support_pairs+=1;assert not independent_intersects(p,expanded[k]),(p['id'],expanded[k]['id'])
 add('all_actual_panel_panel_and_fifty_mm_support_clearance_pairs_independent_SAT',panel_broadphase_pairs=panel_pairs,support_broadphase_pairs=support_pairs)
 supports=G['supports'];rebuilt=build_supports(G['configuration'])
 for key in ['members','ports','ground','case_ids']:assert supports[key]==rebuilt[key],key
 parts={m['id']:material_parts(m) for m in supports['members']};by_part={p['id']:p for pp in parts.values() for p in pp};contacts=R['support_validation']['contacts']
 for rec in contacts:
  a,b=[by_part[n] for n in rec['parts']];assert independent_intersects(a,b)
  if rec['kind']=='overlapping_material':assert independent_intersects(a,offset(b,-1e-7))
  else:assert rec['kind']=='material_face_contact' and rec['area_m2']>1e-10 and not independent_intersects(a,offset(b,-1e-7))
 nodes=set(supports['case_ids'])|{m['id'] for m in supports['members']}|{m['id'] for m in supports['ground']};adj={n:set() for n in nodes}
 for a,b in R['support_validation']['graph_edges']:assert a in nodes and b in nodes;adj[a].add(b);adj[b].add(a)
 reached=set();todo=[m['id'] for m in supports['ground']]
 while todo:
  n=todo.pop()
  if n not in reached:reached.add(n);todo.extend(adj[n]-reached)
 assert reached==nodes
 for ground in supports['ground']:
  body=next(b for b in supports['members'] if b['id']==ground['member_id']);v=vv(body);assert abs(v[:,1].min()-ground['floor_y_m'])<1e-10
 add('rebuilt_support_geometry_all_recorded_material_contacts_and_explicit_ground_graph',material_parts=len(by_part),contacts=len(contacts),nodes=len(nodes),grounded_cases=len(supports['case_ids']),grounds=len(supports['ground']))
 # Independent arithmetic on random full-sphere rays, compared ray-by-ray.
 mu=rng.uniform(-1,1,args.rays);phi=rng.uniform(0,2*np.pi,args.rays);d=np.column_stack((np.sqrt(1-mu*mu)*np.cos(phi),np.sqrt(1-mu*mu)*np.sin(phi),mu));own=independent_hits(P,d,.03);reference=panel_hits(P,d,.03);fractions={};z_scores={}
 for key in own:
  np.testing.assert_allclose(own[key],reference[key],rtol=2e-15,atol=2e-13);count=np.isfinite(own[key]).sum(0);fractions[key]={str(n):float(np.mean(count==n)) for n in range(4)}
  headline=R['independent_integration']['coverage'][key]['fractions']['3'];value=fractions[key]['3'];se=math.sqrt(headline*(1-headline)/args.rays+R['independent_integration']['coverage'][key]['standard_error']['3']**2);z_scores[key]=(value-headline)/se;assert abs(z_scores[key])<5
 assert np.all(np.isfinite(own['depth']).sum(0)<=np.isfinite(own['active']).sum(0)) and np.all(np.isfinite(own['active']).sum(0)<=np.isfinite(own['outer']).sum(0))
 complete=np.isfinite(own['active']).all(0);assert np.all(np.diff(own['active'][:,complete],axis=0)>0)
 add('independent_cross_product_plane_and_depth_arithmetic_all_phi_both_ends',rays=args.rays,seed=40191,station_fractions=fractions,headline_comparison_standard_deviations=z_scores,counts_match_implementation=True)
 with np.load(folder/'coverage.npz') as data:
  mu,phi=data['mu'],data['phi_deg'];assert len(mu)==480 and len(phi)==1440;assert np.allclose(mu,-1+(np.arange(480)+.5)*2/480);assert np.allclose(phi,(np.arange(1440)+.5)*360/1440)
  assert abs(480*1440*(2/480)*(2*np.pi/1440)-4*np.pi)<1e-13
  for key in ['outer','active','depth']:
   a=data[key+'_count'];assert a.shape==(480,1440)
   for n in range(4):assert np.mean(a==n)==R['coverage']['fractions'][key][str(n)]
  for name in ['support','coil']:
   for region in ['any','upstream','between']:assert float(data[name+'_'+region].mean())==R['coverage'][name+'_shadows']['fractions_full_sphere'][region]
 add('all_serialized_grid_counts_route_tag_fractions_full_four_pi_denominator',grid=[480,1440],solid_angle_sr=4*math.pi,grid_is_not_converged=R['sampling']['max_absolute_station_fraction_change']>.04)
 for name in ['support_mass','support_mass_coarse']:
  M=R[name];assert math.isclose(sum(v['unique_mass_kg'] for v in M['materials'].values()),M['unique_mass_kg'],rel_tol=1e-14)
  for mat,v in M['materials'].items():
   gross=sum(area(p['vertices_m'])*p['depth_m'] for p in by_part.values() if p['material']==mat);assert math.isclose(gross,v['gross_stock_volume_m3'],rel_tol=1e-13);assert math.isclose(v['unique_union_volume_m3']*v['density_kg_m3'],v['unique_mass_kg'],rel_tol=1e-14)
 z=(R['support_mass']['unique_mass_kg']-R['support_mass_coarse']['unique_mass_kg'])/math.hypot(R['support_mass']['combined_statistical_standard_error_kg'],R['support_mass_coarse']['combined_statistical_standard_error_kg']);assert abs(z)<5
 add('actual_hollow_part_gross_volume_mass_arithmetic_and_existing_seed_sensitivity',mass_seed_difference_standard_deviations=z,scope='No independent full union-mass integration or engineering uncertainty estimate repeated.')
 result=dict(status='READ-ONLY V1 bounded independent spotchecks; no human approval',reviewed_revision=args.revision,script_sha256=sha(Path(__file__)),checks=checks,elapsed_seconds=time.monotonic()-start,independence='Independent serialized-prism vertex/SAT and plane-edge arithmetic; reused analytic coil mask/certificate and material-wall decomposition. P1 authored planning/math only, not implementation. No full packing/map/energy/1million-ray regeneration.',limits=['Sampling and shared geometry helpers do not supply a second solid-model kernel or continuum proof.','Grid aliasing remains explicit; random integration errors exclude geometry/response/material uncertainty.','Case ports concern warm reservations; no pressure boundary, force/stiffness, chamber mount or precision qualification.'])
 args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
