#!/usr/bin/env python3
"""DES-008 PROTOTYPE: same-module stereo coverage and trial mounting envelopes."""
import argparse
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path

import numpy as np
from geometry import area, inside, intersects, rectangle, rotate, radial_extent

ROOT = Path(__file__).resolve().parents[2]
INPUT = Path(__file__).with_name('inputs.json')
EPS = 1e-9  # numerical boundary tolerance [mm or polygon cross-product mm²]


def validate(cfg):
    if not 0 < cfg['inner_radius'] < cfg['outer_radius']:
        raise ValueError('Require positive ordered annulus radii')
    if not 0 <= cfg['relative_stereo'] < math.pi/2:
        raise ValueError('Relative stereo must be in [0, pi/2)')
    if cfg['separation'] <= cfg['sensor_thickness']:
        raise ValueError('Sensor volumes must not overlap')
    for key in ('pitch', 'sensor_thickness', 'level_spacing'):
        if cfg[key] <= 0:
            raise ValueError(f'{key} must be positive')
    for key in ('row_gap', 'radial_margin', 'tangential_margin', 'guard',
                'radial_service', 'tangential_service', 'external_allowance_per_face',
                'interface_per_face', 'support_skin_per_face', 'cooling_outer_diameter'):
        if cfg[key] < 0:
            raise ValueError(f'{key} must be nonnegative')
    if cfg['disk_z'] <= max(cfg['vertex_z']) + 1.5*cfg['level_spacing'] + cfg['separation']/2:
        raise ValueError('Ray fixture requires every sensor beyond every vertex')
    for c in cfg['candidates']:
        if c['rows'] not in (1, 2) or c['rings'] < 1 or c['width'] <= 2*cfg['tangential_margin']:
            raise ValueError('Invalid candidate rows, rings or width')
        if c['shape'] not in ('rectangle', 'wedge'):
            raise ValueError('Unknown shape')
        if c['shape'] == 'rectangle' and c['height'] <= cfg['row_gap']:
            raise ValueError('Row gap consumes sensor height')


def layout(c, cfg):
    lo, hi = cfg['inner_radius'], cfg['outer_radius']
    margin = cfg['radial_margin']
    edges = np.linspace(lo, hi, c['rings']+1)
    centres = ((edges[:-1]+edges[1:])/2 if c['shape'] == 'wedge' else
               np.linspace(lo+c['height']/2-margin, hi-c['height']/2+margin, c['rings']))
    rings = []
    for i, r in enumerate(centres):
        if c['shape'] == 'rectangle':
            halfangle = math.atan((c['width']/2-cfg['tangential_margin'])/(r+c['height']/2))
            n = 2*math.ceil(math.pi/halfangle/2)
            p = rectangle(-c['height']/2, c['height']/2, c['width'])
        else:
            n = 2*math.ceil(2*math.pi*r/c['width']/2)
            alpha = math.pi/n + cfg['tangential_margin']/r
            a, b = edges[i]-margin, (edges[i+1]+margin)/math.cos(alpha)
            p = np.array([[a*math.cos(alpha)-r, -a*math.sin(alpha)],
                          [b*math.cos(alpha)-r, -b*math.sin(alpha)],
                          [b*math.cos(alpha)-r, b*math.sin(alpha)],
                          [a*math.cos(alpha)-r, a*math.sin(alpha)]])
        sensors = [rotate(p, sign*cfg['relative_stereo']/2)+[r, 0] for sign in (-1, 1)]
        # Conservative occupied box: rotated sensors plus explicit edge/service allowances.
        both = np.concatenate(sensors)
        extra_r = cfg['guard']+cfg['radial_service']
        extra_t = cfg['guard']+cfg['tangential_service']
        body = rectangle(both[:, 0].min()-extra_r, both[:, 0].max()+extra_r,
                         2*(abs(both[:, 1]).max()+extra_t))
        ring = {'ring': i, 'radius': float(r), 'count': n, 'phase': (i % 2)*math.pi/n,
                'local': p, 'sensors': sensors, 'body': body, 'rows': c['rows']}
        # Prove the finite nearest-neighbour search bound for BOTH rotated sensors.
        if max(abs(np.arctan2(s[:, 1], s[:, 0])).max() for s in sensors) >= 1.5*2*math.pi/n:
            raise ValueError('Sensor exceeds nearest-three-module search bound')
        rings.append(ring)
    return rings


