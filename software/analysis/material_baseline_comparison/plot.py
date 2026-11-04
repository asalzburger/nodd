#!/usr/bin/env python3
"""Draw two baseline stacks and ACTS/Geant4 ratios using unrooted."""
import argparse
from importlib.metadata import distribution, version
import json
import os
from pathlib import Path

from compare import COLORS, COMPONENTS, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    os.environ['MPLBACKEND'] = 'Agg'
    os.environ['MPLCONFIGDIR'] = str(args.output.resolve()/'.mpl-cache')
    os.environ['XDG_CACHE_HOME'] = str(args.output.resolve()/'.cache')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    import numpy as np
    from unrooted.core import Axis, Histogram
    from unrooted.plot import HistogramStyle
    from unrooted.plot.mpl import stack, plot

    data = json.loads(args.data.read_text())
    if data['colors'] != COLORS or data['passive_alpha'] != .5 or data['sensitive_alpha'] != 1:
        raise ValueError('Palette/opacity differs from the requested component convention')
    edges = np.array(data['edges'])
    titles = {'old': 'Old baseline · 0.5 mm strixels',
              'current': 'New baseline · 2 mm strixels, reduced services'}
    labels = {'beam_pipe': 'Beam pipe', 'pixel': 'Pixels',
              'short_strip': 'Short strips', 'long_strip': 'Long strips'}
    active = [c for c in COMPONENTS if c != 'beam_pipe_sensitive']
    def hist(entry, name):
        return Histogram(axes=[Axis(edges.copy())], values=np.array(entry['mean']),
                         variances=np.array(entry['variance']), name=name)
    def style(component):
        detector, sensitivity = component.rsplit('_', 1)
        color = COLORS[detector]
        return HistogramStyle.as_stack(fill_color=color, line_color=color,
            fill_alpha=.5 if sensitivity == 'nonsensitive' else 1., line_width=.35)
    marker_style = HistogramStyle.as_markers(marker_color='black', line_color='black',
        error_color='black', marker_size=2.7, error_capsize=0, line_width=.65)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.axisbelow': True,
        'grid.color': '#e5e5e5', 'grid.linewidth': .6, 'savefig.facecolor': 'white'})
    files = []
    for name, baseline in data['baselines'].items():
        fig, axes = plt.subplots(2, 2, figsize=(15.8, 8.1), sharex='col',
            gridspec_kw={'height_ratios': [3.2, 1], 'hspace': .06, 'wspace': .25})
        fig.subplots_adjust(left=.075, right=.79, bottom=.14, top=.84)
        fig.suptitle('nODD tracker material', x=.075, y=.972, ha='left',
                     fontsize=22, fontweight='bold')
        fig.text(.075, .921, titles[name], fontsize=14)
        validation_label = 'validation rays' if name == 'old' else 'independent validation rays'
        fig.text(.075, .879, f"Geant4: {baseline['selected_geant4_rays']:,} rays  ·  "
            f"ACTS: {baseline['selected_acts_rays']:,} {validation_label}  ·  Δη = 0.1",
            fontsize=10.5, color='#505050')
        for col, q in enumerate(('X0', 'L0')):
            ax, ratio_ax = axes[:, col]
            truth = baseline['geant4']['quantities'][q]
            reco = baseline['acts']['quantities'][q]
            stack([hist(truth[c], c) for c in active], ax=ax,
                  styles=[style(c) for c in active], uncertainty=False)
            # The total has component covariance; never sum component variances.
            plot(hist(truth['total'], 'Geant4 total'), ax=ax,
                 style=HistogramStyle.as_line(line_color='#333333', line_width=.65))
            if name == 'current':
                old = data['baselines']['old']['geant4']['quantities'][q]
                plot(hist(old['total'], 'Old total'), ax=ax,
                     style=HistogramStyle.as_line(line_color='#222222',
                         line_style=':', line_width=1.9))
            plot(hist(reco, 'ACTS total'), ax=ax, style=marker_style)
            maximum = max(max(b['geant4']['quantities'][q]['total']['mean'])
                          for b in data['baselines'].values())
            maximum = max(maximum, max(np.array(reco['mean'])+np.sqrt(reco['variance'])))
            ax.set_ylim(0, 1.12*maximum)
            ax.set_ylabel(r'Mean material $\langle t/X_0\rangle$' if q == 'X0' else
                          r'Mean material $\langle t/\lambda_{\mathrm{I}}\rangle$')
            ax.grid(axis='y')
            r = baseline['ratio'][q]
            valid = np.array(r['valid'], dtype=bool)
            # The model rejects unsupported bins; omit them instead of plotting zero.
            if np.all(valid):
                plot(hist(r, 'ACTS / Geant4'), ax=ratio_ax, style=marker_style)
            else:
                centers = .5*(edges[:-1]+edges[1:])
                ratio_ax.errorbar(centers[valid], np.array(r['mean'], dtype=float)[valid],
                    yerr=np.sqrt(np.array(r['variance'], dtype=float)[valid]),
                    fmt='o', color='black', markersize=2.7, linewidth=.65)
            values = np.array([v for v in r['mean'] if v is not None])
            errors = np.sqrt(np.array([v for v in r['variance'] if v is not None]))
            ratio_ax.set_ylim(min(.9, float(min(values-errors))-.025),
                              max(1.1, float(max(values+errors))+.025))
            ratio_ax.axhline(1, color='#777777', linewidth=.8)
            ratio_ax.grid(axis='y')
            ratio_ax.set_ylabel('ACTS / Geant4')
            ratio_ax.set_xlabel(r'Pseudorapidity $\eta$')
            ratio_ax.set_xlim(-4, 4)
        handles = []
        for c in active:
            detector, sensitivity = c.rsplit('_', 1)
            alpha = .5 if sensitivity == 'nonsensitive' else 1.
            label = labels[detector]+' · '+('passive' if sensitivity == 'nonsensitive' else 'sensitive')
            handles.append(Patch(facecolor=COLORS[detector], edgecolor=COLORS[detector],
                                 alpha=alpha, label=label))
        handles.append(Line2D([], [], marker='o', linestyle='none', color='black',
                              markersize=4, label='ACTS total ± ray SEM'))
        if name == 'current':
            handles.append(Line2D([], [], color='#222222', linestyle=':', linewidth=1.9,
                                  label='Old Geant4 total'))
        fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.805, .84),
                   frameon=False, fontsize=10, labelspacing=1.15, handlelength=2.1)
        fig.text(.075, .063, 'Means include zero contributions. Passive opacity: 50%. '
                 'Sensitivity follows the DD4hep volume flag.', fontsize=9, color='#505050')
        fig.text(.075, .033, 'Ratio errors: ACTS ray sampling only, conditional on fixed map '
                 'and Geant4 means; map training uncertainty omitted.', fontsize=9, color='#505050')
        for extension in ('png', 'pdf', 'svg'):
            target = args.output/f'material-{name}.{extension}'
            fig.savefig(target, dpi=180)
            if extension == 'svg':
                target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
            files.append({'name': target.name, 'sha256': sha(target)})
        plt.close(fig)
    direct = distribution('unrooted').read_text('direct_url.json')
    report = {'comparison_sha256': sha(args.data), 'plotter_sha256': sha(__file__),
        'unrooted': version('unrooted'), 'unrooted_source': json.loads(direct) if direct else None,
        'matplotlib': version('matplotlib'), 'files': files,
        'component_colors': COLORS, 'sensitive_alpha': 1, 'passive_alpha': .5}
    (args.output/'plot-report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
