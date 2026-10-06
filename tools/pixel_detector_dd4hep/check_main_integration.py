#!/usr/bin/env python3
"""Audit rigid PR40 shifts against retained DES019 inventory and DES018 bounds."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', required=True, type=Path)
    parser.add_argument('--current', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    previous, current = [json.loads(p.read_text()) for p in (args.previous, args.current)]
    schedule_path = ROOT / 'docs/validation/DES-018/screening.json'
    template_path = ROOT / 'docs/validation/DES-017/four-single-two-quad-layout.json'
    input_path = ROOT / 'tools/pixel_endcap_support/inputs.json'
    schedule = json.loads(schedule_path.read_text())['variants']['four-single-two-quad']['positive_discs']
    template = json.loads(template_path.read_text())
    datums = json.loads(input_path.read_text())['placement']['disc_abs_z_mm']
    shifts = [z - d['datum_mm'] for z, d in zip(datums, schedule)]
    assert previous['counts'] == current['counts'], 'Changed entity counts'
    roles = {'sensitive', 'module', 'asic', 'sensor_guard', 'module_passive', 'contact_shim', 'pickup'}
    old = {e['name']: e for e in previous['entities'] if e['role'] in roles}
    new = {e['name']: e for e in current['entities'] if e['role'] in roles}
    assert old.keys() == new.keys(), 'Changed module component names'
    checked, maximum = 0, 0.0
    for name, entity in old.items():
        expected = dict(entity)
        numbered = re.match(r'^disc([23])_(\d+)_', name)
        lettered = re.match(r'^disc([NP])(\d+)_', name)
        if numbered or lettered:
            match = numbered or lettered
            sign = -1 if match[1] in ('2', 'N') else 1
            expected['center_mm'] = list(entity['center_mm'])
            expected['center_mm'][2] += sign * shifts[int(match[2]) - 1]
        observed = dict(new[name])
        if 'center_mm' in expected:
            residual = max(abs(a-b) for a, b in zip(expected['center_mm'], observed['center_mm']))
            maximum = max(maximum, residual)
            assert residual < 1e-9, (name, residual)
            observed['center_mm'] = expected['center_mm']
        assert expected == observed, 'Changed non-position module data: ' + name
        checked += 1

    source = {m['module_id']: m for m in template['modules']}
    raw = {m['module_id']: m for m in template['raw_modules']}
    # These are the retained DES018 hypotheses, not new performance claims.
    hypotheses = json.loads(schedule_path.read_text())['inputs']
    # Independently evaluate the documented conservative lower radial bound.
    eta = hypotheses['eta_max']
    luminous_z = hypotheses['luminous_half_z_mm']
    vertex_radius = math.sqrt(2) * hypotheses['transverse_vertex_half_box_mm']
    curvature = 0.000299792458 * hypotheses['max_abs_field_T'] / hypotheses['pt_min_GeV']
    margins = []
    for index, disc in enumerate(schedule):
        ring_margins = []
        for patch in template['active_patches']:
            if patch['row'] not in disc['removed_rows']:
                continue
            module = source[patch['module_id']]
            base = raw[patch['module_id']]
            dz = module['local_z_mm']
            anchor = (disc['datum_mm']**2 - luminous_z**2) / disc['datum_mm']
            xy = [base['center_mm'][j] * (1 + dz / anchor)
                  + patch['center_mm'][j] - module['center_mm'][j] for j in range(2)]
            outer = max(math.hypot(*[xy[j] + su * patch['half_u_mm'] * patch['u'][j]
                                    + sv * patch['half_v_mm'] * patch['v'][j] for j in range(2)])
                        for su in (-1, 1) for sv in (-1, 1))
            arc = (datums[index] + dz - luminous_z) / math.sinh(eta)
            assert 0 < curvature * arc < math.pi, 'Outside first half-turn proof'
            lower = 2 * math.sin(curvature * arc / 2) / curvature - vertex_radius
            margin = lower - outer
            assert margin >= hypotheses['radial_retention_buffer_mm'], (index + 1, patch['id'], margin)
            ring_margins.append(margin)
        margins.append({'disc': index + 1, 'datum_mm': datums[index],
                        'shift_positive_mm': shifts[index], 'removed_rows': disc['removed_rows'],
                        'removed_patches_checked': len(ring_margins),
                        'minimum_exclusion_margin_mm': min(ring_margins) if ring_margins else None})
    report = {'status': 'PASS', 'counts': current['counts'],
              'previous_expected_sha256': digest(args.previous),
              'current_expected_sha256': digest(args.current),
              'helper_sha256': digest(Path(__file__)),
              'source_sha256': {str(p.relative_to(ROOT)): digest(p)
                                for p in (schedule_path, template_path, input_path)},
              'module_components_checked': checked, 'maximum_position_residual_mm': maximum,
              'invariants': 'All module IDs, axes, x/y, local z, materials and dimensions unchanged; global z rigidly shifted. Barrel unchanged.',
              'hypotheses': hypotheses, 'proof_scope': 'pT>=1 GeV; |eta|<=4; uniform axial |B|<=4 T; vacuum first outward half-turn; |z_vertex|<=150 mm, x/y vertex in +/-1 mm box. Both ends symmetric.',
              'disc_exclusion': margins,
              'limitations': ['Original coverage/guard gaps and warm thermal/service packing failures remain.',
                              'Transport cells change their spans and mass with the reviewed global datums.',
                              'No new ACTS propagation or full magnetic-field model in this integration.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {checked} module components; minimum removed-patch margin '
          f'{min(x["minimum_exclusion_margin_mm"] for x in margins if x["minimum_exclusion_margin_mm"] is not None):.6f} mm')


if __name__ == '__main__':
    main()
