"""Frozen matched-primary old/compact LAr response controls (PROTOTYPE).

Widths describe raw deposits, including zeros and geometry/material effects.
They are not intrinsic reconstructed resolution or a noninferiority decision.
Full event data remain local; the output retains aggregate statistics only.
"""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess

import numpy as np
import compare as common

MODELS = ('reference', 'candidate')
AXES = common.AXES
PERIOD = common.PERIOD


def finite(value):
    return float(value) if np.isfinite(value) else None


def moments(values):
    """Keep empty/all-zero populations and state undefined widths explicitly."""
    values = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(values)) or np.any(values < 0):
        raise ValueError('Invalid response values')
    n = len(values)
    mean = float(values.mean()) if n else None
    sd = float(values.std(ddof=1)) if n > 1 else None
    quantiles = dict(zip(('q01', 'q16', 'q50', 'q84', 'q99'),
                         map(float, np.quantile(values, [.01, .16, .5, .84, .99])))) if n else None
    below = int(np.count_nonzero(values < .5 * mean)) if n else 0
    return dict(events=n, mean_response=mean, sample_sd=sd,
                fractional_width=sd / mean if sd is not None and mean > 0 else None,
                width_status='defined' if n > 1 and mean > 0 else 'undefined: fewer than two events or zero mean',
                zero_events=int(np.count_nonzero(values == 0)),
                below_half_mean_events=below, below_half_mean_fraction=below / n if n else None,
                central_quantile_width=(quantiles['q84'] - quantiles['q16']) / (2 * quantiles['q50'])
                if quantiles and quantiles['q50'] > 0 else None, quantiles=quantiles)


def validate_pair(loaded, contract, expected_events=10000):
    """Bind labels to frozen compacts/materials and identical primary illumination."""
    for key in ('reference_compact_sha256', 'candidate_compact_sha256',
                'reference_materials_sha256', 'candidate_materials_sha256',
                'input_sha256', 'truth_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', contract.get(key, '')):
            raise ValueError('Missing or invalid frozen hash: ' + key)
    if contract['reference_compact_sha256'] == contract['candidate_compact_sha256']:
        raise ValueError('Reference and candidate compacts must be distinct')
    base = loaded['reference'][1]
    if base.shape != (expected_events, 5):
        raise ValueError('This protocol requires exactly 10,000 complete primary rows')
    for name in MODELS:
        rows, values, evidence = loaded[name]
        if values.shape != base.shape or not np.allclose(values[:, :3], base[:, :3], rtol=0, atol=1e-9):
            raise ValueError('Unmatched primary illumination: ' + name)
        if [r['event'] for r in rows] != list(range(expected_events)):
            raise ValueError('Noncontiguous, missing or duplicate event IDs: ' + name)
        sample = evidence['input']
        for key in ('input_sha256', 'truth_sha256'):
            if sample.get(key) != contract[key]:
                raise ValueError('Primary bytes differ from frozen protocol: ' + key)
        if sample.get('hashes', {}).get('detector.xml') != contract[name + '_compact_sha256']:
            raise ValueError('Mislabeled or changed geometry: ' + name)
        if sample.get('hashes', {}).get('materials.xml') != contract[name + '_materials_sha256']:
            raise ValueError('Mislabeled or changed materials: ' + name)
        if sample.get('hashes', {}).get('particles.HEPEvt') != contract['input_sha256'] or sample.get('hashes', {}).get('truth-input.jsonl') != contract['truth_sha256']:
            raise ValueError('Primary manifest hashes disagree: ' + name)
    a, b = (loaded[name][2]['input'] for name in MODELS)
    if not a.get('source_primary_manifest_sha256') or a['source_primary_manifest_sha256'] != b.get('source_primary_manifest_sha256'):
        raise ValueError('Different source primary manifests')
    bounds = contract.get('transition_union_abs_eta')
    if not isinstance(bounds, list) or len(bounds) != 2 or not 0 <= bounds[0] < bounds[1] <= 3:
        raise ValueError('Need prospective common transition-union bounds inside [0,3]')


