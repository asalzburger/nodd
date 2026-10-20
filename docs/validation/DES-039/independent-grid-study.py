"""Independent local eight-corner refinement control, no exported-map dependency.

Reproduce from any directory with Python and NumPy; the checked-in field backend
compiles locally if needed. Writes only the paired JSON report next to this file.
Probe sampling is finite and does not establish a global field-error bound.
"""
from pathlib import Path
import math,json,sys,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.toroid_prototype.system import toroid_sources,solenoid_sources
from tools.toroid_prototype.geometry import station_intersections,coil_mask
from tools.toroid_prototype.field import evaluate
from tools.toroid_prototype.map import FieldMap
configuration_path=ROOT/'docs/validation/DES-039/results.json'
configuration_bytes=configuration_path.read_bytes()
c=json.loads(configuration_bytes)['configuration']
source=toroid_sources(c);sol,_=solenoid_sources()
rng=np.random.default_rng(39086);points=[];labels=[]
for _ in range(3000):
 eta=rng.uniform(-3,3);phi=rng.uniform(-720,720);g=station_intersections(eta,phi,c)
 if not g['valid']:continue
 lo,hi=np.asarray(g['points_m'])[[0,-1]];fraction=rng.uniform(0,1)
 points.append(lo+fraction*(hi-lo));labels.append([eta,phi,fraction])
# Controlled low-field transition probes and historical broad-check maximum.
for eta in np.arange(1.4,1.801,.025):
 for phi in np.arange(0,30.01,2.5):
  g=station_intersections(eta,phi,c)
  if not g['valid']:continue
  lo,hi=np.asarray(g['points_m'])[[0,-1]]
  for fraction in [.1,.5,.9]:
   points.append(lo+fraction*(hi-lo));labels.append([float(eta),float(phi),fraction])
points.append([-1.854189528974189,7.366067631157076,-6.5099554169045595]);labels.append(['historical_worst',None,None])
p=np.array(points);r=np.hypot(p[:,0],p[:,1]);phi=np.degrees(np.arctan2(p[:,1],p[:,0]));q=np.column_stack((r,p[:,2],phi%30))
def cylindrical(points):
 rad=np.hypot(points[:,0],points[:,1]); ph=np.arctan2(points[:,1],points[:,0]);co=np.cos(ph);si=np.sin(ph)
 tor=evaluate(points,source);tor=np.column_stack((tor[:,0]*co+tor[:,1]*si,-tor[:,0]*si+tor[:,1]*co,tor[:,2]))
 meridian=evaluate(np.column_stack((rad,np.zeros(len(points)),points[:,2])),sol);meridian[:,1]=0
 return tor+meridian
truth=cylindrical(p);reports=[];retained=[];errors=[]
for dr,dph in [(.125,2.5),(.125,1.25),(.0625,1.25),(.0625,.625)]:
 steps=np.array([dr,dr,dph]);origin=np.array([0.,-12.5,0.]);indices=np.floor((q-origin)/steps);frac=(q-origin)/steps-indices
 corners=[];weights=[]
 for a in [0,1]:
  for b in [0,1]:
   for d in [0,1]:
    cor=origin+(indices+[a,b,d])*steps;angle=np.radians(cor[:,2]);corners.append(np.column_stack((cor[:,0]*np.cos(angle),cor[:,0]*np.sin(angle),cor[:,1])))
    weights.append((frac[:,0] if a else 1-frac[:,0])*(frac[:,1] if b else 1-frac[:,1])*(frac[:,2] if d else 1-frac[:,2]))
 corners=np.array(corners);valid=~coil_mask(corners.reshape(-1,3),c,width='pack',clearance=.1).reshape(8,-1).any(axis=0)
 values=cylindrical(corners.reshape(-1,3)).reshape(8,len(p),3)
 interp=np.einsum('kn,kni->ni',np.array(weights),values)
 delta=np.linalg.norm(interp-truth,axis=1);relative=delta/np.linalg.norm(truth,axis=1)
 k=int(np.argmax(np.where(valid,delta,-1)));kr=int(np.argmax(np.where(valid,relative,-1)))
 reports.append({'r_z_step_m':dr,'phi_step_deg':dph,'candidate_points':len(p),'valid_stencils':int(valid.sum()),'masked_stencils':int((~valid).sum()),'rms_absolute_T':float(np.sqrt(np.mean(delta[valid]**2))),'max_absolute_T':float(delta[k]),'max_relative_norm':float(relative[kr]),'worst_absolute_point_m':p[k].tolist(),'worst_absolute_ray_eta_phi_fraction':labels[k],'worst_relative_point_m':p[kr].tolist(),'max_absolute_component_error_T':np.max(np.abs(interp[valid]-truth[valid]),axis=0).tolist(),'absolute_percentiles_T':{str(x):float(np.percentile(delta[valid],x)) for x in [50,90,95,99]}})
 retained.append(valid);errors.append(delta)
