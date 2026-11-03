#!/usr/bin/env python3
"""Audit actual combined geometry against independent component inventories."""

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "pixel_audit", ROOT_DIR / "tools/pixel_barrel_dd4hep/validate.py"
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def capacity(shape):
    """Exact only when the restricted auditor proves the CSG operation."""
    return audit.shape_capacity(shape)


def inventory(detector, dd4hep, root, expected):
    """Measure primitives; bound general CSG instead of subtracting full cuts."""
    from array import array
    lookup={e['name']:e for e in expected['entities']}
    counts=Counter(); materials=defaultdict(lambda:dict(volume_mm3=0.,mass_g=0.))
    nodes=[];sensors=[];errors=[];shapes={};bounded=[];unit=float(dd4hep.mm)
    def visit(node,parent,ids,path):
        volume=node.GetVolume();name=str(volume.GetName());shape=volume.GetShape()
        path=path+'/'+str(node.GetName());matrix=root.TGeoHMatrix(parent);matrix.Multiply(node.GetMatrix())
        ids=dict(ids)
        for field in dd4hep.PlacedVolume(node).volIDs():ids[str(field.first)]=int(field.second)
        entity=lookup.get(name,{});role=entity.get('role')
        if role:counts[role]+=1
        sensitive=bool(dd4hep.Volume(volume).isSensitive())
        if sensitive!=(role=='sensitive'):errors.append('Actual sensitivity differs from expected role: '+name)
        point=array('d',[0.,0.,0.]);matrix.LocalToMaster(array('d',[0.,0.,0.]),point)
        normal=array('d',[0.,0.,0.]);matrix.LocalToMasterVect(array('d',[0.,0.,1.]),normal)
        item=dict(name=name,path=path,role=role,ids=ids,center_mm=[x/unit for x in point],normal=list(normal))
        if not volume.IsAssembly() and volume!=detector.manager().GetTopVolume():
            substance=volume.GetMaterial();material=str(substance.GetName());density=float(substance.GetDensity())
            item['material']=material
            if entity.get('material') and entity['material']!=material:errors.append('Actual material differs: '+name)
            if material in expected['materials'] and not math.isclose(density,expected['materials'][material]['density_g_cm3'],rel_tol=1e-6,abs_tol=1e-9):
                errors.append('Actual material density differs: '+name)
            composite=str(shape.ClassName())=='TGeoCompositeShape'
            if 'cuts' in entity and composite!=(entity['cuts']>0):errors.append('Actual CSG presence differs: '+name)
            if entity.get('center_mm') and math.dist(item['center_mm'],entity['center_mm'])>1e-7:
                errors.append('Actual solid centre differs: '+name)
            try:
                measured=capacity(shape)/unit**3
                displaced=[capacity(volume.GetNode(i).GetVolume().GetShape())/unit**3
                           for i in range(volume.GetNdaughters()) if not volume.GetNode(i).GetVolume().IsAssembly()]
                measured=audit.exclusive_volume(measured,displaced)
            except ValueError:
                base=shape
                while str(base.ClassName())=='TGeoCompositeShape' and str(base.GetBoolNode().ClassName())=='TGeoSubtraction':
                    base=base.GetBoolNode().GetLeftShape()
                if str(base.ClassName())=='TGeoCompositeShape':
                    raise ValueError('Unsupported CSG bound: '+name)
                upper=float(base.Capacity())/unit**3
                item.update(volume_bounds_mm3=[0.,upper],mass_bounds_g=[0.,upper*density/1000])
                bounded.append(dict(name=name,material=material,volume_bounds_mm3=[0.,upper],mass_bounds_g=[0.,upper*density/1000]))
                if 'volume_bounds_mm3' in entity and not math.isclose(upper,entity['volume_bounds_mm3'][1],rel_tol=1e-8,abs_tol=1e-6):
                    errors.append('CSG primitive upper bound differs: '+name)
            else:
                item.update(volume_mm3=measured,mass_g=measured*density/1000)
                if 'volume_mm3' in entity and not math.isclose(measured,entity['volume_mm3'],rel_tol=1e-6,abs_tol=1e-6):
                    errors.append('Exact primitive/exclusive volume differs: '+name)
                material_row=materials[material];material_row['volume_mm3']+=measured;material_row['mass_g']+=measured*density/1000
                material_row.update(density_g_cm3=density,radiation_length_mm=float(substance.GetRadLen())/unit,
                                    interaction_length_mm=float(substance.GetIntLen())/unit)
            if role:shapes[name]=shape
        if sensitive:
            sensor=dict(item,u=[float(matrix.GetRotationMatrix()[3*j]) for j in range(3)],
                v=[float(matrix.GetRotationMatrix()[3*j+1]) for j in range(3)],
                size_mm=[2*float(shape.GetDX())/unit,2*float(shape.GetDY())/unit,2*float(shape.GetDZ())/unit])
            sensors.append(sensor)
        nodes.append(item)
        for i in range(volume.GetNdaughters()):visit(volume.GetNode(i),matrix,ids,path)
    visit(detector.manager().GetTopNode(),root.TGeoHMatrix(),{},'')
    probes=expected.get('shape_probes',[])
    for probe in probes:
        shape=shapes.get(probe['name'])
        if shape is None:errors.append('Missing probed solid: '+probe['name']);continue
        if bool(shape.Contains(array('d',[x*unit for x in probe['point_mm']])))!=probe['inside']:
            errors.append('Actual finite window/contact probe differs: '+probe['name'])
    if expected.get('short_strip_integration'):
        expected_counts=Counter(e['role'] for e in expected['entities'])
        if dict(expected_counts)!=dict(counts):errors.append('Actual combined payload counts differ')
    return dict(counts=dict(counts),materials=dict(materials),sensors=sensors,nodes=nodes,
                physical_placements=len(nodes),errors=errors,bounded_csg=bounded,
                shape_probes_checked=len(probes),probe_counts=dict(Counter(p['reason'] for p in probes)))


