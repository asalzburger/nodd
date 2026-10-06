#!/usr/bin/env python3
"""DES017 isolated layout/support screening, never a production geometry writer."""
import argparse
from collections import Counter
import copy
import datetime
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import shapely
from shapely.geometry import Point
from shapely.strtree import STRtree
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
# Load the frozen sibling implementation under its own name (both have study.py).
SPEC = importlib.util.spec_from_file_location('disc_reference', ROOT/'tools/pixel_disc_optimization/study.py')
reference = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reference)
sys.modules['study'] = reference
sys.path.insert(0, str(ROOT/'tools/pixel_disc_optimization'))
import radial
import service_radius
sys.path.pop(0)
SPEC = importlib.util.spec_from_file_location('sheet_reference', ROOT/'tools/pixel_endcap_support/thermal.py')
sheet_reference = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sheet_reference)


def inputs():
    own = json.loads(Path(__file__).with_name('inputs.json').read_text())
    cfg, limits, prior = service_radius.load_config()
    cfg = copy.deepcopy(cfg)
    cfg['level_spacing_mm'] = own['level_spacing_mm']
    return own, cfg, limits, prior


def raw_control(cfg, prior):
    raw, rings = radial.candidates(cfg, prior['radial_margin_mm'], prior['phi_margin_mm'], prior['policy'])
    return [m for m in raw if m['row'] < 8], rings[:8]


def mixed(raw, rings, radii, populations, phases):
    modules = copy.deepcopy([m for m in raw if m['row'] < 4])
    result = copy.deepcopy(rings[:4])
    for row, radius, n, phase in zip([4, 5], radii, populations, phases):
        result.append(dict(row=row, family='quad', radius_mm=radius, modules=n, phase_cells=phase))
        for col in range(n):
            phi = 2*math.pi*(col+phase)/n
            i = len(modules)
            modules.append(dict(kind='polar', row=row, col=col, family='quad', module_id=200000+i,
                                sensor_id=200000+i, center_mm=[radius*math.cos(phi), radius*math.sin(phi), 0.],
                                u=[-math.sin(phi), math.cos(phi), 0.], v=[math.cos(phi), math.sin(phi), 0.]))
    return modules, result


def place(raw,cfg):
    """Return per-face graph colours; placement uses signed luminous compensation."""
    bodies=[radial.body_polygon(m,cfg).buffer(cfg['colour_padding_mm'],join_style=2) for m in raw]
    faces=[1 if m['col']%2 else -1 for m in raw]
    adjacency=[set() for _ in raw]
    for i,j in radial.intersecting_pairs(bodies,cfg['area_tolerance_mm2']):
        if faces[i]==faces[j]:adjacency[i].add(j);adjacency[j].add(i)
    colours={}
    while len(colours)<len(raw):
        remaining=[i for i in range(len(raw)) if i not in colours]
        i=max(remaining,key=lambda i:(len({colours[j] for j in adjacency[i] if j in colours}),len(adjacency[i]),-i))
        used={colours[j] for j in adjacency[i] if j in colours}
        colours[i]=next(k for k in range(len(raw)) if k not in used)
    return faces,colours


def placed_modules(raw,cfg,datum):
    faces,colours=place(raw,cfg);result=[]
    anchor=(datum*datum-cfg['luminous_half_z_mm']**2)/datum
    for i,m in enumerate(raw):
        dz=faces[i]*(cfg['plate_to_module_mm']+colours[i]*cfg['level_spacing_mm'])
        c=np.asarray(m['center_mm']).copy();c[:2]*=1+dz/anchor;c[2]=datum+dz
        result.append(dict(m,center_mm=c.tolist(),local_z_mm=dz,level=colours[i],mount_face=faces[i]))
    return result


def stem_shapes(modules, cfg, own):
    stems = []
    for m in modules:
        for patch in radial.active_patches([m], cfg):
            c=np.asarray(patch['center_mm']).copy()
            if m['family']=='single':
                c+=own['stem_offsets_mm']['single_radial']*np.asarray(m['v'])
            else:
                sign=1 if patch['patch']//cfg['families'][m['family']]['rows']==0 else -1
                c+=sign*own['stem_offsets_mm']['quad_toward_center_u']*np.asarray(m['u'])
                sign=1 if patch['patch']%cfg['families'][m['family']]['rows']==0 else -1
                c+=sign*own['stem_offsets_mm']['quad_toward_center_v']*np.asarray(m['v'])
            stems.append(dict(module_id=m['module_id'], patch_id=patch['id'], row=m['row'],
                              polygon=reference.rectangle(c, m['u'], m['v'], *np.asarray(own['stem_mm'])/2),
                              center_mm=c.tolist(),
                              mount_face=m.get('mount_face',1),
                              top_z_mm=m['local_z_mm']-m.get('mount_face',1)*(cfg['body_thickness_mm']/2+sum(own['pickup_mm'].values()))))
    return stems


