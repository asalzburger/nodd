#!/usr/bin/env python3
"""Constituent conservation and bounded local-support/service screens."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from model import ROOT,load,execution,sha

def run(expectedfile,out):
    c=load();expected=json.loads(expectedfile.read_text());errors=[];roles=defaultdict(float);petal_mass=0;cells=[]
    for e in expected['entities']:
        if 'mass_g' in e:
            roles[e['role']]+=e['mass_g']
            if e['name'].startswith('D0_P0_') and e['role'] not in ('service_cell','tray'):petal_mass+=e['mass_g']
        if 'constituent_volumes_mm3' not in e:continue
        recipe=expected['materials'][e['material']]
        # Materials builder adds residual Air when the positive recipe is sparse.
        constituents=e['constituent_volumes_mm3'];volume=sum(constituents.values())
        if volume>e['volume_mm3']+1e-8:errors.append(e['name']+': constituent overfill')
        cells.append(dict(name=e['name'],role=e['role'],represented_volume_mm3=volume,
            cell_volume_mm3=e['volume_mm3'],mean_fill=volume/e['volume_mm3'],
            packing_passed=volume/e['volume_mm3']<=c['packing_fraction'],material=e['material']))
        mass=sum(v*expected['materials'][mat]['density_g_cm3']/1000 for mat,v in constituents.items())
        mass+=(e['volume_mm3']-volume)*expected['materials']['Air']['density_g_cm3']/1000
        if not math.isclose(mass,e['mass_g'],rel_tol=1e-10):errors.append(e['name']+': normalization mismatch')
    b=2*236*math.sin(math.pi/12);t=.15;offset=2.675
    I=2*b*(t**3/12+t*offset**2);L=678-243;q=(petal_mass/1000*9.81)/L
    beam=[]
    for E in (70,100,140):
        d=5*q*L**4/(384*E*1000*I)
        beam.append(dict(E_GPa=E,normal_acceleration_m_s2=9.81,span_mm=L,minimum_width_mm=b,section_I_mm4=I,
            deflection_mm=d,goal_mm=.05,passed=d<=.05))
    result=dict(status='PASS' if not errors else 'FAIL',scope='Conservation check and engineering screens; no qualification',errors=errors,execution=execution(),
        expected_sha256=sha(expectedfile),producer_sha256=sha(__file__),role_mass_g=dict(roles),local_petal_mass_g=petal_mass,cells=cells,
        local_fan_maximum_mean_fill=max(e['mean_fill'] for e in cells if e['name'].startswith('D') and e['role']=='service_cell'),
        beam=beam,limitations=['Normal1g load is a beam fixture, not installed gravity or shell/joint FEA.',
            'Cold pickups, adhesive stress, frame joints and services need expert qualification.',
            'Mean cell fill cannot demonstrate individual cable bends or continuous connector routing.'])
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],errors,'petal mass',petal_mass,'g');return not errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();raise SystemExit(0 if run(a.expected,a.output) else 1)
