"""DES036 isolated common module. mm, g, W; standard library only.

Frames are local basis vectors expressed in the carrier frame (row vectors).
Only axis-aligned boxes/cylinders and contained disjoint cuts are supported.
The restricted analytic CSG contract is independently checkable in DD4hep.
"""
import copy
import hashlib
import importlib.util
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_name('config.json')
I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
TUBE_Y = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]
EPS = 1e-8
ID_DESCRIPTOR = 'system:8,side:2,sector:4,layer:6,carrier:12,module:2,sensor:6,x:-1,y:-1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def materials(c):
    # Use a unique module name; never import the legacy calorimeter `model`.
    spec = importlib.util.spec_from_file_location('_hcal_bulk_materials', ROOT / 'tools/pixel_barrel_dd4hep/materials.py')
    bulk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bulk)
    m = bulk.Materials(dict(coolant_density_g_cm3=1, cfrp_carbon_mass_fraction=.7,
                            module=dict(flex_copper_coverage=.5)),
                       dict(density_g_cm3=c['stock_densities_g_cm3']))
    m.add('Aluminium', 2.7, {'Al': 1})
    m.add('Water', 1, {'H': 2, 'O': 1}, atoms=True)
    m.add('Steel235', 7.85, c['steel_mass_fractions'])
    m.add('Quartz', 2.2, {'Si': 1, 'O': 2}, atoms=True)
    m.add('G10', 1.7, {'Cl': .08, 'Quartz': .773, 'Epoxy': .147})
    m.add('PSHost', 1.06, {'C': 8, 'H': 8}, atoms=True)
    m.add('PET', 1.4, {'C': 10, 'H': 8, 'O': 4}, atoms=True)
    for name, fractions in c['package_volume_fractions'].items():
        if any(v <= 0 for v in fractions.values()) or not math.isclose(sum(fractions.values()), 1, abs_tol=1e-12):
            raise ValueError('package volume fractions must sum to one')
        m.effective(name, fractions, 1)
    return m


def capacity(kind, dims):
    if any(not math.isfinite(v) for v in dims.values()):
        raise ValueError('nonfinite shape')
    if kind == 'box' and set(dims) == {'sx', 'sy', 'sz'} and all(v > 0 for v in dims.values()):
        return math.prod(dims.values())
    if kind == 'tube' and set(dims) == {'rmin', 'rmax', 'length'} and 0 <= dims['rmin'] < dims['rmax'] and dims['length'] > 0:
        return math.pi * (dims['rmax'] ** 2 - dims['rmin'] ** 2) * dims['length']
    raise ValueError('invalid or unsupported primitive')


def extent(kind, d):
    capacity(kind, d)
    return [d[k] / 2 for k in ('sx', 'sy', 'sz')] if kind == 'box' else [d['rmax'], d['rmax'], d['length'] / 2]


def validate_frame(frame):
    if len(frame) != 3 or any(len(row) != 3 for row in frame):
        raise ValueError('frame dimension')
    if any(v not in (-1, 0, 1) for row in frame for v in row) or any(sum(abs(v) for v in row) != 1 for row in frame) or any(sum(abs(frame[i][j]) for i in range(3)) != 1 for j in range(3)):
        raise ValueError('only axis-aligned orthonormal frames supported')
    a, b, z = frame
    if [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]] != z:
        raise ValueError('frame must be right handed')


def bounds(p):
    if len(p['center_mm']) != 3 or any(not math.isfinite(v) for v in p['center_mm']):
        raise ValueError('nonfinite/invalid physical centre')
    frame = p['frame']; validate_frame(frame)
    ex = extent(p.get('shape_kind', p.get('kind')), p['dimensions_mm'])
    e = [sum(abs(frame[i][j]) * ex[i] for i in range(3)) for j in range(3)]
    return [(v-a, v+a) for v, a in zip(p['center_mm'], e)]


def tube_axis(p):
    return next(j for j, v in enumerate(p['frame'][2]) if v)


