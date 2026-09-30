#!/usr/bin/env python3
"""DES-002 PROTOTYPE arithmetic and finite-box screen, not a thermal/FEA solver."""
import argparse
import copy
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/module_layout'))
from geometry import _obb_overlap


def beam(parts, modulus_gpa, mass_kg_m, span_mm, gravity):
    # Each rectangle: width, thickness in bending direction, centroid, in mm.
    area = sum(w*t for w,t,y in parts)
    centre = sum(w*t*y for w,t,y in parts)/area
    inertia = sum(w*t**3/12+w*t*(y-centre)**2 for w,t,y in parts)
    rigidity = modulus_gpa*1e9*inertia*1e-12
    length = span_mm/1000
    return dict(I_mm4=inertia, EI_N_m2=rigidity,
                sag_um=5*mass_kg_m*gravity*length**4/(384*rigidity)*1e6,
                first_bending_Hz=math.pi/(2*length**2)*math.sqrt(rigidity/mass_kg_m))


def rectangle(body, width, start, depth):
    r=copy.deepcopy(body)
    r['center_mm']=[v-(body['half_w_mm']+start+depth/2)*n for v,n in zip(body['center_mm'],body['n'])]
    r['center_mm'][2]=0.
    r['half_u_mm']=width/2; r['half_w_mm']=depth/2
    return r


