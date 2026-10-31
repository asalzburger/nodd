"""Separate all-coordinate Gaussian pitch/sqrt(12) control (PROTOTYPE).

This imports the frozen digital study's balanced geometry/material preparation
and all-event reduction, while replacing only this control's generated digi
JSON before native execution. No original source or result is modified.
"""
import argparse
from collections import Counter
import copy
import importlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import truth as frozen
import smearing
from digitization import geometry_fields
from material_runtime import sha256, write_report
from runtime import load_campaign, root_inventory, schedule_native_truth_seed

ROOT = frozen.ROOT
RESPONSE_MODEL = "gaussian_pitch_over_sqrt12_no_merge"
FROZEN_TRUTH_SHA256 = "e6aa98adc2fde8c60fcbf3f067fe069da399eb6a3b337d0149c87e5322b10cd0"


def control_campaign(base, pitch):
    config = frozen.case_config(base, pitch)
    config["pt_GeV"] = [100.0]
    config["events_per_case"] = 5000
    config["measurement_model"] = "Independent native Gaussian p/sqrt(12) in every measured coordinate; no geometric cells or merging"
    config["digitization"].update(model=RESPONSE_MODEL, merge=False,
                                   digital=False, component_digital=False)
    return config


def gaussian_config(sensors, config):
    """Nominal-pitch widths are assumptions, never fabricated training rows."""
    entries, lookup, identities, counts = [], {}, set(), Counter()
    pitches = {**{i: config["digitization"]["pixel_pitch_mm"] for i in (1, 2, 3)},
               **{i: config["digitization"]["short_strip_pitch_mm"] for i in (4, 5)},
               **{i: [config["digitization"]["long_strip_pitch_mm"]] for i in (6, 7)}}
    for sensor in sorted(sensors, key=lambda row: row["geometry_id"]):
        identity, system = sensor["geometry_id"], sensor["ids"]["system"]
        if identity in identities or system not in pitches:
            raise ValueError("Duplicate or unsupported native sensor")
        identities.add(identity)
        fields = geometry_fields(identity)
        smearers = []
        for index, pitch in enumerate(pitches[system]):
            if not math.isfinite(pitch) or pitch <= 0:
                raise ValueError("Expected a positive finite nominal pitch")
            sigma = pitch / math.sqrt(12.)
            smearers.append({"index": index, "type": "Gauss", "mean": 0.,
                             "stddev": sigma, "forcePositiveValues": False})
            key = fields["volume"], index
            row = {"volume": fields["volume"], "system": system, "index": index,
                   "nominal_pitch_mm": pitch, "sigma_mm": sigma}
            if key in lookup and lookup[key] != row:
                raise ValueError("A native volume mixes different Gaussian response contracts")
            lookup[key] = row
        entries.append({**fields, "value": {"smearing": smearers}})
        counts[str(system)] += 1
    if dict(counts) != frozen.EXPECTED_SENSORS:
        raise ValueError("Expected every maintained balanced sensor exactly once")
    payload = {"acts-geometry-hierarchy-map": {"format-version": 0,
               "value-identifier": "digitization-configuration"}, "entries": entries}
    audit = {"model": RESPONSE_MODEL, "sensors_by_system": dict(counts),
             "geometric_entries": 0, "merge": False, "mergeCommonCorner": False,
             "width_origin": "Nominal pitch divided by sqrt(12); independent Gaussian hypothesis, no training sample",
             "widths": [lookup[k] for k in sorted(lookup)],
             "boundary_contract": "Native bounded-Gaussian draws; preserve retry/exhaustion diagnostics"}
    return payload, audit


def audit_gaussian_measurements(path, width_audit):
    import numpy as np
    import uproot
    with uproot.open(path) as stream:
        data = stream["measurements"].arrays(
            ["volume_id", "clus_size", "rec_loc0", "rec_loc1", "true_loc0", "true_loc1",
             "var_loc0", "var_loc1"], library="np")
    if np.any(data["clus_size"] != 0):
        raise ValueError("Gaussian-only writer unexpectedly retained geometric cells")
    lookup = {(row["volume"], row["index"]): row for row in width_audit["widths"]}
    groups, checked = [], 0
    for volume in sorted(set(map(int, data["volume_id"]))):
        mask = data["volume_id"] == volume
        for index in (0, 1):
            rec, truth, variance = [data[f"{name}_loc{index}"][mask] for name in ("rec", "true", "var")]
            row = lookup.get((volume, index))
            if row is None:
                if np.any(np.isfinite(rec)) or np.any(np.isfinite(variance)):
                    raise ValueError("Native Gaussian output introduced an unmeasured coordinate")
                continue
            expected = np.asarray(row["sigma_mm"]**2, dtype=variance.dtype)
            if not np.all(np.isfinite(rec)) or not np.all(np.isfinite(truth)) or not np.all(variance == expected):
                raise ValueError("Native Gaussian coordinates/variance differ from the actual config")
            standardized = (rec.astype(float) - truth.astype(float)) / row["sigma_mm"]
            checked += len(rec)
            groups.append({**row, "entries": len(rec), "stored_variance_mm2": float(expected),
                "standardized_mean": float(standardized.mean()),
                "standardized_rms": float(np.sqrt(np.mean(standardized**2))),
                "standardized_sd": float(standardized.std()),
                "abs_gt3": int(np.sum(np.abs(standardized) > 3))})
    return {"measurement_rows": len(data["volume_id"]), "coordinate_rows": checked,
            "exact_stored_variance_check": "PASS", "geometric_cluster_rows": 0,
            "residual_convention": "persisted reconstructed minus truth local coordinate",
            "groups": groups}


