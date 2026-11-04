"""Audit actual saved calorimeter hit IDs and deposited energies."""
import argparse
import json
import math
from pathlib import Path
import re
from barrel_geometry import sha, decode

def valid_cell(cid,expected):
    ids=decode(cid)
    if ids['system']!=expected['readout']['system_id'] or ids['plane']!=0 or ids['gap']!=0 or not 0<=ids['layer']<=10:
        raise ValueError('Unexpected canonical hit fields')
    layer=expected['readout']['layers'][ids['layer']]
    if ids['theta'] not in layer['indices']:raise ValueError('Ghost/noncanonical saved theta cell')
    return ids

def check(directory):
    import ROOT
    run=json.loads((directory/'run.json').read_text())
    fixture=json.loads((directory/'fixture.json').read_text())
    if sha(directory/'expected.json')!=fixture['expected_sha256']:raise ValueError('Stale readout inventory')
    if sha(Path(__file__).with_name('run_transport.py'))!=run['runner_sha256']:raise ValueError('Run producer mismatch')
    expected=json.loads((directory/'expected.json').read_text())
    for name,key in [('fixture.xml','fixture_sha256'),('smoke.root','root_sha256'),('smoke.log','log_sha256')]:
        if sha(directory/name)!=run[key]:raise ValueError('Run artifact binding mismatch')
    if run['exit_code']!=0:raise ValueError('Recorded DDSim failure')
    f=ROOT.TFile.Open(str(directory/'smoke.root'));tree=f.Get('events')
    if not tree or tree.GetEntries()!=1:raise ValueError('Expected one saved event')
    if 'Finished run 0 after 1 events' not in (directory/'smoke.log').read_text():raise ValueError('Unfinished run')
    tree.GetEntry(0);hits=getattr(tree,'LArBarrelHits')
    rows=[]
    for hit in hits:
        row=dict(cell_id=int(hit.cellID),energy_GeV=float(hit.energy))
        ids=valid_cell(row['cell_id'],expected);row['fields']=ids
        if not math.isfinite(row['energy_GeV']) or row['energy_GeV']<=0:raise ValueError('Nonpositive saved hit energy')
        
        rows.append(row)
    if not rows:raise ValueError('No saved active LAr hits')
    f.Close();text=(directory/'smoke.log').read_text();v=re.search(r'Geant4 version Name:\s*(.+)',text)
    if 'with seed '+str(run['requested']['seed']) not in text or 'FTFP_BERT' not in text:raise ValueError('Observed run seed/physics mismatch')
    import xml.etree.ElementTree as ET
    if ET.parse(directory/'fixture.xml').getroot().find('fields') is not None:raise ValueError('Fixture unexpectedly has a field configuration')
    return dict(status='PASS',scope='One seeded10GeV mu- inside a two-electrode fixture, saved LAr hits; not whole-barrel transport, charge response or ACTS conversion.',
        observed_seed=run['requested']['seed'],observed_physics_list='FTFP_BERT',field_configuration='No fields in hash-bound sparse compact',requested=run['requested'],run_record_sha256=sha(directory/'run.json'),runner_sha256=run['runner_sha256'],events=1,hits=rows,Geant4=v.group(1).strip() if v else None,
        fixture=json.loads((directory/'fixture.json').read_text()),root_sha256=sha(directory/'smoke.root'),log_sha256=sha(directory/'smoke.log'),checker_sha256=sha(__file__))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=check(a.directory);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(r['hits']),'saved hits')