def run(config):
    path=ROOT/config['baseline']; raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=config['baseline_sha256']:
        raise ValueError('Baseline changed: review input provenance before rescreening')
    layout=json.loads(gzip.decompress(raw)); stack=config['stack_mm']; densities=config['density_g_cm3']; x0=config['radiation_length_mm']
    layer_results=[]; all_parts=[]; reps=[]
    for layer in layout['layers']:
        if layer['kind']!='cylinder' or layer['subsystem']!='pixel': continue
        bodies=[b for b in layout['bodies'] if b['layer_id']==layer['id']]
        columns=sorted(set(b['col'] for b in bodies)); family=bodies[0]['family']; f=config['families'][family]
        if any(b['family']!=family for b in bodies): raise ValueError('Mixed family within layer requires new load model')
        if any(b['tilt_degrees']!=0 or b['z_stagger'] for b in bodies): raise ValueError('Cross-section screen assumes untilted z-uniform pixel columns')
        counts=[sum(b['col']==col for b in bodies) for col in columns]
        if len(set(counts))!=1: raise ValueError('Nonuniform stave populations need per-stave screening')
        width=2*bodies[0]['half_u_mm']; length=max(b['center_mm'][2]+b['half_v_mm'] for b in bodies)-min(b['center_mm'][2]-b['half_v_mm'] for b in bodies)
        power=counts[0]*f['chips']*config['power_per_chip_W']; stress=power*config['stress_factor']; bore=f['tube_OD_mm']-2*f['tube_wall_mm']
        flow=f['flow_g_s']; tubes_area=2*math.pi*(f['tube_OD_mm']**2-bore**2)/4; coolant_area=2*math.pi*bore**2/4
        tube_hole_area=2*math.pi*f['tube_OD_mm']**2/4
        plate=stack['interface']+stack['insulation']+stack['graphite']+stack['top_skin']
        candidates={}
        for candidate in ['A','B']:
            areas={'CFRP':width*stack['top_skin']+f['spine_mm']*stack['bottom_skin'],
                   'foam':f['spine_mm']*stack['core']-tube_hole_area,
                   'graphite':width*stack['graphite'], 'titanium':tubes_area,
                   'glue':width*(stack['interface']+stack['internal_glue_equivalent']),
                   'insulation':width*stack['insulation'], 'liquid_CO2':coolant_area}
            parts=[(width,stack['top_skin'],plate-stack['top_skin']/2),
                   (f['spine_mm'],stack['bottom_skin'],plate+stack['core']+stack['bottom_skin']/2)]
            if candidate=='B':
                areas['foam']*=config['B_foam_fraction']
                areas['CFRP']+=2*stack['B_web']*stack['core']
                parts+=[(stack['B_web'],stack['core'],plate+stack['core']/2)]*2
            material={key:100*ar/width/x0[key] for key,ar in areas.items() if key!='liquid_CO2'}
            material['liquid_CO2']=100*areas['liquid_CO2']/width/10*densities['liquid_CO2']/config['co2_X0_g_cm2']
            support_mass=sum(ar*densities[key]/1000 for key,ar in areas.items()) # kg/m
            payload_mass=counts[0]*f['module_mass_g']/length # g/mm = kg/m
            screens={str(span):beam(parts,config['E_GPa'],support_mass+payload_mass,span,config['gravity_m_s2']) for span in config['screen_spans_mm']}
            corners=[beam(parts,e,support_mass+payload_mass*m,250,config['gravity_m_s2']) for e in config['E_range_GPa'] for m in config['module_mass_factors']]
            candidates[candidate]=dict(material_X0_percent=material,
                solid_X0_percent=sum(v for k,v in material.items() if k!='liquid_CO2'),
                liquid_filled_X0_percent=sum(material.values()), support_full_liquid_kg_m=support_mass,
                payload_kg_m=payload_mass, bending=screens,
                sag_250mm_sensitivity_um=[min(c['sag_um'] for c in corners),max(c['sag_um'] for c in corners)])
        k=config['conductivity_W_m_K']; overhang=(width-f['spine_mm'])/2/1000
        conduction=(stack['interface']/1000/k['interface']+stack['insulation']/1000/k['insulation']+stack['top_skin']/1000/k['CFRP_transverse']+overhang**2/(2*k['graphite_inplane']*stack['graphite']/1000))*1e4
        for col in columns:
            b=copy.deepcopy(next(b for b in bodies if b['col']==col));b['center_mm'][2]=0.;reps.append(b)
            # Same bounding envelopes for A and B; internal holes cannot worsen fit.
            all_parts.extend([(b['module_id'],rectangle(b,width,0,plate)),
                              (b['module_id'],rectangle(b,f['spine_mm'],plate,stack['core']+stack['bottom_skin']))])
        qmax=stress*config['heat_fraction_max']
        result=dict(layer=layer['id'],radius_mm=layer['r_m']*1000,family=family,staves=len(columns),modules=len(bodies),modules_per_stave=counts[0],body_width_mm=width,occupied_length_mm=length,
            layer_power_W=power*len(columns),stave_power_W=power,stave_stress_W=stress,circuits=2*len(columns),
            circuit_stress_imbalanced_W=qmax,flow_per_circuit_g_s=flow,
            exit_quality_stress_imbalanced=config['inlet_quality']+qmax/(flow*config['latent_heat_J_g']),
            mass_flux_kg_m2_s=flow/1000/(math.pi*(bore/1000)**2/4),
            conduction_lower_bound_K_cm2_W=conduction,candidates=candidates)
        layer_results.append(result)
    body_conflicts=[(owner,b['module_id']) for owner,p in all_parts for b in reps if owner!=b['module_id'] and _obb_overlap(p,b)]
    support_conflicts=[(o1,o2) for i,(o1,a) in enumerate(all_parts) for o2,b in all_parts[i+1:] if o1!=o2 and _obb_overlap(a,b)]
    rads=[s['r_min_mm']+config['rib_radial_mm']/2 for s in layout['metadata']['services']['supports'] if s['layer_id'] in {r['layer'] for r in layer_results}]
    # Illustrative material allowance only; tabs/global anchoring not included.
    mass_one_ring_plane=sum(2*math.pi*r*config['rib_radial_mm']*config['rib_axial_mm']*densities['CFRP']/1000 for r in rads)
    return dict(status='PROTOTYPE analytic screen; no FEA, hydraulic or engineering qualification',
        baseline_sha256=hashlib.sha256(raw).hexdigest(), layers=layer_results,
        totals=dict(staves=sum(r['staves'] for r in layer_results),modules=sum(r['modules'] for r in layer_results),
            circuits=sum(r['circuits'] for r in layer_results),nominal_power_W=sum(r['layer_power_W'] for r in layer_results),
            stress_power_W=sum(r['layer_power_W'] for r in layer_results)*config['stress_factor'],
            flow_g_s=sum(r['flow_per_circuit_g_s']*r['circuits'] for r in layer_results)),
        cross_section_screen=dict(representative_columns=len(reps),support_body_conflicts=body_conflicts,support_support_conflicts=support_conflicts,
            limitation='Zero-clearance boxes, repeated z-uniform columns. Shared ribs, hardpoints, tolerance and route-end joints are NOT checked. No complete CAD/overlap claim.'),
        illustrative_ribs=dict(mass_g_per_plane_all_layers=mass_one_ring_plane,
            intermediate_planes=4,intermediate_rib_mass_g=4*mass_one_ring_plane,
            local_normal_X0_percent=100*config['rib_radial_mm']/x0['CFRP']),
        thermal_target=dict(TFM_K_cm2_W=config['tfm_target_K_cm2_W'],prospective_sensor_C=config['coolant_temperature_C']+1.05*config['tfm_target_K_cm2_W'],achieved=False))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    cfgpath=Path(__file__).with_name('inputs.json');cfg=json.loads(cfgpath.read_text());result=run(cfg)
    result['provenance']={'input_sha256':hashlib.sha256(cfgpath.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':sys.version,'command':'python3 -B tools/pixel_support/screen.py --output docs/validation/DES-002/screening.json'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'totals':result['totals'],'cross_section_screen':result['cross_section_screen']},indent=2))
if __name__=='__main__':main()
