#!/usr/bin/env python3
"""DES-007 PROTOTYPE. Deterministic polygon screen, not detector simulation."""
import argparse
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
INPUT = Path(__file__).with_name('inputs.json')


def area(poly):
    p = np.asarray(poly)
    return abs(np.dot(p[:, 0], np.roll(p[:, 1], -1)) -
               np.dot(p[:, 1], np.roll(p[:, 0], -1))) / 2


def inside(poly, x, y):
    """Inclusive convex CCW containment; boundary epsilon is numerical only."""
    out = np.ones(np.broadcast_shapes(np.shape(x), np.shape(y)), dtype=bool)
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        out &= ((b[0]-a[0])*(y-a[1]) - (b[1]-a[1])*(x-a[0])) >= -1e-9
    return out


def intersects(a, b):
    """Strict interior overlap using SAT; touching is not an interior overlap."""
    for p in (a, b):
        for d in np.roll(p, -1, axis=0) - p:
            n = np.array([-d[1], d[0]])
            ap, bp = a @ n, b @ n
            if ap.max() <= bp.min()+1e-9 or bp.max() <= ap.min()+1e-9:
                return False
    return True


def rectangle(x0, x1, width):
    return np.array([[x0, -width/2], [x1, -width/2],
                     [x1, width/2], [x0, width/2]])


def rotate(p, phi):
    c, s = math.cos(phi), math.sin(phi)
    return p @ np.array([[c, s], [-s, c]])


def radial_extent(poly):
    nearest = math.inf
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        d = b-a
        t = np.clip(-np.dot(a, d)/np.dot(d, d), 0, 1)
        nearest = min(nearest, float(np.linalg.norm(a+t*d)))
    return nearest, float(np.linalg.norm(poly, axis=1).max())


def layout(c, cfg):
    lo, hi = cfg['inner_radius'], cfg['outer_radius']
    overlap, margin = cfg['radial_overlap'], cfg['tangential_overlap']
    rings = []
    if c['shape'] == 'rectangle':
        h = c['height']
        centres = np.linspace(lo+h/2-overlap, hi-h/2+overlap, c['rings'])
    else:
        edges = np.linspace(lo, hi, c['rings']+1)
        centres = (edges[:-1]+edges[1:])/2
    for i, r in enumerate(centres):
        if c['shape'] == 'rectangle':
            a, b = r-c['height']/2, r+c['height']/2
            # At largest radius, half-angle leaves a tangential overlap margin.
            halfangle = math.atan((c['width']/2-margin)/b)
            n = 2*math.ceil(math.pi/halfangle/2)
            active = rectangle(a, b, c['width'])
        else:
            n = 2*math.ceil(2*math.pi*r/c['width']/2)
            alpha = math.pi/n + margin/r
            # Chord at outer boundary must cover the requested radial edge.
            a = edges[i]-overlap
            b = (edges[i+1]+overlap)/math.cos(alpha)
            active = np.array([[a*math.cos(alpha), -a*math.sin(alpha)],
                               [b*math.cos(alpha), -b*math.sin(alpha)],
                               [b*math.cos(alpha), b*math.sin(alpha)],
                               [a*math.cos(alpha), a*math.sin(alpha)]])
        guard = cfg['guard']
        radial_extra = guard+cfg['radial_service']
        # Conservative rectangular occupied-space fixture also for wedges.
        body = rectangle(active[:, 0].min()-radial_extra,
                         active[:, 0].max()+radial_extra,
                         2*abs(active[:, 1]).max()+2*guard)
        rings.append({'ring': i, 'radius': float(r), 'count': n,
                      'phase': (i % 2)*math.pi/n,
                      'active': active, 'body': body})
    return rings


def modules(rings, cfg):
    result = []
    for r in rings:
        for j in range(r['count']):
            phi = r['phase']+j*2*math.pi/r['count']
            level = 2*(r['ring'] % 2)+(j % 2)
            result.append({'ring': r['ring'], 'module': j, 'level': level,
                           'z': (level-1.5)*cfg['z_spacing'],
                           'active': rotate(r['active'], phi),
                           'body': rotate(r['body'], phi)})
    return result


def sample(rings, cfg, nr, nphi, vertex=None):
    radius = np.linspace(cfg['inner_radius'], cfg['outer_radius'], nr,
                         endpoint=False)+(cfg['outer_radius']-cfg['inner_radius'])/(2*nr)
    phi = (np.arange(nphi)+0.5)*2*math.pi/nphi
    rr, pp = radius[:, None], phi[None, :]
    hits = np.zeros((nr, nphi), dtype=np.int16)
    for ring in rings:
        step = 2*math.pi/ring['count']
        nearest = np.floor((pp-ring['phase'])/step+0.5).astype(int)
        # Polygons subtend <3 module spacings, checked in tests for every input.
        for dj in (-1, 0, 1):
            index = (nearest+dj) % ring['count']
            theta = pp-ring['phase']-index*step
            factor = 1.0
            if vertex is not None:
                level = 2*(ring['ring'] % 2)+(index % 2)
                z = (level-1.5)*cfg['z_spacing']
                factor = (cfg['disk_z']+z-vertex)/(cfg['disk_z']-vertex)
            hits += inside(ring['active'], rr*factor*np.cos(theta),
                           rr*factor*np.sin(theta))
    weights = np.broadcast_to(rr, hits.shape)
    denom = weights.sum()
    return {'radial_bins': nr, 'phi_bins': nphi,
            'uncovered_bins': int((hits == 0).sum()),
            'uncovered_area_fraction': float(weights[hits == 0].sum()/denom),
            'multiple_hit_area_fraction': float(weights[hits > 1].sum()/denom),
            'mean_sensor_crossings': float((hits*weights).sum()/denom)}


