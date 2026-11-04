"""Select, run and check signed sparse DES033 saved-hit transport fixtures.

Only fixture selection and the ID/energy/log controls use the standard library.
The runner requires the existing DDSim runtime; the checker requires ROOT.
"""
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from endcap_geometry import ROOT, ID_FIELDS, decode, gap_point, inside, sha


def transformed(vector,frame,translation=None):
    out=[sum(frame[j][i]*vector[j] for j in range(3)) for i in range(3)]
    return [out[i]+translation[i] for i in range(3)] if translation else out


def fixtures(compact,expected,output):
    report=json.loads(expected.read_text());output.mkdir(parents=True,exist_ok=True)
    material=compact.parent/'materials.xml'
    if report.get('artifact_sha256',{}).get(compact.name)!=sha(compact) or report.get('artifact_sha256',{}).get('materials.xml')!=sha(material):
        raise ValueError('Stale source compact/material inventory binding')
    wheel=next(w for w in report['wheels'] if w['wheel']==1);gap=next(p for p in wheel['pieces'] if p.get('gap')==0)
    point=gap_point(gap,(wheel['inner_radius_mm']+wheel['outer_radius_mm'])/2,0)
    if not inside(gap,point):raise ValueError('Sparse gun start outside actual middle-wheel gap')
    normal=gap['lower_face']['normal'];length=math.sqrt(sum(v*v for v in normal));normal=[v/length for v in normal]
    result=[]
    for side in (1,2):
        directory=output/f'side{side}';directory.mkdir(parents=True,exist_ok=True)
        tree=ET.parse(compact);detector=tree.getroot().find('detectors/detector')
        retained=[]
        for node in list(detector):
            if node.tag=='piece':detector.remove(node)
            elif node.tag=='replica':
                if int(node.get('side'))!=side or int(node.get('plane'))!=0:detector.remove(node)
                else:retained.append(dict(side=side,wheel=int(node.get('wheel')),plane=0))
        if {x['wheel'] for x in retained}!={0,1,2} or len(retained)!=3:raise ValueError('Sparse fixture omitted or duplicated a wheel')
        ET.indent(tree);path=directory/'fixture.xml';tree.write(path,encoding='utf-8',xml_declaration=True)
        shutil.copyfile(material,directory/'materials.xml');shutil.copyfile(expected,directory/'expected.json')
        replica=next(r for r in report['replicas'] if r['side']==side and r['wheel']==1 and r['plane']==0)
        metadata=dict(scope='One physical period of each of3 wheels at one signed end; cryostat/services omitted. Muon begins inside middle-wheel gap0. Sparse machinery check, no full-endcap response.',side=side,retained_replicas=retained,local_position_mm=point,local_direction=normal,position_mm=transformed(point,replica['frame'],replica['center_mm']),direction=transformed(normal,replica['frame']),source_compact_sha256=sha(compact),fixture_sha256=sha(path),materials_sha256=sha(directory/'materials.xml'),expected_sha256=sha(directory/'expected.json'),selector_sha256=sha(__file__),source_sha256=report['source_sha256'])
        (directory/'fixture.json').write_text(json.dumps(metadata,indent=2)+'\n');result.append(metadata)
    return result


def command_for(directory,metadata,python,executable):
    return [python,executable,'--compactFile',str((directory/'fixture.xml').resolve()),'--runType','batch','--numberOfEvents','1','--enableGun','--gun.particle','mu-','--gun.energy','10*GeV','--gun.position',' '.join(map(str,metadata['position_mm'])),'--gun.direction',' '.join(map(str,metadata['direction'])),'--random.seed','42','--physics.list','FTFP_BERT','--part.userParticleHandler','','--outputFile',str((directory/'smoke.root').resolve())]


def run(directory):
    metadata=json.loads((directory/'fixture.json').read_text())
    for filename,key in [('fixture.xml','fixture_sha256'),('materials.xml','materials_sha256'),('expected.json','expected_sha256')]:
        if sha(directory/filename)!=metadata[key]:raise ValueError('Stale sparse fixture:'+filename)
    if metadata['selector_sha256']!=sha(__file__):raise ValueError('Stale fixture selector source')
    executable=shutil.which('ddsim')
    if not executable:raise ValueError('Installed DDSim script unavailable')
    command=command_for(directory,metadata,sys.executable,executable)
    with (directory/'smoke.log').open('w') as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
    record=dict(command=command,requested=dict(particle='mu-',energy='10*GeV',seed=42,events=1,physics_list='FTFP_BERT',side=metadata['side']),exit_code=result.returncode,fixture_sha256=sha(directory/'fixture.xml'),fixture_metadata_sha256=sha(directory/'fixture.json'),root_sha256=sha(directory/'smoke.root') if (directory/'smoke.root').is_file() else None,log_sha256=sha(directory/'smoke.log'),runner_sha256=sha(__file__),ddsim_script_sha256=sha(executable))
    (directory/'run.json').write_text(json.dumps(record,indent=2)+'\n')
    if result.returncode:raise RuntimeError('Recorded DDSim failure; inspect smoke.log/run.json')
    return record


