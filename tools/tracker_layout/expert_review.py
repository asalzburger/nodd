#!/usr/bin/env python3
"""DES-006 R-C09 PROTOTYPE: bounded A/C1 geometry and covariance search.

No production geometry, fit acceptance, IdRes or installed-material claim.
"""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import numpy as np
from inclined_study import crossings, summarize, area_ledger, validate_ring
from study import KAPPA

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/design/DES-006-inclined-split-layouts.json'
OUT = ROOT / 'docs/validation/DES-006-expert-optimisation.json'
GEOM = ROOT / 'docs/design/DES-006-reviewed-layouts.json'


def covariance(hits, eta, pt, field=3., material_scale=1., beam_x0=0.):
    """Straight-reference GLS; independent transverse and meridional projections.

    Thin scatterers act after each measurement. theta_phi=theta0*cosh(eta),
    theta_cot=theta0*cosh(eta)^2, p=pt*cosh(eta). beta=1; leading PDG term.
    beam_x0 is normal X/X0 (fraction), at the 25 mm exclusion fixture.
    """
    if pt <= 0 or not math.isfinite(pt) or field == 0 or not math.isfinite(field):
        raise ValueError('Positive finite pT and nonzero finite field required')
    if material_scale < 0 or beam_x0 < 0:
        raise ValueError('Negative material')
    r = np.array([h[0] for _, h in hits])
    if len(r) < 3:
        raise ValueError('Too few hits')
    sigma = np.array([l['sigma_rphi_m'] for l, _ in hits])
    second = []
    sh, ch = math.sinh(eta), math.cosh(eta)
    for layer, _ in hits:
        if layer['kind'] == 'cylinder':
            projection = 1.
        elif layer['kind'] == 'disc':
            projection = abs(sh)
        else:
            projection = abs(layer['normal_r'] + layer['normal_z']*sh)
        second.append(layer['sigma_second_m']*projection)
    noise = np.array([h[3]/100 * material_scale for _, h in hits])
    arms = np.maximum(r[:, None] - r[None, :], 0.)
    process = (arms * noise) @ arms.T * (.0136 / pt)**2
    if beam_x0:
        lever = np.maximum(r-.025, 0.)
        process += np.outer(lever, lever)*(.0136/pt)**2*beam_x0*ch*material_scale
    vy = np.diag(sigma**2) + process
    vz = np.diag(np.square(second)) + process*ch**2
    hy = np.column_stack((np.ones(len(r)), r, .5*r**2))
    hz = hy[:, :2]
    def solve(h, v):
        whitened = np.linalg.solve(np.linalg.cholesky(v), h)
        _, singular, rotation = np.linalg.svd(whitened, full_matrices=False)
        if singular[-1] < singular[0]*1e-12:
            raise ValueError('Rank deficient covariance')
        return (rotation.T / singular**2) @ rotation
    cy, cz = solve(hy, vy), solve(hz, vz)
    return dict(sigma_d0_um=float(np.sqrt(cy[0, 0])*1e6),
                sigma_phi_rad=float(np.sqrt(cy[1, 1])),
                sigma_qpt_per_GeV=float(np.sqrt(cy[2, 2])/(KAPPA*abs(field))),
                sigma_z0_um=float(np.sqrt(cz[0, 0])*1e6),
                sigma_cot_theta=float(np.sqrt(cz[1, 1])))


def segments(candidate):
    result=[]
    for l in candidate['layers']:
        if l['kind']=='cylinder':
            a,b=(l['r_m'],l['z_min_m']),(l['r_m'],l['z_max_m'])
        elif l['kind']=='disc':
            a,b=(l['r_min_m'],l['z_m']),(l['r_max_m'],l['z_m'])
        else:
            a,b=(l['r1_m'],l['z1_m']),(l['r2_m'],l['z2_m'])
        result.append((l,a,b))
    return result


def intersect(a,b,c,d):
    def orient(p,q,r): return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    eps=1e-12
    if max(min(a[0],b[0]),min(c[0],d[0])) > min(max(a[0],b[0]),max(c[0],d[0]))+eps: return False
    if max(min(a[1],b[1]),min(c[1],d[1])) > min(max(a[1],b[1]),max(c[1],d[1]))+eps: return False
    return orient(a,b,c)*orient(a,b,d)<=eps**2 and orient(c,d,a)*orient(c,d,b)<=eps**2


