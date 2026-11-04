#!/usr/bin/env python3
"""Reduce independent ACTS validation rays to common eta bins without pull claims."""
import argparse
import json
from pathlib import Path

import numpy as np
import uproot

from compare import EDGES, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--expected-tracks', type=int, default=100000)
    args = ap.parse_args()
    with uproot.open(args.input) as source:
        data = source['material_tracks'].arrays(['v_eta', 't_X0', 't_L0'], library='np')
    n = len(data['v_eta'])
    if n != args.expected_tracks or not all(np.all(np.isfinite(x)) for x in data.values()):
        raise ValueError('Invalid validation sample')
    index = np.searchsorted(EDGES, data['v_eta'], side='right')-1
    if np.any((index < 0) | (index >= 80)):
        raise ValueError('Validation rays outside common eta support')
    counts = np.bincount(index, minlength=80)
    if np.any(counts <= 1):
        raise ValueError('Insufficient bin occupancy')
    result = {'tracks': n, 'axes': {'eta': {'edges': EDGES.tolist(), 'quantities': {}}},
              'source_validation_sha256': sha(args.input), 'reducer_sha256': sha(__file__),
              'normalization': 'Every generated ray, including zero material; M2/N^2 SEM squared'}
    for q in ('X0', 'L0'):
        values = data['t_'+q].astype(float)
        if np.any(values < 0):
            raise ValueError('Negative material')
        means = np.bincount(index, weights=values, minlength=80)/counts
        variance = np.maximum(0, np.bincount(index, weights=values*values, minlength=80)/counts-means**2)/counts
        result['axes']['eta']['quantities'][q] = {'counts': counts.tolist(),
            'mean': means.tolist(), 'variance': variance.tolist()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(f'PASS: {n:,} validation rays, {counts.min()} minimum rays/bin')


if __name__ == '__main__':
    main()
