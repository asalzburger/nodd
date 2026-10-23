#!/usr/bin/env python3
"""Fail-closed native DD4hep/ROOT audit of the DES039/040 Air PROTOTYPE.

Source prism vertices and exact CSG primitive dimensions/poses are checked
against the pinned JSON. Deterministic occupancy probes supplement those exact
representation checks; they do not certify engineering clearance or response.
"""
from __future__ import annotations

import argparse
from array import array
from collections import Counter
import json
import math
from pathlib import Path
import platform
import random
import subprocess
import sys

try:
    from . import export as generator
except ImportError:
    import export as generator


def world(local, basis, origin):
    return [origin[i]+sum(basis[i][j]*local[j] for j in range(3)) for i in range(3)]


def source_vertices(panel):
    return [world([*xy,z],panel["basis"],panel["origin_m"])
            for z in (-panel["depth_m"]/2,panel["depth_m"]/2)
            for xy in panel["vertices_m"]]


def compare_chambers(observed, source, expected, tolerance_m):
    errors=[]
    panels={p["id"]:p for p in source["panels"]}
    entities={e["name"]:e for e in expected["entities"]}
    if len(observed)!=936 or len({x["name"] for x in observed})!=936:
        errors.append("Expected 936 uniquely named native chambers")
    maximum_vertex=maximum_origin=maximum_basis=0.
    packed=set()
    for actual in observed:
        e=entities.get(actual["name"])
        if e is None:
            errors.append("Unexpected chamber "+actual["name"])
            continue
        panel=panels[e["source_id"]]
        if actual["ids"]!=e["ids"]:
            errors.append("Identifier mismatch "+e["source_id"])
        identity=tuple(sorted(actual["ids"].items()))
        if identity in packed:
            errors.append("Duplicate native chamber identifier")
        packed.add(identity)
        origin=math.dist(actual["origin_m"],panel["origin_m"])
        basis=max(abs(actual["basis"][i][j]-panel["basis"][i][j]) for i in range(3) for j in range(3))
        maximum_origin=max(maximum_origin,origin)
        maximum_basis=max(maximum_basis,basis)
        if origin>tolerance_m or basis>1e-12:
            errors.append("Native transform mismatch "+e["source_id"])
        target=source_vertices(panel)
        if len(actual["vertices_m"])!=8:
            errors.append("Native chamber is not an eight-vertex prism "+e["source_id"])
            continue
        # Vertex order differs deliberately: source CCW, native Arb8 clockwise.
        residual=max(min(math.dist(v,t) for t in target) for v in actual["vertices_m"])
        reverse=max(min(math.dist(v,t) for t in actual["vertices_m"]) for v in target)
        maximum_vertex=max(maximum_vertex,residual,reverse)
        if max(residual,reverse)>tolerance_m:
            errors.append("Native solid vertices mismatch "+e["source_id"])
        if actual["material"]!="Air" or actual["sensitive"]:
            errors.append("Expected empty nonsensitive Air chamber "+e["source_id"])
    return dict(passed=not errors,errors=errors,observed=len(observed),
        unique_identifiers=len(packed),maximum_vertex_residual_m=maximum_vertex,
        maximum_origin_residual_m=maximum_origin,maximum_basis_residual=maximum_basis)


