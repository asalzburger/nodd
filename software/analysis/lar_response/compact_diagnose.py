"""Post-hoc distribution controls from frozen raw ledgers and saved OOF gains.

No transport, calibration fitting, event selection optimization or new inference.
Only aggregate histograms/statistics are exported; event payloads remain local.
"""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
import compact_compare as pair
import compact_calibrate as calibration

REGIONS = {
    'barrel': (0., 1.2), 'transition': (1.2, 1.5), 'endcap': (1.5, 3.),
    'endcap_shoulder': (1.5, 1.8), 'endcap_bulk': (1.8, 3.),
}
LABELS = {'barrel': 'Core barrel: 0 ≤ |η| < 1.2',
          'transition': 'Transition: 1.2 ≤ |η| < 1.5',
          'endcap': 'Broad endcap: 1.5 ≤ |η| ≤ 3',
          'endcap_shoulder': 'Shoulder: 1.5 ≤ |η| < 1.8',
          'endcap_bulk': 'Endcap bulk: 1.8 ≤ |η| ≤ 3'}


def hist(values, edges):
    return dict(edges=edges.tolist(), counts=np.histogram(values, edges)[0].tolist(),
                events=len(values), underflow=int(np.count_nonzero(values < edges[0])),
                overflow=int(np.count_nonzero(values > edges[-1])),
                normalization='counts / all selected events, not renormalized to displayed range')


def saved_predictions(values, ids, models, scope):
    folds = calibration.make_folds(ids)
    if sorted(m['excluded_fold'] for m in models) != list(range(5)):
        raise ValueError('Need all five distinct evaluated fold models')
    y = np.empty(len(values))
    for m in models:
        heldout = folds == m['excluded_fold']
        if (m['training_primary_ids_sha256'] != calibration.ids_hash(ids[~heldout]) or
                m['heldout_primary_ids_sha256'] != calibration.ids_hash(ids[heldout])):
            raise ValueError('Saved model does not exclude this whole validation fold')
        y[heldout] = calibration.apply_calibration(m, values[heldout, 3], values[heldout, 1], scope) / values[heldout, 0]
    return y


def record(raw, corrected):
    mean = float(np.mean(raw))
    if mean <= 0:
        raise ValueError('Cannot normalize a region with nonpositive mean')
    return dict(raw=pair.moments(raw), heldout=pair.moments(corrected),
                raw_histogram=hist(raw, np.linspace(0., .4, 401)),
                shape_histogram=hist(raw / mean, np.linspace(0., 3., 601)),
                heldout_histogram=hist(corrected, np.linspace(0., 3., 601)),
                shape_definition='Raw R / own regional mean(R); display normalization only, not calibrated precision')


def analyze(args):
    common = pair.common
    contract = json.loads(args.contract.read_text())
    primary = json.loads(args.raw_summary.read_text())
    secondary = json.loads(args.calibrated_summary.read_text())
    saved = json.loads(args.models.read_text())
    if common.sha(args.models) != secondary['calibration_models_sha256']:
        raise ValueError('Changed saved calibration model artifact')
    loaded = {n: common.load_run(p) for n, p in
              [('reference', args.reference_run), ('candidate', args.candidate_run)]}
    pair.validate_pair(loaded, contract)
    result = dict(scope='Post-hoc distribution diagnosis, not a new primary test or causal ablation',
                  regions={k: dict(abs_eta_interval=list(v), upper_inclusive=v[1] == 3., label=LABELS[k]) for k, v in REGIONS.items()},
                  energy_slice_GeV=[45., 50.], models={},
                  source=dict(revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                              script_sha256=common.sha(__file__), raw_summary_sha256=common.sha(args.raw_summary),
                              calibrated_summary_sha256=common.sha(args.calibrated_summary),
                              calibration_models_sha256=common.sha(args.models), contract_sha256=common.sha(args.contract)),
                  limitations=['No new fit or bootstrap; original reported paired intervals remain in the primary and secondary summaries.',
                               'Endcap shoulder/bulk split and selected energy-slice plots are post-hoc descriptive controls.',
                               'Saved-ledger/receipt/source identity is rechecked; no native execution or ROOT rehash is repeated.'])
    for name, (rows, v, evidence) in loaded.items():
        for key in ('ledger_sha256', 'receipt_sha256', 'readback_sha256', 'root_sha256'):
            if evidence[key] != primary['models'][name]['evidence'][key] or evidence[key] != secondary['models'][name]['evidence'][key]:
                raise ValueError('Ledger/receipt identity differs from frozen summaries: ' + key)
        ids = np.array([r['event'] for r in rows])
        scope = {k: contract[name+'_'+k] for k in ('compact_sha256', 'materials_sha256')}
        y = saved_predictions(v, ids, saved['models'][name]['fold_models'], scope)
        eta = np.abs(v[:, 1]); out = dict(label=primary['models'][name]['label'], regions={}, ledger_sha256=evidence['ledger_sha256'])
        for key, (lo, hi) in REGIONS.items():
            select = (eta >= lo) & ((eta <= hi) if hi == 3. else (eta < hi))
            out['regions'][key] = record(v[select, 4], y[select])
        for i, key in enumerate(('barrel', 'transition', 'endcap')):
            for kind, summary in [('raw', primary), ('heldout', secondary)]:
                expected = summary['models'][name]['projections']['broad_eta']['bins'][i]
                actual = out['regions'][key][kind]
                for field in ('events', 'mean_response', 'sample_sd', 'fractional_width', 'zero_events'):
                    if not np.isclose(actual[field], expected[field], rtol=2e-12, atol=2e-14):
                        raise ValueError('Recreated statistic differs from frozen summary: ' + key + '/' + field)
        select = (eta < 1.2) & (v[:, 0] >= 45.) & (v[:, 0] < 50.)
        out['barrel_energy_slice'] = record(v[select, 4], y[select])
        select = eta < 1.2; z = y[select]; e = v[select, 0]
        ss = float(np.sum((z-z.mean())**2)); between = 0.
        for lo in range(10, 80, 5):
            a = z[(e >= lo) & (e < lo+5)]
            between += len(a) * float((a.mean()-z.mean())**2)
        out['barrel_energy_mean_variance_fraction'] = between / ss
        out['variance_limit'] = 'Descriptive sums of squares for 14 energy-bin means; within-bin residual includes eta, shower and other variation, not an isolated stochastic term.'
        result['models'][name] = out
    args.output.mkdir(parents=True, exist_ok=False)
    common.write(args.output / 'summary.json', result)
    print('Frozen ledger/model/statistic checks passed; aggregate distribution summary written.')


