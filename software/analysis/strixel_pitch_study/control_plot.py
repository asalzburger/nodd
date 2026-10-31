#!/usr/bin/env python3
"""Plot the separately labeled Gaussian-response diagnostic with unrooted."""
import argparse
import gzip
import json
from pathlib import Path

import numpy as np

from control_analysis import MODEL
from plot import ROOT, COLORS, LABELS, Line2D, digest, frame, plt, points, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'docs/validation/DES-042/gaussian-control/profiles.json.gz')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/validation/DES-042/gaussian-control/figures')
    args = parser.parse_args()
    data = json.loads(gzip.decompress(args.data.read_bytes()))
    if data.get('response_model') != MODEL:
        raise ValueError('Need separately labeled Gaussian-control evidence')
    if data['provenance']['control_analyzer_sha256'] != digest(Path(__file__).with_name('control_analysis.py')):
        raise ValueError('Control analysis changed; replay before plotting')
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    manifest = {}
    for metric in ('absolute', 'ratio'):
        title = 'Track widths' if metric == 'absolute' else 'Resolution ratios to 0.5 mm'
        fig, axes = frame('Gaussian response control — ' + title,
                         '100 GeV transverse momentum · 5,000 paired muons per pitch · independent Gaussian errors, σ = pitch/√12 · no merging')
        for ax, (quantity, (label, unit, scale)) in zip(axes.flat, LABELS.items()):
            for case in data['groups'][0]['cases']:
                pitch = case['pitch_v_mm']
                if metric == 'ratio' and pitch == .5:
                    continue
                bins = case['eta_profiles']
                stats = [b['quantities'][quantity]['residual'] for b in bins]
                x = [(b['low'] + b['high']) / 2 for b in bins]
                key, error = ('width68', 'width68_se') if metric == 'absolute' else ('ratio_to_baseline', 'ratio_se')
                factor = scale if metric == 'absolute' else 1
                y = [s[key]*factor if s[key] is not None else np.nan for s in stats]
                e = [s[error]*factor if s[error] is not None else np.nan for s in stats]
                points(ax, x, y, pitch, f'{pitch:g} mm', e)
            ax.set(title=label, xlabel='Truth η', xlim=(-4,4))
            ax.grid(alpha=.18)
            if metric == 'absolute':
                ax.set_ylabel(f'Central 68.27% half-width [{unit}]')
                ax.set_yscale('log')
            else:
                ax.axhline(1, color=COLORS[.5], ls='--', lw=1)
                ax.set_ylabel('Width / 0.5 mm width')
        handles = [Line2D([], [], color=c, marker='o', lw=1.5, label=f'{p:g} mm local-v pitch')
                   for p,c in COLORS.items() if metric == 'absolute' or p != .5]
        fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.068,.88),ncol=4,frameon=False,fontsize=9)
        fig.text(.075,.07,f"Separate response diagnostic; all sensor axes use fixed pitch/√12 except the scanned strixel-v width. Paired bootstrap SE, {data['bootstrap']['replicates']} draws.",fontsize=8,color='#52606b')
        save(fig,args.output,'gaussian-'+metric+'-pt100',manifest)
    (args.output/'manifest.json').write_text(json.dumps(dict(schema_version=1,response_model=MODEL,
        plot_source_sha256=digest(__file__),profiles_sha256=digest(args.data),figures_sha256=manifest),indent=2)+'\n')
    print('Rendered',len(manifest),'separate Gaussian-control figure files')


if __name__ == '__main__':
    main()
