#!/usr/bin/env python3
"""Isolated native Fatras Gaussian-smearing truth-tracking cross-check (PROTOTYPE)."""
import argparse
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "software/analysis/gen3_material_mapping"))
sys.path.insert(0, str(ROOT_DIR / "software/analysis/truth_tracking"))
from material_runtime import common_arguments, load_manifest, native_imports, prepare_geometry, provenance, sha256, write_report
from runtime import material_map, root_inventory, schedule_native_truth_seed
from smearing import load_campaign, build_config, schedule_digitization, audit_measurements


def run(args, config, acts, detector, geometry, observer):
    from acts.examples.simulation import (addParticleGun, MomentumConfig, EtaConfig,
        PhiConfig, ParticleConfig, addFatras, addDigiParticleSelection, ParticleSelectorConfig)
    from acts.examples.reconstruction import addKalmanTracks
    from acts.examples.root import (RootParticleWriter, RootTrackStatesWriter,
        RootTrackSummaryWriter, RootTrackParameterPerformanceWriter, RootMeasurementWriter)
    u, level = acts.UnitConstants, acts.logging.WARNING
    field = acts.ConstantBField(acts.Vector3(0., 0., config["field_Bz_T"] * u.T))
    rnd = acts.examples.RandomNumbers(seed=config["seed"])
    sequencer = acts.examples.Sequencer(events=args.events, numThreads=args.threads,
        outputDir=str(args.output), logLevel=level)
    for decorator in detector.contextDecorators():
        sequencer.addContextDecorator(decorator)
    addParticleGun(sequencer, ParticleConfig(num=1, pdg=acts.PdgParticle.eMuon, randomizeCharge=True),
        MomentumConfig(args.pt*u.GeV, args.pt*u.GeV, transverse=True),
        EtaConfig(*config["eta_range"], uniform=True), PhiConfig(*config["phi_range_rad"]),
        vtxGen=acts.examples.GaussianVertexGenerator(mean=acts.Vector4(0., 0., 0., 0.),
            stddev=acts.Vector4(0., 0., 0., 0.)), multiplicity=1, rnd=rnd, logLevel=level)
    sequencer.addWriter(RootParticleWriter(level=level, inputParticles="particles_generated",
        filePath=str(args.output/"particles.root")))
    addFatras(sequencer, geometry, field, rnd=rnd, inputParticles="particles_generated",
        enableInteractions=True, logLevel=level)
    schedule_digitization(sequencer, acts, geometry, rnd, args.output/"digitization.json", observer, level)
    # Smearing has no channelized clusters. Empty inputClusters is explicitly
    # supported by the native writer; local truth and covariance are still filled.
    sequencer.addWriter(RootMeasurementWriter(level=level, inputMeasurements="measurements",
        inputClusters="", inputSimHits="simhits", inputMeasurementSimHitsMap="measurement_simhits_map",
        surfaceByIdentifier=geometry.geoIdSurfaceMap(), filePath=str(args.output/"measurements.root")))
    addDigiParticleSelection(sequencer, ParticleSelectorConfig(
        measurements=(config["truth_tracking"]["minimum_measurements"], None),
        removeNeutral=True, removeSecondaries=True), logLevel=level)
    sequencer.addWriter(RootParticleWriter(level=level, inputParticles="particles_digitized_selected",
        filePath=str(args.output/"particles_selected.root")))
    schedule_native_truth_seed(sequencer, acts, rnd, config["truth_tracking"], level)
    sequencer.addAlgorithm(observer.CorrectTruthProtoTracks())
    addKalmanTracks(sequencer, geometry, field, inputProtoTracks="truth_particle_tracks_corrected", logLevel=level)
    sequencer.addAlgorithm(observer.Audit(str(args.output/"audit.root")))
    common = dict(level=level, inputTracks="kf_tracks", inputParticles="particles_generated",
                  inputTrackParticleMatching="kf_track_particle_matching")
    sequencer.addWriter(RootTrackSummaryWriter(**common, writeCovMat=True,
        filePath=str(args.output/"tracksummary_kf.root")))
    sequencer.addWriter(RootTrackStatesWriter(**common, inputSimHits="simhits",
        inputMeasurementSimHitsMap="measurement_simhits_map", filePath=str(args.output/"trackstates_kf.root")))
    sequencer.addWriter(RootTrackParameterPerformanceWriter(**common,
        filePath=str(args.output/"performance_kf.root")))
    sequencer.run()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    common_arguments(parser)
    parser.add_argument("--campaign", type=Path, default=ROOT_DIR/"software/analysis/truth_tracking/smearing_campaign.json")
    parser.add_argument("--simulation", choices=("fatras",), default="fatras")
    parser.add_argument("--pt", type=float, required=True)
    parser.add_argument("--width-table", type=Path)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--observer-module-dir", type=Path, default=ROOT_DIR/"build/truth-tracking-baseline/native")
    args = parser.parse_args()
    config = load_campaign(args.campaign)
    if args.pt not in config["pt_GeV"] or args.events <= 0 or args.threads <= 0:
        parser.error("Require a configured momentum and positive events/threads")
    args.width_table = (args.width_table or ROOT_DIR/config["digitization"]["width_table"]).resolve()
    table = json.loads(args.width_table.read_text())
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.glob("*.root")) or (args.output/"run-report.json").exists():
        parser.error("Output contains native results; select a fresh output directory")
    manifest = load_manifest(args.manifest)
    ROOT, acts, sidecar = native_imports(args.native_module_dir)
    sys.path.insert(0, str(args.observer_module_dir.resolve()))
    observer = importlib.import_module("nodd_truth_tracking")
    launch_revision = subprocess.check_output(["git", "-C", str(ROOT_DIR), "rev-parse", "HEAD"], text=True).strip()
    source_paths = [Path(__file__).resolve(), ROOT_DIR/"software/analysis/truth_tracking/smearing.py",
        ROOT_DIR/"software/analysis/truth_tracking/runtime.py", ROOT_DIR/"software/analysis/truth_tracking/digitization.py",
        ROOT_DIR/"software/env/truth_tracking.sh", ROOT_DIR/"software/analysis/gen3_material_mapping/material_runtime.py",
        ROOT_DIR/"software/source/ActsExamples/TruthTracking/TruthTracking.cpp",
        ROOT_DIR/"software/source/ActsExamples/TruthTracking/CMakeLists.txt", Path(observer.__file__).resolve()]
    source_hashes = {str(path.relative_to(ROOT_DIR)): sha256(path) for path in source_paths}
    source_map = ROOT_DIR/config["material_map"]
    expanded = args.observer_module_dir.resolve()/"material_map.json"
    if not expanded.is_file():
        raise RuntimeError("Expected the existing immutable expanded PR100 map cache")
    material_map(source_map, expanded)  # Byte-identity check only; existing cache is not modified.
    runtime_files = []
    for name in ("acts.examples.ActsExamplesPythonBindings",):
        runtime_files.append(("runtime_binding", Path(importlib.import_module(name).__file__)))
    runtime_build = Path(importlib.import_module("acts.ActsPythonBindings").__file__).parents[2]
    for library in ("ActsExamplesFatras", "ActsExamplesDigitization", "ActsExamplesTrackFitting",
                    "ActsExamplesTruthTracking", "ActsExamplesIoRoot"):
        path = runtime_build/"lib"/f"lib{library}.dylib"
        if not path.is_file():
            raise RuntimeError(f"Required runtime library absent: {library}")
        runtime_files.append(("runtime_library", path))
    # All code, input and executed runtime bytes are fingerprinted before run().
    startup_provenance = provenance(args, sidecar, [
        ("campaign", args.campaign.resolve()), ("saved_material_map", source_map),
        ("pooled_width_table", args.width_table), ("observer", Path(observer.__file__)),
        *[("executed_source", path) for path in source_paths], *runtime_files])
    start = time.monotonic()
    report = {"schema_version": 1, "status": "PROTOTYPE", "outcome": "started",
        "simulation": "fatras", "pt_GeV": args.pt, "events": args.events, "threads": args.threads,
        "campaign": config, "command": sys.argv, "scientific_input_revision": launch_revision,
        "assignment_input_revision": "c9be04caf58fc7e458c518fd7cb1566662db9ad4",
        "executed_source_sha256": source_hashes, "provenance": startup_provenance,
        "provenance_capture": "Code/runtime/input fingerprints captured before native execution; output fingerprints after files close",
        "width_table": {"name": args.width_table.name, "sha256": sha256(args.width_table)},
        "original_proto_reference": {"enabled": False, "count_field_semantics": "zero sentinel; unsafe reference finder not scheduled"},
        "digitization_native_defaults": {"model": "Gauss", "doMerge": False, "mergeCommonCorner": False,
            "minEnergyDeposit": 0., "geometric": False, "post_cluster_errors": False,
            "variance": "independent diagonal pooled sigma squared", "mean": 0., "forcePositiveValues": False,
            "maxRetries": 0, "boundary": "Native rejection outside sensitive bounds after one draw; no retry"},
        "ROOT": ROOT.gROOT.GetVersion()}
    write_report(args.output/"run-report.json", report)
    try:
        detector, geometry, context, surfaces, decoration = prepare_geometry(args, manifest, acts, sidecar, expanded)
        sensors = json.loads(detector.geometryReport())["sensors"]
        digi, counts = build_config(sensors, config["digitization"], table)
        write_report(args.output/"digitization.json", digi)
        report.update(native_decoration=decoration, digitization_sensors_by_system=counts)
        report["provenance"]["files"].append({"role": "digitization", "name": "digitization.json", "sha256": sha256(args.output/"digitization.json")})
        write_report(args.output/"run-report.json", report)
        run(args, config, acts, detector, geometry, observer)
        names = ("particles.root", "particles_selected.root", "audit.root", "tracksummary_kf.root",
                 "trackstates_kf.root", "performance_kf.root", "measurements.root")
        report["root_inventory"] = {name: root_inventory(ROOT, args.output/name) for name in names}
        audit = ROOT.RDataFrame("audit", str(args.output/"audit.root"))
        report["counts"] = {name: int(audit.Sum["ULong64_t"](name).GetValue()) for name in (
            "generated", "simhits", "measurements", "selected", "fit_attempts", "fit_tracks", "invalid_covariance",
            "primary_measurements", "original_proto_measurements", "corrected_proto_measurements", "primary_measurement_associations_raw")}
        report["counts"]["events"] = int(audit.Count().GetValue())
        if report["counts"]["events"] != args.events or report["counts"]["generated"] != args.events:
            raise RuntimeError("Native output lost requested one-muon events")
        if not 0 <= report["counts"]["measurements"] <= report["counts"]["simhits"]:
            raise RuntimeError("Unmerged Gaussian measurement count differs from one draw per simhit")
        report["counts"]["simhits_without_measurement"] = report["counts"]["simhits"] - report["counts"]["measurements"]
        sensor_system = {sensor["geometry_id"]: sensor["ids"]["system"] for sensor in sensors}
        source = ROOT.TFile.Open(str(args.output/"audit.root"))
        systems, dimensions = {str(i): 0 for i in range(1, 8)}, {"1": 0, "2": 0}
        for event in source.Get("audit"):
            for identity, dimension in zip(event.measurement_geometry_id, event.measurement_dimension):
                system = sensor_system[int(identity)]
                if int(dimension) != (1 if system >= 6 else 2):
                    raise RuntimeError("Native measurement dimension differs from sensor contract")
                systems[str(system)] += 1; dimensions[str(dimension)] += 1
        source.Close()
        report["measurement_counts_by_system"], report["measurement_counts_by_dimension"] = systems, dimensions
        if args.events >= 100 and any(value == 0 for value in systems.values()):
            raise RuntimeError("Native sample lacks one or more tracker systems")
        report["measurement_audit"] = audit_measurements(ROOT, args.output/"measurements.root", table)
        if report["measurement_audit"]["measurement_rows"] != report["counts"]["measurements"]:
            raise RuntimeError("Measurement ROOT rows do not agree with native audit")
        if any(sha256(path) != source_hashes[str(path.relative_to(ROOT_DIR))] for path in source_paths):
            raise RuntimeError("Executed source/native observer changed during run")
        report["provenance"]["files"].extend({"role": "native_output", "name": name,
            "sha256": sha256(args.output/name)} for name in names)
        report["provenance"]["analysis_source_revision_at_launch"] = launch_revision
        report["outcome"] = "completed"
    except Exception as error:
        report["outcome"] = "failed"; report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        report["wall_seconds"] = time.monotonic() - start
        write_report(args.output/"run-report.json", report)
    print(json.dumps({"outcome": report["outcome"], "counts": report.get("counts"), "wall_seconds": report["wall_seconds"]}))


if __name__ == "__main__":
    main()
