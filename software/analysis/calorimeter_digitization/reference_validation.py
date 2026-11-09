#!/usr/bin/env python3
"""Original Key4hep same-hit validation, distinct from the native GPL helper.

Run through the installed checkout's software/env/key4hep_run.sh. All event
payloads, replay inputs and execution logs remain in a fresh ignored work tree.
Only summarize emits the compact public result. No source/install is changed.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
LOADED_SOURCE=Path(__file__).read_bytes()
PROTOCOL=ROOT/'docs/validation/issue117/digitization-protocol.md'
LOADED_PROTOCOL=PROTOCOL.read_bytes() if PROTOCOL.exists() else b''
KEY4_PIN = '03b3676cecbdf85818f6de159ecf90ffe2482cec'
MIP = .00014875
NAMES = [('ECalBarrelCollection', 'I117EcalBarrelDigi', 'I117EcalBarrelID', 'barrel'),
         ('ECalEndcapCollection', 'I117EcalEndcapDigi', 'I117EcalEndcapID', 'endcap')]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda: f.read(1024*1024), b''): h.update(data)
    return h.hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def public(value):
    return json.loads(json.dumps(value).replace(str(ROOT), '${NODD_REPO}').replace(str(Path.home()), '${USER_HOME}'))


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def execute(command, directory, name, environment=None):
    receipt = directory/(name+'.execution.json');log = directory/(name+'.log')
    if receipt.exists() or log.exists(): raise RuntimeError('Refusing execution evidence overwrite: '+str(log))
    start = time.monotonic()
    with log.open('w') as stream:
        result = subprocess.run(command, cwd=ROOT, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    record = dict(command=command, exit_code=result.returncode, elapsed_seconds=time.monotonic()-start,
                  log=str(log), log_sha256=sha(log), producer_sha256=hashlib.sha256(LOADED_SOURCE).hexdigest(),protocol_sha256=hashlib.sha256(LOADED_PROTOCOL).hexdigest())
    save(receipt, record)
    return record


def verify(work):
    m = json.loads((work/'manifest.json').read_text())
    for path, digest in m['immutable'].items():
        if sha(path)!=digest: raise RuntimeError('Changed source/runtime/input: '+path)
    return m


def prepare(a):
    if a.work.exists(): raise RuntimeError('Choose a fresh --work directory')
    prefix = a.framework/'software/build/key4hep/install'
    if Path(shutil.which('k4run') or '').resolve()!=(prefix/'bin/k4run').resolve():
        raise RuntimeError('Activate the specified original Key4hep installation first')
    immutable = {};sources = {}
    for package in ('Gaudi', 'k4FWCore', 'k4RecCalorimeter', 'k4SimGeant4', 'MarlinReco'):
        folder=a.framework/'software/submodules'/package
        if git(folder,'status','--porcelain'): raise RuntimeError('Dirty original source: '+package)
        sources[package]=git(folder,'rev-parse','HEAD')
    if sources['k4RecCalorimeter']!=KEY4_PIN: raise RuntimeError('Unexpected original processor pin')
    source = a.framework/'software/submodules/k4RecCalorimeter/RecCaloDigi'
    paths=[source/'src/BaseDigitiser.cc',source/'src/DigitiserSiliconMip.cc',source/'include/BaseDigitiser.h',
           a.framework/'software/submodules/k4FWCore/k4FWCore/components/UniqueIDGenSvc.cpp',
           prefix/'lib/libRecCaloDigi.dylib',prefix/'lib/libk4RecCaloDigiPlugins.so',prefix/'lib/libk4FWCorePlugins.so',
           prefix/'lib/libk4GeoSvc.so',prefix/'bin/k4run',a.comparator,a.backend,a.odd_library,
           a.odd/'xml/OpenDataDetector.xml',ROOT/'software/source/ActsExamples/Calorimeter/EDM4hep/SiliconReferenceComparison.cpp',
           ROOT/'software/source/ActsExamples/Calorimeter/upstream/marlin/Backend.cpp']
    paths=[p for p in paths if p.exists()]
    paths += list((prefix/'lib').glob('*.dylib'))+list((prefix/'lib').glob('*.so'))
    samples=[]
    for kind in ('muons','showers'):
        manifest=ROOT/'build/issue117'/kind/'samples.json';paths.append(manifest)
        data=json.loads(manifest.read_text())
        if data['odd_revision']!=git(a.odd,'rev-parse','HEAD') or data['odd_library_sha256']!=sha(a.odd_library):
            raise RuntimeError('ODD source/library differs from generated samples')
        for sample in data['samples']:
            path=Path(sample['path'])
            if sha(path)!=sample['sha256'] or sample['exit_code']!=0: raise RuntimeError('Invalid raw sample: '+str(path))
            samples.append(dict(id=path.parent.name,path=str(path),events=sample['requested_events'],particle=sample['particle'],energy_GeV=sample['energy_GeV'],eta=sample['eta']))
            paths.append(path)
    # GeoSvc needs named encoding constants. Copy the actual ODD readout strings.
    readouts=ET.parse(a.odd/'xml/detectors/CalorimeterECal.xml').getroot().findall('.//readout')
    codes={r.get('name'):r.findtext('id').strip() for r in readouts}
    a.work.mkdir(parents=True)
    original_compact=a.odd/'xml/OpenDataDetector.xml'
    wrapper=ET.parse(original_compact).getroot();define=wrapper.find('define')
    def canonical(node):
        attrs=dict(node.attrib)
        if 'ref' in attrs:attrs['ref']=str((original_compact.parent/attrs['ref']).resolve())
        return (node.tag,attrs,(node.text or '').strip(),[canonical(c) for c in node if c.get('name') not in {n[2] for n in NAMES}])
    expected_tree=canonical(wrapper)
    for node in wrapper.iter():
        if 'ref' in node.attrib:node.set('ref',str((original_compact.parent/node.get('ref')).resolve()))
    for sim,_,constant,_ in NAMES:
        code=codes[sim]
        if 'layer:' not in code: raise RuntimeError('No layer field in actual encoding')
        ET.SubElement(define,'constant',name=constant,type='string',value=code)
    if canonical(wrapper)!=expected_tree:raise RuntimeError('Wrapper changed original compact semantics')
    ET.indent(wrapper);ET.ElementTree(wrapper).write(a.work/'wrapper.xml',encoding='utf-8',xml_declaration=True)
    (a.work/'prepare-producer.py').write_bytes(LOADED_SOURCE)
    paths += list((a.odd/'xml').rglob('*.xml'))+[a.work/'wrapper.xml',a.work/'prepare-producer.py']
    immutable={str(p.resolve()):sha(p) for p in paths}
    import ROOT as R
    save(a.work/'manifest.json',dict(status='PROTOTYPE original-framework comparison',source_revision=git(ROOT,'rev-parse','HEAD'),
        sources=sources,odd_revision=git(a.odd,'rev-parse','HEAD'),framework=str(a.framework),prefix=str(prefix),
        comparator=str(a.comparator),backend=str(a.backend),odd_library=str(a.odd_library),
        encodings={sim:codes[sim] for sim,_,_,_ in NAMES},samples=samples,immutable=immutable,
        runtime=dict(Python=platform.python_version(),ROOT=R.gROOT.GetVersion()),
        response=dict(mip_energy_GeV=MIP,threshold_MIP=.6,dynamic_range_MIP=2500),
        seed_contract='Original TRandom3 seeded per event by UniqueIDGenSvc(global Seed, run/event header, algorithm name); native CLHEP event-mixed independent stream.'))
    print('Prepared',len(samples),'verified raw samples')


def write_steering(work, input_path, output, pair, noise, seed, count):
    # These are original upstream Gaudi components, not a substitute algorithm.
    text='''from Configurables import GeoSvc, UniqueIDGenSvc, DigitiserSiliconMip, EventDataSvc
from k4FWCore import ApplicationMgr, IOSvc
io=IOSvc("IOSvc")
io.Input=INPUT
io.Output=OUTPUT
io.OutputType="ROOT"
io.outputCommands=["keep *"]
geo=GeoSvc("GeoSvc",detectors=[COMPACT],EnableGeant4Geo=False)
algorithms=[]
for sim,out,encoding,layout in COLLECTIONS:
 algorithms.append(DigitiserSiliconMip("Issue117Reference"+layout,
  inputHitCollection=sim,inputHeaderCollection="EventHeader",outputHitCollection=out,outputRelationCollection=out+"Links",
  EncodingStringParameterName=encoding,CaloType="em",CaloID="ecal",CaloLayout=layout,
  calibration_mip=MIP_SCALE,silicon_pairEnergy=PAIR,elec_noise_mip=NOISE,elec_range_mip=2500.,threshold=.6,thresholdUnit="MIP",
  miscalibration_uncorrel=0.,miscalibration_correl=0.,deadCell_fraction=0.,integrationMethod="Standard",
  timingCut=0,timingCorrectForPropagation=0,timingResolution=0.,timingWindowMin=-1.e30,timingWindowMax=1.e30))
ApplicationMgr(TopAlg=algorithms,EvtSel="NONE",EvtMax=COUNT,
 ExtSvc=[EventDataSvc("EventDataSvc"),geo,UniqueIDGenSvc("UniqueIDGenSvc",Seed=SEED,OutputLevel=2)])
'''
    replacements={'INPUT':repr(str(input_path)),'OUTPUT':repr(str(output)),'COMPACT':repr(str(work/'wrapper.xml')),
                  'COLLECTIONS':repr(NAMES),'MIP_SCALE':repr(MIP),'PAIR':repr(pair),'NOISE':repr(noise),'SEED':str(seed),'COUNT':str(count)}
    for key,value in replacements.items():text=re.sub(r'\b'+key+r'\b',lambda _:value,text)
    return text


def original(work, directory, source, pair=0., noise=0., seed=11890001, count=-1):
    m=verify(work);output=directory/'original.root';steering=directory/'steering.py'
    if output.exists() or steering.exists():raise RuntimeError('Choose a fresh case directory')
    directory.mkdir(parents=True,exist_ok=True)
    steering.write_text(write_steering(work,source,output,pair,noise,seed,count))
    (directory/'producer.py').write_bytes(LOADED_SOURCE)
    env=os.environ.copy();lib=str(Path(m['odd_library']).parent)
    for name in ('DD4HEP_LIBRARY_PATH','DYLD_LIBRARY_PATH','LD_LIBRARY_PATH'):env[name]=lib+os.pathsep+env.get(name,'')
    record=execute([sys.executable,shutil.which('k4run'),str(steering)],directory,'original',env)
    if record['exit_code']!=0:raise RuntimeError('Original Gaudi execution failed; retained '+str(directory/'original.log'))
    record.update(output_sha256=sha(output),steering_sha256=sha(steering),input_sha256=sha(source),global_seed=seed,pair_energy_eV=pair,noise_MIP=noise)
    save(directory/'original.execution.json',record)
    return output


def deterministic(work, source, directory):
    m=verify(work);output=original(work,directory,source)
    config=dict(m['response'],pair_energy_eV=0,noise_MIP=0,seed=117,reference_energy_unit='MIP',input_position_contract='cell-centres',
        timing_mode='all contributions; energy comparison only',absolute_tolerance_MIP=1e-5,relative_tolerance=5e-6,header_collection='EventHeader',
        collections=[dict(sim=s,reference=o,encoding_constant=e,layout=l) for s,o,e,l in NAMES],sha256_tool='/usr/bin/shasum',input_sha256=sha(source),reference_sha256=sha(output),
        reference_producer=dict(kind='original-framework',repository='key4hep/k4RecCalorimeter',revision=KEY4_PIN,processor='DigitiserSiliconMip',
            runtime_identity=sha(Path(m['prefix'])/'lib/libRecCaloDigi.dylib'),steering_sha256=sha(directory/'steering.py')))
    save(directory/'comparison.json',config)
    record=execute([m['comparator'],str(source),str(output),str(directory/'comparison.json'),str(directory/'comparison-summary.json'),m['backend']],directory,'comparison')
    if record['exit_code']!=0:raise RuntimeError('Deterministic comparison failed; retained evidence in '+str(directory))
    result=json.loads((directory/'comparison-summary.json').read_text())
    print(directory.name,'PASS',result['events'],'events',result['matched_cells'],'matched cells',flush=True)
    return result


def pilot(a):
    from podio import root_io
    m=verify(a.work);directory=a.work/a.pilot_name
    directory.mkdir(exist_ok=False)
    sample=m['samples'][0];source=directory/'input.root';reader=root_io.Reader(sample['path']);writer=root_io.Writer(str(source))
    events=reader.get('events')
    for index in range(2):writer.write_frame(events[index],'events')
    writer.finish()
    deterministic(a.work,source,directory/'run')


def deterministic_all(a):
    freeze(a.work)
    m=verify(a.work)
    for sample in m['samples']:
        if a.sample and sample['id']!=a.sample:continue
        directory=a.work/'deterministic'/sample['id']
        if directory.exists():raise RuntimeError('Refusing case overwrite: '+str(directory))
        deterministic(a.work,Path(sample['path']),directory)


def freeze(work):
    for path in (Path(__file__),PROTOCOL):
        committed=subprocess.check_output(['git','show','HEAD:'+str(path.relative_to(ROOT))],cwd=ROOT)
        if hashlib.sha256(committed).hexdigest()!=sha(path):raise RuntimeError('Commit exact source/protocol before bulk: '+str(path))
    target=work/('protocol-'+sha(PROTOCOL)+'.md')
    if target.exists():
        if sha(target)!=sha(PROTOCOL):raise RuntimeError('Frozen protocol changed')
    else:target.write_bytes(PROTOCOL.read_bytes())


def io_helpers():
    import ROOT as R
    if hasattr(R,'I117ReplayHeader'):return R
    if not R.gInterpreter.Declare('''
#include "podio/Frame.h"
#include "edm4hep/EventHeaderCollection.h"
#include <sstream>
#include <iomanip>
void I117ReplayHeader(podio::Frame& f,int run,int event) {
 auto& h=const_cast<edm4hep::EventHeaderCollection&>(f.get<edm4hep::EventHeaderCollection>("EventHeader"));
 const auto stamp=h[0].getTimeStamp();const auto weight=h[0].getWeight();
 const std::vector<double> weights(h[0].getWeights().begin(),h[0].getWeights().end());
 const auto id=h.getID();h.clear();h.setID(id);auto out=h.create();
 out.setRunNumber(run);out.setEventNumber(event);out.setTimeStamp(stamp);out.setWeight(weight);
 for(const auto v:weights)out.addToWeights(v);
}
std::string I117Payload(const podio::Frame& f,const std::vector<std::string>& names) {
 std::ostringstream out;out<<std::setprecision(17);
 for(const auto& n:names) {out<<n<<"\\n";f.get(n)->print(out,false);}
 return out.str();
}'''):raise RuntimeError('Cannot declare read-only payload audit/header adapter')
    return R


def fingerprint(frame,names):
    R=io_helpers()
    digest=hashlib.sha256(str(R.I117Payload(frame._frame,names)).encode())
    # Independently audit relation endpoints, including unavailable endpoints.
    def oid(x):
        v=x.getObjectID();return int(v.collectionID),int(v.index)
    relations=[]
    for name in names:
        for obj in frame.get(name):
            if hasattr(obj,'getParticle'):relations.append((name,oid(obj),oid(obj.getParticle())))
            if hasattr(obj,'getParents'):relations.append((name,oid(obj),[oid(p) for p in obj.getParents()],[oid(p) for p in obj.getDaughters()]))
    digest.update(json.dumps(relations,separators=(',',':')).encode())
    return digest.hexdigest()


def retained_audit(source,output):
    from podio import root_io
    original_events=root_io.Reader(str(source)).get('events');result_events=root_io.Reader(str(output)).get('events')
    if len(original_events)!=len(result_events):raise RuntimeError('Retained denominator mismatch')
    unique=set();payload=hashlib.sha256();contributions=0
    for a,b in zip(original_events,result_events):
        names=sorted(n for n in a.getAvailableCollections() if n!='EventHeader')
        ha=a.get('EventHeader');hb=b.get('EventHeader')
        if len(ha)!=1 or len(hb)!=1:raise RuntimeError('Nonunique header')
        header=lambda h:(int(h.getRunNumber()),int(h.getEventNumber()),int(h.getTimeStamp()),float(h.getWeight()),tuple(h.getWeights()))
        key=header(ha[0])
        if key!=header(hb[0]) or key[:2] in unique:raise RuntimeError('Changed or duplicated event identity')
        unique.add(key[:2]);fa=fingerprint(a,names);fb=fingerprint(b,names)
        if fa!=fb:raise RuntimeError('Retained collection values/MC relation endpoints changed')
        payload.update(fa.encode())
        for sim,_,_,_ in NAMES:
            ids=set()
            for hit in a.get(sim):
                if int(hit.getCellID()) in ids:raise RuntimeError('Duplicate input cell')
                ids.add(int(hit.getCellID()))
                for c in hit.getContributions():
                    if not -1e30<float(c.getTime())<1e30:raise RuntimeError('Contribution outside integration window')
                    contributions+=1
    return dict(events=len(unique),all_original_collections_unchanged=True,MC_relation_endpoints_unchanged=True,
                contribution_times_inside_window=True,contributions=contributions,retained_payload_sha256=payload.hexdigest())


def replays(a):
    freeze(a.work);m=verify(a.work)
    identity=a.work/'B-native-identity.json'
    if identity.exists():raise RuntimeError('Refusing B identity overwrite')
    source_root=ROOT/'software/source/ActsExamples/Calorimeter'
    save(identity,dict(executable=str(a.native_validation),executable_sha256=sha(a.native_validation),
        repository_revision=git(ROOT,'rev-parse','HEAD'),source_sha256={str(p):sha(p) for p in source_root.rglob('*') if p.is_file() and p.suffix in ('.cpp','.hpp','.hh')},
        original_seeds=[119200,119201,119202,119203],native_seeds=[119300,119301,119302,119303],analysis_seeds=[119400,119401,119402,119403],
        pair_energy_eV=3.6,noise_MIP=[0,.13],threshold_MIP=.6,dynamic_range_MIP=2500,mip_energy_GeV=MIP))
    from podio import root_io
    R=io_helpers()
    for fixture,(sample_id,index) in enumerate([('mu-_E10_eta0',250),('gamma_E20_eta2',0)]):
        directory=a.work/'replays'/str(fixture)
        if directory.exists():raise RuntimeError('Refusing replay overwrite')
        directory.mkdir(parents=True);sample=next(s for s in m['samples'] if s['id']==sample_id)
        reader=root_io.Reader(sample['path']);events=reader.get('events');base=events[index]
        names=sorted(n for n in base.getAvailableCollections() if n!='EventHeader');signature=fingerprint(base,names)
        header=base.get('EventHeader')[0];timestamp=int(header.getTimeStamp());weight=float(header.getWeight());weights=tuple(header.getWeights())
        output=directory/'input.root';writer=root_io.Writer(str(output))
        for event in range(1000):
            # This libc++ bitset hash puts event-number changes in high32 bits,
            # discarded by TRandom3. Vary the run field too; audit real seeds.
            frame=events[index];R.I117ReplayHeader(frame._frame,119800+1000*fixture+event,event)
            if fingerprint(frame,names)!=signature:raise RuntimeError('Replay changed nonheader payload')
            writer.write_frame(frame,'events')
        writer.finish();replayed=root_io.Reader(str(output)).get('events')
        if len(replayed)!=1000:raise RuntimeError('Replay denominator changed')
        for event,frame in enumerate(replayed):
            h=frame.get('EventHeader')[0]
            if (int(h.getRunNumber()),int(h.getEventNumber()),int(h.getTimeStamp()))!=(119800+1000*fixture+event,event,timestamp):raise RuntimeError('Replay header mapping failed')
            if float(h.getWeight())!=weight or tuple(h.getWeights())!=weights:raise RuntimeError('Replay changed non-ID header fields')
            if fingerprint(frame,names)!=signature:raise RuntimeError('Persisted replay changed payload/MC relations')
        save(directory/'replay.json',dict(fixture=fixture,source=sample,source_event_index=index,run_number_base=119800+1000*fixture,run_and_event_increment=True,
            events=1000,payload_sha256=signature,input_sha256=sha(output),input_bytes=output.stat().st_size,
            header_ids_only_changed=True,all_original_collections_and_MC_relations_unchanged=True))
        print('Replay',fixture,'PASS',output.stat().st_size,'bytes',flush=True)


def native(work,directory,source,executable,pair,noise,seed,name):
    m=verify(work);directory.mkdir(parents=True,exist_ok=True)
    config=dict(m['response'],seed=seed,collections=[n[0] for n in NAMES],save_cells=True,
                modes=[dict(name=name,pair_energy_eV=pair,noise_MIP=noise)])
    save(directory/'native-config.json',config);output=directory/'native.jsonl'
    if output.exists():raise RuntimeError('Native output already exists')
    record=execute([str(executable),str(source),str(directory/'native-config.json'),str(output),m['backend']],directory,'native')
    record.update(executable_sha256=sha(executable),input_sha256=sha(source),config_sha256=sha(directory/'native-config.json'))
    if record['exit_code']!=0:raise RuntimeError('Native algorithm execution failed')
    record['output_sha256']=sha(output);save(directory/'native.execution.json',record)
    return output


def stochastic(a):
    freeze(a.work);m=verify(a.work)
    identity=json.loads((a.work/'B-native-identity.json').read_text())
    if sha(a.native_validation)!=identity['executable_sha256']:raise RuntimeError('Frozen native executable changed')
    for path,digest in identity['source_sha256'].items():
        if sha(path)!=digest:raise RuntimeError('Frozen native source changed')
    for sample in m['samples']:
        p=a.work/'deterministic'/sample['id']/'comparison-summary.json'
        if not p.exists() or not json.loads(p.read_text())['passed']:raise RuntimeError('Deterministic gate incomplete')
    for fixture in (0,1):
        replay=a.work/'replays'/str(fixture);info=json.loads((replay/'replay.json').read_text());source=replay/'input.root'
        if sha(source)!=info['input_sha256']:raise RuntimeError('Replay changed')
        for mode,(name,noise) in enumerate([('P',0.),('PN',.13)]):
            directory=a.work/'stochastic'/f'{fixture}-{name}'
            output=original(a.work,directory,source,pair=3.6,noise=noise,seed=119200+2*fixture+mode)
            save(directory/'seed-audit.json',seed_audit(directory,1000))
            audit=retained_audit(source,output);save(directory/'retained-audit.json',audit)
            native(a.work,directory,source,a.native_validation,3.6,noise,119300+2*fixture+mode,name)
            print('Stochastic execution',fixture,name,'PASS',flush=True)


def strict_bound(result):
    h=result['normalized_residual'];edges=h['edges']
    occupied=[i for i,n in enumerate(h['counts']) if n]
    if h['underflow'] or h['overflow'] or not occupied:raise RuntimeError('Cannot bound strict reference-only tolerance')
    margin=max(max(abs(edges[i]),abs(edges[i+1])) for i in occupied)
    relative=result['configuration']['relative_tolerance']
    bound=margin/(1-margin*relative)
    passed=bool(result['passed'] and bound<1)
    if not passed:raise RuntimeError('Strict reference-only tolerance not established; perform per-cell audit')
    return dict(passed=True,comparator='absolute + relative*max(abs(native),abs(reference))',
                protocol='absolute + relative*abs(reference)',
                maximum_strict_normalized_residual_upper_bound=bound,
                proof='If e<=m*(strictTol+r*e), then e/strictTol<=m/(1-m*r); histogram occupied-bin edges bound m, with no under/overflow.')


def seed_audit(directory,n):
    text=(directory/'original.log').read_text()
    rows=re.findall(r"Generated ID (\d+) for algorithm '([^']+)' and evt_num=(\d+), run_num=(\d+) \(seed=(\d+)\)",text)
    if len(rows)!=2*n:raise RuntimeError('Missing original effective seed evidence')
    low=[int(v[0])&0xffffffff for v in rows]
    if len(set(low))!=len(low) or 0 in low:raise RuntimeError('Colliding/zero original TRandom3 event seed')
    return dict(event_collection_seeds=len(rows),distinct_nonzero_low32_seeds=len(set(low)),
                seed_log_sha256=sha(directory/'original.log'),
                original='UniqueIDGenSvc hash(global Seed,run,event,algorithm) passed to TRandom3.SetSeed; low32 checked for uniqueness/nonzero',
                native='Recorded base seed+collection index, event-index mixed by pinned CLHEP helper; independent from ROOT draws')


def measures(values,edges):
    import numpy as np
    values=np.asarray(values,dtype=float);counts,_=np.histogram(values,edges)
    counts[-1]-=int(np.count_nonzero(values==edges[-1]))
    return dict(n=len(values),mean=float(values.mean()),sample_sd=float(values.std(ddof=1)),
        sum=float(values.sum()),sum_squared=float(np.dot(values,values)),zeros=int(np.count_nonzero(values==0)),
        quantiles=dict(zip(['q005','q05','q50','q95','q995'],np.quantile(values,[.005,.05,.5,.95,.995]).tolist())),
        histogram=dict(edges=edges.tolist(),counts=counts.tolist(),underflow=int(np.count_nonzero(values<edges[0])),overflow=int(np.count_nonzero(values>=edges[-1])),normalization='counts; all events/cells retained'))


def permutation(a,b,rng):
    import numpy as np
    n=len(a);values=np.r_[a,b];order=np.argsort(values,kind='stable');ends=np.r_[np.flatnonzero(np.diff(values[order])!=0),len(values)-1]
    labels=(order<n).astype(float)
    observed=float(np.abs(np.cumsum(labels/n-(1-labels)/n)[ends]).max())
    exceed=0
    for _ in range(10000):
        labels=np.zeros(2*n);labels[rng.choice(2*n,n,replace=False)]=1
        distance=float(np.abs(np.cumsum(labels/n-(1-labels)/n)[ends]).max())
        exceed+=distance>=observed-1e-14
    return dict(distance=observed,permutations=10000,p_value=(1+exceed)/10001,passed=(1+exceed)/10001>=.001,
                method='event-label permutations; empirical CDF evaluated only at ends of tied values')


def distribution_gate(a,b,seed,energy):
    import numpy as np
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float);n=len(a)
    if n!=1000 or len(b)!=n or not np.isfinite(np.r_[a,b]).all():raise RuntimeError('Invalid replay population')
    streams=np.random.SeedSequence(seed).spawn(2);perm_rng=np.random.default_rng(streams[0]);boot_rng=np.random.default_rng(streams[1])
    difference=float(b.mean()-a.mean());combined=math.sqrt((float(a.var(ddof=1))+float(b.var(ddof=1)))/n)
    constant_tolerance=1e-5+5e-6*abs(float(a.mean())) if energy else 0
    mean_pass=abs(difference)<=5*combined if combined else abs(difference)<=constant_tolerance
    cdf=permutation(a,b,perm_rng)
    width=None
    if energy:
        if a.std(ddof=1)==0 or b.std(ddof=1)==0:
            width=dict(passed=False,reason='Zero energy variance requires investigation')
        else:
            ratios=[];undefined=0
            for _ in range(10):
                sa=a[boot_rng.integers(0,n,(1000,n))].std(axis=1,ddof=1)
                sb=b[boot_rng.integers(0,n,(1000,n))].std(axis=1,ddof=1)
                undefined+=int(np.count_nonzero(sa==0));ratios.extend((sb/np.where(sa==0,1,sa)).tolist())
            interval=np.quantile(ratios,[.025,.975]).tolist() if undefined==0 else None
            width=dict(ratio=float(b.std(ddof=1)/a.std(ddof=1)),percentile95=interval,replicates=10000,undefined_replicates=undefined,
                       passed=bool(interval is not None and .85<=interval[0] and interval[1]<=1.15))
    return dict(passed=bool(mean_pass and cdf['passed'] and (width is None or width['passed'])),
        mean_difference_native_minus_original=difference,combined_standard_error=combined,mean_within_five_SE=bool(mean_pass),
        constant_tolerance=constant_tolerance,cdf=cdf,width=width,analysis_seed=seed,
        rng=dict(algorithm='PCG64',NumPy=np.__version__,permutation_spawn_key=[0],bootstrap_spawn_key=[1]))


def stochastic_summary(a,fixture,mode):
    import numpy as np
    from podio import root_io
    name=['P','PN'][mode];directory=a.work/'stochastic'/f'{fixture}-{name}'
    for kind in ('original','native'):
        record=json.loads((directory/(kind+'.execution.json')).read_text())
        if record['exit_code']!=0 or sha(directory/(kind+'.log'))!=record['log_sha256'] or sha(directory/('original.root' if kind=='original' else 'native.jsonl'))!=record['output_sha256']:
            raise RuntimeError('Changed stochastic execution evidence')
    original_events=root_io.Reader(str(directory/'original.root')).get('events')
    native_events=[json.loads(line) for line in (directory/'native.jsonl').read_text().splitlines()]
    energy=[[],[]];counts=[[],[]];amplitudes=[[],[]]
    for frame,event in zip(original_events,native_events,strict=True):
        h=frame.get('EventHeader')[0]
        if event['identity']!=[int(h.getRunNumber()),int(h.getEventNumber())]:raise RuntimeError('Stochastic event alignment changed')
        values=[float(hit.getEnergy()) for _,out,_,_ in NAMES for hit in frame.get(out)]
        energy[0].append(math.fsum(values));counts[0].append(len(values));amplitudes[0].extend(values)
        result=event['modes'][name];energy[1].append(result['energy_GeV']/MIP);counts[1].append(result['accepted_cells'])
        accepted=[float(v) for values in result['cells'].values() for _,v in values if v>float(np.float32(.6))]
        if len(accepted)!=result['accepted_cells'] or not math.isclose(math.fsum(accepted)*MIP,result['energy_GeV'],rel_tol=1e-12,abs_tol=1e-14):raise RuntimeError('Native per-cell closure changed')
        amplitudes[1].extend(accepted)
    def shared_edges(values,bins=80):
        lo=min(min(x) for x in values);hi=max(max(x) for x in values);pad=.05*max(hi-lo,abs(lo)*1e-6,1e-6)
        return np.linspace(lo-pad,hi+pad,bins+1)
    ee=shared_edges(energy);ce=np.arange(min(min(x) for x in counts)-.5,max(max(x) for x in counts)+1.5)
    ae=np.r_[np.linspace(0,10,501),np.arange(20,1001,10),np.arange(1100,2601,100)]
    tests={key:distribution_gate(*values,119400+2*fixture+mode,key=='event_energy_MIP') for key,values in [('event_energy_MIP',energy),('accepted_cell_count',counts)]}
    return dict(fixture=['held-out central muon','endcap gamma20'][fixture],mode=name,events=1000,
        passed=all(t['passed'] for t in tests.values()),tests=tests,seeds=seed_audit(directory,1000),
        original=dict(event_energy_MIP=measures(energy[0],ee),accepted_cell_count=measures(counts[0],ce),accepted_cell_amplitude_MIP=measures(amplitudes[0],ae)),
        native=dict(event_energy_MIP=measures(energy[1],ee),accepted_cell_count=measures(counts[1],ce),accepted_cell_amplitude_MIP=measures(amplitudes[1],ae)),
        binning='Event display bins span both observed samples without selection; integer count bins and fixed cell-amplitude bins. All gate statistics unbinned/event-unit.')


def summarize(a):
    m=verify(a.work);det=[];audits=[]
    for sample in m['samples']:
        directory=a.work/'deterministic'/sample['id'];p=directory/'comparison-summary.json';result=json.loads(p.read_text())
        audit_path=directory/'retained-audit.json'
        audit=retained_audit(Path(sample['path']),directory/'original.root');save(audit_path,audit)
        det.append(dict(sample={k:v for k,v in sample.items() if k!='path'},**{k:v for k,v in result.items() if k not in ('configuration','limitations')},
                        strict_reference_tolerance=strict_bound(result),retained_audit=audit))
    stoch=[stochastic_summary(a,f,mode) for f in (0,1) for mode in (0,1)]
    artifacts={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in a.work.rglob('*') if p.is_file() and p.suffix in ('.root','.json','.jsonl','.xml','.py','.log','.md')}
    if a.output.exists():raise RuntimeError('Refusing public output overwrite')
    save(a.output,public(dict(status='PROTOTYPE original-framework software comparison',deterministic=dict(passed=all(d['passed'] for d in det),samples=det),
        stochastic=dict(passed=all(s['passed'] for s in stoch),comparisons=stoch),sources=m['sources'],encodings=m['encodings'],runtime=m['runtime'],
        response=dict(m['response'],modes=dict(D=dict(pair_energy_eV=0,noise_MIP=0),P=dict(pair_energy_eV=3.6,noise_MIP=0),PN=dict(pair_energy_eV=3.6,noise_MIP=.13)),timing_window_ns=[-1e30,1e30],fixed_gain=True,dead_cells=False),
        native_identity=json.loads((a.work/'B-native-identity.json').read_text()),
        corrections=['Include-only wrapper initialized a world before Vacuum was loaded; corrected root-copy wrapper differs only by two encoding constants and absolute source references.',
                     'Pilot steering placeholder once replaced the MIP unit literal; corrected unique placeholder and regression-tested.',
                     'ROOT high-bit-only event seed changes alias after low32 truncation; varied replay run and event IDs, and audited every effective seed.',
                     'Mutating cached read Header objects did not persist IDs; rebuilding the Header collection preserves all other fields and round-trip checks now precede execution.'],
        execution_artifacts=artifacts,immutable_source_runtime_sha256=m['immutable'],protocol_sha256=sha(PROTOCOL),analysis_source_sha256=hashlib.sha256(LOADED_SOURCE).hexdigest(),
        limitations=['Conditional replay tests repeat two fixed real showers; not independent shower performance.','ROOT and CLHEP draws independent; no stochastic bitwise equivalence claimed.',
                    'Sparse populated-cell processing; no detector-wide empty-channel occupancy, pulse/ADC, timing or pileup acceptance.'])))
    print('Compact original-framework reference written',a.output,flush=True)


def self_test(a):
    import numpy as np
    from podio import root_io
    code=write_steering(a.work,Path('input.root'),Path('output.root'),3.6,.13,119200,-1)
    assert 'thresholdUnit="MIP"' in code and 'calibration_mip=0.00014875' in code
    assert permutation(np.ones(1000),np.ones(1000),np.random.default_rng(119400))['p_value']==1
    assert permutation(np.zeros(1000),np.ones(1000),np.random.default_rng(119400))['p_value']<.001
    m=verify(a.work);frame=root_io.Reader(m['samples'][0]['path']).get('events')[250]
    names=sorted(n for n in frame.getAvailableCollections() if n!='EventHeader');before=fingerprint(frame,names)
    R=io_helpers();R.I117ReplayHeader(frame._frame,119800,0);assert fingerprint(frame,names)==before
    with tempfile.TemporaryDirectory(dir=a.work) as directory:
        path=Path(directory)/'header.root';writer=root_io.Writer(str(path));writer.write_frame(frame,'events');writer.finish()
        restored=root_io.Reader(str(path)).get('events')[0];h=restored.get('EventHeader')[0]
        assert (int(h.getRunNumber()),int(h.getEventNumber()))==(119800,0) and fingerprint(restored,names)==before
    R.gInterpreter.Declare('''#include "edm4hep/MCParticleCollection.h"
void I117CorruptRelation(podio::Frame& f) {
 auto& c=const_cast<edm4hep::MCParticleCollection&>(f.get<edm4hep::MCParticleCollection>("MCParticles"));
 c[0].addToParents(c[0]);
}''')
    R.I117CorruptRelation(frame._frame);assert fingerprint(frame,names)!=before
    e1=R.TRandom3(6339446041409160839);e2=R.TRandom3(6339446045704128135)
    assert [e1.Rndm() for _ in range(5)]==[e2.Rndm() for _ in range(5)]
    for p in (a.work/'deterministic').glob('*/comparison-summary.json'):assert strict_bound(json.loads(p.read_text()))['passed']
    print('PASS steering MIP token, discrete/constant CDF controls, shifted-population rejection, header-only replay, MC relation corruption rejection, actual ROOT high-bit seed alias, strict tolerance bounds')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['prepare','pilot','deterministic','replays','stochastic','summarize','self-test'])
    p.add_argument('--work',type=Path,default=ROOT/'build/issue117-reference-validation')
    p.add_argument('--framework',type=Path,default=ROOT.parent/'nodd-pr123-frameworks')
    p.add_argument('--odd',type=Path,default=ROOT.parent/'nodd-software-layout/software/submodules/OpenDataDetector')
    p.add_argument('--odd-library',type=Path,default=ROOT/'build/odd/factory/libOpenDataDetector.dylib')
    p.add_argument('--comparator',type=Path,default=Path('/private/tmp/nodd-digitization117-build/EDM4hep/nodd_silicon_reference'))
    p.add_argument('--backend',type=Path,default=Path('/private/tmp/nodd-digitization117-build/nodd_marlin_silicon_backend'))
    p.add_argument('--sample')
    p.add_argument('--pilot-name',default='pilot')
    p.add_argument('--native-validation',type=Path,default=Path('/private/tmp/nodd-digitization117-build/EDM4hep/nodd_silicon_validation'))
    p.add_argument('--output',type=Path,default=ROOT/'docs/validation/issue117/previews/digitization-reference.json')
    a=p.parse_args();a.work=a.work.resolve()
    {'prepare':prepare,'pilot':pilot,'deterministic':deterministic_all,'replays':replays,'stochastic':stochastic,'summarize':summarize,'self-test':self_test}[a.stage](a)


if __name__=='__main__':main()
