#!/usr/bin/env python3
"""Inventory tracked blobs at an exact revision; never delete or rewrite evidence."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ('docs/validation/DES-011-optimization/cases/'
            'p190-s680-b1-l1287.33-front_loaded-original-pockets/layout.json.gz')
HISTORICAL = ('DES-009-module-coverage', 'DES-009-review-default',
              'DES-010-services', 'DES-011-optimization',
              'DES-011-optimization-rejected-even-rows',
              'DES-011-optimization-rejected-pocket-depths')
NUMERICAL = ('summary.json', 'layout.json.gz', 'study.json', 'study.json.gz',
             'local-coverage-audit.json')
LARGE_BYTES = 1_000_000  # Inventory display threshold, not a detector requirement.


def classify(path, size):
    """Conservative triage, not a claim of demonstrated regeneration."""
    if path == BASELINE:
        return 'retain_dependency', 'frozen-tracker-input'
    if not path.startswith('docs/validation/'):
        return None
    parts = path.split('/')
    if (parts[2] in HISTORICAL and parts[-1] in NUMERICAL):
        return 'scheduled_after_prerequisites', 'historical-tracker-studies'
    if (parts[2] in ('tracker-reconstruction', 'tracker-reconstruction-species')
            and parts[-1] == 'events.npz'):
        return 'scheduled_after_prerequisites', 'reconstruction-event-arrays'
    if path == 'docs/validation/gen3-material-mapping/scatter.npz':
        return 'retain_unknown_input', 'material-survey-scatter'
    if size >= LARGE_BYTES and path.endswith(('.json', '.json.gz', '.npz', '.root')):
        return 'review_required', 'other-large-numerical-evidence'
    if parts[-1] in ('ctest.txt', 'ctest.log', 'build.log', 'support-tests.txt'):
        return 'scheduled_after_prerequisites', 'test-stdout'
    return None


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)


def inventory(root, revision):
    if re.fullmatch(r'[0-9a-f]{40}', revision) is None:
        raise ValueError('revision must be a full 40-character commit SHA')
    if git(root, 'cat-file', '-t', revision).strip() != b'commit':
        raise ValueError('revision must identify a commit')
    entries = []
    for row in git(root, 'ls-tree', '-r', '-l', '-z', revision).split(b'\0'):
        if not row:
            continue
        meta, name = row.split(b'\t', 1)
        mode, kind, oid, size = meta.split()
        # Symlinks and submodules are not ordinary file payloads.
        if kind != b'blob' or mode not in (b'100644', b'100755'):
            continue
        entries.append({'path': name.decode('utf-8'), 'bytes': int(size),
                        'git_blob': oid.decode('ascii')})
    entries.sort(key=lambda entry: entry['path'])
    directories, suffixes, blobs, selected = Counter(), Counter(), defaultdict(list), []
    for entry in entries:
        path, size = entry['path'], entry['bytes']
        directories['/'.join(path.split('/')[:2])] += size
        suffixes[''.join(Path(path).suffixes) or '(none)'] += size
        blobs[entry['git_blob']].append(entry)
        group = classify(path, size)
        if group:
            # Read immutable Git bytes, never substituted working-tree data.
            payload = git(root, 'cat-file', 'blob', entry['git_blob'])
            selected.append({**entry, 'sha256': hashlib.sha256(payload).hexdigest(),
                             'state': group[0], 'group': group[1]})
    totals = Counter()
    counts = Counter()
    for entry in selected:
        totals[entry['state']] += entry['bytes']
        counts[entry['state']] += 1
    duplicates = [{'git_blob': oid, 'bytes_per_path': rows[0]['bytes'],
                   'paths': [entry['path'] for entry in rows]}
                  for oid, rows in sorted(blobs.items()) if len(rows) > 1
                  and rows[0]['bytes'] >= LARGE_BYTES]
    return {
        'schema_version': 1, 'source_revision': revision,
        'scope': 'Ordinary tracked files; excludes symlinks and submodule contents.',
        'policy': 'Triage only. All scheduled removals require the issue-120 plan prerequisites.',
        'large_file_threshold_bytes': LARGE_BYTES,
        'tracked_files': len(entries), 'tracked_bytes': sum(x['bytes'] for x in entries),
        'unique_blob_bytes': sum(rows[0]['bytes'] for rows in blobs.values()),
        'bytes_by_directory': dict(sorted(directories.items())),
        'bytes_by_suffix': dict(sorted(suffixes.items())),
        'triage_totals': {state: {'files': counts[state], 'bytes': totals[state]}
                          for state in sorted(totals)},
        'largest_files': sorted(entries, key=lambda x: (-x['bytes'], x['path']))[:25],
        'large_duplicate_blobs': duplicates, 'files': selected,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--output', type=Path, help='write a compact audit, not source payloads')
    parser.add_argument('--check', action='store_true', help='compare output without changing it')
    args = parser.parse_args(argv)
    try:
        if args.check and args.output is None:
            raise ValueError('--check requires --output')
        report = inventory(args.repo.resolve(), args.revision)
        content = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
        if args.check:
            if args.output.read_text() != content:
                raise ValueError('inventory differs from the recorded revision/rules')
            print(f'Verified {len(report["files"])} triaged files at {args.revision}.')
        elif args.output:
            # Never overwrite a retained audit: make a new named snapshot.
            with args.output.open('x') as stream:
                stream.write(content)
            print(f'Wrote {args.output}; no source files changed.')
        else:
            print(content, end='')
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