def verify_manifest(expected,source,compact):
    if expected["source"]!=dict(revision=generator.SOURCE_REVISION,path=generator.SOURCE_PATH,sha256=generator.SOURCE_SHA256):
        raise ValueError("Expected manifest has incorrect pinned source identity")
    if expected["elements_source"]!=dict(revision=generator.SOURCE_REVISION,path=generator.ELEMENTS_PATH,sha256=generator.ELEMENTS_SHA256):
        raise ValueError("Expected manifest has incorrect pinned element-table identity")
    for filename,digest in expected["exported_sha256"].items():
        if filename not in ("muon-system.xml","materials.xml") or generator.sha((compact.parent/filename).read_bytes())!=digest:
            raise ValueError("Exported XML hash mismatch: "+filename)
    if compact.name!="muon-system.xml":
        raise ValueError("Expected the generated muon-system.xml entry point")
    if expected["counts"]!=dict(chambers=936,warm_groups=3,warm_coil_definitions=36,sensitive=0):
        raise ValueError("Expected manifest inventory mismatch")
    panels=sorted(source["panels"],key=lambda p:p["id"])
    if len(expected["entities"])!=936:
        raise ValueError("Expected manifest does not contain936 source chambers")
    for index,(e,p) in enumerate(zip(expected["entities"],panels),1):
        for key in ("origin_m","basis","vertices_m","depth_m","kind"):
            if e[key]!=p[key]:
                raise ValueError("Expected manifest differs from pinned panel: "+p["id"])
        side=0 if p["kind"]=="barrel" else (1 if p["origin_m"][2]>0 else -1)
        if e["source_id"]!=p["id"] or e["ids"]!=dict(system=generator.SYSTEM_ID,chamber=index,station=p["station"],side=side):
            raise ValueError("Expected manifest chamber identity mismatch")
    magnetic=source["magnetic_configuration"]
    if expected["warm_widths_m"]!=magnetic["warm"] or len(expected["groups"])!=3:
        raise ValueError("Expected manifest warm group mismatch")
    for index,(e,key) in enumerate(zip(expected["groups"],("barrel","endcap_plus","endcap_minus")),1):
        if e["source_group"]!=key or e["configuration"]!=magnetic["coil_groups"][key] or e["ids"]!=dict(system=generator.SYSTEM_ID,group=index):
            raise ValueError("Expected manifest toroid source mismatch")


def expected_primitives(group,warm,folds=12):
    result=[]
    hr,hz,rho=(group[k] for k in ("half_r_m","half_z_m","corner_radius_m"))
    a,b=warm["normal_m"]/2,warm["tangent_m"]/2
    for k in range(folds):
        phi=math.radians(group["phi_offset_deg"]+360*k/folds)
        c,s=math.cos(phi),math.sin(phi)
        q=[[c,0,s],[s,0,-c],[0,1,0]]
        origin=[group["center_r_m"]*c,group["center_r_m"]*s,group["center_z_m"]]
        for center,half in (([hr,0,0],[a,hz-rho,b]),([-hr,0,0],[a,hz-rho,b]),
                            ([0,hz,0],[hr-rho,a,b]),([0,-hz,0],[hr-rho,a,b])):
            result.append(dict(kind="TGeoBBox",center_m=world(center,q,origin),basis=q,dimensions=[*half]))
        for sx,sy,start in ((1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)):
            result.append(dict(kind="TGeoTubeSeg",center_m=world([sx*(hr-rho),sy*(hz-rho),0],q,origin),basis=q,
                               dimensions=[rho-a,rho+a,b,start,start+90]))
    return result


def compare_primitives(observed,expected,tolerance_m):
    errors=[];remaining=list(observed);maximum=0.
    if len(observed)!=len(expected):
        errors.append(f"Expected {len(expected)} CSG primitive instances; observed {len(observed)}")
    for target in expected:
        candidates=[(math.dist(item["center_m"],target["center_m"]),i,item)
                    for i,item in enumerate(remaining) if item["kind"]==target["kind"]]
        if not candidates:
            errors.append("Missing native CSG primitive "+target["kind"])
            continue
        distance,index,actual=min(candidates,key=lambda x:x[0]);remaining.pop(index)
        maximum=max(maximum,distance)
        rotation=max(abs(actual["basis"][i][j]-target["basis"][i][j]) for i in range(3) for j in range(3))
        dimensions=max(abs(x-y) for x,y in zip(actual["dimensions"],target["dimensions"]))
        if distance>tolerance_m or rotation>1e-12 or dimensions>tolerance_m:
            errors.append("Native CSG primitive dimensions/transform mismatch")
    return dict(passed=not errors,errors=errors,observed=len(observed),expected=len(expected),
                maximum_center_residual_m=maximum)


