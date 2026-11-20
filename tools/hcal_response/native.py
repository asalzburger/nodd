#!/usr/bin/env python3
"""Audit reused ROOT HCAL geometry, exact compound cores and bounded IP material rays.

Checks each distinct native logical mother once. ROOT overlap tests are numerical
geometry checks, not a proof of mechanical clearance or shower containment.
"""
import argparse
from array import array
from collections import Counter, defaultdict
from functools import lru_cache
import json
import math
from pathlib import Path
import platform
import random
import subprocess
from model import ROOT, load, sha


def shape_capacity(shape,unit):
    kind=str(shape.ClassName())
    if kind=='TGeoBBox':return 8*shape.GetDX()*shape.GetDY()*shape.GetDZ()/unit**3
    if kind in ('TGeoTube','TGeoTubeSeg'):
        fraction=1 if kind=='TGeoTube' else (shape.GetPhi2()-shape.GetPhi1())/360
        return 2*math.pi*(shape.GetRmax()**2-shape.GetRmin()**2)*shape.GetDz()*fraction/unit**3
    if kind in ('TGeoArb8','TGeoXtru'):return float(shape.Capacity())/unit**3
    if kind=='TGeoCompositeShape':
        b=shape.GetBoolNode();a=shape_capacity(b.GetLeftShape(),unit);c=shape_capacity(b.GetRightShape(),unit)
        if str(b.ClassName())=='TGeoUnion':return a+c # exact because original cores are disjoint
        if str(b.ClassName())=='TGeoSubtraction':return a-c # all module cutters are contained/disjoint
    raise ValueError('unsupported module capacity '+kind)


def boolean_contract(shape,depth=0):
    if str(shape.ClassName())!='TGeoCompositeShape' or str(shape.GetBoolNode().ClassName())!='TGeoUnion':return dict(nodes=0,nonidentity_left=0,max_depth=depth)
    b=shape.GetBoolNode();m=b.GetLeftMatrix()
    nonidentity=any(abs(m.GetTranslation()[i])>1e-12 for i in range(3)) or any(abs(m.GetRotationMatrix()[i*3+j]-(1 if i==j else 0))>1e-12 for i in range(3) for j in range(3))
    a=boolean_contract(b.GetLeftShape(),depth+1);c=boolean_contract(b.GetRightShape(),depth+1)
    return dict(nodes=1+a['nodes']+c['nodes'],nonidentity_left=int(nonidentity)+a['nonidentity_left']+c['nonidentity_left'],max_depth=max(a['max_depth'],c['max_depth']))


def compound_leaves(R,shape,matrix=None):
    matrix=matrix if matrix is not None else R.TGeoHMatrix()
    if str(shape.ClassName())=='TGeoCompositeShape' and str(shape.GetBoolNode().ClassName())=='TGeoUnion':
        b=shape.GetBoolNode()
        for child,placement in ((b.GetLeftShape(),b.GetLeftMatrix()),(b.GetRightShape(),b.GetRightMatrix())):
            m=R.TGeoHMatrix(matrix);m.Multiply(placement)
            yield from compound_leaves(R,child,m)
    else:yield shape,matrix


def part_contains(point, part, centered_depth):
    """Independent source-domain membership for axis-aligned sensitive boxes."""
    if part['shape_kind'] != 'box' or part['frame'] != [[1,0,0],[0,1,0],[0,0,1]]:
        raise ValueError('sensitive primitive/frame outside explicit unit contract')
    center=part['center_mm'][:];center[2]-=centered_depth
    local=[v-c for v,c in zip(point,center)];dims=part['dimensions_mm']
    if any(abs(v)>dims[key]/2 for v,key in zip(local,('sx','sy','sz'))):return False
    for cut in part['cuts']:
        if cut['kind']!='tube' or cut['frame']!=[[1,0,0],[0,1,0],[0,0,1]]:
            raise ValueError('sensitive cut outside explicit cylindrical-recess contract')
        x,y,z=[v-c for v,c in zip(local,cut['center_mm'])];d=cut['dimensions_mm']
        if d['rmin']!=0:raise ValueError('sensitive annular recess unsupported')
        if x*x+y*y<=d['rmax']**2 and abs(z)<=d['length']/2:return False
    return True


