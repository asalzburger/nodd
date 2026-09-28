#!/usr/bin/env python3
"""PROTOTYPE resource/return-area screening, not magnet engineering or a field solve."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MU0 = 4e-7 * math.pi


def main():
    paths = [ROOT/'tools/magnetic_study/candidates.json', ROOT/'tools/magnetic_study/layouts.json',
             ROOT/'docs/design/DES-003-envelopes.json']
    coils, layouts, baseline = [json.loads(p.read_text()) for p in paths]
    muon = next(r for r in baseline['regions'] if r['id'] == 'muon_barrel')
    rows = []
    for coil in coils['vacuum_controls']:
        option = next(o for o in layouts['options'] if o['id'] == coil['id'])
        r, h, b = coil['radius_m'], coil['half_length_m'], coil['central_field_T']
        inner = option['overrides'].get('muon_barrel', {}).get('r_min_m', muon['r_min_m'])
        outer = muon['r_max_m']
        flux = b * math.pi * r*r
        area = math.pi * (outer*outer - inner*inner)
        pressure = b*b/(2*MU0)
        rows.append({'vacuum_control':coil['id'], 'instrumented_return_candidate':'MAG-02' if coil['id']=='MAG-01' else 'MAG-04',
                     'sheet_radius_m':r,'sheet_half_length_m':h,'central_field_T':b,
                     'muon_host_inner_m':inner,'muon_host_outer_m':outer,
                     'flat_field_disk_flux_proxy_Wb':flux,
                     'whole_muon_annulus_area_m2':area,
                     'all_flux_returning_in_solid_host_average_T':flux/area,
                     'central_pressure_scale_MPa':pressure/1e6,
                     'uniform_sheet_bore_energy_proxy_MJ':pressure*math.pi*r*r*2*h/1e6,
                     'ideal_active_return_radius_at_minus_1p5T_m':math.sqrt(r*r+flux/(1.5*math.pi)),
                     'host_start_active_return_radius_at_minus_1p5T_m':math.sqrt(inner*inner+flux/(1.5*math.pi)),
                     'return_area_trials':[{'trial_mean_field_T':trial,'required_area_m2':flux/trial,
                         'fraction_of_whole_host':flux/(trial*area)} for trial in [1.5,2.0]]})
    # Independent dimensional/ratio identities; arithmetic verification only.
    assert math.isclose(rows[1]['flat_field_disk_flux_proxy_Wb']/rows[0]['flat_field_disk_flux_proxy_Wb'],
                        (rows[1]['sheet_radius_m']/rows[0]['sheet_radius_m'])**2)
    assert rows[0]['whole_muon_annulus_area_m2'] > rows[1]['whole_muon_annulus_area_m2'] > 0
    result={'status':'PROTOTYPE inference; not an energy estimate, saturation calculation or feasibility proof',
        'classification':'INFERENCE from explicitly unsigned diagnostic dimensions',
        'assumptions':['Uniform central B across disk of current-sheet radius; actual solved bore flux may differ.',
            'All disk flux assigned to the muon barrel annulus at its midplane; HCal return and external leakage omitted.',
            'Whole annulus treated as available return area; actual steel fraction is smaller because stations and services need space.',
            '1.5 T and 2.0 T are NODD DESIGN CHOICE trial mean return fields, not steel grades, saturation limits or selected operating fields.',
            'Active-return radius screens assume a uniform -1.5 T annulus beginning either at the infinitesimal main sheet or at the muon host inner radius; finite coils, end return and outside flux are omitted.',
            'Uniform sheet-bore energy is B0^2/(2mu0) times geometric winding-bore volume; neither full-field energy nor a rigorous bound.',
            'No endcap bottleneck, nonlinear B-H response, force balance, quench or structural verification.'],
        'formulas':{'flux':'B0*pi*Rsheet^2','area':'pi*(Rmuon_outer^2-Rmuon_inner^2)',
                    'return_mean':'flux/area','pressure':'B0^2/(2mu0)','energy_proxy':'pressure*pi*Rsheet^2*2h'},
        'results':rows,'provenance':{'project_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),
            'command':'python3 -B tools/magnetic_study/option_screen.py','python':sys.version.split()[0],
            'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths+[Path(__file__).resolve()]},
            'random_seed':None,'tolerances':'math.isclose default for algebraic ratio identity; no physical acceptance tolerance'}}
    out=ROOT/'docs/validation/DES-004-option-screen.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(rows,indent=2))

if __name__ == '__main__': main()
