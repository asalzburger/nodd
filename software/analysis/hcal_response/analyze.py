"""Audited fixed-energy HCAL response aggregates and ECAL-style angular plots."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

COLOR = '#cc6600'
PERIOD = math.pi / 8
EDGES = {'eta': np.linspace(-3, 3, 16), 'phi': np.linspace(-50, 50, 16)}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def save_figure(fig, path):
    fig.savefig(path)
    if Path(path).suffix == '.svg':
        Path(path).write_text('\n'.join(line.rstrip() for line in Path(path).read_text().splitlines()) + '\n')


def moments(values):
    values = np.asarray(values, dtype=float)
    if not len(values):
        return dict(events=0, mean_response=None, sample_sd=None, fractional_width=None,
                    zero_events=0, quantiles=None)
    mean = float(values.mean())
    sd = float(values.std(ddof=1)) if len(values) > 1 else None
    return dict(events=len(values), mean_response=mean, sample_sd=sd,
                fractional_width=sd / mean if sd is not None and mean > 0 else None,
                zero_events=int(np.count_nonzero(values == 0)),
                quantiles=dict(zip(('q02', 'q16', 'q50', 'q84', 'q98'),
                                   map(float, np.quantile(values, [.02, .16, .50, .84, .98])))))


def categories(rows):
    if any(not math.isfinite(r['eta']) or not math.isfinite(r['phi']) or not -math.pi <= r['phi'] < math.pi for r in rows):
        raise ValueError('Nonfinite or out-of-range primary direction')
    coords = {'eta': np.array([r['eta'] for r in rows]),
              'phi': 100 * ((np.array([r['phi'] for r in rows]) + PERIOD / 2) % PERIOD - PERIOD / 2) / PERIOD}
    cats = {}
    for axis, edges in EDGES.items():
        if np.any(coords[axis] < edges[0]) or np.any(coords[axis] > edges[-1]):
            raise ValueError('Angular input outside declared interval')
        cats[axis] = np.minimum(np.searchsorted(edges, coords[axis], side='right') - 1, 14)
    return cats


def analyze(args):
    run = args.run.resolve()
    proof = json.loads((run / 'readback.json').read_text())
    receipt = json.loads((run / 'receipt.json').read_text())
    if proof['status'] != 'PASS' or receipt['exit_code'] != 0:
        raise ValueError('Successful transport and complete saved-data readback required')
    ledger = run / 'event-summary.jsonl'
    if proof['event_summary_sha256'] != sha(ledger) or proof['receipt_sha256'] != sha(run / 'receipt.json'):
        raise ValueError('Changed audited input')
    rows = sorted((json.loads(line) for line in ledger.read_text().splitlines()), key=lambda r: r['event'])
    if len(rows) != 10000 or [r['event'] for r in rows] != list(range(10000)):
        raise ValueError('Require exactly the full 10000-primary population')
    if any(not math.isfinite(r['energy_GeV']) or abs(r['energy_GeV'] - 50) > 1e-7 for r in rows):
        raise ValueError('Expected fixed total energy 50 GeV')
    response = np.array([r['response'] for r in rows])
    if not np.all(np.isfinite(response)) or np.any(response < 0):
        raise ValueError('Invalid response')
    if not np.allclose(response, [r['signal_GeV'] / r['energy_GeV'] for r in rows], rtol=1e-12, atol=1e-14):
        raise ValueError('Response/energy mismatch')
    cats = categories(rows)
    hist_edges = np.linspace(0, max(float(response.max()) * 1.000001, .001), 81)
    rng = np.random.default_rng(args.seed)
    widths = np.empty((args.bootstrap, 30))
    means = np.empty_like(widths)
    for b in range(args.bootstrap):
        selected = rng.integers(len(rows), size=len(rows))
        values = response[selected]
        for a, axis in enumerate(EDGES):
            group = cats[axis][selected]
            count = np.bincount(group, minlength=15)
            total = np.bincount(group, weights=values, minlength=15)
            squares = np.bincount(group, weights=values**2, minlength=15)
            mean = np.divide(total, count, out=np.full(15, np.nan), where=count > 0)
            variance = np.divide(squares - total * mean, count - 1, out=np.full(15, np.nan), where=count > 1)
            width = np.divide(np.sqrt(np.maximum(variance, 0)), mean, out=np.full(15, np.nan), where=mean > 0)
            widths[b, a * 15:(a + 1) * 15] = width
            means[b, a * 15:(a + 1) * 15] = mean
    projections = {}
    for a, (axis, edges) in enumerate(EDGES.items()):
        bins = []
        for i in range(15):
            selected = cats[axis] == i
            entry = moments(response[selected])
            entry.update(low=float(edges[i]), high=float(edges[i + 1]),
                         histogram_counts=np.histogram(response[selected], hist_edges)[0].tolist())
            for key, draws in (('fractional_width', widths), ('mean_response', means)):
                values = draws[:, a * 15 + i]
                bad = int(np.count_nonzero(~np.isfinite(values)))
                entry[key + '_undefined_bootstrap'] = bad
                entry[key + '_ci95'] = list(map(float, np.quantile(values, [.025, .975]))) if not bad else None
            bins.append(entry)
        if sum(b['events'] for b in bins) != 10000:
            raise ValueError('Angular projection lost events')
        projections[axis] = dict(edges=edges.tolist(), bins=bins,
                                 unit='signed pseudorapidity' if axis == 'eta' else 'percent of 22.5 degree barrel sector')
    layers = np.array([r['layer_energies_GeV'] for r in rows], dtype=float)
    if layers.shape != (10000, 60) or not np.all(np.isfinite(layers)) or np.any(layers < 0):
        raise ValueError('Invalid longitudinal profile')
    if not np.allclose(layers.sum(axis=1), response * 50, rtol=1e-5, atol=1e-7):
        raise ValueError('Layer profile does not close to saved hit sum')
    tail = np.array([r['terminal_six_fraction'] for r in rows])
    expected_tail = np.divide(layers[:, -6:].sum(axis=1), layers.sum(axis=1),
                              out=np.zeros(10000), where=layers.sum(axis=1) > 0)
    if not np.allclose(tail, expected_tail, rtol=1e-5, atol=1e-7):
        raise ValueError('Terminal layer fraction does not close')
    escape = np.array([r['observer']['world_escape_kinetic_GeV'] for r in rows])
    if not np.all(np.isfinite(escape)) or np.any(escape < 0):
        raise ValueError('Invalid world-escape kinetic energy')
    fullphi = np.array([r['phi'] for r in rows])
    controls = []
    for lo, hi in zip(np.linspace(-math.pi, math.pi, 17)[:-1], np.linspace(-math.pi, math.pi, 17)[1:]):
        keep = (fullphi >= lo) & (fullphi < hi)
        controls.append(dict(low=float(lo), high=float(hi), **moments(response[keep])))
    if sum(c['events'] for c in controls) != 10000:
        raise ValueError('Full-phi control lost primaries')
    sample = proof.get('sample') or {}
    geometry = sample.get('geometry_manifest') or {}
    compact_sample = {k: v for k, v in sample.items() if k != 'geometry_manifest'}
    compact_geometry = {k: geometry[k] for k in ('config', 'counts', 'depth', 'id_descriptor',
                        'source_sha256', 'export_sha256', 'raw_sensitive_volumes',
                        'sensitive_tiles', 'sensitive_representation', 'endcap_rotational_symmetry') if k in geometry}
    workers = proof.get('workers') or []
    steel_materials = {json.dumps(m, sort_keys=True) for w in workers for m in w.get('steel_materials', [])}
    runtime_materials = [json.loads(m) for m in sorted(steel_materials)]
    for material in runtime_materials:
        material['nominal_1800mm_steel_nuclear_lengths'] = 1800 / material['nuclear_interaction_length_mm']
    result = dict(status='PROTOTYPE', events=10000, particle='pi-', total_energy_GeV=50,
        observable='sample SD(R,ddof=1)/mean(R), R=sum(raw scintillator deposits)/primary total energy',
        interpretation='Fixed-energy raw visible-response width, including sampling fluctuations, angular variation, gaps and leakage; no calibration or digitization',
        angular_scope='15 signed eta bins; 15 signed folded-phi bins over a complete 22.5 degree barrel reference sector; all events retained',
        phi_display_padding_percent=15,
        phi_symmetry='Barrel sector reference coordinate; full-phi controls retained because quarter-packed endcaps need not share 16-fold symmetry',
        bootstrap=dict(replicates=args.bootstrap, seed=args.seed, intervals='pointwise 95% percentile',
                       resampling='joint whole-primary resampling across both projections; conditional on saved transports'),
        global_statistics=moments(response), projections=projections,
        histograms=dict(response_edges=hist_edges.tolist(), unit='R=Eraw/Etrue', normalization='unweighted primary counts; all zeros and tails included',
                        inclusive_counts=np.histogram(response, hist_edges)[0].tolist()),
        longitudinal=dict(layer_numbers=list(range(60)), mean_energy_GeV=layers.mean(axis=0).tolist(),
                          mean_energy_standard_error_GeV=(layers.std(axis=0, ddof=1) / 100).tolist(),
                          terminal_six_fraction_mean=float(tail.mean()),
                          terminal_six_fraction_quantiles=dict(zip(('q50', 'q90', 'q95', 'q99'), map(float, np.quantile(tail, [.5, .9, .95, .99])))),
                          events_above_10percent=int(np.count_nonzero(tail > .1)),
                          interpretation='Activity in the final six sampling layers; not a direct leakage or containment measurement'),
        world_escape=dict(mean_kinetic_GeV=float(escape.mean()),
                          quantiles_GeV=dict(zip(('q50', 'q90', 'q95', 'q99'), map(float, np.quantile(escape, [.5, .9, .95, .99])))),
                          interpretation='Kinetic energy crossing the outer world boundary; excludes rest energy and nuclear invisible energy; not a calorimetric balance'),
        controls=dict(full_phi=controls),
        width_covariance=dict(order=[f'{axis}:{i}' for axis in EDGES for i in range(15)], unit='fractional width squared',
                              matrix=np.cov(widths, rowvar=False).tolist() if np.all(np.isfinite(widths)) else None),
        evidence=dict(receipt_sha256=sha(run / 'receipt.json'), readback_sha256=sha(run / 'readback.json'),
                      ledger_sha256=sha(ledger), analysis_sha256=sha(__file__), receipt=receipt,
                      readback={k: v for k, v in proof.items() if k not in ('workers', 'sample')},
                      sample=compact_sample, geometry=compact_geometry,
                      runtime_worker_threads=sorted(w['thread_id'] for w in workers),
                      runtime_steel_materials=runtime_materials))
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    save(out / 'summary.json', result)
    plot(result, out / 'figures')
    print(json.dumps(dict(**result['global_statistics'], longitudinal=result['longitudinal']['terminal_six_fraction_quantiles']), indent=2))


def angular_plot(result, out, key, ylabel, filename):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.1), layout='constrained')
    for axis, (name, projection) in zip(axes, result['projections'].items()):
        bins = projection['bins']
        x = np.array([(b['low'] + b['high']) / 2 for b in bins])
        y = np.array([np.nan if b[key] is None else b[key] * 100 for b in bins])
        lo = np.array([b[key + '_ci95'][0] * 100 if b[key + '_ci95'] else np.nan for b in bins])
        hi = np.array([b[key + '_ci95'][1] * 100 if b[key + '_ci95'] else np.nan for b in bins])
        offsets = (-100, 0, 100) if name == 'phi' else (0,)
        for offset in offsets:
            axis.vlines(x + offset, lo, hi, color=COLOR, alpha=.85)
        axis.plot(np.concatenate([x + offset for offset in offsets]), np.tile(y, len(offsets)),
                  'o-', color=COLOR, markersize=4, linewidth=1.5)
        axis.set(xlim=(-65, 65) if name == 'phi' else (-3, 3), ylim=(0, None),
                 xlabel=r'HCAL barrel sector phase [% of 22.5°]' if name == 'phi' else r'Signed pseudorapidity $\eta$',
                 ylabel=ylabel)
        if name == 'phi':
            for start, end in ((-65, -50), (50, 65)):
                axis.axvspan(start, end, color=COLOR, alpha=.06)
            for edge in (-50, 50):
                axis.axvline(edge, color='#777777', ls='--', lw=.8)
        axis.grid(alpha=.18)
        axis.text(.02, .97, 'n/bin: ' + ' · '.join(str(b['events']) for b in bins), transform=axis.transAxes,
                  va='top', fontsize=6.5, color='#555555')
    fig.suptitle('nODD HCAL · 10,000 π⁻ · 50 GeV total energy', fontsize=15)
    fig.supxlabel('HCAL only · B = 0 · raw scintillator deposits · all zeros and tails included\n95% whole-primary bootstrap intervals; periodic margins repeat existing bins', fontsize=9)
    for ext in ('png', 'pdf', 'svg'):
        save_figure(fig, out / f'{filename}.{ext}')
    plt.close(fig)


def plot(result, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 180})
    angular_plot(result, out, 'fractional_width', r'$\sigma(R)/\langle R\rangle$ [%]', 'raw-energy-resolution')
    angular_plot(result, out, 'mean_response', 'Mean raw response [%]', 'mean-response')
    edges = np.array(result['histograms']['response_edges']) * 100
    for name, projection in result['projections'].items():
        fig, axes = plt.subplots(3, 5, figsize=(15, 8.4), layout='constrained')
        for axis, b in zip(axes.flat, projection['bins']):
            axis.stairs(b['histogram_counts'], edges, color=COLOR, fill=True, alpha=.55)
            label = f"{b['low']:.2f} ≤ η < {b['high']:.2f}" if name == 'eta' else f"{b['low']:.1f}…{b['high']:.1f}% sector"
            width = b['fractional_width'] * 100 if b['fractional_width'] is not None else float('nan')
            axis.set_title(label, fontsize=9)
            axis.text(.97, .94, f"n={b['events']}\nmean={100*b['mean_response']:.3f}%\nwidth={width:.1f}%\nzeros={b['zero_events']}",
                      transform=axis.transAxes, ha='right', va='top', fontsize=7.5)
            axis.grid(alpha=.12)
        fig.suptitle(f'HCAL raw response distributions · 50 GeV π⁻ · {name}', fontsize=15)
        fig.supxlabel('Raw scintillator response R = Eraw / Etrue [%]')
        fig.supylabel('Primaries / bin')
        for ext in ('png', 'pdf', 'svg'):
            save_figure(fig, out / f'response-distributions-{name}.{ext}')
        plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.7), layout='constrained')
    profile = result['longitudinal']
    axes[0].errorbar(np.arange(1, 61), profile['mean_energy_GeV'], yerr=profile['mean_energy_standard_error_GeV'], color=COLOR, lw=1.2)
    axes[0].axvspan(54.5, 60.5, color=COLOR, alpha=.1)
    axes[0].set(xlabel='Sampling layer (front to back)', ylabel='Mean raw deposit per primary [GeV]', xlim=(.5, 60.5), ylim=(0, None))
    axes[1].stairs(result['histograms']['inclusive_counts'], edges, color=COLOR, fill=True, alpha=.55)
    stats = result['global_statistics']
    axes[1].text(.97, .95, f"All {stats['events']:,} primaries\nMean Eraw = {50*stats['mean_response']:.3f} GeV\nSD / mean = {100*stats['fractional_width']:.2f}%\nZero response = {stats['zero_events']}\nMean terminal-six fraction = {100*profile['terminal_six_fraction_mean']:.2f}%",
                 transform=axes[1].transAxes, va='top', ha='right', fontsize=9)
    axes[1].set(xlabel='Raw scintillator response [%]', ylabel='Primaries / bin')
    for axis in axes: axis.grid(alpha=.18)
    fig.suptitle('HCAL depth and inclusive-response controls · 50 GeV π⁻', fontsize=14)
    fig.supxlabel('Terminal-layer activity diagnoses rear shower tails; it does not directly measure containment.', fontsize=9)
    for ext in ('png', 'pdf', 'svg'):
        save_figure(fig, out / f'depth-response-controls.{ext}')
    plt.close(fig)
    save(out / 'render.json', {p.name: sha(p) for p in sorted(out.iterdir()) if p.suffix in ('.png', '.pdf', '.svg')})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='stage', required=True)
    a = sub.add_parser('analyze'); a.add_argument('--run', type=Path, required=True); a.add_argument('--output', type=Path, required=True)
    a.add_argument('--bootstrap', type=int, default=1000); a.add_argument('--seed', type=int, default=13001000)
    a = sub.add_parser('plot'); a.add_argument('--summary', type=Path, required=True); a.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.stage == 'analyze': analyze(args)
    else: plot(json.loads(args.summary.read_text()), args.output)


if __name__ == '__main__':
    main()
