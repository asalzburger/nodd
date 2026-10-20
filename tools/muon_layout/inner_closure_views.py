"""Drawing-only views of frozen, unadopted inner-wheel segmentation studies.

The independent module/interface calculations and their exact source hashes are
retained beside the drawings. This does not rewrite the current candidate.
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

from . import geometry as g
from .wheels import wheel_dimensions, wheel_certificate
from tools.toroid_prototype.geometry import coil_mask

ROOT = Path(__file__).resolve().parents[2]
BASE = '15015d378b5b77b3bb11698809d1680d12b8a91c'
GEOMETRY = ROOT/'docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json'
OUTPUT = ROOT/'docs/validation/DES-040/inner-closure-2026-10-20'
BLUE = (0., 96/256, 255/256)
GREY = (160/256,)*3
MODELS = ('current_one_band', 'two_bands', 'three_bands_slot_localised')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def bodies(geometry, study):
    spec = geometry['wheel_revision']['inner_wheel']
    models = {'current_one_band': [p for p in geometry['panels'] if p.get('wheel') == 'inner_wheel' and p['side'] == 1]}
    for name in MODELS[1:]:
        models[name] = []
        for band in study['optional_dimensions'][name]:
            u0, u1 = band['inner_base_apothem_m'], band['outer_base_apothem_m']
            w0, w1 = band['inner_base_m']/2, band['outer_base_m']/2
            for k in range(spec['sectors']):
                a = math.radians(spec['phase_deg']+360*k/spec['sectors'])
                q = np.array([[math.cos(a), -math.sin(a), 0.], [math.sin(a), math.cos(a), 0.], [0., 0., 1.]])
                models[name].append(g.prism(f'UNADOPTED/{name}/B{band["band"]}/S{k:02d}', 'endcap',
                    [0., 0., spec['abs_z_m']], q, [[u0, -w0], [u1, -w1], [u1, w1], [u0, w0]],
                    geometry['wheel_revision']['depth_m'], station=1, side=1, study_band=band['band']))
    return models


def slot_polygons(geometry, clearance=0.):
    config = geometry['magnetic_configuration']
    bt = config['coil_groups']['barrel']
    radius = bt['center_r_m']-bt['half_r_m']
    a, b = config['warm']['normal_m']/2+clearance, config['warm']['tangent_m']/2+clearance
    result = []
    for k in range(config['folds']):
        angle = math.radians(bt['phi_offset_deg']+360*k/config['folds'])
        er, et = np.array([math.cos(angle), math.sin(angle)]), np.array([-math.sin(angle), math.cos(angle)])
        local = np.array([[radius-a, -b], [radius+a, -b], [radius+a, b], [radius-a, b]])
        result.append(local[:, :1]*er+local[:, 1:]*et)
    return result


def negative_fixture(geometry):
    config = geometry['wheel_revision']
    spec = dict(config['inner_wheel'])
    spec.pop('extra_BT_box_margin_m')
    spec['seam_normal_width_m'] = .02
    d = wheel_dimensions(spec, geometry['magnetic_configuration'], config['coil_clearance_m'])
    a = math.radians(spec['phase_deg'])
    q = np.array([[math.cos(a), -math.sin(a), 0.], [math.sin(a), math.cos(a), 0.], [0., 0., 1.]])
    u0, u1, w0, w1 = d['u0_m'], d['u1_m'], d['inner_base_m']/2, d['outer_base_m']/2
    body = g.prism('NEGATIVE/closing-sector', 'endcap', [0., 0., spec['abs_z_m']], q,
                   [[u0, -w0], [u1, -w1], [u1, w1], [u0, w0]], config['depth_m'], station=1, side=1)
    points = np.array([[4.6, .1, spec['abs_z_m']+offset] for offset in (-.25, 0., .25)])
    inside = g.contains(body, points)
    occupied = coil_mask(points, geometry['magnetic_configuration'], 'warm')
    proof = wheel_certificate(body, config, geometry['magnetic_configuration'])
    if not inside.all() or not occupied.all() or proof['clear']:
        raise ValueError('Closing-the-gap adverse fixture did not demonstrate the BT conflict')
    return dict(scope='Counterfactual negative fixture, not a proposed chamber', points_m=points.tolist(),
                inside_20mm_seam_sector=inside.tolist(), inside_BT_warm=occupied.tolist(), coil_certificate=proof)


def render(geometry, study, models, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Patch
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'path', 'svg.hashsalt': 'DES040-inner-closure'})
    warm = slot_polygons(geometry)
    reserved = slot_polygons(geometry, geometry['wheel_revision']['coil_clearance_m'])

    def save(fig, name):
        for ext in ('png', 'svg'):
            path = output/f'{name}.{ext}'
            fig.savefig(path, dpi=200, facecolor='white', metadata={'Date': None} if ext == 'svg' else None)
            if ext == 'svg':
                path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        plt.close(fig)

    labels = ('Current · one long trapezoid per sector', 'Unadopted option · two radial bands', 'Diagnostic only · three radial bands')
    fig, axes = plt.subplots(1, 3, figsize=(18.6, 8.8))
    for ax, name, label in zip(axes, MODELS, labels):
        polys = [g.vertices3(p)[:4, :2] for p in models[name]]
        ax.add_collection(PolyCollection(polys, facecolors=BLUE, edgecolors='#16385f', linewidths=.45, zorder=2))
        ax.add_collection(PolyCollection(warm, facecolors=GREY, edgecolors='#666666', linewidths=.5, zorder=3))
        ax.add_collection(PolyCollection(reserved, facecolors='none', edgecolors='#b45a16', linewidths=.65, linestyles='--', zorder=4))
        if name == MODELS[2]:
            thin = [g.vertices3(p)[:4, :2] for p in models[name] if p['study_band'] == 2]
            ax.add_collection(PolyCollection(thin, facecolors='none', edgecolors='#b5202e', linewidths=.8, zorder=5))
        ax.set(xlim=(-5.8, 5.8), ylim=(-5.8, 5.8), aspect='equal', xlabel='x [m]', ylabel='y [m]')
        ax.grid(color='#dce1e5', lw=.4); ax.set_axisbelow(True)
        ax.set_title(f'{label}\n{len(polys)} chamber outlines per end', fontsize=12.5, pad=12)
        m = study['metrics'][name]
        text = f"Planar area loss: {100*m['midplane_area_loss_vs_circular_annulus']:.1f}%\nFull-depth same-chamber ray loss: {100*m['IP_full_depth_same_chamber_loss']:.1f}%"
        ax.text(.5, -.16, text, transform=ax.transAxes, ha='center', va='top', fontsize=11)
        if name == MODELS[2]:
            span = study['optional_dimensions'][name][-1]['base_distance_m']
            ax.text(.5, -.29, f'Outer band {span:.3f} m < 0.50 m minimum', color='#b5202e', transform=ax.transAxes, ha='center', fontsize=10)
    fig.suptitle('Inner-wheel gaps: fixed BT slots and avoidable fan-shaped gaps', fontsize=18, y=.963)
    fig.text(.5, .91, 'Same z = +6.7456 m, 0.500 m depth and fixed magnets/frame · Segmentation alternatives are not adopted', ha='center', fontsize=11)
    handles = [Patch(facecolor=BLUE, edgecolor='#16385f', label='Empty chamber envelope'),
               Patch(facecolor=GREY, label='BT inner-leg warm envelope'),
               Patch(facecolor='none', edgecolor='#b45a16', ls='--', label='50 mm conservative clearance box')]
    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(.5, .079), fontsize=10)
    fig.text(.5, .024, 'DRAFT geometry study · Inner-wheel/BT context only · Area and straight-IP-ray losses use different ideal-annulus denominators.\n'
             'Ray loss requires both depth faces in the same chamber. No ACTS transport or reconstruction-efficiency improvement is established.', ha='center', fontsize=9)
    fig.subplots_adjust(left=.045, right=.985, top=.81, bottom=.285, wspace=.18)
    save(fig, 'inner-closure-comparison')

    fig, ax = plt.subplots(figsize=(10.5, 5.7))
    around_seam = [p for p in models[MODELS[0]] if abs(p['compartment']['phi_deg'][0]) < 1e-8 or abs(p['compartment']['phi_deg'][1]-360) < 1e-8]
    ax.add_collection(PolyCollection([g.vertices3(p)[:4, :2] for p in around_seam], facecolors=BLUE, edgecolors='#16385f', linewidths=.9))
    ax.add_collection(PolyCollection([warm[0]], facecolors=GREY, edgecolors='#666666', linewidths=.9, zorder=3))
    ax.add_collection(PolyCollection([reserved[0]], facecolors='none', edgecolors='#b45a16', linewidths=1.5, linestyles='--', zorder=4))
    ax.plot(4.6, .1, 'x', color='#b5202e', ms=8, mew=2, zorder=5)
    ax.annotate('A 20 mm-seam sector would overlap\nthe BT warm envelope here', xy=(4.6, .1), xytext=(2.4, .92),
                arrowprops=dict(arrowstyle='->', color='#b5202e'), color='#b5202e', fontsize=10, ha='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=.95, boxstyle='round,pad=.3'))
    ax.annotate('The straight chamber edge spreads the slot\ninto radial regions with no BT leg', xy=(2.65, .12), xytext=(1.7, -.93),
                arrowprops=dict(arrowstyle='->', color='#333333'), color='#333333', fontsize=10, ha='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=.95, boxstyle='round,pad=.3'))
    ax.set(xlim=(.55, 5.65), ylim=(-1.2, 1.2), aspect='equal', xlabel='u [m] · along the BT seam direction', ylabel='v [m] · tangential to the BT leg')
    ax.grid(color='#dce1e5', lw=.4); ax.set_axisbelow(True)
    ax.set_title('Current inner wheel · detail around the BT seam at phi = 0°', fontsize=15, pad=16)
    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(.5, .055), fontsize=9)
    fig.text(.5, .018, 'DRAFT source geometry · BT warm box u = 4.35–4.85 m, |v| ≤ 0.30 m; clearance box adds 0.05 m.', ha='center', fontsize=9)
    fig.subplots_adjust(left=.09, right=.98, top=.86, bottom=.18)
    save(fig, 'bt-clearance-detail')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args(); output = args.output
    study = json.loads((output/'review/module-check.json').read_text())
    if study['input_revision'] != BASE:
        raise ValueError('Study source revision changed')
    for name, digest in study['sources'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Frozen study input changed: '+name)
    geometry = json.loads(GEOMETRY.read_text())
    models = bodies(geometry, study)
    display = {name: [dict(id=p['id'], band=p.get('study_band'), xy_m=g.vertices3(p)[:4, :2].tolist()) for p in panels] for name, panels in models.items()}
    save_json(output/'display-polygons.json', dict(status='Unadopted study; positive endcap drawing coordinates only', models=display))
    adverse = negative_fixture(geometry)
    render(geometry, study, models, output)
    import matplotlib
    current = geometry['wheel_dimensions']['inner_wheel']; m, b = current['seam_slope'], current['seam_intercept_m']
    gaps = {str(u): 2*(m*u+b) for u in (1., 3., 4.3, 4.6, 4.9, 5.3)}
    sources = [Path(__file__), ROOT/'tools/muon_layout/wheels.py', ROOT/'tools/muon_layout/geometry.py',
               ROOT/'tools/toroid_prototype/geometry.py', output/'review/module-check.json', output/'review/interface-check.json']
    matches = {}
    for path in sources:
        name = str(path.relative_to(ROOT))
        old = subprocess.run(['git', 'show', 'HEAD:'+name], cwd=ROOT, capture_output=True)
        matches[name] = old.returncode == 0 and old.stdout == path.read_bytes()
    save_json(output/'views-provenance.json', dict(status='DRAFT / unadopted feasibility views', input_revision=BASE,
        execution_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        source_sha256={str(p.relative_to(ROOT)): sha(p) for p in sources}, execution_source_matches_head=matches,
        current_local_seam_tangent_gap_m=gaps,
        negative_closing_gap_fixture=adverse, runtime=dict(python=platform.python_version(), numpy=np.__version__, matplotlib=matplotlib.__version__),
        artifacts={p.name: dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(output.iterdir()) if p.suffix in ('.png', '.svg') or p.name == 'display-polygons.json'}))
    print(json.dumps(dict(passed=True, displayed_counts={name: len(panels) for name, panels in models.items()}, negative_fixture=adverse), indent=2))


if __name__ == '__main__':
    main()
