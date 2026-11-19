#!/usr/bin/env python3
"""Sample routed-pipe occupancy in unchanged native ECAL; never compose an overlay."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bind_sources(hashes):
    for name,wanted in hashes.items():
        if sha(ROOT/name) != wanted:
            raise ValueError('Stale scientific source: '+name)


def samples(report,targets):
    """Actual pipe centres/walls and separately unmaterialised radial reservations."""
    radii=report['adjusted_radii_mm'];wall=(radii['inner']+radii['outer'])/2
    for path in report['paths']:
        side=path['side'];station=path['station']
        for segment in path['segments']:
            centre=segment['center_mm'];x,y,z=segment['frame'];length=segment['length_mm']
            for fraction in (.1,.5,.9):
                mid=[centre[k]+(fraction-.5)*length*z[k] for k in range(3)]
                yield 'physical_core',side,station,mid
                for angle in (0.,math.pi/2,math.pi,3*math.pi/2):
                    n=[math.cos(angle)*x[k]+math.sin(angle)*y[k] for k in range(3)]
                    yield 'physical_wall',side,station,[mid[k]+wall*n[k] for k in range(3)]
                    yield 'unmaterialised_100mm_envelope',side,station,[mid[k]+50*n[k] for k in range(3)]
                    yield 'unmaterialised_20mm_clearance',side,station,[mid[k]+70*n[k] for k in range(3)]
        # Targets derive from the existing barrel closure/bath boundaries. Interpolate
        # the actual polyline, not the analytic arc, to catch thin closed walls.
        radial_targets=targets['radial_mm']
        axial_targets=targets['abs_z_mm']
        vertices=path['vertices_mm']
        for first,last in zip(vertices,vertices[1:]):
            r0,r1=math.hypot(*first[:2]),math.hypot(*last[:2])
            z0,z1=abs(first[2]),abs(last[2])
            fractions=[]
            if r1-r0>1e-8:
                fractions += [(r-r0)/(r1-r0) for r in radial_targets if r0<r<r1]
            if z1-z0>1e-8:
                fractions += [(z-z0)/(z1-z0) for z in axial_targets if z0<z<z1]
            for t in fractions:
                yield 'physical_core_boundary_seed',side,station,[first[k]+t*(last[k]-first[k]) for k in range(3)]


def category(material,path):
    if 'N2wall' in path or 'N2fluid' in path:return 'existing_cooling_pipe_or_core'
    if material=='Air':return 'air'
    if material=='Vacuum':return 'cryostat_vacuum_interface'
    if material=='LAr':return 'bath_requiring_daughter_displacement'
    return 'occupied_structural_material'


def inspect(args):
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    context=json.loads((args.context/'combined.json').read_text())
    bind_sources(context['scientific_source_sha256'])
    compact=args.context/'combined.xml';materials=args.context/'materials.xml'
    if sha(compact)!=context['combined_sha256'] or sha(materials)!=context['materials_sha256']:
        raise ValueError('Stale native ECAL compact/material binding')
    bound={str(p.resolve()):sha(p) for p in
           [compact,materials,args.context/'combined.json',Path(__file__),*args.library]}
    for name,wanted in context['scientific_source_sha256'].items():
        bound[str((ROOT/name).resolve())]=wanted
    tree=ET.parse(compact)
    if {int(x.get('id')) for x in tree.findall('detectors/detector')} != {10,11} or tree.find('fields') is not None:
        raise ValueError('Expected unchanged ECAL-only context, no field')
    barrel=json.loads((ROOT/'tools/lar_calorimeter/barrel.json').read_text())
    radial=[barrel['sampling_outer_radius_mm']+barrel['rear_bath_mm']]
    for key in ('rear_cold_mm','rear_vacuum_mm','rear_warm_mm'):radial.append(radial[-1]+barrel[key])
    active=barrel['warm_half_z_mm']-sum(barrel[k] for k in
        ('end_warm_mm','end_vacuum_mm','end_cold_mm','end_bath_mm'))
    axial=[active,active+barrel['end_bath_mm']]
    for key in ('end_cold_mm','end_vacuum_mm','end_warm_mm'):axial.append(axial[-1]+barrel[key])
    targets=dict(radial_mm=[(a+b)/2 for a,b in zip(radial,radial[1:])],
        abs_z_mm=[3250.,3500.,3750.,3900.]+[(a+b)/2 for a,b in zip(axial,axial[1:])],
        source='barrel.json shell/bath midpoints; support/board/cooling-end axial seed locations')
    for library in args.library:
        if R.gSystem.Load(str(library.resolve()))<0:raise RuntimeError('Context library load failed')
    detector=dd4hep.Detector.getInstance();detector.fromXML(str(compact.resolve()))
    manager=R.gGeoManager;mm=float(dd4hep.mm)
    results=[]
    for directory in args.route:
        report=json.loads((directory/'expected.json').read_text());bind_sources(report['source_sha256'])
        bound[str((directory/'expected.json').resolve())]=sha(directory/'expected.json')
        for name,wanted in report['source_sha256'].items():bound[str((ROOT/name).resolve())]=wanted
        for name,wanted in report['artifact_sha256'].items():
            if sha(directory/name)!=wanted:raise ValueError('Stale route artifact: '+name)
            bound[str((directory/name).resolve())]=wanted
        counts=defaultdict(Counter);by_material=defaultdict(Counter);by_side=defaultdict(Counter)
        witnesses=[];seen=set();total=0
        for kind,side,station,point in samples(report,targets):
            node=manager.FindNode(*(v*mm for v in point))
            if not node:raise RuntimeError('Probe outside bound context world')
            material=str(node.GetVolume().GetMaterial().GetName());path=str(manager.GetPath())
            classification=category(material,path);counts[kind][classification]+=1
            by_material[kind][material]+=1;by_side[str(side)][kind]+=1;total+=1
            key=(kind,classification,side)
            if classification!='air' and key not in seen:
                seen.add(key);witnesses.append(dict(kind=kind,side=side,station=station,
                    position_mm=point,classification=classification,material=material,native_path=path))
        blocking=sum(v['occupied_structural_material']+v['existing_cooling_pipe_or_core']+
                     v['cryostat_vacuum_interface'] for k,v in counts.items() if k.startswith('physical'))
        results.append(dict(variant=report['variant'],status='CONTACT_SAMPLES' if blocking else 'NO_BLOCKING_SAMPLES',
            route_expected_sha256=sha(directory/'expected.json'),samples=total,
            counts={k:dict(v) for k,v in counts.items()},material_counts={k:dict(v) for k,v in by_material.items()},
            samples_by_side={k:dict(v) for k,v in by_side.items()},bounded_witnesses=witnesses))
    if {r['variant'] for r in results}!={'old','new'}:raise ValueError('Supply matched old and new route exports')
    if any(sha(path)!=wanted for path,wanted in bound.items()):
        raise ValueError('Context/route inputs changed during diagnostic')
    result=dict(status='DIAGNOSTIC / NO INTEGRATION ACCEPTANCE',
        scope='Occupancy samples in unchanged material-filled native LAr ECAL. Routing volumes are not placed in this context.',
        fit_accepted=False,context_combined_sha256=sha(compact),context_materials_sha256=sha(materials),
        context_record_sha256=sha(args.context/'combined.json'),scientific_source_sha256=context['scientific_source_sha256'],
        context_library_sha256={p.name:sha(p) for p in args.library},tool_sha256=sha(__file__),
        input_path_sha256={str(Path(path).relative_to(ROOT)):wanted for path,wanted in bound.items()},
        inputs_unchanged=True,
        execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),ROOT=R.gROOT.GetVersion()),
        sampling=dict(segment_fractions=[.1,.5,.9],cross_section_angles_rad=[0,math.pi/2,math.pi,3*math.pi/2],
                      boundary_targets=targets),
        variants=results,
        limitations=['Positive samples witness contacts; absence of a sample never proves clearance.',
            'Existing cooling occupancy is a continuation/duplicate-material interface, not independent extra services.',
            'Bath occupancy requires correct parent/daughter displacement; it is not an automatically valid insertion.',
            '100mm envelope and20mm installation allowance have no assigned material; their samples are separate from20mm pipe.',
            'No new native overlap check of the unchanged ECAL is implied; component audits remain separate.',
            'No tracker, magnet, HCAL, forward/collar or muon model is loaded. No400mm ECAL shift or transport overlay.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({r['variant']:dict(samples=r['samples'],status=r['status'],physical=r['counts'].get('physical_core_boundary_seed',{})) for r in results}))
    # Release DD4hep while ROOT runtime state remains alive; this is a standalone
    # diagnostic process, never the maintained detector's shared singleton.
    dd4hep.Detector.destroyInstance()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--context',type=Path,required=True)
    p.add_argument('--library',type=Path,action='append',required=True)
    p.add_argument('--route',type=Path,action='append',required=True)
    p.add_argument('--output',type=Path,required=True)
    inspect(p.parse_args())
