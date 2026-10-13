"""Verify saved positive-energy barrel fixture hits and native parent/cell IDs."""
import argparse
import json
from pathlib import Path
from model import ROOT as PROJECT,sha


def check(directory):
    import ROOT
    ROOT.gROOT.SetBatch(True);fixtures=json.loads((directory/'fixtures.json').read_text());events=[];errors=[]
    for f in fixtures['fixtures']:
        name=f['name'];rootfile=directory/(name+'-smoke.root');log=directory/(name+'-smoke.log');file=ROOT.TFile.Open(str(rootfile));tree=file.Get('events')
        if tree.GetEntries()!=1 or 'Finished run 0 after 1 events' not in log.read_text():errors.append('incomplete '+name)
        tree.GetEntry(0);hits=[]
        for hit in getattr(tree,'BARRELHits'):
            cid=int(hit.cellID);ids=dict(system=cid&255,side=(cid>>8)&3,sector=(cid>>10)&15,layer=(cid>>14)&63,module=(cid>>20)&1023);x=(cid>>30)&63;y=(cid>>36)&63;x=x-64 if x>=32 else x;y=y-64 if y>=32 else y
            if ids!=dict(system=8,side=0,sector=f['sector'],layer=f['layer'],module=f['module']) or not(-8<=x<8 and -8<=y<8) or float(hit.energy)<=0:errors.append('saved ID/energy '+name)
            hits.append(dict(cell_id=cid,ids=ids,x=x,y=y,energy_GeV=float(hit.energy)))
        if not hits or not any([h['x'],h['y']]==f['expected_cell_xy'] for h in hits):errors.append('target electrode absent '+name)
        events.append(dict(fixture=name,seed=f['seed'],events=int(tree.GetEntries()),saved_hits=hits,root_sha256=sha(rootfile),log_sha256=sha(log)));file.Close()
    return dict(status='PASS' if not errors else 'FAIL',errors=errors,scope=fixtures['scope'],field_T=0,physics_list='FTFP_BERT',particle='10GeV mu-',id_descriptor='system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6',fixture_selection=fixtures,checker_sha256=sha(__file__),factory_sha256=sha(PROJECT/'prototypes/calorimeter/BarrelCalorimeter.cpp'),segmentation_source_sha256=sha(PROJECT/'prototypes/calorimeter/EdgeCalorimeter.cpp'),events=events)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=check(a.directory);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['errors']);raise SystemExit(0 if r['status']=='PASS' else 1)
