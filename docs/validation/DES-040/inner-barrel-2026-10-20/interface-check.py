#!/usr/bin/env python3
"""IB-A1 independent, standard-library finite-geometry interface check.
Reads Git blobs only. Writes only the requested scratch JSON. No repo imports.
"""
import argparse, copy, hashlib, json, math, platform, subprocess, sys, time
from pathlib import Path

PIN='56f12ef5b2a9bd410cb77e95ac3140557d92f1b2'
HCAL_PIN='0e8530d56d171f38c9d53d3c60c8b48803680bbd'
GEO='docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json'
INPUTS=['docs/design/DES-040-muon-chambers-frame.md',GEO,'tools/muon_layout/barrel_overlap.py','tools/muon_layout/layout.py','tools/muon_layout/geometry.py','tools/muon_layout/support.py','tools/toroid_prototype/geometry.py','docs/validation/MUON-001/hcal-material.json','docs/validation/DES-039/sources.json']
HCAL_INPUTS=['tools/hcal_barrel/design.py','tools/hcal_barrel/config.json','docs/validation/DES-037/summary.json']

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def add(a,b): return [x+y for x,y in zip(a,b)]
def sub(a,b): return [x-y for x,y in zip(a,b)]
def mul(s,a): return [s*x for x in a]
def norm(a): return math.sqrt(dot(a,a))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def unit(a): return mul(1/norm(a),a)
def column(q,j): return [r[j] for r in q]
def world(body,p): return add(body['origin_m'],[dot(r,p) for r in body['basis']])
def local(body,p): return [dot(column(body['basis'],i),sub(p,body['origin_m'])) for i in range(3)]
def poly_normals(poly):
    return [unit([b[1]-a[1],a[0]-b[0]]) for a,b in zip(poly,poly[1:]+poly[:1])]
def contained(body,p,tol=1e-10):
    x=local(body,p)
    return abs(x[2])<=body['depth_m']/2+tol and all(dot(n,sub(x[:2],v))<=tol for n,v in zip(poly_normals(body['vertices_m']),body['vertices_m']))
def expand(body,gap):
    out=copy.deepcopy(body);poly=out['vertices_m'];ns=poly_normals(poly);bs=[dot(n,p)+gap for n,p in zip(ns,poly)];vs=[]
    for i in range(4):
        a,b=ns[i-1],ns[i];c,d=bs[i-1],bs[i];det=a[0]*b[1]-a[1]*b[0]
        vs.append([(c*b[1]-a[1]*d)/det,(a[0]*d-c*b[0])/det])
    out['vertices_m']=vs;out['depth_m']+=2*gap;return out

def solid(body):
    h=body['depth_m']/2;v=[world(body,[p[0],p[1],z]) for z in [-h,h] for p in body['vertices_m']]
    q=body['basis'];n=[add(mul(a[0],column(q,0)),mul(a[1],column(q,1))) for a in poly_normals(body['vertices_m'])]+[column(q,2)]
    e=[sub(v[(i+1)%4],v[i]) for i in range(4)]+[sub(v[4],v[0])]
    return {'id':body['id'],'body':body,'v':v,'n':n,'e':e,'lo':[min(p[j] for p in v) for j in range(3)],'hi':[max(p[j] for p in v) for j in range(3)]}

def sat(a,b,tol=1e-10):
    if any(a['hi'][j]<b['lo'][j]-tol or b['hi'][j]<a['lo'][j]-tol for j in range(3)): return False
    axes=a['n']+b['n']+[cross(e,f) for e in a['e'] for f in b['e']]
    for ax in axes:
        if norm(ax)<1e-12: continue
        ax=unit(ax);pa=[dot(p,ax) for p in a['v']];pb=[dot(p,ax) for p in b['v']]
        if max(pa)<min(pb)-tol or max(pb)<min(pa)-tol: return False
    return True

def rounded_distance(u,z,g):
    rho=g['corner_radius_m'];qx=abs(u-g['center_r_m'])-(g['half_r_m']-rho);qz=abs(z-g['center_z_m'])-(g['half_z_m']-rho)
    return abs(math.hypot(max(qx,0),max(qz,0))+min(max(qx,qz),0)-rho)
