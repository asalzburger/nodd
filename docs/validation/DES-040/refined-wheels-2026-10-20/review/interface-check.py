#!/usr/bin/env python3
"""Read-only pinned DES040 interface calculation; NumPy only.

No repository imports or writes. All dimensional inputs are git-show bytes at
the requested revision. Geometry algorithms below are independent convex SAT.
"""
import argparse, hashlib, json, math, pathlib, platform, subprocess
import numpy as np

INPUTS = [
 'docs/design/DES-040-muon-chambers-frame.md',
 'tools/muon_layout/wheels.py', 'tools/muon_layout/wheels-config.json',
 'tools/muon_layout/geometry.py',
 'docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json',
 'docs/validation/DES-040/inner-closure-2026-10-20/README.md',
 'tools/muon_layout/support.py', 'tools/toroid_prototype/geometry.py']

def body(vertices, phi, z, depth, ident):
 a=math.radians(phi);c,s=math.cos(a),math.sin(a)
 return dict(vertices_m=vertices,origin_m=[0,0,z],basis=[[c,-s,0],[s,c,0],[0,0,1]],depth_m=depth,id=ident)

def vertices(b):
 p=np.asarray(b['vertices_m']);h=b['depth_m']/2
 local=np.vstack([np.column_stack((p,np.full(4,z))) for z in [-h,h]])
 return local@np.asarray(b['basis']).T+np.asarray(b['origin_m'])

def expand(b, amount):
 p=np.asarray(b['vertices_m']);e=np.roll(p,-1,axis=0)-p
 n=np.column_stack((e[:,1],-e[:,0]));n/=np.linalg.norm(n,axis=1)[:,None]
 h=np.einsum('ij,ij->i',n,p)+amount
 v=[np.linalg.solve(np.stack([n[i-1],n[i]]),[h[i-1],h[i]]).tolist() for i in range(4)]
 return dict(b,vertices_m=v,depth_m=b['depth_m']+2*amount)

def intersects(a,b):
 va,vb=vertices(a),vertices(b)
 if np.any(va.max(axis=0)<vb.min(axis=0)-1e-10) or np.any(vb.max(axis=0)<va.min(axis=0)-1e-10):return False
 ea=np.vstack([va[1:4]-va[:3],va[0]-va[3],va[4]-va[0]])
 eb=np.vstack([vb[1:4]-vb[:3],vb[0]-vb[3],vb[4]-vb[0]])
 na=np.cross(ea[:4],ea[4]);nb=np.cross(eb[:4],eb[4])
 axes=np.vstack([na,nb,np.cross(ea[:,None],eb[None,:]).reshape(-1,3),ea[4],eb[4]])
 lengths=np.linalg.norm(axes,axis=1);axes=axes[lengths>1e-12]/lengths[lengths>1e-12,None]
 aa,bb=va@axes.T,vb@axes.T
 return not bool(np.any((aa.max(axis=0)<bb.min(axis=0)-1e-10)|(bb.max(axis=0)<aa.min(axis=0)-1e-10)))

def width(u,alpha=math.pi/24,delta=.01):return u*math.tan(alpha)-delta/math.cos(alpha)
def outer_u(radius,alpha=math.pi/24,delta=.01):
 return math.cos(alpha)*math.sqrt(radius*radius-delta*delta)+delta*math.sin(alpha)
def trapezoid(u0,u1):return [[u0,-width(u0)],[u1,-width(u1)],[u1,width(u1)],[u0,width(u0)]]

def coil_point(p, magnetic, clearance):
 x,y,z=p;ans=[];a=magnetic['warm']['normal_m']/2+clearance;b=magnetic['warm']['tangent_m']/2+clearance
 for name,c in magnetic['coil_groups'].items():
  for k in range(magnetic['folds']):
   ph=math.radians(c['phi_offset_deg']+30*k);u=x*math.cos(ph)+y*math.sin(ph);v=-x*math.sin(ph)+y*math.cos(ph)
   q=np.abs([u-c['center_r_m'],z-c['center_z_m']])-np.array([c['half_r_m']-c['corner_radius_m'],c['half_z_m']-c['corner_radius_m']])
   distance=abs(float(np.linalg.norm(np.maximum(q,0))+min(max(q),0)-c['corner_radius_m']))
   if abs(v)<=b+1e-12 and distance<=a+1e-12:ans.append([name,k])
 return ans

