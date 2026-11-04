#!/usr/bin/env python3
"""Retain configuration, hashes and counts; never copy event-level payloads."""
import argparse
import gzip
import json
from pathlib import Path
import shutil

from analyze import MOMENTA, sha


REPORT_FIELDS = (
    'schema_version', 'status', 'outcome', 'baseline', 'simulation', 'pt_GeV',
    'events', 'threads', 'seed', 'campaign', 'training', 'pilot',
    'scientific_input_revision', 'analysis_source_revision_at_launch',
    'executed_source_sha256', 'command', 'geometry_source_revision',
    'native_binaries', 'error_table', 'digitization_sensors_by_system',
    'counts', 'provenance', 'output_sha256', 'ROOT', 'wall_seconds')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    reports = {}
    cases = [f'performance/{baseline}-pt{pt}' for baseline in ('old', 'current') for pt in MOMENTA]
    for name in ['training-current', *cases]:
        source = args.input / name / 'run-report.json'
        report = json.loads(source.read_text())
        if report['outcome'] != 'completed' or report['pilot']:
            raise ValueError('Cannot retain incomplete or pilot campaign: ' + name)
        reports[name] = {key: report[key] for key in REPORT_FIELDS}
        reports[name]['local_report_sha256'] = sha(source)
        reports[name]['local_report_path'] = str(source)
    retained = {}
    for name in ('hit-error-parameterization.json', 'hit-error-parameterization-raw.json',
                 'hit-error-training-audit.json'):
        source = args.input / 'calibration-current' / name
        shutil.copyfile(source, args.output / name)
        retained[name] = sha(source)
    # These are compact commands or scalar regression checks, not event arrays.
    for name in ('calibration-command.json', 'contract.json',
                 'old-pt1-reference-equality.json', 'old-pt1-central-regression.json'):
        source = args.input / name
        shutil.copyfile(source, args.output / name)
        retained[name] = sha(source)
    payload = {'schema_version': 1, 'status': 'PROTOTYPE',
        'retention': 'Configuration, provenance, counts and output hashes only; ROOT/events remain local and ignored',
        'retainer_sha256': sha(__file__), 'retained_files_sha256': retained, 'runs': reports}
    (args.output / 'runs.json.gz').write_bytes(gzip.compress(
        (json.dumps(payload, indent=2, allow_nan=False) + '\n').encode(), mtime=0))


if __name__ == '__main__':
    main()
