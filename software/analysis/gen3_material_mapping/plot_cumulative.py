#!/usr/bin/env python3
"""Replay cumulative Geant4/ACTS material comparisons with unrooted."""
import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path

import numpy as np


def audit(data, root, config_path=None):
    from cumulative_profiles import validate_config
    if data['schema_version'] != 1:
        raise ValueError('Unsupported cumulative profile schema')
    config = data['configuration']
    edges, grids = validate_config(config)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    source = Path(__file__).with_name('cumulative_profiles.py')
    if data['provenance']['exporter_sha256'] != digest(source):
        raise ValueError('Cumulative exporter changed since recorded reduction')
    config_path = config_path or source.with_name('cumulative_config.json')
    if (data['provenance']['configuration_sha256'] != digest(config_path)
            or config != json.loads(config_path.read_text())):
        raise ValueError('Cumulative configuration differs from retained input')
    base = root / 'docs/validation/gen3-material-map-run'
    for sample, report_name, role in [('geant4', 'mapping-report.json', 'recording'),
                                      ('validation', 'validation-report.json', 'validation_tracks')]:
        report = json.loads((base / report_name).read_text())
        expected = next(f['sha256'] for f in report['provenance']['files'] if f['role'] == role)
        if data['provenance'][sample + '_sha256'] != expected:
            raise ValueError('Cumulative sample differs from authoritative native campaign')
        dataset = data['samples'][sample]
        native = report['track_budgets']['input'] if sample == 'geant4' else report['track_budgets']
        if dataset['tracks'] != native['tracks'] or dataset['steps'] != native['steps']:
            raise ValueError('Cumulative sample count differs from native campaign')
        if len(dataset['eta_slice_counts']) != len(edges) - 1 or sum(dataset['eta_slice_counts']) != dataset['tracks']:
            raise ValueError('Eta slice counts do not partition rays')
        for q in ('X0', 'L0'):
            np.testing.assert_allclose(dataset['global_mean'][q], native['sum_' + q] / native['tracks'], rtol=5.e-6, atol=1.e-7)
        for axis, grid in grids.items():
            actual = dataset['axes'][axis]
            np.testing.assert_array_equal(actual['grid_mm'], grid)
            if [s['eta_index'] for s in actual['slices']] != config['axes'][axis]['eta_slices']:
                raise ValueError('Missing/repeated eta slice')
            for item in actual['slices']:
                if item['tracks'] <= 0 or item['tracks'] != dataset['eta_slice_counts'][item['eta_index']]:
                    raise ValueError('Cumulative profile has wrong ray normalization')
                for profile in item['quantities'].values():
                    mean, variance = (np.asarray(profile[key]) for key in ('mean', 'variance'))
                    if (len(mean) != len(grid) or mean.shape != variance.shape
                            or not np.all(np.isfinite(mean)) or not np.all(np.isfinite(variance))
                            or np.any(variance < 0) or np.any(mean < -1.e-8)
                            or np.any(np.diff(mean) < -1.e-8)):
                        raise ValueError('Invalid/nonmonotonic cumulative profile')
        distance = dataset['axes']['d']['slices']
        for axis in ('r', 'abs_z'):
            for item in dataset['axes'][axis]['slices']:
                matching = next(s for s in distance if s['eta_index'] == item['eta_index'])
                for q in ('X0', 'L0'):
                    for statistic in ('mean', 'variance'):
                        np.testing.assert_allclose(item['quantities'][q][statistic][-1],
                                                   matching['quantities'][q][statistic][-1], rtol=1.e-8, atol=1.e-9)
        if [s['eta_index'] for s in distance] == list(range(len(edges) - 1)):
            for q in ('X0', 'L0'):
                endpoint = sum(s['tracks'] * s['quantities'][q]['mean'][-1] for s in distance) / dataset['tracks']
                np.testing.assert_allclose(endpoint, dataset['global_mean'][q], rtol=1.e-8, atol=1.e-9)
    print('Cumulative source/count/endpoint/monotonicity audit PASS')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--config', type=Path, default=Path(__file__).with_name('cumulative_config.json'),
                    help='The exact configuration used for this reduction, including a custom --config input')
    args = ap.parse_args()
    raw = args.data.read_bytes()
    data = json.loads(gzip.decompress(raw) if args.data.suffix == '.gz' else raw)
    root = Path(__file__).resolve().parents[3]
    audit(data, root, args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    cache = root / 'build/gen3-cumulative-material/plot-cache'
    os.environ['MPLBACKEND'] = 'Agg'
    os.environ.setdefault('MPLCONFIGDIR', str(cache / 'matplotlib'))
    os.environ.setdefault('XDG_CACHE_HOME', str(cache / 'xdg'))
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from unrooted.core import Axis, Histogram
    from unrooted.plot import HistogramStyle
    from unrooted.plot.mpl import plot
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'svg.hashsalt': 'nodd-cumulative-material'})
    colors = {'geant4': '#202c37', 'validation': '#b2182b'}
    styles = {name: HistogramStyle.as_line(line_style=None, line_color=color, line_width=1.5,
              error_display='band', error_color=color, error_alpha=.15) for name, color in colors.items()}
    names = {'geant4': 'Geant4 physical steps', 'validation': 'ACTS thin portals'}
    labels = {'r': 'Radius r [mm]', 'abs_z': r'Absolute z $|z|$ [mm]',
              'd': r'Distance from origin $d=\sqrt{r^2+z^2}$ [mm]'}
    quantities = {'X0': r'Mean accumulated $t/X_0$', 'L0': r'Mean accumulated $t/\lambda_{\mathrm{I}}$'}
    config = data['configuration']
    summary = []
    for axis in config['axes']:
        reference = data['samples']['geant4']['axes'][axis]
        grid = np.array(reference['grid_mm'])
        for q in ('X0', 'L0'):
            for a, b in zip(reference['slices'], data['samples']['validation']['axes'][axis]['slices']):
                truth, validation = (np.array(item['quantities'][q]['mean']) for item in (a, b))
                delta = validation - truth
                k = int(np.argmax(abs(delta)))
                lo, hi = config['abs_eta_edges'][a['eta_index']:a['eta_index'] + 2]
                summary.append([axis, lo, hi, q, a['tracks'], b['tracks'], truth[-1], validation[-1],
                                validation[-1] / truth[-1] - 1, abs(delta[k]), grid[k], abs(delta[k]) / truth[-1]])
        figure_quantities = [('X0', 'L0')] if axis == 'r' else [('X0',), ('L0',)]
        for qs in figure_quantities:
            panels = [(s, q) for q in qs for s in config['axes'][axis]['eta_slices']]
            columns = 2 if axis == 'r' else 3
            rows = (len(panels) + columns - 1) // columns
            fig, axes = plt.subplots(rows, columns, figsize=(14, 5.2 if rows == 1 else 3.1 * rows + 1.4), squeeze=False)
            fig.subplots_adjust(left=.065, right=.985, bottom=.12 if rows == 1 else .08,
                                top=.72 if rows == 1 else .82, wspace=.27, hspace=.47)
            title = 'Barrel radius' if axis == 'r' else 'Forward |z|' if axis == 'abs_z' else 'Distance from origin'
            fig.suptitle('nODD Gen3 — cumulative material: ' + title, x=.065, y=.98, ha='left', weight='bold', fontsize=17)
            fig.text(.065, .91 if rows == 1 else .94,
                     'PROTOTYPE · 100,000 rays per sample · one phi bin · per-ray means ± statistical SEM', color='#52606b')
            for ax, (s, q) in zip(axes.flat, panels):
                lo, hi = config['abs_eta_edges'][s:s + 2]
                counts = []
                for sample in ('geant4', 'validation'):
                    item = next(item for item in data['samples'][sample]['axes'][axis]['slices'] if item['eta_index'] == s)
                    profile = item['quantities'][q]
                    # Each checkpoint value is held to the next checkpoint, so
                    # a portal jump is never moved before its first sampled q.
                    h = Histogram(axes=[Axis(grid.copy())], values=np.array(profile['mean'][:-1]),
                                  variances=np.array(profile['variance'][:-1]), name=names[sample])
                    plot(h, ax=ax, style=styles[sample])
                    # The pinned styled unrooted line closes to zero. A CDF
                    # must remain at its endpoint: keep its unrooted band and
                    # draw an open-ended stair line through the same values.
                    ax.stairs(h.values, h.axes[0].edges, baseline=None,
                              color=colors[sample], linewidth=1.5)
                    counts.append(item['tracks'])
                relation = r'\leq' if s == len(config['abs_eta_edges']) - 2 else '<'
                ax.set_title(fr'${lo:g}\leq|\eta|{relation}{hi:g}$' + f'   G4/ACTS rays: {counts[0]:,}/{counts[1]:,}', fontsize=9)
                ax.set(xlabel=labels[axis], ylabel=quantities[q], xlim=(grid[0], grid[-1]), ylim=(0, None))
                ax.grid(alpha=.2)
                ax.set_axisbelow(True)
            for ax in list(axes.flat)[len(panels):]:
                ax.set_visible(False)
            fig.legend(handles=[Line2D([], [], color=colors[s], lw=1.5, label=names[s] + ' ± SEM') for s in colors],
                       loc='upper right', bbox_to_anchor=(.985, .86 if rows == 1 else .905), frameon=False, ncol=2)
            fig.text(.065, .015, f"Both z signs/full phi; every ray including zeros. {config['axes'][axis]['step_mm']:g} mm checkpoints, held between samples. Bands omit map-training uncertainty.",
                     color='#52606b', fontsize=8)
            filename = 'cumulative_' + axis + ('' if axis == 'r' else '_' + qs[0])
            for extension in ('png', 'pdf', 'svgz'):
                path = args.output / (filename + '.' + extension)
                fig.savefig(path, dpi=170, bbox_inches='tight')
                if extension == 'svgz':
                    svg = gzip.decompress(path.read_bytes()).decode()
                    path.write_bytes(gzip.compress(('\n'.join(line.rstrip() for line in svg.splitlines()) + '\n').encode(), mtime=0))
            plt.close(fig)
    with (args.output / 'comparison-summary.csv').open('w', newline='') as stream:
        writer = csv.writer(stream, lineterminator='\n')
        writer.writerow(['axis', 'abs_eta_low', 'abs_eta_high', 'quantity', 'geant4_rays', 'validation_rays',
                         'geant4_final', 'validation_final', 'final_relative_difference',
                         'maximum_absolute_cumulative_difference', 'maximum_at_mm', 'maximum_over_geant4_final'])
        writer.writerows(summary)
    print('Rendered five cumulative comparisons as PNG/PDF/SVGZ with summary CSV')


if __name__ == '__main__':
    main()
