"""Portable exact-revision input/display checks for PR90 three endcap XY cuts.

Requires Python 3 and NumPy. Reads source through git show; never imports or
writes the working tree. --output is the only retained written artifact.
"""
import argparse, ast, hashlib, itertools, json, math, pathlib, subprocess, tempfile, types
import numpy as np
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=pathlib.Path,required=True)
parser.add_argument('--revision',required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
revision=subprocess.check_output(['git','-C',str(args.repo),'rev-parse','--verify',args.revision+'^{commit}'],text=True).strip()
temporary=tempfile.TemporaryDirectory(prefix='nodd-xy-review-')
BASE=pathlib.Path(temporary.name)
paths=['docs/design/DES-040-muon-chambers-frame.md','docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json','tools/muon_layout/draw.py','tools/muon_layout/support.py','tools/toroid_prototype/geometry.py','tools/muon_layout/geometry.py','docs/validation/DES-040/wheels-2026-10-20/README.md']
source_hashes={}
for path in paths:
 data=subprocess.check_output(['git','-C',str(args.repo),'show',revision+':'+path])
 destination=BASE/path;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
 source_hashes[path]=hashlib.sha256(data).hexdigest()
geometry_path=paths[1]
assert source_hashes[geometry_path]=='621b5cb9d45906b338251d527d932abd6b9aca86c84ffaa0918c7e535a17781f','This checker assesses only the frozen shortened-ECT geometry.' 
g=json.loads((BASE/'docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json').read_text())
# Independent half-plane intersection: footprint and extrusion planes restricted to z=constant.
def cut(body,z):
 p=np.asarray(body['vertices_m']);q=np.asarray(body['basis']);o=np.asarray(body['origin_m'])
 e=np.roll(p,-1,axis=0)-p;n=np.column_stack([e[:,1],-e[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None]
 w=n@q[:,:2].T;ns=np.vstack([w,q[:,2],-q[:,2]])
 bs=np.r_[np.einsum('ij,ij->i',n,p)+w@o,q[:,2]@o+body['depth_m']/2,-q[:,2]@o+body['depth_m']/2]
 A=ns[:,:2];b=bs-ns[:,2]*z;ps=[]
 for i,j in itertools.combinations(range(6),2):
  mat=A[[i,j]]
  if abs(np.linalg.det(mat))<1e-13:continue
  x=np.linalg.solve(mat,b[[i,j]])
  if (A@x<=b+2e-10).all():ps.append(x)
 if len(ps)<3:return None
 ps=np.unique(np.round(ps,10),axis=0);c=ps.mean(axis=0);ps=ps[np.argsort(np.arctan2(ps[:,1]-c[1],ps[:,0]-c[0]))]
 area=abs((ps[:,0]*np.roll(ps[:,1],-1)-ps[:,1]*np.roll(ps[:,0],-1)).sum())/2
 return ps if area>1e-18 else None
# Exact pinned material partition helper with independent dictionary constructor.
def prism(identifier,kind,origin,basis,vertices,depth,**kw):
 return dict(id=identifier,kind=kind,origin_m=np.asarray(origin).tolist(),basis=np.asarray(basis).tolist(),vertices_m=np.asarray(vertices).tolist(),depth_m=depth,**kw)
mod=ast.parse((BASE/'tools/muon_layout/support.py').read_text());f=next(x for x in mod.body if isinstance(x,ast.FunctionDef) and x.name=='material_parts')
ns={'np':np,'math':math,'geo':types.SimpleNamespace(prism=prism)};exec(compile(ast.Module(body=[f],type_ignores=[]),'pinned material_parts','exec'),ns)
parts=[p for m in g['supports']['members'] for p in ns['material_parts'](m)]
def slice_filled(group,z,a):
 hr=group['half_r_m']+a;hz=group['half_z_m']+a;rho=group['corner_radius_m']+a;dz=abs(z-group['center_z_m'])
 if dz>hz:return None
 s=max(0.,dz-(hz-rho));w=hr-rho+math.sqrt(max(0.,rho*rho-s*s));return [group['center_r_m']-w,group['center_r_m']+w]
def intervals(group,z,a):
 out=slice_filled(group,z,a)
 if out is None:return []
 inside=slice_filled(group,z,-a)
 return [out] if inside is None else [[out[0],inside[0]],[inside[1],out[1]]]
result={'input_revision':revision,'geometry_sha256':source_hashes[geometry_path],'source_sha256':source_hashes,'method':'Independent restricted half-plane intersection, pinned hollow-stock partition, analytic rounded-rectangle offset interval slices.','total_frame_material_parts':len(parts),'wheels':[]}
for z in [6.7456,9.5,12.8]:
 row={'z_m':z};allcuts={}
 for name,bodies in [('endcap',[p for p in g['panels'] if p['kind']=='endcap']),('barrel',[p for p in g['panels'] if p['kind']=='barrel']),('support_material',parts),('support_outer',g['supports']['members'])]:
  selected=[(b['id'],c) for b in bodies if (c:=cut(b,z)) is not None];allcuts[name]=selected
  points=np.vstack([c for _,c in selected]) if selected else np.zeros((0,2))
  row[name]={'count':len(selected),'ids':[i for i,c in selected],'bounds_m':[points.min(axis=0).tolist(),points.max(axis=0).tolist()] if len(points) else None,'area_sum_m2':float(sum(abs((c[:,0]*np.roll(c[:,1],-1)-c[:,1]*np.roll(c[:,0],-1)).sum())/2 for _,c in selected))}
 row['coil_intervals_u_m']={n:intervals(v,z,g['magnetic_configuration']['warm']['normal_m']/2) for n,v in g['magnetic_configuration']['coil_groups'].items()}
 row['coil_rectangle_count']=sum(12*len(x) for x in row['coil_intervals_u_m'].values())
 # Fixed global-axis negative-end reflection must preserve endcap source-coordinate set.
 pos=sorted(tuple(x) for _,c in allcuts['endcap'] for x in np.round(c,9));neg=sorted(tuple(x) for b in g['panels'] if b['kind']=='endcap' if (c:=cut(b,-z)) is not None for x in np.round(c,9));assert pos==neg
 row['endcap_global_xy_mirror_exact_at_1nm']=True
 result['wheels'].append(row)
# Frozen geometry expectations, independent of any generated figure metadata.
for row, expected in zip(result['wheels'],[(12,36,120,48,24),(108,24,96,24,48),(24,0,0,0,0)]):
 observed=tuple(row[k]['count'] for k in ['endcap','barrel','support_material','support_outer'])+(row['coil_rectangle_count'],)
 assert observed==expected,(row['z_m'],observed,expected)
result['frozen_expected_counts_pass']=True
# Compare pinned edge/plane helper against the separately derived half-plane cuts.
def vertices3(body):
 p=np.asarray(body['vertices_m']);h=body['depth_m']/2;loc=np.vstack([np.column_stack([p,np.full(4,s)]) for s in [-h,h]])
 return loc@np.asarray(body['basis']).T+body['origin_m']
mod=ast.parse((BASE/'tools/muon_layout/draw.py').read_text());f=next(x for x in mod.body if isinstance(x,ast.FunctionDef) and x.name=='section_polygon')
ns2={'np':np,'vertices3':vertices3,'EDGE_INDICES':((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7))};exec(compile(ast.Module(body=[f],type_ignores=[]),'pinned section_polygon','exec'),ns2)
err=0.;count=0
for z in [6.7456,9.5,12.8,-6.7456,-9.5,-12.8]:
 for b in g['panels']+parts:
  a=cut(b,z);v=ns2['section_polygon'](b,[0,0,1],z,[1,0,0],[0,1,0]);assert (a is None)==(v is None),(b['id'],z)
  if a is not None:
   d=np.linalg.norm(a[:,None,:]-v[None,:,:],axis=2);err=max(err,float(d.min(axis=1).max()),float(d.min(axis=0).max()));count+=1
assert err<2e-9
result['section_helper_crosscheck']={'positive_and_negative_planes':6,'body_plane_checks':6*(len(g['panels'])+len(parts)),'nonempty_cuts':count,'max_bidirectional_vertex_distance_m':err,'pass':True}
# membership-vs-analytic slice rectangle validation away from numerical boundary tolerance.
mod=ast.parse((BASE/'tools/toroid_prototype/geometry.py').read_text());names={'_points','rounded_rectangle_distance','group_mask'}
fns=[x for x in mod.body if isinstance(x,ast.FunctionDef) and x.name in names];ns3={'np':np,'math':math};exec(compile(ast.Module(body=fns,type_ignores=[]),'pinned coil mask','exec'),ns3)
rng=np.random.default_rng(905);maskchecks=[]
for z in [6.7456,9.5,12.8,-6.7456,-9.5,-12.8]:
 p=np.column_stack([rng.uniform(-10,10,(131072,2)),np.full(131072,z)])
 for name,group in g['magnetic_configuration']['coil_groups'].items():
  expected=np.zeros(len(p),bool)
  for k in range(12):
   ph=math.radians(group['phi_offset_deg']+k*30);u=p[:,0]*math.cos(ph)+p[:,1]*math.sin(ph);v=-p[:,0]*math.sin(ph)+p[:,1]*math.cos(ph)
   for lo,hi in intervals(group,z,.25):expected|=(u>=lo)&(u<=hi)&(abs(v)<=.3)
  actual=ns3['group_mask'](p,group,12,.5,.6);assert np.array_equal(expected,actual),(z,name)
  maskchecks.append({'z_m':z,'group':name,'points':len(p),'mismatches':0})
result['analytic_coil_crosscheck']={'seed':905,'queries':131072*18,'checks':maskchecks,'pass':True}
# Explicit coincident-face, outside and edge tangency fixtures for source helper.
fixture=prism('FIXTURE','test',[0,0,0],np.eye(3),[[-1,-1],[1,-1],[1,1],[-1,1]],2)
assert ns2['section_polygon'](fixture,[0,0,1],1,[1,0,0],[0,1,0]) is not None
assert ns2['section_polygon'](fixture,[0,0,1],1.001,[1,0,0],[0,1,0]) is None
sq=2**-.5
assert ns2['section_polygon'](fixture,[sq,sq,0],2*sq,[sq,-sq,0],[0,0,1]) is None
result['section_adverse_fixtures']={'coincident_face_retained':True,'outside_body_omitted':True,'edge_tangent_omitted':True}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'revision':revision,'output':str(args.output),'body_plane_checks':result['section_helper_crosscheck']['body_plane_checks'],'max_vertex_distance_m':err,'analytic_coil_queries':result['analytic_coil_crosscheck']['queries'],'passed':True},indent=2))
