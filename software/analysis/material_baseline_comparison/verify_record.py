#!/usr/bin/env python3
"""Check the current map record against retained native evidence without ROOT."""
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'docs/validation/baseline-material-comparison'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_grid(material, selection, reload):
    require(not material['Surfaces']['entries'] and not material['Volumes']['entries'],
            'Unexpected unkeyed material')
    keyed = material['KeyedSurfaces']
    by_id = {entry['geometry_id']: entry for entry in keyed}
    ids = {surface['geometry_id'] for surface in selection['surfaces']}
    require(len(by_id) == len(keyed) == len(ids) and set(by_id) == ids,
            'Duplicate or mismatched material surface identities')
    bins = empty = 0
    for surface in selection['surfaces']:
        entry = by_id[surface['geometry_id']]
        require(entry['key'] == surface['material_key'], 'Material key mismatch')
        coordinate = 'z' if surface['type'] == 'cylinder' else 'r'
        axes = entry['material']['binUtility']['binningdata']
        counts = [surface['bins']['phi'], surface['bins'][coordinate]]
        require([a['value'] for a in axes] == ['AxisPhi', 'Axis' + coordinate.upper()]
                and [a['bins'] for a in axes] == counts, 'Material axes/bin counts mismatch')
        grid = entry['material']['data']
        require(len(grid) == counts[1] and all(len(row) == counts[0] for row in grid),
                'Material grid shape mismatch')
        for row in grid:
            for slab in row:
                thickness = slab['thickness']
                require(math.isfinite(thickness) and thickness >= 0, 'Invalid slab thickness')
                values = slab['material']
                require(thickness == 0 or (values is not None and len(values) == 5
                        and all(math.isfinite(v) and v > 0 for v in values)),
                        'Nonzero slab lacks finite positive material properties')
                bins += 1
                empty += thickness == 0
    require(bins == selection['counts']['material_bins'] == reload['material_bins'],
            'Material-bin total differs from native reload')
    require(len(keyed) == reload['map_key_count'] and empty == reload['empty_bins'],
            'Material-key/empty-bin totals differ from native reload')
    return len(keyed), bins, empty


def verify(directory=DATA):
    read = lambda name: json.loads((directory / name).read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    record = read('material-map-record.json')
    require(record['status'] == 'PROTOTYPE', 'Map lifecycle must remain qualified')
    for name, digest in record['evidence_sha256'].items():
        require(sha(directory / name) == digest, 'Changed retained map evidence: ' + name)
    prep, selection = read('preparation-report.json'), read('selection.json')
    mapping, validation = read('current-mapping-report.json'), read('current-validation-report.json')
    require(record['geometry_source_revision'] == prep['source_revision']
            == selection['provenance']['native_geometry_provenance']['source_revision']
            == mapping['recording_checks']['geometry_source_revision'], 'Geometry revision mismatch')
    files = {Path(f['path']).name: f['sha256'] for f in prep['geometry_inputs']
             if f['role'] in ('tracker.xml', 'materials.xml', 'factory')}
    require(record['geometry_files_sha256'] == files, 'Geometry/factory fingerprint mismatch')
    require(record['geometry_inventory'] == {k: prep['checks'][k]
            for k in record['geometry_inventory']}, 'Geometry inventory mismatch')
    packed = directory / record['map']['path']
    raw = gzip.decompress(packed.read_bytes())
    require(sha(packed) == record['map']['sha256'], 'Compressed map fingerprint mismatch')
    require(hashlib.sha256(raw).hexdigest() == record['map']['decompressed_sha256']
            == mapping['material_map']['sha256'], 'Native map fingerprint mismatch')
    material = json.loads(raw)
    counts = verify_grid(material, selection, mapping['serialized_reload'])
    require(counts == tuple(record['map'][k] for k in
            ('keyed_surfaces', 'material_bins', 'zero_thickness_bins')), 'Recorded map inventory mismatch')
    require(all(s['bins']['phi'] == record['map']['phi_bins'] for s in selection['surfaces']),
            'Recorded phi binning mismatch')
    require(record['training']['rays'] == mapping['per_track_budget_partition']['tracks']
            and record['training']['seed'] == mapping['training']['seed']
            and record['training']['eta_range'] == mapping['training']['eta'], 'Training record mismatch')
    require(record['independent_validation']['rays'] == validation['track_budgets']['tracks']
            and record['independent_validation']['seed'] == validation['sampling']['seed']
            and record['independent_validation']['eta_range'] == validation['sampling']['eta_uniform'],
            'Independent validation record mismatch')
    return counts


if __name__ == '__main__':
    keys, bins, empty = verify()
    print(f'Current map record PASS: {keys} keyed portals, {bins} bins, {empty} zero slabs; identities match native evidence')