def masks(p,c,width='warm',clearance=0):
    result=[];a=c[width]['normal_m']/2+clearance;b=c[width]['tangent_m']/2+clearance
    for name,g in c['coil_groups'].items():
        for k in range(c['folds']):
            ph=math.radians(g['phi_offset_deg']+k*360/c['folds']);u=p[0]*math.cos(ph)+p[1]*math.sin(ph);t=-p[0]*math.sin(ph)+p[1]*math.cos(ph)
            if abs(t)<=b+1e-12 and rounded_distance(u,p[2],g)<=a+1e-12: result.append([name,k])
    return result

def hcal_body(ident,sector,r0,r1,zhalf,tangent,inset,material):
    ph=sector*2*math.pi/16;c,s=math.cos(ph),math.sin(ph)
    poly=[[r0,-r0*tangent+inset],[r1,-r1*tangent+inset],[r1,r1*tangent-inset],[r0,r0*tangent-inset]]
    return dict(id=ident,origin_m=[0,0,0],basis=[[c,-s,0],[s,c,0],[0,0,1]],vertices_m=poly,depth_m=2*zhalf,material=material)

def poly_clip(poly,normal,bound):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da=dot(normal,a)-bound;db=dot(normal,b)-bound
        if da<=0: out.append(a)
        if (da<0 and db>0) or (da>0 and db<0): out.append(add(a,mul(da/(da-db),sub(b,a))))
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',required=True,type=Path);ap.add_argument('--revision',required=True);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args();start=time.monotonic()
    if args.revision!=PIN: raise ValueError('This bounded checker is pinned to '+PIN)
    sources={}
    def read(rev,path):
        b=subprocess.check_output(['git','-C',str(args.repo),'show',rev+':'+path]);sources[rev+':'+path]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};return b
    raw={p:read(PIN,p) for p in INPUTS};geo=json.loads(raw[GEO]);mag=geo['magnetic_configuration'];cc=geo['configuration']['chambers'];catalog=json.loads(raw['docs/validation/MUON-001/hcal-material.json'])
    assert catalog['repo_head']==HCAL_PIN
    hraw={p:read(HCAL_PIN,p) for p in HCAL_INPUTS}
    for p,b in hraw.items(): assert hashlib.sha256(b).hexdigest()==catalog['source_sha256'][p],p
    hc=json.loads(hraw['tools/hcal_barrel/config.json']);hs=json.loads(hraw['docs/validation/DES-037/summary.json']);assert hc==hs['config']
    assert len(geo['panels'])==888 and len(geo['supports']['members'])==484
    assert sum(p['kind']=='barrel' for p in geo['panels'])==696
    depth=cc['depth_m'];half=depth/2;clear=cc['coil_clearance_m'];bt=mag['coil_groups']['barrel'];assert depth==.5 and clear==.05
    straight_inner=bt['center_r_m']-bt['half_r_m'];warm_face=straight_inner-mag['warm']['normal_m']/2;below_max=warm_face-clear-half
    hbound=mag['hcal']['barrel_corner_radius_m'];conservative_min=hbound+clear+half
    tangent=math.tan(math.pi/hc['sectors']);hz=(hc['half_length_mm']-hc['end_flange_mm'])/1000;out=hc['proposed_outer_apothem_mm']/1000;rear=out-hc['back_cover_mm']/1000
    # Full finite plate wedge and rear cover shapes; all chamber/support SATs
    # use complete prisms, independent of projection/point witnesses.
    hcal=[]
    for sec in range(hc['sectors']):
        for lay in hs['layers']:
            a=lay['steel_front_mm']/1000;b=a+hc['steel_mm']/1000
            hcal.append(hcal_body('HCAL/S%02d/Steel%02d'%(sec,lay['layer']),sec,a,b,hz,tangent,(hc['sector_half_seam_mm']+hc['edge_rail_mm'])/1000,'Steel235'))
        hcal.append(hcal_body('HCAL/S%02d/RearCover'%sec,sec,rear,out,hz,tangent,hc['sector_half_seam_mm']/1000,'Aluminium'))
    b1=[p for p in geo['panels'] if p['kind']=='barrel' and p['station']==1];width=max(abs(p['vertices_m'][i][0]) for p in b1 for i in range(4))
    moved=[];retained=[]
    for p in b1:
        q=copy.deepcopy(p)
        if round(q['compartment']['phi_deg']/15)%2==0:
            ph=math.radians(q['compartment']['phi_deg']);q['origin_m']=[below_max*math.cos(ph),below_max*math.sin(ph),0];q['id']='UNSELECTED/BELOW/'+p['id'];moved.append(q)
        else: retained.append(q)
    # Actual finite cover support within the retained chamber's tangent span.
    plane_bounds=[]
    for k in range(mag['folds']):
        ph=math.radians(bt['phi_offset_deg']+k*360/mag['folds']);er=[math.cos(ph),math.sin(ph)];ep=[-math.sin(ph),math.cos(ph)];best=(-math.inf,None,None)
        for body in hcal:
            if body['material']!='Aluminium': continue
            poly=[world(body,p+[0])[:2] for p in body['vertices_m']];poly=poly_clip(poly,ep,width);poly=poly_clip(poly,mul(-1,ep),width)
            for v in poly:
                u=dot(er,v)
                if u>best[0]: best=(u,body['id'],v)
        plane_bounds.append(dict(coil_index=k,phi_deg=math.degrees(ph),maximum_actual_hcal_projection_m=best[0],cover_id=best[1],cover_vertex_xy_m=best[2],minimum_R_from_actual_cover_m=best[0]+clear+half,deficit_m=best[0]+clear+half-below_max,maximum_depth_with_both_50mm_margins_m=warm_face-best[0]-2*clear))
    msol=[solid(p) for p in moved];hsol=[solid(p) for p in hcal];sups=[solid(expand(p,cc['support_clearance_m'])) for p in geo['supports']['members']]
    hconf=[]
    for p in msol:
        hits=[q['id'] for q in hsol if sat(p,q)]
        if hits: hconf.append({'panel':p['id'],'actual_material_conflict_count':len(hits),'first_four_material_ids':hits[:4]})
    support_conflicts=[[p['id'],q['id']] for p in msol for q in sups if sat(p,q)]
    bsol=msol+[solid(p) for p in retained];pair_conflicts=[[p['id'],q['id']] for i,p in enumerate(bsol) for q in bsol[i+1:] if sat(p,q)]
    nonb=[solid(p) for p in geo['panels'] if p not in b1];other_conflicts=[[p['id'],q['id']] for p in msol for q in nonb if sat(p,q)]
    # Interior witnesses use actual retained central B1 Z02 panel, z=1m.
    trial=next(p for p in moved if p['id'].endswith('B1/F00/Z02'));plate=next(p for p in hcal if p['id']=='HCAL/S00/Steel35');cover=next(p for p in hcal if p['id']=='HCAL/S00/RearCover')
    steelpoint=[(hs['layers'][-1]['steel_front_mm']+hc['steel_mm']/2)/1000,0,1];coverpoint=[(rear+out)/2,0,1]
    outward=copy.deepcopy(trial);outward['origin_m']=[conservative_min,0,0];coilpoint=[straight_inner,0,1]
    witnesses={'steel':dict(point_m=steelpoint,panel_id=trial['id'],material_id=plate['id'],inside_trial=contained(trial,steelpoint),inside_actual_material=contained(plate,steelpoint)), 'rear_cover':dict(point_m=coverpoint,panel_id=trial['id'],material_id=cover['id'],inside_trial=contained(trial,coverpoint),inside_actual_material=contained(cover,coverpoint)), 'coil_if_raised_to_HCAL_bound':dict(R_m=conservative_min,point_m=coilpoint,inside_panel=contained(outward,coilpoint),warm_coils=masks(coilpoint,mag),pack_coils=masks(coilpoint,mag,'pack'))}
    # Source-rounded bound has 35.8nm round-off relative to a nominal no-seam
    # mathematical corner. Retain its bytes; report that interpretation limit.
    global_exact_corner=math.hypot(out,out*tangent-hc['sector_half_seam_mm']/1000)
    # Straight IP full-depth crossing has limiting far radial face, with border.
    beta_even=math.atan((width-cc['active_border_m'])/(below_max+half));beta_odd=math.atan((width-cc['active_border_m'])/(cc['barrel_apothems_m'][0]+half));angular=math.degrees(beta_even+beta_odd)-15
    sep=cc['barrel_apothems_m'][0]-half-((below_max+half)*math.cos(math.radians(15))+width*math.sin(math.radians(15)))
    angular_target_deg=.1
    derived_odd_half=(cc['barrel_apothems_m'][0]+half)*math.tan(math.radians(15+angular_target_deg)-beta_even)+cc['active_border_m']
    widened=[]
    for p in retained:
        q=copy.deepcopy(p); q['id']='UNSELECTED/WIDEN/'+p['id']; q['vertices_m']=[[math.copysign(derived_odd_half,x),z] for x,z in p['vertices_m']]; widened.append(q)
    widened_sol=[solid(p) for p in widened];mix=msol+widened_sol
    widened_pair_conflicts=[[p['id'],q['id']] for i,p in enumerate(mix) for q in mix[i+1:] if sat(p,q)]
    widened_support_conflicts=[[p['id'],q['id']] for p in widened_sol for q in sups if sat(p,q)]
    assert max(abs(z) for p in b1 for _,z in p['vertices_m'])+clear < bt['half_z_m']-bt['corner_radius_m']
    warm_straight=[]
    for k in range(mag['folds']):
        for tag,rleg in [('inner',bt['center_r_m']-bt['half_r_m']),('outer',bt['center_r_m']+bt['half_r_m'])]:
            a=mag['warm']['normal_m']/2; b=mag['warm']['tangent_m']/2; ph=math.radians(bt['phi_offset_deg']+k*360/mag['folds']);co,si=math.cos(ph),math.sin(ph)
            warm_straight.append(dict(id='BT/%02d/%s/straight'%(k,tag),origin_m=[0,0,0],basis=[[co,-si,0],[si,co,0],[0,0,1]],vertices_m=[[rleg-a,-b],[rleg+a,-b],[rleg+a,b],[rleg-a,b]],depth_m=2*(bt['half_z_m']-bt['corner_radius_m'])))
    warm_sol=[solid(p) for p in warm_straight]; warm50=[solid(expand(p,clear)) for p in warm_straight]
    warm_conflicts=[[p['id'],q['id']] for p in mix for q in warm_sol if sat(p,q)]
    warm50_conflicts=[[p['id'],q['id']] for p in mix for q in warm50 if sat(p,q)]
    projection_geometry=dict(unit='m',z_witness_m=1.,source_revision=HCAL_PIN,sector_count=hc['sectors'],steel_bands_m=[[p['steel_front_mm']/1000,(p['steel_front_mm']+hc['steel_mm'])/1000] for p in hs['layers']],steel_tangent_half_angle_rad=math.pi/hc['sectors'],steel_edge_inset_m=(hc['sector_half_seam_mm']+hc['edge_rail_mm'])/1000,steel_and_cover_abs_z_limit_m=hz,back_cover_bodies=[p for p in hcal if p['material']=='Aluminium'])
    positive=solid(trial);duplicate=solid(dict(trial,id='CONTROL/duplicate'));far=copy.deepcopy(trial);far['origin_m']=[100,0,0]
    controls=dict(duplicate_prism_detected=sat(positive,duplicate),distant_prism_separated=not sat(positive,solid(far)),occupied_steel_detected=sat(positive,solid(plate)),occupied_cover_detected=sat(positive,solid(cover)),all_48_moved_panels_have_actual_hcal_conflict=len(hconf)==48,warm_coil_point_detected=bool(masks(coilpoint,mag)),source_hashes_match=True,steel_point_inside_material_and_trial=contained(plate,steelpoint) and contained(trial,steelpoint),cover_point_inside_material_and_trial=contained(cover,coverpoint) and contained(trial,coverpoint),coil_point_inside_HCAL_clear_panel=contained(outward,coilpoint))
    assert all(controls.values())
    result=dict(assignment='IB-A1',role='SysArch explicit-instruction fallback',input_revision=PIN,hcal_source_revision=HCAL_PIN,status='PROTOTYPE feasibility evidence; requested central below-BT placement is infeasible; no implementation or approval',sources=sources,baseline=dict(panel_count=888,barrel_count=696,endcap_count=192,B1_count=len(b1),support_member_count=len(sups)),hard_bounds=dict(BT_inner_centerline_m=straight_inner,BT_warm_inner_face_m=warm_face,depth_m=depth,coil_clearance_m=clear,below_coil_R_max_m=below_max,HCAL_conservative_corner_bound_m=hbound,HCAL_conservative_R_min_m=conservative_min,conservative_interval_empty_by_m=conservative_min-below_max,actual_HCAL_outer_apothem_m=out,actual_finite_cover_max_corner_m=global_exact_corner,actual_vs_nominal_corner_scope='source-rounded corner bound encloses finite covers after1mm seam inset; not a filled HCAL cylinder',actual_HCAL_barrel_usable_half_z_m=hz,actual_cover_plane_bounds=plane_bounds),witnesses=witnesses,actual_HCAL_XY_geometry=projection_geometry,full_volume_checks=dict(moved_coil_plane_B1_count=len(moved),actual_hcal_material_prisms=len(hsol),HCAL_SAT_pair_count=len(msol)*len(hsol),moved_panels_with_actual_hcal_conflicts=hconf,support_envelopes_per_trial=len(sups),support_SAT_pair_count=len(msol)*len(sups),support_conflicts_at50mm=support_conflicts,B1_panel_pair_count=len(bsol)*(len(bsol)-1)//2,B1_pair_conflicts=pair_conflicts,other_chamber_pair_count=len(msol)*len(nonb),other_chamber_conflicts=other_conflicts,method='Independent stdlib 3D convex-prism SAT; support faces offset by50mm, touching conflicts. HCAL includes all36plates+rearcover for16sectors; otherHCALcomponents omitted, so detected intersections are actual source-model witnesses and clearance is not certified.'),angular_projection=dict(scope='Unselected counterfactual below-coil trial; retained fullwidth B1 intercoil; no HCAL clearance implied; same30mm border',even_below_R_m=below_max,odd_retained_R_m=cc['barrel_apothems_m'][0],half_width_m=width,full_depth_border_overlap_deg=angular,midplane_overlap_deg=math.degrees(math.atan(width/below_max)+math.atan(width/cc['barrel_apothems_m'][0]))-15,independent_radial_supporting_plane_gap_m=sep,widened_intercoil_half_width_for_0p1deg_full_depth_overlap_m=derived_odd_half,widened_intercoil_full_width_m=2*derived_odd_half,widened_B1_pair_count=len(mix)*(len(mix)-1)//2,widened_B1_pair_conflicts=widened_pair_conflicts,widened_odd_support_SAT_pair_count=len(widened_sol)*len(sups),widened_odd_support_conflicts=widened_support_conflicts,warm_straight_BT_SAT_pair_count=len(mix)*len(warm_sol),warm_straight_BT_physical_conflicts=warm_conflicts,warm_straight_BT_50mm_expanded_touch_conflicts=warm50_conflicts,warm_check_scope='AtB1absz<=6.4456 allBTcoils areexactstraightlegs; returnsstartabsz10.8, ECTwarmfront7.05 isaxiallyseparated. R4.05 islimiting50mmcontact, so conservative touching-is-conflict kernel rejects equality; smallerR cannotrescueHCAL.',widening_scope='Unselected mathematical width for retained30mm border and0.1deg full-depth angular target; all48inwardpanels remainHCAL-intersecting, no feasiblecandidateorapproval'),controls=controls,limits=['No DD4hep, Geant4, ACTS, native runtime, external service or dependency was invoked.','Warm and winding-pack sweeps are finite source-model reservations/current allocations; no engineered case/conductor material qualification.','Finite HCAL steel/Al witnesses are from hash-matched pinned prototype sources; not a measured installed detector.','All changed-radius certificates from original geometry are discarded in the hypothetical trial; no source layout is generated or selected.','500mm depth and50mm margins are fixed; all lower-depth/HCAL/magnet redesigns are unselected alternatives.'],runtime=dict(python=platform.python_version(),implementation=platform.python_implementation(),seconds=time.monotonic()-start,argv=sys.argv))
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'output':str(args.output),'source_hashes_matched':True,'below_R_max_m':below_max,'HCAL_bound_R_min_m':conservative_min,'actual_HCAL_conflicting_moved_panels':len(hconf),'moved_panel_count':len(moved),'support_conflict_count':len(support_conflicts),'B1_pair_conflict_count':len(pair_conflicts),'other_panel_conflict_count':len(other_conflicts),'controls':controls,'seconds':time.monotonic()-start},indent=2))
if __name__=='__main__': main()
