#!/usr/bin/env python3
"""Verify retained balanced-baseline execution and current source fingerprints.

This replays provenance checks, not native construction or physics simulation.
"""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / 'docs/validation/DES-040-baseline'


def read(name):
    p = DATA / name
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_text())


def main():
    manifest = read('manifest.json')
    for path, digest in manifest['files_sha256'].items():
        if hashlib.sha256((REPO / path).read_bytes()).hexdigest() != digest:
            raise ValueError('Retained baseline evidence/source changed: ' + path)
    native = read('native-tracker.json.gz')
    gen3 = read('gen3-geometry.json.gz')
    source = read('gen3-source-comparison.json.gz')
    if native['status'] != 'PASS' or native['errors'] or native['overlaps']:
        raise ValueError('Native audit did not pass')
    if native['unique_volume_ids'] != 46250 or native['physical_placements'] != 687724:
        raise ValueError('Native balanced inventory changed')
    if source['status'] != 'PASS' or source['unique_geometry_ids'] != 46250 or source['volumes'] != 120:
        raise ValueError('Native Gen3 source comparison did not pass')
    if gen3['checks']['sensor_groups'] != 54 or gen3['checks']['unsupported_portals']:
        raise ValueError('Incomplete balanced Gen3 export')
    if gen3['checks']['native_json_round_trip'] != 'PASS: complete serialized payload identical':
        raise ValueError('Missing complete native round trip')
    hashes = native['execution']['hashes']
    exported = {p['name']: p['sha256'] for p in gen3['provenance']['files']}
    for name, digest in hashes.items():
        if name in exported and exported[name] != digest:
            raise ValueError('Native/Gen3 execution inputs differ: ' + name)
    smoke = read('geant4-smoke.json')
    if smoke['exit_code'] != 0 or smoke['root_events'] != 3:
        raise ValueError('Geant4 transport smoke failed')
    publication = read('pdf-review.json')
    current_tree = subprocess.check_output([
        'git', 'rev-parse', 'HEAD:docs/publication/tracker-baseline-2026-10-29'
    ], cwd=REPO, text=True).strip()
    if current_tree != publication['source_tree'] or publication['status'] != 'PASS':
        raise ValueError('Current TDR source differs from the compiled/reviewed tree')
    print('PASS: balanced source/evidence fingerprints, native inventory, Gen3 round trip, Geant4 smoke and compiled TDR tree')


if __name__ == '__main__':
    main()