def primitive_overlap(a, b):
    """Exact positive-volume overlap for this fixture's primitive families."""
    aa, bb = bounds(a), bounds(b)
    if any(min(x[1], y[1]) - max(x[0], y[0]) <= EPS for x, y in zip(aa, bb)):
        return False
    ka, kb = a.get('shape_kind', a.get('kind')), b.get('shape_kind', b.get('kind'))
    if ka == kb == 'box':
        return True
    if ka == 'box':
        return primitive_overlap(b, a)
    axis = tube_axis(a); radial = [j for j in range(3) if j != axis]
    if kb == 'tube':
        if tube_axis(b) != axis or any(abs(a['center_mm'][j]-b['center_mm'][j]) > EPS for j in radial):
            raise ValueError('unsupported noncoaxial cylinder pair')
        da, db = a['dimensions_mm'], b['dimensions_mm']
        return min(da['rmax'], db['rmax']) - max(da['rmin'], db['rmin']) > EPS
    d = a['dimensions_mm']; lo2 = hi2 = 0
    for j in radial:
        low, high = (bb[j][0]-a['center_mm'][j], bb[j][1]-a['center_mm'][j])
        lo2 += (0 if low <= 0 <= high else min(abs(low), abs(high)))**2
        hi2 += max(abs(low), abs(high))**2
    return lo2 < d['rmax']**2-EPS and hi2 > d['rmin']**2+EPS


def primitive_inside_box_region(region, cut, other=None):
    """Whether an intersection box (or its coaxial cylindrical subset) is cut."""
    cb = bounds(cut)
    if any(a < c-EPS or b > d+EPS for (a,b),(c,d) in zip(region, cb)):
        # A long cylinder can intersect a shorter cutter, so only compare the
        # clipped intersection region, never the original other's full length.
        return False
    if cut['kind'] == 'box':
        return True
    axis = tube_axis(cut); radial = [j for j in range(3) if j != axis]
    cd = cut['dimensions_mm']
    if cd['rmin'] != 0:
        raise ValueError('annular cutter unsupported')
    if other is not None and other.get('shape_kind') == 'tube' and tube_axis(other) == axis:
        if all(abs(other['center_mm'][j]-cut['center_mm'][j]) <= EPS for j in radial) and other['dimensions_mm']['rmax'] <= cd['rmax']+EPS:
            return True
    return sum(max(abs(region[j][0]-cut['center_mm'][j]), abs(region[j][1]-cut['center_mm'][j]))**2 for j in radial) <= cd['rmax']**2+EPS


def global_cut(part, cut):
    # Both input frames use local-basis rows.
    f = part['frame']; q = copy.deepcopy(cut)
    q['center_mm'] = [part['center_mm'][j] + sum(cut['center_mm'][i]*f[i][j] for i in range(3)) for j in range(3)]
    q['frame'] = [[sum(cut['frame'][k][i]*f[i][j] for i in range(3)) for j in range(3)] for k in range(3)]
    return q


def parts_overlap(a, b):
    if not primitive_overlap(a, b):
        return False
    region = [(max(x[0], y[0]), min(x[1], y[1])) for x,y in zip(bounds(a), bounds(b))]
    ac = [global_cut(a, q) for q in a['cuts']]; bc = [global_cut(b, q) for q in b['cuts']]
    splits = []
    for j, (lo, hi) in enumerate(region):
        points = sorted({lo, hi} | {v for q in ac+bc for v in bounds(q)[j] if lo+EPS < v < hi-EPS})
        splits.append(list(zip(points, points[1:])))
    for sub in itertools.product(*splits):
        proxy = dict(shape_kind='box', frame=I, center_mm=[sum(v)/2 for v in sub], dimensions_mm=dict(zip(('sx','sy','sz'), (v[1]-v[0] for v in sub))))
        if not primitive_overlap(a, proxy) or not primitive_overlap(b, proxy):
            continue
        if any(primitive_inside_box_region(sub, q, b) for q in ac) or any(primitive_inside_box_region(sub, q, a) for q in bc):
            continue
        return True
    return False


def validate_cuts(kind, dims, cuts):
    parent = dict(kind=kind, dimensions_mm=dims, center_mm=[0,0,0], frame=I)
    pb = bounds(parent)
    for cut in cuts:
        cb = bounds(cut)
        if kind != 'box' or any(c < a-EPS or d > b+EPS for (c,d),(a,b) in zip(cb,pb)):
            raise ValueError('cutter not contained in box')
        if cut['kind'] == 'tube' and cut['dimensions_mm']['rmin'] != 0:
            raise ValueError('annular cutter unsupported')
    for i, a in enumerate(cuts):
        for b in cuts[i+1:]:
            if primitive_overlap(a,b):
                raise ValueError('cutters overlap')


def cut(kind, dims, centre=(0,0,0), frame=I):
    return dict(kind=kind, dimensions_mm=dims, center_mm=list(centre), frame=copy.deepcopy(frame))