def plot(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    s = json.loads(args.summary.read_text())
    # Established LAr palette, with a lighter reference shade.
    colors = {'reference': '#d6dd65', 'candidate': '#c6d300'}
    args.output.mkdir(parents=True, exist_ok=False)
    renders = {}
    def export(fig, name):
        fig.text(.01, .012, 'Same saved 10k electrons · all selected events and tails retained · post-hoc descriptive controls · no Gaussian fits', fontsize=9)
        fig.tight_layout(rect=(0, .04, 1, .95))
        for ext in ('png', 'pdf', 'svg'):
            p = args.output / (name+'.'+ext); fig.savefig(p, dpi=160)
            if ext == 'svg':
                p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
            renders[p.name] = pair.common.sha(p)
        plt.close(fig)
    def panel(ax, records, kind, limits):
        outside = []
        for name in pair.MODELS:
            r = records[name]; h = r[kind+'_histogram']; edges = np.array(h['edges'])
            centers = (edges[:-1]+edges[1:])/2
            outside.append(int(np.sum(np.array(h['counts'])[(centers < limits[0]) | (centers > limits[1])])) + h['underflow'] + h['overflow'])
            stats = r['heldout' if kind == 'heldout' else 'raw']
            ax.stairs(np.array(h['counts']) / h['events'], edges, color=colors[name],
                      linestyle='--' if name == 'reference' else '-', linewidth=1.6,
                      label=('Original' if name == 'reference' else 'Compact')+f': n={h["events"]}, CV={100*stats["fractional_width"]:.2f}%')
        ax.set_xlim(*limits); ax.set_ylabel('Fraction of all selected events / bin'); ax.grid(alpha=.2)
        ax.legend(fontsize=8, loc='upper right')
        ax.text(.02, .03, f'Outside axis: original {outside[0]}, compact {outside[1]}\nAll events enter the reported CV', transform=ax.transAxes, va='bottom', fontsize=8,
                bbox=dict(facecolor='white', edgecolor='none', alpha=.85))
        ax.set_xlabel({'raw': 'Raw R = active deposited energy / true energy',
                       'shape': 'Raw R / own regional mean(R)  [display only]',
                       'heldout': 'Held-out Ehat / true energy  [no recentering]'}[kind])
        if kind != 'raw': ax.axvline(1., color='.4', lw=.7)
    fig, axs = plt.subplots(2, 3, figsize=(17, 9))
    for j, key in enumerate(('barrel', 'transition', 'endcap')):
        records = {n: m['regions'][key] for n, m in s['models'].items()}
        panel(axs[0,j], records, 'raw', (0., .26)); panel(axs[1,j], records, 'shape', (0., 2.5) if key == 'transition' else (.55, 1.45))
        axs[0,j].set_title(LABELS[key])
    fig.suptitle('Underlying uncalibrated distributions used for the raw SD(R)/mean(R) controls')
    export(fig, 'regional-raw-distributions')
    fig, axs = plt.subplots(2, 2, figsize=(13, 8))
    for i, key in enumerate(('endcap_shoulder', 'endcap_bulk')):
        records = {n: m['regions'][key] for n, m in s['models'].items()}
        panel(axs[i,0], records, 'raw', (0., .26)); panel(axs[i,1], records, 'heldout', (0., 2.))
        for ax in axs[i]: ax.set_title(LABELS[key])
    fig.suptitle('The broad endcap penalty is concentrated near the shifted barrel–endcap shoulder')
    export(fig, 'endcap-shoulder-distributions')
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8))
    records = {n: m['barrel_energy_slice'] for n, m in s['models'].items()}
    panel(axs[0], records, 'shape', (.75, 1.25)); panel(axs[1], records, 'heldout', (.75, 1.25))
    fig.suptitle('Core barrel, 45 ≤ Etrue < 50 GeV: broader shape remains within one energy slice')
    export(fig, 'barrel-energy-slice-distributions')
    pair.common.write(args.output / 'render.json', dict(summary_sha256=pair.common.sha(args.summary), figures=renders))
    print('Three distribution figure groups written as PNG/PDF/SVG.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('analyze')
    for key in ('reference-run', 'candidate-run', 'contract', 'raw-summary', 'calibrated-summary', 'models', 'output'):
        a.add_argument('--'+key, type=Path, required=True)
    a = sub.add_parser('plot'); a.add_argument('--summary', type=Path, required=True); a.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); (analyze if a.command == 'analyze' else plot)(a)