def analytic_contains(point,group,warm,folds=12):
    """Independent rounded-box signed-distance equation, union over all coils."""
    a,b=warm["normal_m"]/2,warm["tangent_m"]/2
    rho=group["corner_radius_m"]
    for k in range(folds):
        phi=math.radians(group["phi_offset_deg"]+360*k/folds)
        c,s=math.cos(phi),math.sin(phi)
        tangent=-point[0]*s+point[1]*c
        if abs(tangent)>b:
            continue
        u=point[0]*c+point[1]*s
        dr=abs(u-group["center_r_m"])-(group["half_r_m"]-rho)
        dz=abs(point[2]-group["center_z_m"])-(group["half_z_m"]-rho)
        signed=math.hypot(max(dr,0),max(dz,0))+min(max(dr,dz),0)-rho
        if abs(signed)<=a:
            return True
    return False


def occupancy_points(group,warm,seed=9293):
    rng=random.Random(seed)
    cr,cz,hr,hz,rho=(group[k] for k in ("center_r_m","center_z_m","half_r_m","half_z_m","corner_radius_m"))
    a,b=warm["normal_m"]/2,warm["tangent_m"]/2
    bound=cr+hr+a+.1
    points=[[rng.uniform(-bound,bound),rng.uniform(-bound,bound),rng.uniform(cz-hz-a-.1,cz+hz+a+.1)] for _ in range(4096)]
    for k in range(12):
        phi=math.radians(group["phi_offset_deg"]+30*k);c,s=math.cos(phi),math.sin(phi)
        q=[[c,0,s],[s,0,-c],[0,1,0]];origin=[cr*c,cr*s,cz]
        for sx,sy,start in ((1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)):
            for theta in (15,45,75):
                angle=math.radians(start+theta)
                for delta in (-a-1e-5,-a+1e-5,0,a-1e-5,a+1e-5):
                    for tangent in (-b-1e-5,-b+1e-5,0,b-1e-5,b+1e-5):
                        local=[sx*(hr-rho)+(rho+delta)*math.cos(angle),sy*(hz-rho)+(rho+delta)*math.sin(angle),tangent]
                        points.append(world(local,q,origin))
        for sign in (-1,1):
            for delta in (-a-1e-5,-a+1e-5,0,a-1e-5,a+1e-5):
                for tangent in (-b-1e-5,0,b+1e-5):
                    points.append(world([sign*(hr+delta),0,tangent],q,origin))
                    points.append(world([0,sign*(hz+delta),tangent],q,origin))
    return points


def matrix_data(matrix,unit):
    return ([float(matrix.GetTranslation()[i])/unit for i in range(3)],
            [[float(matrix.GetRotationMatrix()[3*i+j]) for j in range(3)] for i in range(3)])


def native_primitives(shape,matrix,ROOT,unit):
    if str(shape.ClassName())=="TGeoCompositeShape":
        node=shape.GetBoolNode()
        if str(node.ClassName())!="TGeoUnion":
            raise ValueError("Warm geometry contains a non-union CSG operation")
        result=[]
        for child,transform in ((node.GetLeftShape(),node.GetLeftMatrix()),(node.GetRightShape(),node.GetRightMatrix())):
            pose=ROOT.TGeoHMatrix(matrix);pose.Multiply(transform)
            result.extend(native_primitives(child,pose,ROOT,unit))
        return result
    kind=str(shape.ClassName());center,basis=matrix_data(matrix,unit)
    if kind=="TGeoBBox":
        dimensions=[float(shape.GetDX())/unit,float(shape.GetDY())/unit,float(shape.GetDZ())/unit]
    elif kind=="TGeoTubeSeg":
        dimensions=[float(shape.GetRmin())/unit,float(shape.GetRmax())/unit,float(shape.GetDz())/unit,float(shape.GetPhi1()),float(shape.GetPhi2())]
    else:
        raise ValueError("Unexpected warm CSG leaf "+kind)
    return [dict(kind=kind,center_m=center,basis=basis,dimensions=dimensions)]


