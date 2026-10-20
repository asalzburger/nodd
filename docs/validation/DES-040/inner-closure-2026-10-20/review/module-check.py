from pathlib import Path
import argparse, platform, subprocess, sys, json, hashlib, math, itertools, tempfile, time
import numpy as np
parser=argparse.ArgumentParser(description='Unadopted inner-wheel radial-band diagnostic from exact committed geometry; no replacement layout or ACTS result.')
parser.add_argument('--repo',type=Path,default=Path.cwd())
parser.add_argument('--revision',required=True,help='Full source commit SHA')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
REV=args.revision
ROOT=args.repo.resolve()
if len(REV)!=40 or any(c not in '0123456789abcdef' for c in REV):raise ValueError('exact40-character lowercase commit SHA required')
TEMP=tempfile.TemporaryDirectory(prefix='pr90-IC-M1-pinned-')
BASE=Path(TEMP.name)
def read(path): return subprocess.check_output(['git','-C',str(ROOT),'show',REV+':'+path])
files=['tools/muon_layout/geometry.py','tools/muon_layout/wheels.py','tools/muon_layout/layout.py','tools/muon_layout/support.py','tools/toroid_prototype/geometry.py']
for f in files:
 p=BASE/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(read(f))
for d in [BASE/'tools',BASE/'tools/muon_layout',BASE/'tools/toroid_prototype']:(d/'__init__.py').write_text('')
sys.path.insert(0,str(BASE))
from tools.muon_layout import geometry as g
from tools.muon_layout import wheels
config=json.loads(read('tools/muon_layout/wheels-config.json'))
geo=json.loads(read('docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json'))
sections=json.loads(read('docs/validation/DES-040/wheels-2026-10-20/xy-sections/sections.json'))
mag=geo['magnetic_configuration'];alpha=math.pi/config['inner_wheel']['sectors'];c,s=math.cos(alpha),math.sin(alpha)
bt=mag['coil_groups']['barrel']; radius=bt['center_r_m']-bt['half_r_m'];clearance=config['coil_clearance_m']
xlo=radius-mag['warm']['normal_m']/2-clearance;xhi=radius+mag['warm']['normal_m']/2+clearance
yguard=mag['warm']['tangent_m']/2+clearance;cert_guard=yguard+config['inner_wheel']['extra_BT_box_margin_m']
expanded_box=np.array([[xlo,-yguard],[xhi,-yguard],[xhi,yguard],[xlo,yguard]])
cert_box=np.array([[xlo,-cert_guard],[xhi,-cert_guard],[xhi,cert_guard],[xlo,cert_guard]])
# Actual rotation from BT leg coordinates into sector-centre radial coordinate.
projected_u=cert_box@np.array([c,s]);raw_projected_u=expanded_box@np.array([c,s])
ulo=float(projected_u.min())-.01;uhi=float(projected_u.max())+.01
R=config['inner_wheel']['outer_radius_m']

def outer_u(delta):
 A=math.tan(alpha);B=-delta/c
 return (-A*B+math.sqrt((A*B)**2-(1+A*A)*(B*B-R*R)))/(1+A*A)

# Local constant seam-normal half-gap; separates neighbouring sectors by 2delta.
def make_band(j,u0,u1,delta):
 w0=u0*math.tan(alpha)-delta/c;w1=u1*math.tan(alpha)-delta/c
 bodies=[]
 for side in [-1,1]:
  for k in range(12):
   phi=math.radians(15+30*k);er=[math.cos(phi),math.sin(phi),0];ep=[-math.sin(phi),math.cos(phi),0]
   bodies.append(g.prism(f'OPTION/E{side}/B{j}/S{k:02d}','endcap',[0,0,side*6.7456],np.column_stack((er,ep,[0,0,1])),[[u0,-w0],[u1,-w1],[u1,w1],[u0,w0]],.5,station=1,side=side))
 return bodies,dict(band=j,inner_base_apothem_m=u0,outer_base_apothem_m=u1,base_distance_m=u1-u0,inner_base_m=2*w0,outer_base_m=2*w1,normal_half_seam_m=delta,one_chamber_face_area_m2=(u1-u0)*(w0+w1),max_corner_radius_m=math.hypot(u1,w1))

