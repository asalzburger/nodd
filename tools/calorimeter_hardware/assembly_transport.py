"""Audit saved DDSim calorimeter hits in physical sector0 fixtures."""
import argparse,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from model import sha

def check(directory):
    import ROOT
    ROOT.gROOT.SetBatch(True);expected=json.loads((directory/'expected.json').read_text());errors=[];events=[]
    fixture=ET.parse(directory/'sector-fixture.xml');selected={r.get('name'):{(int(p.get('layer')),int(p.get('cassette'))) for p in r.findall('placement')} for r in fixture.getroot().findall('./detectors/detector/region')}
    for kind,side in (('barrel',0),('positive',1),('negative',2)):
        root=directory/f'{kind}-smoke.root';log=directory/f'{kind}-smoke.log';text=log.read_text();file=ROOT.TFile.Open(str(root));tree=file.Get('events');tree.GetEntry(0);collections={}
        if tree.GetEntries()!=1 or 'Finished run 0 after 1 events' not in text:errors.append('unfinished '+kind)
        for unit,system in (('ecal',8),('hcal',9)):
            region=next(r for r in expected['regions'] if r['unit']==unit and r['kind']==('barrel' if side==0 else 'endcap'))
            valid={(p['layer'],p['cassette']) for p in region['placements']};hits=[]
            for hit in getattr(tree,unit.upper()+'Hits'):
                cid=int(hit.cellID);parent=dict(system=cid&255,side=(cid>>8)&3,sector=(cid>>10)&31,layer=(cid>>15)&63,cassette=(cid>>21)&4095,sensor=(cid>>33)&255)
                if parent['system']!=system or parent['side']!=side or parent['sector']!=0:errors.append('unexpected parent '+kind)
                if (parent['layer'],parent['cassette']) not in valid or (parent['layer'],parent['cassette']) not in selected[region['name']] or parent['sensor']>=(4 if system==8 else 144):errors.append('invalid physical ID '+kind)
                x=(cid>>41)&511;y=(cid>>50)&511;x=x-512 if x>=256 else x;y=y-512 if y>=256 else y
                if not ((-8<=x<8 and -8<=y<8) if system==8 else (x==0 and y==0)):errors.append('cell range '+kind)
                if hit.energy<=0:errors.append('nonpositive energy '+kind)
                hits.append(dict(cell_id=cid,ids=parent,x=x,y=y,energy_GeV=float(hit.energy)))
            if not hits:errors.append('empty '+kind+' '+unit)
            collections[unit]=dict(saved_hits=len(hits),layers=sorted({h['ids']['layer'] for h in hits}),hits=hits)
        version=re.search(r'Geant4 version Name:\s*(.+)',text)
        events.append(dict(fixture=kind,side=side,events=int(tree.GetEntries()),collections=collections,Geant4=version.group(1).strip() if version else None,root_sha256=sha(root),log_sha256=sha(log)));file.Close()
    return dict(status='FAIL' if errors else 'PASS',errors=errors,scope='Three seeded10 GeV mu- events: sparse physical sector0 of each barrel and both endcaps, one selected cassette per layer; all absorber plates/frames retained. Saved hits checked; no complete-sector or full-detector transport/response qualification.',seed=42,physics_list='FTFP_BERT',field_T=0,source_compact_sha256=sha(directory/'calorimeter.xml'),fixture_sha256=sha(directory/'sector-fixture.xml'),expected_sha256=sha(directory/'expected.json'),factory_sha256=sha(Path(__file__).resolve().parents[2]/'prototypes/calorimeter/Calorimeter.cpp'),checker_sha256=sha(__file__),fixture_selector_sha256=sha(Path(__file__).with_name('sector_fixture.py')),selected_cassettes_per_logical_region={k:len(v) for k,v in selected.items()},events=events)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=check(a.directory);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['errors']);raise SystemExit(1 if r['errors'] else 0)
