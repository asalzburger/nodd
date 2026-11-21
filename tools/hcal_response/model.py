"""DES046 standalone HCAL; original DES036 interior plus new narrow edge units.

All lengths are mm. Frame rows are local axes expressed in parent coordinates.
No old design evidence is regenerated or relabelled by this scoped model.
"""
import copy
import hashlib
import importlib.util
import json
import math
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_name('config.json')
DESCRIPTOR = 'system:8,side:2,sector:4,layer:6,carrier:12,module:2,sensor:6,x:-1,y:-1,unit:8'
I = [[1,0,0],[0,1,0],[0,0,1]]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def common():
    unit,mat=load('_hcal45_unit','tools/hcal_readout/readout.py').build(absorber=False)
    retained=json.loads((ROOT/'docs/validation/DES-036/budgets.json').read_text())['source_sha256']
    if any(retained.get(k)!=v for k,v in unit['source_sha256'].items()):
        raise ValueError('DES036 physical hardware changed without amendment')
    if len(unit['parts'])!=394 or unit['sensitive_count']!=72:
        raise ValueError('unchanged DES036 unit inventory')
    return unit,mat


@lru_cache(maxsize=1)
def endcap_helpers(): return load('_hcal45_endcap','tools/hcal_endcap/design.py')


def transform(point, origin, frame):
    return [origin[j]+sum(point[i]*frame[i][j] for i in range(3)) for j in range(3)]


def encode(system,side,sector,layer,carrier,module=0,sensor=0,unit=0):
    vals=(system,side,sector,layer,carrier,module,sensor,unit)
    if any(type(v)is not int or not 0<=v<b for v,b in zip(vals,(256,4,16,64,4096,2,36,256))):
        raise ValueError('cell identifier capacity')
    if system not in (13,14) or (system==13 and side!=0) or (system==14 and side not in (1,2)):
        raise ValueError('system and side contract')
    return system | side<<8 | sector<<10 | layer<<14 | carrier<<20 | module<<32 | sensor<<34 | unit<<42


def decode(cell):
    return dict(system=cell&255,side=cell>>8&3,sector=cell>>10&15,layer=cell>>14&63,
                carrier=cell>>20&4095,module=cell>>32&3,sensor=cell>>34&63,x=cell>>40&1,y=cell>>41&1,unit=cell>>42&255)


def validate_config(c):
    b,e=c['barrel'],c['endcap']; u,_=common(); depth=u['fixture']['carrier_size_mm'][2]
    if c['sectors']!=16 or c['layers']!=60 or depth!=12:
        raise ValueError('DES045 frozen 16-sector,60-layer,unchanged12mm carrier contract')
    total=c['layers']*(c['steel_mm']+depth+c['installation_gap_mm'])+c['back_cover_mm']
    if any(not math.isfinite(v) or v<=0 for v in (c['steel_mm'],c['installation_gap_mm'],c['back_cover_mm'])):
        raise ValueError('positive finite stack dimensions')
    if abs(b['outer_apothem_mm']-b['front_apothem_mm']-total)>1e-8 or abs(e['back_abs_z_mm']-e['front_abs_z_mm']-total)>1e-8:
        raise ValueError('stack/envelope closure')
    if b['half_z_mm']>=e['front_abs_z_mm'] or e['outer_apothem_mm']>=b['outer_apothem_mm']:
        raise ValueError('barrel/endcap separation')
    corner=b['outer_apothem_mm']/math.cos(math.pi/c['sectors'])
    allowances=(c['handoff_service_radius_mm'],c['handoff_clearance_mm'])
    if any(not math.isfinite(v) or v<0 for v in allowances):
        raise ValueError('finite nonnegative radial handoff allowances')
    if corner+sum(allowances)>c['radial_handoff_mm']+1e-8:
        raise ValueError('outer corner and service clearance violate radial handoff')
    if min(c['world_half_xyz_mm'][:2])<=corner or c['world_half_xyz_mm'][2]<=e['back_abs_z_mm']:
        raise ValueError('world margin')
    if b['edge_rail_mm']!=2 or b['edge_min_width_mm']!=32 or b['edge_fit_mm']!=.5:
        raise ValueError('DES046 explicit guide/edge cassette contract')
    if len(b['axial_phases_mm'])!=len(b['tangent_phases_mm']) or not b['axial_phases_mm']:
        raise ValueError('barrel phase cycle')
    if any(p%22.5 for p in e['phases_deg']): raise ValueError('endcap phase must preserve polygon')
    return total