def modules(rings, cfg):
    return [{'ring': r['ring'], 'module': j, 'level': 2*(r['ring'] % 2)+j % 2,
             'z': (2*(r['ring'] % 2)+j % 2-1.5)*cfg['level_spacing'],
             'body': rotate(r['body'], r['phase']+j*2*math.pi/r['count'])}
            for r in rings for j in range(r['count'])]


def active(ring, cfg, x, y, side):
    # Undo physical sensor rotation about the MODULE centre, not disk centre.
    angle = (-1 if side == 0 else 1)*cfg['relative_stereo']/2
    u = (x-ring['radius'])*math.cos(angle)+y*math.sin(angle)
    v = -(x-ring['radius'])*math.sin(angle)+y*math.cos(angle)
    hit = inside(ring['local'], u, v)
    if ring['rows'] == 2:
        hit &= abs(u) >= cfg['row_gap']/2
    return hit


def sample(rings, cfg, nr, nphi, vertex=None):
    radius = cfg['inner_radius']+(np.arange(nr)+.5)*(cfg['outer_radius']-cfg['inner_radius'])/nr
    phi = (np.arange(nphi)+.5)*2*math.pi/nphi
    rr, pp = radius[:, None], phi[None, :]
    pair_hits = np.zeros((nr, nphi), dtype=np.int16)
    side_any = [np.zeros_like(pair_hits, dtype=bool) for _ in range(2)]
    crossings = np.zeros_like(pair_hits)
    for r in rings:
        step = 2*math.pi/r['count']
        nearest = np.floor((pp-r['phase'])/step+.5).astype(int)
        for dj in (-1, 0, 1):
            index = (nearest+dj) % r['count']
            theta = pp-r['phase']-index*step
            level = 2*(r['ring'] % 2)+index % 2
            z = (level-1.5)*cfg['level_spacing']
            hits = []
            for side, sign in enumerate((-1, 1)):
                factor = 1 if vertex is None else (cfg['disk_z']+z+sign*cfg['separation']/2-vertex)/(cfg['disk_z']-vertex)
                h = active(r, cfg, rr*factor*np.cos(theta), rr*factor*np.sin(theta), side)
                hits.append(h)
                side_any[side] |= h
                crossings += h
            pair_hits += hits[0] & hits[1]
    w = np.broadcast_to(rr, pair_hits.shape)
    total = w.sum()
    fraction = lambda mask: float(w[mask].sum()/total)
    return {'radial_bins': nr, 'phi_bins': nphi,
            'missing_pair_bins': int((pair_hits == 0).sum()),
            'missing_pair_fraction': fraction(pair_hits == 0),
            'no_sensor_fraction': fraction(~(side_any[0] | side_any[1])),
            'both_sides_but_no_same_module_pair_fraction': fraction(side_any[0] & side_any[1] & (pair_hits == 0)),
            'multiple_pair_fraction': fraction(pair_hits > 1),
            'mean_pairs': float((w*pair_hits).sum()/total),
            'mean_sensor_crossings': float((w*crossings).sum()/total)}


def body_thickness(cfg):
    return cfg['separation']+cfg['sensor_thickness']+2*cfg['external_allowance_per_face']


def collisions(mods, cfg):
    """3D intersections of conservative prisms, including different z levels."""
    bounds = [(m['body'].min(axis=0), m['body'].max(axis=0)) for m in mods]
    pairs = []
    for i, a in enumerate(mods):
        for j in range(i):
            b = mods[j]
            if abs(a['z']-b['z']) >= body_thickness(cfg)-EPS:
                continue
            if np.any(bounds[i][0] >= bounds[j][1]) or np.any(bounds[j][0] >= bounds[i][1]):
                continue
            if intersects(a['body'], b['body']):
                pairs.append([[a['ring'], a['module'], a['level']], [b['ring'], b['module'], b['level']]])
    return pairs