def geometry_errors(candidate):
    result=[]
    seg=segments(candidate)
    for l,a,b in seg:
        if min(a[0],b[0])<.030-1e-12 or max(a[0],b[0])>1.14 or max(abs(a[1]),abs(b[1]))>3.15:
            result.append('host/exclusion:'+l['id'])
        if l['kind']=='inclined_ring':
            validate_ring(l,dict(r_min_m=.025,r_max_m=1.14,abs_z_max_m=3.15))
            if min(a[0],b[0])<.205 or max(a[0],b[0])>.72:
                result.append('short-strip row allocation:'+l['id'])
    for (la,a,b),(lb,c,d) in itertools.combinations(seg,2):
        if intersect(a,b,c,d): result.append('intersection:'+la['id']+':'+lb['id'])
    return result


def modify(candidate, changes):
    result=copy.deepcopy(candidate)
    for l in result['layers']:
        name=l['id'].split('-',1)[1]
        for key, value in changes.items():
            if key=='pixel_disk_rmax' and l['kind']=='disc' and l['subsystem']=='pixel': l['r_max_m']=value
            elif key=='short_disk_rmin' and l['kind']=='disc' and l['subsystem']=='short_strip': l['r_min_m']=value
            elif key=='long_disk_rmin' and l['kind']=='disc' and l['subsystem']=='long_strip': l['r_min_m']=value
            elif key=='long_half' and l['kind']=='cylinder' and l['subsystem']=='long_strip': l['z_min_m'],l['z_max_m']=-value,value
            elif key.endswith('_r') and name==key[:-2] and l['kind']=='cylinder': l['r_m']=value
    return result


def disk_z(candidate, subsystem, number, z):
    result=copy.deepcopy(candidate)
    for l in result['layers']:
        if l['kind']=='disc' and l['subsystem']==subsystem and l['id'].split('-')[-1] in [f'P{number}',f'N{number}']:
            l['z_m']=math.copysign(z,l['z_m'])
    return result


def rows_from(a, mode='eta', shift=0., margin=.005):
    result=copy.deepcopy(a); result['id']='C1'; result['name']='Short-strip inclined, expert-review iteration'
    layers=[]
    for orig in result['layers']:
        l=copy.deepcopy(orig); l['id']=l['id'].replace('A-','C1-',1); l['station_group']=l['id']
        if l['kind']!='cylinder' or l['subsystem']!='short_strip': layers.append(l); continue
        base_r=l['r_m']; radius=base_r+shift
        l['z_min_m'],l['z_max_m']=-.6,.6
        layers.append(l)
        if mode=='eta':
            edges=radius*np.sinh(np.linspace(math.asinh(.6/radius),math.asinh(1.2/radius),7))
        else: edges=np.linspace(.6,1.2,7)
        for side in [-1,1]:
            for i,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
                zc=(float(lo)+float(hi))/2
                alpha=min(math.atan2(zc,radius),math.pi/4)
                nr,nz=math.cos(alpha),math.sin(alpha); d=nr*radius+nz*zc
                end=[]
                for zedge, ext in [(float(lo),-margin),(float(hi),margin)]:
                    slope=zedge/radius; r=d/(nr+nz*slope); z=slope*r
                    end.append((r-nz*ext,side*(z+nr*ext)))
                row={k:v for k,v in l.items() if k not in ['r_m','z_min_m','z_max_m']}
                row.update(id=l['id']+f'-{"P" if side>0 else "N"}{i+1}',kind='inclined_ring',
                           r0_m=radius,z0_m=side*zc,normal_r=nr,normal_z=side*nz,
                           r1_m=end[0][0],z1_m=end[0][1],r2_m=end[1][0],z2_m=end[1][1],provenance='DES-006-R-C09')
                layers.append(row)
    result['layers']=layers
    return result


METRICS=['sigma_d0_um','sigma_z0_um','sigma_qpt_per_GeV']
SEARCH_ETAS=[round(i*.05,8) for i in range(81)]
SEARCH_CASES=list(itertools.product(SEARCH_ETAS,[-.15,0.,.15],[1.,100.]))


def sample(candidate, eta, zv, pt, scale=1., beam=0.):
    hits=crossings(candidate,eta,zv,pt,0.) # straight-reference covariance at 3 T
    info=summarize(hits)
    rs=[h[0] for _,h in hits]; paths=[h[2] for _,h in hits]
    return dict(eta=eta,vertex_z_m=zv,pt_GeV=pt,**info,
                first_r_m=rs[0],second_r_m=rs[1],last_r_m=rs[-1],
                max_path_gap_m=max(np.diff(paths),default=0.),
                **covariance(hits,eta,pt,material_scale=scale,beam_x0=beam))