def valid_cell(cell,expected,fixture):
    bits=sum(n for _,n in ID_FIELDS)
    if not isinstance(cell,int) or cell<0 or cell>>bits:raise ValueError('Saved hit has unused/high ID bits')
    ids=decode(cell)
    if ids['system']!=expected['readout']['system_id'] or ids['side']!=fixture['side'] or ids['plane']!=0 or ids['gap']!=0:raise ValueError('Saved hit is not a retained canonical physical cell')
    if ids['wheel'] not in (0,1,2):raise ValueError('Saved hit has no constructed wheel')
    wheel=next(w for w in expected['wheels'] if w['wheel']==ids['wheel'])
    if not 0<=ids['rho']<wheel['radial_bins'] or not 0<=ids['z']<expected['readout']['axial_bins']:raise ValueError('Ghost radial/axial readout cell')
    reference=next((r for r in wheel['reference_points'] if r['rho']==ids['rho'] and r['z']==ids['z']),None)
    gap=next(p for p in wheel['pieces'] if p.get('gap')==0)
    if reference is None or not inside(gap,reference['position_mm']):raise ValueError('Saved hit has no physical canonical reference')
    return ids


def validate_rows(rows,expected,fixture):
    checked=[]
    for row in rows:
        energy=float(row['energy_GeV'])
        if not math.isfinite(energy) or energy<=0:raise ValueError('Nonpositive/nonfinite saved deposited energy')
        checked.append(dict(cell_id=row['cell_id'],energy_GeV=energy,fields=valid_cell(row['cell_id'],expected,fixture)))
    if not checked:raise ValueError('No saved active LAr hits')
    return checked


def observed_run(log,request):
    if 'Finished run 0 after 1 events' not in log:raise ValueError('Run did not finish one event')
    if request['seed']!=42 or request['events']!=1 or request['physics_list']!='FTFP_BERT':raise ValueError('Unexpected requested smoke run')
    if not re.search(r'with seed\s+42\b',log) or not re.search(r'\bFTFP_BERT\b',log):raise ValueError('Observed seed/physics mismatch')
    version=re.search(r'Geant4 version Name:\s*(.+)',log)
    return dict(seed=42,physics_list='FTFP_BERT',Geant4=version.group(1).strip() if version else None)


def check(directory):
    import ROOT as R
    record=json.loads((directory/'run.json').read_text());fixture=json.loads((directory/'fixture.json').read_text());expected=json.loads((directory/'expected.json').read_text())
    if record['exit_code']!=0:raise ValueError('Recorded DDSim failure')
    if record['command']!=command_for(directory,fixture,record['command'][0],record['command'][1]):raise ValueError('Recorded DDSim argv does not match the signed fixture/request')
    if record['requested']!=dict(particle='mu-',energy='10*GeV',seed=42,events=1,physics_list='FTFP_BERT',side=fixture['side']):raise ValueError('Run requested fields differ from exact argv')
    if sha(Path(record['command'][1]))!=record['ddsim_script_sha256']:raise ValueError('DDSim producer script changed')
    if record['runner_sha256']!=sha(__file__) or fixture['selector_sha256']!=sha(__file__):raise ValueError('Transport source identity changed')
    for filename,key in [('fixture.xml','fixture_sha256'),('fixture.json','fixture_metadata_sha256'),('smoke.root','root_sha256'),('smoke.log','log_sha256')]:
        if sha(directory/filename)!=record[key]:raise ValueError('Run artifact binding mismatch:'+filename)
    for filename,key in [('materials.xml','materials_sha256'),('expected.json','expected_sha256')]:
        if sha(directory/filename)!=fixture[key]:raise ValueError('Fixture artifact mismatch:'+filename)
    tree=ET.parse(directory/'fixture.xml');root=tree.getroot()
    if root.find('fields') is not None:raise ValueError('Sparse fixture unexpectedly contains field configuration')
    retained=[dict(side=int(n.get('side')),wheel=int(n.get('wheel')),plane=int(n.get('plane'))) for n in root.findall('detectors/detector/replica')]
    if sorted(retained,key=lambda x:x['wheel'])!=sorted(fixture['retained_replicas'],key=lambda x:x['wheel']) or len(retained)!=3:raise ValueError('Sparse physical replica metadata mismatch')
    observed=observed_run((directory/'smoke.log').read_text(),record['requested'])
    file=R.TFile.Open(str(directory/'smoke.root'))
    if not file or file.IsZombie():raise ValueError('Unreadable saved ROOT event file')
    try:
        events=file.Get('events')
        if not events or events.GetEntries()!=1:raise ValueError('Expected exactly one saved event')
        events.GetEntry(0);hits=getattr(events,expected['readout']['name'])
        rows=validate_rows([dict(cell_id=int(h.cellID),energy_GeV=float(h.energy)) for h in hits],expected,fixture)
    finally:file.Close()
    return dict(status='PASS',scope='One requested10GeV mu- per signed sparse3-wheel fixture; actual saved positive finite LAr hits. No whole-endcap/combined transport, digitization or response claim.',observed=observed,requested=record['requested'],events=1,hits=rows,fixture=fixture,run_record_sha256=sha(directory/'run.json'),root_sha256=sha(directory/'smoke.root'),log_sha256=sha(directory/'smoke.log'),checker_sha256=sha(__file__))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);commands=p.add_subparsers(dest='mode',required=True)
    f=commands.add_parser('fixtures');f.add_argument('--compact',type=Path,required=True);f.add_argument('--expected',type=Path,required=True);f.add_argument('--output',type=Path,required=True)
    r=commands.add_parser('run');r.add_argument('--directory',type=Path,required=True)
    c=commands.add_parser('check');c.add_argument('--directory',type=Path,required=True);c.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.mode=='fixtures':print('Created',len(fixtures(a.compact,a.expected,a.output)),'signed fixtures')
    elif a.mode=='run':run(a.directory)
    else:
        result=check(a.directory);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(result['hits']),'saved hits')