def box_dims(size):
    return dict(zip(('sx','sy','sz'), size))


def tube_dims(r, length, rmin=0):
    return dict(rmin=rmin, rmax=r, length=length)


class Inventory:
    def __init__(self, m): self.parts=[]; self.m=m

    def add(self, name, role, material, centre, kind, dims, owner='carrier', cuts=None, frame=I, module=None, sensor=None):
        cuts = copy.deepcopy(cuts or [])
        validate_cuts(kind, dims, cuts)
        v = capacity(kind,dims)-sum(capacity(q['kind'],q['dimensions_mm']) for q in cuts)
        if v <= 0: raise ValueError('nonpositive exclusive capacity')
        p = dict(name=name, role=role, owner=owner, material=material, center_mm=list(centre), frame=copy.deepcopy(frame), shape_kind=kind, dimensions_mm=dims, cuts=cuts, volume_mm3=v, mass_g=v*self.m.recipes[material]['density_g_cm3']/1000)
        if module is not None: p['module']=module
        if sensor is not None: p['sensor']=sensor
        self.parts.append(p)
        return p

    def box(self, name, role, material, centre, size, **kw):
        return self.add(name, role, material, centre, 'box', box_dims(size), **kw)


def validate_config(c):
    m,e,s,k = (c[n] for n in ('module','electronics','services','contract'))
    if k['collision_energy_TeV'] != 14 or k['continuous_duty'] != 1:
        raise ValueError('14 TeV continuous contract; no hidden duty factor')
    if m['rows'] != 6 or len(c['carrier']['board_centres_xy_mm']) != 2 or e['chips_per_module'] != 1:
        raise ValueError('common 6x6 board/two-board carrier contract')
    if e['ordinary_channels'] != 72 or e['powered_channels'] != 78 or Counter(e['auxiliary_roles']) != {'calibration':2,'common_mode':4}:
        raise ValueError('ordinary/auxiliary/powered channel ownership')
    if not 0 < m['pcb_copper_equivalent_mm'] < m['pcb_size_mm'][2] or not 0 < e['payload_fraction'] <= 1 or not 0 < s['converter_efficiency'] <= 1:
        raise ValueError('normalized board/link/converter budget')
    if m['tile_size_mm'][0]+2*m['wrap_mm'] >= m['tile_pitch_mm'] or m['tile_size_mm'][1]+2*m['wrap_mm'] >= m['tile_pitch_mm']:
        raise ValueError('wrapped tile pitch clearance')
    if not m['sipm_nominal_height_mm']-m['sipm_height_tolerance_mm']-EPS <= m['sipm_size_mm'][2] <= m['sipm_nominal_height_mm']+m['sipm_height_tolerance_mm']+EPS:
        raise ValueError('SiPM height outside sourced tolerance')
    if not math.isclose(m['sipm_z_mm']+m['sipm_size_mm'][2]/2,m['sipm_back_mm'],abs_tol=EPS):
        raise ValueError('SiPM back must stay anchored to solder contact')
    if not 0 < m['recess_depth_mm'] < m['tile_size_mm'][2] or not math.isclose(m['sipm_y_offset_mm']+m['optical_centre_y_offset_mm'],0,abs_tol=EPS):
        raise ValueError('recess/optical-centre contract')
    positive = [k['sample_ns'],k['latency_us'],k['accepted_Hz'],k['stress_Hz'],e['W_per_powered_channel'],e['support_W_per_module'],e['shared_interface_W'],e['latency_samples'],e['output_fifo_entries'],e['DAQ_lanes_per_chip'],e['trigger_lanes_per_chip'],e['lane_Gbps'],e['bits_per_channel'],e['header_bits_per_chip'],s['LV_V'],s['bias_V'],s['nominal_current_A_per_device'],s['water_rise_K'],s['water_cp_J_kg_K']]+s['stress_current_A_per_device']
    if any(not math.isfinite(v) or v <= 0 for v in positive): raise ValueError('positive finite operating budgets')
    if e['latency_samples']*k['sample_ns'] < k['latency_us']*1000:
        raise ValueError('inadequate latency capacity')
    ca=c['carrier']
    if not 0 < ca['skin_mm'] or not 0 < ca['rear_insulation_mm'] or ca['size_mm'][2] <= 2*ca['skin_mm']+ca['rear_insulation_mm']:
        raise ValueError('carrier skin/insulation/depth budget')
    if c['carrier']['tube_inner_radius_mm'] >= c['carrier']['tube_outer_radius_mm']:
        raise ValueError('tube wall must be positive')