def part_boundary(point,part,centered_depth):
    """Identify exact source surfaces; their floating CSG convention is backend-specific.

    The1e-12mm classification scale is far below every declared geometry or
    membership tolerance. Both±1e-4mm neighbours are checked analytically.
    """
    center=part['center_mm'][:];center[2]-=centered_depth
    local=[v-c for v,c in zip(point,center)];d=part['dimensions_mm'];tiny=1e-12
    if any(abs(v)>d[key]/2+tiny for v,key in zip(local,('sx','sy','sz'))):return False
    if any(abs(abs(v)-d[key]/2)<=tiny for v,key in zip(local,('sx','sy','sz'))):return True
    for cut in part['cuts']:
        x,y,z=[v-c for v,c in zip(local,cut['center_mm'])];cd=cut['dimensions_mm']
        radial=math.hypot(x,y)
        if abs(z)<=cd['length']/2+tiny and abs(radial-cd['rmax'])<=tiny:return True
        if radial<=cd['rmax']+tiny and abs(abs(z)-cd['length']/2)<=tiny:return True
    return False


def compare_compound(R,dd4hep,volume,readout,unit_scale,unit_id,unit_definition):
    u=unit_definition;parts=[p for p in u['parts'] if p['role']=='sensitive']
    size=u['fixture']['carrier_size_mm'];half_depth=size[2]/2
    offset=u['active_offset_from_carrier_center_mm'];native=load('_hcal46_module_native','tools/hcal_readout/native.py')
    leaves=list(compound_leaves(R,volume.GetShape()));errors=[];contract=boolean_contract(volume.GetShape())
    count=len(parts)
    if not 1<=count<=72:raise ValueError('compound unit physical channel capacity')
    if contract['nonidentity_left'] or contract['nodes']!=count-1 or contract['max_depth']>math.ceil(math.log2(count)):
        errors.append('compound boolean conversion contract')
    if len(leaves)!=count:raise ValueError('compound leaf count differs from physical unit')
    for (solid,m),part in zip(leaves,parts):
        if native.dimension_errors(solid,part,unit_scale):errors.append('core shape/cut dimensions '+part['name'])
        expected=part['center_mm'][:];expected[2]-=half_depth
        if any(abs(m.GetTranslation()[i]/unit_scale+offset[i]-expected[i])>1e-8 for i in range(3)):
            errors.append('compound core transform '+part['name'])
    total=shape_capacity(volume.GetShape(),unit_scale)
    source_volume=sum(part['volume_mm3'] for part in parts)
    if not math.isclose(total,source_volume,rel_tol=1e-12,abs_tol=1e-7):errors.append('compound exact volume/mass')
    probes=[];eps=1e-4
    for part in parts:
        x,y,z=part['center_mm'];z-=half_depth;d=part['dimensions_mm'];hx,hy,hz=(d[k]/2 for k in ('sx','sy','sz'))
        for dx,dy in ((0,0),(hx-eps,0),(hx+eps,0),(-hx-eps,0),(0,hy+eps),(hx-eps,hy-eps)):
            for dz in (-hz-eps,-hz+eps,0,hz-eps,hz+eps):probes.append([x+dx,y+dy,z+dz])
        for cut in part['cuts']:
            cx,cy,cz=cut['center_mm'];cd=cut['dimensions_mm'];cut_front=cz-cd['length']/2
            for radius in (0,cd['rmax']-eps,cd['rmax']+eps):
                for azimuth in (0,math.pi/3,math.pi):
                    for zz in (cut_front-eps,cut_front+eps,cz+cd['length']/2-eps):
                        probes.append([x+cx+radius*math.cos(azimuth),y+cy+radius*math.sin(azimuth),z+zz])
    # Retain all original unit0 fixed controls and random population. Every new
    # unit adds its actual core/recess edges and 256 seeded carrier-volume probes.
    if unit_id==0:
        probes.extend([[x,y,z] for x in (-190,-183,-171.5,-153,-15,0,15,153,171.5,183,190) for y in (-120,-102,-87,0,78,100,120) for z in (-5.5,-4,-2.5,0)])
    else:
        probes.extend([[x,y,z] for x in (-size[0]/2,0,size[0]/2) for y in (-120,-104,-12,78,100,120) for z in (-5.5,-4,-2.5,0)])
    rng=random.Random(45172+unit_id)
    probes.extend([[rng.uniform(-size[0]/2,size[0]/2),rng.uniform(-size[1]/2,size[1]/2),rng.uniform(-half_depth,half_depth)] for _ in range(2000 if unit_id==0 else 256)])
    compound=volume.GetShape();matched=0;active=0;boundary_probes=0;segmentation=readout.segmentation();decoder=readout.idSpec().decoder()
    raw=(13 if str(readout.name())=='HCALBarrelHits' else 14|1<<8)|(unit_id<<42)
    for point in probes:
        vector=array('d',((v-o)*unit_scale for v,o in zip(point,offset)))
        inside=bool(compound.Contains(vector));original=[];boundary=False
        for (solid,m),part in zip(leaves,parts):
            if part_boundary(point,part,half_depth):
                # Preserve inherited exact-surface controls with their original
                # native-leaf oracle; dimensions/transforms were checked above.
                boundary=True;local=array('d',[0,0,0]);m.MasterToLocal(vector,local)
                contains=bool(solid.Contains(local))
            else:contains=part_contains(point,part,half_depth)
            if contains:original.append(part)
        boundary_probes+=int(boundary)
        if inside!=bool(original) or len(original)>1:
            if len(errors)<30:errors.append('compound/source containment disagreement '+repr(point))
            continue
        matched+=1
        if inside:
            pos=dd4hep.Position(*((v-o)*unit_scale for v,o in zip(point,offset)));cell=int(segmentation.cellID(pos,pos,raw))
            part=original[0];returned=segmentation.position(cell)
            if int(decoder.get(cell,'module'))!=part['module'] or int(decoder.get(cell,'sensor'))!=part['sensor'] or int(decoder.get(cell,'unit'))!=unit_id:
                errors.append('compound segmentation component identity')
            expected_center=part['center_mm'][:];expected_center[2]-=half_depth;expected_center=[v-o for v,o in zip(expected_center,offset)]
            if any(abs(v/unit_scale-e)>1e-8 for v,e in zip((returned.x(),returned.y(),returned.z()),expected_center)):
                errors.append('compound segmentation reference position')
            if int(segmentation.volumeID(cell))!=raw:errors.append('compound logical-to-raw ID')
            active+=1
    centers=[]
    for part in parts:
        v=part['center_mm'][:];v[2]-=half_depth;pos=dd4hep.Position(*((x-o)*unit_scale for x,o in zip(v,offset)))
        centers.append(int(segmentation.cellID(pos,pos,raw)))
    if len(set(centers))!=count:errors.append('physical unit cell bijection')
    source_ids={(part['module'],part['sensor']) for part in parts}
    mapped_ids={(row['module'],row['sensor']) for row in u['channel_map']}
    if source_ids!=mapped_ids or len(mapped_ids)!=count:errors.append('unit channel/source inventory mismatch')
    return dict(errors=errors,unit=unit_id,boolean_contract=contract,leaf_count=len(leaves),exact_volume_mm3=total,source_volume_mm3=source_volume,
                exact_mass_g=total*1.06/1000,probes=len(probes),matched_original_core_contains=matched,
                exact_surface_probes_with_checked_native_leaf_oracle=boundary_probes,analytic_non_surface_probes=len(probes)-boundary_probes,
                active_segmentation_probes=active,unique_center_cells=len(set(centers)),active_offset_from_carrier_center_mm=offset,
                probe_scope='Independent source membership off surfaces; inherited checked-native-leaf oracle on exact source surfaces; every±1e-4mm core/recess boundary neighbour and cell centre; source dimensions/transforms/exclusive mass checked independently')


