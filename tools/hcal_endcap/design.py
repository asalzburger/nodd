"""DES038 analytical whole-carrier endcap proposal; mm, g, W, standard library.

The active mask samples actual tile-core rectangles at carrier local z=2 mm.
It does not intersect finite scintillator/recess solids or simulate particles.
"""
import argparse
import copy
import csv
import functools
import hashlib
import importlib.util
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CONFIG=Path(__file__).with_name('config.json')
EPS=1e-7
SCENARIOS=('uniform','adaptive','staggered','narrow_wedge')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@functools.lru_cache(maxsize=1)
def _load_common_readout():
    path=ROOT/'tools/hcal_readout/readout.py'
    spec=importlib.util.spec_from_file_location('_des038_common_readout',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    report,_=module.build(absorber=False)
    return report


def verify_common_sources(report, retained=None):
    """Bind executed module inputs to retained DES036 evidence, not just HEAD."""
    if retained is None:
        retained=json.loads((ROOT/'docs/validation/DES-036/budgets.json').read_text())['source_sha256']
    for path,digest in report['source_sha256'].items():
        if retained.get(path)!=digest or sha(ROOT/path)!=digest:
            raise ValueError('common working baseline differs from retained DES036 source: '+path)
    return True


def common_readout():
    report=_load_common_readout()
    verify_common_sources(report)
    return report


def polygon(apothem,n=16):
    r=apothem/math.cos(math.pi/n)
    return [[r*math.cos((2*i+1)*math.pi/n),r*math.sin((2*i+1)*math.pi/n)] for i in range(n)]


def polygon_area(points):
    return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1])))/2 if points else 0


def regular_area(apothem,n=16): return n*apothem**2*math.tan(math.pi/n)


def clip_halfplane(points,nx,ny,threshold):
    """Keep nx*x+ny*y >= threshold, with exact line intersections."""
    out=[]
    if not points:return out
    for a,b in zip(points,points[1:]+points[:1]):
        va=nx*a[0]+ny*a[1]-threshold;vb=nx*b[0]+ny*b[1]-threshold
        if va>=-EPS:out.append(a[:])
        if (va<0<vb) or (vb<0<va):
            t=va/(va-vb);out.append([a[j]+t*(b[j]-a[j]) for j in (0,1)])
    return out


def quarter_polygon(apothem,gap,n):
    return clip_halfplane(clip_halfplane(polygon(apothem,n),1,0,gap/2),0,1,gap/2)


def inside_polygon(point,apothem,n=16):
    return all(point[0]*math.cos(2*i*math.pi/n)+point[1]*math.sin(2*i*math.pi/n)<=apothem+EPS for i in range(n))


def rect_corners(cx,cy,w,h):
    return [[cx+sx*w/2,cy+sy*h/2] for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]


def separated(poly,rectangle):
    """Exact convex SAT; touching boundaries are permitted, interiors excluded."""
    for points in (poly,rectangle):
        for a,b in zip(points,points[1:]+points[:1]):
            nx,ny=-(b[1]-a[1]),b[0]-a[0]
            pa=[nx*p[0]+ny*p[1] for p in poly];pb=[nx*p[0]+ny*p[1] for p in rectangle]
            if max(pa)<=min(pb)+EPS or max(pb)<=min(pa)+EPS:return True
    return False


def whole_carrier_fits(cx,cy,c,common=None):
    u=common or common_readout();w,h,_=u['fixture']['carrier_size_mm'];e=c['envelope']
    corners=rect_corners(cx,cy,w,h)
    return all(inside_polygon(p,e['outer_apothem_mm']-e['outer_frame_mm'],e['sides']) for p in corners) and separated(polygon(e['inner_apothem_mm']+e['inner_frame_mm'],e['sides']),corners)


def safe_front(x_low,apothem,n):
    # For a positive-quadrant rectangle, aperture separation is reached when
    # its lower-left corner leaves any positive supporting halfplane.
    if x_low>=apothem-EPS:return 0.
    limits=[(apothem-math.cos(2*i*math.pi/n)*x_low)/math.sin(2*i*math.pi/n) for i in range(n) if math.sin(2*i*math.pi/n)>EPS and math.cos(2*i*math.pi/n)>=-EPS]
    return max(0,min(limits))


