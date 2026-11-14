"""Source-bound independent sensitive-step observation; original transport is frozen."""
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from geometry import ROOT,FROZEN,sha,load,save,verify,reference_bindings,check_sources
from native import verify_report
from software.analysis.lar_response import transport as original

NAMES=tuple(original.COLLECTIONS)
OBSERVER_PROTOCOL=ROOT/'docs/validation/lar-gap10k/observer-protocol.md'
FILES=('CMakeLists.txt','StepAudit.cpp','observed_steering.py','observed_transport.py','observed_compare.py','test_observed.py')
UPSTREAM=dict(DD4hep_commit='142cbb7eb29ec4feafb1af9317fac38775872085',
    scintillator_action='DDG4/plugins/Geant4SDActions.cpp:465-489',filter='DDG4/plugins/Geant4SensDetFilters.cpp:144-145',
    midpoint='DDG4/src/Geant4SensDetAction.cpp:323-357',writer='DDG4/edm4hep/Geant4Output2EDM4hep.cpp:680',
    precision='Installed edm4hep/SimCalorimeterHitData.h: float energy; one native double MeV / GeV conversion then float setter; no installed plugin source claim',
    exact_tag_git_blobs=dict(Geant4SDActions_cpp='31c1e15fd26c452843914fb06aff2ee9a27f4965',
        Geant4SensDetFilters_cpp='2c4e60a5ef88e9541e6e20a17099b7b6f5b4ab4c',Geant4SensDetAction_cpp='c606f3d189bcb233793f731be6e7a786ef1a7f0a',
        Geant4Data_cpp='03f1e25b476c3d9a73709cd9df39f218879cb315',Geant4Output2EDM4hep_cpp='f5d22ef85482227a03cca029fa6677ff2f096070'))


def producers():
    paths=[Path(__file__).with_name(n) for n in FILES]
    paths += [OBSERVER_PROTOCOL,*[ROOT/'software/analysis/lar_response'/n for n in ('transport.py','steering.py','Audit.cpp','CMakeLists.txt')]]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def bound_sample(sample,native_report):
    sample=Path(sample).resolve();m=load(sample/'sample.json');original.verify_hashes(sample,m['hashes'])
    if 'gap_experiment' in m:
        m=verify(sample);binding=m['gap_experiment']['reference_binding'];label='candidate'
    else:
        binding=reference_bindings(sample,sample.parent/'production12');label='standard'
    native=verify_report(native_report);entry=native['snapshots'][label]
    if entry['sample_sha256']!=sha(sample/'sample.json') or entry['compact_sha256']!=m['hashes']['detector.xml']:
        raise ValueError('Native proof does not bind observer geometry')
    for name in ('particles.HEPEvt','truth-input.jsonl','materials.xml'):
        if m['hashes'][name]!=FROZEN[name]:raise ValueError('Changed frozen input/material')
    return m,binding,label


def config(sample):
    seg=ET.parse(sample/'detector.xml').find("readouts/readout[@name='LArEndcapHits']/segmentation")
    values=list(map(float,seg.get('wheel_table_mm').split()))
    return dict(endcap_wheels=[dict(inner_mm=values[4*i],outer_mm=values[4*i+1],half_depth_mm=float(seg.get('sampling_depth_mm'))/2) for i in range(3)],
        source_facts=UPSTREAM,energy_policy='Unweighted extractContribution(step,true), raw edep>0, weight1, Birks0; optical rejected',
        coverage='All sensitive callbacks observed; unique positive track/step keys checked in C++; successful-cell aggregates and rare full failure records retained')


def f32(value):return struct.unpack('!f',struct.pack('!f',value))[0]


def float32_cell_bounds(value):
    if not math.isfinite(value) or value<0 or f32(value)!=value:raise ValueError('Not a nonnegative saved float32')
    bits=struct.unpack('!I',struct.pack('!f',value))[0]
    previous=struct.unpack('!f',struct.pack('!I',bits-1))[0] if bits else -struct.unpack('!f',struct.pack('!I',1))[0]
    following=struct.unpack('!f',struct.pack('!I',bits+1))[0]
    return (previous+value)/2,(value+following)/2


