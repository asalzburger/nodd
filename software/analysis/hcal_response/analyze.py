"""Audited fixed-energy HCAL response aggregates and ECAL-style angular plots."""
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
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
    if args.bootstrap<2:raise ValueError('At least two bootstrap replicates required')
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
            raw=np.array([r['signal_GeV'] for r,k in zip(rows,selected) if k])
            entry.update(mean_raw_energy_GeV=float(raw.mean()) if len(raw) else None,raw_energy_sample_sd_GeV=float(raw.std(ddof=1)) if len(raw)>1 else None)
            entry.update(low=float(edges[i]), high=float(edges[i + 1]),
                         histogram_counts=np.histogram(response[selected], hist_edges)[0].tolist())
            for key, draws in (('fractional_width', widths), ('mean_response', means)):
                values = draws[:, a * 15 + i]
                bad = int(np.count_nonzero(~np.isfinite(values)))
                entry[key + '_undefined_bootstrap'] = bad
                entry[key + '_ci95'] = list(map(float, np.quantile(values, [.025, .975]))) if not bad else None
            j=a*15+i
            entry['mean_raw_energy_ci95_GeV']=None if entry['mean_response_ci95'] is None else [50*x for x in entry['mean_response_ci95']]
            entry['raw_energy_sample_sd_bootstrap']=interval(widths[:,j]*means[:,j]*50)
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
        controls=dict(full_phi=controls,eta_sign={str(sign):moments(response[np.array([r['eta']<0 for r in rows])==bool(sign)]) for sign in (0,1)}),
        width_covariance=dict(order=[f'{axis}:{i}' for axis in EDGES for i in range(15)], unit='fractional width squared',
                              matrix=np.cov(widths, rowvar=False).tolist() if np.all(np.isfinite(widths)) else None),
        evidence=dict(receipt_sha256=sha(run / 'receipt.json'), readback_sha256=sha(run / 'readback.json'),
                      ledger_sha256=sha(ledger), analysis_sha256=sha(__file__), receipt=receipt,
                      readback={k: v for k, v in proof.items() if k not in ('workers', 'sample')},
                      sample=compact_sample, geometry=compact_geometry,
                      runtime_worker_threads=sorted(w['thread_id'] for w in workers),
                      runtime_steel_materials=runtime_materials))
    if getattr(args,'baseline_run',None):
        result['comparison']=paired_angular_comparison(rows,args.baseline_run,args.bootstrap,args.seed)
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
        finite_upper = hi[np.isfinite(hi)]
        if len(finite_upper): axis.set_ylim(0, max(float(finite_upper.max()) * 1.18, 1e-6))
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
    if result.get('comparison'):
        comparison_plot(result,out)
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
    axes[1].text(.03, .97, f"All {stats['events']:,} primaries\nMean raw E: {50*stats['mean_response']:.3f} GeV\nSD / mean: {100*stats['fractional_width']:.2f}%\nZero response: {stats['zero_events']}\nFinal six layers: {100*profile['terminal_six_fraction_mean']:.2f}% mean",
                 transform=axes[1].transAxes, va='top', ha='left', fontsize=9)
    axes[1].set(xlabel='Raw scintillator response [%]', ylabel='Primaries / bin')
    for axis in axes: axis.grid(alpha=.18)
    fig.suptitle('HCAL depth and inclusive-response controls · 50 GeV π⁻', fontsize=14)
    fig.supxlabel('Terminal-layer activity diagnoses rear shower tails; it does not directly measure containment.', fontsize=9)
    for ext in ('png', 'pdf', 'svg'):
        save_figure(fig, out / f'depth-response-controls.{ext}')
    plt.close(fig)
    save(out / 'render.json', {p.name: sha(p) for p in sorted(out.iterdir()) if p.suffix in ('.png', '.pdf', '.svg')})


