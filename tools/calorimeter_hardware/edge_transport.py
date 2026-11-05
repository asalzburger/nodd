"""Check saved Geant4 hits from the two DES030 custom-inner-mask fixtures."""
import argparse
import json
from pathlib import Path
from model import ROOT as PROJECT, sha


def check(directory):
    import ROOT
    ROOT.gROOT.SetBatch(True);fixture=json.loads((directory/'fixture.json').read_text());events=[];errors=[]
    for name,side,seed in (('positive',1,43),('negative',2,44)):
        path=directory/(name+'-smoke.root');log=directory/(name+'-smoke.log');file=ROOT.TFile.Open(str(path));tree=file.Get('events');tree.GetEntry(0);hits=[]
        if tree.GetEntries()!=1 or 'Finished run 0 after 1 events' not in log.read_text():errors.append('unfinished '+name)
        for hit in getattr(tree,'EDGEHits'):
            cid=int(hit.cellID);fields=dict(system=cid&255,side=(cid>>8)&3,sector=(cid>>10)&15,layer=(cid>>14)&63,module=(cid>>20)&1023);x=(cid>>30)&63;y=(cid>>36)&63;x=x-64 if x>=32 else x;y=y-64 if y>=32 else y
            if fields!=dict(system=8,side=side,sector=0,layer=0,module=fixture['module']):errors.append('parent fields '+name)
            if [x,y]!=fixture['expected_cell_xy']:errors.append('unexpected electrode '+name)
            if float(hit.energy)<=0:errors.append('nonpositive energy '+name)
            hits.append(dict(cell_id=cid,ids=fields,x=x,y=y,energy_GeV=float(hit.energy)))
        if not hits:errors.append('no hits '+name)
        events.append(dict(fixture=name,seed=seed,events=int(tree.GetEntries()),saved_hits=hits,root_sha256=sha(path),log_sha256=sha(log)));file.Close()
    return dict(status='PASS' if not errors else 'FAIL',errors=errors,scope='Two one-event10GeV mu- single-layer custom inner-mask fixtures, proper positive/negative placements; complete detector transport and response unqualified.',field_T=0,physics_list='FTFP_BERT',id_descriptor='system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6',fixture_sha256=sha(directory/'edge-fixture.xml'),selector_sha256=sha(Path(__file__).with_name('edge_fixture.py')),checker_sha256=sha(__file__),factory_sha256=sha(PROJECT/'prototypes/calorimeter/EdgeCalorimeter.cpp'),events=events)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=check(a.directory);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['errors']);raise SystemExit(0 if r['status']=='PASS' else 1)
