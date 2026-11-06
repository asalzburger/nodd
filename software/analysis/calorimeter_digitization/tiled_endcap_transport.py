#!/usr/bin/env python3
"""Raw Geant4 view of the current DES030 tiled endcap, without digitization.

Run with software/env/run.sh after its acts-spack preflight/runtime checks.
Only a task-owned fixture is selected: side1, sector0, first three layers,
all112 current square/custom modules, unchanged masks and local hardware.
The full48-layer/two-endcap detector is not simulated by this display sample.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
ID_DESCRIPTOR = "system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def record_path(path):
    return os.path.relpath(Path(path).resolve(), ROOT)


def sensor_offset(expected, module_id):
    """Use the exported sensitive primitive's actual layer-local depth."""
    pieces = [p for p in expected["hardware"]["layer_parts"]
              if p.get("module") == module_id and p["role"] == "sensitive"]
    if len(pieces) != 1:
        raise ValueError("Missing or repeated sensitive primitive")
    return pieces[0]["center_mm"][2]


def verify_component(component):
    expected = json.loads((component / "expected.json").read_text())
    if (expected["layout_name"] != "edges" or len(expected["modules"]) != 112
            or sum(not m["full"] for m in expected["modules"]) != 36):
        raise ValueError("Expected current112module wedge,76 squares+36 custom; old quadrant exports are unsupported")
    sources = dict(expected["source_sha256"])
    sources.update(expected["layout_report"]["source_sha256"])
    for name, digest in sources.items():
        if sha(ROOT / name) != digest:
            raise ValueError("Current source differs from component inventory: " + name)
    tree = ET.parse(component / "calorimeter.xml")
    readout = tree.getroot().find("readouts/readout")
    if readout.find("id").text != ID_DESCRIPTOR or readout.find("segmentation").get("type") != "nODDEdgeGrid":
        raise ValueError("Unexpected current endcap readout")
    detector = tree.getroot().find("detectors/detector")
    if detector.get("type") != "nODDEcalEdgePrototype" or detector.get("id") != "8":
        raise ValueError("Unexpected standalone endcap factory/system")
    active = detector.find("region[@name='edge_layer']")
    sensitive = [p for p in active.findall("piece") if p.get("module") is not None]
    if sorted(int(p.get("module")) for p in sensitive) != sorted(m["index"] for m in expected["modules"]):
        raise ValueError("Sensitive module IDs differ between compact and inventory")
    return expected, tree, sources


def prepare(args):
    expected, tree, sources = verify_component(args.component)
    args.work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.component / "materials.xml", args.work / "materials.xml")
    shutil.copyfile(args.component / "expected.json", args.work / "expected.json")
    detector = tree.getroot().find("detectors/detector")
    for region in list(detector.findall("region")):
        if region.get("name") != "edge_layer":
            detector.remove(region)
    for replica in list(detector.findall("replica")):
        if not (replica.get("region") == "edge_layer" and replica.get("side") == "1"
                and replica.get("sector") == "0" and int(replica.get("layer")) < 3):
            detector.remove(replica)
    if len(detector.findall("replica")) != 3:
        raise ValueError("Expected exactly three selected physical layers")
    ET.indent(tree, space="  ")
    tree.write(args.work / "tiled-fixture.xml", encoding="utf-8", xml_declaration=True)
    save(args.work / "fixture.json", {
        "status": "isolated raw-hit display fixture; no detector acceptance",
        "input_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": sources,
        "component": {"path": record_path(args.component),
                      "expected_sha256": sha(args.component / "expected.json"),
                      "compact_sha256": sha(args.component / "calorimeter.xml"),
                      "materials_sha256": sha(args.component / "materials.xml")},
        "selected": {"system": 8, "side": 1, "sector": 0, "layers": [0, 1, 2],
                     "modules_per_wedge_layer": 112, "square_modules": 76, "custom_modules": 36,
                     "logical_pads_per_wedge_layer": sum(len(m["pads"]) for m in expected["modules"])},
        "scope": "All 112 modules and unchanged local material per selected layer; other sectors/sides/layers and support frame omitted. Standalone system 8; LAYOUT-001 integration remaps this root to 9.",
        "fixture_sha256": sha(args.work / "tiled-fixture.xml"),
        "id_descriptor": ID_DESCRIPTOR,
        "script_sha256": sha(__file__),
    })


