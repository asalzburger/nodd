#!/usr/bin/env python3
"""Native ACTS truth-associated Kalman baseline for the PR100 Gen3 nODD tracker."""
import argparse
import importlib
import json
from pathlib import Path
import sys
import time
import subprocess

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "software/analysis/gen3_material_mapping"))
sys.path.insert(0, str(ROOT_DIR / "software/analysis/truth_tracking"))
from material_runtime import common_arguments, load_manifest, native_imports, prepare_geometry, provenance, sha256, write_report
from runtime import load_campaign, material_map, root_inventory
from digitization import build_config, apply_variance_table


def run(args, config, ROOT, acts, detector, geometry, observer):
    from acts.examples.simulation import (addParticleGun, MomentumConfig, EtaConfig,
        PhiConfig, ParticleConfig, addGeant4, addFatras,
        addDigiParticleSelection, ParticleSelectorConfig)
    from acts.examples.reconstruction import (addSeeding, SeedingAlgorithm,
        TrackSmearingSigmas, addKalmanTracks)
    from acts.examples.root import (RootParticleWriter, RootTrackStatesWriter,
        RootTrackSummaryWriter, RootTrackParameterPerformanceWriter, RootMeasurementWriter, RootSimHitWriter)
    u, level = acts.UnitConstants, acts.logging.WARNING
    field = acts.ConstantBField(acts.Vector3(0.,0.,config["field_Bz_T"]*u.T))
    training=config.get("error_training",{}) if args.training else {}
    rnd = acts.examples.RandomNumbers(seed=training.get("seed",config["seed"]))
    momentum=(MomentumConfig(*[x*u.GeV for x in training["pt_range_GeV"]],transverse=True,logUniform=True)
              if args.training else MomentumConfig(args.pt*u.GeV,args.pt*u.GeV,transverse=True))
    s = acts.examples.Sequencer(events=args.events, numThreads=args.threads,
        outputDir=str(args.output), logLevel=level)
    for decorator in detector.contextDecorators():
        s.addContextDecorator(decorator)
    addParticleGun(s, ParticleConfig(num=1,pdg=acts.PdgParticle.eMuon,randomizeCharge=True),
        momentum,
        EtaConfig(*config["eta_range"],uniform=True),PhiConfig(*config["phi_range_rad"]),
        vtxGen=acts.examples.GaussianVertexGenerator(mean=acts.Vector4(0.,0.,0.,0.),
            stddev=acts.Vector4(0.,0.,0.,0.)),multiplicity=1,rnd=rnd,logLevel=level)
    s.addWriter(RootParticleWriter(level=level,inputParticles="particles_generated",
        filePath=str(args.output/"particles.root")))
    persistent_handle=None
    if args.simulation == "geant4":
        if args.geant4_run_mode == "persistent":
            import acts.examples.geant4
            import acts.examples.simulation as simulation
            persistent_handle=observer.persistent_handle(args.events)
            # The pinned helper explicitly supports reusing this native handle.
            simulation.__geant4Handle=persistent_handle
        addGeant4(s,detector,geometry,field,rnd=rnd,inputParticles="particles_generated",
            killVolume=geometry.highestTrackingVolume,killAfterTime=25*u.ns,
            keepParticlesWithoutHits=True,recordHitsOfSecondaries=True,
            materialMappings=["Silicon","pixel_Silicon"],
            killSecondaries=False,physicsList="FTFP_BERT",logLevel=level)
    else:
        addFatras(s,geometry,field,rnd=rnd,inputParticles="particles_generated",
            enableInteractions=True,logLevel=level)
    if args.write_simhits:
        s.addWriter(RootSimHitWriter(level=level,inputSimHits="simhits",
            filePath=str(args.output/"hits.root")))
    # Native addDigitization-equivalent with explicit raw keys for the local
    # uniqueness/covariance adapters. Full measurement-simhit contributions remain.
    from acts.examples import json as acts_json
    s.addAlgorithm(acts.examples.DigitizationAlgorithm(
        acts.examples.DigitizationAlgorithm.Config(
            digitizationConfigs=acts_json.readDigiConfigFromJson(str(args.output/"digitization.json")),
            surfaceByIdentifier=geometry.geoIdSurfaceMap(),randomNumbers=rnd,
            inputSimHits="simhits",outputMeasurements="measurements_raw" if args.error_table else "measurements",
            outputMeasurementParticlesMap="measurement_particles_map_raw",
            outputMeasurementSimHitsMap="measurement_simhits_map",
            outputParticleMeasurementsMap="particle_measurements_map_raw",
            outputSimHitMeasurementsMap="simhit_measurements_map",
            doMerge=True,mergeCommonCorner=True,minEnergyDeposit=0.),level))
    s.addAlgorithm(observer.UniqueAssociations())
    if args.error_table is not None:
        s.addAlgorithm(observer.ClusterErrors(json.loads(args.error_table.read_text())["entries"]))
        s.addWhiteboardAlias("measurements","measurements_calibrated")
    s.addWriter(RootMeasurementWriter(level=level,inputMeasurements="measurements",
        inputClusters="clusters",inputSimHits="simhits",
        inputMeasurementSimHitsMap="measurement_simhits_map",
        surfaceByIdentifier=geometry.geoIdSurfaceMap(),
        filePath=str(args.output/"measurements.root")))
    addDigiParticleSelection(s,ParticleSelectorConfig(
        measurements=(config["truth_tracking"]["minimum_measurements"],None),
        removeNeutral=True,removeSecondaries=True),logLevel=level)
    s.addWriter(RootParticleWriter(level=level,inputParticles="particles_digitized_selected",
        filePath=str(args.output/"particles_selected.root")))
    truth=config["truth_tracking"]
    addSeeding(s,geometry,field,rnd=rnd,seedingAlgorithm=SeedingAlgorithm.TruthSmeared,
        trackSmearingSigmas=TrackSmearingSigmas(loc0=0.,loc0PtA=0.,loc0PtB=0.,
            loc1=0.,loc1PtA=0.,loc1PtB=0.,time=0.,phi=0.,theta=0.,ptRel=0.),
        particleHypothesis=acts.ParticleHypothesis.muon,
        initialSigmas=[*[x*u.mm for x in truth["initial_sigma_loc_mm"]],
            *[x*u.degree for x in truth["initial_sigma_angle_degree"]],0./u.GeV,1.*u.ns],
        initialSigmaQoverPt=truth["initial_sigma_qoverpt_e_per_GeV"]/u.GeV,
        initialSigmaPtRel=truth["initial_sigma_pt_relative"],
        initialVarInflation=truth["initial_variance_inflation"],logLevel=level)
    s.addAlgorithm(observer.CorrectTruthProtoTracks())
    addKalmanTracks(s,geometry,field,inputProtoTracks="truth_particle_tracks_corrected",logLevel=level)
    s.addAlgorithm(observer.Audit(str(args.output/"audit.root")))
    common=dict(level=level,inputTracks="kf_tracks",inputParticles="particles_generated",
                inputTrackParticleMatching="kf_track_particle_matching")
    s.addWriter(RootTrackSummaryWriter(**common,writeCovMat=True,
        filePath=str(args.output/"tracksummary_kf.root")))
    s.addWriter(RootTrackStatesWriter(**common,inputSimHits="simhits",
        inputMeasurementSimHitsMap="measurement_simhits_map",
        filePath=str(args.output/"trackstates_kf.root")))
    s.addWriter(RootTrackParameterPerformanceWriter(**common,
        filePath=str(args.output/"performance_kf.root")))
    try:
        s.run()
    finally:
        if persistent_handle is not None:
            observer.finish_persistent(persistent_handle)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    common_arguments(parser)
    parser.add_argument("--campaign",type=Path,default=ROOT_DIR/"software/analysis/truth_tracking/campaign.json")
    parser.add_argument("--simulation",choices=("geant4","fatras"),required=True)
    parser.add_argument("--pt",type=float)
    parser.add_argument("--training",action="store_true",help="Independent Fatras loguniform-pT error-training sample")
    parser.add_argument("--error-table",type=Path,help="Native ACTS hit-error-parametrisation RMS table")
    parser.add_argument("--threads",type=int,default=1)
    parser.add_argument("--geant4-run-mode",choices=("standard","persistent"),default="persistent")
    parser.add_argument("--write-simhits",action="store_true",help="Retain native simhits for lifecycle controls")
    parser.add_argument("--observer-module-dir",type=Path,default=ROOT_DIR/"build/truth-tracking-baseline/native")
    args=parser.parse_args()
    config=load_campaign(args.campaign)
    if args.training and (args.simulation != "fatras" or args.pt is not None or args.error_table is not None or "error_training" not in config):
        parser.error("Training requires Fatras, configured training inputs, no fixed pT and no fitted error table")
    if (not args.training and args.pt not in config["pt_GeV"]) or args.events <= 0 or args.threads <= 0:
        parser.error("Expected configured momentum and positive events/threads")
    if args.simulation=="geant4" and args.threads != 1:
        parser.error("Native Geant4 requires one thread")
    args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=True)
    # Reject accidental replacement of a completed result.
    if (args.output/"run-report.json").exists():
        parser.error("Output already has a report; select a fresh output directory")
    manifest=load_manifest(args.manifest)
    ROOT,acts,sidecar=native_imports(args.native_module_dir)
    sys.path.insert(0,str(args.observer_module_dir.resolve()))
    observer=importlib.import_module("nodd_truth_tracking")
    launch_revision=subprocess.check_output(["git","-C",str(ROOT_DIR),"rev-parse","HEAD"],text=True).strip()
    source_files=[Path(__file__).resolve(), ROOT_DIR/"software/analysis/truth_tracking/digitization.py",
                  ROOT_DIR/"software/analysis/truth_tracking/runtime.py",
                  ROOT_DIR/"software/source/ActsExamples/TruthTracking/TruthTracking.cpp",
                  ROOT_DIR/"software/source/ActsExamples/TruthTracking/CMakeLists.txt",
                  Path(observer.__file__).resolve()]
    executed_source_hashes={str(p.relative_to(ROOT_DIR)):sha256(p) for p in source_files}
    source_map=ROOT_DIR/config["material_map"]
    expanded=args.observer_module_dir.resolve()/"material_map.json"
    material_map(source_map,expanded)
    start=time.monotonic()
    report={"schema_version":1,"status":"PROTOTYPE","outcome":"started",
        "simulation":args.simulation,"pt_GeV":args.pt,"events":args.events,
        "threads":args.threads,"campaign":config,"command":sys.argv,
        "scientific_input_revision":launch_revision,
        "original_handoff_revision":"675612ef5a2c5b23b7c1bcf7456f278a4447b819",
        "human_amended_design_revision":"eb86998ad5d42c37bf7d244063c575f93b0c42a3",
        "executed_source_sha256":executed_source_hashes}
    try:
        detector,geometry,context,surfaces,decoration=prepare_geometry(args,manifest,acts,sidecar,expanded)
        sensors=json.loads(detector.geometryReport())["sensors"]
        digi,counts=build_config(sensors,config["digitization"])
        if args.error_table is not None:
            apply_variance_table(digi,json.loads(args.error_table.read_text()))
        report["error_table"]={"path":str(args.error_table.resolve()),"sha256":sha256(args.error_table)} if args.error_table else None
        report["training"]=args.training
        write_report(args.output/"digitization.json",digi)
        report.update(native_decoration=decoration,digitization_sensors_by_system=counts,
            digitization_native_defaults={"componentDigital":True,"doMerge":True,
                "mergeCommonCorner":True,"minEnergyDeposit":0.,"charge":"Exact(0) path length",
                "drift":"native unimplemented: zero","diffusion":"none",
                "variance":"native GeometricConfig::variances; pitch squared /12 without table"})
        run(args,config,ROOT,acts,detector,geometry,observer)
        report["outcome"]="completed"
        names=("particles.root","particles_selected.root","audit.root","tracksummary_kf.root",
               "trackstates_kf.root","performance_kf.root","measurements.root")
        if args.write_simhits:names+=("hits.root",)
        report["geant4_run_mode"]=args.geant4_run_mode if args.simulation=="geant4" else None
        report["root_inventory"]={name:root_inventory(ROOT,args.output/name) for name in names}
        audit=ROOT.RDataFrame("audit",str(args.output/"audit.root"))
        report["counts"]={name:int(audit.Sum["ULong64_t"](name).GetValue()) for name in
            ("generated","simhits","measurements","selected","fit_attempts","fit_tracks","invalid_covariance","primary_measurements","original_proto_measurements","corrected_proto_measurements","primary_measurement_associations_raw")}
        report["counts"]["events"]=int(audit.Count().GetValue())
        if report["counts"]["events"] != args.events or report["counts"]["generated"] != args.events:
            raise RuntimeError("Native output does not preserve all requested one-muon events")
        sensor_system={sensor["geometry_id"]:sensor["ids"]["system"] for sensor in sensors}
        source=ROOT.TFile.Open(str(args.output/"audit.root"))
        systems={str(i):0 for i in range(1,8)}
        dimensions={"1":0,"2":0}
        for event in source.Get("audit"):
            for identity,dimension in zip(event.measurement_geometry_id,event.measurement_dimension):
                system=sensor_system[int(identity)]
                if int(dimension) != (1 if system>=6 else 2):
                    raise RuntimeError("Native measurement dimension differs from the sensor contract")
                systems[str(system)]+=1; dimensions[str(dimension)]+=1
        source.Close()
        report["measurement_counts_by_system"]=systems
        report["measurement_counts_by_dimension"]=dimensions
        if args.events >= 100 and any(value == 0 for value in systems.values()):
            raise RuntimeError("Native sample lacks measurements in one or more tracker systems")
        report["provenance"]=provenance(args,sidecar,[("campaign",args.campaign.resolve()),
            ("saved_material_map",source_map),("digitization",args.output/"digitization.json"),
            ("observer",Path(observer.__file__)),
            ("observer_source",ROOT_DIR/"software/source/ActsExamples/TruthTracking/TruthTracking.cpp"),
            ("digitizer_source",ROOT_DIR/"software/analysis/truth_tracking/digitization.py"),
            *[("native_output",args.output/name) for name in names]])
        if args.error_table is not None:
            report["provenance"]["files"].append({"role":"error_table","name":args.error_table.name,
                "path":str(args.error_table.resolve()),"sha256":sha256(args.error_table)})
        report["provenance"]["analysis_source_revision_at_launch"]=launch_revision
        report["provenance"]["revision_note"]="Executed source identity is pinned at launch with content hashes; the helper git inventory is read after the run."
        report["ROOT"]=ROOT.gROOT.GetVersion()
        extra_modules=("acts.examples.ActsExamplesPythonBindings", "acts.examples.ActsExamplesPythonBindingsGeant4")
        extra=[]
        for module_name in extra_modules:
            module=importlib.import_module(module_name)
            extra.append(("runtime_binding",Path(module.__file__)))
        runtime_build=Path(importlib.import_module("acts.ActsPythonBindings").__file__).parents[2]
        for library in ("ActsExamplesFatras", "ActsExamplesGeant4", "ActsExamplesDigitization",
                        "ActsExamplesTrackFitting", "ActsExamplesTruthTracking", "ActsExamplesIoRoot"):
            path=runtime_build/"lib"/f"lib{library}.dylib"
            if path.is_file():extra.append(("runtime_library",path))
        report["provenance"]["files"].extend({"role":role,"name":path.name,"path":str(path),"sha256":sha256(path)} for role,path in extra)
        report["geant4_sensitive_materials"]=["Silicon","pixel_Silicon"]
    except Exception as error:
        report["outcome"]="failed";report["error"]=f"{type(error).__name__}: {error}"
        raise
    finally:
        report["wall_seconds"]=time.monotonic()-start
        write_report(args.output/"run-report.json",report)
    print(json.dumps({"outcome":report["outcome"],"counts":report.get("counts"),"wall_seconds":report["wall_seconds"]}))

if __name__=="__main__":
    main()
