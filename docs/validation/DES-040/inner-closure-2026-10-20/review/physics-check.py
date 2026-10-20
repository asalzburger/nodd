#!/usr/bin/env python3
"""Focused independent PhysVal check; standard library only; reads immutable Git blobs."""
import argparse,hashlib,itertools,json,math,platform,random,re,subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--revision',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert re.fullmatch('[0-9a-f]{40}',a.revision)
base='docs/validation/DES-040/inner-closure-2026-10-20/'
def read(path,rev=None):return subprocess.check_output(['git','-C',str(a.repo),'show',(rev or a.revision)+':'+path])
def obj(path,rev=None):return json.loads(read(path,rev))
def sha(b):return hashlib.sha256(b).hexdigest()
def dot(u,v):return sum(x*y for x,y in zip(u,v))
def cross(u,v):return u[0]*v[1]-u[1]*v[0]
def sub(u,v):return [x-y for x,y in zip(u,v)]
def area(poly):return sum(cross(x,y) for x,y in zip(poly,poly[1:]+poly[:1]))/2

def planes(poly,border=0):
 r=[]
 for u,v in zip(poly,poly[1:]+poly[:1]):
  d=sub(v,u);length=math.hypot(*d);n=[d[1]/length,-d[0]/length];r.append((n,dot(n,u)-border))
 return r

def clip(poly,n,b):
 out=[]
 if not poly:return out
 for x,y in zip(poly,poly[1:]+poly[:1]):
  fx,fy=dot(n,x)-b,dot(n,y)-b
  if fx<=0:out.append(x)
  if (fx<0<fy) or (fy<0<fx):out.append([x[j]+fx/(fx-fy)*(y[j]-x[j]) for j in range(2)])
 return out

def cone(poly,front,back,border=0):
 out=[[-2.,-2.],[2.,-2.],[2.,2.],[-2.,2.]]
 for n,b in planes(poly,border):
  out=clip(out,n,b/front);out=clip(out,n,b/back)
 return out

def solid_angle(poly,nsteps=128):
 # Green's theorem: curl((-y,x)/(s*(s+1)))=(1+x*x+y*y)^(-3/2), s=sqrt(1+r*r).
 # This line integral is independent of the source's spherical-triangle sum.
 result=0.
 for x,y in zip(poly,poly[1:]+poly[:1]):
  d=sub(y,x);v=[]
  for k in range(nsteps+1):
   t=k/nsteps;r=[x[j]+t*d[j] for j in range(2)];s=math.sqrt(1+dot(r,r));v.append(cross(x,d)/(s*(s+1)))
  result+=(v[0]+v[-1]+4*sum(v[1:-1:2])+2*sum(v[2:-1:2]))/(3*nsteps)
 return result

def inside(poly,point):return all(dot(n,point)<=b+1e-12 for n,b in planes(poly))
def overlaps(poly,other):
 for n,_ in planes(poly)+planes(other):
  if max(dot(n,x) for x in poly)<min(dot(n,x) for x in other)-1e-11 or max(dot(n,x) for x in other)<min(dot(n,x) for x in poly)-1e-11:return False
 return True

def rotate(poly,t):
 c,s=math.cos(t),math.sin(t);return [[x*c-y*s,x*s+y*c] for x,y in poly]

def vertices(body):
 q=body['basis'];o=body['origin_m'];h=body['depth_m']/2
 return [[o[k]+q[k][0]*x+q[k][1]*y+q[k][2]*z for k in range(3)] for z in [-h,h] for x,y in body['vertices_m']]

def hull(points):
 ss=sorted(set(map(tuple,points)))
 def half(seq):
  h=[]
  for x in seq:
   while len(h)>1 and cross(sub(h[-1],h[-2]),sub(x,h[-1]))<=1e-12:h.pop()
   h.append(x)
  return h
 return half(ss)[:-1]+half(ss[::-1])[:-1]

def minrad(poly):
 ans=min(math.hypot(*x) for x in poly)
 for x,y in zip(poly,poly[1:]+poly[:1]):
  d=sub(y,x);t=max(0,min(1,-dot(x,d)/dot(d,d)));ans=min(ans,math.hypot(*[x[j]+t*d[j] for j in range(2)]))
 return ans

