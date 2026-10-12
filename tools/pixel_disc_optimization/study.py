#!/usr/bin/env python3
"""DES016 isolated PROTOTYPE: finite RD53i disc coverage, overlap and services."""
import argparse
import datetime
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import numpy as np
import shapely
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rectangle(center, u, v, hu, hv):
    c, u, v = np.asarray(center[:2]), np.asarray(u[:2]), np.asarray(v[:2])
    return Polygon([c + a * hu * u + b * hv * v
                    for a, b in [(-1, -1), (1, -1), (1, 1), (-1, 1)]])


def annulus(cfg, resolution=2048, superset=False):
    a, b = cfg['annulus_mm']
    # Inscribed inner / circumscribed outer polygons contain the true annulus.
    outer = b / math.cos(math.pi / (4 * resolution)) if superset else b
    return Point(0, 0).buffer(outer, quad_segs=resolution).difference(
        Point(0, 0).buffer(a, quad_segs=resolution))


def polar(cfg, margin=0.):
    a, end = cfg['annulus_mm']; hu, hv = np.asarray(cfg['active_mm']) / 2
    rings = []
    while a < end:
        for n in range(3, 256):
            r = a * math.cos(math.pi / n) + hv - margin
            if (r + hv) * math.sin(math.pi / n) <= hu: break
        else: raise ValueError('No bounded phi solution')
        rings.append((r, n)); a = r + hv
    return rings


def candidates(cfg, pitch_reduction=0.3):
    au, av = cfg['active_mm']; px, py = au-pitch_reduction, av-pitch_reduction
    guard = cfg['sensor_guard_mm']; bu, bv = cfg['body_mm']
    result = []
    # Inner ring compensates the lattice beam-pipe cut. Its extra phi redundancy
    # is an explicit choice; no active pixel matrix is stretched or cropped.
    n = cfg['inner_phi_modules']; r = cfg['inner_ring_radius_mm']
    for k in range(n):
        phi = 2*math.pi*k/n
        result.append(dict(kind='inner-polar', row=0, col=k, center_mm=[r*math.cos(phi),r*math.sin(phi),0.],
                           u=[-math.sin(phi),math.cos(phi),0.],v=[math.cos(phi),math.sin(phi),0.]))
    target = annulus(cfg, resolution=256)
    ring = unary_union([rectangle(m['center_mm'],m['u'],m['v'],au/2,av/2) for m in result])
    for i in range(-cfg['lattice_limit'],cfg['lattice_limit']+1):
        for j in range(-cfg['lattice_limit'],cfg['lattice_limit']+1):
            x,y=i*px,j*py
            # Periphery is directed outward in y; axes retain a proper frame.
            v=[0.,1. if y>=0 else -1.,0.];u=[v[1],0.,0.]
            body=rectangle([x,y+v[1]*cfg['periphery_offset_mm'],0.],u,v,bu/2,bv/2)
            active=box(x-au/2,y-av/2,x+au/2,y+av/2)
            if body.distance(Point(0,0))<cfg['beam_clearance_radius_mm']:continue
            area=active.intersection(target)
            if area.area==0 or area.difference(ring).area<cfg['area_tolerance_mm2']:continue
            result.append(dict(kind='cartesian',row=i,col=j,center_mm=[x,y,0.],u=u,v=v))
    for i,m in enumerate(result):
        m.update(template_pitch_reduction_mm=pitch_reduction,id=100000+i,sensor_id=100000+i,module_id=100000+i,layer_id='DES016-template',
                 half_u_mm=au/2,half_v_mm=av/2,subsystem='pixel',region='endcap',family='single')
    return result


def body_polygon(m,cfg):
    center=np.asarray(m['center_mm'])+cfg['periphery_offset_mm']*np.asarray(m['v'])
    return rectangle(center,m['u'],m['v'],cfg['body_mm'][0]/2,cfg['body_mm'][1]/2)


