#!/usr/bin/env python3
"""DES041 isolated full Fatras → smearing → GBTS → CKF tracker prototype."""
import argparse
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import copy
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "software/analysis/tracker_reconstruction"))
from prepare import prepare
import gbts
import species
import transport
from material_runtime import sha256, write_report
import smearing


def run(args, config, acts, detector, geometry, observer):
    from acts.examples.simulation import (addParticleGun, MomentumConfig, EtaConfig,
        PhiConfig, ParticleConfig)
    from acts.examples.reconstruction import addSpacePointsMaking
    from acts.examples.root import RootTrackSummaryWriter, RootMeasurementWriter
    sys.path.insert(0, str(ROOT / "build/tracker-reconstruction/native-audit"))
    audit = importlib.import_module("nodd_reconstruction")
    u, level = acts.UnitConstants, acts.logging.WARNING
    gun_pdg, hypothesis, particle_configuration = species.configure(acts, config["particle"])
    field = acts.ConstantBField(acts.Vector3(0., 0., config["field_Bz_T"] * u.T))
    rnd = acts.examples.RandomNumbers(seed=args.seed)
    seq = acts.examples.Sequencer(events=args.events, numThreads=args.threads,
        outputDir=str(args.output), logLevel=level)
    for decorator in detector.contextDecorators(): seq.addContextDecorator(decorator)
    addParticleGun(seq, ParticleConfig(num=1, pdg=gun_pdg, randomizeCharge=True),
        MomentumConfig(args.pt*u.GeV, args.pt*u.GeV, transverse=True),
        EtaConfig(*config["eta_range"], uniform=True), PhiConfig(*config["phi_range_rad"]),
        vtxGen=acts.examples.GaussianVertexGenerator(mean=acts.Vector4(0.,0.,0.,0.),
            stddev=acts.Vector4(0.,0.,0.,0.)), multiplicity=1, rnd=rnd, logLevel=level)
    simulation_detector=audit.SensitiveDetector(detector) if config["simulation"]=="geant4" else detector
    transport_configuration, cleanup = transport.schedule(seq,acts,simulation_detector,geometry,field,rnd,observer,config,args.events,level)
    try:
        mapping_summary = None
        if config["simulation"] == "geant4":
            mapping = json.loads(audit.geant4_mapping_json(geometry))
            native = json.loads((args.output/"native-report.json").read_text())
            expected = {s["geometry_id"] for s in native["sensors"]}
            mapped = set(mapping["mapped_geometry_ids"])
            if (not mapping["all_sensitive_surfaces_mapped"] or mapped != expected or
                set(mapping["expected_geometry_ids"]) != expected or mapping["duplicate_geometry_ids"]):
                write_report(args.output/"geant4-mapping.json",mapping)
                raise RuntimeError("Geant4 active-surface mapping incomplete or duplicated")
            from collections import Counter
            mapping["mapped_by_system"] = dict(Counter(str(s["ids"]["system"]) for s in native["sensors"] if s["geometry_id"] in mapped))
            write_report(args.output/"geant4-mapping.json",mapping)
            mapping_summary = {k:mapping[k] for k in ("all_sensitive_surfaces_mapped","mapped_by_system","duplicate_geometry_ids")}
            mapping_summary["expected"] = len(expected)
            mapping_summary["mapped"] = len(mapped)
            mapping_summary["unmatched_g4_volumes"] = len(mapping["unmatched_g4_volumes"])
        smearing.schedule_digitization(seq, acts, geometry, rnd, args.output/"digitization.json", observer, level)
        # Digitization publishes a native MeasurementSubset containing ALL indices.
        # No truth/particle selection filters it. Only pixel volumes form space points.
        addSpacePointsMaking(seq, geometry, args.output/"pixel-selection.json", None, logLevel=level)
        seeder = gbts.schedule(seq, acts, geometry, args.output/"gbts", config["profiles"][args.profile], level)
        p = config["parameter_estimation"]
        seq.addAlgorithm(acts.examples.TrackParamsEstimationAlgorithm(level=level,
            inputSeeds="seeds", outputTrackParameters="estimatedparameters", outputSeeds="estimatedseeds",
            trackingGeometry=geometry, magneticField=field, particleHypothesis=hypothesis,
            spacePointSelection=getattr(acts.examples.SeedSpacePointSelection,p["spacepoint_selection"]),
            initialSigmas=[p["sigma_loc0_mm"]*u.mm,p["sigma_loc1_mm"]*u.mm,
                p["sigma_phi_deg"]*u.degree,p["sigma_theta_deg"]*u.degree,0.,p["sigma_time_ns"]*u.ns],
            initialSigmaQoverPt=p["sigma_qoverpt_GeV_inv"]/u.GeV,
            initialSigmaPtRel=p["sigma_pt_relative"]))
        c, q = config["ckf"], config["quality"]
        finder = acts.examples.TrackFindingAlgorithm(level=level,
            inputMeasurements="measurement_subset", inputInitialTrackParameters="estimatedparameters",
            inputSeeds="estimatedseeds", outputTracks="ckf_tracks", trackingGeometry=geometry, magneticField=field,
            findTracks=acts.examples.TrackFindingAlgorithm.makeTrackFinderFunction(geometry,field,level),
            findTracksBrem=acts.examples.TrackFindingAlgorithm.makeBremTrackFinderFunction(geometry,field,level),
            measurementSelectorCfg=acts.MeasurementSelector.Config([(acts.GeometryIdentifier(),
                ([],[c["measurement_chi2"]],[c["outlier_chi2"]],[c["max_measurements_per_surface"]]))]),
            maxSteps=c["max_steps"], twoWay=(c["two_way"] if config["particle"]!="electron" else config.get("species_extension",{}).get("electron_two_way",False)), reverseSearch=False,
            seedDeduplication=c["seed_deduplication"], stayOnSeed=c["stay_on_seed"],
            trimTracks=True, recordMaterialStates=False, useJosephFormulation=True)
        seq.addAlgorithm(finder)
        a = config["ambiguity"]
        seq.addAlgorithm(acts.examples.GreedyAmbiguityResolutionAlgorithm(level=level,
            inputTracks="ckf_tracks", outputTracks="ambi_tracks", maximumSharedHits=a["maximum_shared_hits"],
            nMeasurementsMin=q["minimum_measurements"], maximumIterations=a["maximum_iterations"]))
        # Explicit, identical generated-primary truth input for both stage writers.
        # Independent audit below also classifies every candidate, including entries
        # which the native matcher skips and real simulated-secondary matches.
        for stage in ("ckf", "ambi"):
            seq.addAlgorithm(acts.examples.TrackTruthMatcher(level=level,inputTracks=stage+"_tracks",
                inputParticles="particles_generated", inputMeasurementParticlesMap="measurement_particles_map",
                outputTrackParticleMatching=stage+"_primary_matching", outputParticleTrackMatching=stage+"_primary_tracks",
                matchingRatio=config["matching"]["purity"], doubleMatching=True))
            if args.write_root:
                common=dict(level=level,inputTracks=stage+"_tracks", inputParticles="particles_generated",
                    inputTrackParticleMatching=stage+"_primary_matching")
                seq.addWriter(RootTrackSummaryWriter(**common, writeCovMat=True,
                    filePath=str(args.output/("tracksummary_"+stage+".root"))))
        if args.write_root:
            seq.addWriter(RootMeasurementWriter(level=level,inputMeasurements="measurements",inputClusters="",
                inputSimHits="simhits",inputMeasurementSimHitsMap="measurement_simhits_map",
                surfaceByIdentifier=geometry.geoIdSurfaceMap(),filePath=str(args.output/"measurements.root")))
        seq.addAlgorithm(audit.ReconstructionAudit(str(args.output/"events.jsonl")))
        sequencer_start=time.monotonic()
        try:
            seq.run()
        except RuntimeError:
            write_report(args.output/"native-fpe-diagnostic.json",{"native_fpe_result":str(seq.fpeResult)})
            raise
        if config["simulation"]=="geant4":
            transport_configuration.update(json.loads(audit.geant4_runtime_json()))
            transport_configuration["native_geant4_events"]=audit.geant4_event_count()
            transport_configuration["fpe_scope"]="Reconstruction sequencer monitors retained; upstream Geant4 BeamOn disables FPE monitoring internally"
            if transport_configuration["native_geant4_events"]!=args.events:raise RuntimeError("Geant4/ACTS event-count mismatch")
        return {**seeder.statistics(), "particle_configuration": particle_configuration,
            "transport_configuration": transport_configuration, "geant4_mapping_audit": mapping_summary,
                "effective_two_way": (c["two_way"] if config["particle"]!="electron" else config.get("species_extension",{}).get("electron_two_way",False)),
                "effective_configuration": json.loads(seeder.effective_configuration_json()),
                "sequencer_seconds":time.monotonic()-sequencer_start}

    finally:
        cleanup()