def compare_passive(R,dd4hep,volumes,active_name,unit_scale,u):
    """Check each original passive part once in its actual unit template."""
    native=load('_hcal46_passive_native','tools/hcal_readout/native.py');parent_name=active_name[:-len('CompoundTiles')]
    parent=volumes[parent_name];size=u['fixture']['carrier_size_mm'];errors=[];count=0;mass=0.
    shape=parent.GetShape()
    if str(shape.ClassName())!='TGeoBBox' or any(abs(v/unit_scale-e/2)>1e-8 for v,e in zip((shape.GetDX(),shape.GetDY(),shape.GetDZ()),size)):
        errors.append('carrier dimensions '+parent_name)
    nodes={str(parent.GetNode(i).GetVolume().GetName()):parent.GetNode(i) for i in range(parent.GetNdaughters())}
    for part in u['parts']:
        if part['role']=='sensitive':continue
        name=parent_name+part['name'];node=nodes.get(name)
        if node is None:errors.append('missing passive part '+name);continue
        count+=1;v=node.GetVolume();matrix=node.GetMatrix()
        if native.dimension_errors(v.GetShape(),part,unit_scale):errors.append('passive dimensions/cuts '+name)
        want=part['center_mm'][:];want[2]-=size[2]/2
        if any(abs(matrix.GetTranslation()[i]/unit_scale-want[i])>1e-8 for i in range(3)):
            errors.append('passive transform '+name)
        if any(abs(matrix.GetRotationMatrix()[j*3+i]-part['frame'][i][j])>1e-10 for i in range(3) for j in range(3)):
            errors.append('passive rotation '+name)
        material=v.GetMaterial()
        if str(material.GetName())!=part['material']:errors.append('passive material '+name)
        measured=shape_capacity(v.GetShape(),unit_scale)
        if not math.isclose(measured,part['volume_mm3'],rel_tol=1e-12,abs_tol=1e-7):errors.append('passive exclusive volume '+name)
        measured_mass=measured*float(material.GetDensity())/1000
        if not math.isclose(measured_mass,part['mass_g'],rel_tol=2e-8,abs_tol=1e-7):errors.append('passive mass '+name)
        mass+=measured_mass
    return dict(errors=errors,parts_checked=count,passive_mass_g=mass,scope='All source passive dimensions,cuts,placements,materials and exclusive mass in this reused template')


