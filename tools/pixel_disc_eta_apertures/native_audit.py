#!/usr/bin/env python3
"""Matched native ACTS checks of retained hits and explicit out-of-scope losses."""
import argparse
import copy
import importlib.util
import json
import math
from pathlib import Path
import sys

SPEC = importlib.util.spec_from_file_location('eta_model', Path(__file__).with_name('study.py'))
model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)
sys.path.insert(0, str(model.ROOT/'tools/module_layout'))
import acts_validate
sys.path.pop(0)


def cohort(name, cfg, own, discs, before):
    tracks = model.witnesses(name, cfg, discs)
    for witness in list(tracks):
        for charge in [-1.,1.]:
            track=copy.deepcopy(witness)
            delta=model.np.asarray(track['target_point_mm'])-model.np.asarray(track['origin_mm'])
            distance=math.hypot(*delta[:2])
            k=-model.intersections.KAPPA_MM*charge*own['max_abs_field_T']/own['pt_min_GeV']
            arc=2*math.asin(abs(k)*distance/2)/abs(k)
            track.update(eta=math.asinh(delta[2]/arc),phi=math.atan2(delta[1],delta[0])-k*arc/2,
                         charge=charge,field_T=own['max_abs_field_T'],cohort='first-retained-ring-bent-witness')
            if abs(track['eta'])>own['eta_max']:
                raise ValueError('Bent witness left the eta scope')
            tracks.append(track)
    for side in [-1, 1]:
      for z in [-150., 150.]:
       for eta in [3.95, 4.]:
        for field in own['native_fields_T']:
         for charge in [-1., 1.]:
            index = len(tracks)
            x,y = [(-1.,-1.),(-1.,1.),(1.,-1.),(1.,1.)][index%4]
            tracks.append(dict(eta=side*eta, phi=(index*.3819660112501051)%(2*math.pi),
                               origin_mm=[x,y,z], pt_GeV=own['pt_min_GeV'], field_T=field, charge=charge, cohort='native-boundary'))
    random = [t for t in model.tracks(own) if t['cohort']=='seeded-off-grid' and t['charge']!=0.]
    tracks += random[:own['native_random_tracks']]
    # The original detector has genuine hits beyond eta4: retain those losses as controls.
    for side in [-1, 1]:
        layer = f'pixel_disc_{side:+d}_9'
        p = next(p for p in before['modules'] if p['layer_id']==layer and p['row']==0)
        c = p['center_mm']
        tracks.append(dict(eta=math.asinh(c[2]/math.hypot(*c[:2])), phi=math.atan2(c[1],c[0]),
                           origin_mm=[0.,0.,0.], pt_GeV=1., field_T=0., charge=1.,
                           target_patch_id=p['id'], cohort='out-of-scope-eta-control'))
    return tracks


def run(run_dir, output, acts_source):
    own, support, cfg, limits = model.inputs()
    screen = json.loads((run_dir/'screening.json').read_text())
    output.mkdir(parents=True, exist_ok=True)
    result = dict(status=own['status'], variants={})
    for name in model.VARIANTS:
        discs = screen['variants'][name]['positive_discs']
        before = model.assembly(name,cfg,discs,trimmed=False)
        after = model.assembly(name,cfg,discs,trimmed=True)
        tracks = cohort(name,cfg,own,discs,before)
        outputs = []
        for label, layout in [('before',before),('after',after)]:
            dest = output/name/label
            native = acts_validate.validate(layout,tracks,dest,acts_source=acts_source,
                        host_radius_mm=own['host_radius_mm'],host_half_z_mm=own['host_half_z_mm'])
            if not native['passed']:
                raise ValueError('Native ACTS/oracle mismatch')
            outputs.append(native)
            print(json.dumps(dict(variant=name,phase=label,tracks=native['tracks_requested'],passed=native['passed'])),flush=True)
        losses = []
        controls = []
        for i,track in enumerate(tracks):
            a,b = [set(r['per_track'][i]['observed_patch_hits']) for r in outputs]
            if track['cohort']=='out-of-scope-eta-control':
                if track['target_patch_id'] not in a or track['target_patch_id'] in b:
                    raise ValueError('Out-of-scope control failed to expose intentional removed hit')
                controls.append(dict(track=i,eta=track['eta'],removed_hits=sorted(a-b)))
            elif a!=b:
                losses.append(dict(track=i,removed_hits=sorted(a-b),extra_hits=sorted(b-a)))
            if track['cohort'].startswith('first-retained-ring') and track['target_patch_id'] not in b:
                raise ValueError('Native first retained ring witness missing')
        if losses:
            raise ValueError('Native in-scope baseline hit changed')
        exhaustive = {}
        witness = next(t for t in tracks if t['cohort']=='first-retained-ring-bent-witness' and t['target_point_mm'][2]>3000)
        for label,layout in [('before',before),('after',after)]:
            leaf = dict(modules=[p for p in layout['modules'] if p['layer_id']=='pixel_disc_+1_9'])
            dest = output/name/(label+'-exhaustive')
            native = acts_validate.validate(leaf,[witness],dest,acts_source=acts_source,host_radius_mm=own['host_radius_mm'],host_half_z_mm=own['host_half_z_mm'],exhaustive=True)
            if not native['passed'] or witness['target_patch_id'] not in native['per_track'][0]['observed_patch_hits']:
                raise ValueError('Exhaustive retained-ring control failed')
            exhaustive[label] = dict(passed=native['passed'],patches=native['active_patches'],
                                    native_sha256=model.digest(dest/'native-target-audit.json'))
        result['variants'][name] = dict(in_scope_tracks=len(tracks)-len(controls),out_of_scope_controls=controls,
                    changed_in_scope_hit_sets=losses,exhaustive=exhaustive,
                    audits={label:{**{k:v for k,v in r.items() if k!='per_track'},'per_track_sha256':model.digest(output/name/label/'native-target-audit.json')} for label,r in zip(['before','after'],outputs)})
    result['provenance'] = dict(screening_sha256=model.digest(run_dir/'screening.json'),producer_sha256=model.digest(__file__),
                               scope='ACTS finite supporting-plane/RectangleBounds audit, not global navigation or passive/material/fitted-track validation. Neutral trajectories are audited analytically and by equivalent charged zero-field controls; native binding accepts +/-1 only.')
    (output/'acts.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--acts-source',type=Path,required=True)
    args=parser.parse_args()
    run(args.run,args.output,args.acts_source)