def add_pcb(inv, name, centre_xy, size, front, copper, owner, module=None):
    x,y=centre_xy; sx,sy,thick=size; substrate=thick-copper
    inv.box(name+'_G10','pcb','G10',[x,y,front+substrate/2],[sx,sy,substrate],owner=owner,module=module)
    inv.box(name+'_Cu','pcb','Copper',[x,y,front+substrate+copper/2],[sx,sy,copper],owner=owner,module=module)


def add_chip_stack(inv, name, centre_xy, c, owner, module=None, interface=False):
    x,y=centre_xy; m=c['module']; sx,sy,t=m['asic_size_mm']; z=m['asic_z_mm']; front=z-t/2
    for suffix,role,material,z0,d in [('bond','bond','Epoxy',front-m['adhesive_mm'],m['adhesive_mm']),('chip','shared_interface' if interface else 'frontend','HCalFrontendProxy',front,t),('contact','thermal_contact','Graphite',front+t,m['graphite_mm']),('post','thermal_post','Aluminium',front+t+m['graphite_mm'],m['post_mm'])]:
        inv.box(name+'_'+suffix,role,material,[x,y,z0+d/2],[sx,sy,d],owner=owner,module=module)


def budgets(c):
    e,s,k=c['electronics'],c['services'],c['contract']; chips=2; tiles=72
    front=chips*e['powered_channels']*e['W_per_powered_channel']; support=2*e['support_W_per_module']; interface=e['shared_interface_W']
    lv=(front+support+interface)/s['converter_efficiency']; bits=e['powered_channels']*e['bits_per_channel']+e['header_bits_per_chip']; perchip=e['DAQ_lanes_per_chip']*e['lane_Gbps']*1e9*e['payload_fraction']
    power=[]
    for current in [s['nominal_current_A_per_device']]+s['stress_current_A_per_device']:
        bias=tiles*s['bias_V']*current; heat=lv+bias
        power.append(dict(current_A_per_device=current,LV_input_W=lv,LV_input_A=lv/s['LV_V'],bias_W=bias,bias_current_A=tiles*current,total_heat_W=heat,ideal_water_g_s=1000*heat/(s['water_cp_J_kg_K']*s['water_rise_K'])))
    daq=[]
    for rate in (k['accepted_Hz'],k['stress_Hz']):
        demand=bits*rate; util=demand/perchip
        daq.append(dict(accepted_Hz=rate,event_bits_per_chip=bits,per_chip_demand_bps=demand,per_chip_payload_capacity_bps=perchip,carrier_demand_bps=chips*demand,carrier_payload_capacity_bps=chips*perchip,utilization=util,status='OVERLOAD' if util>1 else 'BELOW_ARITHMETIC_CAPACITY',qualification='budget screen only; no queue/dead-time or protocol certification'))
    return dict(duty=1,powered_channels=156,connected_tiles=tiles,frontend_W=front,support_W=support,shared_interface_W=interface,LV_delivered_W=front+support+interface,conversion_loss_W=lv-front-support-interface,power_scenarios=power,separate_interface_comparison=dict(two_interfaces_LV_input_W=(front+support+2*interface)/s['converter_efficiency'],shared_LV_input_W=lv,LV_input_saving_W=interface/s['converter_efficiency'],note='same two boards; exactly one interface owned and budgeted by carrier'),daq=daq,trigger=dict(lanes_per_chip=e['trigger_lanes_per_chip'],raw_bps_per_chip=e['trigger_lanes_per_chip']*e['lane_Gbps']*1e9,note='separate trigger allocation; no DAQ reuse'),latency=dict(samples=e['latency_samples'],span_us=e['latency_samples']*k['sample_ns']/1000,requested_us=k['latency_us'],ideal_margin_samples=e['latency_samples']-k['latency_us']*1000/k['sample_ns'],output_fifo_entries=e['output_fifo_entries'],note='arithmetic capacity only; not timing closure or queue qualification'))


