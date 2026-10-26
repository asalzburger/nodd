#!/usr/bin/env python3
"""Audit the retained trial inputs, keyed map and total-profile normalization."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from select_surfaces import select


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    root = Path(__file__).resolve().parents[3]
    data = root / 'docs/validation/gen3-material-map-run'
    read = lambda p: json.loads(p.read_text())
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = read(data / 'selection.json')
    geometry = root / 'docs/validation/gen3-material-mapping/geometry-summary.json'
    config = Path(__file__).with_name('mapping_config.json')
    regenerated = select(read(geometry), read(config))
    require(regenerated == {k: v for k, v in manifest.items() if k != 'provenance'},
            'Retained portal selection differs from current geometry/configuration')
    for key, path in [('geometry_sha256', geometry), ('config_sha256', config),
                      ('selector_sha256', Path(__file__).with_name('select_surfaces.py'))]:
        require(manifest['provenance'][key] == digest(path), f'Stale {key}')

    mapping = read(data / 'mapping-report.json')
    validation = read(data / 'validation-report.json')
    raw_map = gzip.decompress((data / 'material_map.json.gz').read_bytes())
    for report in (mapping, validation):
        files = {f['role']: f for f in report['provenance']['files']}
        require(files['selection_manifest']['sha256'] == digest(data / 'selection.json'),
                'Native run used another selection')
        require(files['material_map']['sha256'] == hashlib.sha256(raw_map).hexdigest(),
                'Retained map bytes differ from native run')
        steering = root / 'software/running' / files['steering']['name']
        require(files['steering']['sha256'] == digest(steering), 'Steering source changed since full run')
    relocation = read(data / 'source-relocation.json')
    patch = data / 'source-relocation.patch'
    require(digest(patch) == relocation['final_source_patch']['sha256'], 'Source patch hash mismatch')
    with tempfile.TemporaryDirectory(prefix='nodd-source-audit-') as temporary:
        directory = Path(temporary)
        for entry in relocation['final_source_patch']['files']:
            source = root / entry['path']
            require(digest(source) == entry['after_sha256'], 'Final source differs from reconciled source')
            target = directory / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=directory, check=True)
        for entry in relocation['final_source_patch']['files']:
            require(digest(directory / entry['path']) == entry['before_sha256'], 'Full-run source reconstruction failed')
        subprocess.run(['git', 'apply', str(patch)], cwd=directory, check=True)
        for entry in relocation['final_source_patch']['files']:
            require(digest(directory / entry['path']) == entry['after_sha256'], 'Final source reconstruction failed')
    for report in relocation['immutable_full_run_reports']:
        require(digest(data / Path(report['path']).name) == report['sha256'], 'Authoritative report changed')
    material = json.loads(raw_map)
    keyed = material['KeyedSurfaces']
    require(not material['Surfaces']['entries'] and not material['Volumes']['entries'],
            'Unexpected unkeyed surface/volume material')
    by_id = {p['geometry_id']: p for p in keyed}
    require(len(by_id) == len(keyed) == len(manifest['surfaces']), 'Duplicate/missing keyed material')
    bins = empty = 0
    for surface in manifest['surfaces']:
        actual = by_id[surface['geometry_id']]
        require(actual['key'] == surface['material_key'], 'Material-key mismatch')
        axes = actual['material']['binUtility']['binningdata']
        axis = 'z' if surface['type'] == 'cylinder' else 'r'
        require([a['value'] for a in axes] == ['AxisPhi', 'Axis' + axis.upper()], 'Unexpected map axes')
        counts = [surface['bins']['phi'], surface['bins'][axis]]
        require([a['bins'] for a in axes] == counts, 'Map binning differs from manifest')
        slabs = actual['material']['data']
        require(len(slabs) == counts[1] and all(len(row) == counts[0] for row in slabs),
                'Map slab grid differs from manifest')
        bins += sum(len(row) for row in slabs)
        empty += sum(slab['thickness'] == 0 for row in slabs for slab in row)
    require(bins == manifest['counts']['material_bins'], 'Material-bin count mismatch')
    require(empty == mapping['serialized_reload']['empty_bins'], 'Zero-thickness count mismatch')

    profiles = read(data / 'validation-profiles.json')
    require(profiles['source_truth_sha256'] == digest(root / 'docs/validation/geantino-material-profiles/profiles.json'),
            'Stale truth profiles')
    require(profiles['source_exporter_sha256'] == digest(Path(__file__).with_name('export_validation.py')),
            'Total-profile exporter changed')
    require(profiles['source_validation_sha256'] == next(
        f['sha256'] for f in validation['provenance']['files'] if f['role'] == 'validation_tracks'),
        'Total profiles came from another validation recording')
    for axis in profiles['axes'].values():
        for quantity, profile in axis['quantities'].items():
            n = sum(profile['counts'])
            require(n == profiles['tracks'] == validation['track_budgets']['tracks'], 'Ray-count mismatch')
            mean = sum(c * m for c, m in zip(profile['counts'], profile['mean'])) / n
            require(abs(mean - profiles['global_mean'][quantity]) < 1.e-12, 'Profile normalization mismatch')
            require(not profile['empty_bins'], 'Unsupported validation profile bin')
    print(f"Retained trial PASS: {len(keyed)} keyed portals, {bins} bins, {empty} zero slabs; all inputs/counts/hashes agree")


if __name__ == '__main__':
    main()