geo=obj('docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json');m=obj(base+'review/module-check.json');pr=obj(base+'views-provenance.json');di=obj(base+'display-polygons.json');un=obj(base+'unchanged-evidence.json')
sp=geo['wheel_revision']['inner_wheel'];z=sp['abs_z_m'];depth=geo['wheel_revision']['depth_m'];front,back=z-depth/2,z+depth/2;alpha=math.pi/sp['sectors'];c,s=math.cos(alpha),math.sin(alpha);R=sp['outer_radius_m'];r0=sp['inner_radius_m']
mag=geo['magnetic_configuration'];bt=mag['coil_groups']['barrel'];leg=bt['center_r_m']-bt['half_r_m'];clear=geo['wheel_revision']['coil_clearance_m'];an=mag['warm']['normal_m']/2;at=mag['warm']['tangent_m']/2
xlo,xhi=leg-an-clear,leg+an+clear;guard=at+clear+sp['extra_BT_box_margin_m'];umin=xlo*c-guard*s;umax=xhi*c+guard*s

def band(u0,u1,delta):
 w=lambda u:u*math.tan(alpha)-delta/c
 return [[u0,-w(u0)],[u1,-w(u1)],[u1,w(u1)],[u0,w(u0)]]
def outer(delta):
 lo,hi=r0,R
 for _ in range(80):
  mid=(lo+hi)/2
  if math.hypot(mid,mid*math.tan(alpha)-delta/c)>R:hi=mid
  else:lo=mid
 return (lo+hi)/2
current=[b for b in geo['panels'] if b.get('wheel')=='inner_wheel' and b['side']==1]
models={'current_one_band':[current[0]['vertices_m']],'two_bands':[band(r0,umin-.01,.01),band(umin+.01,outer(guard),guard)],'three_bands_slot_localised':[band(r0,umin-.01,.01),band(umin+.01,umax+.01,guard),band(umax+.03,outer(.01),.01)]}
ideal_area=math.pi*(R*R-r0*r0);ideal_solid=2*math.pi*(1/math.sqrt(1+(r0/front)**2)-1/math.sqrt(1+(R/back)**2));ideal_mid=2*math.pi*(1/math.sqrt(1+(r0/z)**2)-1/math.sqrt(1+(R/z)**2))
metrics={};disp_delta=0.;sat_count=0;conflicts=[];svg_results={}
warm=[[leg-an,-at],[leg+an,-at],[leg+an,at],[leg-an,at]];reserved=[[xlo,-at-clear],[xhi,-at-clear],[xhi,at+clear],[xlo,at+clear]]
for name,bands in models.items():
 full=sum(solid_angle(cone(b,front,back)) for b in bands)*12;border=sum(solid_angle(cone(b,front,back,.03)) for b in bands)*12;mid=sum(solid_angle(cone(b,z,z)) for b in bands)*12
 metrics[name]={'face_area_one_end_m2':sum(area(b) for b in bands)*12,'midplane_area_loss_vs_circular_annulus':1-sum(area(b) for b in bands)*12/ideal_area,'IP_midplane_solid_angle_loss':1-mid/ideal_mid,'IP_full_depth_same_chamber_loss':1-full/ideal_solid,'IP_full_depth_same_chamber_border30mm_loss':1-border/ideal_solid,'full_depth_solid_angle_one_end_sr':full,'band_solid_angles_one_sector_sr':[solid_angle(cone(b,front,back)) for b in bands]}
 for k,v in metrics[name].items():
  if k in m['metrics'][name]:assert abs(v-m['metrics'][name][k])<2e-11,(name,k,v)
 display=[]
 for j,b in enumerate(bands):
  assert area(b)>0 and all(cross(sub(b[(k+1)%4],b[k]),sub(b[(k+2)%4],b[(k+1)%4]))>0 for k in range(4))
  for k in range(12):
   bp=rotate(b,alpha+2*alpha*k);display.append(bp)
   for q in range(12):
    sat_count+=1
    if overlaps(bp,rotate(reserved,2*alpha*q)):conflicts.append([name,j,k,q])
 for expected,recorded in zip(display,di['models'][name]):
  disp_delta=max(disp_delta,max(math.dist(x,y) for x,y in zip(expected,recorded['xy_m'])))
 assert len(display)==len(di['models'][name])
 assert disp_delta<1e-12
