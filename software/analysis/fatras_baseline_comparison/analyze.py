#!/usr/bin/env python3
"""Loss-accounted old/current Fatras truth-fit resolutions and paired ratios."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('resolution_native_reader',ROOT/'software/analysis/tracker_optimization/analyze.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
PARAMETERS=('d0','z0','phi','theta','q_over_p','pt_relative','q_over_pt_relative')
MOMENTA=(1,5,10,100)
ABS_EDGES=np.arange(0,4.1,.5)
SIGNED_EDGES=np.linspace(-4,4,33)
PROBABILITY=.6826894921370859


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def check_contract(report,baseline,momentum):
    if report.get('outcome')!='completed' or report.get('simulation')!='fatras':
        raise ValueError('Incomplete or non-Fatras performance case')
    c=report['campaign']
    if (report['events']!=20000 or report['pt_GeV']!=momentum or report['threads']!=1 or
            c['seed']!=42042 or c['field_Bz_T']!=3 or c['eta_range']!=[-4.,4.] or c['phi_range_rad']!=[-np.pi,np.pi] or
            c['particles_per_event']!=1 or c['vertex_mm']!=[0.,0.,0.] or not c['randomize_charge']):
        raise ValueError('Changed comparison gun/field/event contract')
    digi=c['digitization']
    expected_pitch=[.075,.5 if baseline=='old' else 2.]
    if (digi['pixel_pitch_mm']!=[.05,.05] or digi['short_strip_pitch_mm']!=expected_pitch or
            digi['long_strip_pitch_mm']!=.08 or digi['long_strip_measured_coordinates']!=1 or
            not digi['digital'] or not digi['component_digital'] or digi['threshold']!=0 or
            digi['drift'] or digi['diffusion'] or c['truth_tracking']['minimum_measurements']!=7):
        raise ValueError('Changed baseline readout/selection contract')
    if not report.get('executed_source_sha256') or 'software/running/nodd_truth_tracking.py' not in report['executed_source_sha256']:
        raise ValueError('Missing tracked source fingerprints')
    for path,digest in report['executed_source_sha256'].items():
        # Binaries have independent provenance. Only tracked source belongs here.
        source=subprocess.check_output(['git','-C',str(ROOT),'show',report['scientific_input_revision']+':'+path])
        if hashlib.sha256(source).hexdigest()!=digest:
            raise ValueError('Executed source differs from pinned source: '+path)


def check_baseline_inputs(report,baseline):
    reference=ROOT/('docs/validation/geantino-material-profiles/provenance.json' if baseline=='old' else
                    'docs/validation/baseline-material-comparison/classification-provenance.json')
    expected=json.loads(reference.read_text())['files']
    actual=report['provenance']['files']
    for item in expected:
        if item['name'] not in ('tracker.xml','materials.xml') and not item['name'].endswith('.dylib'):continue
        matches=[f['sha256'] for f in actual if f['name']==item['name']]
        if matches!=[item['sha256']]:raise ValueError('Baseline geometry identity differs: '+item['name'])
    source=ROOT/('docs/validation/gen3-material-map-run/material_map.json.gz' if baseline=='old' else
                 'docs/validation/baseline-material-comparison/material_map.json.gz')
    matches=[f['sha256'] for f in actual if f.get('role')=='saved_material_map']
    if matches!=[sha(source)]:raise ValueError('Baseline material map identity differs')


def width(values,minimum=30):
    x=np.asarray(values,dtype=float);x=x[np.isfinite(x)]
    return float(np.diff(np.quantile(x,[(1-PROBABILITY)/2,(1+PROBABILITY)/2]))[0]/2) if len(x)>=minimum else None


def summary(values,bootstrap=0,rng=None):
    x=np.asarray(values,dtype=float);finite=x[np.isfinite(x)];n=len(finite)
    out={'entries':n,'nonfinite':len(x)-n,'status':'measured' if n>=30 else 'undersampled',
         'mean':None,'mean_se':None,'median':None,'std':None,'rms':None,'width68':None,'width68_se':None}
    if n<30:return out
    out.update(mean=float(finite.mean()),median=float(np.median(finite)),std=float(finite.std(ddof=1)),
               rms=float(np.sqrt(np.mean(finite**2))),width68=width(finite),
               mean_se=float(finite.std(ddof=1)/np.sqrt(n)))
    if bootstrap:
        rng=rng if rng is not None else np.random.default_rng(74042)
        estimates=[width(finite[rng.integers(n,size=n)]) for _ in range(bootstrap)]
        out['width68_se']=float(np.std(estimates,ddof=1))
    return out


def summarize_case(case,mask,bootstrap,rng):
    n=int(mask.sum())
    counts={'generated':n}
    for key in ('selected','attempts','fitted','has_parameters','finite_fit','valid_covariance','native_match'):
        counts[key]=int(np.count_nonzero(case[key][mask]))
    counts['fit_failures']=counts['attempts']-counts['fitted']
    counts['nonfinite_fits']=counts['has_parameters']-counts['finite_fit']
    counts['invalid_covariance']=int(np.count_nonzero(mask&case['has_parameters']&~case['valid_covariance']))
    counts['wrong_charge']=int(np.count_nonzero(mask&case['finite_fit']&case['wrong_charge']))
    counts['finite_fit_fraction']=reader.wilson(counts['finite_fit'],n)
    counts['wrong_charge_fraction_of_finite_fits']=reader.wilson(counts['wrong_charge'],counts['finite_fit'])
    def parameter(name):
        pulls=case['values'][name]['pull'][mask]
        pull_stats=summary(pulls)
        pull_stats['outside_abs_3']=int(np.count_nonzero(np.isfinite(pulls)&(abs(pulls)>3)))
        return {'residual':summary(case['values'][name]['residual'][mask],bootstrap,rng),
                'pull_truth_minus_fit':pull_stats}
    return {'counts':counts,'parameters':{p:parameter(p) for p in PARAMETERS},
        'mean_created_measurements_per_generated':float(case['created'][mask].mean()) if n else None,
        'mean_used_measurements_per_generated':float(case['used'][mask].mean()) if n else None}


def reduce_case(case,bootstrap):
    rng=np.random.default_rng(74042)
    out={'global':summarize_case(case,np.ones(len(case['eta']),dtype=bool),0,rng)}
    for axis,coordinate,edges in [('abs_eta',abs(case['eta']),ABS_EDGES),('eta',case['eta'],SIGNED_EDGES)]:
        rows=[]
        for i,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
            mask=(coordinate>=lo)&((coordinate<=hi) if i==len(edges)-2 else (coordinate<hi))
            row=summarize_case(case,mask,bootstrap if axis=='abs_eta' else 0,rng)
            row.update(low=float(lo),high=float(hi));rows.append(row)
        if sum(r['counts']['generated'] for r in rows)!=len(case['eta']):
            raise ValueError('Eta bins lose generated denominator')
        out[axis]=rows
    return out


def paired_ratio(x,y,replicates=400,rng=None):
    """Resample generated events together, retaining each baseline's missing fits."""
    x,y=np.asarray(x),np.asarray(y)
    if x.shape!=y.shape:raise ValueError('Unpaired residual arrays')
    rng=rng if rng is not None else np.random.default_rng(174042)
    common=np.isfinite(x)&np.isfinite(y)
    a,b=width(x),width(y)
    result={'old_finite':int(np.isfinite(x).sum()),'current_finite':int(np.isfinite(y).sum()),
        'common_finite':int(common.sum()),'old_width68':a,'current_width68':b,'ratio':None,
        'ratio_bootstrap95':None,'ratio_bootstrap_se':None,'valid_bootstraps':0,
        'common_fit_ratio':None}
    ca,cb=width(x[common]),width(y[common])
    if ca is not None and cb is not None and ca>0:result['common_fit_ratio']=cb/ca
    if a is None or b is None or a<=0:return result
    result['ratio']=b/a;ratios=[]
    for _ in range(replicates):
        ix=rng.integers(len(x),size=len(x));v0,v1=width(x[ix]),width(y[ix])
        if v0 is not None and v1 is not None and v0>0:ratios.append(v1/v0)
    if ratios:
        result.update(ratio_bootstrap95=np.quantile(ratios,[.025,.975]).tolist(),
                      ratio_bootstrap_se=float(np.std(ratios,ddof=1)),valid_bootstraps=len(ratios))
    return result


