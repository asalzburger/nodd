"""Geometry-only PROTOTYPE: finite coil sweeps and clipped chamber outlines.

Coordinates are metres. Chamber outlines carry an envelope thickness but no
chamber material, tubes, supports or sensitive implementation. Overlapping ECT
cold/warm sleeves are a UNION allocation; they are not independent cryostats.
"""
from __future__ import annotations

import json
from pathlib import Path
import math
import numpy as np


def load_design(path=None):
    return json.loads(Path(path or Path(__file__).with_name('design.json')).read_text())


def _points(points):
    p = np.asarray(points, dtype=float)
    if p.ndim == 1:
        p = p[None, :]
    if p.ndim != 2 or p.shape[1] != 3 or not np.all(np.isfinite(p)):
        raise ValueError('points must be finite Nx3 coordinates')
    return p


def widths(config, width='warm', override=None):
    v = override if override is not None else config[width]
    a, b = float(v['normal_m']) / 2, float(v['tangent_m']) / 2
    if a <= 0 or b <= 0:
        raise ValueError('positive finite sweep dimensions required')
    return a, b


def rounded_rectangle_distance(rz, group):
    """Exact unsigned distance to the rounded-rectangle centreline."""
    p = np.asarray(rz, dtype=float)
    rho = float(group['corner_radius_m'])
    half = np.array([group['half_r_m'], group['half_z_m']], dtype=float)
    if rho <= 0 or np.any(half <= rho):
        raise ValueError('corner radius must be below both half-extents')
    center = np.array([group['center_r_m'], group['center_z_m']])
    q = np.abs(p - center) - (half - rho)
    signed = np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(np.max(q, axis=-1), 0) - rho
    return np.abs(signed)


def group_mask(points, group, folds=12, normal_m=.5, tangent_m=.6,
               clearance=0., return_count=False):
    """Union/count of coil-following rectangular-section sweeps in one family.

    An exact planar centreline distance and a tangential slab define each
    sweep. Added clearance is conservative at cross-section corners.
    """
    p = _points(points)
    a, b = normal_m / 2 + clearance, tangent_m / 2 + clearance
    if min(a, b) < 0 or not np.isfinite([a, b]).all():
        raise ValueError('invalid sweep width or clearance')
    count = np.zeros(len(p), dtype=np.uint16)
    for k in range(int(folds)):
        angle = math.radians(group['phi_offset_deg'] + k * 360 / folds)
        c, s = math.cos(angle), math.sin(angle)
        v = -p[:, 0] * s + p[:, 1] * c
        candidate = np.abs(v) <= b + 1e-12
        if not np.any(candidate):
            continue
        u = p[candidate, 0] * c + p[candidate, 1] * s
        rz = np.column_stack((u, p[candidate, 2]))
        count[candidate] += rounded_rectangle_distance(rz, group) <= a + 1e-12
    return count if return_count else count > 0


def coil_mask(points, config, width='warm', clearance=0., width_override=None,
              return_groups=False):
    """Vectorized union mask; pack/cold/warm widths stay config-driven."""
    a, b = widths(config, width, width_override)
    masks = {name: group_mask(points, group, config['folds'], 2*a, 2*b, clearance)
             for name, group in config['coil_groups'].items()}
    return masks if return_groups else np.logical_or.reduce(list(masks.values()))


def chamber_depth_mask(points, config, kind, clearance=.05, width='warm',
                       depth_step_m=.025, cell_bound_m=0., width_override=None):
    """Conservatively test the chamber's actual normal extrusion.

    Barrel depth is radial; disk depth is axial. Sample the whole depth at
    <=depth_step_m intervals, inflating each sampled coil mask by half an
    interval. Since coil distance coordinates are 1-Lipschitz, any crossing
    between depth samples is covered. cell_bound_m independently encloses an
    outline surface cell. Disk depth never becomes a fictitious radial width.
    """
    p=_points(points); depth=float(config['stations']['outline_thickness_m'])
    if depth<0 or depth_step_m<=0 or cell_bound_m<0:
        raise ValueError('nonnegative depth/cell bound and positive depth step required')
    n=max(1,math.ceil(depth/depth_step_m)); offsets=np.linspace(-depth/2,depth/2,n+1)
    guard=(offsets[1]-offsets[0])/2
    if kind in ('B','barrel'):
        radius=np.linalg.norm(p[:,:2],axis=1)
        if np.any(radius<=depth/2):
            raise ValueError('barrel extrusion must have positive inner radius')
        normal=np.column_stack((p[:,0]/radius,p[:,1]/radius,np.zeros(len(p))))
    elif kind in ('D','disk'):
        normal=np.tile([0.,0.,1.],(len(p),1))
    else:
        raise ValueError('chamber kind must be barrel/B or disk/D')
    hit=np.zeros(len(p),bool)
    # The broad mask only selects work; it does not reject chamber points.
    candidate=coil_mask(p,config,width,clearance+depth/2+cell_bound_m+guard,width_override)
    for offset in offsets:
        active=candidate & ~hit
        if not np.any(active):
            break
        hit[active]=coil_mask(p[active]+offset*normal[active],config,width,
                             clearance+cell_bound_m+guard,width_override)
    return hit


