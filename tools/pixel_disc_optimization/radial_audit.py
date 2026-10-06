#!/usr/bin/env python3
"""Matched native ACTS finite-plane audit of the revised radial assemblies."""
import argparse
import json
from pathlib import Path

import audit
import radial
from study import digest


def layouts(cfg, raw):
    _, baseline, discs = audit.layouts(cfg, [])
    proposed = []
    radial.check_datums(cfg, [d['proposed_z_mm'] for d in discs])
    for k, d in enumerate(discs):
        modules = radial.stagger(raw, cfg, abs(d['proposed_z_mm']))
        patches = radial.active_patches(modules, cfg)
        for m in patches:
            m.update(id=m['id']+k*10000, sensor_id=m['sensor_id']+k*10000,
                     module_id=m['module_id']+k*10000, layer_id=d['layer'])
            m['center_mm'][2] *= d['side']
            if d['side'] < 0:
                m['u'] = [-x for x in m['u']]
        proposed.extend(patches)
    if len({m['id'] for m in proposed})!=len(proposed):
        raise ValueError('Duplicate active patch IDs')
    return dict(modules=proposed), baseline, discs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--screening', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--acts-source', type=Path, required=True)
    a = p.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
    cfg = radial.load_config(); report = json.loads(a.screening.read_text()); row = report['selected']
    raw, _ = radial.candidates(cfg, row['radial_margin_mm'], row['phi_margin_mm'], row['policy'])
    new, old, discs = layouts(cfg, raw); tracks = audit.tracks(discs)
    first = dict(modules=[m for m in new['modules'] if m['layer_id']==discs[0]['layer']])
    outputs = {}; compact = {}
    for name, layout, ts, exhaustive in [('candidate', new, tracks, False), ('baseline', old, tracks, False), ('exhaustive', first, tracks[:6], True)]:
        result = audit.acts_validate.validate(layout, ts, a.output/name, acts_source=a.acts_source,
                                             host_radius_mm=234., host_half_z_mm=3150., exhaustive=exhaustive)
        outputs[name] = result
        by_id = {m['id']:m['layer_id'] for m in layout['modules']}
        compact[name] = {k:v for k, v in result.items() if k!='per_track'}
        compact[name]['tracks_missing_target_disc'] = [dict(track=t['track'], input=t['input']) for t in result['per_track'] if not any(by_id[i]==t['input']['target_layer'] for i in t['observed_patch_hits'])]
        compact[name]['per_track_sha256'] = digest(a.output/name/'native-target-audit.json')
    compact['input_provenance'] = dict(screening_sha256=digest(a.screening), config_sha256=digest(Path(radial.__file__).with_name('radial-inputs.json')),
                                       audit_code_sha256=digest(__file__), patches_per_disc=len(first['modules']), all_disc_patches=len(new['modules']))
    (a.output/'acts-summary.json').write_text(json.dumps(compact, indent=2, allow_nan=False)+'\n')
    print(json.dumps({n:dict(passed=r['passed'], tracks=r['tracks_requested'], native_targets=r['reached_native_targets'], missing_target_disc=len(compact[n]['tracks_missing_target_disc'])) for n, r in outputs.items()}, indent=2))
    if not all(r['passed'] and not compact[n]['tracks_missing_target_disc'] for n, r in outputs.items()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
