"""Reproduce DES-039 vacuum geometry, joint field map and MDT proxy observables.

Run from repository root: python3 -m tools.toroid_prototype.run
Plotting requires matplotlib. No ACTS/DD4hep/Geant4 runtime is used.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
import subprocess
import time
import numpy as np
from .system import (load_design,normalize_currents,toroid_sources,solenoid_sources,
                     solenoid_parameters,signed_response,response_points,C_LIGHT)
from .field import evaluate
from .geometry import (coil_mask,station_intersections,chamber_outline_polylines,
                       export_outlines,loop_polyline,sweep_union_volumes,analytic_sweep_union_volumes,export_vtp,outline_envelope_faces)
from .map import FieldMap
from .energy import rescale_energy

OUT=Path('docs/validation/DES-039')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def check_energy_geometry(energy,config):
    """Current scaling cannot reuse an energy matrix after a source-geometry edit."""
    reference=energy['source_configuration']
    def geometry(c):
        return {key:c[key] for key in ('folds','pack')} | {
            'coil_groups':{name:{k:v for k,v in group.items() if k!='ampere_turns_per_coil'}
                           for name,group in c['coil_groups'].items()}}
    if geometry(reference)!=geometry(config):
        raise ValueError('energy source geometry changed; rerun energy_study before current rescaling')

def central_check(toroid,solenoid):
    r=np.linspace(0,1.2,13);z=np.linspace(-3.6,3.6,49);ph=np.radians(np.arange(0,30,2.5))
    rr,zz,pp=np.meshgrid(r,z,ph,indexing='ij')
    p=np.column_stack((rr.ravel()*np.cos(pp.ravel()),rr.ravel()*np.sin(pp.ravel()),zz.ravel()))
    b=evaluate(p,toroid)+evaluate(p,solenoid)
    v=np.linalg.norm(b,axis=1);k=int(np.argmax(v))
    origin=evaluate([[0,0,0]],toroid)+evaluate([[0,0,0]],solenoid)
    return {'B_origin_cart_T':origin[0].tolist(),'sampled_tracker_max_norm_T':float(v[k]),
       'sampled_tracker_max_at_m':p[k].tolist(),'sample_count':len(p),
       'central_cap_T':5.,'passes_sampled_cap':bool(v.max()<=5),
       'scope':'complete joint vacuum field in nominal tracker R<=1.2m, |z|<=3.6m; grid, not all-space maximum'}

def performance(eta,phi,c,src):
    geo=station_intersections(float(eta),float(phi),c)
    row={'eta':float(eta),'phi_deg':float(phi),'hit_types':geo['hit_types'],'clear_three_hits':geo['valid']}
    if not geo['valid']:return row
    resp=signed_response(eta,phi,c,src)
    s=np.array(resp['stations_s_m']);a,b=np.diff(s);L=a+b
    # Native MDT z coordinate in barrel; r coordinate on disks. Project to track-normal RZ.
    sigmas=np.array([math.hypot(35,30)/math.cosh(eta) if t=='B' else
                    math.hypot(35,40)*abs(math.tanh(eta)) for t in geo['hit_types']])*1e-6
    sig_s=math.sqrt((b/L*sigmas[0])**2+sigmas[1]**2+(a/L*sigmas[2])**2)
    theta0=.0136/500*math.sqrt(1.3)*(1+.038*math.log(1.3))
    sig_ms=theta0*a*b/(math.sqrt(3)*L)
    response=C_LIGHT*abs(resp['integral_T_m2'])/500
    row.update(resp);row.update({'station_sigma_transverse_um':(sigmas*1e6).tolist(),
         'measurement_fraction_at_500GeV':sig_s/response,
         'internal_MS_fraction_at_500GeV':sig_ms/response,
         'standalone_proxy_fraction_at_500GeV':math.hypot(sig_s,sig_ms)/response})
    return row

def field_map(c,tor,sol,out):
    m=c['map'];r=np.arange(m['r_min_m'],m['r_max_m']+1e-8,m['r_step_m'])
    z=np.arange(m['z_min_m'],m['z_max_m']+1e-8,m['z_step_m'])
    ph=np.arange(m['phi_min_deg'],m['phi_max_deg']+1e-8,m['phi_step_deg'])
    rr,zz,pp=np.meshgrid(r,z,np.radians(ph),indexing='ij');shape=rr.shape
    cs,sn=np.cos(pp.ravel()),np.sin(pp.ravel())
    points=np.column_stack((rr.ravel()*cs,rr.ravel()*sn,zz.ravel()))
    def cylindrical(b):return np.column_stack((b[:,0]*cs+b[:,1]*sn,-b[:,0]*sn+b[:,1]*cs,b[:,2])).reshape(shape+(3,))
    # The physical solenoid is axisymmetric. Compute one meridional slice and rotate.
    r2,z2=np.meshgrid(r,z,indexing='ij');p2=np.column_stack((r2.ravel(),0*r2.ravel(),z2.ravel()))
    bs=evaluate(p2,sol).reshape((len(r),len(z),3));bs[:,:,1]=0
    bs=np.broadcast_to(bs[:,:,None,:],shape+(3,)).copy()
    bt=evaluate(points,tor,by_group=True)
    arrays={name:cylindrical(bt[:,k,:]) for k,name in enumerate(tor.group_names)}
    total=bs+sum(arrays.values())
    par=solenoid_parameters();dr=np.maximum.reduce([par['cold_inner_radius_m']-rr,
               rr-par['winding_outer_radius_m'],np.zeros(shape)])
    dz=np.maximum(abs(zz)-par['cold_mass_length_m']/2,0)
    valid=(np.hypot(dr,dz)>m['pack_guard_m']) & ~coil_mask(points,c,width='pack',clearance=m['pack_guard_m']).reshape(shape)
    warm=coil_mask(points,c,width='warm').reshape(shape)
    # Periodic endpoint values are identical cylindrical components by C12 symmetry.
    for array in [bs,total,*arrays.values()]:
        array[:,:,-1]=array[:,:,0]
        array[~valid]=np.nan
    payload={'r_m':r,'z_m':z,'phi_deg':ph,'valid_field':valid,'inside_toroid_warm_reservation':warm,
             'B_total_cyl_T':total.astype('f4')}
    # Fine joint grid is the deliverable; separate coarser source components
    # keep decomposition inspectable without duplicating large fine binaries.
    coarse=(slice(None,None,2),slice(None,None,2),slice(None,None,4))
    components={'r_m':r[::2],'z_m':z[::2],'phi_deg':ph[::4],
                'valid_field':valid[coarse],'B_solenoid_cyl_T':bs[coarse].astype('f4')}
    components.update({f'B_{name}_cyl_T':b[coarse].astype('f4') for name,b in arrays.items()})
    np.savez_compressed(out/'field-components.npz',**components)
    path=out/'joint-field.npz';np.savez_compressed(path,**payload)
    metadata={'status':'joint finite-coil VACUUM field, no HCAL magnetization',
      'filename':path.name,'sha256':sha(path),'contents':'combined field only; source decomposition in field-components.npz at doubled RZ / quadrupled phi spacing','shape_r_z_phi_components':list(total.shape),
      'axes_order':['r_m','z_m','phi_deg','Br_Bphi_Bz_T'],'stored_dtype':'float32 fields, float64 axes',
      'r_range_m':[float(r[0]),float(r[-1])],'z_range_m':[float(z[0]),float(z[-1])],
      'phi_range_deg':[float(ph[0]),float(ph[-1])],'spacing':[m['r_step_m'],m['z_step_m'],m['phi_step_deg']],
      'periodicity':'C12: cylindrical components repeat every30deg; rotate Br/Bphi to global Cartesian at requested phi',
      'mask':'NaN in finite current-pack plus0.10m guard; no extrapolation; warm sweep mask separate',
      'valid_nodes':int(valid.sum()),'all_nodes':int(valid.size),
      'solenoid':'axisymmetric continuous winding approximated by3radial x96axial Gauss loops,192polygon edges; B(0) normalized3T',
      'toroid':'4x4 uniform pack Gauss filaments;16segments per rounded corner; each straight segment exact',
      'query':'tools.toroid_prototype.map.FieldMap.field(points_Nx3_metres) returns Cartesian tesla; rejects invalid stencil/outside domain'}
    write_json(out/'map-metadata.json',metadata)
    return metadata

def interpolation_check(path,tor,sol,c):
    f=FieldMap(path);rng=np.random.default_rng(12086);p=[]
    # Representative clear chamber gaps; this is not a whole-domain error bound.
    for _ in range(200):
        eta=rng.uniform(-2.8,2.8);phi=rng.uniform(0,360)
        g=station_intersections(eta,phi,c)
        if not g['valid']:continue
        q,_,_,s=response_points(eta,phi,c,order=4)
        point=q[rng.integers(len(q))]
        if coil_mask([point],c,width='warm',clearance=.30)[0]:continue
        try:f.field([point])
        except ValueError:continue
        p.append(point)
    p=np.array(p);got=f.field(p);direct=evaluate(p,tor)+evaluate(p,sol)
    delta=np.linalg.norm(got-direct,axis=1)
    return {'sample_count':len(p),'max_absolute_T':float(delta.max()),'rms_absolute_T':float(np.sqrt(np.mean(delta**2))),
       'max_relative_norm':float(np.max(delta/np.linalg.norm(direct,axis=1))),
       'scope':'deterministic random clear3hit gap samples, >=0.30m outside warm reservations; not a near-coil/global bound'}

def convergence(c):
    etas=[0,1.1,1.14,1.3,2,2.8];phis=[0,7.5,15]
    probes=[(e,p) for e in etas for p in phis if station_intersections(e,p,c)['valid']]
    src=toroid_sources(c,order=4,corners=16);fine=toroid_sources(c,order=6,corners=32)
    rows=[]
    for e,p in probes:
        a=signed_response(e,p,c,src)['B_sag_T'];b=signed_response(e,p,c,fine,order=96)['B_sag_T']
        rows.append({'eta':e,'phi_deg':p,'nominal_B_sag_T':a,'fine_B_sag_T':b,'relative_change':abs(a-b)/abs(b)})
    return {'rows':rows,'maximum_relative_sagitta_change':max(r['relative_change'] for r in rows)}

def plots(out,c):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'nodd-des039'})
    outlines=chamber_outline_polylines(c,phi_step_deg=2,longitudinal_step_m=.2)
    colors={'barrel':'#c74c2c','endcap_plus':'#b1972e','endcap_minus':'#b1972e'}
    fig=plt.figure(figsize=(12,8),layout='constrained');ax=fig.add_subplot(111,projection='3d')
    for name,g in c['coil_groups'].items():
        for k in range(c['folds']):
            p=loop_polyline(g,g['phi_offset_deg']+k*30,arc_steps=20)
            ax.plot(p[:,2],p[:,0],p[:,1],color=colors[name],lw=1.15,alpha=.8)
    for st in outlines:
        seg=outline_envelope_faces(st)
        if len(seg):ax.add_collection3d(Line3DCollection(seg[:,:,[2,0,1]],colors='#258b83',linewidths=.3,alpha=.35))
    # Solenoid outer reservation outline only.
    for z in [-3.85,3.85]:
        ph=np.linspace(0,2*np.pi,120);ax.plot(0*ph+z,1.558656*np.cos(ph),1.558656*np.sin(ph),color='#7966ad',lw=1)
    ax.set(xlabel='z [m]',ylabel='x [m]',zlabel='y [m]',xlim=(-12.5,12.5),ylim=(-9.5,9.5),zlim=(-9.5,9.5))
    ax.set_box_aspect((25,19,19));ax.view_init(elev=21,azim=-57)
    ax.set_title('DES-039:12 barrel +12 toroid coils per end;3 nested chamber outlines\nCoil centre lines shown; chamber cutouts include warm reservations')
    fig.savefig(out/'geometry-3d.png',dpi=170);plt.close(fig)
    fig,(ax,xy)=plt.subplots(1,2,figsize=(13,6),layout='constrained')
    for name,g in c['coil_groups'].items():
        p=loop_polyline(g,0);ax.plot(p[:,2],p[:,0],color=colors[name],lw=2,label=name.replace('_',' '))
    for r,z in zip(c['stations']['barrel_radii_m'],c['stations']['disk_abs_z_m']):
        h=c['stations']['outline_thickness_m']/2;hz=z-c['stations']['barrel_end_shortening_m']
        ax.add_patch(plt.Rectangle((-hz,r-h),2*hz,2*h,fill=False,edgecolor='#258b83',lw=.8))
        for side in (-1,1):ax.add_patch(plt.Rectangle((side*z-h,.7),2*h,r+h-.7,fill=False,edgecolor='#258b83',lw=.8))
    ax.add_patch(plt.Rectangle((-4.4832,2.6),8.9664,4.23946-2.6,color='0.65',alpha=.4,label='HCAL envelope'))
    for z in [-6.4412,4.8832]:ax.add_patch(plt.Rectangle((z,.3),1.558,4.229-.3,color='0.65',alpha=.4))
    ax.add_patch(plt.Rectangle((-3.85,1.24),7.7,.318656,color='#7966ad',alpha=.5,label='solenoid vessel'))
    ax.set(xlabel='z [m]',ylabel='R [m]',title='Axial projection (azimuths superposed; not a slice)',xlim=(-12.5,12.5),ylim=(0,9.5));ax.legend(fontsize=8,loc='lower center')
    ph=np.linspace(0,2*np.pi,361)
    for r in c['stations']['barrel_radii_m']:xy.plot(r*np.cos(ph),r*np.sin(ph),color='#258b83',lw=.8)
    for k in range(12):
        a=k*np.pi/6;g=c['coil_groups']['barrel'];ri=g['center_r_m']-g['half_r_m'];ro=g['center_r_m']+g['half_r_m']
        xy.plot([ri*np.cos(a),ro*np.cos(a)],[ri*np.sin(a),ro*np.sin(a)],color=colors['barrel'],lw=3)
    xy.add_patch(plt.Circle((0,0),4.23946,color='0.65',alpha=.3));xy.add_patch(plt.Circle((0,0),1.558656,color='#7966ad',alpha=.4))
    xy.set(xlabel='x [m]',ylabel='y [m]',title='Axial projection of BT returns (not z=0 slice)',aspect='equal',xlim=(-9.5,9.5),ylim=(-9.5,9.5))
    fig.savefig(out/'geometry-rz-xy.png',dpi=170);plt.close(fig)
    if (out/'joint-field.npz').exists():
        with np.load(out/'joint-field.npz') as f:
            r,z=f['r_m'],f['z_m'];b=f['B_total_cyl_T']
            fig,axes=plt.subplots(2,2,figsize=(13,8),layout='constrained')
            for ax,k,title in [(axes[0,0],0,'Bφ: barrel coil plane / endcap gap,φ=0°'),(axes[0,1],int(np.argmin(abs(f['phi_deg']-15))),'Bφ: barrel gap / endcap coil plane,φ=15°')]:
                im=ax.pcolormesh(z,r,b[:,:,k,1],cmap='RdBu_r',vmin=-2.5,vmax=2.5,shading='nearest');fig.colorbar(im,ax=ax,label='T')
                ax.set(title=title,xlabel='z [m]',ylabel='R [m]')
                for ri,zi in zip(c['stations']['barrel_radii_m'],c['stations']['disk_abs_z_m']):
                    ax.plot([-zi,zi],[ri,ri],color='k',lw=.5);ax.vlines([-zi,zi],.7,ri,color='k',lw=.5)
            ax=axes[1,0];im=ax.pcolormesh(z,r,b[:,:,int(np.argmin(abs(f['phi_deg']-7.5))),2],cmap='RdBu_r',vmin=-3,vmax=3,shading='nearest');fig.colorbar(im,ax=ax,label='T');ax.set(title='Joint Bz atφ=7.5°',xlabel='z [m]',ylabel='R [m]')
            ax=axes[1,1];mid=c['stations']['barrel_radii_m'][1];i=np.argmin(abs(r-mid));j=np.argmin(abs(z));ax.plot(f['phi_deg'],b[i,j,:,1]);ax.set(xlabel='φ [degree]',ylabel='Bφ [T]',title=f'Barrel mid-span ripple,R≈{r[i]:g}m,z=0');ax.grid(alpha=.2)
            fig.suptitle('Joint3T solenoid +36 toroid coils: VACUUM field; white areas mask current packs+0.10m guard')
            fig.savefig(out/'joint-field.png',dpi=170);plt.close(fig)
    result=json.loads((out/'results.json').read_text());rows=result['acceptance_performance_scan']
    etas=np.unique([r['eta'] for r in rows]);phis=np.unique([r['phi_deg'] for r in rows])
    data=np.full((len(etas),len(phis)),np.nan);response=data.copy()
    for row in rows:
        if row['clear_three_hits']:
            i=np.searchsorted(etas,row['eta']);j=np.searchsorted(phis,row['phi_deg']);data[i,j]=100*row['standalone_proxy_fraction_at_500GeV'];response[i,j]=row['B_sag_T']
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,array,title,label in [(axes[0],response,'Signed sagitta-equivalent field','B_sag [T]'),(axes[1],data,'Standalone500GeV MDT proxy','σp/p [%]')]:
        im=ax.pcolormesh(phis,etas,array,shading='nearest',cmap='viridis');fig.colorbar(im,ax=ax,label=label);ax.set(xlabel='φ [degree]',ylabel='η',title=title)
    fig.suptitle('Clear3station trajectories only; blank=coil/case/seam/aperture exclusion\n1.3X₀ internal proxy;35μm chamber +30μm barrel /40μm disk alignment')
    fig.savefig(out/'muon-response.png',dpi=170);plt.close(fig)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=OUT);p.add_argument('--skip-map',action='store_true');p.add_argument('--skip-plots',action='store_true');p.add_argument('--plots-only',action='store_true');args=p.parse_args()
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    if args.plots_only:
        plots(out,json.loads((out/'results.json').read_text())['configuration']);return
    start=time.time();c=load_design();normalization=normalize_currents(c);src=toroid_sources(c);sol,factor=solenoid_sources()
    energy_path=out/'energy.json';cold=None
    if energy_path.exists():
        energy=json.loads(energy_path.read_text())
        check_energy_geometry(energy,c)
        # Exact energy scalar selected by the independent energy study, not map-volume energy.
        selected=rescale_energy(energy['selected'],normalization['currents_Aturn'])
        scaled_rows=[rescale_energy(row,normalization['currents_Aturn']) for row in energy['studies']]
        coupled=selected['total_energy_J']+solenoid_parameters()['stored_energy_MJ']*1e6
        operating={'status':'DRAFT / complete joint vacuum field energy',
            'raw_reference_sha256':sha(energy_path),'configuration':c,
            'method':'Exact linear vacuum current rescaling of every self/mutual coupling; fixed geometry and current-pack profile',
            'selected':selected,'scaled_convergence_rows':scaled_rows,
            'solenoid_energy_J':solenoid_parameters()['stored_energy_MJ']*1e6,
            'solenoid_toroid_mutual_energy_J':0.,
            'mutual_zero_basis':'Axisymmetric azimuthal solenoid currents vs meridional loops with paired tangential offsets; numeric bidirectional check retained in energy.json',
            'complete_coupled_energy_J':coupled}
        operating['source_configuration']={k:c[k] for k in ('folds','pack','coil_groups','field_target')}
        del operating['configuration']
        write_json(out/'operating-point-energy.json',operating)
        U=selected['total_energy_J']
        # Constant aspect ratio, global system budget. Include UNION of shared ECT supports.
        # The smaller endcap inner leg limits the adjacent-pair-only union
        # reduction. Keep a verified valid bracket; never evaluate or silently
        # extrapolate the union formula beyond its geometric guards.
        target=U/30e6;lo,hi=.06001,.133
        bracket=[]
        for area in (lo,hi):
            c['cold']={'normal_m':math.sqrt(area*.24/.35),'tangent_m':math.sqrt(area*.35/.24)}
            bracket.append(analytic_sweep_union_volumes(c,width='cold',order=128)['sum_group_union_volume_m3'])
        if not bracket[0]<=target<=bracket[1]:
            raise ValueError('cold-volume target outside verified union bracket; revise allocation geometry')
        for _ in range(17):
            area=(lo+hi)/2;c['cold']={'normal_m':math.sqrt(area*.24/.35),'tangent_m':math.sqrt(area*.35/.24)}
            v=analytic_sweep_union_volumes(c,width='cold',order=128)
            total=v['sum_group_union_volume_m3']
            if total<target:lo=area
            else:hi=area
        c['cold']={'normal_m':math.sqrt((lo+hi)/2*.24/.35),'tangent_m':math.sqrt((lo+hi)/2*.35/.24)}
        cold=analytic_sweep_union_volumes(c,width='cold',order=256)
        cold['global_toroid_target_volume_m3']=target
        cold['area_bracket_m2']=[.06001,.133]
        cold['normal_to_tangent_aspect_ratio']=.24/.35
        cold['complete_energy_J']=coupled
        cold['complete_cold_volume_m3']=cold['sum_group_union_volume_m3']+solenoid_parameters()['cold_volume_m3']
        cold['complete_energy_density_MJ_m3']=coupled/cold['complete_cold_volume_m3']/1e6
        cold['scope']='global complete vacuum coupled-system U/V rule only; no local coil stress/thermal/conductor qualification'
    rows=[performance(e,ph,c,src) for e in np.round(np.arange(0,3.051,.05),8) for ph in np.arange(0,30.01,2.5)]
    fine=[performance(float(e),float(ph),c,src) for e in np.round(np.arange(1.4,1.8001,.005),8) for ph in np.arange(0,15.001,.5)]
    good=[r for r in fine if r['clear_three_hits']]
    transition={'eta_step':.005,'phi_step_deg':.5,'eta_range':[1.4,1.8],'phi_range_deg':[0,15],
      'all_rays':len(fine),'clear_rays':len(good),
      'minimum_B_sag_ray':min(good,key=lambda r:r['B_sag_T']),
      'maximum_resolution_ray':max(good,key=lambda r:r['standalone_proxy_fraction_at_500GeV']),
      'scope':'sampled clear straight rays only; not global acceptance/efficiency or a continuum performance bound'}
    with (out/'transition-scan.csv').open('w') as f:
        f.write('eta,phi_deg,clear_three_hits,hit_types,B_sag_T,standalone_500GeV_fraction\n')
        for r in fine:
            f.write(f"{r['eta']},{r['phi_deg']},{int(r['clear_three_hits'])},{r['hit_types']},{r.get('B_sag_T','')},{r.get('standalone_proxy_fraction_at_500GeV','')}\n")
    benchmarks=[performance(e,ph,c,src) for e,ph in [(0,15),(1.10,7.5),(1.14,7.5),(2,0),(2.8,0),(-2,0)]]
    result={'status':'DRAFT / PROTOTYPE; vacuum map only; HCAL nonlinear B-H response unresolved',
       'base_revision':c['base_revision'],'configuration':c,'normalization':normalization,
       'source_sha256':{str(p):sha(p) for p in sorted(Path('tools/toroid_prototype').glob('*')) if p.suffix in ['.py','.cpp','.json']},
       'python':platform.python_version(),'numpy':np.__version__,'solenoid_polygon_normalization':factor,
       'solenoid_pinned_parameters':solenoid_parameters(),'central_field':central_check(src,sol),
       'energy_cold_volume':cold,'field_response_convergence':convergence(c),'benchmarks':benchmarks,
       'acceptance_performance_scan':rows,'fine_transition_scan':transition,'observable_assumptions':{'muon_p_at_station_GeV':500,'internal_material_X0':1.3,
          'tube_resolution_um':81.7,'fitted_chamber_coordinate_um':35,'barrel_alignment_um':30,'endcap_alignment_um':40,
          'precision_coordinates':'barrel z, disks r; projected perpendicular to initial ray in RZ; independent station errors',
          'method':'straight high-p ray, signed Bphi sagitta; unequal3station interpolation; uniform internal scattering; not a reconstruction or transport simulation',
          'upstream_material':'HCAL/ECAL/solenoid energy loss and scattering are not re-run or charged as internal curvature material; see PR86'},
       'elapsed_seconds_before_map':time.time()-start}
    write_json(out/'results.json',result);export_outlines(out/'chamber-outlines.json',c,phi_step_deg=2,longitudinal_step_m=.2)
    export_vtp(out/'geometry.vtp',c,phi_step_deg=2,longitudinal_step_m=.2)
    if not args.skip_map:
        result['map']=field_map(c,src,sol,out)
        result['interpolation_control']=interpolation_check(out/'joint-field.npz',src,sol,c)
        result['elapsed_seconds']=time.time()-start;write_json(out/'results.json',result)
    if not args.skip_plots:plots(out,c)
    print(json.dumps({'output':str(out),'currents':normalization['currents_Aturn'],'central':result['central_field'],
      'benchmarks':benchmarks,'map':result.get('map'),'interpolation':result.get('interpolation_control')},indent=2))

if __name__=='__main__':main()
