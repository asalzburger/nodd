"""Exact sampled vacuum planes; a hit requires both faces of SAME pair."""
import argparse,gzip,json,math,sys
from pathlib import Path
import numpy as np
from model import ROOT,load,build,execution,sha
sys.path.insert(0,str(ROOT/'tools/module_layout'))
from intersections import SurfaceIndex,traversal_limit,ideal_layer_hits

def pair_layers(layout,hits):
 faces={}
 for i,_ in hits:
  m=layout['modules'][i];faces.setdefault((m['layer_id'],m['module_id']),set()).add(m['face'])
 return {layer for (layer,pair),found in faces.items() if found=={0,1}}
def barrel_hits(c,l,tracks):
 o=np.array([t['origin_mm'] for t in tracks]);eta=np.array([t['eta'] for t in tracks]);phi=np.array([t['phi'] for t in tracks]);k=np.array([-.000299792458*t['charge']*t['field_T']/t['pt_GeV'] for t in tracks]);lim=np.array([traversal_limit(t,1140,3300) for t in tracks]);pitch=l['row_pitch_mm'];hit=np.zeros((len(tracks),2),bool)
 for stave in l['staves']:
  r=stave['radius_mm'];alpha=stave['phi_rad']+math.radians(c['tilt_deg']);nx,ny=math.cos(alpha),math.sin(alpha)
  for parity in (0,1):
   coord=[];valid=[]
   for face in (0,1):
    w=(2*face-1)*(3.35+parity*1.5);dist=r*math.cos(math.radians(c['tilt_deg']))+w-nx*o[:,0]-ny*o[:,1]
    linear=np.divide(dist,np.cos(phi-alpha),out=np.full(len(k),np.inf),where=abs(np.cos(phi-alpha))>1e-14)
    target=k*dist+np.sin(phi-alpha);possible=abs(target)<=1;gamma=np.arcsin(np.clip(target,-1,1))
    roots=[np.divide(np.mod(np.sign(k)*(phase-phi),2*np.pi),abs(k),out=np.full(len(k),np.inf),where=abs(k)>1e-15) for phase in (alpha+gamma,alpha+math.pi-gamma)]
    roots=[np.where((root>1e-6)&(root<=lim+1e-6)&possible,root,np.inf) for root in roots]
    s=np.where(abs(k)<1e-15,linear,np.minimum(*roots));good=(s>1e-6)&(s<=lim+1e-6);s=np.where(good,s,0);a=.5*k*s;chord=s*np.sinc(a/np.pi)
    x=o[:,0]+chord*np.cos(phi+a)-stave['center_mm'][0];y=o[:,1]+chord*np.sin(phi+a)-stave['center_mm'][1];z=o[:,2]+s*np.sinh(eta)
    coord.append((-ny*x+nx*y,z));valid.append(good)
   nearest=np.rint((coord[0][1]/pitch+(c['rows']-1)/2-parity)/2).astype(int)*2+parity
   for off in (-2,0,2):
    row=nearest+off;zc=(row-(c['rows']-1)/2)*pitch;both=(row>=0)&(row<c['rows'])
    for face in (0,1):
     u,z=coord[face];beta=(face-.5)*.04;v=z-zc
     both=both&valid[face]&(abs(u*math.cos(beta)+v*math.sin(beta))<=48+1e-6)&(abs(-u*math.sin(beta)+v*math.cos(beta))<=48+1e-6)
    hit[:,stave['layer']]|=both
 return hit

def run(output):
 c=load();l=build(c);tracks=[]
 fixtures=((0,1,1),(4,1,1),(4,1,-1),(4,10,1),(4,10,-1))
 for B,pt,q in fixtures:
  for z in (-150,0,150):
   for eta in np.linspace(-4,4,81):
    for phi in (np.arange(64)+.371)*2*np.pi/64:tracks.append(dict(origin_mm=[0,0,z],eta=float(eta),phi=float(phi),field_T=B,pt_GeV=pt,charge=q))
 hits=barrel_hits(c,l,tracks)
 oldpath=ROOT/'docs/validation/DES-011-optimization/cases/p190-s680-b1-l1287.33-front_loaded-original-pockets/layout.json.gz';old=json.load(gzip.open(oldpath));old['modules']=[m for m in old['modules'] if m['subsystem']=='long_strip' and m['region']=='barrel']
 old_index=SurfaceIndex(old);index=SurfaceIndex(l)
 sample=[tracks[i] for i in np.linspace(0,len(tracks)-1,160,dtype=int)]+[dict(origin_mm=[1,-1,z],eta=e,phi=p,field_T=4,pt_GeV=1,charge=q) for z,e,p,q in [(150,1,.37,1),(-150,-1,1.3,-1),(0,0,2.8,-1),(0,.5,5.4,1)]]
 fast=barrel_hits(c,l,sample);errors=[];comparison=[]
 for i,t in enumerate(sample):
  actual=pair_layers(l,index.hits(t));expected=set(np.flatnonzero(fast[i]).tolist())
  if actual!=expected:errors.append(dict(track=t,fast=sorted(expected),oracle=sorted(actual)))
  oldhits=pair_layers(old,old_index.hits(t));comparison.append(dict(track=t,old_layers=sorted(oldhits),new_layers=sorted(actual)))
 levels=[dict(kind='cylinder',id=i,r_m=r/1000,z_min_m=-c['active_half_length_mm']/1000,z_max_m=c['active_half_length_mm']/1000) for i,r in enumerate(c['radii_mm'])]
 ideal=np.zeros_like(hits)
 for j,t in enumerate(tracks):
  for i in ideal_layer_hits(levels,t):ideal[j,i]=True
 groups=[]
 for B,pt,q in fixtures:
  mask=np.array([t['field_T']==B and t['pt_GeV']==pt and t['charge']==q for t in tracks]);miss=ideal[mask]&~hits[mask]
  groups.append(dict(field_T=B,pt_GeV=pt,charge=q,tracks=int(mask.sum()),ideal_crossings=int(ideal[mask].sum()),missing_same_pair_crossings=int(miss.sum()),per_layer_missed=miss.sum(axis=0).tolist()))
 result=dict(status='FAIL' if errors else 'PASS',scope='Plane/oracle software check; coverage acceptance separate',execution=execution(),producer_sha256=sha(__file__),model_sha256=sha(Path(__file__).with_name('model.py')),oracle_sha256=sha(ROOT/'tools/module_layout/intersections.py'),input_sha256=sha(Path(__file__).with_name('inputs.json')),fixed_reference_sha256=sha(oldpath),tracks=len(tracks),eta_grid=[-4,4,.1],phi_bins=64,phi_phase=.371,luminous_z_mm=[-150,0,150],host_mm=[1140,3300],groups=groups,oracle_tracks=len(sample),oracle_errors=errors,matched_old_new_sample=comparison,coverage_gate_passed=not bool(np.any(ideal&~hits)),limitations=['Finite sampled first traversal in vacuum, not continuum coverage proof.','Both faces of the same pair are necessary; separate neighbouring face hits never make a pair.','Old native model did not contain a qualified cooled stave; immutable DES-011 finite planes are compared on the explicit matched subset.','No reconstruction conversion, material interactions, sensor inefficiency, calibrated resolution, occupancy or electronics qualification.'])
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('status','tracks','groups','oracle_tracks','coverage_gate_passed')},indent=2));return not errors
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();raise SystemExit(0 if run(a.output) else 1)