def run_native(args, config, acts, observer, detector, geometry):
    from acts.examples.simulation import (addParticleGun, MomentumConfig, EtaConfig,
        PhiConfig, ParticleConfig, addFatras, addDigiParticleSelection, ParticleSelectorConfig)
    from acts.examples.reconstruction import addKalmanTracks
    from acts.examples.root import RootParticleWriter, RootTrackSummaryWriter, RootMeasurementWriter, RootSimHitWriter
    u, level = acts.UnitConstants, acts.logging.WARNING
    field = acts.ConstantBField(acts.Vector3(0., 0., config["field_Bz_T"] * u.T))
    rnd = acts.examples.RandomNumbers(seed=config["seed"])
    sequencer = acts.examples.Sequencer(events=args.events, numThreads=1,
        outputDir=str(args.output), logLevel=level)
    for decorator in detector.contextDecorators():
        sequencer.addContextDecorator(decorator)
    addParticleGun(sequencer, ParticleConfig(num=1, pdg=acts.PdgParticle.eMuon, randomizeCharge=True),
        MomentumConfig(args.pt * u.GeV, args.pt * u.GeV, transverse=True),
        EtaConfig(*config["eta_range"], uniform=True), PhiConfig(*config["phi_range_rad"]),
        vtxGen=acts.examples.GaussianVertexGenerator(mean=acts.Vector4(0.,0.,0.,0.),
            stddev=acts.Vector4(0.,0.,0.,0.)), multiplicity=1, rnd=rnd, logLevel=level)
    sequencer.addWriter(RootParticleWriter(level=level, inputParticles="particles_generated",
        filePath=str(args.output / "particles.root")))
    addFatras(sequencer, geometry, field, rnd=rnd, inputParticles="particles_generated",
              enableInteractions=True, logLevel=level)
    sequencer.addWriter(RootSimHitWriter(level=level, inputSimHits="simhits",
        filePath=str(args.output / "hits.root")))
    smearing.schedule_digitization(sequencer, acts, geometry, rnd,
        args.output / "digitization.json", observer, level)
    sequencer.addWriter(RootMeasurementWriter(level=level, inputMeasurements="measurements",
        inputClusters="", inputSimHits="simhits", inputMeasurementSimHitsMap="measurement_simhits_map",
        surfaceByIdentifier=geometry.geoIdSurfaceMap(), filePath=str(args.output / "measurements.root")))
    addDigiParticleSelection(sequencer, ParticleSelectorConfig(
        measurements=(config["truth_tracking"]["minimum_measurements"], None),
        removeNeutral=True, removeSecondaries=True), logLevel=level)
    sequencer.addWriter(RootParticleWriter(level=level, inputParticles="particles_digitized_selected",
        filePath=str(args.output / "particles_selected.root")))
    schedule_native_truth_seed(sequencer, acts, rnd, config["truth_tracking"], level)
    sequencer.addAlgorithm(observer.CorrectTruthProtoTracks())
    addKalmanTracks(sequencer, geometry, field, inputProtoTracks="truth_particle_tracks_corrected", logLevel=level)
    sequencer.addAlgorithm(observer.Audit(str(args.output / "audit.root")))
    sequencer.addWriter(RootTrackSummaryWriter(level=level, inputTracks="kf_tracks", inputParticles="particles_generated",
        inputTrackParticleMatching="kf_track_particle_matching", writeCovMat=True,
        filePath=str(args.output / "tracksummary_kf.root")))
    sequencer.run()


