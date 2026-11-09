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
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
LOADED_SOURCE=Path(__file__).read_bytes()
PROTOCOL=ROOT/'docs/validation/issue117/digitization-protocol.md'
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
                  log=str(log), log_sha256=sha(log), producer_sha256=hashlib.sha256(LOADED_SOURCE).hexdigest(),protocol_sha256=sha(PROTOCOL))
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
    target=work/'frozen-protocol.md'
    if target.exists():
        if sha(target)!=sha(PROTOCOL):raise RuntimeError('Frozen protocol changed')
    else:target.write_bytes(PROTOCOL.read_bytes())


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['prepare','pilot','deterministic'])
    p.add_argument('--work',type=Path,default=ROOT/'build/issue117-reference-validation')
    p.add_argument('--framework',type=Path,default=ROOT.parent/'nodd-pr123-frameworks')
    p.add_argument('--odd',type=Path,default=ROOT.parent/'nodd-software-layout/software/submodules/OpenDataDetector')
    p.add_argument('--odd-library',type=Path,default=ROOT/'build/odd/factory/libOpenDataDetector.dylib')
    p.add_argument('--comparator',type=Path,default=Path('/private/tmp/nodd-digitization117-build/EDM4hep/nodd_silicon_reference'))
    p.add_argument('--backend',type=Path,default=Path('/private/tmp/nodd-digitization117-build/nodd_marlin_silicon_backend'))
    p.add_argument('--sample')
    p.add_argument('--pilot-name',default='pilot')
    a=p.parse_args();a.work=a.work.resolve()
    {'prepare':prepare,'pilot':pilot,'deterministic':deterministic_all}[a.stage](a)


if __name__=='__main__':main()