def service_graph(c, handoffs):
    """Functional connectivity only: separate logical DAQ/trigger endpoints.

    Trace/connector routing, lane fan-in, serialization and concentrator protocol
    are deliberately unqualified. A shared data envelope carries both budgets.
    """
    e=c['electronics']; links=[]
    for mid in (0,1):
        prefix=f'm{mid}'
        links.extend([
            dict(source=prefix+'_sipm_inputs',target=prefix+'_frontend',kind='analogue_tile_inputs',channels=36,role='ordinary',implementation='functional proxy; traces omitted'),
            dict(source=prefix+'_frontend_DAQ',target='carrier_interface_DAQ',kind='DAQ',lanes=e['DAQ_lanes_per_chip'],raw_bps=e['DAQ_lanes_per_chip']*e['lane_Gbps']*1e9),
            dict(source=prefix+'_frontend_trigger',target='carrier_interface_trigger',kind='trigger',lanes=e['trigger_lanes_per_chip'],raw_bps=e['trigger_lanes_per_chip']*e['lane_Gbps']*1e9),
            dict(source='carrier_connector_LV',target=prefix+'_frontend_and_support',kind='LV',voltage_V=c['services']['LV_V'],implementation='regulator/support proxy; traces omitted'),
            dict(source='carrier_connector_bias',target=prefix+'_sipm_inputs',kind='bias',voltage_V=c['services']['bias_V'],devices=36,implementation='bias trim/regulation unselected'),
            dict(source='carrier_interface_control',target=prefix+'_LED_driver_support_proxy',kind='calibration_control',devices=36,implementation='direct-front LED envelopes; driver/optics not emulated')])
    links.extend([
        dict(source='carrier_interface_DAQ',target='carrier_connector_data_DAQ',kind='DAQ',lanes=2*e['DAQ_lanes_per_chip'],raw_bps=2*e['DAQ_lanes_per_chip']*e['lane_Gbps']*1e9),
        dict(source='carrier_interface_trigger',target='carrier_connector_data_trigger',kind='trigger',lanes=2*e['trigger_lanes_per_chip'],raw_bps=2*e['trigger_lanes_per_chip']*e['lane_Gbps']*1e9),
        dict(source='carrier_connector_control',target='carrier_interface_control',kind='control',implementation='protocol unselected'),
        dict(source='carrier_connector_LV',target='carrier_interface',kind='LV',voltage_V=c['services']['LV_V'],implementation='single shared interface and converter loss allocation')])
    connectors=[dict(name='carrier_connector_'+role,role=role,external_owner='cable/collector design pending') for role in ('LV','bias','data','control')]
    connectors[2].update(logical_endpoints=['carrier_connector_data_DAQ','carrier_connector_data_trigger'],DAQ_lanes=2*e['DAQ_lanes_per_chip'],trigger_lanes=2*e['trigger_lanes_per_chip'],note='combined data connector envelope; DAQ/trigger lane budgets separate; pinout and fan-in unqualified')
    return dict(cooling_handoffs=handoffs,connectors=connectors,links=links,qualification='geometric handoffs, functional proxy connections and ideal budgets only')


