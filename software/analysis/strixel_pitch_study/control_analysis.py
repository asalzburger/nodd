#!/usr/bin/env python3
"""Retain/replay the separate 100 GeV Gaussian-response diagnostic control."""
import argparse
import csv
import gzip
import json
from pathlib import Path

from analyze import ROOT, PITCHES, QUANTITIES, analyze, digest, dump_gzip, retain

MODEL = 'gaussian_pitch_over_sqrt12_no_merge'
SOURCE_SHA256 = digest(__file__)


def validate_control(inventory):
    reports = [item['report'] for item in inventory['reports']]
    matrix = [(r['pt_GeV'], r['pitch_mm']) for r in reports]
    if len(matrix) != 4 or set(matrix) != {(100., p) for p in PITCHES}:
        raise ValueError('Control needs exactly four pitches at 100 GeV')
    for report in reports:
        if report['requested_events'] != 5000 or report['outcome'] != 'completed':
            raise ValueError('Control requires four completed 5000-event cases')
        if report.get('response_model') != MODEL:
            raise ValueError('Gaussian control response label differs')
        fingerprints = report.get('control_source_sha256', {})
        required = {'repository/software/analysis/strixel_pitch_study/gaussian_control.py',
                    'repository/software/analysis/truth_tracking/metrics.py',
                    'repository/software/analysis/truth_tracking/smearing.py'}
        if not required.issubset(fingerprints):
            raise ValueError('Missing separate control source fingerprints')
        for logical, expected in fingerprints.items():
            if logical.startswith('repository/') and digest(ROOT / logical.removeprefix('repository/')) != expected:
                raise ValueError('Control source differs: ' + logical)
        for logical, expected in report['preparation']['files_sha256'].items():
            if logical.startswith('repository/software/') and digest(ROOT / logical.removeprefix('repository/')) != expected:
                raise ValueError('Executed repository source differs: ' + logical)
    if any(r['control_source_sha256'] != reports[0]['control_source_sha256'] for r in reports):
        raise ValueError('Control source bytes differ across pitches')


def compute(directory, inventory, replicates=400):
    validate_control(inventory)
    result = analyze(directory, inventory, replicates=replicates, pilot=True, write=False)
    result['response'] = 'Independent Gaussian hit errors, sigma=pitch/sqrt(12), all measured coordinates, doMerge=False'
    result['response_model'] = MODEL
    result['sample_kind'] = 'Separate 100 GeV response diagnostic; not a replacement for the twelve-case digital campaign'
    result['events_per_case'] = 5000
    result['provenance']['control_analyzer_sha256'] = SOURCE_SHA256
    if digest(__file__) != SOURCE_SHA256:
        raise ValueError('Control analysis source changed during execution')
    return result


def write_csv(path, data):
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['pitch_v_mm', 'projection', 'eta_low', 'eta_high', 'generated',
                         'finite_fit', 'quantity', 'width68', 'width68_se', 'std',
                         'pull_std', 'ratio', 'ratio_se'])
        for case in data['groups'][0]['cases']:
            for projection in ('global', 'eta_profiles', 'abs_eta_profiles', 'summary_regions'):
                points = [case['global']] if projection == 'global' else case[projection]
                for point in points:
                    for q in QUANTITIES:
                        s = point['quantities'][q]
                        writer.writerow([case['pitch_v_mm'], projection, point.get('low'), point.get('high'),
                                         point['counts']['generated'], point['counts']['finite_fit'], q,
                                         s['residual']['width68'], s['residual']['width68_se'],
                                         s['residual']['std'], s['pull']['std'],
                                         s['residual']['ratio_to_baseline'], s['residual']['ratio_se']])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--pattern', default='gaussian-v1-*')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/validation/DES-042/gaussian-control')
    parser.add_argument('--replicates', type=int, default=400)
    parser.add_argument('--verify', action='store_true', help='Repeat the full deterministic bootstrap without overwriting evidence')
    args = parser.parse_args()
    inventory = (retain(args.source, args.output, args.pattern) if args.source else
                 json.loads(gzip.decompress((args.output/'native-reports.json.gz').read_bytes())))
    data = compute(args.output, inventory, args.replicates)
    if args.verify:
        saved = json.loads(gzip.decompress((args.output/'profiles.json.gz').read_bytes()))
        if data != saved:
            raise ValueError('Gaussian-control deterministic replay differs')
        print('PASS: four paired 5000-event Gaussian controls, exact sources and full bootstrap replay')
    else:
        dump_gzip(args.output/'profiles.json.gz', data)
        write_csv(args.output/'summary.csv', data)
        print('Retained and analyzed four separate 5000-event Gaussian controls')


if __name__ == '__main__':
    main()
