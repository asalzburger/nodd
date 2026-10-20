"""Source-derived inner-barrel feasibility figures; no candidate adoption.

The below-coil picture is an explicitly invalid counterfactual. The outward
picture is an unselected finite-packing diagnostic, not a replacement layout.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np

from . import wheels_xy as xy

ROOT = Path(__file__).resolve().parents[2]
SCOPE = ROOT / 'docs/validation/DES-040/inner-barrel-2026-10-20'
BASE = ROOT / 'docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json'
Z = 1.0
BLUE, GREY, RED = '#0060fe', '#a0a0a0', '#c52626'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_figure(fig, stem):
    for ext in ('png', 'svg'):
        p = stem.with_suffix('.' + ext)
        fig.savefig(p, dpi=180, facecolor='white', metadata={'Date': None} if ext == 'svg' else None)
        if ext == 'svg':
            p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines()).rstrip() + '\n')


def produce():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Patch, Rectangle
    matplotlib.rcParams['svg.hashsalt'] = 'nodd-inner-barrel-feasibility'
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    source_paths = [Path(__file__), ROOT / 'tools/muon_layout/wheels_xy.py',
                    ROOT / 'tools/muon_layout/draw.py', ROOT / 'tools/muon_layout/geometry.py']
    for p in source_paths:
        assert p.read_bytes() == subprocess.check_output(['git', 'show', revision + ':' + str(p.relative_to(ROOT))], cwd=ROOT)
    paths = [BASE, SCOPE / 'interface-check.json', SCOPE / 'conditional-check.json', SCOPE / 'conditional-B1-outlines.json']
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    base, interface, conditional, outlines = [json.loads(p.read_text()) for p in paths]
    current = [p for p in base['panels'] if p['kind'] == 'barrel' and p['station'] == 1]
    assert len(current) == 96 and len(outlines['panels']) == 144
    hcal = interface['actual_HCAL_XY_geometry']
    assert hcal['z_witness_m'] == Z and hcal['steel_and_cover_abs_z_limit_m'] > Z
    covers = [dict(id=p['id'], material='Aluminium', xy_m=xy.xy_cut(p, Z).tolist()) for p in hcal['back_cover_bodies']]
    steel = []
    tangent, inset = math.tan(hcal['steel_tangent_half_angle_rad']), hcal['steel_edge_inset_m']
    for sector in range(hcal['sector_count']):
        angle = 2 * math.pi * sector / hcal['sector_count']
        er, et = np.array([math.cos(angle), math.sin(angle)]), np.array([-math.sin(angle), math.cos(angle)])
        for index, (a, b) in enumerate(hcal['steel_bands_m']):
            v = np.array([[a, -a*tangent+inset], [b, -b*tangent+inset],
                          [b, b*tangent-inset], [a, a*tangent-inset]])
            steel.append(dict(id=f'HCAL/S{sector:02d}/Steel{index:02d}', material='Steel235',
                              xy_m=(v[:, :1]*er + v[:, 1:]*et).tolist()))
    warm = xy.warm_sections(base['magnetic_configuration'], Z)
    invalid = copy.deepcopy(current)
    rbelow = interface['hard_bounds']['below_coil_R_max_m']
    odd_half = interface['angular_projection']['widened_intercoil_half_width_for_0p1deg_full_depth_overlap_m']
    for p in invalid:
        p['id'] = 'INVALID-BELOW/' + p['id']
        facet = round(p['compartment']['phi_deg']/15) % 24
        if facet % 2 == 0:
            p['origin_m'] = (np.asarray(p['origin_m']) * (rbelow/5.2)).tolist()
        else:
            for v in p['vertices_m']:
                v[0] = math.copysign(odd_half, v[0])
        p.pop('coil_certificate', None)
        p.pop('support_certificate', None)
    cuts = {}
    for label, panels in [('current', current), ('invalid_below', invalid), ('unselected_outward', outlines['panels'])]:
        cuts[label] = [dict(id=p['id'], xy_m=cut.tolist()) for p in panels if (cut := xy.xy_cut(p, Z)) is not None]
        assert len(cuts[label]) == 24
    out = SCOPE / 'views'
    out.mkdir(exist_ok=True)
    fig = plt.figure(figsize=(18, 10))
    grid = fig.add_gridspec(2, 3, height_ratios=[1.6, 1])
    titles = [('current', 'Current B1 · selected outline candidate'),
              ('invalid_below', 'Requested below-coil trial · INVALID: HCAL collision'),
              ('unselected_outward', 'Outward inter-coil trial · UNSELECTED')]
    for i, (label, title) in enumerate(titles):
        ax = fig.add_subplot(grid[0, i])
        for p in steel:
            ax.add_patch(Polygon(p['xy_m'], facecolor='#cdba9d', edgecolor='#a28c6c', lw=.2))
        for p in covers:
            ax.add_patch(Polygon(p['xy_m'], facecolor='#e9941b', edgecolor='#a96500', lw=.7))
        for p in warm:
            ax.add_patch(Polygon(p['xy_m'], facecolor=GREY, edgecolor='#555555', lw=.7))
        for p in cuts[label]:
            bad = label == 'invalid_below' and '/F00/' in p['id']
            ax.add_patch(Polygon(p['xy_m'], facecolor='none' if label == 'invalid_below' else BLUE,
                edgecolor=RED if label == 'invalid_below' else '#163f69', lw=1.2 if bad else .7,
                hatch='///' if label == 'invalid_below' else None))
        if label == 'invalid_below':
            ax.plot(4.12, 0, 'o', color=RED, ms=5)
            ax.annotate('Actual steel/chamber\ninterior witness', (4.12, 0), xytext=(4.8, -.55),
                        arrowprops={'arrowstyle': '->', 'color': RED}, color=RED, fontsize=9)
        ax.set(xlim=(3.2, 6.4), ylim=(-.8, 3.7), xlabel='x [m]', ylabel='y [m]', title=title)
        ax.set_aspect('equal')
        ax.grid(alpha=.2)
    ax = fig.add_subplot(grid[1, :])
    for a, b in hcal['steel_bands_m']:
        ax.add_patch(Rectangle((a, 2.65), b-a, .42, color='#cdba9d'))
    ax.add_patch(Rectangle((4.148, 2.65), .01, .42, color='#e9941b'))
    btface = interface['hard_bounds']['BT_warm_inner_face_m']
    ax.add_patch(Rectangle((btface, 1.85), .5, .42, color=GREY))
    ax.add_patch(Rectangle((rbelow-.25, 1.05), .5, .42, facecolor='none', hatch='///', edgecolor=RED))
    ax.add_patch(Rectangle((5.2-.25, .25), .5, .42, color=BLUE))
    labels = [(3.1, 'HCAL steel + rear cover (actual source subset)'),
              (2.3, 'BT warm inner leg'), (1.5, 'Requested 500 mm below-coil chamber (invalid)'),
              (.7, 'Current 500 mm coil-plane chamber')]
    for yy, label in labels:
        ax.text(5.55, yy-.24, label, va='center', fontsize=10)
    gap_a, gap_b = 4.158+.05, btface-.05
    ax.annotate('', (gap_a, 3.5), (gap_b, 3.5), arrowprops={'arrowstyle': '<->', 'color': '#333333'})
    ax.text((gap_a+gap_b)/2, 3.67, '92 mm room after both 50 mm margins\n500 mm required', ha='center', fontsize=10)
    ax.set(xlim=(3.6, 7.3), ylim=(0, 4.4), xlabel='Radial coordinate on coil plane phi=0° [m]', yticks=[],
           title='Finite radial budget at z=+1 m · the conservative HCAL corner circle is not used as material')
    ax.grid(axis='x', alpha=.2)
    fig.suptitle('Inner-barrel feasibility · current, invalid requested placement and unselected alternative', fontsize=17)
    fig.legend(handles=[Patch(facecolor=BLUE, label='Chamber outlines'), Patch(facecolor=GREY, label='Warm coil envelope'),
                        Patch(facecolor='#cdba9d', label='Actual HCAL steel plates'), Patch(facecolor='#e9941b', label='Actual HCAL Al rear cover')],
               loc='lower center', ncol=4, bbox_to_anchor=(.5, .055), frameon=False)
    fig.text(.5, .015, 'DRAFT PROTOTYPE · z=+1 m transverse cuts; frame omitted from this detail. Full-volume checks and longitudinal losses are reported separately.\n'
             'For the retained width, other coil-plane footprints have at most 19.75 mm depth room after clearances. Neither trial changes the active 888-chamber candidate.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .13, 1, .95))
    save_figure(fig, out / 'inner-barrel-feasibility')
    plt.close(fig)
    longitudinal = {}
    fig, axes = plt.subplots(1, 2, figsize=(15, 5), sharex=True, sharey=True)
    for ax, label, panels in [(axes[0], 'Current selected B1', current), (axes[1], 'Unselected outward B1 · frame cuts retained', outlines['panels'])]:
        chosen = [p for p in panels if abs(p['compartment']['phi_deg']-15) < 1e-8]
        longitudinal[label] = [dict(id=p['id'], vertices_tangent_z_m=p['vertices_m']) for p in chosen]
        for p in chosen:
            v = np.array(p['vertices_m'])
            ax.add_patch(Polygon(v[:, [1, 0]], facecolor=BLUE, edgecolor='#163f69', lw=.6))
        ax.set(xlim=(-6.7, 6.7), ylim=(-1.1, 1.1), xlabel='z [m]', ylabel='local tangent [m]', title=label+f' · {len(chosen)} cassettes on phi15°')
        ax.grid(alpha=.2)
    fig.suptitle('Actual B1 longitudinal source footprints · common scales', fontsize=16)
    fig.text(.5, .025, 'DRAFT / UNSELECTED · Fixed-frame packing, relocated z seams and finite ends reduce the all-three-station proxy in this trial.', ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .08, 1, .92))
    save_figure(fig, out / 'inner-barrel-longitudinal')
    plt.close(fig)
    assert all(sha(ROOT / p) == h for p, h in hashes.items())
    report = dict(status='DRAFT feasibility drawing; requested below-coil trial invalid; outward trial unselected; active geometry unchanged',
        source_revision=revision, source_sha256={str(p.relative_to(ROOT)): sha(p) for p in source_paths},
        input_sha256=hashes, section_z_m=Z, common_xy_limits_m=[[3.2, 6.4], [-.8, 3.7]],
        cuts=cuts, hcal_steel=steel, hcal_rear_covers=covers, warm_coils=warm, longitudinal=longitudinal,
        invalid_display_only_radius_m=rbelow, invalid_display_only_odd_half_width_m=odd_half,
        artifacts={p.name: sha(p) for p in out.iterdir() if p.suffix in ('.png', '.svg')},
        limits=['Actual HCAL occupied subset includes steel and Al rear cover, not the entire material assembly.',
                'Frame omitted in XY detail but retained in all whole-volume and longitudinal packing checks.',
                'No active geometry, OBJ, field, native transport, response or reconstruction change.'])
    (out / 'views.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(source_revision=revision, sections={k: len(v) for k, v in cuts.items()}), indent=2))


if __name__ == '__main__':
    produce()