def rotate_xy(point,degrees):
    a=math.radians(degrees);co,si=math.cos(a),math.sin(a)
    return [co*point[0]-si*point[1],si*point[0]+co*point[1]]


def sector_of(x,y,n=16):return int((math.atan2(y,x)%(2*math.pi))*n/(2*math.pi))%n


def make_pattern(c,adaptive=True,narrow=False):
    u=common_readout();w,h,_=u['fixture']['carrier_size_mm'];e,p=c['envelope'],c['packing'];out=[];columns=[];reserved=[]
    outer=e['outer_apothem_mm']-e['outer_frame_mm'];inner=e['inner_apothem_mm']+e['inner_frame_mm'];qgap=p['quarter_gap_mm']/2
    i=0
    while p['first_column_x_mm']+i*p['column_pitch_mm']-w/2<outer:
        cx=p['first_column_x_mm']+i*p['column_pitch_mm']
        yfront=max(qgap,safe_front(cx-w/2,inner,e['sides'])) if adaptive else qgap
        columns.append(dict(column=i,x_mm=cx,first_front_y_mm=yfront))
        row=0
        while yfront+row*p['row_pitch_mm']<outer:
            cy=yfront+row*p['row_pitch_mm']+h/2
            for sx,sy in ((1,1),(-1,1),(-1,-1),(1,-1)):
                x,y=sx*cx,sy*cy;corners=rect_corners(x,y,w,h)
                fit=whole_carrier_fits(x,y,c,u)
                if narrow:
                    sector=sector_of(x,y,e['sides'])
                    fit=fit and all(sector_of(*v,e['sides'])==sector for v in corners)
                if fit:out.append(dict(index=len(out),column=i,row=row,quadrant=(0 if sx>0 and sy>0 else 1 if sy>0 else 2 if sx<0 else 3),sign_xy=[sx,sy],center_xy_mm=[x,y],corners_xy_mm=corners))
            row+=1
        i+=1
    for q in out:
        x,y=q['center_xy_mm'];sx,sy=q['sign_xy']
        for role,rx,ry,rw,rh in [('column_trunk',x+sx*(w/2+p['collector_gap_mm']/2),y,p['collector_gap_mm'],h),('row_collector',x,y+sy*(h/2+p['collector_gap_mm']/2),w,p['collector_gap_mm'])]:
            corners=rect_corners(rx,ry,rw,rh)
            if all(inside_polygon(v,outer,e['sides']) for v in corners) and separated(polygon(inner,e['sides']),corners):
                reserved.append(dict(role=role,center_xy_mm=[rx,ry],size_xy_mm=[rw,rh],owner='external collector design pending',material='none; empty reservation'))
    return dict(carriers=out,columns=columns,collector_reservations=reserved,phases_deg=p['phases_deg'] if adaptive and not narrow else [0],basis='carrier axes global x/y before whole-layer phase rotation')


def frame_for(degrees,side):
    co,si=math.cos(math.radians(degrees)),math.sin(math.radians(degrees));sign=1 if side==1 else -1
    return [[co,sign*si,0],[-si,sign*co,0],[0,0,sign]]


def determinant(f):
    a,b,c=f;return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])


def transform(point,center,frame):
    return [center[j]+sum(point[i]*frame[i][j] for i in range(3)) for j in range(3)]


def carrier_volume_id(side,sector,layer,carrier,module=0,sensor=0):
    values=(side,sector,layer,carrier,module,sensor)
    if not (side in (1,2) and 0<=sector<16 and 0<=layer<64 and 0<=carrier<4096 and 0<=module<2 and 0<=sensor<36):raise ValueError('identifier capacity')
    return 9 | side<<8 | sector<<10 | layer<<14 | carrier<<20 | module<<32 | sensor<<34


