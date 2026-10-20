import subprocess,json,math,hashlib,sys,argparse
from pathlib import Path
import numpy as np
parser=argparse.ArgumentParser(description='Pinned IC-A1 fixed-interface feasibility checks; scratch options only, no detector adoption.')
parser.add_argument('--repo',type=Path,default=Path.cwd())
parser.add_argument('--revision',default='15015d378b5b77b3bb11698809d1680d12b8a91c')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
ROOT=args.repo.resolve();REV=args.revision
if len(REV)!=40 or any(c not in '0123456789abcdef' for c in REV):parser.error('--revision must be a full lowercase Git SHA')
def blob(path):return subprocess.check_output(['git','show',f'{REV}:{path}'],cwd=ROOT)
def inp(path):return json.loads(blob(path))
source_paths=['tools/muon_layout/geometry.py','tools/toroid_prototype/geometry.py','tools/muon_layout/wheels.py','tools/muon_layout/support.py','tools/muon_layout/wheels-config.json','docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json','docs/validation/DES-040/wheels-2026-10-20/xy-sections/sections.json','docs/validation/DES-040/wheels-2026-10-20/magnetic/configuration.json']
identity={p:{'sha256':hashlib.sha256(blob(p)).hexdigest(),'working_bytes_equal_pinned':(ROOT/p).read_bytes()==blob(p)} for p in source_paths}
assert all(x['working_bytes_equal_pinned'] for x in identity.values())
sys.path.insert(0,str(ROOT))
from tools.muon_layout import geometry as g
from tools.toroid_prototype.geometry import coil_mask,group_mask
J=inp(source_paths[5]); C=J['magnetic_configuration']; wc=J['wheel_revision'];alpha=math.pi/12;ct,st=math.cos(alpha),math.sin(alpha);d=.01;R=5.45
A=math.tan(alpha);B=-d/ct;u0=.7;u1=(-A*B+math.sqrt((A*B)**2-(1+A*A)*(B*B-R*R)))/(1+A*A)
body=g.prism('hypothetical/straight-20mm-seam','test',[0,0,6.7456],[[ct,-st,0],[st,ct,0],[0,0,1]],[[u0,-(A*u0+B)],[u1,-(A*u1+B)],[u1,A*u1+B],[u0,A*u0+B]],.5)
points=np.array([[4.6,.1,z] for z in [6.4956,6.7456,6.9956]])
inside=g.contains(body,points);occupied=coil_mask(points,C);groups=coil_mask(points,C,return_groups=True)
assert inside.all() and occupied.all()
bt=C['coil_groups']['barrel'];rleg=bt['center_r_m']-bt['half_r_m'];a=C['warm']['normal_m']/2;b=C['warm']['tangent_m']/2;c=wc['coil_clearance_m']
xlo,xhi,yhi=rleg-a-c,rleg+a+c,b+c
rbound=math.hypot(xhi,yhi)
slab_outer_u=xhi*ct+yhi*st
# Exact minimum radial distance of projection of support prism, using hull edges.
def hull(points):
 p=sorted(set(map(tuple,points)))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 if len(p)<=1:return np.array(p)
 lo=[]
 for q in p:
  while len(lo)>=2 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 hi=[]
 for q in p[::-1]:
  while len(hi)>=2 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return np.array(lo[:-1]+hi[:-1])
def minrad(body):
 p=hull(g.vertices3(body)[:,:2]);ans=math.inf
 for q,r in zip(p,np.roll(p,-1,axis=0)):
  v=r-q;t=np.clip(-(q@v)/(v@v),0,1) if v@v else 0;ans=min(ans,float(np.linalg.norm(q+t*v)))
 return ans
zlo,zhi=6.4956,6.9956
near=[]
for m in J['supports']['members']:
 lo,hi=g.aabb(m)
 if lo[2]-c<=zhi and hi[2]+c>=zlo:
  near.append({'id':m['id'],'min_radius_full_prism_projection_m':minrad(m),'z_bounds_m':[float(lo[2]),float(hi[2])]})
near.sort(key=lambda x:x['min_radius_full_prism_projection_m'])
barrels={}
for station in [1,2,3]:
 pp=[p for p in J['panels'] if p['kind']=='barrel' and p['station']==station]
 barrels[str(station)]={'count':len(pp),'min_radius_full_prism_projection_m':min(map(minrad,pp)),'max_abs_z_m':max(abs(g.vertices3(p)[:,2]).max() for p in pp)}