def sum_bound(count,total):
    # Higham gamma_(n-1), converted from exact-sum to observed-sum bound.
    x=max(0,count-1)*2**-53
    if x>=.5:raise ValueError('Unsupported accumulation length')
    gamma=x/(1-x)
    return gamma/(1-gamma)*abs(total)


def collection_closure(row,hits):
    a,u=row['A_MeV'],row['U_MeV'];cells=row['cells'];failures=row['failures']
    if any(not math.isfinite(x) or x<0 for x in (a,u)):raise ValueError('Invalid native accounting energy')
    if any(not isinstance(row[k],int) or row[k]<0 for k in ('sensitive_callbacks','positive_steps','zero_steps')):raise ValueError('Invalid callback counts')
    if row['sensitive_callbacks']!=row['positive_steps']+row['zero_steps']:raise ValueError('Missing callback accounting')
    if len({c['cell'] for c in cells})!=len(cells) or set(hits)!={c['cell'] for c in cells}:raise ValueError('Missing/extra/duplicate successful cell')
    count=sum(c['steps'] for c in cells)+len(failures)
    if count!=row['positive_steps']:raise ValueError('Missing positive step accounting')
    keys=[(f['track'],f['step']) for f in failures]
    if len(set(keys))!=len(keys):raise ValueError('Duplicate failed step')
    for f in failures:
        if (f['weight']!=1 or not math.isfinite(f['edep_MeV']) or f['edep_MeV']<=0 or
                f['contribution_MeV']!=f['edep_MeV']):raise ValueError('Failure filter/contribution policy differs')
        if any(not math.isfinite(v) for k in ('pre_global_mm','post_global_mm','mid_global_mm','pre_local_mm','post_local_mm','mid_local_mm') for v in f[k]):
            raise ValueError('Nonfinite failed-step coordinates')
    fail_sum=math.fsum(f['contribution_MeV'] for f in failures)
    if abs(u-fail_sum)>sum_bound(len(failures),u)+.5*math.ulp(fail_sum):raise ValueError('Unassigned contribution sum differs')
    native_cells=[];rounding=0.;accumulation=0.
    for cell in cells:
        s=cell['sum_MeV'];n=cell['steps'];h=hits[cell['cell']]
        if not math.isfinite(s) or s<=0 or not isinstance(n,int) or n<=0:raise ValueError('Invalid native successful cell')
        expected=f32(s/1000.)
        if h!=expected:raise ValueError('Saved cell differs from exact float32 native accumulation')
        lo,hi=float32_cell_bounds(h)
        rounding+=max(h-lo,hi-h)+.5*math.ulp(s/1000.)
        native_cells.append(s);accumulation+=sum_bound(n,s)
    s=math.fsum(native_cells);native_total=math.fsum([s,u])
    native_bound=sum_bound(count,a)+accumulation+sum_bound(len(failures),u)+.5*math.ulp(s)+.5*math.ulp(native_total)+.5*math.ulp(a-native_total)
    if abs(a-native_total)>native_bound:raise ValueError('Native A=S+U closure failed')
    h=math.fsum(hits.values());residual=a/1000.-math.fsum([h,u/1000.])
    output_bound=native_bound/1000.+rounding+sum(.5*math.ulp(v) for v in (a/1000.,u/1000.,h,math.fsum([h,u/1000.]),residual))
    if abs(residual)>output_bound:raise ValueError('Saved-energy precision closure failed')
    return dict(A_GeV=a/1000.,S_GeV=s/1000.,H_GeV=h,U_GeV=u/1000.,positive_steps=count,failed_steps=len(failures),
        native_closure_bound_GeV=native_bound/1000.,saved_closure_bound_GeV=output_bound,rounding_residual_GeV=h-s/1000.)


def log_failures(log):
    lines=log.splitlines();result=[]
    for i,line in enumerate(lines):
        if 'cellID: failed to access segmentation' not in line:continue
        raw=int(re.search(r'VolumeID:\s+([0-9A-Fa-f]+)',line)[1],16)
        local=next((x for x in lines[i+1:i+6] if 'G4-local:' in x),None)
        volume=next((x for x in lines[i+1:i+6] if 'Pre-step:' in x),None)
        if local is None or volume is None:raise ValueError('Incomplete original SD error block')
        xyz=[float(x) for x in re.search(r'G4-local:\s*\(([^)]+)\)',local)[1].split(',')]
        result.append((raw,re.search(r'Pre-step:\s+(\S+)',volume)[1],xyz))
    return result


