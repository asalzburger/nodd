#!/usr/bin/env python3
"""Replay compact DES043 calculations and verify committed figure hashes."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import model


def compare(a,b,path='summary'):
    if type(a) is dict:
        if a.keys()!=b.keys():raise ValueError(path+': keys differ')
        for k in a:compare(a[k],b[k],path+'.'+k)
    elif type(a) is list:
        if len(a)!=len(b):raise ValueError(path+': lengths differ')
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+f'[{i}]')
    elif isinstance(a,(int,float)) and not isinstance(a,bool):
        if not math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-10):raise ValueError(path+': numeric mismatch')
    elif a!=b:raise ValueError(path+': value mismatch')


def main():
    report=model.ROOT/'docs/validation/DES-043';expected=json.loads((report/'summary.json').read_text())
    with tempfile.TemporaryDirectory(prefix='DES043-') as tmp:
        path=Path(tmp)/'summary.json'
        subprocess.run([sys.executable,'-B',str(model.HERE/'model.py'),'--output',str(path)],check=True,stdout=subprocess.DEVNULL)
        compare(expected,json.loads(path.read_text()))
    manifest=json.loads((report/'figures/manifest.json').read_text())
    if model.sha(report/'summary.json')!=manifest['input_sha256']:raise ValueError('Figure inputs stale')
    if model.sha(model.HERE/'plot.py')!=manifest['plot_sha256']:raise ValueError('Plot producer stale')
    for path,digest in manifest['files'].items():
        if model.sha(report/'figures'/path)!=digest:raise ValueError('Figure bytes changed: '+path)
    if any(x['failed_rays'] for x in expected['coverage']['checks']):raise ValueError('Candidate coverage failure')
    if not all(x['passed'] for x in expected['packing']):raise ValueError('Candidate trunk failure')
    plumbing=expected['cooling_routes']
    if plumbing['pad_contacts']['failed_modules']:raise ValueError('Uncooled module saddle')
    if not plumbing['interloop_clearance']['passed'] or not all(x['passed'] for x in plumbing['same_loop_clearance'].values()):raise ValueError('Cooling source routing conflict')
    native=json.loads((report/'native-summary.json').read_text())
    if native['status']!='PASS' or native['errors'] or native['overlap_count']:raise ValueError('Native evidence failed')
    if native['identifiers']!={'passed':True,'errors':[],'unique_volume_ids':792,'grid':[640,48],'cells_checked':3960}:raise ValueError('Native sensitive evidence incomplete')
    if native['counts']['sensitive']!=792 or native['window_probes']!=7200:raise ValueError('Native payload/probe evidence incomplete')
    if native['pipe_contact_screen']['definite_missing_contacts']:raise ValueError('Native pipe contact evidence failed')
    for path,digest in native['provenance']['generated_source'].items():
        if model.sha(model.ROOT/path)!=digest:raise ValueError('Native source evidence stale: '+path)
    if native['curator_sha256']!=model.sha(model.HERE/'curate_native.py'):raise ValueError('Native curator stale')
    barrel=json.loads((report/'barrel-summary.json').read_text())
    if not barrel['passed'] or barrel['native_geometry_constructed']:raise ValueError('Barrel source evidence invalid')
    if barrel['provenance']['input_sha256']!=model.sha(model.HERE/'inputs.json') or barrel['provenance']['producer_sha256']!=model.sha(model.HERE/'barrel_interfaces.py'):raise ValueError('Barrel source evidence stale')
    for path,digest in barrel['provenance']['source_sha256'].items():
        if model.sha(model.ROOT/path)!=digest:raise ValueError('Barrel baseline source stale')
    print(f'PASS: numerical replay, contacts/coverage/packing, {len(manifest["files"])}figure fingerprints, native evidence bindings and barrel source evidence; no event data needed.')


if __name__=='__main__':main()