def validate_maps(run, name, contract):
    """Check serial initialization against independently frozen raw ID counts."""
    run = Path(run)
    proof = json.loads((run / 'readback.json').read_text())
    receipt = json.loads((run / 'receipt.json').read_text())
    path = run / 'audit/maps-initialized.json'
    maps = json.loads(path.read_text())
    expected = contract.get(name + '_raw_sensitive_ids')
    if type(expected) is not int or expected <= 0:
        raise ValueError('Need frozen positive raw-sensitive count: ' + name)
    digest = common.sha(path)
    if (maps.get('status') != 'PASS' or maps.get('thread_id', 0) >= 0 or
            maps.get('raw_sensitive_ids') != expected or maps.get('native_contexts_checked') != expected or
            receipt.get('maps_audit_sha256') != digest or proof.get('maps_audit_sha256') != digest or
            proof.get('maps_audit') != maps):
        raise ValueError('Unbound or incomplete serial native map initialization: ' + name)
    return dict(status='PASS', raw_sensitive_ids=expected, maps_sha256=digest)


def projections(values, contract):
    n = len(values)
    abs_eta = np.abs(values[:, 1])
    coords = dict(abs_eta=abs_eta, broad_eta=abs_eta, signed_eta=values[:, 1], energy=values[:, 0],
                  full_phi=values[:, 2], siw_folded_phi=(values[:, 2] + PERIOD / 2) % PERIOD - PERIOD / 2)
    cats = {'global': np.zeros(n, dtype=int)}
    meta = {'global': dict(bins=1, labels=['all primaries'])}
    for axis, edges in AXES.items():
        cats[axis] = common.index(coords[axis], edges)
        meta[axis] = dict(bins=len(edges)-1, edges=edges.tolist(),
                          unit='GeV' if axis == 'energy' else 'rad' if 'phi' in axis else 'dimensionless')
    cats['broad_eta_energy'] = cats['broad_eta'] * 14 + cats['energy']
    meta['broad_eta_energy'] = dict(bins=42, energy_edges=AXES['energy'].tolist(),
                                   abs_eta_edges=AXES['broad_eta'].tolist(),
                                   ordering='broad eta region first, energy bin second')
    lo, hi = contract['transition_union_abs_eta']
    cats['transition_union'] = ((abs_eta >= lo) & (abs_eta <= hi)).astype(int)
    meta['transition_union'] = dict(bins=2, labels=['outside union', 'inside union'], abs_eta_interval=[lo, hi],
                                    boundary='inside includes both interval endpoints')
    return cats, meta


def geometry_migration(abs_eta, contract):
    """Classify from frozen geometric-envelope limits, never observed response."""
    specs = contract.get('geometry_transition')
    if specs is None:
        return dict(status='NOT PROVIDED', limitation='No geometric classification input; no migration inferred from response.')
    labels = ['full_barrel', 'full_endcap', 'partial_depth', 'no_sampling_envelope']
    classes = {}
    for name in MODELS:
        p = specs[name]
        for key in ('barrel_full_eta', 'barrel_any_eta', 'endcap_any_eta', 'endcap_full_eta'):
            if not np.isfinite(p[key]) or not 0 <= p[key] <= 3:
                raise ValueError('Invalid geometric envelope boundary')
        if p['barrel_full_eta'] > p['barrel_any_eta'] or p['endcap_any_eta'] > p['endcap_full_eta']:
            raise ValueError('Inverted full/any sampling boundary')
        full_barrel = abs_eta <= p['barrel_full_eta']
        full_endcap = abs_eta >= p['endcap_full_eta']
        any_sampling = (abs_eta <= p['barrel_any_eta']) | (abs_eta >= p['endcap_any_eta'])
        classes[name] = np.select([full_barrel, full_endcap, any_sampling], [0, 1, 2], default=3)
    counts = np.bincount(classes['reference'] * 4 + classes['candidate'], minlength=16).reshape(4, 4)
    return dict(status='PROVIDED', source=contract.get('geometry_transition_source', 'Frozen model envelope limits'),
                interpretation='Envelope path classes only; not native sampling X0, active-cell efficiency or response classification.',
                labels=labels, row_model='reference', column_model='candidate', counts=counts.tolist(),
                events=int(counts.sum()), boundaries=specs)