def layout_placements(c,pattern,u):
    out=[];s=c['sampling'];e=c['envelope'];depth=u['fixture']['carrier_size_mm'][2];pitch=s['steel_mm']+depth+s['installation_gap_mm']
    endpoints=[(p['name'],p['center_mm']) for p in u['parts'] if p['role'].startswith('connector_')]
    for side in (1,2):
        sign=1 if side==1 else -1
        for layer in range(s['layers']):
            phase=c['packing']['phases_deg'][layer%len(c['packing']['phases_deg'])];frame=frame_for(phase,side);counters=Counter()
            for q in pattern['carriers']:
                x,y=rotate_xy(q['center_xy_mm'],phase);y*=sign;z=sign*(e['front_abs_z_mm']+layer*pitch+s['steel_mm']);sector=sector_of(x,y,e['sides']);cid=counters[sector];counters[sector]+=1
                if cid>=4096:raise ValueError('identifier carrier capacity')
                center=[x,y,z]
                water=[dict(name=p['name'],center_mm=transform(p['centre_mm'],center,frame),direction=transform(p['direction'],[0,0,0],frame),flow_role=p['flow_role'],branch=p['branch']) for p in u['services']['cooling_handoffs']]
                out.append(dict(side=side,layer=layer,sector=sector,carrier=cid,prototype=q['index'],phase_deg=phase,origin_mm=center,frame=frame,volume_id=carrier_volume_id(side,sector,layer,cid),water_ports=water,connectors=[dict(name=name,center_mm=transform(point,center,frame)) for name,point in endpoints],collector_handoff=dict(quadrant=q['quadrant'],column=q['column'],row=q['row'],quadrant_bus=f"side{side}_layer{layer}_quarter{q['quadrant']}_column{q['column']}",perimeter_bus=f"side{side}_layer{layer}_perimeter_sector{sector}",target='named quadrant/perimeter reservations; connecting routes and frame crossing ports absent',connected=False)))
    return out


def rollup(c,u,n):
    e,s=c['envelope'],c['sampling'];layers=s['layers'];sampling_depth=layers*(s['steel_mm']+u['fixture']['carrier_size_mm'][2]+s['installation_gap_mm'])
    inner=e['inner_apothem_mm']+e['inner_frame_mm'];outer=e['outer_apothem_mm']-e['outer_frame_mm'];qo=quarter_polygon(outer,c['packing']['quarter_gap_mm'],e['sides']);qi=quarter_polygon(inner,c['packing']['quarter_gap_mm'],e['sides']);steel_area=4*(polygon_area(qo)-polygon_area(qi))
    al_frame_area=regular_area(inner,e['sides'])-regular_area(e['inner_apothem_mm'],e['sides'])+regular_area(e['outer_apothem_mm'],e['sides'])-regular_area(outer,e['sides'])
    full_area=regular_area(e['outer_apothem_mm'],e['sides'])-regular_area(e['inner_apothem_mm'],e['sides']);packable=regular_area(outer,e['sides'])-regular_area(inner,e['sides']);steel_volume=2*layers*s['steel_mm']*steel_area;frame_volume=2*sampling_depth*al_frame_area;cover_volume=2*s['back_cover_mm']*full_area
    totals={k:dict(volume_mm3=v['volume_mm3']*n,mass_g=v['mass_g']*n) for k,v in u['material_totals'].items()}
    for material,volume in [('Steel235',steel_volume),('Aluminium',frame_volume+cover_volume)]:
        item=totals.setdefault(material,dict(volume_mm3=0.,mass_g=0.));item['volume_mm3']+=volume;item['mass_g']+=volume*u['materials'][material]['density_g_cm3']/1000
    power=[{k:(v*n if k!='current_A_per_device' else v) for k,v in scenario.items()} for scenario in u['budgets']['power_scenarios']]
    daq=[dict(accepted_Hz=q['accepted_Hz'],aggregate_demand_bps=q['carrier_demand_bps']*n,aggregate_payload_budget_bps=q['carrier_payload_capacity_bps']*n,utilization=q['utilization'],status=q['status'],qualification='sum of local budgets; concentration/connectivity not qualified') for q in u['budgets']['daq']]
    return dict(carriers=n,boards=2*n,tiles=72*n,connected_channels=72*n,powered_channels=156*n,ordinary_unused_channels=72*n,auxiliary_channels=12*n,local_water_ports=4*n,LV_bias_data_control_handoffs_each=n,material_totals=totals,mass_g=sum(v['mass_g'] for v in totals.values()),common_hardware_mass_g=n*u['carrier_and_modules_mass_g'],steel_mass_g=steel_volume*u['materials']['Steel235']['density_g_cm3']/1000,shared_frame_mass_g=frame_volume*u['materials']['Aluminium']['density_g_cm3']/1000,back_cover_mass_g=cover_volume*u['materials']['Aluminium']['density_g_cm3']/1000,power_scenarios=power,daq=daq,trigger=dict(lanes=8*n,raw_budget_bps=2*u['budgets']['trigger']['raw_bps_per_chip']*n,note='separate from DAQ; no concentrator qualification'),areas_mm2=dict(full_fiducial_annulus=full_area,packable_annulus=packable,steel_per_layer=steel_area,frame_annuli=al_frame_area),shared_geometry=dict(steel_quarter_outer=qo,steel_quarter_inner_hole=qi,steel_quarters_per_layer=4,steel_quarter_rotations_deg=[0,90,180,270],steel_seam_rotates_with_layer=True,inner_frame_apothems_mm=[e['inner_apothem_mm'],inner],outer_frame_apothems_mm=[outer,e['outer_apothem_mm']],sampling_depth_mm=sampling_depth,frame_ownership='once per end, continuous annuli',back_cover_ownership='once per end after sampling stack',empty_collector_strips_remove_steel=False),sampling_depth_mm=sampling_depth,total_depth_mm=sampling_depth+s['back_cover_mm'])