def trace(manager,dd4hep,eta,phi,max_length_mm):
    unit=float(dd4hep.mm);direction=[math.cos(phi)/math.cosh(eta),math.sin(phi)/math.cosh(eta),math.tanh(eta)]
    manager.InitTrack(0,0,0,*direction);nav=manager.GetCurrentNavigator();distance=0;steps=0;materials=defaultdict(float);interaction=0;paths=set();layers=set()
    while not nav.IsOutside() and distance<max_length_mm:
        node=nav.GetCurrentNode()
        if not node:break
        volume=node.GetVolume();mat=volume.GetMaterial();path=str(nav.GetPath());sensitive=bool(dd4hep.Volume(volume).isSensitive())
        branch_ids={}
        if sensitive:
            for up in range(nav.GetLevel()+1):
                ancestor=node if up==0 else nav.GetMother(up)
                if ancestor:branch_ids.update({str(pair.first):int(pair.second) for pair in dd4hep.PlacedVolume(ancestor).volIDs()})
        nav.FindNextBoundaryAndStep((max_length_mm-distance)*unit);length=float(nav.GetStep())/unit
        if not math.isfinite(length) or length<=0:raise RuntimeError('nonpositive ROOT boundary step at '+path)
        distance+=length;steps+=1
        if str(volume.GetName())!=str(manager.GetTopVolume().GetName()):
            materials[str(mat.GetName())]+=length
            nuclear=float(mat.GetIntLen())/unit
            if nuclear>0:interaction+=length/nuclear
        if sensitive:
            paths.add(path)
            if all(k in branch_ids for k in ('system','side','layer')):layers.add((branch_ids['system'],branch_ids['side'],branch_ids['layer']))
            else:raise RuntimeError('sensitive ray branch missing layer identity '+path)
        if steps>100000:raise RuntimeError('bounded ROOT ray exceeded100000steps')
    return dict(eta=eta,phi_rad=phi,material_path_mm=dict(materials),l_over_lambda=interaction,sensitive_crossings=len(paths),active_layers=[list(v) for v in sorted(layers)],active_layer_count=len(layers),boundary_steps=steps,distance_mm=distance)


