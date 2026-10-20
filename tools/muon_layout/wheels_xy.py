"""True XY sections of the three retained DES040 endcap wheels; drawing only.

Run ``python -B -m tools.muon_layout.wheels_xy`` with NumPy and Matplotlib.
Chambers/support stock use finite prism cuts. Warm sweeps use analytic slices
of the exact rounded-rectangle-distance/slab definition, without a raster.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess

import numpy as np

from .draw import section_polygon
from .geometry import vertices3
from .support import material_parts
from tools.toroid_prototype.geometry import coil_mask

ROOT = Path(__file__).resolve().parents[2]
BASE_REVISION = '99bb67a6d3a65d4ef6de30ff2def8698b3ed053d'
GEOMETRY = ROOT/'docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json'
GEOMETRY_SHA256 = '621b5cb9d45906b338251d527d932abd6b9aca86c84ffaa0918c7e535a17781f'
OUTPUT = ROOT/'docs/validation/DES-040/wheels-2026-10-20/xy-sections'
BLUE = (0., 96/256, 255/256)
COIL = (160/256,)*3


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def xy_cut(body, z):
    return section_polygon(body, [0, 0, 1], z, [1, 0, 0], [0, 1, 0])


def warm_sections(config, z):
    """Analytic horizontal slice of |rounded-rectangle SDF| <= normal/2.

    A positive offset dilates a rounded rectangle, a negative offset erodes it.
    Their horizontal intervals differ by two side strips, or one return strip.
    The tangential slab turns each interval into a rotated XY rectangle.
    """
    a, b = (config['warm'][name]/2 for name in ('normal_m', 'tangent_m'))
    result = []
    for name, group in config['coil_groups'].items():
        hx, hz, rho = (group[k] for k in ('half_r_m', 'half_z_m', 'corner_radius_m'))
        if not 0 < a < rho < min(hx, hz) or b <= 0:
            raise ValueError('Analytic slice requires positive widths and normal half-width < corner radius < half-extents')
        qz = abs(z-group['center_z_m'])-(hz-rho)
        if qz > rho+a:
            continue
        outer = hx+a if qz <= 0 else hx-rho+math.sqrt(max(0., (rho+a)**2-qz*qz))
        if qz < rho-a:
            inner = hx-a if qz <= 0 else hx-rho+math.sqrt(max(0., (rho-a)**2-qz*qz))
            intervals = [(-outer, -inner), (inner, outer)]
        else:
            intervals = [(-outer, outer)]
        for k in range(config['folds']):
            angle = math.radians(group['phi_offset_deg']+360*k/config['folds'])
            er, et = np.array([math.cos(angle), math.sin(angle)]), np.array([-math.sin(angle), math.cos(angle)])
            for index, (lo, hi) in enumerate(intervals):
                lo, hi = lo+group['center_r_m'], hi+group['center_r_m']
                polygon = np.array([[lo, -b], [hi, -b], [hi, b], [lo, b]])
                polygon = polygon[:, :1]*er+polygon[:, 1:]*et
                result.append(dict(group=name, coil=k, interval=index, xy_m=polygon.tolist()))
    return result


def contains(points, polygon):
    p, v = np.asarray(points), np.asarray(polygon)
    edges = np.roll(v, -1, axis=0)-v
    cross = edges[None, :, 0]*(p[:, None, 1]-v[None, :, 1])-edges[None, :, 1]*(p[:, None, 0]-v[None, :, 0])
    return (cross >= -1e-11).all(axis=1)


def sections(geometry):
    endcaps = [p for p in geometry['panels'] if p['kind'] == 'endcap' and p['side'] == 1]
    parts = [(member['id'], part) for member in geometry['supports']['members'] for part in material_parts(member)]
    result = []
    for station, label in ((1, 'Inner'), (2, 'Middle'), (3, 'Outer')):
        selected = [p for p in endcaps if p['station'] == station]
        centers = {p['origin_m'][2] for p in selected}
        if len(centers) != 1:
            raise ValueError('Wheel has no unique source centre plane')
        z = centers.pop()
        chambers = [dict(id=p['id'], xy_m=cut.tolist()) for p in endcaps if (cut := xy_cut(p, z)) is not None]
        if {p['id'] for p in chambers} != {p['id'] for p in selected}:
            raise ValueError('Plane selection differs from actual finite endcap intersections')
        support = [dict(member_id=mid, part_id=p['id'], material=p.get('material'), xy_m=cut.tolist())
                   for mid, p in parts if (cut := xy_cut(p, z)) is not None]
        result.append(dict(station=station, label=label, z_m=z, chambers=chambers,
                           warm_coils=warm_sections(geometry['magnetic_configuration'], z), support_stock=support))
    return result


def controls(geometry, cuts, limit):
    rng = np.random.default_rng(906290)
    records = []
    for cut in cuts:
        z = cut['z_m']
        # Independent exact source membership versus the analytic display polygons.
        points = rng.uniform(-limit, limit, (50000, 2))
        actual = np.zeros(len(points), bool)
        for poly in cut['warm_coils']:
            actual |= contains(points, poly['xy_m'])
        expected = coil_mask(np.c_[points, np.full(len(points), z)], geometry['magnetic_configuration'], 'warm')
        if not np.array_equal(actual, expected):
            raise ValueError('Analytic XY coil section disagrees with exact source membership')
        opposite = {p['id']: xy_cut(p, -z) for p in geometry['panels'] if p['kind'] == 'endcap' and p['side'] == -1 and p['station'] == cut['station']}
        positive = sorted(tuple(sorted(tuple(v) for v in p['xy_m'])) for p in cut['chambers'])
        negative = sorted(tuple(sorted(tuple(v) for v in p)) for p in opposite.values() if p is not None)
        if positive != negative:
            raise ValueError('Opposite endcap has different global XY footprints')
        for p in cut['chambers']:
            source = next(q for q in geometry['panels'] if q['id'] == p['id'])
            v = vertices3(source)
            if not v[:, 2].min() < z < v[:, 2].max():
                raise ValueError('Chamber drawing is not an interior cut')
            if xy_cut(source, v[:, 2].max()+.001) is not None:
                raise ValueError('Off-plane adverse fixture was projected into the cut')
        records.append(dict(station=cut['station'], z_m=z, endcap_panels=len(cut['chambers']),
                            warm_rectangles=len(cut['warm_coils']), support_stock_parts=len(cut['support_stock']),
                            warm_random_points=50000, warm_membership_mismatches=0,
                            opposite_endcap_global_xy_equal=True, off_plane_adverse_cases=len(cut['chambers'])))
    return dict(passed=True, seed=906290, planes=records)


def render(cuts, limit, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Patch
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'path', 'svg.hashsalt': 'DES040-three-wheel-xy'})

    def save(fig, path):
        fig.savefig(path, dpi=200, facecolor='white', metadata={'Date': None} if path.suffix == '.svg' else None)
        if path.suffix == '.svg':
            # Matplotlib's multiline SVG path attributes contain trailing blanks.
            # Keep line breaks (XML attribute whitespace) and all path numbers.
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')

    def panel(ax, cut):
        for key, color, edge, hatch, order in [('warm_coils', COIL, '#707070', None, 2),
                                             ('support_stock', '#d4d4d4', '#777777', '///', 3),
                                             ('chambers', BLUE, '#18365b', None, 4)]:
            polys = [item['xy_m'] for item in cut[key]]
            if polys:
                ax.add_collection(PolyCollection(polys, facecolors=color, edgecolors=edge, linewidths=.32, hatch=hatch, zorder=order))
        ax.set(xlim=(-limit, limit), ylim=(-limit, limit), aspect='equal', xlabel='x [m]', ylabel='y [m]')
        ax.grid(color='#dce1e5', lw=.45); ax.set_axisbelow(True)
        ax.set_title(f"{cut['label']} wheel · z = +{cut['z_m']:g} m\n{len(cut['chambers'])} endcap chamber outlines", fontsize=13, pad=12)

    legend = [Patch(facecolor=BLUE, edgecolor='#18365b', label='Endcap chamber envelope'),
              Patch(facecolor=COIL, edgecolor='#707070', label='Warm coil envelope'),
              Patch(facecolor='#d4d4d4', edgecolor='#777777', hatch='///', label='Frame material stock; hollow cavities empty')]
    def decorate(fig, single=False):
        fig.suptitle('Endcap wheels · x–y cross-sections', fontsize=19, y=.965)
        fig.text(.5, .905, 'Positive endcap · global x and y axes · common metric scale', ha='center', fontsize=11)
        fig.legend(handles=legend, loc='lower center', ncol=1 if single else 3, frameon=False, bbox_to_anchor=(.5, .065), fontsize=10)
        fig.text(.5, .025, 'DRAFT PROTOTYPE · Finite plane intersections; chamber internals are not modeled.', ha='center', fontsize=9)

    fig, axes = plt.subplots(1, 3, figsize=(18.6, 8.0))
    for ax, cut in zip(axes, cuts):
        panel(ax, cut)
    decorate(fig); fig.subplots_adjust(left=.045, right=.988, top=.81, bottom=.18, wspace=.20)
    for ext in ('png', 'svg'):
        save(fig, output/f'endcap-wheels-xy.{ext}')
    plt.close(fig)
    for cut in cuts:
        fig, ax = plt.subplots(figsize=(8.0, 9.3)); panel(ax, cut); decorate(fig, True)
        fig.subplots_adjust(left=.10, right=.96, top=.82, bottom=.23)
        for ext in ('png', 'svg'):
            save(fig, output/f"wheel-{cut['station']}-xy.{ext}")
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', type=Path, default=GEOMETRY)
    parser.add_argument('--expected-geometry-sha256', default=GEOMETRY_SHA256)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    before = sha(args.geometry)
    if before != args.expected_geometry_sha256:
        raise ValueError('Source geometry changed; choose the reviewed input explicitly')
    geometry = json.loads(args.geometry.read_text())
    cuts = sections(geometry)
    vertices = np.vstack([p['xy_m'] for cut in cuts for key in ('chambers', 'warm_coils', 'support_stock') for p in cut[key]])
    limit = float(math.ceil(np.abs(vertices).max()+.3))
    checked = controls(geometry, cuts, limit)
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output/'sections.json', dict(coordinates='metres, right-handed global xyz; positive z endcap; no viewer-facing mirror',
        scope='Actual endcap chamber sections and intersecting warm-coil/frame stock context; no barrel chamber projection or geometry change.',
        common_xy_limits_m=[-limit, limit], sections=cuts))
    render(cuts, limit, args.output)
    import matplotlib
    source_paths = [Path(__file__), ROOT/'tools/muon_layout/draw.py', ROOT/'tools/muon_layout/geometry.py',
                    ROOT/'tools/muon_layout/support.py', ROOT/'tools/toroid_prototype/geometry.py']
    committed = {}
    for path in source_paths:
        name = str(path.relative_to(ROOT))
        recorded = subprocess.run(['git', 'show', 'HEAD:'+name], cwd=ROOT, capture_output=True)
        committed[name] = recorded.returncode == 0 and recorded.stdout == path.read_bytes()
    write_json(args.output/'provenance.json', dict(status='DRAFT / isolated drawing-only PROTOTYPE',
        requested_by='https://github.com/asalzburger/nodd/pull/90#issuecomment-6285630535',
        input_revision=BASE_REVISION, geometry=str(args.geometry.resolve().relative_to(ROOT)), geometry_sha256=before,
        execution_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        source_sha256={str(p.relative_to(ROOT)): sha(p) for p in source_paths},
        execution_source_matches_head=committed,
        methods=dict(chambers='Finite convex prism / XY plane intersection; existing helper rounds coordinates to 1e-10 m',
                     warm_coils='Analytic offset rounded-rectangle intervals intersected with tangential slab; no raster or tessellation',
                     frame='Finite material-parts prism sections; hollow cavities empty; not outer reservations or a mass union'),
        runtime=dict(python=platform.python_version(), numpy=np.__version__, matplotlib=matplotlib.__version__), controls=checked,
        artifacts={p.name: dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(args.output.iterdir()) if p.suffix in ('.png', '.svg') or p.name == 'sections.json'}))
    if sha(args.geometry) != before:
        raise ValueError('Input geometry changed during drawing')
    print(json.dumps(checked, indent=2))


if __name__ == '__main__':
    main()