def evaluate(candidate, reference):
    errors=geometry_errors(candidate)
    if errors: return dict(valid=False,errors=errors[:8])
    values=[sample(candidate,*case) for case in SEARCH_CASES]
    ratios=np.array([[v[k]/r[k] for k in METRICS] for v,r in zip(values,reference)])
    deficits=np.array([max(0,r['stations']-v['stations']) for v,r in zip(values,reference)])
    pixel_losses=sum(v['pixel_stations']<r['pixel_stations'] for v,r in zip(values,reference))
    # Equal log weights plus worst-probe and gap penalties: do not hide local losses.
    score=float(np.mean(np.log(ratios))+.20*np.max(np.log(ratios))+.04*np.mean(deficits)
                +.02*np.mean([math.log(v['max_path_gap_m']/r['max_path_gap_m']) for v,r in zip(values,reference)]))
    return dict(valid=True,score=score,mean_resolution_ratios=np.mean(ratios,axis=0).tolist(),
                worst_resolution_ratios=np.max(ratios,axis=0).tolist(),
                lost_station_probes=int(sum(deficits>0)),lost_pixel_probes=pixel_losses,
                min_stations=min(v['stations'] for v in values),
                mean_material_percent=float(np.mean([v['local_material_percent'] for v in values])),
                max_path_gap_m=max(v['max_path_gap_m'] for v in values))


def search(initial, reference, cid):
    current=copy.deepcopy(initial); trace=[]
    transition_control=[sample(initial,1.1,0.,pt)['sigma_qpt_per_GeV'] for pt in [1.,100.]]
    def choose(stage, options):
        nonlocal current
        trials=[]
        for parameters, candidate in options:
            result=evaluate(candidate,reference)
            if stage=='coupled outer radius and transition refinement' and result['valid']:
                transition=[sample(candidate,1.1,0.,pt)['sigma_qpt_per_GeV']/control
                            for pt,control in zip([1.,100.],transition_control)]
                result['eta1p1_origin_qpt_ratios']=transition
                if max(transition)>1.+1e-10:
                    result.update(valid=False,errors=['review guard: eta1.1 origin momentum regression'])
            trials.append(dict(parameters=parameters,**result))
        valid=[(i,t) for i,t in enumerate(trials) if t['valid']]
        if not valid: raise ValueError('No feasible option:'+stage)
        index,best=min(valid,key=lambda item:item[1]['score'])
        current=options[index][1]
        trace.append(dict(stage=stage,trials=trials,selected=index))
        print(cid,stage,best['parameters'],round(best['score'],5),flush=True)
    options=[]
    for pr,sr,lr in itertools.product([.180,.185,.190],[.200,.205,.210],[.710,.720,.735]):
        if sr-pr<.010-1e-12: continue
        d=dict(pixel_disk_rmax=pr,short_disk_rmin=sr,long_disk_rmin=lr)
        options.append((d,modify(current,d)))
    choose('disjoint disk volumes',options)
    for iteration in range(2):
        for key,values in [('pixel-B1_r',[.034,.036,.039]),('pixel-B2_r',[.060,.070,.080]),
                           ('pixel-B3_r',[.106,.116,.126]),('pixel-B4_r',[.162,.172,.182]),
                           ('short_strip-B1_r',[.25,.26,.28]),('short_strip-B2_r',[.34,.36,.38]),
                           ('short_strip-B3_r',[.48,.50,.52]),('short_strip-B4_r',[.64,.66,.68]),
                           ('long_strip-B1_r',[.80,.82,.84]),('long_strip-B2_r',[1.02,1.06,1.10])]:
            # C1 rows move with their parent when short-strip radii change.
            options=[]
            for value in values:
                cand=modify(current,{key:value})
                if cid=='C1' and key.startswith('short_strip'):
                    old=next(l['r_m'] for l in current['layers'] if l['id'].split('-',1)[1]==key[:-2])
                    for l in cand['layers']:
                        if l['kind']=='inclined_ring' and l['station_group'].split('-',1)[1]==key[:-2]:
                            for k in ['r0_m','r1_m','r2_m']: l[k]+=value-old
                options.append(({key:value},cand))
            choose(f'radial pass {iteration+1} {key}',options)
    options=[]
    for z1,z2,z3 in itertools.product([.58,.60,.65],[.78,.85],[1.,1.1]):
        cand=current
        for i,z in enumerate([z1,z2,z3],1): cand=disk_z(cand,'pixel',i,z)
        options.append((dict(pixel_z_m=[z1,z2,z3]),cand))
    choose('first pixel disks',options)
    options=[]
    for half in [1.2,1.3,1.4]:
        for z1 in [half+.03,half+.10,half+.17]:
            for z2 in [1.50,1.60,1.70]:
                if z2-z1<.06: continue
                cand=modify(current,{'long_half':half})
                cand=disk_z(disk_z(cand,'long_strip',1,z1),'long_strip',2,z2)
                options.append((dict(long_half=half,long_z_m=[z1,z2]),cand))
    choose('outer transition and final-hit radius',options)
    for iteration in range(2):
        for subsystem in ['short_strip','long_strip']:
            for number in range(1,7):
                z=next(abs(l['z_m']) for l in current['layers'] if l['kind']=='disc' and l['subsystem']==subsystem and l['id'].endswith(f'-P{number}'))
                half=max(l['z_max_m'] for l in current['layers'] if l['kind']=='cylinder' and l['subsystem']==subsystem)
                options=[]
                for delta in [-.05,0.,.05]:
                    value=round(z+delta,8)
                    if value<half+.030-1e-12 or value>3.12: continue
                    cand=disk_z(current,subsystem,number,value)
                    zs=sorted(l['z_m'] for l in cand['layers'] if l['kind']=='disc' and l['subsystem']==subsystem and l['z_m']>0)
                    if min(np.diff(zs))<.060-1e-12: continue
                    options.append((dict(subsystem=subsystem,disk=number,z_m=value),cand))
                choose(f'axial pass {iteration+1} {subsystem} disk {number}',options)
    options=[]
    for radius,half in itertools.product([1.02,1.06,1.10],[1.2,1.3,1.4]):
        for offset,z2 in itertools.product([.03,.10,.17],[1.5,1.6,1.7,1.8]):
            z1=round(half+offset,8)
            if z2-z1<.060-1e-12: continue
            cand=modify(current,{'long_strip-B2_r':radius,'long_half':half})
            cand=disk_z(disk_z(cand,'long_strip',1,z1),'long_strip',2,z2)
            options.append((dict(outer_r_m=radius,long_half=half,long_z_m=[z1,z2]),cand))
    choose('coupled outer radius and transition refinement',options)
    return current,trace