def fingerprints():
    files = [Path(__file__), ROOT/"software/env/truth_tracking.sh", ROOT/"software/analysis/tracker_reconstruction/prepare.py", ROOT/"software/analysis/tracker_reconstruction/gbts.py", ROOT/"software/analysis/tracker_reconstruction/species.py", ROOT/"software/analysis/tracker_reconstruction/transport.py"]
    for directory in ("software/source/ActsExamples/TrackerGbts",
        "software/source/ActsExamples/TrackerReconstruction", "software/analysis/gen3_material_mapping",
        "software/analysis/truth_tracking", "software/analysis/tracker_optimization"):
        files.extend(p for p in (ROOT/directory).rglob("*") if p.is_file() and p.suffix in (".py", ".cpp", ".hpp") and not p.name.startswith("test"))
    for directory in ("build/tracker-reconstruction/native-audit", "build/tracker-reconstruction/native-gbts"):
        files.extend((ROOT/directory).glob("*.so"))
    for directory in ("TrackerGbts","TrackerReconstruction"):
        files.append(ROOT/"software/source/ActsExamples"/directory/"CMakeLists.txt")
    return {str(p.resolve()): sha256(p) for p in sorted(set(files))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign",type=Path,default=ROOT/"software/analysis/tracker_reconstruction/campaign.json")
    parser.add_argument("--pt",type=float,required=True)
    parser.add_argument("--simulation", choices=("fatras","geant4"), help="Override the campaign transport")
    parser.add_argument("--particle", choices=tuple(species.SPECIES), help="Override the campaign species; default is its particle field")
    parser.add_argument("--events",type=int,default=100)
    parser.add_argument("--profile",default="control")
    parser.add_argument("--phase",choices=("smoke","tuning","validation"),default="smoke")
    parser.add_argument("--seed",type=int)
    parser.add_argument("--threads",type=int,default=1)
    parser.add_argument("--write-root",action="store_true")
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    config=json.loads(args.campaign.read_text())
    if args.particle is not None: config["particle"]=args.particle
    if args.simulation is not None: config["simulation"]=args.simulation
    if config["simulation"]=="geant4" and (args.threads!=1 or args.profile=="all"): parser.error("Geant4 requires one thread and one profile per fresh process")
    if config.get("particle") not in species.SPECIES: parser.error("Unsupported campaign particle")
    if (args.phase=="validation" and config.get("species_extension") and
        args.profile!=config["species_extension"]["selected_profile"]):
        parser.error("Species validation requires its frozen selected GBTS profile")
    if args.pt not in config["pt_GeV"] or args.events<=0 or args.threads<=0 or args.profile not in {*config["profiles"],"all"}:
        parser.error("Require configured pT/profile and positive events/threads")
    args.seed = args.seed if args.seed is not None else config["sample_seeds"]["tuning" if args.phase=="smoke" else args.phase]
    args.output=args.output.resolve()
    if args.output.exists() and any(args.output.iterdir()): parser.error("Choose a fresh output directory")
    args.output.mkdir(parents=True,exist_ok=True)
    if args.profile=="all":
        prepared=None;parent=args.output
        for profile in config["profiles"]:
            case=copy.copy(args);case.profile=profile;case.output=parent/profile
            case.output.mkdir()
            prepared=execute_case(case,config,prepared)
    else: execute_case(args,config)


def execute_case(args,config,prepared=None):
    startup = fingerprints()
    report = {"schema_version":1,"status":"PROTOTYPE","outcome":"started", "command":sys.argv,
        "source_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "pt_GeV":args.pt,"events":args.events,"seed":args.seed,"phase":args.phase,"profile":args.profile,
        "campaign":config,"campaign_sha256":sha256(args.campaign),"source_sha256":startup}
    start=time.monotonic()
    write_report(args.output/"run-report.json",report)
    try:
        if prepared is None:
            prepared=(*prepare(args),args.output)
        else:
            for name in ("selection.json","material-map.json","error-table.json","digitization.json","native-report.json","pixel-selection.json"):
                shutil.copyfile(prepared[-1]/name,args.output/name)
        ROOTmod,acts,observer,detector,geometry,native,info=prepared[:-1]
        report["preparation"]=info
        report["gbts_preparation"]=gbts.prepare(native,args.output/"gbts",config["profiles"][args.profile])
        # Fingerprint the actual executing native runtime rather than a newer
        # development checkout whose HEAD is unrelated to these bindings.
        binding=Path(importlib.import_module("acts.examples.ActsExamplesPythonBindings").__file__).resolve()
        build=binding.parents[3]
        runtime=[binding,*sorted((build/"lib").glob("libActs*.dylib"))]
        runtime.extend(sorted((build/"Examples/Detectors/DD4hepDetector").glob("*.dylib")))
        runtime.extend(sorted((ROOT/"build/balanced-baseline/dd4hep/detector").glob("*.dylib")))
        if config["simulation"]=="geant4":
            program=shutil.which("geant4-config")
            if program is None:raise RuntimeError("Geant4 runtime CLI identity unavailable")
            runtime.extend(sorted((Path(program).resolve().parents[1]/"lib").glob("libG4*.dylib")))
        report["runtime_sha256"]={str(p):sha256(p) for p in runtime}
        write_report(args.output/"campaign.json",config)
        write_report(args.output/"run-report.json",report)
        report["prepared_input_sha256"]={str(p.relative_to(args.output)):sha256(p) for p in args.output.rglob("*") if p.is_file() and p.name!="run-report.json"}
        write_report(args.output/"run-report.json",report)
        report["gbts_statistics"]=run(args,config,acts,detector,geometry,observer)
        if any(sha256(args.output/name)!=digest for name,digest in report["prepared_input_sha256"].items()):
            raise RuntimeError("Prepared scientific input changed during execution")
        if fingerprints()!=startup: raise RuntimeError("Reconstruction code changed during native execution")
        if any(sha256(path)!=digest for path,digest in report["runtime_sha256"].items()):
            raise RuntimeError("Executing native runtime/factory changed during execution")
        with (args.output/"events.jsonl").open("rb") as source, gzip.open(args.output/"events.jsonl.gz","wb") as target:
            for line in source: target.write(line)
        (args.output/"events.jsonl").unlink()
        report["output_sha256"]={p.name:sha256(p) for p in args.output.iterdir() if p.is_file() and p.name!="run-report.json"}
        report["outcome"]="completed"
    except Exception as error:
        report["outcome"]="failed";report["error"]=f"{type(error).__name__}: {error}"
        raise
    finally:
        report["wall_seconds"]=time.monotonic()-start
        write_report(args.output/"run-report.json",report)
    print(json.dumps({"outcome":report["outcome"],"profile":args.profile,"wall_seconds":report["wall_seconds"],"gbts":report.get("gbts_statistics")}),flush=True)
    return prepared


if __name__=="__main__": main()
