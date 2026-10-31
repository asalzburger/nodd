import pathlib,json,gzip,math,collections,numpy as np
W=pathlib.Path(__file__).resolve().parents[3];P=W/'docs/validation/DES-042/ttbar-pu200'
def portable(path):
 with np.load(path,allow_pickle=False) as f:d={k:f[k] for k in f.files}
 ids=[tuple(map(int,p)) for p in d['particle_ids']];mids=d['measurement_indices'].astype(int).tolist();r={'event':int(d['event'][0]),'generated':[],'measurements':[],'ckf':[],'ambi':[],'seeds':[],'estimated_seeds':[],'ckf_input_measurements':len(mids)}
 for pid,v in zip(ids,d['particle_values']):
  if v[0]:r['generated'].append(dict(id=pid,hard_scatter=bool(v[1]),charge=float(v[2]),pt=float(v[3]),eta=float(v[4]),position_mm=v[5:8].tolist()))
 for j,mid in enumerate(mids):
  aa,bb=d['association_offsets'][j:j+2];r['measurements'].append(dict(index=mid,geometry_id=int(d['measurement_geometry'][j]),particles=[ids[z] for z in d['association_particles'][int(aa):int(bb)]]))
 for j,v in enumerate(d['track_values']):
  a,b=d['track_link_offsets'][j:j+2];c,e=d['shared_link_offsets'][j:j+2]
  t=dict(index=int(d['track_indices'][j]),reference=bool(v[0]),covariance_positive_definite=bool(v[1]),nMeasurements=int(v[2]),nHoles=int(v[3]),nOutliers=int(v[4]),chi2=float(v[5]),ndf=float(v[6]),parameters=v[7:13].tolist(),variance=v[13:19].tolist(),measurements=[mids[z] for z in d['track_links'][int(a):int(b)]],shared_measurements=[mids[z] for z in d['shared_links'][int(c):int(e)]])
  r[('ckf','ambi')[d['track_stage'][j]]].append(t)
 for j,stage in enumerate(d['seed_stage']):
  a,b=d['seed_link_offsets'][j:j+2];r[('seeds','estimated_seeds')[stage]].append(dict(measurements=[mids[z] for z in d['seed_links'][int(a):int(b)]]))
 return r
finite=lambda x:x is not None and math.isfinite(x)
ptedges=[1.,2.,5.,10.,20.,50.,100.,1000.];etaedges=list(np.arange(-3,3.001,.5))
def binof(x,edges):
 if not finite(x) or x<edges[0] or x>edges[-1]:return -1
 return min(int(np.searchsorted(edges,x,side='right'))-1,len(edges)-2)
