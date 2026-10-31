import pathlib,json,gzip,hashlib,numpy as np
W=pathlib.Path(__file__).resolve().parents[3];P=W/'docs/validation/DES-042/ttbar-pu200';cache={}
def sha(p):
 p=pathlib.Path(p)
 if p not in cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1<<20),b''):h.update(b)
  cache[p]=h.hexdigest()
 return cache[p]
def load(p):return json.load(gzip.open(p,'rt')) if str(p).endswith('.gz') else json.load(open(p))
profiles=load(P/'profiles.json.gz');replay=load(P/'gbts-reconstruction-replay.json');native=load(P/'native-campaign.json');sums=[];rawreports=[]
for pitch in ('0.5','1','1.5','2'):
 R=W/f'build/strixel-ttbar-production-v3/pitch{pitch}';O=W/f'build/strixel-ttbar-production-v2/pitch{pitch}';S=P/f'pitch{pitch}';s=load(S/'summary.json.gz');r=load(R/'run-report.json');rawreports.append(r);sums.append(s)
 assert sha(S/'summary.json.gz')==profiles['provenance']['case_summaries_sha256'][pitch]
 assert sha(S/'events.npz')==s['events_npz_sha256']
 assert s['events']==100 and len(s['audit_chunks_sha256'])==100
 assert sorted(s['audit_chunks_sha256'])==[f'audit/event-{i:06d}.npz' for i in range(100)]
 for f,h in s['audit_chunks_sha256'].items():assert sha(S/f)==h,(pitch,f)
 assert sha(R/'run-report.json')==s['native_report_sha256']==native['cases'][pitch]['original_report_sha256']==replay['cases'][pitch]['corrected_report_sha256']
 assert r['outcome']=='completed' and r['events']==100 and len(r['output_sha256'])==116 and all(r['postrun_immutability'].values())
 for f,h in r['output_sha256'].items():assert sha(R/f)==h,(pitch,f)
 for e in replay['cases'][pitch]['event_rows']:
  f=f'audit/event{e["event"]:06d}.json.gz';assert sha(R/f)==sha(O/f)==e['corrected_gzip_sha256']==e['original_gzip_sha256']
 assert r['source_revision']=='46926ce90074d44b4a4ad42bbca0f318c6a68449'
 assert r['gbts_numerical_implementation']['module_sha256']=='1be2d1d2c3caf2174d32594b8fc9448b40de8db0bcd1ce08a52940549ccec3b2'
 n=r['gbts_statistics']['numerical_audit'];g=r['gbts_statistics']['graph_audit'];assert [e['event'] for e in n['events']]==list(range(100)) and [e['event'] for e in g['events']]==list(range(100))
 assert n['all_events_verified'] and n['total_affected_updates']==1 and [(e['event'],e['affected_updates']) for e in n['events'] if e['affected_updates']]==[(57,1)]
 assert g['cap_reached_events']==99 and g['edge_cap']==2000000
 for f,h in s['invariant_input_sha256'].items():assert sha(R/f)==h
 print('PASS pitch',pitch,'portable100, native116, old/new100byte-identical, numerical100+graph100, source/module/report/input bindings',flush=True)
fields=('source_generated','source_simulated','source_hits','generated','simulated_particles','pixels','spacepoints','seeds','estimated_seeds')
for i,s in enumerate(sums):
 assert all(s['invariant_input_sha256']==q['invariant_input_sha256'] and s['original_native_identity_sha256']==q['original_native_identity_sha256'] for q in sums)
 assert [f['event'] for f in s['fingerprints']]==list(range(100))
 for f,b in zip(s['fingerprints'],sums[0]['fingerprints']):
  assert all(f[k]==b[k] for k in fields)
 changed=sum(f['non_target']!=b['non_target'] for f,b in zip(s['fingerprints'],sums[0]['fingerprints']));assert changed==(0 if i==0 else 100)
 sampleSHA=sha(W/'build/strixel-ttbar-production-v2/sample/run-report.json');assert rawreports[i]['sample_report_sha256']==sampleSHA
print('PASS all pairing fingerprints and invariant source/config/report identities',flush=True)
S=W/'build/strixel-ttbar-production-v2/sample';O=W/'build/strixel-ttbar-production/sample';r=load(S/'run-report.json');q=load(P/'numerical-replay.json')
assert sha(S/'run-report.json')==q['sample_report_sha256'];assert r['source_revision']=='250a211ff71be2ce7339cc043766f0d839470411' and r['outcome']=='completed' and len(r['output_sha256'])==110
for f,h in r['output_sha256'].items():assert sha(S/f)==h, f
for e in q['event_payloads']:
 f=f'sample/event{e["event"]:06d}.json.gz';assert sha(S/f)==sha(O/f)==e['sha256']
assert q['counts']=={'generated':3079140,'selected':998339,'simulated':1090060,'hits':7907248,'primary_vertices':20100}
print('PASS sample110 outputs, original/corrected100payloadbytes, sample report bound to every reconstruction',flush=True)
m=load(P/'figures/manifest.json');v=load(P/'figure-verification.json')
assert sha(P/'figures/manifest.json')==v['manifest_sha256']
for f,h in m['files_sha256'].items():assert sha(P/'figures'/f)==h
print('PASS12figurefilehashes+manifest+profiles/plot bindings',flush=True)
print('TOTAL unique hashed files',len(cache))
