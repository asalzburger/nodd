"""Whole rectangular/trapezoidal chamber packing in the fixed DES039 magnet."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from . import geometry as g

ROOT=Path(__file__).resolve().parents[2]


def inputs(path=None):
    c=json.loads(Path(path or ROOT/'tools/muon_layout/design.json').read_text())
    for stem in ('magnetic_results','magnetic_map'):
        if hashlib.sha256((ROOT/c[stem]).read_bytes()).hexdigest()!=c[stem+'_sha256']:
            raise ValueError('pinned magnetic input changed: '+stem)
    return c,json.loads((ROOT/c['magnetic_results']).read_text())['configuration']


def tiles(lo,hi,maximum,gap):
    n=math.ceil((hi-lo+gap)/(maximum+gap));size=(hi-lo-(n-1)*gap)/n
    return [(lo+i*(size+gap),lo+i*(size+gap)+size) for i in range(n)]


def _barrel(identifier,station,phi,R,zlo,zhi,xlo,xhi,c):
    a=math.radians(phi);er=np.array([math.cos(a),math.sin(a),0.]);ep=np.array([-math.sin(a),math.cos(a),0.])
    return g.prism(identifier,'barrel',R*er,np.column_stack((ep,[0,0,1],er)),
        [[xlo,zlo],[xhi,zlo],[xhi,zhi],[xlo,zhi]],c['depth_m'],station=station,
        compartment=dict(phi_deg=phi,z_m=[zlo,zhi],tangent_m=[xlo,xhi]),face='rectangle')


def _disk(identifier,station,side,z,rlo,rhi,plo,phi,c):
    angle=(plo+phi)/2;alpha=math.radians((phi-plo)/2);a=math.radians(angle)
    er=np.array([math.cos(a),math.sin(a),0.]);ep=np.array([-math.sin(a),math.cos(a),0.])
    # local coordinates (radial,tangential), er cross ep = +z on both ends.
    u0,u1=rlo,rhi*math.cos(alpha);w0=u0*math.tan(alpha)-c['gap_m']/2;w1=u1*math.tan(alpha)-c['gap_m']/2
    if u1<=u0 or w0<=0:return None
    return g.prism(identifier,'endcap',[0,0,side*z],np.column_stack((er,ep,[0,0,1])),
        [[u0,-w0],[u1,-w1],[u1,w1],[u0,w0]],c['depth_m'],station=station,side=side,
        compartment=dict(phi_deg=[plo,phi],radial_m=[rlo,rhi]),face='trapezoid')


def candidates(c):
    c=c['chambers'];N=c['barrel_facets'];half=math.pi/N
    for j,(R,zmax,phase) in enumerate(zip(c['barrel_apothems_m'],c['barrel_half_z_m'],c['barrel_phase_deg']),1):
        width=2*(R-c['depth_m']/2)*math.tan(half)-c['gap_m']
        for k in range(N):
            for iz,(lo,hi) in enumerate(tiles(-zmax,zmax,c['max_barrel_length_m'],c['gap_m'])):
                yield _barrel(f'B{j}/F{k:02d}/Z{iz:02d}',j,phase+k*360/N,R,lo,hi,-width/2,width/2,c)
    N=c['endcap_sectors']
    for j,(z,rmax) in enumerate(zip(c['disk_abs_z_m'],c['disk_outer_r_m']),1):
        for side,label in [(-1,'M'),(1,'P')]:
            for k in range(N):
                centre=c['endcap_phase_deg']+k*360/N
                for ir,(lo,hi) in enumerate(tiles(c['disk_inner_r_m'],rmax,c['max_endcap_radial_span_m'],c['gap_m'])):
                    body=_disk(f'E{label}{j}/S{k:02d}/R{ir:02d}',j,side,z,lo,hi,centre-180/N,centre+180/N,c)
                    if body is not None:yield body


def _children(body,c,depth):
    p=body['compartment'];gap=c['gap_m'];ident=body['id'];j=body['station']
    if body['kind']=='barrel':
        z0,z1=p['z_m'];x0,x1=p['tangent_m'];R=np.linalg.norm(np.asarray(body['origin_m'])[:2])
        # Split the longer dimension; avoid undersized longitudinal fragments.
        z_possible=(z1-z0-gap)/2>=c['min_span_m']
        axes=['z','x'] if z_possible and z1-z0>=x1-x0 else ['x','z']
        for axis in axes:
            if axis=='z' and z_possible:
                mid=(z0+z1)/2
                children=[_barrel(ident+f'/z{i}',j,p['phi_deg'],R,a,b,x0,x1,c)
                          for i,(a,b) in enumerate([(z0,mid-gap/2),(mid+gap/2,z1)])]
            elif axis=='x':
                mid=(x0+x1)/2
                children=[_barrel(ident+f'/x{i}',j,p['phi_deg'],R,z0,z1,a,b,c)
                          for i,(a,b) in enumerate([(x0,mid-gap/2),(mid+gap/2,x1)])]
            else:continue
            if all(g.polygon_area(x['vertices_m'])>=c['min_area_m2'] for x in children):return children
    else:
        r0,r1=p['radial_m'];p0,p1=p['phi_deg'];rad_possible=(r1-r0-gap)/2>=c['min_span_m']
        tangential=(r0+r1)*math.sin(math.radians((p1-p0)/2))
        axes=['r','p'] if rad_possible and r1-r0>=tangential else ['p','r']
        for axis in axes:
            if axis=='r' and rad_possible:
                mid=(r0+r1)/2;regions=[(r0,mid-gap/2,p0,p1),(mid+gap/2,r1,p0,p1)]
            elif axis=='p':
                mid=(p0+p1)/2;regions=[(r0,r1,p0,mid),(r0,r1,mid,p1)]
            else:continue
            children=[_disk(ident+f'/{axis}{i}',j,body['side'],abs(body['origin_m'][2]),*reg,c)
                      for i,reg in enumerate(regions)]
            if all(x is not None and g.polygon_area(x['vertices_m'])>=c['min_area_m2'] for x in children):return children
    return []


def build_layout(config,magnetic_config,supports):
    c=config['chambers'];members=supports['members'];bounds=np.array([g.aabb(x) for x in members])
    cache={};certificate_cells=0
    def coil_check(body):
        nonlocal certificate_cells
        key=body['id']
        if key not in cache:
            cache[key]=g.certify_coil_clear(body,magnetic_config,c['coil_clearance_m'],c['coil_certificate_resolution_m'])
            certificate_cells+=cache[key]['cells']
        return cache[key]
    def support_check(body):
        low,high=g.aabb(body);pad=c['support_clearance_m']*2 # enclosing AABB for expanded rotated member
        nearby=np.flatnonzero(((bounds[:,1]+pad>=low)&(bounds[:,0]-pad<=high)).all(axis=1))
        return [members[i]['id'] for i in nearby if g.intersects(body,members[i],c['support_clearance_m'])]
    def pack(use_support):
        accepted=[];rejected=[];splits=0
        def visit(body,depth):
            nonlocal splits
            certificate=coil_check(body);clashes=support_check(body) if certificate['clear'] and use_support else []
            if certificate['clear'] and not clashes:
                body=dict(body,coil_certificate=certificate);accepted.append(body);return
            children=_children(body,c,depth) if depth<c['max_subdivision_depth'] else []
            if children:
                splits+=1
                for child in children:visit(child,depth+1)
            else:rejected.append(dict(id=body['id'],reason=certificate['reason'] if not certificate['clear'] else 'support clearance',support_ids=clashes))
        initial=list(candidates(config))
        for body in initial:visit(body,0)
        return accepted,dict(initial_compartments=len(initial),subdivisions=splits,accepted=len(accepted),rejected_leaves=rejected)
    reference,ref_stats=pack(False);panels,stats=pack(True)
    overlaps=[];bb=np.array([g.aabb(p) for p in panels])
    for i,body in enumerate(panels):
        nearby=np.flatnonzero(((bb[i,1]>=bb[i+1:,0])&(bb[i,0]<=bb[i+1:,1])).all(axis=1))+i+1
        for k in nearby:
            if g.intersects(body,panels[k]):overlaps.append([body['id'],panels[k]['id']])
    if overlaps:raise ValueError(f'whole chamber volumes overlap: {overlaps[:5]}')
    return dict(panels=panels,without_support_panels=reference,packing=stats,without_support_packing=ref_stats,
                validation=dict(panel_panel_conflicts=overlaps,accepted_coil_certificates=len(panels),
                coil_certificate_cells=certificate_cells,panel_support_clearance_m=c['support_clearance_m'],
                coil_clearance_m=c['coil_clearance_m'],unresolved_cells_accepted=0))
