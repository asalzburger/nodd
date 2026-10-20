"""Full-sphere straight IP rays: outline availability, never efficiency."""
from __future__ import annotations
import math
import numpy as np
from . import geometry as g
from .support import material_parts


def sphere_grid(nmu,nphi):
    mu=-1+(np.arange(nmu)+.5)*2/nmu;phi=(np.arange(nphi)+.5)*360/nphi
    m,p=np.meshgrid(mu,np.radians(phi),indexing='ij');r=np.sqrt(1-m*m)
    return mu,phi,np.column_stack((r.ravel()*np.cos(p).ravel(),r.ravel()*np.sin(p).ravel(),m.ravel()))


def _near(body,directions):
    vertices=g.vertices3(body);centre=vertices.mean(axis=0);distance=np.linalg.norm(centre)
    radius=np.linalg.norm(vertices-centre,axis=1).max()
    if radius>=distance:return np.arange(len(directions))
    return np.flatnonzero(directions@(centre/distance)>=math.sqrt(1-(radius/distance)**2)-1e-12)


def panel_hits(panels,directions,border):
    distances={k:np.full((3,len(directions)),np.inf) for k in ('outer','active','depth')}
    for body in panels:
        near=_near(body,directions)
        if not len(near):continue
        for key,edge,depth in [('outer',0,False),('active',border,False),('depth',border,True)]:
            s=g.midplane_hits(body,directions[near],edge,depth);j=body['station']-1
            distances[key][j,near]=np.minimum(distances[key][j,near],s)
    return distances


def _fractions(count):
    return {str(k):float(np.mean(count==k)) for k in range(4)}


def _lever(distances):
    good=np.isfinite(distances).all(axis=0)
    span=np.ptp(distances[:,good],axis=0)
    if not len(span):return dict(rays=0,quantiles_m=None)
    return dict(rays=int(good.sum()),quantiles_m=dict(zip(['min','p05','median','p95','max'],
                np.quantile(span,[0,.05,.5,.95,1]).tolist())))


def evaluate(geometry,nmu,nphi,shadows=True,reference=True):
    mu,phi,d=sphere_grid(nmu,nphi);shape=(nmu,nphi);N=len(d)
    config=geometry['configuration'];border=config['chambers']['active_border_m']
    distances=panel_hits(geometry['panels'],d,border)
    counts={k:np.isfinite(s).sum(axis=0) for k,s in distances.items()}
    result=dict(mu=mu,phi_deg=phi)
    for k,v in counts.items():result[k+'_count']=v.reshape(shape).astype(np.uint8)
    active=distances['active'];first=np.min(active,axis=0)
    last=np.max(np.where(np.isfinite(active),active,-np.inf),axis=0)
    summary=dict(scope='4pi, both ends, all phi; equal-solid-angle midpoint quadrature',
                 grid=[nmu,nphi],rays=N,solid_angle_sr=4*math.pi,
                 fractions={k:_fractions(v) for k,v in counts.items()},
                 active_three_station_path_span=_lever(active),depth_three_station_path_span=_lever(distances['depth']),
                 hemispheres={label:{k:_fractions(v.reshape(shape)[mask].ravel()) for k,v in counts.items()}
                              for label,mask in [('minus',mu<0),('plus',mu>0)]})
    # Signed eta bands are descriptive subsets; the headline denominator stays 4pi.
    eta=np.arctanh(mu)
    summary['eta_bands']={f'{low:g}<=abs_eta<{high:g}':dict(sphere_fraction=float(np.mean((abs(eta)>=low)&(abs(eta)<high))),
            active_station_fractions=_fractions(counts['active'].reshape(shape)[(abs(eta)>=low)&(abs(eta)<high)].ravel()))
            for low,high in [(0,.8),(.8,1.5),(1.5,2.5),(2.5,math.inf)]}
    if reference:
        ref=panel_hits(geometry['without_support_panels'],d,border)
        ref_count=np.isfinite(ref['active']).sum(axis=0)
        summary['without_support_repacking']=dict(active_station_fractions=_fractions(ref_count),
            three_station_fraction_difference=float(np.mean(ref_count==3)-np.mean(counts['active']==3)),
            scope='counterfactual whole-panel repacking without frame; includes segmentation changes, not a material veto')
        result['without_support_active_count']=ref_count.reshape(shape).astype(np.uint8)
    def flags():return dict(any=np.zeros(N,bool),upstream=np.zeros(N,bool),between=np.zeros(N,bool))
    coil,support=flags(),flags()
    def update(target,index,lo,hi):
        good=np.isfinite(lo)&(hi>=lo)&(hi>=0)
        target['any'][index]|=good
        target['upstream'][index]|=good&(lo<first[index])&np.isfinite(first[index])
        target['between'][index]|=good&(hi>=first[index])&(lo<=last[index])&(counts['active'][index]>=2)
    if shadows:
        index=np.arange(N)
        for _,_,lo,hi in g.coil_ray_intervals(d,geometry['magnetic_configuration']):update(coil,index,lo,hi)
        for member in geometry['supports']['members']:
            for part in material_parts(member):
                near=_near(part,d)
                if len(near):
                    lo,hi=g.ray_intervals(part,d[near]);update(support,near,lo,hi)
    for name,target in [('coil',coil),('support',support)]:
        for key,value in target.items():result[name+'_'+key]=value.reshape(shape)
        good=counts['active']==3
        summary[name+'_shadows']=dict(fractions_full_sphere={k:float(v.mean()) for k,v in target.items()},
            conditional_on_three_active_stations={k:float(v[good].mean()) if good.any() else None for k,v in target.items()},
            scope='warm reservation occupancy (not material budget)' if name=='coil' else 'actual hollow support walls; not a reconstruction veto')
    result['active_station_distances_m']=active.reshape(3,*shape)
    result['summary']=summary
    return result


