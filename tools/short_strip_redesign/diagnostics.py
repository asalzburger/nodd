"""Finite straight-plane, planar plumbing and Cu-only directional diagnostics.

All coordinates are mm. These deterministic source screens do not construct
DD4hep solids, propagate curved tracks, or qualify service installation.
"""
import math


def coverage(c, layout, samples=1440):
    """Union exact finite-rectangle radial intervals at each sensor z offset."""
    checks=[]
    for d in layout['discs'][:6]:
        modules=[m for m in layout['modules'] if m['layer']==d['layer']]
        for z0 in (-150.,0.,150.):
            failures=0; min_margin=math.inf; largest_hole=0.
            for k in range(samples):
                phi=(k+.5)*2*math.pi/samples; intervals=[]
                for m in modules:
                    # Positive-z representative; mirrored endcap is identical.
                    delta=phi-math.atan2(m['center_mm'][1],m['center_mm'][0])
                    co=math.cos(delta)
                    if co<=0:continue
                    f=(m['center_mm'][2]-z0)/(d['z_mm']-z0)
                    lo=(m['radius_mm']-48)/(f*co)
                    si=abs(f*math.sin(delta))
                    hi=min((m['radius_mm']+48)/(f*co),24/si if si>1e-14 else math.inf)
                    if hi>=lo:intervals.append((lo,hi))
                intervals.sort(); end=c['target_annulus_mm'][0]; holes=[]
                for lo,hi in intervals:
                    if hi<end:continue
                    if lo>end+1e-9:
                        if end<c['target_annulus_mm'][1]:holes.append(min(lo,c['target_annulus_mm'][1])-end)
                        break
                    end=max(end,hi)
                if end<c['target_annulus_mm'][1]:
                    failures+=1;largest_hole=max(largest_hole,max(holes or [c['target_annulus_mm'][1]-end]))
                min_margin=min(min_margin,end-c['target_annulus_mm'][1])
            checks.append(dict(disc=d['layer'],z0_mm=z0,phi_samples=samples,failed_rays=failures,minimum_outer_margin_mm=min_margin,largest_sampled_hole_mm=largest_hole))
    return dict(method='Finite active rectangles at staggered z; union radial intervals on each disc datum; deterministic midpoint phi. Mirrored endcap symmetry. Not helices/reconstruction or continuous coverage proof.',target_annulus_mm=c['target_annulus_mm'],checks=checks,total_rays=sum(x['phi_samples'] for x in checks))


def cooling_pieces(centres, ports, port_r, offset=20., bend=10.):
    radii=[r+o for r in centres for o in (-offset,offset)]
    pieces=[];a,b=map(math.radians,(6.,24.))
    def arc(label,center,r,start,angle):
        pieces.append(dict(label=label,kind='arc',center=center,radius=r,start=start,angle=angle))
    for i,r in enumerate(radii):
        end=b
        if i in (0,len(radii)-1):
            phi=math.radians(ports[0 if i==0 else 1]);delta=math.asin(bend/(r+bend));cx=math.sqrt(r*r+2*r*bend)
            end=phi-delta;center=[cx*math.cos(phi)+bend*math.sin(phi),cx*math.sin(phi)-bend*math.cos(phi)]
            arc('entry'+str(i),center,bend,phi+math.pi/2,math.pi/2-delta)
            if port_r<=cx:raise ValueError('Negative terminal cooling straight')
            pieces.append(dict(label='port'+str(i),kind='line',a=[cx*math.cos(phi),cx*math.sin(phi)],b=[port_r*math.cos(phi),port_r*math.sin(phi)]))
        arc('leg'+str(i),[0.,0.],r,a,end-a)
        if i<len(radii)-1:
            right=i%2==1;phi=b if right else a;mid=(r+radii[i+1])/2
            arc('U'+str(i),[mid*math.cos(phi),mid*math.sin(phi)],(radii[i+1]-r)/2,phi if right else phi+math.pi,math.pi)
    return pieces


def piece_length(p):
    return p['radius']*p['angle'] if p['kind']=='arc' else math.dist(p['a'],p['b'])


def sample_piece(p, step=.5):
    n=math.ceil(piece_length(p)/step)
    if p['kind']=='line':return [[p['a'][j]+(p['b'][j]-p['a'][j])*i/n for j in (0,1)] for i in range(n+1)]
    return [[p['center'][j]+p['radius']*(math.cos if j==0 else math.sin)(p['start']+p['angle']*i/n) for j in (0,1)] for i in range(n+1)]


