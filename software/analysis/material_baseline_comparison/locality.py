#!/usr/bin/env python3
"""Measure along-ray material displacement onto the current native portals."""
import argparse
import json
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

from compare import sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = {'definition': 'Absolute native sur_distance from recorded material midpoint to assigned finite portal intersection along ray; diagnostic thresholds without accuracy acceptance criteria',
        'steps': 0, 'maximum_distance_mm': 0., 'thresholds': {str(t): {'steps': 0, 'X0': 0., 'L0': 0.} for t in (10,50,100)},
        'sum_X0': 0., 'sum_L0': 0., 'source_mapped_sha256': sha(args.input), 'reducer_sha256': sha(__file__)}
    with uproot.open(args.input) as source:
        for arrays in source['material_tracks'].iterate(['sur_distance','mat_step_length','mat_X0','mat_L0'], step_size=1000, library='ak'):
            flatten = lambda key: ak.to_numpy(ak.flatten(arrays[key]))
            distance, length = abs(flatten('sur_distance')), flatten('mat_step_length')
            weights = {q: length/flatten('mat_'+q) for q in ('X0','L0')}
            if not np.all(np.isfinite(distance)):
                raise ValueError('Nonfinite mapping distance')
            result['steps'] += len(distance)
            result['maximum_distance_mm'] = max(result['maximum_distance_mm'], float(distance.max()))
            for q, w in weights.items():
                result['sum_'+q] += float(w.sum(dtype=float))
            for threshold, group in result['thresholds'].items():
                mask = distance > float(threshold)
                group['steps'] += int(mask.sum())
                for q, w in weights.items():
                    group[q] += float(w[mask].sum(dtype=float))
    for group in result['thresholds'].values():
        for q in ('X0','L0'):
            group[q+'_fraction'] = group[q]/result['sum_'+q]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