def match_failures(failures,logged):
    remaining=list(logged)
    for f in failures:
        matches=[i for i,(raw,volume,xyz) in enumerate(remaining) if raw==f['raw_volume'] and volume==f['volume'] and
            all(abs(a-b)<=.5e-6+math.ulp(a)+math.ulp(b) for a,b in zip(f['mid_local_mm'],xyz))]
        if not matches:raise ValueError('Observer failure does not match original SD raw ID/volume/local point')
        remaining.pop(matches[0])
    if remaining:raise ValueError('Original SD error missing from observer')


def event_identity(row,seen,required):
    if row['run']!=0 or row['event'] in seen or row['event'] not in required:
        raise ValueError('Duplicate/unexpected observer event')
    if row.get('rounding_mode')!='FE_TONEAREST':raise ValueError('Unaudited observer rounding mode')


def run(args):
    sample=args.sample.resolve();m,binding,label=bound_sample(sample,args.native_report)
    oldlibs=[p.resolve() for p in [*args.geometry_library,args.audit_library]];observer=args.observer_library.resolve()
    if len(oldlibs)!=3 or len(set(oldlibs))!=3 or {str(p):sha(p) for p in oldlibs}!=binding['library_sha256']:
        raise ValueError('Observer must reuse the exact three original libraries')
    if args.events<args.threads or args.threads not in (1,12) or args.events<=0 or args.events>m['events']:raise ValueError('Invalid observed population')
    state=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines()
    if state:raise ValueError('Observer source must be committed clean before native execution')
    reserve=args.reserve_gib*1024**3
    if not math.isfinite(reserve) or reserve<0 or shutil.disk_usage(sample).free<reserve:raise ValueError('Invalid/insufficient disk reserve')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);(out/'audit').mkdir();(out/'observer').mkdir()
    save(out/'observer/config.json',config(sample));source=producers();libraries={str(p):sha(p) for p in [*oldlibs,observer]}
    env=os.environ.copy();env.update(NODD_LAR_AUDIT=str(out/'audit'),NODD_LAR_MAX_STEP_MM='5',NODD_LAR_AUDIT_LIBRARY=str(args.audit_library.resolve()),
        NODD_LAR_OBSERVER=str(out/'observer'),NODD_LAR_OBSERVER_LIBRARY=str(observer))
    for key in ('DD4HEP_LIBRARY_PATH','DYLD_LIBRARY_PATH','LD_LIBRARY_PATH'):env[key]=os.pathsep.join([*(str(p.parent) for p in [*oldlibs,observer]),env.get(key,'')])
    executable=shutil.which('ddsim')
    if not executable:raise ValueError('DDSim unavailable')
    command=[sys.executable,'-u',executable,'--compactFile',str(sample/'detector.xml'),'--steeringFile',str(Path(__file__).with_name('observed_steering.py')),
        '--runType','batch','--inputFiles',str(sample/'particles.HEPEvt'),'--numberOfEvents',str(args.events),'--skipNEvents','0','--numberOfThreads',str(args.threads),
        '--random.seed','133812341','--random.enableEventSeed','--physics.list','FTFP_BERT','--physics.rangecut','0.7','--part.userParticleHandler','',
        '--outputConfig.forceEDM4HEP','--outputFile',str(out/'events.root')]
    common=dict(command=command,events=args.events,skip=0,threads=args.threads,seed=133812341,max_step_mm=5.,source_state=state,
        source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),producer_sha256=source,library_sha256=libraries,
        sample=str(sample),sample_sha256=sha(sample/'sample.json'),native_report=str(args.native_report.resolve()),native_report_sha256=sha(args.native_report),
        observer_config_sha256=sha(out/'observer/config.json'),variant=label,source_facts=UPSTREAM)
    save(out/'started.json',common);start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN);aborted=False;last=start
    with (out/'transport.log').open('w') as stream:
        with subprocess.Popen(command,cwd=out,env=env,stdout=stream,stderr=subprocess.STDOUT) as child:
            while child.poll() is None:
                if shutil.disk_usage(out).free<reserve:aborted=True;child.terminate()
                if time.monotonic()-last>=30:last=time.monotonic();print(f'Observed {label}: {last-start:.1f}s',flush=True)
                time.sleep(1)
            code=child.returncode
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt=dict(**common,exit_code=code,disk_abort=aborted,wall_seconds=time.monotonic()-start,
        cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,log_sha256=sha(out/'transport.log'),
        producers_unchanged=all(sha(ROOT/p)==h for p,h in source.items()),libraries_unchanged=all(sha(p)==h for p,h in libraries.items()),
        maps_audit_sha256=sha(out/'audit/maps-initialized.json') if (out/'audit/maps-initialized.json').exists() else None,
        observer_sha256={p.name:sha(p) for p in sorted((out/'observer').glob('worker-*.jsonl'))})
    save(out/'receipt.json',receipt)
    if code or aborted or not receipt['producers_unchanged'] or not receipt['libraries_unchanged']:raise RuntimeError('Observed run failed; diagnostics retained')