# SAT on illustrative three-piece per-sector recovery, only fixed-interface feasibility.
# radialcap: all lower-band vertices <4.30; upperband all points radius>=4.92.
# middle continues existing corridor, clipping by u-planes. 20mm gaps between the threebands.
dim=J['wheel_dimensions']['inner_wheel'];old=next(p for p in J['panels'] if p['id']=='EP1/WHEEL/S00')
def trap(u0,u1,A,B,name):return g.prism(name,'test',[0,0,6.7456],old['basis'],[[u0,-(A*u0+B)],[u1,-(A*u1+B)],[u1,A*u1+B],[u0,A*u0+B]],.5)
# lower u1 solves radius4.29 (10mm safe radiusmargin), then middle starts20mmfurther.
Rlow=4.29
ulow=(-A*B+math.sqrt((A*B)**2-(1+A*A)*(B*B-Rlow*Rlow)))/(1+A*A)
# conservative upper u0=4.93 leaves17.5mmradial margin beyond inflatedboxcorner.
options=[trap(.7,ulow,A,B,'exploration/lower'),trap(ulow+.02,4.91,dim['half_width_slope'],dim['half_width_intercept_m'],'exploration/middle'),trap(4.93,u1,A,B,'exploration/upper')]
# Signed convex finite support SAT only; coil proof via analytic radial band + independent adaptive BT.
coils_bt={**C,'coil_groups':{'barrel':bt}}
option_checks=[]
for p in options:
 tests={'id':p['id'],'volume_m3':g.volume(p),'base_distance_m':p['vertices_m'][1][0]-p['vertices_m'][0][0],'support_conflicts_50mm':[m['id'] for m in J['supports']['members'] if g.intersects(p,m,c)],'barrel_conflicts':[q['id'] for q in J['panels'] if q['kind']=='barrel' and g.intersects(p,q)],'bt_proof':g.certify_coil_clear(p,coils_bt,c,.005,max_cells=500000)}
 tests['panel_conflicts']=[q['id'] for q in options if q is not p and g.intersects(p,q)]
 option_checks.append(tests)
assert all(not p['support_conflicts_50mm'] and not p['barrel_conflicts'] and not p['panel_conflicts'] and p['bt_proof']['clear'] for p in option_checks)
wdim=J['wheel_dimensions']['inner_wheel'];m,bb=wdim['seam_slope'],wdim['seam_intercept_m']
result={'assignment':'IC-A1','input_revision':REV,'scope':'Read-only fixed-interface feasibility; illustrative scratch volumes only; no geometry adoption/engineering approval','input_identity':identity,'axial':{'hcal_back_abs_z_m':6.4412,'wheel_faces_abs_z_m':[zlo,zhi],'ect_warm_front_abs_z_m':7.05,'gross_slot_m':7.05-6.4412,'margin_each_m':zlo-6.4412,'allowed_centre_interval_m':[6.4412+.05+.25,7.05-.05-.25],'remaining_centre_motion_each_m':.0044,'BT_straight_inner_leg_full_z_bound_m':[-10.8,10.8]},'occupied_witness':{'hypothetical_20mm_seam_trapezoid':body,'points_m':points.tolist(),'inside_hypothetical_chamber':inside.tolist(),'inside_warm_coil':occupied.tolist(),'groups':{k:v.tolist() for k,v in groups.items()}},'BT_slots':{'actual_rectangle_in_seam_frame_m':[[rleg-a,-b],[rleg+a,b]],'inflated_50mm_rectangle_m':[[xlo,-yhi],[xhi,yhi]],'actual_outer_corner_radius_m':math.hypot(rleg+a,b),'inflated_outer_corner_radius_m':rbound,'safe_lower_band_outer_vertex_R_bound_m':xlo,'safe_upper_band_inner_point_R_bound_m':rbound,'sector_supporting_slab_upper_u_bound_m':slab_outer_u,'sufficient_not_maximally_permissive':True,'current_corridor_y_at_x_m':{str(x):m*x+bb for x in [4.3,4.35,4.85,4.9,old['dimensions']['u1_m']]},'actual_occupied_phi_fraction_at_R4p6':12*math.asin(.3/4.6)/math.pi,'clearance_reserved_phi_fraction_at_R4p6':12*math.asin(.35/4.6)/math.pi,'current_outer_seam_full_gap_m':2*(m*5.4296525558+bb),'minimum_current_side_to_actual_box_distance_m':(m*4.35+bb-.3)/math.hypot(1,m)},'supports':{'clearance_m':c,'members_near_wheel_z_with_50mm_padding':len(near),'minimum_projected_radius_m':min(p['min_radius_full_prism_projection_m'] for p in near),'nearest_records':near[:40],'all_near_members_radially_beyond_5p5m':all(p['min_radius_full_prism_projection_m']>5.5 for p in near)},'barrels':barrels,'illustrative_three_band_checks':option_checks,'radial_depth_limit':{'IP_ray_R4p6_front_to_rear_delta_R_m':4.6*.5/6.7456,'conservative_upper_band_u_m':[4.93,u1],'conservative_upper_band_has_straight_IP_full_depth_ray':bool(4.93/zlo < u1/zhi),'sector_plane_upper_band_u_m':[4.83,u1],'sector_plane_upper_band_has_straight_IP_full_depth_ray':bool(4.83/zlo < u1/zhi),'sector_plane_upper_band_base_distance_m':u1-4.83,'ordinary_min_span_m':J['configuration']['chambers']['min_span_m']},'limits':['Illustrative option not design: lower/middle radialspan rules andnarrow uppercassette require explicit contract choices; currentwholewheelexception doesnotautomaticallyauthorize fragmentation.','The all-radial conservative bounds do not sayeverypoint between4.30and4.9125m isoccupied; only12finiteBT rectanglesexist.','Proof isreservationgeometry only,not materialtransportresponseorhardwareforcequalification.','No full coverage, ACTS performance, field or energy changes computed; magnets unchanged.']}