def audited_rows(run, count=None, role=None):
    """Read compact ledgers only after checking their actual immutable receipts."""
    run=Path(run).resolve();proof=json.loads((run/'readback.json').read_text());receipt=json.loads((run/'receipt.json').read_text())
    if proof['status']!='PASS' or receipt['exit_code'] or proof['event_summary_sha256']!=sha(run/'event-summary.jsonl') or proof['receipt_sha256']!=sha(run/'receipt.json'):
        raise ValueError('Complete unchanged saved-data readback required')
    rows=sorted(map(json.loads,(run/'event-summary.jsonl').read_text().splitlines()),key=lambda r:r['event'])
    if len(rows)!=proof['events'] or [r['event'] for r in rows]!=list(range(len(rows))) or (count is not None and len(rows)!=count):
        raise ValueError('Required complete primary population differs')
    sample=proof.get('sample') or {}
    if role is not None and sample.get('sample_role','angular')!=role:raise ValueError('Sample role differs from protocol')
    for row in rows:
        if not math.isfinite(row['energy_GeV']) or abs(row['energy_GeV']-50)>1e-7 or not math.isfinite(row['signal_GeV']) or row['signal_GeV']<0 or not math.isfinite(row['response']) or not math.isclose(row['response'],row['signal_GeV']/row['energy_GeV'],rel_tol=1e-12,abs_tol=1e-14):
            raise ValueError('Invalid fixed-energy raw response')
    categories(rows)
    return rows,proof,receipt,sample


def projection_width_draws(rows,draws):
    values=np.array([r['response'] for r in rows]);cats=categories(rows);output=np.full((len(draws),30),np.nan)
    for b,selected in enumerate(draws):
        sampled=values[selected]
        for a,axis in enumerate(EDGES):
            groups=cats[axis][selected];counts=np.bincount(groups,minlength=15);sums=np.bincount(groups,weights=sampled,minlength=15);squares=np.bincount(groups,weights=sampled**2,minlength=15)
            means=np.divide(sums,counts,out=np.full(15,np.nan),where=counts>0)
            variance=np.divide(squares-sums*means,counts-1,out=np.full(15,np.nan),where=counts>1)
            output[b,a*15:(a+1)*15]=np.divide(np.sqrt(np.maximum(variance,0)),means,out=np.full(15,np.nan),where=means>0)
    return output


def interval(draws):
    draws=np.asarray(draws,dtype=float);bad=int(np.count_nonzero(~np.isfinite(draws)))
    return dict(ci95=None if bad else list(map(float,np.quantile(draws,[.025,.975]))),undefined_replicates=bad)


def paired_angular_comparison(new_rows,baseline_run,replicates,seed):
    old,proof,receipt,sample=audited_rows(baseline_run,10000,'angular')
    if len(new_rows)!=len(old):raise ValueError('Matched angular populations differ')
    for a,b in zip(new_rows,old):
        if a['event']!=b['event'] or any(not math.isclose(a[k],b[k],rel_tol=0,abs_tol=1e-9) for k in ('energy_GeV','eta','phi')):
            raise ValueError('Old/new primary identities or directions differ')
    if replicates<2:raise ValueError('At least two bootstrap replicates required')
    rng=np.random.default_rng(seed);draws=[rng.integers(len(old),size=len(old)) for _ in range(replicates)]
    old_draws=projection_width_draws(old,draws);new_draws=projection_width_draws(new_rows,draws)
    cats=categories(old);models={};differences={}
    for a,axis in enumerate(EDGES):
        models[axis]=[];differences[axis]=[]
        for i in range(15):
            keep=cats[axis]==i;before=moments([r['response'] for r,k in zip(old,keep) if k]);after=moments([r['response'] for r,k in zip(new_rows,keep) if k])
            j=a*15+i;before['width_interval']=interval(old_draws[:,j]);after['width_interval']=interval(new_draws[:,j]);models[axis].append(dict(baseline=before,edge=after))
            delta=None if before['fractional_width'] is None or after['fractional_width'] is None else after['fractional_width']-before['fractional_width']
            differences[axis].append(dict(events=int(keep.sum()),edge_minus_baseline=delta,**interval(new_draws[:,j]-old_draws[:,j])))
    combined=np.concatenate((old_draws,new_draws),axis=1)
    return dict(status='PROTOTYPE',events=10000,models=models,width_differences=differences,
        bootstrap=dict(replicates=replicates,seed=seed,resampling='Same whole-primary multiplicities across both geometries and both angular projections',intervals='pointwise95percent percentile'),
        covariance=dict(order=[f'{model}:{axis}:{i}' for model in ('baseline','edge') for axis in EDGES for i in range(15)],unit='fractional width squared',matrix=np.cov(combined,rowvar=False).tolist() if np.all(np.isfinite(combined)) else None),
        baseline_evidence=dict(receipt_sha256=sha(Path(baseline_run)/'receipt.json'),readback_sha256=sha(Path(baseline_run)/'readback.json'),ledger_sha256=proof['event_summary_sha256'],input_hashes=sample.get('hashes'),source_revision=receipt.get('source_revision')),
        interpretation='Matched illumination; altered geometry changes shower histories. No angular response correction is trained.')