def build(config=None):
    c=copy.deepcopy(config if config is not None else json.loads(CONFIG.read_text()));u=common_readout()
    validate_config(c,u)
    adaptive=make_pattern(c);uniform=make_pattern(c,adaptive=False);narrow=make_pattern(c,narrow=True)
    patterns=dict(uniform=uniform,adaptive=copy.deepcopy(adaptive),staggered=adaptive,narrow_wedge=narrow);patterns['adaptive']['phases_deg']=[0]
    placements=layout_placements(c,adaptive,u);summary=rollup(c,u,len(placements));s=c['sampling'];e=c['envelope'];pitch=s['steel_mm']+u['fixture']['carrier_size_mm'][2]+s['installation_gap_mm'];localz=u['config']['module']['tile_z_mm'];first=e['front_abs_z_mm']+s['steel_mm']+localz
    corewidth=u['config']['module']['tile_size_mm'][0];coreheight=u['config']['module']['tile_size_mm'][1];corearea=72*corewidth*coreheight
    diagnostics={}
    for name,pat in patterns.items():
        minimum=math.inf
        for q in pat['carriers']:
            cx,cy=q['center_xy_mm']
            for tile in u['channel_map']:
                tx,ty=tile['tile_center_mm'][:2];x,y=cx+tx,cy+ty
                minimum=min(minimum,math.hypot(max(abs(x)-corewidth/2,0),max(abs(y)-coreheight/2,0)))
        count=len(pat['carriers']);diagnostics[name]=dict(carriers_per_layer_per_end=count,core_area_mm2=count*corearea,full_face_core_fraction=count*corearea/summary['areas_mm2']['full_fiducial_annulus'],packable_face_core_fraction=count*corearea/summary['areas_mm2']['packable_annulus'],first_core_radius_mm=minimum)
    summary.update(pattern_diagnostics=diagnostics,first_active_plane_abs_z_mm=first,last_active_plane_abs_z_mm=first+(s['layers']-1)*pitch,common_face_core_fraction=corearea/(u['fixture']['carrier_size_mm'][0]*u['fixture']['carrier_size_mm'][1]),steel_path_screening=dict(status='NOT_RUN',reason='finite-depth clipped-quarter plate/ray intersection is outside the core-plane mask scope'),qualification='analytical geometry, source-bound local ledgers and core-plane sampling only')
    source=dict(u['source_sha256']);source.update({str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),CONFIG,ROOT/'docs/design/DES-038-hcal-endcap-common-module.md',ROOT/'docs/validation/DES-036/budgets.json')})
    layers=[dict(side=side,layer=layer,phase_deg=c['packing']['phases_deg'][layer%len(c['packing']['phases_deg'])],absorber_front_abs_z_mm=e['front_abs_z_mm']+layer*pitch,absorber_back_abs_z_mm=e['front_abs_z_mm']+layer*pitch+s['steel_mm'],carrier_front_abs_z_mm=e['front_abs_z_mm']+layer*pitch+s['steel_mm'],carrier_back_abs_z_mm=e['front_abs_z_mm']+layer*pitch+s['steel_mm']+u['fixture']['carrier_size_mm'][2],core_plane_abs_z_mm=first+layer*pitch,whole_pattern_ownership='phase rotates carriers, steel quarter joints and empty collector reservations together',frame=frame_for(c['packing']['phases_deg'][layer%len(c['packing']['phases_deg'])],side)) for side in (1,2) for layer in range(s['layers'])]
    data=dict(schema_version=1,status='PROTOTYPE / DRAFT',input_revision=c['input_revision'],config=c,common=u,patterns=patterns,placements=placements,layers=layers,summary=summary,source_sha256=source)
    validate(data);return data


