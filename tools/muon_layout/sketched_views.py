"""Actual barrel XY sections and longitudinal cassette footprints, before/after.

Geometry-only display: all polygons come from source finite prisms. No detector
volume, magnetic source or historical artifact is changed by this module.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from . import geometry as geo
from . import wheels_xy as xy
from .support import material_parts

ROOT = Path(__file__).resolve().parents[2]
PREFIX = ROOT / 'docs/validation/DES-040/sketched-stagger-2026-10-20'
BLUE, GRAY = '#0060fe', '#a0a0a0'
SECTION_Z_M = .5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_figure(fig, stem):
    for extension in ('png', 'svg'):
        path = stem.with_suffix('.' + extension)
        fig.savefig(path, dpi=180, facecolor='white', metadata={'Date': None} if extension == 'svg' else None)
        if extension == 'svg':
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()).rstrip() + '\n')


def produce(before_path, after_path, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Patch
    matplotlib.rcParams['svg.hashsalt'] = 'nodd-sketched-stagger'
    before, after = [json.loads(Path(p).read_text()) for p in (before_path, after_path)]
    assert before['magnetic_configuration'] == after['magnetic_configuration']
    assert before['supports'] == after['supports']
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    cuts, longitudinal, controls = {}, {}, {}
    rng = np.random.default_rng(906321)
    probes = rng.uniform(-10, 10, (50000, 2))
    world = np.c_[probes, np.full(len(probes), SECTION_Z_M)]
    for label, geometry in (('before', before), ('after', after)):
        cut = [dict(id=p['id'], station=p['station'], xy_m=xy.xy_cut(p, SECTION_Z_M).tolist())
               for p in geometry['panels'] if p['kind'] == 'barrel' and xy.xy_cut(p, SECTION_Z_M) is not None]
        cuts[label] = cut
        actual, shown = np.zeros(len(probes), bool), np.zeros(len(probes), bool)
        for p in geometry['panels']:
            if p['kind'] == 'barrel':
                lo, hi = geo.aabb(p)
                if lo[2] <= SECTION_Z_M <= hi[2]:
                    actual |= geo.contains(p, world)
        for p in cut:
            shown |= xy.contains(probes, p['xy_m'])
        assert np.array_equal(actual, shown)
        longitudinal[label] = []
        for p in geometry['panels']:
            if p['kind'] != 'barrel':
                continue
            phase = p['compartment']['phi_deg']
            selected_phase = 22.5 if label == 'after' and p['station'] == 2 else 15.
            if abs((phase - selected_phase + 180) % 360 - 180) < 1e-8:
                longitudinal[label].append(dict(id=p['id'], station=p['station'],
                    vertices_tangent_z_m=p['vertices_m'], radius_m=float(np.linalg.norm(p['origin_m'][:2])), phi_deg=phase))
        controls[label] = dict(section_chamber_polygons=len(cut), source_membership_points=len(probes),
            membership_mismatches=0, longitudinal_chambers=len(longitudinal[label]))
    warm = xy.warm_sections(after['magnetic_configuration'], SECTION_Z_M)
    stock = [dict(id=part['id'], xy_m=polygon.tolist())
             for member in after['supports']['members'] for part in material_parts(member)
             if (polygon := xy.xy_cut(part, SECTION_Z_M)) is not None]
    context_xy = np.vstack([p['xy_m'] for panels in cuts.values() for p in panels] +
                           [p['xy_m'] for p in warm + stock])
    context_limit = float(np.ceil(np.abs(context_xy).max() + .3))
    fig, axes = plt.subplots(2, 2, figsize=(14, 13))
    for column, label in enumerate(('before', 'after')):
        for row, zoom in enumerate((False, True)):
            ax = axes[row, column]
            for p in cuts[label]:
                ax.add_patch(Polygon(p['xy_m'], facecolor=BLUE, edgecolor='#12365b', lw=.45))
            for p in warm:
                ax.add_patch(Polygon(p['xy_m'], facecolor=GRAY, edgecolor='#555555', lw=.5))
            for p in stock:
                ax.add_patch(Polygon(p['xy_m'], facecolor='#d5d5d5', hatch='///', edgecolor='#777777', lw=.3))
            ax.set_aspect('equal')
            ax.set(xlim=(3.7, 5.7) if zoom else (-context_limit, context_limit),
                   ylim=(-.3, 3.1) if zoom else (-context_limit, context_limit), xlabel='x [m]', ylabel='y [m]')
            ax.grid(alpha=.2)
            ax.set_title(('Before' if label == 'before' else 'Inward B1; B2 offset 7.5°') +
                         (' · one inner C12 cell' if zoom else ' · all three barrel stations'))
    fig.suptitle(f'Barrel chamber sections at z=+{SECTION_Z_M:g} m · actual finite cuts', fontsize=17)
    fig.legend(handles=[Patch(facecolor=BLUE, label='Chamber envelope'),
        Patch(facecolor=GRAY, label='Warm coil envelope'), Patch(facecolor='#d5d5d5', hatch='///', label='Frame stock')],
        loc='lower center', ncol=3, bbox_to_anchor=(.5, .035), frameon=False)
    fig.text(.5, .012, 'DRAFT PROTOTYPE · Angular overlap is not solid overlap. Interior display slice; acceptance uses the full direction bank.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .07, 1, .95))
    save_figure(fig, output / 'barrel-cross-sections')
    plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(18, 8), sharex=True)
    for row, label in enumerate(('before', 'after')):
        for column, station in enumerate((1, 2, 3)):
            ax = axes[row, column]
            panels = [p for p in longitudinal[label] if p['station'] == station]
            for p in panels:
                v = np.asarray(p['vertices_tangent_z_m'])
                ax.add_patch(Polygon(v[:, [1, 0]], facecolor=BLUE, edgecolor='#18365b', lw=.5))
            max_length = max(float(np.ptp(np.asarray(p['vertices_tangent_z_m'])[:, 1])) for p in panels)
            ax.set(xlim=(-13, 13), ylim=(-1.5, 1.5), xlabel='z [m]', ylabel='local tangent [m]')
            ax.grid(alpha=.2)
            radius = sorted({round(p['radius_m'], 6) for p in panels})
            ax.set_title(f'{label.capitalize()} · B{station} · {len(panels)} cassettes\nR apothem {radius} m · max z length {max_length:.3f} m', fontsize=10)
    fig.suptitle('Longitudinal packing · B1/B3 phi=15°, B2 after phi=22.5°', fontsize=16)
    fig.text(.5, .02, 'DRAFT PROTOTYPE · Common z and tangent scales. Only one facet shown; the full inventory includes every facet.', ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .055, 1, .94))
    save_figure(fig, output / 'longitudinal-packing')
    plt.close(fig)
    source_paths = [Path(__file__), ROOT / 'tools/muon_layout/wheels_xy.py', ROOT / 'tools/muon_layout/draw.py',
                    ROOT / 'tools/muon_layout/geometry.py', ROOT / 'tools/muon_layout/support.py', ROOT / 'tools/toroid_prototype/geometry.py']
    report = dict(status='DRAFT source-derived views; no efficiency or engineering acceptance',
        before_geometry_sha256=sha(before_path), after_geometry_sha256=sha(after_path),
        section_z_m=SECTION_Z_M, display_slice_choice='Central interior cassette slice; avoids using a z seam as a representative chamber cross-section.',
        common_xy_limits_m=[-context_limit, context_limit], zoom_xy_m=[[3.7, 5.7], [-.3, 3.1]],
        cuts=cuts, warm_coils=warm, support_stock=stock, longitudinal_selection='B1/B3 phi15; B2 before phi15, after phi22.5',
        longitudinal=longitudinal, controls=controls,
        source_sha256={str(p.relative_to(ROOT)): sha(p) for p in source_paths},
        artifacts={p.name: sha(p) for p in sorted(output.iterdir()) if p.suffix in ('.png', '.svg')})
    (output / 'views.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    return controls


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before', type=Path, default=ROOT / 'docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json')
    p.add_argument('--after', type=Path, default=PREFIX / 'candidate/geometry.json')
    p.add_argument('--output', type=Path, default=PREFIX / 'views')
    a = p.parse_args()
    print(json.dumps(produce(a.before, a.after, a.output), indent=2))


if __name__ == '__main__':
    main()