def aggregate_materials(manager,dd4hep,unit_scale,expected):
    """Count instantiated source-independent native non-Air material by graph reuse.

    Non-Air parents in this prototype have exclusive shapes and no material
    daughters. Air/assembly containers contribute only their physical children.
    Multiplicity caching avoids expanding millions of repeated passive paths.
    """
    volumes={str(volume.GetName()):volume for volume in manager.GetListOfVolumes()}
    ps=float(next(volume.GetMaterial() for volume in volumes.values()
                  if not volume.IsAssembly() and str(volume.GetMaterial().GetName())=='PSHost').GetDensity())
    if not math.isclose(ps,1.06,rel_tol=1e-12,abs_tol=1e-12):
        raise ValueError('ROOT material density convention differs from verified PSHost1.06g/cm3')
    @lru_cache(maxsize=None)
    def ledger(name):
        volume=volumes[name];totals={}
        if not volume.IsAssembly():
            material=volume.GetMaterial();key=str(material.GetName())
            if key!='Air':
                capacity=shape_capacity(volume.GetShape(),unit_scale)
                totals[key]=dict(volume_mm3=capacity,mass_g=capacity*float(material.GetDensity())/1000)
        children=Counter(str(volume.GetNode(i).GetVolume().GetName()) for i in range(volume.GetNdaughters()))
        for child,count in children.items():
            for material,values in ledger(child).items():
                row=totals.setdefault(material,dict(volume_mm3=0.,mass_g=0.))
                for key,value in values.items():row[key]+=count*value
        return totals
    actual=ledger(str(manager.GetTopVolume().GetName()));source=expected['material_totals'];errors=[];differences={}
    if set(actual)!=set(source):errors.append('native/source aggregate material set differs')
    for material in sorted(set(actual)|set(source)):
        if material not in actual or material not in source:continue
        differences[material]={key:actual[material][key]-source[material][key] for key in ('volume_mm3','mass_g')}
        if not math.isclose(actual[material]['volume_mm3'],source[material]['volume_mm3'],rel_tol=1e-10,abs_tol=1e-4):
            errors.append('native/source aggregate volume '+material)
        if not math.isclose(actual[material]['mass_g'],source[material]['mass_g'],rel_tol=2e-8,abs_tol=1e-4):
            errors.append('native/source aggregate mass '+material)
    return dict(status='FAIL' if errors else 'PASS',errors=errors,material_totals=actual,source_material_totals=source,
                differences=differences,total_mass_g=sum(row['mass_g'] for row in actual.values()),
                ROOT_PSHost_density_g_cm3=ps,volume_relative_tolerance=1e-10,mass_relative_tolerance=2e-8,
                volume_absolute_tolerance_mm3=1e-4,mass_absolute_tolerance_g=1e-4,
                cached_logical_subgraphs=ledger.cache_info().currsize,
                scope='Actual instantiated native non-Air box,tube,Arb8,Xtru and exclusive Boolean capacities/masses, counted with physical placement multiplicities; source ledger comparison')