def path_intersections(start, end, config, width='warm', clearance=0., step_m=.01,
                       width_override=None):
    """Sampled finite path intervals through sweeps, with bounded sample step.

    This is a geometry diagnostic, not a native solid/material navigator.
    Interval endpoints are uncertain by at most step_m along the segment.
    """
    start, end = np.asarray(start, float), np.asarray(end, float)
    length = float(np.linalg.norm(end-start))
    if step_m <= 0 or length == 0:
        raise ValueError('nonzero path and positive sample step required')
    n = max(1, math.ceil(length / step_m))
    t = np.linspace(0, 1, n+1)
    hit = coil_mask(start[None,:] + t[:,None]*(end-start), config, width,
                    clearance, width_override)
    indices = np.flatnonzero(np.diff(np.r_[False,hit,False].astype(np.int8)))
    return [(float(t[max(0,i-1)]), float(t[min(n,j)])) for i,j in indices.reshape(-1,2)]


def station_intersections(eta, phi_deg, config, mask_width='warm', clearance=.05,
                          check_path=True, path_step_m=.01):
    """Straight IP-ray surface hits, retaining excluded hits and mixed topology.

    phi is degrees; eta sign selects the endcap. Surface centres define the
    exact 3 m spans. Finite envelope seams and both toroid-family masks apply.
    """
    st = config['stations']; h = st['outline_thickness_m']/2
    phi=math.radians(phi_deg)
    sz = math.sinh(abs(float(eta))); side = -1 if eta < 0 else 1
    hits = []
    for i,(r,z) in enumerate(zip(st['barrel_radii_m'],st['disk_abs_z_m']),1):
        halfz = z-st['barrel_end_shortening_m']
        zr = r*sz
        if zr <= halfz:
            xyz = [r*math.cos(phi),r*math.sin(phi),side*zr]
            kind = 'B'
        else:
            rd = z/sz if sz else math.inf
            if not st['disk_inner_radius_m'] <= rd <= r+h:
                continue
            xyz = [rd*math.cos(phi),rd*math.sin(phi),side*z]
            kind = 'D'
        excluded = bool(chamber_depth_mask([xyz],config,kind,clearance,mask_width)[0])
        hits.append({'station':i,'surface':kind,'side':side if kind=='D' else 0,
                     'point_m':xyz,'excluded':excluded})
    intervals=[]
    if check_path and len(hits)>1:
        intervals=path_intersections(hits[0]['point_m'],hits[-1]['point_m'],
                                     config,mask_width,clearance,path_step_m)
    excluded=any(x['excluded'] for x in hits)
    return {'hits':hits,'hit_types':''.join(x['surface'] for x in hits),
            'points_m':[x['point_m'] for x in hits],'three_hits':len(hits)==3,
            'excluded_hits':excluded,'path_intervals':intervals,
            'valid':len(hits)==3 and not excluded and not intervals,
            'path_sample_step_m':path_step_m if check_path else None,
            'path_checked':check_path}


def loop_polyline(group, phi_deg=0., arc_steps=20):
    """Closed exact-corner polygon for display, with convergence under refinement."""
    hr,hz,rho = (group[k] for k in ('half_r_m','half_z_m','corner_radius_m'))
    center=np.array([group['center_r_m'],group['center_z_m']])
    parts=[]
    for sx,sz,start in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
        a=np.deg2rad(np.linspace(start,start+90,arc_steps+1))
        corner=np.array([sx*(hr-rho),sz*(hz-rho)])
        parts.extend(center+corner+rho*np.column_stack((np.cos(a),np.sin(a))))
    rz=np.vstack((parts,parts[0])); ph=math.radians(phi_deg)
    return np.column_stack((rz[:,0]*math.cos(ph),rz[:,0]*math.sin(ph),rz[:,1]))


