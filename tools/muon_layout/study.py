#!/usr/bin/env python3
"""Reproduce/check DES040, leaving every DES039 artifact untouched."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.muon_layout.layout import inputs,build_layout
from tools.muon_layout.support import build_supports,validate_supports,support_mass
from tools.muon_layout.coverage import evaluate,compare_sampling,integrate
from tools.muon_layout.geometry import vertices3


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def outlines(path,panels):
    lines=['# DES040 chamber envelope edges only, metres; no detector internals']
    edges=[(i,(i+1)%4) for i in range(4)]+[(i+4,(i+1)%4+4) for i in range(4)]+[(i,i+4) for i in range(4)]
    for k,body in enumerate(panels):
        lines.append('o '+body['id'].replace('/','_'))
        lines.extend('v '+' '.join(f'{x:.12g}' for x in point) for point in vertices3(body))
        lines.extend(f'l {8*k+a+1} {8*k+b+1}' for a,b in edges)
    path.write_text('\n'.join(lines)+'\n')


def run(output):
    start=time.monotonic();c,magnetic=inputs();output.mkdir(parents=True,exist_ok=True)
    supports=build_supports(c);support_validation=validate_supports(supports,magnetic)
    if not support_validation['valid']:raise ValueError('support validation failed')
    print('Support contacts and coil clearances passed',flush=True)
    layout=build_layout(c,magnetic,supports)
    geometry=dict(configuration=c,magnetic_configuration=magnetic,supports=supports,**layout)
    save(output/'geometry.json',geometry)
    outlines(output/'chamber-outlines.obj',layout['panels'])
    print(f"Whole panels: {len(layout['panels'])}, without-support control: {len(layout['without_support_panels'])}",flush=True)
    cv=c['coverage'];coarse=evaluate(geometry,cv['mu_bins'],cv['phi_bins'])
    print('Coarse full-sphere quadrature done',flush=True)
    fine=evaluate(geometry,cv['refined_mu_bins'],cv['refined_phi_bins'])
    np.savez_compressed(output/'coverage.npz',**{k:v for k,v in fine.items() if k!='summary'})
    save(output/'coverage-summary.json',fine['summary'])
    print('Refined full-sphere map done; independent random integration follows',flush=True)
    integral=integrate(geometry,samples=cv['integration_samples'],seed=40087)
    mass_coarse=support_mass(supports['members'],samples=262144,seed=40036)
    mass=support_mass(supports['members'],samples=1048576,seed=40037)
    counts={kind:{str(j):sum(x['kind']==kind and x['station']==j for x in layout['panels']) for j in (1,2,3)} for kind in ('barrel','endcap')}
    sources=['tools/muon_layout/design.json','docs/validation/DES-040/support-input.json']
    sources += sorted(str(p.relative_to(ROOT)) for p in (ROOT/'tools/muon_layout').glob('*.py'))
    ch=c['chambers'];polar=1-ch['disk_abs_z_m'][0]/np.hypot(ch['disk_abs_z_m'][0],ch['disk_inner_r_m'])
    result=dict(status=c['status'],base_revision=c['base_revision'],units='m, kg, sr',
        inputs={p:digest(ROOT/p) for p in sources},magnetic_inputs={c[k]:c[k+'_sha256'] for k in ('magnetic_results','magnetic_map')},
        panel_counts=counts,packing=layout['packing'],without_support_packing=layout['without_support_packing'],
        chamber_validation=layout['validation'],support_validation=support_validation,support_mass=mass,support_mass_coarse=mass_coarse,
        coverage=fine['summary'],coarse_coverage=coarse['summary'],sampling=compare_sampling(coarse,fine),independent_integration=integral,
        analytic_beam_opening=dict(first_disk_only_fraction_4pi=float(polar),solid_angle_sr=float(4*np.pi*polar),
            half_angle_deg=float(np.degrees(np.arctan(ch['disk_inner_r_m']/ch['disk_abs_z_m'][0]))),
            scope='two polar cones through nominal first-disk bore; additional coil/module gaps separate'),
        limits=['geometric straight IP rays, no detector response, scattering or efficiency',
            'full-depth proxy is stricter than measurement-plane footprint',
            'support connectivity and self-mass do not certify strength, stiffness or energized forces',
            '30 mm border, 20 mm gaps and 50 mm installation clearance are unsigned choices',
            'mu_r=1 support proxies preserve pinned vacuum field; installed HCAL/steel solution absent',
            'no MDT internal geometry, chamber masses, electronics, services or chamber mounts',
            'support unique union mass has Monte Carlo sampling error; material/dimension uncertainty unquantified'],
        runtime=dict(python=platform.python_version(),numpy=np.__version__,seconds=time.monotonic()-start),
        artifacts={name:digest(output/name) for name in ('geometry.json','coverage.npz','coverage-summary.json','chamber-outlines.obj')})
    save(output/'results.json',result)
    print(json.dumps(dict(panels=counts,coverage=fine['summary']['fractions'],sampling=result['sampling'],seconds=result['runtime']['seconds']),indent=2),flush=True)
    return geometry,fine


def check(output):
    c,_=inputs();result=json.loads((output/'results.json').read_text())
    for path,sha in result['inputs'].items():
        if digest(ROOT/path)!=sha:raise ValueError('stale generated evidence: '+path)
    for name,sha in result['artifacts'].items():
        if digest(output/name)!=sha:raise ValueError('artifact mismatch: '+name)
    if result['magnetic_inputs']!={c[k]:c[k+'_sha256'] for k in ('magnetic_results','magnetic_map')}:
        raise ValueError('magnetic input mismatch')
    if not result['support_validation']['valid'] or result['chamber_validation']['panel_panel_conflicts']:
        raise ValueError('invalid saved geometry')
    with np.load(output/'coverage.npz',allow_pickle=False) as data:
        shape=(c['coverage']['refined_mu_bins'],c['coverage']['refined_phi_bins'])
        for key in ('outer','active','depth'):
            count=data[key+'_count'];assert count.shape==shape
            for n in range(4):
                assert abs(np.mean(count==n)-result['coverage']['fractions'][key][str(n)])<1e-12
        assert np.all(data['depth_count']<=data['active_count']) and np.all(data['active_count']<=data['outer_count'])
    print('DES040 input/artifact hashes and full-sphere station accounting passed')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'docs/validation/DES-040')
    parser.add_argument('--check',action='store_true');args=parser.parse_args()
    check(args.output) if args.check else run(args.output)