def stagger(modules,cfg,datum):
    """Deterministic DSATUR colouring; expand conflicts for centre compensation."""
    modules=[dict(m,center_mm=list(m['center_mm'])) for m in modules]
    au,av=cfg['active_mm']
    for m in modules:
        if m['kind']=='cartesian':
            red=m['template_pitch_reduction_mm'];scaled_red=red*cfg['disc_datum_mm']/datum
            m['center_mm'][0]*=(au-scaled_red)/(au-red)
            m['center_mm'][1]*=(av-scaled_red)/(av-red)
    bodies=[body_polygon(m,cfg).buffer(cfg['colour_padding_mm'],join_style=2) for m in modules]
    adjacency=[set() for _ in modules]
    for i,a in enumerate(bodies):
        for j in range(i):
            if a.intersection(bodies[j]).area>cfg['area_tolerance_mm2']:
                adjacency[i].add(j);adjacency[j].add(i)
    colors={}
    while len(colors)<len(modules):
        available=[i for i in range(len(modules)) if i not in colors]
        i=max(available,key=lambda i:(len({colors[j] for j in adjacency[i] if j in colors}),len(adjacency[i]),-i))
        used={colors[j] for j in adjacency[i] if j in colors}
        colors[i]=next(k for k in range(len(modules)) if k not in used)
    output=[]
    for i,m in enumerate(modules):
        dz=cfg['plate_to_module_mm']+colors[i]*cfg['level_spacing_mm']
        c=np.asarray(m['center_mm']).copy();half=cfg['luminous_half_z_mm']
        anchor_distance=(datum*datum-half*half)/datum
        c[:2]*=1+dz/anchor_distance;c[2]=datum+dz
        output.append(dict(m,center_mm=c.tolist(),level=colors[i],local_z_mm=dz))
    return output


def project(modules,cfg,datum,vertex=0.,guard=0.):
    au,av=cfg['active_mm'];polygons=[]
    for m in modules:
        scale=(datum-vertex)/(m['center_mm'][2]-vertex)
        p=rectangle(m['center_mm'],m['u'],m['v'],au/2+guard,av/2+guard)
        polygons.append(Polygon([(x*scale,y*scale) for x,y in p.exterior.coords]))
    return polygons


def metrics(polygons,cfg):
    union=unary_union(polygons);a=annulus(cfg);superset=annulus(cfg,superset=True)
    summed=sum(p.area for p in polygons);clipped=sum(p.intersection(a).area for p in polygons)
    inside=union.intersection(a).area
    return dict(summed_mm2=summed,union_mm2=union.area,
                overlap_over_union_percent=100*(summed/union.area-1),
                overlap_over_installed_percent=100*(1-union.area/summed),
                annular_overlap_over_union_percent=100*(clipped/inside-1),
                installed_outside_annulus_mm2=summed-clipped,
                uncovered_annulus_superset_mm2=superset.difference(union).area,
                polygon_circle_area_error_bound_mm2=superset.area-a.area,
                covered_fraction=inside/a.area)


def coverage_certificate(modules,cfg,datum):
    """Prove coverage over continuous on-axis vertex intervals by containment.

    Each projected plane rectangle is a monotone homothety about the origin.
    The intersection of its two endpoint footprints is contained in every
    intermediate footprint. Union containment of an annulus
    superset therefore certifies each accepted interval without a ray raster.
    """
    target=annulus(cfg,superset=True);half=cfg['luminous_half_z_mm']
    stack=[(-half,half,0)];intervals=[];failed=[]
    while stack:
        a,b,depth=stack.pop()
        common=[x.intersection(y) for x,y in zip(project(modules,cfg,datum,a),project(modules,cfg,datum,b))]
        gap=target.difference(unary_union(common)).area
        if gap<=cfg['area_tolerance_mm2']:
            intervals.append(dict(lo_vertex_mm=a,hi_vertex_mm=b,gap_upper_mm2=gap));continue
        if depth>=cfg['certificate_max_depth']:
            failed.append(dict(lo_vertex_mm=a,hi_vertex_mm=b,gap_upper_mm2=gap));continue
        c=(a+b)/2;stack.extend([(a,c,depth+1),(c,b,depth+1)])
    return dict(passed=not failed,datum_mm=datum,intervals=sorted(intervals,key=lambda x:x['lo_vertex_mm']),failed_intervals=failed,
                scope='Continuous straight rays from on-axis vertices; finite active rectangles. No helix or transverse vertex certificate.')


def body_screen(modules,cfg):
    shapes=[body_polygon(m,cfg) for m in modules];pairs=[];min_z_gap=math.inf
    for i,a in enumerate(shapes):
        for j in range(i):
            area=a.intersection(shapes[j]).area
            if area<=cfg['area_tolerance_mm2']:continue
            gap=abs(modules[i]['center_mm'][2]-modules[j]['center_mm'][2])-cfg['body_thickness_mm']
            min_z_gap=min(min_z_gap,gap)
            if gap<cfg['required_gap_mm']-1e-8:pairs.append([i,j,gap])
    return dict(overlaps_or_insufficient_gap=pairs,minimum_z_gap_mm=min_z_gap,
                minimum_beam_radius_mm=min(p.distance(Point(0,0)) for p in shapes),
                maximum_radius_mm=max(math.hypot(x,y) for p in shapes for x,y in p.exterior.coords),
                levels=max(m['level'] for m in modules)+1,
                occupied_local_z_mm=[min(m['local_z_mm'] for m in modules)-cfg['body_thickness_mm']/2,
                                     max(m['local_z_mm'] for m in modules)+cfg['body_thickness_mm']/2])


