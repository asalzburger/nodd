#!/usr/bin/env python3
"""Independent finite-plane coverage, occupied-box and beam-sag screens."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import sys

from model import ROOT,INPUT,load,build,sha
sys.path.insert(0,str(ROOT/"tools/module_layout"))
from geometry import body_overlap_diagnostics
from intersections import SurfaceIndex, ideal_layer_hits, _radial_paths


def check(c,layout,expected,refined=False):
    bodies=[dict(m,half_u_mm=24.5,half_v_mm=51.5,half_w_mm=.625,
                  center_mm=[m['center_mm'][i]-.4*m['n'][i] for i in range(3)],
                  level=m['row']%2,subsystem='short_strip') for m in layout['modules']]
    collisions=body_overlap_diagnostics(dict(bodies=bodies))
    oracle=SurfaceIndex(layout)
    levels=[dict(kind='cylinder',id=i,r_m=r/1000,z_min_m=-1.2,z_max_m=1.2) for i,r in enumerate(c['nominal_radii_mm'])]
    samples=[]
    nphi=128 if refined else 64
    neta=161 if refined else 81
    for origin in ([0,0,-150],[0,0,0],[0,0,150],[-1,-1,-150],[1,1,150]):
        for k in range(neta):
            eta=-4+8*k/(neta-1)
            for j in range(nphi):
                # Off-grid phi phase; points do not simply follow stave centres.
                samples.append(dict(origin_mm=origin,eta=eta,phi=2*math.pi*(j+.371)/nphi,pt_GeV=1,field_T=4))
    result=[]
    for mode,charge,field in (('straight',0,0),('positive',1,4),('negative',-1,4)):
        expected_hits=misses=extra=interior_misses=0;examples=[];by_layer=defaultdict(lambda:dict(eligible=0,missed=0))
        for original in samples:
            track=dict(original,charge=charge,field_T=field)
            eligible=set(ideal_layer_hits(levels,track,host_radius_mm=800,host_half_z_mm=1400))
            hitset={layout['modules'][i]['layer'] for i,s in oracle.hits(track,host_radius_mm=800,host_half_z_mm=1400)}
            missed=eligible-hitset
            expected_hits+=len(eligible);misses+=len(missed);extra+=len(hitset-eligible)
            for layer in eligible:
                by_layer[layer]['eligible']+=1;by_layer[layer]['missed']+=(layer in missed)
            margins={}
            for layer in missed:
                crossing=_radial_paths(track,c['nominal_radii_mm'][layer],3000)[0]
                margin=1200-abs(track['origin_mm'][2]+crossing*math.sinh(track['eta']))
                margins[layer]=float(margin)
                interior_misses+=int(margin>100)
            if missed and len(examples)<20:examples.append(dict(track=track,missed_layers=sorted(missed),
                distance_to_nominal_end_mm=margins))
        result.append(dict(mode=mode,tracks=len(samples),eligible_ideal_crossings=expected_hits,
            missed_ideal_crossings=misses,extra_layer_crossings=extra,by_layer=dict(by_layer),examples=examples,
            interior_misses_beyond_100mm_end_band=interior_misses,passed=misses==0))
    # Simply supported sandwich beam; measured constituent mass from export.
    # Use exact prefix selection to avoid suffix conventions assigning parts incorrectly.
    mass_by_stave=defaultdict(float)
    for e in expected['entities']:
        if e['name'].startswith('L') and '_S' in e['name']:
            mass_by_stave['_'.join(e['name'].split('_')[:2])]+=e.get('mass_g',0)
    mass=max(mass_by_stave.values())
    width=c['stave_width_mm']; I=2*(width*.15**3/12+width*.15*(2.675**2))
    q=mass/1000*9.80665/(2*c['stave_half_length_mm'])
    span=max(b-a for a,b in zip(c['bearing_z_mm'],c['bearing_z_mm'][1:]))
    sag=[dict(E_GPa=E,span_mm=span,mass_per_stave_g=mass,second_moment_mm4=I,
        sag_mm=5*q*span**4/(384*E*1000*I),passed=5*q*span**4/(384*E*1000*I)<=c['sag_limit_mm'])
        for E in c['E_GPa']]
    return dict(scope='PROTOTYPE finite-sample coverage and simplified beam screen',
        occupied_bodies=collisions,coverage=result,beam=sag,
        source_hashes=dict(check_layout=sha(__file__),geometry=sha(ROOT/'tools/module_layout/geometry.py'),
            oracle=sha(ROOT/'tools/module_layout/intersections.py'),input=sha(INPUT)),
        sample=dict(eta=[-4,4],eta_points=neta,phi_points=nphi,phi_phase=.371,
            origins_mm=[list(o) for o in ([0,0,-150],[0,0,0],[0,0,150],[-1,-1,-150],[1,1,150])],
            pt_GeV=1,field_T=4,random_seed=None),
        limitations=['Ideal eligible cylinders are a fixed denominator; barrel-end differences remain visible.',
            'No continuum hermeticity proof, energy loss, detector response or tracking resolution.',
            'Beam estimate ignores joints, torsion, service forces, composite anisotropy and dynamics.',
            'End boards and local feet are conservatively spread into line load; rings excluded; global support requires FEA.'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,default=INPUT)
    p.add_argument('--expected',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--refined',action='store_true');a=p.parse_args()
    c=load(a.input);result=check(c,build(c),json.loads(a.expected.read_text()),a.refined)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(collisions=result['occupied_bodies']['overlapping_body_pairs'],
        coverage=[(x['mode'],x['missed_ideal_crossings']) for x in result['coverage']],beam=result['beam']),indent=2))
