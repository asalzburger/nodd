"""Exploratory secondary held-out eta-only gain diagnostic, not reconstruction.

Train forward mean(S/Etrue) on other folds; apply Ehat=S/gain(eta) without a
true-energy input. Raw comparison remains primary. No event payload is exported.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

import numpy as np
import compact_compare as pair

MODELS = pair.MODELS
ETA_EDGES = np.linspace(0., 3., 61)
FOLDS = 5
FOLD_SEED = 14865017
BOOTSTRAPS = 1000
BOOTSTRAP_SEED = 14865018
ALGORITHM = 'forward-mean-R-60-abseta-bins-v1'
ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / 'docs/validation/lar-compact/calibration-protocol.md'


class InvalidTrainingGain(ValueError):
    """A gain is undefined; bootstrap retains rather than redraws this replicate."""


def ids_hash(ids):
    return hashlib.sha256(np.asarray(sorted(map(int, ids)), dtype='<u8').tobytes()).hexdigest()


def make_folds(ids):
    """Sort IDs, permute their positions, partition into five balanced blocks."""
    ids = np.asarray(ids)
    if ids.ndim != 1 or len(ids) < FOLDS or len(np.unique(ids)) != len(ids) or np.any(ids < 0) or not np.all(ids == ids.astype(np.int64)):
        raise ValueError('Need unique nonnegative integer primary IDs')
    order = np.random.default_rng(FOLD_SEED).permutation(np.argsort(ids))
    folds = np.empty(len(ids), dtype=int)
    folds[order] = np.arange(len(ids)) * FOLDS // len(ids)
    return folds


def eta_bins(eta):
    eta = np.asarray(eta, dtype=float)
    if eta.ndim != 1 or not np.all(np.isfinite(eta)):
        raise ValueError('Invalid eta feature')
    return pair.common.index(np.abs(eta), ETA_EDGES)


def checked_weights(weights, n):
    out = np.ones(n, dtype=np.int64) if weights is None else np.asarray(weights)
    if out.shape != (n,) or not np.all(np.isfinite(out)) or np.any(out < 0) or not np.all(out == out.astype(np.int64)):
        raise ValueError('Invalid primary multiplicities')
    return out.astype(np.int64)


def fit_gain(response, eta, ids, scope, weights=None, kind='training-fit'):
    """Fit the forward response mean, retaining zeros in training denominators."""
    response = np.asarray(response, dtype=float)
    bins = eta_bins(eta)
    if response.shape != bins.shape or len(ids) != len(bins) or not np.all(np.isfinite(response)) or np.any(response < 0):
        raise ValueError('Invalid training response')
    weights = checked_weights(weights, len(response))
    counts = np.bincount(bins, weights=weights, minlength=60)
    sums = np.bincount(bins, weights=weights * response, minlength=60)
    if np.any(counts <= 0):
        raise InvalidTrainingGain('Missing training population in eta bins ' + str(np.flatnonzero(counts <= 0).tolist()))
    gains = sums / counts
    if not np.all(np.isfinite(gains)) or np.any(gains <= 0):
        raise InvalidTrainingGain('Nonpositive or nonfinite trained gain')
    return dict(algorithm=ALGORITHM, kind=kind, scope=scope, eta_edges=ETA_EDGES.tolist(),
                gains=gains.tolist(), training_bin_multiplicities=counts.astype(int).tolist(),
                training_multiplicity_total=int(weights.sum()),
                training_unique_positive_weight=int(np.count_nonzero(weights)),
                training_primary_ids_sha256=ids_hash(ids),
                gain_definition='Weighted mean of S/Etrue in each training eta bin; zeros included',
                application='Ehat_GeV = signal_GeV / gain(abs_eta); true energy is not an application input')


def apply_calibration(model, signal_GeV, eta, geometry):
    """Reusable application interface: signal, eta, matching geometry; no true E."""
    for key in ('compact_sha256', 'materials_sha256'):
        if not re.fullmatch('[0-9a-f]{64}', geometry.get(key, '')) or model.get('scope', {}).get(key) != geometry[key]:
            raise ValueError('Calibration geometry/material scope mismatch: ' + key)
    if model.get('algorithm') != ALGORITHM or model.get('eta_edges') != ETA_EDGES.tolist():
        raise ValueError('Unsupported calibration algorithm/binning')
    gains = np.asarray(model.get('gains'), dtype=float)
    if gains.shape != (60,) or not np.all(np.isfinite(gains)) or np.any(gains <= 0):
        raise ValueError('Invalid calibrated gains')
    signals = np.asarray(signal_GeV, dtype=float)
    bins = eta_bins(eta)
    if signals.shape != bins.shape or not np.all(np.isfinite(signals)) or np.any(signals < 0):
        raise ValueError('Invalid signal application input')
    return signals / gains[bins]


def out_of_fold(signals, true_energy, eta, ids, folds, scope, weights=None):
    """Fit each model without its complete validation fold, then apply signal only."""
    signals, true_energy = np.asarray(signals, dtype=float), np.asarray(true_energy, dtype=float)
    ids, folds, eta = np.asarray(ids), np.asarray(folds), np.asarray(eta)
    n = len(ids)
    if any(a.shape != (n,) for a in (signals, true_energy, folds, eta)) or set(folds.tolist()) != set(range(FOLDS)):
        raise ValueError('Invalid fold/training arrays')
    if not np.all(np.isfinite(true_energy)) or np.any(true_energy <= 0):
        raise ValueError('Invalid training truth energy')
    weights = checked_weights(weights, n)
    response = signals / true_energy
    predictions = np.empty(n)
    models = []
    for fold in range(FOLDS):
        training, heldout = folds != fold, folds == fold
        try:
            model = fit_gain(response[training], eta[training], ids[training], scope, weights[training], kind='out-of-fold-training')
        except InvalidTrainingGain as exc:
            exc.excluded_fold = fold
            exc.completed_refits = len(models)
            raise
        model.update(excluded_fold=fold, heldout_unique_primaries=int(heldout.sum()),
                     heldout_primary_ids_sha256=ids_hash(ids[heldout]),
                     heldout_multiplicity_total=int(weights[heldout].sum()))
        predictions[heldout] = apply_calibration(model, signals[heldout], eta[heldout], scope)
        models.append(model)
    return predictions, models


def scope_for(contract, name, source):
    return dict(model=name, compact_sha256=contract[name+'_compact_sha256'],
                materials_sha256=contract[name+'_materials_sha256'],
                training_primary_manifest_sha256=contract[name+'_primary_manifest_sha256'],
                training_primary_revision=contract[name+'_primary_revision'],
                training_input_sha256=contract['input_sha256'], training_truth_sha256=contract['truth_sha256'],
                feature='ideal absolute primary eta, not measured cluster direction', **source)


def response_histogram(ratio):
    edges = np.linspace(0, 3, 121)
    return dict(edges=edges.tolist(), counts=np.histogram(ratio, edges)[0].tolist(), events=len(ratio),
                underflow=int(np.count_nonzero(ratio < edges[0])), overflow=int(np.count_nonzero(ratio > edges[-1])),
                normalization='Ehat/Etrue, no normalization by fitted evaluation mean')


def summarize(loaded, contract, source, bootstrap=BOOTSTRAPS):
    """Synthetic-testable core. CLI runs fixed 1000 refitted replicates after gates."""
    if bootstrap < 2:
        raise ValueError('Need at least two bootstrap replicates')
    values = loaded['reference'][1]
    ids = np.array([r['event'] for r in loaded['reference'][0]], dtype=int)
    n = len(ids); folds = make_folds(ids)
    eta, true_energy = values[:, 1], values[:, 0]
    categories, meta = pair.projections(values, contract)
    scopes = {name:scope_for(contract, name, source) for name in MODELS}
    ratios, calibration = {}, {}
    for name in MODELS:
        v = loaded[name][1]
        predictions, fold_models = out_of_fold(v[:, 3], v[:, 0], v[:, 1], ids, folds, scopes[name])
        ratios[name] = predictions / v[:, 0]  # Truth only evaluates held-out predictions.
        full = fit_gain(v[:, 3]/v[:, 0], v[:, 1], ids, scopes[name], kind='full-fit-reuse-only')
        full['validation_status'] = f'Trained on all {n}; this full-fit model was not evaluated on independent primaries'
        calibration[name] = dict(fold_models=fold_models, full_fit_reuse_only=full)
    boot = {name:{axis:np.empty((bootstrap, item['bins'], 2)) for axis,item in meta.items()} for name in MODELS}
    fit_digests = {name:hashlib.sha256() for name in MODELS}
    invalid = {name:[] for name in MODELS}
    completed_refits = dict.fromkeys(MODELS, 0)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    for b in range(bootstrap):
        weights = np.bincount(rng.integers(n, size=n), minlength=n)
        for name in MODELS:
            v = loaded[name][1]
            fit_digests[name].update(b.to_bytes(8, 'little'))
            try:
                estimates, models = out_of_fold(v[:, 3], v[:, 0], v[:, 1], ids, folds, scopes[name], weights)
            except InvalidTrainingGain as exc:
                failure = dict(replicate=b, excluded_fold=exc.excluded_fold,
                               completed_refits_before_failure=exc.completed_refits, reason=str(exc))
                invalid[name].append(failure)
                completed_refits[name] += exc.completed_refits
                fit_digests[name].update(json.dumps(failure, sort_keys=True).encode())
                for axis in meta: boot[name][axis][b, :, :] = np.nan
                continue
            completed_refits[name] += len(models)
            # Binds the actual refitted gain/count sequence without exporting it.
            for model in models:
                fit_digests[name].update(np.asarray(model['gains'], dtype='<f8').tobytes())
                fit_digests[name].update(np.asarray(model['training_bin_multiplicities'], dtype='<i8').tobytes())
            response = estimates / v[:, 0]
            for axis, cats in categories.items():
                mean, width = pair.common.binned_moments(response, cats, weights, meta[axis]['bins'])
                boot[name][axis][b, :, 0] = mean; boot[name][axis][b, :, 1] = width
    models = {}
    for name in MODELS:
        entry = dict(label=contract.get(name+'_label', name), evidence=loaded[name][2], projections={},
                     raw_global=pair.moments(loaded[name][1][:, 4]), calibration_model_name=name)
        for axis,cats in categories.items():
            rows = []
            for i in range(meta[axis]['bins']):
                row = pair.moments(ratios[name][cats == i])
                for j,field in enumerate(('mean_response','fractional_width')):
                    row[field+'_bootstrap'] = pair.common.interval(boot[name][axis][:, i, j])
                if axis in ('global','abs_eta','siw_folded_phi','transition_union'):
                    row['calibrated_response_histogram'] = response_histogram(ratios[name][cats == i])
                rows.append(row)
            if axis == 'global': entry['global'] = rows[0]
            else: entry['projections'][axis] = dict(meta[axis], bins=rows)
        models[name] = entry
    contrasts = {}
    order, columns, contrast_order, contrast_columns = [], [], [], []
    for axis,item in meta.items():
        delta = boot['candidate'][axis][:, :, 1] - boot['reference'][axis][:, :, 1]
        rows = []
        for i in range(item['bins']):
            a = models['candidate']['global'] if axis == 'global' else models['candidate']['projections'][axis]['bins'][i]
            b = models['reference']['global'] if axis == 'global' else models['reference']['projections'][axis]['bins'][i]
            x,y = a['fractional_width'], b['fractional_width']
            rows.append(dict(events=a['events'], difference=x-y if x is not None and y is not None else None, **pair.common.interval(delta[:, i])))
            contrast_order.append(f'candidate_minus_reference:{axis}:{i}'); contrast_columns.append(delta[:, i])
        contrasts[axis] = rows
    for name in MODELS:
        for axis,item in meta.items():
            for i in range(item['bins']):
                order.append(f'{name}:{axis}:{i}'); columns.append(boot[name][axis][:, i, 1])
    fold_bytes = np.column_stack([ids, folds]).astype('<i8').tobytes()
    fold_record = dict(folds=FOLDS, seed=FOLD_SEED,
                       assignment='Sort primary IDs; NumPy default_rng(seed).permutation of sorted positions; five balanced contiguous blocks',
                       populations=[int(np.count_nonzero(folds==i)) for i in range(FOLDS)],
                       assignment_ids_and_labels_sha256=hashlib.sha256(fold_bytes).hexdigest())
    artifact = dict(status='EXPLORATORY PROTOTYPE', algorithm=ALGORITHM, eta_edges=ETA_EDGES.tolist(),
                    scope=source, fold_assignment=fold_record, models=calibration,
                    deployment_limit='The full-fit table needs fresh independent validation and matching geometry/materials; ideal primary eta is an oracle direction feature.')
    result = dict(status='EXPLORATORY SECONDARY PROTOTYPE', events=n,
                  observable='Held-out C=Ehat/Etrue; sample SD(C)/mean(C)',
                  interpretation='Exploratory cross-validated eta-only ideal-direction diagnostic: calibration family selected after full raw inspection; raw study remains primary. No held-out recentering, independent-validation, intrinsic reconstructed-resolution, digitization, pileup, multi-TeV or noninferiority claim.',
                  contract=contract, source=source, algorithm=ALGORITHM, fold_assignment=fold_record,
                  raw_comparison_limit='raw_global is descriptive only; no calibrated-vs-raw uncertainty contrast is computed. Inference here compares the two cross-validated models under common refitted secondary-bootstrap weights.',
                  bootstrap=dict(replicates=bootstrap, seed=BOOTSTRAP_SEED, folds_fixed=True,
                                 resampling='Shared whole-primary multiplicities across both models/projections; refit every training fold then weighted held-out statistics',
                                 requested_fold_refits_per_model=bootstrap*FOLDS, completed_fold_refits=completed_refits,
                                 refit_audit_sha256={k:v.hexdigest() for k,v in fit_digests.items()},
                                 invalid_gain_replicates=invalid,
                                 complete_prediction_replicates={name:bootstrap-len(invalid[name]) for name in MODELS},
                                 undefined_rule='No redraw or deletion: failed gain replicate gives undefined statistics; any undefined bootstrap statistic gives null interval/covariance with its undefined count.',
                                 intervals='Pointwise 95% percentile, conditional on calibration family chosen after raw inspection and saved simulation', noninferiority_margin=None),
                  models=models, candidate_minus_reference=contrasts,
                  width_covariance=pair.covariance(columns, order), contrast_covariance=pair.covariance(contrast_columns, contrast_order))
    return result, artifact


def analyze(args):
    contract = json.loads(args.contract.read_text())
    paths = dict(reference=args.reference_run, candidate=args.candidate_run)
    loaded = {name:pair.common.load_run(path) for name,path in paths.items()}
    pair.validate_pair(loaded, contract)
    checks = {name:dict(transport=pair.common.validate_contract(path, 'lar'), maps=pair.validate_maps(path, name, contract)) for name,path in paths.items()}
    source = dict(source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  analysis_sha256=pair.common.sha(__file__), pair_helper_sha256=pair.common.sha(pair.__file__),
                  raw_helper_sha256=pair.common.sha(pair.common.__file__), contract_sha256=pair.common.sha(args.contract),
                  protocol_sha256=pair.common.sha(PROTOCOL), numpy_version=np.__version__)
    result, artifact = summarize(loaded, contract, source)
    result['native_contract_checks'] = checks
    args.output.mkdir(parents=True, exist_ok=False)
    artifact_path = args.output/'calibration-models.json'; pair.common.write(artifact_path, artifact)
    result['calibration_models_file'] = artifact_path.name; result['calibration_models_sha256'] = pair.common.sha(artifact_path)
    pair.common.write(args.output/'summary.json',result)
    print(json.dumps({name:{k:v for k,v in model['global'].items() if 'histogram' not in k} for name,model in result['models'].items()},indent=2))
    print('Candidate minus reference:',json.dumps(result['candidate_minus_reference']['global']))


def plot(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    result = json.loads(args.summary.read_text())
    if result.get('algorithm') != ALGORITHM: raise ValueError('Unexpected calibration algorithm')
    args.output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'nodd-compact-heldout-calibration-v1'})
    styles = dict(reference=dict(color='#dada66',ls='--',marker='s',markeredgecolor='#555555'),
                  candidate=dict(color='#cccc00',ls='-',marker='o',markeredgecolor='#333333'))
    labels = dict(abs_eta='|η|',siw_folded_phi='φ folded with legacy Si–W sector period [rad]',energy='Primary total energy [GeV]')
    exports=[]
    def export(fig,name):
        fig.text(.02,.012,'Exploratory secondary · 5-fold held-out ideal-η gains · same 10k electrons · raw comparison remains primary · no digitization',fontsize=8)
        fig.tight_layout(rect=(0,.05,1,.94))
        for ext in ('png','pdf','svg'):
            path=args.output/f'{name}.{ext}'
            fig.savefig(path,dpi=160,metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else {'Date':None} if ext=='svg' else {})
            if ext=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
            exports.append(path)
        plt.close(fig)
    def projection(ax,axis,field,region=None):
        for name,model in result['models'].items():
            p=model['projections'][axis]
            edges=np.array(p['energy_edges'] if region is not None else p['edges'])
            rows=p['bins'][region*14:(region+1)*14] if region is not None else p['bins']
            x=(edges[:-1]+edges[1:])/2;scale=100 if field=='fractional_width' else 1
            y=np.array([r[field] if r[field] is not None else np.nan for r in rows])*scale
            err=np.array([[max(0,y[i]-r[field+'_bootstrap']['ci95'][0]*scale),max(0,r[field+'_bootstrap']['ci95'][1]*scale-y[i])]
                          if r[field+'_bootstrap']['ci95'] else [np.nan,np.nan] for i,r in enumerate(rows)]).T
            ax.errorbar(x,y,yerr=err,label=model['label'],capsize=2,markersize=4,**styles[name])
        ax.set_xlabel(labels.get(axis,'Primary total energy [GeV]'));ax.grid(alpha=.22)
        ax.set_ylabel('SD(Ehat/Etrue) / mean [%]' if field=='fractional_width' else 'Mean Ehat/Etrue · held out')
        if field=='mean_response':ax.axhline(1,color='#777777',lw=1)
    fig,axs=plt.subplots(1,2,figsize=(12,4.7))
    for ax,axis in zip(axs,('abs_eta','siw_folded_phi')):projection(ax,axis,'fractional_width')
    axs[0].legend();fig.suptitle('Held-out calibrated response widths · fixed η-only forward gains');export(fig,'calibrated-angular-widths')
    fig,axs=plt.subplots(1,2,figsize=(12,4.7))
    for ax,axis in zip(axs,('abs_eta','energy')):projection(ax,axis,'mean_response')
    axs[0].legend();fig.suptitle('Held-out mean closure · energy dependence is retained');export(fig,'calibrated-closure')
    fig,axs=plt.subplots(1,3,figsize=(15,4.7))
    for i,ax in enumerate(axs):
        projection(ax,'broad_eta_energy','fractional_width',i)
        ax.set_title(f'{pair.AXES["broad_eta"][i]:g} ≤ |η| < {pair.AXES["broad_eta"][i+1]:g}')
    axs[0].legend();fig.suptitle('Held-out energy widths in fixed broad angular regions');export(fig,'calibrated-energy-by-region')
    fig,axs=plt.subplots(1,3,figsize=(15,4.7))
    for i,ax in enumerate(axs):
        projection(ax,'broad_eta_energy','mean_response',i)
        ax.set_title(f'{pair.AXES["broad_eta"][i]:g} ≤ |η| < {pair.AXES["broad_eta"][i+1]:g}')
    axs[0].legend();fig.suptitle('Held-out energy closure in fixed broad angular regions');export(fig,'calibrated-closure-by-region')
    def hist(ax,rows):
        for name,row in zip(MODELS,rows):
            h=row['calibrated_response_histogram']
            if not h['events']:continue
            style={k:v for k,v in styles[name].items() if k in ('color','ls')}
            ax.stairs(np.array(h['counts'])/h['events'],h['edges'],label=result['models'][name]['label'],**style)
        ax.set_yscale('log');ax.grid(alpha=.2)
    fig,axs=plt.subplots(1,2,figsize=(12,4.7))
    hist(axs[0],[result['models'][n]['global'] for n in MODELS])
    hist(axs[1],[result['models'][n]['projections']['transition_union']['bins'][1] for n in MODELS])
    axs[0].set_title('All primaries, zeros retained');axs[1].set_title('Common old/new partial-depth union')
    for ax in axs:ax.set_xlabel('Held-out Ehat/Etrue');ax.set_ylabel('Fraction of selected events / bin')
    axs[0].legend();fig.suptitle('Underlying calibrated response distributions · no evaluation-mean rescaling');export(fig,'calibrated-response-distributions')
    for axis in ('abs_eta','siw_folded_phi'):
        fig,axs=plt.subplots(2,5,figsize=(16,7),sharex=True,sharey=True)
        edges=result['models']['reference']['projections'][axis]['edges']
        for i,ax in enumerate(axs.flat):
            rows=[result['models'][n]['projections'][axis]['bins'][i] for n in MODELS];hist(ax,rows)
            ax.set_title(f'{edges[i]:.3f}…{edges[i+1]:.3f} (n={rows[0]["events"]})')
        axs.flat[0].legend(fontsize=8);fig.supxlabel('Held-out Ehat/Etrue',y=.06);fig.supylabel('Fraction of angular-bin events / bin')
        fig.suptitle('Underlying held-out calibrated distributions: '+labels[axis]);export(fig,'calibrated-distributions-'+axis)
    fig,axs=plt.subplots(1,3,figsize=(15,4.7))
    for ax,axis in zip(axs,('abs_eta','siw_folded_phi','energy')):
        p=result['models']['reference']['projections'][axis];edges=np.array(p['edges']);x=(edges[:-1]+edges[1:])/2
        rows=result['candidate_minus_reference'][axis];y=np.array([r['difference'] if r['difference'] is not None else np.nan for r in rows])*100
        err=np.array([[max(0,y[i]-r['ci95'][0]*100),max(0,r['ci95'][1]*100-y[i])] if r['ci95'] else [np.nan,np.nan] for i,r in enumerate(rows)]).T
        ax.errorbar(x,y,yerr=err,color='#cccc00',marker='o',markeredgecolor='#333333',capsize=2)
        ax.axhline(0,color='#777777',lw=1);ax.grid(alpha=.22);ax.set_xlabel(labels[axis]);ax.set_ylabel('Compact − original calibrated width [pp]')
    fig.suptitle('Held-out paired width differences · refitted pointwise 95% bounds; no acceptance margin');export(fig,'calibrated-paired-difference')
    pair.common.write(args.output/'render.json',dict(summary_sha256=pair.common.sha(args.summary),plotter_sha256=pair.common.sha(__file__),
                      matplotlib_version=matplotlib.__version__,figures={p.name:pair.common.sha(p) for p in exports}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('analyze')
    for name in ('reference-run','candidate-run','contract','output'):p.add_argument('--'+name,type=Path,required=True)
    p=sub.add_parser('plot');p.add_argument('--summary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();analyze(args) if args.command=='analyze' else plot(args)


if __name__=='__main__':main()
