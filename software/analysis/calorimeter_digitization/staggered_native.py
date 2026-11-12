"""Native physical counts, silicon volumes, electrode references and full overlaps."""
import argparse
from array import array
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from angular_sample import ROOT, save, sha
from staggered_features import masks_from_xml


def read_profiles(compact):
    result = {}
    for readout in ET.parse(compact).findall("./readouts/readout"):
        system = 8 if readout.get("name") == "BARRELHits" else 9
        segmentation = readout.find("segmentation")
        numbers = list(map(float, segmentation.get("sensor_polygons_mm").split()))
        profiles, i = {}, 0
        while i < len(numbers):
            module, count = int(numbers[i]), int(numbers[i + 1]); i += 2
            if module in profiles or count < 3:
                raise ValueError("Invalid/duplicate readout mask")
            profiles[module] = dict(polygon=[numbers[j:j + 2] for j in range(i, i + 2 * count, 2)], table={})
            i += 2 * count
        table = list(map(float, segmentation.get("cell_table_mm", "").split()))
        if len(table) % 9:
            raise ValueError("Malformed electrode table")
        for i in range(0, len(table), 9):
            row = table[i:i + 9]
            profiles[int(row[0])]["table"][(int(row[1]), int(row[2]))] = row
        result[system] = profiles
    return result


