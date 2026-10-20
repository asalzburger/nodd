#!/usr/bin/env python3
"""SS-P2: exact Git-object metadata-only amendment audit; standard library only."""
import argparse,hashlib,json,pathlib,subprocess,sys,time
OLD='11ec9bb670bca2b882929d1d2b4ef7d9da534da6'
NEW='1d9a49fee5651e41855bd5ad6fdb6adc475b0407'
FREEZE='65cf2741bd697ddb8c4022a751f275b41f63241e'
SCOPE='docs/validation/DES-040/sketched-stagger-2026-10-20/'
REPORT=SCOPE+'native-validation/validation.json'
MODULE='tools/muon_layout/sketched_validation.py'
BEFORE='Geometric fractions use the declared barrel band, not full 4pi.'
AFTER='Only geometric_bank uses the declared central barrel band; full_sphere uses the separately declared full4pi iid bank.'
EXPECTED={SCOPE+'README.md':'adc2fc540ccc64f9676685e0ea963b01c3b822361435228a649b8913ab928521',REPORT:'8545075d486e646b0668866f942eed769074c8caf36dede1afe425a50d5627b8',MODULE:'5cd884d086f69d71f54bfc1c355f1dcf2b541c2d862f1f7f2cc68d9be8e03e71'}
def sha(b):return hashlib.sha256(b).hexdigest()
def main(a):
 start=time.time();repo=str(pathlib.Path(a.repo))
 def git(*args):return subprocess.check_output(['git','-C',repo,*args])
 def raw(rev,p):return git('show',rev+':'+p)
 def tree(rev):
  answer={}
  for row in git('ls-tree','-r','-z',rev).split(b'\0'):
   if row:
    attr,path=row.split(b'\t');mode,typ,oid=attr.decode().split();answer[path.decode()]=(mode,typ,oid)
  return answer
 oldtree,newtree=tree(OLD),tree(NEW)
 changes=sorted(p for p in oldtree.keys()|newtree.keys() if oldtree.get(p)!=newtree.get(p))
 allowed=sorted([SCOPE+'README.md',REPORT,MODULE,'logs/design/SESSION-2026-10-20-pr90-sketched-stagger.md','project/tracking.json'])
 assert changes==allowed,changes
 blobs={p:raw(NEW,p) for p in EXPECTED}
 for p,h in EXPECTED.items():assert sha(blobs[p])==h,p
 oldmodule=raw(OLD,MODULE);assert oldmodule.count(BEFORE.encode())==1
 assert blobs[MODULE]==oldmodule.replace(BEFORE.encode(),AFTER.encode())
 oldreadme=raw(OLD,SCOPE+'README.md');assert blobs[SCOPE+'README.md'].startswith(oldreadme)
 added=blobs[SCOPE+'README.md'][len(oldreadme):].decode()
 for phrase in ['Scope-label correction','geometric_bank','full_sphere','All scientific fields','remain unchanged','actual65cf274','not new acquisition','original11ec9bb']:
  assert phrase in added,phrase
 oldraw=raw(OLD,REPORT);old=json.loads(oldraw);new=json.loads(blobs[REPORT]);amendment=new.pop('metadata_amendment')
 assert old['limits'][0]==BEFORE and new['limits'][0]==AFTER and old['limits'][1:]==new['limits'][1:]
 original_science={k:v for k,v in old.items() if k!='limits'}
 new_science={k:v for k,v in new.items() if k!='limits'}
 assert original_science==new_science
 scientific_hash=sha(json.dumps(original_science,sort_keys=True,separators=(',',':')).encode())
 assert amendment['original_artifact_revision']==OLD
 assert amendment['original_validation_json_sha256']==sha(oldraw)=='707725d59e5af9dc18c5c57c4ecf6950e1b5e01e1ce56b2ad9477383b7cf0eb1'
 assert amendment['unchanged_scientific_fields_sha256']==scientific_hash=='23af330273597f01e3643f8470e5e1a5903178c7b2fcc46e6a0b138d2783776b'
 assert new['source_revision']==old['source_revision']==FREEZE
 for p,h in new['source_sha256'].items():assert sha(raw(FREEZE,p))==h and sha(raw(OLD,p))==h,p
 assert sha(blobs[MODULE])!=new['source_sha256'][MODULE]
 prefixes=['docs/validation/DES-040/','docs/validation/DES-039/','docs/validation/MUON-001/','tools/muon_layout/','tools/toroid_prototype/']
 science_paths=sorted(p for p in oldtree if any(p.startswith(pre) for pre in prefixes))
 exceptions={REPORT,MODULE,SCOPE+'README.md'}
 assert set(p for p in science_paths if oldtree[p]!=newtree.get(p))==exceptions
 assert set(p for p in newtree if any(p.startswith(pre) for pre in prefixes))==set(science_paths)
 artifact_paths=sorted(p for p in oldtree if p.startswith(SCOPE) and p not in exceptions)
 assert all(oldtree[p]==newtree[p] for p in artifact_paths)
 # Git blob object equality provides exact retained-byte identity, including
 # large NPZ/OBJ/raw-event files, without recomputing the scientific scan.
 objects={p:oldtree[p][2] for p in artifact_paths}
 result={'assignment':'SS-P2','role':'PhysVal explicit mandate fallback','original_revision':OLD,'reviewed_revision':NEW,'passed_bounded_checks':True,'finding':'SS-P1-F1 resolved','changed_repository_files':changes,'reviewer_changed_repository_files':[],'source_module_change':'Exactly one literal scope sentence; no executable mathematics changed.','readme_change':'Only appended scope-label provenance clarification.','validation_json_change':'Only limits[0] plus metadata_amendment; all remaining JSON values identical.','canonical_scientific_fields_sha256':scientific_hash,'original_validation_json_sha256':sha(oldraw),'corrected_validation_json_sha256':sha(blobs[REPORT]),'pinned_input_sha256':EXPECTED,'original_execution_source_revision':FREEZE,'original_execution_source_hashes_factual':True,'future_module_sha256':sha(blobs[MODULE]),'actual_execution_module_sha256':new['source_sha256'][MODULE],'scientific_scope_file_count':len(science_paths),'identical_scientific_scope_files':len(science_paths)-len(exceptions),'identical_raw_artifact_files':len(artifact_paths),'identical_artifact_blob_oids':objects,'metadata_amendment':amendment,'actual_checks':['Exact pinned three-input SHA-256 verification','Whole-repository tree diff limited to declared five paths','Source module exact one-literal replacement','README append-only clarification','All scientific JSON values equal and canonical hash exact','Recorded executed-source hashes match original execution Git objects','All retained scientific and raw artifact blob identities exact'],'limitations':['No full numerical scan, native engine, field solve or installed dependencies rerun.','This is metadata amendment verification attached to SS-P1 exact-original assessment; it does not grant engineering or human acceptance.'],'checker_sha256':sha(pathlib.Path(__file__).read_bytes()),'elapsed_seconds':time.time()-start,'runtime':sys.version}
 output=pathlib.Path(a.output);assert str(output).startswith('/private/tmp/pr90-SS-P1-');output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['identical_artifact_blob_oids','metadata_amendment']},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',default='/Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout');p.add_argument('--output',default='/private/tmp/pr90-SS-P1-amendment-results.json');main(p.parse_args())