def mechanical(cfg):
    free = cfg['separation']-cfg['sensor_thickness']
    budget = free-2*cfg['interface_per_face']-2*cfg['support_skin_per_face']-cfg['cooling_outer_diameter']
    return {'silicon_face_gap_mm': free,
            'cooling_stack_residual_mm': budget,
            'cooling_stack_fits_fixture': budget >= 0,
            'body_thickness_mm': body_thickness(cfg),
            'adjacent_level_clearance_mm': cfg['level_spacing']-body_thickness(cfg),
            'four_level_z_extent_mm': 3*cfg['level_spacing']+body_thickness(cfg),
            'max_sensor_plane_offset_mm': 1.5*cfg['level_spacing']+cfg['separation']/2,
            'max_within_pair_radial_parallax_mm': cfg['separation']*cfg['outer_radius']/(cfg['disk_z']-max(cfg['vertex_z']))}


def resolution(pitch, angle):
    sigma = pitch/math.sqrt(12)
    return {'relative_stereo_mrad': angle*1000,
            'sigma_across_mm': sigma/(math.sqrt(2)*math.cos(angle/2)),
            'sigma_along_mm': None if angle == 0 else sigma/(math.sqrt(2)*math.sin(angle/2)),
            'condition_number': None if angle == 0 else 1/math.tan(angle/2)**2,
            'rank': 1 if angle == 0 else 2}


def evaluate(c, cfg, refined=False, scan=False):
    rings = layout(c, cfg)
    mods = modules(rings, cfg)
    sampling = cfg['scan_sampling'] if scan else cfg['sampling']
    nr, np_ = sampling['radial_bins'], sampling['phi_bins']
    coverage = {}
    for scale in ((1, 2) if refined else (1,)):
        for vertex in (None, *cfg['vertex_z']):
            name = 'normal' if vertex is None else f'vertex_{vertex:g}_mm'
            coverage[f'{name}_{scale}x'] = sample(rings, cfg, nr*scale, np_*scale, vertex)
    collision_pairs = collisions(mods, cfg)
    # Nominal silicon area includes the row seam; seam is inactive silicon, not removed mass.
    silicon_area = 2*sum(area(r['local'])*r['count'] for r in rings)
    extents = [radial_extent(r['body']) for r in rings]
    return {'candidate': c, 'module_types': len(rings) if c['shape'] == 'wedge' else 1,
            'modules': len(mods), 'sensors': 2*len(mods),
            'sensor_outline_area_mm2': silicon_area,
            'two_sensor_area_over_annulus': silicon_area/(math.pi*(cfg['outer_radius']**2-cfg['inner_radius']**2)),
            'occupied_radius_mm': [min(x[0] for x in extents), max(x[1] for x in extents)],
            'body_collisions': len(collision_pairs), 'collision_examples': collision_pairs[:5],
            'mechanical': mechanical(cfg), 'coverage': coverage,
            'rings': [{'ring': r['ring'], 'radius_mm': r['radius'], 'modules': r['count'],
                       'phase_rad': r['phase'], 'sensor_local_polygon_mm': r['local'].tolist(),
                       'body_polygon_mm': r['body'].tolist(),
                       'nominal_row_span_mm': float(np.ptp(r['local'][:, 0])/r['rows']),
                       'strip_channel_estimate_per_pair': float(2*r['rows']*np.ptp(r['local'][:, 1])/cfg['pitch'])}
                      for r in rings]}


def sweeps(cfg):
    results = []
    # Hold tiling rules/margins fixed; changing angle does not retune module counts.
    for c in (cfg['candidates'][1], cfg['candidates'][3]):
        variants = [('angle', 'relative_stereo', a) for a in cfg['angle_scan']]
        variants += [('gap', 'separation', d) for d in cfg['separation_scan']]
        variants += [('short_strip_stagger_control', 'level_spacing', 3.0),
                     ('large_mount_control', 'radial_service', 30.0),
                     ('no_row_seam_control', 'row_gap', 0.0)]
        for name, key, value in variants:
            scenario = dict(cfg, **{key: value})
            validate(scenario)
            r = evaluate(c, scenario, scan=True)
            results.append({'candidate': c['id'], 'scan': name, 'parameter': key, 'value': value,
                            'max_missing_pair_fraction': max(s['missing_pair_fraction'] for s in r['coverage'].values()),
                            'body_collisions': r['body_collisions'], 'mechanical': r['mechanical'],
                            'coverage': r['coverage']})
    return results


