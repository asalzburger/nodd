"""Audit expanded native PR132 geometry; retain large identity snapshots locally.

Run once without --manifest/--baseline for the unchanged control, then with
the variant manifest and baseline snapshot in a fresh process. This supplements
the maintained validator, retaining per-instance contacts after template sharing.
"""
import argparse
from array import array
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
spec = importlib.util.spec_from_file_location("tracker_audit", REPO / "tools/tracker_dd4hep/validate.py")
tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracker)
audit = tracker.audit


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def matrix_values(matrix):
    return [float(matrix.GetTranslation()[i]) for i in range(3)] + [float(matrix.GetRotationMatrix()[i]) for i in range(9)]


def shape_values(shape):
    """Exact supported native solid parameters and recursive Boolean transforms."""
    kind = str(shape.ClassName())
    if kind == "TGeoCompositeShape":
        node = shape.GetBoolNode()
        return [kind, str(node.ClassName()), shape_values(node.GetLeftShape()),
                shape_values(node.GetRightShape()), matrix_values(node.GetLeftMatrix()),
                matrix_values(node.GetRightMatrix())]
    methods = {
        "TGeoBBox": ("GetDX", "GetDY", "GetDZ"),
        "TGeoTube": ("GetRmin", "GetRmax", "GetDz"),
        "TGeoTubeSeg": ("GetRmin", "GetRmax", "GetDz", "GetPhi1", "GetPhi2"),
        "TGeoTorus": ("GetR", "GetRmin", "GetRmax", "GetPhi1", "GetDphi"),
    }
    if kind in methods:
        result = [kind, *[float(getattr(shape, method)()) for method in methods[kind]]]
        if kind == "TGeoBBox":
            result.append([float(shape.GetOrigin()[i]) for i in range(3)])
        return result
    if kind == "TGeoXtru":
        return [kind, [[float(shape.GetX(i)), float(shape.GetY(i))] for i in range(shape.GetNvert())],
                [[float(shape.GetZ(i)), float(shape.GetXOffset(i)), float(shape.GetYOffset(i)),
                  float(shape.GetScale(i))] for i in range(shape.GetNz())]]
    raise ValueError("Unsupported exact shape fingerprint: " + kind)


def mapping(manifest):
    if not manifest:
        return {}, None
    by_ids = {}
    for item in manifest["instances"]:
        key = tuple(item["ids"][field] for field in ("system", "layer", "stave", "module"))
        if key in by_ids:
            raise ValueError("Duplicate manifest module identity")
        by_ids[key] = item
    return by_ids, manifest["template_name"]