def compare_pair(old,current,bootstrap):
    for key in ('event_id','eta','phi','pt','charge'):
        np.testing.assert_array_equal(old[key],current[key],err_msg='Generated muons differ: '+key)
    common_keys=('field_Bz_T','eta_range','phi_range_rad','truth_tracking')
    for key in common_keys:
        if old['report']['campaign'][key]!=current['report']['campaign'][key]:
            raise ValueError('Changed common reconstruction contract: '+key)
    rng=np.random.default_rng(174042);rows=[]
    for i,(lo,hi) in enumerate(zip(ABS_EDGES[:-1],ABS_EDGES[1:])):
        coordinate=abs(old['eta']);mask=(coordinate>=lo)&((coordinate<=hi) if i==len(ABS_EDGES)-2 else (coordinate<hi))
        rows.append({'low':float(lo),'high':float(hi),'generated':int(mask.sum()),
            'parameters':{p:paired_ratio(old['values'][p]['residual'][mask],current['values'][p]['residual'][mask],bootstrap,rng)
                          for p in PARAMETERS}})
    return {'generated_truth_exactly_equal':True,'scope':'Full baseline change includes geometry,material and 0.5-to-2mm response; paired generated-event bootstrap, no tail/charge/quality cuts',
            'abs_eta':rows}


