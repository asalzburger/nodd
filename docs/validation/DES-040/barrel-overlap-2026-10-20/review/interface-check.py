#!/usr/bin/env python3
"""BO-A1 independent geometry-only interface calculation; NumPy and Git only.
Reads exact Git blobs; never imports or writes repository source. No ACTS needed.
All lengths metres. This is an unsigned isolated PROTOTYPE assessment.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import argparse, hashlib, json, math, subprocess
import numpy as np

GEOMETRY='docs/validation/DES-040/refined-wheels-2026-10-20/candidate/geometry.json'
SOURCES=[GEOMETRY,'docs/design/DES-040-muon-chambers-frame.md','tools/muon_layout/layout.py','tools/muon_layout/geometry.py','tools/muon_layout/wheels.py','tools/muon_layout/support.py','tools/muon_layout/refined_wheels.py','tools/toroid_prototype/geometry.py','tools/muon_layout/refined_validation.py','docs/validation/DES-040/refined-wheels-2026-10-20/README.md']

def read(repo,rev,path):
    return subprocess.check_output(['git','-C',str(repo),'show',rev+':'+path])

def planes(body,offset=0):
    p=np.asarray(body['vertices_m']);q=np.asarray(body['basis']);o=np.asarray(body['origin_m'])
    e=np.roll(p,-1,axis=0)-p;n=np.column_stack((e[:,1],-e[:,0]));n/=np.linalg.norm(n,axis=1)[:,None]
    a=n@q[:,:2].T
    A=np.vstack((a,q[:,2],-q[:,2]));B=np.r_[np.einsum('ij,ij->i',n,p)+a@o, q[:,2]@o+body['depth_m']/2,-q[:,2]@o+body['depth_m']/2]
    return A,B+offset

def vertices(body):
    p=np.asarray(body['vertices_m']);h=body['depth_m']/2
    local=np.vstack((np.column_stack((p,np.full(4,-h))),np.column_stack((p,np.full(4,h)))))
    return local@np.asarray(body['basis']).T+body['origin_m']

def body(radius,halfwidth,phi,zmax=12.5):
    a=math.radians(phi);er=np.array([math.cos(a),math.sin(a),0]);ep=np.array([-math.sin(a),math.cos(a),0])
    return dict(id=f'column/{phi}',origin_m=(radius*er).tolist(),basis=np.column_stack((ep,[0,0,1],er)).tolist(),vertices_m=[[-halfwidth,-zmax],[halfwidth,-zmax],[halfwidth,zmax],[-halfwidth,zmax]],depth_m=.5)

def intersection_vertices(A,B):
    # All vertices of a bounded 3D polytope occur at >=3 independent planes.
    tri=np.asarray(list(combinations(range(len(A)),3)));mat=A[tri];det=np.linalg.det(mat);tri=tri[abs(det)>1e-11];mat=A[tri]
    if not len(tri):return np.empty((0,3))
    vv=np.linalg.solve(mat,B[tri][...,None])[...,0];return vv[(vv@A.T<=B+2e-10).all(axis=1)]

def polygon(phi,R,w):
    a=math.radians(phi);u=np.array([math.cos(a),math.sin(a)]);v=np.array([-math.sin(a),math.cos(a)])
    return np.array([(R+x)*u+y*v for x,y in [(-.25,-w),(.25,-w),(.25,w),(-.25,w)]])

def polygon_distance(a,b):
    def point_segment(p,x,y):
        e=y-x;t=np.clip((p-x)@e/(e@e),0,1);return float(np.linalg.norm(p-x-t*e))
    return min([point_segment(p,x,y)for p in a for x,y in zip(b,np.roll(b,-1,axis=0))]+[point_segment(p,x,y)for p in b for x,y in zip(a,np.roll(a,-1,axis=0))])

def inset_phi_half(radius,halfwidth,border):return math.atan((halfwidth-border)/(radius+.25))

def union(intervals):
    out=[]
    for lo,hi in sorted(intervals):
        if out and lo<=out[-1][1]+1e-8:out[-1][1]=max(hi,out[-1][1])
        else:out.append([lo,hi])
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--revision',required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    rev=subprocess.check_output(['git','-C',str(args.repo),'rev-parse',args.revision+'^{commit}'],text=True).strip()
    blobs={p:read(args.repo,rev,p)for p in SOURCES};g=json.loads(blobs[GEOMETRY]);c=g['configuration']['chambers'];m=g['magnetic_configuration'];support=g['supports']['members'];N=c['barrel_facets'];delta=2*math.pi/N;R=c['barrel_apothems_m'][2];h=c['depth_m']/2;gap=c['gap_m'];border=c['active_border_m'];a=(R-h)*math.tan(delta/2)-gap/2;Ro=8.75
    b0=(Ro-h)*math.tan(delta/2)-gap/2
    bclose=(Ro+h)*math.tan(delta-inset_phi_half(R,a,0))
    bborder=border+(Ro+h)*math.tan(delta-inset_phi_half(R,a,border))
    btrial=border+(Ro+h)*math.tan(delta+math.radians(.1)-inset_phi_half(R,a,border))
    trials=[]
    for name,r,b in [('baseline',R,a),('radial_stagger_original_compartment_width',Ro,b0),('full_depth_closed',Ro,bclose),('border_full_depth_closed',Ro,bborder),('border_full_depth_0.1deg_overlap',Ro,btrial)]:
        phis={str(t):2*(inset_phi_half(R,a,t)+inset_phi_half(r,b,t))/ (2*delta)for t in [0,border]}
        overlap={str(t):math.degrees(inset_phi_half(R,a,t)+inset_phi_half(r,b,t)-delta)for t in [0,border]}
        trials.append(dict(name=name,odd_apothem_m=r,odd_halfwidth_m=b,odd_width_m=2*b,corner_radius_m=math.hypot(r+h,b),phi_union_fraction_no_axial_or_hardware_losses={k:min(1,v)for k,v in phis.items()},adjacent_full_depth_phi_overlap_deg=overlap,exact_xy_distance_to_even_m=polygon_distance(polygon(0,R,a),polygon(15,r,b))))
    e=body(R,a,0);o=body(R,btrial,15);A1,B1=planes(e);A2,B2=planes(o);w=intersection_vertices(np.vstack((A1,A2)),np.r_[B1,B2]);witness=w.mean(axis=0).tolist()
    assert len(w)>0
    same=dict(odd_apothem_m=R,odd_halfwidth_m=btrial,intersection_vertex_count=len(w),strict_interior_witness_m=witness,minimum_face_depth_m=float(np.min(np.r_[B1-A1@witness,B2-A2@witness])))
    constraint=dict(separating_axis='radial axis of odd facet',lower_bound_m=Ro-h-((R+h)*math.cos(delta)+a*math.sin(delta)),minimum_odd_apothem_for_20mm_m=h+gap+((R+h)*math.cos(delta)+a*math.sin(delta)))
    assert constraint['lower_bound_m']>.02
    bt=m['coil_groups']['barrel'];ect=[v for k,v in m['coil_groups'].items()if k.startswith('endcap')];warm=m['warm'];cc=c['coil_clearance_m']
    btmin=(Ro-h)*math.sin(delta)-btrial*math.cos(delta);ectmax=max(math.hypot(x['center_r_m']+x['half_r_m']+warm['normal_m']/2,warm['tangent_m']/2)for x in ect)
    coils=dict(scope='all points in odd B3 rectangles; every z; fixed finite warm sweeps; conservative Euclidean50mm proof',BT_nearest_plane_minimum_abs_tangent_m=btmin,BT_required_abs_tangent_m=warm['tangent_m']/2+cc,BT_slab_excess_m=btmin-warm['tangent_m']/2-cc,ECT_all_warm_points_maximum_radius_m=ectmax,odd_B3_minimum_radius_m=Ro-h,ECT_radial_gap_lower_bound_m=Ro-h-ectmax,ECT_clearance_m=cc)
    assert btmin>warm['tangent_m']/2+cc and Ro-h-ectmax>cc
    # Expanded support halfspaces contain the Euclidean50mm neighbourhood.
    # Intersect whole columns, never just corners. Bounded vertices locate all
    # possible z where the unchanged finite member reservation meets a column.
    records=[];support_bounds=[];all_station_records=[]
    for s in support:
        A,B=planes(s,c['support_clearance_m']);v=intersection_vertices(A,B);support_bounds.append((A,B,v.min(axis=0),v.max(axis=0)))
    for k in range(N):
        p=body(Ro if k%2 else R,btrial if k%2 else a,360*k/N);A,B=planes(p);v=vertices(p);lo,hi=v.min(axis=0),v.max(axis=0);hits=[]
        for s,(C,D,sl,sh)in zip(support,support_bounds):
            if np.any(hi<sl)or np.any(sh<lo):continue
            vv=intersection_vertices(np.vstack((A,C)),np.r_[B,D])
            if len(vv):hits.append(dict(id=s['id'],category=s['category'],z_interval_m=[float(vv[:,2].min()),float(vv[:,2].max())]))
        records.append(dict(facet=k,phi_deg=360*k/N,apothem_m=Ro if k%2 else R,halfwidth_m=btrial if k%2 else a,forbidden_z_union_m=union([x['z_interval_m']for x in hits]),members=hits))
    for j,(r,zmax)in enumerate(zip(c['barrel_apothems_m'],c['barrel_half_z_m']),1):
        aa=(r-h)*math.tan(delta/2)-gap/2
        for k in range(N):
            p=body(r,aa,360*k/N,zmax);A,B=planes(p);v=vertices(p);lo,hi=v.min(axis=0),v.max(axis=0);hits=[]
            for ss,(C,D,sl,sh)in zip(support,support_bounds):
                if np.any(hi<sl)or np.any(sh<lo):continue
                vv=intersection_vertices(np.vstack((A,C)),np.r_[B,D])
                if len(vv):hits.append(dict(id=ss['id'],category=ss['category'],z_interval_m=[float(vv[:,2].min()),float(vv[:,2].max())]))
            all_station_records.append(dict(station=j,facet=k,forbidden_z_union_m=union([x['z_interval_m']for x in hits]),members=hits))
    cross_sections=[polygon(360*k/N,Ro if k%2 else R,btrial if k%2 else a)for k in range(N)]
    pair_distances=[dict(facets=[i,j],distance_m=polygon_distance(cross_sections[i],cross_sections[j]))for i in range(N)for j in range(i+1,N)]
    pair_conflicts=[]
    for i in range(N):
        A,B=planes(body(Ro if i%2 else R,btrial if i%2 else a,360*i/N))
        for j in range(i+1,N):
            C,D=planes(body(Ro if j%2 else R,btrial if j%2 else a,360*j/N),gap)
            if len(intersection_vertices(np.vstack((A,C)),np.r_[B,D])):pair_conflicts.append([i,j])
    assert not pair_conflicts
    allsv=np.vstack([vertices(ss)for ss in support]);frsv=np.vstack([vertices(ss)for ss in support if not ss['category'].startswith('foot_')])
    counts={};families={}


    for j in [1,2,3]:
        pp=[p for p in g['panels']if p['kind']=='barrel'and p['station']==j];counts[str(j)]=len(pp)
        keys=Counter((round(max(v[0]for v in p['vertices_m'])-min(v[0]for v in p['vertices_m']),9),round(max(v[1]for v in p['vertices_m'])-min(v[1]for v in p['vertices_m']),9),p['depth_m'])for p in pp)
        families[str(j)]=[dict(width_m=x[0],length_m=x[1],depth_m=x[2],count=n)for x,n in keys.items()]
    ret=dict(assignment='BO-A1',status='DRAFT isolated PROTOTYPE; no engineering approval',input_revision=rev,source_sha256={p:hashlib.sha256(b).hexdigest()for p,b in blobs.items()},parameters=dict(facets=N,delta_deg=math.degrees(delta),even_apothem_m=R,even_halfwidth_m=a,depth_m=2*h,physical_gap_m=gap,border_m=border,odd_trial_apothem_m=Ro),neighbor_separation=constraint,trials=trials,same_radius_negative_control=same,all_z_odd_B3_coil_proof=coils,supports_total=len(support),support_corner_radius_bound_m=float(np.linalg.norm(allsv[:,:2],axis=1).max()),frame_without_feet_corner_radius_bound_m=float(np.linalg.norm(frsv[:,:2],axis=1).max()),all_B3_cross_section_pairs=dict(checked=len(pair_distances),minimum_distance_m=min(x['distance_m']for x in pair_distances),expanded_20mm_conflicts=pair_conflicts),B3_full_column_expanded_support_intersections=records,all_current_full_column_expanded_support_intersections=all_station_records,current_barrel_counts=counts,current_barrel_dimension_families=families,four_m_seed_counts={str(j):24*math.ceil((2*z+gap)/(4+gap))for j,z in enumerate(c['barrel_half_z_m'],1)},four_m_seed_lengths_m={str(j):(2*z-(math.ceil((2*z+gap)/(4+gap))-1)*gap)/math.ceil((2*z+gap)/(4+gap))for j,z in enumerate(c['barrel_half_z_m'],1)},even_B3_full_width_BT_interruption_abs_z_m=[bt['half_z_m']-bt['corner_radius_m']+math.sqrt((bt['corner_radius_m']-warm['normal_m']/2-cc)**2-((R+h)-(bt['center_r_m']+bt['half_r_m']-bt['corner_radius_m']))**2),bt['half_z_m']-bt['corner_radius_m']+math.sqrt((bt['corner_radius_m']+warm['normal_m']/2+cc)**2-((R-h)-(bt['center_r_m']+bt['half_r_m']-bt['corner_radius_m']))**2)],map_radius_m=m['map']['r_max_m'],source_world_radius_m=9.1,source_world_half_z_m=13.3,requested_chamber_radius_cap_m=9.4,trial_world_corner_margin_m=9.1-math.hypot(Ro+h,btrial),current_endcaps=len([p for p in g['panels']if p['kind']=='endcap']),limitations=['Phi fractions are 2D full-depth IP-ray bounds, independent of axial segmentation/hardware shadows.','Support conflicts conservatively use finite outer envelopes expanded by face offsets; empty hollow cavities remain reserved.','Only odd B3 has the whole-z analytic coil proof here. Even B3 retains BT end-return interruptions; B1/B2 require fresh full-volume checks under changed tiling.','Existing192endcaps and middle eta3 obstruction retained; no field recalculation, native propagation, chamber response or mechanical qualification performed.'])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(ret,indent=2)+'\n')
    print(json.dumps(dict(input_revision=rev,counts=counts,endcaps=ret['current_endcaps'],separation=constraint,coils=coils,trials=trials,support_representatives=[r for r in records if r['facet'] in [0,1]],all_station_support_representatives=[r for r in all_station_records if r['facet'] in [0,1]],four_m_seed_counts=ret['four_m_seed_counts'],four_m_seed_lengths_m=ret['four_m_seed_lengths_m'],even_B3_full_width_BT_interruption_abs_z_m=ret['even_B3_full_width_BT_interruption_abs_z_m'],negative=same,world_margin=ret['trial_world_corner_margin_m']),indent=2))

if __name__=='__main__':main()
