"""DES023 sampled vacuum same-pair coverage against the fixed old disc envelope."""
import argparse,gzip,json,math,sys
from pathlib import Path
import numpy as np
from model import ROOT,load,build,rings,execution,sha
sys.path.append(str(ROOT/'tools/module_layout'))
from intersections import SurfaceIndex,traversal_limit

def pair_layers(layout,hits):
 faces={}
 for i,s in hits:
  m=layout['modules'][i];faces.setdefault((m['layer_id'],m['module_id']),set()).add(m['face'])
 return {layer for (layer,mid),found in faces.items() if found=={0,1}}
def batch(c,tracks,old_datum=False):
 o=np.array([t['origin_mm'] for t in tracks]);sh=np.sinh([t['eta'] for t in tracks]);phi=np.array([t['phi'] for t in tracks]);k=np.array([-.000299792458*t['charge']*t['field_T']/t['pt_GeV'] for t in tracks]);limit=np.array([traversal_limit(t,1140,3150) for t in tracks]);hits=np.zeros((len(tracks),12),bool);ideal=np.zeros_like(hits)
 def at(z):
  s=np.divide(z-o[:,2],sh,out=np.full(len(sh),np.inf),where=sh!=0);good=(s>1e-6)&(s<=limit+1e-6);s=np.where(good,s,0);a=.5*k*s;chord=s*np.sinc(a/np.pi);x=o[:,0]+chord*np.cos(phi+a);y=o[:,1]+chord*np.sin(phi+a);return good,np.hypot(x,y),np.arctan2(y,x)
 for lid,(side,j) in enumerate((s,j) for s in (1,-1) for j in range(6)):
  z=c['old_first_z_mm'] if old_datum and j==0 else c['disc_z_mm'][j];good,rad,ang=at(side*z);ideal[:,lid]=good&(rad>=c['annulus_mm'][0])&(rad<=c['annulus_mm'][1])
  for ring in rings(c):
   n=ring['pairs']
   for parity in (0,1):
    lift=1.5*(2*(ring['ring']%2)+parity);planes=[at(side*(z+sign*(3.45+lift))) for sign in (-1,1)];nearest=np.rint(planes[0][2]*n/(2*np.pi)-.5).astype(int)
    for offset in (-2,-1,0,1,2):
     col=(nearest+offset)%n;both=col%2==parity
     for face,(ok,r,a) in enumerate(planes):
      delta=a-(col+.5)*2*np.pi/n;u=side*r*np.sin(delta);v=ring['radius_mm']-r*np.cos(delta);beta=(face-.5)*.04
      both=both&ok&(abs(u*math.cos(beta)+v*math.sin(beta))<=48+1e-6)&(abs(-u*math.sin(beta)+v*math.cos(beta))<=48+1e-6)
     hits[:,lid]|=both
 return hits,ideal

def run(out):
 c=load();l=build(c);tracks=[];fixtures=((0,1,1),(4,1,1),(4,1,-1),(4,10,1),(4,10,-1))
 for B,pt,q in fixtures:
  for z in (-150,0,150):
   for eta in np.linspace(-4,4,81):
    for phi in (np.arange(96)+.371)*2*np.pi/96:tracks.append(dict(origin_mm=[0,0,z],eta=float(eta),phi=float(phi),field_T=B,pt_GeV=pt,charge=q))
 hits,new_ideal=batch(c,tracks);old_datum_hits,denominator=batch(c,tracks,True)
 sample=[tracks[i] for i in np.linspace(0,len(tracks)-1,144,dtype=int)]+[dict(origin_mm=[1,-1,z],eta=e,phi=p,field_T=4,pt_GeV=1,charge=q) for z,e,p,q in [(150,1.3,.37,1),(-150,-1.3,1.3,-1),(0,2,2.8,-1),(0,1.5,5.4,1)]]
 fast,_=batch(c,sample);index=SurfaceIndex(l);errors=[];oldpath=ROOT/'docs/validation/DES-011-optimization/cases/p190-s680-b1-l1287.33-front_loaded-original-pockets/layout.json.gz';old=json.load(gzip.open(oldpath));old['modules']=[m for m in old['modules'] if m['subsystem']=='long_strip' and m['region']=='endcap'];oldindex=SurfaceIndex(old);comparison=[]
 for i,t in enumerate(sample):
  actual=pair_layers(l,index.hits(t,host_half_z_mm=3150));expect=set(np.flatnonzero(fast[i]).tolist())
  if actual!=expect:errors.append(dict(track=t,fast=sorted(expect),oracle=sorted(actual)))
  comparison.append(dict(track=t,old_layers=sorted(pair_layers(old,oldindex.hits(t,host_half_z_mm=3150))),new_layers=sorted(actual)))
 groups=[]
 for B,pt,q in fixtures:
  mask=np.array([t['field_T']==B and t['pt_GeV']==pt and t['charge']==q for t in tracks]);miss=denominator[mask]&~hits[mask]
  groups.append(dict(field_T=B,pt_GeV=pt,charge=q,tracks=int(mask.sum()),fixed_old_ideal_intersections=int(denominator[mask].sum()),missing_same_pair_intersections=int(miss.sum()),per_disc_missing=miss.sum(axis=0).tolist(),missing_new_datum_intersections=int((new_ideal[mask]&~hits[mask]).sum()),same_layout_old_datum_misses=int((denominator[mask]&~old_datum_hits[mask]).sum()),old_datum_tracks_losing_all_hits=int((np.any(old_datum_hits[mask],axis=1)&~np.any(hits[mask],axis=1)).sum())))
 r=dict(status='FAIL' if errors else 'PASS',scope='Software/oracle check; finite coverage and engineering acceptance separate',execution=execution(),tracks=len(tracks),eta_grid=[-4,4,.1],phi_bins=96,phi_phase=.371,luminous_z_mm=[-150,0,150],host_mm=[1140,3150],fixed_old_first_mm=1403.65,new_first_mm=1470,annulus_mm=c['annulus_mm'],producer_sha256=sha(__file__),model_sha256=sha(Path(__file__).with_name('model.py')),input_sha256=sha(Path(__file__).with_name('inputs.json')),reference_sha256=sha(oldpath),groups=groups,oracle_tracks=len(sample),oracle_errors=errors,matched_old_new_subset=comparison,coverage_gate_passed=not bool(np.any(denominator&~hits)),limitations=['Finite first-traversal vacuum helices, not continuum coverage, detector efficiency, scattering or reconstruction.','Two faces must belong to the SAME paired module.','Same-layout old-datum control isolates datum loss; immutable historical DES011 finite planes are compared on an explicit subset.','Fixed original annulus/datums prevent hiding losses by redefining acceptance.'])
 out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ('status','tracks','groups','oracle_tracks','coverage_gate_passed')},indent=2));return not errors
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();raise SystemExit(0 if run(a.output) else 1)