def barrel_layout(c):
    u,_=common();b=c['barrel'];w,h,d=u['fixture']['carrier_size_mm'];t=math.tan(math.pi/c['sectors'])
    usable=b['half_z_mm']-b['end_flange_mm']; maxshift=max(abs(v) for v in b['axial_phases_mm'])
    rows=math.floor((2*(usable-maxshift)+b['row_gap_mm'])/(h+b['row_gap_mm']))
    if rows%2==0: rows-=1
    ys=[(i-(rows-1)/2)*(h+b['row_gap_mm']) for i in range(rows)]
    layers=[]; pitch=c['steel_mm']+d+c['installation_gap_mm']
    from edge_units import column_count
    for layer in range(c['layers']):
        front=b['front_apothem_mm']+layer*pitch;cf=front+c['steel_mm']
        hs=cf*t-b['sector_half_seam_mm']-b['edge_rail_mm']
        reserve=b['edge_min_width_mm']+b['edge_fit_mm']+b['tangent_gap_mm']
        cols=math.floor((2*(hs-reserve)+b['tangent_gap_mm'])/(w+b['tangent_gap_mm']))
        xs=[(i-(cols-1)/2)*(w+b['tangent_gap_mm']) for i in range(cols)]
        half=(cols*w+(cols-1)*b['tangent_gap_mm'])/2
        req=b['tangent_phases_mm'][layer%len(b['tangent_phases_mm'])]
        tx=math.copysign(min(abs(req),max(0,hs-half-reserve)),req)
        ay=b['axial_phases_mm'][layer%len(b['axial_phases_mm'])]
        edges=[]
        for side in (-1,1):
            outside=side*(hs-b['edge_fit_mm'])
            inside=tx+side*(half+b['tangent_gap_mm'])
            width=round(abs(outside-inside),9)
            x=(outside+inside)/2
            nc,sp=column_count(width)
            if width<b['edge_min_width_mm']-1e-8:raise ValueError('edge width reservation')
            edges.append(dict(side=side,width_mm=width,center_x_mm=x,columns=nc,tangent_pitch_mm=sp))
        if max(abs(y+ay)+h/2 for y in ys)>usable+1e-8:raise ValueError('barrel axial fit')
        core_area=cols*72*29.7**2+sum(6*q['columns']*(q['tangent_pitch_mm']-.3)*29.7 for q in edges)
        layers.append(dict(layer=layer,steel_front_mm=front,carrier_front_mm=cf,columns_mm=xs,rows_mm=ys,
                           requested_tangent_phase_mm=req,tangent_phase_mm=tx,axial_phase_mm=ay,edges=edges,
                           common_carriers_per_sector=rows*cols,edge_carriers_per_sector=2*rows,
                           carriers_per_sector=rows*(cols+2),full_face_core_fraction=rows*core_area/(4*cf*t*b['half_z_mm'])))
    widths=sorted({q['width_mm'] for layer in layers for q in layer['edges']})
    ids={width:i+1 for i,width in enumerate(widths)}
    for layer in layers:
        for q in layer['edges']:q['unit']=ids[q['width_mm']]
    return layers


def endcap_pattern(c):
    helper=endcap_helpers();u,_=common();e=c['endcap']
    adapted=dict(envelope=dict(sides=c['sectors'],inner_apothem_mm=e['inner_apothem_mm'],outer_apothem_mm=e['outer_apothem_mm'],
                    inner_frame_mm=e['inner_frame_mm'],outer_frame_mm=e['outer_frame_mm']),
                 packing=dict(column_pitch_mm=e['column_pitch_mm'],row_pitch_mm=e['row_pitch_mm'],
                    first_column_x_mm=e['column_pitch_mm']/2,quarter_gap_mm=e['quarter_gap_mm'],
                    collector_gap_mm=e['quarter_gap_mm'],phases_deg=e['phases_deg']))
    # Reuse the exact whole-carrier/SAT packing helper with amended dimensions.
    pattern=helper.make_pattern(adapted)
    if any(not helper.whole_carrier_fits(*p['center_xy_mm'],adapted,u) for p in pattern['carriers']):
        raise ValueError('endcap whole-carrier fit')
    return pattern


def barrel_row_units(layer):
    return ([dict(x=e['center_x_mm'],unit=e['unit']) for e in layer['edges'][:1]]
            +[dict(x=x+layer['tangent_phase_mm'],unit=0) for x in layer['columns_mm']]
            +[dict(x=e['center_x_mm'],unit=e['unit']) for e in layer['edges'][1:]])