def support_screen(modules, cfg, limits, own):
    bodies = [radial.body_polygon(m, cfg) for m in modules]
    tree = STRtree(bodies)
    stems = stem_shapes(modules, cfg, own)
    collisions = []
    insert_collisions=[]
    horizontal_gaps = []
    tol = own['geometry_tolerance_mm']
    plate_top = 3.15  # inherited half of the SV-C05 6.3mm sandwich
    for s in stems:
        poly = s['polygon']
        owner = next(i for i, m in enumerate(modules) if m['module_id'] == s['module_id'])
        if not bodies[owner].buffer(tol).covers(poly):
            raise ValueError('Thermal stem outside its occupied module')
        for j in tree.query(poly.buffer(cfg['required_gap_mm']), predicate='intersects'):
            j = int(j)
            if j == owner:
                continue
            face=modules[j].get('mount_face',1)
            lo = modules[j]['local_z_mm']-cfg['body_thickness_mm']/2-(sum(own['pickup_mm'].values()) if face==1 else 0)
            hi = modules[j]['local_z_mm']+cfg['body_thickness_mm']/2+(sum(own['pickup_mm'].values()) if face==-1 else 0)
            a,b=sorted([s['mount_face']*plate_top,s['top_z_mm']])
            if min(b, hi) > max(a, lo)+tol:
                gap = poly.distance(bodies[j])
                horizontal_gaps.append(gap)
                if gap < cfg['required_gap_mm']-tol:
                    collisions.append(dict(stem_patch=s['patch_id'], other_module=modules[j]['module_id'], xy_gap_mm=gap))
    body = radial.body_screen(modules, cfg)
    polygons=[s['polygon'] for s in stems]
    for i,j in radial.intersecting_pairs([p.buffer(cfg['required_gap_mm']/2) for p in polygons],cfg['area_tolerance_mm2']):
        insert_collisions.append([stems[i]['patch_id'],stems[j]['patch_id']])
    collector_gap = own['collector_start_local_z_mm']-body['occupied_local_z_mm'][1]
    max_radius = max(body['maximum_radius_mm'], max(service_radius.radius_of(s['polygon']) for s in stems))
    barrel_gap=cfg['disc_datum_mm']+body['occupied_local_z_mm'][0]-605.
    return dict(passed=not collisions and not insert_collisions and collector_gap >= cfg['required_gap_mm']-tol and max_radius<=limits['plate_outer_mm'] and barrel_gap>=cfg['required_gap_mm']-tol,
                stems=len(stems), stem_lower_module_collisions=collisions,
                core_insert_xy_conflicts=insert_collisions,nearest_plate_barrel_turn_gap_mm=barrel_gap,
                minimum_tested_horizontal_stem_gap_mm=min(horizontal_gaps) if horizontal_gaps else None,
                max_radius_mm=max_radius, plate_clearance_mm=limits['plate_outer_mm']-max_radius,
                collector_axial_gap_mm=collector_gap,
                body=body, pickup_gap_mm=body['minimum_z_gap_mm']-sum(own['pickup_mm'].values()),
                scope='Prismatic stem/body/pickup bounds at all stations. Contact hardware, flex sweeps, tube bends and tolerance stack not qualified.')


def screen(raw, cfg, limits, own, datum, detail=True):
    placed = placed_modules(raw, cfg, datum)
    body = radial.body_screen(placed, cfg)
    metric = reference.metrics if detail else scan_metrics
    sensor = metric(radial.project(placed, cfg, datum, guard=cfg['sensor_guard_mm']), cfg)
    active = [dict(vertex_z_mm=v, **metric(radial.project(placed, cfg, datum, vertex=v), cfg)) for v in cfg['vertices_z_mm']]
    overlap = max(sensor['overlap_over_union_percent'], sensor['annular_overlap_over_union_percent'])
    mechanical = support_screen(placed, cfg, limits, own) if detail else None
    passed = body['maximum_radius_mm']<=limits['plate_outer_mm'] and not body['overlaps_or_insufficient_gap'] and overlap<=cfg['overlap_limit_percent']
    return placed, dict(datum_mm=datum, sensor=sensor, active_vertices=active,
                        worst_gap_mm2=max(x['uncovered_annulus_superset_mm2'] for x in active),
                        overlap_percent=overlap, interface_overlap_pass=passed, support=mechanical, body=body)


