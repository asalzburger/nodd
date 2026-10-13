"""DES033 independent turbine faces, circular clipping and physical readout.

Planes tilt about the radial axis. Lead tapers linearly in each blade's local
radial Cartesian coordinate; this is a quantified nODD approximation to taper
specified in cylindrical radius. Readout subdivisions are virtual.
"""
from collections import defaultdict
import json
import math
from pathlib import Path
from barrel_geometry import ROOT, I, annular_area, material_model, sha, dot, cross, rotate

ID_FIELDS = [('system', 8), ('side', 2), ('wheel', 2), ('plane', 11), ('gap', 1), ('rho', 6), ('z', 4)]
ID_DESCRIPTOR = ','.join(f'{key}:{n}' for key,n in ID_FIELDS)


def encode(fields):
    value, offset = 0, 0
    for key,bits in ID_FIELDS:
        number = fields.get(key,0)
        if not 0 <= number < 1 << bits: raise ValueError('ID field bound:'+key)
        value |= number << offset; offset += bits
    return value


def decode(value):
    result, offset = {}, 0
    for key,bits in ID_FIELDS:
        result[key] = (value >> offset) & ((1 << bits)-1); offset += bits
    return result


def frame(angle, negative=False):
    c,s = math.cos(angle),math.sin(angle)
    return [[c,s,0],[s if negative else -s,-c if negative else c,0],[0,0,-1 if negative else 1]]


def at_circle(face, z, radius):
    """Positive-radial branch of tilted planar face at a fixed axial slice."""
    n,b = face['normal'],face['bound']
    q = math.hypot(*n[:2]); nn = [n[0]/q,n[1]/q]
    distance = (b-n[2]*z)/q
    if abs(distance) >= radius: raise ValueError('Blade face misses circular slice')
    chord = math.sqrt(radius*radius-distance*distance)
    return [nn[0]*distance+nn[1]*chord,nn[1]*distance-nn[0]*chord]


def gap_point(piece, radius, z):
    a,b = [at_circle(piece[key],z,radius) for key in ('lower_face','upper_face')]
    angle = math.atan2(a[1],a[0])+math.atan2(cross(a,b),dot(a,b))/2
    return [radius*math.cos(angle),radius*math.sin(angle),z]


def polygon_at(vertices, half, z):
    t = (z+half)/(2*half)
    return [[(1-t)*vertices[i][k]+t*vertices[i+4][k] for k in range(2)] for i in range(4)]


def inside(piece,point,tolerance=1e-8):
    r = math.hypot(*point[:2]);a=piece['clip_annulus_mm']
    if not a['rmin']-tolerance <= r <= a['rmax']+tolerance or abs(point[2]) > piece['half_z_mm']+tolerance: return False
    poly=polygon_at(piece['vertices_mm'],piece['half_z_mm'],point[2])
    values=[cross([b[k]-a[k] for k in range(2)],[point[k]-a[k] for k in range(2)]) for a,b in zip(poly,poly[1:]+poly[:1])]
    return min(values) >= -tolerance or max(values) <= tolerance


def volume(vertices,half,rmin,rmax,steps):
    """Composite Simpson integral of exact circle–polygon slice areas."""
    if steps < 2 or steps%2: raise ValueError('Even axial integration grid required')
    dz = 2*half/steps
    values = [annular_area(polygon_at(vertices,half,-half+i*dz),rmin,rmax) for i in range(steps+1)]
    return dz/3*(values[0]+values[-1]+4*sum(values[1:-1:2])+2*sum(values[2:-1:2]))


