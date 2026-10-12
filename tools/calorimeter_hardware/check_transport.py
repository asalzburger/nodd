"""Inspect saved unit-fixture DDSim hits using the existing ROOT runtime."""
import argparse,json,re
from pathlib import Path
from model import sha

def check(directory):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    native=json.loads((directory/'native.json').read_text());results=[];errors=[]
    for kind,system in (('ecal',8),('hcal',9)):
        log=directory/f'{kind}-smoke.log';root=directory/f'{kind}-smoke.root';text=log.read_text()
        file=ROOT.TFile.Open(str(root));tree=file.Get('events');tree.GetEntry(0);hits=[]
        if tree.GetEntries()!=1 or 'Finished run 0 after 1 events' not in text:errors.append(kind+' incomplete event')
        for hit in getattr(tree,kind.upper()+'Hits'):
            cid=int(hit.cellID);sid=(cid>>33)&255
            cellx=(cid>>41)&511;celly=(cid>>50)&511
            cellx=cellx-512 if cellx>=256 else cellx;celly=celly-512 if celly>=256 else celly
            if cid&255!=system or (cid>>8)&((1<<25)-1)!=0:errors.append(kind+' wrong parent ID')
            if sid>=(4 if system==8 else 144):errors.append(kind+' sensor ID')
            valid=(-8<=cellx<8 and -8<=celly<8) if system==8 else (cellx==0 and celly==0)
            if not valid:errors.append(kind+' cell range')
            if hit.energy<=0:errors.append(kind+' zero deposition')
            hits.append(dict(cell_id=cid,sensor=sid,x=cellx,y=celly,energy_GeV=float(hit.energy),position_mm=[float(hit.position.x),float(hit.position.y),float(hit.position.z)]))
        if not hits:errors.append(kind+' no saved sensitive hit')
        if getattr(tree,('HCAL' if system==8 else 'ECAL')+'Hits').size()!=0:errors.append(kind+' wrong cassette hit')
        version=re.search(r'Geant4 version Name:\s*(.+)',text)
        results.append(dict(cassette=kind,events=int(tree.GetEntries()),saved_hits=hits,Geant4=version.group(1).strip() if version else None,root_sha256=sha(root),log_sha256=sha(log)))
        file.Close()
    return dict(status='FAIL' if errors else 'PASS',errors=errors,scope='Two independent seeded10 GeV mu- fixture events with saved calorimeter hits; not shower performance',random_seed=42,physics_list='FTFP_BERT',field_T=0,execution=native['execution'],expected_sha256=sha(directory/'expected.json'),checker_sha256=sha(__file__),events=results)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=check(a.directory);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['errors']);raise SystemExit(1 if r['errors'] else 0)
