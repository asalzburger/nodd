"""Reproducible LAYOUT-002 service space budget. Hypotheses, not qualification."""
import json
import math
from pathlib import Path
from barrel_geometry import ROOT, sha

CONFIG = Path(__file__).with_name('services.json')


def side_egress_reservation(c, stations, bends):
    """Conditional empty lanes; these checks do not construct connected ports."""
    clear=c['installation_clearance_mm'];lo,hi=c['side_neck_band_abs_z_mm']
    if not all(math.isfinite(x) for x in [clear,lo,hi,c['external_route_radius_mm'],*c['ordinary_lane_mm'],*c['utility_lane_mm']]) or clear<=0 or min(*c['ordinary_lane_mm'],*c['utility_lane_mm'])<=0:
        raise ValueError('Need finite positive reservation dimensions')
    if not 0<=lo<hi<=c['barrel_warm_half_z_mm']:
        raise ValueError('Side-neck band must precede the barrel warm end')
    if not math.isclose(c['endcap_warm_front_z_mm']-c['barrel_warm_half_z_mm'],c['front_service_gap_mm']):
        raise ValueError('Front envelope gap differs from the routing specification')
    window=c['hcal_endcap_front_z_mm']-c['hcal_barrel_half_z_mm']
    if c['endcap_warm_back_z_mm']>c['hcal_barrel_half_z_mm'] or not math.isclose(window,c['rear_service_gap_mm']):
        raise ValueError('HCAL context does not retain the radial exit window')
    n=c['station_sectors_per_end'];u=c['barrel_utility_sector'];v=c['endcap_utility_sector']
    if n!=16 or c['barrel_stations']!=2*n or c['endcap_stations_each']!=n or not all(isinstance(i,int) and 0<=i<n for i in (u,v)) or u==v:
        raise ValueError('Need distinct barrel/endcap utility sectors in the retained station grid')
    lanes={};radius=c['external_route_radius_mm']
    for kind in ('ordinary','utility'):
        width,height=c[kind+'_lane_mm'];inner,outer=radius-height/2,radius+height/2
        angle=width/radius;edge=inner*math.sin((2*math.pi/n-angle)/2)
        if inner-c['endcap_warm_outer_radius_mm']<clear or c['hcal_barrel_front_apothem_mm']-outer<clear or angle>=2*math.pi/n or edge<clear:
            raise ValueError('Annular lane fails radial/angular face clearance')
        lanes[kind]=dict(inner_radius_mm=inner,outer_radius_mm=outer,angular_width_rad=angle,
            area_mm2=width*height,angular_face_clearance_mm=edge)
    ordinary=sum(stations[k]['ordinary_occupied_area_mm2'] for k in ('barrel','endcap'))
    mixed={k:stations[k]['utility_occupied_area_mm2']+stations['endcap' if k=='barrel' else 'barrel']['ordinary_occupied_area_mm2'] for k in ('barrel','endcap')}
    if ordinary>lanes['ordinary']['area_mm2'] or max(mixed.values())>lanes['utility']['area_mm2']:
        raise ValueError('Shared barrel/endcap station bundles exceed their lane')
    for bend in bends.values():
        required=bend['axial_s_bend_envelope_mm']+clear
        rear=bend['rear_quarter_turn_mm']+clear
        if required>hi-lo or rear>window:
            raise ValueError('Pre-end S bend or rear exit fails two-face clearance')
        bend['side_neck_required_axial_mm']=required;bend['rear_two_face_bound_mm']=rear
    max_od=max(c['nitrogen_external_jacket_od_mm'],c['lar_utility_external_od_mm'])
    return dict(status='CONDITIONAL RESERVATION ONLY',external_route_constructed=False,
        side_neck_band_abs_z_mm=[lo,hi],radial_single_jacket_bounds_mm=[c['nitrogen_pipe_radius_mm']-max_od/2-clear,radius+max_od/2+clear],
        radial_exit_window_abs_z_mm=[c['hcal_barrel_half_z_mm'],c['hcal_endcap_front_z_mm']],
        endcap_to_hcal_axial_interval_mm=c['hcal_endcap_front_z_mm']-c['endcap_warm_back_z_mm'],
        lanes=lanes,ordinary_combined_area_mm2=ordinary,mixed_utility_station_area_mm2=mixed,
        utility_sector_assignment=dict(barrel=u,endcap=v),
        limitations=['No native external pipe/cable/port material is constructed.',
            'Neck band intersects populated boards/H-rings; no swept clearance, connected headers or pressure/vacuum port design.',
            'Annular area and single-jacket bounds do not establish individual bundle packing or engineering fit.'])


