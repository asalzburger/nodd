"""Read-only, standard-library interface arithmetic at the assigned Git revision."""
from pathlib import Path
import collections
import hashlib
import json
import math
import subprocess

import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
ROOT=args.root
REV='5674a7688319d6dd5179c04cd381cb59f48d36bb'
PATHS=['docs/design/DES-040-muon-chambers-frame.md',
       'docs/design/DES-039-twelvefold-toroid.md',
       'docs/validation/DES-040/geometry.json',
       'docs/validation/DES-040/support-input.json',
       'tools/muon_layout/design.json','tools/muon_layout/layout.py',
       'tools/muon_layout/geometry.py']
def source(path):
    return subprocess.check_output(['git','-C',str(ROOT),'show',REV+':'+path])
data={p:source(p) for p in PATHS}
geometry=json.loads(data[PATHS[2]])
mag=geometry['magnetic_configuration']
design=json.loads(data[PATHS[4]])['chambers']

def vertices(body):
    out=[]
    for z in [-body['depth_m']/2,body['depth_m']/2]:
        for x,y in body['vertices_m']:
            out.append([body['origin_m'][i]+sum(body['basis'][i][j]*v for j,v in enumerate([x,y,z])) for i in range(3)])
    return out
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(points):
    p=sorted(set(tuple(x) for x in points))
    lower=[]
    for x in p:
        while len(lower)>1 and cross(lower[-2],lower[-1],x)<=0:lower.pop()
        lower.append(x)
    upper=[]
    for x in reversed(p):
        while len(upper)>1 and cross(upper[-2],upper[-1],x)<=0:upper.pop()
        upper.append(x)
    return lower[:-1]+upper[:-1]
def radial_min(points):
    p=hull([x[:2] for x in points])
    if all(cross(a,b,[0,0])>=-1e-12 for a,b in zip(p,p[1:]+p[:1])):return 0.
    result=math.inf
    for a,b in zip(p,p[1:]+p[:1]):
        d=[b[j]-a[j] for j in range(2)]
        t=max(0,min(1,-sum(a[j]*d[j] for j in range(2))/sum(x*x for x in d)))
        result=min(result,math.hypot(*(a[j]+t*d[j] for j in range(2))))
    return result
def bounds(body):
    v=vertices(body)
    return dict(id=body['id'],category=body['category'],
                radial_min_m=radial_min(v),radial_max_m=max(math.hypot(*x[:2]) for x in v),
                z_min_m=min(x[2] for x in v),z_max_m=max(x[2] for x in v))
def in_prism(body,p):
    delta=[p[i]-body['origin_m'][i] for i in range(3)]
    local=[sum(delta[i]*body['basis'][i][j] for i in range(3)) for j in range(3)]
    poly=body['vertices_m']
    inside=all(cross(a,b,local[:2])>=-1e-12 for a,b in zip(poly,poly[1:]+poly[:1])) and abs(local[2])<=body['depth_m']/2+1e-12
    if not inside:return False,local
    if body.get('shape')=='rhs':
        lo=[min(v[j] for v in poly) for j in range(2)]
        hi=[max(v[j] for v in poly) for j in range(2)]
        t=body['wall_m']
        cavity=all(lo[j]+t<local[j]<hi[j]-t for j in range(2))
        return not cavity,local
    return inside,local
def warm_contains(group,point,coil=0):
    angle=math.radians(group['phi_offset_deg']+coil*360/mag['folds'])
    u=point[0]*math.cos(angle)+point[1]*math.sin(angle)
    v=-point[0]*math.sin(angle)+point[1]*math.cos(angle)
    qr=abs(u-group['center_r_m'])-(group['half_r_m']-group['corner_radius_m'])
    qz=abs(point[2]-group['center_z_m'])-(group['half_z_m']-group['corner_radius_m'])
    signed=math.hypot(max(qr,0),max(qz,0))+min(max(qr,qz),0)-group['corner_radius_m']
    return abs(signed)<=mag['warm']['normal_m']/2+1e-12 and abs(v)<=mag['warm']['tangent_m']/2+1e-12

