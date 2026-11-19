"""Held-out 50 GeV active-deposit response; full events remain local.

The fitted f is an effective visible response fraction including geometric and
containment losses. It is not a separately scored active/passive material
sampling fraction. Multiplication by 1/f leaves SD/mean exactly unchanged.
"""
import argparse
import json
import math
from pathlib import Path
import subprocess

import numpy as np

import compare as common

ROOT = Path(__file__).resolve().parents[3]
ENERGY = 50.0
ETA = 0.1
PHI = math.radians(0.7)
MODELS = ('lar', 'siw')
POPULATIONS = ('calibration', 'evaluation')
COUNTS = {'calibration': 2000, 'evaluation': 10000}
SEEDS = {'lar': {'calibration': 705020, 'evaluation': 705021},
         'siw': {'calibration': 705030, 'evaluation': 705031}}
GEOMETRY = {
    'lar': {'detector.xml': '2cfd36df7483b5382276ae1c77bb30d485a28ff8fd07865a929483ef517eda0c',
            'materials.xml': 'a074b67a8d0b96b6ebb80742088474a4d46ae639b77693fc240650268efc7353'},
    'siw': {'detector.xml': 'd78ecea5c5aa5173af54a4ce392994491eede936a7f4edb87d55bc72e69a0c2b',
            'materials.xml': '5091f0cbc2444b6ef481c2293ec99375e5eada82a84ab03be7a50f3b8375cee1'},
}
LABELS = {'lar': 'LAr (restored baseline)', 'siw': 'Si–W (staggered)'}
COLLECTIONS = {'lar': ('LArBarrelHits', 'LArEndcapHits'), 'siw': ('BARRELHits', 'EDGEHits')}
METRICS = ('effective_response_fraction', 'raw_energy_mean_GeV', 'raw_energy_sd_GeV',
           'raw_energy_cv', 'raw_fraction_mean', 'raw_fraction_sd',
           'corrected_fraction_mean', 'corrected_fraction_sd', 'corrected_fraction_cv')


def portable(value):
    value = common.portable(value)
    if isinstance(value, str):
        return value.replace(str(Path.home()), '$HOME')
    if isinstance(value, list):
        return [portable(v) for v in value]
    if isinstance(value, dict):
        return {portable(k): portable(v) for k, v in value.items()}
    return value


def validate_population(name, population, values, receipt, proof):
    """Bind population, direction, geometry and independent RNG stream labels."""
    n = COUNTS[population]
    seed = SEEDS[name][population]
    if values.shape != (n, 5) or receipt.get('events') != n or proof.get('events') != n:
        raise ValueError('Wrong exact population: ' + name + '/' + population)
    if receipt.get('skip') != 0 or receipt.get('seed') != seed or receipt.get('threads') != 12:
        raise ValueError('Wrong stream/worker contract: ' + name + '/' + population)
    if not np.allclose(values[:, :3], [ENERGY, ETA, PHI], rtol=0, atol=1e-9):
        raise ValueError('Primary differs from fixed 50 GeV direction')
    sample = proof.get('sample', {})
    point = sample.get('validation_point', {})
    for key, wanted in {'energy_GeV': ENERGY, 'eta': ETA, 'phi_rad': PHI}.items():
        if not isinstance(point.get(key), (int, float)) or not math.isclose(point[key], wanted, rel_tol=0, abs_tol=1e-12):
            raise ValueError('Missing/mislabeled validation point: ' + key)
    for key, wanted in {'population': population, 'transport_seed': seed, 'events': n}.items():
        if point.get(key) != wanted:
            raise ValueError('Missing/mislabeled validation point: ' + key)
    if sample.get('events') != n:
        raise ValueError('Primary manifest population differs')
    for filename, digest in GEOMETRY[name].items():
        if sample.get('hashes', {}).get(filename) != digest:
            raise ValueError('Mislabeled or changed geometry: ' + filename)
    if set(proof.get('cells_by_collection', {})) != set(COLLECTIONS[name]):
        raise ValueError('Wrong sensitive collections')
    command = receipt.get('command', [])
    for flag, wanted in (('--physics.list', 'FTFP_BERT'), ('--physics.rangecut', '0.7')):
        if flag not in command or command[command.index(flag) + 1] != wanted:
            raise ValueError('Wrong physics policy: ' + flag)
    if '--random.enableEventSeed' not in command:
        raise ValueError('Per-event random seeding missing')
    workers = proof.get('workers', [])
    if len(workers) != 12 or {w['thread_id'] for w in workers} != set(range(12)) or sum(w['events'] for w in workers) != n:
        raise ValueError('Incomplete worker population')
    roles = ('LArBarrel', 'LArEndcaps') if name == 'lar' else ('BARREL', 'EDGE')
    for worker in workers:
        if (worker.get('status') != 'complete' or worker.get('events', 0) <= 0
                or worker.get('maximum_abs_magnetic_field_tesla') != 0
                or worker.get('begin_run_rng_seed') != seed or worker.get('rng_engine') != 'MixMaxRng'):
            raise ValueError('Wrong native worker status/field/RNG')
        cuts = worker.get('region_cuts', [])
        if not cuts or any(r['mm'] != [.7] * 4 for r in cuts):
            raise ValueError('Wrong native range cuts')
        sensitive = worker.get('sensitive_lar' if name == 'lar' else 'sensitive_si', {})
        if set(sensitive) != set(roles):
            raise ValueError('Wrong native sensitive roles')
        for role in sensitive.values():
            volumes = role.get('volumes', []) if name == 'lar' else [role]
            if not volumes or any(v.get('max_step_mm') is None or not 0 < v['max_step_mm'] <= 5
                                  or v.get('Birks_mm_per_MeV') != 0 for v in volumes):
                raise ValueError('Wrong active step/Birks policy')
    return {'events': n, 'seed': seed,
            'identity': '(detector, population, transport_seed, event); primary four-vectors intentionally identical'}


