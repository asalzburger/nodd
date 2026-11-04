#!/usr/bin/env python3
"""DES042 conditional power/cable study; does not modify detector geometry."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def harness_count(modules, module_W, board_W, reference_W, modules_per_harness):
    """Relative-load hypothesis only; no qualified cable-current assertion."""
    return max(1, math.ceil((modules * module_W + board_W) /
                            (modules_per_harness * reference_W)))


def annular_width(area_mm2, radius_mm, phi_fraction, packing_fraction):
    return math.sqrt(radius_mm**2 + area_mm2 /
                     (math.pi * phi_fraction * packing_fraction)) - radius_mm


def network_loss(taps_mm, entry_mm, current_A, resistivity, rail_area_mm2):
    """Supply + return loss for the unchanged DES020/021 discrete rails."""
    last = entry_mm
    loss = 0.0
    for index, position in enumerate(sorted(taps_mm, reverse=True)):
        resistance = 2 * resistivity * (last - position) / 1000 / rail_area_mm2
        loss += resistance * ((len(taps_mm) - index) * current_A)**2
        last = position
    return loss


def inputs():
    barrel = load_module('des042_barrel', ROOT/'tools/short_strip_barrel/model.py')
    endcap = load_module('des042_endcap', ROOT/'tools/short_strip_endcap/model.py')
    bc, ec = barrel.load(), endcap.load()
    bl, el = barrel.build(bc), endcap.build(ec)
    staves = {(s['layer'], s['stave']): s for s in bl['staves']}
    records = []
    for route in bl['routes']:
        radius = staves[route['layer'], route['stave']]['radius_mm']
        records.append(dict(region='barrel', modules=len(route['modules']),
                            side=route['side'], sector=route['sector'], harnesses=route['harnesses'],
                            length_mm=750-radius+math.pi*50+bc['trunk_mm'][3]-bc['trunk_mm'][2]))
    for route in el['routes']:
        z = abs(el['discs'][route['layer']]['z_mm'])
        records.append(dict(region='endcap', modules=len(route['modules']),
                            side=route['side'], sector=route['global_trunk_sector'], harnesses=route['harnesses'],
                            length_mm=750-695+math.pi*50+3500-(z+85)))
    # Match additive native service payload; do not merge independent pipe banks.
    barrel_pipe_pairs = sum(s['manifolds'] for s in bl['sectors'])
    endcap_pipe_pairs = ec['petals'] * math.ceil(len(ec['disc_z_mm']) / ec['loops_per_manifold'])
    b_taps = [m['center_mm'][2] for m in bl['modules']
              if m['layer']==0 and m['stave']==0 and m['center_mm'][2]>0]
    e_taps = [m['radius_mm'] for m in el['modules'] if m['layer']==0 and m['petal']==0]
    pipes_by_sector = [s['manifolds']+math.ceil(len(ec['disc_z_mm'])/ec['loops_per_manifold'])
                       for s in bl['sectors']]
    return bc, ec, records, barrel_pipe_pairs+endcap_pipe_pairs, b_taps, e_taps, pipes_by_sector


def evaluate(config):
    bc, ec, routes, pipe_pairs, b_taps, e_taps, pipes_by_sector = inputs()
    module_counts = {region: sum(r['modules'] for r in routes if r['region']==region)
                     for region in ('barrel','endcap')}
    if module_counts != dict(barrel=8064, endcap=4320):
        raise ValueError('Current baseline module inventory changed; review DES042 inputs')
    area_power = math.pi/4 * bc['power_cable_OD_mm']**2
    area_fibre = math.pi/4 * bc['fibre_cable_OD_mm']**2
    baseline_harnesses = sum(r['harnesses'] for r in routes)
    baseline_lengths = {region: sum(r['harnesses']*r['length_mm'] for r in routes if r['region']==region)
                        for region in module_counts}
    fibre_L = sum(baseline_lengths.values()) * area_fibre/1e6
    baseline_power_L = sum(baseline_lengths.values()) * area_power/1e6
    fixed_pipe_area = pipe_pairs * math.pi/4 * sum(d*d for d in bc['trunk_pipe_OD_mm'])
    baseline_area = baseline_harnesses/2 * (area_power+area_fibre) + fixed_pipe_area
    width_args = (bc['trunk_mm'][0], bc['phi_fraction'], bc['packing_fraction'])
    baseline_width = annular_width(baseline_area, *width_args)
    pipe_area = math.pi/4*sum(d*d for d in bc['trunk_pipe_OD_mm'])
    sector_baseline_harnesses = [sum(r['harnesses'] for r in routes if r['side']==1 and r['sector']==i)
                                for i in range(bc['sectors'])]
    sector_baseline_area = [n*(area_power+area_fibre)+p*pipe_area
                            for n,p in zip(sector_baseline_harnesses,pipes_by_sector)]
    baseline_worst_width = annular_width(max(sector_baseline_area)*bc['sectors'],*width_args)
    counts_by_region = {region: sum(r['region']==region for r in routes) for region in module_counts}
    base_loss_unit = dict(barrel=network_loss(b_taps,1210,1,bc['resistivity_ohm_mm2_m'],12*.2),
                          endcap=network_loss(e_taps,678,1,ec['resistivity_ohm_mm2_m'],12*.2))
    rows=[]
    for pitch in config['pitch_v_mm']:
        if not math.isfinite(pitch) or pitch<=0 or not math.isclose(96/pitch,round(96/pitch)):
            raise ValueError('Pitch must divide the 96 mm active length')
        fraction = .5/pitch
        channels_per_module = 640*round(96/pitch)
        for normalization, base_W in config['power_normalizations_W_module'].items():
            for dependent in config['channel_dependent_fraction']:
                if not 0<=dependent<=1: raise ValueError('Invalid channel-dependent fraction')
                module_W = base_W * (1-dependent+dependent*fraction)
                board_W = len(routes)*bc['end_board_W']
                leakage_W = sum(module_counts.values())*bc['leakage_W_module']
                def local_loss(power):
                    return sum(counts_by_region[region]*base_loss_unit[region]*(power/bc['supply_V'])**2
                               for region in module_counts)
                baseline_heat = sum(module_counts.values())*base_W+board_W+leakage_W+local_loss(base_W)
                heat = sum(module_counts.values())*module_W+board_W+leakage_W+local_loss(module_W)
                harnesses = {region:0 for region in module_counts}
                power_lengths = {region:0.0 for region in module_counts}
                for route in routes:
                    n=harness_count(route['modules'],module_W,bc['end_board_W'],base_W,bc['modules_per_harness'])
                    harnesses[route['region']]+=n
                    power_lengths[route['region']]+=n*route['length_mm']
                power_L=sum(power_lengths.values())*area_power/1e6
                new_area=sum(harnesses.values())/2*area_power+baseline_harnesses/2*area_fibre+fixed_pipe_area
                new_width=annular_width(new_area,*width_args)
                sector_power = [sum(harness_count(r['modules'],module_W,bc['end_board_W'],base_W,bc['modules_per_harness'])
                                    for r in routes if r['side']==1 and r['sector']==i)
                                for i in range(bc['sectors'])]
                sector_area = [p*area_power+f*area_fibre+c*pipe_area
                               for p,f,c in zip(sector_power,sector_baseline_harnesses,pipes_by_sector)]
                worst_width = annular_width(max(sector_area)*bc['sectors'],*width_args)
                rows.append(dict(pitch_v_mm=pitch,power_normalization=normalization,
                    channel_dependent_fraction=dependent,channel_fraction=fraction,
                    sigma_u_um=75/math.sqrt(12),sigma_v_um=pitch*1000/math.sqrt(12),
                    channels_per_module=channels_per_module,
                    channels={region:n*channels_per_module for region,n in module_counts.items()},
                    module_electronics_W=module_W,
                    electronics_kW=sum(module_counts.values())*module_W/1000,
                    fixed_boards_kW=board_W/1000,fixed_HV_leakage_kW=leakage_W/1000,
                    local_LV_rail_loss_kW=local_loss(module_W)/1000,
                    heat_kW=heat/1000,saved_heat_kW=(baseline_heat-heat)/1000,
                    saved_electronics_kW=sum(module_counts.values())*(base_W-module_W)/1000,
                    power_harnesses=harnesses,fibre_harnesses=baseline_harnesses,
                    power_envelope_L=power_L,fibre_envelope_L=fibre_L,
                    saved_power_envelope_L=baseline_power_L-power_L,
                    saved_effective_material_L={name:(baseline_power_L-power_L)*part
                                                for name,part in [('Copper',.2),('Polyimide',.3),('internal_void_air',.5)]},
                    cable_envelope_L=power_L+fibre_L,
                    saved_power_envelope_by_region_L={region:(baseline_lengths[region]-power_lengths[region])*area_power/1e6
                                                       for region in module_counts},
                    one_end_service_area_mm2=new_area,
                    saved_one_end_service_area_mm2=baseline_area-new_area,
                    area_equivalent_annular_width_mm=new_width,
                    saved_area_equivalent_width_mm=baseline_width-new_width,
                    one_end_sector_service_area_mm2=sector_area,
                    worst_sector_equivalent_width_mm=worst_width,
                    saved_worst_sector_equivalent_width_mm=baseline_worst_width-worst_width,
                    unchanged_hardware_saved_volume_L=0,
                    upper_LV_copper_material_saved_L=baseline_power_L*.2*dependent*(1-fraction)))
    sources=config['source_paths']+['software/analysis/strixel_pitch_study/services.py',
                                   'software/analysis/strixel_pitch_study/services.json']
    return dict(schema_version=1,status='PROTOTYPE; conditional sensitivity, not engineering qualification',
        source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
        module_counts=module_counts,network_counts=counts_by_region,
        baseline=dict(power_harnesses_both_ends=baseline_harnesses,fibre_harnesses_both_ends=baseline_harnesses,
                      routed_harness_length_m=sum(baseline_lengths.values())/1000,
                      power_envelope_L=baseline_power_L,fibre_envelope_L=fibre_L,
                      cable_envelope_L=baseline_power_L+fibre_L,
                      pipe_pairs_per_end=pipe_pairs,one_end_service_area_mm2=baseline_area,
                      area_equivalent_annular_width_mm=baseline_width,
                      one_end_sector_service_area_mm2=sector_baseline_area,
                      worst_sector_equivalent_width_mm=baseline_worst_width),
        limitations=[
            'Fixed installed-hardware control saves zero physical cable, pipe, tray or electronics footprint.',
            'Power proxies are not lower/upper hardware bounds; channel fraction is an explicit sensitivity.',
            'Reaggregation requires new LV/HV/control conductors, fanout and connectors; benchmark OD has no qualified current rating.',
            'Power-cable envelope includes a20%Cu/30%PI/50%air material fixture; gross litres are not solid-copper litres.',
            'Copper-only column is a material upper proxy before unknown fixed HV/control copper, not external space saved.',
            'Fibre count, cooling pipes, tray, local buses, module ASIC footprints and leakage are fixed.',
            'No automatic bandwidth reduction at fixed particle flux, no hydraulic or local bend/packing qualification.',
            'Equivalent width uses75%azimuth/50%packing and native additive pipe payload; does not shrink current73mm corridor.',
            'Heat includes FE, board, leakage and unchanged local rail I²R; external distribution/converter losses unknown.'
        ],cases=rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=HERE/'services.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=evaluate(json.loads(args.config.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report['baseline']))


if __name__=='__main__':main()
