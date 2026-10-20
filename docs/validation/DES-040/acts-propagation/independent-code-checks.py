#!/usr/bin/env python3
"""Read-only exact-revision PhysVal probes; outputs exclusively below --work."""
from __future__ import annotations
import argparse,ast,csv,hashlib,io,json,math,subprocess,sys
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True

def digest(b):return hashlib.sha256(b).hexdigest()
def rows(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--revision',default='85b044d2a5591828efe492a651b8aee11593a42b');p.add_argument('--executable',required=True,type=Path);p.add_argument('--work',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
    def source(path):return subprocess.check_output(['git','-C',str(a.root),'show',a.revision+':'+path])
    control=json.loads(source('docs/validation/DES-040/acts-propagation/controls.json'))
    exe_sha=digest(a.executable.read_bytes());assert exe_sha==control['executable_sha256']
    geometry_raw=source('docs/validation/DES-040/geometry.json');panels=json.loads(geometry_raw)['panels']
    geom=a.work/'geometry.dat'
    with geom.open('w') as f:
        f.write(str(len(panels))+'\n')
        for panel in panels:
            values=[panel['depth_m'],*panel['origin_m'],*np.array(panel['basis']).ravel(),*np.array(panel['vertices_m']).ravel()]
            f.write(panel['id']+' '+str(panel['station'])+' '+' '.join(format(float(x),'.17g') for x in values)+'\n')
    commands=[]
    def native(name,args):
        dest=a.work/name;cmd=[str(a.executable.resolve()),'--output-dir',str(dest),*map(str,args)]
        r=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(argv=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stderr;return dest
    inspect=native('geometry',['--geometry',geom,'--field','zero','--inspect-only'])
    cr=rows(inspect/'geometry-corners.csv');fr=rows(inspect/'geometry.csv');corners={}
    for row in cr:corners.setdefault((int(row['panel_index']),int(row['face_index'])),[]).append([float(row[k+'_m']) for k in ['x','y','z']])
    ids=[];max_corner=0.;large_count=0
    for row in fr:
        j,k=int(row['panel_index']),int(row['face_index']);panel=panels[j];ids.append(int(row['geometry_id']));large_count+=int(row['is_large'])
        center=np.array([float(row[x+'_m']) for x in ['cx','cy','cz']]);normal=np.array([float(row[x]) for x in ['nx','ny','nz']]);assert abs(np.linalg.norm(normal)-1)<1e-12
        b=np.array(panel['basis']);xy=np.array(panel['vertices_m']);h=panel['depth_m']/2
        verts=np.vstack([np.c_[xy,np.full(4,w)] for w in [-h,h]])@b.T+panel['origin_m']
        dist=abs((verts-center)@normal);expected=verts[dist<1e-9];actual=np.array(corners[j,k]);assert expected.shape==actual.shape==(4,3)
        d=np.linalg.norm(expected[:,None,:]-actual[None,:,:],axis=2);res=max(d.min(0).max(),d.min(1).max());assert res<1e-9;max_corner=max(max_corner,float(res))
    assert len(fr)==9360 and len(ids)==len(set(ids)) and large_count==3120
    mapraw=source('docs/validation/DES-039/joint-field.npz');stream=io.BytesIO(mapraw)
    with np.load(stream,allow_pickle=False) as f:r,z,phi,B,valid=[f[k].copy() for k in ['r_m','z_m','phi_deg','B_total_cyl_T','valid_field']]
    mp=a.work/'map.bin'
    with mp.open('wb') as f:
        import struct
        f.write(b'NODDMAP1');f.write(struct.pack('<QQQ',len(r),len(z),len(phi)))
        for x in [r,z,phi]:f.write(x.astype('<f8').tobytes())
        f.write(B.astype('<f4').tobytes());f.write(valid.astype('u1').tobytes())
    ns={};exec(compile(source('tools/toroid_prototype/map.py').decode(),'pinned_FieldMap.py','exec'),ns)
    # Constructor reads the pinned original NPZ, retained only in the scratch work.
    npz=a.work/'joint-field.npz';npz.write_bytes(mapraw);field=ns['FieldMap'](npz)
    rng=np.random.default_rng(900531);n=1024;rad=rng.uniform(0,9.5,n);az=rng.uniform(-2*np.pi,4*np.pi,n);zz=rng.uniform(-12.5,12.5,n)
    points=np.c_[rad*np.cos(az),rad*np.sin(az),zz]
    points=np.vstack([points,[[0,0,0],[1.3,0,0],[4.35,0,6.5],[9.5,0,0],[9.50001,0,0],[0,0,-12.50001]],[[4.35*np.cos(t),4.35*np.sin(t),-.4] for t in np.deg2rad([-1e-8,0,1e-8,30-1e-8,30,30+1e-8,360])]])
    qp=a.work/'queries.dat'
    with qp.open('w') as f:f.write(str(len(points))+'\n');np.savetxt(f,points,fmt='%.17g')
    q=native('field',['--map',mp,'--query-field',qp]);qr=rows(q/'field.csv');max_field=0.;status_counts={}
    for point,row in zip(points,qr):
        try:expected=field.field(point[None,:])[0];status='valid'
        except ValueError as e:status='outside_map' if 'outside' in str(e) else 'field_masked';expected=None
        assert row['status']==status,(point,row,status);status_counts[status]=status_counts.get(status,0)+1
        actual=np.array([float(row[x+'_T']) for x in ['Bx','By','Bz']])
        if expected is None:assert np.isnan(actual).all()
        else:
            residual=float(abs(actual-expected).max());max_field=max(max_field,residual);assert residual<1e-10
    # Load exact pure counter functions without importing or executing checkout modules.
    tree=ast.parse(source('tools/muon_layout/acts/analyze.py').decode());selected=[]
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HIT_DTYPE' for t in node.targets):selected.append(node)
        if isinstance(node,ast.FunctionDef) and node.name in ['count_events','_availability']:selected.append(node)
    pure={'np':np};exec(compile(ast.Module(body=selected,type_ignores=[]),'pinned_counter_functions.py','exec'),pure)
    def counter(tangent=False,same_station=False,side_visit=False):
        cat={};ev=[]
        for panel in range(3):
            for face in [0,1]:
                cat[panel,face]=dict(plane=4+face,large=True,normal=np.array([-1 if face==0 else 1,0,0]),station=1 if same_station else panel+1)
                path=2*panel+face+1.;d=[0,1,0] if tangent else [1,0,0]
                ev.append((0,len(ev),panel,face,True,2**60+panel*10+face,path,0,0,path,*d))
        x=np.array(ev,dtype=pure['HIT_DTYPE']);return {k:int(v) for k,v in pure['count_events'](x,cat,np.ones(6,bool)).items() if k!='keep_indices'}
    nominal=counter();same=counter(same_station=True);tangent=counter(tangent=True)
    assert nominal['outer_unique_faces']==6 and nominal['outer_paired_stations']==3
    assert same['outer_unique_faces']==6 and same['outer_paired_stations']==1
    assert tangent['outer_unique_faces']==6 and tangent['outer_paired_stations']==0 and tangent['tangent_events']==6
    avail=pure['_availability'](np.array([True,False,False]),np.array([True,True,False]),np.ones(3));assert avail['proven_lower_fraction']==1/3 and avail['possible_upper_fraction']==2/3
    # Three independent uniform-field cylinder tests; roots are compared to an analytic helix.
    fixture=a.work/'cylinder-geometry.dat';fixture.write_text('1\nTEST 1 0.5 8 0 0 0 0 1 1 0 0 0 1 0 -0.5 -0.5 0.5 -0.5 0.5 0.5 -0.5 0.5\n')
    tp=a.work/'cylinder-tracks.dat';tp.write_text('3\n0 2.65 -1 4.35001 0 0 0 1 0\n1 2.65 -1 4.35001 0 0 1 0 0\n2 2.65 1 4.35001 0 0 0 1 0\n')
    cyl=native('cylinder',['--geometry',fixture,'--tracks',tp,'--field','constant','--bz','3','--max-step-m','.05','--tolerance-m','1e-8','--rk-tolerance-m','1e-11','--path-limit-m','25','--audit-roots'])
    rt=rows(cyl/'root-audit.csv');tr=rows(cyl/'tracks.csv');cyl_results=[]
    for row,track in zip(rt,tr):
        i=int(row['track_id']);s=float(row['path_m']);q=-1 if i<2 else 1;k=q*.299792458*3/2.65;d=np.array([1,0,0]) if i==1 else np.array([0,1,0]);sn,cs=np.sin(k*s),np.cos(k*s)
        expected=np.array([4.35001+d[0]*sn/k+d[1]*(1-cs)/k,d[1]*sn/k-d[0]*(1-cs)/k,0]);actual=np.array([float(row[x+'_m']) for x in ['x','y','z']]);res=float(np.linalg.norm(expected-actual));assert res<1e-6
        assert track['status']==('completed' if i==2 else 'returned_to_entrance')
        cyl_results.append(dict(track_id=i,status=track['status'],native_path_m=s,helix_position_residual_m=res,native_corrections=int(track['native_corrections'])))
    # Explicitly reproduce the pinned postprocessor's duplicate-keyword construction defect.
    try:dict(**dict(max_plane_residual_m=0),max_plane_residual_m=0)
    except TypeError as e:summary_defect=repr(e)
    report=dict(revision=a.revision,executable_sha256=exe_sha,geometry_sha256=digest(geometry_raw),map_sha256=digest(mapraw),
        native_geometry=dict(chambers=len(panels),faces=len(fr),large_faces=large_count,unique_ids=len(set(ids)),max_corner_residual_m=max_corner),
        field=dict(points=len(points),seed=900531,status_counts=status_counts,max_absolute_residual_T=max_field),
        counters=dict(nominal=nominal,same_station=same,tangent=tangent,availability=avail),cylinder_checks=cyl_results,
        target_revision_summary_defect=summary_defect,commands=commands,
        scope='Bounded geometry/provider/counter/native-cylinder review; no production coverage artifacts assessed',human_approval=False)
    a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({k:report[k] for k in ['revision','native_geometry','field','cylinder_checks','target_revision_summary_defect']},indent=2))
if __name__=='__main__':main()
