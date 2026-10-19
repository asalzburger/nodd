#!/usr/bin/env python3
"""Independent OBJ/MTL/ZIP geometry audit; no exporter imports or ACTS runs."""
import argparse,collections,csv,hashlib,io,json,math,re,subprocess,sys,zipfile
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
REV='8b24dc692713d27bbfbfac04209e095437cc8c13'
P='docs/validation/DES-040/obj/'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--revision',default=REV);p.add_argument('--output',type=Path,required=True);p.add_argument('--native-corners',type=Path);a=p.parse_args();cache={}
 def get(path,rev=None):
  k=(rev or a.revision,path)
  if k not in cache:cache[k]=subprocess.check_output(['git','-C',str(a.root),'show',k[0]+':'+path])
  return cache[k]
 evidence=json.loads(get(P+'export.json'));geometry=json.loads(get('docs/validation/DES-040/geometry.json'));panels=geometry['panels'];config=geometry['magnetic_configuration']
 obj=get(P+'chambers-and-coils.obj');mtl=get(P+'chambers-and-coils.mtl');bundle=get(P+'chambers-and-coils.zip')
 for name,digest in evidence['artifacts'].items():assert sha(get(P+name))==digest
 assert sha(get('docs/validation/DES-040/geometry.json'))==evidence['geometry_sha256']
 for name,digest in evidence['source_sha256'].items():assert sha(get(name,evidence['source_revision']))==digest==sha(get(name))
 with zipfile.ZipFile(io.BytesIO(bundle)) as z:
  assert set(z.namelist())=={'chambers-and-coils.obj','chambers-and-coils.mtl'} and z.testzip() is None
  for name in z.namelist():assert z.read(name)==get(P+name)
 material={};name=None
 for line in mtl.decode().splitlines():
  item=line.split()
  if not item:continue
  if item[0]=='newmtl':name=item[1];assert name not in material;material[name]={}
  else:material[name][item[0]]=list(map(float,item[1:]))
 assert set(material)=={'material_0_96_255','material_160_160_160'}
 for name,rgb in [('material_0_96_255',[0,96,255]),('material_160_160_160',[160,160,160])]:
  for key in ['Ka','Kd','Ks']:assert np.max(abs(np.array(material[name][key])-np.array(rgb)/256))<5e-7
 verts=[];objects={};current=None;mat=None;references=[];records=collections.Counter()
 for line in obj.decode().splitlines():
  words=line.split()
  if not words or words[0].startswith('#'):continue
  kind=words[0];records[kind]+=1
  if kind=='mtllib':assert words[1:]==['chambers-and-coils.mtl'];references+=words[1:]
  elif kind=='o':current=words[1];assert current not in objects;objects[current]=[]
  elif kind=='usemtl':mat=words[1];assert mat in material
  elif kind=='v':assert len(words)==4;verts.append(list(map(float,words[1:])))
  elif kind=='f':
   ids=np.array([int(w)-1 for w in words[1:]]);assert len(ids)==4 and ids.min()>=0 and ids.max()<len(verts)
   assert current is not None;objects[current].append((mat,ids))
  else:raise AssertionError('unexpected OBJ record '+kind)
 v=np.array(verts);assert v.shape==(187200,3) and np.isfinite(v).all();assert references==['chambers-and-coils.mtl']
 assert len(objects)==1596 and sum(len(f) for f in objects.values())==46800
 expected_chambers={'chamber_'+re.sub('[^A-Za-z0-9_.-]','_',b['id']):b for b in panels}
 expected_coils={f'coil_{family}_{k:02d}':(family,k,group) for family,group in config['coil_groups'].items() for k in range(12)}
 assert set(objects)==set(expected_chambers)|set(expected_coils)
 native={}
 if a.native_corners:
  raw=a.native_corners.read_bytes();assert sha(raw)==evidence['native_face_corners_sha256']
  for row in csv.DictReader(io.StringIO(raw.decode())):native.setdefault((int(row['panel_index']),int(row['face_index'])),[]).append([float(row[k+'_m']) for k in 'xyz'])
 chamber_index={name:i for i,name in enumerate(expected_chambers)}
 max_source=0.;max_native=0.;max_chamber_volume=0.;max_chord=0.;min_coil_normal=1.;symmetry={};coil_results=[];signed_volumes=[];weld_counts={};seams=0
 for name,face_records in objects.items():
  faces=np.array([v[idx] for _,idx in face_records]);colors={m for m,_ in face_records}
  assert colors==({'material_0_96_255'} if name in expected_chambers else {'material_160_160_160'})
  # ObjVisualization3D duplicates vertices per face: closure is geometric after
  #1nm coordinate welding, not shared raw OBJ index topology.
  keys=np.round(faces.reshape(-1,3),9);unique,index=np.unique(keys,axis=0,return_inverse=True);idx=index.reshape(-1,4)
  assert np.all(np.array([len(set(x)) for x in idx])==4)
  directed=collections.Counter((int(x),int(y)) for q in idx for x,y in zip(q,np.roll(q,-1)));edges=collections.Counter(tuple(sorted((int(x),int(y)))) for q in idx for x,y in zip(q,np.roll(q,-1)))
  assert set(edges.values())=={2} and all(directed[(y,x)]==n for (x,y),n in directed.items())
  euler=len(unique)-len(edges)+len(faces);assert euler==(2 if name in expected_chambers else 0)
  normals=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);length=np.linalg.norm(normals,axis=1);assert (length>1e-15).all();normals/=length[:,None]
  volume=sum(float(np.einsum('ij,ij->i',faces[:,0],np.cross(faces[:,j],faces[:,j+1])).sum())/6 for j in [1,2]);assert volume>0;signed_volumes.append(volume)
  weld_counts[name]=len(unique);seams+=1
  if name in expected_chambers:
   b=expected_chambers[name];xy=np.array(b['vertices_m']);basis=np.array(b['basis']);origin=np.array(b['origin_m']);h=b['depth_m']/2
   source=np.vstack([np.c_[xy,np.full(4,w)] for w in [-h,h]])@basis.T+origin
   dist=np.linalg.norm(faces.reshape(-1,3)[:,None,:]-source[None,:,:],axis=2);max_source=max(max_source,float(dist.min(1).max()));assert dist.min(1).max()<1e-10 and np.all(dist.min(0)<1e-10)
   assert len(faces)==6 and len(unique)==8
   assert np.all(np.einsum('ij,ij->i',normals,faces.mean(1)-source.mean(0))>0)
   area=abs(np.sum(xy[:,0]*np.roll(xy[:,1],-1)-xy[:,1]*np.roll(xy[:,0],-1)))/2
   max_chamber_volume=max(max_chamber_volume,abs(volume-float(area)*b['depth_m']))
   if native:
    for f in range(6):
     raw=np.array(native[chamber_index[name],f]);d=np.linalg.norm(faces[f][:,None,:]-raw[None,:,:],axis=2);max_native=max(max_native,float(d.min(0).max()),float(d.min(1).max()));assert max_native<1e-10
  else:
   family,k,g=expected_coils[name];angle=np.deg2rad(g['phi_offset_deg']+k*30);er=np.array([np.cos(angle),np.sin(angle),0]);et=np.array([-np.sin(angle),np.cos(angle),0]);u=faces@er;t=faces@et;z=faces[:,:,2];rz=np.stack([u,z],axis=-1);rel=rz-[g['center_r_m'],g['center_z_m']];half=np.array([g['half_r_m'],g['half_z_m']]);rho=g['corner_radius_m'];a0=config['warm']['normal_m']/2;b0=config['warm']['tangent_m']/2
   def sdf(x):
    q=np.abs(x-[g['center_r_m'],g['center_z_m']])-(half-rho);return np.linalg.norm(np.maximum(q,0),axis=-1)+np.minimum(q.max(-1),0)-rho
   assert len(faces)==1040 and len(unique)==1040 and np.max(abs(abs(t)-b0))<1e-12 and np.max(abs(abs(sdf(rz))-a0))<1e-12
   assert abs(u.min()-(g['center_r_m']-g['half_r_m']-a0))<1e-12 and abs(u.max()-(g['center_r_m']+g['half_r_m']+a0))<1e-12
   assert abs(z.min()-(g['center_z_m']-g['half_z_m']-a0))<1e-12 and abs(z.max()-(g['center_z_m']+g['half_z_m']+a0))<1e-12
   mid=rz.mean(1);tangential=np.ptp(t,axis=1)<1e-12;expected=np.zeros_like(normals);expected[tangential]=np.sign(t.mean(1)[tangential,None])*et
   curve=~tangential;delta=mid[curve]-[g['center_r_m'],g['center_z_m']];q=np.maximum(abs(delta)-(half-rho),0)*np.sign(delta);q/=np.linalg.norm(q,axis=1)[:,None];q*=np.sign(sdf(mid[curve]))[:,None];expected[curve]=q[:,:1]*er+q[:,1:]*[0,0,1]
   alignment=np.einsum('ij,ij->i',normals,expected);min_coil_normal=min(min_coil_normal,float(alignment.min()));assert alignment.min()>1-1e-10
   deviation=abs(abs(sdf(mid[curve]))-a0);measured=float(deviation.max());max_chord=max(max_chord,measured);bound=(rho+a0)*(1-np.cos(np.pi/(4*64)));assert measured<=bound+1e-12 and measured>bound-1e-10
   # Polygonal area deficit has a known chord formula, independent of exporter.
   perimeter=4*(g['half_r_m']+g['half_z_m']-2*rho)+2*np.pi*rho;exact=4*a0*b0*perimeter;theta=np.pi/(2*64);deficit=4*a0*b0*rho*256*(theta-np.sin(theta));assert abs(volume-(exact-deficit))<1e-10
   local=np.unique(np.round(np.stack([u,t,z],axis=-1).reshape(-1,3),9),axis=0)
   if family not in symmetry:symmetry[family]=local
   else:assert np.array_equal(local,symmetry[family])
   coil_results.append(dict(name=name,mesh_volume_m3=volume,analytic_sweep_volume_m3=exact,chord_volume_deficit_m3=exact-volume,max_chord_deviation_m=measured,z_range_m=[float(z.min()),float(z.max())]))
 assert max_source<1e-10 and max_chamber_volume<1e-10 and max_chord<1e-4
 # Verify all original R3 scientific artifacts remain unchanged, excluding
 # additions that record this visualization and its review.
 roots=['tools/muon_layout/acts','docs/validation/DES-040/acts-propagation','docs/validation/DES-039','tools/toroid_prototype','tools/muon_study','docs/design/DES-040-muon-chambers-frame.md','docs/validation/DES-040/geometry.json']
 base='2f1d12b440b2d4e6c34bfeb88133fd4161c240df';files=subprocess.check_output(['git','-C',str(a.root),'ls-tree','-r','--name-only',base,*roots],text=True).splitlines()
 for file in files:assert subprocess.check_output(['git','-C',str(a.root),'rev-parse',base+':'+file])==subprocess.check_output(['git','-C',str(a.root),'rev-parse',a.revision+':'+file])
 result=dict(assignment='OBJ-R1',revision=a.revision,passed=True,human_approval=False,findings=[],
  input_hashes={name:sha(get(P+name)) for name in ['chambers-and-coils.obj','chambers-and-coils.mtl','chambers-and-coils.zip','export.json']},
  objects=dict(total=len(objects),chambers=len(expected_chambers),coils=len(expected_coils),raw_vertices=len(v),quads=sum(len(o) for o in objects.values()),materials=material,relative_mtllib=references[0],zip_exact_two_payload_files=True),
  mesh=dict(geometrically_closed_objects=seams,weld_tolerance_m=1e-9,raw_vertex_indices_face_local=True,chamber_euler_characteristic=2,coil_euler_characteristic=0,all_faces_consistently_outward=True,minimum_positive_signed_volume_m3=min(signed_volumes),minimum_coil_normal_dot_analytic_outward=min_coil_normal),
  fidelity=dict(max_chamber_source_corner_residual_m=max_source,max_native_corner_residual_m=max_native if native else None,native_corner_cache_checked=bool(native),max_chamber_volume_error_m3=max_chamber_volume,max_measured_coil_chord_deviation_m=max_chord,all36full_extents_match_source=True,all3families_C12_verified=True,units='metres; right-handed; beam z',unchanged_scientific_files=len(files)),
  coil_volumes=coil_results,
  scope='Current chamber solids plus36analytic warm-envelope allocations only; not windings, internals, Boolean-union cases, field or performance',
  limitations=['Closure is after geometric1nm welding; raw ACTS OBJ vertices are face-local.','Warm allocations can overlap and remain separately named; summed mesh volume is not their union.','Curve approximation is bounded by94.123micrometres, not exact analytic arcs.','No new ACTS execution, installation modification, transport or engineering approval.'])
 a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({k:result[k] for k in ['passed','objects','mesh','fidelity']},indent=2))
if __name__=='__main__':main()
