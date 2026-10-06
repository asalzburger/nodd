#!/usr/bin/env python3
"""Matched native ACTS finite-plane audit; expected coverage misses are retained."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys

SPEC=importlib.util.spec_from_file_location('variant_model',Path(__file__).with_name('study.py'))
model=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(model)
sys.path.insert(0,str(model.ROOT/'tools/pixel_disc_optimization'))
import audit


def layout(raw,cfg,discs):
    patches=[]
    for k,d in enumerate(discs):
        placed=model.placed_modules(raw,cfg,abs(d['proposed_z_mm']))
        for p in model.radial.active_patches(placed,cfg):
            p.update(id=p['id']+k*10000,sensor_id=p['sensor_id']+k*10000,module_id=p['module_id']+k*10000,layer_id=d['layer'])
            p['center_mm'][2]*=d['side']
            if d['side']<0:p['u']=[-x for x in p['u']]
            patches.append(p)
    if len({p['id'] for p in patches})!=len(patches):raise ValueError('Nonunique patch IDs')
    return dict(modules=patches)


def run(run_dir,out,acts_source):
    own,cfg,limits,prior=model.inputs()
    _,_,discs=audit.layouts(cfg,[])
    model.radial.check_datums(cfg,[d['proposed_z_mm'] for d in discs])
    tracks=audit.tracks(discs)
    for d in discs:
        for radius in own['edge_controls_mm']:
            for phi in [0.,1.,2.]:
                tracks.append(dict(target_layer=d['layer'],target_radius_mm=radius,eta=math.asinh(d['proposed_z_mm']/radius),phi=phi,field_T=0.,pt_GeV=1.,charge=1.,origin_mm=[0.,0.,0.]))
    out.mkdir(parents=True,exist_ok=True);result={}
    for name in ['eight-single','four-single-two-quad']:
        raw=json.loads((run_dir/(name+'-layout.json')).read_text())['raw_modules']
        assembly=layout(raw,cfg,discs)
        for suffix,geo,ts,exhaustive in [('',assembly,tracks,False),('-exhaustive',dict(modules=[p for p in assembly['modules'] if p['layer_id']==discs[0]['layer']]),tracks[:6],True)]:
            key=name+suffix; dest=out/key
            native=audit.acts_validate.validate(geo,ts,dest,acts_source=acts_source,host_radius_mm=234.,host_half_z_mm=3150.,exhaustive=exhaustive)
            by_id={p['id']:p['layer_id'] for p in geo['modules']}
            misses=[dict(track=t['track'],input=t['input']) for t in native['per_track'] if not any(by_id[i]==t['input']['target_layer'] for i in t['observed_patch_hits'])]
            result[key]={k:v for k,v in native.items() if k!='per_track'}
            result[key].update(tracks_missing_target_disc=misses,per_track_sha256=model.reference.digest(dest/'native-target-audit.json'))
            print(json.dumps(dict(variant=key,passed=native['passed'],tracks=native['tracks_requested'],misses=len(misses))),flush=True)
            if not native['passed']:raise ValueError('ACTS/oracle mismatch')
    result['provenance']=dict(screening_sha256=model.reference.digest(run_dir/'screening.json'),audit_sha256=model.reference.digest(__file__),scope='Native EigenStepper supporting-plane finite-bounds/identifier audit. Expected target misses retained; vacuum transport without passive support or fitted resolution.')
    (out/'acts.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--acts-source',type=Path,required=True)
    a=p.parse_args();run(a.run,a.output,a.acts_source)