def service_estimate(modules,cfg,outer_radius):
    inp=json.loads((ROOT/cfg['services_input']).read_text());barrel=json.loads((ROOT/cfg['barrel_services']).read_text())
    # Separate spatial row/ring groups; never replace quad chains by chip scaling.
    groups={}
    for m in modules:groups.setdefault((m['kind'],m['row']),[]).append(m)
    nchips=len(modules);p=inp['pixel'];chains=sum(math.ceil(len(v)/min(p['max_chain_chips'],p['max_chain_modules'])) for v in groups.values())
    circuits=sum(math.ceil(len(v)*p['power_per_chip_W']/p['cooling_power_per_circuit_W']) for v in groups.values())
    pipes=circuits*2*math.pi*(p['feed_outer_diameter_mm']/2)**2
    tube_length=sum(max(cfg['active_mm']) if len(v)==1 else
                    (2*math.pi*cfg['inner_ring_radius_mm'] if v[0]['kind']=='inner-polar' else
                     max(m['center_mm'][1] for m in v)-min(m['center_mm'][1] for m in v)+cfg['active_mm'][1]) for v in groups.values())
    scenarios=[];trunk_inner=math.ceil(outer_radius+cfg['collector_radial_gap_mm'])
    trunk_outer=cfg['carrier_shell_inner_mm'];section=math.pi*max(0,trunk_outer**2-trunk_inner**2)
    for name,s in inp['scenarios'].items():
        links=nchips*(s['pixel_uplinks_per_module']+s['pixel_uplinks_per_chip']+s['pixel_commands_per_module'])
        cable=chains*p['ancillary_chain_area_mm2']+links*p['differential_link_area_mm2'];bare=cable+pipes
        sides=[]
        for side in ['positive','negative']:
            braw=sum(sum(x['scenarios'][name]['terminal_cable_footprint_mm2'].values())+x['scenarios'][name]['terminal_pipe_footprint_mm2'] for x in barrel['sectors'] if x['side']==side)
            demand=(braw+8*bare)*s['demand_multiplier'];cap=section*s['available_phi_fraction']*s['packing_fraction']
            sides.append(dict(side=side,after_disc_8_demand_mm2=demand,capacity_mm2=cap,utilization=demand/cap if cap else None,status='PASS' if demand<=cap else 'FAIL'))
        scenarios.append(dict(scenario=name,uplink_command_links=links,cables_mm2=cable,feed_return_pipe_mm2=pipes,bare_disc_total_mm2=bare,end_trunks=sides))
    return dict(modules_per_disc=nchips,chips_per_disc=nchips,nominal_W=nchips*p['power_per_chip_W'],power_chains=chains,
                local_circuits=circuits,absolute_heat_only_circuit_lower_bound=math.ceil(nchips*p['power_per_chip_W']/p['cooling_power_per_circuit_W']),
                local_tube_OD_mm=cfg['local_tube_OD_mm'],row_ring_tube_length_without_feeds_mm=tube_length,
                local_tube_volume_envelope_mm3=tube_length*math.pi*(cfg['local_tube_OD_mm']/2)**2,
                transport_leg_OD_mm=p['feed_outer_diameter_mm'],trunk_inner_mm=trunk_inner,trunk_outer_mm=trunk_outer,scenarios=scenarios,
                limitations=['Separate cooling circuit per spatial row/ring, subdivided above300W; no hydraulic qualification.',
                             'Row/ring bus lengths omit feed routing, bends, connectors and complete material inventory.',
                             'Shared barrel inventory and last-disc bypass retained; aggregate packing is not routed CAD.',
                             'Existing r188.5 plate and r192 trunk must be redesigned; carrier rails/mounts and thermal feet have not been validated.'])


def baseline(cfg,source):
    bodies=[b for b in source['bodies'] if b['layer_id']=='A-pixel-P1']
    polys=[rectangle(b['center_mm'],b['u'],b['v'],20.6,19.8) for b in bodies]
    patches=[m for m in source['modules'] if m['layer_id']=='A-pixel-P1']
    active=[rectangle(m['center_mm'],m['u'],m['v'],m['half_u_mm'],m['half_v_mm']) for m in patches]
    return dict(modules=len(bodies),chips=len(patches),sensor=metrics(polys,cfg),active=metrics(active,cfg))