def omega(body,border=0,full=True):
 n,b=g.polygon_planes(body['vertices_m']);b=b-border
 z=abs(body['origin_m'][2]);h=body['depth_m']/2
 bb=np.minimum(b/(z-h),b/(z+h)) if full else b/z
 p=np.array([np.linalg.solve(np.stack((n[i-1],n[i])),[bb[i-1],bb[i]]) for i in range(4)])
 # Eroded narrow band can disappear. General halfspace polygon vertices test.
 if np.any(p@n.T-bb>1e-10):
  points=[]
  for i,j in itertools.combinations(range(4),2):
   m=np.stack((n[i],n[j]));det=np.linalg.det(m)
   if abs(det)<1e-12:continue
   pt=np.linalg.solve(m,[bb[i],bb[j]])
   if np.all(pt@n.T<=bb+1e-10):points.append(pt)
  if len(points)<3:return 0.
  p=np.array(points);p=p[np.argsort(np.arctan2(p[:,1]-p[:,1].mean(),p[:,0]-p[:,0].mean()))]
 v=np.column_stack((p,np.ones(len(p))));answer=0.
 for i in range(1,len(p)-1):
  a,b,c=v[[0,i,i+1]];la,lb,lc=np.linalg.norm(v[[0,i,i+1]],axis=1)
  answer+=2*math.atan2(abs(float(np.linalg.det(np.stack((a,b,c))))),la*lb*lc+(a@b)*lc+(a@c)*lb+(b@c)*la)
 return answer

z=6.7456;h=.25
ideal_full=4*math.pi*(math.cos(math.atan(.7/(z-h)))-math.cos(math.atan(5.45/(z+h))))
ideal_mid=4*math.pi*(math.cos(math.atan(.7/z))-math.cos(math.atan(5.45/z)))
area_annulus=math.pi*(5.45**2-.7**2)
models={
 'current_one_band': [p for p in geo['panels'] if p.get('wheel')=='inner_wheel'],
}
specs={}
for name, bands in {
 'two_bands':[(.7,ulo,.01),(ulo+.02,outer_u(.36),.36)],
 'three_bands_slot_localised':[(.7,ulo,.01),(ulo+.02,uhi,.36),(uhi+.02,outer_u(.01),.01)],
 'three_bands_split_inner':[(.7,(.7+ulo)/2-.01,.01),((.7+ulo)/2+.01,ulo,.01),(ulo+.02,outer_u(.36),.36)],
}.items():
 bodies=[];dimensions=[]
 for j,(u0,u1,delta) in enumerate(bands):
  bb,dd=make_band(j,u0,u1,delta);bodies+=bb;dimensions.append(dd)
 models[name]=bodies;specs[name]=dimensions

others=[p for p in geo['panels'] if not(p['kind']=='endcap' and p['station']==1)]
members=geo['supports']['members'];sbounds=np.asarray([g.aabb(x) for x in members]);obounds=np.asarray([g.aabb(x) for x in others])
checks={};metrics={}
for name,bodies in models.items():
 start=time.monotonic();conflicts=[];support_clashes=[];other_clashes=[];proofs=[]
 for b in bodies:
  proof=wheels.wheel_certificate(b,config,mag);proofs.append(proof)
  lo,hi=g.aabb(b)
  near=np.flatnonzero(((sbounds[:,1]+.1>=lo)&(sbounds[:,0]-.1<=hi)).all(axis=1))
  support_clashes += [[b['id'],members[i]['id']] for i in near if g.intersects(b,members[i],.05)]
  near=np.flatnonzero(((obounds[:,1]>=lo)&(obounds[:,0]<=hi)).all(axis=1))
  other_clashes += [[b['id'],others[i]['id']] for i in near if g.intersects(b,others[i])]
 for i,a in enumerate(bodies):
  for b in bodies[i+1:]:
   if g.intersects(a,b):conflicts.append([a['id'],b['id']])
 # Same underlying analytic kernel as candidate full-volume proof, plus independent SAT
 # all corners/projections verified below; adaptive probes are separate, both-side all-panel.
 checks[name]=dict(count=len(bodies),pair_count=len(bodies)*(len(bodies)-1)//2,
  coil_certificate_passes=sum(p['clear'] for p in proofs),coil_certificate_count=len(proofs),
  support_count=len(members),support_conflicts=support_clashes,other_chamber_count=len(others),other_chamber_conflicts=other_clashes,
  option_panel_conflicts=conflicts,max_abs_z_m=max(abs(g.vertices3(b)[:,2]).max() for b in bodies),
  max_corner_radius_m=max(np.linalg.norm(g.vertices3(b)[:,:2],axis=1).max() for b in bodies),seconds=time.monotonic()-start)
 face_area=sum(g.polygon_area(b['vertices_m']) for b in bodies)/2
 metrics[name]=dict(chambers_per_end=len(bodies)//2,families_per_inner_wheel=len(specs.get(name,[{}])),
  face_area_one_end_m2=face_area,midplane_area_loss_vs_circular_annulus=1-face_area/area_annulus,
  IP_midplane_solid_angle_loss=1-sum(omega(b,full=False) for b in bodies)/ideal_mid,
  IP_full_depth_same_chamber_loss=1-sum(omega(b) for b in bodies)/ideal_full,
  IP_full_depth_same_chamber_border30mm_loss=1-sum(omega(b,.03) for b in bodies)/ideal_full)