assert not conflicts
# Actual source bases independently agree with their displayed global polygons.
for b,d in zip(current,di['models']['current_one_band']):
 assert max(math.dist(x[:2],y) for x,y in zip(vertices(b)[:4],d['xy_m']))<1e-12
 for k in range(3):
  for j in range(3):assert abs(sum(b['basis'][i][k]*b['basis'][i][j] for i in range(3))-(k==j))<1e-12

# Entire slab lies in the BT straight section; the warm witness is occupied at every z in it.
negative=band(r0,outer(.01),.01);witness_global=[leg,.1];witness_local=rotate([witness_global],-alpha)[0]
assert inside(negative,witness_local) and not inside(models['current_one_band'][0],witness_local)
assert front>-bt['half_z_m']+bt['corner_radius_m'] and back<bt['half_z_m']-bt['corner_radius_m']
assert abs(witness_global[0]-leg)<=an and abs(witness_global[1])<=at
assert overlaps(rotate(negative,alpha),warm)
# Incorrectly treating seam x=4.30 as the sector-centre u=4.30 is unsafe.
assert overlaps(rotate(band(r0,4.29,.01),alpha),reserved)
a1=cone(band(4.93,outer(.01),.01),front,back);m1=cone(models['three_bands_slot_localised'][-1],front,back)
assert not a1 and area(m1)>0
# One ray crosses both faces in two different radial bands and fails same-module selection.
q=[.6,0];endpoint_hits=[[inside(b,[front*x for x in q]),inside(b,[back*x for x in q])] for b in models['two_bands']]
assert any(v[0] for v in endpoint_hits) and any(v[1] for v in endpoint_hits) and not any(all(v) for v in endpoint_hits)
# Whole-depth support separation using finite vertices, with every nearby member included.
near=[]
for b in geo['supports']['members']:
 vv=vertices(b);zs=[x[2] for x in vv]
 if max(zs)+.05>=front and min(zs)-.05<=back:near.append({'id':b['id'],'min_projected_radius_m':minrad(hull([x[:2] for x in vv]))})
assert len(near)==84 and min(x['min_projected_radius_m'] for x in near)>R+.05

# Source and retained artifact byte identities; records describe precommit drawing sources honestly.
hashes={}
i=obj(base+'review/interface-check.json')
assert sha(read(base+'review/module-check.py'))==m['script_sha256']
for source,digest in {**m['sources'],**pr['source_sha256'],**{k:v['sha256'] for k,v in i['input_identity'].items()}}.items():
 actual=sha(read(source));assert actual==digest,source;hashes[source]=actual
for source,info in pr['artifacts'].items():
 b=read(base+source);assert sha(b)==info['sha256'] and len(b)==info['bytes'],source
identities=0
for path,oid in un['unchanged_Git_blobs'].items():
 for rev in [un['baseline_revision'],a.revision]:
  actual=subprocess.check_output(['git','-C',str(a.repo),'rev-parse',rev+':'+path],text=True).strip();assert actual==oid,path
 identities+=1
index=un['index_exception']['path'];old_index=read(index,un['baseline_revision']);new_index=read(index);assert sha(old_index)==un['index_exception']['baseline_sha256'] and new_index.startswith(old_index)
des='docs/design/DES-040-muon-chambers-frame.md';old_des=read(des,un['baseline_revision']);new_des=read(des);assert new_des.startswith(old_des) and b'## Inner-sector closure feasibility' in new_des[len(old_des):]

