"""Review plots of retained ACTS boundary events for DES040 (PROTOTYPE).

``draw(workdir, outputdir)`` reads tracks.npz, hits.npz and summary.json.
It never generates trajectories, intersections, counters or detector geometry.
An unfinished track remains in every denominator. Its returned counts are lower
bounds; reaching a requested threshold already proves that threshold.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


STATION_COLORS = {1: '#007f82', 2: '#4169b1', 3: '#8c50a0'}
TRACK_FIELDS = (
    'track_id', 'momentum_GeV', 'charge', 'sample', 'eta_bin', 'phi_bin',
    'eta_pos', 'phi_pos_deg', 'outer_unique_faces', 'active_unique_faces',
    'outer_paired_stations', 'active_paired_stations', 'incomplete',
)
HIT_FIELDS = (
    'track_id', 'panel_index', 'station', 'face_index', 'is_large', 'active',
    'x_m', 'y_m', 'z_m', 'path_m',
)
OUTPUT_NAMES = (
    'hit-positions.png', 'entrance-segments.png',
    'entrance-paired-stations.png', 'momentum-coverage.png',
)


def availability_bounds(values, incomplete, threshold):
    """Return proven/possible fractions without dropping unfinished tracks.

    These are unresolved-outcome bounds, not confidence intervals. A track
    already above threshold cannot become a failure when propagation continues.
    """
    values, incomplete = np.asarray(values), np.asarray(incomplete, dtype=bool)
    if values.ndim != 1 or values.shape != incomplete.shape or not len(values):
        raise ValueError('Availability requires equally sized nonempty vectors')
    passed = values >= threshold
    return float(passed.mean()), float((passed | incomplete).mean())


def _load(workdir):
    workdir = Path(workdir)
    with np.load(workdir / 'tracks.npz', allow_pickle=False) as data:
        tracks = {name: data[name] for name in TRACK_FIELDS}
        tracks.update({name: data[name] for name in ('eta_edges', 'phi_edges_deg')})
    with np.load(workdir / 'hits.npz', allow_pickle=False) as data:
        hits = {name: data[name] for name in HIT_FIELDS}
    summary = json.loads((workdir / 'summary.json').read_text())
    n = len(tracks['track_id'])
    if not n or any(tracks[name].shape != (n,) for name in TRACK_FIELDS):
        raise ValueError('Every track field must be a nonempty row vector')
    if not np.array_equal(tracks['track_id'], np.arange(n)):
        raise ValueError('track_id must identify its tracks.npz row')
    nh = len(hits['track_id'])
    if any(hits[name].shape != (nh,) for name in HIT_FIELDS):
        raise ValueError('Every hit field must have the same one-dimensional shape')
    ids = hits['track_id']
    if not np.issubdtype(ids.dtype, np.integer) or np.any((ids < 0) | (ids >= n)):
        raise ValueError('A hit refers to a missing track')
    for name in ('momentum_GeV', 'eta_pos', 'phi_pos_deg'):
        if not np.isfinite(tracks[name]).all():
            raise ValueError(f'Nonfinite track {name}')
    for name in ('x_m', 'y_m', 'z_m', 'path_m'):
        if not np.isfinite(hits[name]).all():
            raise ValueError(f'Nonfinite ACTS hit {name}')
    if np.any(tracks['momentum_GeV'] <= 0):
        raise ValueError('Momentum must be positive')
    if not np.isin(tracks['charge'], [-1, 1]).all():
        raise ValueError('Expected charge -1 or +1')
    if not np.isin(tracks['sample'], [0, 1]).all():
        raise ValueError('Expected map sample=0 or independent sphere sample=1')
    for data, names in ((tracks, ('incomplete',)), (hits, ('is_large', 'active'))):
        for name in names:
            if not np.isin(data[name], [0, 1]).all():
                raise ValueError(f'{name} must be boolean')
            data[name] = data[name].astype(bool)
    for name in ('outer_unique_faces', 'active_unique_faces',
                 'outer_paired_stations', 'active_paired_stations'):
        values = tracks[name]
        if not np.issubdtype(values.dtype, np.integer) or np.any(values < 0):
            raise ValueError(f'{name} must be nonnegative integer counts')
        if name.endswith('paired_stations') and np.any(values > 3):
            raise ValueError(f'{name} exceeds the three logical stations')
    for suffix in ('unique_faces', 'paired_stations'):
        if np.any(tracks['active_' + suffix] > tracks['outer_' + suffix]):
            raise ValueError('Border-inset counts exceed outer counts')
    if not np.isin(hits['station'], [1, 2, 3]).all():
        raise ValueError('Unexpected ACTS hit station ID')
    for name in ('eta_edges', 'phi_edges_deg'):
        if (tracks[name].ndim != 1 or len(tracks[name]) < 2 or
                not np.isfinite(tracks[name]).all() or
                np.any(np.diff(tracks[name]) <= 0)):
            raise ValueError(f'Invalid map edges: {name}')
    phi_edges = tracks['phi_edges_deg']
    if not np.allclose([phi_edges[0], phi_edges[-1]], [0, 360]):
        raise ValueError('The entrance maps must cover the complete azimuth')
    configuration = summary['configuration']
    plot_momenta = np.asarray(configuration['plot_momentum_GeV'], dtype=float)
    if plot_momenta.shape != (3,) or np.any(plot_momenta <= 0):
        raise ValueError('Exactly three positive plot momenta are required')
    configured_momenta = np.asarray(configuration['momentum_GeV'], dtype=float)
    for sample in (0, 1):
        actual = np.unique(tracks['momentum_GeV'][tracks['sample'] == sample])
        if (actual.shape != configured_momenta.shape or
                not np.allclose(actual, np.sort(configured_momenta), rtol=1e-9, atol=1e-10)):
            raise ValueError('A configured momentum case is missing or unexpected')
        for momentum in configured_momenta:
            for charge in (-1, 1):
                rows = _case(tracks, momentum, charge, sample)
                if sample == 0:
                    _grid(tracks, rows, 'outer_unique_faces')
                elif rows.sum() != configuration['full_sphere_directions']:
                    raise ValueError('Full-sphere denominator differs from the generated case size')
    return tracks, hits, configuration, plot_momenta


def _case(tracks, momentum, charge, sample):
    return ((tracks['sample'] == sample) & (tracks['charge'] == charge) &
            np.isclose(tracks['momentum_GeV'], momentum, rtol=1e-9, atol=1e-10))


def _grid(tracks, rows, field):
    """Put exactly one retained map track in each cell; never fill failures."""
    ny, nx = len(tracks['eta_edges']) - 1, len(tracks['phi_edges_deg']) - 1
    iy, ix = tracks['eta_bin'][rows], tracks['phi_bin'][rows]
    if (not np.issubdtype(iy.dtype, np.integer) or
            not np.issubdtype(ix.dtype, np.integer) or
            np.any((iy < 0) | (iy >= ny) | (ix < 0) | (ix >= nx))):
        raise ValueError('Invalid map cell index')
    cells = iy * nx + ix
    if len(cells) != ny * nx or len(np.unique(cells)) != ny * nx:
        raise ValueError('Each momentum/charge map must retain one track per cell')
    values = np.empty((ny, nx), dtype=tracks[field].dtype)
    values[iy, ix] = tracks[field][rows]
    incomplete = np.empty((ny, nx), dtype=bool)
    incomplete[iy, ix] = tracks['incomplete'][rows]
    return values, incomplete


def _momentum_label(momentum):
    return '1 TeV' if np.isclose(momentum, 1000) else f'{momentum:g} GeV'


def _charge_label(charge):
    return r'$\mu^-$, $q=-e$' if charge < 0 else r'$\mu^+$, $q=+e$'


def _scope(configuration):
    entrance = configuration.get('entrance', {})
    r, z = entrance.get('radius_m', 4.35), entrance.get('half_z_m', 6.5)
    return (f'Local total momentum at closed entrance cylinder (R={r:g} m, half-z={z:g} m); '
            'radial launch; joint vacuum field')


def _save(fig, path):
    fig.savefig(path, dpi=180, facecolor='white',
                metadata={'Description': 'DES040 DRAFT isolated ACTS vacuum PROTOTYPE'})


def _hit_positions(tracks, hits, configuration, momenta, path):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig, axes = plt.subplots(3, 2, figsize=(13.8, 13.2))
    fig.subplots_adjust(left=.075, right=.97, bottom=.145, top=.88,
                        hspace=.35, wspace=.20)
    track_ids = hits['track_id']
    hit_p, hit_q = tracks['momentum_GeV'][track_ids], tracks['charge'][track_ids]
    x, y, z = hits['x_m'], hits['y_m'], hits['z_m']
    radius = np.hypot(x, y)
    xy_limit = max(1., float(np.max(np.abs(np.r_[x, y]), initial=0))) * 1.05
    z_limit = max(1., float(np.max(np.abs(z), initial=0))) * 1.05
    r_limit = max(1., float(np.max(radius, initial=0))) * 1.05
    for row, momentum in enumerate(momenta):
        keep = np.isclose(hit_p, momentum, rtol=1e-9, atol=1e-10)
        side = keep & ~hits['is_large']
        for ax, horizontal, vertical in ((axes[row, 0], x, y),
                                         (axes[row, 1], z, radius)):
            ax.scatter(horizontal[side], vertical[side], marker='x', s=3.5,
                       linewidths=.35, color='#7c7c7c', alpha=.5, rasterized=True)
            for charge, marker in ((-1, 'o'), (1, '^')):
                for station, color in STATION_COLORS.items():
                    pick = keep & hits['is_large'] & (hit_q == charge) & (hits['station'] == station)
                    ax.scatter(horizontal[pick], vertical[pick], marker=marker,
                               s=1.7, linewidths=0, color=color, alpha=.45,
                               rasterized=True)
            ax.grid(alpha=.17)
            ax.set_axisbelow(True)
        ax_xy, ax_zr = axes[row]
        ax_xy.set(xlim=(-xy_limit, xy_limit), ylim=(-xy_limit, xy_limit),
                  xlabel='x [m]', ylabel='y [m]')
        ax_xy.set_aspect('equal', adjustable='box')
        ax_zr.set(xlim=(-z_limit, z_limit), ylim=(0, r_limit),
                  xlabel='Signed z [m]', ylabel='r [m]')
        label = f'Local p = {_momentum_label(momentum)}; both charges'
        ax_xy.set_title(label + ' — XY', fontsize=11, pad=9)
        ax_zr.set_title(label + ' — z–r', fontsize=11, pad=9)
        ax_zr.text(.02, .97, f'{np.count_nonzero(keep):,} returned boundary events',
                   transform=ax_zr.transAxes, ha='left', va='top', fontsize=9,
                   bbox={'facecolor': 'white', 'alpha': .9, 'edgecolor': 'none'})
        if not keep.any():
            for ax in axes[row]:
                ax.text(.5, .5, 'No returned ACTS hits', transform=ax.transAxes,
                        ha='center', va='center')
    handles = [Line2D([], [], marker='o', ls='', color=color, label=f'Station {s}: large faces')
               for s, color in STATION_COLORS.items()]
    handles += [Line2D([], [], marker='x', ls='', color='#7c7c7c', label='Side faces'),
                Line2D([], [], marker='o', ls='', color='black', label=r'$\mu^-$ large-face hits'),
                Line2D([], [], marker='^', ls='', color='black', label=r'$\mu^+$ large-face hits')]
    fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, .045),
               ncol=3, frameon=False, fontsize=10)
    fig.suptitle('ACTS returned chamber-boundary positions\nDES040 DRAFT / isolated PROTOTYPE',
                 fontsize=17, y=.97)
    fig.text(.5, .905, _scope(configuration), ha='center', fontsize=10)
    fig.text(.5, .016, 'Actual returned hits only, including incomplete tracks. Both map and full-sphere samples are shown.\n'
             'Side faces are excluded from segment counts. Hit density is not efficiency; no material or detector response is modelled.',
             ha='center', va='bottom', fontsize=9)
    _save(fig, path)
    plt.close(fig)


def _entrance_map(tracks, configuration, momenta, path, paired=False):
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.colors import BoundaryNorm, ListedColormap
    from matplotlib.lines import Line2D

    field = 'active_paired_stations' if paired else 'outer_unique_faces'
    top = 3 if paired else 6
    cmap = ListedColormap(plt.get_cmap('viridis')(np.linspace(.07, .98, top + 1)))
    norm = BoundaryNorm(np.arange(-.5, top + 1.5), cmap.N)
    fig, axes = plt.subplots(2, 3, figsize=(17, 8.9), sharex=True, sharey=True)
    fig.subplots_adjust(left=.055, right=.90, bottom=.19, top=.79,
                        hspace=.24, wspace=.12)
    xe, ye = tracks['phi_edges_deg'], tracks['eta_edges']
    mesh = None
    for row, charge in enumerate((-1, 1)):
        for col, momentum in enumerate(momenta):
            ax = axes[row, col]
            values, incomplete = _grid(tracks, _case(tracks, momentum, charge, 0), field)
            mesh = ax.pcolormesh(xe, ye, np.minimum(values, top), cmap=cmap,
                                 norm=norm, shading='flat', rasterized=True)
            iy, ix = np.nonzero(incomplete)
            if len(ix):
                # One diagonal slash per unfinished cell, including proven passes.
                segments = np.stack((np.column_stack((xe[ix], ye[iy])),
                                     np.column_stack((xe[ix + 1], ye[iy + 1]))), axis=1)
                ax.add_collection(LineCollection(segments, colors='#151515',
                                                linewidths=.55, alpha=.9))
            ax.set_title(f'{_charge_label(charge)}; local p = {_momentum_label(momentum)}',
                         fontsize=11, pad=8)
            ax.set(xlim=(xe[0], xe[-1]), ylim=(ye[0], ye[-1]),
                   xticks=np.arange(0, 361, 60))
            ax.text(.025, .97, f'Incomplete: {incomplete.sum():,}/{values.size:,}',
                    transform=ax.transAxes, ha='left', va='top', fontsize=8.5,
                    bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .9})
            if row == 1:
                ax.set_xlabel('Entrance azimuth φ [degrees]')
            if col == 0:
                ax.set_ylabel('Entrance pseudorapidity η')
    cax = fig.add_axes([.925, .23, .014, .49])
    colorbar = fig.colorbar(mesh, cax=cax, ticks=np.arange(top + 1))
    colorbar.ax.set_yticklabels([str(i) for i in range(top + 1)] if paired else
                               [str(i) for i in range(top)] + ['≥6'])
    colorbar.set_label('Paired logical stations' if paired else 'Unique outer large faces',
                       labelpad=11)
    title = ('Three-station traversal proxy: both large faces of one chamber per station'
             if paired else 'Segment proxy: unique outer large-face crossings')
    subtitle = ('30 mm inactive-border proxy; side faces do not count'
                if paired else 'Literal >5 threshold means ≥6 unique (chamber, large-face) hits; side faces do not count')
    fig.suptitle(title + '\nDES040 DRAFT / isolated ACTS vacuum PROTOTYPE', fontsize=17, y=.975)
    fig.text(.5, .873, _scope(configuration), ha='center', fontsize=10)
    fig.text(.5, .838, subtitle, ha='center', fontsize=10)
    fig.legend(handles=[Line2D([], [], color='#151515', marker='$/$', ls='',
                              markersize=10, label='Incomplete event: shown multiplicity is a lower bound')],
               loc='lower center', bbox_to_anchor=(.5, .092), frameon=False, fontsize=10)
    fig.text(.5, .025, 'One jittered direction per cell; this is not a converged efficiency map. Black slashes also mark unfinished tracks that already pass.\n'
             'An unfinished track below threshold has an unresolved outcome, not a demonstrated failure. No scattering, energy loss or segment response.',
             ha='center', va='bottom', fontsize=10)
    _save(fig, path)
    plt.close(fig)


def _momentum_coverage(tracks, configuration, path):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    momenta = np.unique(tracks['momentum_GeV'][tracks['sample'] == 1])
    if not len(momenta):
        raise ValueError('No independent full-sphere sample')
    metrics = [
        ('outer_unique_faces', 6, '#2474a8', '≥6 unique large faces: outer'),
        ('active_unique_faces', 6, '#d78124', '≥6 unique large faces: 30 mm border'),
        ('outer_paired_stations', 3, '#26916d', '3 paired stations: outer'),
        ('active_paired_stations', 3, '#8b559f', '3 paired stations: 30 mm border'),
    ]
    fig = plt.figure(figsize=(14.2, 9.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[4, 1], left=.07, right=.97,
                         bottom=.24, top=.80, hspace=.10, wspace=.16)
    for col, charge in enumerate((-1, 1)):
        ax = fig.add_subplot(gs[0, col])
        failure_ax = fig.add_subplot(gs[1, col], sharex=ax)
        counts, unfinished = [], []
        for momentum in momenta:
            rows = _case(tracks, momentum, charge, 1)
            if not rows.any():
                raise ValueError('Missing full-sphere momentum/charge case')
            counts.append(int(rows.sum()))
            unfinished.append(float(tracks['incomplete'][rows].mean()) * 100)
        for name, threshold, color, _ in metrics:
            bounds = np.asarray([availability_bounds(tracks[name][rows], tracks['incomplete'][rows], threshold)
                                 for momentum in momenta
                                 for rows in [_case(tracks, momentum, charge, 1)]]) * 100
            ax.fill_between(momenta, bounds[:, 0], bounds[:, 1], color=color, alpha=.14)
            ax.plot(momenta, bounds[:, 0], color=color, marker='o', ms=4, lw=1.7)
            ax.plot(momenta, bounds[:, 1], color=color, ls='--', lw=1)
        denominator = (f'N={counts[0]:,} at every momentum' if len(set(counts)) == 1
                       else 'N=' + ', '.join(map(str, counts)) + ' in ascending momentum')
        ax.set_title(f'{_charge_label(charge)}; {denominator}', fontsize=11, pad=10)
        ax.set(xscale='log', ylim=(0, 100), yticks=np.arange(0, 101, 20))
        ax.grid(alpha=.22)
        ax.tick_params(axis='x', labelbottom=False)
        if col == 0:
            ax.set_ylabel('Full-sphere boundary availability [%]')
        failure_ax.plot(momenta, unfinished, color='#333333', marker='x', lw=1)
        failure_ax.fill_between(momenta, 0, unfinished, color='#333333', alpha=.07)
        failure_ax.set(ylim=(0, min(100., max(5., max(unfinished) * 1.15))),
                       xlabel='Local total momentum at entrance [GeV]')
        failure_ax.set_xticks(momenta, [f'{p:g}' for p in momenta])
        failure_ax.minorticks_off()
        failure_ax.grid(alpha=.22)
        if col == 0:
            failure_ax.set_ylabel('Incomplete\n[%]')
    handles = [Line2D([], [], color=color, lw=2, label=label) for _, _, color, label in metrics]
    handles += [Line2D([], [], color='#333333', marker='o', lw=1.5, label='Solid: proven-pass lower bound'),
                Line2D([], [], color='#333333', ls='--', label='Dashed: possible-pass upper bound'),
                Patch(facecolor='#888888', alpha=.2, label='Band: unresolved outcomes; not a statistical CI')]
    fig.legend(handles=handles, ncol=2, loc='lower center', bbox_to_anchor=(.5, .07),
               fontsize=10, frameon=False)
    fig.suptitle('ACTS chamber-boundary availability over 4π\nDES040 DRAFT / isolated PROTOTYPE',
                 fontsize=17, y=.97)
    fig.text(.5, .865, _scope(configuration), ha='center', fontsize=10)
    fig.text(.5, .83, 'Independent uniform-cos(θ), full-azimuth directions; every generated track remains in the denominator',
             ha='center', fontsize=10)
    fig.text(.5, .017, 'Lower = proven passes / all tracks. Upper adds only unfinished tracks that have not already passed.\n'
             'Paired stations require both large faces of the same chamber in one traversal. No fitted segments, material transport or reconstruction efficiency.',
             ha='center', va='bottom', fontsize=9.5)
    _save(fig, path)
    plt.close(fig)


def draw(workdir, outputdir):
    """Write four review PNGs from retained ACTS arrays; return their paths.

    Inputs are validated before any output is written. Additional NPZ/summary
    fields are ignored. Use a scratch output directory for synthetic fixtures.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    tracks, hits, configuration, momenta = _load(workdir)
    outputdir = Path(outputdir)
    outputdir.mkdir(parents=True, exist_ok=True)
    paths = [outputdir / name for name in OUTPUT_NAMES]
    with plt.rc_context({'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'font.family': 'DejaVu Sans'}):
        _hit_positions(tracks, hits, configuration, momenta, paths[0])
        _entrance_map(tracks, configuration, momenta, paths[1])
        _entrance_map(tracks, configuration, momenta, paths[2], paired=True)
        _momentum_coverage(tracks, configuration, paths[3])
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workdir', type=Path, help='Retained ACTS NPZ/summary directory')
    parser.add_argument('outputdir', type=Path, help='Directory for the four review PNGs')
    args = parser.parse_args()
    for path in draw(args.workdir, args.outputdir):
        print(path)


if __name__ == '__main__':
    main()
