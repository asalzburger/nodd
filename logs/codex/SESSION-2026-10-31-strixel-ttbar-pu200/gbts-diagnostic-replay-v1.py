#!/usr/bin/env python3
"""Bounded observation-only replay; immutable original artifacts are inputs."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys
import time

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(row): return json.dumps(row,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def fbits(x): return struct.unpack('<I',struct.pack('<f',x))[0]

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--events',type=int,default=100);args=p.parse_args()
    if args.output.exists(): raise ValueError('Fresh output required')
    args.output.mkdir(parents=True)
    root=args.root.resolve();native=root/'build/strixel-ttbar-safe-gbts-diagnostic'
    import acts
    import acts.examples
    sys.path.insert(0,str(native));import nodd_ttbar_gbts_diagnostic as module
    provenance=json.loads(module.provenance_json())
    for kind,base in [('upstream_sha256',root.parent/'nodd-software-layout/software/submodules/acts'),
                      ('generated_sha256',native/'generated'),
                      ('local_source_sha256',root/'software/source/ActsExamples/StrixelPileupSafeGbts')]:
        for name,digest in provenance[kind].items():
            if sha(base/name)!=digest: raise RuntimeError('Stale module '+kind+':'+name)
    production=root/'build/strixel-ttbar-production-v2/pitch0.5'
    config=production/'gbts'
    prepared={p.name:sha(p) for p in config.iterdir() if p.is_file()}
    algorithms={name:cls(str(config),acts.logging.ERROR) for name,cls in
        [('shared',module.SharedSeeding),('renamed',module.RenamedSeeding),('observed',module.GbtsSeeding)]}
    settings={name:json.loads(a.effective_configuration_json()) for name,a in algorithms.items()}
    if settings['shared']!=settings['renamed'] or settings['shared']!=settings['observed']: raise RuntimeError('Configuration mismatch')
    mapping={int(a):int(b) for a,b in (line.split(',') for line in (config/'mapping.csv').read_text().splitlines())}
    summary=dict(input_revision='250a211ff71be2ce7339cc043766f0d839470411',module_sha256=sha(Path(module.__file__)),
        provenance=provenance,driver_sha256=sha(Path(__file__)),prepared_sha256=prepared,
        effective_configuration=settings['shared'],events=[],status='running')
    started=time.monotonic()
    for event in range(args.events):
        path=production/'audit'/f'event{event:06d}.json.gz'
        with gzip.open(path,'rt') as stream: row=json.load(stream)
        if row['event']!=event: raise RuntimeError('Event mismatch')
        ms={m['index']:m for m in row['measurements']}
        points=[]
        for point in row['spacepoints']:
            if len(point['measurements'])!=1: raise RuntimeError('Unexpected pixel links')
            layer=mapping[ms[point['measurements'][0]]['geometry_id']]
            if any(struct.unpack('<f',struct.pack('<f',x))[0]!=x for x in point['position']): raise RuntimeError('Input not exact float32')
            points.append([point['index'],*point['position'],layer])
        baseline=[dict(indices=s['spacepoint_indices'],quality_bits=None if s['quality'] is None else fbits(s['quality'])) for s in row['seeds']]
        results={name:algorithm.replay(event,points) for name,algorithm in algorithms.items()}
        same=results['shared']['seeds']==results['renamed']['seeds']==results['observed']['seeds']
        baseline_equal=len(baseline)==len(results['shared']['seeds']) and all(a==b for a,b in zip(baseline,results['shared']['seeds']))
        if not same or not baseline_equal: raise RuntimeError(f'Original/renamed/observed seed differential event {event}: {same}, {baseline_equal}')
        for name,result in results.items():
            result['division_audit']=json.loads(result.pop('division_audit_json'))
            with gzip.open(args.output/f'event{event:06d}-{name}.json.gz','wt') as stream: json.dump(result,stream,sort_keys=True,allow_nan=False)
        note=dict(event=event,input_audit_sha256=sha(path),points_sha256=hashlib.sha256(canonical(points)).hexdigest(),
            seeds_sha256=hashlib.sha256(canonical(results['shared']['seeds'])).hexdigest(),seed_count=len(baseline),
            exact_original_saved_seeds=True,exact_all_variants=True,
            fpes={name:r['fpes'] for name,r in results.items()},
            adverse_divisions=len(results['observed']['division_audit']),native_seconds={name:r['native_seconds'] for name,r in results.items()})
        summary['events'].append(note)
        (args.output/'report.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(note),flush=True)
    summary.update(status='PASS',wall_seconds=time.monotonic()-started)
    (args.output/'report.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':main()