def sampled_interloop_clearance(first, second, diameter):
    """Grid-accelerated point distance; .5mm steps imply <=.5mm error.

    A lower bound subtracts both half-step errors, so PASS is conservative.
    Only interloop separation is tested; within-loop bend self-intersection and
    complete pipe/foam/module solids need a native construction.
    """
    buckets={};cell=10.
    for p in first:
        for xy in sample_piece(p):buckets.setdefault(tuple(math.floor(x/cell) for x in xy),[]).append(xy)
    minimum=math.inf
    for p in second:
        for xy in sample_piece(p):
            ix,iy=[math.floor(x/cell) for x in xy]
            for x in range(ix-2,ix+3):
                for y in range(iy-2,iy+3):
                    for other in buckets.get((x,y),[]):minimum=min(minimum,math.dist(xy,other))
    if not math.isfinite(minimum):raise ValueError('No close route pair in search')
    return dict(sample_step_mm=.5,sampled_minimum_centreline_mm=minimum,conservative_lower_bound_mm=minimum-.5,surface_clearance_lower_bound_mm=minimum-.5-diameter,passed=minimum-.5>diameter,scope='Interloop planar sampled lower bound only; excludes same-loop and solid/support/manifold checks')


def cooling_routes(c, old):
    lo,hi=old['annulus_mm'];old_centres=[lo+48-2+i*((hi-48+2)-(lo+48-2))/4 for i in range(5)]
    # The old source contains a negative final port length: keep its signed
    # length for traceability, rather than claiming it is constructible.
    try:old_p=cooling_pieces(old_centres,[29,28],old['port_radius_mm'])
    except ValueError:old_p=cooling_pieces(old_centres,[29,28],712.)
    # Undo the temporary port extension to preserve the historical source's
    # signed analytical length, including its invalid negative final straight.
    old_signed_length=sum(map(piece_length,old_p))-2*(712.-old['port_radius_mm'])
    inner=cooling_pieces(c['ring_centres_mm'][:3],c['cooling_ports_deg'][:2],c['cooling_port_radius_mm'])
    outer=cooling_pieces(c['ring_centres_mm'][3:],c['cooling_ports_deg'][2:],c['cooling_port_radius_mm'])
    return dict(old_total_length_mm=old_signed_length,new_total_length_mm=sum(map(piece_length,inner+outer)),old_comparison='Historical five-ring signed analytical length; inherited678mm port has a negative straight and is not constructible as written. New length includes its correction; old geometry not repaired in place.',inner=inner,outer=outer,interloop_clearance=sampled_interloop_clearance(inner,outer,c['leaf_pipe_OD_mm']),loop_module_counts=[16,17])


def copper_profile(c,ec,bl):
    """Azimuth-averaged longitudinal trunk copper alone, not full tracker X0."""
    values=[];edges=[.7+i*.02 for i in range(151)]
    for lo,hi in zip(edges,edges[1:]):
        eta=(lo+hi)/2;results=[]
        for selected in (False,True):
            rin,rout=(c['trunk_mm'][:2] if selected else [710.,783.]);cu=(2*c['lv_area_per_conductor_mm2']+2*14*c['hv_area_per_conductor_mm2']+c['control_copper_mm2']+c['shield_copper_mm2'] if selected else math.pi/4*13.4**2*.2)
            joins=[1310.]+[z+(100. if selected else 85.) for z in ec['disc_z_mm']]+[3500.]
            total=0.
            for i,(z1,z2) in enumerate(zip(joins,joins[1:])):
                lower=max(z1,rin*math.sinh(eta));upper=min(z2,rout*math.sinh(eta))
                if upper>lower:
                    feeds=(288 if selected else 576)+36*i
                    fraction=feeds*cu/(math.pi*(rout*rout-rin*rin))
                    total+=(upper-lower)/math.tanh(eta)*fraction/c['material']['Cu_X0_mm']
            results.append(total)
        values.append(results)
    return dict(eta_edges=edges,old_X0=[v[0] for v in values],new_X0=[v[1] for v in values],normalization='Straight origin rays, azimuth-averaged homogeneous annulus copper density; positive end by symmetry. Only longitudinal power/HV/control/shield trunk Cu. Excludes all other tracker material, collectors, radial legs and scattering. No statistical uncertainty; design assumptions dominate.')