def placements(c, barrel=None, endcap=None):
    barrel=barrel if barrel is not None else barrel_layout(c)
    endcap=endcap if endcap is not None else endcap_pattern(c)
    helper=endcap_helpers();pitch=c['steel_mm']+12+c['installation_gap_mm']
    for q in barrel:
        for sector in range(c['sectors']):
            phi=sector*2*math.pi/c['sectors'];f=[[-math.sin(phi),math.cos(phi),0],[0,0,1],[math.cos(phi),math.sin(phi),0]]
            entries=barrel_row_units(q)
            for row,y in enumerate(q['rows_mm']):
                for col,entry in enumerate(entries):
                    cid=row*len(entries)+col
                    origin=transform([entry['x'],y+q['axial_phase_mm'],q['carrier_front_mm']],[0,0,0],f)
                    yield dict(system=13,side=0,sector=sector,layer=q['layer'],carrier=cid,unit=entry['unit'],origin_mm=origin,frame=f,
                               volume_id=encode(13,0,sector,q['layer'],cid,unit=entry['unit']))
    for side in (1,2):
        sign=1 if side==1 else -1
        for layer in range(c['layers']):
            phase=c['endcap']['phases_deg'][layer%len(c['endcap']['phases_deg'])];f=helper.frame_for(phase,side);counters=Counter()
            for q in endcap['carriers']:
                x,y=helper.rotate_xy(q['center_xy_mm'],phase);y*=sign
                sector=helper.sector_of(x,y,c['sectors']);cid=counters[sector];counters[sector]+=1
                yield dict(system=14,side=side,sector=sector,layer=layer,carrier=cid,unit=0,
                           origin_mm=[x,y,sign*(c['endcap']['front_abs_z_mm']+layer*pitch+c['steel_mm'])],frame=f,
                           volume_id=encode(14,side,sector,layer,cid))


def unit_zero():
    u,_=common();unit=copy.deepcopy(u)
    for tile in unit['channel_map']:tile['tile_size_mm']=[29.7,29.7,3]
    unit.update(boards=2,powered_channels=156,active_offset_from_carrier_front_mm=[-168,-87,2],
                active_offset_from_carrier_center_mm=[-168,-87,-4],
                active_volume_names=['HCALBarrelBarrelCarrierCompoundTiles','HCALEndcapsEndcapCarrierCompoundTiles'])
    return unit


@lru_cache(maxsize=256)
def edge_unit(width):
    from edge_units import make
    u,mat=common();source=dict(u,_builder=load('_hcal46_edge_source','tools/hcal_readout/readout.py'))
    return make(width,source,mat)


def regional_materials(c):
    # Exact source polygon/trapezoid capacities. Units carry their own separate ledger.
    b,e=c['barrel'],c['endcap'];t=math.tan(math.pi/c['sectors']);n=c['sectors']
    pitch=c['steel_mm']+12+c['installation_gap_mm'];sampling=c['layers']*pitch
    usable=b['half_z_mm']-b['end_flange_mm'];inset=b['sector_half_seam_mm']+b['edge_rail_mm']
    steel=sum((t*(2*(b['front_apothem_mm']+i*pitch)+c['steel_mm'])-2*inset)*2*usable*c['steel_mm']*n for i in range(c['layers']))
    al=2*b['edge_rail_mm']*2*usable*sampling*n
    back=b['front_apothem_mm']+sampling
    al+=(t*(back+b['outer_apothem_mm'])-2*b['sector_half_seam_mm'])*2*usable*c['back_cover_mm']*n
    al+=(t*(b['front_apothem_mm']+b['outer_apothem_mm'])-2*b['sector_half_seam_mm'])*2*b['end_flange_mm']*(b['outer_apothem_mm']-b['front_apothem_mm'])*n
    helper=endcap_helpers()
    def area(poly):return abs(sum(x*v-y*u for (x,y),(u,v) in zip(poly,poly[1:]+poly[:1])))/2
    inner=e['inner_apothem_mm']+e['inner_frame_mm'];outer=e['outer_apothem_mm']-e['outer_frame_mm']
    steel+=8*c['layers']*c['steel_mm']*(area(helper.quarter_polygon(outer,e['quarter_gap_mm'],n))-area(helper.quarter_polygon(inner,e['quarter_gap_mm'],n)))
    factor=n*t
    al+=2*sampling*factor*(inner**2-e['inner_apothem_mm']**2+e['outer_apothem_mm']**2-outer**2)
    al+=2*c['back_cover_mm']*factor*(e['outer_apothem_mm']**2-e['inner_apothem_mm']**2)
    return dict(Steel235=dict(volume_mm3=steel,mass_g=steel*7.85/1000),Aluminium=dict(volume_mm3=al,mass_g=al*2.7/1000))