def source_fingerprints(args):
    sources = [Path(__file__).resolve(), ROOT / "software/running/nodd_strixel_gaussian_control.py",
               ROOT / "software/analysis/strixel_pitch_study/test_gaussian_control.py",
               Path(frozen.__file__).resolve(), Path(smearing.__file__).resolve(),
               ROOT / "software/analysis/truth_tracking/metrics.py",
               ROOT / "software/analysis/truth_tracking/runtime.py",
               ROOT / "software/analysis/truth_tracking/digitization.py",
               ROOT / "software/env/truth_tracking.sh",
               ROOT / "software/source/ActsExamples/TruthTracking/TruthTracking.cpp",
               ROOT / "software/source/ActsExamples/TruthTracking/CMakeLists.txt"]
    acts_source = args.nodd_dir / "software/submodules/acts"
    sources.extend(acts_source / "Examples/Algorithms/Digitization/src" / name for name in
                   ("ModuleClusters.cpp", "DigitizationAlgorithm.cpp", "GeometricConfig.cpp"))
    return {str(path): sha256(path) for path in sources}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, default=ROOT / "software/analysis/strixel_pitch_study/campaign.json")
    parser.add_argument("--pitch", type=float, required=True)
    parser.add_argument("--pt", type=float, default=100.)
    parser.add_argument("--events", type=int, default=5000)
    parser.add_argument("--threads", type=int, default=1)
    for name in ("nodd-dir", "build-dir", "native-module-dir", "observer-module-dir", "material-module-dir", "comparison-dir", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if args.pt != 100. or args.events <= 0 or args.threads != 1:
        parser.error("Control requires 100 GeV, positive events and exactly one native thread")
    for name, value in vars(args).items():
        if isinstance(value, Path):
            setattr(args, name, value.resolve())
    if sha256(frozen.__file__) != FROZEN_TRUTH_SHA256:
        parser.error("Frozen digital-study helper source identity changed")
    config = control_campaign(load_campaign(args.campaign), args.pitch)
    if not args.output.is_relative_to((ROOT / "build/strixel-pitch-study").resolve()):
        parser.error("Control outputs must stay under ignored build/strixel-pitch-study")
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.iterdir()):
        parser.error("Choose a fresh control directory; existing evidence is immutable")
    launch_sources = source_fingerprints(args)
    report = {"schema_version": 1, "status": "PROTOTYPE", "outcome": "started",
        "response_model": RESPONSE_MODEL, "campaign": config, "pitch_mm": args.pitch,
        "pt_GeV": args.pt, "requested_events": args.events, "threads": 1, "simulation": "fatras",
        "command": sys.argv, "scientific_input_revision": subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "digital_reference_revision": "8b7c147b3b0da4bd40dcd9ad06c98abcb2de58f9",
        "control_source_sha256": launch_sources, "residual_convention": frozen.RESIDUAL_CONVENTION,
        "array_coordinate_order": ["d0_mm", "z0_mm", "phi_rad", "theta_rad", "qOverP_GeV_inv"],
        "response_limit": "Independent Gaussian nominal-pitch hypothesis; no calibrated electronics, geometric clusters, occupancy or pattern-recognition claim"}
    start = time.monotonic()
    try:
        ROOTmod, acts, observer, detector, geometry, native, info = frozen.prepare(args, config)
        report["preparation"] = info
        gaussian, audit = gaussian_config(native["sensors"], config)
        # Replace only this fresh control's unused geometric preparation JSON.
        # Actual native execution below reads the audited Gaussian-only config.
        write_report(args.output / "digitization.json", gaussian)
        if json.loads((args.output / "digitization.json").read_text()) != gaussian:
            raise RuntimeError("Serialized control configuration differs from generated Gaussian hypothesis")
        write_report(args.output / "gaussian-config-audit.json", audit)
        report["gaussian_config_audit"] = audit
        report["native_digitization"] = {"model": "Gauss", "geometric": False,
            "doMerge": False, "mergeCommonCorner": False, "minEnergyDeposit": 0.,
            "variance": "independent diagonal nominal pitch squared /12", **smearing.native_boundary_contract(acts)}
        report["prepare_seconds"] = time.monotonic() - start
        run_native(args, config, acts, observer, detector, geometry)
        report["native_seconds"] = time.monotonic() - start - report["prepare_seconds"]
        reduction_args = copy.copy(args)
        reduction_args.write_measurements = False  # Skip frozen geometric-only measurement diagnostics.
        report["reduction"] = frozen.reduce_case(reduction_args, native["sensors"])
        report["gaussian_measurement_audit"] = audit_gaussian_measurements(args.output / "measurements.root", audit)
        if report["gaussian_measurement_audit"]["measurement_rows"] != report["reduction"]["counts"]["measurements"]:
            raise RuntimeError("Gaussian measurement writer differs from native all-event audit")
        report["reduction"]["counts"]["simhits_without_measurement"] = (
            report["reduction"]["counts"]["simhits"] - report["reduction"]["counts"]["measurements"])
        if source_fingerprints(args) != launch_sources:
            raise RuntimeError("Control source/helper fingerprints changed during native execution")
        names = ("particles.root", "particles_selected.root", "audit.root", "tracksummary_kf.root", "hits.root", "measurements.root")
        report["root_inventory"] = {name: root_inventory(ROOTmod, args.output / name) for name in names}
        report["output_sha256"] = {p.name: sha256(p) for p in args.output.iterdir() if p.is_file()}
        report["outcome"] = "completed"
    except Exception as error:
        report["outcome"] = "failed"
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        report["wall_seconds"] = time.monotonic() - start
        write_report(args.output / "run-report.json", report)
    print(json.dumps({"outcome": report["outcome"], "response_model": RESPONSE_MODEL,
        "pitch_mm": args.pitch, "events": args.events, "counts": report["reduction"]["counts"],
        "wall_seconds": report["wall_seconds"]}))


if __name__ == "__main__":
    main()
