#!/usr/bin/env python3
"""Freeze selected tracker review data from an explicitly chosen nODD checkout.

Pure data extraction: no native geometry, simulation or optimization is run.
The publication revision is separate from every retained execution identity.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys

REPORT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', '/tmp/nodd-tracker-tdr-matplotlib')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', type=Path, required=True)
    args = ap.parse_args()
    root = args.source_root.resolve()
    sources = {}
    def read(path):
        p = root / path
        sources[path] = sha(p)
        raw = gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes()
        return json.loads(raw)
    def module(name, path):
        sources[path] = sha(root/path)
        spec = importlib.util.spec_from_file_location(name, root/path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    sb = read('docs/validation/DES-020/phi-tilted/layout.json.gz')
    sbc = read('tools/short_strip_barrel/inputs-phi-tilted.json')
    sec = read('tools/short_strip_endcap/inputs.json')
    se_model = module('short_endcap_snapshot', 'tools/short_strip_endcap/model.py')
    sel = se_model.build(se_model.load(root/'tools/short_strip_endcap/inputs.json'))
    lb = read('docs/validation/DES-022/inventory.json.gz')
    le = read('docs/validation/DES-023/inventory.json.gz')
    lbc = read('tools/long_strip_barrel/inputs.json')
    lec = read('tools/long_strip_endcap/inputs.json')
    native_paths = [
        'docs/validation/DES-020/baseline-selection/native.json',
        'docs/validation/DES-021/native.json',
        'docs/validation/DES-022/native.json.gz',
        'docs/validation/DES-023/native.json.gz',
    ]
    native = {p: read(p) for p in native_paths}
    for design in range(19,24):
        p = next((root/'docs/design').glob(f'DES-{design:03}-*.md'))
        sources[str(p.relative_to(root))] = sha(p)
    for path in ['docs/validation/DES-020/phi-tilted/results.md',
                 'docs/validation/DES-020/baseline-selection.md',
                 'docs/validation/DES-021/results.md',
                 'docs/validation/DES-022/results.md',
                 'docs/validation/DES-023/results.md']:
        sources[path] = sha(root/path)
    # A true physical cut, using the unchanged, independently checked recipe.
    xy = module('long_strip_xy_snapshot', 'tools/long_strip_barrel/draw_xy.py')
    cuts = []
    for e in lb['entities']:
        if e['role'] in ('routed_services', 'service_tray', 'end_board'):
            continue
        cut = xy.section(e,166.5)
        if cut is None:
            continue
        kind, data = cut
        if kind == 'polygon': data = data.tolist()
        else: data = [data[0].tolist(), float(data[1]), float(data[2])]
        cuts.append(dict(name=e['name'], role=e['role'], material=e['material'], kind=kind, data=data))
    def compact(m):
        return {k:v for k,v in m.items() if k in ['name','layer','row','face','ring','petal','center_mm','u','v','n','half_u_mm','half_v_mm','lift_mm']}
    data = dict(
        status='Selected tracker review baseline; engineering qualification pending',
        source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        source_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()),
        short_barrel=dict(input=sbc,layers=sb['layers'],rows=28,modules=8064,
            row_pitch_mm=sb['row_pitch_mm'],xy_modules=[compact(m) for m in sb['modules'] if m['row'] in (13,14)]),
        short_endcap=dict(input=sec,rings=sel['rings'],modules=4320,
            disc_modules=[compact(m) for m in sel['modules'] if m['layer']==0],cooling=se_model.cooling(sec)),
        long_barrel=dict(input=lbc,staves_by_layer=[sum(s['layer']==i for s in lb['layout']['staves']) for i in range(2)],
            pairs=len(lb['layout']['pairs']),sensors=len(lb['layout']['modules']),
            engineering=lb['engineering'],xy_z_mm=166.5,xy_sections=cuts),
        long_endcap=dict(input=lec,rings=le['layout']['rings'],pairs=len(le['layout']['pairs']),
            sensors=len(le['layout']['modules']),engineering=le['engineering'],
            disc_modules=[compact(m) for m in le['layout']['modules'] if m['layer']==0],
            petal_entities=[e for e in le['entities'] if e['name'].startswith('L0_P0_')]),
    )
    assert len(sb['modules'])==8064 and len(sel['modules'])==4320
    assert data['long_barrel']['sensors']==13968 and data['long_endcap']['sensors']==7488
    out=REPORT/'data/tracker-baseline.json'
    out.write_text(json.dumps(data,indent=2)+'\n')
    def identities(d):
        # Preserve measured identity, without republishing local command paths.
        return dict(execution={k:v for k,v in d['execution'].items() if k!='command'},
                    input_provenance=d['input_provenance'])
    provenance=dict(date='2026-10-07',source_revision=data['source_revision'],
        snapshot_sha256=sha(out),extractor_sha256=sha(Path(__file__)),
        sources=[dict(path=p,sha256=h) for p,h in sorted(sources.items())],
        retained_native_identities={p:identities(d) for p,d in native.items()},
        boundaries=[
            'Source revision identifies publication inputs, never a native execution revision.',
            'Short endcap layout is deterministic extraction from the exact retained producer/input, not a new native execution.',
            'Long barrel panels intersect the retained inventory at z=166.50mm. Short barrel and disc plans are projections.',
            'Effective corridors from independent compacts must be reconciled before integration; no combined mass or clearance asserted.',
            'Pixel snapshots and all authored pixel text/figures are preserved unchanged.',
        ])
    (REPORT/'data/tracker-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print('Frozen 8064/4320 strixels, 13968/7488 strip faces and exact long-barrel sections.')


if __name__=='__main__':
    main()