def _boundary_segments(valid, points):
    """Boundary only of retained periodic-phi cells; never output internal grid."""
    nphi,nv=valid.shape; out=[]
    # Edges parallel to phi: cell above/below each v-grid boundary.
    for j in range(nv+1):
        below=valid[:,j-1] if j else np.zeros(nphi,bool)
        above=valid[:,j] if j<nv else np.zeros(nphi,bool)
        for i in np.flatnonzero(below != above):
            out.append([points[i,j],points[(i+1)%nphi,j]])
    # Edges parallel to v: periodic neighbouring phi cells.
    for i in range(nphi):
        for j in np.flatnonzero(valid[(i-1)%nphi] != valid[i]):
            out.append([points[i,j],points[i,j+1]])
    return np.asarray(out,float).reshape(-1,2,3)


def chamber_outline_polylines(config, phi_step_deg=1., longitudinal_step_m=.10,
                              radial_step_m=.10, clearance=.05):
    """Conservative staircase outlines of allowed chamber footprints.

    Each retained surface cell's whole normal extrusion is tested, with a
    half-depth-sample interval guard PLUS the surface-cell bounding radius.
    The distance functions are 1-Lipschitz, so an entire retained cell is clear
    of coil sweeps at the declared clearance. Disk depth is purely axial;
    barrel depth is radial, and never an isotropic chamber inflation.
    Only external/cutout boundary segments are emitted, not a chamber grid.
    Refining sampling reduces the conservative extra cutout. These footprints
    are outlines; no tubes, internal layers or engineering chamber model exist.
    """
    if min(phi_step_deg,longitudinal_step_m,radial_step_m) <= 0:
        raise ValueError('positive outline grid steps required')
    st=config['stations']; h=st['outline_thickness_m']/2
    nphi=math.ceil(360/phi_step_deg); dp=2*math.pi/nphi
    pe=np.arange(nphi)*dp; pc=pe+dp/2
    out=[]
    def finish(name,kind,index,side,points,centers,bound):
        valid=~chamber_depth_mask(centers.reshape(-1,3),config,kind,clearance,
                                  cell_bound_m=bound).reshape(centers.shape[:2])
        segments=_boundary_segments(valid,points)
        out.append({'name':name,'kind':kind,'station':index,'side':side,
                    'outline_thickness_m':2*h,'clearance_to_warm_m':clearance,
                    'conservative_sampling_extra_m':bound,
                    'depth_sample_max_interval_m':.025,
                    'depth_sampling_half_interval_guard_m':h/max(1,math.ceil(2*h/.025)),
                    'retained_surface_cell_fraction':float(valid.mean()),
                    'segments_m':segments})
    for i,(r,z) in enumerate(zip(st['barrel_radii_m'],st['disk_abs_z_m']),1):
        hz=z-st['barrel_end_shortening_m']
        ze=np.linspace(-hz,hz,math.ceil(2*hz/longitudinal_step_m)+1)
        zc=(ze[:-1]+ze[1:])/2
        points=np.stack(np.broadcast_arrays(r*np.cos(pe[:,None]),r*np.sin(pe[:,None]),ze[None,:]),axis=-1)
        centers=np.stack(np.broadcast_arrays(r*np.cos(pc[:,None]),r*np.sin(pc[:,None]),zc[None,:]),axis=-1)
        # Outer radial extrusion has the largest azimuthal cell extent.
        bound=math.hypot(2*(r+h)*math.sin(dp/4),(ze[1]-ze[0])/2)
        finish(f'B{i}','barrel',i,0,points,centers,bound)
        re=np.linspace(st['disk_inner_radius_m'],r+h,math.ceil((r+h-st['disk_inner_radius_m'])/radial_step_m)+1)
        rc=(re[:-1]+re[1:])/2
        bound=math.hypot((re[1]-re[0])/2,2*(r+h)*math.sin(dp/4))
        for side in (-1,1):
            points=np.stack(np.broadcast_arrays(re[None,:]*np.cos(pe[:,None]),re[None,:]*np.sin(pe[:,None]),np.full((nphi,len(re)),side*z)),axis=-1)
            centers=np.stack(np.broadcast_arrays(rc[None,:]*np.cos(pc[:,None]),rc[None,:]*np.sin(pc[:,None]),np.full((nphi,len(rc)),side*z)),axis=-1)
            finish(f'D{i}{"+" if side>0 else "-"}','disk',i,side,points,centers,bound)
    return out


