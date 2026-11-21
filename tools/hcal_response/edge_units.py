"""DES046 newly manufactured narrow cassettes; original units are never cropped.

Dimensions/physical choices are governed by DES046, not shower results. The
source DES036 component builder supplies the same materials and package stacks.
"""
import copy
import math
from collections import Counter, defaultdict


def column_count(width):
    for n in range(1, 13):
        pitch = (width - (6 if n <= 6 else 12)) / n
        if 0 < pitch <= 30 + 1e-10:
            if pitch - .3 <= 7 or min(k*pitch+4 for k in ([n] if n<=6 else [6,n-6])) < 20:
                raise ValueError('edge tile recess or front-end clearance')
            return n, pitch
    raise ValueError('edge cassette exceeds twelve-column capacity')


def make(width, source, material):
    if not math.isfinite(width) or width < 32 - 1e-8:
        raise ValueError('edge cassette minimum width32mm')
    c = copy.deepcopy(source['config']); m = c['module']; ca = c['carrier']
    helper = source['_builder']; inv = helper.Inventory(material)
    n, pitch = column_count(width)
    columns = [n] if n <= 6 else [6, n - 6]
    board_x = []; cursor = -width/2 + 1
    for nc in columns:
        board_x.append(cursor + (nc*pitch+4)/2)
        cursor += nc*pitch + 6
    if not math.isclose(cursor-2, width/2-1, abs_tol=1e-8):
        raise ValueError('edge PCB/cassette width closure')
    channel_map = []
    for mid, (nc, cx) in enumerate(zip(columns, board_x)):
        owner = f'module:{mid}'; prefix = f'm{mid}'
        for row in range(6):
            for col in range(nc):
                sid = row*6+col
                x = cx + (col-(nc-1)/2)*pitch; y = -12+(row-2.5)*30
                z = m['tile_z_mm']; sx = pitch-.3; sy = 29.7; t = 3
                w = m['wrap_mm']; r = m['recess_radius_mm']; depth = m['recess_depth_mm']
                inv.box(f'{prefix}_t{sid}_active','sensitive','PSHost',[x,y,z],[sx,sy,t],owner=owner,module=mid,sensor=sid,
                        cuts=[helper.cut('tube',helper.tube_dims(r,depth),[0,0,(t-depth)/2])])
                inv.box(f'{prefix}_t{sid}_reflector','reflector','PET',[x,y,z],[sx+2*w,sy+2*w,t+2*w],owner=owner,module=mid,
                        cuts=[helper.cut('box',helper.box_dims([sx,sy,t])),helper.cut('tube',helper.tube_dims(r,w),[0,0,(t+w)/2])])
                sipm = [x,y+m['sipm_y_offset_mm'],m['sipm_z_mm']]
                inv.box(f'{prefix}_t{sid}_sipm','sipm','HCalSiPMProxy',sipm,m['sipm_size_mm'],owner=owner,module=mid)
                solder_z = m['sipm_z_mm']+m['sipm_size_mm'][2]/2+m['solder_mm']/2
                inv.box(f'{prefix}_t{sid}_solder','solder_copper_equivalent','Copper',[x,sipm[1],solder_z],m['sipm_size_mm'][:2]+[m['solder_mm']],owner=owner,module=mid)
                led = m['led_offset_xyz_mm']
                inv.box(f'{prefix}_t{sid}_led','direct_calibration_led','HCalLEDProxy',[x+led[0],y+led[1],led[2]],m['led_size_mm'],owner=owner,module=mid)
                channel_map.append(dict(module=mid,sensor=sid,chip=mid,channel=sid,channel_role='ordinary',tile_center_mm=[x,y,z],
                                        tile_size_mm=[sx,sy,t],physical_name=f'{prefix}_t{sid}_active'))
        helper.add_pcb(inv,prefix+'_pcb',[cx,-12],[nc*pitch+4,184,1.2],m['pcb_front_mm'],m['pcb_copper_equivalent_mm'],owner,mid)
        helper.add_chip_stack(inv,prefix,[cx,-12],c,owner,mid)
    skin = ca['skin_mm']; insulation = ca['rear_insulation_mm']; rail_z=6; rail_depth=12-2*skin
    inv.box('carrier_front_skin','front_skin','Aluminium',[0,0,skin/2],[width,240,skin])
    inv.box('carrier_rear_skin','rear_skin','Aluminium',[0,0,12-skin/2],[width,240,skin])
    inv.box('carrier_insulation','rear_insulation','Polyimide',[0,0,12-skin-insulation/2],[width-1,236,insulation])
    plate_cuts=[helper.cut('tube',helper.tube_dims(1,236),[x,0,0],helper.TUBE_Y) for x in board_x]
    inv.box('carrier_cold_plate','cold_plate','Copper',[0,0,8.5],[width-1,236,3],cuts=plate_cuts)
    for sign in (-1,1):
        inv.box(f'carrier_xrail{sign}','side_rail','Aluminium',[sign*(width-.5)/2,0,rail_z],[.5,240,rail_depth])
        ports=[helper.cut('box',helper.box_dims([2.2,2,2.2]),[x,0,8.5-rail_z]) for x in board_x]
        inv.box(f'carrier_yrail{sign}','ported_rail','Aluminium',[0,sign*119,rail_z],[width-1,2,rail_depth],cuts=ports)
    handoffs=[]
    for branch,x in enumerate(board_x):
        inv.add(f'carrier_tube{branch}','cooling_tube','Titanium',[x,0,8.5],'tube',helper.tube_dims(1,240,.8),frame=helper.TUBE_Y)
        inv.add(f'carrier_water{branch}','coolant','Water',[x,0,8.5],'tube',helper.tube_dims(.8,240),frame=helper.TUBE_Y)
        for sign in (-1,1):
            handoffs.append(dict(branch=branch,flow_role='inlet' if sign<0 else 'outlet',centre_mm=[x,sign*120,8.5],
                                 direction=[0,sign,0],outer_radius_mm=1,external_owner='collector design pending'))
    helper.add_pcb(inv,'carrier_service_pcb',[0,100],[width-2,30,1.2],m['pcb_front_mm'],m['pcb_copper_equivalent_mm'],'carrier')
    helper.add_chip_stack(inv,'carrier_interface',[board_x[0],45],c,'carrier',interface=True)
    inv.box('carrier_connector_combined','connector_combined','HCalConnectorProxy',[0,100,5.95],[20,12,2])
    totals=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    for p in inv.parts:
        for key in ('volume_mm3','mass_g'): totals[p['material']][key] += p[key]
    boards=len(columns); e=c['electronics']; service=c['services']; scenarios=[]
    local=(boards*e['powered_channels']*e['W_per_powered_channel']+boards*e['support_W_per_module']+e['shared_interface_W'])/service['converter_efficiency']
    for current in [service['nominal_current_A_per_device']]+service['stress_current_A_per_device']:
        heat=local+6*n*service['bias_V']*current
        scenarios.append(dict(current_A_per_device=current,LV_input_W=local,total_heat_W=heat,
                              ideal_water_g_s=1000*heat/(service['water_cp_J_kg_K']*service['water_rise_K'])))
    parts=inv.parts; first=next(p for p in parts if p['role']=='sensitive')['center_mm']
    unit=dict(status='DRAFT / PROTOTYPE; DES046 new edge unit',parts=parts,material_totals=dict(totals),
              mass_g=sum(p['mass_g'] for p in parts),channel_map=channel_map,sensitive_count=6*n,
              fixture=dict(carrier_size_mm=[width,240,12],absorber_present=False),
              columns=n,tangent_pitch_mm=pitch,board_columns=columns,board_centres_x_mm=board_x,
              boards=boards,powered_channels=boards*78,
              services=dict(cooling_handoffs=handoffs,connector_roles=['LV','bias','DAQ','trigger','control'],
                            qualification='local physical ports; external collectors/pinout/routing unqualified'),
              budgets=dict(power_scenarios=scenarios,connected_tiles=6*n,powered_channels=boards*78,
                           shared_interface_W=e['shared_interface_W']),
              active_offset_from_carrier_front_mm=first[:],
              active_offset_from_carrier_center_mm=[first[0],first[1],first[2]-6])
    validate(unit,helper)
    return unit


def validate(unit,helper):
    """Analytic physical containment, inventory and connectivity; native checks follow."""
    w,h,d=unit['fixture']['carrier_size_mm']; parts=unit['parts']; sensitive=[]
    if len({p['name'] for p in parts})!=len(parts): raise ValueError('edge duplicate part')
    for p in parts:
        bounds=helper.bounds(p)
        if any(lo<a-1e-8 or hi>b+1e-8 for (lo,hi),(a,b) in zip(bounds,((-w/2,w/2),(-h/2,h/2),(0,d)))):
            raise ValueError('edge part outside carrier '+p['name'])
        if p['role']=='sensitive': sensitive.append((p['module'],p['sensor']))
    if len(sensitive)!=unit['sensitive_count'] or len(set(sensitive))!=len(sensitive): raise ValueError('edge tile inventory')
    if len(unit['services']['cooling_handoffs'])!=2*unit['boards']: raise ValueError('edge cooling endpoint count')
    if sum(p['role']=='shared_interface' for p in parts)!=1: raise ValueError('edge shared interface ownership')
    # Bounds reject almost all disjoint pairs before finite cut-aware checks.
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            if helper.parts_overlap(a,b): raise ValueError('edge physical overlap '+a['name']+' / '+b['name'])
    return True