c=design['coil_clearance_m'];s=design['support_clearance_m'];d=design['depth_m']
hcal_margin=.05 # Explicit provisional interface assumption, not design.json.
a=mag['warm']['normal_m']/2
bt=mag['coil_groups']['barrel'];ect=mag['coil_groups']['endcap_plus']
hcal_back=mag['hcal']['endcap_back_abs_z_m']
ect_front=ect['center_z_m']-ect['half_z_m']-a
ect_rear=ect['center_z_m']+ect['half_z_m']+a
bt_rear=bt['half_z_m']+a
inner_min=hcal_back+hcal_margin+d/2
inner_max=ect_front-c-d/2
bs=[bounds(x) for x in geometry['supports']['members']]
outer_r=design['disk_outer_r_m'][-1]
relevant=[x for x in bs if x['radial_min_m']<=outer_r+s and x['radial_max_m']>=design['disk_inner_r_m']-s and x['z_max_m']>0]
support_rear=max(x['z_max_m'] for x in relevant)
outer_coil_min=max(bt_rear,ect_rear)+c+d/2
outer_all_min=max(max(bt_rear,ect_rear)+c,support_rear+s)+d/2
phi=math.radians(15)
point=[6.5*math.cos(phi)-.14*math.sin(phi),6.5*math.sin(phi)+.14*math.cos(phi),12.3]
spoke=next(x for x in geometry['supports']['members'] if x['id']=='ECTP-rear/SPOKE00')
material,local=in_prism(spoke,point)
assert material
assert .7<=math.hypot(*point[:2])<=outer_r and outer_coil_min-d/2<=point[2]<=outer_coil_min+d/2
bt_point=[bt['center_r_m']-bt['half_r_m'],0,inner_min]
assert warm_contains(bt,bt_point)
ect_point=[2*math.cos(phi),2*math.sin(phi),ect['center_z_m']-ect['half_z_m']]
assert warm_contains(ect,ect_point)
assert inner_min-d/2<=ect_point[2]<=inner_min+d/2
assert inner_min>inner_max
alt_inner,alt_outer,alt_z=4.92,5.50,6.24
alt_front,alt_back=alt_z-d/2,alt_z+d/2
support_gaps=[]
for item in bs:
    radial=max(item['radial_min_m']-alt_outer,alt_inner-item['radial_max_m'],0.)
    axial=max(item['z_min_m']-alt_back,alt_front-item['z_max_m'],0.)
    support_gaps.append(max(radial,axial))
assert min(support_gaps)>s
alt_bt_guarded_rmax=math.hypot(bt['center_r_m']-bt['half_r_m']+a+c,mag['warm']['tangent_m']/2+c)
assert alt_inner>alt_bt_guarded_rmax
assert ect_front-alt_back>c
alt_span=alt_outer*math.cos(math.pi/design['endcap_sectors'])-alt_inner
assert alt_span>=design['min_span_m']
bt_inner=bt['center_r_m']-bt['half_r_m']
gap_half_min=math.degrees(math.atan2(mag['warm']['tangent_m']/2+c,bt_inner-a-c))
gap_half=5.
sector_half=15-gap_half
assert gap_half>gap_half_min
nrad=math.ceil((design['disk_outer_r_m'][0]-design['disk_inner_r_m']+design['gap_m'])/(design['max_endcap_radial_span_m']+design['gap_m']))
band=(design['disk_outer_r_m'][0]-design['disk_inner_r_m']-(nrad-1)*design['gap_m'])/nrad
trapezoids=[]
for i in range(nrad):
    rlo=design['disk_inner_r_m']+i*(band+design['gap_m']);rhi=rlo+band
    u0=rlo;u1=rhi*math.cos(math.radians(sector_half))
    w0=u0*math.tan(math.radians(sector_half))-design['gap_m']/2
    w1=u1*math.tan(math.radians(sector_half))-design['gap_m']/2
    area=(w0+w1)*(u1-u0)
    assert u1-u0>=design['min_span_m'] and area>=design['min_area_m2']
    trapezoids.append(dict(radial_compartment_m=[rlo,rhi],physical_radial_span_m=u1-u0,area_m2=area,outer_width_m=2*w1))
