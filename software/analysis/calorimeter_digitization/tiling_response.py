#!/usr/bin/env python3
"""Current full +z DES030 raw electron response against continuous-Si control.

PROTOTYPE: no Marlin/digitization. Fixed native-G4-gun macro blocks retain
independent seeds, run IDs and one ROOT file per sample. Run prepare, native
for both cases, run for both cases, then analyze. Full data stay ignored.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from tiled_endcap_transport import verify_component, sensor_offset, decode

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / 'docs/validation/issue117/tiling-response-plan.md'
PROTOCOL_REVISION = '6f9bcdfc04adbd5068ab2aa049ccd010f869b957'
DESCRIPTOR_CONTROL = 'system:8,side:2,sector:4,layer:6,module:10,x:-16,y:-16'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def public(value):
    return json.loads(json.dumps(value).replace(str(ROOT), '${NODD_REPO}').replace(str(Path.home()), '${USER_HOME}'))


def relative(path):
    return os.path.relpath(Path(path).resolve(), ROOT)


def polygon_area(points):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points, points[1:]+points[:1]))) / 2


def polygon_contains(points, point, tolerance=1e-7):
    return all((b[0]-a[0])*(point[1]-a[1])-(b[1]-a[1])*(point[0]-a[0]) >= -tolerance
               for a,b in zip(points, points[1:]+points[:1]))


def make_points(expected):
    modules = {m['index']: m for m in expected['modules']}
    square = modules[115]
    if square['center_mm'] != [1139., 48.] or not square['full']:
        raise ValueError('Frozen square-module reference changed')
    x, cy = square['center_mm']
    seam = x*math.tan(math.pi/16)
    # Exact values are the frozen protocol's geometry-derived first-plane targets.
    positions = [('C',x,cy,'square centre'), ('E-in',x,4.5,'active edge inside'),
        ('E-boundary',x,4.,'exact active boundary diagnostic'), ('E-guard',x,3.5,'guard'),
        ('G',x,0.,'tangential gap'), ('K-in',1095.5,4.5,'inside active corner'),
        ('K-gap',1091.,0.,'gap crossing'), ('U',x,206.74141090233807,'custom cross-section centre'),
        ('U-in',x,216.,'custom edge inside'), ('U-out',x,217.,'custom guard'),
        ('S-minus',x,seam-2,'support below seam'), ('S',x,seam,'exact mechanical seam'),
        ('S-plus',x,seam+2,'support beyond seam')]
    square_poly = [[square['center_mm'][0]+p[0], square['center_mm'][1]+p[1]] for p in square['active']]
    custom = modules[117]
    custom_poly = [[custom['center_mm'][0]+p[0],custom['center_mm'][1]+p[1]] for p in custom['active']]
    expected_inside = {'C': True,'E-in': True,'E-boundary': True,'E-guard': False,'K-in': True,'K-gap': False}
    z = expected['layout_report']['front_mm']+sensor_offset(expected,115)
    result = []
    for name, px, py, label in positions:
        if name in expected_inside and polygon_contains(square_poly,[px,py]) != expected_inside[name]:
            raise ValueError('Frozen square classification changed: '+name)
        if name in ('U','U-in','U-out') and polygon_contains(custom_poly,[px,py]) != (name!='U-out'):
            raise ValueError('Frozen custom classification changed: '+name)
        n = math.sqrt(px*px+py*py+z*z)
        result.append(dict(id=name,label=label,impact_mm=[px,py,z],direction=[px/n,py/n,z/n],
                           theta_rad=math.atan2(math.hypot(px,py),z),phi_rad=math.atan2(py,px),eta=math.asinh(z/math.hypot(px,py))))
    if not math.isclose(seam,226.56118644543045,abs_tol=1e-9):
        raise ValueError('Frozen seam coordinate changed')
    return result


def write_xml(path, tree):
    ET.indent(tree,space='  ')
    tree.write(path,encoding='utf-8',xml_declaration=True)


def prepare(args):
    if (args.work/'manifest.json').exists():
        raise ValueError('Prepared manifest already exists; choose a fresh --work directory to preserve execution evidence')
    expected, original, sources = verify_component(args.component)
    committed = subprocess.check_output(['git','show',PROTOCOL_REVISION+':'+str(PROTOCOL.relative_to(ROOT))],cwd=ROOT)
    if hashlib.sha256(committed).hexdigest() != sha(PROTOCOL):
        raise ValueError('Protocol bytes differ from the frozen revision')
    args.work.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(args.component/'materials.xml',args.work/'materials.xml')
    shutil.copyfile(args.component/'expected.json',args.work/'expected.json')
    tiled = deepcopy(original)
    detector = tiled.getroot().find('detectors/detector')
    for replica in list(detector.findall('replica')):
        if replica.get('side')!='1': detector.remove(replica)
    if len(detector.findall('replica')) != 16*49:
        raise ValueError('Full positive-end layer/frame inventory missing')
    write_xml(args.work/'tiled.xml',tiled)
    continuous = deepcopy(tiled)
    det_control = continuous.getroot().find('detectors/detector')
    layer = det_control.find("region[@name='edge_layer']")
    removed = []
    first = None
    for piece in list(layer.findall('piece')):
        if piece.get('role') in ('sensitive','sensor_edge'):
            removed.append(piece.get('name'))
            if piece.get('role')=='sensitive' and first is None: first=deepcopy(piece)
            layer.remove(piece)
    if len(removed)!=224 or first is None: raise ValueError('Unexpected original Si inventory')
    sheet = first
    sheet.set('name','continuous_sensitive_sheet');sheet.set('module','0')
    sheet.set('x','0*mm');sheet.set('y','0*mm')
    for child in list(sheet): sheet.remove(child)
    footprint = expected['layout_report']['carrier_face_mm']
    for x,y in footprint: ET.SubElement(sheet,'vertex',x=f'{x:.17g}*mm',y=f'{y:.17g}*mm')
    layer.append(sheet)
    readout = continuous.getroot().find('readouts/readout')
    readout.remove(readout.find('segmentation'))
    ET.SubElement(readout,'segmentation',type='CartesianGridXY',grid_size_x='5.5*mm',grid_size_y='5.5*mm',offset_x='2.75*mm',offset_y='2.75*mm')
    readout.find('id').text = DESCRIPTOR_CONTROL
    write_xml(args.work/'continuous.xml',continuous)
    ecal=json.loads((ROOT/'tools/calorimeter_hardware/cassettes.json').read_text())['ecal']
    offset=sensor_offset(expected,115);thickness=ecal['sensor_mm']
    if not math.isclose(offset,2.5) or not math.isclose(thickness,.5): raise ValueError('Frozen sheet depth changed')
    # Preserve all non-Si XML primitives byte-for-byte as element structures.
    oldpieces = original.getroot().find("detectors/detector/region[@name='edge_layer']")
    # Whitespace indentation is not geometry; compare canonical element trees.
    def canonical(node): return (node.tag,tuple(sorted(node.attrib.items())),tuple(canonical(c) for c in node))
    if [canonical(p) for p in oldpieces if p.get('role') not in ('sensitive','sensor_edge')] != [canonical(p) for p in layer if p.get('name')!='continuous_sensitive_sheet']:
        raise ValueError('Control changed unrelated hardware')
    density=expected['hardware']['materials']['Silicon']['density_g_cm3']
    old_si_volume=sum(p['volume_mm3'] for p in expected['hardware']['layer_parts'] if p['role'] in ('sensitive','sensor_edge'))
    new_si_volume=polygon_area(footprint)*thickness
    new_active_area=polygon_area(footprint)
    old_active_area=sum(m['sensitive_area_mm2'] for m in expected['modules'])
    points=make_points(expected)
    cases=[]
    for energy,selected in [(20,[p['id'] for p in points]),(5,['C','G','S']),(50,['C','G','S'])]:
        for point in selected: cases.append(dict(point_id=point,energy_GeV=energy,n=200,kind='response'))
    groups={}
    for geometry,base in [('continuous',11840000),('tiled',11840100)]:
        rows=([dict(point_id='C',energy_GeV=20,n=100,kind='calibration')]+deepcopy(cases)) if geometry=='continuous' else deepcopy(cases)
        for index,row in enumerate(rows):
            row.update(geometry=geometry,run_number=index,seed=base+index,
                       seed_pair=[base+index,base+index+100003])
            row['id']=f"{geometry}-{row['energy_GeV']}GeV-{row['point_id']}-{row['kind']}"
            row['file']=row['id']+'.edm4hep.root'
        groups[geometry]=rows
    libraries=list(args.factory.glob('*nODDCalorimeterPrototype.dylib'))+list(args.factory.glob('*nODDCalorimeterPrototype.so'))
    if len(libraries)!=1: raise ValueError('Missing unique matching factory library')
    manifest=dict(status='PROTOTYPE raw transport experiment',protocol_revision=PROTOCOL_REVISION,
        protocol_sha256=sha(PROTOCOL),source_sha256=sources,source_component=dict(path=relative(args.component),
        compact_sha256=sha(args.component/'calorimeter.xml'),expected_sha256=sha(args.component/'expected.json'),materials_sha256=sha(args.component/'materials.xml')),
        geometry=dict(side=1,sectors=list(range(16)),layers=list(range(48)),frame_sectors=16,
          tiled_sensors_per_wedge_layer=112,tiled_sensitive_placements=16*48*112,continuous_sensitive_placements=16*48),
        control=dict(footprint_mm=footprint,thickness_mm=thickness,centre_layer_z_mm=offset,
          removed_primitive_count=len(removed),unchanged_other_hardware=True,
          silicon_volume_mm3_per_wedge_layer=dict(tiled=old_si_volume,continuous=new_si_volume),
          active_area_mm2_per_wedge_layer=dict(tiled=old_active_area,continuous=new_active_area),
          added_silicon_mass_kg=(new_si_volume-old_si_volume)*density/1000*768/1000,
          confound='Adds Si in prior air gaps and activates prior guards; retains spatially nonuniform electronics/films and real wedge seams. Not pure segmentation rebinning.',
          descriptor=DESCRIPTOR_CONTROL),points=points,groups=groups,
        compacts={g:sha(args.work/(g+'.xml')) for g in groups},materials_sha256=sha(args.work/'materials.xml'),local_expected_sha256=sha(args.work/'expected.json'),
        factory=dict(path=relative(libraries[0]),sha256=sha(libraries[0]),components_sha256=sha(args.factory/'libnODDCalorimeterPrototype.components')),
        transport=dict(particle='e-',energy_convention='Native G4 gun kinetic GeV; primary total energy=kinetic+electron rest mass is checked. All visible fractions use requested kinetic energy.',
          field_T=0,physics_list='FTFP_BERT',range_cut_mm=.7,no_analysis_hit_or_event_threshold=True),
        analysis=dict(histogram_max_visible_fraction=.10,histogram_bins=1000,bootstrap_replicates=2000,bootstrap_seed=11893000,
          tail='One frozen cut=.8*meanvisiblefraction from independent100eventcontinuous-C20GeV calibration, excluded from bulk; samecut allenergies/points/geometries.'),
        prepared_script_sha256=sha(__file__))
    save(args.work/'manifest.json',manifest)
    print(json.dumps(dict(points=len(points),bulk_events=sum(r['n'] for rows in groups.values() for r in rows if r['kind']=='response'),control=manifest['control']),indent=2))


def verify(args):
    manifest=json.loads((args.work/'manifest.json').read_text())
    if manifest['protocol_sha256']!=sha(PROTOCOL): raise ValueError('Frozen protocol changed')
    for name,digest in manifest['source_sha256'].items():
        if sha(ROOT/name)!=digest: raise ValueError('Scientific source changed: '+name)
    for geometry,digest in manifest['compacts'].items():
        if sha(args.work/(geometry+'.xml'))!=digest: raise ValueError('Prepared compact changed')
    if sha(args.work/'expected.json')!=manifest['local_expected_sha256']:
        raise ValueError('Prepared inventory changed')
    if sha(args.work/'materials.xml')!=manifest['materials_sha256'] or sha(ROOT/manifest['factory']['path'])!=manifest['factory']['sha256']:
        raise ValueError('Executed material or factory changed')
    components=(ROOT/manifest['factory']['path']).parent/'libnODDCalorimeterPrototype.components'
    if sha(components)!=manifest['factory']['components_sha256']:
        raise ValueError('Executed factory component registration changed')
    return manifest


def _native(args):
    manifest=verify(args)
    import ROOT as R,dd4hep
    sys.path.insert(0,str(ROOT/'tools/calorimeter_hardware'))
    from edge_native import native_capacity
    R.gROOT.SetBatch(True)
    if R.gSystem.Load(str((ROOT/manifest['factory']['path']).resolve()))<0: raise RuntimeError('Factory load failed')
    detector=dd4hep.Detector.getInstance();detector.fromXML(str((args.work/(args.geometry+'.xml')).resolve()))
    manager=detector.manager();mm=float(dd4hep.mm)
    top=next(manager.GetTopVolume().GetNode(i).GetVolume() for i in range(manager.GetTopVolume().GetNdaughters()) if str(manager.GetTopVolume().GetNode(i).GetVolume().GetName())=='EDGE')
    if top.GetNdaughters()!=784: raise ValueError('Full positive layer/frame replicas absent')
    regions={};parents=set()
    for i in range(top.GetNdaughters()):
        node=top.GetNode(i);ids={str(p.first):int(p.second) for p in dd4hep.PlacedVolume(node).volIDs()}
        tag=str(node.GetVolume().GetName());key=(tag,ids['side'],ids['sector'],ids['layer'])
        if key in parents or ids['side']!=1 or not 0<=ids['sector']<16 or not 0<=ids['layer']<48: raise ValueError('Invalid replica IDs')
        parents.add(key);regions[tag]=node.GetVolume()
    layer=regions['edge_layer'];sensitive=0;silicon_volume=0.;mass=0.
    for i in range(layer.GetNdaughters()):
        node=layer.GetNode(i);volume=node.GetVolume();material=volume.GetMaterial()
        cap=native_capacity(volume.GetShape())/mm**3
        mass+=cap*material.GetDensity()/1000
        name=str(volume.GetName())
        if args.geometry=='continuous' and name=='continuous_sensitive_sheet':
            silicon_volume+=cap;sensitive+=1
            target=manifest['control']['silicon_volume_mm3_per_wedge_layer']['continuous']
            if not math.isclose(cap,target,rel_tol=1e-10): raise ValueError('Native control sheet volume mismatch')
        if args.geometry=='tiled' and (name.endswith('_active') or name.endswith('_guard')):
            silicon_volume+=cap
            if name.endswith('_active'): sensitive+=1
    target=manifest['control']['silicon_volume_mm3_per_wedge_layer'][args.geometry]
    if not math.isclose(silicon_volume,target,rel_tol=1e-9): raise ValueError('Native silicon volume mismatch')
    expected_sensors=112 if args.geometry=='tiled' else 1
    if sensitive!=expected_sensors: raise ValueError('Native sensitive inventory mismatch')
    readout_probes=0
    if args.geometry=='continuous':
        readout=detector.readout('EDGEHits');seg=readout.segmentation();decoder=readout.idSpec().decoder()
        for sector in range(16):
            for layer_id in (0,47):
                parent=8|(1<<8)|(sector<<10)|(layer_id<<14)
                for x,y in [(140,0),(1139,48),(2000,-350),(2000,350)]:
                    point=dd4hep.Position(x*mm,y*mm,0)
                    cid=int(seg.cellID(point,point,parent))
                    fields=decode_control(cid)
                    if (fields['system'],fields['side'],fields['sector'],fields['layer'],fields['module'])!=(8,1,sector,layer_id,0):
                        raise ValueError('Continuous readout lost a parent field')
                    back=seg.position(cid)
                    if abs(back.x()/mm-(5.5*fields['x']+2.75))>1e-9 or abs(back.y()/mm-(5.5*fields['y']+2.75))>1e-9:
                        raise ValueError('Continuous signed-grid round trip failed')
                    readout_probes+=1
    layer.CheckOverlaps(1e-5*mm)
    overlaps=manager.GetListOfOverlaps()
    overlap_count=int(overlaps.GetEntries()) if overlaps else 0
    if overlap_count: raise RuntimeError('Native layer overlaps: '+str(overlap_count))
    frame=regions['edge_frame'];frame_mass=0
    for i in range(frame.GetNdaughters()):
        volume=frame.GetNode(i).GetVolume();frame_mass+=native_capacity(volume.GetShape())/mm**3*volume.GetMaterial().GetDensity()/1000
    report=dict(status='PASS',geometry=args.geometry,physical_layer_replicas=768,physical_frame_replicas=16,
       sensitive_per_layer_wedge=sensitive,physical_sensitive_placements=sensitive*768,
       logical_layer_mass_g=mass,positive_end_mass_kg=(mass*768+frame_mass*16)/1000,
       silicon_volume_mm3_per_layer_wedge=silicon_volume,logical_layer_overlap_count=overlap_count,
       overlap_tolerance_mm=1e-5,continuous_signed_grid_probes=readout_probes,overlap_scope='Complete logical layer; retained sector/layer/frame transforms are source-identical. Full-detector overlap acceptance is not claimed.',
       compact_sha256=manifest['compacts'][args.geometry],factory_sha256=manifest['factory']['sha256'],ROOT=str(R.gROOT.GetVersion()))
    return report


def native(args):
    import ROOT as R,dd4hep
    R.EnableImplicitMT(1)
    try:
        report=_native(args)
    finally:
        R.DisableImplicitMT()
        dd4hep.Detector.destroyInstance()
    report['normal_cleanup_completed']=True
    save(args.work/(args.geometry+'-native.json'),report)
    print(json.dumps(report,indent=2))


def run(args):
    manifest=verify(args)
    from DDSim.Helper.Random import Random
    random_defaults=Random()
    if random_defaults.enableEventSeed is not False:
        raise ValueError('Per-event reseeding would override macroblock seeds')
    random_source=Path(sys.modules[Random.__module__].__file__)
    seed_provenance=dict(enableEventSeed=False,mode='Explicit native /random/setSeeds perblock; no EventSeeder action',helper_sha256=sha(random_source))
    for g in ('tiled','continuous'):
        report=json.loads((args.work/(g+'-native.json')).read_text())
        if report['status']!='PASS' or not report.get('normal_cleanup_completed') or report['compact_sha256']!=manifest['compacts'][g]: raise ValueError('Native gates not passed')
    rows=manifest['groups'][args.geometry]
    if args.calibration_only:
        rows=[r for r in rows if r['kind']=='calibration']
    elif args.skip_calibration:
        rows=[r for r in rows if r['kind']!='calibration']
    pending=[]
    for row in rows:
        record_path=args.work/(row['id']+'.execution.json')
        if record_path.exists():
            execution_record(args,manifest,row)
            continue
        pending.append(deepcopy(row))
    if not pending: print('All requested samples already complete');return
    point_map={p['id']:p for p in manifest['points']}
    # Each attempt keeps distinct evidence/output paths, including after resume.
    suffix=('calibration' if args.calibration_only else 'bulk')
    attempt=args.work/'attempts'/(args.geometry+'-'+suffix+'-'+str(time.time_ns()))
    attempt.mkdir(parents=True,exist_ok=False)
    macro=attempt/'commands.mac'
    lines=['/gun/particle e-','/gun/position 0 0 0 mm']
    for run_number,row in enumerate(pending):
        row['actual_run_number']=run_number
        row['file']=str((attempt/(row['id']+'.edm4hep.root')).relative_to(args.work))
        lines += ['/ddg4/EDM4hepOutput/Output '+str((args.work/row['file']).resolve()),
                  f"/gun/energy {row['energy_GeV']} GeV",'/gun/direction '+' '.join(format(v,'.17g') for v in point_map[row['point_id']]['direction']),
                  '/random/setSeeds '+' '.join(str(v) for v in row['seed_pair']),f"/run/beamOn {row['n']}"]
    macro.write_text('\n'.join(lines)+'\n')
    command=[sys.executable,shutil.which('ddsim'),'--compactFile',str((args.work/(args.geometry+'.xml')).resolve()),'--runType','run','--enableG4Gun',
        '--macroFile',str(macro.resolve()),'--numberOfThreads','1','--random.seed','11839999','--physics.list','FTFP_BERT','--physics.rangecut','0.7',
        '--part.userParticleHandler','','--outputConfig.forceEDM4HEP','--outputFile',str((attempt/'unused.edm4hep.root').resolve())]
    environment=os.environ.copy();factory=(ROOT/manifest['factory']['path']).parent
    for name in ('DD4HEP_LIBRARY_PATH','DYLD_LIBRARY_PATH','LD_LIBRARY_PATH'): environment[name]=str(factory)+os.pathsep+environment.get(name,'')
    snapshot=attempt/'producer.py';shutil.copyfile(__file__,snapshot)
    logfile=attempt/'transport.log';start=time.monotonic()
    from podio import root_io
    completed=set()
    records={}
    def observe(final=False, exit_code=None):
        text=logfile.read_text(errors='replace')
        finished={int(n) for n in re.findall(r'Finished run (\d+) after',text)}
        for row in pending:
            output=args.work/row['file']
            if row['id'] in completed and not final:
                continue
            if row['id'] not in completed or final:
                if row['actual_run_number'] not in finished or not output.exists(): continue
                try:
                    count=sum(1 for _ in root_io.Reader(str(output)).get('events'))
                except Exception:
                    if final: raise
                    continue
                if count!=row['n']:
                    if final: raise RuntimeError('Incomplete finished run: '+row['id'])
                    continue
                if row['id'] not in completed:
                    completed.add(row['id'])
                    records[row['id']]=dict(sample=row,exit_code=0,block_completed=True,seed_provenance=seed_provenance,
                    group_exit_code=None,command=command,log_file=relative(logfile),macro_file=relative(macro),producer_file=relative(snapshot),macro_sha256=sha(macro),producer_sha256=sha(snapshot),
                    compact_sha256=manifest['compacts'][args.geometry],protocol_sha256=manifest['protocol_sha256'],
                    checkpoint_output_sha256=sha(output))
                records[row['id']].update(output_sha256=sha(output),output_bytes=output.stat().st_size,
                    final_output_verified=final,verified_event_count=count)
            record=records[row['id']]
            if 'EventSeeder added' in text:
                raise RuntimeError('Unexpected per-event seeder in execution')
            engine=re.search(r'Reused HepRandom engine instance (\w+)',text)
            record['seed_provenance']['actual_engine']=engine.group(1) if engine else None
            record.update(group_wall_seconds=time.monotonic()-start,group_exit_code=exit_code,
                maximum_resident_set_size_bytes=(int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)*(1 if platform.system()=='Darwin' else 1024)) if final else None,rss_measurement='Maximum terminated child RSS from getrusage; fresh controller process, DDsim transport child',log_sha256=sha(logfile))
            save(args.work/(row['id']+'.execution.json'),record)
    with logfile.open('w') as log:
        process=subprocess.Popen(command,env=environment,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        while process.poll() is None:
            observe()
            time.sleep(5)
    observe(final=True,exit_code=process.returncode)
    if process.returncode: raise RuntimeError('Geant4 macro group failed; completed blocks retained for resume; inspect '+str(logfile))
    if len(completed)!=len(pending): raise RuntimeError('Missing/incomplete per-block ROOT output')
    print(args.geometry,len(pending),'blocks',time.monotonic()-start,'seconds; all blocks recorded')


def decode_control(cell_id):
    def signed(v): return v-65536 if v>=32768 else v
    return dict(system=cell_id&255,side=(cell_id>>8)&3,sector=(cell_id>>10)&15,layer=(cell_id>>14)&63,module=(cell_id>>20)&1023,x=signed((cell_id>>30)&65535),y=signed((cell_id>>46)&65535))


def execution_record(args,manifest,row):
    record=json.loads((args.work/(row['id']+'.execution.json')).read_text())
    sample_keys=('geometry','point_id','energy_GeV','n','kind','seed','seed_pair')
    if any(record['sample'].get(k)!=row.get(k) for k in sample_keys):
        raise ValueError('Sample configuration changed: '+row['id'])
    path=args.work/record['sample']['file']
    if (record['exit_code']!=0 or record.get('group_exit_code') is None
        or sha(path)!=record['output_sha256'] or record['protocol_sha256']!=manifest['protocol_sha256']
        or record['compact_sha256']!=manifest['compacts'][row['geometry']]):
        raise ValueError('Stale or unsuccessful raw artifact: '+row['id'])
    for kind in ('macro','producer','log'):
        if sha(ROOT/record[kind+'_file'])!=record[kind+'_sha256']:
            raise ValueError('Changed '+kind+' evidence: '+row['id'])
    return record


def read_sample(args,manifest,row):
    from podio import root_io
    import numpy as np
    record=execution_record(args,manifest,row);path=args.work/record['sample']['file']
    expected=json.loads((args.work/'expected.json').read_text())
    modules={m['index']:m for m in expected['modules']};catalog={(m['index'],*p['key']):p for m in expected['modules'] for p in m['pads']}
    replicas={(r['sector'],r['layer']):r for r in expected['replicas'] if r['side']==1 and r['region']=='edge_layer'}
    point=next(p for p in manifest['points'] if p['id']==row['point_id'])
    energies=[];layers=[];seen=set();hit_count=0;max_residual=0.;primary_total=[]
    for frame in root_io.Reader(str(path)).get('events'):
        header=frame.get('EventHeader')
        if len(header)!=1: raise ValueError('Missing unique EventHeader')
        key=(int(header[0].getRunNumber()),int(header[0].getEventNumber()))
        if key in seen or key[0]!=record['sample']['actual_run_number'] or key[1]!=len(energies): raise ValueError('Run/event block mismatch')
        seen.add(key)
        primaries=[p for p in frame.get('MCParticles') if p.getGeneratorStatus()==1 and len(p.getParents())==0]
        if len(primaries)!=1 or primaries[0].getPDG()!=11: raise ValueError('Wrong primary')
        primary=primaries[0];momentum=primary.getMomentum();pv=[momentum.x,momentum.y,momentum.z];norm=math.sqrt(sum(v*v for v in pv))
        energy_error = abs(norm-row['energy_GeV']) if row['kind']=='pilot' else abs(primary.getEnergy()-primary.getMass()-row['energy_GeV'])
        if energy_error>1e-6 or sum((v/norm-t)**2 for v,t in zip(pv,point['direction']))>1e-16:
            raise ValueError('Primary energy/direction mismatch')
        primary_total.append(float(primary.getEnergy()))
        event_layers=[0.]*48
        for hit in frame.get('EDGEHits'):
            cid=int(hit.getCellID());f=decode(cid) if row['geometry']=='tiled' else decode_control(cid)
            if f['system']!=8 or f['side']!=1 or not 0<=f['sector']<16 or not 0<=f['layer']<48: raise ValueError('Hit parent ID outside full positive endcap')
            if row['geometry']=='tiled':
                pad=catalog.get((f['module'],f['x'],f['y']))
                if pad is None or cid>>42: raise ValueError('Unknown tiled electrode')
                module=modules[f['module']]
                local=[module['center_mm'][0]+pad['reference_mm'][0],module['center_mm'][1]+pad['reference_mm'][1],sensor_offset(expected,f['module'])]
            else:
                if f['module']!=0 or cid>>62: raise ValueError('Invalid continuous-sheet ID')
                local=[5.5*f['x']+2.75,5.5*f['y']+2.75,manifest['control']['centre_layer_z_mm']]
            replica=replicas[(f['sector'],f['layer'])]
            global_position=[replica['center_mm'][i]+sum(replica['frame'][j][i]*local[j] for j in range(3)) for i in range(3)]
            p=hit.getPosition();error=max(abs(v-t) for v,t in zip([p.x,p.y,p.z],global_position));max_residual=max(max_residual,error)
            if error>.002: raise ValueError('Hit reference position inconsistent with native source geometry')
            energy=float(hit.getEnergy())
            if not math.isfinite(energy) or energy<=0: raise ValueError('Invalid raw hit energy')
            for contribution in hit.getContributions():
                if not math.isfinite(float(contribution.getTime())) or not math.isfinite(float(contribution.getEnergy())):
                    raise ValueError('Invalid raw contribution payload')
            event_layers[f['layer']]+=energy;hit_count+=1
        layers.append(event_layers);energies.append(math.fsum(event_layers))
    if len(energies)!=row['n']: raise ValueError('Event denominator mismatch: '+row['id'])
    values=np.asarray(energies,dtype=float);longitudinal=np.asarray(layers,dtype=float)
    return values,longitudinal,dict(saved_hits=hit_count,occupied_layers=np.flatnonzero(longitudinal.sum(axis=0)>0).tolist(),
        maximum_cell_reference_residual_mm=max_residual,invalid_ids=0,primary_total_energy_GeV_min=min(primary_total),primary_total_energy_GeV_max=max(primary_total)),record


def moments(values):
    return dict(n=len(values),sum_E=math.fsum(float(v) for v in values),sum_E2=math.fsum(float(v)**2 for v in values),
                sum_E3=math.fsum(float(v)**3 for v in values),sum_E4=math.fsum(float(v)**4 for v in values))


def sensitive_defaults():
    from DDSim.Helper.Action import Action
    from DDSim.Helper.Filter import Filter
    from DDSim.Helper.Random import Random
    action,filtering,random=Action(),Filter(),Random()
    if (action.calo!='Geant4ScintillatorCalorimeterAction' or action.mapActions
        or filtering.calo!='edep0' or filtering.mapDetFilter
        or filtering.filters['edep0']!={'name':'EnergyDepositMinimumCut/Cut0','parameter':{'Cut':0.0}}
        or random.enableEventSeed is not False):
        raise ValueError('Installed sensitive/seed defaults differ from executed conditions')
    return dict(action=action.calo,filter=filtering.calo,filter_definition=filtering.filters['edep0'],
        action_map=action.mapActions,filter_map=filtering.mapDetFilter,enableEventSeed=False,
        helper_sha256={c.__name__:sha(sys.modules[c.__module__].__file__) for c in (Action,Filter,Random)},
        analysis_hit_threshold=None,analysis_event_selection=None,
        distinction='Cut0 is the intrinsic step energy-deposit filter, separate from the 0.7mm secondary production range cut. No additional analysis energy threshold.')


def sensitive(args):
    """One excluded event checks actual G4 Silicon Birks constant, same materials."""
    manifest=verify(args)
    producer=args.work/'sensitive-diagnostic-producer.py';shutil.copyfile(__file__,producer)
    import ROOT as R
    from DDSim.DD4hepSimulation import DD4hepSimulation
    defaults=sensitive_defaults()
    R.gSystem.Load(str(ROOT/manifest['factory']['path']))
    include=Path(shutil.which('geant4-config')).resolve().parents[1]/'include'
    R.gInterpreter.AddIncludePath(str(include));R.gInterpreter.AddIncludePath(str(include/'Geant4'))
    R.gInterpreter.Declare('''
#include "G4Material.hh"
#include "G4IonisParamMat.hh"
#include "G4SystemOfUnits.hh"
double nodd_actual_silicon_birks_mm_per_MeV() {
 const auto* m=G4Material::GetMaterial("Silicon",false);
 if(!m) throw std::runtime_error("Silicon material missing");
 return m->GetIonisation()->GetBirksConstant()/(mm/MeV);
}
''')
    tree=ET.parse(args.work/'tiled.xml');detector=tree.getroot().find('detectors/detector')
    for replica in list(detector.findall('replica')):
        if not (replica.get('region')=='edge_layer' and replica.get('sector')=='0' and replica.get('layer')=='0'):
            detector.remove(replica)
    if len(detector.findall('replica'))!=1: raise ValueError('Diagnostic replica selection failed')
    compact=args.work/'sensitive-diagnostic.xml';write_xml(compact,tree)
    sim=DD4hepSimulation();sim.compactFile=[str(compact)];sim.runType='batch';sim.numberOfEvents=1;sim.enableGun=True
    sim.gun.particle='e-';sim.gun.energy='20*GeV';sim.gun.direction=' '.join(str(v) for v in manifest['points'][0]['direction'])
    sim.random.seed=11890001;sim.part.userParticleHandler='';sim.outputConfig.forceEDM4HEP=True
    sim.outputFile=str(args.work/'sensitive-diagnostic.edm4hep.root');sim.physics.list='FTFP_BERT';sim.physics.rangecut=.7
    result=sim.run()
    if result not in (None,0): raise RuntimeError('Sensitive diagnostic transport failed')
    birks=float(R.nodd_actual_silicon_birks_mm_per_MeV())
    if birks!=0: raise ValueError('Unexpected nonzero Silicon Birks constant')
    save(args.work/'sensitive-diagnostic.json',dict(status='PASS',defaults=defaults,birks_constant_mm_per_MeV=birks,
        actual_G4Material_name='Silicon',query='G4Material::GetMaterial(Silicon)->GetIonisation()->GetBirksConstant()/(mm/MeV)',
        scope='One sector/layer diagnostic only, same original logical layer and materials, one event excluded from all response/calibration samples.',
        materials_sha256=sha(args.work/'materials.xml'),compact_sha256=sha(compact),producer_file=relative(producer),producer_sha256=sha(producer)))


def analyze(args):
    import numpy as np
    manifest=verify(args);rows=[r for group in manifest['groups'].values() for r in group]
    calibration=next(r for r in rows if r['kind']=='calibration')
    cal,cal_layers,cal_checks,cal_execution=read_sample(args,manifest,calibration)
    rng=np.random.default_rng(manifest['analysis']['bootstrap_seed']);replicates=manifest['analysis']['bootstrap_replicates']
    reference=float(cal.mean()/20);cut=.8*reference
    if not math.isfinite(reference) or reference<=0 or not math.isfinite(cut) or cut<=0:
        raise ValueError('Calibration mean/cut must be finite and strictly positive')
    cal_boot=cal[rng.integers(0,len(cal),size=(replicates,len(cal)))].mean(axis=1)/20
    cut_boot=.8*cal_boot
    tail_definition=dict(visible_fraction_cut=cut,reference_mean_visible_fraction=reference,
        convention='E_Si/requested gun kinetic energy; strict f_visible<cut for all energies/points/geometries',
        calibration=dict(sample=calibration,moments=moments(cal),checks=cal_checks,execution=public(cal_execution)),
        reference_mean_bootstrap_standard_error=float(cal_boot.std(ddof=1)),reference_cut_bootstrap_percentile95=np.quantile(cut_boot,[.025,.975]).tolist(),
        conditional_intervals='Wilson95% from fixed observed calibration cut; joint bootstrap additionally varies the independent reference cut; bootstrap intervals do not replace Wilson upper bounds at zero tail count.')
    samples=[];tail_replicas=[];sample_ids=[]
    for index,row in enumerate(r for r in rows if r['kind']=='response'):
        values,layer,checks,execution=read_sample(args,manifest,row)
        sample_rng=np.random.default_rng(manifest['analysis']['bootstrap_seed']+1000+index)
        indices=sample_rng.integers(0,len(values),size=(replicates,len(values)));boot=values[indices]
        means=boot.mean(axis=1);widths=boot.std(axis=1,ddof=1)
        undefined=int(np.count_nonzero(means==0));relative_width=float(values.std(ddof=1)/values.mean()) if values.mean()!=0 else None
        bootstrap_width=widths/np.where(means==0,1,means)
        edges=np.linspace(0,row['energy_GeV']*.10,manifest['analysis']['histogram_bins']+1);counts,_=np.histogram(values,bins=edges)
        # numpy includes the final right edge; use explicit overflow convention.
        counts[-1]-=int(np.count_nonzero(values==edges[-1]))
        tail_events=int(np.count_nonzero(values/row['energy_GeV']<cut))
        tail_boot=(boot/row['energy_GeV']<cut_boot[:,None]).mean(axis=1)
        tail_replicas.append(tail_boot);sample_ids.append(row['id'])
        q=np.quantile(values,[.05,.16,.5,.84,.95]).tolist()
        samples.append(dict(id=row['id'],geometry=row['geometry'],point_id=row['point_id'],energy_GeV=row['energy_GeV'],seed=row['seed'],seed_pair=row['seed_pair'],
            moments=moments(values),zero_events=int(np.count_nonzero(values==0)),mean_E_GeV=float(values.mean()),sample_RMS_GeV=float(values.std(ddof=1)),relative_width=relative_width,
            quantiles_GeV=dict(zip(['q05','q16','q50','q84','q95'],q)),tail_events=tail_events,
            bootstrap=dict(replicates=replicates,seed=manifest['analysis']['bootstrap_seed']+1000+index,undefined_width_replicates=undefined,
                relative_width_standard_error=float(bootstrap_width.std(ddof=1)) if undefined==0 else None,
                relative_width_percentile95=np.quantile(bootstrap_width,[.025,.975]).tolist() if undefined==0 else None,
                tail_fraction_with_reference_cut_percentile95=np.quantile(tail_boot,[.025,.975]).tolist()),
            histogram=dict(edges_GeV=edges.tolist(),counts=counts.tolist(),underflow=int(np.count_nonzero(values<edges[0])),overflow=int(np.count_nonzero(values>=edges[-1])),normalization='all generated events; zeros retained; no analysis selection'),
            layer_energy=dict(sum_GeV=layer.sum(axis=0).tolist(),sum_GeV2=(layer*layer).sum(axis=0).tolist(),scope='Per-layer means/SE only; no longitudinal covariance claim'),
            checks=checks,execution=public(execution)))
    import ROOT as R
    factory_cache=((ROOT/manifest['factory']['path']).parent/'CMakeCache.txt').read_text()
    configured_dd4hep=re.search(r'^DD4hep_DIR:PATH=(.+)$',factory_cache,re.MULTILINE)
    version_file=Path(os.environ.get('DD4hep_DIR',configured_dd4hep.group(1) if configured_dd4hep else ''))/'DD4hepConfigVersion.cmake'
    dd4hep_match=re.search(r'set\(PACKAGE_VERSION "([^"]+)"\)',version_file.read_text()) if version_file.exists() else None
    runtime=dict(Python=platform.python_version(),ROOT=str(R.gROOT.GetVersion()),Geant4=subprocess.check_output(['geant4-config','--version'],text=True).strip(),DD4hep=dd4hep_match.group(1) if dd4hep_match else None,NumPy=np.__version__,bootstrap_bit_generator=type(rng.bit_generator).__name__,ddsim_entrypoint_sha256=sha(shutil.which('ddsim')))
    sensitive_report=json.loads((args.work/'sensitive-diagnostic.json').read_text())
    if (sensitive_report['status']!='PASS' or sensitive_report['materials_sha256']!=manifest['materials_sha256']
        or sensitive_report['defaults']!=sensitive_defaults() or sensitive_report['birks_constant_mm_per_MeV']!=0
        or sha(ROOT/sensitive_report['producer_file'])!=sensitive_report['producer_sha256']
        or sha(args.work/'sensitive-diagnostic.xml')!=sensitive_report['compact_sha256']):
        raise ValueError('Sensitive-material defaults probe is missing/stale')
    artifact_paths=[args.work/'manifest.json',args.work/'tiled.xml',args.work/'continuous.xml',args.work/'materials.xml',args.work/'expected.json',
        ROOT/manifest['factory']['path'],(ROOT/manifest['factory']['path']).parent/'libnODDCalorimeterPrototype.components',PROTOCOL,
        args.work/'sensitive-diagnostic.json',args.work/'sensitive-diagnostic.xml',args.work/'sensitive-diagnostic.edm4hep.root',args.work/'sensitive-diagnostic.log',
        ROOT/sensitive_report['producer_file'],
        args.work/'pilot-checks.json',args.work/'pilot-tiled.edm4hep.root',args.work/'pilot-tiled.log',
        args.work/'tiled-native.json',args.work/'continuous-native.json']
    evidence_logs=set()
    for row in rows:
        record=json.loads((args.work/(row['id']+'.execution.json')).read_text())
        artifact_paths += [args.work/record['sample']['file'],args.work/(row['id']+'.execution.json'),ROOT/record['log_file'],ROOT/record['macro_file'],ROOT/record['producer_file']]
        evidence_logs.add(ROOT/record['log_file'])
    for path in evidence_logs:
        text=path.read_text()
        if ("Setting up SD for EDGE with Geant4ScintillatorCalorimeterAction" not in text
            or "Adding default filter 'edep0' to sensitive detector for 'EDGE'" not in text
            or not re.search(r'GlobalRangeCut.*0\.700000.*mm',text)):
            raise ValueError('Executed action/filter/range conditions not confirmed in '+str(path))
    artifacts={relative(p):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(artifact_paths))}
    result=dict(status='PROTOTYPE full-positive-end raw-Geant4 electron characterization; no digitization',runtime=runtime,artifacts=artifacts,pilot=json.loads((args.work/'pilot-checks.json').read_text()),manifest=public(manifest),points=manifest['points'],samples=samples,
        sensitive_response=sensitive_report,tail_definition=tail_definition,
        joint_tail_bootstrap=dict(sample_ids=sample_ids,covariance=np.cov(np.stack(tail_replicas,axis=1),rowvar=False,ddof=1).tolist(),
            units='tail fraction squared',replicates=replicates,calibration_seed=manifest['analysis']['bootstrap_seed'],
            sample_seeds=[s['bootstrap']['seed'] for s in samples],
            convention='Independent event resampling per sample; each replicate shares the same independent calibration-cut resample across all samples. Sample order labels both covariance axes.',
            caveat='An observed zero tail may have zero bootstrap variance; Wilson95 upper bounds remain required.'),
        native={g:json.loads((args.work/(g+'-native.json')).read_text()) for g in ('tiled','continuous')},
        analysis_script_sha256=sha(__file__),limitations=['Independent unpaired populations; no event covariance across geometry cases.',
        'Continuous sheet adds silicon and activates guards while retaining nonuniform module electronics: not a pure readout segmentation comparison.',
        'Other detector subsystems/opposite end absent; raw visible spread is not reconstructed resolution or detector acceptance.',
        'Undefined zero-denominator widths/bootstrap replicates are retained as null with explicit counts.'])
    save(args.output,result);print('Summarized',len(samples),'samples',sum(s['moments']['n'] for s in samples),'bulk events; tailcut',cut)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['prepare','native','sensitive','run','analyze'])
    p.add_argument('--component',type=Path,default=ROOT/'build/tiled-endcap-geometry-check');p.add_argument('--work',type=Path,default=ROOT/'build/nodd-tiling-response')
    p.add_argument('--factory',type=Path,default=ROOT/'build/tiled-endcap-view/factory');p.add_argument('--geometry',choices=['tiled','continuous'])
    p.add_argument('--calibration-only',action='store_true');p.add_argument('--skip-calibration',action='store_true')
    p.add_argument('--output',type=Path,default=ROOT/'docs/validation/issue117/previews/nodd-tiling-response.json')
    a=p.parse_args()
    if a.stage in ('native','run') and not a.geometry: p.error('--geometry is required')
    {'prepare':prepare,'native':native,'sensitive':sensitive,'run':run,'analyze':analyze}[a.stage](a)


if __name__=='__main__': main()