def export_outlines(path, config, **kwargs):
    outlines=chamber_outline_polylines(config,**kwargs)
    result={'status':'PROTOTYPE / chamber outlines only; shared ECT vessel unresolved',
            'coordinate_unit':'m','source_design':config.get('base_revision'),
            'station_outline_thickness_m':config['stations']['outline_thickness_m'],
            'coil_exclusion':'union of both barrel and endcap warm coil sweeps',
            'sampling':'conservative retained cells; no chamber internal grid',
            'outlines':[{k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in x.items()} for x in outlines]}
    Path(path).write_text(json.dumps(result,separators=(',',':'))+'\n')
    return result


def outline_envelope_faces(outline):
    """Display the two full-depth external boundary faces; no internal grid."""
    seg=np.asarray(outline['segments_m']);h=outline['outline_thickness_m']/2
    n=np.zeros_like(seg)
    if outline['kind']=='barrel':
        n[:,:,:2]=seg[:,:,:2]/np.linalg.norm(seg[:,:,:2],axis=2)[:,:,None]
    else:n[:,:,2]=1.
    return np.concatenate((seg-h*n,seg+h*n),axis=0)


def export_vtp(path, config, outlines=None, arc_steps=24, **outline_kwargs):
    """ParaView-readable 3D coil centrelines and clipped chamber boundaries.

    Lines only: no tube/chamber internals or invented filled cryostat volume.
    Cell category 0/1/2 is BT/ECT+/ECT-, 3 is barrel chambers, 4/5 D-/D+.
    """
    from xml.etree.ElementTree import Element, SubElement, ElementTree
    outlines=outlines if outlines is not None else chamber_outline_polylines(config,**outline_kwargs)
    lines=[]; category=[]; object_id=[]; names=[]
    for gi,(name,group) in enumerate(config['coil_groups'].items()):
        for k in range(config['folds']):
            oid=len(names); names.append(f'{name}_coil_{k:02d}')
            lines.append(loop_polyline(group,group['phi_offset_deg']+k*360/config['folds'],arc_steps))
            category.append(gi);object_id.append(oid)
    for outline in outlines:
        oid=len(names);names.append(outline['name'])
        cat=3 if outline['kind']=='barrel' else (5 if outline['side']>0 else 4)
        for segment in outline_envelope_faces(outline):
            lines.append(segment);category.append(cat);object_id.append(oid)
    counts=np.asarray([len(x) for x in lines],dtype=int)
    points=np.concatenate(lines); offsets=np.cumsum(counts); connectivity=np.arange(len(points))
    root=Element('VTKFile',type='PolyData',version='0.1',byte_order='LittleEndian')
    data=SubElement(root,'PolyData');piece=SubElement(data,'Piece',NumberOfPoints=str(len(points)),NumberOfLines=str(len(lines)),NumberOfVerts='0',NumberOfStrips='0',NumberOfPolys='0')
    pp=SubElement(piece,'Points')
    SubElement(pp,'DataArray',type='Float64',NumberOfComponents='3',format='ascii').text=' '.join(f'{x:.10g}' for x in points.ravel())
    ll=SubElement(piece,'Lines')
    SubElement(ll,'DataArray',type='Int64',Name='connectivity',format='ascii').text=' '.join(map(str,connectivity))
    SubElement(ll,'DataArray',type='Int64',Name='offsets',format='ascii').text=' '.join(map(str,offsets))
    cd=SubElement(piece,'CellData',Scalars='category')
    SubElement(cd,'DataArray',type='Int32',Name='category',format='ascii').text=' '.join(map(str,category))
    SubElement(cd,'DataArray',type='Int32',Name='object_id',format='ascii').text=' '.join(map(str,object_id))
    ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
    return {'points':len(points),'lines':len(lines),'objects':names,
            'categories':{'0':'barrel coils','1':'ECT+ coils','2':'ECT- coils','3':'barrel chamber boundaries','4':'disk- boundaries','5':'disk+ boundaries'},
            'status':'PROTOTYPE outlines only; shared endcap vessel unresolved'}