def load_population(path, name, population, protocol_digest):
    rows, values, evidence = common.load_run(path)
    proof = json.loads((path / 'readback.json').read_text())
    receipt = json.loads((path / 'receipt.json').read_text())
    contract = validate_population(name, population, values, receipt, proof)
    if proof['sample'].get('study_protocol_sha256') != protocol_digest:
        raise ValueError('Input is not bound to the selected study protocol')
    evidence['validation_point'] = proof['sample']['validation_point']
    evidence['study_protocol_sha256'] = protocol_digest
    evidence['readback_audit_sha256'] = proof.get('audit_sha256')
    evidence['geometry_source_manifest_sha256'] = proof['sample'].get('geometry_source_manifest_sha256')
    evidence['contract'] = contract
    evidence['native_audit_scope'] = 'Inherited exact successful native readback; receipt and event ledger rehashed here; raw ROOT not rehashed by this analysis'
    return values[:, 3], portable(evidence)


def scalar_metrics(calibration, evaluation):
    """One response fraction per calibration population, no evaluation recentering."""
    calibration = np.asarray(calibration, dtype=float)
    evaluation = np.asarray(evaluation, dtype=float)
    if min(len(calibration), len(evaluation)) < 2 or not np.isfinite(calibration).all() or not np.isfinite(evaluation).all():
        raise ValueError('Need finite calibration and evaluation populations')
    if np.any(calibration < 0) or np.any(evaluation < 0):
        raise ValueError('Negative active deposits')
    f = float(calibration.mean() / ENERGY)
    mean = float(evaluation.mean())
    if f <= 0 or mean <= 0:
        raise ValueError('Undefined fraction or relative width')
    sd = float(evaluation.std(ddof=1))
    cv = sd / mean
    return dict(zip(METRICS, (f, mean, sd, cv, mean / ENERGY, sd / ENERGY,
                              mean / (ENERGY * f), sd / (ENERGY * f), cv)))


def bootstrap(calibration, evaluation, replicates=1000, seed=5019001):
    """Resample each detector/population independently; one refitted f per draw."""
    if replicates < 2:
        raise ValueError('Need at least two bootstrap replicates')
    streams = np.random.SeedSequence(seed).spawn(4)
    draws = {}
    for model_index, name in enumerate(MODELS):
        cal = np.asarray(calibration[name], dtype=float)
        ev = np.asarray(evaluation[name], dtype=float)
        scalar_metrics(cal, ev)
        cal_rng = np.random.default_rng(streams[2 * model_index])
        ev_rng = np.random.default_rng(streams[2 * model_index + 1])
        values = np.empty((replicates, len(METRICS)))
        for b in range(replicates):
            fitted = cal[cal_rng.integers(len(cal), size=len(cal))]
            heldout = ev[ev_rng.integers(len(ev), size=len(ev))]
            result = scalar_metrics(fitted, heldout)
            values[b] = [result[k] for k in METRICS]
        draws[name] = values
    return draws


