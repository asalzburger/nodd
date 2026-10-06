#!/usr/bin/env python3
"""Run matched DES016 prototype/baseline sensitive-plane audits in acts-nodd."""
import argparse
import copy
import importlib.util
import json
import math
from pathlib import Path
import sys
from study import ROOT, candidates, stagger, digest
sys.path.insert(0,str(ROOT/'tools/module_layout'))
import acts_validate
sys.path.insert(0,str(ROOT/'tools/pixel_endcap_support'))
spec=importlib.util.spec_from_file_location('endcap_model',ROOT/'tools/pixel_endcap_support/model.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)


def layouts(cfg,raw):
    ec,source,_=support.load_inputs();discs=support.disc_records(source,ec)
    proposed=[];old=[]
    for k,d in enumerate(discs):
        z=abs(d['proposed_z_mm']);side=d['side']
        placed=stagger(raw,cfg,z)
        for m in placed:
            m.update(id=m['id']+k*1000,sensor_id=m['sensor_id']+k*1000,module_id=m['module_id']+k*1000,layer_id=d['layer'])
            m['center_mm'][2]*=side
            if side<0:m['v']=[-x for x in m['v']]
        proposed+=placed
        bodies={b['module_id']:b for b in source['bodies'] if b['layer_id']==d['layer']}
        newb={b['module_id']:b for b in support.proposal(list(bodies.values()),ec)[0]}
        for p in source['modules']:
            if p['layer_id']!=d['layer']:continue
            m=copy.deepcopy(p);m['center_mm'][2]=d['proposed_z_mm']+side*newb[p['module_id']]['center_mm'][2]
            old.append(m)
    return dict(modules=proposed),dict(modules=old),discs


def tracks(discs):
    result=[]
    for k,d in enumerate(discs):
        for v in [-150.,0.,150.]:
            for radius in [40.,100.,175.]:
                for field in [0.,2.]:
                    phi=(k*2.399963229728653+radius*.031+v*.003)%(2*math.pi)
                    result.append(dict(target_layer=d['layer'],target_radius_mm=radius,eta=math.asinh((d['proposed_z_mm']-v)/radius),phi=phi,field_T=field,
                                       pt_GeV=1.,charge=(-1. if k%2 else 1.),origin_mm=[0.,0.,v]))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--screening',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--acts-source',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    cfg=json.loads((ROOT/'tools/pixel_disc_optimization/inputs.json').read_text());r=json.loads(a.screening.read_text());raw=candidates(cfg,r['selected']['pitch_reduction_mm']);new,old,discs=layouts(cfg,raw);ts=tracks(discs)
    outputs={}
    for name,layout in [('candidate',new),('baseline',old)]:
        outputs[name]=acts_validate.validate(layout,ts,a.output/name,acts_source=a.acts_source,host_radius_mm=234.,host_half_z_mm=3150.)
    # Exhaustive all-plane control has no shared broad-phase candidate filter.
    first=dict(modules=[m for m in new['modules'] if m['layer_id']==discs[0]['layer']]);small=ts[:6]
    outputs['exhaustive_control']=acts_validate.validate(first,small,a.output/'exhaustive',acts_source=a.acts_source,host_radius_mm=234.,exhaustive=True)
    compact={}
    for name,r in outputs.items():
        compact[name]={k:v for k,v in r.items() if k!='per_track'}
        compact[name]['tracks_with_hit']=sum(bool(t['observed_patch_hits']) for t in r['per_track'])
        compact[name]['missed_tracks']=[dict(track=t['track'],input=t['input']) for t in r['per_track'] if not t['observed_patch_hits']]
        by_id={m['id']:m['layer_id'] for m in (first if name=='exhaustive_control' else new if name=='candidate' else old)['modules']}
        compact[name]['tracks_missing_target_disc']=[dict(track=t['track'],input=t['input']) for t in r['per_track'] if not any(by_id[p]==t['input']['target_layer'] for p in t['observed_patch_hits'])]
        compact[name]['per_track_sha256']=digest(a.output/({'exhaustive_control':'exhaustive'}.get(name,name))/'native-target-audit.json')
    (a.output/'acts-summary.json').write_text(json.dumps(compact,indent=2,allow_nan=False)+'\n')
    print(json.dumps({n:dict(passed=r['passed'],tracks=r['tracks_requested'],hits=r['reached_native_targets'],misses=len(compact[n]['missed_tracks']),seconds=r['elapsed_seconds']) for n,r in outputs.items()},indent=2))
    if not all(r['passed'] for r in outputs.values()):raise SystemExit(1)

if __name__=='__main__':main()