result=dict(input_revision=REV,source_sha256={p:hashlib.sha256(b).hexdigest() for p,b in data.items()},
    scope='Read-only finite-envelope arithmetic and exact sweep/material witnesses; no layout or field regeneration',
    chamber_depth_m=d,coil_clearance_m=c,support_clearance_m=s,provisional_hcal_margin_m=hcal_margin,
    source_bounds=dict(hcal_endcap_back_abs_z_m=hcal_back,ect_warm_front_abs_z_m=ect_front,
                       ect_warm_rear_abs_z_m=ect_rear,bt_warm_abs_z_max_m=bt_rear,
                       bt_inner_warm_straight_local_r_m=[bt['center_r_m']-bt['half_r_m']-a,bt['center_r_m']-bt['half_r_m']+a]),
    inner_wheel=dict(required_center_abs_z_min_m=inner_min,allowed_center_abs_z_max_m=inner_max,
        raw_axial_gap_m=ect_front-hcal_back,available_depth_with_clearances_m=ect_front-hcal_back-c-hcal_margin,
        axial_deficit_m=inner_min-inner_max,zero_margin_axial_deficit_m=d-(ect_front-hcal_back),
        coil_clearance_only_axial_deficit_m=d+c-(ect_front-hcal_back),
        uninterrupted_annulus_bt_clear_radial_upper_m=bt['center_r_m']-bt['half_r_m']-a-c,
        retained_radial_upper_m=design['disk_outer_r_m'][0],bt_occupied_witness_m=bt_point,
        ect_occupied_witness_for_hcal_clear_placement_m=ect_point),
    outer_wheel=dict(center_after_coils_min_m=outer_coil_min,full_z_after_coils_m=[outer_coil_min-d/2,outer_coil_min+d/2],
        relevant_support_z_max_m=support_rear,limiting_support_ids=[x['id'] for x in relevant if abs(x['z_max_m']-support_rear)<1e-10],
        center_after_fixed_coils_and_frame_min_m=outer_all_min,full_z_after_fixed_frame_m=[outer_all_min-d/2,outer_all_min+d/2],
        rear_spoke_material_witness_m=point,rear_spoke_local_m=local,
        out_of_map_depth_m=outer_all_min+d/2-mag['map']['z_max_m']),
    minimal_interface_changes=dict(ect_front_outward_displacement_m=inner_min-inner_max,
        hcal_back_required_for_fixed_ect_m=ect_front-c-hcal_margin-d,
        hcal_depth_if_front_unchanged_m=ect_front-c-hcal_margin-d-4.8832,
        bt_inner_leg_outward_displacement_for_retained_first_rmax_m=design['disk_outer_r_m'][0]+a+c-(bt['center_r_m']-bt['half_r_m']),
        front_return_only_ect_center_z_m=(ect['center_z_m']+ect['half_z_m']+ect['center_z_m']-ect['half_z_m']+inner_min-inner_max)/2,
        front_return_only_ect_half_z_m=(2*ect['half_z_m']-(inner_min-inner_max))/2),
    large_hole_alternative=dict(status='spatially feasible bound only; changes requested aperture, radius and acceptance',
        radial_interval_m=[alt_inner,alt_outer],center_abs_z_m=alt_z,full_abs_z_m=[alt_front,alt_back],
        conservative_support_separation_lower_bound_m=min(support_gaps),
        expanded_bt_inner_sleeve_radial_max_m=alt_bt_guarded_rmax,
        ect_warm_axial_gap_m=ect_front-alt_back,actual_trapezoid_radial_span_m=alt_span,
        barrel1_half_z_max_if_retaining_50mm_seam_m=alt_front-.05),
    bt_gap_wheel=dict(status='BT-clear full radial reach with explicit sector gaps; axial HCAL/ECT failure remains',
        sectors=12,sector_center_phi_deg='15+30*k',bt_gap_center_phi_deg='30*k',
        gap_half_angle_min_deg=gap_half_min,example_gap_half_angle_deg=gap_half,
        example_trapezoid_compartment_span_deg=2*sector_half,
        example_azimuth_fraction_before_module_gaps=12*2*sector_half/360,
        radial_band_count=nrad,total_modules_per_wheel=12*nrad,trapezoids=trapezoids),
    support_member_count=len(bs),map_bounds=mag['map'])
out=args.output
out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','map_bounds']},indent=2))
