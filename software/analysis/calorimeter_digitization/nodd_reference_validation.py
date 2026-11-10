#!/usr/bin/env python3
"""Source-pinned original/native validation of fresh full LAYOUT-001 samples.

Run through the read-only Key4hep installation's key4hep_run.sh. The completed
ODD runner is reused as an explicitly pinned library; its source/data are never
edited. All ROOT/JSONL payloads stay in a fresh ignored work directory.
"""
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
LOADED_SOURCE=Path(__file__).read_bytes()
HELPER_PATH=Path(__file__).with_name('reference_validation.py')
HELPER_PIN='483710f30c9942bc6e865c6d3656f80ed60f4c27c70d64d0c6d9ad2b65861554'
PROTOCOL=ROOT/'docs/validation/issue117/nodd-digitization-protocol.md'
LOADED_PROTOCOL=PROTOCOL.read_bytes() if PROTOCOL.exists() else b''
MIP=.00014875
DESCRIPTOR='system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6'
COLLECTIONS=[('BARRELHits','NODDI117BarrelDigi','NODDI117BarrelID','barrel'),
             ('EDGEHits','NODDI117EndcapDigi','NODDI117EndcapID','endcap')]
SYSTEMS={'BARRELHits':8,'EDGEHits':9}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def save_new(path,value):
    path=Path(path)
    if path.exists():raise RuntimeError('Refusing evidence overwrite: '+str(path))
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def load_helper(path=HELPER_PATH,expected=HELPER_PIN):
    if sha(path)!=expected:raise RuntimeError('Loaded helper differs from pinned source')
    spec=importlib.util.spec_from_file_location('_nodd_reference_helpers',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    if hashlib.sha256(module.LOADED_SOURCE).hexdigest()!=expected:raise RuntimeError('Helper loaded-byte mismatch')
    module.NAMES=list(COLLECTIONS);module.PROTOCOL=PROTOCOL
    module.LOADED_PROTOCOL=LOADED_PROTOCOL
    return module


def artifact(item):
    path=Path(item['path']).resolve()
    if sha(path)!=item['sha256']:raise RuntimeError('Changed declared artifact: '+str(path))
    return path


def validate_input(data):
    if data.get('geometry_label',data.get('geometry'))!='LAYOUT-001':raise RuntimeError('Expected fresh LAYOUT-001 geometry')
    compact=artifact(data['compact'])
    libraries=[artifact(v) for v in data['libraries']]
    if not libraries:raise RuntimeError('All actual factory libraries are required')
    samples=data['samples'];seen=set();seen_paths=set()
    if not samples:raise RuntimeError('No samples declared')
    for sample in samples:
        if sample['id'] in seen or not sample['id'] or Path(sample['id']).name!=sample['id']:raise RuntimeError('Repeated/unsafe sample ID')
        seen.add(sample['id']);path=artifact(sample)
        if path in seen_paths:raise RuntimeError('Repeated raw input file across populations')
        seen_paths.add(path)
        if sample['exit_code']!=0 or sample['events']<=0:raise RuntimeError('Incomplete generated sample')
    receipts=[artifact(v) for v in data.get('artifacts',data.get('receipts',[]))]
    return compact,libraries,receipts


def receipt_dependencies(paths):
    """Verify producer-declared source and closed transport evidence as well."""
    result=set(paths);pending=list(paths)
    for path in pending:
        if path.suffix!='.json':continue
        value=json.loads(path.read_text())
        for source,digest in value.get('immutable',{}).items():
            p=artifact(dict(path=source,sha256=digest));result.add(p)
        for item in value.get('receipts',[]):
            if isinstance(item,dict) and 'path' in item and 'sha256' in item:
                p=artifact(item)
                if p not in result:result.add(p);pending.append(p)
        for name,key in [('commands.mac','macro_sha256'),('transport.log','log_sha256'),('producer.py','producer_sha256'),('steering.py','steering_sha256'),('native-transport-audit.json','native_transport_audit_sha256')]:
            if key in value:
                p=path.parent/name
                if p.is_file() or key=='steering_sha256' or 'native_transport_audit_sha256' in value:result.add(artifact(dict(path=p,sha256=value[key])))
        for row in value.get('samples',[]):
            if 'rng_audit_path' in row:
                p=Path(row['rng_audit_path'])
                result.add(artifact(dict(path=p,sha256=row['rng_audit_sha256'])))
                result.add(artifact(dict(path=str(p)+'.state',sha256=row['rng_state_sha256'])))
    return result


def xml_closure(compact):
    """Resolve all referenced XML/GDML files without modifying any source."""
    trees={};pending=[Path(compact).resolve()]
    while pending:
        path=pending.pop()
        if path in trees:continue
        tree=ET.parse(path);trees[path]=tree
        for node in tree.getroot().iter():
            ref=node.get('ref')
            if ref and node.tag in ('include','gdmlFile'):
                target=(path.parent/ref).resolve()
                if not target.is_file():raise RuntimeError('Unresolved geometry reference: '+str(target))
                pending.append(target)
    return trees


def wrapper(compact,destination):
    trees=xml_closure(compact);codes={};roots={};all_roots=set();sides=set()
    for path,tree in trees.items():
        root=tree.getroot()
        for node in root.findall('.//readout'):
            name=node.get('name');text=node.findtext('id')
            if name in SYSTEMS:
                if name in codes:raise RuntimeError('Duplicate target readout')
                codes[name]=(text or '').strip()
        for node in root.findall('.//detectors/detector'):
            root_id=int(node.get('id'))
            if root_id in all_roots:raise RuntimeError('Duplicate constructed root ID')
            all_roots.add(root_id)
            name=node.get('readout')
            if name in SYSTEMS:
                if name in roots:raise RuntimeError('Duplicate target detector root')
                roots[name]=root_id
        for node in root.findall('.//replica'):
            if node.get('side') in ('1','2'):sides.add(int(node.get('side')))
        if root.findall('.//fields/field'):raise RuntimeError('LAYOUT-001 reference requires the declared field-free scope')
    if codes!={n:DESCRIPTOR for n in SYSTEMS} or roots!=SYSTEMS:raise RuntimeError('Wrong integrated root IDs/readout namespace/encoding')
    if all_roots!=set(range(10)):raise RuntimeError('Complete maintained tracker+pipe0-7 and ECAL8/9 required')
    if sides!={1,2}:raise RuntimeError('Both configured endcap sides are required')
    source=Path(compact).resolve();root=ET.parse(source).getroot();define=root.find('define')
    if define is None:define=ET.SubElement(root,'define')
    constants={n[2] for n in COLLECTIONS}
    if any(n.get('name') in constants for n in define):raise RuntimeError('Encoding constant collision')
    def canonical(node):
        attrs=dict(node.attrib)
        if attrs.get('ref') and node.tag in ('include','gdmlFile'):attrs['ref']=str((source.parent/attrs['ref']).resolve())
        return node.tag,attrs,(node.text or '').strip(),[canonical(c) for c in node if c.get('name') not in constants]
    before=canonical(root)
    for node in root.iter():
        if node.get('ref') and node.tag in ('include','gdmlFile'):node.set('ref',str((source.parent/node.get('ref')).resolve()))
    for sim,_,constant,_ in COLLECTIONS:ET.SubElement(define,'constant',name=constant,type='string',value=codes[sim])
    if canonical(root)!=before:raise RuntimeError('Wrapper changed source geometry semantics')
    if Path(destination).exists():raise RuntimeError('Refusing wrapper overwrite')
    ET.indent(root);ET.ElementTree(root).write(destination,encoding='utf-8',xml_declaration=True)
    return dict(encodings=codes,root_ids=roots,all_constructed_root_ids=sorted(all_roots),configured_endcap_sides=sorted(sides),only_added_string_constants=True),list(trees)


def source_identity(h):
    return dict(runner_sha256=hashlib.sha256(LOADED_SOURCE).hexdigest(),helper_sha256=hashlib.sha256(h.LOADED_SOURCE).hexdigest(),protocol_sha256=hashlib.sha256(LOADED_PROTOCOL).hexdigest())


def freeze(a,h):
    for path in (Path(__file__),HELPER_PATH,PROTOCOL):
        committed=subprocess.check_output(['git','show','HEAD:'+str(path.relative_to(ROOT))],cwd=ROOT)
        if hashlib.sha256(committed).hexdigest()!=sha(path):raise RuntimeError('Commit exact producer/helper/protocol before execution')
    expected=source_identity(h)
    if sha(HELPER_PATH)!=HELPER_PIN:raise RuntimeError('Pinned helper changed')
    target=a.work/'execution-source.json'
    if target.exists():
        if json.loads(target.read_text())!=expected:raise RuntimeError('Frozen execution source identity changed; use a fresh work directory')
    else:save_new(target,expected)


def prepare(a,h):
    if a.work.exists():raise RuntimeError('Choose a fresh --work directory')
    data=json.loads(a.input_manifest.read_text());compact,libraries,receipts=validate_input(data)
    prefix=a.framework/'software/build/key4hep/install'
    if Path(shutil.which('k4run') or '').resolve()!=(prefix/'bin/k4run').resolve():raise RuntimeError('Activate the actual original Key4hep installation')
    sources={}
    for name in ('Gaudi','k4FWCore','k4RecCalorimeter','k4SimGeant4','MarlinReco'):
        folder=a.framework/'software/submodules'/name
        if h.git(folder,'status','--porcelain'):raise RuntimeError('Dirty original framework source')
        sources[name]=h.git(folder,'rev-parse','HEAD')
    if sources['k4RecCalorimeter']!=h.KEY4_PIN:raise RuntimeError('Wrong original processor source')
    a.work.mkdir(parents=True);proof,xmls=wrapper(compact,a.work/'wrapper.xml')
    (a.work/'runner-source.py').write_bytes(LOADED_SOURCE);(a.work/'helper-source.py').write_bytes(h.LOADED_SOURCE)
    paths=[a.input_manifest,PROTOCOL,Path(__file__),HELPER_PATH,compact,*xmls,*libraries,*receipt_dependencies(receipts),a.comparator,a.backend,a.native_validation,a.work/'wrapper.xml',a.work/'runner-source.py',a.work/'helper-source.py']
    for lib in libraries:
        registration=lib.with_suffix('.components')
        if registration.exists():paths.append(registration)
    paths+=list((prefix/'lib').glob('*.dylib'))+list((prefix/'lib').glob('*.so'))+[prefix/'bin/k4run']
    native=ROOT/'software/source/ActsExamples/Calorimeter'
    paths += [p for p in native.rglob('*') if p.is_file() and p.suffix in ('.cpp','.hpp','.hh')]
    paths += [Path(s['path']) for s in data['samples']]
    import ROOT as R
    save_new(a.work/'manifest.json',dict(status='PROTOTYPE full nODD original/native reference',geometry_label='LAYOUT-001',geometry=proof,
        repository_revision=h.git(ROOT,'rev-parse','HEAD'),producer_scoped_dirty_status=h.git(ROOT,'status','--porcelain','--',str(Path(__file__).relative_to(ROOT)),str(HELPER_PATH.relative_to(ROOT)),str(PROTOCOL.relative_to(ROOT))),
        compact=str(compact),libraries=[str(v) for v in libraries],sources=sources,prefix=str(prefix),samples=data['samples'],
        response=dict(mip_energy_GeV=MIP,threshold_MIP=.6,dynamic_range_MIP=2500),comparator=str(a.comparator),backend=str(a.backend),native_validation=str(a.native_validation),
        immutable={str(p.resolve()):sha(p) for p in paths},loaded_sources=source_identity(h),runtime=dict(Python=platform.python_version(),ROOT=R.gROOT.GetVersion()),
        input_manifest_sha256=sha(a.input_manifest)))
    print('Prepared',len(data['samples']),'samples',sum(s['events'] for s in data['samples']),'declared events',flush=True)


def verify(a,h):
    m=h.verify(a.work)
    if m['loaded_sources']!=source_identity(h):raise RuntimeError('Actual loaded runner/helper/protocol differs from preparation')
    return m


def execute(a,h,directory,name,command,environment=None):
    log=directory/(name+'.log');receipt=directory/(name+'.execution.json')
    if log.exists() or receipt.exists():raise RuntimeError('Refusing execution evidence overwrite')
    inputs={str(Path(v).resolve()):sha(v) for v in command if Path(v).is_file()}
    start=time.monotonic()
    with log.open('w') as stream:result=subprocess.run(command,cwd=ROOT,env=environment,stdout=stream,stderr=subprocess.STDOUT)
    record=dict(command=command,exit_code=result.returncode,elapsed_seconds=time.monotonic()-start,log=str(log),log_sha256=sha(log),loaded_sources=source_identity(h),input_files=inputs)
    save_new(receipt,record)
    return record


def original(a,h,m,source,directory,pair,noise,seed):
    if directory.exists():raise RuntimeError('Refusing original output directory overwrite')
    directory.mkdir(parents=True)
    code='import ROOT\n'
    for library in m['libraries']:code+=f'assert ROOT.gSystem.Load({library!r})>=0, "Factory load failed"\n'
    code+=h.write_steering(a.work,source,directory/'original.root',pair,noise,seed,-1)
    (directory/'steering.py').write_text(code)
    (directory/'runner-source.py').write_bytes(LOADED_SOURCE);(directory/'helper-source.py').write_bytes(h.LOADED_SOURCE)
    env=os.environ.copy();directories=os.pathsep.join(dict.fromkeys(str(Path(v).parent) for v in m['libraries']))
    for key in ('DD4HEP_LIBRARY_PATH','DYLD_LIBRARY_PATH','LD_LIBRARY_PATH'):env[key]=directories+os.pathsep+env.get(key,'')
    rec=execute(a,h,directory,'original',[sys.executable,shutil.which('k4run'),str(directory/'steering.py')],env)
    if rec['exit_code']!=0:raise RuntimeError('Original Gaudi failed; inspect '+str(directory/'original.log'))
    # Completion is a new immutable receipt; the launch receipt remains intact.
    save_new(directory/'original-complete.json',dict(input_sha256=sha(source),output_sha256=sha(directory/'original.root'),steering_sha256=sha(directory/'steering.py'),seed=seed,pair_energy_eV=pair,noise_MIP=noise))
    return directory/'original.root'


def validate_cell_id(cid,collection):
    side=(cid>>8)&3
    if cid&255!=SYSTEMS[collection] or cid>>42 or ((cid>>14)&63)>=48:raise RuntimeError('Invalid nODD cell ID namespace')
    if side not in ({0} if collection=='BARRELHits' else {1,2}):raise RuntimeError('Wrong nODD cell side')
    return side


def id_audit(source):
    from podio import root_io
    counts={n:{} for n in SYSTEMS};events=0
    for frame in root_io.Reader(str(source)).get('events'):
        events+=1
        for sim in SYSTEMS:
            seen=set()
            for hit in frame.get(sim):
                cid=int(hit.getCellID());side=validate_cell_id(cid,sim)
                if cid in seen:raise RuntimeError('Duplicated nODD cell ID')
                seen.add(cid);counts[sim][str(side)]=counts[sim].get(str(side),0)+1
    return dict(events=events,counts_by_collection_side=counts,system_ids=SYSTEMS,invalid_ids=0)


def deterministic(a,h,m,sample,source,directory,pilot=False):
    output=original(a,h,m,source,directory,0,0,125000)
    config=dict(m['response'],pair_energy_eV=0,noise_MIP=0,seed=125001,reference_energy_unit='MIP',input_position_contract='cell-centres',
        timing_mode='all contributions; energy comparison only',absolute_tolerance_MIP=1e-5,relative_tolerance=5e-6,header_collection='EventHeader',
        collections=[dict(sim=s,reference=o,encoding_constant=e,layout=l) for s,o,e,l in COLLECTIONS],sha256_tool='/usr/bin/shasum',input_sha256=sha(source),reference_sha256=sha(output),
        reference_producer=dict(kind='original-framework',repository='key4hep/k4RecCalorimeter',revision=h.KEY4_PIN,processor='DigitiserSiliconMip',runtime_identity=sha(Path(m['prefix'])/'lib/libRecCaloDigi.dylib'),steering_sha256=sha(directory/'steering.py')))
    save_new(directory/'comparison.json',config)
    rec=execute(a,h,directory,'comparison',[m['comparator'],str(source),str(output),str(directory/'comparison.json'),str(directory/'comparison-summary.json'),m['backend']])
    if rec['exit_code']!=0:raise RuntimeError('nODD deterministic gate failed: '+str(directory))
    save_new(directory/'comparison-complete.json',dict(output_sha256=sha(directory/'comparison-summary.json')))
    result=json.loads((directory/'comparison-summary.json').read_text());ids=id_audit(source)
    if result['events']!=sample['events'] or ids['events']!=sample['events']:raise RuntimeError('nODD denominator mismatch')
    audit=h.retained_audit(source,output)
    save_new(directory/'validated.json',dict(sample={k:v for k,v in sample.items() if k!='path'},result={k:v for k,v in result.items() if k not in ('configuration','limitations')},
        strict_reference_tolerance=h.strict_bound(result),retained_audit=audit,id_audit=ids,pilot=pilot,
        source_sha256=sha(source),output_sha256=sha(output)))
    print(sample['id'],'PASS',result['events'],'events',result['matched_cells'],'cells',flush=True)


def run_deterministic(a,h):
    m=verify(a,h);freeze(a,h)
    if a.stage=='pilot':
        from podio import root_io
        sample=dict(m['samples'][0],id='pilot',events=2);directory=a.work/'pilot-input';directory.mkdir(exist_ok=False)
        reader=root_io.Reader(sample['path']).get('events');source=directory/'input.root';writer=root_io.Writer(str(source))
        for i in range(2):writer.write_frame(reader[i],'events')
        writer.finish();deterministic(a,h,m,sample,source,a.work/'pilot',True)
    else:
        for sample in m['samples']:deterministic(a,h,m,sample,Path(sample['path']),a.work/'deterministic'/sample['id'])


def replay_sources(samples):
    targets=[('mu-',10,0),('gamma',20,2)];selected=[]
    for particle,energy,eta in targets:
        matches=[s for s in samples if s['particle']==particle and s['energy_GeV']==energy and s['eta']==eta]
        if len(matches)!=1:raise RuntimeError('Missing/ambiguous frozen replay origin')
        selected.append(matches[0])
    return selected


def replays(a,h):
    m=verify(a,h);freeze(a,h)
    from podio import root_io
    R=h.io_helpers()
    for fixture,sample in enumerate(replay_sources(m['samples'])):
        directory=a.work/'replays'/str(fixture)
        if directory.exists():raise RuntimeError('Refusing replay overwrite')
        directory.mkdir(parents=True);events=root_io.Reader(sample['path']).get('events');base=events[0]
        names=sorted(n for n in base.getAvailableCollections() if n!='EventHeader');fingerprint=h.fingerprint(base,names)
        head=base.get('EventHeader')[0];metadata=(int(head.getTimeStamp()),float(head.getWeight()),tuple(head.getWeights()))
        source=directory/'input.root';writer=root_io.Writer(str(source))
        for event in range(1000):
            frame=events[0];R.I117ReplayHeader(frame._frame,125800+1000*fixture+event,event)
            if h.fingerprint(frame,names)!=fingerprint:raise RuntimeError('Replay changed nonheader data')
            writer.write_frame(frame,'events')
        writer.finish();roundtrip=root_io.Reader(str(source)).get('events')
        if len(roundtrip)!=1000:raise RuntimeError('Replay persistence denominator mismatch')
        for event,frame in enumerate(roundtrip):
            head=frame.get('EventHeader')[0]
            if (int(head.getRunNumber()),int(head.getEventNumber()))!=(125800+1000*fixture+event,event):raise RuntimeError('Replay IDs did not persist')
            if (int(head.getTimeStamp()),float(head.getWeight()),tuple(head.getWeights()))!=metadata or h.fingerprint(frame,names)!=fingerprint:raise RuntimeError('Replay altered metadata/payload/MC endpoints')
        save_new(directory/'replay.json',dict(fixture=fixture,source_sample=sample['id'],source_event_index=0,source_sha256=sha(sample['path']),
            input_sha256=sha(source),events=1000,payload_sha256=fingerprint,header_run_base=125800+1000*fixture,
            only_run_event_ids_changed=True,loaded_sources=source_identity(h)))
        print('Replay',fixture,'PASS',source.stat().st_size,'bytes',flush=True)


def native(a,h,m,source,directory,fixture,mode):
    name=['P','PN'][mode];config=dict(m['response'],seed=125300+2*fixture+mode,collections=[n[0] for n in COLLECTIONS],save_cells=True,
        modes=[dict(name=name,pair_energy_eV=3.6,noise_MIP=[0,.13][mode])])
    save_new(directory/'native-config.json',config)
    rec=execute(a,h,directory,'native',[m['native_validation'],str(source),str(directory/'native-config.json'),str(directory/'native.jsonl'),m['backend']])
    if rec['exit_code']!=0:raise RuntimeError('Actual native algorithm failed')
    save_new(directory/'native-complete.json',dict(executable_sha256=sha(m['native_validation']),config_sha256=sha(directory/'native-config.json'),input_sha256=sha(source),output_sha256=sha(directory/'native.jsonl')))


def stochastic(a,h):
    m=verify(a,h);freeze(a,h)
    for sample in m['samples']:
        if not (a.work/'deterministic'/sample['id']/'validated.json').is_file():raise RuntimeError('Complete deterministic gate required first')
    for fixture in (0,1):
        source=a.work/'replays'/str(fixture)/'input.root';replay=json.loads(source.with_name('replay.json').read_text())
        if sha(source)!=replay['input_sha256']:raise RuntimeError('Changed replay input')
        for mode,name in enumerate(('P','PN')):
            directory=a.work/'stochastic'/f'{fixture}-{name}';verify(a,h)
            output=original(a,h,m,source,directory,3.6,[0,.13][mode],125200+2*fixture+mode)
            save_new(directory/'seed-audit.json',h.seed_audit(directory,1000))
            save_new(directory/'retained-audit.json',h.retained_audit(source,output))
            native(a,h,m,source,directory,fixture,mode)
            print('Stochastic execution',fixture,name,'complete',flush=True)


def verify_case(directory,expected_sources=None):
    """Close receipt/raw/config/source chains before consuming results."""
    for path in directory.glob('*.execution.json'):
        record=json.loads(path.read_text())
        if record['exit_code']!=0 or sha(record['log'])!=record['log_sha256']:raise RuntimeError('Failed/changed execution receipt')
        if expected_sources is not None and record['loaded_sources']!=expected_sources:raise RuntimeError('Changed loaded producer/helper identity')
        for source,digest in record['input_files'].items():
            if sha(source)!=digest:raise RuntimeError('Changed command input/configuration')
    if expected_sources is not None:
        for name,key in [('runner-source.py','runner_sha256'),('helper-source.py','helper_sha256')]:
            if sha(directory/name)!=expected_sources[key]:raise RuntimeError('Changed source snapshot')
    original=json.loads((directory/'original-complete.json').read_text())
    if sha(directory/'original.root')!=original['output_sha256'] or sha(directory/'steering.py')!=original['steering_sha256']:raise RuntimeError('Changed original output/configuration')
    if (directory/'native-complete.json').exists():
        native=json.loads((directory/'native-complete.json').read_text())
        if sha(directory/'native.jsonl')!=native['output_sha256'] or sha(directory/'native-config.json')!=native['config_sha256']:raise RuntimeError('Changed native output/configuration')
    if (directory/'comparison.json').exists():
        config=json.loads((directory/'comparison.json').read_text())
        if config['reference_sha256']!=original['output_sha256']:raise RuntimeError('Comparison input chain mismatch')
        complete=json.loads((directory/'comparison-complete.json').read_text())
        if sha(directory/'comparison-summary.json')!=complete['output_sha256']:raise RuntimeError('Changed deterministic comparison result')


def stochastic_summary(a,h,fixture,mode):
    import numpy as np
    from podio import root_io
    name=['P','PN'][mode];directory=a.work/'stochastic'/f'{fixture}-{name}';verify_case(directory,source_identity(h))
    frames=root_io.Reader(str(directory/'original.root')).get('events')
    rows=[json.loads(line) for line in (directory/'native.jsonl').read_text().splitlines()]
    energy=[[],[]];counts=[[],[]];amplitudes=[[],[]]
    for frame,row in zip(frames,rows,strict=True):
        head=frame.get('EventHeader')[0]
        if row['identity']!=[int(head.getRunNumber()),int(head.getEventNumber())]:raise RuntimeError('Stochastic Header alignment mismatch')
        values=[float(hit.getEnergy()) for _,out,_,_ in COLLECTIONS for hit in frame.get(out)]
        energy[0].append(math.fsum(values));counts[0].append(len(values));amplitudes[0].extend(values)
        result=row['modes'][name];accepted=[float(v) for cells in result['cells'].values() for _,v in cells if v>float(np.float32(.6))]
        if len(accepted)!=result['accepted_cells'] or not math.isclose(math.fsum(accepted)*MIP,result['energy_GeV'],rel_tol=1e-12,abs_tol=1e-14):raise RuntimeError('Native cell/total closure mismatch')
        energy[1].append(result['energy_GeV']/MIP);counts[1].append(result['accepted_cells']);amplitudes[1].extend(accepted)
    def edges(values):
        lo=min(map(min,values));hi=max(map(max,values));pad=.05*max(hi-lo,abs(lo)*1e-6,1e-6)
        return np.linspace(lo-pad,hi+pad,81)
    ee=edges(energy);ce=np.arange(min(map(min,counts))-.5,max(map(max,counts))+1.5)
    ae=np.r_[np.linspace(0,10,501),np.arange(20,1001,10),np.arange(1100,2601,100)]
    tests={key:h.distribution_gate(*values,126000+2*fixture+mode,key=='event_energy_MIP') for key,values in [('event_energy_MIP',energy),('accepted_cell_count',counts)]}
    sides=[]
    for index in range(2):sides.append(dict(event_energy_MIP=h.measures(energy[index],ee),accepted_cell_count=h.measures(counts[index],ce),accepted_cell_amplitude_MIP=h.measures(amplitudes[index],ae)))
    return dict(fixture=['nODD central muon','nODD endcap gamma20'][fixture],mode=name,events=1000,passed=all(t['passed'] for t in tests.values()),
        tests=tests,seeds=h.seed_audit(directory,1000),original=sides[0],native=sides[1])


def summarize(a,h):
    if a.output.exists():raise RuntimeError('Refusing compact result overwrite')
    m=verify(a,h);det=[];sides={n:{} for n in SYSTEMS}
    for sample in m['samples']:
        directory=a.work/'deterministic'/sample['id'];verify_case(directory,source_identity(h))
        row=json.loads((directory/'validated.json').read_text())
        if row['source_sha256']!=sha(sample['path']) or row['output_sha256']!=sha(directory/'original.root'):raise RuntimeError('Changed audited raw files')
        for name,counts in row['id_audit']['counts_by_collection_side'].items():
            for side,n in counts.items():sides[name][side]=sides[name].get(side,0)+n
        det.append(row)
    if not sides['BARRELHits'].get('0') or not all(sides['EDGEHits'].get(s) for s in ('1','2')):raise RuntimeError('Full barrel/both-endcap hit coverage not measured')
    stoch=[stochastic_summary(a,h,f,mode) for f in (0,1) for mode in (0,1)]
    receipts=[dict(role=str(p.relative_to(a.work)),**json.loads(p.read_text())) for p in sorted(a.work.rglob('*.execution.json'))]
    artifacts={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in a.work.rglob('*') if p.is_file() and 'controller' not in p.name}
    save_new(a.output,h.public(dict(status='PROTOTYPE full LAYOUT-001 original/native software comparison',geometry=m['geometry'],sources=m['sources'],runtime=m['runtime'],repository_revision=m['repository_revision'],producer_scoped_dirty_status=m['producer_scoped_dirty_status'],
        deterministic=dict(passed=all(d['result']['passed'] for d in det),cases=len(det),events=sum(d['result']['events'] for d in det),samples=det,counts_by_collection_side=sides),
        stochastic=dict(passed=all(s['passed'] for s in stoch),comparisons=stoch),response=m['response'],loaded_sources=source_identity(h),
        execution_receipts=receipts,artifacts=artifacts,immutable_source_runtime_inputs=m['immutable'],
        limitations=['Maintained tracker+complete ECAL only; field/HCAL/FCAL absent.','Conditional replay ensembles repeat two real events, not independent showers.',
                    'Energy/selection only; timing, waveforms, empty-detector noise occupancy and detector acceptance not established.'])))
    print('Wrote',a.output,flush=True)


def main():
    global PROTOCOL,LOADED_PROTOCOL
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['prepare','pilot','deterministic','replays','stochastic','summarize'])
    p.add_argument('--input-manifest',type=Path,default=ROOT/'build/issue117/nodd/reference-input.json')
    p.add_argument('--protocol',type=Path,default=PROTOCOL)
    p.add_argument('--work',type=Path,default=ROOT/'build/issue117/nodd-reference-validation')
    p.add_argument('--framework',type=Path,default=ROOT.parent/'nodd-pr123-frameworks')
    p.add_argument('--comparator',type=Path,default=Path('/private/tmp/nodd-digitization117-build/EDM4hep/nodd_silicon_reference'))
    p.add_argument('--backend',type=Path,default=Path('/private/tmp/nodd-digitization117-build/nodd_marlin_silicon_backend'))
    p.add_argument('--native-validation',type=Path,default=Path('/private/tmp/nodd-digitization117-build/EDM4hep/nodd_silicon_validation'))
    p.add_argument('--output',type=Path,default=ROOT/'docs/validation/issue117/previews/nodd-digitization-reference.json')
    a=p.parse_args()
    for key in ('work','framework','input_manifest','comparator','backend','native_validation','output'):setattr(a,key,getattr(a,key).resolve())
    PROTOCOL=a.protocol.resolve();LOADED_PROTOCOL=PROTOCOL.read_bytes()
    h=load_helper()
    if a.stage=='prepare':prepare(a,h)
    elif a.stage in ('pilot','deterministic'):run_deterministic(a,h)
    else:{'replays':replays,'stochastic':stochastic,'summarize':summarize}[a.stage](a,h)


if __name__=='__main__':main()