def moments(values):
    values = np.asarray(values, dtype=float)
    mean = float(values.mean())
    sd = float(values.std(ddof=1))
    return {'events': len(values), 'mean': mean, 'sample_sd': sd, 'cv': sd / mean,
            'zero_events': int(np.count_nonzero(values == 0)),
            'sum': float(values.sum()), 'sum_of_squares': float(np.square(values).sum()),
            'minimum': float(values.min()), 'maximum': float(values.max()),
            'quantiles': dict(zip(('q01', 'q16', 'q50', 'q84', 'q99'),
                                  map(float, np.quantile(values, [.01, .16, .5, .84, .99]))))}


def histogram(values, edges=None, bins=60):
    values = np.asarray(values, dtype=float)
    if edges is None:
        low, high = float(values.min()), float(values.max())
        if low == high:
            margin = max(abs(low) * .01, 1e-9)
            low, high = low - margin, high + margin
        edges = np.linspace(low, high, bins + 1)
    counts, edges = np.histogram(values, edges)
    return {'edges': edges.tolist(), 'counts': counts.tolist(), 'events': len(values),
            'underflow': int(np.count_nonzero(values < edges[0])),
            'overflow': int(np.count_nonzero(values > edges[-1])),
            'normalization': 'counts / all evaluation events per bin; final upper edge included'}


def summarize(calibration, evaluation, evidence, replicates=1000, seed=5019001):
    draws = bootstrap(calibration, evaluation, replicates, seed)
    models = {}
    corrected = {}
    for name in MODELS:
        metrics = scalar_metrics(calibration[name], evaluation[name])
        corrected[name] = evaluation[name] / (ENERGY * metrics['effective_response_fraction'])
        distributions = {}
        for key, values, unit in (('raw_energy', evaluation[name], 'GeV'),
                                  ('raw_fraction', evaluation[name] / ENERGY, 'dimensionless'),
                                  ('corrected_fraction', corrected[name], 'dimensionless')):
            distributions[key] = {'unit': unit, 'moments': moments(values), 'histogram': histogram(values)}
        intervals = {metric: np.quantile(draws[name][:, i], [.025, .975]).tolist() for i, metric in enumerate(METRICS)}
        models[name] = {'label': LABELS[name], 'evidence': evidence.get(name, {}),
                        'calibration': {'events': len(calibration[name]),
                                        'effective_response_fraction': metrics['effective_response_fraction'],
                                        'fraction_ci95': intervals['effective_response_fraction'],
                                        'raw_moments': moments(calibration[name]),
                                        'interpretation': 'Independent mean(S/50); effective visible response including containment/dead-material losses, not pure material sampling fraction'},
                        'metrics': metrics, 'metric_ci95': intervals, 'distributions': distributions}
        a, b = distributions['raw_energy']['moments'], distributions['corrected_fraction']['moments']
        if not math.isclose(a['cv'], b['cv'], rel_tol=3e-14, abs_tol=1e-15):
            raise ValueError('Constant response scaling changed CV')
    low = min(float(v.min()) for v in corrected.values())
    high = max(float(v.max()) for v in corrected.values())
    if low == high:
        low, high = low - .01, high + .01
    common_edges = np.linspace(low, high, 81)
    for name in MODELS:
        models[name]['corrected_overlay_histogram'] = histogram(corrected[name], common_edges)
    order = [name + ':' + metric for name in MODELS for metric in METRICS]
    matrix = np.concatenate([draws[name] for name in MODELS], axis=1)
    contrasts = {}
    for metric in ('corrected_fraction_sd', 'raw_energy_cv'):
        i = METRICS.index(metric)
        contrasts['siw_minus_lar:' + metric] = {
            'value': models['siw']['metrics'][metric] - models['lar']['metrics'][metric],
            'ci95': np.quantile(draws['siw'][:, i] - draws['lar'][:, i], [.025, .975]).tolist()}
    return {'status': 'PROTOTYPE', 'validation_point': {'energy_GeV': ENERGY, 'eta': ETA, 'phi_rad': PHI, 'phi_deg': .7},
            'interpretation': 'Fixed-direction active-deposit response; no digitization, noise, Gaussian fit or tail selection. Constant correction leaves SD/mean invariant.',
            'definitions': {'S': 'sum of all raw active ECAL Geant4 hit energy deposits',
                            'R': 'S / 50 GeV', 'f': 'mean_calibration(S / 50 GeV)', 'T': 'S / (f * 50 GeV)',
                            'raw_fraction_sd': 'SD(S)/50 = SD(R)',
                            'corrected_fraction_sd': 'SD(T) = SD(S)/(50*f)',
                            'cv': 'sample SD / sample mean; identical for S, R and T',
                            'sampling_scope': 'f is an effective visible response fraction, not separately scored active/(active+passive) deposition'},
            'bootstrap': {'replicates': replicates, 'seed': seed,
                          'resampling': 'Independent whole-event resampling for each detector and each calibration/evaluation population; one common refitted f per replicate, not per-event smearing',
                          'intervals': 'pointwise 95% percentile, conditional on saved geometry/physics/transport; no systematic coverage',
                          'rng': 'NumPy SeedSequence(seed).spawn(4), ordered lar-cal, lar-eval, siw-cal, siw-eval'},
            'models': models, 'contrasts': contrasts,
            'metric_covariance': {'order': order, 'units': 'product of named metric units; energy entries in GeV, all others dimensionless',
                                  'matrix': np.cov(matrix, rowvar=False, ddof=1).tolist()}}