def scan_metrics(polygons,cfg):
    """Cheap ranking only; retained station bounds always use the original2048 grid."""
    a=reference.annulus(cfg,resolution=128);superset=reference.annulus(cfg,resolution=128,superset=True)
    union=unary_union(polygons);summed=sum(p.area for p in polygons)
    clipped=float(shapely.area(shapely.intersection(np.asarray(polygons,dtype=object),a)).sum())
    inside=union.intersection(a).area
    return dict(overlap_over_union_percent=100*(summed/union.area-1),annular_overlap_over_union_percent=100*(clipped/inside-1),uncovered_annulus_superset_mm2=superset.difference(union).area,
                polygon_circle_area_error_bound_mm2=superset.area-a.area,ranking_only=True,annulus_quad_segments=128)


def cooling(modules, rings, cfg, own):
    tracks = []
    circuits = []
    chips = radial.active_patches(modules, cfg)
    by_patch={s['patch_id']:s for s in stem_shapes(modules,cfg,own)}
    f = own['cooling']
    for ring in rings:
        family = cfg['families'][ring['family']]
        for radial_row in range(family['rows']):
            patches = [p for p in chips if p['row']==ring['row'] and p['patch']%family['rows']==radial_row]
            radii = [math.hypot(*by_patch[p['id']]['center_mm'][:2]) for p in patches]
            radius = (min(radii)+max(radii))/2
            reach = (max(radii)-min(radii))/2+f['tube_OD_mm']/2
            tracks.append(dict(physical_ring=ring['row']+1, chip_row=radial_row,
                               radius_mm=radius, stem_to_track_max_offset_mm=(max(radii)-min(radii))/2,
                               saddle_radial_reach_mm=reach, stem_half_v_mm=own['stem_mm'][1]/2,
                               radial_contact_pass=reach<=own['stem_mm'][1]/2))
            for half in range(2):
                count = sum(1 for p in patches if int(p['col']>=ring['modules']/2)==half)
                nominal = count*own['power_W_chip']
                stress = nominal*own['stress_multiplier']
                minimum = stress/(f['latent_J_g']*(f['quality_limit']-f['quality_in']))
                flow = max(f['minimum_flow_g_s'], math.ceil(minimum/f['flow_rounding_g_s']-1e-12)*f['flow_rounding_g_s'])
                circuits.append(dict(physical_ring=ring['row']+1, chip_row=radial_row, half=half,
                                     chips=count, nominal_W=nominal, stress_W=stress, flow_g_s=flow,
                                     outlet_quality=f['quality_in']+stress/(flow*f['latent_J_g']),
                                     arc_mm=math.pi*radius, radial_legs_mm=2*(188.5-radius),
                                     bends_allowance_mm=2*f['bend_allowance_per_leg_mm']))
    tube_length = sum(c['arc_mm']+c['radial_legs_mm']+c['bends_allowance_mm'] for c in circuits)
    return dict(tracks=tracks, circuits=circuits, number_tracks=len(tracks), number_circuits=len(circuits),
                feed_return_legs=2*len(circuits), total_flow_g_s=sum(c['flow_g_s'] for c in circuits),
                nominal_W=len(chips)*own['power_W_chip'], stress_W=len(chips)*own['power_W_chip']*own['stress_multiplier'],
                estimated_tube_length_mm=tube_length,
                tube_envelope_volume_mm3=tube_length*math.pi*(f['tube_OD_mm']/2)**2,
                skin_nominal_clearance_mm=3.-max(abs(x) for x in f['routing_planes_mm'])-f['tube_OD_mm']/2,
                crossing_nominal_clearance_mm=abs(f['routing_planes_mm'][1]-f['routing_planes_mm'][0])-f['tube_OD_mm'],
                scope='Azimuthal evaporators plus both radial legs and bend allowance. Branch-end routing, fittings, pressure drop, boiling stability and manifold CAD remain open.')