def converged_volume(vertices,half,rmin,rmax):
    previous = volume(vertices,half,rmin,rmax,32)
    for n in (64,128,256,512,1024):
        current=volume(vertices,half,rmin,rmax,n)
        relative=abs(current-previous)/current
        if relative < 2e-9:
            return current,dict(coarse_steps=n//2,fine_steps=n,coarse_volume_mm3=previous,fine_volume_mm3=current,relative_change=relative,tolerance=2e-9)
        previous=current
    raise ValueError('Turbine analytic-area axial integral did not converge')


def tapered_face(angle,signed,lead_slope,lead_intercept,offset,alpha):
    ex,ey=rotate([1,0],angle),rotate([0,1],angle)
    n=[math.sin(alpha)*ey[k]-signed*lead_slope*ex[k] for k in range(2)]+[-math.cos(alpha)]
    return dict(normal=n,bound=signed*(lead_intercept+offset))


def primitive(name,role,material,lower,upper,ri,ro,half,m):
    points=[at_circle(face,z,r) for face in (lower,upper) for z in (-half,half) for r in (ri,ro)]
    xmin=min(p[0] for p in points)-10; xmax=ro+10
    vertices=[]
    for z in (-half,half):
        def y(face,x):return (face['bound']-face['normal'][0]*x-face['normal'][2]*z)/face['normal'][1]
        lo=[y(lower,xmin),y(lower,xmax)];hi=[y(upper,xmin),y(upper,xmax)]
        if any(a>=b for a,b in zip(lo,hi)): raise ValueError('Nonpositive physical plate or LAr gap')
        # ROOT Arb8 requires clockwise vertices viewed from positive z.
        vertices += [[xmin,lo[0]],[xmax,lo[1]],[xmax,hi[1]],[xmin,hi[0]]][::-1]
    v,convergence=converged_volume(vertices,half,ri,ro)
    if v <= 0:raise ValueError('Nonpositive clipped turbine volume')
    return dict(name=name,role=role,material=material,shape_kind='arb8',vertices_mm=vertices,half_z_mm=half,clip_annulus_mm=dict(rmin=ri,rmax=ro),center_mm=[0,0,0],frame=I,lower_face=lower,upper_face=upper,volume_mm3=v,mass_g=v*m.recipes[material]['density_g_cm3']/1000,capacity_convergence=convergence)


def cell_indices(point,wheel,readout):
    radius=math.hypot(*point[:2]); r0,r1=wheel['inner_radius_mm'],wheel['outer_radius_mm'];half=readout['sampling_depth_mm']/2
    if radius < r0-1e-8 or radius > r1+1e-8 or abs(point[2]) > half+1e-8:raise ValueError('Hit outside wheel/depth')
    ir=min(wheel['radial_bins']-1,max(0,math.floor((radius-r0)/(r1-r0)*wheel['radial_bins'])))
    iz=min(readout['axial_bins']-1,max(0,math.floor((point[2]+half)/(2*half)*readout['axial_bins'])))
    return ir,iz


def logical_id(fields,point,wheel,readout):
    if fields['side'] not in (1,2) or not 0 <= fields['plane'] < wheel['periods'] or fields['gap'] not in (0,1):raise ValueError('Invalid physical turbine ID')
    rho,z=cell_indices(point,wheel,readout);ids=dict(fields,rho=rho,z=z,gap=0)
    return encode(ids)


def validate_config(c):
    for key,value in c.items():
        if isinstance(value,(int,float)) and (not math.isfinite(value) or value <= 0):raise ValueError('Positive finite input:'+key)
    if c['periods'] != [384,720,1360] or c['radial_bins'] != [10,14,34] or c['axial_bins'] != 10:raise ValueError('Three-wheel DES033 physical/readout contract')
    if c['cold_outer_radius_mm'] != c['source_base_rmax_mm'] or c['cold_inner_radius_mm'] != c['source_base_rmin_mm']:raise ValueError('Source wheel/cold-bath interface')
    front=c['warm_front_z_mm']+c['front_warm_mm']+c['front_vacuum_mm']+c['front_cold_mm']
    back=c['warm_back_z_mm']-c['rear_warm_mm']-c['rear_vacuum_mm']-c['rear_cold_mm']
    if abs(front-c['cold_front_z_mm']) > 1e-8 or abs(back-c['cold_back_z_mm']) > 1e-8:raise ValueError('Axial wall closure')
    if c['sampling_front_z_mm'] < front or c['sampling_front_z_mm']+c['sampling_depth_mm'] >= back:raise ValueError('Sampling/bath depth')
    if abs(c['warm_inner_radius_mm']+c['inner_warm_mm']+c['inner_vacuum_mm']+c['inner_cold_mm']-c['cold_inner_radius_mm']) > 1e-8:raise ValueError('Bore radial wall closure')
    if abs(c['cold_outer_radius_mm']+c['outer_cold_mm']+c['outer_vacuum_mm']+c['outer_warm_mm']-c['warm_outer_radius_mm']) > 1e-8:raise ValueError('Outer radial wall closure')


def build(config=None):
    c=config or json.loads((ROOT/'tools/lar_calorimeter/endcaps.json').read_text());validate_config(c);m=material_model()
    alpha=math.radians(c['inclination_deg']);half=c['sampling_depth_mm']/2
    ratio=((c['source_base_rmax_mm']-c['support_tube_mm'])/c['source_base_rmin_mm'])**(1/3)
    source_inner=c['source_base_rmin_mm'];wheels=[];replicas=[];passive=[]
    centre=c['sampling_front_z_mm']+half
    for wi,(periods,bins) in enumerate(zip(c['periods'],c['radial_bins'])):
        ri=source_inner+c['support_tube_mm'];ro=source_inner*ratio
        if wi==2:ro=c['source_base_rmax_mm']-c['support_tube_mm']
        if math.tan(alpha) < half/ri:raise ValueError('Tilted blade cannot reach declared inner radius')
        source_xmin=math.sqrt(ri*ri-(half/math.tan(alpha))**2)
        lead_outer=c['lead_inner_mm']*(ro/ri)
        slope=(lead_outer-c['lead_inner_mm'])/(ro-source_xmin)/2
        intercept=c['lead_inner_mm']/2-slope*source_xmin
        delta=2*math.pi/periods
        def lead_face(angle,side,offset=0):return tapered_face(angle,side,slope,intercept,offset,alpha)
        def pcb_face(side):return tapered_face(delta/2,side,0,c['electrode_mm']/2,0,alpha)
        pieces=[]
        def add(tag,role,material,lower,upper,gap=None):
            p=primitive(f'w{wi}_{tag}',role,material,lower,upper,ri,ro,half,m)
            if gap is not None:p['gap']=gap
            pieces.append(p)
        add('lead','absorber','Lead',lead_face(0,-1),lead_face(0,1))
        for side in (-1,1):
            a=lead_face(0,side);b=lead_face(0,side,c['glue_total_mm']/2)
            add('glue_'+str(side),'glue','lArCaloGlue',*(a,b) if side>0 else (b,a))
            a=b;b=lead_face(0,side,(c['glue_total_mm']+c['steel_total_mm'])/2)
            add('steel_'+str(side),'skin','lArCaloSteel',*(a,b) if side>0 else (b,a))
        add('pcb','electrode','PCB',pcb_face(-1),pcb_face(1))
        offset=(c['glue_total_mm']+c['steel_total_mm'])/2
        add('gap0','sensitive','LAr',lead_face(0,1,offset),pcb_face(-1),0)
        add('gap1','sensitive','LAr',pcb_face(1),lead_face(delta,-1,offset),1)
        p0=next(p for p in pieces if p.get('gap')==0)
        refs=[];minimum_gap=math.inf;maximum_taper_difference=0.
        for ir in range(bins):
            r=ri+(ir+.5)*(ro-ri)/bins
            for iz in range(c['axial_bins']):
                z=-half+(iz+.5)*2*half/c['axial_bins'];point=gap_point(p0,r,z)
                if not inside(p0,point):raise ValueError('Canonical turbine reference outside physical gap')
                refs.append(dict(rho=ir,z=iz,position_mm=point))
        for r in (ri,(ri+ro)/2,ro):
            for z in (-half,-half/2,0,half/2,half):
                for gap in [p for p in pieces if p['role']=='sensitive']:
                    a,b=[at_circle(gap[key],z,r) for key in ('lower_face','upper_face')]
                    width=math.hypot(b[0]-a[0],b[1]-a[1])*math.sin(alpha)
                    if width<=0:raise ValueError('Nonpositive LAr gap at slice bounds')
                    minimum_gap=min(minimum_gap,width)
                p=at_circle(lead_face(0,1),z,r)
                cartesian=2*(slope*p[0]+intercept);cylindrical=c['lead_inner_mm']*(r/ri)
                maximum_taper_difference=max(maximum_taper_difference,abs(cartesian-cylindrical))
        filled=sum(p['volume_mm3'] for p in pieces)*periods;annulus=math.pi*(ro*ro-ri*ri)*2*half
        residual=filled/annulus-1
        if abs(residual)>1e-7:raise ValueError('Turbine period does not partition wheel annulus')
        wheels.append(dict(wheel=wi,periods=periods,radial_bins=bins,inner_radius_mm=ri,outer_radius_mm=ro,pieces=pieces,reference_points=refs,logical_cells_per_side=periods*bins*c['axial_bins'],min_sampled_gap_mm=minimum_gap,fill_relative_residual=residual,taper=dict(convention='Linear half-thickness in local radial Cartesian x, between sqrt(ri^2-(half_depth*cot(alpha))^2) and ro; source cylindrical endpoint ratio retained.',source_xmin_mm=source_xmin,lead_inner_mm=c['lead_inner_mm'],lead_outer_mm=lead_outer,half_thickness_slope=slope,half_thickness_intercept_mm=intercept,max_sampled_abs_difference_from_cylindrical_taper_mm=maximum_taper_difference)))
        for side in (1,2):
            for plane in range(periods):replicas.append(dict(side=side,wheel=wi,plane=plane,center_mm=[0,0,centre if side==1 else -centre],frame=frame(plane*delta,side==2)))
        source_inner=ro
    def tube(name,role,material,r0,r1,z0,z1,side):
        vol=math.pi*(r1*r1-r0*r0)*(z1-z0)
        passive.append(dict(name=name+'_'+str(side),role=role,material=material,shape_kind='tube',dimensions_mm=dict(rmin=r0,rmax=r1,length=z1-z0),center_mm=[0,0,(z0+z1)/2*(1 if side==1 else -1)],frame=I if side==1 else frame(0,True),volume_mm3=vol,mass_g=vol*m.recipes[material]['density_g_cm3']/1000))
    wf,wb=c['warm_front_z_mm'],c['warm_back_z_mm'];cf,cb=c['cold_front_z_mm'],c['cold_back_z_mm']
    riw=c['warm_inner_radius_mm']+c['inner_warm_mm'];riv=riw+c['inner_vacuum_mm'];ric=c['cold_inner_radius_mm']
    roc=c['cold_outer_radius_mm'];rov=roc+c['outer_cold_mm'];row=rov+c['outer_vacuum_mm']
    wif,wib=wf+c['front_warm_mm'],wb-c['rear_warm_mm'];cof,cob=cf-c['front_cold_mm'],cb+c['rear_cold_mm']
    sf,sb=c['sampling_front_z_mm'],c['sampling_front_z_mm']+2*half
    for side in (1,2):
        for args in [('inner_warm','warm_wall','Aluminium',c['warm_inner_radius_mm'],riw,wf,wb),('outer_warm','warm_wall','Aluminium',row,c['warm_outer_radius_mm'],wf,wb),('inner_vacuum','vacuum','Vacuum',riw,riv,cof,cob),('outer_vacuum','vacuum','Vacuum',rov,row,cof,cob),('inner_cold','cold_wall','Aluminium',riv,ric,cf,cb),('outer_cold','cold_wall','Aluminium',roc,rov,cf,cb),('front_warm','warm_wall','Aluminium',riw,row,wf,wif),('rear_warm','warm_wall','Aluminium',riw,row,wib,wb),('front_vacuum','vacuum','Vacuum',riw,row,wif,cof),('rear_vacuum','vacuum','Vacuum',riw,row,cob,wib),('front_cold','cold_wall','Aluminium',riv,rov,cof,cf),('rear_cold','cold_wall','Aluminium',riv,rov,cb,cob),('front_bath','bath','LAr',ric,roc,cf,sf),('rear_bath','bath','LAr',ric,roc,sb,cb),('sampling_inner_bath','bath','LAr',ric,wheels[0]['inner_radius_mm'],sf,sb)]:tube(*args,side)
        for wheel in wheels:tube('wheel_support'+str(wheel['wheel']),'wheel_support','Aluminium',wheel['outer_radius_mm'],wheel['outer_radius_mm']+c['support_tube_mm'],sf,sb,side)
    ro=dict(name='LArEndcapHits',system_id=c['system_id'],descriptor=ID_DESCRIPTOR,axial_bins=c['axial_bins'],sampling_depth_mm=2*half,semantics='Virtual cylindrical radial and local axial subdivisions; both physical gaps merge to canonical gap0 on the same wheel/electrode. Calibration5/1/1 subdivisions are not physical shower layers.',canonical_gap=0)
    totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    for wheel in wheels:
        for p in wheel['pieces']:
            for key in ('volume_mm3','mass_g'):totals[p['material']][key]+=2*wheel['periods']*p[key]
    for p in passive:
        for key in ('volume_mm3','mass_g'):totals[p['material']][key]+=p[key]
    return dict(status='DRAFT / PROTOTYPE',config=c,materials=m.recipes,wheels=wheels,replicas=replicas,passive=passive,readout=ro,logical_cells_per_side=sum(w['logical_cells_per_side'] for w in wheels),logical_channels=2*sum(w['logical_cells_per_side'] for w in wheels),physical_sensitive_elements=4*sum(c['periods']),physical_material_parts=2*sum(w['periods']*len(w['pieces']) for w in wheels)+len(passive),material_totals=dict(totals),mass_g=sum(v['mass_g'] for v in totals.values()),envelopes=dict(warm_front_z_mm=wf,warm_back_z_mm=wb,warm_inner_radius_mm=c['warm_inner_radius_mm'],warm_outer_radius_mm=c['warm_outer_radius_mm'],sampling_front_z_mm=sf,sampling_back_z_mm=sb),limitations=['Physical blade taper uses Cartesian local radial x; quantified sampled difference from cylindrical-r taper is retained.','Readout rho/z boundaries are virtual; two LAr gaps share one logical cell.','Public calibration5/1/1 labels are not transferred to physical readout layer counts.','Empty service/forward/FCal reservations are not filled by this factory.','Engineering, machine interfaces, response and continuous forward acceptance remain unqualified.'],source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),ROOT/'tools/lar_calorimeter/endcaps.json',ROOT/'tools/lar_calorimeter/barrel_geometry.py',ROOT/'tools/pixel_barrel_dd4hep/materials.py',ROOT/'detector/config/elements.json')}),m