def read_case(path,baseline,momentum):
    report=json.loads((path/'run-report.json').read_text());check_contract(report,baseline,momentum)
    check_baseline_inputs(report,baseline)
    case=reader.read_case(path)
    calibration=reader.audit_calibration(path,'geometric')
    if not report.get('error_table') or report['error_table']['sha256']!=calibration['error_table_sha256']:
        raise ValueError('Measured calibration differs from the declared frozen table')
    metadata=case['metadata'].copy()
    metadata.pop('native_unmatched_event_ids',None)
    metadata.update(baseline=baseline,measurement_error_audit=calibration,
        native_unmatched_count=len(case['metadata']['native_unmatched_event_ids']))
    case.update(report=report,retained_metadata=metadata)
    return case


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--bootstrap',type=int,default=400)
    ap.add_argument('--source-revision',help='Exact committed analysis source; defaults to current HEAD')
    ap.add_argument('--partial',action='store_true',help='Diagnostic reduction of completed pairs only')
    args=ap.parse_args()
    if args.bootstrap<2:ap.error('Require at least two bootstrap replicates')
    revision=args.source_revision or subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    helpers=[Path(__file__),ROOT/'software/analysis/tracker_optimization/analyze.py',
             *[ROOT/'software/analysis/truth_tracking'/name for name in ('export_profiles.py','metrics.py','pull_histograms.py')]]
    executed={str(p.resolve().relative_to(ROOT)):sha(p) for p in helpers}
    if not args.partial:
        for name,digest in executed.items():
            source=subprocess.check_output(['git','-C',str(ROOT),'show',revision+':'+name])
            if hashlib.sha256(source).hexdigest()!=digest:raise ValueError('Analysis source not at requested revision: '+name)
    result={'schema_version':1,'status':'PROTOTYPE','momenta_GeV':list(MOMENTA),'momentum_definition':'fixed transverse momentum',
        'parameters':list(PARAMETERS),'resolution_definition':'Central empirical68.268949% half-width, no residual/pull/tail/charge cuts',
        'units':{'d0':'mm','z0':'mm','phi':'rad','theta':'rad','q_over_p':'e/GeV','pt_relative':'fraction','q_over_pt_relative':'fraction'},
        'residual_sign':'Fit minus truth; phi wrapped to [-pi,pi)',
        'pull_sign':'Truth minus fit; pT and signed-curvature pulls include theta-q/p covariance',
        'population':'Each resolution uses that baseline\'s finite fitted values; unavailable fits retained in generated-event accounting',
        'bootstrap':{'replicates':args.bootstrap,'case_seed':74042,'paired_seed':174042,'unit':'generated event'},
        'cases':{},'paired':{},'analysis_sha256':sha(__file__),'analysis_source_revision':revision,
        'executed_analysis_sha256':executed,'partial_diagnostic':args.partial}
    for momentum in MOMENTA:
        paths={b:args.input/f'{b}-pt{momentum}' for b in ('old','current')}
        complete=all((p/'run-report.json').is_file() and json.loads((p/'run-report.json').read_text()).get('outcome')=='completed'
                     for p in paths.values())
        if not complete:
            if args.partial:continue
            raise ValueError(f'Missing completed old/current pair pT={momentum}')
        cases={b:read_case(p,b,momentum) for b,p in paths.items()}
        for baseline,case in cases.items():
            result['cases'][f'{baseline}-pt{momentum}']={**reduce_case(case,args.bootstrap),'metadata':case['retained_metadata']}
        result['paired'][str(momentum)]=compare_pair(cases['old'],cases['current'],args.bootstrap)
        print(f'PASS: pT={momentum}, paired truth and loss accounting/calibration verified')
    if any(sha(ROOT/name)!=digest for name,digest in executed.items()):raise ValueError('Analysis source changed during reduction')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    payload=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    args.output.write_bytes(gzip.compress(payload,mtime=0) if args.output.suffix=='.gz' else payload)


if __name__=='__main__':main()