def build(config=None, absorber=True):
    c=copy.deepcopy(config if config is not None else json.loads(CONFIG.read_text()))
    validate_config(c); mat=materials(c); inv=Inventory(mat); m=c['module']; ca=c['carrier']; channel_map=[]; modules=[]
    for mid,(cx,cy) in enumerate(ca['board_centres_xy_mm']):
        owner=f'module:{mid}'; prefix=f'm{mid}'
        for sid in range(m['rows']**2):
            x=cx+(sid%m['rows']-(m['rows']-1)/2)*m['tile_pitch_mm']; y=cy+(sid//m['rows']-(m['rows']-1)/2)*m['tile_pitch_mm']; z=m['tile_z_mm']; sx,sy,t=m['tile_size_mm']; w=m['wrap_mm']; r=m['recess_radius_mm']; depth=m['recess_depth_mm']
            inv.box(f'{prefix}_t{sid}_active','sensitive','PSHost',[x,y,z],[sx,sy,t],owner=owner,module=mid,sensor=sid,cuts=[cut('tube',tube_dims(r,depth),[0,0,(t-depth)/2])])
            inv.box(f'{prefix}_t{sid}_reflector','reflector','PET',[x,y,z],[sx+2*w,sy+2*w,t+2*w],owner=owner,module=mid,cuts=[cut('box',box_dims([sx,sy,t])),cut('tube',tube_dims(r,w),[0,0,(t+w)/2])])
            sipm_xyz=[x,y+m['sipm_y_offset_mm'],m['sipm_z_mm']]
            inv.box(f'{prefix}_t{sid}_sipm','sipm','HCalSiPMProxy',sipm_xyz,m['sipm_size_mm'],owner=owner,module=mid)
            solder_z=m['sipm_z_mm']+m['sipm_size_mm'][2]/2+m['solder_mm']/2
            inv.box(f'{prefix}_t{sid}_solder','solder_copper_equivalent','Copper',[x,sipm_xyz[1],solder_z],m['sipm_size_mm'][:2]+[m['solder_mm']],owner=owner,module=mid)
            led=m['led_offset_xyz_mm']
            inv.box(f'{prefix}_t{sid}_led','direct_calibration_led','HCalLEDProxy',[x+led[0],y+led[1],led[2]],m['led_size_mm'],owner=owner,module=mid)
            channel_map.append(dict(module=mid,sensor=sid,chip=mid,channel=sid,channel_role='ordinary',tile_center_mm=[x,y,z],sipm_package_center_mm=sipm_xyz,optical_center_mm=[x,sipm_xyz[1]+m['optical_centre_y_offset_mm'],m['sipm_z_mm']],led_center_mm=[x+led[0],y+led[1],led[2]],local_cell_xy=[0,0],volume_id=(9 | mid << 32 | sid << 34),physical_name=f'{prefix}_t{sid}_active'))
        add_pcb(inv,prefix+'_pcb',[cx,cy],m['pcb_size_mm'],m['pcb_front_mm'],m['pcb_copper_equivalent_mm'],owner,mid)
        add_chip_stack(inv,prefix,[cx,cy],c,owner,mid)
        modules.append(dict(module=mid,centre_xy_mm=[cx,cy],tiles=36,chip=mid,powered_channels=78,ordinary_channels=72,connected_channels=list(range(36)),unused_ordinary_channels=list(range(36,72)),auxiliary_channels=[dict(channel=72+i,role=role) for i,role in enumerate(c['electronics']['auxiliary_roles'])],connection_model='functional proxy only; no ASIC emulation',support_electronics_W=c['electronics']['support_W_per_module'],support_electronics_representation='material allowance in frontend package proxy; no additional physical duplicate'))
    width,height,depth=ca['size_mm']; rail=ca['rail_mm']
    skin=ca['skin_mm']; insulation=ca['rear_insulation_mm']; rail_z=depth/2; rail_depth=depth-2*skin
    inv.box('carrier_front_skin','front_skin','Aluminium',[0,0,skin/2],[width,height,skin])
    inv.box('carrier_rear_skin','rear_skin','Aluminium',[0,0,depth-skin/2],[width,height,skin])
    inv.box('carrier_insulation','rear_insulation','Polyimide',[0,0,depth-skin-insulation/2],[width-2*rail,height-2*rail,insulation])
    plate_cuts=[cut('tube',tube_dims(ca['tube_outer_radius_mm'],ca['plate_size_mm'][1]),[x,0,ca['tube_z_mm']-ca['plate_z_mm']],TUBE_Y) for x in ca['tube_x_mm']]
    inv.box('carrier_cold_plate','cold_plate','Copper',[0,0,ca['plate_z_mm']],ca['plate_size_mm'],cuts=plate_cuts)
    for sign in (-1,1):
        inv.box(f'carrier_xrail{sign}','side_rail','Aluminium',[sign*(width-rail)/2,0,rail_z],[rail,height,rail_depth])
        ports=[cut('box',box_dims([ca['port_size_mm'],rail,ca['port_size_mm']]),[x,0,ca['tube_z_mm']-rail_z]) for x in ca['tube_x_mm']]
        inv.box(f'carrier_yrail{sign}','ported_rail','Aluminium',[0,sign*(height-rail)/2,rail_z],[width-2*rail,rail,rail_depth],cuts=ports)
    handoffs=[]
    for branch,x in enumerate(ca['tube_x_mm']):
        inv.add(f'carrier_tube{branch}','cooling_tube','Titanium',[x,0,ca['tube_z_mm']],'tube',tube_dims(ca['tube_outer_radius_mm'],ca['tube_length_mm'],ca['tube_inner_radius_mm']),frame=TUBE_Y)
        inv.add(f'carrier_water{branch}','coolant','Water',[x,0,ca['tube_z_mm']],'tube',tube_dims(ca['tube_inner_radius_mm'],ca['tube_length_mm']),frame=TUBE_Y)
        for sign in (-1,1): handoffs.append(dict(name=f'branch{branch}_{"inlet" if sign<0 else "outlet"}',branch=branch,centre_mm=[x,sign*height/2,ca['tube_z_mm']],direction=[0,sign,0],outer_radius_mm=ca['tube_outer_radius_mm'],external_owner='collector design pending',flow_role='inlet' if sign<0 else 'outlet'))
    add_pcb(inv,'carrier_service_pcb',ca['service_board_xy_mm'],ca['service_board_size_mm'],m['pcb_front_mm'],m['pcb_copper_equivalent_mm'],'carrier')
    add_chip_stack(inv,'carrier_interface',ca['service_board_xy_mm'],c,'carrier',interface=True)
    for x,role in zip(ca['connector_x_mm'],('LV','bias','data','control')):
        inv.box(f'carrier_connector_{role}','connector_'+role,'HCalConnectorProxy',[x]+ca['connector_yz_mm'],ca['connector_size_mm'])
    if absorber: inv.box('sector_reference_absorber','absorber_reference','Steel235',[0,0,-ca['absorber_mm']/2],[width,height,ca['absorber_mm']],owner='sector')
    totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    for p in inv.parts:
        for key in ('volume_mm3','mass_g'): totals[p['material']][key]+=p[key]
    report=dict(schema_version=1,status='PROTOTYPE / DRAFT',input_revision=c['input_revision'],config=c,frame_convention='rows are local basis vectors expressed in carrier coordinates; centre and all lengths in mm',system_id=9,id_descriptor=ID_DESCRIPTOR,parts=inv.parts,materials=mat.recipes,material_totals=dict(totals),modules=modules,channel_map=channel_map,counts=dict(Counter(p['role'] for p in inv.parts)),sensitive_count=72,fixture=dict(carrier_size_mm=ca['size_mm'],absorber_present=bool(absorber),absorber_owner='sector',absorber_reference_only=True,cell_pitch_mm=m['tile_pitch_mm'],cell_offset_mm=0),services=service_graph(c, handoffs),budgets=budgets(c),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),CONFIG,ROOT/'tools/pixel_barrel_dd4hep/materials.py',ROOT/'detector/config/elements.json')})
    report['mass_g']=sum(p['mass_g'] for p in inv.parts)
    report['carrier_and_modules_mass_g']=sum(p['mass_g'] for p in inv.parts if p['owner']!='sector')
    report['module_mass_g']={str(mid):sum(p['mass_g'] for p in inv.parts if p['owner']==f'module:{mid}') for mid in (0,1)}
    report['shared_carrier_mass_g']=sum(p['mass_g'] for p in inv.parts if p['owner']=='carrier')
    validate_report(report)
    return report,mat


