#!/usr/bin/env python3
"""Attach descriptive unbinned quantiles without altering a closed response run.

The original frozen producer omitted protocol-required quantiles. This separate
post-run attachment preserves its output, gates, event selection and seeds.
Only population quantiles are exported; event diagnostics remain local.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

PROBABILITIES = [0, .01, .05, .16, .5, .84, .95, .99, 1]
STAGES = ['raw', 'off', 'on']


def sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def checked_totals(row, population):
    """Read every event from the exact closed diagnostics, keeping zero totals."""
    if row['kind'] != 'showers' or row['sample']['kind'] != 'showers':
        raise ValueError('Expected a shower population')
    sample, receipt = row['sample'], row['receipt']
    identity = (row['geometry'], sample['particle'], sample['energy_GeV'], sample['eta'])
    expected = (population['geometry'], population['particle'], population['momentum_GeV'], population['eta'])
    if (identity != expected or row['geometry'] != sample['geometry']
            or receipt['exit_code'] or receipt['identity']['input_sha256'] != sample['sha256']
            or population['input_sha256'] != sample['sha256']
            or sha(row['diagnostics']) != receipt['output_sha256']
            or population['native_output_sha256'] != receipt['output_sha256']):
        raise ValueError('Changed population, source input or native diagnostics')
    values = []
    with Path(row['diagnostics']).open() as source:
        for line in source:
            event = json.loads(line)
            if event['index'] != len(values) or event['identity'] != [sample['actual_run_number'], len(values)]:
                raise ValueError('Changed event order or identity')
            values.append([event['raw_GeV'], event['modes']['off']['energy_GeV'], event['modes']['on']['energy_GeV']])
    x = np.asarray(values, dtype=float)
    if (x.shape != (population['n'], 3) or len(x) != sample['requested_events']
            or not np.isfinite(x).all() or np.any(x < 0)):
        raise ValueError('Invalid or incomplete event totals')
    for i, stage in enumerate(STAGES):
        stats = population['stages'][stage]['energy_GeV']
        # Same unrounded totals and NumPy conventions must reproduce exactly.
        if (stats['n'] != len(x) or stats['mean'] != float(x[:, i].mean())
                or stats['SD'] != float(x[:, i].std(ddof=1))
                or stats['zero_count'] != int(np.sum(x[:, i] == 0))):
            raise ValueError('Event totals do not reproduce the closed moments')
    return x


def attach(response_path, runs_path):
    response = json.loads(response_path.read_text())
    if (response['scope'] != 'Complete frozen 48-population study'
            or response['provenance']['native_runs_sha256'] != sha(runs_path)):
        raise ValueError('A closed full response and its exact native run inventory are required')
    runs = json.loads(runs_path.read_text())
    populations = response['showers']['populations']
    rows = [r for r in runs if r['kind'] == 'showers']
    if len(runs) != 48 or len(rows) != 38 or len(populations) != 38:
        raise ValueError('Expected the complete 38-shower population inventory')
    source = Path(__file__).with_name('nodd_response.py')
    if sha(source) != response['provenance']['analysis_sha256']:
        raise ValueError('Frozen response producer changed')
    result = []
    for row, population in zip(rows, populations, strict=True):
        x = checked_totals(row, population)
        energy = population['primary_total_energy_GeV']
        if not np.isfinite(energy) or energy <= 0:
            raise ValueError('Invalid generated total energy')
        factor = response['showers']['calibration'][str(population['eta'])]['factor']
        if not np.isfinite(factor) or factor <= 0:
            raise ValueError('Invalid closed common calibration')
        q = np.quantile(x, PROBABILITIES, axis=0, method='linear')
        result.append(dict(geometry=population['geometry'], particle=population['particle'],
            momentum_GeV=population['momentum_GeV'], eta=population['eta'], n=len(x),
            primary_total_energy_GeV=energy, common_calibration_factor=factor,
            input_sha256=population['input_sha256'], native_output_sha256=population['native_output_sha256'],
            stages={stage: dict(energy_GeV=q[:, i].tolist(),
                                visible_fraction=(q[:, i]/energy).tolist(),
                                common_scale_response=(q[:, i]*factor/energy).tolist())
                    for i, stage in enumerate(STAGES)}))
    return dict(status='PROTOTYPE descriptive attachment to unchanged closed response',
        convention=dict(probabilities=PROBABILITIES, method='NumPy quantile linear interpolation',
            selection='All generated events, including zero totals; no histogram approximation',
            timing='Descriptive probability grid specified after execution; no acceptance gate or retuning'),
        provenance=dict(response_sha256=sha(response_path), native_runs_sha256=sha(runs_path),
            closed_response_provenance=response['provenance'], producer_sha256=sha(__file__),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            NumPy=np.__version__), populations=result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--response', type=Path, required=True)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink() or args.output.resolve() in (args.response.resolve(), args.runs.resolve()):
        raise ValueError('Choose a fresh attachment path; closed inputs are reserved')
    data = attach(args.response, args.runs)
    with args.output.open('x') as target:
        json.dump(data, target, indent=2, allow_nan=False)
        target.write('\n')


if __name__ == '__main__':
    main()