def validate_config(c,u):
    e,s,p=c['envelope'],c['sampling'],c['packing'];w,h,d=u['fixture']['carrier_size_mm']
    if c['collision_energy_TeV']!=14 or e['sides']!=16 or s['layers']!=36:raise ValueError('DES038 operating/layer/polygon contract')
    if [w,h,d]!=[380,240,12] or u['fixture']['absorber_present'] or any(q['role']=='absorber_reference' or q['owner']=='sector' for q in u['parts']):raise ValueError('common carrier or duplicated absorber')
    expected=s['layers']*(s['steel_mm']+d+s['installation_gap_mm'])+s['back_cover_mm']
    if not math.isclose(e['back_abs_z_mm']-e['front_abs_z_mm'],expected,abs_tol=EPS):raise ValueError('endcap depth budget')
    if p['column_pitch_mm']<w+p['collector_gap_mm'] or p['row_pitch_mm']<h+p['collector_gap_mm'] or p['first_column_x_mm']-w/2<p['quarter_gap_mm']/2-EPS:raise ValueError('grid or quarter clearance')
    if c['negative_end_frame']!=[[1,0,0],[0,-1,0],[0,0,-1]]:raise ValueError('negative end requires proper Rx(pi), not reflection')
    if any(not math.isclose(v/22.5,round(v/22.5),abs_tol=EPS) for v in p['phases_deg']) or not p['phases_deg']:raise ValueError('polygon-invariant layer phases')
    if min(e['inner_frame_mm'],e['outer_frame_mm'],s['steel_mm'],s['installation_gap_mm'],s['back_cover_mm'],p['quarter_gap_mm'])<=0 or e['inner_apothem_mm']+e['inner_frame_mm']>=e['outer_apothem_mm']-e['outer_frame_mm']:raise ValueError('positive disjoint support/stack dimensions')


