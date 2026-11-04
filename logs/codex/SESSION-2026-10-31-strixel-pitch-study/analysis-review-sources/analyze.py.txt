#!/usr/bin/env python3
"""Retain and replay paired DES042 truth-associated pitch sensitivity."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'software/analysis/truth_tracking'))
from metrics import QUANTITIES, binomial_interval, perigee_observables

PROBABILITY=.6826894921370859
PITCHES=(.5,1.,1.5,2.)


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump_gzip(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(gzip.compress((json.dumps(value,allow_nan=False,separators=(',',':'))+'\n').encode(),mtime=0))


def basic(values,minimum=30):
    values=np.asarray(values,dtype=float)
    finite=values[np.isfinite(values)]
    out=dict(entries=int(finite.size),nonfinite=int(values.size-finite.size))
    names=('mean','median','std','rms','width68','mean_se')
    out.update({name:None for name in names})
    if finite.size>=minimum:
        lo,med,hi=np.quantile(finite,[(1-PROBABILITY)/2,.5,(1+PROBABILITY)/2])
        sd=float(np.std(finite,ddof=1))
        out.update(mean=float(np.mean(finite)),median=float(med),std=sd,
                   rms=float(np.sqrt(np.mean(finite**2))),width68=float((hi-lo)/2),
                   mean_se=sd/np.sqrt(finite.size))
    return out


def paired_widths(values,replicates=400,seed=74042,minimum=30):
    """Resample the same generated event IDs for each pitch; preserve NaNs.

    Widths condition on each variant's successful finite fits. A second result
    conditions on the intersection of all four variants to expose attrition.
    """
    values=np.asarray(values,dtype=float)
    if values.ndim!=2 or values.shape[0]!=4:
        raise ValueError('Require four pitch rows with common generated-event columns')
    if replicates<2:raise ValueError('Need at least two bootstrap replicates')
    rng=np.random.default_rng(seed)
    output=[]
    for mode,selected in [('all_success',values),('common_success',values[:,np.all(np.isfinite(values),axis=0)])]:
        stats=[basic(row,minimum) for row in selected]
        point=np.array([np.nan if x['width68'] is None else x['width68'] for x in stats])
        widths=np.full((replicates,4),np.nan)
        if selected.shape[1]>=minimum:
            for start in range(0,replicates,32):
                stop=min(replicates,start+32)
                ids=rng.integers(selected.shape[1],size=(stop-start,selected.shape[1]))
                for pitch_index,row in enumerate(selected):
                    draw=row[ids]
                    valid=np.sum(np.isfinite(draw),axis=1)>=minimum
                    if np.any(valid):
                        qs=np.nanquantile(draw[valid],[(1-PROBABILITY)/2,(1+PROBABILITY)/2],axis=1)
                        widths[start+np.flatnonzero(valid),pitch_index]=(qs[1]-qs[0])/2
        cases=[]
        for index,stat in enumerate(stats):
            w=widths[:,index]
            finite=w[np.isfinite(w)]
            denom=widths[:,0]
            valid=np.isfinite(w)&np.isfinite(denom)&(denom>0)
            ratio=w[valid]/denom[valid]
            estimate=float(point[index]/point[0]) if np.isfinite(point[index]) and point[0]>0 else None
            stat.update(width68_se=float(np.std(finite,ddof=1)) if finite.size>1 else None,
                        width_bootstrap_defined=int(finite.size),
                        ratio_to_baseline=estimate,
                        ratio_bootstrap_defined=int(ratio.size),
                        ratio_se=float(np.std(ratio,ddof=1)) if ratio.size>1 else None,
                        ratio_interval68=[float(x) for x in np.quantile(ratio,[(1-PROBABILITY)/2,(1+PROBABILITY)/2])] if ratio.size>1 else None)
            cases.append(stat)
        output.append(dict(mode=mode,generated_or_common_events=int(selected.shape[1]),cases=cases))
    return output


def count_summary(array,mask):
    n=int(mask.sum())
    counts={name:int(np.count_nonzero(array[key][mask])) for name,key in [
        ('selected','audit_selected'),('fit_attempts','audit_fit_attempts'),('fit_tracks','audit_fit_tracks'),
        ('finite_fit','finite_fitted_parameters'),('native_matched','native_primary_match'),
        ('valid_covariance','valid_covariance')]}
    counts['generated']=n
    fit=array['finite_fitted_parameters'][mask]
    counts['wrong_charge']=int(np.count_nonzero(array['wrong_charge'][mask]&fit))
    out=dict(counts=counts)
    for name in ('selected','fit_tracks','finite_fit','native_matched','valid_covariance'):
        out[name+'_fraction']=binomial_interval(counts[name],n)
    out['wrong_charge_of_finite']=binomial_interval(counts['wrong_charge'],counts['finite_fit'])
    return out


def paired_bin(arrays,mask,replicates,seed):
    cases=[count_summary(a,mask) for a in arrays]
    for c in cases:c['quantities']={}
    for qi,quantity in enumerate(QUANTITIES):
        residual=np.stack([a[quantity+'_residual'][mask] for a in arrays])
        paired=paired_widths(residual,replicates,seed+qi)
        for i,case in enumerate(cases):
            case['quantities'][quantity]=dict(
                residual=paired[0]['cases'][i],common_success_residual=paired[1]['cases'][i],
                common_success_events=paired[1]['generated_or_common_events'],
                pull=basic(arrays[i][quantity+'_pull'][mask]))
    # Pair the all-generated fit fractions as well as the conditional widths.
    ids=np.flatnonzero(mask)
    for i,case in enumerate(cases):
        base=arrays[0]['finite_fitted_parameters'][ids].astype(float)
        own=arrays[i]['finite_fitted_parameters'][ids].astype(float)
        diff=own-base
        case['finite_fit_fraction_difference_to_baseline']=float(diff.mean()) if ids.size else None
        case['finite_fit_fraction_difference_se']=float(diff.std(ddof=1)/np.sqrt(ids.size)) if ids.size>1 else None
        case['discordant_fit_events']=int(np.count_nonzero(diff))
    return cases


def sanitize(value):
    """Keep logical roles and hashes without publishing machine-local paths."""
    if isinstance(value,dict):return {sanitize(k):sanitize(v) for k,v in value.items()}
    if isinstance(value,list):return [sanitize(v) for v in value]
    if isinstance(value,str) and value.startswith('/'):
        path=Path(value)
        for prefix,label in [(ROOT,'repository'),(ROOT.parent,'workspace')]:
            try:return label+'/'+str(path.relative_to(prefix))
            except ValueError:pass
        return 'external/'+path.name
    return value


def retain(source,output,pattern):
    """Cross-check full arrays before retaining compact per-event observables."""
    output.mkdir(parents=True,exist_ok=True)
    retained=[]
    for path in sorted(source.glob(pattern+'/run-report.json')):
        report=json.loads(path.read_text())
        if report['outcome']!='completed':raise ValueError('Incomplete native run: '+str(path))
        event_path=path.parent/'events.npz'
        if digest(event_path)!=report['reduction']['event_array_sha256']:
            raise ValueError('Native event-array hash differs')
        with np.load(event_path,allow_pickle=False) as stream:
            a={name:stream[name] for name in stream.files}
        recalculated,flags=perigee_observables(a['fitted'],a['truth'],a['covariance'])
        for quantity in QUANTITIES:
            for kind in ('residual','pull'):
                if not np.allclose(a[quantity+'_'+kind],recalculated[quantity][kind],rtol=0,atol=0,equal_nan=True):
                    raise ValueError('Stored observable differs from independently replayed perigee formula')
        for key,value in flags.items():
            if not np.array_equal(a[key],value):raise ValueError('Stored fit/covariance flag differs')
        if len(a['event'])!=report['requested_events'] or not np.all(a['audit_generated']==1):
            raise ValueError('Generated-event denominator differs')
        if not np.array_equal(a['event'],np.arange(len(a['event']))):
            raise ValueError('Native events do not have contiguous unique identities')
        kept={key:value for key,value in a.items() if key not in ('fitted','truth','covariance')}
        target=output/'events'/f'{path.parent.name}.npz'
        target.parent.mkdir(exist_ok=True)
        np.savez_compressed(target,**kept)
        retained.append(dict(case=path.parent.name,report=sanitize(report),
            native_report_sha256=digest(path),native_event_array_sha256=digest(event_path),
            retained_event_array_sha256=digest(target),events_file=str(target.relative_to(output))))
    if not retained:raise ValueError('No completed native runs match requested pattern')
    inventory=dict(schema_version=1,status='PROTOTYPE',reports=retained,
        metrics_source_sha256=digest(ROOT/'software/analysis/truth_tracking/metrics.py'),
        retention_source_sha256=digest(__file__),
        retention_check='Full fitted/truth/covariance independently recomputed every stored residual,pull and flag exactly before compact retention',
        provenance_limit='Native preparation omitted metrics.py fingerprint; retention separately records it and verifies all outputs from full fitted/truth/covariance.')
    dump_gzip(output/'native-reports.json.gz',inventory)
    return inventory


def analyze(output,inventory,replicates=400,pilot=False):
    groups=[]
    inputs=inventory['reports']
    for pt in sorted({x['report']['pt_GeV'] for x in inputs}):
        reports=sorted([x for x in inputs if x['report']['pt_GeV']==pt],key=lambda x:x['report']['pitch_mm'])
        if [x['report']['pitch_mm'] for x in reports]!=list(PITCHES):
            raise ValueError('Each momentum needs exactly the four pitch cases')
        arrays=[]
        for item in reports:
            path=output/item['events_file']
            if digest(path)!=item['retained_event_array_sha256']:raise ValueError('Retained events changed')
            with np.load(path,allow_pickle=False) as stream:arrays.append({key:stream[key] for key in stream.files})
        n=len(arrays[0]['event'])
        if not pilot and n!=20000:raise ValueError('Production requires20000events/case')
        for own in arrays[1:]:
            for key in ('event','eta','pt_GeV','charge','audit_generated','audit_simhits'):
                if not np.array_equal(own[key],arrays[0][key]):raise ValueError('Pairing differs: '+key)
        reductions=[x['report']['reduction'] for x in reports]
        # Native payload hashes include physical simhits independently of response.
        pair_fields=['generated_sample_sha256','transport_pairing']
        required={'all_payload_sha256','primary_payload_sha256','all_simhits','primary_simhits'}
        if any(not required.issubset(x.get('transport_pairing',{})) for x in reductions):
            raise ValueError('Missing generated/all-hit/primary-hit pairing fingerprints')
        for key in pair_fields:
            if len({json.dumps(x[key],sort_keys=True) for x in reductions})!=1:
                raise ValueError('Native transport sample fingerprint differs: '+key)
        prep=[x['report']['preparation'] for x in reports]
        if any(not all(x['balanced_comparison'].values()) for x in prep):
            raise ValueError('Missing balanced geometry/material comparison')
        counts=[x['sensor_counts'] for x in prep]
        if not all(x==counts[0] for x in counts):raise ValueError('Native sensor inventory differs')
        hashes=[x['files_sha256'] for x in prep]
        if not all(x==hashes[0] for x in hashes):raise ValueError('Native executable source/configuration/binary hashes differ')
        configurations=[]
        for pitch,item in zip(PITCHES,reports):
            config=json.loads(json.dumps(item['report']['campaign']))
            if config['digitization']['short_strip_pitch_mm']!=[.075,pitch]:
                raise ValueError('Native response pitch differs from case label')
            config['digitization']['short_strip_pitch_mm'][1]=.5
            configurations.append(config)
            if not pilot and not item['report']['residual_convention'].startswith('fitted minus truth'):
                raise ValueError('Native residual-convention metadata differs')
        if not all(x==configurations[0] for x in configurations):
            raise ValueError('A native campaign property other than short-strip pitch changed')
        cases=[dict(pitch_v_mm=p,case=item['case'],events=n,eta_profiles=[],abs_eta_profiles=[],summary_regions=[])
               for p,item in zip(PITCHES,reports)]
        bins=[('global',0,4,np.ones(n,dtype=bool))]
        eta=arrays[0]['eta']
        for projection,edges in [('eta_profiles',np.linspace(-4,4,33)),('abs_eta_profiles',np.linspace(0,4,9))]:
            values=eta if projection=='eta_profiles' else np.abs(eta)
            for i,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
                bins.append((projection,float(lo),float(hi),(values>=lo)&((values<=hi) if i==len(edges)-2 else values<hi)))
        for lo,hi in [(0,1),(1,2.5),(2.5,4)]:
            bins.append(('summary_regions',lo,hi,(np.abs(eta)>=lo)&(np.abs(eta)<=hi if hi==4 else np.abs(eta)<hi)))
        for bi,(projection,lo,hi,mask) in enumerate(bins):
            result=paired_bin(arrays,mask,replicates,74042+int(pt)*10000+bi*10)
            for case,stats in zip(cases,result):
                if projection=='global':case['global']=stats
                else:case[projection].append(dict(low=lo,high=hi,**stats))
        groups.append(dict(pt_GeV=pt,pairing={key:reductions[0][key] for key in pair_fields},cases=cases))
    report=dict(schema_version=1,status='PROTOTYPE',response='Native geometric digital; pitch-derived clustered covariance; ideal uncalibrated response',
        geometry='PR104 balanced',field_Bz_T=3,simulations=['fatras'],residual_convention='fitted minus truth',
        bootstrap=dict(replicates=replicates,probability=PROBABILITY,minimum_entries=30,
                       pairing='Same generated-event bootstrap indices for all four variants; common-success control conditions on intersection'),
        uncertainty='Statistical only; no calibrated-response, material-map, field or detector-model systematic coverage',
        provenance=dict(native_reports_sha256=digest(output/'native-reports.json.gz'),analyzer_sha256=digest(__file__),
                        metrics_sha256=digest(ROOT/'software/analysis/truth_tracking/metrics.py')),
        groups=groups)
    dump_gzip(output/'profiles.json.gz',report)
    with (output/'summary.csv').open('w',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(['pt_GeV','pitch_v_mm','projection','eta_low','eta_high','generated','finite_fit','native_matched','quantity','width68','width68_se','ratio','ratio_low68','ratio_high68','common_success_ratio','residual_std','residual_mean','pull_mean','pull_std'])
        for group in groups:
            for case in group['cases']:
                for projection,points in [('global',[dict(low=0,high=4,**case['global'])]),('eta',case['eta_profiles']),('abs_eta',case['abs_eta_profiles']),('summary_region',case['summary_regions'])]:
                    for point in points:
                        for q,s in point['quantities'].items():
                            r=s['residual'];bounds=r['ratio_interval68'] or [None,None]
                            writer.writerow([group['pt_GeV'],case['pitch_v_mm'],projection,point['low'],point['high'],point['counts']['generated'],point['counts']['finite_fit'],point['counts']['native_matched'],q,r['width68'],r['width68_se'],r['ratio_to_baseline'],*bounds,s['common_success_residual']['ratio_to_baseline'],r['std'],r['mean'],s['pull']['mean'],s['pull']['std']])
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,help='Native run directory; omit to replay retained arrays')
    parser.add_argument('--pattern',default='full-v3-*')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--replicates',type=int,default=400)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    inventory=(retain(args.source,args.output,args.pattern) if args.source else
               json.loads(gzip.decompress((args.output/'native-reports.json.gz').read_bytes())))
    report=analyze(args.output,inventory,args.replicates,args.pilot)
    print('Retained and analyzed',len(inventory['reports']),'native cases;',len(report['groups']),'paired momentum groups')


if __name__=='__main__':main()
