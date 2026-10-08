#!/usr/bin/env python3
"""Finite-plane coverage in vacuum; fixed old annulus/datums are the denominator."""
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np
from model import ROOT,load,build,rings,execution,sha
sys.path.insert(0,str(ROOT/'tools/module_layout'))
from intersections import SurfaceIndex,positions,traversal_limit


def batch_hits(c,tracks,old=False):
    """Exact z-plane intersections. Three nearest azimuth centres cover the
    rectangular tangential interval (<one pitch on either side at every ring).
    Evaluate each elevation first; never approximate a curved track at a datum.
    """
    origins=np.array([t['origin_mm'] for t in tracks]);eta=np.array([t['eta'] for t in tracks]);phi=np.array([t['phi'] for t in tracks])
    k=np.array([-.000299792458*t['charge']*t['field_T']/t['pt_GeV'] for t in tracks]);sh=np.sinh(eta)
    limits=np.array([traversal_limit(t,800,3300) for t in tracks]);hits=np.zeros((len(tracks),12),bool);ideal=np.zeros_like(hits)
    def point(z):
        s=np.divide(z-origins[:,2],sh,out=np.full(len(tracks),np.inf),where=sh!=0)
        good=(s>0)&(s<=limits);s=np.where(good,s,0);a=.5*k*s;chord=s*np.sinc(a/np.pi)
        x=origins[:,0]+chord*np.cos(phi+a);y=origins[:,1]+chord*np.sin(phi+a)
        return good,np.hypot(x,y),np.arctan2(y,x)
    for lid,(side,station) in enumerate((s,j) for s in (1,-1) for j in range(6)):
        z=c['disc_z_mm'][station]
        if old and station==0:z=c['old_first_z_mm']
        good,rad,_=point(side*z);ideal[:,lid]=good&(rad>=c['annulus_mm'][0])&(rad<=c['annulus_mm'][1])
        for r in rings(c):
            n=r['modules'];per=r['modules_per_petal'];base=(r['ring']%2)*c['ring_lift_mm']
            for parity in (0,1):
                good,rad,angle=point(side*(z+base+parity*c['phi_lift_mm']))
                angle*=side
                nearest=np.rint(angle*n/(2*np.pi)-.5).astype(int)
                for offset in (-1,0,1):
                    idx=(nearest+offset)%n;delta=angle-(idx+.5)*2*np.pi/n
                    u=rad*np.sin(delta);v=r['radius_mm']-rad*np.cos(delta)
                    hits[:,lid]|=good&(idx%2==parity)&(abs(u)<=24+1e-6)&(abs(v)<=48+1e-6)
    return hits,ideal


def run(out):
    c=load();l=build(c);tracks=[]
    for field,pt,charge in ((0,1,1),(4,1,1),(4,1,-1),(4,10,1),(4,10,-1)):
        for z0 in (-150,0,150):
            for eta in np.linspace(-4,4,81):
                for phi in np.arange(96)*2*np.pi/96:
                    tracks.append(dict(origin_mm=[0,0,z0],eta=float(eta),phi=float(phi),pt_GeV=pt,field_T=field,charge=charge))
    hits,nominal=batch_hits(c,tracks);oldhits,oldnom=batch_hits(c,tracks,True)
    # Independent broad-phase / finite-plane solver; include off-axis origins.
    sample=[tracks[i] for i in np.linspace(0,len(tracks)-1,60,dtype=int)]
    sample += [dict(origin_mm=[1,-1,z],eta=e,phi=p,pt_GeV=1,field_T=4,charge=q) for z,e,p,q in [(150,2.2,.37,1),(-150,-2.2,1.3,-1),(0,1.5,2.8,-1),(0,3,5.4,1)]]
    exact,_=batch_hits(c,sample);index=SurfaceIndex(l);errors=[]
    for i,t in enumerate(sample):
        rows=index.hits(t,host_radius_mm=800,host_half_z_mm=3300)
        actual={l['modules'][h[0]]['layer'] for h in rows}
        expect=set(np.flatnonzero(exact[i]).tolist())
        if actual!=expect:errors.append(dict(track=t,fast=sorted(expect),oracle=sorted(actual)))
    groups=[]
    for field,pt,charge in ((0,1,1),(4,1,1),(4,1,-1),(4,10,1),(4,10,-1)):
        selected=np.array([t['field_T']==field and t['pt_GeV']==pt and t['charge']==charge for t in tracks])
        denominator=oldnom[selected]
        missed=denominator&~hits[selected];oldmiss=denominator&~oldhits[selected]
        groups.append(dict(field_T=field,pt_GeV=pt,charge=charge,tracks=int(selected.sum()),
            fixed_old_ideal_disc_intersections=int(denominator.sum()),missing_active_disc_intersections=int(missed.sum()),
            missing_old_datum_active_intersections=int(oldmiss.sum()),
            per_disc_missing=missed.sum(axis=0).tolist(),
            tracks_with_any_strip_disc_hit=int(np.any(hits[selected],axis=1).sum()),
            old_tracks_with_any_strip_disc_hit=int(np.any(oldhits[selected],axis=1).sum()),
            tracks_losing_all_strip_disc_hits=int((np.any(oldhits[selected],axis=1)&~np.any(hits[selected],axis=1)).sum()),
            tracks_gaining_any_strip_disc_hit=int((~np.any(oldhits[selected],axis=1)&np.any(hits[selected],axis=1)).sum()),
            any_active_hit_fraction=float(np.any(hits[selected],axis=1).mean()),
            misses_new_nominal_annuli=int((nominal[selected]&~hits[selected]).sum()),
            shifted_first_disc_old_intersection_lost=int((denominator[:,[0,6]]&~hits[selected][:,[0,6]]&oldhits[selected][:,[0,6]]).sum())))
    hist=[]
    for eta in np.linspace(-4,4,81):
        sel=np.array([abs(t['eta']-eta)<1e-8 for t in tracks])
        hist.append(dict(eta=float(eta),tracks=int(sel.sum()),mean_active_discs=float(hits[sel].sum(axis=1).mean()),
            missing_old_ideal_disc_intersections=int((oldnom[sel]&~hits[sel]).sum())))
    failures=np.flatnonzero(np.any(oldnom&~hits,axis=1))
    result=dict(status='PASS' if not errors else 'FAIL',scope='Software/oracle check, not coverage acceptance',execution=execution(),tracks=len(tracks),
        denominator='Original annulus and original first datum1295.5mm, first host traversal r800/|z|3300mm',
        eta_grid=[-4,4,.1],phi_bins=96,luminous_z_mm=[-150,0,150],oracle_tracks=len(sample),oracle_errors=errors,groups=groups,eta_histogram=hist,
        coverage_gate_passed=not len(failures),examples=[dict(track=tracks[int(i)],missing_discs=np.flatnonzero(oldnom[i]&~hits[i]).tolist()) for i in failures[:20]],
        limitations=['Finite sampled vacuum helices, no scattering/energy loss or detector inefficiency.',
        'Endcap-only disc coverage; barrel and pixel coverage are separate and cannot be inferred from these counts.',
        'The fixed original denominator prevents hiding first-disc losses by redefining acceptance.'])
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','tracks','oracle_tracks','coverage_gate_passed')}))
    return not errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'build/short-strip-endcap/coverage.json');a=p.parse_args();raise SystemExit(0 if run(a.output) else 1)