def covariance(columns, order):
    """Use all shared replicates; undefined columns stay null, never pairwise dropped."""
    matrix = np.array(columns)
    defined = np.all(np.isfinite(matrix), axis=1)
    cov = np.full((len(order), len(order)), np.nan)
    if np.any(defined):
        cov[np.ix_(defined, defined)] = np.atleast_2d(np.cov(matrix[defined], ddof=1))
    return dict(order=order, matrix=[[finite(x) for x in row] for row in cov],
                undefined_replicates=[int(np.count_nonzero(~np.isfinite(row))) for row in matrix],
                replicates=int(matrix.shape[1]),
                rule='All shared whole-event replicates; any undefined column has null covariance row/column. No pairwise deletion.')


def histogram(values, mean):
    raw_edges = np.linspace(0., .4, 121)
    def record(data, edges):
        return dict(edges=edges.tolist(), counts=np.histogram(data, edges)[0].tolist(), events=len(data),
                    underflow=int(np.count_nonzero(data < edges[0])), overflow=int(np.count_nonzero(data > edges[-1])))
    raw = record(values, raw_edges)
    norm = record(values / mean, np.linspace(0, 3, 121)) if mean and mean > 0 else None
    if norm is not None:
        norm['normalization'] = 'R / own inclusive mean(R); diagnostic display, no fitted calibration'
    return raw, norm


def summarize(loaded, contract, bootstrap=1000, seed=13001000):
    if bootstrap < 2:
        raise ValueError('At least two bootstrap replicates required')
    base = loaded['reference'][1]
    n = len(base)
    cats, meta = projections(base, contract)
    responses = {name: loaded[name][1][:, 4] for name in MODELS}
    boot = {name: {axis: np.empty((bootstrap, item['bins'], 2)) for axis, item in meta.items()} for name in MODELS}
    rng = np.random.default_rng(seed)
    for b in range(bootstrap):
        weights = np.bincount(rng.integers(n, size=n), minlength=n)
        for name, response in responses.items():
            for axis, cat in cats.items():
                mean, width = common.binned_moments(response, cat, weights, meta[axis]['bins'])
                boot[name][axis][b, :, 0] = mean
                boot[name][axis][b, :, 1] = width
    models = {}
    for name, response in responses.items():
        own_mean = float(response.mean())
        model = dict(label=contract.get(name + '_label', 'Original LAr' if name == 'reference' else 'Compact LAr'),
                     evidence=loaded[name][2], projections={})
        for axis, cat in cats.items():
            rows = []
            for i in range(meta[axis]['bins']):
                row = moments(response[cat == i])
                for j, field in enumerate(('mean_response', 'fractional_width')):
                    row[field + '_bootstrap'] = common.interval(boot[name][axis][:, i, j])
                row['response_uniformity'] = row['mean_response'] / own_mean if row['mean_response'] is not None and own_mean > 0 else None
                uniform = np.divide(boot[name][axis][:, i, 0], boot[name]['global'][:, 0, 0],
                                    out=np.full(bootstrap, np.nan), where=boot[name]['global'][:, 0, 0] > 0)
                row['response_uniformity_bootstrap'] = common.interval(uniform)
                if axis in ('global', 'abs_eta', 'siw_folded_phi', 'transition_union'):
                    row['raw_response_histogram'], row['normalized_response_histogram'] = histogram(response[cat == i], own_mean)
                rows.append(row)
            if axis == 'global':
                model['global'] = rows[0]
            else:
                model['projections'][axis] = dict(meta[axis], bins=rows)
        models[name] = model
    contrasts = {}
    for axis in cats:
        diffs = boot['candidate'][axis][:, :, 1] - boot['reference'][axis][:, :, 1]
        rows = []
        for i in range(meta[axis]['bins']):
            old = models['reference']['global'] if axis == 'global' else models['reference']['projections'][axis]['bins'][i]
            new = models['candidate']['global'] if axis == 'global' else models['candidate']['projections'][axis]['bins'][i]
            a, b = new['fractional_width'], old['fractional_width']
            rows.append(dict(difference=a-b if a is not None and b is not None else None,
                             events=old['events'], **common.interval(diffs[:, i])))
        contrasts[axis] = rows
    order, columns, contrast_order, contrast_columns = [], [], [], []
    for name in MODELS:
        for axis, item in meta.items():
            for i in range(item['bins']):
                order.append(f'{name}:{axis}:{i}')
                columns.append(boot[name][axis][:, i, 1])
    for axis, item in meta.items():
        for i in range(item['bins']):
            contrast_order.append(f'candidate_minus_reference:{axis}:{i}')
            contrast_columns.append(boot['candidate'][axis][:, i, 1] - boot['reference'][axis][:, i, 1])
    return dict(status='PROTOTYPE', events=n,
                observable='R=active ECAL deposited energy / primary total energy; sample SD(R)/mean(R)',
                interpretation='Raw spectrum-averaged response including zeros and geometry/material/leakage effects. No intrinsic-resolution, digitization or noninferiority claim.',
                contract=contract, bootstrap=dict(replicates=bootstrap, seed=seed, resampling='Shared whole-primary-event multiplicities across both geometries and every projection', intervals='Pointwise 95% percentile; any undefined replicate gives null bounds', noninferiority_margin=None),
                models=models, candidate_minus_reference=contrasts,
                width_covariance=covariance(columns, order), contrast_covariance=covariance(contrast_columns, contrast_order),
                geometry_migration=geometry_migration(np.abs(base[:, 1]), contract))