def saved_events(path):
    import edm4hep  # dictionary registration
    from podio import root_io
    for frame in root_io.Reader(str(path)).get('events'):
        header,=frame.get('EventHeader');event=int(header.getEventNumber());collections={};signature=[]
        for name in NAMES:
            values=[];cells={}
            for hit in frame.get(name):
                cell=int(hit.getCellID());energy=float(hit.getEnergy());p=hit.getPosition()
                if cell in cells:raise ValueError('Duplicate saved cell')
                cells[cell]=energy;values.append((cell,energy.hex(),float(p.x).hex(),float(p.y).hex(),float(p.z).hex()))
            collections[name]=cells;signature.append((name,sorted(values)))
        digest=hashlib.sha256(json.dumps(signature,separators=(',',':')).encode()).hexdigest()
        yield event,collections,digest


def audit(args):
    sample=args.sample.resolve();run=args.run.resolve();receipt=load(run/'receipt.json')
    m,_,_=bound_sample(sample,Path(receipt['native_report']))
    if (receipt['exit_code'] or receipt['disk_abort'] or not receipt['producers_unchanged'] or not receipt['libraries_unchanged'] or
            receipt['sample_sha256']!=sha(sample/'sample.json') or sha(Path(receipt['native_report']))!=receipt['native_report_sha256']):raise ValueError('Unsuccessful/unbound observer run')
    check_sources(receipt['producer_sha256'])
    if sha(run/'transport.log')!=receipt['log_sha256']:raise ValueError('Changed observed transport log')
    for p,h in receipt['library_sha256'].items():
        if sha(p)!=h:raise ValueError('Changed observed library')
    if sha(run/'observer/config.json')!=receipt['observer_config_sha256']:raise ValueError('Changed observer config')
    for name,h in receipt['observer_sha256'].items():
        if Path(name).name!=name or sha(run/'observer'/name)!=h:raise ValueError('Changed observer worker')
    if {p.name for p in (run/'observer').glob('worker-*.jsonl')}!=set(receipt['observer_sha256']):raise ValueError('Unexpected observer worker artifact')
    if not (run/'readback.json').exists():original.audit(argparse.Namespace(sample=sample,run=run))
    proof=load(run/'readback.json')
    if proof['receipt_sha256']!=sha(run/'receipt.json') or proof['root_sha256']!=sha(run/'events.root') or proof['event_summary_sha256']!=sha(run/'event-summary.jsonl'):
        raise ValueError('Unbound saved-data readback')
    log=(run/'transport.log').read_text()
    for role in ('LArBarrel','LArEndcaps'):
        if not re.search('Setting up SD for '+role+' with Geant4ScintillatorCalorimeterAction',log) or not re.search("Adding default filter 'edep0' to sensitive detector for '"+role+"'",log):
            raise ValueError('Actual observer action/filter differs')
    if any(re.search('FastSim|GFlash',p,re.I) for w in proof['workers'] for names in w['processes'].values() for p in names):
        raise ValueError('Unobserved fast-simulation process')
    required=set(range(receipt['events']));locations={};workers=Counter()
    for name in receipt['observer_sha256']:
        path=run/'observer'/name
        with path.open() as stream:
            while True:
                offset=stream.tell();line=stream.readline()
                if not line:break
                row=json.loads(line);event=row['event']
                event_identity(row,locations,required)
                locations[event]=(path,offset);workers[str(row['thread'])]+=1
    if set(locations)!=required or dict(workers)!=proof['worker_events']:raise ValueError('Missing observer event/worker coverage')
    ledger=run/'observed-events.jsonl'
    if ledger.exists():raise ValueError('Refusing observed event ledger overwrite')
    all_failures=[];seen=set();fingerprints={};max_bounds=0.;failure_count=0
    primaries={r['event']:r for r in map(json.loads,(run/'event-summary.jsonl').read_text().splitlines())}
    with ledger.open('w') as output:
        for event,hits,digest in saved_events(run/'events.root'):
            if event in seen or event not in locations:raise ValueError('Duplicate/unexpected saved observer event')
            seen.add(event);fingerprints[event]=digest;path,offset=locations[event]
            with path.open() as stream:stream.seek(offset);row=json.loads(stream.readline())
            if set(row['collections'])!=set(NAMES):raise ValueError('Unexpected observer collections')
            if row['positive_identity_count']!=sum(c['positive_steps'] for c in row['collections'].values()):raise ValueError('Positive step identity accounting differs')
            totals={name:collection_closure(row['collections'][name],hits[name]) for name in NAMES}
            for name in NAMES:
                for f in row['collections'][name]['failures']:
                    if (f['event'],f['run'],f['collection'])!=(event,0,name):raise ValueError('Misassigned failed observer step')
                    all_failures.append(f)
            failure_count+=sum(t['failed_steps'] for t in totals.values());max_bounds=max(max_bounds,sum(t['saved_closure_bound_GeV'] for t in totals.values()))
            ref=primaries[event];result={k:ref[k] for k in ('event','energy_GeV','eta','phi')}
            result.update(collections=totals,saved_cell_sha256=digest)
            for k in ('A_GeV','S_GeV','H_GeV','U_GeV','native_closure_bound_GeV','saved_closure_bound_GeV'):
                result[k]=math.fsum(t[k] for t in totals.values())
            output.write(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n')
    if seen!=required:raise ValueError('Incomplete saved observer events')
    match_failures(all_failures,log_failures((run/'transport.log').read_text()))
    replay=dict(requested=False,exact=False,policy='Use fresh matched observed vectors; never add unassigned energy to an unverified retained H')
    if args.retained_run:
        from software.analysis.lar_response.compare import validate_contract,load_run
        validate_contract(args.retained_run,'lar');load_run(args.retained_run)
        previous=load(args.retained_run/'receipt.json')
        if previous['sample_sha256']!=receipt['sample_sha256']:raise ValueError('Replay reference sample differs')
        prior={event:digest for event,_,digest in saved_events(args.retained_run/'events.root')}
        old_vectors={r['event']:(r['energy_GeV'],r['eta'],r['phi'],r['signal_GeV']) for r in map(json.loads,(args.retained_run/'event-summary.jsonl').read_text().splitlines())}
        new_vectors={r['event']:(r['energy_GeV'],r['eta'],r['phi'],r['signal_GeV']) for r in primaries.values()}
        replay=dict(requested=True,exact=prior==fingerprints and old_vectors==new_vectors,event_vectors_exact=old_vectors==new_vectors,events_compared=len(prior),
            different_events=sum(prior.get(e)!=d for e,d in fingerprints.items()),
            retained_receipt_sha256=sha(args.retained_run/'receipt.json'),retained_readback_sha256=sha(args.retained_run/'readback.json'),
            comparison='Per-event exact canonical cell IDs, float energies and positions; saved primary identity separately validated against same frozen input')
    result=dict(status='PASS',events=len(seen),failed_steps=failure_count,failed_observer_matches_original_SD=True,
        receipt_sha256=sha(run/'receipt.json'),readback_sha256=sha(run/'readback.json'),ledger_sha256=sha(ledger),
        maximum_saved_closure_bound_GeV=max_bounds,precision='Per-cell exact float32(S_nativeMeV/1000), gamma_(n-1) native double accumulation bounds, asymmetric half-neighbour float32 intervals; A independently accumulated',
        observer_sha256=receipt['observer_sha256'],replay=replay,auditor_sha256=sha(__file__))
    save(run/'observer-readback.json',result);print(json.dumps(result,indent=2))


def evidence(run,production=False):
    run=Path(run);receipt=load(run/'receipt.json');proof=load(run/'observer-readback.json');saved=load(run/'readback.json')
    if (proof['status']!='PASS' or receipt['exit_code'] or receipt['disk_abort'] or receipt['source_state'] or
            proof['receipt_sha256']!=sha(run/'receipt.json') or proof['readback_sha256']!=sha(run/'readback.json') or
            proof['ledger_sha256']!=sha(run/'observed-events.jsonl') or proof['auditor_sha256']!=sha(__file__)):
        raise ValueError('Unsuccessful/unbound observed evidence')
    check_sources(receipt['producer_sha256']);bound_sample(Path(receipt['sample']),Path(receipt['native_report']))
    if sha(Path(receipt['native_report']))!=receipt['native_report_sha256'] or sha(run/'transport.log')!=receipt['log_sha256']:
        raise ValueError('Changed observer native/log binding')
    for p,h in receipt['library_sha256'].items():
        if sha(p)!=h:raise ValueError('Changed executed observer library')
    if sha(run/'observer/config.json')!=receipt['observer_config_sha256']:raise ValueError('Changed observer config')
    for name,h in receipt['observer_sha256'].items():
        if sha(run/'observer'/name)!=h:raise ValueError('Changed observed worker')
    if production:
        from software.analysis.lar_response.compare import validate_contract,load_run
        validate_contract(run,'lar');load_run(run)
    elif saved['root_sha256']!=sha(run/'events.root'):raise ValueError('Changed observed ROOT')
    rows=sorted(map(json.loads,(run/'observed-events.jsonl').read_text().splitlines()),key=lambda r:r['event'])
    if [r['event'] for r in rows]!=list(range(receipt['events'])):raise ValueError('Incomplete/duplicate observed ledger events')
    return rows,receipt,proof


def controls(args):
    a,ra,pa=evidence(args.serial);b,rb,pb=evidence(args.mt)
    if (ra['events'],ra['threads'],rb['events'],rb['threads'])!=(24,1,24,12):raise ValueError('Expected serial/MT24 controls')
    if ra['sample_sha256']!=rb['sample_sha256'] or ra['library_sha256']!=rb['library_sha256']:raise ValueError('Control configuration mismatch')
    if a!=b:raise ValueError('Observer serial/MT event/cell/energy/position/counter mismatch')
    def failures(run):
        result={}
        for path in (run/'observer').glob('worker-*.jsonl'):
            for r in map(json.loads,path.read_text().splitlines()):
                result[r['event']]={name:c['failures'] for name,c in r['collections'].items()}
        return result
    if failures(args.serial)!=failures(args.mt):raise ValueError('Observer serial/MT failure detail mismatch')
    if args.output.exists():raise ValueError('Refusing observer control overwrite')
    save(args.output,dict(status='PASS',events=24,observer_and_saved_cells_exact=True,
        serial_observer_readback_sha256=sha(args.serial/'observer-readback.json'),mt_observer_readback_sha256=sha(args.mt/'observer-readback.json')))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='stage',required=True)
    a=sub.add_parser('run')
    for n in ('sample','native-report','audit-library','observer-library','output'):a.add_argument('--'+n,type=Path,required=True)
    a.add_argument('--geometry-library',type=Path,action='append',required=True);a.add_argument('--events',type=int,default=10000)
    a.add_argument('--threads',type=int,default=12);a.add_argument('--reserve-gib',type=float,default=30.)
    a=sub.add_parser('audit')
    for n in ('sample','run'):a.add_argument('--'+n,type=Path,required=True)
    a.add_argument('--retained-run',type=Path)
    a=sub.add_parser('controls')
    for n in ('serial','mt','output'):a.add_argument('--'+n,type=Path,required=True)
    args=p.parse_args();globals()[args.stage](args)
