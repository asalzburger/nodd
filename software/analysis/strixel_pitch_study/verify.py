#!/usr/bin/env python3
"""Offline accounting/source audit of compact DES042 native evidence."""
import argparse
import gzip
import json
from pathlib import Path

import numpy as np

from analyze import ROOT, QUANTITIES, basic, count_summary, digest, validate_comparison, validate_matrix, analyze
from services import evaluate


def same_number(left,right):
    if left is None or right is None:return left is right
    return bool(np.isclose(left,right,rtol=1e-11,atol=1e-14))


def verify(directory,bootstrap=False):
    inventory=json.loads(gzip.decompress((directory/'native-reports.json.gz').read_bytes()))
    data=json.loads(gzip.decompress((directory/'profiles.json.gz').read_bytes()))
    if data['provenance']['native_reports_sha256']!=digest(directory/'native-reports.json.gz'):
        raise ValueError('Native report inventory changed')
    for name,path in [('analyzer_sha256',ROOT/'software/analysis/strixel_pitch_study/analyze.py'),
                      ('metrics_sha256',ROOT/'software/analysis/truth_tracking/metrics.py')]:
        if data['provenance'][name]!=digest(path):raise ValueError('Analysis source changed: '+name)
    reports={x['case']:x for x in inventory['reports']}
    validate_matrix([x['report'] for x in inventory['reports']])
    scalars=0
    for group in data['groups']:
        arrays=[]
        for case in group['cases']:
            item=reports[case['case']];report=item['report']
            path=directory/item['events_file']
            if digest(path)!=item['retained_event_array_sha256']:raise ValueError('Retained native array changed')
            with np.load(path,allow_pickle=False) as stream:arrays.append({key:stream[key] for key in stream.files})
            if report['requested_events']!=20000 or report['outcome']!='completed':raise ValueError('Incomplete campaign')
            validate_comparison(report['preparation']['balanced_comparison'])
            for key,expected in group['pairing'].items():
                if report['reduction'][key]!=expected:raise ValueError('Native transport pairing evidence changed')
            for logical,expected in report['preparation']['files_sha256'].items():
                if logical.startswith('repository/software/'):
                    current=ROOT/logical.removeprefix('repository/')
                    if digest(current)!=expected:raise ValueError('Executed repository source differs: '+logical)
        if len(arrays)!=4:raise ValueError('Need four pitch variants')
        for own in arrays[1:]:
            for key in ('event','eta','pt_GeV','charge','audit_generated','audit_simhits'):
                if not np.array_equal(own[key],arrays[0][key]):raise ValueError('Event pairing changed')
        eta=arrays[0]['eta']
        for projection in ('global','eta_profiles','abs_eta_profiles','summary_regions'):
            points=[c['global'] for c in group['cases']] if projection=='global' else [c[projection] for c in group['cases']]
            count=1 if projection=='global' else len(points[0])
            generated_partition=0
            for index in range(count):
                own_points=points if projection=='global' else [p[index] for p in points]
                if projection=='global':mask=np.ones(eta.size,dtype=bool)
                else:
                    lo,hi=own_points[0]['low'],own_points[0]['high']
                    x=eta if projection=='eta_profiles' else np.abs(eta)
                    mask=(x>=lo)&((x<=hi) if hi==4 else (x<hi))
                generated_partition+=int(mask.sum())
                for a,p in zip(arrays,own_points):
                    computed=count_summary(a,mask)
                    if p['counts']!=computed['counts']:raise ValueError('Retained counts differ from events')
                    for name in computed:
                        if name!='counts' and p[name]!=computed[name]:raise ValueError('Fraction interval changed')
                    diff=a['finite_fitted_parameters'][mask].astype(float)-arrays[0]['finite_fitted_parameters'][mask].astype(float)
                    checks=dict(finite_fit_fraction_difference_to_baseline=float(diff.mean()) if diff.size else None,
                                finite_fit_fraction_difference_se=float(diff.std(ddof=1)/np.sqrt(diff.size)) if diff.size>1 else None,
                                discordant_fit_events=int(np.count_nonzero(diff)))
                    if any(not same_number(p[k],v) for k,v in checks.items()):raise ValueError('Paired efficiency difference changed')
                for q in QUANTITIES:
                    rows=np.stack([a[q+'_residual'][mask] for a in arrays])
                    common=np.all(np.isfinite(rows),axis=0)
                    expected=[basic(row) for row in rows]
                    expected_common=[basic(row[common]) for row in rows]
                    for pi,p in enumerate(own_points):
                        for key,stats in [('residual',expected[pi]),('common_success_residual',expected_common[pi]),
                                          ('pull',basic(arrays[pi][q+'_pull'][mask]))]:
                            observed=p['quantities'][q][key]
                            for name,value in stats.items():
                                if not same_number(value,observed[name]):raise ValueError('Uncut point statistic changed: '+q+'/'+key+'/'+name)
                                scalars+=1
                            if key!='pull':
                                baseline=(expected if key=='residual' else expected_common)[0]['width68']
                                ratio=stats['width68']/baseline if baseline is not None and baseline>0 and stats['width68'] is not None else None
                                if not same_number(ratio,observed['ratio_to_baseline']):raise ValueError('Ratio changed')
                                if not 0<=observed['ratio_bootstrap_defined']<=data['bootstrap']['replicates']:
                                    raise ValueError('Bootstrap replicate accounting invalid')
                        if p['quantities'][q]['common_success_events']!=int(common.sum()):
                            raise ValueError('Common-success event accounting differs')
            if projection!='global' and generated_partition!=20000:raise ValueError('Eta bins do not partition generated events')
    saved=json.loads((directory/'services.json').read_text())
    current=evaluate(json.loads((ROOT/'software/analysis/strixel_pitch_study/services.json').read_text()))
    for name in ('input_sha256','baseline','module_counts','network_counts','cases'):
        if saved[name]!=current[name]:raise ValueError('Service replay changed: '+name)
    if bootstrap:
        replay=analyze(directory,inventory,replicates=data['bootstrap']['replicates'],write=False)
        if replay!=data:raise ValueError('Full deterministic bootstrap replay changed retained evidence')
    print(f'PASS: {len(reports)} native cases, paired generated/transport samples, {scalars} uncut point statistics, fraction intervals/differences, point ratios and24service cases')
    print('Full deterministic bootstrap uncertainty replay PASS' if bootstrap else 'Bootstrap uncertainties not recomputed in this point-statistic audit; use --bootstrap for full replay')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=ROOT/'docs/validation/DES-042')
    parser.add_argument('--bootstrap',action='store_true',help='Also repeat every deterministic paired bootstrap and compare all uncertainty fields')
    args=parser.parse_args();verify(args.data,args.bootstrap)


if __name__=='__main__':main()
