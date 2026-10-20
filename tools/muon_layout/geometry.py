"""Convex outline reservations for DES040; metres, Cartesian right handed axes.

Chambers are whole prisms, not Boolean-cut or internally detailed detectors.
Coil separation is certified over their volume using distance bounds; a finite
corner sample is deliberately insufficient. No simulation framework is used.
"""
from __future__ import annotations
import math
import numpy as np
from tools.toroid_prototype.geometry import coil_mask


def polygon_area(vertices):
    p=np.asarray(vertices,float)
    return float(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))/2)


def polygon_planes(vertices):
    p=np.asarray(vertices,float);edge=np.roll(p,-1,axis=0)-p
    outward=np.column_stack((edge[:,1],-edge[:,0]))
    outward/=np.linalg.norm(outward,axis=1)[:,None]
    return outward,np.einsum('ij,ij->i',outward,p)


def prism(identifier,kind,origin,basis,vertices,depth,**metadata):
    p=np.asarray(vertices,float);q=np.asarray(basis,float)
    if p.shape!=(4,2) or polygon_area(p)<=0 or depth<=0:
        raise ValueError('positive-depth counterclockwise quadrilateral required')
    if not np.allclose(q.T@q,np.eye(3),atol=1e-12) or np.linalg.det(q)<.999999:
        raise ValueError('basis columns must be a right-handed orthonormal triad')
    n,b=polygon_planes(p)
    if np.max(p@n.T-b)>1e-10:
        raise ValueError('footprint must be convex')
    return dict(id=identifier,kind=kind,origin_m=np.asarray(origin,float).tolist(),
                basis=q.tolist(),vertices_m=p.tolist(),depth_m=float(depth),**metadata)


def beam(identifier,start,end,width,height,**metadata):
    a,b=np.asarray(start,float),np.asarray(end,float);delta=b-a
    length=float(np.linalg.norm(delta));normal=delta/length
    helper=np.eye(3)[int(np.argmin(abs(normal)))]
    x=np.cross(helper,normal);x/=np.linalg.norm(x);y=np.cross(normal,x)
    return prism(identifier,metadata.pop('kind','frame'),(a+b)/2,
                 np.column_stack((x,y,normal)),
                 [[-width/2,-height/2],[width/2,-height/2],
                  [width/2,height/2],[-width/2,height/2]],length,
                 endpoints_m=[a.tolist(),b.tolist()],section_m=[width,height],**metadata)


def vertices3(body):
    p=np.asarray(body['vertices_m']);h=body['depth_m']/2
    local=np.vstack([np.column_stack((p,np.full(4,z))) for z in (-h,h)])
    return local@np.asarray(body['basis']).T+body['origin_m']


def aabb(body):
    v=vertices3(body);return v.min(axis=0),v.max(axis=0)


def volume(body):
    return polygon_area(body['vertices_m'])*body['depth_m']


def planes3(body):
    q=np.asarray(body['basis']);o=np.asarray(body['origin_m']);n,b=polygon_planes(body['vertices_m'])
    world=n@q[:,:2].T
    normals=np.vstack((world,q[:,2],-q[:,2]))
    bounds=np.r_[b+world@o,q[:,2]@o+body['depth_m']/2,-q[:,2]@o+body['depth_m']/2]
    return normals,bounds


def contains(body,points,border=0):
    local=(np.asarray(points)-body['origin_m'])@np.asarray(body['basis'])
    n,b=polygon_planes(body['vertices_m'])
    return ((local[:,:2]@n.T<=b-border+1e-12).all(axis=1)&
            (abs(local[:,2])<=body['depth_m']/2+1e-12))


def midplane_hits(body,directions,border=0,full_depth=False):
    """Plane-footprint distances, optionally requiring both depth faces.

    Neither test implies measured hits or reconstructed efficiency. The second
    is a conservative whole-stack geometric proxy: side-entry paths fail it.
    """
    d=np.asarray(directions);q=np.asarray(body['basis']);o=np.asarray(body['origin_m'])
    denom=d@q[:,2]
    s=np.divide(o@q[:,2],denom,out=np.full(len(d),np.inf),where=abs(denom)>1e-12)
    possible=(s>0)&np.isfinite(s)
    result=np.full(len(d),np.inf)
    if possible.any():
        local=(s[possible,None]*d[possible]-o)@q
        n,b=polygon_planes(body['vertices_m'])
        good=(local[:,:2]@n.T<=b-border+1e-12).all(axis=1)
        if full_depth:
            for sign in (-1,1):
                face_s=s[possible]+sign*body['depth_m']/2/denom[possible]
                face=(face_s[:,None]*d[possible]-o)@q
                good&=(face[:,:2]@n.T<=b-border+1e-12).all(axis=1)&(face_s>0)
        index=np.flatnonzero(possible)[good];result[index]=s[index]
    return result