def validate(data):
    c,u=data['config'],data['common'];validate_config(c,u)
    for name,pat in data['patterns'].items():
        seen=set()
        for q in pat['carriers']:
            x,y=q['center_xy_mm']
            if not whole_carrier_fits(x,y,c,u):raise ValueError('whole carrier outer/aperture containment')
            if q['corners_xy_mm']!=rect_corners(x,y,*u['fixture']['carrier_size_mm'][:2]):raise ValueError('carrier corner representation')
            column=pat['columns'][q['column']];sx,sy=q['sign_xy'];expected_center=[sx*column['x_mm'],sy*(column['first_front_y_mm']+q['row']*c['packing']['row_pitch_mm']+u['fixture']['carrier_size_mm'][1]/2)]
            if any(abs(a-b)>EPS for a,b in zip(q['center_xy_mm'],expected_center)):raise ValueError('overlapping/shifted carrier grid')
            key=tuple(q['center_xy_mm'])
            if key in seen:raise ValueError('overlapping carrier grid')
            seen.add(key)
    ids=set();counts=Counter()
    for q in data['placements']:
        if not math.isclose(determinant(q['frame']),1,abs_tol=EPS):raise ValueError('improper carrier frame')
        wanted_frame=frame_for(q['phase_deg'],q['side'])
        if any(abs(q['frame'][i][j]-wanted_frame[i][j])>EPS for i in range(3) for j in range(3)):raise ValueError('carrier frame differs from proper layer/end rotation')
        base=data['patterns']['staggered']['carriers'][q['prototype']];xy=rotate_xy(base['center_xy_mm'],q['phase_deg']);sign=1 if q['side']==1 else -1
        pitch=c['sampling']['steel_mm']+u['fixture']['carrier_size_mm'][2]+c['sampling']['installation_gap_mm']
        expected_center=[xy[0],sign*xy[1],sign*(c['envelope']['front_abs_z_mm']+q['layer']*pitch+c['sampling']['steel_mm'])]
        if any(abs(a-b)>EPS for a,b in zip(q['origin_mm'],expected_center)):raise ValueError('carrier placement transform/stack')
        key=(q['side'],q['layer'],q['sector'],q['carrier'])
        if key in ids:raise ValueError('duplicate carrier ID')
        ids.add(key);counts[q['side'],q['layer']]+=1
        if q['volume_id']!=carrier_volume_id(q['side'],q['sector'],q['layer'],q['carrier']):raise ValueError('carrier volume ID')
        if q['sector']!=sector_of(*q['origin_mm'][:2],c['envelope']['sides']):raise ValueError('angular sector bookkeeping')
        for p,local in zip(q['water_ports'],u['services']['cooling_handoffs']):
            expected=transform(local['centre_mm'],q['origin_mm'],q['frame']);direction=transform(local['direction'],[0,0,0],q['frame'])
            if any(abs(a-b)>EPS for a,b in zip(p['center_mm'],expected)) or any(abs(a-b)>EPS for a,b in zip(p['direction'],direction)):raise ValueError('water port transform')
        if len(q['water_ports'])!=4 or len(q['connectors'])!=4:raise ValueError('physical service handoff count')
    n=len(data['patterns']['staggered']['carriers'])
    if set(counts.values())!={n} or len(counts)!=2*c['sampling']['layers']:raise ValueError('end/layer carrier conservation')
    expected=rollup(c,u,len(data['placements']))
    for key in ('tiles','powered_channels','mass_g','common_hardware_mass_g','steel_mass_g','shared_frame_mass_g','back_cover_mass_g','material_totals','power_scenarios','daq','trigger'):
        if data['summary'][key]!=expected[key]:raise ValueError('mass/channel/power conservation '+key)
    if data['summary']['powered_channels']!=156*len(data['placements']):raise ValueError('all powered channels')
    return True


def hit_core(data,x,y,phase,scenario):
    """O(1) column/row lookup, then nearest board/tile; no sensitive sheet."""
    c=data['config'];u=data['common'];p=c['packing'];pat=data['patterns'][scenario];x,y=rotate_xy([x,y],-phase)
    ax,ay=abs(x),abs(y);w,h,_=u['fixture']['carrier_size_mm'];col=round((ax-p['first_column_x_mm'])/p['column_pitch_mm'])
    if col<0 or col>=len(pat['columns']):return False
    first=pat['columns'][col]['first_front_y_mm'];row=math.floor((ay-first)/p['row_pitch_mm'])
    if row<0:return False
    sx=1 if x>=0 else -1;sy=1 if y>=0 else -1
    # Membership enforces outer/aperture clipping, including narrow-wedge control.
    lookup=_lookup(data,scenario)
    q=lookup.get((col,row,sx,sy))
    if q is None:return False
    dx=x-q['center_xy_mm'][0];dy=y-q['center_xy_mm'][1]
    if abs(dx)>w/2+EPS or abs(dy)>h/2+EPS:return False
    module=0 if dx<0 else 1;bx,by=u['config']['carrier']['board_centres_xy_mm'][module];m=u['config']['module'];pitch=m['tile_pitch_mm'];ix=round((dx-bx)/pitch+(m['rows']-1)/2);iy=round((dy-by)/pitch+(m['rows']-1)/2)
    if not (0<=ix<m['rows'] and 0<=iy<m['rows']):return False
    tx=bx+(ix-(m['rows']-1)/2)*pitch;ty=by+(iy-(m['rows']-1)/2)*pitch
    return abs(dx-tx)<=m['tile_size_mm'][0]/2+EPS and abs(dy-ty)<=m['tile_size_mm'][1]/2+EPS


_LOOKUPS={}

