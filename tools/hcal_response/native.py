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
from model import ROOT, common, load, sha


def shape_capacity(shape,unit):
    kind=str(shape.ClassName())
    if kind=='TGeoBBox':return 8*shape.GetDX()*shape.GetDY()*shape.GetDZ()/unit**3
    if kind in ('TGeoTube','TGeoTubeSeg'):
        fraction=1 if kind=='TGeoTube' else (shape.GetPhi2()-shape.GetPhi1())/360
        return 2*math.pi*(shape.GetRmax()**2-shape.GetRmin()**2)*shape.GetDz()*fraction/unit**3
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


def compare_compound(R,dd4hep,volume,readout,unit):
    u,_=common();parts=[p for p in u['parts'] if p['role']=='sensitive'];offset=[-168,-87,-4];native=load('_hcal45_module_native','tools/hcal_readout/native.py')
    leaves=list(compound_leaves(R,volume.GetShape()));errors=[];contract=boolean_contract(volume.GetShape())
    if contract['nonidentity_left'] or contract['nodes']!=71 or contract['max_depth']>7:errors.append('compound boolean conversion contract')
    if len(leaves)!=72:raise ValueError('compound leaf count differs from72 physical cores')
    for (solid,m),p in zip(leaves,parts):
        if native.dimension_errors(solid,p,unit):errors.append('core shape/cut dimensions '+p['name'])
        expected=p['center_mm'][:];expected[2]-=6
        if any(abs(m.GetTranslation()[i]/unit+offset[i]-expected[i])>1e-8 for i in range(3)):
            errors.append('compound core transform '+p['name'])
    total=shape_capacity(volume.GetShape(),unit)
    expected=sum(p['volume_mm3'] for p in parts)
    if not math.isclose(total,expected,rel_tol=1e-12,abs_tol=1e-7):errors.append('compound exact volume/mass')
    probes=[];eps=1e-4
    for p in parts:
        x,y,z=p['center_mm'];z-=6
        for dx,dy in ((0,0),(14.85-eps,0),(14.85+eps,0),(-14.85-eps,0),(0,14.85+eps),(14.85-eps,14.85-eps)):
            for dz in (-1.5-eps,-1.5+eps,0,1.5-eps,1.5+eps):probes.append([x+dx,y+dy,z+dz])
        # Cylindrical recess radius3.5mm begins at carrierfront z2.4mm.
        for radius in (0,3.5-eps,3.5+eps):
            for azimuth in (0,math.pi/3,math.pi):
                for zz in (2.4-eps,2.4+eps,3.5-eps):probes.append([x+radius*math.cos(azimuth),y+radius*math.sin(azimuth),zz-6])
    # Reflector channels, board seam, carrier service bay and arbitrary positions.
    probes.extend([[x,y,z] for x in (-190,-183,-171.5,-153,-15,0,15,153,171.5,183,190) for y in (-120,-102,-87,0,78,100,120) for z in (-5.5,-4,-2.5,0)])
    rng=random.Random(45172)
    probes.extend([[rng.uniform(-190,190),rng.uniform(-120,120),rng.uniform(-6,6)] for _ in range(2000)])
    compound=volume.GetShape();matched=0;active=0;segmentation=readout.segmentation();decoder=readout.idSpec().decoder()
    raw=13 if str(readout.name())=='HCALBarrelHits' else 14|1<<8
    for point in probes:
        vector=array('d',((v-o)*unit for v,o in zip(point,offset)));inside=bool(compound.Contains(vector));original=[]
        for (solid,m),p in zip(leaves,parts):
            center=[p['center_mm'][0],p['center_mm'][1],p['center_mm'][2]-6]
            if abs(point[0]-center[0])>14.851 or abs(point[1]-center[1])>14.851 or abs(point[2]-center[2])>1.501:continue
            local=array('d',[0,0,0]);m.MasterToLocal(vector,local)
            if solid.Contains(local):original.append(p)
        if inside!=bool(original) or len(original)>1:
            errors.append('compound/original containment disagreement '+repr(point));continue
        matched+=1
        if inside:
            pos=dd4hep.Position(*((v-o)*unit for v,o in zip(point,offset)));cell=int(segmentation.cellID(pos,pos,raw))
            p=original[0];returned=segmentation.position(cell)
            if int(decoder.get(cell,'module'))!=p['module'] or int(decoder.get(cell,'sensor'))!=p['sensor']:
                errors.append('compound segmentation component identity')
            expected_center=p['center_mm'][:];expected_center[2]-=6;expected_center=[v-o for v,o in zip(expected_center,offset)]
            if any(abs(v/unit-e)>1e-8 for v,e in zip((returned.x(),returned.y(),returned.z()),expected_center)):
                errors.append('compound segmentation reference position')
            if int(segmentation.volumeID(cell))!=raw:errors.append('compound logical-to-raw ID')
            active+=1
    # All72 centres must map bijectively, including both board addresses.
    centers=[]
    for p in parts:
        v=p['center_mm'][:];v[2]-=6;pos=dd4hep.Position(*((x-o)*unit for x,o in zip(v,offset)))
        cell=int(segmentation.cellID(pos,pos,raw));centers.append(cell)
    if len(set(centers))!=72:errors.append('compound72cell bijection')
    return dict(errors=errors,boolean_contract=contract,leaf_count=len(leaves),exact_volume_mm3=total,source_volume_mm3=expected,
                exact_mass_g=total*1.06/1000,probes=len(probes),matched_original_core_contains=matched,
                active_segmentation_probes=active,unique_center_cells=len(set(centers)),active_offset_from_carrier_center_mm=offset,
                probe_scope='Native original leaf shapes and transforms versus balanced union; all core edges,recess boundaries,reflector gaps,board seam,service bay and seeded arbitrary positions')


