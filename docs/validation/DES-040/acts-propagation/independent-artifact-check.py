#!/usr/bin/env python3
"""Independent immutable artifact audit. No ACTS execution or repository writes.

All scientific inputs come from git show --revision; --raw-run optionally
cross-checks untracked acquisition CSVs against committed hash identities.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,subprocess,sys,time
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
REV='b33403ac7476fd8392542d28f984a426660527b3'
PREFIX='docs/validation/DES-040/acts-propagation/'

def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--revision',default=REV);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--raw-run',type=Path);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True);start=time.perf_counter();cache={}
 def get(path,rev=None):
  key=(rev or a.revision,path)
  if key not in cache:cache[key]=subprocess.check_output(['git','-C',str(a.root),'show',key[0]+':'+path])
  return cache[key]
 def js(path):return json.loads(get(path))
 def npz(name):
  with np.load(io.BytesIO(get(PREFIX+name)),allow_pickle=False) as z:return {k:z[k] for k in z.files}
 manifest=js(PREFIX+'artifact-manifest.json');manifest_matches={x:digest(get(x))==v for x,v in manifest['files'].items()};assert all(manifest_matches.values())
 tracks,hits=npz('tracks.npz'),npz('hits.npz');summary=js(PREFIX+'summary.json');cfg=summary['configuration'];panels=js(cfg['geometry'])['panels'];N=len(tracks['track_id']);M=len(hits['track_id'])
 assert np.array_equal(tracks['track_id'],np.arange(N)) and N==148960 and M==464397
 assert hits['geometry_id'].dtype==np.dtype('uint64')
 assert np.all(np.diff(hits['track_id'])>=0) and hits['track_id'].min()>=0 and hits['track_id'].max()<N
 xyz=np.column_stack([hits[k+'_m'] for k in ['x','y','z']]);d=np.column_stack([hits[k] for k in ['dx','dy','dz']]);assert np.isfinite(xyz).all() and np.isfinite(d).all()
 assert np.max(abs(np.linalg.norm(d,axis=1)-1))<1e-10
 # Derive source halfspaces independently from each CCW quadrilateral and rigid transform.
 normal=np.zeros((M,3));source_plane=np.full(M,-1,int);active=np.zeros(M,bool);station=np.empty(M,int);residual=np.zeros(M);excess=np.zeros(M)
 order=np.argsort(hits['panel_index'],kind='stable');po=np.searchsorted(hits['panel_index'][order],np.arange(len(panels)+1));native_map={};identifiers={}
 for j,body in enumerate(panels):
  idx=order[po[j]:po[j+1]]
  if not len(idx):continue
  basis=np.array(body['basis']);center=np.array(body['origin_m']);xy=np.array(body['vertices_m']);h=body['depth_m']/2
  delta=np.roll(xy,-1,axis=0)-xy;edge=np.column_stack([delta[:,1],-delta[:,0]]);edge/=np.linalg.norm(edge,axis=1)[:,None];bound=np.sum(edge*xy,axis=1)
  local=(xyz[idx]-center)@basis
  vals=np.column_stack([local[:,:2]@edge.T-bound,-local[:,2]-h,local[:,2]-h]);excess[idx]=np.maximum(0,vals.max(1))
  active[idx]=np.all(local[:,:2]@edge.T<=bound-.03+1e-8,axis=1);station[idx]=body['station']
  norms=np.vstack([np.c_[edge,np.zeros(4)],[0,0,-1],[0,0,1]])@basis.T
  for face in np.unique(hits['face_index'][idx]):
   at=idx[hits['face_index'][idx]==face];v=vals[hits['face_index'][idx]==face];scores=abs(v).max(0);pl=int(scores.argmin());assert scores[pl]<1e-7
   # Every observed native face maps uniquely to the same exact source face.
   native_map[j,int(face)]=pl;normal[at]=norms[pl];source_plane[at]=pl;residual[at]=abs(v[:,pl])
   assert np.all(hits['is_large'][at]==(pl>=4))
   native_ids=np.unique(hits['geometry_id'][at]);assert len(native_ids)==1
   ident=int(native_ids[0]);assert ident not in identifiers or identifiers[ident]==(j,int(face));identifiers[ident]=(j,int(face))
 assert np.all(source_plane>=0) and np.array_equal(hits['active'],active) and np.array_equal(hits['station'],station)
 assert max(residual.max(),excess.max())<1e-8
 assert np.allclose(hits['plane_residual_m'],residual,rtol=0,atol=5e-14)
 assert np.allclose(hits['finite_excess_m'],excess,rtol=0,atol=5e-14)
 # Independent ordered-event state machine. A pair is accepted only within one
 # uninterrupted entry/exit visit of a source prism; station IDs are set-valued.
 names=['outer_unique_faces','active_unique_faces','outer_paired_stations','active_paired_stations','numerical_duplicates','reentries','side_events','orphan_transitions','open_visits','tangent_events']
 counters={k:np.zeros(N,int) for k in names};off=np.searchsorted(hits['track_id'],np.arange(N+1));unique=np.zeros(M,bool);sense=(normal*d).sum(1);min_path_delta=0.
 for tid in np.flatnonzero(np.diff(off)):
  lo,hi=off[tid:tid+2];face_set=set();border_set=set();pairs=set();border_pairs=set();current={};previous={};last={};counts={k:0 for k in names}
  assert np.array_equal(hits['sequence'][lo:hi],np.arange(hi-lo))
  if hi-lo>1:
   md=float(np.diff(hits['path_m'][lo:hi]).min());min_path_delta=min(min_path_delta,md);assert md>=-2e-8
  for i in range(lo,hi):
   panel=int(hits['panel_index'][i]);face=int(hits['face_index'][i]);identity=int(hits['geometry_id'][i]);old=last.get(identity);path=float(hits['path_m'][i])
   if old is not None and abs(path-old[0])<=2e-8 and np.linalg.norm(xyz[i]-old[1])<=2e-8:counts['numerical_duplicates']+=1;continue
   last[identity]=(path,xyz[i]);unique[i]=True
   is_large=source_plane[i]>=4
   if not is_large:counts['side_events']+=1
   if abs(sense[i])<1e-10:counts['tangent_events']+=1;continue
   if is_large:
    face_set.add(identity)
    if active[i]:border_set.add(identity)
   if sense[i]<0:
    if panel in current:counts['orphan_transitions']+=1
    counts['reentries']+=int(panel in previous);previous[panel]=True;current[panel]=(int(source_plane[i]),bool(active[i]))
   else:
    entry=current.pop(panel,None)
    if entry is None:counts['orphan_transitions']+=1
    elif entry[0]>=4 and source_plane[i]>=4 and entry[0]!=source_plane[i]:
     pairs.add(int(station[i]))
     if entry[1] and active[i]:border_pairs.add(int(station[i]))
  counts.update(outer_unique_faces=len(face_set),active_unique_faces=len(border_set),outer_paired_stations=len(pairs),active_paired_stations=len(border_pairs),open_visits=len(current))
  for k in names:counters[k][tid]=counts[k]
 counter_comparisons={k:int(np.count_nonzero(v!=tracks[k])) for k,v in counters.items()};assert not any(counter_comparisons.values())
 assert np.array_equal(hits['numerical_unique_event'],unique)
 complete=np.isin(tracks['status'],['completed','returned_to_entrance']);unqualified=(counters['orphan_transitions']>0)|(complete&(counters['open_visits']>0))|(tracks['parallel_ambiguities']>0);incomplete=~complete|unqualified
 assert np.array_equal(incomplete,tracks['incomplete']) and not unqualified.any()
 assert np.array_equal(incomplete,tracks['status']=='field_masked')
 # Validate generated coordinates, full-sphere denominators and map-cell weights.
 direction=tracks['direction'];pos=tracks['entrance_position_m'];starts=tracks['start_m'];R,H=4.35,6.5
 assert np.allclose(starts-pos,1e-5*direction,rtol=0,atol=3e-15)
 assert np.allclose(np.arcsinh(pos[:,2]/np.hypot(pos[:,0],pos[:,1])),tracks['eta_pos'],rtol=0,atol=3e-13)
 az=np.degrees(np.arctan2(pos[:,1],pos[:,0]))%360;assert np.max(abs(az-tracks['phi_pos_deg']))<1e-12
 assert np.allclose(np.linalg.norm(direction,axis=1),1,rtol=0,atol=1e-14)
 kinds=tracks['entrance_kind'];assert np.allclose(np.hypot(pos[kinds==0,0],pos[kinds==0,1]),R) and np.allclose(abs(pos[kinds!=0,2]),H)
 metrics=[('outer_unique_faces',6),('active_unique_faces',6),('outer_paired_stations',3),('active_paired_stations',3)];cases=[];comparisons=0;reference_direction=None
 for case in summary['cases']:
  take=(tracks['momentum_GeV']==case['momentum_GeV'])&(tracks['charge']==case['charge']);direction_ids=tracks['direction_id'][take]
  assert np.array_equal(direction_ids,np.arange(14896));common=direction[take]
  if reference_direction is None:reference_direction=common
  else:assert np.array_equal(reference_direction,common)
  row=dict(momentum_GeV=case['momentum_GeV'],charge=case['charge'],samples={})
  for sample,label in [(0,'eta_display'),(1,'full_sphere')]:
   mask=take&(tracks['sample']==sample);weights=tracks['solid_angle_weight_sr'][mask];bad=incomplete[mask];n=int(mask.sum());expected=case['samples'][label];assert n==expected['tracks']==(10800 if sample==0 else 4096)
   assert np.isclose(weights.sum(),4*np.pi*(np.tanh(3) if sample==0 else 1),rtol=0,atol=2e-14)
   if sample==0:
    eta_bin=tracks['eta_bin'][mask];phi_bin=tracks['phi_bin'][mask];cells=eta_bin*180+phi_bin;assert np.array_equal(np.sort(cells),np.arange(10800));ee=tracks['eta_edges'];pe=tracks['phi_edges_deg']
    assert np.all((tracks['eta_pos'][mask]>ee[eta_bin])&(tracks['eta_pos'][mask]<ee[eta_bin+1]))
    assert np.all((tracks['phi_pos_deg'][mask]>pe[phi_bin])&(tracks['phi_pos_deg'][mask]<pe[phi_bin+1]))
    w=(np.tanh(ee[eta_bin+1])-np.tanh(ee[eta_bin]))*2*np.pi/180;assert np.allclose(w,weights,rtol=0,atol=1e-18)
   out=dict(N=n,incomplete=int(bad.sum()),metrics={})
   assert out['incomplete']==expected['incomplete_tracks']
   for field,threshold in metrics:
    passed=counters[field][mask]>=threshold;lo=float(np.dot(weights,passed)/weights.sum());up=float(np.dot(weights,passed|bad)/weights.sum());proven=int(passed.sum());unknown=int((bad&~passed).sum());orig=expected[field]
    assert abs(lo-orig['proven_lower_fraction'])<1e-14 and abs(up-orig['possible_upper_fraction'])<1e-14
    assert proven==orig['proven_tracks'] and unknown==orig['unqualified_below_threshold'];comparisons+=1
    if sample==1:assert abs(orig['binomial_standard_error_lower']-np.sqrt(lo*(1-lo)/n))<1e-14
    else:assert orig['binomial_standard_error_lower'] is None
    out['metrics'][field]=dict(lower_fraction=lo,upper_fraction=up,proven=proven,unresolved_below_threshold=unknown)
   row['samples'][label]=out
  cases.append(row)
 # Independently check every rounded full-sphere table cell and plotted hit count.
 table_rows=0
 for line in get(PREFIX+'results.md').decode().splitlines():
  if not line.startswith('|'):continue
  cells=[x.strip() for x in line.strip('|').split('|')]
  try:pm=float(cells[0]);charge=int(cells[1])
  except (ValueError,IndexError):continue
  entry=next(x for x in cases if x['momentum_GeV']==pm and x['charge']==charge)['samples']['full_sphere']
  for col,key in [(2,'outer_unique_faces'),(3,'outer_paired_stations'),(4,'active_paired_stations')]:
   vals=list(map(float,cells[col].split('–')));want=entry['metrics'][key]
   assert vals==[round(100*want['lower_fraction'],2),round(100*want['upper_fraction'],2)]
  assert float(cells[5])==round(100*entry['incomplete']/entry['N'],2);table_rows+=1
 assert table_rows==10
 plotted_hit_counts={str(pm):int((tracks['momentum_GeV'][hits['track_id']]==pm).sum()) for pm in [2.65,100.,1000.]}
 # Provenance and fixed upstream inputs, including all52 retained magnetic files.
 provenance=js(PREFIX+'provenance.json');fig=js(PREFIX+'figures.json');controls=js(PREFIX+'controls.json');acq=js(PREFIX+'controls-acquisition.json')
 assert controls['passed'] and acq['passed'] and controls['executable_sha256']==acq['executable_sha256']==provenance['native_executable_sha256']
 assert digest(get(PREFIX+'controls.json'))==provenance['controls_sha256'] and digest(get(PREFIX+'controls-acquisition.json'))==provenance['acquisition_controls_sha256']==summary['native_metadata']['controls_sha256']
 assert summary['native_metadata']['source_revision']==provenance['native_acquisition_source_revision'] and summary['postprocessing']==provenance['postprocessing']
 for path,h in summary['native_metadata']['source_files_sha256'].items():assert digest(get(path,provenance['native_acquisition_source_revision']))==h
 for path,h in summary['postprocessing']['source_files_sha256'].items():assert digest(get(path,summary['postprocessing']['source_revision']))==h==digest(get(path))
 for name,h in controls['source_sha256'].items():assert digest(get('tools/muon_layout/acts/'+name))==h
 for name,h in acq['source_sha256'].items():assert digest(get('tools/muon_layout/acts/'+name,provenance['native_acquisition_source_revision']))==h
 assert digest(get(cfg['geometry']))==cfg['geometry_sha256']==provenance['fixed_geometry_sha256'];assert digest(get(cfg['map']))==cfg['map_sha256']==provenance['fixed_field_map_sha256']
 for name,h in fig['input_sha256'].items():assert digest(get(PREFIX+name))==h
 for name,info in fig['outputs'].items():assert digest(get(PREFIX+name))==info['sha256'] and len(get(PREFIX+name))==info['bytes']
 scope=['docs/validation/DES-039','tools/toroid_prototype','tools/muon_study'];files=subprocess.check_output(['git','-C',str(a.root),'ls-tree','-r','--name-only',a.revision,*scope],text=True).splitlines();assert len(files)==52
 inherited_matches={name:subprocess.check_output(['git','-C',str(a.root),'rev-parse',a.revision+':'+name],text=True).strip()==subprocess.check_output(['git','-C',str(a.root),'rev-parse','b3ff6a3b2ae111251fbc126d5ad489114877c3c7:'+name],text=True).strip() for name in files};assert all(inherited_matches.values())
 # Run exactly the11 committed NumPy counter/entrance unit tests in a scratch
 # reconstruction of their minimal source tree. No monkeypatched implementation.
 unitroot=a.work/'unit-tree'
 needed=['tools/muon_layout/acts/test_analysis.py','tools/muon_layout/acts/analyze.py','tools/muon_layout/acts/prepare.py','tools/muon_layout/acts/config.json','tools/muon_layout/geometry.py','tools/toroid_prototype/geometry.py','tools/toroid_prototype/map.py',cfg['geometry'],cfg['map']]
 for path in needed:
  out=unitroot/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(get(path))
 test=subprocess.run([sys.executable,'-B','-m','unittest','tools.muon_layout.acts.test_analysis'],cwd=unitroot,text=True,capture_output=True);assert test.returncode==0 and 'Ran 11 tests' in test.stderr,test.stderr
 # Explicit source construction fix and contact regression are covered above;
 # the summary from actual postprocessing exists and every audited field matches.
 raw=dict(requested=a.raw_run is not None,available=False)
 if a.raw_run is not None:
  rp=a.raw_run;assert digest((rp/'hits.csv').read_bytes())==summary['inputs']['raw_hits_sha256'];assert digest((rp/'tracks.csv').read_bytes())==summary['inputs']['raw_tracks_sha256'];raw['available']=True
  with (rp/'hits.csv').open(newline='') as f:
   for i,r in enumerate(csv.DictReader(f)):
    for k in ['track_id','sequence','panel_index','face_index','is_large','geometry_id']:assert int(r[k])==hits[k][i]
    for k in ['x_m','y_m','z_m','path_m','dx','dy','dz']:assert float(r[k])==hits[k][i]
   assert i+1==M
  with (rp/'tracks.csv').open(newline='') as f:
   for i,r in enumerate(csv.DictReader(f)):
    assert int(r['track_id'])==i and r['status']==tracks['status'][i] and r['error']==tracks['error'][i]
    for k in ['steps','native_corrections','guard_caps','parallel_ambiguities']:assert int(r[k])==tracks[k][i]
    assert float(r['path_m'])==tracks['path_m'][i]
   assert i+1==N
  raw.update(native_event_rows_exact=M,native_track_rows_exact=N)
 report=dict(revision=a.revision,passed=True,scope='Independent artifact/counter/finite-hit/denominator audit; no new ACTS transport',
  human_approval=False,runtime=dict(python=sys.version,numpy=np.__version__),rounded_result_table_rows_verified=table_rows,plotted_hit_counts=plotted_hit_counts,manifest_entries_verified=len(manifest_matches),inherited_magnetic_files_verified=len(inherited_matches),
  native_rows=dict(tracks=N,events=M,large_events=int(hits['is_large'].sum()),side_events=int((~hits['is_large']).sum()),unique_observed_face_ids=len(identifiers),max_source_plane_residual_m=float(residual.max()),max_source_prism_excess_m=float(excess.max()),min_event_path_delta_m=min_path_delta),
  independent_counter_mismatch_rows=counter_comparisons,counter_totals={k:int(v.sum()) for k,v in counters.items()},
  statuses={str(k):int(v) for k,v in zip(*np.unique(tracks['status'],return_counts=True))},availability_summary_comparisons=comparisons,cases=cases,
  sample_scope=dict(full_sphere_per_case=4096,eta_display_per_case=10800,display_solid_angle_sr=float(4*np.pi*np.tanh(3)),excluded_display_solid_angle_fraction=float(1-np.tanh(3)),sphere_polar_overflow_per_case=int(((tracks['sample']==1)&(tracks['momentum_GeV']==2.65)&(tracks['charge']==-1)&(abs(tracks['eta_pos'])>3)).sum()),incomplete_proven_six_faces=int((incomplete&(counters['outer_unique_faces']>=6)).sum())),
  raw_csv_crosscheck=raw,unit_tests=dict(returncode=test.returncode,stderr=test.stderr.strip()),
  hashes=dict(tracks_npz=digest(get(PREFIX+'tracks.npz')),hits_npz=digest(get(PREFIX+'hits.npz')),geometry=digest(get(cfg['geometry'])),field_map=digest(get(cfg['map']))),
  elapsed_seconds=time.perf_counter()-start,limitations=['Independent event analysis verifies retained roots, not missing intersections in arbitrary trajectories.','No material propagation, chamber response, reconstruction or global portal-transition qualification.','Finite angular samples and wide field-unavailable bounds limit coverage claims.'])
 a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({k:report[k] for k in ['passed','native_rows','independent_counter_mismatch_rows','counter_totals','statuses','availability_summary_comparisons','sample_scope','raw_csv_crosscheck','unit_tests','elapsed_seconds']},indent=2))
if __name__=='__main__':main()
