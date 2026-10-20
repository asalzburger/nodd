#!/usr/bin/env python3
"""Independent immutable paired-native/OBJ/inventory audit; no ACTS runs.
Read inputs via git show. Optional --raw-root verifies ignored acquisition CSVs,
which remain supplemental, never claimed as tracked evidence. No repo imports.
"""
import argparse,collections,csv,gzip,hashlib,io,itertools,json,math,re,subprocess,time,zipfile
from pathlib import Path
import numpy as np
REV='0576b7a615c81d1687f0cf7a3ceb0ca310478481'
SOURCE='22a3f8c113a276b1321adeb9b994107594eb3c7d'
D='docs/validation/DES-040/wheels-2026-10-20/'
NAMES=['outer_unique_faces','active_unique_faces','outer_paired_stations','active_paired_stations','numerical_duplicates','reentries','side_events','orphan_transitions','open_visits','tangent_events']
METRICS={prefix+k:t for prefix in ['', 'endcap_'] for k,t in zip(NAMES[:4],[6,6,3,3])}
METRICS.update({f'endcap_station_{s}_{b}_paired':1 for s in [1,2,3] for b in ['outer','active']})
def sha(x):return hashlib.sha256(x).hexdigest()
def main(a):
 start=time.perf_counter();cache={};hashes={}
 def get(p,rev=None):
  key=(rev or a.revision,p)
  if key not in cache:cache[key]=subprocess.check_output(['git','-C',str(a.repo),'show',key[0]+':'+p]);hashes[key[0]+':'+p]=sha(cache[key])
  return cache[key]
 def js(p):return json.loads(get(p))
 def load(p):
  with np.load(io.BytesIO(get(p)),allow_pickle=False) as z:return dict(z)
 def halfspaces(body):
  q=np.asarray(body['basis']);xy=np.asarray(body['vertices_m']);e=np.roll(xy,-1,axis=0)-xy;n=np.c_[e[:,1],-e[:,0]];n/=np.linalg.norm(n,axis=1)[:,None];b=np.sum(n*xy,axis=1)
  return q,xy,n,b
 def se(v,w,s):
  if (s==0).any():return None
  v=v.astype(float);variance=0.
  for bank in np.unique(s):
   k=s==bank;n=k.sum();assert n>1 and np.allclose(w[k],w[k][0],rtol=1e-12,atol=0)
   variance+=(w[k].sum()/w.sum())**2*np.var(v[k],ddof=1)/n
  return float(math.sqrt(variance))
 def regions(t,c):
  s,e=t['sample'],t['eta_pos'];cut=c['endcap_abs_eta_min'];return {'eta_display':s==0,'full_sphere':s==1,'full_sphere_endcap':(s==1)&(abs(e)>=cut),'full_sphere_endcap_positive':(s==1)&(e>=cut),'full_sphere_endcap_negative':(s==1)&(e<=-cut),'endcap_caps':np.isin(s,[2,3]),'endcap_cap_positive':s==2,'endcap_cap_negative':s==3}
 summaries={};tracks={};hits={};systems={}
 for system in ['before','after']:
  p=D+'propagation/'+system+'/';s=js(p+'summary.json');c=s['configuration'];t=load(p+'tracks.npz');h=load(p+'hits.npz');panels=js(c['geometry'])['panels'];N=len(t['track_id']);M=len(h['track_id']);assert N==230880
  for name in ['tracks.npz','hits.npz']:assert sha(get(p+name))==s['artifacts'][name]['sha256']
  assert h['geometry_id'].dtype==np.dtype('uint64');assert np.array_equal(t['track_id'],np.arange(N));assert np.all(np.diff(h['track_id'])>=0)
  assert sha(get(c['geometry']))==c['geometry_sha256'] and sha(get(c['map']))==c['map_sha256']
  xyz=np.c_[h['x_m'],h['y_m'],h['z_m']];direction=np.c_[h['dx'],h['dy'],h['dz']];assert np.isfinite(xyz).all() and np.isfinite(direction).all();assert np.max(abs(np.linalg.norm(direction,axis=1)-1))<1e-10
  normals=np.empty((M,3));plane=np.full(M,-1,int);active=np.zeros(M,bool);endcap=np.zeros(M,bool);station=np.empty(M,int);residual=np.zeros(M);excess=np.zeros(M);identities={};face_map={}
  order=np.argsort(h['panel_index'],kind='stable');off=np.searchsorted(h['panel_index'][order],np.arange(len(panels)+1))
  for j,body in enumerate(panels):
   k=order[off[j]:off[j+1]]
   if not len(k):continue
   Q,xy,n,b=halfspaces(body);local=(xyz[k]-body['origin_m'])@Q;v=np.c_[local[:,:2]@n.T-b,-local[:,2]-body['depth_m']/2,local[:,2]-body['depth_m']/2];excess[k]=np.maximum(0,v.max(1))
   active[k]=(local[:,:2]@n.T<=b-.03+1e-8).all(axis=1);endcap[k]=body['kind']=='endcap';station[k]=body['station'];outward=np.vstack((np.c_[n,np.zeros(4)],[0,0,-1],[0,0,1]))@Q.T
   for face in np.unique(h['face_index'][k]):
    take=h['face_index'][k]==face;ids=k[take];vv=v[take];pl=int(abs(vv).max(0).argmin());assert abs(vv[:,pl]).max()<1e-7
    plane[ids]=pl;normals[ids]=outward[pl];residual[ids]=abs(vv[:,pl]);assert np.all(h['is_large'][ids]==(pl>=4));nid=np.unique(h['geometry_id'][ids]);assert len(nid)==1
    ident=int(nid[0]);key=(j,int(face));assert ident not in identities or identities[ident]==key;identities[ident]=key;face_map[key]=(pl,ident)
  assert (plane>=0).all() and np.array_equal(active,h['active']) and np.array_equal(station,h['station']) and np.array_equal(endcap,h['is_endcap'])
  assert max(residual.max(),excess.max())<1e-8;assert np.allclose(h['plane_residual_m'],residual,rtol=0,atol=5e-14);assert np.allclose(h['finite_excess_m'],excess,rtol=0,atol=5e-14)
  counts={prefix+k:np.zeros(N,'i4') for prefix in ['', 'endcap_'] for k in NAMES};counts.update({k:np.zeros(N,'i1') for k in METRICS if '_station_' in k});unique=np.zeros(M,bool);sense=np.einsum('ij,ij->i',normals,direction);offset=np.searchsorted(h['track_id'],np.arange(N+1))
  for tid in np.flatnonzero(np.diff(offset)):
   lo,hi=offset[tid:tid+2];assert np.array_equal(h['sequence'][lo:hi],np.arange(hi-lo));assert hi-lo<2 or np.min(np.diff(h['path_m'][lo:hi]))>=-2e-8
   last={};current={};previous=set();fset=[set(),set()];aset=[set(),set()];pairs=[set(),set()];apairs=[set(),set()]
   for i in range(lo,hi):
    ident=int(h['geometry_id'][i]);pn=int(h['panel_index'][i]);pl=int(plane[i]);path=float(h['path_m'][i]);ec=bool(endcap[i]);ix=[0,1] if ec else [0];old=last.get(ident)
    if old is not None and abs(path-old[0])<=2e-8 and np.dot(xyz[i]-old[1],xyz[i]-old[1])<=4e-16:
     for group in ix:counts[('endcap_' if group else '')+'numerical_duplicates'][tid]+=1
     continue
    last[ident]=(path,xyz[i]);unique[i]=True;large=pl>=4
    if not large:
     for group in ix:counts[('endcap_' if group else '')+'side_events'][tid]+=1
    if abs(sense[i])<1e-10:
     for group in ix:counts[('endcap_' if group else '')+'tangent_events'][tid]+=1
     continue
    if large:
     for group in ix:
      fset[group].add(ident)
      if active[i]:aset[group].add(ident)
    if sense[i]<0:
     for group in ix:
      prefix='endcap_' if group else ''
      if pn in current:counts[prefix+'orphan_transitions'][tid]+=1
      if pn in previous:counts[prefix+'reentries'][tid]+=1
     previous.add(pn);current[pn]=(pl,bool(active[i]),ec)
    else:
     entry=current.pop(pn,None)
     if entry is None:
      for group in ix:counts[('endcap_' if group else '')+'orphan_transitions'][tid]+=1
     elif entry[0]>=4 and pl>=4 and entry[0]!=pl:
      for group in ix:pairs[group].add(int(station[i]))
      if entry[1] and active[i]:
       for group in ix:apairs[group].add(int(station[i]))
      if ec:
       counts[f'endcap_station_{station[i]}_outer_paired'][tid]=1
       if entry[1] and active[i]:counts[f'endcap_station_{station[i]}_active_paired'][tid]=1
   for group in [0,1]:
    prefix='endcap_' if group else ''
    for key,value in zip(NAMES[:4],[len(fset[group]),len(aset[group]),len(pairs[group]),len(apairs[group])]):counts[prefix+key][tid]=value
    counts[prefix+'open_visits'][tid]=sum(1 for v in current.values() if group==0 or v[2])
  mismatches={k:int(np.count_nonzero(v!=t[k])) for k,v in counts.items()};assert not any(mismatches.values()),mismatches
  assert np.array_equal(unique,h['numerical_unique_event']);complete=np.isin(t['status'],['completed','returned_to_entrance']);uncertain=(counts['orphan_transitions']>0)|(complete&(counts['open_visits']>0))|(t['parallel_ambiguities']>0);bad=~complete|uncertain
  assert np.array_equal(bad,t['incomplete']) and not uncertain.any()
  statuses={str(k):int(v) for k,v in zip(*np.unique(t['status'],return_counts=True))};assert statuses==s['audit']['statuses'];assert M==s['audit']['raw_boundary_hits'] and int(unique.sum())==s['audit']['unique_crossing_events']
  rs=regions(t,c);comparisons=0;ref=None
  for case in s['cases']:
   pick=(t['momentum_GeV']==case['momentum_GeV'])&(t['charge']==case['charge']);assert pick.sum()==23088;assert np.array_equal(t['direction_id'][pick],np.arange(23088));dd=t['direction'][pick]
   if ref is None:ref=dd
   else:assert np.array_equal(ref,dd)
   for label,mask in rs.items():
    use=pick&mask;w=t['solid_angle_weight_sr'][use];sam=t['sample'][use];expected=case['samples'][label];assert use.sum()==expected['tracks'] and bad[use].sum()==expected['incomplete_tracks'];assert abs(w.sum()-expected['weight_sr'])<1e-12
    for metric,threshold in METRICS.items():
     passed=counts[metric][use]>=threshold;possible=passed|bad[use];v=expected[metric];lo=float(w@passed/w.sum());hi=float(w@possible/w.sum())
     assert abs(lo-v['proven_lower_fraction'])<2e-14 and abs(hi-v['possible_upper_fraction'])<2e-14;assert passed.sum()==v['proven_tracks'] and possible.sum()==v['possible_tracks']
     for key,z in [('sampling_standard_error_lower',se(passed,w,sam)),('sampling_standard_error_upper',se(possible,w,sam))]:assert (z is None and v[key] is None) or abs(z-v[key])<1e-14
     comparisons+=1
  assert np.array_equal(h['panel_source_id'],np.asarray([p['id'] for p in panels]));assert np.allclose(t['start_m']-t['entrance_position_m'],1e-5*t['direction'],rtol=0,atol=3e-15)
  c0=(t['momentum_GeV']==2.65)&(t['charge']==-1);sphere=c0&(t['sample']==1);caps=c0&np.isin(t['sample'],[2,3]);assert abs(t['solid_angle_weight_sr'][sphere].sum()-4*np.pi)<2e-14;assert abs(t['solid_angle_weight_sr'][caps].sum()-4*np.pi*(1-np.tanh(c['endcap_abs_eta_min'])))<2e-14
  rawcheck={'requested':a.raw_root is not None,'tracked':False}
  if a.raw_root:
   rr=a.raw_root/(system+'-run');rhash={name:sha((rr/name).read_bytes()) for name in s['inputs']['native_files_sha256']};assert rhash==s['inputs']['native_files_sha256'];native_faces={};native_ids=set()
   with (rr/'geometry.csv').open() as stream:
    for row in csv.DictReader(stream):
     j,k,nid=int(row['panel_index']),int(row['face_index']),int(row['geometry_id']);assert nid not in native_ids;native_ids.add(nid);native_faces[j,k]=nid
   assert len(native_faces)==6*len(panels) and all(native_faces[k]==ident for k,(_,ident) in face_map.items())
   with (rr/'hits.csv').open() as stream:
    for i,row in enumerate(csv.DictReader(stream)):
     for k in ['track_id','sequence','panel_index','face_index','geometry_id','is_large']:assert int(row[k])==h[k][i]
     for k in ['x_m','y_m','z_m','path_m','dx','dy','dz']:assert float(row[k])==h[k][i]
    assert i+1==M
   with (rr/'tracks.csv').open() as stream:
    for i,row in enumerate(csv.DictReader(stream)):
     assert int(row['track_id'])==i and row['status']==t['status'][i] and row['error']==t['error'][i]
     for k in ['steps','native_corrections','guard_caps','parallel_ambiguities']:assert int(row[k])==t[k][i]
     assert float(row['path_m'])==t['path_m'][i]
    assert i+1==N
   rawcheck.update(hash_verified_files=len(rhash),event_rows_equal=M,track_rows_equal=N,native_faces=len(native_faces),exact_uint64_IDs=True)
  gate=js(D+'propagation/'+system+'-controls.json');assert gate['passed'] and len(gate['checks'])==12 and all(k['passed'] for k in gate['checks']);gate_names=[k['name'] for k in gate['checks']]
  assert gate.get('validated_committed_source_revision',gate['source_revision'])==SOURCE
  for path,hsh in s['postprocessing']['source_files_sha256'].items():assert sha(get(path,SOURCE))==hsh==sha(get(path))
  for path,hsh in gate['source_sha256'].items():assert sha(get(path,SOURCE))==hsh==sha(get(path))
  failed=np.flatnonzero(t['status']=='step_limit');assert failed.tolist()==([88059] if system=='before' else [28149]);assert t['incomplete'][failed].all()
  summaries[system]=s;tracks[system]=t;hits[system]=h;systems[system]={'tracks':N,'events':M,'unique_events':int(unique.sum()),'statuses':statuses,'counter_mismatch_rows':mismatches,'counter_totals':{k:int(v.sum()) for k,v in counts.items()},'max_plane_residual_m':float(residual.max()),'max_prism_excess_m':float(excess.max()),'availability_metric_regions_recomputed':comparisons,'observed_exact_native_face_IDs':len(identities),'gate_names':gate_names,'recorded_native_gates_pass':True,'step_limit_track':int(failed[0]),'raw_csv_crosscheck':rawcheck}
  print(system+' all retained events/counters/bounds checked',flush=True)
 # Paired primary rows, uncertainty bounds and independent-stratum errors.
 b,aa=tracks['before'],tracks['after'];config=summaries['before']['configuration'];comparison=js(D+'propagation/comparison/comparison.json');paired=0
 primary=['track_id','direction_id','momentum_GeV','charge','sample','direction','entrance_position_m','start_m','entrance_kind','eta_pos','phi_pos_deg','eta_bin','phi_bin','solid_angle_weight_sr','eta_edges','phi_edges_deg']
 assert all(np.array_equal(b[k],aa[k]) for k in primary)
 for case in comparison['cases']:
  pick=(b['momentum_GeV']==case['momentum_GeV'])&(b['charge']==case['charge'])
  for label,mask in regions(b,config).items():
   take=pick&mask;w=b['solid_angle_weight_sr'][take];sam=b['sample'][take];ib=b['incomplete'][take];ia=aa['incomplete'][take];norm=w/w.sum();row=case['samples'][label]
   for metric,threshold in METRICS.items():
    before=b[metric][take]>=threshold;after=aa[metric][take]>=threshold;ub=before|ib;ua=after|ia;lo=after.astype(int)-ub.astype(int);hi=ua.astype(int)-before.astype(int);value=row[metric]
    for key,vec in [('before_lower_fraction',before),('before_upper_fraction',ub),('after_lower_fraction',after),('after_upper_fraction',ua),('change_lower_fraction',lo),('change_upper_fraction',hi)]:assert abs(float(norm@vec)-value[key])<2e-14
    for key,vec in [('change_lower_sampling_standard_error',lo),('change_upper_sampling_standard_error',hi)]:
     x=se(vec,w,sam);assert (x is None and value[key] is None) or abs(x-value[key])<1e-14
    gain=after&~ub;loss=before&~ua;assert gain.sum()==value['definitely_gained_tracks'] and loss.sum()==value['definitely_lost_tracks']
    for key,vec in [('definitely_gained_fraction',gain),('definitely_lost_fraction',loss)]:assert abs(float(norm@vec)-value[key])<2e-14
    common=~ib&~ia;assert common.sum()==value['common_complete_tracks']
    if common.any():assert abs(float(w[common]@(after[common].astype(int)-before[common].astype(int))/w[common].sum())-value['common_complete_change_diagnostic'])<2e-14
    conservative=None
    if not (sam==0).any():
     variance=0.
     for bank in np.unique(sam):
      ix=sam==bank;nn=ix.sum();variance+=(norm[ix].sum())**2*np.maximum(lo[ix]**2,hi[ix]**2).sum()/(nn*(nn-1))
     conservative=float(math.sqrt(variance))
    observed=value['conservative_true_change_sampling_standard_error_upper'];assert (conservative is None and observed is None) or abs(conservative-observed)<1e-14
    paired+=1
 # Inspect every compressed supplemental native diagnostic and its raw-byte hash.
 audit=js(D+'propagation/failure-audit/audit.json');failure={}
 for system,record in audit['systems'].items():
  tid=record['primary_ids'][0];assert tracks[system]['status'][tid]=='step_limit';vr={};decompressed={}
  for variant,run in record['supplemental_runs'].items():
   blocks={}
   for filename,info in run['files'].items():
    blob=get(D+'propagation/failure-audit/'+system+'/'+filename);assert sha(blob)==info['sha256'];body=gzip.decompress(blob);assert sha(body)==info['decompressed_sha256'];blocks[filename.split('-',1)[1] if variant=='original' else filename[len(variant)+1:]]=body
   rows=list(csv.DictReader(io.StringIO(blocks['tracks.csv.gz'].decode())));steps=list(csv.DictReader(io.StringIO(blocks['step-audit.csv.gz'].decode())));roots=list(csv.DictReader(io.StringIO(blocks['root-audit.csv.gz'].decode())));assert rows==run['tracks'];assert len(rows)==1 and int(rows[0]['track_id'])==tid
   for root in roots:int(root.get('geometry_id',root.get('current_geometry_id',0)))
   vr[variant]={'status':rows[0]['status'],'steps':int(rows[0]['steps']),'recorded_step_rows':len(steps),'recorded_root_rows':len(roots),'final_remaining_native_step_m':float(steps[-1]['native_remaining_step_m'])};decompressed[variant]=blocks
  for name in ['tracks.csv.gz','hits.csv.gz','root-audit.csv.gz','step-audit.csv.gz']:assert decompressed['original'][name]==decompressed['exhaustive'][name]
  assert all(vr[v]['status']=='step_limit' for v in ['original','exhaustive','half-step','tight-surface'])
  assert vr['tight-rk']['status']==('field_masked' if system=='before' else 'completed');failure[system]={'track_id':tid,'variants':vr,'primary_retained_incomplete':True}
 # Invariance of prior frozen numerical source, maps and geometry inputs.
 invariant_paths=['tools/muon_layout/wheels.py','tools/muon_layout/wheels-config.json','tools/muon_layout/wheels_field.py','tools/muon_layout/wheels_acts/variant.py','tools/muon_layout/wheels_acts/config.json','tools/muon_layout/wheels_acts/prepare.py','tools/muon_layout/wheels_acts/controls.py','tools/muon_layout/wheels_acts/analyze.py','tools/muon_layout/wheels_acts/compare.py','tools/muon_layout/acts/propagate.cpp',D+'candidate/geometry.json',D+'magnetic/configuration.json',D+'magnetic/energy.json',D+'magnetic/cold.json',D+'magnetic/controls.json',D+'magnetic/baseline-extended-map.npz',D+'magnetic/candidate-map.npz']
 for path in invariant_paths:assert get(path,SOURCE)==get(path)
 # P2 documentation hash note: a single eight-line derived-dimension paragraph.
 old_doc=get('docs/design/DES-040-muon-chambers-frame.md',SOURCE);lines=old_doc.decode().splitlines(keepends=True);target='78590c60800e60d55d986b9f94cbe012dc470d4d0b83d7c46b50eec681b95678';proof=[]
 for i in range(len(lines)-7):
  if sha(''.join(lines[:i]+lines[i+8:]).encode())==target:proof.append([i+1,i+8])
 assert len(proof)==1
 result={'passed':True,'assignment':'W-P3','revision':a.revision,'source_acquisition_revision':SOURCE,'human_approval':False,'systems':systems,'paired_metric_regions_recomputed':paired,'all_identical_primary_keys':primary,'failure_audit':failure,'numerical_input_files_identical_to_P2':len(invariant_paths),'P2_DES040_hash_resolution':{'removed_derived_dimension_paragraph_lines':proof[0],'matches_recorded_generation_hash':target},'input_sha256':hashes,'elapsed_seconds':time.perf_counter()-start,'limitations':['No new ACTS propagation or energy/map solver runs.','Independent retained-root/counter audit cannot prove absence of arbitrary missing intersections.','Native control gates cover bounded samples; actual full scans retain two unresolved correction cycles.','Field-unavailable bounds dominate; no material transport, response, reconstruction or engineering acceptance.']}
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['input_sha256','all_identical_primary_keys']},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--revision',default=REV);p.add_argument('--raw-root',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