def _lookup(data,scenario):
    # Process-local acceleration cache. Exported data contains no runtime keys.
    key=(id(data),scenario)
    if key not in _LOOKUPS:_LOOKUPS[key]=(data,{(q['column'],q['row'],*q['sign_xy']):q for q in data['patterns'][scenario]['carriers']})
    return _LOOKUPS[key][1]


def ray_counts(data,eta,phi,scenario='staggered'):
    if scenario not in SCENARIOS:raise ValueError('unknown coverage scenario')
    if eta==0:return dict(count=0,layers=[],side=1)
    c=data['config'];u=data['common'];s=c['sampling'];first=data['summary']['first_active_plane_abs_z_mm'];pitch=s['steel_mm']+u['fixture']['carrier_size_mm'][2]+s['installation_gap_mm'];negative=eta<0;co,si=math.cos(phi),math.sin(phi);scale=1/math.sinh(abs(eta));layers=[];phases=data['patterns'][scenario]['phases_deg']
    for layer in range(s['layers']):
        radius=(first+layer*pitch)*scale;x,y=radius*co,radius*si
        if negative:y=-y
        phase=phases[layer%len(phases)]
        if hit_core(data,x,y,phase,scenario):layers.append(layer)
    return dict(count=len(layers),layers=layers,side=2 if negative else 1)


def coverage(data):
    c=data['config']['coverage'];etas=sorted({round(c['eta_min']+i*c['eta_step'],10) for i in range(round((c['eta_max']-c['eta_min'])/c['eta_step'])+1)}|set(c['extra_eta']));phis=[2*math.pi*i/c['phi_bins'] for i in range(c['phi_bins'])];rows=[];samples=[];mirror=True
    for scenario in SCENARIOS:
        for eta in etas:
            values=[]
            for phi in phis:
                value=ray_counts(data,eta,phi,scenario)['count'];values.append(value)
                samples.append(dict(scenario=scenario,eta=eta,phi_rad=phi,core_planes=value))
            rows.append(dict(scenario=scenario,eta=eta,phi_bins=len(phis),minimum=min(values),mean=sum(values)/len(values),maximum=max(values),zero_fraction=values.count(0)/len(values),partial_fraction=sum(0<v<data['config']['sampling']['layers'] for v in values)/len(values),minimum_fraction=min(values)/data['config']['sampling']['layers'],mean_fraction=sum(values)/(len(values)*data['config']['sampling']['layers']),maximum_fraction=max(values)/data['config']['sampling']['layers']))
        # Rx(pi) maps a positive (eta,phi) ray to negative (-eta,-phi).
        for eta in (1.,2.,3.,3.5,4.,5.):
            for phi in phis[::15]:
                mirror &= ray_counts(data,eta,phi,scenario)['layers']==ray_counts(data,-eta,-phi,scenario)['layers']
    return dict(scope='IP rays sampled at local tile-core z=2 mm; no finite solid or particle efficiency claim',phi_bins=c['phi_bins'],eta_samples=etas,rows=rows,negative_end_Rx_pi_mirror_consistent=mirror,steel_path_screening=data['summary']['steel_path_screening'],source_sha256=data['source_sha256'],full_samples_file='samples.csv'),samples


def export(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);data=build();cov,samples=coverage(data)
    execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)))
    summary=dict(schema_version=1,status=data['status'],input_revision=data['input_revision'],config=data['config'],summary=data['summary'],source_sha256=data['source_sha256'],execution=execution,limits=data['config']['limits'])
    for name,value in [('layout.json',dict(patterns=data['patterns'],placements=data['placements'],common_prototype_parts=data['common']['parts'],layers=data['layers'],source_sha256=data['source_sha256'])),('coverage.json',cov)]:
        (out/name).write_text(json.dumps(value,indent=2)+'\n')
    with (out/'samples.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['scenario','eta','phi_rad','core_planes']);writer.writeheader();writer.writerows(samples)
    summary['output_sha256']={name:sha(out/name) for name in ('layout.json','coverage.json','samples.csv')}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f"DES038 PROTOTYPE: {data['summary']['carriers']} paired carriers; {data['summary']['tiles']} tiles; {data['summary']['powered_channels']} powered channels; {len(samples)} sampled rays")
    return data,cov


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);export(p.parse_args().output)
