#!/usr/bin/env python3
"""PROTOTYPE native Fatras comparison with separately identified old/current inputs."""

import argparse
import copy
import gzip
import importlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = REPO / "build/fatras-baseline-comparison"
RUNTIME = REPO.parent / "nodd-software-layout"
PREVIOUS = REPO.parent / "nodd-gen3-material-mapping"
PORTAL_DIR = PREVIOUS / "build/gen3-material-map-run/native"
OBSERVER_DIR = PREVIOUS / "build/truth-tracking-baseline/native"
OLD_CASE = PREVIOUS / "build/truth-tracking-baseline/fatras-pt1"
OLD_TRAINING = PREVIOUS / "build/truth-tracking-baseline/training-fatras"
SOURCE_FILES = ["software/analysis/fatras_baseline_comparison/run_native.py",
    "software/analysis/material_baseline_comparison/map_workflow.py",
    "software/running/nodd_truth_tracking.py", "software/analysis/truth_tracking/runtime.py",
    "software/analysis/truth_tracking/digitization.py", "software/analysis/truth_tracking/calibrate_errors.py",
    "software/analysis/truth_tracking/campaign.json", "software/analysis/gen3_material_mapping/material_runtime.py",
    "software/source/ActsExamples/TruthTracking/TruthTracking.cpp",
    "software/source/ActsExamples/TruthTracking/CMakeLists.txt",
    "software/source/ActsExamples/MaterialMapping/PortalMaterial.cpp"]


def load(path):
    path = Path(path)
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as stream:
        return json.load(stream)


