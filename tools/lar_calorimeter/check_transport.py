"""Audit actual saved calorimeter hit IDs and deposited energies."""
import argparse
import json
import math
from pathlib import Path
import re
from barrel_geometry import sha, decode

def check(directory):
    import ROOT
    f=ROOT.TFile.Open(str(directory/'smoke.root'));tree=f.Get('events')
    if not tree or tree.GetEntries()!=1:raise ValueError('Expected one saved event')
    if 'Finished run 0 after 1 events' not in (directory/'smoke.log').read_text():raise ValueError('Unfinished run')
    tree.GetEntry(0);hits=getattr(tree,'LArBarrelHits')
    rows=[]
    for hit in hits:
        row=dict(cell_id=int(hit.cellID),energy_GeV=float(hit.energy))
        ids=decode(row['cell_id']);row['fields']=ids
        if not math.isfinite(row['energy_GeV']) or row['energy_GeV']<=0:raise ValueError('Nonpositive saved hit energy')
        if ids['system']!=10 or ids['plane']!=0 or ids['gap']!=0 or not 0<=ids['layer']<=10:raise ValueError('Unexpected canonical hit fields')
        rows.append(row)
    if not rows:raise ValueError('No saved active LAr hits')
    f.Close();text=(directory/'smoke.log').read_text();v=re.search(r'Geant4 version Name:\s*(.+)',text)
    return dict(status='PASS',scope='One seeded10GeV mu- inside a two-electrode fixture, saved LAr hits; not whole-barrel transport, charge response or ACTS conversion.',
        seed=42,physics_list='FTFP_BERT',field_T=0,events=1,hits=rows,Geant4=v.group(1).strip() if v else None,
        fixture=json.loads((directory/'fixture.json').read_text()),root_sha256=sha(directory/'smoke.root'),log_sha256=sha(directory/'smoke.log'),checker_sha256=sha(__file__))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=check(a.directory);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(r['hits']),'saved hits')
