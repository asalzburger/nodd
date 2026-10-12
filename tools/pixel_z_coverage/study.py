#!/usr/bin/env python3
"""Repeatable DES-013 geometry, coverage and native ACTS study (PROTOTYPE)."""
import argparse
import gzip
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys

from layout import ROOT, barrel, build, load, transverse_support_screen
from geometry import summarize, body_overlap_diagnostics
from intersections import SurfaceIndex, evaluate, _summarize_columns
from sampling import directions, tracks_for, native_sample


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def compressed(path,value):
    # Deterministic compressed outputs, without path or wall-clock headers.
    path.write_bytes(gzip.compress(json.dumps(value,allow_nan=False).encode(),mtime=0))


def inventory(layout,config):
    result={'silicon':summarize(layout),'layers':{}}
    for layer in layout['layers']:
        bodies=[b for b in layout['bodies'] if barrel(b) and b['layer_id']==layer['id']]
        if not bodies: continue
        patches=[m for m in layout['modules'] if m['layer_id']==layer['id']]
        row=sorted([b for b in bodies if b['col']==0],key=lambda b:b['center_mm'][2])
        z=[b['center_mm'][2] for b in row]
        sensor_area=sum(next(p['sensor_area_mm2'] for p in patches if p['module_id']==b['module_id']) for b in bodies)
        family=bodies[0]['family']; old=json.loads((ROOT/'tools/pixel_support/inputs.json').read_text())
        flow=old['families'][family]['flow_g_s']
        nominal=len(patches)*config['power_W_per_chip']; staves=len({b['col'] for b in bodies})
        result['layers'][layer['id']]=dict(modules=len(bodies),chips=len(patches),staves=staves,rows=len(row),
            sensor_area_m2=sensor_area*1e-6,active_area_m2=sum(p['active_area_mm2'] for p in patches)*1e-6,
            body_phi_mm=2*row[0]['half_u_mm'],body_z_mm=2*row[0]['half_v_mm'],
            pitch_z_mm=z[1]-z[0],gap_mm=z[1]-z[0]-2*row[0]['half_v_mm'],
            occupied_z_min_mm=z[0]-row[0]['half_v_mm'],occupied_z_max_mm=z[-1]+row[-1]['half_v_mm'],
            nominal_power_W=nominal,stress_power_W=nominal*config['power_stress_factor'],
            stress_power_per_stave_W=nominal*config['power_stress_factor']/staves,
            inherited_flow_g_s_per_circuit=flow,
            exit_quality_stress_imbalanced=old['inlet_quality']+nominal*config['power_stress_factor']/staves*old['heat_fraction_max']/(flow*old['latent_heat_J_g']))
    return result


def coverage(layout,tracks):
    index=SurfaceIndex(layout); summaries={}; raw={}; worst={}
    for mode,values in tracks.items():
        print(' evaluating',mode,len(values),flush=True)
        report=evaluate(layout,values,index=index)
        rows=report.pop('per_track');raw[mode]=rows
        report['cohorts']={}
        for cohort in ('off_grid','central_grid','luminous_boundary_grid','eta0_z0'):
            mask=[(t['eta']==0 and t['origin_mm'][2]==0) if cohort=='eta0_z0' else t['cohort']==cohort for t in values]
            report['cohorts'][cohort]={}
            for scope,data in [('total',{k:v for k,v in rows.items() if isinstance(v,list)})]+list(rows['per_subdetector_region'].items()):
                report['cohorts'][cohort][scope]=_summarize_columns(data,mask)
        worst[mode]=sorted(range(len(values)),key=lambda i:-rows['per_subdetector_region']['pixel_barrel']['missing_stations'][i])[:4]
        summaries[mode]=report
    return summaries,raw,worst