def helper(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


mapping = helper(REPO / "software/analysis/material_baseline_comparison/map_workflow.py", "mapping_controls")
sha = mapping.digest
write = mapping.write
identity = mapping.identity


def campaign(baseline):
    config = load(REPO / "software/analysis/truth_tracking/campaign.json")
    current = baseline == "current"
    config["geometry"] = "DES043 PR110+112 current" if current else "PR100 old 530080cf"
    config["pt_GeV"] = [1., 5., 10., 100.]
    config["simulations"] = ["fatras"]
    config["digitization"]["short_strip_pitch_mm"] = [0.075, 2. if current else 0.5]
    directory = "baseline-material-comparison" if current else "gen3-material-map-run"
    config["material_map"] = f"docs/validation/{directory}/material_map.json.gz"
    config["selection_manifest"] = f"docs/validation/{directory}/selection.json"
    if current:
        config["error_training"]["error_table"] = "build/fatras-baseline-comparison/calibration-current/hit-error-parameterization.json"
    return config


def check_settings(config):
    expected = {"particles_per_event": 1, "vertex_mm": [0., 0., 0.],
                "seed": 42042, "field_Bz_T": 3., "eta_range": [-4., 4.],
                "phi_range_rad": [-math.pi, math.pi], "randomize_charge": True}
    if any(config.get(k) != v for k, v in expected.items()):
        raise ValueError("Comparison generator/field settings differ from the frozen contract")
    if config["truth_tracking"]["minimum_measurements"] != 7:
        raise ValueError("Require seven unique measurements")
    training = config["error_training"]
    if (training["events"], training["seed"], training["pt_range_GeV"], training["log_uniform_pt"]) != (
            50000, 142042, [1., 100.], True):
        raise ValueError("Independent training contract changed")


def check_error_identity(config, audit, table_path):
    if sha(table_path) != audit["table_sha256"]:
        raise ValueError("Frozen error table hash differs from its calibration audit")
    reference = audit["configuration"]
    for key in ("digitization", "field_Bz_T", "eta_range", "phi_range_rad", "vertex_mm"):
        if config[key] != reference[key]:
            raise ValueError("Error calibration belongs to a different response/geometry: " + key)
    if audit["training"] != config["error_training"]:
        # The output table locator may differ; all sampling/statistical settings must match.
        a, b = copy.deepcopy(audit["training"]), copy.deepcopy(config["error_training"])
        a.pop("error_table", None); b.pop("error_table", None)
        if a != b:
            raise ValueError("Error calibration training identity differs")


def verify_named_files(actual, evidence):
    known = {item["name"]: item["sha256"] for item in evidence}
    for item in actual:
        if Path(item["path"]).name not in known or known[Path(item["path"]).name] != item["sha256"]:
            raise ValueError("Geometry/binary differs from retained native evidence: " + item["path"])


def source_fingerprint(revision=None):
    result = {}
    for name in SOURCE_FILES:
        path = REPO / name
        result[name] = sha(path)
        if revision:
            payload = subprocess.check_output(["git", "show", f"{revision}:{name}"], cwd=REPO)
            import hashlib
            if result[name] != hashlib.sha256(payload).hexdigest():
                raise ValueError("Executed source differs from requested commit: " + name)
    return result


def prepare(args):
    if (args.root / "contract.json").exists():
        raise FileExistsError("Input contract already exists; select a fresh root")
    old = load(OLD_CASE / "run-report.json")
    training = load(OLD_TRAINING / "run-report.json")
    old_audit = load(REPO / "docs/validation/truth-tracking-baseline/hit-error-training-audit.json")
    if sha(OLD_TRAINING / "run-report.json") != old_audit["training_report_sha256"]:
        raise ValueError("Old training report is not the audited frozen input")
    measurements = OLD_TRAINING / "measurements.root"
    if sha(measurements) != old_audit["training_measurements_sha256"]:
        raise ValueError("Old training measurements changed")
    observer = next(OBSERVER_DIR.glob("nodd_truth_tracking*.so"))
    observer_source = REPO / "software/source/ActsExamples/TruthTracking/TruthTracking.cpp"
    verify_named_files([identity(observer, "observer"), identity(observer_source, "observer_source")],
                       [f for f in old["provenance"]["files"] if f["role"] in ("observer", "observer_source")])
    portal = next(PORTAL_DIR.glob("nodd_portal_material*.so"))
    portal_evidence = load(PREVIOUS / "build/gen3-material-map-run/homogeneous-smoke-final/mapping/mapping-report.json")
    mapping.verify_sidecar_evidence(portal_evidence, portal,
        REPO / "software/source/ActsExamples/MaterialMapping/PortalMaterial.cpp")
    result = {"schema_version": 1, "status": "PROTOTYPE", "baselines": {},
              "observer_evidence": identity(OLD_CASE / "run-report.json", "successful_native_case"),
              "portal": identity(portal, "portal_sidecar"),
              "old_training_report": identity(OLD_TRAINING / "run-report.json", "training_report"),
              "old_training_measurements": identity(measurements, "training_measurements")}
    for baseline in ("old", "current"):
        config = campaign(baseline); check_settings(config)
        build = RUNTIME / "build/dd4hep" if baseline == "old" else REPO / "build/material-comparison/dd4hep"
        geometry = mapping.baseline_files(build)
        if baseline == "old":
            verify_named_files([f for f in geometry if f["role"] != "expected.json"], old["provenance"]["files"])
            check_error_identity(config, old_audit, REPO / "docs/validation/truth-tracking-baseline/hit-error-parameterization.json")
        else:
            evidence = load(REPO / "docs/validation/baseline-material-comparison/preparation-report.json")
            mapping.assert_same_geometry(evidence, build)
        native = args.root / "native" / baseline
        native.mkdir(parents=True, exist_ok=True)
        copy_path = native / observer.name
        shutil.copy2(observer, copy_path)
        if sha(copy_path) != sha(observer): raise ValueError("Observer copy changed bytes")
        write(args.root / f"campaign-{baseline}.json", config)
        result["baselines"][baseline] = {"build": str(build), "geometry": geometry,
            "geometry_revision": "530080cfe16c7513228bf60238b99d4b9938538a" if baseline == "old" else "62f6056395e0dfee0c7985cf24e88dc9919c4e2d",
            "planes": 45646 if baseline == "old" else 46682,
            "observer": identity(copy_path, "observer"),
            "selection": identity(REPO / config["selection_manifest"], "selection"),
            "map": identity(REPO / config["material_map"], "material_map"),
            "campaign": identity(args.root / f"campaign-{baseline}.json", "campaign")}
    # Runtime verification is explicit, not inferred from the stale registry.
    sys.path.insert(0, str(REPO / "software/analysis/gen3_material_mapping"))
    import material_runtime as material
    ROOT, acts, sidecar = material.native_imports(PORTAL_DIR)
    import acts.examples.geant4
    sys.path.insert(0, str(args.root / "native/old"))
    observer_module = importlib.import_module("nodd_truth_tracking")
    if (observer_module.pybind11_internals_version, sidecar.pybind11_internals_version) != (11, 11):
        raise ValueError("Native sidecar ABI differs from selected ACTS internals11")
    result["runtime"] = {"ROOT": ROOT.gROOT.GetVersion(), "python": sys.version,
        "observer_pybind11": observer_module.pybind11_version,
        "portal_pybind11": sidecar.pybind11_version, "pybind11_internals_version": 11}
    write(args.root / "contract.json", result)
    print(json.dumps({"outcome": "prepared", "runtime": result["runtime"]}, indent=2))


def native_training(args, config, acts, detector, geometry, observer):
    """Native measurement-only prefix of nodd_truth_tracking.run; no fitted-pull input."""
    from acts.examples.simulation import addParticleGun, MomentumConfig, EtaConfig, PhiConfig, ParticleConfig, addFatras
    from acts.examples.root import RootParticleWriter, RootMeasurementWriter
    from acts.examples import json as acts_json
    u, level = acts.UnitConstants, acts.logging.WARNING
    rnd = acts.examples.RandomNumbers(seed=config["error_training"]["seed"])
    field = acts.ConstantBField(acts.Vector3(0., 0., config["field_Bz_T"] * u.T))
    seq = acts.examples.Sequencer(events=args.events, numThreads=1, outputDir=str(args.output), logLevel=level)
    for decorator in detector.contextDecorators(): seq.addContextDecorator(decorator)
    addParticleGun(seq, ParticleConfig(num=1, pdg=acts.PdgParticle.eMuon, randomizeCharge=True),
        MomentumConfig(1*u.GeV, 100*u.GeV, transverse=True, logUniform=True),
        EtaConfig(*config["eta_range"], uniform=True), PhiConfig(*config["phi_range_rad"]),
        vtxGen=acts.examples.GaussianVertexGenerator(mean=acts.Vector4(0.,0.,0.,0.),stddev=acts.Vector4(0.,0.,0.,0.)),
        multiplicity=1, rnd=rnd, logLevel=level)
    seq.addWriter(RootParticleWriter(level=level, inputParticles="particles_generated",filePath=str(args.output/"particles.root")))
    addFatras(seq, geometry, field, rnd=rnd, inputParticles="particles_generated", enableInteractions=True, logLevel=level)
    seq.addAlgorithm(acts.examples.DigitizationAlgorithm(acts.examples.DigitizationAlgorithm.Config(
        digitizationConfigs=acts_json.readDigiConfigFromJson(str(args.output/"digitization.json")),
        surfaceByIdentifier=geometry.geoIdSurfaceMap(), randomNumbers=rnd, inputSimHits="simhits",
        outputMeasurements="measurements", outputMeasurementParticlesMap="measurement_particles_map_raw",
        outputMeasurementSimHitsMap="measurement_simhits_map", outputParticleMeasurementsMap="particle_measurements_map_raw",
        outputSimHitMeasurementsMap="simhit_measurements_map", doMerge=True, mergeCommonCorner=True, minEnergyDeposit=0.),level))
    seq.addAlgorithm(observer.UniqueAssociations())
    seq.addWriter(RootMeasurementWriter(level=level,inputMeasurements="measurements",inputClusters="clusters",
        inputSimHits="simhits",inputMeasurementSimHitsMap="measurement_simhits_map",
        surfaceByIdentifier=geometry.geoIdSurfaceMap(),filePath=str(args.output/"measurements.root")))
    seq.run()


def run_job(args):
    if not args.pilot and not args.source_revision:
        raise ValueError("Full jobs require the coordinator's committed source revision")
    if args.pilot and args.events > 200: raise ValueError("Pilot must have at most200 events")
    if not args.pilot and args.events != (50000 if args.stage == "train" else 20000):
        raise ValueError("Full event count differs from the frozen contract")
    if args.stage == "train" and args.baseline != "current": raise ValueError("Only current calibration is regenerated")
    if (args.output / "run-report.json").exists(): raise FileExistsError("Output report exists; select a fresh case")
    tracked = source_fingerprint(args.source_revision)
    contract = load(args.root / "contract.json")
    baseline = contract["baselines"][args.baseline]
    for item in [*baseline["geometry"], baseline["observer"], baseline["selection"], baseline["map"], baseline["campaign"], contract["portal"]]:
        if sha(item["path"]) != item["sha256"]: raise ValueError("Frozen input changed: " + item["path"])
    config = load(baseline["campaign"]["path"]); check_settings(config)
    sys.path.insert(0, str(REPO / "software/analysis/truth_tracking"))
    sys.path.insert(0, str(REPO / "software/analysis/gen3_material_mapping"))
    runner = helper(REPO / "software/running/nodd_truth_tracking.py", "maintained_truth_runner")
    material = importlib.import_module("material_runtime")
    digi_module = importlib.import_module("digitization")
    native_runtime = importlib.import_module("runtime")
    ROOT, acts, sidecar = material.native_imports(PORTAL_DIR)
    import acts.examples.geant4
    observer_dir = Path(baseline["observer"]["path"]).parent
    sys.path.insert(0,str(observer_dir)); observer=importlib.import_module("nodd_truth_tracking")
    expanded = observer_dir / "material_map.json"
    native_runtime.material_map(REPO / config["material_map"], expanded)
    args.output.mkdir(parents=True, exist_ok=True)
    native_args = SimpleNamespace(output=args.output, events=args.events, threads=1, pt=args.pt,
        simulation="fatras", training=args.stage == "train", geant4_run_mode="standard", write_simhits=False,
        error_table=None, manifest=Path(baseline["selection"]["path"]), nodd_dir=RUNTIME,
        build_dir=Path(baseline["build"]), native_module_dir=PORTAL_DIR)
    report = {"schema_version":1,"status":"PROTOTYPE","outcome":"started","baseline":args.baseline,
        "simulation":"fatras","pt_GeV":args.pt,"events":args.events,"threads":1,
        "seed":config["error_training"]["seed"] if native_args.training else config["seed"],
        "campaign":config,"training":native_args.training,"pilot":args.pilot,
        "scientific_input_revision":args.source_revision,
        "analysis_source_revision_at_launch":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO,text=True).strip(),
        "executed_source_sha256":tracked,"command":sys.argv,"geometry_source_revision":baseline["geometry_revision"],
        "native_binaries":{"observer":baseline["observer"],"portal":contract["portal"]}}
    start=time.monotonic()
    try:
        detector, geometry, context, surfaces, decoration = material.prepare_geometry(native_args,
            material.load_manifest(native_args.manifest),acts,sidecar,expanded)
        sensors=load_native_report(detector)
        if len(sensors) != baseline["planes"]:raise ValueError("Native sensor inventory differs from baseline")
        digi, counts=digi_module.build_config(sensors,config["digitization"])
        write(args.output/"digitization-uncalibrated.json",digi)
        if args.baseline == "old":
            original=load(OLD_TRAINING/"run-report.json")
            known=[f["sha256"] for f in original["provenance"]["files"] if f["name"]=="digitization.json"]
            if known != [sha(args.output/"digitization-uncalibrated.json")]:
                raise ValueError("Old native digitization differs from frozen training")
        if not native_args.training and not args.uncalibrated:
            table=args.table or (REPO/"docs/validation/truth-tracking-baseline/hit-error-parameterization.json" if args.baseline=="old" else args.root/"calibration-current/hit-error-parameterization.json")
            audit_path=REPO/"docs/validation/truth-tracking-baseline/hit-error-training-audit.json" if args.baseline=="old" else args.root/"calibration-current/hit-error-training-audit.json"
            check_error_identity(config,load(audit_path),table)
            digi_module.apply_variance_table(digi,load(table))
            native_args.error_table=args.output/"error-table.json";shutil.copy2(table,native_args.error_table)
            report["error_table"]={"path":str(native_args.error_table),"sha256":sha(native_args.error_table),"audit":identity(audit_path,"calibration_audit")}
        elif args.uncalibrated and not args.pilot:raise ValueError("Only explicitly labelled pilots may omit calibration")
        else:report["error_table"]=None
        write(args.output/"digitization.json",digi)
        report.update(native_decoration=decoration,digitization_sensors_by_system=counts)
        if native_args.training:native_training(native_args,config,acts,detector,geometry,observer)
        else:runner.run(native_args,config,ROOT,acts,detector,geometry,observer)
        names=("particles.root","measurements.root") if native_args.training else (
            "particles.root","particles_selected.root","audit.root","tracksummary_kf.root","measurements.root",
            "trackstates_kf.root","performance_kf.root")
        report["root_inventory"]={name:native_runtime.root_inventory(ROOT,args.output/name) for name in names}
        if native_args.training:
            tree=ROOT.RDataFrame("particles",str(args.output/"particles.root"))
            report["counts"]={"events":int(tree.Count().GetValue()),"generated":int(tree.Count().GetValue()),
                "measurements":report["root_inventory"]["measurements.root"]["measurements"]["entries"]}
        else:
            audit=ROOT.RDataFrame("audit",str(args.output/"audit.root"))
            fields=("generated","simhits","measurements","selected","fit_attempts","fit_tracks","invalid_covariance",
                    "primary_measurements","original_proto_measurements","corrected_proto_measurements","primary_measurement_associations_raw")
            report["counts"]={name:int(audit.Sum["ULong64_t"](name).GetValue()) for name in fields}
            report["counts"]["events"]=int(audit.Count().GetValue())
        if report["counts"]["events"]!=args.events or report["counts"]["generated"]!=args.events:
            raise ValueError("Native output lost requested one-muon events")
        extras=[("native_output",args.output/name) for name in names]+[("digitization",args.output/"digitization.json"),
            ("observer",Path(observer.__file__)),("observer_source",REPO/"software/source/ActsExamples/TruthTracking/TruthTracking.cpp"),
            ("saved_material_map",REPO/config["material_map"])]
        report["provenance"]=material.provenance(native_args,sidecar,extras)
        native_build=Path(importlib.import_module("acts.ActsPythonBindings").__file__).parents[2]
        libraries=[]
        for name in ("ActsExamplesFatras","ActsExamplesDigitization","ActsExamplesTrackFitting",
                     "ActsExamplesTruthTracking","ActsExamplesIoRoot","ActsExamplesGeant4"):
            path=native_build/"lib"/("lib"+name+(".dylib" if sys.platform=="darwin" else ".so"))
            if path.is_file():libraries.append(identity(path,"runtime_library"))
        for name in ("acts.examples.ActsExamplesPythonBindings","acts.examples.ActsExamplesPythonBindingsGeant4"):
            libraries.append(identity(importlib.import_module(name).__file__,"runtime_binding"))
        report["native_binaries"]["processing_libraries"]=libraries
        report["output_sha256"]={name:sha(args.output/name) for name in names}
        report["ROOT"]=ROOT.gROOT.GetVersion()
        if source_fingerprint(args.source_revision)!=tracked:raise ValueError("Executed source changed during the case")
        report["outcome"]="completed"
    except BaseException as error:
        report["outcome"]="failed";report["error"]=f"{type(error).__name__}: {error}"
        raise
    finally:
        report["wall_seconds"]=time.monotonic()-start
        write(args.output/"run-report.json",report)
    print(json.dumps({"outcome":report["outcome"],"baseline":args.baseline,"counts":report["counts"],"wall_seconds":report["wall_seconds"]}))