# independent numerical straight-ray test full-depth and midplane, common random bank.
rng=np.random.default_rng(409090)
N=1048576;cost=rng.uniform(math.cos(math.atan(5.45/(z+h))), math.cos(math.atan(.7/(z-h))),N)
phi=rng.uniform(0,2*math.pi,N);directions=np.column_stack((np.sqrt(1-cost**2)*np.cos(phi),np.sqrt(1-cost**2)*np.sin(phi),cost))
mc={}
for name,bodies in models.items():
 hit=np.zeros(N,bool);active=np.zeros(N,bool)
 for b in bodies:
  if b['side']<0:continue
  hit |= np.isfinite(g.midplane_hits(b,directions,0,True))
  active |= np.isfinite(g.midplane_hits(b,directions,.03,True))
 f=1-float(hit.mean());err=math.sqrt(f*(1-f)/N)
 mc[name]=dict(loss=f,standard_error=err,analytic_minus_mc_sigma=(metrics[name]['IP_full_depth_same_chamber_loss']-f)/err,border_loss=1-float(active.mean()))

# Negative occupied-corner fixture must fail exact box SAT, not silently disappear.
near=g.prism('negative/BT','endcap',[4.6,0,6.7456],np.eye(3),[[-.1,-.1],[.1,-.1],[.1,.1],[-.1,.1]],.5,station=1)
negative=not wheels.wheel_certificate(near,config,mag)['clear']
# A radial-radius substitute u=4.30 ignores the rotated box's true support.
naive, _=make_band('negative-naive',.7,4.29,.01)
naive_rejected=all(not wheels.wheel_certificate(b,config,mag)['clear'] for b in naive)
assert negative and naive_rejected
# Verify the reviewed XY figure uses the same footprint, to rounding only.
section=next(s for s in sections['sections'] if s['station']==1);lookup={b['id']:b for b in models['current_one_band']}
section_delta=max(min(np.linalg.norm(np.asarray(v)-q) for q in g.vertices3(lookup[b['id']])[:4,:2]) for b in section['chambers'] for v in b['xy_m'])
assert section_delta<1e-9
for ccc in checks.values():
 assert ccc['coil_certificate_passes']==ccc['coil_certificate_count']
 assert not ccc['support_conflicts'] and not ccc['other_chamber_conflicts'] and not ccc['option_panel_conflicts']
assert all(abs(m['analytic_minus_mc_sigma'])<4 for m in mc.values())

out=dict(assignment='IC-M1',input_revision=REV,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),runtime=dict(python=platform.python_version(),numpy=np.__version__),command=['python3','-B',Path(__file__).name,'--repo','.','--revision',REV,'--output',args.output.name],status='READ-ONLY UNADOPTED feasibility concepts; no design acceptance or ACTS result',
 sources={f:hashlib.sha256(read(f)).hexdigest() for f in files+['tools/muon_layout/wheels-config.json','docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json','docs/validation/DES-040/wheels-2026-10-20/xy-sections/sections.json']},
 inference=dict(expanded_BT_leg_box_local_xy_m=expanded_box.tolist(),certification_box_local_xy_m=cert_box.tolist(),
 sector_centre_rotation_deg=15,expanded_box_sector_u_extrema_m=[float(raw_projected_u.min()),float(raw_projected_u.max())],
 certification_box_sector_u_extrema_m=[float(projected_u.min()),float(projected_u.max())],band1_outer_apothem_m=ulo,band3_inner_apothem_m=uhi+.02,
 radial_interband_gap_m=.02,extra_apothem_guard_m=.01,ideal_midplane_area_m2=area_annulus,
 total_physical_leg_area_per_end_m2=12*.5*.6,total_clearance_box_area_per_end_m2=12*.6*.7,total_cert_box_area_per_end_m2=12*.6*.72),
 optional_dimensions=specs,metrics=metrics,checks=checks,straight_ray_monte_carlo=dict(seed=409090,N=N,sampling='iid uniform cos(theta),phi over whole-depth ideal positive endcap annulus; common bank across options',results=mc),negative_occupied_fixture_rejected=negative,negative_naive_radius_band_rejected=naive_rejected,XY_section_to_actual_footprint_max_corner_delta_m=section_delta,
 limits=['No geometry adopted; current contract forbids radial tiling, so alternatives need explicit amendment.',
 'Midplane area gain is not coverage or response; radial splits create full-depth same-module angular gaps.',
 'Slot-localised third outer band is narrower than old0.50m minimum module span and needs a separate exception or different topology.',
 'Two-band low radial span exceeds old1.50m ordinary module cap; current whole-wheel exemption does not by itself adopt a new band design.',
 'No MDT tubes, gas, readout, sag/alignment, timing/background, services or reconstruction qualification.',
 'Geometric full-volume checks do not establish magnetic loads, cryostat/coil construction or support stiffness.',
 'No ACTS propagation or field recomputation performed. Fixed magnet/frame/source bytes unchanged.'])
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(dimensions=specs,metrics=metrics,checks=checks,mc=mc,inference=out['inference']),indent=2))