def thermal(modules, cfg, own):
    t = own['thermal']; f = own['cooling']; pick = own['pickup_mm']
    area = math.prod(own['stem_mm'])*1e-6
    # To far tube centre; 180-degree saddle and two bonded narrow interfaces.
    length = max(abs(m['local_z_mm'])-.5-sum(pick.values())+1.5 for m in modules)
    fixed = dict(stem_core_K_W=length/1000/(t['stem_axial_k_W_m_K']*area),
                 bonds_K_W=2*pick['bond']/1000/(t['bond_k_W_m_K']*area),
                 sheet_normal_K_W=pick['graphite']/1000/(t['normal_k_W_m_K']*area),
                 full_chip_interface_K_W=(pick['TIM']/1000/t['TIM_k_W_m_K']+pick['insulator']/1000/t['insulator_k_W_m_K'])/(math.prod(cfg['active_mm'])*1e-6),
                 Ti_saddle_K_W=math.log(f['tube_OD_mm']/(f['tube_OD_mm']-2*f['tube_wall_mm']))/(math.pi*t['Ti_k_W_m_K']*own['stem_mm'][0]/1000))
    variants=[]; convergence=[]
    wet_area = math.pi*(f['tube_OD_mm']-2*f['tube_wall_mm'])*own['stem_mm'][0]*1e-6
    for family,offset in [('single',own['stem_offsets_mm']['single_radial']),('quad',own['stem_offsets_mm']['quad_toward_center_v'])]:
      if not any(m['family']==family for m in modules):continue
      for k in t['inplane_k_W_m_K']:
        for fraction in [0., t['edge_fraction']]:
            solve = sheet_reference.sheet_resistance(*cfg['active_mm'], *own['stem_mm'], offset, k, pick['graphite'], t['fine_grid_mm'], fraction, t['edge_width_mm'], t['cg_relative_tolerance'])
            if k == t['inplane_k_W_m_K'][0]:
                coarse=sheet_reference.sheet_resistance(*cfg['active_mm'], *own['stem_mm'], offset, k, pick['graphite'], t['coarse_grid_mm'], fraction, t['edge_width_mm'], t['cg_relative_tolerance'])
                convergence.append(dict(family=family,edge_fraction=fraction, fine_K_W=solve['max_K_W'], coarse_K_W=coarse['max_K_W'], relative_change=abs(coarse['max_K_W']/solve['max_K_W']-1)))
            for h in f['htc_W_m2_K']:
                R=solve['max_K_W']+sum(fixed.values())+1/(h*wet_area)
                variants.append(dict(family=family,contact_offset_v_mm=offset,k_inplane_W_m_K=k, edge_fraction=fraction, h_W_m2_K=h, sheet=solve, total_K_W=R,
                                     nominal_C=f['coolant_C']+own['power_W_chip']*R,
                                     stress_C=f['coolant_C']+own['power_W_chip']*own['stress_multiplier']*R,
                                     warm_stress_C=f['warm_coolant_C']+own['power_W_chip']*own['stress_multiplier']*R))
    return dict(fixed=fixed, worst_path_length_mm=length, variants=variants, convergence=convergence,
                all_stress_minus40_pass=all(v['stress_C']<=f['sensor_screen_C'] for v in variants),
                all_stress_minus35_pass=all(v['warm_stress_C']<=f['sensor_screen_C'] for v in variants),
                scope='Independent chip pickup approximation; quad thermal cross-talk ignored. Full-circumference boiling area optimistic:10k h represents half of20k. No leakage feedback, pressure drop or thermal FEA qualification.')