# Decode SVG blue paths via the actual axes clipping rectangle; compare exact display coordinates.
for filename,limits,groups in [('inner-closure-comparison.svg',(-5.8,5.8,-5.8,5.8),[(1,'current_one_band'),(4,'two_bands'),(7,'three_bands_slot_localised')]),('bt-clearance-detail.svg',(.55,5.65,-1.2,1.2),[(1,'current_one_band')])]:
 doc=ET.fromstring(read(base+filename));nodes={x.attrib.get('id'):x for x in doc.iter() if 'id' in x.attrib};maxerr=0.;count=0
 for group,name in groups:
  paths=list(nodes['PolyCollection_'+str(group)]);polys=di['models'][name]
  if filename=='bt-clearance-detail.svg':polys=[polys[0],polys[-1]]
  assert len(paths)==len(polys)
  for path,body in zip(paths,polys):
   rect=list(nodes[re.search(r'#([^)]*)',path.attrib['clip-path']).group(1)])[0].attrib
   sx,sy=float(rect['width'])/(limits[1]-limits[0]),float(rect['height'])/(limits[3]-limits[2]);left,top=float(rect['x']),float(rect['y'])
   coords=list(map(float,re.findall(r'-?\d+(?:\.\d+)?(?:e[-+]?\d+)?',path.attrib['d'])))
   for (x,y),(px,py) in zip(body['xy_m'],zip(coords[::2],coords[1::2])):maxerr=max(maxerr,math.hypot((px-left)/sx+limits[0]-x,limits[3]-(py-top)/sy-y))
   count+=1
 assert maxerr<4e-8,(filename,maxerr)
 svg_results[filename]={'chamber_paths_checked':count,'max_physical_vertex_delta_m':maxerr}

# Small independent common iid bank, with sector rotation reduction; no transport or response.
rng=random.Random(20261020);N=65536;hits={n:0 for n in models};cmin=1/math.sqrt(1+(R/back)**2);cmax=1/math.sqrt(1+(r0/front)**2)
plan={n:[planes(b) for b in bb] for n,bb in models.items()}
for _ in range(N):
 ct=rng.uniform(cmin,cmax);ph=rng.uniform(-alpha,alpha);t=math.sqrt(1-ct*ct)/ct;q=[t*math.cos(ph),t*math.sin(ph)]
 for name,bb in plan.items():
  hit=any(all(dot(n,q)*front<=b and dot(n,q)*back<=b for n,b in pp) for pp in bb)
  hits[name]+=hit
mc={}
for name,hits_n in hits.items():
 loss=1-hits_n/N;se=math.sqrt(loss*(1-loss)/N);sig=(loss-metrics[name]['IP_full_depth_same_chamber_loss'])/se;assert abs(sig)<4
 mc[name]={'loss':loss,'standard_error':se,'mc_minus_independent_integral_sigma':sig}
out={'assignment':'IC-P1','reviewed_revision':a.revision,'status':'Independent technical assessment; no human acceptance','passed':True,'checker_sha256':sha(Path(__file__).read_bytes()),'runtime':{'python':platform.python_version(),'dependencies':'Python standard library only'},'metrics':metrics,'denominators':{'ideal_area_one_end_m2':ideal_area,'ideal_full_depth_solid_angle_one_end_sr':ideal_solid,'ideal_midplane_solid_angle_one_end_sr':ideal_mid},'focused_checks':{'convex_footprints_and_source_bases':True,'all_display_max_vertex_delta_m':disp_delta,'positive_endcap_BT_box_SAT_tests':sat_count,'BT_box_conflicts':conflicts,'ECT_axial_clearance_m':7.05-back,'negative_20mm_seam_witness_occupied_through_entire_depth':True,'incorrect_rotated_bound_negative_rejected':True,'A1_conservative_outer_band_solid_angle_sr':0.,'M1_outer_band_solid_angle_one_sector_sr':solid_angle(m1),'M1_outer_base_distance_m':models['three_bands_slot_localised'][-1][1][0]-models['three_bands_slot_localised'][-1][0][0],'same_ray_different_front_back_bands':endpoint_hits,'near_support_count':len(near),'near_support_min_projected_radius_m':min(x['min_projected_radius_m'] for x in near),'SVGs':svg_results,'unchanged_scientific_blob_count':identities,'old_index_preserved_as_prefix':True,'old_DES040_preserved_as_prefix':True},'source_sha256':hashes,'independent_common_bank':{'seed':20261020,'N':N,'results':mc},'limitations':['No ACTS/field/material/response/reconstruction or engineering validation performed.','System-python scratch rerender attempted and stopped before rendering: ModuleNotFoundError: matplotlib. No dependencies changed.','Both actual pinned PNGs were visually inspected separately; hashes and exact SVG path transforms checked.','Full M1/A1 interface tests and 1,048,576-bank are retained prior evidence; this focused checker does not rerun their broad matrices.']}
a.output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':True,'metrics':metrics,'focused_checks':out['focused_checks'],'independent_common_bank':out['independent_common_bank']},indent=2))
