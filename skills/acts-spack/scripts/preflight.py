#!/usr/bin/env python3
"""Read-only node/fingerprint checks; not a replacement for runtime verification."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import sys


def inspect(registry, hostname, require_sources=False):
    node = next((n for n in registry['nodes'] if n['hostname'] == hostname), None)
    result = dict(hostname=hostname, status='unverified', warnings=[])
    if node is None:
        result['warnings'].append('ACTS Spack workflow is unverified on this node; '
                                  'no matching node record. Verify the local setup before use.')
        return result
    result['verified_at'] = node['verified_at']
    missing, changed = [], []
    for filename in node['required_files']:
        if not Path(filename).is_file():
            missing.append(filename)
    for name, record in node['fingerprints'].items():
        try:
            current = hashlib.sha256(Path(record['path']).read_bytes()).hexdigest()
        except OSError:
            current = None
        if current != record['sha256']:
            changed.append(name)
    if missing:
        result['status'] = 'unavailable'
        result['warnings'].append('ACTS Spack workflow prerequisites unavailable: ' + ', '.join(missing))
    if changed:
        result['warnings'].append('Recorded environment changed or is unreadable; re-verify: ' + ', '.join(changed))
    if require_sources:
        for package, source in node['source_trees'].items():
            if not source or not (Path(source)/'CMakeLists.txt').is_file():
                result['warnings'].append(f'{package} full source tree is not available in the node record; '
                                          'recheck spack location --source-dir before source-level work.')
    if not result['warnings']:
        result['status'] = 'prerequisites-present'
        result['note'] = 'Recorded files/fingerprints match. Activate and rerun required runtime checks.'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path,
                        default=Path(__file__).resolve().parents[1]/'references/nodes.json')
    parser.add_argument('--require-sources', action='store_true')
    args = parser.parse_args()
    try:
        result = inspect(json.loads(args.registry.read_text()), socket.gethostname(), args.require_sources)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('WARNING: ACTS Spack node registry cannot be checked: ' + str(error), file=sys.stderr)
        return 2
    for warning in result['warnings']:
        print('WARNING: ' + warning, file=sys.stderr)
    print(json.dumps(result, indent=2))
    return 2 if result['warnings'] else 0


if __name__ == '__main__':
    sys.exit(main())
