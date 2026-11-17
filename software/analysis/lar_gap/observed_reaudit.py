"""Separate observer readback: native-catalog logical/physical identity correction."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

import observed_transport as frozen
from geometry import ROOT,sha,load,save,check_sources
from native import verify_report

ADDENDUM=ROOT/'docs/validation/lar-gap10k/readback-addendum.md'


def helpers():
    paths=[Path(__file__),Path(__file__).with_name('observed_recompare.py'),Path(__file__).with_name('test_reaudit.py'),ADDENDUM]
    paths += [Path(__file__).with_name(n) for n in ('observed_transport.py','observed_compare.py','geometry.py','native.py')]
    paths += [ROOT/'software/analysis/lar_response'/n for n in ('transport.py','compare.py')]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def catalog_rows(rows):
    aliases=defaultdict(set);count=0
    for row in rows:
        if not row.get('sensitive'):continue
        logical=row.get('volume');path=row.get('path','');physical=path.rsplit('/',1)[-1]
        if not logical or not path.startswith('/') or not physical:raise ValueError('Invalid sensitive native identity')
        aliases[logical].add(physical);count+=1
    return dict(aliases),count


def read_catalog(path,digest):
    if sha(path)!=digest:raise ValueError('Changed native alias ledger')
    with Path(path).open() as stream:return catalog_rows(json.loads(line) for line in stream)


def native_catalog(report_path,label):
    report=verify_report(report_path);entry=report['snapshots'][label];directory=Path(entry['directory'])
    snapshot=load(directory/'snapshot.json');path=directory/'placements.jsonl'
    aliases,count=read_catalog(path,snapshot['ledger_sha256'])
    if count!=snapshot['counts']['sensitive'] or count!=43648:raise ValueError('Incomplete native sensitive alias catalog')
    canonical={k:sorted(v) for k,v in sorted(aliases.items())}
    binding=dict(native_report=str(Path(report_path).resolve()),native_report_sha256=sha(report_path),
        snapshot_sha256=sha(directory/'snapshot.json'),ledger=str(path),ledger_sha256=sha(path),sensitive_placements=count,
        logical_names=len(aliases),catalog_sha256=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':')).encode()).hexdigest())
    return aliases,binding


def match_catalog_failures(failures,logged,aliases):
    remaining=list(logged)
    for failure in failures:
        logical=failure['volume']
        if logical not in aliases:raise ValueError('Failure logical volume absent from native sensitive catalog')
        matches=[i for i,(raw,physical,point) in enumerate(remaining)
                 if raw==failure['raw_volume'] and physical in aliases[logical] and len(point)==len(failure['mid_local_mm'])==3 and
                 all(math.isfinite(a) and math.isfinite(b) and abs(a-b)<=.5e-6+math.ulp(a)+math.ulp(b)
                     for a,b in zip(failure['mid_local_mm'],point))]
        if not matches:raise ValueError('Failure raw ID/native physical alias/local point correspondence failed')
        remaining.pop(matches[0])
    if remaining:raise ValueError('Original SD errors missing from corrected observer readback')


def raw_bindings(sample,run):
    sample,run=Path(sample).resolve(),Path(run).resolve();receipt=load(run/'receipt.json')
    manifest,binding,label=frozen.bound_sample(sample,Path(receipt['native_report']))
    if (receipt['exit_code'] or receipt['disk_abort'] or receipt['source_state'] or not receipt['producers_unchanged'] or not receipt['libraries_unchanged'] or
            receipt['sample_sha256']!=sha(sample/'sample.json') or Path(receipt['sample']).resolve()!=sample or receipt['variant']!=label or
            receipt['native_report_sha256']!=sha(Path(receipt['native_report']))):raise ValueError('Unsuccessful or unbound original observer transport')
    check_sources(receipt['producer_sha256'])
    if len(receipt['library_sha256'])!=4 or any(receipt['library_sha256'].get(p)!=h for p,h in binding['library_sha256'].items()):
        raise ValueError('Original three libraries/observer library binding differs')
    for p,h in receipt['library_sha256'].items():
        if sha(p)!=h:raise ValueError('Changed original observer library')
    if sha(run/'transport.log')!=receipt['log_sha256'] or sha(run/'observer/config.json')!=receipt['observer_config_sha256']:
        raise ValueError('Changed original observer log/config')
    if load(run/'observer/config.json')!=frozen.config(sample):raise ValueError('Observer config differs from frozen compact')
    names=set(receipt['observer_sha256'])
    if {p.name for p in (run/'observer').glob('worker-*.jsonl')}!=names:raise ValueError('Unexpected/missing original observer worker file')
    for name,h in receipt['observer_sha256'].items():
        if Path(name).name!=name or sha(run/'observer'/name)!=h:raise ValueError('Changed original observer worker file')
    for key,value in dict(skip=0,seed=133812341,max_step_mm=5.).items():
        if receipt[key]!=value:raise ValueError('Changed frozen observer policy')
    if receipt['threads'] not in (1,12) or not 0<receipt['events']<=10000:raise ValueError('Invalid original event/worker policy')
    command=receipt['command'];log=(run/'transport.log').read_text()
    for flag,value in (('--physics.list','FTFP_BERT'),('--physics.rangecut','0.7')):
        if flag not in command or command[command.index(flag)+1]!=value:raise ValueError('Changed executed physics command')
    if '--random.enableEventSeed' not in command or not re.search(r'with seed\s+133812341\b',log) or 'FTFP_BERT' not in log:
        raise ValueError('Missing actual seeded physics evidence')
    for role in ('LArBarrel','LArEndcaps'):
        if not re.search('Setting up SD for '+role+' with Geant4ScintillatorCalorimeterAction',log) or not re.search("Adding default filter 'edep0' to sensitive detector for '"+role+"'",log):
            raise ValueError('Actual sensitive action/filter differs')
    return manifest,receipt,label


def common_readback(sample,run,output):
    if (run/'readback.json').exists():return run,'Reused immutable common readback after full raw/map/hash checks'
    common=output/'common';common.mkdir()
    for name in ('receipt.json','transport.log','events.root','audit'):(common/name).symlink_to((run/name).resolve(),target_is_directory=name=='audit')
    frozen.original.audit(argparse.Namespace(sample=sample,run=common))
    return common,'Frozen original common auditor executed against read-only raw links in this new output directory'


def verify_common(sample,run,common,receipt):
    saved=load(common/'readback.json');manifest=load(sample/'sample.json')
    if (saved['status']!='PASS' or saved['sample']!=manifest or saved['events']!=receipt['events'] or
            saved['receipt_sha256']!=sha(run/'receipt.json') or saved['root_sha256']!=sha(run/'events.root') or
            saved['event_summary_sha256']!=sha(common/'event-summary.jsonl') or saved['audit_sha256']!=sha(frozen.original.__file__)):
        raise ValueError('Unbound common saved-data readback')
    maps=frozen.verify_serial_maps(run,receipt,saved)
    worker_events=frozen.original.check_workers(saved['workers'],receipt)
    if worker_events!=saved['worker_events']:raise ValueError('Changed worker event totals')
    actual={p.name for p in (run/'audit').glob('worker-*.json')}
    if actual!=set(saved['worker_audit_sha256']):raise ValueError('Unexpected/missing saved worker audit')
    for worker in saved['workers']:
        path=run/'audit'/f'worker-{worker["thread_id"]}.json'
        if load(path)!=worker or sha(path)!=saved['worker_audit_sha256'][path.name]:raise ValueError('Changed embedded/raw worker audit')
        if worker['rng_engine']!='MixMaxRng' or worker['begin_run_rng_seed']!=133812341:raise ValueError('Changed actual worker RNG')
        if not worker['region_cuts'] or any(region['mm']!=[.7]*4 for region in worker['region_cuts']):raise ValueError('Changed actual worker region cuts')
        if any('StepLimiter' not in worker['processes'][particle] for particle in ('e-','e+')):raise ValueError('Missing actual charged StepLimiter')
        if any(re.search('FastSim|GFlash',p,re.I) for names in worker['processes'].values() for p in names):raise ValueError('Unobserved fast-simulation path')
    return saved,maps


def audit(args):
    sample=args.sample.resolve();run=args.run.resolve();out=args.output.resolve();manifest,receipt,label=raw_bindings(sample,run)
    aliases,catalog=native_catalog(Path(receipt['native_report']),label)
    out.mkdir(parents=True,exist_ok=False);common,origin=common_readback(sample,run,out)
    saved,maps=verify_common(sample,run,common,receipt);required=set(range(receipt['events']));locations={};workers=Counter()
    for name in receipt['observer_sha256']:
        path=run/'observer'/name
        with path.open() as stream:
            while True:
                offset=stream.tell();line=stream.readline()
                if not line:break
                row=json.loads(line);frozen.event_identity(row,locations,required)
                locations[row['event']]=(path,offset);workers[str(row['thread'])]+=1
    if set(locations)!=required or dict(workers)!=saved['worker_events']:raise ValueError('Incomplete observed event/worker coverage')
    primaries={r['event']:r for r in map(json.loads,(common/'event-summary.jsonl').read_text().splitlines())}
    if set(primaries)!=required or len(primaries)!=saved['events']:raise ValueError('Incomplete common primary ledger')
    ledger=out/'derived-events.jsonl';seen=set();failures=[];fingerprints={};maximum_bound=0.;failure_count=0
    with ledger.open('w') as output:
        for event,hits,digest in frozen.saved_events(run/'events.root'):
            if event in seen or event not in locations:raise ValueError('Duplicate/unexpected saved event')
            seen.add(event);fingerprints[event]=digest;path,offset=locations[event]
            with path.open() as stream:stream.seek(offset);row=json.loads(stream.readline())
            if set(row['collections'])!=set(frozen.NAMES) or row['positive_identity_count']!=sum(c['positive_steps'] for c in row['collections'].values()):
                raise ValueError('Unexpected collection or positive-step identity accounting')
            totals={name:frozen.collection_closure(row['collections'][name],hits[name]) for name in frozen.NAMES}
            for name in frozen.NAMES:
                for failure in row['collections'][name]['failures']:
                    if (failure['event'],failure['run'],failure['collection'])!=(event,0,name):raise ValueError('Misassigned failed step')
                    failures.append(failure)
            failure_count+=sum(t['failed_steps'] for t in totals.values());maximum_bound=max(maximum_bound,sum(t['saved_closure_bound_GeV'] for t in totals.values()))
            result={k:primaries[event][k] for k in ('event','energy_GeV','eta','phi')};result.update(collections=totals,saved_cell_sha256=digest)
            for key in ('A_GeV','S_GeV','H_GeV','U_GeV','native_closure_bound_GeV','saved_closure_bound_GeV'):result[key]=math.fsum(t[key] for t in totals.values())
            output.write(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n')
    if seen!=required:raise ValueError('Incomplete saved ROOT population')
    match_catalog_failures(failures,frozen.log_failures((run/'transport.log').read_text()),aliases)
    replay=dict(requested=False,exact=False,policy='Use only fresh observed vectors; do not add U to unverified retained H')
    if args.retained_run:
        from software.analysis.lar_response.compare import validate_contract,load_run
        previous=args.retained_run.resolve();validate_contract(previous,'lar');load_run(previous)
        prior_receipt=load(previous/'receipt.json');prior_saved=load(previous/'readback.json')
        if prior_receipt['sample_sha256']!=receipt['sample_sha256']:raise ValueError('Retained replay sample differs')
        frozen.verify_serial_maps(previous,prior_receipt,prior_saved);check_sources(prior_receipt['producer_sha256'])
        if sha(previous/'transport.log')!=prior_receipt['log_sha256']:raise ValueError('Changed retained replay log')
        for path,digest in prior_receipt['library_sha256'].items():
            if sha(path)!=digest:raise ValueError('Changed retained replay library')
        prior={}
        for event,_,digest in frozen.saved_events(previous/'events.root'):
            if event in prior:raise ValueError('Duplicate retained replay event')
            prior[event]=digest
        old_vectors={r['event']:(r['energy_GeV'],r['eta'],r['phi'],r['signal_GeV']) for r in map(json.loads,(previous/'event-summary.jsonl').read_text().splitlines())}
        new_vectors={event:(r['energy_GeV'],r['eta'],r['phi'],r['signal_GeV']) for event,r in primaries.items()}
        replay=dict(requested=True,exact=prior==fingerprints and old_vectors==new_vectors,event_vectors_exact=old_vectors==new_vectors,
            events_compared=len(prior),different_events=sum(prior.get(e)!=h for e,h in fingerprints.items()),
            retained_run=str(previous),retained_receipt_sha256=sha(previous/'receipt.json'),retained_readback_sha256=sha(previous/'readback.json'),
            retained_root_sha256=prior_saved['root_sha256'],retained_ledger_sha256=prior_saved['event_summary_sha256'])
    proof=dict(status='PASS',auditor=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=sha(__file__),
        revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()),helper_sha256=helpers(),
        sample=str(sample),run=str(run),events=len(seen),variant=label,failed_steps=failure_count,
        receipt_sha256=sha(run/'receipt.json'),common_directory=str(common),common_origin=origin,
        common_readback_sha256=sha(common/'readback.json'),common_ledger_sha256=sha(common/'event-summary.jsonl'),
        derived_ledger_sha256=sha(ledger),serial_maps=maps,native_alias_catalog=catalog,failed_observer_matches_original_SD=True,
        maximum_saved_closure_bound_GeV=maximum_bound,replay=replay,
        precision='Unchanged frozen exact float32 cell/native A=S+U/derived saved-rounding bounds',
        correction='Logical-to-physical names resolved only through actual hash-bound native sensitive placements; raw ID/point/count gates unchanged')
    save(out/'reaudit.json',proof);print(json.dumps({k:proof[k] for k in ('status','events','failed_steps','replay','auditor')},indent=2))


def proof_identity(proof):
    if proof['status']!='PASS' or proof['auditor']['path']!=str(Path(__file__).relative_to(ROOT)) or proof['auditor']['sha256']!=sha(__file__):
        raise ValueError('Failed or foreign corrected auditor identity')
    if proof['helper_sha256']!=helpers():raise ValueError('Changed or missing corrected auditor/helper source binding')
    check_sources(proof['helper_sha256'])


def evidence(directory,production=False):
    directory=Path(directory).resolve();proof=load(directory/'reaudit.json');proof_identity(proof)
    sample=Path(proof['sample']);run=Path(proof['run']);_,receipt,label=raw_bindings(sample,run)
    if proof['variant']!=label or proof['events']!=receipt['events']:raise ValueError('Corrected proof label/population mismatch')
    if sha(run/'receipt.json')!=proof['receipt_sha256'] or sha(directory/'derived-events.jsonl')!=proof['derived_ledger_sha256']:
        raise ValueError('Changed corrected receipt/derived ledger')
    common=Path(proof['common_directory']);_,maps=verify_common(sample,run,common,receipt)
    if maps!=proof['serial_maps'] or sha(common/'readback.json')!=proof['common_readback_sha256'] or sha(common/'event-summary.jsonl')!=proof['common_ledger_sha256']:
        raise ValueError('Changed corrected common/map binding')
    _,catalog=native_catalog(Path(receipt['native_report']),label)
    if catalog!=proof['native_alias_catalog']:raise ValueError('Changed corrected native alias catalog')
    if production:
        from software.analysis.lar_response.compare import validate_contract,load_run
        validate_contract(common,'lar');load_run(common)
    replay=proof['replay']
    if replay['requested']:
        previous=Path(replay['retained_run'])
        if sha(previous/'receipt.json')!=replay['retained_receipt_sha256'] or sha(previous/'readback.json')!=replay['retained_readback_sha256']:
            raise ValueError('Changed corrected retained-replay proof')
        prior_receipt=load(previous/'receipt.json');prior_saved=load(previous/'readback.json')
        frozen.verify_serial_maps(previous,prior_receipt,prior_saved);check_sources(prior_receipt['producer_sha256'])
        if (sha(previous/'events.root')!=replay['retained_root_sha256'] or sha(previous/'event-summary.jsonl')!=replay['retained_ledger_sha256'] or
                sha(previous/'transport.log')!=prior_receipt['log_sha256']):raise ValueError('Changed corrected retained raw artifact')
        for path,digest in prior_receipt['library_sha256'].items():
            if sha(path)!=digest:raise ValueError('Changed corrected retained library')
    rows=sorted(map(json.loads,(directory/'derived-events.jsonl').read_text().splitlines()),key=lambda r:r['event'])
    if len(rows)!=proof['events'] or [r['event'] for r in rows]!=list(range(receipt['events'])):raise ValueError('Incomplete corrected derived population')
    return rows,receipt,proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='stage',required=True)
    a=sub.add_parser('audit')
    for n in ('sample','run','output'):a.add_argument('--'+n,type=Path,required=True)
    a.add_argument('--retained-run',type=Path)
    a=sub.add_parser('verify');a.add_argument('--directory',type=Path,required=True)
    args=p.parse_args();audit(args) if args.stage=='audit' else print('PASS',len(evidence(args.directory)[0]))
