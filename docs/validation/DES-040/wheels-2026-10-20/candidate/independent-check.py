#!/usr/bin/env python3
"""Portable numerical cross-check of the frozen DES040 wheel candidate.

This is a separately executed algorithm check, not an independent specialist
assessment or detector-efficiency calculation. All sampling directions are
conditional on each ideal annulus's full-depth angular acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import numpy as np


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd(),help='repository root')
    parser.add_argument('--output',type=Path,default=Path(__file__).with_suffix('.json'))
    parser.add_argument('--samples',type=int,default=524288,help='directions per wheel')
    parser.add_argument('--seed',type=int,default=400201)
    args=parser.parse_args()
    if args.samples<2:raise ValueError('at least two samples required')
    root=args.root.resolve();sys.path.insert(0,str(root))
    from tools.muon_layout import geometry as g
    folder=root/'docs/validation/DES-040/wheels-2026-10-20/candidate'
    geometry_path=folder/'geometry.json';controls_path=folder/'geometry-controls.json'
    data=json.loads(geometry_path.read_text());controls=json.loads(controls_path.read_text())
    start=time.monotonic();rng=np.random.default_rng(args.seed);rows={}
    for key in ['inner_wheel','outer_wheel']:
        spec=data['wheel_revision'][key];z=spec['abs_z_m'];h=data['wheel_revision']['depth_m']/2
        # The ray must remain outside the bore on the near face and within
        # the outer radius on the far face. Uniform cos(theta) is uniform dOmega.
        lower=1/math.sqrt(1+(spec['outer_radius_m']/(z+h))**2)
        upper=1/math.sqrt(1+(spec['inner_radius_m']/(z-h))**2)
        mu=rng.uniform(lower,upper,args.samples);phi=rng.uniform(0,2*math.pi,args.samples)
        r=np.sqrt(1-mu*mu);directions=np.column_stack((r*np.cos(phi),r*np.sin(phi),mu))
        hit=np.zeros(args.samples,bool);active=np.zeros(args.samples,bool)
        for body in data['panels']:
            if body.get('wheel')!=key or body['side']!=1:continue
            hit|=np.isfinite(g.midplane_hits(body,directions,0,True))
            active|=np.isfinite(g.midplane_hits(body,directions,.03,True))
        reference=controls['straight_wheel_gap_diagnostic']['wheels'][key];row={}
        for label,accepted,expected in [
            ('envelope',hit,reference['envelope_gap_fraction_within_ideal_annulus']),
            ('border_inset',active,reference['border_inset_loss_fraction_within_ideal_annulus'])]:
            value=float((~accepted).mean());error=math.sqrt(value*(1-value)/args.samples)
            difference=value-expected
            row[label]=dict(mc_loss=value,analytic_loss=expected,standard_error=error,
                            difference=difference,z_score=difference/error,
                            passed=abs(difference)<=5*error)
        rows[key]=row
    assert all(value['passed'] for row in rows.values() for value in row.values())
    assert len(data['panels'])==1344
    assert all(body['coil_certificate']['clear'] and body['support_certificate']['clear'] for body in data['panels'])
    assert not controls['panel_validation']['panel_panel_conflicts']
    assert controls['panel_validation']['unresolved_cells_accepted']==0
    assert controls['support_validation']['valid'] and not controls['support_validation']['ungrounded_cases']
    old=json.loads((root/'docs/validation/DES-040/geometry.json').read_text())
    def middle(value):
        return {body['id']:{k:v for k,v in body.items() if k not in ['coil_certificate','support_certificate']}
                for body in value['panels'] if body['kind']=='endcap' and body['station']==2}
    assert middle(old)==middle(data)
    old_members={body['id']:body for body in old['supports']['members']}
    unchanged=[body for body in data['supports']['members'] if '-front/LUG' not in body['id']]
    assert all(body==old_members[body['id']] for body in unchanged)
    assert len(controls['frame_changes']['changed_members'])==48
    script=Path(__file__).resolve()
    def rel(path):
        path=Path(path).resolve()
        return str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    sources=[geometry_path,controls_path,root/'tools/muon_layout/wheels.py',
             root/'tools/muon_layout/wheels-config.json',root/'tools/muon_layout/geometry.py',
             root/'docs/validation/DES-040/geometry.json',script]
    result=dict(passed=True,input_revision=data['wheel_revision']['input_revision'],
        geometry_sha256=sha(geometry_path),controls_sha256=sha(controls_path),
        sources={rel(path):sha(path) for path in sources},seed=args.seed,samples_per_wheel=args.samples,
        method='iid directions uniform in solid angle of ideal full-depth annulus; independent direct convex-face crossings',
        five_standard_error_agreement_gate=True,results=rows,
        middle216_exact_retention=True,unchanged_frame_members_exact=len(unchanged),
        checks=['1344 coil/support certificates','zero overlaps/unresolved cells','36 case ground graph','48 changed front lugs'],
        command=['python',rel(script),'--root','.','--output',rel(args.output),'--samples',str(args.samples),'--seed',str(args.seed)],
        argv_paths='repository-relative; executed from repository root',
        runtime=dict(python=platform.python_version(),numpy=np.__version__,seconds=time.monotonic()-start),
        scope='geometric algorithm check only; sampling standard errors do not include geometry uncertainty or detector response')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