def figure(cfg, path):
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['svg.hashsalt'] = 'DES-008'
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig, axes = plt.subplots(2, 4, figsize=(18, 10))
    for ax, c in zip(axes.flat, cfg['candidates']):
        rings = layout(c, cfg)
        polys = [[], []]
        for r in rings:
            for j in range(r['count']):
                for side in (0, 1):
                    polys[side].append(rotate(r['sensors'][side], r['phase']+j*2*math.pi/r['count']))
        for side, colour in enumerate(('#167d9a', '#e88b39')):
            ax.add_collection(PolyCollection(polys[side], facecolors=colour, alpha=.25,
                                             edgecolors=colour, linewidths=.15))
        for radius in (cfg['inner_radius'], cfg['outer_radius'], 1140):
            ax.add_patch(plt.Circle((0, 0), radius, fill=False, color='#374151', linewidth=.5))
        ax.set(xlim=(-1160, 1160), ylim=(-1160, 1160), aspect='equal',
               title=f"{c['id']}: {sum(r['count'] for r in rings)} pairs", xlabel='x [mm]', ylabel='y [mm]')
    ax = axes.flat[-1]
    r = layout(cfg['candidates'][1], cfg)[2]
    for side, colour in enumerate(('#167d9a', '#e88b39')):
        p = r['sensors'][side]-[r['radius'], 0]
        ax.fill(p[:, 1], p[:, 0], color=colour, alpha=.35, label=f'sensor {side}')
    p = r['body']-[r['radius'], 0]
    ax.plot(*np.vstack((p, p[0]))[:, ::-1].T, color='#374151', label='trial occupied body')
    ax.set(aspect='equal', xlabel='tangential [mm]', ylabel='radial [mm]', title='Square pair: ±20 mrad, 5 mm separation')
    ax.legend(fontsize=8)
    fig.suptitle('DES-008 PROTOTYPE · projected sensor outlines, not pair coverage\nFour stagger levels; row seams omitted from overview; outer circle = 1140 mm host boundary')
    fig.tight_layout()
    fig.savefig(path, metadata={'Date': None})
    plt.close(fig)
    if path.suffix.lower() == '.svg':
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=INPUT)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/validation/DES-008-ring-study.json')
    parser.add_argument('--refined', action='store_true')
    parser.add_argument('--sweeps', action='store_true')
    parser.add_argument('--figure', type=Path)
    args = parser.parse_args()
    cfg = json.loads(args.input.read_text())
    validate(cfg)
    files = [args.input, Path(__file__), Path(__file__).with_name('geometry.py')]
    output = {'status': 'PROTOTYPE; not detector validation',
              'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'working_tree': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).splitlines(),
              'python': platform.python_version(), 'numpy': np.__version__, 'random_seed': None,
              'sampling_method': 'deterministic polar midpoint grids, area-weighted',
              'numerical_boundary_epsilon': EPS,
              'hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              'configuration': cfg,
              'results': [evaluate(c, cfg, args.refined) for c in cfg['candidates']],
              'resolution': [resolution(cfg['pitch'], a) for a in cfg['angle_scan']],
              'sweeps': sweeps(cfg) if args.sweeps else []}
    if args.figure:
        import matplotlib
        output['matplotlib'] = matplotlib.__version__
        figure(cfg, args.figure)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False)+'\n')
    for r in output['results']:
        print(r['candidate']['id'], r['modules'], 'pairs; silicon ratio', round(r['two_sensor_area_over_annulus'], 4),
              'collisions', r['body_collisions'], 'max missing pairs', max(v['missing_pair_fraction'] for v in r['coverage'].values()))


if __name__ == '__main__':
    main()
