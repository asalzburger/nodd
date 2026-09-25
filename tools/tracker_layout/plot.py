#!/usr/bin/env python3
"""Render review figures from the isolated DES-006 prototype evidence."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
COLORS = dict(pixel='#1565a8', short_strip='#be7c12', long_strip='#7c429a')


def main():
    data = json.loads((ROOT / 'docs/design/DES-006-layouts.json').read_text())
    report = json.loads((ROOT / 'docs/validation/DES-006-layout-screen.json').read_text())
    out = ROOT / 'docs/design/figures'
    for candidate in data['candidates']:
        fig, ax = plt.subplots(figsize=(9, 3.5), layout='constrained')
        for layer in candidate['layers']:
            color = COLORS[layer['subsystem']]
            if layer['kind'] == 'cylinder':
                ax.plot([0, layer['z_max_m']], [layer['r_m']] * 2, c=color, lw=2)
            elif layer['z_m'] > 0:
                ax.plot([layer['z_m']] * 2, [layer['r_min_m'], layer['r_max_m']], c=color, lw=1.7)
        import math
        for eta in [1., 2., 3., 4.]:
            z = min(3.15, 1.14 * math.sinh(eta))
            ax.plot([0, z], [0, z / math.sinh(eta)], c='gray', lw=.7, ls='--')
            ax.text(z, z / math.sinh(eta), f' eta={eta:g}', fontsize=8)
        ax.axhline(1.14, c='black', lw=.8)
        ax.axvline(3.15, c='black', lw=.8)
        for key, color in COLORS.items():
            ax.plot([], [], c=color, label=key.replace('_', ' '))
        ax.set(xlabel='z [m]; negative side reflected', ylabel='r [m]', xlim=(0, 3.42), ylim=(0, 1.24),
               title=f"{candidate['id']} | {candidate['name']} | PROTOTYPE ideal surfaces")
        ax.legend(loc='upper left', ncol=3, fontsize=8)
        fig.savefig(out / f"DES-006-{candidate['id']}-rz.png", dpi=170)
        svg = out / f"DES-006-{candidate['id']}-rz.svg"
        fig.savefig(svg)
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
        plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), layout='constrained')
    for cid, candidate in report['candidates'].items():
        for zv, ls in [(0., '-'), (.15, '--')]:
            p = next(p for p in candidate['profiles'] if p['vertex_z_m'] == zv and p['pt_GeV'] == 100.)
            mask = [i for i,e in enumerate(report['eta_grid']) if e >= 0]
            eta = [report['eta_grid'][i] for i in mask]
            for ax, key, title in zip(axes.flat,
                ['stations','pixel_stations','radial_span_m','local_material_percent'],
                ['Effective measurement stations','Pixel stations','Radial span [m]','Local material scenario [% X0]']):
                ax.plot(eta,[p[key][i] for i in mask],ls,label=f'{cid}: vertex z={zv:g} m')
                ax.set(xlabel='eta',title=title)
                ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8)
    fig.suptitle('PROTOTYPE: 3 T, pT=100 GeV; no module gaps, beam pipe or remote services')
    fig.savefig(out/'DES-006-comparison.png',dpi=170)
    plt.close(fig)

    idres = json.loads((ROOT/'docs/validation/DES-006-idres-results.json').read_text())
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.7), layout='constrained')
    for run in idres['runs']:
        if run['field_T'] != 3 or run['material_scale'] != 1:
            continue
        for ax, pt in zip(axes, [1., 10., 100.]):
            rows = [r for r in run['origin_profile'] if r['pt_GeV'] == pt]
            ax.semilogy([r['eta'] for r in rows], [r['sigma_inverse_pt_GeV_inverse'] for r in rows],
                        label=run['candidate'])
            ax.set(xlabel='eta', title=f'pT = {pt:g} GeV')
            ax.grid(alpha=.25)
    axes[0].set_ylabel('sigma(1/pT) [GeV^-1]')
    axes[0].legend()
    fig.suptitle('IdRes PROTOTYPE | 3 T, origin, nominal local material | no beam pipe/services')
    fig.savefig(out/'DES-006-idres-resolution.png', dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    main()