def ray_intervals(body,directions,clearance=0):
    """Exact convex-prism ray clipping from the IP; face padding is conservative."""
    d=np.asarray(directions);n,b=planes3(body);b=b+clearance
    lo=np.zeros(len(d));hi=np.full(len(d),np.inf);valid=np.ones(len(d),bool)
    for normal,bound in zip(n,b):
        denom=d@normal;pos=denom>1e-12;neg=denom< -1e-12
        hi[pos]=np.minimum(hi[pos],bound/denom[pos])
        lo[neg]=np.maximum(lo[neg],bound/denom[neg])
        valid&=~((~pos&~neg)&(bound<0))
    valid&=(hi>=lo)&(hi>=0)
    return np.where(valid,lo,np.inf),np.where(valid,hi,-np.inf)


def expanded(body,margin):
    """Face-offset polyhedron contains the Euclidean margin around the prism."""
    out=dict(body);n,b=polygon_planes(body['vertices_m']);b=b+margin
    out['vertices_m']=[np.linalg.solve(np.stack((n[i-1],n[i])),[b[i-1],b[i]]).tolist()
                       for i in range(4)]
    out['depth_m']=body['depth_m']+2*margin
    return out


def intersects(a,b,clearance=0,tolerance=1e-10):
    """Separating-axis test for convex prisms; touching is a conflict.

    Expanding b by face offsets conservatively enforces clearance. This can
    reject extra near-corner placements; it cannot open an unsafe margin.
    """
    if clearance:b=expanded(b,clearance)
    amin,amax=aabb(a);bmin,bmax=aabb(b)
    if np.any(amax<bmin-tolerance) or np.any(bmax<amin-tolerance):return False
    va,vb=vertices3(a),vertices3(b);na,_=planes3(a);nb,_=planes3(b)
    ea=np.vstack((va[1:4]-va[:3],va[0]-va[3],va[4]-va[0]))
    eb=np.vstack((vb[1:4]-vb[:3],vb[0]-vb[3],vb[4]-vb[0]))
    cross=np.cross(ea[:,None,:],eb[None,:,:]).reshape(-1,3)
    axes=np.vstack((na,nb,cross));norm=np.linalg.norm(axes,axis=1)
    axes=axes[norm>1e-12]/norm[norm>1e-12,None]
    pa,pb=va@axes.T,vb@axes.T
    separate=(pa.max(axis=0)<pb.min(axis=0)-tolerance)|(pb.max(axis=0)<pa.min(axis=0)-tolerance)
    return not bool(separate.any())


def certify_coil_clear(body,config,clearance=.05,resolution=.02,max_cells=50000,width='warm'):
    """Full-volume adaptive proof against exact warm sweeps plus clearance.

    Every cell is enclosed by a sphere. Exact loop-distance and slab masks are
    1-Lipschitz, so a centre clear after adding that sphere radius certifies the
    entire cell. Polygon-plane bounds discard cells wholly outside the prism.
    An actual occupied interior sample rejects it. Unresolved cells are rejected,
    not accepted as clear. Returned evidence distinguishes those two outcomes.
    """
    p=np.asarray(body['vertices_m']);q=np.asarray(body['basis']);o=np.asarray(body['origin_m'])
    n,b=polygon_planes(p);low=np.r_[p.min(axis=0),-body['depth_m']/2]
    high=np.r_[p.max(axis=0),body['depth_m']/2]
    centers=np.array([(low+high)/2]);halves=np.array([(high-low)/2]);checked=0
    while len(centers):
        outside=(centers[:,:2]@n.T-b > halves[:,:2]@abs(n).T+1e-12).any(axis=1)
        centers,halves=centers[~outside],halves[~outside]
        if not len(centers):break
        checked+=len(centers)
        if checked>max_cells:return dict(clear=False,reason='unresolved cell budget',cells=checked)
        bound=np.linalg.norm(halves,axis=1)
        # Batches at one subdivision level share half-widths and hence radius.
        world=centers@q.T+o
        uncertain=np.zeros(len(world),bool)
        for radius in np.unique(bound):
            take=bound==radius
            uncertain[take]=coil_mask(world[take],config,width,clearance=clearance+float(radius))
        if not uncertain.any():break
        centers,halves,world=centers[uncertain],halves[uncertain],world[uncertain]
        inside=(centers[:,:2]@n.T<=b+1e-12).all(axis=1)
        occupied=inside&coil_mask(world,config,width,clearance=clearance)
        if occupied.any():return dict(clear=False,reason='occupied volume witness',cells=checked,
                                     witness_m=world[np.flatnonzero(occupied)[0]].tolist())
        if np.any(np.linalg.norm(halves,axis=1)<=resolution):
            return dict(clear=False,reason='unresolved boundary cells',cells=checked)
        axis=np.argmax(halves,axis=1);child_half=halves.copy()
        child_half[np.arange(len(axis)),axis]/=2
        offset=np.zeros_like(centers);offset[np.arange(len(axis)),axis]=child_half[np.arange(len(axis)),axis]
        centers=np.vstack((centers-offset,centers+offset));halves=np.vstack((child_half,child_half))
    return dict(clear=True,reason='full-volume distance-bound certificate',cells=checked)