def compare_sampling(coarse,fine):
    a,b=coarse['summary']['fractions'],fine['summary']['fractions']
    return dict(max_absolute_station_fraction_change=max(abs(a[k][str(n)]-b[k][str(n)]) for k in a for n in range(4)),
                changes={k:{str(n):b[k][str(n)]-a[k][str(n)] for n in range(4)} for k in a},
                interpretation='deterministic grid sensitivity, not statistical error or a convergence proof')


def integrate(geometry,samples=1048576,seed=40087):
    """Independent iid solid-angle integral avoids periodic grid aliasing."""
    rng=np.random.default_rng(seed);mu=rng.uniform(-1,1,samples);phi=rng.uniform(0,2*np.pi,samples)
    r=np.sqrt(1-mu*mu);d=np.column_stack((r*np.cos(phi),r*np.sin(phi),mu))
    distances=panel_hits(geometry['panels'],d,geometry['configuration']['chambers']['active_border_m'])
    out={}
    for key,ss in distances.items():
        count=np.isfinite(ss).sum(axis=0);f=_fractions(count)
        out[key]=dict(fractions=f,standard_error={k:math.sqrt(v*(1-v)/samples) for k,v in f.items()},
                      first_quarter_fractions=_fractions(count[:samples//4]))
    reference=panel_hits(geometry['without_support_panels'],d,geometry['configuration']['chambers']['active_border_m'])
    without=np.isfinite(reference['active']).sum(axis=0)==3
    with_support=np.isfinite(distances['active']).sum(axis=0)==3
    delta=without.astype(float)-with_support.astype(float)
    return dict(method='iid uniform cos(theta),phi; independent of image grid',samples=samples,seed=seed,
                coverage=out,active_three_station_path_span=_lever(distances['active']),
                depth_three_station_path_span=_lever(distances['depth']),
                without_support_repacking=dict(three_active_station_fraction=float(without.mean()),
                    paired_fraction_difference=float(delta.mean()),paired_standard_error=float(delta.std(ddof=1)/np.sqrt(samples)),
                    scope='whole-panel repacking control; includes segmentation changes, not support material veto'),
                scope='binomial standard errors describe integration sampling only; geometry uncertainty excluded')
