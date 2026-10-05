#!/usr/bin/env python3
"""DES-008 PROTOTYPE: pin ring coverage to the active PR13 A/C1 disk geometries."""
import argparse
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path

import numpy as np
import study

CATALOGUE = Path(__file__).with_name('pr13-layouts.json')


def contract(cfg, catalogue):
    """Reject drift in either proposal, annulus, first disk or signed-side geometry."""
    if catalogue['units'] != 'm' or set(catalogue['active_options']) != {'A', 'C1'}:
        raise ValueError('Expected PR13 A/C1 geometry in metres')
    if sorted(c['id'] for c in catalogue['candidates']) != ['A', 'C1']:
        raise ValueError('Both active candidates must be present exactly once')
    normalized = {}
    for c in catalogue['candidates']:
        disks = [l for l in c['layers'] if l['subsystem'] == 'long_strip' and l['kind'] == 'disc']
        positions = [round(l['z_m']*1000, 6) for l in disks]
        if len(set(positions)) != 12 or len(positions) != 12 or set(positions) != {-z for z in positions}:
            raise ValueError('Expected six uniquely identified mirrored disk pairs')
        for layer in disks:
            if not (math.isclose(layer['r_min_m']*1000, cfg['inner_radius'], abs_tol=1e-8)
                    and math.isclose(layer['r_max_m']*1000, cfg['outer_radius'], abs_tol=1e-8)):
                raise ValueError(f"Annulus differs from PR13 {layer['id']}")
        normalized[c['id']] = sorted(abs(z) for z in positions if z > 0)
        if not math.isclose(normalized[c['id']][0], cfg['disk_z'], abs_tol=1e-8):
            raise ValueError(f"First disk differs from PR13 {c['id']}")
    if normalized['A'] != normalized['C1']:
        raise ValueError('A and C1 require separate z studies')
    return normalized['A']


def interface_summary(result, cfg, catalogue):
    """Envelope reservations, not a detailed shared-support collision test."""
    half_depth = study.mechanical(cfg)['four_level_z_extent_mm']/2
    radius_min, radius_max = result['occupied_radius_mm']
    rings = study.layout(result['candidate'], cfg)
    sensor_extents = [study.radial_extent(sensor) for r in rings for sensor in r['sensors']]
    per_layout = []
    for c in catalogue['candidates']:
        ls = [l for l in c['layers'] if l['subsystem'] == 'long_strip' and l['kind'] == 'disc']
        ss = [l for l in c['layers'] if l['subsystem'] == 'short_strip' and l['kind'] == 'disc']
        barrel = [l for l in c['layers'] if l['subsystem'] == 'long_strip' and l['kind'] == 'cylinder']
        nearest = min(abs(l['z_m']-s['z_m'])*1000 for l in ls for s in ss)
        barrel_end = max(max(abs(l['z_min_m']), abs(l['z_max_m'])) for l in barrel)*1000
        first_z, last_z = min(abs(l['z_m'])*1000 for l in ls), max(abs(l['z_m'])*1000 for l in ls)
        short_outer = max(l['r_max_m'] for l in ss)*1000
        per_layout.append({'layout': c['id'],
                           'ideal_active_band_gap_mm': cfg['inner_radius']-short_outer,
                           'body_radial_gap_to_short_strip_active_edge_mm': radius_min-short_outer,
                           'nearest_short_long_disk_centres_mm': nearest,
                           'short_long_trial_axial_envelope_gap_mm': nearest-half_depth-catalogue['short_strip_body_fixture']['full_depth_mm']/2,
                           'first_disk_body_to_ideal_barrel_end_mm': first_z-half_depth-barrel_end,
                           'last_disk_body_to_host_end_mm': catalogue['host']['abs_z_max_m']*1000-last_z-half_depth})
    return {'occupied_radius_mm': [radius_min, radius_max],
            'rotated_active_outline_radius_mm': [min(x[0] for x in sensor_extents), max(x[1] for x in sensor_extents)],
            'radial_host_residual_mm': catalogue['host']['r_max_m']*1000-radius_max,
            'layouts': per_layout,
            'limitation': 'Short-strip depth is the PR21 trial fixture; actual barrel-end structures, carriers and services are unmodeled. Negative radial gap does not imply a 3D collision when z envelopes are separated.'}


