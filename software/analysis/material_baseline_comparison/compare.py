#!/usr/bin/env python3
"""Retain common eta bins and finite-ray statistics for two material baselines."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

COLORS = {"beam_pipe": "#ffcc66", "pixel": "#0066cc",
          "short_strip": "#ff9933", "long_strip": "#009999"}
COMPONENTS = [f"{d}_{s}" for d in COLORS for s in ("nonsensitive", "sensitive")]
EDGES = np.linspace(-4., 4., 81)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def crop(group):
    """Select whole aligned bins; never interpolate means or pool unlike eta bins."""
    edges = np.asarray(group['edges'], dtype=float)
    start = np.flatnonzero(np.isclose(edges, EDGES[0], rtol=0, atol=1e-12))
    if len(start) != 1:
        raise ValueError('Missing common lower eta edge')
    start = int(start[0]); end = start + len(EDGES) - 1
    if not np.allclose(edges[start:end+1], EDGES, rtol=0, atol=1e-12):
        raise ValueError('Common eta bins must align exactly')
    def subset(values):
        result = np.asarray(values)[start:end]
        if len(result) != 80 or not np.all(np.isfinite(result)):
            raise ValueError('Incomplete or nonfinite profile')
        return result.tolist()
    result = {'edges': EDGES.tolist(), 'quantities': {}}
    if 'counts' in group:
        result['counts'] = subset(group['counts'])
    for q in ('X0', 'L0'):
        source = group['quantities'][q]
        if 'total' in source:
            result['quantities'][q] = {name: {stat: subset(source[name][stat])
                for stat in ('mean', 'variance')} for name in [*COMPONENTS, 'total']}
        else:
            result['quantities'][q] = {stat: subset(source[stat])
                for stat in ('counts', 'mean', 'variance')}
    return result


def ratio(numerator, denominator):
    """ACTS/G4 mean with ACTS finite-ray SEM only, fixing map and denominator."""
    a, b = np.asarray(numerator['mean']), np.asarray(denominator['mean'])
    va = np.asarray(numerator['variance'])
    valid = np.isfinite(a) & np.isfinite(b) & np.isfinite(va) & (b > 0) & (va >= 0)
    return {'mean': [float(a[i]/b[i]) if ok else None for i, ok in enumerate(valid)],
            'variance': [float(va[i]/b[i]**2) if ok else None for i, ok in enumerate(valid)],
            'valid': valid.tolist()}


def eta_average(values):
    """Equal-width eta-bin average, avoiding different sample occupancy weights."""
    return float(np.mean(values))


def assemble(old_truth, old_acts, new_truth, new_acts):
    out = {'schema_version': 1, 'axis': 'signed pseudorapidity eta',
           'edges': EDGES.tolist(), 'colors': COLORS,
           'passive_alpha': .5, 'sensitive_alpha': 1., 'baselines': {},
           'normalization': 'Per generated ray, including zero contributions, within each eta bin',
           'variance_convention': 'ROOT population SEM squared M2/N^2',
           'ratio_uncertainty': 'ACTS finite-ray sampling SEM only, conditional on fixed material map and Geant4 bin means; map training uncertainty and numerator/denominator covariance omitted',
           'sensitivity_caveat': 'DD4hep sensitive-volume flag; rounding-cell ambiguity diagnostics are detected-only, not an exhaustive allocation uncertainty bound',
           'summary': {}}
    for name, truth, acts in [('old', old_truth, old_acts), ('current', new_truth, new_acts)]:
        g4, reco = crop(truth['axes']['eta']), crop(acts['axes']['eta'])
        n = np.asarray(g4['counts'])
        if np.any(n <= 1) or np.any(n != np.floor(n)):
            raise ValueError('Insufficient or noninteger Geant4 occupancy')
        if truth['classification']['unassigned_steps'] or truth['classification']['density_mismatches']:
            raise ValueError('Incomplete component classification')
        ratios = {}
        for q in ('X0', 'L0'):
            components = g4['quantities'][q]
            np.testing.assert_allclose(sum(np.array(components[c]['mean']) for c in COMPONENTS),
                                       components['total']['mean'], rtol=2e-13, atol=2e-14)
            for entry in components.values():
                if np.any(np.array(entry['mean']) < 0) or np.any(np.array(entry['variance']) < 0):
                    raise ValueError('Negative material or variance')
            if np.any(np.array(reco['quantities'][q]['counts']) <= 1):
                raise ValueError('Insufficient ACTS occupancy')
            ratios[q] = ratio(reco['quantities'][q], components['total'])
        out['baselines'][name] = {'geant4': g4, 'acts': reco, 'ratio': ratios,
            'selected_geant4_rays': int(n.sum()),
            'selected_acts_rays': int(sum(reco['quantities']['X0']['counts'])),
            'classification': truth['classification'], 'checks': truth['checks']}
    for q in ('X0', 'L0'):
        out['summary'][q] = {}
        for component in ['total', 'short_strip', 'pixel', 'long_strip', 'beam_pipe']:
            means = {}
            for baseline, data in out['baselines'].items():
                g = data['geant4']['quantities'][q]
                values = np.array(g['total']['mean']) if component == 'total' else sum(
                    np.array(g[f'{component}_{s}']['mean']) for s in ('sensitive', 'nonsensitive'))
                means[baseline] = eta_average(values)
            out['summary'][q][component] = {**means,
                'fractional_reduction': 1-means['current']/means['old'] if means['old'] > 0 else None}
    out['summary_definition'] = 'Equal-weight mean of 80 eta-bin means over [-4,4]; descriptive baseline change, no significance or cable-only attribution'
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('old-truth', 'old-acts', 'current-truth', 'current-acts'):
        parser.add_argument('--'+key, type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    paths = [args.old_truth, args.old_acts, args.current_truth, args.current_acts]
    out = assemble(*(json.loads(p.read_text()) for p in paths))
    out['sources'] = {key: {'name': p.name, 'sha256': sha(p)} for key, p in zip(
        ('old_truth', 'old_acts', 'current_truth', 'current_acts'), paths)}
    out['analysis_sha256'] = sha(__file__)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    print(json.dumps(out['summary'], indent=2))


if __name__ == '__main__':
    main()
