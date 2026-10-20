"""Static review figures from retained native wheel-analysis arrays only.

CLI: ``draw.py ANALYSIS_DIR FIGURE_DIR``. Neither boundary intersections nor
detector shapes are generated here. Incomplete events keep their map cells.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.muon_layout.wheels_acts.analyze import METRICS, sha, save, source_state, validate_primaries
from tools.muon_layout.acts.draw import _case, _grid, _charge_label, _momentum_label, _scope

BLUE = (0., .375, .996094)
OUTPUT_NAMES = ('hit-positions.png', 'entrance-six-faces.png', 'entrance-three-pairs.png',
                'entrance-endcap-pairs.png', 'endcap-wheel-1.png', 'endcap-wheel-2.png',
                'endcap-wheel-3.png', 'momentum-coverage.png', 'wheel-availability.png')


def load(path):
    path = Path(path)
    summary = json.loads((path/'summary.json').read_text())
    for filename in ('tracks.npz', 'hits.npz'):
        if sha(path/filename) != summary['artifacts'][filename]['sha256']:
            raise ValueError('Retained native-analysis artifact changed: '+filename)
    with np.load(path/'tracks.npz', allow_pickle=False) as data:
        tracks = dict(data)
    with np.load(path/'hits.npz', allow_pickle=False) as data:
        hits = dict(data)
    validate_primaries(tracks, summary['configuration'])
    n, nh = len(tracks['track_id']), len(hits['track_id'])
    if any(tracks[name].shape != (n,) or np.any(tracks[name] < 0) for name in METRICS):
        raise ValueError('Invalid retained counter shapes/values')
    if any(hits[name].shape != (nh,) for name in ('is_large', 'active', 'is_endcap', 'station', 'x_m', 'y_m', 'z_m')):
        raise ValueError('Inconsistent retained boundary event columns')
    if nh and np.any((hits['track_id'] < 0) | (hits['track_id'] >= n)):
        raise ValueError('A boundary event refers to an absent primary')
    if not np.isfinite(np.column_stack([hits[axis+'_m'] for axis in ('x', 'y', 'z')])).all():
        raise ValueError('Nonfinite native boundary position')
    for prefix in ('', 'endcap_'):
        for name in ('unique_faces', 'paired_stations'):
            if np.any(tracks[prefix+'active_'+name] > tracks[prefix+'outer_'+name]):
                raise ValueError('Active border counts exceed the outer counts')
        if np.any(tracks[prefix+'outer_paired_stations'] > 3):
            raise ValueError('More than three logical stations')
    return tracks, hits, summary


def _save(fig, path):
    fig.savefig(path, dpi=180, facecolor='white', metadata={
        'Description': 'DES040 DRAFT isolated ACTS vacuum paired wheel PROTOTYPE'})


def hit_positions(tracks, hits, c, path):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    momenta = c['plot_momentum_GeV']
    fig, axes = plt.subplots(3, 2, figsize=(13.5, 13))
    fig.subplots_adjust(left=.075, right=.975, top=.86, bottom=.15, hspace=.31, wspace=.2)
    ids = hits['track_id']; x, y, z = (hits[axis+'_m'] for axis in ('x', 'y', 'z'))
    r = np.hypot(x, y)
    extent = max(1., float(np.max(abs(np.r_[x, y]), initial=0)))*1.04
    z_extent = max(1., float(np.max(abs(z), initial=0)))*1.04
    r_extent = max(1., float(np.max(r, initial=0)))*1.04
    for row, momentum in enumerate(momenta):
        take = np.isclose(tracks['momentum_GeV'][ids], momentum, rtol=1e-9, atol=1e-10)
        for ax, horizontal, vertical in ((axes[row, 0], x, y), (axes[row, 1], z, r)):
            side = take & ~hits['is_large']
            ax.scatter(horizontal[side], vertical[side], marker='x', color='#777777', s=2.8, linewidths=.3, alpha=.4, rasterized=True)
            for charge, marker in ((-1, 'o'), (1, '^')):
                pick = take & hits['is_large'] & (tracks['charge'][ids] == charge)
                ax.scatter(horizontal[pick], vertical[pick], marker=marker, color=BLUE, s=1.8, linewidths=0, alpha=.35, rasterized=True)
            ax.grid(alpha=.18); ax.set_axisbelow(True)
        axes[row, 0].set(xlim=(-extent, extent), ylim=(-extent, extent), xlabel='x [m]', ylabel='y [m]',
                         title=f'Local p = {_momentum_label(momentum)}; both charges — XY')
        axes[row, 0].set_aspect('equal', adjustable='box')
        axes[row, 1].set(xlim=(-z_extent, z_extent), ylim=(0, r_extent), xlabel='Signed z [m]', ylabel='r [m]',
                         title=f'Local p = {_momentum_label(momentum)}; both charges — RZ')
        axes[row, 1].text(.02, .97, f'{take.sum():,} actual returned boundary events', transform=axes[row, 1].transAxes,
                          ha='left', va='top', fontsize=9, bbox=dict(facecolor='white', alpha=.9, edgecolor='none'))
    fig.legend(handles=[Line2D([], [], marker='o', ls='', color=BLUE, label='Large faces, q=−e'),
                        Line2D([], [], marker='^', ls='', color=BLUE, label='Large faces, q=+e'),
                        Line2D([], [], marker='x', ls='', color='#777777', label='Side faces')],
               loc='lower center', bbox_to_anchor=(.5, .065), ncol=3, frameon=False)
    fig.suptitle(f"{c['system'].capitalize()}: native ACTS boundary positions\nDRAFT / isolated vacuum PROTOTYPE", y=.97, fontsize=17)
    fig.text(.5, .9, _scope(c), ha='center', fontsize=10)
    fig.text(.5, .014, 'All returned events are shown, including incomplete tracks, eta display, sphere and both cap precision banks.\n'
             'Point density reflects the separate sampling banks and is not coverage or efficiency. No material, scattering or response.', ha='center', fontsize=9)
    _save(fig, path); plt.close(fig)


def entrance_map(tracks, c, path, metric, title, top):
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.colors import ListedColormap, BoundaryNorm
    from matplotlib.lines import Line2D
    fig, axes = plt.subplots(2, 3, figsize=(16.8, 8.8), sharex=True, sharey=True)
    fig.subplots_adjust(left=.06, right=.9, top=.79, bottom=.19, hspace=.24, wspace=.13)
    cmap = ListedColormap(plt.get_cmap('viridis')(np.linspace(.07, .98, top+1)))
    norm = BoundaryNorm(np.arange(-.5, top+1.5), cmap.N)
    xe, ye = tracks['phi_edges_deg'], tracks['eta_edges']
    for row, charge in enumerate((-1, 1)):
        for col, momentum in enumerate(c['plot_momentum_GeV']):
            ax = axes[row, col]
            values, incomplete = _grid(tracks, _case(tracks, momentum, charge, 0), metric)
            mesh = ax.pcolormesh(xe, ye, np.minimum(values, top), shading='flat', cmap=cmap, norm=norm, rasterized=True)
            iy, ix = np.nonzero(incomplete)
            if len(ix):
                segments = np.stack((np.column_stack((xe[ix], ye[iy])), np.column_stack((xe[ix+1], ye[iy+1]))), axis=1)
                ax.add_collection(LineCollection(segments, colors='#161616', linewidths=.55, alpha=.9))
            ax.set_title(f'{_charge_label(charge)}; local p = {_momentum_label(momentum)}', fontsize=11)
            ax.set(xlim=(0, 360), ylim=(ye[0], ye[-1]), xticks=np.arange(0, 361, 60))
            for eta in (-c['endcap_abs_eta_min'], c['endcap_abs_eta_min']):
                ax.axhline(eta, color='white', ls=':', lw=.7, alpha=.8)
            ax.text(.02, .97, f'Incomplete: {incomplete.sum():,}/{values.size:,}', transform=ax.transAxes,
                    va='top', fontsize=8, bbox=dict(facecolor='white', alpha=.9, edgecolor='none'))
            if row == 1:
                ax.set_xlabel('Initial azimuth φ [degrees]')
            if col == 0:
                ax.set_ylabel('Initial direction η')
    cax = fig.add_axes([.925, .23, .014, .48]); cb = fig.colorbar(mesh, cax=cax, ticks=np.arange(top+1))
    cb.set_label('Observed lower-bound count' if top > 1 else 'Observed paired traversal (0/1)')
    if top == 6:
        cb.ax.set_yticklabels([str(i) for i in range(6)]+['≥6'])
    fig.suptitle(f"{c['system'].capitalize()}: {title}\nDRAFT / isolated ACTS vacuum PROTOTYPE", y=.97, fontsize=17)
    fig.text(.5, .867, _scope(c), ha='center', fontsize=10)
    fig.text(.5, .83, 'White dotted lines: fixed endcap angular boundary; all eta display cells remain shown.', ha='center', fontsize=10)
    fig.legend(handles=[Line2D([], [], marker='$/$', color='#161616', ls='', markersize=10,
                        label='Incomplete/native-navigation-uncertain: count is a lower bound')],
               loc='lower center', bbox_to_anchor=(.5, .085), frameon=False)
    fig.text(.5, .02, 'One jittered direction per cell; not a converged efficiency map. Black slashes also mark already-proven passes.\n'
             'Unique faces exclude sides and tangent touches; pairs require both large faces in one contiguous chamber visit.', ha='center', fontsize=10)
    _save(fig, path); plt.close(fig)


def momentum_coverage(summary, path):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    c = summary['configuration']
    metrics = [('outer_unique_faces', '#206ba7', 'Six large faces: outer'),
               ('active_unique_faces', '#b36c1c', 'Six large faces: 30 mm border'),
               ('outer_paired_stations', '#21855f', 'Three paired stations: outer'),
               ('active_paired_stations', '#915699', 'Three paired stations: 30 mm border')]
    fig, axes = plt.subplots(2, 2, figsize=(13.8, 10), sharex=True, sharey=True)
    fig.subplots_adjust(left=.085, right=.98, top=.82, bottom=.22, hspace=.27, wspace=.13)
    for row, (region, prefix, title) in enumerate((('full_sphere', '', 'Full 4pi: all chamber families'),
                ('endcap_caps', 'endcap_', 'Fixed endcap region: endcap-only'))):
        for col, charge in enumerate((-1, 1)):
            ax = axes[row, col]; cases = [case for case in summary['cases'] if case['charge'] == charge]
            momenta = np.asarray([case['momentum_GeV'] for case in cases])
            for metric, color, _ in metrics:
                lo = [100*case['samples'][region][prefix+metric]['proven_lower_fraction'] for case in cases]
                hi = [100*case['samples'][region][prefix+metric]['possible_upper_fraction'] for case in cases]
                ax.fill_between(momenta, lo, hi, color=color, alpha=.12)
                ax.plot(momenta, lo, color=color, marker='o', ms=3); ax.plot(momenta, hi, color=color, ls='--', lw=1)
            count = cases[0]['samples'][region]['tracks']
            ax.set(xscale='log', ylim=(0, 100), title=f'{title}; q={charge:+d}e; N={count:,}')
            ax.set_xticks(momenta, [f'{p:g}' for p in momenta]); ax.minorticks_off(); ax.grid(alpha=.2)
            if row == 1:
                ax.set_xlabel('Local entrance momentum [GeV]')
            if col == 0:
                ax.set_ylabel('Boundary availability [%]')
    handles = [Line2D([], [], color=color, lw=2, label=label) for _, color, label in metrics]
    handles += [Line2D([], [], color='#333333', marker='o', lw=1.5, label='Solid: proven lower bound'),
                Line2D([], [], color='#333333', ls='--', label='Dashed: possible upper bound'),
                Patch(facecolor='#888888', alpha=.2, label='Unresolved-event range; not a confidence interval')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .065), ncol=2, frameon=False)
    fig.suptitle(f"{c['system'].capitalize()}: native chamber-boundary availability\nDRAFT / isolated ACTS vacuum PROTOTYPE", y=.97, fontsize=16)
    fig.text(.5, .867, _scope(c), ha='center', fontsize=10)
    fig.text(.5, .015, 'All generated events remain in the denominators. Sphere and cap precision banks are separate; cap hemispheres are stratified.\n'
             'Sampling errors and both endcap sides are retained in CSV/JSON. No material transport, response or reconstruction efficiency.', ha='center', fontsize=9)
    _save(fig, path); plt.close(fig)


def wheel_coverage(summary, path):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    c = summary['configuration']
    fig, axes = plt.subplots(2, 2, figsize=(13.8, 9.4), sharex=True, sharey=True)
    fig.subplots_adjust(left=.08, right=.98, top=.81, bottom=.18, hspace=.28, wspace=.13)
    colors = {1: '#206ba7', 2: '#21855f', 3: '#915699'}
    for row, (region, label) in enumerate((('endcap_cap_positive', 'Positive endcap'), ('endcap_cap_negative', 'Negative endcap'))):
        for col, charge in enumerate((-1, 1)):
            ax = axes[row, col]; cases = [case for case in summary['cases'] if case['charge'] == charge]
            momenta = np.asarray([case['momentum_GeV'] for case in cases])
            for station in (1, 2, 3):
                for border, style in (('outer', '-'), ('active', ':')):
                    metric = f'endcap_station_{station}_{border}_paired'
                    lo = np.asarray([case['samples'][region][metric]['proven_lower_fraction'] for case in cases])*100
                    hi = np.asarray([case['samples'][region][metric]['possible_upper_fraction'] for case in cases])*100
                    ax.fill_between(momenta, lo, hi, color=colors[station], alpha=.07)
                    ax.plot(momenta, lo, color=colors[station], ls=style, marker='o', ms=2.5)
                    ax.plot(momenta, hi, color=colors[station], ls='--', lw=.8)
            ax.set(xscale='log', ylim=(0, 100), title=f'{label}; q={charge:+d}e')
            ax.set_xticks(momenta, [f'{p:g}' for p in momenta]); ax.minorticks_off(); ax.grid(alpha=.2)
            if row == 1:
                ax.set_xlabel('Local entrance momentum [GeV]')
            if col == 0:
                ax.set_ylabel('Single-wheel paired availability [%]')
    handles = [Line2D([], [], color=color, lw=2, label=f'Wheel {station}') for station, color in colors.items()]
    handles += [Line2D([], [], color='#333333', lw=1.5, label='Solid: outer lower'),
                Line2D([], [], color='#333333', ls=':', label='Dotted: 30 mm border lower'),
                Line2D([], [], color='#333333', ls='--', label='Dashed: possible upper')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .055), ncol=3, frameon=False)
    fig.suptitle(f"{c['system'].capitalize()}: per-wheel paired traversal availability\nDRAFT / isolated ACTS vacuum PROTOTYPE", y=.97, fontsize=16)
    fig.text(.5, .86, 'Independent precision cap banks; fixed initial-direction angular region; all generated events retained.', ha='center', fontsize=10)
    fig.text(.5, .014, 'A wheel passes only after both large faces of the same endcap chamber in one contiguous visit.\n'
             'Aligned gap losses are correlated; do not multiply single-wheel fractions. Bands are unresolved-event bounds, not confidence intervals.', ha='center', fontsize=9)
    _save(fig, path); plt.close(fig)


def draw(analysis_dir, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tracks, hits, summary = load(analysis_dir); c = summary['configuration']
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    paths = [output/name for name in OUTPUT_NAMES]
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False}):
        hit_positions(tracks, hits, c, paths[0])
        entrance_map(tracks, c, paths[1], 'outer_unique_faces', 'six unique large faces (all families)', 6)
        entrance_map(tracks, c, paths[2], 'active_paired_stations', 'three paired stations, 30 mm border (all families)', 3)
        entrance_map(tracks, c, paths[3], 'endcap_active_paired_stations', 'three paired endcap stations, 30 mm border', 3)
        for station in (1, 2, 3):
            entrance_map(tracks, c, paths[3+station], f'endcap_station_{station}_active_paired',
                         f'endcap wheel {station} paired traversal, 30 mm border', 1)
        momentum_coverage(summary, paths[7]); wheel_coverage(summary, paths[8])
    save(output/'figures.json', dict(scope='Static figures from retained native ACTS arrays; no synthetic roots or reconstruction efficiency.',
        analysis_summary_sha256=sha(Path(analysis_dir)/'summary.json'), postprocessing=source_state(),
        artifacts={path.name: dict(sha256=sha(path), bytes=path.stat().st_size) for path in paths}))
    return paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('analysis_dir', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    for artifact in draw(args.analysis_dir, args.output):
        print(artifact)