def collisions(mods):
    result = []
    bounds = [(m['body'].min(axis=0), m['body'].max(axis=0)) for m in mods]
    for i, a in enumerate(mods):
        for j in range(i):
            b = mods[j]
            if a['level'] != b['level']:
                continue
            if np.any(bounds[i][0] >= bounds[j][1]) or np.any(bounds[j][0] >= bounds[i][1]):
                continue
            if intersects(a['body'], b['body']):
                result.append([[a['ring'], a['module']], [b['ring'], b['module']]])
    return result


def evaluate(c, cfg, refined):
    rings = layout(c, cfg)
    mods = modules(rings, cfg)
    nr, np_ = cfg['sampling']['radial_bins'], cfg['sampling']['phi_bins']
    sensor_area = sum(area(r['active'])*r['count'] for r in rings)
    extents = [radial_extent(r['body']) for r in rings]
    collisions_ = collisions(mods)
    scans = {'projected': sample(rings, cfg, nr, np_)}
    for vertex in cfg['vertex_z']:
        scans[f'vertex_{vertex:g}_mm'] = sample(rings, cfg, nr, np_, vertex)
    if refined:
        scans['projected_refined'] = sample(rings, cfg, nr*2, np_*2)
        for vertex in cfg['vertex_z']:
            scans[f'vertex_{vertex:g}_mm_refined'] = sample(rings, cfg, nr*2, np_*2, vertex)
    return {'candidate': c, 'module_types': len(rings) if c['shape'] == 'wedge' else 1,
            'module_count': len(mods), 'active_silicon_area_mm2': sensor_area,
            'area_over_annulus': sensor_area/(math.pi*(cfg['outer_radius']**2-cfg['inner_radius']**2)),
            'channel_estimates': [{'cell_mm': cell, 'channels': sensor_area/math.prod(cell)} for cell in cfg['cells']],
            'body_radius_range_mm': [min(x[0] for x in extents), max(x[1] for x in extents)],
            'body_z_extent_mm': 3*cfg['z_spacing']+cfg['body_thickness'],
            'same_level_body_collisions': len(collisions_), 'collision_examples': collisions_[:10],
            'coverage': scans,
            'rings': [{'ring': r['ring'], 'radius_mm': r['radius'], 'modules': r['count'],
                       'phase_rad': r['phase'], 'active_polygon_mm': r['active'].tolist(),
                       'body_polygon_mm': r['body'].tolist()} for r in rings]}


def figure(candidates, cfg, path):
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['svg.hashsalt'] = 'DES-007'
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    for ax, c in zip(axes.flat, candidates):
        rings = layout(c, cfg)
        m = modules(rings, cfg)
        ax.add_collection(PolyCollection([x['body'] for x in m], facecolors='none',
                                        edgecolors='#9ca3af', linewidths=.18))
        ax.add_collection(PolyCollection([x['active'] for x in m],
                                        array=np.array([x['ring'] for x in m]),
                                        cmap='viridis', edgecolors='white', linewidths=.12, alpha=.8))
        for r in (cfg['inner_radius'], cfg['outer_radius']):
            ax.add_patch(plt.Circle((0, 0), r, fill=False, color='#111827', linewidth=.7))
        ax.set(xlim=(-730, 730), ylim=(-730, 730), aspect='equal', xlabel='x [mm]', ylabel='y [mm]',
               title=f"{c['id']}: {len(m)} modules / {len(rings)} rings")
    axes.flat[-1].axis('off')
    axes.flat[-1].text(.04, .9, 'DES-007 · PROTOTYPE\n\nColour: active sensor / ring\nGrey: trial body and service space\nCircles: 200–700 mm target annulus\n\nFour z levels projected together.\nOverlap here is deliberate.\nReadout and supports remain unsigned.\n\nFive-ring rectangle is a gap control.', va='top', fontsize=12)
    fig.suptitle('Short-strip endcap: sensor reuse versus ring-specific outlines', fontsize=16)
    fig.tight_layout()
    fig.savefig(path, metadata={'Date': None})
    plt.close(fig)
    if path.suffix.lower() == '.svg':
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refined', action='store_true')
    parser.add_argument('--input', type=Path, default=INPUT)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/validation/DES-007-ring-study.json')
    parser.add_argument('--figure', type=Path)
    args = parser.parse_args()
    cfg = json.loads(args.input.read_text())
    if cfg['body_thickness'] >= cfg['z_spacing']:
        raise ValueError('Trial bodies must fit strictly between neighbouring z levels')
    result = {'status': 'PROTOTYPE; not detector validation',
              'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'working_tree': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).splitlines(),
              'python': platform.python_version(), 'numpy': np.__version__, 'random_seed': None,
              'randomness': 'none; deterministic polar midpoint grid',
              'input_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'configuration': cfg,
              'results': [evaluate(c, cfg, args.refined) for c in cfg['candidates']]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    if args.figure:
        import matplotlib
        result['matplotlib'] = matplotlib.__version__
        args.output.write_text(json.dumps(result, indent=2)+'\n')
        figure(cfg['candidates'], cfg, args.figure)
    for r in result['results']:
        print(r['candidate']['id'], 'modules', r['module_count'], 'area ratio', round(r['area_over_annulus'], 4),
              'body collisions', r['same_level_body_collisions'],
              'max missing fraction', max(x['uncovered_area_fraction'] for x in r['coverage'].values()))


if __name__ == '__main__':
    main()