def budget(modules, cfg, own, cool):
    inherited=json.loads((ROOT/'tools/pixel_support/inputs.json').read_text())
    density=inherited['density_g_cm3']
    area=math.pi*(188.5**2-27.**2)
    chips=radial.active_patches(modules,cfg)
    stem_area=math.prod(own['stem_mm'])
    stems=stem_shapes(modules,cfg,own)
    # Subtract pipe bores and stem/core inserts from foam: never stack full core + solids.
    core_insert_volume=stem_area*sum(3.15+1.5 for s in stems)
    ti_volume=cool['estimated_tube_length_mm']*math.pi*((own['cooling']['tube_OD_mm']/2)**2-(own['cooling']['tube_OD_mm']/2-own['cooling']['tube_wall_mm'])**2)
    pickup_area=len(chips)*math.prod(cfg['active_mm'])
    components=dict(CFRP_skin_g=2*.15*(area-len(stems)*stem_area)/1000*density['CFRP'],
                    foam_g=(6*area-cool['tube_envelope_volume_mm3']-core_insert_volume-.08*area)/1000*density['foam'],
                    graphite_pickup_g=pickup_area*own['pickup_mm']['graphite']/1000*density['graphite'],
                    graphite_stems_and_core_g=stem_area*sum(abs(s['top_z_mm'])+1.5 for s in stems)/1000*density['graphite'],
                    titanium_tubes_g=ti_volume/1000*density['titanium'],
                    pickup_cradle_g=pickup_area*own['pickup_mm']['cradle']/1000*density['CFRP'],
                    insulation_g=pickup_area*own['pickup_mm']['insulator']/1000*density['insulation'],
                    TIM_g=pickup_area*own['pickup_mm']['TIM']/1000*density['glue'],
                    pickup_and_stem_bond_g=(pickup_area+2*len(stems)*stem_area)*own['pickup_mm']['bond']/1000*density['glue'],
                    core_glue_g=.08*area/1000*density['glue'],
                    clips_g=.1*len(modules), disc_mount_allowance_g=12.)
    # SADDLING removes180deg tube envelope from graphite/core inserts, allocated once.
    bore=len(stems)*math.pi*(own['cooling']['tube_OD_mm']/2)**2/2*own['stem_mm'][0]
    components['graphite_stems_and_core_g']-=bore/1000*density['graphite']
    # Restore intersection already subtracted in both core tube/insert reservations.
    components['foam_g']+=bore/1000*density['foam']
    dry=sum(components.values())
    payload=len(chips)  # inherited1g/chip proxy, not a BOM
    span=math.sqrt(3)*188.5
    I=2*188.5*2*.15*(6.3/2-.15/2)**2
    force=(dry+payload)/1000*9.80665
    stiffness=[dict(E_GPa=E, distributed_deflection_mm=5*force*span**3/(384*E*1000*I), point_load_deflection_mm=force*span**3/(48*E*1000*I)) for E in [70.,100.,140.]]
    return dict(components=components, local_dry_screen_g=dry, payload_proxy_g=payload, gravity_beam_brackets=stiffness,
                scope='Displaced foam/skin and shared quad payload counted once. Estimated local core/pickups/tubes/clips/mounts; excludes flexes, CO2 inventory, edge closeouts, tongue details, manifolds and shared carrier. Beam brackets are not disc/laminate FEA or alignment qualification.')


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    own,cfg,limits,prior=inputs(); raw,rings=raw_control(cfg,prior)
    scan=[]; candidates=[]; s=own['quad_scan']
    from itertools import product
    for r1,r2,n1,n2,p1,p2 in product(s['inner_radii_mm'],s['outer_radii_mm'],s['inner_populations'],s['outer_populations'],s['phase_cells'],s['phase_cells']):
        trial, rr=mixed(raw,rings,[r1,r2],[n1,n2],[p1,p2])
        placed,check=screen(trial,cfg,limits,own,cfg['disc_datum_mm'],detail=False)
        entry=dict(radii_mm=[r1,r2],populations=[n1,n2],phases=[p1,p2],chips=len(radial.active_patches(trial,cfg)),
                   gap_mm2=check['worst_gap_mm2'],overlap_percent=check['overlap_percent'],max_body_radius_mm=check['body']['maximum_radius_mm'],levels=check['body']['levels'],passing=check['interface_overlap_pass'])
        scan.append(entry)
        if len(scan)%24==0:print(json.dumps(dict(scan_candidates=len(scan))),flush=True)
        if entry['passing']:
            candidates.append((entry['gap_mm2'],entry['chips'],entry['overlap_percent'],trial,rr,entry))
    chosen=None; rejected=[]
    (out/'scan.json').write_text(json.dumps(dict(ranking_annulus_quad_segments=own['scan_annulus_quad_segments'],candidates=scan),indent=2)+'\n')
    for _,_,_,trial,rr,entry in sorted(candidates,key=lambda x:x[:3]):
        # Fast rejection before computing expensive full-precision station metrics.
        quick=[support_screen(placed_modules(trial,cfg,z),cfg,limits,own) for z in cfg['positive_disc_datums_mm']]
        if not all(c['passed'] for c in quick):
            rejected.append(dict(candidate=entry,supports=quick))
            continue
        checks=[screen(trial,cfg,limits,own,z)[1] for z in cfg['positive_disc_datums_mm']]
        if all(c['interface_overlap_pass'] and c['support']['passed'] for c in checks):
            chosen=trial,rr,entry;break
        rejected.append(dict(candidate=entry, failed_stations=[dict(datum_mm=c['datum_mm'], support=c['support']) for c in checks if not c['support']['passed'] or not c['interface_overlap_pass']]))
        if len(rejected)>=12:
            break
    # Retain best fitting layout even if the support design needs an explicit amendment.
    if chosen is None:
        best=sorted(candidates,key=lambda x:x[:3])[0]
        chosen=best[3],best[4],best[5]
    report=dict(status=own['status'], scan=scan, rejected_support_candidates=rejected, selected=chosen[2],variants={})
    for name,source,rr in [('eight-single',raw,rings),('four-single-two-quad',chosen[0],chosen[1])]:
        checks=[screen(source,cfg,limits,own,z)[1] for z in cfg['positive_disc_datums_mm']]
        placed=placed_modules(source,cfg,cfg['disc_datum_mm'])
        cool=cooling(placed,rr,cfg,own)
        services=service_radius.fixed_services(placed,rr,cfg,limits)
        # Same 16 chip-row circuits; the generic physical-ring helper would undercount quads.
        if services['local_circuits']!=cool['number_circuits']:
            inp=json.loads((ROOT/cfg['services_input']).read_text())
            extra=(cool['number_circuits']-services['local_circuits'])*math.pi*2*(own['cooling']['transport_OD_mm']/2)**2
            for scenario in services['scenarios']:
                scenario['feed_return_pipe_mm2']+=extra
                for side in scenario['end_trunks']:
                    side['after_disc_8_demand_mm2']+=8*extra*inp['scenarios'][scenario['scenario']]['demand_multiplier']
                    side.update(utilization=side['after_disc_8_demand_mm2']/side['capacity_mm2'],flange_neck_utilization=side['after_disc_8_demand_mm2']/side['flange_neck_capacity_mm2'])
                    side['status']='PASS' if side['utilization']<=1 else 'FAIL'
                    side['flange_neck_status']='PASS' if side['flange_neck_utilization']<=1 else 'FAIL'
            services['local_circuits']=cool['number_circuits']
            services['local_feed_return_radial_legs']=cool['feed_return_legs']
        report['variants'][name]=dict(modules=len(placed),chips=len(radial.active_patches(placed,cfg)),families=dict(Counter(m['family'] for m in placed)),rings=rr,
                                     per_disc_screens=checks,cooling=cool,thermal=thermal(placed,cfg,own),budget=budget(placed,cfg,own,cool),services=services,
                                     orientation=radial.orientation_screen(placed,cfg), guard_0p5mm_control=reference.metrics(radial.project(placed,cfg,cfg['disc_datum_mm'],guard=.5),cfg),
                                     all_18_interface_overlap_pass=all(c['interface_overlap_pass'] for c in checks),all_18_support_pass=all(c['support']['passed'] for c in checks),
                                     original_annulus_hermetic=False)
        (out/(name+'-layout.json')).write_text(json.dumps(dict(status=own['status'],raw_modules=source,modules=placed,active_patches=radial.active_patches(placed,cfg),rings=rr),indent=2)+'\n')
    paths=[Path(__file__),Path(__file__).with_name('inputs.json'),ROOT/own['control_layout'],ROOT/'tools/pixel_disc_optimization/radial.py',ROOT/'tools/pixel_disc_optimization/radial-inputs.json',ROOT/'tools/pixel_disc_optimization/study.py',ROOT/'tools/pixel_disc_optimization/service_radius.py',ROOT/'tools/pixel_disc_optimization/service-radius-inputs.json',ROOT/'tools/pixel_endcap_support/thermal.py',ROOT/'tools/pixel_endcap_support/inputs.json',ROOT/'tools/pixel_support/inputs.json',ROOT/cfg['services_input'],ROOT/cfg['barrel_services']]
    report['provenance']=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=platform.python_version(),numpy=np.__version__,shapely=shapely.__version__,hashes={str(p.relative_to(ROOT)):reference.digest(p) for p in paths})
    (out/'screening.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({n:dict(modules=r['modules'],chips=r['chips'],support_pass=r['all_18_support_pass'],interface_pass=r['all_18_interface_overlap_pass'],r_max=max(c['body']['maximum_radius_mm'] for c in r['per_disc_screens']),overlap=max(c['overlap_percent'] for c in r['per_disc_screens']),worst_gap_mm2=max(c['worst_gap_mm2'] for c in r['per_disc_screens']),thermal40=r['thermal']['all_stress_minus40_pass'],thermal35=r['thermal']['all_stress_minus35_pass']) for n,r in report['variants'].items()},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