def analyze(runs, output, replicates=1000, seed=5019001, protocol=None):
    protocol = protocol or ROOT / 'docs/validation/ecal50gev-central/protocol.json'
    protocol_digest = common.sha(protocol)
    calibration, evaluation, evidence = {}, {}, {}
    for name in MODELS:
        evidence[name] = {}
        for population, destination in (('calibration', calibration), ('evaluation', evaluation)):
            destination[name], evidence[name][population] = load_population(runs / population / name, name, population, protocol_digest)
    # Primary four-vectors coincide by design; distinct seed/population keys,
    # not identical input momentum bytes, establish independent populations.
    result = summarize(calibration, evaluation, evidence, replicates, seed)
    result.update(source_revision=subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                  analysis_sha256=common.sha(__file__), helper_sha256=common.sha(common.__file__),
                  protocol_sha256=protocol_digest, numpy_version=np.__version__)
    output.mkdir(parents=True, exist_ok=False)
    common.write(output / 'summary.json', result)
    print(json.dumps({name: model['metrics'] for name, model in result['models'].items()}, indent=2))


def plot(summary, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    result = json.loads(summary.read_text())
    output.mkdir(parents=True, exist_ok=True)
    styles = {'lar': '-', 'siw': ':'}
    columns = [('raw_energy', 'Raw active deposited energy', r'$S=\sum E_{\rm dep,active}$ [GeV]'),
               ('raw_fraction', 'Raw deposited-energy fraction', r'$R=S/E_0$'),
               ('corrected_fraction', 'Response-fraction corrected', r'$T=S/(f E_0)$')]
    with plt.rc_context({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'nodd-ecal50gev-central', 'pdf.fonttype': 42}):
        def export(fig, stem):
            for ext in ('png', 'pdf', 'svg'):
                path = output / f'{stem}.{ext}'
                metadata = {'CreationDate': None, 'ModDate': None} if ext == 'pdf' else {'Date': None} if ext == 'svg' else {}
                fig.savefig(path, dpi=180, facecolor='white', metadata=metadata)
                if ext == 'svg':
                    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
            plt.close(fig)
        fig, axes = plt.subplots(2, 3, figsize=(14, 8))
        fig.subplots_adjust(left=.07, right=.985, bottom=.17, top=.80, wspace=.24, hspace=.40)
        fig.suptitle('50 GeV electrons: raw deposits and sampling response', x=.07, y=.975, ha='left', fontsize=18, weight='bold')
        fig.text(.07, .915, r'$\eta=0.1$, $\phi=+0.7^\circ$ · ECAL only, $B=0$ · 10,000 evaluation + 2,000 independent calibration events per detector', fontsize=10.5)
        fig.text(.07, .865, 'Active silicon / LAr energy deposits before digitization · all events and tails retained', color='#555555')
        for row, name in enumerate(MODELS):
            model = result['models'][name]
            for col, (key, title, label) in enumerate(columns):
                ax = axes[row, col]
                distribution = model['distributions'][key]
                hist = distribution['histogram']; moment = distribution['moments']
                heights = np.array(hist['counts']) / hist['events']
                ax.stairs(heights, hist['edges'], color='#cccc00', linestyle=styles[name], linewidth=2.2)
                ax.set_xlim(hist['edges'][0], hist['edges'][-1])
                ax.set_ylim(0, max(float(heights.max()) * 1.4, .01))
                ax.set_xlabel(label)
                ax.set_title(title if row == 0 else '', fontsize=11, pad=12)
                ax.xaxis.set_major_locator(MaxNLocator(5))
                ax.ticklabel_format(axis='x', style='sci', scilimits=(-2, 3), useMathText=True)
                ax.grid(axis='y', alpha=.17); ax.set_axisbelow(True)
                annotation = f"mean = {moment['mean']:.5g}\nSD = {moment['sample_sd']:.4g}\nSD/mean = {100 * moment['cv']:.3f}%"
                ax.text(.025, .96, annotation, transform=ax.transAxes, va='top', fontsize=9,
                        bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .85, 'pad': 2})
                if col == 0:
                    ax.set_ylabel(f"{LABELS[name]}\nFraction of evaluation events / bin", fontsize=9)
                if key == 'corrected_fraction':
                    ax.axvline(1, color='#888888', linewidth=.8, linestyle='--', zorder=0)
                    ax.text(.98, .96, f"f = {model['calibration']['effective_response_fraction']:.5g}",
                            transform=ax.transAxes, va='top', ha='right', fontsize=9)
        fig.text(.07, .065, r'$f=\langle S/E_0\rangle_{\rm independent\ calibration}$ includes containment and dead-material losses; it is an effective visible response fraction.', fontsize=10)
        fig.text(.07, .025, 'A constant 1/f correction changes scale and SD(R), but leaves SD/mean exactly unchanged. Evaluation events are not recentered.', fontsize=9, color='#555555')
        export(fig, 'central-response-distributions')
        fig, ax = plt.subplots(figsize=(9, 5.5))
        fig.subplots_adjust(left=.10, right=.98, bottom=.23, top=.80)
        maximum_height = 0
        for name in MODELS:
            model = result['models'][name]; hist = model['corrected_overlay_histogram']
            sd = model['metrics']['corrected_fraction_sd']; interval = model['metric_ci95']['corrected_fraction_sd']
            label = f"{LABELS[name]}: SD(T) = {100*sd:.3f}% [{100*interval[0]:.3f}, {100*interval[1]:.3f}]"
            ax.stairs(np.array(hist['counts']) / hist['events'], hist['edges'], color='#cccc00',
                      linestyle=styles[name], linewidth=2.4, label=label)
            maximum_height = max(maximum_height, float(np.max(hist['counts'])) / hist['events'])
        ax.set_ylim(0, maximum_height * 1.3)
        ax.axvline(1, color='#888888', linewidth=.8, linestyle='--', zorder=0)
        ax.set_xlabel(r'Corrected response $T=S/(f E_0)$'); ax.set_ylabel('Fraction of evaluation events / common bin')
        ax.grid(axis='y', alpha=.18); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=9)
        fig.suptitle('Held-out response after the sampling-response correction', x=.10, y=.97, ha='left', fontsize=15, weight='bold')
        fig.text(.10, .86, r'50 GeV electrons · $\eta=0.1$, $\phi=+0.7^\circ$ · 10,000 events per detector · ECAL only, $B=0$', fontsize=10)
        fig.text(.10, .105, 'Intervals: pointwise 95% independent calibration/evaluation bootstrap, including refitted f.', fontsize=9)
        fig.text(.10, .055, 'Effective f includes containment/dead material; all zeros and tails retained. Constant scaling preserves SD/mean.', fontsize=8.8, color='#555555')
        export(fig, 'central-corrected-comparison')
    common.write(output / 'render.json', {'summary_sha256': common.sha(summary), 'plotter_sha256': common.sha(__file__),
                 'numpy_version': np.__version__, 'matplotlib_version': matplotlib.__version__,
                 'figures': {p.name: common.sha(p) for p in sorted(output.iterdir()) if p.suffix in ('.png', '.pdf', '.svg')}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('analyze')
    p.add_argument('--runs', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--bootstrap', type=int, default=1000); p.add_argument('--seed', type=int, default=5019001)
    p.add_argument('--protocol', type=Path, default=ROOT / 'docs/validation/ecal50gev-central/protocol.json')
    p = sub.add_parser('plot')
    p.add_argument('--summary', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'analyze':
        analyze(args.runs, args.output, args.bootstrap, args.seed, args.protocol)
    else:
        plot(args.summary, args.output)


if __name__ == '__main__':
    main()