def verify_sources(expected):
    sources=dict(expected['assembly_source_hashes'])
    for component in expected['components']:
        sources.update(component.get('provenance',{}).get('source_hashes',{}))
    errors=[]
    for name,digest in sources.items():
        if hashlib.sha256((ROOT_DIR/name).read_bytes()).hexdigest()!=digest:
            errors.append('Executing source differs from generated provenance: '+name)
    return errors


def main():
    parser = argparse.ArgumentParser()
    for name in ("compact", "expected", "library_dir", "output"):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    args = parser.parse_args()
    import ROOT as R
    import dd4hep

    R.gROOT.SetBatch(True)
    R.EnableImplicitMT(1)
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    libs = [
        args.library_dir / f"lib{name}{suffix}"
        for name in (
            "nODDBeamPipe",
            "nODDPixelBarrel",
            "nODDShortStripBarrel",
            "nODDShortStripEndcap",
            "nODDLongStrip",
        )
    ]
    for lib in libs:
        if R.gSystem.Load(str(lib.resolve())) < 0:
            raise RuntimeError("Factory load failed: " + str(lib))
    expected = json.loads(args.expected.read_text())
    d = dd4hep.Detector.getInstance()
    d.fromXML(str(args.compact.resolve()))
    actual = inventory(d, dd4hep, R, expected)
    sensors = audit.compare_sensors(
        actual["sensors"],
        [e for e in expected["entities"] if e["role"] == "sensitive"],
    )
    errors = verify_sources(expected) + actual["errors"] + list(sensors["errors"])
    packed = set()
    identifiers = []
    for system, readout in (
        (1, "PixelBarrelHits"),
        (2, "PixelEndcapHits"),
        (3, "PixelEndcapHits"),
        (4, "ShortStripBarrelHits"),
        (5, "ShortStripEndcapHits"),
        (6, "LongStripBarrelHits"),
        (7, "LongStripEndcapHits"),
    ):
        ro = d.readout(readout)
        checked = 0
        cell_checks = 0
        for s in actual["sensors"]:
            if s["ids"]["system"] != system:
                continue
            fields = R.std.vector("pair<string,int>")()
            for key, value in s["ids"].items():
                fields.emplace_back(key, value)
            vid = int(ro.idSpec().encode(fields))
            if vid in packed:
                errors.append("Duplicate global volumeID")
            packed.add(vid)
            for key, value in s["ids"].items():
                if int(ro.idSpec().decoder().get(vid, key)) != value:
                    errors.append("Identifier decode mismatch")
            if system in (4, 5):
                segmentation = ro.segmentation()
                for ix, iy in ((-320,-24), (319,23), (-320,23), (319,-24), (0,0)):
                    point = dd4hep.Position((ix+.5)*.075*dd4hep.mm, (iy+.5)*2.*dd4hep.mm, 0.)
                    cid = int(segmentation.cellID(point, point, vid))
                    position = segmentation.position(cid)
                    if (int(ro.idSpec().decoder().get(cid, 'x')), int(ro.idSpec().decoder().get(cid, 'y'))) != (ix, iy):
                        errors.append('Selected strixel cell identifier mismatch')
                    if math.hypot(position.x()-point.x(), position.y()-point.y()) > 1e-9*dd4hep.mm:
                        errors.append('Selected strixel cell position mismatch')
                    cell_checks += 1
            checked += 1
        identifiers.append(
            dict(system=system, readout=readout, sensitive_count=checked, cell_checks=cell_checks)
        )
    # Every exact primitive/exclusive volume and its material was checked above.
    # General intersecting CSG is reported by bounds, never an exact total mass.
    material_errors=[e for e in actual['errors'] if any(k in e for k in ('material','volume','bound'))]
    import xml.etree.ElementTree as ET

    compact = ET.parse(args.compact).getroot()
    pipe_outer = expected["beam"]["outer_radius_mm"]
    apertures = [
        float(part.get("rmin").removesuffix("*mm"))
        for detector in compact.findall("./detectors/detector")
        if detector.get("name").startswith("PixelEndcap")
        for part in detector.iter("part")
        if part.get("shape") == "sector"
        and part.get("rmin")
        and float(part.get("rmin").removesuffix("*mm")) < 40
        and float(part.get("rmax").removesuffix("*mm")) > pipe_outer
    ]
    clearance = min(apertures) - pipe_outer
    if clearance < -1e-9:
        errors.append("Analytic pixel passive aperture intersects pipe")
    d.manager().CheckOverlaps(1e-5 * dd4hep.mm)
    overlaps = [
        dict(
            description=str(x.GetTitle()),
            penetration_mm=float(x.GetOverlap()) / dd4hep.mm,
        )
        for x in d.manager().GetListOfOverlaps()
    ]
    if overlaps:
        errors.append(f"{len(overlaps)} overlaps in full assembly")
    paths = {s["path"]: s for s in actual["sensors"]}
    rays = []
    for eta in (-4, -3, -2, -1, 0, 1, 2, 3, 4):
        for phi in (0, 0.37, 1.11):
            ray = audit.trace_ray(
                d.manager(),
                dd4hep,
                [0, 0, 0],
                audit.ray_direction(eta, phi),
                paths,
                4100,
            )
            ray.update(eta=eta, phi=phi)
            rays.append(ray)
            if not math.isclose(
                ray["material_path_mm"].get("Beryllium", 0),
                expected["beam"]["config"]["wall_mm"] * math.cosh(eta),
                abs_tol=1e-7,
            ):
                errors.append("Pipe material path changed in assembly")
    errors.extend(verify_sources(expected))
    report = dict(
        status="PASS" if not errors else "FAIL",
        errors=errors,
        sensitive_comparison=sensors,
        identifiers=identifiers,
        unique_volume_ids=len(packed),
        material_comparison=dict(
            passed=not material_errors,
            errors=material_errors,
            materials_checked=len(actual["materials"]),
            scope="Exact primitive/exclusive quantities only; general CSG bounded, total mass not asserted",
            bounded_csg=actual["bounded_csg"],
        ),
        shape_probes_checked=actual["shape_probes_checked"],
        probe_counts=actual["probe_counts"],
        minimum_pixel_passive_clearance_mm=clearance,
        counts=actual["counts"],
        physical_placements=actual["physical_placements"],
        materials=actual["materials"],
        mass_policy='Only proved exact primitive/exclusive volumes are accumulated in materials. General CSG has explicit bounds; no complete tracker mass is asserted.',
        overlaps=overlaps,
        navigation=rays,
        execution=dict(
            revision=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT_DIR, text=True
            ).strip(),
            dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT_DIR,text=True).strip()),
            root_version=R.gROOT.GetVersion(),
            hashes={
                str(p.name): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [args.compact, args.expected, Path(__file__), *libs]
            },
        ),
        limitations=[
            "No engineering sign-off; sparse straight rays are not acceptance or field navigation; Assembly uses explicitly reconciled service ownership; fixed packing limits remain unqualified."
        ],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    dd4hep.Detector.destroyInstance()
    if R.gGeoManager:
        R.gGeoManager.Delete()
    print(
        json.dumps(
            dict(
                status=report["status"],
                errors=errors[:8],
                overlaps=len(overlaps),
                sensors=len(packed),
            )
        )
    )
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