def validate_report(report):
    """Checks inventories, exact CSG capacities, fit, ownership and channels."""
    c=report['config']; validate_config(c); parts=report['parts']; names=[p['name'] for p in parts]
    if len(names)!=len(set(names)): raise ValueError('duplicate part name')
    for p in parts:
        if p['owner'] not in ('carrier','sector','module:0','module:1') or (p['owner'].startswith('module:') and p.get('module')!=int(p['owner'][-1])):
            raise ValueError('part/module ownership')
    expected={'front_skin':1,'rear_skin':1,'rear_insulation':1,'cold_plate':1,'shared_interface':1,'cooling_tube':2,'coolant':2,'ported_rail':2,'side_rail':2}
    for role,count in expected.items():
        owned=[p for p in parts if p['role']==role]
        if len(owned)!=count or any(p['owner']!='carrier' for p in owned): raise ValueError('shared ownership/count '+role)
    absorbers=[p for p in parts if p['role']=='absorber_reference']
    if len(absorbers)!=int(report['fixture']['absorber_present']) or any(p['owner']!='sector' for p in absorbers): raise ValueError('absorber ownership')
    sensitive={(p.get('module'),p.get('sensor')):p for p in parts if p['role']=='sensitive'}
    wanted={(i,j) for i in range(2) for j in range(36)}
    if set(sensitive)!=wanted or sum(p['role']=='sensitive' for p in parts)!=72: raise ValueError('sensitive identifiers')
    if {(q['module'],q['sensor']) for q in report['channel_map']}!=wanted or len(report['channel_map'])!=72: raise ValueError('channel map completeness')
    for q in report['channel_map']:
        if q['channel_role']!='ordinary' or not 0<=q['channel']<72 or q['channel']!=q['sensor'] or q['chip']!=q['module']:
            raise ValueError('invalid tile channel role/address')
        if q['tile_center_mm']!=sensitive[q['module'],q['sensor']]['center_mm'] or q['volume_id']!=(9 | q['module']<<32 | q['sensor']<<34) or q['local_cell_xy']!=[0,0]: raise ValueError('channel physical transform/identifier')
    for mid,mod in enumerate(report['modules']):
        if mod['module']!=mid or mod['connected_channels']!=list(range(36)) or mod['unused_ordinary_channels']!=list(range(36,72)) or mod['auxiliary_channels']!=[dict(channel=72+i,role=r) for i,r in enumerate(c['electronics']['auxiliary_roles'])]: raise ValueError('module channel ownership')
    width,height,depth=c['carrier']['size_mm']
    for p in parts:
        validate_cuts(p['shape_kind'],p['dimensions_mm'],p['cuts']); b=bounds(p)
        limit=[(-width/2,width/2),(-height/2,height/2),(-c['carrier']['absorber_mm'] if p['owner']=='sector' else 0,depth)]
        if any(lo<a-EPS or hi>b+EPS for (lo,hi),(a,b) in zip(b,limit)): raise ValueError('carrier containment '+p['name'])
        volume=capacity(p['shape_kind'],p['dimensions_mm'])-sum(capacity(q['kind'],q['dimensions_mm']) for q in p['cuts'])
        if not math.isclose(volume,p['volume_mm3'],rel_tol=1e-12,abs_tol=EPS) or not math.isclose(volume*report['materials'][p['material']]['density_g_cm3']/1000,p['mass_g'],rel_tol=1e-12,abs_tol=EPS): raise ValueError('capacity/mass accounting '+p['name'])
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            if parts_overlap(a,b): raise ValueError('physical overlap '+a['name']+' / '+b['name'])
    # A tube must physically traverse the plate and both square rail ports.
    plate=next(p for p in parts if p['role']=='cold_plate')
    if len(plate['cuts'])!=2: raise ValueError('cooling plate must have two cylindrical cuts')
    for tube in [p for p in parts if p['role']=='cooling_tube']:
        if tube_axis(tube)!=1 or tube['dimensions_mm']['length']!=height: raise ValueError('blocked cooling handoff')
        if not any(q['kind']=='tube' and tube_axis(global_cut(plate,q))==1 and all(abs(tube['center_mm'][j]-global_cut(plate,q)['center_mm'][j])<EPS for j in (0,2)) and math.isclose(q['dimensions_mm']['rmax'],tube['dimensions_mm']['rmax']) and math.isclose(q['dimensions_mm']['length'],c['carrier']['plate_size_mm'][1]) for q in plate['cuts']): raise ValueError('missing aligned cylindrical displacement')
    if len(report['services']['cooling_handoffs'])!=4: raise ValueError('cooling handoff count')
    for branch,tube in enumerate(p for p in parts if p['role']=='cooling_tube'):
        for sign in (-1,1):
            handoff=next((q for q in report['services']['cooling_handoffs'] if q['branch']==branch and q['flow_role']==('inlet' if sign<0 else 'outlet')),None)
            if handoff is None or handoff['centre_mm']!=[tube['center_mm'][0],sign*height/2,tube['center_mm'][2]] or handoff['direction']!=[0,sign,0] or handoff['outer_radius_mm']!=tube['dimensions_mm']['rmax']:
                raise ValueError('cooling handoff does not match physical tube')
    if report['services'] != service_graph(c, report['services']['cooling_handoffs']): raise ValueError('functional service connectivity')
    # Recompute headline ledgers, preventing stale scalar totals after mutations.
    totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    for p in parts:
        for key in ('volume_mm3','mass_g'):totals[p['material']][key]+=p[key]
    for mat, values in totals.items():
        if mat not in report['material_totals'] or any(not math.isclose(v,report['material_totals'][mat][key],rel_tol=1e-12,abs_tol=EPS) for key,v in values.items()): raise ValueError('material total mismatch')
    for key,value in [('mass_g',sum(p['mass_g'] for p in parts)),('carrier_and_modules_mass_g',sum(p['mass_g'] for p in parts if p['owner']!='sector')),('shared_carrier_mass_g',sum(p['mass_g'] for p in parts if p['owner']=='carrier'))]:
        if not math.isclose(value,report[key],rel_tol=1e-12,abs_tol=EPS):raise ValueError('aggregate mass mismatch')
    if report['budgets']!=budgets(c): raise ValueError('inconsistent service budgets')
    return True