def trace(manager,dd4hep,eta,phi,max_length_mm):
    unit=float(dd4hep.mm);direction=[math.cos(phi)/math.cosh(eta),math.sin(phi)/math.cosh(eta),math.tanh(eta)]
    manager.InitTrack(0,0,0,*direction);nav=manager.GetCurrentNavigator();distance=0;steps=0;materials=defaultdict(float);interaction=0;paths=set()
    while not nav.IsOutside() and distance<max_length_mm:
        node=nav.GetCurrentNode()
        if not node:break
        volume=node.GetVolume();mat=volume.GetMaterial();path=str(nav.GetPath());sensitive=bool(dd4hep.Volume(volume).isSensitive())
        nav.FindNextBoundaryAndStep((max_length_mm-distance)*unit);length=float(nav.GetStep())/unit
        if not math.isfinite(length) or length<=0:raise RuntimeError('nonpositive ROOT boundary step at '+path)
        distance+=length;steps+=1
        if str(volume.GetName())!=str(manager.GetTopVolume().GetName()):
            materials[str(mat.GetName())]+=length
            nuclear=float(mat.GetIntLen())/unit
            if nuclear>0:interaction+=length/nuclear
        if sensitive:paths.add(path)
        if steps>100000:raise RuntimeError('bounded ROOT ray exceeded100000steps')
    return dict(eta=eta,phi_rad=phi,material_path_mm=dict(materials),l_over_lambda=interaction,sensitive_crossings=len(paths),boundary_steps=steps,distance_mm=distance)


def check(args):
    import ROOT as R
    import dd4hep
    R.EnableImplicitMT(1)
    try:
        R.gROOT.SetBatch(True);R.gRandom.SetSeed(45010);unit=float(dd4hep.mm)
        directory=args.directory.resolve();expected=json.loads((directory/'expected.json').read_text());errors=[]
        for name,digest in expected['export_sha256'].items():
            if sha(directory/name)!=digest:raise ValueError('changed exported input '+name)
        if R.gSystem.Load(str(args.library.resolve()))<0:raise RuntimeError('cannot load HCAL prototype library')
        detector=dd4hep.Detector.getInstance();detector.fromXML(str(directory/'detector.xml'));manager=detector.manager()
        volumes={str(v.GetName()):v for v in manager.GetListOfVolumes()};checks={}
        for root,ro in (('HCALBarrel','HCALBarrelHits'),('HCALEndcaps','HCALEndcapHits')):
            compound=next(v for name,v in volumes.items() if name==root+('BarrelCarrier' if root=='HCALBarrel' else 'EndcapCarrier')+'CompoundTiles')
            checks[root]=compare_compound(R,dd4hep,compound,detector.readout(ro),unit)
            errors.extend(root+': '+e for e in checks[root]['errors'])
        # Count expanded sensitive contexts without expanding millions of passive paths.
        @lru_cache(maxsize=None)
        def expanded_sensitive(name):
            v=volumes[name];return int(bool(dd4hep.Volume(v).isSensitive()))+sum(expanded_sensitive(str(v.GetNode(i).GetVolume().GetName())) for i in range(v.GetNdaughters()))
        observed=expanded_sensitive(str(manager.GetTopVolume().GetName()))
        if observed!=expected['raw_sensitive_volumes']:errors.append('native raw sensitive volume multiplicity')
        shape=manager.GetTopVolume().GetShape()
        world=[2*shape.GetDX()/unit,2*shape.GetDY()/unit,2*shape.GetDZ()/unit]
        steel=detector.material('Steel235');nuclear=float(steel.intLength())/unit
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
        report=dict(status='FAIL' if errors else 'PASS',errors=errors,
            scope='Native logical-template construction,exact-core representation/cell mapping,expanded sensitive multiplicity,distinct-mother ROOT overlap tests and bounded combined-barrel/endcap IP material paths; no engineering acceptance',
            execution=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),python=platform.python_version(),ROOT=R.gROOT.GetVersion(),library_sha256=sha(args.library),auditor_sha256=sha(__file__),expected_sha256=sha(directory/'expected.json'),compact_sha256=sha(directory/'detector.xml')),
            compound_checks=checks,raw_sensitive_volumes=observed,logical_tile_channels=expected['sensitive_tiles'],
            unique_logical_volumes=len(volumes),world_full_xyz_mm=world,Steel235_nuclear_interaction_length_mm=nuclear,
            overlap_tolerance_mm=1e-5,overlap_scope='not run' if args.skip_overlaps else 'each distinct native direct-daughter mother once,includingworld',checked_mothers=checked,overlaps=overlaps,
            material_rays=rays,material_ray_scope='not run' if args.skip_rays else '68 deterministic IP directions; no containment claim')
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