def run():
    config=json.loads(BASE.read_text())
    original={c['id']:c for c in config['candidates'] if c['id'] in ['A','C1']}
    reference=[sample(original['A'],*case) for case in SEARCH_CASES]
    selected={}; traces={}
    for cid in ['A','C1']:
        selected[cid],traces[cid]=search(original[cid],reference,cid)
    # Retune inclined rows after independent radial/endcap iterations. Convert its
    # own chosen central short-strip radii into a cylinder template, retaining disks.
    flat=copy.deepcopy(selected['C1'])
    flat['layers']=[l for l in flat['layers'] if l['kind']!='inclined_ring']
    for l in flat['layers']:
        if l['kind']=='cylinder' and l['subsystem']=='short_strip': l['z_min_m'],l['z_max_m']=-1.2,1.2
    tilt_gap_limit=evaluate(selected['C1'],reference)['max_path_gap_m']
    options=[]
    for mode,shift,margin in itertools.product(['z','eta'],[-.02,0.,.02,.04,.08,.10],[0.,.005,.010]):
        cand=rows_from(flat,mode,shift,margin)
        result=evaluate(cand,reference)
        if result['valid'] and result['max_path_gap_m']>tilt_gap_limit+1e-10:
            result.update(valid=False,errors=['review guard: inclined rows enlarge worst extrapolation gap'])
        if result['valid']:
            rows=[sample(cand,e,v,100) for e in SEARCH_ETAS for v in [-.15,0,.15]]
            counts=[r['stations'] for r in rows if .8<=r['eta']<=2.5]
            # Count stability has an explicit secondary contribution; retain resolution scores.
            result['station_spread_0p8_2p5']=max(counts)-min(counts)
            result['tilt_score']=result['score']+.01*result['station_spread_0p8_2p5']
        options.append((dict(mode=mode,radial_shift_m=shift,tangent_margin_m=margin),cand,result))
    index=min((i for i,x in enumerate(options) if x[2]['valid']),key=lambda i:options[i][2]['tilt_score'])
    selected['C1']=options[index][1]
    traces['C1'].append(dict(stage='inclined row eta spacing and radial offsets',selected=index,
                            trials=[dict(parameters=p,**r) for p,_,r in options]))
    print('selected tilt',options[index][0],flush=True)
    output=dict(schema_version=1,status='DRAFT / PROTOTYPE',governing_design='DES-006 R-C09',
                host=config['host'],units=config['units'],candidates=list(selected.values()),
                active_options=['A','C1'],withdrawn_options=['B','C2'],
                definition='Review iteration; original inputs retained in DES-006-layouts and inclined-split-layouts')
    GEOM.write_text(json.dumps(output,indent=2)+'\n')
    profiles={}; diagnostics={}; controls={}
    for label,cand in {**{k+'0':v for k,v in original.items()},**selected}.items():
        profiles[label]=[sample(cand,round(i*.025,8),v,pt) for i in range(161) for v in [-.15,0.,.15] for pt in [1.,100.]]
        finite=[]
        for field,pt,zv in itertools.product([2.,3.,4.],[1.,10.,100.],[-.15,0.,.15]):
            vals=[summarize(crossings(cand,round(i*.01,8),zv,pt,field)) for i in range(-400,401)]
            baseline_vals=[summarize(crossings(original['A'],round(i*.01,8),zv,pt,field)) for i in range(-400,401)]
            finite.append(dict(field_T=field,pt_GeV=pt,vertex_z_m=zv,
                               lost_station_probes_vs_A0=sum(x['stations']<y['stations'] for x,y in zip(vals,baseline_vals)),
                               lost_pixel_probes_vs_A0=sum(x['pixel_stations']<y['pixel_stations'] for x,y in zip(vals,baseline_vals)),
                               min_stations=min(x['stations'] for x in vals),
                               min_pixel_stations=min(x['pixel_stations'] for x in vals),
                               max_material_percent=max(x['local_material_percent'] for x in vals)))
        diagnostics[label]=dict(geometry_errors=geometry_errors(cand),area=area_ledger(cand),finite_field=finite)
        controls[label]=[dict(material_scale=scale,beam_x0_normal=beam,**sample(cand,e,0.,pt,scale,beam))
                          for scale,beam,e,pt in itertools.product([0.,.5,1.,2.],[0.,.002],[0.,1.1,1.2,2.,3.,4.],[1.,100.])]
    report=dict(status='DRAFT / PROTOTYPE; bounded search, not global optimum or fit acceptance',
                search_cases=len(SEARCH_CASES),search_eta_step=.05,search_vertices_m=[-.15,0,.15],search_pt_GeV=[1,100],
                objective='mean(log resolution ratio to A0) + .20*max(log resolution ratio) + .04*mean lost stations + .02*mean(log maximum-path-gap ratio); equal d0/z0/qpt and case weights; tilt adds .01*(max-min stations in .8<=eta<=2.5)',
                review_guards=['Final outer refinement cannot worsen origin eta1.1 qpt uncertainty at either pT1 or100 relative to its original option', 'Final inclined-row change cannot enlarge pre-tilt worst path gap on search grid'],tilt_gap_limit_m=tilt_gap_limit,metric_order=METRICS,traces=traces,profiles=profiles,diagnostics=diagnostics,material_controls=controls,
                finite_field_probes_per_layout=801*27,profile_cases_per_layout=161*3*2,
                limitations=['Straight-reference five-parameter block covariance, not finite-curvature fit',
                             'Leading Gaussian thin-scatterer model; beta=1; no energy loss/log correction/tails',
                             'Normal layer allowances retained; no engineered supports/services; pipe material is sensitivity only',
                             'Ideal r-z segments, no finite modules/phi gaps/engineering certification',
                             'Uniform fields and vertex stress tests, not beamspot or physics benchmark'],
                provenance=dict(project_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                                dirty=bool(subprocess.check_output(['git','status','--porcelain'])),
                                python=platform.python_version(),numpy=np.__version__,seed=None,
                                command=' '.join(sys.orig_argv),hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                [BASE,GEOM,Path(__file__),ROOT/'tools/tracker_layout/inclined_study.py',ROOT/'tools/tracker_layout/study.py']}))
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('Wrote',OUT)


if __name__=='__main__': run()
