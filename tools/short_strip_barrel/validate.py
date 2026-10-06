#!/usr/bin/env python3
"""Native construction audit for DES-020; engineering acceptance is separate."""
import argparse
from array import array
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

from model import ROOT, sha
sys.path.insert(0,str(ROOT/"tools/pixel_barrel_dd4hep"))
# Import the shared audit by file path: this entry point has the same basename.
import importlib.util
spec=importlib.util.spec_from_file_location("pixel_audit",ROOT/"tools/pixel_barrel_dd4hep/validate.py")
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


def capacity(s):
    """Analytical capacities; cuts are contained/disjoint by producer controls.

    Avoid ROOT's stochastic composite Capacity estimate. This does not by itself
    prove CSG containment; the model/controls and native overlap check are separate.
    """
    kind=str(s.ClassName())
    if kind=="TGeoBBox":return 8*float(s.GetDX())*float(s.GetDY())*float(s.GetDZ())
    if kind in ("TGeoTube","TGeoTubeSeg"):
        angle=2*math.pi if kind=="TGeoTube" else math.radians(float(s.GetPhi2())-float(s.GetPhi1()))
        return angle*(float(s.GetRmax())**2-float(s.GetRmin())**2)*float(s.GetDz())
    if kind=="TGeoTorus":
        return math.radians(float(s.GetDphi()))*math.pi*float(s.GetR())*(float(s.GetRmax())**2-float(s.GetRmin())**2)
    if kind=="TGeoCompositeShape":
        node=s.GetBoolNode()
        if str(node.ClassName())!="TGeoSubtraction":raise ValueError("Unexpected CSG")
        return capacity(node.GetLeftShape())-capacity(node.GetRightShape())
    raise ValueError("Unsupported shape: "+kind)


def identifiers(detector,ROOTmod,dd4hep,sensors,cells):
    ro=detector.readout("ShortStripBarrelHits")
    decoder=ro.idSpec().decoder();seg=ro.segmentation()
    packed=set();errors=[];checked=0
    for s in sensors:
        fields=ROOTmod.std.vector("pair<string,int>")()
        for key,val in s["ids"].items():fields.emplace_back(key,val)
        vid=int(ro.idSpec().encode(fields))
        if vid in packed:errors.append("Duplicate volume ID")
        packed.add(vid)
        for key,val in s["ids"].items():
            if int(decoder.get(vid,key))!=val:errors.append("Volume ID decode mismatch")
        for ix,iy in ((-320,-96),(319,95),(-320,95),(319,-96),(0,0)):
            local=dd4hep.Position((ix+.5)*cells[0]*dd4hep.mm,(iy+.5)*cells[1]*dd4hep.mm,0)
            cid=int(seg.cellID(local,local,vid));back=seg.position(cid)
            if (int(decoder.get(cid,"x")),int(decoder.get(cid,"y")))!=(ix,iy):errors.append("Anisotropic cell mismatch")
            if math.hypot(back.x()-local.x(),back.y()-local.y())>1e-9*dd4hep.mm:errors.append("Cell centre mismatch")
            checked+=1
    return dict(passed=not errors,errors=errors,unique_volume_ids=len(packed),cells_checked=checked,grid=[640,192])


def run(args):
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    if R.gSystem.Load(str(args.library.resolve()))<0:raise RuntimeError("Factory load failed")
    detector=dd4hep.Detector.getInstance()
    expected=json.loads(args.expected.read_text())
    errors=[]
    try:
        detector.fromXML(str(args.compact.resolve()))
        manager=detector.manager()
        audit.shape_capacity=capacity
        inventory=audit.physical_inventory(detector,dd4hep,R,expected["entities"])
        entities=audit.compare_entities(inventory["nodes"],expected["entities"])
        sensors=audit.compare_sensors(inventory["sensors"],[e for e in expected["entities"] if e["role"]=="sensitive"])
        ids=identifiers(detector,R,dd4hep,inventory["sensors"],expected["cell_mm"])
        for test in (entities,sensors,ids):errors.extend(test["errors"])
        if inventory["counts"]!=expected["counts"]:errors.append("Role count mismatch")
        for mat,values in expected["material_totals"].items():
            actual=inventory["materials"].get(mat,{})
            for key in ("volume_mm3","mass_g"):
                if not math.isclose(actual.get(key,-1),values[key],rel_tol=1e-6,abs_tol=1e-8):errors.append(f"{mat}: {key} mismatch")
        manager.CheckOverlaps(1e-5*dd4hep.mm)
        overlaps=[dict(description=str(x.GetTitle()),penetration_mm=float(x.GetOverlap())/dd4hep.mm)
                  for x in manager.GetListOfOverlaps()]
        if overlaps:errors.append(f"{len(overlaps)} overlaps")
        paths={s["path"]:s for s in inventory["sensors"]}
        rays=[]
        for origin in ([0,0,0],[1,1,-150],[1,1,150]):
            for eta in (-2,-1,0,1,2):
                for phi in (0,.37,1.11,2.29,4.73):
                    ray=audit.trace_ray(manager,dd4hep,origin,audit.ray_direction(eta,phi),paths)
                    ray.update(origin_mm=origin,eta=eta,phi_rad=phi);rays.append(ray)
        layers={key for ray in rays for key in ray["hits_by_detector_layer"]}
        if layers!={f"3:{i}" for i in range(4)}:errors.append("Navigation did not exercise all layers")
        output_root=args.output.with_suffix(".root")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        manager.Export(str(output_root.resolve()))
        materials=inventory["materials"]
        report=dict(status="PASS" if not errors else "FAIL",errors=errors,
            scope="DD4hep/ROOT prototype construction; not engineering qualification",
            execution=dict(commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                dirty=bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip()),
                compact_sha256=sha(args.compact),expected_sha256=sha(args.expected),library_sha256=sha(args.library),
                validator_sha256=sha(__file__),shared_validator_sha256=sha(ROOT/"tools/pixel_barrel_dd4hep/validate.py"),
                factory_sha256=sha(ROOT/"prototypes/short_strip_barrel/ShortStripBarrel.cpp"),
                root_version=str(R.gROOT.GetVersion()),python=platform.python_version(),command=sys.argv),
            counts=inventory["counts"],physical_placements=inventory["physical_placements"],
            input_provenance=expected['provenance'],
            sensor_comparison=sensors,entity_comparison=entities,identifiers=ids,
            materials=materials,mass_g=sum(v["mass_g"] for v in materials.values()),
            overlap_tolerance_mm=1e-5,overlaps=overlaps,navigation=rays,
            root_export_sha256=sha(output_root),
            limitations=["Sparse straight ROOT rays are navigation/material checks, not coverage proof.",
                "No ACTS conversion or calibrated strixel response.",
                "Composite volumes use analytical subtraction; model controls establish disjoint contained holes.",
                "Effective service material does not establish cable bends or fittings."])
        args.output.write_text(json.dumps(report,indent=2)+"\n")
        print(f"{report['status']}: {len(paths)} sensors, {len(overlaps)} overlaps, {len(rays)} material rays")
        return 0 if not errors else 1
    finally:
        dd4hep.Detector.destroyInstance()
        if R.gGeoManager:R.gGeoManager.Delete()


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("compact","expected","library","output"):p.add_argument("--"+name,type=Path,required=True)
    raise SystemExit(run(p.parse_args()))