def audit(args):
    import ROOT as R
    import dd4hep
    R.gROOT.SetBatch(True); R.gRandom.SetSeed(136)
    if R.gSystem.Load(str(args.library.resolve())) < 0:
        raise RuntimeError("Factory library load failed")
    detector = dd4hep.Detector.getInstance()
    counts, volumes, channels = Counter(), defaultdict(float), Counter()
    seen, profile_checks, cache = set(), {}, {}
    errors, cell_checks = [], 0
    profiles = read_profiles(args.sample / "detector.xml")
    geometry = masks_from_xml(args.sample / "detector.xml")
    expected_counts = {8: sum(len(l["polygons"]) for l in geometry[0]) * 16,
                       9: sum(len(l["polygons"]) for l in geometry[1]) * 32}
    def area(p):
        return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))) / 2
    expected_volumes = {8: sum(area(p) for l in geometry[0] for p in l["polygons"]) * .5 * 16,
                        9: sum(area(p) for l in geometry[1] for p in l["polygons"]) * .5 * 32}
    try:
        detector.fromXML(str((args.sample / "detector.xml").resolve()))
        manager, unit = detector.manager(), float(dd4hep.mm)
        def has_sensitive(volume):
            key = int(R.addressof(volume))
            if key not in cache:
                cache[key] = bool(dd4hep.Volume(volume).isSensitive()) or any(
                    has_sensitive(volume.GetNode(i).GetVolume()) for i in range(volume.GetNdaughters()))
            return cache[key]

        def visit(node, parent_ids):
            nonlocal cell_checks
            volume = node.GetVolume()
            if not has_sensitive(volume):
                return
            ids = dict(parent_ids)
            for field in dd4hep.PlacedVolume(node).volIDs():
                ids[str(field.first)] = int(field.second)
            if dd4hep.Volume(volume).isSensitive():
                system, module = ids["system"], ids["module"]
                for key, width in (("system",8),("side",2),("sector",4),("layer",6),("module",10)):
                    if not 0 <= ids[key] < 2**width:
                        raise ValueError("Parent ID overflow")
                vid = system | ids["side"]<<8 | ids["sector"]<<10 | ids["layer"]<<14 | module<<20
                if vid in seen:
                    raise ValueError("Duplicate physical sensitive ID")
                seen.add(vid); counts[system] += 1
                if "Silicon" not in str(volume.GetMaterial().GetName()):
                    raise ValueError("Sensitive material is not silicon")
                capacity = float(volume.GetShape().Capacity()) / unit**3
                volumes[system] += capacity
                key = (system, module)
                if key not in profile_checks:
                    readout = detector.readout("BARRELHits" if system == 8 else "EDGEHits")
                    decoder, segmentation = readout.idSpec().decoder(), readout.segmentation()
                    fields = R.std.vector("pair<string,int>")()
                    for k, value in ids.items():
                        fields.emplace_back(k, value)
                    if int(readout.idSpec().encode(fields)) != vid:
                        raise ValueError("Actual readout schema differs from packed parent IDs")
                    profile = profiles[system][module]; poly = profile["polygon"]
                    if not math.isclose(capacity, area(poly) * .5, rel_tol=1e-8, abs_tol=1e-7):
                        raise ValueError("Native active shape differs from readout mask area")
                    unique = set()
                    for ix in range(math.floor(min(p[0] for p in poly)/5.5), math.ceil(max(p[0] for p in poly)/5.5)):
                        for iy in range(math.floor(min(p[1] for p in poly)/5.5), math.ceil(max(p[1] for p in poly)/5.5)):
                            entry = profile["table"].get((ix,iy))
                            x,y = entry[5:7] if entry else ((ix+.5)*5.5,(iy+.5)*5.5)
                            local = array('d',[x*unit,y*unit,0.])
                            if not volume.GetShape().Contains(local):
                                if entry:
                                    raise ValueError("Declared electrode reference outside native sensitive shape")
                                continue
                            point = dd4hep.Position(*local)
                            cid = int(segmentation.cellID(point,point,vid)); back = segmentation.position(cid)
                            expected = (int(entry[3]),int(entry[4])) if entry else (ix,iy)
                            if (int(decoder.get(cid,"x")),int(decoder.get(cid,"y"))) != expected:
                                raise ValueError("Electrode ID roundtrip failed")
                            if not volume.GetShape().Contains(array('d',[back.x(),back.y(),back.z()])):
                                raise ValueError("Persisted electrode reference outside physical sensor")
                            for k,value in ids.items():
                                if int(decoder.get(cid,k)) != value:
                                    raise ValueError("Cell ID corrupts physical parent field")
                            unique.add(cid);cell_checks += 1
                    if not unique:
                        raise ValueError("No physical electrodes in sensitive module")
                    profile_checks[key] = (len(unique),capacity)
                ncell, old_capacity = profile_checks[key]
                if not math.isclose(capacity, old_capacity, rel_tol=1e-9, abs_tol=1e-7):
                    raise ValueError("Module ID reused for a different native shape")
                channels[system] += ncell
                if len(seen) % 100000 == 0:
                    print(f"Native sensitive IDs checked: {len(seen)}", flush=True)
            for i in range(volume.GetNdaughters()):
                visit(volume.GetNode(i),ids)
        visit(manager.GetTopNode(),{})
        for system in (8,9):
            if counts[system] != expected_counts[system]:
                errors.append(f"Physical sensitive count differs:{system}")
            if not math.isclose(volumes[system], expected_volumes[system], rel_tol=1e-8, abs_tol=1e-3):
                errors.append(f"Native sensitive silicon volume differs:{system}")
        print(f"Checked {len(seen)} native sensitive IDs and {cell_checks} electrode references; checking overlaps", flush=True)
        manager.CheckOverlaps(1e-5*unit)
        overlaps = [dict(description=str(o.GetTitle()),penetration_mm=float(o.GetOverlap())/unit)
                    for o in manager.GetListOfOverlaps()]
        if overlaps: errors.append(f"Native overlaps:{len(overlaps)}")
        report = dict(status="FAIL" if errors else "PASS",errors=errors,counts=dict(counts),
            unique_physical_sensitive_ids=len(seen),logical_module_masks_checked=len(profile_checks),
            native_electrode_references_checked=cell_checks,logical_electrodes_by_system=dict(channels),
            sensitive_volume_mm3=dict(volumes),expected_sensitive_volume_mm3=expected_volumes,
            overlap_tolerance_mm=1e-5,overlap_seed=136,overlaps=overlaps,
            compact_sha256=sha(args.sample/'detector.xml'),library_sha256=sha(args.library),
            validator_sha256=sha(__file__),mask_reader_sha256=sha(Path(__file__).with_name('staggered_features.py')),
            source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            ROOT=R.gROOT.GetVersion(),scope="Actual native sensitive modules, capacity, physical electrode references, parent IDs and full overlaps; no engineering acceptance")
        if args.output.exists(): raise ValueError("Refusing audit overwrite")
        save(args.output,report);print(report['status'],dict(counts),len(overlaps),'overlaps',flush=True)
        return bool(errors)
    finally:
        dd4hep.Detector.destroyInstance()
        if R.gGeoManager:R.gGeoManager.Delete()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sample',type=Path,required=True);p.add_argument('--library',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    raise SystemExit(audit(p.parse_args()))
