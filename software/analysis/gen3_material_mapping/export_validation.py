#!/usr/bin/env python3
"""Reduce an ACTS validation recording to total per-ray material profiles."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import uproot


def profile(coordinate, values, edges):
    index=np.searchsorted(edges,coordinate,side='right')-1
    if not np.all((index>=0)&(index<len(edges)-1)):
        raise ValueError('Validation coordinate outside retained truth profile support')
    counts=np.bincount(index,minlength=len(edges)-1)
    total=np.bincount(index,weights=values,minlength=len(counts))
    square=np.bincount(index,weights=values*values,minlength=len(counts))
    mean=np.divide(total,counts,out=np.zeros_like(total),where=counts>0)
    sem2=np.divide(square,counts,out=np.zeros_like(square),where=counts>0)-mean*mean
    sem2=np.divide(np.maximum(0,sem2),counts,out=np.zeros_like(sem2),where=counts>0)
    return {'counts':counts.tolist(),'mean':mean.tolist(),'variance':sem2.tolist(),
            'empty_bins':np.flatnonzero(counts==0).tolist()}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--truth',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--expected-tracks',type=int,default=100000)
    args=ap.parse_args();truth=json.loads(args.truth.read_text())
    with uproot.open(args.input) as f:
        tree=f['material_tracks']
        data=tree.arrays(['v_eta','v_phi','t_X0','t_L0'],library='np')
    n=len(data['v_eta'])
    if n!=args.expected_tracks:raise ValueError(f'Expected {args.expected_tracks} validation tracks, got {n}')
    for key,a in data.items():
        if len(a)!=n or not np.all(np.isfinite(a)):raise ValueError(f'Invalid branch {key}')
    if np.any(data['t_X0']<0) or np.any(data['t_L0']<0):raise ValueError('Negative material budget')
    coordinates={'eta':data['v_eta'].astype(float),'abs_eta':abs(data['v_eta'].astype(float)),
                 'phi':(data['v_phi'].astype(float)+np.pi)%(2*np.pi)-np.pi}
    out={'schema_version':1,'tracks':n,'tree':'material_tracks','axes':{},
         'zero_budget_tracks':{q:int(np.count_nonzero(data['t_'+q]==0)) for q in ('X0','L0')},
         'global_mean':{q:float(np.mean(data['t_'+q],dtype=float)) for q in ('X0','L0')},
         'comparison':{},'normalization':'Every generated validation ray, including zeros; ROOT population SEM squared M2/N^2',
         'source_validation_sha256':None,'source_truth_sha256':hashlib.sha256(args.truth.read_bytes()).hexdigest(),
         'source_exporter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    digest=hashlib.sha256()
    with args.input.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):digest.update(block)
    out['source_validation_sha256']=digest.hexdigest()
    for axis,coordinate in coordinates.items():
        g=truth['axes'][axis];edges=np.array(g['edges'])
        out['axes'][axis]={'edges':edges.tolist(),'quantities':{}}
        for q in ('X0','L0'):
            p=profile(coordinate,data['t_'+q].astype(float),edges)
            if sum(p['counts'])!=n:raise ValueError('Profile count closure failed')
            out['axes'][axis]['quantities'][q]=p
            actual=np.array(p['mean']);expected=np.array(g['quantities'][q]['total']['mean'])
            relative=np.divide(actual-expected,expected,out=np.zeros_like(actual),where=expected>0)
            variances=np.array(p['variance'])+np.array(g['quantities'][q]['total']['variance'])
            pull=np.divide(actual-expected,np.sqrt(variances),out=np.zeros_like(actual),where=variances>0)
            out['comparison'][axis+'_'+q]={'relative_difference':relative.tolist(),
                'maximum_absolute_relative_difference':float(np.max(abs(relative))),
                'rms_relative_difference':float(np.sqrt(np.mean(relative*relative))),
                'difference_over_combined_statistical_sem':pull.tolist(),
                'interpretation':'Descriptive comparison of two samples; no accuracy acceptance threshold applied'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'tracks':n,'zero_budget_tracks':out['zero_budget_tracks'],
                      'global_mean':out['global_mean'],'max_abs_relative_eta_X0':out['comparison']['eta_X0']['maximum_absolute_relative_difference']},indent=2))


if __name__=='__main__':main()