def comparison_plot(result,out):
    import matplotlib.pyplot as plt
    comparison=result['comparison'];fig,axes=plt.subplots(1,2,figsize=(12.8,5.1),layout='constrained')
    for axis,(name,projection) in zip(axes,result['projections'].items()):
        x=np.array([(a+b)/2 for a,b in zip(projection['edges'][:-1],projection['edges'][1:])]);offsets=(-100,0,100) if name=='phi' else (0,)
        for model,label,color,style in (('baseline','Original HCAL (DES-045)','#d9a16a','--'),('edge','Edge modules (DES-046)',COLOR,'-')):
            bins=[b[model] for b in comparison['models'][name]];y=np.array([np.nan if b['fractional_width'] is None else 100*b['fractional_width'] for b in bins])
            lo=np.array([np.nan if b['width_interval']['ci95'] is None else 100*b['width_interval']['ci95'][0] for b in bins]);hi=np.array([np.nan if b['width_interval']['ci95'] is None else 100*b['width_interval']['ci95'][1] for b in bins])
            for offset in offsets:axis.vlines(x+offset,lo,hi,color=color,alpha=.8)
            axis.plot(np.concatenate([x+offset for offset in offsets]),np.tile(y,len(offsets)),marker='o',ls=style,color=color,label=label,markersize=4)
        axis.set(xlim=(-65,65) if name=='phi' else(-3,3),ylim=(0,None),xlabel='Barrel sector phase [% of 22.5°]' if name=='phi' else r'Signed pseudorapidity $\eta$',ylabel=r'Raw $\sigma(r)/\langle r\rangle$ [%]');axis.grid(alpha=.18)
        if name=='phi':
            for edge in(-50,50):axis.axvline(edge,color='#777777',ls=':',lw=.8)
            for lo,hi in((-65,-50),(50,65)):axis.axvspan(lo,hi,color=COLOR,alpha=.05)
    axes[0].legend(frameon=False,loc='lower left');fig.suptitle('nODD HCAL · edge coverage · matched 10,000 π⁻ · 50 GeV',fontsize=15)
    fig.supxlabel('HCAL only · B = 0 · all zeros and tails retained · 95% matched whole-primary bootstrap intervals\nPeriodic margins repeat existing bins without adding statistics.',fontsize=9)
    for ext in('png','pdf','svg'):save_figure(fig,Path(out)/f'raw-energy-resolution-comparison.{ext}')
    plt.close(fig)


def fixed_statistics(signal,energy,fs):
    signal=np.asarray(signal,dtype=float);energy=np.asarray(energy,dtype=float)
    if len(signal)<2 or energy.shape!=signal.shape or not np.all(np.isfinite(signal)) or np.any(signal<0) or not np.all(np.isfinite(energy)) or np.any(energy<=0) or not math.isfinite(fs) or fs<=0:
        raise ValueError('Invalid inclusive fixed-direction sample or calibration factor')
    fractional=signal/energy;corrected=signal/fs;delta=fractional/fs-1
    arrays={'raw':signal,'fractional':fractional,'residual':delta};stats={'fs':float(fs)}
    for name,values in arrays.items():
        stats[name+'_mean']=float(values.mean());stats[name+'_sd']=float(values.std(ddof=1))
        for q,value in zip(('q02','q16','q50','q84','q98'),np.quantile(values,[.02,.16,.50,.84,.98])):stats[name+'_'+q]=float(value)
    cv=lambda a:None if a.mean()<=0 else float(a.std(ddof=1)/a.mean())
    stats.update(raw_cv=cv(signal),fractional_cv=cv(fractional),corrected_cv=cv(corrected),corrected_mean_GeV=float(corrected.mean()),corrected_sd_GeV=float(corrected.std(ddof=1)),zero_response_fraction=float(np.count_nonzero(signal==0)/len(signal)))
    defined=[stats[k] for k in ('raw_cv','fractional_cv','corrected_cv')]
    if any(v is None for v in defined):
        if not all(v is None for v in defined):raise ValueError('Scale-invariance definedness differs')
    elif not np.allclose(defined,defined[0],rtol=1e-10,atol=1e-12):raise ValueError('Constant positive scale changed coefficient of variation')
    if not math.isclose(stats['fractional_sd'],stats['raw_sd']/50,rel_tol=1e-10,abs_tol=1e-12) or not math.isclose(stats['residual_sd'],stats['raw_sd']/(fs*50),rel_tol=1e-10,abs_tol=1e-12):
        raise ValueError('Fixed true-energy denominator identity failed')
    return stats


