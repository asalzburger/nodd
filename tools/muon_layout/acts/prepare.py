"""Prepare exact DES040 prisms, immutable field bytes and common entrance seeds."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.toroid_prototype.map import FieldMap


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data):Path(path).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def configuration():
    c=json.loads((Path(__file__).parent/'config.json').read_text())
    for key in ('geometry','map'):
        if sha(ROOT/c[key])!=c[key+'_sha256']:raise ValueError('fixed input changed: '+key)
    return c


def export_geometry(c,path):
    panels=json.loads((ROOT/c['geometry']).read_text())['panels']
    with Path(path).open('w') as f:
        f.write(str(len(panels))+'\n')
        for p in panels:
            values=[p['depth_m'],*p['origin_m'],*np.asarray(p['basis']).ravel(),*np.asarray(p['vertices_m']).ravel()]
            f.write(p['id']+' '+str(p['station'])+' '+' '.join(format(float(x),'.17g') for x in values)+'\n')
    return panels


def export_map(c,path):
    with np.load(ROOT/c['map'],allow_pickle=False) as f,Path(path).open('wb') as out:
        r,z,phi=(f[k] for k in ('r_m','z_m','phi_deg'))
        out.write(b'NODDMAP1');out.write(struct.pack('<QQQ',len(r),len(z),len(phi)))
        for values in (r,z,phi):out.write(values.astype('<f8').tobytes(order='C'))
        out.write(f['B_total_cyl_T'].astype('<f4').tobytes(order='C'))
        out.write(f['valid_field'].astype('u1').tobytes(order='C'))


def entrance(directions,c):
    d=np.asarray(directions);R,H=c['radius_m'],c['half_z_m']
    transverse=np.linalg.norm(d[:,:2],axis=1)
    barrel=np.divide(R,transverse,out=np.full(len(d),np.inf),where=transverse>0)
    cap=np.divide(H,abs(d[:,2]),out=np.full(len(d),np.inf),where=abs(d[:,2])>0)
    distance=np.minimum(barrel,cap)
    kind=np.where(barrel<=cap,0,np.where(d[:,2]>0,1,2)).astype('i1')
    return distance[:,None]*d,(distance+c['forward_offset_m'])[:,None]*d,kind


def directions(c):
    rng=np.random.default_rng(c['seed']);grid=c['map_grid'];ne,nf=grid['eta_bins'],grid['phi_bins']
    ee=np.linspace(grid['eta_min'],grid['eta_max'],ne+1);pe=np.linspace(0,360,nf+1)
    eb,pb=np.meshgrid(np.arange(ne),np.arange(nf),indexing='ij');eb,pb=eb.ravel(),pb.ravel()
    # Uniform solid angle *within* each eta/phi image cell, with explicit weights.
    mu=rng.uniform(np.tanh(ee[eb]),np.tanh(ee[eb+1]));phi=rng.uniform(pe[pb],pe[pb+1])
    weight=(np.tanh(ee[eb+1])-np.tanh(ee[eb]))*2*np.pi/nf
    count=c['full_sphere_directions']
    mu=np.r_[mu,rng.uniform(-1,1,count)];phi=np.r_[phi,rng.uniform(0,360,count)]
    sample=np.r_[np.zeros(len(eb),'i1'),np.ones(count,'i1')]
    weight=np.r_[weight,np.full(count,4*np.pi/count)]
    eb=np.r_[eb,np.full(count,-1)];pb=np.r_[pb,np.full(count,-1)]
    r=np.sqrt(1-mu*mu);angle=np.radians(phi);d=np.column_stack((r*np.cos(angle),r*np.sin(angle),mu))
    surface,start,kind=entrance(d,c['entrance'])
    return dict(direction=d,entrance_position_m=surface,start_m=start,entrance_kind=kind,
                eta_pos=np.arctanh(mu),phi_pos_deg=phi,eta_bin=eb,phi_bin=pb,sample=sample,
                solid_angle_weight_sr=weight,eta_edges=ee,phi_edges_deg=pe)


def tracks(c):
    seeds=directions(c);N=len(seeds['direction']);result={}
    cases=[(p,q) for p in c['momentum_GeV'] for q in c['charge_e']]
    for key in ['direction','entrance_position_m','start_m','entrance_kind','eta_pos','phi_pos_deg','eta_bin','phi_bin','sample','solid_angle_weight_sr']:
        result[key]=np.concatenate([seeds[key] for _ in cases],axis=0)
    result['direction_id']=np.tile(np.arange(N),len(cases));result['track_id']=np.arange(N*len(cases))
    result['momentum_GeV']=np.repeat([p for p,_ in cases],N);result['charge']=np.repeat([q for _,q in cases],N)
    result['eta_edges']=seeds['eta_edges'];result['phi_edges_deg']=seeds['phi_edges_deg']
    return result


def write_tracks(path,data,indices=None):
    ids=np.arange(len(data['track_id'])) if indices is None else np.asarray(indices,int)
    with Path(path).open('w') as f:
        f.write(str(len(ids))+'\n')
        for i in ids:
            values=[data['momentum_GeV'][i],data['charge'][i],*data['start_m'][i],*data['direction'][i]]
            f.write(str(data['track_id'][i])+' '+' '.join(format(float(x),'.17g') for x in values)+'\n')


def field_queries(c,work):
    rng=np.random.default_rng(90400);N=4096
    r=rng.uniform(0,9.5,N);z=rng.uniform(-12.5,12.5,N);a=rng.uniform(-4*np.pi,4*np.pi,N)
    p=np.column_stack((r*np.cos(a),r*np.sin(a),z))
    # Exact axis/seam/domain boundaries and intentional failures.
    p=np.vstack((p,[[0,0,0],[4.35,0,0],[9.5,0,0],[0,0,12.5],[9.501,0,0],[0,0,12.501],[1.4,0,0]],
                 [[4.35*np.cos(x),4.35*np.sin(x),.3] for x in np.radians([-.000001,0,.000001,29.999999,30,30.000001,359.999999,360])]))
    field=FieldMap(ROOT/c['map']);expected=np.full_like(p,np.nan);status=[]
    for k,point in enumerate(p):
        try:expected[k]=field.field(point[None,:])[0];status.append('ok')
        except ValueError as error:status.append('outside_map' if 'outside' in str(error) else 'field_masked')
    with (work/'query-points.dat').open('w') as f:
        f.write(str(len(p))+'\n');np.savetxt(f,p,fmt='%.17g')
    np.savez_compressed(work/'query-reference.npz',position_m=p,field_T=expected,status=np.array(status))


def prepare(work):
    c=configuration();work=Path(work);work.mkdir(parents=True,exist_ok=True)
    panels=export_geometry(c,work/'geometry.dat');export_map(c,work/'map.bin')
    data=tracks(c);write_tracks(work/'tracks.dat',data);np.savez_compressed(work/'primaries.npz',**data)
    # Same directions at all momenta/charges; bounded native controls use IDs.
    per_case=len(data['track_id'])//(len(c['momentum_GeV'])*len(c['charge_e']))
    chosen=np.arange(0,len(data['track_id']),max(1,per_case//20))
    write_tracks(work/'smoke-tracks.dat',data,chosen[:40])
    case_count=len(c['momentum_GeV'])*len(c['charge_e'])
    control=np.concatenate([k*per_case+np.linspace(0,per_case-1,80,dtype=int) for k in range(case_count)])
    write_tracks(work/'control-tracks.dat',data,control)
    # Small exhaustive case covers both caps/barrel and all five momenta/charges.
    exhaustive=np.concatenate([np.arange(k*per_case,k*per_case+per_case,max(1,per_case//4))[:4] for k in range(case_count)])
    write_tracks(work/'exhaustive-tracks.dat',data,exhaustive)
    field_queries(c,work)
    save(work/'inputs.json',dict(configuration=c,panels=len(panels),tracks=len(data['track_id']),
             files={name:sha(work/name) for name in ['geometry.dat','map.bin','tracks.dat','primaries.npz','query-points.dat','query-reference.npz']}))
    print(json.dumps(dict(work=str(work),panels=len(panels),tracks=len(data['track_id'])),indent=2))
    return c,data


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);a=p.parse_args();prepare(a.work)