def check(args):
    import ROOT as R
    import dd4hep
    R.EnableImplicitMT(1)
    try:
        R.gROOT.SetBatch(True);R.gRandom.SetSeed(45010);unit=float(dd4hep.mm)
        auditor_hash=sha(__file__);directory=args.directory.resolve();expected=json.loads((directory/'expected.json').read_text());errors=[]
        for name,digest in expected['export_sha256'].items():
            if sha(directory/name)!=digest:raise ValueError('changed exported input '+name)
        if R.gSystem.Load(str(args.library.resolve()))<0:raise RuntimeError('cannot load HCAL prototype library')
        detector=dd4hep.Detector.getInstance();detector.fromXML(str(directory/'detector.xml'));manager=detector.manager()
        volumes={str(v.GetName()):v for v in manager.GetListOfVolumes()};checks={}
        source_units=expected['units'];declared=set();actual={name for name,v in volumes.items() if bool(dd4hep.Volume(v).isSensitive())}
        for key,u in sorted(source_units.items(),key=lambda row:int(row[0])):
            unit_id=int(key)
            for name in u['active_volume_names']:
                if name in declared:raise ValueError('duplicate declared active-volume name')
                declared.add(name)
                if name not in volumes:raise ValueError('missing native active volume '+name)
                ro='HCALBarrelHits' if name.startswith('HCALBarrel') else 'HCALEndcapHits'
                checks[name]=compare_compound(R,dd4hep,volumes[name],detector.readout(ro),unit,unit_id,u)
                checks[name]['passive_check']=compare_passive(R,dd4hep,volumes,name,unit,u)
                errors.extend(name+': '+e for e in checks[name]['errors']+checks[name]['passive_check']['errors'])
        if actual!=declared:errors.append('native sensitive solid set differs from explicit unit manifest')
        # Count expanded sensitive contexts without expanding millions of passive paths.
        @lru_cache(maxsize=None)
        def expanded_sensitive(name):
            v=volumes[name];return int(bool(dd4hep.Volume(v).isSensitive()))+sum(expanded_sensitive(str(v.GetNode(i).GetVolume().GetName())) for i in range(v.GetNdaughters()))
        observed=expanded_sensitive(str(manager.GetTopVolume().GetName()))
        if observed!=expected['raw_sensitive_volumes']:errors.append('native raw sensitive volume multiplicity')
        shape=manager.GetTopVolume().GetShape()
        world=[2*shape.GetDX()/unit,2*shape.GetDY()/unit,2*shape.GetDZ()/unit]
        steel=detector.material('Steel235');nuclear=float(steel.intLength())/unit
        material_check=aggregate_materials(manager,dd4hep,unit,expected);errors.extend(material_check['errors'])
        overlaps=[];checked=[]
        if not args.skip_overlaps:
            # ROOT checks direct daughters of each distinct mother. Every reused
            # placement belongs to one of these mothers; no repeated world traversal.
            manager.GetListOfOverlaps().Clear()
            for name,v in sorted(volumes.items()):
                if v.GetNdaughters():
                    v.CheckOverlaps(1e-5*unit);checked.append(name)
            overlaps=[dict(description=str(o.GetTitle()),penetration_mm=float(o.GetOverlap())/unit) for o in manager.GetListOfOverlaps()]
            if overlaps:errors.append('native overlaps/extrusions '+str(len(overlaps)))
        rays=[]
        if not args.skip_rays:
            for eta in (-3,-2.5,-2,-1.5,-1.2,-1,-.8,-.5,0,.5,.8,1,1.2,1.5,2,2.5,3):
                for phi in (0,.123,math.pi/16,math.pi/4+.077):rays.append(trace(manager,dd4hep,eta,phi,19000))
            t=math.tan(math.pi/expected['config']['sectors']);front=expected['config']['barrel']['front_apothem_mm']
            for eta in (0,.5):
                for sign in (-1,1):
                    for inset in (3.,6.65,7.1,10.,20.):
                        ray=trace(manager,dd4hep,eta,sign*math.atan(t-inset/front),19000)
                        ray['edge_probe_front_face_inset_mm']=inset;rays.append(ray)
        if sha(__file__)!=auditor_hash:raise RuntimeError('native auditor source changed during execution')
        report=dict(status='FAIL' if errors else 'PASS',errors=errors,
            scope='Native logical-template construction,exact-core representation/cell mapping,expanded sensitive multiplicity,distinct-mother ROOT overlap tests and bounded combined-barrel/endcap IP material paths; no engineering acceptance',
            execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),library_sha256=sha(args.library),auditor_sha256=auditor_hash,expected_sha256=sha(directory/'expected.json'),compact_sha256=sha(directory/'detector.xml')),
            compound_checks=checks,aggregate_material_check=material_check,raw_sensitive_volumes=observed,logical_tile_channels=expected['sensitive_tiles'],
            unique_logical_volumes=len(volumes),world_full_xyz_mm=world,Steel235_nuclear_interaction_length_mm=nuclear,
            overlap_tolerance_mm=1e-5,overlap_scope='not run' if args.skip_overlaps else 'each distinct native direct-daughter mother once,includingworld',checked_mothers=checked,overlaps=overlaps,
            material_rays=rays,material_ray_scope='not run' if args.skip_rays else '68 inherited directions plus20 finite edge-neighbour probes; no containment claim')
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
        print(report['status'],observed,'raw sensitive contexts',len(rays),'material rays',len(overlaps),'overlaps')
        return 1 if errors else 0
    finally:
        R.DisableImplicitMT()
        dd4hep.Detector.destroyInstance()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for field in ('directory','library','output'):p.add_argument('--'+field,type=Path,required=True)
    p.add_argument('--skip-overlaps',action='store_true');p.add_argument('--skip-rays',action='store_true');raise SystemExit(check(p.parse_args()))