def load_native_report(detector):
    return json.loads(detector.geometryReport())["sensors"]


def calibrate(args):
    source=REPO/"software/analysis/truth_tracking/calibrate_errors.py"
    copy_path=args.root/"calibration-source/software/analysis/truth_tracking/calibrate_errors.py"
    copy_path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,copy_path)
    if sha(copy_path)!=sha(source):raise ValueError("Calibration source copy changed bytes")
    command=[str(args.analysis_python),"-B",str(copy_path),"--training",str(args.root/"training-current"),
             "--acts-source",str(RUNTIME/"software/submodules/acts"),"--output",str(args.root/"calibration-current")]
    with (args.root/"calibration-current.log").open("w") as stream:
        result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=False)
    write(args.root/"calibration-command.json",{"command":command,"exit_code":result.returncode,
        "source":identity(source,"maintained_source"),"copy":identity(copy_path,"byte_identical_executed_copy")})
    if result.returncode:raise RuntimeError("Calibration failed; see calibration-current.log")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage",choices=("prepare","case","train","calibrate"))
    p.add_argument("--root",type=Path,default=DEFAULT_ROOT)
    p.add_argument("--baseline",choices=("old","current"),default="current")
    p.add_argument("--pt",type=float,choices=(1.,5.,10.,100.))
    p.add_argument("--events",type=int)
    p.add_argument("--output",type=Path)
    p.add_argument("--table",type=Path)
    p.add_argument("--analysis-python",type=Path)
    p.add_argument("--source-revision")
    p.add_argument("--pilot",action="store_true")
    p.add_argument("--uncalibrated",action="store_true")
    a=p.parse_args();a.root=a.root.resolve();a.root.mkdir(parents=True,exist_ok=True)
    if a.stage=="prepare":prepare(a);return
    if a.stage=="calibrate":
        if not a.analysis_python:p.error("Calibration requires an existing analysis Python")
        calibrate(a);return
    if a.stage=="case" and a.pt is None:p.error("Performance case requires fixed pT")
    a.events=a.events or (50000 if a.stage=="train" else 20000)
    a.output=(a.output or a.root/("training-current" if a.stage=="train" else f"performance/{a.baseline}-pt{a.pt:g}")).resolve()
    if a.events<=0:p.error("Positive event count required")
    run_job(a)


if __name__=="__main__":main()