def budget(config=None):
    c = config or json.loads(CONFIG.read_text())
    if not 0 < c['packing_fill'] < 1:
        raise ValueError('Packing fill must be between zero and one')
    result = {'status': 'PROTOTYPE / explicit planning hypotheses', 'config': c, 'stations': {}}
    for kind, channels, stations in (
        ('barrel', c['barrel_channel_budget'], c['barrel_stations']),
        ('endcap', c['endcap_channel_budget_each'], c['endcap_stations_each'])):
        boards = math.ceil(channels/c['channels_per_board'])
        per_station = math.ceil(boards/stations)
        aggregators = math.ceil(per_station/c['boards_per_aggregator'])
        counts = {}
        area = 0.
        for name, b in c['station_bundle'].items():
            n = b.get(kind+'_count', b.get('per_aggregator', 0)*aggregators)
            counts[name] = n
            area += n*math.pi*(b['od_mm']/2)**2
        cable_area = area/c['packing_fill']
        pipe_area = (2*math.pi*(c['nitrogen_external_jacket_od_mm']/2)**2+2*math.pi*(c['warm_water_external_od_mm']/2)**2)/c['packing_fill']
        throat = cable_area+pipe_area
        utility = throat+4*math.pi*(c['lar_utility_external_od_mm']/2)**2/c['packing_fill']
        length = c['cable_length_per_station_m'][kind]
        result['stations'][kind] = dict(channels_budget=channels, boards_required=boards,
            boards_per_station=per_station, aggregators_per_station=aggregators,
            cable_counts_per_station=counts, cable_packed_area_mm2=cable_area,
            ordinary_occupied_area_mm2=throat, utility_occupied_area_mm2=utility,
            ordinary_lane_area_mm2=math.prod(c['ordinary_lane_mm']),
            utility_lane_area_mm2=math.prod(c['utility_lane_mm']),
            ordinary_area_margin_mm2=math.prod(c['ordinary_lane_mm'])-throat,
            utility_area_margin_mm2=math.prod(c['utility_lane_mm'])-utility,
            cable_lengths_m={k:n*stations*length for k,n in counts.items()},
            cable_packed_volume_m3=cable_area*stations*length/1e6,
            cable_length_range_factor=[1-c['route_length_uncertainty_fraction'],1+c['route_length_uncertainty_fraction']],
            warm_single_cable_packed_area_per_station_mm2=channels/stations*math.pi*(c['warm_analog_cable_od_mm']/2)**2/c['packing_fill'])
        if throat > math.prod(c['ordinary_lane_mm']) or utility > math.prod(c['utility_lane_mm']):
            raise ValueError('Service lane has insufficient packed area')
    shift = c['external_route_radius_mm']-c['nitrogen_pipe_radius_mm']
    policy=c.get('front_routing_policy','front_s_bend')
    if policy not in ('front_s_bend','pre_end_side_neck_reservation'):
        raise ValueError('Unknown front routing policy')
    bends = {}
    for od in (c['nitrogen_external_jacket_od_mm'], c['lar_utility_external_od_mm']):
        minimum_radius = c['minimum_bend_radius_od']*od
        radius = c.get('actual_bend_radii_mm', {}).get(str(od), minimum_radius)
        if radius < minimum_radius:
            raise ValueError('Chosen bend radius below minimum OD rule')
        if not 0 < shift <= 2*radius:
            raise ValueError('Radial S bend outside chosen bend construction')
        angle = math.acos(1-shift/(2*radius))
        axial = 2*radius*math.sin(angle)+c['installation_clearance_mm']
        rear = radius+od/2+c['installation_clearance_mm']
        bends[str(od)] = dict(radial_shift_mm=shift, bend_radius_mm=radius,
            axial_centreline_with_clearance_mm=axial, axial_s_bend_envelope_mm=axial+od, rear_quarter_turn_mm=rear)
        if (policy=='front_s_bend' and axial+od > c['front_service_gap_mm']) or rear > c['rear_service_gap_mm']:
            raise ValueError('Axial service gap fails minimum bend allocation')
    if policy=='pre_end_side_neck_reservation':
        result['external_route_reservation']=side_egress_reservation(c,result['stations'],bends)
    result['bends'] = bends
    q = c['barrel_cooling_reference_kW']+2*c['endcap_cooling_planning_kW_each']
    result['heat'] = dict(source_barrel_scenario_kW=c['barrel_cooling_reference_kW'],
        source_flow_kg_s=c['barrel_cooling_reference_flow_kg_s'], planning_total_kW=q,
        inferred_flow_kg_s=q/c['barrel_cooling_reference_kW']*c['barrel_cooling_reference_flow_kg_s'],
        electronics_total_kW_scenarios=[(c['barrel_channel_budget']+2*c['endcap_channel_budget_each'])*p/1e6 for p in c['electronics_power_mW_per_channel_scenarios']],
        adverse_total_shortfall_kW=max(0,(c['barrel_channel_budget']+2*c['endcap_channel_budget_each'])*max(c['electronics_power_mW_per_channel_scenarios'])/1e6-q), limitation='Scaling one published nitrogen scenario; no pressure-drop, dry-out, header or bath-load certification.')
    current = c['barrel_cooling_reference_kW']*1000/c['barrel_stations']/c['supply_V']/c['conversion_efficiency']
    resistance = c['copper_room_resistivity_ohm_m']*c['power_loop_length_m']/(c['parallel_conductors']*c['conductor_area_mm2']*1e-6)
    result['power_example'] = dict(current_A=current, loop_resistance_ohm=resistance,
        voltage_drop_V=current*resistance, dissipation_W=current**2*resistance,
        scope='Room-temperature 48V copper loop only; return length included, connectors and cryogenic leads excluded.')
    result['bandwidth'] = dict(barrel_uncompressed_Tbit_s=c['barrel_channel_budget']*c['bandwidth_max_hit_rate_Hz']*c['bandwidth_bits_per_hit']/1e12,
        aggregator_Gbit_s=c['channels_per_board']*c['boards_per_aggregator']*c['bandwidth_max_hit_rate_Hz']*c['bandwidth_bits_per_hit']/1e9,
        electrical_capacity_Gbit_s=4*c['electrical_link_Gbit_s'],
        optical_capacity_Gbit_s=2*c['optical_link_Gbit_s'],
        limitation='Maximum triggering-rate scenario with64-bit hit payload choice; excludes multi-sample waveforms, protocol overhead, occupancy and compression.')
    result['source_sha256']={str(CONFIG.relative_to(ROOT)):sha(CONFIG),str(Path(__file__).relative_to(ROOT)):sha(__file__)}
    return result


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(budget(),indent=2)+'\n')
