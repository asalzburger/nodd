"""Check retained inventory counts and reconstruct every source footprint."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
source = args.root/'docs/validation/DES-040/geometry.json'
geometry = json.loads(source.read_text())
base = args.root/'docs/validation/DES-040/wheels-2026-10-20/before-inventory'
summary = {}
maximum_error = 0.
for kind, expected_count, expected_families in [('barrel', 816, 6), ('endcap', 744, 18)]:
    report = json.loads((base/(kind+'.json')).read_text())
    assert report['source_geometry_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    panels = {p['id']: p for p in geometry['panels'] if p['kind'] == kind}
    assert report['total_panels'] == len(panels) == expected_count
    assert report['shape_families'] == len(report['families']) == expected_families
    assert len(report['panels']) == len(panels)
    assert {p['panel_id'] for p in report['panels']} == set(panels)
    assigned = [ident for f in report['families'] for ident in f['panel_ids']]
    assert Counter(assigned) == Counter(panels.keys())
    by_family = {f['shape_id']: f for f in report['families']}
    for family in by_family.values():
        members = [panels[i] for i in family['panel_ids']]
        assert family['quantity'] == len(members)
        assert family['station_counts'] == dict(Counter(str(p['station']) for p in members))
        if kind == 'endcap':
            assert family['side_counts'] == dict(Counter('plus' if p['side'] > 0 else 'minus' for p in members))
    for entry in report['panels']:
        panel = panels[entry['panel_id']]
        family = by_family[entry['shape_id']]
        assert panel['id'] in family['panel_ids']
        v = np.asarray(panel['vertices_m'])
        d = family['dimensions_m']
        if kind == 'barrel':
            w, h = d['tangential_width_m'], d['longitudinal_length_m']
            normalized = v-[v[:, 0].mean(), v[:, 1].min()]
            reconstructed = [[-w/2, 0], [w/2, 0], [w/2, h], [-w/2, h]]
        else:
            low = v[v[:, 0] == v[:, 0].min()]
            normalized = v-[low[:, 0].mean(), low[:, 1].mean()]
            a, b, h, offset = [d[k] for k in ['inner_base_m', 'outer_base_m', 'radial_span_m', 'outer_base_offset_m']]
            reconstructed = [[0, -a/2], [h, offset-b/2], [h, offset+b/2], [0, a/2]]
        distance = np.linalg.norm(normalized[:, None, :]-np.asarray(reconstructed)[None, :, :], axis=2)
        error = float(max(distance.min(axis=0).max(), distance.min(axis=1).max()))
        maximum_error = max(maximum_error, error)
        assert error < 1e-9, (panel['id'], error)
        assert d['depth_m'] == panel['depth_m']
    with (base/(kind+'.csv')).open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == expected_families
    for row in rows:
        family = by_family[row['shape_id']]
        assert int(row['quantity']) == family['quantity']
        assert all(abs(float(row[k])-v) < 1e-12 for k, v in family['dimensions_m'].items())
    summary[kind] = dict(panels=len(panels), families=len(by_family),
                         station_counts=dict(Counter(str(p['station']) for p in panels.values())))
result = dict(source_geometry_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              scope='Inventory-only reconstruction; no candidate geometry or response validation.',
              counts=summary, maximum_source_footprint_error_m=maximum_error,
              footprint_tolerance_m=1e-9, all_checks_passed=True)
args.output.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
