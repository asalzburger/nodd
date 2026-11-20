"""DES045 standalone HCAL; unchanged physical DES036 module, new regional fit.

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
DESCRIPTOR = 'system:8,side:2,sector:4,layer:6,carrier:12,module:2,sensor:6,x:-1,y:-1'
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


def encode(system,side,sector,layer,carrier,module=0,sensor=0):
    vals=(system,side,sector,layer,carrier,module,sensor)
    if any(type(v)is not int or not 0<=v<b for v,b in zip(vals,(256,4,16,64,4096,2,36))):
        raise ValueError('cell identifier capacity')
    if system not in (13,14) or (system==13 and side!=0) or (system==14 and side not in (1,2)):
        raise ValueError('system and side contract')
    return system | side<<8 | sector<<10 | layer<<14 | carrier<<20 | module<<32 | sensor<<34


def decode(cell):
    return dict(system=cell&255,side=cell>>8&3,sector=cell>>10&15,layer=cell>>14&63,
                carrier=cell>>20&4095,module=cell>>32&3,sensor=cell>>34&63,x=cell>>40&1,y=cell>>41&1)


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
    layers=[]
    pitch=c['steel_mm']+d+c['installation_gap_mm']
    for layer in range(c['layers']):
        front=b['front_apothem_mm']+layer*pitch; cf=front+c['steel_mm'];hs=cf*t-b['sector_half_seam_mm']-b['edge_rail_mm']
        cols=math.floor((2*hs+b['tangent_gap_mm'])/(w+b['tangent_gap_mm']))
        xs=[(i-(cols-1)/2)*(w+b['tangent_gap_mm']) for i in range(cols)]
        req=b['tangent_phases_mm'][layer%len(b['tangent_phases_mm'])]
        margin=hs-max(abs(x)+w/2 for x in xs)
        tx=math.copysign(min(abs(req),max(0,margin-1)),req);ay=b['axial_phases_mm'][layer%len(b['axial_phases_mm'])]
        if max(abs(x+tx)+w/2 for x in xs)>hs+1e-8 or max(abs(y+ay)+h/2 for y in ys)>usable+1e-8:
            raise ValueError('barrel whole-carrier fit')
        layers.append(dict(layer=layer,steel_front_mm=front,carrier_front_mm=cf,columns_mm=xs,rows_mm=ys,
                           tangent_phase_mm=tx,axial_phase_mm=ay,carriers_per_sector=rows*cols,
                           full_face_core_fraction=rows*cols*72*29.7**2/(4*cf*t*b['half_z_mm'])))
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


def placements(c, barrel=None, endcap=None):
    barrel=barrel if barrel is not None else barrel_layout(c)
    endcap=endcap if endcap is not None else endcap_pattern(c)
    helper=endcap_helpers();pitch=c['steel_mm']+12+c['installation_gap_mm']
    for q in barrel:
        for sector in range(c['sectors']):
            phi=sector*2*math.pi/c['sectors'];f=[[-math.sin(phi),math.cos(phi),0],[0,0,1],[math.cos(phi),math.sin(phi),0]]
            for row,y in enumerate(q['rows_mm']):
                for col,x in enumerate(q['columns_mm']):
                    cid=row*len(q['columns_mm'])+col
                    origin=transform([x+q['tangent_phase_mm'],y+q['axial_phase_mm'],q['carrier_front_mm']],[0,0,0],f)
                    yield dict(system=13,side=0,sector=sector,layer=q['layer'],carrier=cid,origin_mm=origin,frame=f,
                               volume_id=encode(13,0,sector,q['layer'],cid))
    for side in (1,2):
        sign=1 if side==1 else -1
        for layer in range(c['layers']):
            phase=c['endcap']['phases_deg'][layer%len(c['endcap']['phases_deg'])];f=helper.frame_for(phase,side);counters=Counter()
            for q in endcap['carriers']:
                x,y=helper.rotate_xy(q['center_xy_mm'],phase);y*=sign
                sector=helper.sector_of(x,y,c['sectors']);cid=counters[sector];counters[sector]+=1
                yield dict(system=14,side=side,sector=sector,layer=layer,carrier=cid,
                           origin_mm=[x,y,sign*(c['endcap']['front_abs_z_mm']+layer*pitch+c['steel_mm'])],frame=f,
                           volume_id=encode(14,side,sector,layer,cid))


def build(config=None):
    c=copy.deepcopy(config if config is not None else json.loads(CONFIG.read_text()));total=validate_config(c)
    u,_=common();b=barrel_layout(c);e=endcap_pattern(c)
    bc=c['sectors']*sum(v['carriers_per_sector'] for v in b);ec=2*c['layers']*len(e['carriers']);count=bc+ec
    source={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),CONFIG,ROOT/'tools/hcal_endcap/design.py',ROOT/'docs/validation/DES-036/budgets.json')}
    source.update(u['source_sha256'])
    return dict(schema_version=1,status='DRAFT / PROTOTYPE; DES045',config=c,id_descriptor=DESCRIPTOR,
                sensitive_tiles=72*count,sensitive_tiles_by_system={'13':bc*72,'14':ec*72},
                counts=dict(barrel_carriers=bc,endcap_carriers=ec,carriers=count,boards=2*count,
                            sensitive_tiles=72*count,powered_channels=156*count,physical_parts_per_carrier=394),
                depth=dict(total_mm=total,steel_mm=c['layers']*c['steel_mm'],pure_iron_nuclear_lambda=c['layers']*c['steel_mm']/167.7,
                           pure_iron_pion_lambda=c['layers']*c['steel_mm']/204.1,
                           qualification='elemental screening; native Steel235 directional paths are separate'),
                barrel_layers=b,endcap_pattern=e,unit_tile_map=u['channel_map'],unit_material_totals=u['material_totals'],
                unit_source_sha256=u['source_sha256'],source_sha256=source,
                endcap_rotational_symmetry='fourfold carrier/quarter packing; 16-sector angular addresses do not establish 16fold response',
                limits=['No optical statistics,SiPM saturation,noise,threshold,time-window or calibrated reconstruction',
                        'External collectors/cables,frame penetrations,plant,mounts and magnetic loads absent',
                        'Standalone vacuum/air context excludes ECAL,tracker,beam pipe,magnet,FCAL and magnetic field'])