def trace(manager, unit, origin, direction, paths, length=4100.):
    """Include ambient/world material so added same-material mothers normalize.

    Native boundary segmentation may change, while material path and sensor IDs
    must agree. This avoids treating new Air mothers as newly added material.
    """
    manager.InitTrack(*[x*unit for x in origin], *direction)
    nav = manager.GetCurrentNavigator()
    distance = 0.; materials = defaultdict(float); hits = set(); steps = 0
    while not nav.IsOutside() and distance < length:
        node = nav.GetCurrentNode()
        if not node:
            break
        path = str(nav.GetPath())
        material = str(node.GetVolume().GetMaterial().GetName())
        nav.FindNextBoundaryAndStep((length-distance)*unit)
        segment = float(nav.GetStep())/unit
        if not math.isfinite(segment) or segment <= 0:
            raise RuntimeError("Nonpositive native boundary step: " + path)
        distance += segment; materials[material] += segment; steps += 1
        if path in paths:
            hits.add(paths[path])
        if steps > 100000:
            raise RuntimeError("Excess native boundary steps")
    return dict(origin_mm=origin, direction=direction, distance_mm=distance,
                material_path_mm=dict(sorted(materials.items())), packed_sensor_ids=sorted(hits), boundary_steps=steps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("compact", "expected", "library-dir", "snapshot", "output"):
        parser.add_argument("--"+name, type=Path, required=True)
    for name in ("extra-library", "manifest", "baseline", "overlap-evidence"):
        parser.add_argument("--"+name, type=Path)
    parser.add_argument("--snapshot-only", action="store_true",
                        help="Baseline only: create supplementary identity snapshot; no overlap verdict")
    args = parser.parse_args()
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True)
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    libraries = [args.library_dir / f"lib{name}{suffix}" for name in
                 ("nODDBeamPipe", "nODDPixelBarrel", "nODDShortStripBarrel", "nODDShortStripEndcap", "nODDLongStrip")]
    if args.extra_library:
        libraries.append(args.extra_library)
    for library in libraries:
        if R.gSystem.Load(str(library.resolve())) < 0:
            raise RuntimeError("Cannot load " + str(library))
    expected = json.loads(args.expected.read_text())
    manifest = json.loads(args.manifest.read_text()) if args.manifest else None
    if manifest and manifest["compact_sha256"] != sha(args.compact):
        raise ValueError("Variant compact does not match manifest")
    if manifest:
        for name,path in (("expected.json",args.expected),("materials.xml",args.compact.parent / "materials.xml")):
            if manifest["source_sha256"][name] != sha(path):
                raise ValueError("Variant input differs from unchanged source: " + name)
    by_ids, template_name = mapping(manifest)
    baseline = json.loads(args.baseline.read_text()) if args.baseline else None
    d = dd4hep.Detector.getInstance()
    d.fromXML(str(args.compact.resolve()))
    manager, unit = d.manager(), float(dd4hep.mm)
    lookup = {e["name"]:e for e in expected["entities"]}
    shape_cache = {}; native = {}; sensors = []; paths = {}; shapes = {}; errors = tracker.verify_sources(expected); counts = Counter()
    material_counts = Counter(); volume_addresses = set(); mother_instances = 0
    beam = expected['beam']['config']
    beam_specs = {
        'BeamPipe_bore': ('Vacuum',0.,beam['inner_radius_mm'],beam['vacuum_density_g_cm3'],{}),
        'BeamPipe_wall': ('Beryllium',beam['inner_radius_mm'],expected['beam']['outer_radius_mm'],
                          beam['density_g_cm3'],{'system':beam['system_id']})}
    beam_seen = set()
    readouts = {i:d.readout(name) for i,name in enumerate(("", "PixelBarrelHits", "PixelEndcapHits", "PixelEndcapHits",
                 "ShortStripBarrelHits", "ShortStripEndcapHits", "LongStripBarrelHits", "LongStripEndcapHits")) if i}
    packed_ids = set(); shape_types = Counter()

    def visit(node, parent, ids, path):
        nonlocal mother_instances
        volume = node.GetVolume(); actual_name = str(volume.GetName())
        local = node.GetMatrix(); world = R.TGeoHMatrix(parent); world.Multiply(local)
        ids = dict(ids)
        for field in dd4hep.PlacedVolume(node).volIDs():
            ids[str(field.first)] = int(field.second)
        path += "/" + str(node.GetName())
        key = tuple(ids.get(field) for field in ("system", "layer", "stave", "module"))
        instance = by_ids.get(key)
        is_template = bool(instance and actual_name == template_name)
        name = instance["module_name"] if is_template else instance["pieces"].get(actual_name, actual_name) if instance else actual_name
        entity = lookup.get(name)
        if entity:
            counts[entity["role"]] += 1
        sensitive = bool(dd4hep.Volume(volume).isSensitive())
        if sensitive != bool(entity and entity["role"] == "sensitive"):
            errors.append("Unexpected native sensitivity: " + name)
        shape = volume.GetShape()
        volume_addresses.add(int(R.addressof(volume)))
        if not volume.IsAssembly() and volume != manager.GetTopVolume():
            if is_template:
                mother_instances += 1
                if str(volume.GetMaterial().GetName()) != str(manager.GetTopVolume().GetMaterial().GetName()):
                    errors.append("Mother changes ambient material")
            else:
                address = int(R.addressof(shape))
                if address not in shape_cache:
                    shape_cache[address] = digest(shape_values(shape))
                substance = volume.GetMaterial(); material = str(substance.GetName())
                material_counts[material] += 1; shape_types[str(shape.ClassName())] += 1
                info = [shape_cache[address], material, float(substance.GetDensity()), float(substance.GetRadLen()),
                        float(substance.GetIntLen()), matrix_values(local), matrix_values(world), ids, sensitive]
                identity = json.dumps([name, sorted(ids.items())], separators=(",", ":"))
                if identity in native:
                    errors.append("Duplicate expanded native identity: " + name)
                native[identity] = digest(info)
                if not entity and name in beam_specs:
                    # BeamPipe uses the separate expected['beam'] contract,
                    # rather than entries in the tracker entity inventory.
                    substance_name,rmin,rmax,density,beam_ids = beam_specs[name]
                    kind = str(shape.ClassName())
                    full_tube = (kind == 'TGeoTube' or (kind == 'TGeoTubeSeg'
                                 and math.isclose(float(shape.GetPhi1()),0.,abs_tol=1e-12)
                                 and math.isclose(float(shape.GetPhi2()),360.,abs_tol=1e-12)))
                    valid = (full_tube and material == substance_name
                             and ids == beam_ids and name not in beam_seen
                             and math.isclose(float(substance.GetDensity()),density,rel_tol=1e-9)
                             and all(math.isclose(a,b,abs_tol=1e-9,rel_tol=1e-12) for a,b in (
                                 (float(shape.GetRmin())/unit,rmin),(float(shape.GetRmax())/unit,rmax),
                                 (float(shape.GetDz())/unit,beam['half_length_mm'])))
                             and matrix_values(world) == [0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.,1.])
                    if not valid:
                        errors.append('Native beampipe differs from its separate inventory: '+name)
                    beam_seen.add(name)
                elif not entity:
                    errors.append("Native constituent absent from unchanged inventory: " + name)
                elif entity.get("material") != material:
                    errors.append("Native material differs from unchanged inventory: " + name)
                shapes[name] = shape
        if sensitive:
            rotation = matrix_values(world)[3:]
            center = [x/unit for x in matrix_values(world)[:3]]
            item = dict(name=name, ids=ids, center_mm=center,
                        u=rotation[0::3], v=rotation[1::3], normal=rotation[2::3],
                        size_mm=[2*float(shape.GetDX())/unit, 2*float(shape.GetDY())/unit, 2*float(shape.GetDZ())/unit])
            sensors.append(item)
            fields = R.std.vector("pair<string,int>")()
            ro = readouts[ids["system"]]
            for field, value in ids.items():
                fields.emplace_back(field, value)
            packed = int(ro.idSpec().encode(fields))
            if packed in packed_ids:
                errors.append("Duplicate packed native sensor ID")
            packed_ids.add(packed);paths[path] = packed
            for field,value in ids.items():
                if int(ro.idSpec().decoder().get(packed, field)) != value:
                    errors.append("Packed native ID roundtrip differs")
        for i in range(volume.GetNdaughters()):
            visit(volume.GetNode(i), world, ids, path)
    visit(manager.GetTopNode(), R.TGeoHMatrix(), {}, "")
    if beam_seen != set(beam_specs):
        errors.append('Incomplete native beampipe inventory')
    comparison = audit.compare_sensors(sensors, [e for e in expected["entities"] if e["role"] == "sensitive"])
    errors.extend(comparison["errors"])
    expected_counts = Counter(e["role"] for e in expected["entities"])
    if counts != expected_counts:
        errors.append("Expanded native payload counts differ")
    for probe in expected.get("shape_probes", []):
        shape = shapes.get(probe["name"])
        if shape is None or bool(shape.Contains(array("d", [x*unit for x in probe["point_mm"]]))) != probe["inside"]:
            errors.append("Per-instance native window/contact differs: " + probe["name"])
    if manifest and len(by_ids) != manifest["module_instances"]:
        errors.append("Incomplete instance/template provenance map")
    if baseline:
        missing = set(baseline["constituents"]) - set(native)
        extra = set(native) - set(baseline["constituents"])
        changed = [key for key in native.keys() & baseline["constituents"].keys() if native[key] != baseline["constituents"][key]]
        if missing or extra or changed:
            errors.append(f"Native constituent identity/shape/material/transform mismatch: missing={len(missing)} extra={len(extra)} changed={len(changed)}")
    else:
        missing = extra = changed = []
    de_sensors = {}; native_sensors = {tuple(sorted(s["ids"].items())):s for s in sensors}
    def visit_element(element, inherited):
        ids = dict(inherited)
        pv = element.placement()
        if pv.isValid():
            for field in pv.volIDs():
                ids[str(field.first)] = int(field.second)
            if pv.volume().isSensitive():
                key = tuple(sorted(ids.items()))
                if key in de_sensors:
                    errors.append("Duplicate sensitive DetElement identity")
                matrix = element.nominal().worldTransformation()
                values = matrix_values(matrix)
                de_sensors[key] = dict(name=str(element.name()), world=values, local=matrix_values(pv.ptr().GetMatrix()))
                actual = native_sensors.get(key)
                if actual is None:
                    errors.append("Sensitive DetElement missing expanded physical placement")
                elif (math.dist([x/unit for x in values[:3]],actual["center_mm"]) > 1e-7
                      or max(abs(a-b) for a,b in zip(values[3:], [actual["u"][j//3] if j%3==0 else actual["v"][j//3] if j%3==1 else actual["normal"][j//3] for j in range(9)])) > 1e-9):
                    errors.append("Sensitive DetElement world frame differs from physical instance: " + str(element.name()))
        for child in element.children():
            visit_element(child.second, ids)
    visit_element(d.world(), {})
    if set(de_sensors) != set(native_sensors):
        errors.append("Sensitive DetElement/expanded-placement identity sets differ")
    de_snapshot = {json.dumps(key,separators=(",", ":")):digest(value) for key,value in de_sensors.items()}
    if baseline and de_snapshot != baseline["sensitive_detelements"]:
        errors.append("Sensitive DetElement names/local/world frames differ from control")
    overlap_evidence = None
    if args.snapshot_only:
        if manifest or baseline or args.overlap_evidence:
            raise ValueError("Snapshot-only mode is restricted to the unchanged baseline")
        overlaps = None
    elif args.overlap_evidence:
        if manifest:
            raise ValueError("Retained overlap evidence is allowed only for unchanged baseline snapshots")
        evidence = json.loads(args.overlap_evidence.read_text())
        retained = evidence["execution"]["hashes"]
        required_files = [args.compact,args.expected,*libraries]
        if evidence["status"] != "PASS" or evidence["overlaps"] or evidence["execution"]["root_version"] != R.gROOT.GetVersion():
            raise ValueError("Retained baseline overlap report did not pass this ROOT runtime")
        if any(retained.get(path.name) != sha(path) for path in required_files):
            raise ValueError("Retained baseline overlap report differs in compact/expected/factory bytes")
        # The maintained validator hardcodes CheckOverlaps(1e-5 * dd4hep.mm).
        if retained.get("validate.py") != sha(REPO / "tools/tracker_dd4hep/validate.py"):
            raise ValueError("Retained validator differs; overlap tolerance cannot be verified")
        overlap_evidence = dict(path=str(args.overlap_evidence),sha256=sha(args.overlap_evidence),tolerance_mm=1e-5)
        overlaps = []
    else:
        manager.CheckOverlaps(1e-5*unit)
        overlaps = [dict(description=str(x.GetTitle()), penetration_mm=float(x.GetOverlap())/unit) for x in manager.GetListOfOverlaps()]
    if overlaps:
        errors.append(f"Full native geometry has {len(overlaps)} overlaps")
    rays = []
    for eta in (-4,-3,-2,-1,0,1,2,3,4):
        for phi in (0.,.37,1.11):
            rays.append(trace(manager, unit, [0.,0.,0.], audit.ray_direction(eta,phi), paths))
    # Target both cold contacts, notch edges and flex/module boundaries on one
    # known barrel instance; directions pass through actual native sensor frame.
    sensor = next(s for s in sensors if s["ids"] == dict(system=4,layer=0,stave=0,module=0,sensor=0))
    for u,v in ((-12.,0.),(12.,0.),(-22.049,0.),(-22.051,0.),(22.049,0.),(22.051,0.),
                (0.,32.049),(0.,32.051),(0.,48.499),(0.,48.501),(0.,50.)):
        origin = [sensor["center_mm"][j]+u*sensor["u"][j]+v*sensor["v"][j]-12*sensor["normal"][j] for j in range(3)]
        rays.append(trace(manager, unit, origin, sensor["normal"], paths, 24.))
    if baseline:
        if len(rays) != len(baseline["rays"]):
            errors.append("Ray sets differ")
        for i,(old,new) in enumerate(zip(baseline["rays"],rays)):
            if old["origin_mm"] != new["origin_mm"] or old["direction"] != new["direction"] or old["packed_sensor_ids"] != new["packed_sensor_ids"]:
                errors.append(f"Native ray definition/crossings differs: {i}")
            for material in old["material_path_mm"].keys() | new["material_path_mm"].keys():
                if not math.isclose(old["material_path_mm"].get(material,0.),new["material_path_mm"].get(material,0.),abs_tol=1e-7,rel_tol=1e-9):
                    errors.append(f"Native material ray differs: {i}/{material}")
    provenance = dict(source_revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO,text=True).strip(),
                      root_version=R.gROOT.GetVersion(),sha256={str(p):sha(p) for p in [args.compact,args.expected,args.compact.parent / "materials.xml",Path(__file__),*libraries]+([args.manifest] if args.manifest else [])+([args.baseline] if args.baseline else [])})
    args.snapshot.parent.mkdir(parents=True,exist_ok=True)
    args.snapshot.write_text(json.dumps(dict(constituents=native,sensitive_detelements=de_snapshot,rays=rays,provenance=provenance),separators=(",", ":"))+"\n")
    report = dict(status=("SNAPSHOT" if args.snapshot_only else "PASS") if not errors else "FAIL", errors=errors[:100], total_errors=len(errors),
                  constituent_placements=len(native), unique_native_logical_volumes=len(volume_addresses),
                  mother_instances=mother_instances, sensitive_comparison=comparison, unique_packed_ids=len(packed_ids),
                  shape_types=dict(shape_types), material_placement_counts=dict(material_counts),
                  shape_probes_checked=len(expected.get("shape_probes",[])),sensitive_detelements_checked=len(de_sensors),
                  overlaps=overlaps,retained_baseline_overlap_evidence=overlap_evidence,
                  overlap_test_performed=not args.snapshot_only and not bool(overlap_evidence),
                  baseline_comparison=dict(performed=bool(baseline),missing=len(missing),extra=len(extra),changed=len(changed)),
                  rays=rays, provenance=provenance,
                  limitations=["Native DD4hep/ROOT expanded IDs, signed transforms, exact constituent-solid fingerprints, per-instance finite probes and sparse material rays only.",
                               "General CSG total masses not asserted. No Geant4 per-sensor-ID/transform or ACTS conversion/response equivalence assertion."])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("status","total_errors","constituent_placements","unique_native_logical_volumes","mother_instances","unique_packed_ids","baseline_comparison")}))
    print(json.dumps(errors[:8]))
    # Match the maintained validator's explicit teardown for ROOT 6.40 after
    # CheckOverlaps; leave no live manager to static-destructor ordering.
    dd4hep.Detector.destroyInstance()
    if R.gGeoManager:
        R.gGeoManager.Delete()
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