def run(cfg,out):
    out.mkdir(parents=True,exist_ok=True)
    source=json.loads(gzip.decompress((ROOT/cfg['baseline']).read_bytes()))
    if digest(ROOT/cfg['baseline'])!=cfg['baseline_sha256']:raise ValueError('Stale baseline pin')
    rows=[];selected=None
    for reduction in cfg['pitch_reductions_mm']:
        raw=candidates(cfg,reduction);placed=stagger(raw,cfg,cfg['disc_datum_mm'])
        sensor=metrics(project(placed,cfg,cfg['disc_datum_mm'],guard=cfg['sensor_guard_mm']),cfg)
        active=metrics(project(placed,cfg,cfg['disc_datum_mm']),cfg);body=body_screen(placed,cfg)
        vertices=[dict(vertex_z_mm=v,active=metrics(project(placed,cfg,cfg['disc_datum_mm'],vertex=v),cfg)) for v in cfg['vertices_z_mm']]
        passing=(sensor['overlap_over_union_percent']<=cfg['overlap_limit_percent'] and
                 sensor['annular_overlap_over_union_percent']<=cfg['overlap_limit_percent'] and
                 all(v['active']['uncovered_annulus_superset_mm2']<=cfg['area_tolerance_mm2'] for v in vertices) and
                 not body['overlaps_or_insufficient_gap'])
        rows.append(dict(pitch_reduction_mm=reduction,modules=len(raw),sensor=sensor,active=active,body=body,vertices=vertices,selection_pass=passing))
        if passing and (selected is None or len(placed)<len(selected[0])):selected=(placed,rows[-1])
    polar_modules=[]
    au,av=cfg['active_mm']
    for r,n in polar(cfg):
        for k in range(n):
            phi=2*math.pi*k/n
            polar_modules.append(rectangle([r*math.cos(phi),r*math.sin(phi),0],[-math.sin(phi),math.cos(phi),0],[math.cos(phi),math.sin(phi),0],au/2+cfg['sensor_guard_mm'],av/2+cfg['sensor_guard_mm']))
    report=dict(polar_control=dict(chips=len(polar_modules),sensor=metrics(polar_modules,cfg)),status='DRAFT / isolated PROTOTYPE',baseline=baseline(cfg,source),scan=rows,
                selected=None,provenance=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),
                generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=platform.python_version(),numpy=np.__version__,shapely=shapely.__version__,
                hashes={str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__),ROOT/'tools/pixel_disc_optimization/inputs.json',ROOT/cfg['services_input'],ROOT/cfg['barrel_services'],ROOT/cfg['baseline']]}))
    if selected:
        placed,row=selected
        report['selected']=row
        raw=candidates(cfg,row['pitch_reduction_mm'])
        discs=[l for l in source['layers'] if l['subsystem']=='pixel' and l['kind']=='disc' and l['id'].rsplit('-',1)[-1].startswith('P')]
        datums=[]
        for l in discs:
            b=next(b for b in source['bodies'] if b['layer_id']==l['id'])
            datums.append(b['center_mm'][2]-b['normal_offset_mm']+(3.5 if l['id'].endswith('P1') else 0))
        report['coverage_certificates']=[coverage_certificate(stagger(raw,cfg,z),cfg,z) for z in datums]
        report['per_disc_screens']=[dict(datum_mm=z,body=body_screen(stagger(raw,cfg,z),cfg),sensor=metrics(project(stagger(raw,cfg,z),cfg,z,guard=cfg['sensor_guard_mm']),cfg)) for z in datums]
        report['all_18_overlap_body_pass']=all(d['sensor']['overlap_over_union_percent']<=cfg['overlap_limit_percent'] and d['sensor']['annular_overlap_over_union_percent']<=cfg['overlap_limit_percent'] and not d['body']['overlaps_or_insufficient_gap'] for d in report['per_disc_screens'])
        report['all_18_straight_coverage_pass']=all(c['passed'] for c in report['coverage_certificates'])
        report['guard_control_0p5mm']=metrics(project(placed,cfg,cfg['disc_datum_mm'],guard=.5),cfg)
        report['services']=service_estimate(placed,cfg,max(d['body']['maximum_radius_mm'] for d in report['per_disc_screens']))
        report['vertices']=row['vertices']
        (out/'layout.json').write_text(json.dumps(dict(status=report['status'],modules=placed),indent=2)+'\n')
    (out/'screening.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(pitch=r['pitch_reduction_mm'],n=r['modules'],overlap=r['sensor']['overlap_over_union_percent'],ann_overlap=r['sensor']['annular_overlap_over_union_percent'],gap=r['active']['uncovered_annulus_superset_mm2'],body=r['body'],passes=r['selection_pass']) for r in rows],indent=2))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'build/disc-optimization/final');args=parser.parse_args()
    cfg=json.loads((ROOT/'tools/pixel_disc_optimization/inputs.json').read_text());run(cfg,args.output)

if __name__=='__main__':main()