def analyze(args):
    contract = json.loads(args.contract.read_text())
    paths = dict(reference=args.reference_run, candidate=args.candidate_run)
    loaded = {name: common.load_run(path) for name, path in paths.items()}
    validate_pair(loaded, contract)
    checks = {name: dict(transport=common.validate_contract(path, 'lar'), maps=validate_maps(path, name, contract)) for name, path in paths.items()}
    result = summarize(loaded, contract, args.bootstrap, args.seed)
    result.update(source_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=Path(__file__).resolve().parents[3], text=True).strip(),
                  analysis_sha256=common.sha(__file__), helper_sha256=common.sha(common.__file__), contract_sha256=common.sha(args.contract), native_contract_checks=checks)
    args.output.mkdir(parents=True, exist_ok=False)
    common.write(args.output / 'summary.json', result)
    print(json.dumps({name: {k: v for k, v in result['models'][name]['global'].items() if 'histogram' not in k} for name in MODELS}, indent=2))
    print('Candidate minus reference:', json.dumps(result['candidate_minus_reference']['global']))


def plot(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    result = json.loads(args.summary.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'svg.hashsalt': 'nodd-lar-compact-v1'})
    styles = dict(reference=dict(color='#dada66', ls='--', marker='s', markeredgecolor='#555555'),
                  candidate=dict(color='#cccc00', ls='-', marker='o', markeredgecolor='#333333'))
    labels = dict(abs_eta='|η|', siw_folded_phi='φ folded with legacy Si–W sector period [rad]',
                  energy='Primary total energy [GeV]', full_phi='φ [rad]', signed_eta='η')
    exports = []
    def export(fig, name):
        fig.text(.02, .012, 'PROTOTYPE · matched 10k electrons · E=10–80 GeV, η=−3…3 · ECAL-only B=0 · raw deposits; no digitization', fontsize=8)
        fig.tight_layout(rect=(0, .045, 1, .94))
        for ext in ('png', 'pdf', 'svg'):
            p = args.output / f'{name}.{ext}'
            fig.savefig(p, dpi=160, metadata={'CreationDate': None, 'ModDate': None} if ext == 'pdf' else {'Date': None} if ext == 'svg' else {})
            exports.append(p)
        plt.close(fig)
    def draw(ax, axis, field, region=None):
        for name in MODELS:
            model = result['models'][name]
            proj = model['projections'][axis]
            if axis == 'broad_eta_energy':
                edges = np.array(proj['energy_edges']); rows = proj['bins'][14*region:14*(region+1)]
            else:
                edges = np.array(proj['edges']); rows = proj['bins']
            x = (edges[:-1]+edges[1:])/2
            scale = 100 if field in ('fractional_width', 'below_half_mean_fraction') else 1
            y = np.array([r[field] if r[field] is not None else np.nan for r in rows]) * scale
            err = np.zeros((2, len(y)))
            if field != 'below_half_mean_fraction':
                for i, row in enumerate(rows):
                    ci = row[field + '_bootstrap']['ci95']
                    err[:, i] = np.maximum([y[i]-ci[0]*scale, ci[1]*scale-y[i]], 0) if ci else np.nan
            ax.errorbar(x, y, yerr=err, label=model['label'], capsize=2, markersize=4, **styles[name])
        ax.grid(alpha=.22)
        ax.set_xlabel(labels.get(axis, 'Primary total energy [GeV]'))
        ax.set_ylabel({'fractional_width':'SD(R) / mean(R) [%]', 'response_uniformity':'Mean R / own inclusive mean R',
                       'mean_response':'Mean active deposited fraction', 'below_half_mean_fraction':"Below half the bin's own mean R [%]"}[field])
    for field, title, stem in [('fractional_width', 'Raw response widths · pointwise 95% intervals', 'angular-comparison'),
                               ('response_uniformity', 'Directional response uniformity', 'angular-means'),
                               ('below_half_mean_fraction', 'Low-response tails · descriptive bin-dependent thresholds', 'angular-tails')]:
        fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
        for ax, axis in zip(axs, ('abs_eta', 'siw_folded_phi')): draw(ax, axis, field)
        axs[0].legend(); fig.suptitle(title); export(fig, stem)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
    draw(axs[0], 'energy', 'fractional_width'); draw(axs[1], 'energy', 'mean_response')
    axs[0].legend(); fig.suptitle('Energy controls · directions remain mixed within each energy slice'); export(fig, 'energy-controls')
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.7))
    for i, ax in enumerate(axs):
        draw(ax, 'broad_eta_energy', 'fractional_width', i); ax.set_title(f'{AXES["broad_eta"][i]:g} ≤ |η| < {AXES["broad_eta"][i+1]:g}')
    axs[0].legend(); fig.suptitle('Energy-conditioned widths in fixed broad angular regions'); export(fig, 'energy-by-region')
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    for i, axis in enumerate(('signed_eta', 'full_phi')):
        draw(axs[0, i], axis, 'fractional_width'); draw(axs[1, i], axis, 'response_uniformity')
    axs[0, 0].legend(); fig.suptitle('Signed direction and absolute azimuth controls'); export(fig, 'direction-controls')
    def distribution(ax, rows, normalized=True):
        for name, row in zip(MODELS, rows):
            hist = row['normalized_response_histogram' if normalized else 'raw_response_histogram']
            if hist is None or not hist['events']: continue
            style = {k: v for k, v in styles[name].items() if k in ('color', 'ls')}
            ax.stairs(np.array(hist['counts']) / hist['events'], hist['edges'], label=result['models'][name]['label'], **style)
        ax.set_yscale('log'); ax.grid(alpha=.2)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
    rows = [result['models'][n]['global'] for n in MODELS]
    distribution(axs[0], rows, False); distribution(axs[1], rows)
    axs[0].set_xlabel('Raw R'); axs[1].set_xlabel('R / own inclusive mean(R)')
    for ax in axs: ax.set_ylabel('Fraction of all generated events / bin')
    axs[0].legend(); fig.suptitle('Underlying raw response distributions · zero events retained'); export(fig, 'response-distributions')
    for axis in ('abs_eta', 'siw_folded_phi'):
        fig, axs = plt.subplots(2, 5, figsize=(16, 7), sharex=True, sharey=True)
        edges = result['models']['reference']['projections'][axis]['edges']
        for i, ax in enumerate(axs.flat):
            rows = [result['models'][n]['projections'][axis]['bins'][i] for n in MODELS]
            distribution(ax, rows); ax.set_title(f'{edges[i]:.3f}…{edges[i+1]:.3f} (n={rows[0]["events"]})')
        axs.flat[0].legend(fontsize=8)
        fig.supxlabel('R / own inclusive mean(R)', y=.055)
        fig.supylabel('Fraction of angular-bin events / response bin')
        fig.suptitle('Underlying distributions: ' + labels[axis]); export(fig, 'distributions-' + axis)
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
    for ax, axis in zip(axs, ('abs_eta', 'siw_folded_phi', 'energy')):
        edges = np.array(result['models']['reference']['projections'][axis]['edges']); x = (edges[:-1]+edges[1:])/2
        rows = result['candidate_minus_reference'][axis]
        y = np.array([r['difference'] if r['difference'] is not None else np.nan for r in rows]) * 100
        err = np.array([[max(0, y[i]-r['ci95'][0]*100), max(0, r['ci95'][1]*100-y[i])] if r['ci95'] else [np.nan, np.nan] for i, r in enumerate(rows)]).T
        ax.errorbar(x, y, yerr=err, color='#cccc00', marker='o', markeredgecolor='#333333', capsize=2)
        ax.axhline(0, color='#777777', lw=1); ax.grid(alpha=.22); ax.set_xlabel(labels[axis]); ax.set_ylabel('Compact − original width [percentage points]')
    fig.suptitle('Paired width contrasts · pointwise 95% intervals; no acceptance margin'); export(fig, 'paired-width-difference')
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8))
    rows = [result['models'][n]['projections']['transition_union']['bins'][1] for n in MODELS]
    distribution(axs[0], rows); axs[0].legend(fontsize=8); axs[0].set_xlabel('R / own inclusive mean(R)'); axs[0].set_ylabel('Fraction of union events / bin')
    bounds = result['contract']['transition_union_abs_eta']; axs[0].set_title(f'Common partial-depth union: {bounds[0]:.4f} ≤ |η| ≤ {bounds[1]:.4f}')
    migration = result['geometry_migration']
    if migration['status'] == 'PROVIDED':
        matrix = np.array(migration['counts'])
        axs[1].imshow(matrix, cmap=LinearSegmentedColormap.from_list('ECAL', ['#ffffff', '#cccc00']), vmin=0)
        for i in range(4):
            for j in range(4): axs[1].text(j, i, str(matrix[i, j]), ha='center', va='center')
        tick = ['Full barrel', 'Full endcap', 'Partial depth', 'No envelope']
        axs[1].set_xticks(range(4), tick, rotation=25, ha='right'); axs[1].set_yticks(range(4), tick)
        axs[1].set_xlabel('Compact envelope class'); axs[1].set_ylabel('Original envelope class'); axs[1].set_title('Same-primary geometric migration counts')
    else:
        axs[1].text(.5, .5, 'Geometric migration input not provided', ha='center'); axs[1].set_axis_off()
    fig.suptitle('Transition controls · envelope classifications do not measure sampling X₀'); export(fig, 'transition-controls')
    common.write(args.output / 'render.json', dict(summary_sha256=common.sha(args.summary), plotter_sha256=common.sha(__file__),
                 matplotlib_version=matplotlib.__version__, figures={p.name: common.sha(p) for p in exports}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('analyze')
    for name in ('reference-run', 'candidate-run', 'contract', 'output'):
        a.add_argument('--' + name, type=Path, required=True)
    a.add_argument('--bootstrap', type=int, default=1000); a.add_argument('--seed', type=int, default=13001000)
    a = sub.add_parser('plot'); a.add_argument('--summary', type=Path, required=True); a.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    analyze(args) if args.command == 'analyze' else plot(args)


if __name__ == '__main__':
    main()