def native_tracks(tracks,count,seed,worst):
    chosen=native_sample(tracks,count,seed,worst)
    for mode,values in tracks.items():
        central=[(i,t) for i,t in enumerate(values) if t['eta']==0 and t['origin_mm'][2]==0]
        for i,t in central[::max(1,len(central)//8)]:
            row=dict(t,mode=mode,original_index=i)
            if row not in chosen:chosen.append(row)
    return chosen


def run_case(config,case,output,probe=False):
    target=Path(output)/case['id'];target.mkdir(parents=True,exist_ok=False)
    print('CASE',case['id'],flush=True)
    baseline=load(config);layout=build(baseline,case)
    compressed(target/'layout.json.gz',layout)
    # Only pixel barrel boxes change, but compare them to all detector bodies.
    overlap=body_overlap_diagnostics(layout,tolerance_mm=config['overlap_tolerance_mm'])
    support=transverse_support_screen(layout,config['overlap_tolerance_mm'])
    report=dict(case=case,inventory=inventory(layout,config),body_screen=overlap,support_screen=support)
    if overlap['overlapping_body_pairs'] or support['conflicts']:
        write(target/'summary.json',report)
        raise RuntimeError('Unexplained overlap: stop study and inspect '+case['id'])
    sampling=dict(config['sampling'])
    if probe:sampling.update(random_tracks=64,eta_points=5,phi_points=4,stress_eta_points=3,stress_phi_points=2)
    samples=directions(sampling)
    tracks={mode:tracks_for(samples,mode,sampling) for mode in ('straight','positive','negative')}
    report['coverage'],raw,worst=coverage(layout,tracks)
    compressed(target/'track-results.json.gz',raw)
    chosen=native_tracks(tracks,config['native_count'],config['native_seed'],worst)
    # Separate total-p=1 GeV sensitivity: same independent random vertices/directions.
    offgrid=[s for s in samples if s['cohort']=='off_grid']
    total_sampling=dict(sampling,momentum_convention='p')
    total_tracks={mode:tracks_for(offgrid,mode,total_sampling) for mode in ('positive','negative')}
    report['total_p_coverage'],total_raw,total_worst=coverage(layout,total_tracks)
    compressed(target/'total-p-track-results.json.gz',total_raw)
    chosen+=native_sample(total_tracks,12,config['native_seed']+1,total_worst)
    write(target/'native-tracks.json',chosen)
    write(target/'summary.json',report)
    print('DONE',case['id'],flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=Path(__file__).with_name('config.json'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--case',action='append')
    p.add_argument('--probe',action='store_true',help='Small development cohort; not final evidence')
    p.add_argument('--native-only',action='store_true')
    p.add_argument('--acts-source',type=Path)
    p.add_argument('--runtime-manifest',type=Path)
    args=p.parse_args();config=json.loads(args.config.read_text())
    cases=[c for c in config['cases'] if not args.case or c['id'] in args.case]
    if args.native_only:
        from acts_validate import validate
        for case in cases:
            target=args.output/case['id']
            layout=json.loads(gzip.decompress((target/'layout.json.gz').read_bytes()))
            tracks=json.loads((target/'native-tracks.json').read_text())
            audit=validate(layout,tracks,target/'acts',acts_source=args.acts_source)
            if args.runtime_manifest:
                manifest=json.loads(args.runtime_manifest.read_text())
                if audit['runtime']['acts_extension_sha256']!=manifest['acts_extension_sha256']:
                    raise RuntimeError('Imported extension differs from overlay declaration')
                audit['overlay_provenance']={k:manifest[k] for k in ('acts_extension_sha256','overlay_has_sensitive_binding','overlay_has_step_size_binding')}
                audit['overlay_provenance']['note']='Reused installed ACTS libraries and build objects; source checkout is not a clean rebuild of imported overlay.'
                write(target/'acts/native-target-audit.json',audit)
            print(case['id'],'ACTS',audit['passed'],'tracks',len(tracks),'residual',audit['maximum_trajectory_residual_mm'],flush=True)
            if not audit['passed']:raise RuntimeError('Native audit failed')
    else:
        args.output.mkdir(parents=True,exist_ok=True)
        provenance=dict(status='PROTOTYPE; development probe' if args.probe else 'PROTOTYPE; final sampling',
            command=sys.argv,config=config,python=sys.version,platform=platform.platform(),
            git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            source_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()
                           for pattern in ('tools/pixel_z_coverage/*.py','tools/module_layout/*.py') for f in ROOT.glob(pattern)})
        write(args.output/'provenance.json',provenance)
        for case in cases:run_case(config,case,args.output,args.probe)

if __name__=='__main__':main()