def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--revision',required=True);p.add_argument('--output',required=True);args=p.parse_args()
 sources={}
 for path in INPUTS:
  data=subprocess.check_output(['git','-C',args.repo,'show',args.revision+':'+path]);sources[path]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
  if path.endswith('/candidate/geometry.json'):D=json.loads(data)
 mag=D['magnetic_configuration'];half=D['wheel_revision']['depth_m']/2;clear=D['wheel_revision']['coil_clearance_m'];ch=D['configuration']['chambers']
 eta=[]
 for i,(z,n) in enumerate(zip(ch['disk_abs_z_m'],[12,24,24]),1):
  R=(z-half)/math.sinh(3);u=outer_u(R,math.pi/n);w=width(u,math.pi/n)
  chosen_corner=math.hypot(R,width(R,math.pi/n))
  eta.append(dict(station=i,z_center_m=z,near_m=z-half,far_m=z+half,eta3_nearface_radius_m=R,eta3_centralplane_radius_m=z/math.sinh(3),chosen_circumscribed_aperture=dict(inner_apothem_m=R,inner_base_m=2*width(R,math.pi/n),inner_corner_radius_m=chosen_corner,centralphi_eta_max=3.,corner_eta_max=math.asinh((z-half)/chosen_corner),corner_radius_excess_m=chosen_corner-R),alternative_cover_eta3_corners=dict(inner_apothem_m=u,inner_base_m=2*w,inner_corner_radius_m=math.hypot(u,w),centralphi_eta_max=math.asinh((z-half)/u),polygon_extra_radius_at_centre_m=R-u)))
 # One conservative three-family witness. These larger bores are stated openly;
 # they are not claimed to satisfy nominal global-phi eta3 at z=9.5m.
 spans={'full_ECT_sector':(1.01,outer_u(6.95)), 'BT_inner':(1.07,4.29), 'BT_outer':(4.91,outer_u(6.95))}
 middle=[]
 for side in [-1,1]:
  for k in range(12):
   for name,(u0,u1) in spans.items():middle.append(body(trapezoid(u0,u1),30*k+(15 if name=='full_ECT_sector' else 0),side*9.5,.5,f'{side}/{name}/{k}'))
 boxes=[]
 for side in [-1,1]:
  for name,c in mag['coil_groups'].items():
   if name.startswith('endcap') and (c['center_z_m']>0)!=(side>0):continue
   for k in range(12):
    for leg in [-1,1]:
     u=c['center_r_m']+leg*c['half_r_m'];a=mag['warm']['normal_m']/2+clear;b=mag['warm']['tangent_m']/2+clear
     boxes.append(body([[u-a,-b],[u+a,-b],[u+a,b],[u-a,b]],c['phi_offset_deg']+30*k,side*9.5,.5,f'{side}/{name}/{k}/{leg}'))
 warm_conflicts=[[x['id'],b['id']] for x in middle for b in boxes if intersects(x,b)]
 support=[expand(s,.05) for s in D['supports']['members']]
 support_conflicts=[[x['id'],s['id']] for x in middle for s in support if intersects(x,s)]
 others=[x for x in D['panels'] if not(x['kind']=='endcap' and x['station']==2)]
 other_conflicts=[[x['id'],s['id']] for x in middle for s in others if intersects(x,s)]
 internal=[[a['id'],b['id']] for i,a in enumerate(middle) for b in middle[i+1:] if intersects(a,b)]
 families=[]
 for name,(u0,u1) in spans.items():families.append(dict(name=name,inner_apothem_m=u0,outer_apothem_m=u1,inner_base_m=2*width(u0),outer_base_m=2*width(u1),span_m=u1-u0,area_m2=(u1-u0)*(width(u0)+width(u1))))
 # Adverse eta3 witness at the current middle plane.
 r=9.5/math.sinh(3);a=math.radians(15);point=[r*math.cos(a),r*math.sin(a),9.5]
 # Narrow axial-shift diagnostic: exact contracted inner rounded corner edge.
 shift=[]
 for z in [10.85,10.87,10.8806,10.89,10.9,10.91,10.95]:
  R=(z-.25)/math.sinh(3);dz=max(0,z+.25-11.1);right=1.3-math.sqrt(.3**2-dz**2);projection=right*math.cos(a)+.35*math.sin(a)
  shift.append(dict(z_center_m=z,eta3_front_radius_m=R,normal20mm_seam_eta3_apothem_m=outer_u(R),farface_ECT_clearance_right_edge_m=right,ECT_projection_into_BT_sector_m=projection,base_apothem_margin_m=outer_u(R)-projection,circular_aperture_margin_m=R-math.hypot(right,.35)))
 moved={}
 for z in [12.25,12.35,12.75]:
  panels=[dict(x,origin_m=[0,0,z]) for x in middle if x['origin_m'][2]>0]
  clashes=[[x['id'],s['id']] for x in panels for s in support if intersects(x,s)]
  outer=[x for x in others if x['kind']=='endcap' and x['station']==3 and x['origin_m'][2]>0]
  collisions=[[x['id'],s['id']] for x in panels for s in outer if intersects(x,s)]
  moved[str(z)]=dict(support_conflict_count=len(clashes),support_conflict_examples=clashes[:8],outer_wheel_overlap_count=len(collisions),outer_wheel_overlap_examples=collisions[:4])
 result=dict(assignment='CR-A1',revision=args.revision,status='DRAFT independent geometry-only scratch; no sign-off',sources=sources,runtime=dict(python=platform.python_version(),numpy=np.__version__),eta_apertures=eta,nominal_eta3_middle_witness=dict(point_m=point,eta=3,phi_deg=15,warm_occupied_by=coil_point(point,mag,0),warm_plus_50mm_by=coil_point(point,mag,.05)),three_shape_witness=dict(panels=len(middle),per_end=len(middle)//2,families=families,coil_box_count=len(boxes),support_members=len(support),other_panels=len(others),coil_conflicts=warm_conflicts,support_conflicts=support_conflicts,other_panel_conflicts=other_conflicts,internal_conflicts=internal,nominal_eta3_not_satisfied=True),narrow_z_shift_diagnostic=shift,moved_middle_checks=moved,limits=['Whole-volume coil proof at original z uses exact straight-leg rectangular sweeps; no copied certificates.','Three-shape witness intentionally enlarges bore for actual ECT clearance; it does not certify global-phi eta3 coverage.','Narrow-z diagnostic is exact corner support bound plus specified ordinary seam recipe, not an exhaustive search of other topologies.','No transport, response, chamber engineering, structural or human approval claim.'])
 pathlib.Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(revision=args.revision,panel_count=len(middle),coil_conflicts=len(warm_conflicts),support_conflicts=len(support_conflicts),other_panel_conflicts=len(other_conflicts),internal_conflicts=len(internal),output=args.output),indent=2))

if __name__=='__main__':main()
