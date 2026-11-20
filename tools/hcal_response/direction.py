#!/usr/bin/env python3
"""Prospective finite-solid HCAL barrel direction selection; no shower data.

The input is the frozen exported physical geometry, not a fitted response map.
Full candidate data stay local. A compact immutable receipt records the winner
and independent ROOT confirmation before any new shower sample is launched.
"""
import argparse
from bisect import bisect_left, bisect_right
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
EPS_MM = 1e-9
STEEL_TOLERANCE_MM = 1e-5
CLEARANCE_TIE_MM = 1e-6
OFFSETS_MM = (-5., 0., 5.)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def slab(interval, slope, lower, upper):
    """Clip a radial-parameter interval to an open finite Cartesian slab."""
    if lower >= upper:return None
    if abs(slope)<1e-15:
        return interval if lower<0<upper else None
    a,b=lower/slope,upper/slope
    if a>b:a,b=b,a
    low,high=max(interval[0],a),min(interval[1],b)
    return (low,high) if high-low>EPS_MM else None


def box_interval(p,q,center,dims):
    """Ray (t,a,r)=(p*r,q*r,r) against a finite axis-aligned box."""
    result=(0.,float('inf'))
    for slope,c,key in zip((p,q,1.),center,('sx','sy','sz')):
        result=slab(result,slope,c-dims[key]/2,c+dims[key]/2)
        if result is None:return None
    return result


def recess_interval(p,q,center,radius,length,interval):
    """Finite cylinder with its axis along the radial coordinate."""
    result=slab(interval,1.,center[2]-length/2,center[2]+length/2)
    if result is None:return None
    a=p*p+q*q;b=-2*(p*center[0]+q*center[1]);c=center[0]**2+center[1]**2-radius**2
    if a<1e-30:return result if c<0 else None
    discriminant=b*b-4*a*c
    if discriminant<=0:return None
    radius_term=math.sqrt(discriminant)
    low,high=(-b-radius_term)/(2*a),(-b+radius_term)/(2*a)
    low,high=max(result[0],low),min(result[1],high)
    return (low,high) if high-low>EPS_MM else None


def core_intersection(p,q,center,part):
    """Exact box-minus-cylinder radial path and reference-plane clearance."""
    interval=box_interval(p,q,center,part['dimensions_mm'])
    if interval is None:return 0.,None
    cuts=[]
    for cut in part['cuts']:
        if cut['kind']!='tube' or cut['frame']!=[[1,0,0],[0,1,0],[0,0,1]] or cut['dimensions_mm']['rmin']!=0:
            raise ValueError('selector supports only declared radial cylindrical core recesses')
        cc=[v+c for v,c in zip(center,cut['center_mm'])];d=cut['dimensions_mm']
        clipped=recess_interval(p,q,cc,d['rmax'],d['length'],interval)
        if clipped:cuts.append(clipped)
    # Merge removed intervals, so the arithmetic also handles disjoint cutters.
    removed=0.;end=-float('inf')
    for low,high in sorted(cuts):
        if high>end:removed+=high-max(low,end);end=high
    length=interval[1]-interval[0]-removed
    if length<=EPS_MM:return 0.,None
    r=center[2];dx,dy=p*r-center[0],q*r-center[1];d=part['dimensions_mm']
    clearance=min(d['sx']/2-abs(dx),d['sy']/2-abs(dy))
    if clearance<=0:clearance=0.
    elif any(low<=r<=high for low,high in cuts):clearance=0.
    return length,clearance


def steel_path(p,q,c):
    """Clip the actual sector-owned steel trapezoids; return true path mm."""
    b=c['barrel'];t=math.tan(math.pi/c['sectors']);inset=b['sector_half_seam_mm']+b['edge_rail_mm']
    half_z=b['half_z_mm']-b['end_flange_mm'];pitch=c['steel_mm']+12+c['installation_gap_mm']
    radial_length=0.
    for layer in range(c['layers']):
        front=b['front_apothem_mm']+layer*pitch;result=(front,front+c['steel_mm'])
        result=slab(result,q,-half_z,half_z)
        if result is None:continue
        for coefficient in (t-p,t+p):
            if coefficient<=0:result=None;break
            low=max(result[0],inset/coefficient)
            if result[1]-low<=EPS_MM:result=None;break
            result=(low,result[1])
        if result:radial_length+=result[1]-result[0]
    norm=math.sqrt(1+p*p+q*q)
    nominal=c['layers']*c['steel_mm']*norm
    actual=radial_length*norm
    return actual,abs(actual-nominal)<=STEEL_TOLERANCE_MM


