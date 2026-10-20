#!/usr/bin/env python3
"""Read-only PR87 before/after signed-response check.

Requires Python3, numpy and a C++17 compiler. Example:
 python3 pr87-V2-response-comparison.py --repo /path/to/nodd --output report.json
Sources are snapshotted from git-show BASE and current worktree into TemporaryDirectory;
no repository modules/build products are imported/written in place. No eta requirement
or reconstruction efficiency is inferred. This script is authored independently of run.py.
"""
from __future__ import annotations
import argparse,copy,hashlib,importlib,importlib.util,json,math,platform,subprocess,sys,tempfile,time
from pathlib import Path
import numpy as np
BASE='71406b09fa2d3fbfa119dba61e436f8fad1d11ac'
FILES=['field.py','field_backend.cpp','geometry.py','system.py','design.json','solenoid-input.json']
PREFIX='tools/toroid_prototype/'
C=.299792458

def sha(b):return hashlib.sha256(b).hexdigest()
def cmd(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def module_snapshot(repo,revision,parent,name):
 p=parent/name/'tools'/'toroid_prototype';p.mkdir(parents=True)
 (p/'__init__.py').write_text('') # synthetic package shim; source tree uses namespaces
 manifest={}
 for f in FILES:
  relative=PREFIX+f
  data=cmd(repo,'show',revision+':'+relative) if revision else (repo/relative).read_bytes()
  (p/f).write_bytes(data);manifest[relative]=sha(data)
 spec=importlib.util.spec_from_file_location(name,p/'__init__.py',submodule_search_locations=[str(p)])
 package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
 return importlib.import_module(name+'.system'),importlib.import_module(name+'.geometry'),importlib.import_module(name+'.field'),manifest

def points_and_weights(eta,phi,config,order=48):
 # Independently derive station centres from finite surfaces. Positive-eta half
 # suffices for symmetric ECTs; chamber-envelope/path masks are checked separately.
 st=config['stations'];sinh=math.sinh(eta);h=st['outline_thickness_m']/2
 u=np.array([math.cos(math.radians(phi))/math.cosh(eta),math.sin(math.radians(phi))/math.cosh(eta),math.tanh(eta)])
 distances=[];kinds=[]
 for radius,z in zip(st['barrel_radii_m'],st['disk_abs_z_m']):
  if radius*sinh<=z-st['barrel_end_shortening_m']:
   distances.append(radius*math.cosh(eta));kinds.append('B')
  else:
   rr=z/sinh
   if not st['disk_inner_radius_m']<=rr<=radius+h:return None
   distances.append(z/math.tanh(eta));kinds.append('D')
 d=np.array(distances);a,b=np.diff(d);L=a+b
 nodes,gauss=np.polynomial.legendre.leggauss(order);ss=[];weights=[]
 # Chord-minus-middle displacement is linear interpolation of endpoint
 # displacements minus middle displacement. Green kernel is positive below.
 for lo,hi,factor,increasing in [(d[0],d[1],b/L,True),(d[1],d[2],a/L,False)]:
  t=(lo+hi)/2+(hi-lo)*nodes/2
  kernel=factor*(t-d[0] if increasing else d[2]-t)
  ss.extend(t);weights.extend(gauss*(hi-lo)/2*kernel)
 return np.asarray(ss)[:,None]*u,np.array(weights),np.array([-math.sin(math.radians(phi)),math.cos(math.radians(phi)),0.]),d,kinds

def response(eta,phi,config,integral,distances,kinds):
 a,b=np.diff(distances);L=a+b
 # Project native MDT z precision in barrel/r precision in disk onto RZ normal.
 sigma=np.array([math.hypot(35.,30.)/math.cosh(eta) if k=='B' else math.hypot(35.,40.)*abs(math.tanh(eta)) for k in kinds])*1e-6
 variance=(b/L*sigma[0])**2+sigma[1]**2+(a/L*sigma[2])**2
 theta=.0136/500.*math.sqrt(1.3)*(1.+.038*math.log(1.3))
 ms=theta*a*b/(math.sqrt(3.)*L)
 signal=C*abs(integral)/500.
 return {'signed_integral_T_m2':float(integral),'signed_B_sag_T':float(2.*integral/(a*b)),
         'station_s_m':distances.tolist(),'hit_types':''.join(kinds),
         'measurement_sigma_s_m':math.sqrt(variance),'MS_sigma_s_m':float(ms),
         'measurement_fraction_500GeV':math.sqrt(variance)/signal,
         'internal_MS_fraction_500GeV':float(ms/signal),
         'proxy_fraction_500GeV':math.sqrt(variance+ms**2)/signal}

def distribution(values):
 x=np.asarray(values,float)
 return {'count':len(x),'minimum':float(x.min()),'median':float(np.median(x)),'maximum':float(x.max()),'p95':float(np.quantile(x,.95))} if len(x) else {'count':0}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True,type=Path);p.add_argument('--baseline',default=BASE);p.add_argument('--output',required=True,type=Path);p.add_argument('--threads',type=int,default=2);args=p.parse_args();start=time.time()
 baseline_results=cmd(args.repo,'show',args.baseline+':docs/validation/DES-039/results.json')
 old=json.loads(baseline_results)['configuration'];new=json.loads((args.repo/(PREFIX+'design.json')).read_bytes())
 eta_values=sorted(set(np.round(np.arange(0,3.10001,.1),9).tolist()+[1.05,1.15,1.25,1.35,1.45,1.55,1.65,1.75,2.55,2.65,2.75]+[1.0843506236,1.1281331878,1.1959930564]))
 phi_values=((np.arange(12)+.5)*2.5).tolist()
 rays=[(float(e),float(ph)) for e in eta_values for ph in phi_values]
 with tempfile.TemporaryDirectory(prefix='pr87-v2-response-') as temp:
  temp=Path(temp);modules={};manifest={};normalization={}
  for label,revision in [('before',args.baseline),('after',None)]:
   system,geometry,field,hashes=module_snapshot(args.repo,revision,temp,label)
   modules[label]=(system,geometry,field);manifest[label]=hashes
  # Normalize candidate current from both signed targets before evaluating rays.
  normalization['after']=modules['after'][0].normalize_currents(new)
  configs={'before':old,'after':new};outputs={};geometry_checks=[]
  for label in ['before','after']:
   system,geometry,field=modules[label];config=configs[label];source=system.toroid_sources(config)
   output=[];all_points=[];work=[]
   for e,ph in rays:
    geo=geometry.station_intersections(e,ph,config)
    own=points_and_weights(e,ph,config)
    if bool(own is not None)!=geo['three_hits']:raise AssertionError('independent centre-intersection mismatch')
    row={'eta':e,'phi_deg':ph,'nominal_three':geo['three_hits'],'envelope_clear':geo['three_hits'] and not geo['excluded_hits'],'interstation_clear':geo['valid'],'hit_types':geo['hit_types']}
    if own is not None:
     if not np.allclose(own[3],np.linalg.norm(geo['points_m'],axis=1),rtol=0,atol=1e-12):raise AssertionError('stationdistance mismatch')
    if geo['valid']:
     points,w,ephi,dist,kinds=own;work.append((len(output),len(all_points),len(points),w,ephi,dist,kinds));all_points.extend(points)
    output.append(row)
   fields=field.evaluate(np.array(all_points),source,backend='cpp',threads=args.threads)
   for index,offset,n,w,ephi,dist,kinds in work:
    integ=np.dot(w,fields[offset:offset+n]@ephi)
    output[index].update(response(output[index]['eta'],output[index]['phi_deg'],config,integ,dist,kinds))
   outputs[label]=output
   # A few independent ray-integration and source-discretization controls.
   fine=system.toroid_sources(config,order=6,corners=32);controls=[]
   for e,ph in [(0.,15.),(1.1,7.5),(1.5,7.5),(1.65,1.25),(2.,0.),(2.7,7.5)]:
    if not geometry.station_intersections(e,ph,config)['valid']:continue
    row={'eta':e,'phi_deg':ph};integrals=[]
    for order,src in [(48,source),(96,source),(96,fine)]:
     q,w,ep,dist,kinds=points_and_weights(e,ph,config,order)
     integral=float(np.dot(w,field.evaluate(q,src,backend='cpp',threads=args.threads)@ep));integrals.append(integral)
    row.update(integral_48_nominal_T_m2=integrals[0],integral_96_nominal_T_m2=integrals[1],integral_96_fine_source_T_m2=integrals[2],relative_ray_quadrature_change=abs(integrals[1]-integrals[0])/abs(integrals[1]),relative_source_refinement_change=abs(integrals[2]-integrals[1])/abs(integrals[2]))
    independent_proxy=response(e,ph,config,integrals[0],dist,kinds)
    row['independent_proxy_fraction_500GeV']=independent_proxy['proxy_fraction_500GeV']
    if label=='before':
     matches=[r for r in json.loads(baseline_results)['acceptance_performance_scan'] if abs(r['eta']-e)<1e-9 and abs(r['phi_deg']-ph)<1e-9 and r['clear_three_hits']]
     if matches:
      reference=matches[0]
      row['pinned_results_control']={'reference_proxy_fraction_500GeV':reference['standalone_proxy_fraction_at_500GeV'],'absolute_proxy_difference':abs(reference['standalone_proxy_fraction_at_500GeV']-independent_proxy['proxy_fraction_500GeV']),'reference_B_sag_T':reference['B_sag_T'],'absolute_B_sag_difference_T':abs(reference['B_sag_T']-independent_proxy['signed_B_sag_T'])}
    controls.append(row)
   geometry_checks.append({'case':label,'controls':controls})
  for path,digest in manifest['after'].items():
   if sha((args.repo/path).read_bytes())!=digest:raise RuntimeError('current source drift during evaluation: '+path)
  paired=[];groups={'common_clear':[],'newly_clear':[],'lost_clear':[],'neither_clear':[]}
  for a,b in zip(outputs['before'],outputs['after']):
   category='common_clear' if a['interstation_clear'] and b['interstation_clear'] else 'newly_clear' if b['interstation_clear'] else 'lost_clear' if a['interstation_clear'] else 'neither_clear'
   row={'eta':a['eta'],'phi_deg':a['phi_deg'],'category':category,'before':a,'after':b}
   if category=='common_clear':row.update(proxy_after_over_before=b['proxy_fraction_500GeV']/a['proxy_fraction_500GeV'],B_sag_after_over_before=b['signed_B_sag_T']/a['signed_B_sag_T'])
   paired.append(row);groups[category].append(row)
  summaries={}
  for category,rows in groups.items():
   d={'rays':len(rows),'fraction_of_fixed_sampled_grid':len(rows)/len(rays)}
   for label in ['before','after']:
    valid=[r for r in rows if r[label]['interstation_clear']]
    d[label]={'signed_B_sag_T':distribution([r[label]['signed_B_sag_T'] for r in valid]),'proxy_fraction_500GeV':distribution([r[label]['proxy_fraction_500GeV'] for r in valid])}
    if valid:
     worst=max(valid,key=lambda r:r[label]['proxy_fraction_500GeV']);d[label]['worst_proxy_ray']={k:worst[k] for k in ['eta','phi_deg']};d[label]['negative_signed_response_rays']=int(sum(r[label]['signed_B_sag_T']<0 for r in valid))
   if category=='common_clear':
    d['proxy_after_over_before']=distribution([r['proxy_after_over_before'] for r in rows]);d['improved_proxy_rays']=int(sum(r['proxy_after_over_before']<1 for r in rows));d['worse_proxy_rays']=int(sum(r['proxy_after_over_before']>1 for r in rows))
   summaries[category]=d
  report={'status':'INDEPENDENT READ-ONLY DRAFT CHECK; no human approval','baseline_revision':args.baseline,
   'candidate_revision':'dirty working-tree source snapshot; physical design supplied by parent; exact input hashes below',
   'worktree_HEAD':cmd(args.repo,'rev-parse','HEAD').decode().strip(),'worktree_status_at_completion':cmd(args.repo,'status','--short').decode(),
   'input_sha256':manifest|{'baseline_results_json':sha(baseline_results),'script':sha(Path(__file__).read_bytes())},
   'configurations':configs,'candidate_current_normalization':normalization['after'],
   'sampling':{'eta_values':eta_values,'phi_midpoints_deg':phi_values,'ray_count':len(rays),'interpretation':'fixed sampled grid, no eta acceptance requirement; irregular eta spacing and no production/solidangle weights; fractions are diagnostics only'},
   'proxy_definition':{'momentum_GeV':500,'chamber_resolution_um':35,'barrel_alignment_um':30,'disk_alignment_um':40,'internal_material_X0':1.3,'signed_integral':'chord-minus-middle = .299792458*q/p integral(w Bphi ds); separately Gauss48 on both unequal station intervals','B_sag':'2 integral(w Bphi ds)/((s2-s1)(s3-s2))','sources':'finite uniform current-pack4x4 Gauss filaments;16polygon segments per corner; exact straight segment vacuum field; solenoid Bphi exactly zero by axisymmetry'},
   'summaries':summaries,'independent_numeric_controls':geometry_checks,'paired_rays':paired,
   'independence':'Independent intersection/Green-kernel/proxy arithmetic and beforeafter pairing; reused implementation analytic finite-envelope/case masks and exact-segment field evaluator. Root authored current edits of existing independent-response-controls.py and independent-grid-study.py; this new script does not import them or run.py.',
   'limits':['Clear means full chamber envelopes and sampled firstlast route avoid warmcase with50mm clearance; it is not reconstruction or efficiency.','Analytic source evaluator reused; no independent field solver, steel magnetization, ECT supports/webs, material transport, eloss, curvature or background response.','Upstream IPfirst case shadows are not vetoed; uniform1.3X0 is a conditional internal-gap proxy only.','No field/performance threshold was silently relaxed; all clear rays on the fixed grid are retained even with weak or negative signed response.','Irregular eta points/midpointphi sampling and finite discretization do not establish continuous extrema/fullacceptance.','Current cold envelope in design.json is provisional and unused by these warmcase/signedresponse diagnostics; final energy-sized cold section must be reviewed with regenerated results.'],
   'runtime':{'python':platform.python_version(),'numpy':np.__version__,'threads':args.threads,'seconds':time.time()-start}}
 args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'grid':report['sampling'],'normalization':report['candidate_current_normalization'],'summaries':summaries,'numeric_controls':geometry_checks,'seconds':report['runtime']['seconds']},indent=2))
if __name__=='__main__':main()
