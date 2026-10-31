#!/usr/bin/env python3
"""Verify a fresh completed GBTS repair replay against preserved failed audits."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / 'software/analysis/strixel_ttbar'))
    import campaign
    old = root / 'build/strixel-ttbar-production-v2'
    new = root / 'build/strixel-ttbar-production-v3'
    journal = root / 'logs/codex/SESSION-2026-10-31-strixel-ttbar-pu200'
    inventory = json.loads((journal / 'reconstruction-attempt-01.json').read_text())
    plan = json.loads((new / 'campaign-plan.json').read_text())
    if campaign.source_identity() != plan['source_sha256']:
        raise RuntimeError('Executing reconstruction sources changed')
    verification = campaign.verify(new, plan)
    cases = {}
    for pitch in campaign.PITCHES:
        label = f'{pitch:g}'
        before, after = old / f'pitch{label}', new / f'pitch{label}'
        expected = inventory['cases'][label]
        for name, digest in expected['files_sha256'].items():
            if sha(before / name) != digest:
                raise RuntimeError('Preserved failed report/log changed: ' + label + '/' + name)
        report = json.loads((after / 'run-report.json').read_text())
        if not report['event_audit']['all_native_survivors_converged']:
            raise RuntimeError('Fresh ambiguity convergence failed')
        rows = []
        for event in range(plan['events']):
            name = f'event{event:06d}.json.gz'
            a, b = before / 'audit' / name, after / 'audit' / name
            original, corrected = sha(a), sha(b)
            if original != expected['event_audit_inventory'][name]:
                raise RuntimeError('Preserved failed audit changed: ' + label + '/' + name)
            payload_a, payload_b = gzip.decompress(a.read_bytes()), gzip.decompress(b.read_bytes())
            if payload_a != payload_b:
                raise RuntimeError('Scientific reconstruction payload differs: ' + label + '/' + name)
            rows.append({'event': event, 'original_gzip_sha256': original,
                         'corrected_gzip_sha256': corrected,
                         'gzip_byte_identical': original == corrected,
                         'payload_sha256': hashlib.sha256(payload_a).hexdigest(),
                         'payload_byte_identical': True})
        cases[label] = {'events': len(rows), 'gzip_byte_identical_events': sum(r['gzip_byte_identical'] for r in rows),
                        'payload_byte_identical_events': len(rows), 'event_rows': rows,
                        'corrected_report_sha256': sha(after / 'run-report.json')}
    result = {'schema_version': 1, 'status': 'PASS', 'qualification': 'Failed original reports remain failed; fresh native monitoring, complete output hashes and exact scientific payload identity are verified independently.',
              'script_sha256': sha(Path(__file__)), 'native_campaign_verification': verification,
              'preserved_failure_inventory_sha256': sha(journal / 'reconstruction-attempt-01.json'),
              'original_reconstruction_revision': inventory['source_revision'],
              'corrected_reconstruction_revision': plan['source_revision'], 'cases': cases}
    if args.output.exists():
        raise ValueError('Choose a fresh proof output; preserve prior evidence')
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'PASS', 'case_events': sum(c['events'] for c in cases.values()),
                      'payload_byte_identical': sum(c['payload_byte_identical_events'] for c in cases.values())}))


if __name__ == '__main__':
    main()
