#!/usr/bin/env python3
"""Independent actual OBJ/MTL/ZIP and inventory audit. No exporter imports."""
import argparse,collections,hashlib,io,json,math,re,subprocess,zipfile
from pathlib import Path
import numpy as np
REV='0576b7a615c81d1687f0cf7a3ceb0ca310478481';D='docs/validation/DES-040/wheels-2026-10-20/'
def sha(x):return hashlib.sha256(x).hexdigest()
def main(a):
 cache={};hashes={}
 def get(path):
  if path not in cache:cache[path]=subprocess.check_output(['git','-C',str(a.repo),'show',a.revision+':'+path]);hashes[path]=sha(cache[path])
  return cache[path]
 def js(p):return json.loads(get(p))
 g=js(D+'candidate/geometry.json');old=js('docs/validation/DES-040/geometry.json');export=js(D+'obj-revised/export.json');panels=g['panels'];config=g['magnetic_configuration'];sanitize=lambda x:re.sub('[^A-Za-z0-9_.-]','_',x)
 chambers={'chamber_'+sanitize(p['id']):p for p in panels};frame={'frame_'+sanitize(p['id']):p for p in g['supports']['members']};coils={f'coil_{family}_{k:02d}':(family,k,c) for family,c in config['coil_groups'].items() for k in range(12)}
 allsource={**chambers,**frame};reports={};maxcorner=0.;maxvolume=0.;mincoilnorm=1.;maxchord=0.
 for tag in ['chambers-and-coils','barrel-chambers','positive-endcap-chambers','toroids-and-frame']:
  mtl=get(D+'obj-revised/'+tag+'.mtl').decode();mats={};name=None
  for line in mtl.splitlines():
   x=line.split()
   if not x:continue
   if x[0]=='newmtl':name=x[1];assert name not in mats;mats[name]={}
   else:mats[name][x[0]]=list(map(float,x[1:]))
  for name,props in mats.items():
   rgb=[0,96,255] if name=='material_0_96_255' else [160,160,160];assert name in ['material_0_96_255','material_160_160_160']
   for k in ['Ka','Kd','Ks']:assert np.max(abs(np.array(props[k])-np.array(rgb)/256))<5e-7
  verts=[];objects={};mat=None;current=None;refs=[]
  for line in get(D+'obj-revised/'+tag+'.obj').decode().splitlines():
   x=line.split()
   if not x or x[0].startswith('#'):continue
   if x[0]=='mtllib':assert x[1:]==[tag+'.mtl'];refs+=x[1:]
   elif x[0]=='o':current=x[1];assert current not in objects;objects[current]=[]
   elif x[0]=='usemtl':mat=x[1];assert mat in mats
   elif x[0]=='v':assert len(x)==4;verts.append(list(map(float,x[1:])))
   elif x[0]=='f':idx=np.array([int(i)-1 for i in x[1:]]);assert len(idx)==4 and idx.min()>=0 and idx.max()<len(verts);objects[current].append((mat,idx))
   else:raise AssertionError(x[0])
  v=np.array(verts);assert np.isfinite(v).all();assert refs==[tag+'.mtl']
  expected=set(chambers)|set(coils) if tag=='chambers-and-coils' else {k for k,p in chambers.items() if p['kind']=='barrel'} if tag=='barrel-chambers' else {k for k,p in chambers.items() if p['kind']=='endcap' and p['origin_m'][2]>0} if tag=='positive-endcap-chambers' else set(frame)|set(coils)
  assert set(objects)==expected;minimum=math.inf;families={};quads=0
  for name,entries in objects.items():
   faces=np.array([v[i] for _,i in entries]);is_coil=name in coils;assert {m for m,_ in entries}==({'material_0_96_255'} if name in chambers else {'material_160_160_160'});quads+=len(faces)
   u,idx=np.unique(np.round(faces.reshape(-1,3),9),axis=0,return_inverse=True);idx=idx.reshape(-1,4);edges=collections.Counter(tuple(sorted((int(i),int(j)))) for f in idx for i,j in zip(f,np.roll(f,-1)));direct=collections.Counter((int(i),int(j)) for f in idx for i,j in zip(f,np.roll(f,-1)))
   assert set(edges.values())=={2} and all(direct[j,i]==n for (i,j),n in direct.items());assert len(u)-len(edges)+len(faces)==(0 if is_coil else 2)
   normal=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);norm=np.linalg.norm(normal,axis=1);assert (norm>1e-15).all();normal/=norm[:,None]
   volume=sum(float(np.einsum('ij,ij->i',faces[:,0],np.cross(faces[:,j],faces[:,j+1])).sum())/6 for j in [1,2]);assert volume>0;minimum=min(minimum,volume)
   if not is_coil:
    p=allsource[name];xy=np.array(p['vertices_m']);Q=np.array(p['basis']);h=p['depth_m']/2;source=np.vstack([np.c_[xy,np.full(4,z)] for z in [-h,h]])@Q.T+p['origin_m'];dist=np.linalg.norm(faces.reshape(-1,3)[:,None]-source[None],axis=2);err=float(dist.min(1).max());maxcorner=max(maxcorner,err);assert err<1e-10 and (dist.min(0)<1e-10).all();assert len(u)==8 and len(faces)==6
    assert (np.einsum('ij,ij->i',normal,faces.mean(1)-source.mean(0))>0).all();area=abs(np.sum(xy[:,0]*np.roll(xy[:,1],-1)-xy[:,1]*np.roll(xy[:,0],-1)))/2;maxvolume=max(maxvolume,abs(volume-area*p['depth_m']))
   else:
    family,k,c=coils[name];angle=math.radians(c['phi_offset_deg']+30*k);er=np.array([math.cos(angle),math.sin(angle),0]);et=np.array([-math.sin(angle),math.cos(angle),0]);rr=faces@er;tt=faces@et;zz=faces[:,:,2];rz=np.stack((rr,zz),axis=-1);rho=c['corner_radius_m'];half=np.array([c['half_r_m'],c['half_z_m']]);center=np.array([c['center_r_m'],c['center_z_m']]);aa=.25;bb=.30
    def sdf(x):q=abs(x-center)-(half-rho);return np.linalg.norm(np.maximum(q,0),axis=-1)+np.minimum(q.max(-1),0)-rho
    assert len(faces)==1040 and len(u)==1040 and np.max(abs(abs(tt)-bb))<1e-12 and np.max(abs(abs(sdf(rz))-aa))<1e-12
    assert abs(zz.min()-(c['center_z_m']-c['half_z_m']-aa))<1e-12 and abs(zz.max()-(c['center_z_m']+c['half_z_m']+aa))<1e-12
    mid=rz.mean(1);tangent=np.ptp(tt,axis=1)<1e-12;out=np.zeros_like(normal);out[tangent]=np.sign(tt.mean(1)[tangent,None])*et;curved=~tangent;q=np.maximum(abs(mid[curved]-center)-(half-rho),0)*np.sign(mid[curved]-center);q/=np.linalg.norm(q,axis=1)[:,None];q*=np.sign(sdf(mid[curved]))[:,None];out[curved]=q[:,:1]*er+q[:,1:]*[0,0,1];dot=np.einsum('ij,ij->i',normal,out);mincoilnorm=min(mincoilnorm,float(dot.min()));assert dot.min()>1-1e-10
    chord=float(abs(abs(sdf(mid[curved]))-aa).max());maxchord=max(maxchord,chord);assert chord<=(rho+aa)*(1-np.cos(np.pi/256))+1e-12
    local=np.unique(np.round(np.stack((rr,tt,zz),axis=-1).reshape(-1,3),9),axis=0)
    if family in families:assert np.array_equal(local,families[family])
    else:families[family]=local
  expected_report=export['checks'][tag];assert len(objects)==expected_report['objects'] and len(v)==expected_report['raw_obj_vertices'] and quads==expected_report['quad_faces']
  reports[tag]={'objects':len(objects),'raw_vertices':len(v),'quad_faces':quads,'geometric_1nm_weld_closure_and_consistent_orientation':True,'minimum_positive_volume_m3':minimum,'bounds_xyz_m':[v.min(0).tolist(),v.max(0).tolist()]}
 zipchecks={}
 for zname,report in export['zip_checks'].items():
  raw=get(D+'obj-revised/'+zname);assert sha(raw)==report['sha256']
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   assert z.namelist()==report['member_names'] and z.testzip() is None
   for name in z.namelist():assert z.read(name)==get(D+'obj-revised/'+name)
  zipchecks[zname]={'exact_sibling_payloads':True,'member_names':report['member_names']}
 for artifact in export['artifacts'].values():
  for name,h in artifact.items():assert sha(get(D+'obj-revised/'+name))==h
 # Dimensions and panel IDs are independently grouped at the declared 1nm grid.
 inventory={}
 for tag,geometry,kind in [('before-endcap',old,'endcap'),('after-endcap',g,'endcap'),('current-barrel',g,'barrel')]:
  data=js(D+'inventory-comparison/'+tag+'.json');selected={p['id']:p for p in geometry['panels'] if p['kind']==kind};seen=set();keys=set()
  for fam in data['families']:
   key=tuple(fam['dimension_grid_key']);keys.add(key)
   for ident in fam['panel_ids']:
    assert ident in selected and ident not in seen;seen.add(ident);p=selected[ident];xy=np.array(p['vertices_m'])
    if kind=='barrel':dims=[np.ptp(xy[:,0]),np.ptp(xy[:,1]),p['depth_m']]
    else:
     lo,hi=xy[:,0].min(),xy[:,0].max();inner=xy[np.isclose(xy[:,0],lo),1];outer=xy[np.isclose(xy[:,0],hi),1];dims=[hi-lo,np.ptp(inner),np.ptp(outer),outer.mean()-inner.mean(),p['depth_m']]
    assert tuple(np.rint(np.array(dims)/1e-9).astype('i8'))==key
  assert seen==set(selected) and len(keys)==data['shape_families'] and len(selected)==data['total_panels'];inventory[tag]={'panels':len(selected),'shape_families':len(keys)}
 invprov=js(D+'inventory-comparison/provenance.json')
 for p,h in invprov['artifacts_sha256'].items():assert sha(get(D+'inventory-comparison/'+p))==h
 figure_hashes={}
 for system in ['before','after']:
  prefix=D+'propagation/'+system+'/';fig=js(prefix+'figures/figures.json');assert fig['analysis_summary_sha256']==sha(get(prefix+'summary.json'))
  for name,info in fig['artifacts'].items():
   blob=get(prefix+'figures/'+name);assert sha(blob)==info['sha256'] and len(blob)==info['bytes'];figure_hashes[system+'/'+name]=info['sha256']
 comp=js(D+'propagation/comparison/comparison.json')
 for name,info in comp['artifacts'].items():assert sha(get(D+'propagation/comparison/'+name))==info['sha256']
 headline=next(c for c in comp['cases'] if c['momentum_GeV']==100 and c['charge']==1)
 headline={region:headline['samples'][region][metric] for region,metric in [('full_sphere','active_paired_stations'),('endcap_caps','endcap_active_paired_stations')]}
 result={'revision':a.revision,'passed':True,'human_approval':False,'actual_OBJ':reports,'propagation_figures_hash_verified':len(figure_hashes),'headline_100GeV_qplus':headline,'zip_payload_checks':zipchecks,'max_source_corner_residual_m':maxcorner,'max_prism_volume_error_m3':maxvolume,'min_coil_normal_dot_analytic_outward':mincoilnorm,'max_coil_chord_deviation_m':maxchord,'inventory':inventory,'input_sha256':hashes,'limits':['Native ObjVisualization3D face-local raw indices require geometric1nm welding for closure.','Frame/prism meshes depict outer reservations; hollow stock cavities and mass unions are not exported.','Coil meshes are separate warm sleeves, not current packs or Boolean union vessels.','No ACTS execution, material transport, reconstruction efficiency or engineering approval.']};a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--revision',default=REV);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