def boundary_sample(rings, cfg, nphi, vertex):
    """Explicitly test target inner/outer circles; fractions are angular, not area."""
    radius = np.array([cfg['inner_radius'], cfg['outer_radius']])[:, None]
    phi = (np.arange(nphi)+.5)*2*math.pi/nphi
    covered = np.zeros((2, nphi), dtype=bool)
    # Full module enumeration also avoids sharing the nearest-neighbour shortcut.
    for ring in rings:
        for j in range(ring['count']):
            theta = phi-ring['phase']-j*2*math.pi/ring['count']
            z = (2*(ring['ring'] % 2)+j % 2-1.5)*cfg['level_spacing']
            hits = []
            for side, sign in enumerate((-1, 1)):
                factor = (cfg['disk_z']+z+sign*cfg['separation']/2-vertex)/(cfg['disk_z']-vertex)
                hits.append(study.active(ring, cfg, radius*factor*np.cos(theta), radius*factor*np.sin(theta), side))
            covered |= hits[0] & hits[1]
    return {'vertex_z_mm': vertex, 'phi_samples_per_boundary': nphi,
            'missing_inner_boundary_samples': int((~covered[0]).sum()),
            'missing_outer_boundary_samples': int((~covered[1]).sum())}


def run(cfg, catalogue, refined=True):
    z_values = contract(cfg, catalogue)
    cases = []
    templates = [c for c in cfg['candidates'] if c['id'] in ('square-long-6', 'square-5-control')]
    if len(templates) != 2:
        raise ValueError('Require six-ring working candidate and five-ring control')
    for z in z_values:
        for c in templates:
            scenario = dict(cfg, disk_z=z)
            study.validate(scenario)
            r = study.evaluate(c, scenario, refined=refined)
            # Reflection z -> -z, vertex -> -vertex preserves the ray factors exactly
            # if the module stack is reflected too. Retain all covered source IDs.
            ids = [l['id'] for candidate in catalogue['candidates'] for l in candidate['layers']
                   if l['subsystem'] == 'long_strip' and l['kind'] == 'disc'
                   and math.isclose(abs(l['z_m'])*1000, z, abs_tol=1e-8)]
            cases.append({'abs_disk_z_mm': z, 'source_layer_ids': ids, 'candidate': c['id'],
                          'modules': r['modules'], 'body_collisions': r['body_collisions'],
                          'max_missing_pair_fraction': max(s['missing_pair_fraction'] for s in r['coverage'].values()),
                          'coverage': r['coverage'],
                          'boundary_checks': [boundary_sample(study.layout(c, scenario), scenario,
                                                              cfg['sampling']['phi_bins']*2, vertex)
                                              for vertex in cfg['vertex_z']] if c['id'] == 'square-long-6' else []})
    selected = next(c for c in templates if c['id'] == 'square-long-6')
    result = study.evaluate(selected, cfg, scan=True)
    return {'contract': {'layouts': ['A', 'C1'], 'annulus_mm': [cfg['inner_radius'], cfg['outer_radius']],
                         'abs_disk_z_mm': z_values,
                         'negative_side_rule': 'Reflect disk and complete module stack; relabel vertex z with opposite sign. Coverage factors and collision geometry are invariant.'},
            'cases': cases, 'interfaces': interface_summary(result, cfg, catalogue),
            'six_rings_pass_sampled_coverage_and_body_checks': all(c['max_missing_pair_fraction'] == 0 and c['body_collisions'] == 0
                and all(b['missing_inner_boundary_samples'] == 0 and b['missing_outer_boundary_samples'] == 0 for b in c['boundary_checks']) for c in cases if c['candidate'] == selected['id'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=study.ROOT/'docs/validation/DES-008-layout-compatibility.json')
    args = parser.parse_args()
    cfg = json.loads(study.INPUT.read_text())
    catalogue = json.loads(CATALOGUE.read_text())
    paths = [study.INPUT, CATALOGUE, Path(__file__), Path(study.__file__), Path(study.__file__).with_name('geometry.py')]
    result = {'status': 'PROTOTYPE; target-band compatibility, not engineered service clearance',
              'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=study.ROOT, text=True).strip(),
              'working_tree': subprocess.check_output(['git', 'status', '--porcelain'], cwd=study.ROOT, text=True).splitlines(),
              'python': platform.python_version(), 'numpy': np.__version__,
              'sampling_method': 'deterministic polar midpoints, radius-weighted; base and doubled grids',
              'numerical_boundary_epsilon': study.EPS,
              'random_seed': None, 'configuration': cfg, 'layout_source': catalogue['source'],
              'hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
              **run(cfg, catalogue)}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for c in result['cases']:
        print(c['abs_disk_z_mm'], c['candidate'], c['modules'], 'pairs; missing fraction', c['max_missing_pair_fraction'], 'body conflicts', c['body_collisions'])
    if not result['six_rings_pass_sampled_coverage_and_body_checks']:
        raise SystemExit('Six-ring working candidate failed; see retained evidence')


if __name__ == '__main__':
    main()