def cohort_evidence(run,proof,receipt,sample):
    return dict(receipt_sha256=sha(Path(run)/'receipt.json'),readback_sha256=sha(Path(run)/'readback.json'),ledger_sha256=proof['event_summary_sha256'],sample_id=sample.get('sample_id'),role=sample.get('sample_role'),seed=receipt['seed'],direction=sample.get('fixed_direction'),geometry_hashes={k:sample.get('hashes',{}).get(k) for k in ('detector.xml','materials.xml','expected.json')},source_revision=receipt.get('source_revision'),producer_sha256=receipt.get('producer_sha256'))


def calibrate(args):
    if args.bootstrap<2:raise ValueError('At least two bootstrap replicates required')
    rows,proof,receipt,sample=audited_rows(args.run,2000,'calibration')
    if receipt['seed']!=202650102 or not sample.get('fixed_direction'):raise ValueError('Calibration must use independent declared fixed-direction cohort')
    response=np.array([r['response'] for r in rows]);fs=float(response.mean())
    if not math.isfinite(fs) or fs<=0:raise ValueError('Calibration response factor must be finite positive')
    rng=np.random.default_rng(13001002);draws=np.array([response[rng.integers(len(rows),size=len(rows))].mean() for _ in range(args.bootstrap)])
    result=dict(status='FROZEN / PROTOTYPE',frozen_at=datetime.now(timezone.utc).isoformat(),fs=fs,events=2000,
        fs_standard_error=float(response.std(ddof=1)/math.sqrt(len(rows))),fs_bootstrap=interval(np.where(draws>0,draws,np.nan)),
        bootstrap=dict(replicates=args.bootstrap,seed=13001002),
        meaning='Effective50GeV pi-minus response factor at the prospectively selected direction; includes represented geometry/sampling/hadronic losses, not an intrinsic material sampling fraction',
        evidence=cohort_evidence(args.run,proof,receipt,sample),analysis_sha256=sha(__file__))
    output=Path(args.output).resolve()
    if output.exists():raise ValueError('Refusing calibration receipt overwrite')
    output.parent.mkdir(parents=True,exist_ok=True);save(output,result);print(json.dumps(result,indent=2))


