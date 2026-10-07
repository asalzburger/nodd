"""Inspect saved seeded DDSim hits; require both faces of an identical pair."""
import argparse,json,re
from pathlib import Path
import uproot
from model import sha

def run(root,log,expected,native,out):
 e=json.loads(expected.read_text());n=json.loads(native.read_text());text=log.read_text();errors=[]
 with uproot.open(root) as f:
  events=f['events'];hits={k:events[e['name']+'Hits/'+e['name']+'Hits.'+k].array(library='np')[0].tolist() for k in ('cellID','eDep','pathLength','position.x','position.y','position.z')};count=events.num_entries
 ids=[dict(system=cell&31,layer=(cell>>5)&15,stave=(cell>>9)&255,module=(cell>>17)&63,sensor=(cell>>23)&1) for cell in hits['cellID']]
 pairs={}
 for i in ids:pairs.setdefault((i['layer'],i['stave'],i['module']),set()).add(i['sensor'])
 layers=sorted({p[0] for p,faces in pairs.items() if faces=={0,1}})
 if count!=1 or layers!=list(range(e['layers'])):errors.append('Expected one event with a complete same-module pair in every target layer')
 if any(i['system']!=e['system_id'] for i in ids):errors.append('Wrong system ID')
 if not hits['eDep'] or any(x<=0 for x in hits['eDep']):errors.append('Nonpositive saved sensitive energy')
 if 'Finished run 0 after 1 events' not in text:errors.append('DDSim completion absent')
 if not re.search(rf"{e['counts']['sensitive']}\s+sensitive path entries",text):errors.append('Sensitive path inventory mismatch')
 if sha(expected)!=n['execution']['expected_sha256']:errors.append('Different native expected inventory')
 r=dict(status='FAIL' if errors else 'PASS',errors=errors,scope='One zero-field10GeV muon; transport and saved paired hits, not coverage or response',events=count,saved_hits=len(ids),complete_pair_layers=layers,hit_data=hits,decoded_volume_ids=ids,geant4_version=re.search(r'Geant4 version Name:\s*(.+)',text).group(1),physics_list='FTFP_BERT',seed=42,field_T=0,hashes=dict(root=sha(root),runtime_log=sha(log),expected=sha(expected),native=sha(native),checker=sha(__file__)))
 out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ('status','errors','saved_hits','complete_pair_layers')}));return not errors
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in ('root','log','expected','native','output'):p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();raise SystemExit(0 if run(a.root,a.log,a.expected,a.native,a.output) else 1)
