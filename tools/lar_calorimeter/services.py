"""Reproducible LAYOUT-002 service space budget. Hypotheses, not qualification."""
import json
import math
from pathlib import Path
from barrel_geometry import ROOT, sha

CONFIG = Path(__file__).with_name('services.json')


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
    bends = {}
    for od in (c['nitrogen_external_jacket_od_mm'], c['lar_utility_external_od_mm']):
        radius = c['minimum_bend_radius_od']*od
        if not 0 < shift <= 2*radius:
            raise ValueError('Radial S bend outside chosen bend construction')
        angle = math.acos(1-shift/(2*radius))
        axial = 2*radius*math.sin(angle)+c['installation_clearance_mm']
        rear = radius+od/2+c['installation_clearance_mm']
        bends[str(od)] = dict(radial_shift_mm=shift, bend_radius_mm=radius,
            axial_s_bend_mm=axial, rear_quarter_turn_mm=rear)
        if axial > c['front_service_gap_mm'] or rear > c['rear_service_gap_mm']:
            raise ValueError('Axial service gap fails minimum bend allocation')
    result['bends'] = bends
    q = c['barrel_cooling_reference_kW']+2*c['endcap_cooling_planning_kW_each']
    result['heat'] = dict(source_barrel_scenario_kW=c['barrel_cooling_reference_kW'],
        source_flow_kg_s=c['barrel_cooling_reference_flow_kg_s'], planning_total_kW=q,
        inferred_flow_kg_s=q/c['barrel_cooling_reference_kW']*c['barrel_cooling_reference_flow_kg_s'],
        electronics_total_kW_scenarios=[(c['barrel_channel_budget']+2*c['endcap_channel_budget_each'])*p/1e6 for p in c['electronics_power_mW_per_channel_scenarios']],
        limitation='Scaling one published nitrogen scenario; no pressure-drop, dry-out, header or bath-load certification.')
    current = c['barrel_cooling_reference_kW']*1000/c['barrel_stations']/c['supply_V']/c['conversion_efficiency']
    resistance = c['copper_room_resistivity_ohm_m']*c['power_loop_length_m']/(c['parallel_conductors']*c['conductor_area_mm2']*1e-6)
    result['power_example'] = dict(current_A=current, loop_resistance_ohm=resistance,
        voltage_drop_V=current*resistance, dissipation_W=current**2*resistance,
        scope='Room-temperature 48V copper loop only; return length included, connectors and cryogenic leads excluded.')
    result['bandwidth'] = dict(barrel_uncompressed_Tbit_s=c['barrel_channel_budget']*c['bandwidth_sample_rate_Hz']*c['bandwidth_bits_per_sample']/1e12,
        aggregator_Gbit_s=c['channels_per_board']*c['boards_per_aggregator']*c['bandwidth_sample_rate_Hz']*c['bandwidth_bits_per_sample']/1e9,
        electrical_capacity_Gbit_s=4*c['electrical_link_Gbit_s'],
        optical_capacity_Gbit_s=2*c['optical_link_Gbit_s'],
        limitation='R&D sample-rate capability scenario before protocol overhead, occupancy or compression.')
    result['source_sha256']={str(CONFIG.relative_to(ROOT)):sha(CONFIG),str(Path(__file__).relative_to(ROOT)):sha(__file__)}
    return result


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(budget(),indent=2)+'\n')
