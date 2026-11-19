"""Rebin the audited restored-LAr/staggered-SiW samples; retain aggregates only."""
import argparse
import json
from pathlib import Path

import numpy as np

import compare as common

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    'lar': ('docs/validation/lar-restored/original-summary.json', 'candidate'),
    'siw': ('docs/validation/lar10k/summary.json', 'siw_staggered'),
}
AXES = {'eta': np.linspace(-3, 3, 16), 'phi': np.linspace(-np.pi, np.pi, 16)}
LABELS = {'lar': 'LAr (restored baseline)', 'siw': 'Si–W (staggered)'}


def analyze(runs, output):
    loaded = {name: common.load_run(path) for name, path in runs.items()}
    evidence = {}
    for name, (relative, key) in SOURCES.items():
        frozen = json.loads((ROOT / relative).read_text())['models'][key]
        actual = loaded[name][2]
        # Reuse the exact already audited samples, including their geometry labels.
        for field in ('receipt_sha256', 'readback_sha256', 'ledger_sha256', 'root_sha256', 'input'):
            if actual[field] != frozen['evidence'][field]:
                raise ValueError(f'{name}: differs from published sample: {field}')
        evidence[name] = {
            'summary': relative, 'summary_sha256': common.sha(ROOT / relative),
            'model_key': key,
            **{k: actual[k] for k in ('receipt_sha256', 'readback_sha256', 'ledger_sha256', 'root_sha256', 'input')},
            'global': common.moments(loaded[name][1][:, 4]),
        }
        if not np.isclose(evidence[name]['global']['fractional_width'], frozen['global']['fractional_width'], rtol=1e-12):
            raise ValueError('Inclusive width differs from published sample')
    base = loaded['lar'][1]
    if base.shape != (10000, 5):
        raise ValueError('Expected all 10,000 events')
    if not np.allclose(loaded['siw'][1][:, :3], base[:, :3], rtol=0, atol=1e-9):
        raise ValueError('Primary energies/directions do not match by event ID')
    for field in ('input_sha256', 'truth_sha256'):
        if evidence['lar']['input'][field] != evidence['siw']['input'][field]:
            raise ValueError('Primary input hashes differ')
    cats = {axis: common.index(base[:, col], edges)
            for (axis, edges), col in zip(AXES.items(), (1, 2))}
    responses = {name: entry[1][:, 4] for name, entry in loaded.items()}
    boot = {(name, axis): np.empty((1000, 15)) for name in SOURCES for axis in AXES}
    rng = np.random.default_rng(13001000)
    for b in range(1000):
        weights = np.bincount(rng.integers(len(base), size=len(base)), minlength=len(base))
        for (name, axis), draws in boot.items():
            _, draws[b] = common.binned_moments(responses[name], cats[axis], weights, 15)
    models = {}
    for name in SOURCES:
        projections = {}
        for axis, edges in AXES.items():
            rows = []
            for i in range(15):
                selected = cats[axis] == i
                row = common.moments(responses[name][selected])
                row['width_ci95'] = common.interval(boot[name, axis][:, i])['ci95']
                row['mean_primary_energy_GeV'] = float(base[selected, 0].mean())
                rows.append(row)
            projections[axis] = {'edges': edges.tolist(), 'unit': 'rad' if axis == 'phi' else 'dimensionless', 'bins': rows}
        models[name] = {'label': LABELS[name], 'evidence': evidence[name], 'projections': projections}
    order = [f'{name}:{axis}:{i}' for name in SOURCES for axis in AXES for i in range(15)]
    draws = np.concatenate([boot[name, axis] for name in SOURCES for axis in AXES], axis=1)
    if not np.isfinite(draws).all():
        raise ValueError('Undefined bootstrap width')
    result = {
        'events_per_model': len(base), 'observable': 'sample SD(R)/mean(R), R=Eraw/Etrue; ddof=1',
        'scope': 'Matched ECAL-only B=0 electrons, total energy uniform 10–80 GeV; all events, zeros and tails retained; no calibration',
        'interpretation': 'Spectrum-averaged raw response width, including within-bin angular variation, losses and leakage; not fixed-energy intrinsic reconstructed resolution',
        'bin_convention': 'Lower inclusive, upper exclusive; final upper edge included. Signed eta and full phi, no folding.',
        'bootstrap': {'replicates': 1000, 'seed': 13001000, 'intervals': 'pointwise 95% percentile',
                      'resampling': 'shared whole-event multiplicities across models and projections; conditional on saved transports'},
        'analysis_sha256': common.sha(__file__), 'helper_sha256': common.sha(common.__file__),
        'models': models, 'width_covariance': {'order': order, 'unit': 'fractional width squared', 'matrix': np.cov(draws, rowvar=False).tolist()},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    common.write(output, result)


def plot(summary, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    result = json.loads(summary.read_text())
    output.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none', 'pdf.fonttype': 42}):
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
        fig.subplots_adjust(left=.08, right=.985, top=.77, bottom=.23, wspace=.13)
        for ax, axis in zip(axes, AXES):
            for name, style in (('lar', '-'), ('siw', ':')):
                proj = result['models'][name]['projections'][axis]
                edges = np.array(proj['edges'])
                x = (edges[1:] + edges[:-1]) / 2
                y = 100 * np.array([r['fractional_width'] for r in proj['bins']])
                ci = 100 * np.array([r['width_ci95'] for r in proj['bins']])
                ax.plot(x, y, color='#cccc00', linestyle=style, linewidth=2.7, label=LABELS[name])
                ax.vlines(x, ci[:, 0], ci[:, 1], color='#cccc00', linewidth=1, alpha=.85)
            ax.set_xlim(edges[0], edges[-1])
            ax.set_ylim(bottom=0)
            ax.set_xlabel(r'Pseudorapidity $\eta$' if axis == 'eta' else r'Azimuth $\phi$ [rad]')
            ax.grid(axis='y', alpha=.2)
            ax.set_axisbelow(True)
        axes[0].set_xticks(np.arange(-3, 4))
        axes[1].set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi], [r'$-\pi$', r'$-\pi/2$', '0', r'$\pi/2$', r'$\pi$'])
        axes[0].set_ylabel('Raw fractional energy resolution [%]')
        fig.suptitle('LAr and Si–W raw energy resolution', x=.08, y=.98, ha='left', fontsize=17, weight='bold')
        fig.text(.08, .86, r'10,000 matched electrons · $E_{\rm true}=10$–$80$ GeV · ECAL only, $B=0$ · 15 bins', fontsize=11)
        axes[1].legend(frameon=False, loc='upper right', handlelength=3.3)
        fig.text(.08, .095, r'$R=E_{\rm raw}/E_{\rm true}$; resolution = sample SD$(R)$/mean$(R)$ · Error bars: pointwise 95% bootstrap intervals', fontsize=10)
        fig.text(.08, .04, 'All events, including zeros and tails; no calibration. Width includes response variation within each angular bin.', fontsize=9, color='#555555')
        for suffix in ('png', 'pdf', 'svg'):
            path = output / f'raw-energy-resolution.{suffix}'
            fig.savefig(path, dpi=200, facecolor='white')
            if suffix == 'svg':
                path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
        plt.close(fig)
    common.write(output / 'render.json', {'summary_sha256': common.sha(summary), 'plotter_sha256': common.sha(__file__),
                 'numpy_version': np.__version__, 'matplotlib_version': matplotlib.__version__,
                 'outputs': {p.name: common.sha(p) for p in sorted(output.glob('raw-energy-resolution.*'))}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('analyze')
    p.add_argument('--lar-run', type=Path, required=True)
    p.add_argument('--siw-run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('plot')
    p.add_argument('--summary', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'analyze':
        analyze({'lar': args.lar_run, 'siw': args.siw_run}, args.output)
    else:
        plot(args.summary, args.output)


if __name__ == '__main__':
    main()