allp=[]
for side in [-1,1]:
 for k in range(12):
  a=k*math.pi/6;rot=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
  for p in options:
   b=dict(p,id=p['id']+f'/{side}/{k}',basis=(rot@np.array(p['basis'])).tolist(),origin_m=[0,0,side*6.7456]);allp.append(b)
# whole-frame/saved-panel exact SAT; no sampling-based acceptance.
clashes=[]
for p in allp:
 for m in J['supports']['members']:
  if g.intersects(p,m,.05):clashes.append([p['id'],m['id'],'support'])
 for q in J['panels']:
  if q['kind']=='barrel' and g.intersects(p,q):clashes.append([p['id'],q['id'],'barrel'])
for i,p in enumerate(allp):
 for q in allp[i+1:]:
  if g.intersects(p,q):clashes.append([p['id'],q['id'],'candidate'])
assert not clashes
# sector-plane sufficient recipe has a less-conservative upper band.
# Test eachfold/oppositeend against BT distancecert andunchangedframe/barrels.
probes=[]
for side in [-1,1]:
 for k in range(12):
  a=math.pi/12+k*math.pi/6;ct,st=math.cos(a),math.sin(a);A=math.tan(math.pi/12);B=-.01/math.cos(math.pi/12);u0,u1=4.83,u1
  p=g.prism(f'alternative-support-plane-upper/{side}/{k}','test',[0,0,side*6.7456],[[ct,-st,0],[st,ct,0],[0,0,1]],[[u0,-(A*u0+B)],[u1,-(A*u1+B)],[u1,A*u1+B],[u0,A*u0+B]],.5)
  proof=g.certify_coil_clear(p,coils_bt,.05,.005,max_cells=500000)
  conflicts=[m['id'] for m in J['supports']['members'] if g.intersects(p,m,.05)]+[q['id'] for q in J['panels'] if q['kind']=='barrel' and g.intersects(p,q)]
  assert proof['clear'] and not conflicts
  probes.append({'id':p['id'],'BT_certificate':proof,'support_barrel_conflicts':conflicts})
r={'assignment':'IC-A1','input_revision':REV,'three_band_conservative_recipe_volumes':len(allp),'support_SAT_tests':len(allp)*len(J['supports']['members']),'barrel_SAT_tests':len(allp)*sum(p['kind']=='barrel' for p in J['panels']),'candidate_pair_SAT_tests':len(allp)*(len(allp)-1)//2,'conflicts':clashes,'support_plane_upper_band_checks':probes,'interpretation':'Independent scratch feasibility only; no adoption, manufacturing/coverage/engineeringclaim. Entire ECTseparatedby54.4mm axialsupportingplanes, BTfullvolumebyadaptivecertificates. Checks explicit bothends/all12folds withoutframeC12assumption.'}

result["rotated_checks"]=r
args.output.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"assignment":"IC-A1","input_revision":REV,"output":args.output.name,"occupied_witness_confirmed":bool(inside.all() and occupied.all()),"support_SAT_tests":r["support_SAT_tests"],"barrel_SAT_tests":r["barrel_SAT_tests"],"candidate_pair_SAT_tests":r["candidate_pair_SAT_tests"],"all_fold_plane_upper_BT_certificates":len(probes),"conflicts":clashes},indent=2))