def fixed_analyze(args):
    if args.bootstrap<2:raise ValueError('At least two bootstrap replicates required')
    calibration=json.loads(Path(args.calibration).read_text());cal_rows,cp,cr,cs=audited_rows(args.calibration_run,2000,'calibration');rows,proof,receipt,sample=audited_rows(args.run,10000,'validation')
    evidence=cohort_evidence(args.calibration_run,cp,cr,cs)
    try:
        frozen=datetime.fromisoformat(calibration['frozen_at']);started=datetime.fromisoformat(receipt['started_at'])
    except (KeyError,TypeError,ValueError) as error:
        raise ValueError('Calibration/validation chronology is unverifiable') from error
    if frozen.tzinfo is None or started.tzinfo is None or frozen>started:
        raise ValueError('Calibration must be frozen before validation transport starts')
    if calibration['status']!='FROZEN / PROTOTYPE' or evidence!=calibration['evidence'] or cr['seed']!=202650102 or receipt['seed']!=202650103 or cs.get('sample_id')==sample.get('sample_id'):
        raise ValueError('Frozen calibration identity or independent validation cohort differs')
    if not cs.get('fixed_direction') or cs['fixed_direction']!=sample.get('fixed_direction') or evidence['geometry_hashes']!=cohort_evidence(args.run,proof,receipt,sample)['geometry_hashes']:
        raise ValueError('Fixed cohorts have different directions or geometries')
    for population in(cal_rows,rows):
        if any(abs(r['eta']-sample['fixed_direction']['eta'])>1e-9 or abs(r['phi']-sample['fixed_direction']['phi_rad'])>1e-9 for r in population):raise ValueError('Fixed cohort contains angular smearing')
    signal=np.array([r['signal_GeV'] for r in rows]);energy=np.array([r['energy_GeV'] for r in rows]);cal=np.array([r['response'] for r in cal_rows]);fs=float(calibration['fs'])
    if not math.isclose(fs,float(cal.mean()),rel_tol=1e-12,abs_tol=1e-15):raise ValueError('Frozen response factor differs from calibration population')
    point=fixed_statistics(signal,energy,fs);keys=list(point);draws=np.full((args.bootstrap,len(keys)),np.nan)
    vrng=np.random.default_rng(13001001);crng=np.random.default_rng(13001002)
    for b in range(args.bootstrap):
        vi=vrng.integers(len(rows),size=len(rows));ci=crng.integers(len(cal),size=len(cal));fb=float(cal[ci].mean())
        if fb>0:
            values=fixed_statistics(signal[vi],energy[vi],fb)
            draws[b]=[np.nan if values[k] is None else values[k] for k in keys]
    intervals={k:interval(draws[:,i]) for i,k in enumerate(keys)}
    coords={'raw_energy':signal,'raw_fractional':signal/energy,'corrected_residual':signal/(fs*energy)-1};histograms={}
    for name,values in coords.items():
        lo=min(float(values.min()),0.);hi=max(float(values.max()),0.)
        if hi<=lo:hi=lo+1e-6
        edges=np.linspace(lo,hi+max(abs(hi),1)*1e-9,81);counts=np.histogram(values,edges)[0]
        if int(counts.sum())!=len(rows):raise ValueError('Fixed histogram lost zeros/tails')
        histograms[name]=dict(edges=edges.tolist(),counts=counts.tolist(),underflow=0,overflow=0,normalization='Unweighted inclusive primary counts')
    layers=np.array([r['layer_energies_GeV'] for r in rows]);tail=np.array([r['terminal_six_fraction'] for r in rows]);escape=np.array([r['observer']['world_escape_kinetic_GeV'] for r in rows])
    if layers.shape!=(10000,60) or not np.all(np.isfinite(layers)) or np.any(layers<0) or not np.allclose(layers.sum(axis=1),signal,rtol=1e-5,atol=1e-7) or not np.all(np.isfinite(tail)) or not np.all(np.isfinite(escape)) or np.any(escape<0):raise ValueError('Invalid fixed depth/escape control')
    result=dict(status='PROTOTYPE',events=10000,calibration_events=2000,total_energy_GeV=50,direction=sample['fixed_direction'],statistics=point,intervals=intervals,histograms=histograms,
        zero_response_events=int(np.count_nonzero(signal==0)),width_definitions=dict(raw_sd='SD(S)[GeV]',fractional_sd='SD(S/Etrue), denominator true50GeV',residual_sd='SD(S/(fs*Etrue)-1), denominator fs*true50GeV',coefficient_of_variation='SD(S)/mean(S), unchanged by constant positive sampling correction'),
        bootstrap=dict(replicates=args.bootstrap,validation_seed=13001001,calibration_seed=13001002,resampling='Independent calibration and validation multiplicities; validation draw reused across all panels; refit fs per calibration replica',intervals='Pointwise95percent two-sample percentile intervals'),
        covariance=dict(order=keys,matrix=np.cov(draws,rowvar=False).tolist() if np.all(np.isfinite(draws)) else None),
        depth=dict(layer_mean_GeV=layers.mean(axis=0).tolist(),terminal_six_fraction_mean=float(tail.mean()),world_escape_kinetic_mean_GeV=float(escape.mean()),interpretation='Terminal activity/escaped kinetic energy are separate diagnostics, not complete containment or energy balance'),
        calibration=dict(receipt=calibration,receipt_sha256=sha(args.calibration)),validation_evidence=cohort_evidence(args.run,proof,receipt,sample),analysis_sha256=sha(__file__),
        scale_invariance='Verified for the point estimate and every defined bootstrap replica; correction changes scale and SD/Etrue, not coefficient of variation')
    out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=False);save(out/'summary.json',result);fixed_plot(result,out/'figures')
    print(json.dumps(dict(fs=fs,statistics=point),indent=2))


