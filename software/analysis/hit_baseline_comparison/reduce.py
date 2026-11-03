#!/usr/bin/env python3
"""Reduce matched direct Geant4 sensitive-placement counts, preserving covariance."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

EDGES = np.linspace(-4,4,81)
COMPONENTS = ('pixel','short_strip','long_strip','total')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def profile(eta, values, edges=EDGES):
    values=np.asarray(values,dtype=float)
    index=np.searchsorted(edges,eta,side='right')-1
    if np.any((index<0)|(index>=len(edges)-1)):
        raise ValueError('Ray outside retained eta support')
    if values.ndim!=2 or values.shape!=(len(eta),4) or np.any(values<0) or np.any(values!=np.floor(values)):
        raise ValueError('Invalid integer crossing counts')
    np.testing.assert_array_equal(values[:,:3].sum(axis=1),values[:,3])
    n=np.bincount(index,minlength=len(edges)-1)
    if np.any(n<2):
        raise ValueError('Insufficient eta-bin occupancy')
    means=np.stack([np.bincount(index,weights=v,minlength=len(n))/n for v in values.T],axis=1)
    variances=np.stack([np.maximum(0,np.bincount(index,weights=v*v,minlength=len(n))/n-means[:,i]**2)/n
                        for i,v in enumerate(values.T)],axis=1)
    cov=np.empty((len(n),3,3))
    for i in range(3):
        for j in range(3):
            cov[:,i,j]=(np.bincount(index,weights=values[:,i]*values[:,j],minlength=len(n))/n-means[:,i]*means[:,j])/n
    np.testing.assert_allclose(cov.sum(axis=(1,2)),variances[:,3],rtol=1e-9,atol=1e-13)
    return {'counts':n.tolist(),'quantities':{c:{'mean':means[:,i].tolist(),'variance':variances[:,i].tolist(),
        'zero_count_rays':np.bincount(index,weights=values[:,i]==0,minlength=len(n)).astype(int).tolist()}
        for i,c in enumerate(COMPONENTS)},'component_covariance_of_mean':cov.tolist(),
        'global_mean':dict(zip(COMPONENTS,values.mean(axis=0).tolist()))}


def load_case(directory):
    metrics=json.loads((directory/'metrics.json').read_text())
    if not metrics.get('completed') or metrics['lifecycle']['aborted'] or not metrics['lifecycle']['finished']:
        raise ValueError('Incomplete Geant4 run')
    if metrics['hits_sha256']!=sha(directory/'hits.csv'):
        raise ValueError('Changed hit table')
    n=metrics['settings']['events']*metrics['settings']['tracks_per_event']
    settings=metrics['settings']
    if (n!=100000 or settings['seed']!=228 or settings['eta']!=[-4,4] or
            settings['phi_degrees']!=[0,360] or settings['threads']!=1 or settings['charge']!=0):
        raise ValueError('Unexpected matched hit campaign settings')
    table=np.genfromtxt(directory/'hits.csv',delimiter=',',names=True,dtype=None,encoding='utf-8')
    if len(table)!=n or len(set(zip(table['event_id'],table['track_id'])))!=n:
        raise ValueError('Missing or duplicate rays')
    if any(not np.all(np.isfinite(table[k])) for k in table.dtype.names):
        raise ValueError('Nonfinite hit-table field')
    np.testing.assert_allclose(sum(table[k]**2 for k in ('dx','dy','dz')),1.,rtol=0,atol=2e-14)
    event_counts=np.bincount(table['event_id'])
    if len(event_counts)!=metrics['settings']['events'] or np.any(event_counts!=metrics['settings']['tracks_per_event']):
        raise ValueError('Event accounting mismatch')
    if any(np.any(table[k]!=0) for k in ('x_mm','y_mm','z_mm')):
        raise ValueError('Expected origin vertices')
    values=np.stack([table[c] for c in COMPONENTS],axis=1)
    result=profile(table['eta'],values)
    result['rays']=n
    result['native_checks']=metrics['hit_counter_report']
    result['source_hits_sha256']=metrics['hits_sha256']
    result['source_metrics_sha256']=sha(directory/'metrics.json')
    result['settings']=metrics['settings']
    result['geometry_inputs']={k:metrics[k] for k in ('compact_sha256','materials_sha256','factories')}
    if int(values[:,3].sum())!=metrics['hit_counter_report']['distinct_hits']:
        raise ValueError('Native distinct hit count does not close')
    if int(table['sensitive_steps'].sum())!=metrics['hit_counter_report']['positive_sensitive_steps']:
        raise ValueError('Native step count does not close')
    return table,values,result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--old',type=Path,required=True)
    ap.add_argument('--current',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    old,old_values,old_profile=load_case(args.old)
    current,current_values,current_profile=load_case(args.current)
    bank=['event_id','track_id','eta','phi','x_mm','y_mm','z_mm','dx','dy','dz']
    for key in bank:
        np.testing.assert_array_equal(old[key],current[key],err_msg='Generated ray bank differs: '+key)
    delta=current_values-old_values
    paired={c:{'mean_current_minus_old':float(delta[:,i].mean()),
               'paired_ray_sampling_sem':float(delta[:,i].std()/np.sqrt(len(delta)))} for i,c in enumerate(COMPONENTS)}
    result={'schema_version':1,'edges':EDGES.tolist(),'components':list(COMPONENTS),
        'definition':'Distinct positive-length DD4hep-sensitive physical placements per generated neutral straight ray; chips, overlaps and both strip faces count separately',
        'normalization':'Every generated ray, including zero component/total crossings',
        'variance_convention':'Population SEM squared M2/N^2; total includes component covariance',
        'pairing':{'exact_equal_generated_ray_fields':bank,'rays':len(old),'changes':paired},
        'baselines':{'old':old_profile,'current':current_profile},'reducer_sha256':sha(__file__)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'old':old_profile['global_mean'],'current':current_profile['global_mean'],'paired_changes':paired},indent=2))


if __name__=='__main__':main()