def run(args):
    import dd4hep
    import ROOT
    ROOT.gROOT.SetBatch(True)
    ROOT.EnableImplicitMT(1)
    if ROOT.gSystem.Load(str(args.library.resolve()))<0:
        raise RuntimeError("Muon factory library load failed")
    source=generator.load_source();expected=json.loads(args.expected.read_text())
    verify_manifest(expected,source,args.compact)
    detector=dd4hep.Detector.getInstance()
    try:
        detector.fromXML(str(args.compact.resolve()))
        manager=detector.manager();unit=float(dd4hep.m)
        chambers=[];groups={};unexpected=[];sensitive=0
        names={e["name"]:e for e in expected["entities"]}
        group_names={e["name"]:e for e in expected["groups"]}
        def visit(node,parent,inherited):
            nonlocal sensitive
            volume=node.GetVolume();matrix=ROOT.TGeoHMatrix(parent);matrix.Multiply(node.GetMatrix())
            ids=dict(inherited)
            for item in dd4hep.PlacedVolume(node).volIDs():
                ids[str(item.first)]=int(item.second)
            name=str(volume.GetName());is_sensitive=bool(dd4hep.Volume(volume).isSensitive())
            sensitive+=int(is_sensitive)
            if name in names:
                shape=volume.GetShape();vertices=[]
                if str(shape.ClassName())!="TGeoArb8":
                    raise ValueError("Expected native Arb8 chamber "+name)
                raw=shape.GetVertices()
                for i in range(8):
                    local=array("d",[float(raw[2*i]),float(raw[2*i+1]),(-1 if i<4 else 1)*float(shape.GetDz())])
                    global_point=array("d",[0.,0.,0.]);matrix.LocalToMaster(local,global_point)
                    vertices.append([x/unit for x in global_point])
                origin,basis=matrix_data(matrix,unit)
                chambers.append(dict(name=name,ids=ids,origin_m=origin,basis=basis,vertices_m=vertices,
                    material=str(volume.GetMaterial().GetName()),sensitive=is_sensitive))
            elif name in group_names:
                if name in groups:
                    raise ValueError("Duplicate warm group placement")
                groups[name]=(volume,matrix,ids)
            elif not volume.IsAssembly() and volume!=manager.GetTopVolume():
                unexpected.append(name)
            for i in range(volume.GetNdaughters()):
                visit(volume.GetNode(i),matrix,ids)
        visit(manager.GetTopNode(),ROOT.TGeoHMatrix(),{})
        comparison=compare_chambers(chambers,source,expected,args.transform_tolerance_mm/1000)
        errors=list(comparison["errors"])
        if unexpected:errors.append("Unexpected physical volumes: "+str(unexpected))
        if sensitive:errors.append("Unexpected sensitive placements")
        if len(groups)!=3:errors.append("Expected exactly three native warm group volumes")
        warm=source["magnetic_configuration"]["warm"];warm_checks=[]
        for e in expected["groups"]:
            if e["name"] not in groups:continue
            volume,matrix,ids=groups[e["name"]];shape=volume.GetShape()
            primitives=native_primitives(shape,matrix,ROOT,unit)
            primitive_check=compare_primitives(primitives,expected_primitives(e["configuration"],warm),args.transform_tolerance_mm/1000)
            errors.extend(primitive_check["errors"])
            mismatches=[];inside=0;points=occupancy_points(e["configuration"],warm)
            for point in points:
                native=array("d",[0.,0.,0.]);matrix.MasterToLocal(array("d",[x*unit for x in point]),native)
                actual=bool(shape.Contains(native));target=analytic_contains(point,e["configuration"],warm)
                inside+=int(target)
                if actual!=target and len(mismatches)<20:mismatches.append(dict(point_m=point,native=actual,source=target))
            if mismatches:errors.append("Native warm occupancy mismatch "+e["source_group"])
            if ids!=e["ids"] or str(volume.GetMaterial().GetName())!="Air" or volume.GetNdaughters()!=0:
                errors.append("Native warm group identity/material/children mismatch")
            warm_checks.append(dict(group=e["source_group"],primitives=primitive_check,
                occupancy=dict(passed=not mismatches,points=len(points),source_inside=inside,source_outside=len(points)-inside,seed=9293,mismatches=mismatches)))
        # Check ROOT's overlap collection explicitly: the stock utility exits0
        # even when it prints overlaps, so process success alone is insufficient.
        manager.CheckOverlaps(args.overlap_tolerance_mm*float(dd4hep.mm))
        overlaps=[dict(name=str(x.GetName()),description=str(x.GetTitle()),penetration_mm=float(x.GetOverlap())/float(dd4hep.mm)) for x in manager.GetListOfOverlaps()]
        if overlaps:errors.append(f"ROOT found {len(overlaps)} overlaps/extrusions")
        if args.root_output:
            args.root_output.parent.mkdir(parents=True,exist_ok=True)
            manager.Export(str(args.root_output.resolve()))
        ROOT.gInterpreter.Declare('#include "DD4hep/Version.h"\nnamespace nodd_muon_audit { constexpr int major=DD4HEP_MAJOR_VERSION; constexpr int minor=DD4HEP_MINOR_VERSION; }')
        return dict(status="PASS" if not errors else "FAIL",errors=errors,counts=dict(chambers=len(chambers),warm_groups=len(groups),warm_coil_definitions=36,sensitive=sensitive),
            chamber_comparison=comparison,warm_comparison=warm_checks,overlaps=overlaps,
            source=expected["source"],root_version=str(ROOT.gROOT.GetVersion()),
            dd4hep_version=f"{ROOT.nodd_muon_audit.major}.{ROOT.nodd_muon_audit.minor}",
            dd4hep_mm_in_root_units=float(dd4hep.mm),dd4hep_m_in_root_units=unit)
    finally:
        ROOT.DisableImplicitMT()
        dd4hep.Detector.destroyInstance()
        if ROOT.gGeoManager:ROOT.gGeoManager.Delete()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact",type=Path,required=True)
    parser.add_argument("--expected",type=Path,required=True)
    parser.add_argument("--library",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--root-output",type=Path)
    parser.add_argument("--overlap-tolerance-mm",type=float,default=1e-5)
    parser.add_argument("--transform-tolerance-mm",type=float,default=1e-7)
    args=parser.parse_args()
    for value in (args.overlap_tolerance_mm,args.transform_tolerance_mm):
        if not math.isfinite(value) or value<=0:parser.error("Tolerances must be positive and finite")
    report=dict(schema_version=1,scope="Isolated empty Air chamber and toroid warm-reservation PROTOTYPE; geometry validation only",
        command=sys.argv,python_version=platform.python_version(),
        overlap_tolerance_mm=args.overlap_tolerance_mm,transform_tolerance_mm=args.transform_tolerance_mm,
        limitations=["Numerical tolerances are characterization choices, not engineering acceptance.",
            "Warm unions reserve space only; no physical coil composition, chamber internals, supports, HCAL, magnetic field or response.",
            "Occupancy probes supplement exact native CSG primitive and transform comparison; they alone are not a volume-separation proof.",
            "Geant4 transport is checked by the separate execution runner."])
    try:
        report.update(commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=generator.ROOT,text=True).strip(),
            dirty=bool(subprocess.check_output(["git","status","--porcelain"],cwd=generator.ROOT,text=True).strip()),
            file_sha256={str(p):generator.sha(p.read_bytes()) for p in (args.compact,args.expected,args.library,Path(__file__),generator.ROOT/"prototypes/muon/Muon.cpp")})
        report.update(run(args))
    except Exception as error:
        report.update(status="FAIL",errors=[f"{type(error).__name__}: {error}"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(report["status"]+": "+"; ".join(report["errors"]))
    return 0 if report["status"]=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