def compile_geometry(directory):
    directory=Path(directory);expected=json.loads((directory/'expected.json').read_text())
    for name,digest in expected['export_sha256'].items():
        if Path(name).name!=name or sha(directory/name)!=digest:raise ValueError('changed exported geometry '+name)
    units={}
    for key,u in expected['units'].items():
        groups={}
        for part in u['parts']:
            if part['role']!='sensitive':continue
            if part['shape_kind']!='box' or part['frame']!=[[1,0,0],[0,1,0],[0,0,1]]:
                raise ValueError('selector requires declared axis-aligned sensitive boxes')
            groups.setdefault(part['center_mm'][1],[]).append(part)
        keys=sorted(groups)
        units[int(key)]=dict(definition=u,rows=keys,parts_by_row=groups,
            half_size=[v/2 for v in u['fixture']['carrier_size_mm']],
            max_core_half_y=max(part['dimensions_mm']['sy']/2 for group in groups.values() for part in group),
            max_core_half_z=max(part['dimensions_mm']['sz']/2 for group in groups.values() for part in group),
            core_z_values=sorted({part['center_mm'][2] for group in groups.values() for part in group}))
    layers={}
    with (directory/'placements.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            if int(row['system'])!=13 or int(row['sector'])!=0:continue
            frame=[[float(row[f'a{i}{j}']) for j in range(3)] for i in range(3)]
            if frame!=[[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]]:raise ValueError('unexpected sector0 carrier frame')
            carrier=dict(unit=int(row['unit']),carrier=int(row['carrier']),origin=[float(row[k]) for k in ('x_mm','y_mm','z_mm')])
            layers.setdefault(int(row['layer']),{}).setdefault(carrier['origin'][2],[]).append(carrier)
    if set(layers)!=set(range(expected['config']['layers'])):raise ValueError('incomplete barrel layer placement table')
    compiled={}
    for layer,rows in layers.items():
        carriers=[carrier for values in rows.values() for carrier in values]
        compiled[layer]=dict(rows=sorted(rows),carriers_by_row=rows,
            front=carriers[0]['origin'][0],max_half_y=max(units[carrier['unit']]['half_size'][1] for carrier in carriers),
            max_half_z=max(units[carrier['unit']]['half_size'][2] for carrier in carriers))
    return expected,units,compiled


def active_paths(p,q,units,layers):
    """Count actual finite active layers using placement-indexed source solids."""
    active=[];clearance=float('inf');length=0.;norm=math.sqrt(1+p*p+q*q)
    for layer,layout in sorted(layers.items()):
        front=layout['front'];mid=front+layout['max_half_z'];query=q*mid
        extent=layout['max_half_y']+abs(q)*layout['max_half_z']
        low=bisect_left(layout['rows'],query-extent);high=bisect_right(layout['rows'],query+extent)
        crossed=False
        for row in layout['rows'][low:high]:
            for carrier in layout['carriers_by_row'][row]:
                unit=units[carrier['unit']];r0,t0,a0=carrier['origin'];hs=unit['half_size']
                if box_interval(p,q,[t0,a0,r0+hs[2]],dict(sx=2*hs[0],sy=2*hs[1],sz=2*hs[2])) is None:continue
                czmin=min(unit['core_z_values']);czmax=max(unit['core_z_values'])
                reference=(czmin+czmax)/2;query=q*(r0+reference)-a0
                extent=unit['max_core_half_y']+abs(q)*(unit['max_core_half_z']+(czmax-czmin)/2)
                lower=bisect_left(unit['rows'],query-extent);upper=bisect_right(unit['rows'],query+extent)
                for core_row in unit['rows'][lower:upper]:
                    for part in unit['parts_by_row'][core_row]:
                        x,y,z=part['center_mm'];center=[t0+x,a0+y,r0+z];d=part['dimensions_mm']
                        if abs(p*center[2]-center[0])>d['sx']/2+abs(p)*d['sz']/2:continue
                        span,edge=core_intersection(p,q,center,part)
                        if span>EPS_MM:
                            crossed=True;length+=span*norm;clearance=min(clearance,edge)
        if crossed:active.append(layer)
    return dict(active_layers=active,active_layer_count=len(active),core_path_mm=length,
                minimum_core_reference_clearance_mm=0. if not active else clearance)


def evaluate(eta,phi,expected,units,layers):
    front=expected['config']['barrel']['front_apothem_mm'];p0=math.tan(phi);q0=math.sinh(eta)/math.cos(phi);rays=[]
    for tangent in OFFSETS_MM:
        for axial in OFFSETS_MM:
            p=p0+tangent/front;q=q0+axial/front;norm=math.sqrt(1+p*p+q*q)
            ray_phi=math.atan(p);ray_eta=math.asinh(q/math.sqrt(1+p*p))
            steel,full=steel_path(p,q,expected['config'])
            if not full:return None
            ray=active_paths(p,q,units,layers)
            ray.update(eta=ray_eta,phi_rad=ray_phi,front_tangential_offset_mm=tangent,front_axial_offset_mm=axial,
                       steel_path_mm=steel,nominal_steel_path_mm=expected['config']['layers']*expected['config']['steel_mm']*norm)
            rays.append(ray)
    counts=[ray['active_layer_count'] for ray in rays]
    return dict(eta=eta,phi_rad=phi,phi_deg=math.degrees(phi),minimum_active_layer_count=min(counts),
                active_layer_count_sum=sum(counts),mean_active_layer_count=sum(counts)/len(counts),
                minimum_core_reference_clearance_mm=min(ray['minimum_core_reference_clearance_mm'] for ray in rays),rays=rays)


def tie_key(candidate):
    return (abs(candidate['eta']),abs(candidate['phi_rad']),candidate['eta']<0,candidate['phi_rad']<0)


def select(candidates):
    if not candidates:raise ValueError('no candidate has complete steel traversal in all9rays')
    first=max(candidate['minimum_active_layer_count'] for candidate in candidates)
    selected=[candidate for candidate in candidates if candidate['minimum_active_layer_count']==first]
    second=max(candidate['active_layer_count_sum'] for candidate in selected)
    selected=[candidate for candidate in selected if candidate['active_layer_count_sum']==second]
    third=max(candidate['minimum_core_reference_clearance_mm'] for candidate in selected)
    selected=[candidate for candidate in selected if third-candidate['minimum_core_reference_clearance_mm']<CLEARANCE_TIE_MM]
    return min(selected,key=tie_key)


def confirm_native(directory,library,winner):
    import ROOT as R
    import dd4hep
    from native import trace
    R.EnableImplicitMT(1)
    try:
        R.gROOT.SetBatch(True)
        if R.gSystem.Load(str(Path(library).resolve()))<0:raise RuntimeError('cannot load HCAL prototype library')
        detector=dd4hep.Detector.getInstance();detector.fromXML(str(Path(directory).resolve()/'detector.xml'));manager=detector.manager()
        checks=[]
        for analytic in winner['rays']:
            native=trace(manager,dd4hep,analytic['eta'],analytic['phi_rad'],19000)
            layers=[row[2] for row in native['active_layers'] if row[0]==13 and row[1]==0]
            steel=native['material_path_mm'].get('Steel235',0.)
            errors=[]
            if layers!=analytic['active_layers']:errors.append('analytic/native active layer set mismatch')
            if abs(steel-analytic['steel_path_mm'])>STEEL_TOLERANCE_MM:errors.append('analytic/native steel path mismatch')
            actual_core=native['material_path_mm'].get('PSHost',0.)
            if abs(actual_core-analytic['core_path_mm'])>1e-4:errors.append('analytic/native sensitive path mismatch')
            checks.append(dict(analytic=analytic,native=native,steel_residual_mm=steel-analytic['steel_path_mm'],
                               core_residual_mm=actual_core-analytic['core_path_mm'],errors=errors))
        return dict(status='FAIL' if any(check['errors'] for check in checks) else 'PASS',rays=checks,
                    steel_tolerance_mm=STEEL_TOLERANCE_MM,core_path_tolerance_mm=1e-4,ROOT=R.gROOT.GetVersion(),
                    library_sha256=sha(library),scope='Independent actual ROOT navigation confirms all9winning finite rays, steel path, sensitive path and active layer identities')
    finally:
        R.DisableImplicitMT();dd4hep.Detector.destroyInstance()


def run(args):
    start=time.monotonic();directory=args.directory.resolve();output=args.output.resolve()
    source_paths=[Path(__file__),Path(__file__).with_name('native.py'),ROOT/'docs/validation/hcal50-edge/protocol.md',ROOT/'docs/design/DES-046-hcal-sector-edge-coverage.md']
    source_hashes={str(path.relative_to(ROOT)):sha(path) for path in source_paths}
    output.mkdir(parents=True,exist_ok=False)
    expected,units,layers=compile_geometry(directory)
    candidates=[];rejected=0
    with (output/'candidates.jsonl').open('w') as stream:
        for eta_index in range(-30,31):
            eta=eta_index*.02
            for phi_quarters in range(-45,46):
                phi=math.radians(phi_quarters*.25);candidate=evaluate(eta,phi,expected,units,layers)
                if candidate is None:
                    rejected+=1;record=dict(eta=eta,phi_rad=phi,status='REJECTED_INCOMPLETE_STEEL')
                else:
                    candidates.append(candidate)
                    record={key:value for key,value in candidate.items() if key!='rays'}
                    record['rays']=[{key:value for key,value in ray.items() if key!='active_layers'} for ray in candidate['rays']]
                    record['status']='ELIGIBLE'
                stream.write(json.dumps(record,separators=(',',':'),allow_nan=False)+'\n')
            if eta_index%5==0:print(f'geometry scan eta={eta:+.2f}: {len(candidates)} eligible, {rejected} rejected',flush=True)
    winner=select(candidates)
    confirmation=confirm_native(directory,args.library,winner)
    if source_hashes!={str(path.relative_to(ROOT)):sha(path) for path in source_paths}:raise RuntimeError('selector source/protocol changed during execution')
    receipt=dict(schema_version=1,status=confirmation['status'],created_at=datetime.now(timezone.utc).isoformat(),purpose='Geometry-only prospective fixed50GeV barrel direction; no shower outcomes consulted',
        grid=dict(eta_start=-.6,eta_stop=.6,eta_step=.02,phi_start_deg=-11.25,phi_stop_deg=11.25,phi_step_deg=.25,
                  candidates_total=61*91,eligible=len(candidates),rejected_incomplete_steel=rejected,front_offsets_mm=list(OFFSETS_MM)),
        ranking=['largest minimum active-layer count over9rays','largest active-layer-count sum over9rays',
                 'largest minimum transverse core-reference clearance; values within1e-6mm of global best tie',
                 'smallest absolute eta,absolute phi,then positive eta,positive phi'],winner=winner,native_confirmation=confirmation,
        execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                       dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),python=platform.python_version(),seconds=time.monotonic()-start),
        source_sha256=source_hashes,geometry_source_sha256=expected['source_sha256'],geometry_execution=expected['execution'],
        geometry_export_sha256=expected['export_sha256'],expected_sha256=sha(directory/'expected.json'),
        all_candidates_sha256=sha(output/'candidates.jsonl'),all_candidates_local_file='candidates.jsonl',
        limits=['Conditional central-barrel grid optimum, not a continuous angular optimum',
                'Nine displaced rays sample a declared neighbourhood, not its continuous interior',
                'Geometric coverage and depth do not predict shower resolution or containment'])
    save(output/'receipt.json',receipt)
    print(json.dumps(dict(status=receipt['status'],winner={key:value for key,value in winner.items() if key!='rays'},seconds=receipt['execution']['seconds'])),flush=True)
    return 0 if receipt['status']=='PASS' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for field in ('directory','library','output'):parser.add_argument('--'+field,type=Path,required=True)
    raise SystemExit(run(parser.parse_args()))