def run(args):
    if not (args.work / "fixture.json").exists():
        raise ValueError("Prepare the fixture first")
    fixture = json.loads((args.work / "fixture.json").read_text())
    if fixture["fixture_sha256"] != sha(args.work / "tiled-fixture.xml"):
        raise ValueError("Fixture changed after selection")
    if not (args.factory / "libnODDCalorimeterPrototype.components").exists():
        raise ValueError("Build Components_nODDCalorimeterPrototype to register the custom segmentation/factory")
    environment = os.environ.copy()
    for name in ("DD4HEP_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "LD_LIBRARY_PATH"):
        environment[name] = str(args.factory.resolve()) + os.pathsep + environment.get(name, "")
    expected = json.loads((args.work / "expected.json").read_text())
    if args.events % 4:
        raise ValueError("Stratified event total must be divisible by four")
    scenarios = [("broad", args.events // 2, .04, .49, -.18, .18)]
    for module_id in (26, 27):
        module = next(m for m in expected["modules"] if m["index"] == module_id)
        points = [[module["center_mm"][0] + x, module["center_mm"][1] + y]
                  for x, y in module["active"]]
        z = expected["layout_report"]["front_mm"] + sensor_offset(expected, module_id)
        theta = [math.atan2(math.hypot(x, y), z) for x, y in points]
        phi = [math.atan2(y, x) for x, y in points]
        scenarios.append((f"module{module_id}", args.events // 4,
                          min(theta), max(theta), min(phi), max(phi)))
    runs = []
    for index, (name, count, t0, t1, p0, p1) in enumerate(scenarios):
        command = [sys.executable, shutil.which("ddsim"),
                   "--compactFile", str((args.work / "tiled-fixture.xml").resolve()),
                   "--runType", "batch", "--numberOfEvents", str(count), "--enableGun",
                   "--gun.particle", "mu-", "--gun.energy", "10*GeV", "--gun.position", "0 0 0",
                   "--gun.distribution", "uniform", "--gun.thetaMin", str(t0), "--gun.thetaMax", str(t1),
                   "--gun.phiMin", str(p0), "--gun.phiMax", str(p1), "--random.seed", str(args.seed + index),
                   "--physics.list", "FTFP_BERT", "--part.userParticleHandler", "",
                   "--outputConfig.forceEDM4HEP", "--outputFile", str((args.work / (name + ".edm4hep.root")).resolve())]
        with (args.work / (name + ".log")).open("w") as log:
            result = subprocess.run(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
        runs.append({"name": name, "command": [v.replace(str(ROOT), ".") for v in command],
                     "exit_code": result.returncode, "events_requested": count, "seed": args.seed + index,
                     "theta_range_rad": [t0, t1], "phi_range_rad": [p0, p1]})
        save(args.work / "execution.json", {"runs": runs, "events_requested": args.events,
             "particle": "mu-", "energy_GeV": 10, "field_T": 0, "physics_list": "FTFP_BERT",
             "direction_sampling": "Stratified display illumination: half broad wedge, one quarter angular bounding rectangle of module26 active mask, one quarter module27. DDSim uniform theta/phi sampling includes misses. No efficiency inference.",
             "factory_path": record_path(args.factory)})
        if result.returncode:
            raise RuntimeError("Geant4 transport failed; inspect ignored " + name + ".log")


def decode(cell_id):
    def signed(value):
        return value - 64 if value >= 32 else value
    return {"system": cell_id & 255, "side": (cell_id >> 8) & 3,
            "sector": (cell_id >> 10) & 15, "layer": (cell_id >> 14) & 63,
            "module": (cell_id >> 20) & 1023,
            "x": signed((cell_id >> 30) & 63), "y": signed((cell_id >> 36) & 63)}


def analyze(args):
    from podio import root_io
    import ROOT as pyroot
    fixture = json.loads((args.work / "fixture.json").read_text())
    execution = json.loads((args.work / "execution.json").read_text())
    expected = json.loads((args.work / "expected.json").read_text())
    verify_component(args.component)
    if fixture["fixture_sha256"] != sha(args.work / "tiled-fixture.xml"):
        raise ValueError("Executed fixture differs from recorded fixture")
    catalog = {(m["index"], *p["key"]): (m, p) for m in expected["modules"] for p in m["pads"]}
    bins = defaultdict(lambda: {"saved_hit_count": 0, "event_count": 0,
                                "energy_sum_GeV": 0., "energy_sum_squared_GeV2": 0.})
    def frames():
        for run in execution["runs"]:
            reader = root_io.Reader(str(args.work / (run["name"] + ".edm4hep.root")))
            count = 0
            for frame in reader.get("events"):
                count += 1
                yield frame
            if count != run["events_requested"]:
                raise ValueError("Incomplete stratum: " + run["name"])
    events = hits = empty = 0
    max_position_error = 0.
    modules_hit, families_hit = set(), set()
    for frame in frames():
        events += 1
        seen = set()
        event_hits = 0
        for hit in frame.get("EDGEHits"):
            cell_id = int(hit.getCellID())
            fields = decode(cell_id)
            if fields["system"] != 8 or fields["side"] != 1 or fields["sector"] != 0 or fields["layer"] not in (0, 1, 2):
                raise ValueError("Hit outside selected parent-ID scope")
            key = (fields["module"], fields["x"], fields["y"])
            if key not in catalog:
                raise ValueError("Hit electrode absent from current DES030 catalog: " + str(key))
            module, pad = catalog[key]
            position = hit.getPosition()
            reference = [module["center_mm"][0] + pad["reference_mm"][0],
                         module["center_mm"][1] + pad["reference_mm"][1],
                         expected["layout_report"]["front_mm"] + fields["layer"] * expected["layout_report"]["layer_pitch_mm"] + sensor_offset(expected, module["index"])]
            error = max(abs(value - target) for value, target in zip((position.x, position.y, position.z), reference))
            max_position_error = max(max_position_error, error)
            if error > .002:
                raise ValueError("Saved hit position differs from current electrode reference")
            energy = float(hit.getEnergy())
            if not math.isfinite(energy) or energy <= 0:
                raise ValueError("Invalid raw deposited energy")
            b = bins[(fields["layer"], *key)]
            b["saved_hit_count"] += 1
            b["energy_sum_GeV"] += energy
            b["energy_sum_squared_GeV2"] += energy * energy
            seen.add((fields["layer"], *key))
            modules_hit.add(module["index"])
            families_hit.add(module["family"])
            hits += 1
            event_hits += 1
        for key in seen:
            bins[key]["event_count"] += 1
        empty += event_hits == 0
    if events != execution["events_requested"] or not hits:
        raise ValueError("Incomplete or empty transport output")
    if "square" not in families_hit or len(families_hit) < 2:
        raise ValueError("Display sample did not illuminate both square and custom sensors")
    libraries = sorted(args.factory.glob("*nODDCalorimeterPrototype*.dylib")) + sorted(args.factory.glob("*nODDCalorimeterPrototype*.so"))
    if len(libraries) != 1:
        raise ValueError("Cannot identify unique executed factory library")
    rows = []
    for (layer, module_id, x, y), values in sorted(bins.items()):
        module, pad = catalog[(module_id, x, y)]
        rows.append({"side": 1, "sector": 0, "layer": layer, "module": module_id,
                     "pad_key": [x, y], "family": module["family"],
                     "position_mm": [module["center_mm"][0] + pad["reference_mm"][0],
                                     module["center_mm"][1] + pad["reference_mm"][1],
                                     expected["layout_report"]["front_mm"] + layer * expected["layout_report"]["layer_pitch_mm"] + sensor_offset(expected, module_id)],
                     "pad_area_mm2": pad["area_mm2"], **values})
    result = {"status": "actual raw Geant4 sensitive-hit display sample; PROTOTYPE",
              "display_caption": f"{events} simulated 10 GeV muons; +z endcap sector 0, first 3 layers; stratified broad/module 26/module 27 display illumination; raw deposited hits, no digitization.",
              "digitization": "none", "geometry": fixture, "execution": json.loads(json.dumps(execution).replace(str(Path.home()), "${USER_HOME}")),
              "events": events, "events_without_saved_hits": empty, "saved_hits": hits,
              "illuminated_modules": len(modules_hit), "illuminated_sensor_families": sorted(families_hit),
              "id_checks": {"invalid_parent_or_pad_ids": 0, "max_cell_reference_position_error_mm": max_position_error,
                            "position_tolerance_mm": .002,
                            "tolerance_reason": "float hit-position persistence at 4 m; software consistency only"},
              "binning": "Exact current physical electrode keys(layer,module,x,y); unlisted catalog bins have zero saved hits in this sample.",
              "normalization": "Raw positive silicon energy deposits in GeV, saved-hit and event counts; denominator is all generated events, including no-hit events.",
              "bins": rows,
              "artifacts": {record_path(p): {"sha256": sha(p), "bytes": p.stat().st_size}
                            for p in [args.work / "tiled-fixture.xml", args.work / "materials.xml", libraries[0],
                                      args.factory / "libnODDCalorimeterPrototype.components"]
                            + [args.work / (r["name"] + suffix) for r in execution["runs"]
                               for suffix in (".edm4hep.root", ".log")]},
              "runtime": {"ROOT": str(pyroot.gROOT.GetVersion()),
                          "Geant4": subprocess.check_output(["geant4-config", "--version"], text=True).strip(),
                          "ddsim_entrypoint_sha256": sha(shutil.which("ddsim"))},
              "script_sha256": sha(__file__),
              "reproduction": [
                  "software/env/run.sh cmake -S prototypes/calorimeter -B build/tiled-endcap-view/factory -G Ninja -DCMAKE_BUILD_TYPE=Release",
                  "software/env/run.sh cmake --build build/tiled-endcap-view/factory --target Components_nODDCalorimeterPrototype --parallel 4",
                  "python3 software/analysis/calorimeter_digitization/tiled_endcap_transport.py prepare --component " + record_path(args.component),
                  "software/env/run.sh python3 software/analysis/calorimeter_digitization/tiled_endcap_transport.py run --component " + record_path(args.component) + " --events 512 --seed 118030",
                  "software/env/run.sh python3 software/analysis/calorimeter_digitization/tiled_endcap_transport.py analyze --component " + record_path(args.component)],
              "limitations": ["One positive-end wedge, three layers, 112 modules/layer; no complete detector transport.",
                              "Muon illumination chosen for a raw pad display; no calibration, digitization, shower response or acceptance measurement.",
                              "Other end/sectors/layers and supported wedge frame omitted; all selected module masks, electrodes and local layer hardware retained."]}
    save(args.output, result)
    print(json.dumps({k: result[k] for k in ("events", "saved_hits", "illuminated_modules", "illuminated_sensor_families", "id_checks")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "run", "analyze"))
    parser.add_argument("--component", type=Path, required=True)
    parser.add_argument("--work", type=Path, default=ROOT / "build/tiled-endcap-view")
    parser.add_argument("--factory", type=Path, default=ROOT / "build/tiled-endcap-view/factory")
    parser.add_argument("--events", type=int, default=512)
    parser.add_argument("--seed", type=int, default=118030)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/validation/issue117/previews/nodd-tiled-endcap-hit-bins.json")
    args = parser.parse_args()
    if args.events < 1:
        raise ValueError("Need a positive finite event count")
    {"prepare": prepare, "run": run, "analyze": analyze}[args.stage](args)


if __name__ == "__main__":
    main()