# Verify the saved fine grid and reader reproduce independently evaluated corners.
selected_path=ROOT/'docs/validation/DES-039/joint-field.npz'
selected_reader=FieldMap(selected_path)
assert np.isclose(selected_reader.r[1]-selected_reader.r[0],.0625)
assert np.isclose(selected_reader.phi[1]-selected_reader.phi[0],.625)
selected_points=p[valid]
loaded_cart=selected_reader.field(selected_points)
angle=np.arctan2(selected_points[:,1],selected_points[:,0]);co=np.cos(angle);si=np.sin(angle)
loaded=np.column_stack((loaded_cart[:,0]*co+loaded_cart[:,1]*si,-loaded_cart[:,0]*si+loaded_cart[:,1]*co,loaded_cart[:,2]))
serialization_delta=np.linalg.norm(loaded-interp[valid],axis=1)
assert serialization_delta.max()<2e-6,serialization_delta.max()
loaded_error=np.linalg.norm(loaded-truth[valid],axis=1)
selected_sha=hashlib.sha256(selected_path.read_bytes()).hexdigest()
metadata_path=ROOT/'docs/validation/DES-039/map-metadata.json'
assert json.loads(metadata_path.read_text())['sha256']==selected_sha
serialized_check={'filename':'joint-field.npz','sha256':selected_sha,'metadata_hash_matches':True,'candidate_points':len(p),'sample_count':len(selected_points),'masked_stencils':int((~valid).sum()),'max_difference_from_independent_local_eight_corner_T':float(serialization_delta.max()),'max_absolute_error_against_direct_T':float(loaded_error.max()),'rms_absolute_error_against_direct_T':float(np.sqrt(np.mean(loaded_error**2))),'maximum_relative_norm_error_against_direct':float(np.max(loaded_error/np.linalg.norm(truth[valid],axis=1)))}
common=np.logical_and.reduce(retained)
for row,error in zip(reports,errors):row['common_stencil_points']=int(common.sum());row['common_stencil_max_absolute_T']=float(error[common].max());row['common_stencil_rms_absolute_T']=float(np.sqrt(np.mean(error[common]**2)))
report={'status':'Independent local direct-eight-corner grid refinement diagnostic for final1.6Tendcap vacuum source; no extra warm-distance filter','normalization_Aturn':{k:v['ampere_turns_per_coil'] for k,v in c['coil_groups'].items()},'probe_generation':'3000deterministicrandomrays, uniformlyrandomfractionbetween actualclear3stationcrossings, pluseta1.4–1.8phi0–30fractions.1/.5/.9 and historicalworstpoint; sourcepackguardstencilsrejected','seed':39086,'studies':reports,'selected_grid':{'r_z_step_m':.0625,'phi_step_deg':.625},'serialized_selected_map_check':serialized_check,'input_sha256':{**{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'tools/toroid_prototype'/x for x in ['system.py','field.py','field_backend.cpp','geometry.py','solenoid-input.json','map.py']]},str(configuration_path.relative_to(ROOT)):hashlib.sha256(configuration_bytes).hexdigest()},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reproduction_command':'python3 docs/validation/DES-039/independent-grid-study.py','limits':['Finite deterministic sampling is not a global interpolation bound.','Compared to the same source-pack4x4/corner16 and solenoid3x96/polygon192 source approximations.','Test uses analytic meridional rotation for axisymmetric solenoid, matching exportedmap convention.']}
Path(__file__).with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'output':str(Path(__file__).with_suffix('.json')),'probe_count':len(p),'serialized_selected_map_check':serialized_check,'studies':[{'r_z_step_m':r['r_z_step_m'],'phi_step_deg':r['phi_step_deg'],'max_absolute_T':r['max_absolute_T'],'rms_absolute_T':r['rms_absolute_T'],'max_relative_norm':r['max_relative_norm']} for r in reports]},indent=2))