def assess(row,sensors):
 gen={tuple(p['id']):p for p in row['generated']};ms={m['index']:m for m in row['measurements']};assoc={};links={}
 assert len(ms)==row['ckf_input_measurements']
 for mid,m in ms.items():
  pp=set(map(tuple,m['particles']));assert len(pp)==len(m['particles']);links[mid]=pp
  for pid in pp:assoc.setdefault(pid,set()).add(mid)
 sets={sc:{'fiducial':set(),'guide9':set(),'reconstructable':set()} for sc in ('inclusive','hardscatter','pileup')}
 for pid,p in gen.items():
  xx,yy,zz=p['position_mm']
  ok=all(map(finite,(xx,yy,zz,p['charge'],p['pt'],p['eta']))) and p['charge']!=0 and p['pt']>=1 and abs(p['eta'])<=3 and math.hypot(xx,yy)<=24 and abs(zz)<=1000
  if not ok:continue
  scopes=('inclusive','hardscatter' if p['hard_scatter'] else 'pileup');sens={ms[i]['geometry_id'] for i in assoc.get(pid,set())};pg={tuple(sensors[g]) for g in sens if sensors[g][0]<=3}
  for scope in scopes:
   sets[scope]['fiducial'].add(pid)
   if len(assoc.get(pid,set()))>=9:sets[scope]['guide9'].add(pid)
   if len(sens)>=6 and len(pg)>=3:sets[scope]['reconstructable'].add(pid)
 eligible=sets['inclusive']['fiducial'];out={};identity_rows={}
 for stage in ('seeds','estimated_seeds'):
  covered=set()
  for seed in row[stage]:
   inds=set(seed['measurements']);assert inds <= ms.keys();groups={tuple(sensors[ms[i]['geometry_id']]) for i in inds};assert all(g[0]<=3 for g in groups)
   if len(groups)>=3:covered |= set.intersection(*(links[i] for i in inds)) & eligible
  out[f'seeding/{stage}/raw']=len(row[stage])
  for sc,ss in sets.items():
   for den,pids in ss.items():stem=f'seeding/{stage}/eff/{sc}/{den}';out[stem+'/den']=len(pids);out[stem+'/num']=len(pids&covered)
 usage=collections.Counter(i for t in row['ambi'] for i in set(t['shared_measurements']));shared=max((sum(usage[i]>1 for i in t['shared_measurements']) for t in row['ambi']),default=0);assert shared<3
 for stage in ('ckf','ambi'):
  ts=row[stage];candidates=[]
  for t in ts:
   unique=set(t['measurements']);pars=t['parameters'];var=t['variance'];assert unique <= ms.keys()
   good=bool(t['reference']) and len(unique)>=7 and bool(t['covariance_positive_definite']) and finite(t['chi2']) and finite(t['ndf']) and t['ndf']>0 and len(pars)==6 and all(map(finite,pars)) and len(var)==6 and all(finite(v) and v>0 for v in var)
   if good:assert len(unique)==t['nMeasurements']
   pt,eta=None,None
   if len(pars)==6 and all(map(finite,pars)) and 0<pars[3]<math.pi and pars[4]!=0:pt=math.sin(pars[3])/abs(pars[4]);eta=-math.log(math.tan(pars[3]/2))
   guide=good and pt is not None and finite(pt) and finite(eta) and pt>=1 and abs(eta)<=3 and abs(pars[0])<=4 and t['nHoles']<=2 and t['nOutliers']<=2
   contributions=collections.Counter(p for i in unique for p in links[i]);winner=None
   if contributions:
    pid=min(contributions,key=lambda p:(-contributions[p],p));overlap=contributions[pid]
    if 2*overlap>=len(unique) and 2*overlap>=len(assoc[pid]):winner=pid
   category='fake' if winner is None else 'eligible_generated' if winner in eligible else 'out_of_scope_generated' if winner in gen else 'simulated_secondary'
   candidates.append((t,good,bool(guide),winner,category,pt,eta))
  identity_rows[stage]=[(c[0]['index'],*c[1:5]) for c in candidates]
  for sel,jj in [('frozen',1),('guide',2)]:
   pre=f'{sel}/{stage}/';accepted=[c for c in candidates if c[jj]];matched=collections.defaultdict(list)
   for c in accepted:
    if c[3] is not None:matched[c[3]].append(c)
   reps=[min(cs,key=lambda c:(-c[0]['nMeasurements'],c[0]['chi2']/c[0]['ndf'],c[0]['index'])) for cs in matched.values()];representative_ids={c[0]['index'] for c in reps};matched_ids=set(matched)
   counts=collections.Counter(c[4] for c in accepted)
   out[pre+'raw']=len(ts);out[pre+'accepted']=len(accepted);out[pre+'quality_rejected']=sum(not c[1] for c in candidates);out[pre+'selection_rejected']=sum(c[1] and not c[jj] for c in candidates)
   out[pre+'raw_inlier_count_mismatch']=sum(len(set(c[0]['measurements']))!=c[0]['nMeasurements'] for c in candidates)
   out[pre+'quality_rejected_inlier_count_mismatch']=sum(not c[1] and len(set(c[0]['measurements']))!=c[0]['nMeasurements'] for c in candidates)
   for cat in ('fake','eligible_generated','out_of_scope_generated','simulated_secondary'):out[pre+cat]=counts[cat]
   assert sum(counts.values())==len(accepted)
   out[pre+'duplicates']=sum(len(cs)-1 for cs in matched.values());out[pre+'fake_event']=int(counts['fake']>0);out[pre+'duplicate_event']=int(out[pre+'duplicates']>0)
   eligreps=[c for c in reps if c[3] in eligible];out[pre+'eligible_representatives']=len(eligreps);out[pre+'wrong_charge']=sum(c[0]['parameters'][4]*gen[c[3]]['charge']<0 for c in eligreps)
   for sc,ss in sets.items():
    for den,pids in ss.items():stem=pre+f'eff/{sc}/{den}';out[stem+'/den']=len(pids);out[stem+'/num']=len(pids&matched_ids)
    for axis,edges in [('pt',ptedges),('eta',etaedges)]:
     bins=collections.defaultdict(set)
     for pid in ss['fiducial']:bins[binof(gen[pid][axis],edges)].add(pid)
     for b in [*range(len(edges)-1),'outside']:
      pp=bins[-1 if b=='outside' else b];stem=pre+f'effprofile/{sc}/{axis}/{b}';out[stem+'/den']=len(pp);out[stem+'/num']=len(pp&matched_ids)
   for axis,edges,col in [('pt',ptedges,5),('eta',etaedges,6)]:
    bins=collections.defaultdict(list)
    for c in accepted:bins[binof(c[col],edges)].append(c)
    for b in range(len(edges)-1):
     cc=bins[b];stem=pre+f'candidateprofile/{axis}/{b}';out[stem+'/den']=len(cc);out[stem+'/fake']=sum(c[4]=='fake' for c in cc);out[stem+'/duplicates']=sum(c[3] is not None and c[0]['index'] not in representative_ids for c in cc)
    out[pre+f'candidateprofile/{axis}/outside']=len(bins[-1])
 return out,identity_rows,shared
n=0
for pitch in ('0.5','1','1.5','2'):
 summary=json.load(gzip.open(P/f'pitch{pitch}/summary.json.gz','rt'));sensors={int(k):v for k,v in summary['sensors'].items()};a=np.load(P/f'pitch{pitch}/events.npz');names=a['metric_names'].tolist()
 for event in (0,57,99):
  row=json.load(gzip.open(W/f'build/strixel-ttbar-production-v3/pitch{pitch}/audit/event{event:06d}.json.gz','rt'));raw=assess(row,sensors);pr=assess(portable(P/f'pitch{pitch}/audit/event-{event:06d}.npz'),sensors)
  assert raw==pr,(pitch,event,'raw-vs-portable');assert raw[2]==int(a['ambiguity_shared_max'][event])
  observed={name:int(a['counts'][event,j]) for j,name in enumerate(names)};assert raw[0]==observed,(pitch,event,{k:(v,observed.get(k)) for k,v in raw[0].items() if v!=observed.get(k)})
  n+=1;print('PASS',pitch,event,'all910counts, raw/portable candidate identities, sharedmax',raw[2],'guide ambiguity eligible/fakes',[raw[0]['guide/ambi/'+k] for k in ('eligible_representatives','fake')],flush=True)
print('INDEPENDENT_REPRESENTATIVE_CLASSIFICATION_PASS',n,'raw+portable pairs',n*910,'countchecks',flush=True)