def _sample_single_sweep(group, a, b, samples, rng):
    """Uniform centreline/normal/tangent samples with exact curvature weights."""
    hr,hz,rho=(float(group[k]) for k in ('half_r_m','half_z_m','corner_radius_m'))
    if a >= rho:
        raise ValueError('normal halfwidth must be below corner radius for tube volume')
    # Counterclockwise path, straight then quadrant. Outward normal is right.
    lr,lz=2*(hr-rho),2*(hz-rho)
    pieces=[('line',lz),('arc',rho*math.pi/2),('line',lr),('arc',rho*math.pi/2),
            ('line',lz),('arc',rho*math.pi/2),('line',lr),('arc',rho*math.pi/2)]
    perimeter=sum(x[1] for x in pieces); s=rng.uniform(0,perimeter,samples)
    u=rng.uniform(-a,a,samples); v=rng.uniform(-b,b,samples)
    rz=np.empty((samples,2)); normal=np.empty_like(rz); jac=np.ones(samples)
    # Start at upper-right straight tangent, progress CCW around rounded rect.
    cursor=0.
    for j,(kind,length) in enumerate(pieces):
        take=(s>=cursor)&(s<cursor+length); q=s[take]-cursor
        if j==0: rz[take]=np.column_stack((np.full(len(q),hr),-hz+rho+q)); normal[take]=[1,0]
        elif j==2: rz[take]=np.column_stack((hr-rho-q,np.full(len(q),hz))); normal[take]=[0,1]
        elif j==4: rz[take]=np.column_stack((np.full(len(q),-hr),hz-rho-q)); normal[take]=[-1,0]
        elif j==6: rz[take]=np.column_stack((-hr+rho+q,np.full(len(q),-hz))); normal[take]=[0,-1]
        else:
            corner={1:[hr-rho,hz-rho],3:[-hr+rho,hz-rho],5:[-hr+rho,-hz+rho],7:[hr-rho,-hz+rho]}[j]
            theta=(j//2)*math.pi/2+q/rho
            normal[take]=np.column_stack((np.cos(theta),np.sin(theta)))
            rz[take]=np.asarray(corner)+rho*normal[take]
            jac[take]=1+u[take]/rho
        cursor+=length
    rz+=u[:,None]*normal+np.array([group['center_r_m'],group['center_z_m']])
    angle=math.radians(group['phi_offset_deg']); c,ss=math.cos(angle),math.sin(angle)
    points=np.column_stack((rz[:,0]*c-v*ss,rz[:,0]*ss+v*c,rz[:,1]))
    return points,jac,perimeter*4*a*b


def sweep_union_volumes(config, width='cold', samples=262144, seed=12086,
                        width_override=None):
    """Reproducible importance-sampled UNION volumes, with statistical errors.

    C12 symmetry samples one complete coil per family. Its Jacobian-weighted
    occupancy 1/k gives union volume without double-counting shared sleeves.
    Estimates include own-family overlaps. Inter-family overlap is reported
    separately as a blocker; do not add group volumes if it is detected.
    """
    a,b=widths(config,width,width_override); rng=np.random.default_rng(seed); groups={}
    for name,group in config['coil_groups'].items():
        p,jac,one=_sample_single_sweep(group,a,b,samples,rng)
        count=group_mask(p,group,config['folds'],2*a,2*b,return_count=True)
        if np.any(count==0): raise AssertionError('sample escaped own sweep')
        # Calibrate analytic single-coil volume exactly, reducing curvature noise.
        # Y=(1−1/k)J is only nonzero in actual shared sleeve regions.
        correction=jac*(1-1/count)
        total=one*config['folds']; overlap=total*float(correction.mean())
        error=total*float(correction.std(ddof=1))/math.sqrt(samples)
        others=np.zeros(samples,bool)
        for other,og in config['coil_groups'].items():
            if other!=name: others|=group_mask(p,og,config['folds'],2*a,2*b)
        groups[name]={'summed_sleeve_volume_m3':total,'union_volume_m3':total-overlap,
                      'overlap_correction_m3':overlap,'one_sigma_statistical_error_m3':error,
                      'sample_fraction_in_other_groups':float(others.mean())}
    return {'method':'analytic tube volume minus Jacobian-weighted multiplicity correction',
            'samples_per_group':samples,'seed':seed,'width':width,'groups':groups,
            'sum_group_union_volume_m3':sum(x['union_volume_m3'] for x in groups.values()),
            'cross_group_overlap_detected':any(x['sample_fraction_in_other_groups']>0 for x in groups.values()),
            'interpretation':'shared geometric allocation only, not material mass or engineered cryostat; finite MC error is reported; undetected cross-group intersections are not a native solid overlap check'}


def analytic_sweep_union_volumes(config, width='cold', order=128, width_override=None):
    """Unique tube volume with analytic-y/GL-x adjacent-inner-leg correction.

    This special reduction is valid only when sleeves overlap exclusively at
    adjacent inner legs/corners; guards reject broad sleeves or other-family
    intersections. A general sweep must instead use a reviewed union solver.
    The volume is a proposed common cold allocation, not engineered material.
    """
    a,b=widths(config,width,width_override)
    delta=math.pi/config['folds']; c,s=math.cos(delta),math.sin(delta)
    groups={}; nodes,weights=np.polynomial.legendre.leggauss(order)
    for name,gp in config['coil_groups'].items():
        hr,hz,rho=(float(gp[k]) for k in ('half_r_m','half_z_m','corner_radius_m'))
        r=float(gp['center_r_m'])-hr
        if a>=rho or a>=r:
            raise ValueError('tube or positive-radius volume condition violated')
        perimeter=4*(hr+hz-2*rho)+2*math.pi*rho
        summed=config['folds']*perimeter*4*a*b; correction=0.
        lo=(r-a)/c; hi=b/s
        if hi>lo:
            if hi>r+a or math.atan2(b,r-a)>=2*delta:
                raise ValueError('adjacent-inner-leg-only union reduction unavailable')
            mid=b*s+(r-a)*c; A=rho+a
            def primitive(t):
                t=np.clip(t,-A,A)
                return .5*(t*np.sqrt(np.maximum(0,A*A-t*t))+A*A*np.arcsin(t/A))
            pair=0.
            for left,right in [(lo,mid),(mid,hi)]:
                x=(left+right)/2+(right-left)/2*nodes
                ymax=np.minimum((x*c-(r-a))/s,(b-x*s)/c)
                D=r+rho-x*c
                # Symmetric y and z; the inner corner's maximum |z| is
                # hz-rho + sqrt((rho+a)^2-(r+rho-u_min)^2).
                value=4*((hz-rho)*ymax+(primitive(D+s*ymax)-primitive(D))/s)
                pair+=(right-left)/2*float(np.dot(weights,value))
            correction=config['folds']*pair
        groups[name]={'summed_sleeve_volume_m3':summed,'overlap_correction_m3':correction,
                      'union_volume_m3':summed-correction}
    # Sufficient plane/axial separation proof for different assemblies.
    separation=[]; items=list(config['coil_groups'].items())
    for i,(name,gp) in enumerate(items):
        for other,og in items[i+1:]:
            zgap=abs(gp['center_z_m']-og['center_z_m'])-gp['half_z_m']-og['half_z_m']-2*a
            angle=abs(math.radians(gp['phi_offset_deg']-og['phi_offset_deg']))%(2*delta)
            angle=min(angle,2*delta-angle)
            rmin=max(gp['center_r_m']-gp['half_r_m']-a,og['center_r_m']-og['half_r_m']-a)
            plane_gap=rmin*math.sin(angle)-b*math.cos(angle)-b
            if max(zgap,plane_gap)<=0:
                raise ValueError('different-family separation not proven for analytic sum')
            separation.append({'groups':[name,other],'separation_lower_bound_m':max(zgap,plane_gap)})
    return {'method':'exact tube volume minus adjacent-pair inner-corner overlap; analytic y and Gauss-Legendre x',
            'quadrature_order':order,'width':width,'groups':groups,
            'sum_group_union_volume_m3':sum(x['union_volume_m3'] for x in groups.values()),
            'cross_group_separation_proofs':separation,
            'interpretation':'unique shared geometric allocation only; not conductor or support mass, pressure boundary, or construction acceptance'}