def build(config=None):
    c=copy.deepcopy(config if config is not None else json.loads(CONFIG.read_text()));total=validate_config(c)
    u,_=common();b=barrel_layout(c);e=endcap_pattern(c)
    bc=c['sectors']*sum(v['common_carriers_per_sector'] for v in b)
    edgec=c['sectors']*sum(v['edge_carriers_per_sector'] for v in b);ec=2*c['layers']*len(e['carriers'])
    units={'0':unit_zero()};multiplicity=Counter({'0':bc+ec})
    for layer in b:
        for q in layer['edges']:
            key=str(q['unit'])
            if key not in units:
                units[key]=copy.deepcopy(edge_unit(q['width_mm']))
                units[key]['active_volume_names']=[f'HCALBarrelBarrelEdgeU{key}CompoundTiles']
            multiplicity[key]+=c['sectors']*len(layer['rows_mm'])
    tiles=sum(multiplicity[k]*v['sensitive_count'] for k,v in units.items());count=sum(multiplicity.values())
    materials=regional_materials(c)
    for key,unit in units.items():
        for name,values in unit['material_totals'].items():
            target=materials.setdefault(name,dict(volume_mm3=0.,mass_g=0.))
            for field in target:target[field]+=multiplicity[key]*values[field]
    heat=[]
    for scenario in range(3):
        heat.append(dict(current_A_per_device=[.000002,.0001,.001][scenario],
                         local_input_heat_W=sum(multiplicity[k]*v['budgets']['power_scenarios'][scenario]['total_heat_W'] for k,v in units.items()),
                         ideal_water_g_s=sum(multiplicity[k]*v['budgets']['power_scenarios'][scenario]['ideal_water_g_s'] for k,v in units.items())))
    source={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),CONFIG,ROOT/'tools/hcal_response/edge_units.py',ROOT/'tools/hcal_endcap/design.py',ROOT/'docs/validation/DES-036/budgets.json')}
    source.update(u['source_sha256'])
    return dict(schema_version=2,status='DRAFT / PROTOTYPE; DES046',config=c,id_descriptor=DESCRIPTOR,
                sensitive_tiles=tiles,sensitive_tiles_by_system={'13':tiles-ec*72,'14':ec*72},units=units,
                unit_multiplicity=dict(multiplicity),material_totals=materials,local_service_budgets=heat,
                counts=dict(barrel_common_carriers=bc,barrel_edge_carriers=edgec,barrel_carriers=bc+edgec,endcap_carriers=ec,carriers=count,
                            boards=sum(multiplicity[k]*v['boards'] for k,v in units.items()),sensitive_tiles=tiles,
                            powered_channels=sum(multiplicity[k]*v['powered_channels'] for k,v in units.items()),
                            physical_parts_per_unit={k:len(v['parts']) for k,v in units.items()}),
                depth=dict(total_mm=total,steel_mm=c['layers']*c['steel_mm'],pure_iron_nuclear_lambda=c['layers']*c['steel_mm']/167.7,
                           pure_iron_pion_lambda=c['layers']*c['steel_mm']/204.1,
                           qualification='elemental screening; native Steel235 directional paths are separate'),
                barrel_layers=b,endcap_pattern=e,unit_tile_map=u['channel_map'],unit_material_totals=u['material_totals'],
                unit_source_sha256=u['source_sha256'],source_sha256=source,
                edge_coverage=dict(core_plane_inactive_half_strip_mm=1+2+.5+3.15+2*math.tan(math.pi/16),
                                   rear_taper_shadow_mm=12*math.tan(math.pi/16),qualification='per-side local tangent distances; exact seam remains'),
                endcap_rotational_symmetry='fourfold carrier/quarter packing; 16-sector angular addresses do not establish 16fold response',
                limits=['No optical statistics,SiPM saturation,noise,threshold,time-window or calibrated reconstruction',
                        'External collectors/cables,frame penetrations,plant,mounts and magnetic loads absent;2mm guide is not qualified plate support',
                        'Standalone air context excludes ECAL,tracker,beam pipe,magnet,FCAL and magnetic field'])
