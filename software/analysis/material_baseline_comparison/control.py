#!/usr/bin/env python3
"""Compare supplied PR109 and current recordings using their exact common rays."""
import argparse
import json
from pathlib import Path

import numpy as np
import uproot

from compare import sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pr109', type=Path, required=True)
    ap.add_argument('--current', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    branches = ['event_id','v_x','v_y','v_z','v_px','v_py','v_pz','v_eta','v_phi','t_X0','t_L0']
    samples = []
    for path in (args.pr109, args.current):
        with uproot.open(path) as f:
            samples.append(f['material_tracks'].arrays(branches, library='np'))
    equal = {k: bool(np.array_equal(samples[0][k], samples[1][k])) for k in branches if not k.startswith('t_')}
    if not all(equal.values()) or len(samples[0]['v_eta']) != 100000:
        raise ValueError('Control requires the identical 100000 generated rays')
    report = {'samples': ['PR109 supplied 2 mm before reduced services', 'current PR110+112 geometry'],
        'rays': 100000, 'exact_equal_ray_branches': equal, 'quantities': {},
        'pr109_sha256': sha(args.pr109), 'current_sha256': sha(args.current), 'control_sha256': sha(__file__),
        'attribution': 'PR109 to current changes the short-strip redesign package, including modules, cooling/services and added endcap sensors; not cable-only or pitch-only savings.',
        'uncertainty': 'Paired finite-ray sampling SEM of the absolute material difference; geometry model uncertainties omitted'}
    for q in ('X0', 'L0'):
        a, b = [s['t_'+q].astype(float) for s in samples]
        difference = a-b
        report['quantities'][q] = {'pr109_mean': float(a.mean()), 'current_mean': float(b.mean()),
            'difference_mean': float(difference.mean()), 'fractional_reduction': float(1-b.mean()/a.mean()),
            'paired_ray_sampling_sem': float(np.std(difference)/np.sqrt(len(difference)))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(report['quantities'], indent=2))


if __name__ == '__main__':
    main()