def connected_components(edges):
    graph={}
    for a,b in edges:
        graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
    remaining=set(graph);components=[]
    while remaining:
        pending=[min(remaining)];seen=set()
        while pending:
            item=pending.pop()
            if item in seen:continue
            seen.add(item);pending.extend(graph[item]-seen)
        remaining-=seen;components.append(sorted(seen))
    return components


def _rectangle_ray_interval(du,dz,xlo,xhi,zlo,zhi):
    lo=np.zeros(len(du));hi=np.full(len(du),np.inf);valid=np.ones(len(du),bool)
    for d,lower,upper in ((du,xlo,xhi),(dz,zlo,zhi)):
        moving=abs(d)>1e-14
        one=np.divide(lower,d,out=np.zeros_like(d),where=moving)
        two=np.divide(upper,d,out=np.zeros_like(d),where=moving)
        lo[moving]=np.maximum(lo[moving],np.minimum(one,two)[moving])
        hi[moving]=np.minimum(hi[moving],np.maximum(one,two)[moving])
        valid&=moving|((lower<=0)&(upper>=0))
    valid&=hi>=lo
    return np.where(valid,lo,np.inf),np.where(valid,hi,-np.inf)


def _rounded_ray_interval(du,dz,cr,cz,hr,hz,rho):
    """Filled convex rounded rectangle = two rectangles union four full disks."""
    pieces=[_rectangle_ray_interval(du,dz,cr-hr+rho,cr+hr-rho,cz-hz,cz+hz),
            _rectangle_ray_interval(du,dz,cr-hr,cr+hr,cz-hz+rho,cz+hz-rho)]
    aa=du*du+dz*dz
    for sx in (-1,1):
        for sz in (-1,1):
            x,z=cr+sx*(hr-rho),cz+sz*(hz-rho)
            bb=du*x+dz*z;disc=bb*bb-aa*(x*x+z*z-rho*rho)
            valid=(disc>=0)&(aa>1e-28);root=np.sqrt(np.maximum(0,disc))
            lo=np.divide(bb-root,aa,out=np.full(len(du),np.inf),where=valid)
            hi=np.divide(bb+root,aa,out=np.full(len(du),-np.inf),where=valid)
            lo=np.maximum(0,lo);valid&=hi>=lo
            pieces.append((np.where(valid,lo,np.inf),np.where(valid,hi,-np.inf)))
    # The union is convex, so its nonempty line pieces form one interval.
    return np.min([x[0] for x in pieces],axis=0),np.max([x[1] for x in pieces],axis=0)


def coil_ray_intervals(directions,config,clearance=0,width='warm'):
    """Yield exact positive-ray intervals for every finite rounded coil sweep.

    This is an equivalent geometric path query, not a magnetic field solver.
    No C12 replication of rays or support geometry is used.
    """
    d=np.asarray(directions,float);a=config[width]['normal_m']/2+clearance
    b=config[width]['tangent_m']/2+clearance
    for name,g in config['coil_groups'].items():
        rho=g['corner_radius_m'];hr,hz=g['half_r_m'],g['half_z_m']
        if not 0<a<rho:raise ValueError('warm sweep reduction requires0<halfwidth<corner radius')
        for k in range(config['folds']):
            ph=math.radians(g['phi_offset_deg']+k*360/config['folds'])
            du=d[:,0]*math.cos(ph)+d[:,1]*math.sin(ph)
            tangent=-d[:,0]*math.sin(ph)+d[:,1]*math.cos(ph)
            outer=_rounded_ray_interval(du,d[:,2],g['center_r_m'],g['center_z_m'],hr+a,hz+a,rho+a)
            inner=_rounded_ray_interval(du,d[:,2],g['center_r_m'],g['center_z_m'],hr-a,hz-a,rho-a)
            slab=np.divide(b,abs(tangent),out=np.full(len(d),np.inf),where=abs(tangent)>1e-14)
            olo,ohi=outer[0],np.minimum(outer[1],slab)
            for lo,hi in ((olo,np.minimum(ohi,inner[0])),(np.maximum(olo,inner[1]),ohi)):
                valid=np.isfinite(lo)&(hi>=lo)&(hi>=0)
                yield name,k,np.where(valid,lo,np.inf),np.where(valid,hi,-np.inf)