def fixed_plot(result,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
    fig,axes=plt.subplots(1,3,figsize=(15,5.8),layout='constrained');stats=result['statistics']
    panels=(('raw_energy','Raw deposited energy',r'$E_\mathrm{raw}$ [GeV]','raw',1.,' GeV'),
            ('raw_fractional','Raw fractional response',r'$E_\mathrm{raw}/E_\mathrm{true}$ [%]','fractional',100.,'%'),
            ('corrected_residual','Sampling-corrected residual',r'$E_\mathrm{raw}/(f_s E_\mathrm{true})-1$ [%]','residual',100.,'%'))
    for axis,(name,title,label,key,factor,unit) in zip(axes,panels):
        h=result['histograms'][name]
        axis.stairs(h['counts'],np.array(h['edges'])*factor,color=COLOR,fill=True,alpha=.5)
        axis.set(xlabel=label,ylabel='Primaries / bin',title=title);axis.grid(alpha=.15)
        ci=result['intervals'][key+'_sd']['ci95']
        ci_text='undefined' if ci is None else f"[{factor*ci[0]:.4g}, {factor*ci[1]:.4g}]{unit}"
        text=f"Mean = {factor*stats[key+'_mean']:.4g}{unit}\nSD = {factor*stats[key+'_sd']:.4g}{unit}\n95% CI {ci_text}"
        cv=stats['corrected_cv'] if key=='residual' else stats['raw_cv']
        label_cv='SD(Ecorr) / mean(Ecorr)' if key=='residual' else 'SD / mean'
        text+=f"\n{label_cv} = {100*cv:.3g}%" if cv is not None else '\nSD / mean undefined'
        text+=f"\nN = {result['events']:,}; zeros = {result['zero_response_events']}"
        if key=='residual':axis.axvline(0,color='#555555',ls=':',lw=1)
        axis.text(.025,.97,text,transform=axis.transAxes,ha='left',va='top',fontsize=8.5)
    d=result['direction']
    fig.suptitle(f"nODD HCAL · 10,000 π⁻ · 50 GeV\nFixed barrel direction: η = {d['eta']:.5g}, φ = {math.degrees(d['phi_rad']):.5g}°",fontsize=14)
    fig.supxlabel(f"Independent 2,000-event calibration · frozen fs = {stats['fs']:.7g} · 95% two-sample bootstrap intervals\nAll zeros and tails included · constant sampling scaling leaves SD / mean unchanged",fontsize=9)
    for ext in('png','pdf','svg'):save_figure(fig,out/f'fixed-direction-response.{ext}')
    plt.close(fig)
    save(out/'render.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.suffix in('.png','.pdf','.svg')})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='stage', required=True)
    a = sub.add_parser('analyze'); a.add_argument('--run', type=Path, required=True); a.add_argument('--output', type=Path, required=True)
    a.add_argument('--bootstrap', type=int, default=1000); a.add_argument('--seed', type=int, default=13001000);a.add_argument('--baseline-run',type=Path)
    a = sub.add_parser('plot'); a.add_argument('--summary', type=Path, required=True); a.add_argument('--output', type=Path, required=True)
    a=sub.add_parser('calibrate');a.add_argument('--run',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--bootstrap',type=int,default=1000)
    a=sub.add_parser('fixed-analyze');a.add_argument('--run',type=Path,required=True);a.add_argument('--calibration-run',type=Path,required=True);a.add_argument('--calibration',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--bootstrap',type=int,default=1000)
    args = p.parse_args()
    if args.stage=='analyze':analyze(args)
    elif args.stage=='calibrate':calibrate(args)
    elif args.stage=='fixed-analyze':fixed_analyze(args)
    else:plot(json.loads(args.summary.read_text()),args.output)


if __name__ == '__main__':
    main()
