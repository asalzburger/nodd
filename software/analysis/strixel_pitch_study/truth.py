"""Isolated paired native ACTS short-strip pitch sensitivity (PROTOTYPE).

The geometry and effective material representation remain the PR104 balanced
baseline. Only the geometric short-strip cell local-v pitch changes. Native
ACTS transports, channelizes, clusters, truth-associates and Kalman-fits muons.
This is uncalibrated ideal digital-response sensitivity, not reconstruction.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
for directory in ("gen3_material_mapping", "truth_tracking", "tracker_optimization"):
    sys.path.append(str(ROOT / "software/analysis" / directory))
from material_runtime import native_imports, apply_saved_map, sha256, write_report
from export_geometry import build_export
from select_surfaces import select
from material import select_candidate, transport
from digitization import build_config
from runtime import load_campaign, schedule_native_truth_seed, root_inventory

EXPECTED_SENSORS = {"1": 6794, "2": 2808, "3": 2808, "4": 8064,
                    "5": 4320, "6": 13968, "7": 7488}
COMPACT_SHA256 = "81e2d439a66f0978d0613929842cf6aa4658cd0e0300ede7513d30caae296023"
PARAMETERS = ("eLOC0", "eLOC1", "ePHI", "eTHETA", "eQOP")
BARCODE = ("vertex_primary", "vertex_secondary", "particle", "generation", "sub_particle")
AUDIT = ("generated", "simhits", "measurements", "selected", "fit_attempts",
         "fit_tracks", "invalid_covariance", "primary_measurements")
RESIDUAL_CONVENTION = "fitted minus truth; phi wrapped; perigee truth from origin gun"


def case_config(campaign, pitch):
    """Copy the campaign, changing precisely the short-strip local-v pitch."""
    if pitch not in campaign["short_strip_local_v_pitch_mm"]:
        raise ValueError("Pitch is absent from the frozen scan")
    config = json.loads(json.dumps(campaign))
    config["digitization"]["short_strip_pitch_mm"] = [0.075, pitch]
    return config


def same_geometry(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same_geometry(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same_geometry(x, y) for x, y in zip(a, b))
    if isinstance(a, float) and isinstance(b, float):
        return abs(a-b) < 1.e-9
    return a == b


def prepare(args, config):
    """Reuse maintained reconstruction role-transport with explicit build paths.

    This intentionally omits prepare.py's frozen Gaussian hit-error remapping:
    stale 0.5 mm calibrated widths must not enter this changing-pitch campaign.
    """
    ROOTmod, acts, portal = native_imports(args.native_module_dir)
    sys.path.insert(0, str(args.observer_module_dir))
    observer = importlib.import_module("nodd_truth_tracking")
    sys.path.insert(0, str(args.material_module_dir))
    helper = importlib.import_module("nodd_tracker_material")
    from acts.examples.nodd import getNoddDetector
    compact = args.build_dir / "detector/tracker/tracker.xml"
    if sha256(compact) != COMPACT_SHA256:
        raise RuntimeError("Expected registered PR104 balanced compact")
    detector = getNoddDetector(nodd_dir=args.nodd_dir, build_dir=args.build_dir,
                              compact_file=compact, logLevel=acts.logging.WARNING)
    geometry, context = detector.trackingGeometry(), detector.nominalGeometryContext()
    native = json.loads(detector.geometryReport())
    counts = dict(Counter(str(s["ids"]["system"]) for s in native["sensors"]))
    if counts != EXPECTED_SENSORS:
        raise RuntimeError(f"Balanced native sensor inventory differs: {counts}")
    converter = acts.json.TrackingGeometryJsonConverter(level=acts.logging.WARNING)
    exported = build_export(json.loads(converter.toJson(context, geometry)), native,
                           lambda x: acts.GeometryIdentifier(**(x or {})).value)
    source_manifest_path = ROOT / "docs/validation/gen3-material-map-run/selection.json"
    source_map_path = ROOT / config["material_map"]
    variant_path = ROOT / "software/analysis/tracker_optimization/variants/balanced.json"
    source_manifest = json.loads(source_manifest_path.read_text())
    variant = json.loads(variant_path.read_text())
    manifest = select_candidate(exported, source_manifest["configuration"], variant, select)
    with gzip.open(source_map_path, "rt") as stream:
        mapped, material_audit = transport(source_manifest, manifest, json.load(stream), variant, helper)
    write_report(args.output / "selection.json", manifest)
    write_report(args.output / "material-map.json", mapped)
    decoration = portal.configure(geometry, context, manifest["surfaces"])
    decoration.pop("surfaces")
    decoration.update(apply_saved_map(geometry, manifest, acts, args.output / "material-map.json", portal))
    digi, digi_counts = build_config(native["sensors"], config["digitization"])
    if digi_counts != EXPECTED_SENSORS:
        raise RuntimeError("Digitization did not cover every balanced sensor")
    write_report(args.output / "digitization.json", digi)
    write_report(args.output / "native-report.json", native)
    comparison = args.comparison_dir
    equivalence = {}
    if comparison:
        for name in ("selection.json", "material-map.json"):
            previous = comparison / name
            if not previous.is_file():
                raise ValueError("Missing retained balanced comparison " + str(previous))
            current = json.loads((args.output / name).read_text())
            old = json.loads(previous.read_text())
            equivalence[name] = same_geometry(current, old) if name == "selection.json" else current == old
        if not all(equivalence.values()):
            raise RuntimeError(f"Material/geometry differs from balanced confirmation: {equivalence}")
    files = [source_manifest_path, source_map_path, variant_path, compact,
             Path(__file__).resolve(), args.campaign,
             ROOT / "software/running/nodd_strixel_pitch_truth.py",
             ROOT / "software/analysis/truth_tracking/digitization.py",
             ROOT / "software/analysis/truth_tracking/runtime.py",
             ROOT / "software/analysis/tracker_reconstruction/prepare.py",
             ROOT / "software/analysis/tracker_optimization/material.py",
             ROOT / "software/analysis/gen3_material_mapping/material_runtime.py",
             ROOT / "software/analysis/gen3_material_mapping/export_geometry.py",
             ROOT / "software/analysis/gen3_material_mapping/select_surfaces.py"]
    for module in (portal, observer, helper,
                   importlib.import_module("acts.ActsPythonBindings"),
                   importlib.import_module("acts.examples.ActsExamplesPythonBindings"),
                   importlib.import_module("acts.examples.ActsExamplesPythonBindingsNodd")):
        files.append(Path(module.__file__).resolve())
    detector_dir = compact.parents[1]
    files.extend(sorted(detector_dir.rglob("*.xml")))
    files.extend(sorted(detector_dir.glob("*.dylib")))
    runtime = Path(importlib.import_module("acts.ActsPythonBindings").__file__).parents[2]
    for name in ("ActsCore", "ActsExamplesFramework", "ActsExamplesFatras", "ActsExamplesDigitization",
                 "ActsExamplesTrackFitting", "ActsExamplesTruthTracking", "ActsExamplesIoRoot"):
        library = runtime / "lib" / f"lib{name}.dylib"
        if library.is_file():
            files.append(library)
    info = {"native_geometry": exported["checks"], "sensor_counts": counts,
            "material_transport": material_audit, "material_decoration": decoration,
            "balanced_comparison": equivalence,
            "files_sha256": {str(p): sha256(p) for p in sorted(set(files))},
            "ROOT": ROOTmod.gROOT.GetVersion(), "python": sys.version,
            "native_source_revision": subprocess.check_output(
                ["git", "-C", str(args.nodd_dir), "rev-parse", "HEAD"], text=True).strip(),
            "ACTS_source_revision": subprocess.check_output(
                ["git", "-C", str(args.nodd_dir / "software/submodules/acts"), "rev-parse", "HEAD"], text=True).strip(),
            "ACTS_source_dirty_paths": subprocess.check_output(
                ["git", "-C", str(args.nodd_dir / "software/submodules/acts"), "status", "--short"], text=True).splitlines()}
    return ROOTmod, acts, observer, detector, geometry, native, info


def run_native(args, config, acts, observer, detector, geometry):
    from acts.examples.simulation import (addParticleGun, MomentumConfig, EtaConfig,
        PhiConfig, ParticleConfig, addFatras, addDigiParticleSelection, ParticleSelectorConfig)
    from acts.examples.reconstruction import addKalmanTracks
    from acts.examples.root import RootParticleWriter, RootTrackSummaryWriter, RootMeasurementWriter, RootSimHitWriter
    from acts.examples import json as acts_json
    u, level = acts.UnitConstants, acts.logging.WARNING
    field = acts.ConstantBField(acts.Vector3(0., 0., config["field_Bz_T"] * u.T))
    rnd = acts.examples.RandomNumbers(seed=config["seed"])
    s = acts.examples.Sequencer(events=args.events, numThreads=args.threads,
        outputDir=str(args.output), logLevel=level)
    for decorator in detector.contextDecorators():
        s.addContextDecorator(decorator)
    addParticleGun(s, ParticleConfig(num=1, pdg=acts.PdgParticle.eMuon, randomizeCharge=True),
        MomentumConfig(args.pt * u.GeV, args.pt * u.GeV, transverse=True),
        EtaConfig(*config["eta_range"], uniform=True), PhiConfig(*config["phi_range_rad"]),
        vtxGen=acts.examples.GaussianVertexGenerator(mean=acts.Vector4(0.,0.,0.,0.),
            stddev=acts.Vector4(0.,0.,0.,0.)), multiplicity=1, rnd=rnd, logLevel=level)
    s.addWriter(RootParticleWriter(level=level, inputParticles="particles_generated",
                                  filePath=str(args.output / "particles.root")))
    addFatras(s, geometry, field, rnd=rnd, inputParticles="particles_generated",
              enableInteractions=True, logLevel=level)
    s.addWriter(RootSimHitWriter(level=level, inputSimHits="simhits",
                                filePath=str(args.output / "hits.root")))
    s.addAlgorithm(acts.examples.DigitizationAlgorithm(acts.examples.DigitizationAlgorithm.Config(
        digitizationConfigs=acts_json.readDigiConfigFromJson(str(args.output / "digitization.json")),
        surfaceByIdentifier=geometry.geoIdSurfaceMap(), randomNumbers=rnd, inputSimHits="simhits",
        outputMeasurements="measurements", outputMeasurementParticlesMap="measurement_particles_map_raw",
        outputMeasurementSimHitsMap="measurement_simhits_map", outputParticleMeasurementsMap="particle_measurements_map_raw",
        outputSimHitMeasurementsMap="simhit_measurements_map", doMerge=True, mergeCommonCorner=True,
        minEnergyDeposit=0.), level))
    s.addAlgorithm(observer.UniqueAssociations())
    if args.write_measurements:
        s.addWriter(RootMeasurementWriter(level=level, inputMeasurements="measurements",
            inputClusters="clusters", inputSimHits="simhits", inputMeasurementSimHitsMap="measurement_simhits_map",
            surfaceByIdentifier=geometry.geoIdSurfaceMap(), filePath=str(args.output / "measurements.root")))
    addDigiParticleSelection(s, ParticleSelectorConfig(
        measurements=(config["truth_tracking"]["minimum_measurements"], None),
        removeNeutral=True, removeSecondaries=True), logLevel=level)
    s.addWriter(RootParticleWriter(level=level, inputParticles="particles_digitized_selected",
                                  filePath=str(args.output / "particles_selected.root")))
    schedule_native_truth_seed(s, acts, rnd, config["truth_tracking"], level)
    s.addAlgorithm(observer.CorrectTruthProtoTracks())
    addKalmanTracks(s, geometry, field, inputProtoTracks="truth_particle_tracks_corrected", logLevel=level)
    s.addAlgorithm(observer.Audit(str(args.output / "audit.root")))
    s.addWriter(RootTrackSummaryWriter(level=level, inputTracks="kf_tracks", inputParticles="particles_generated",
        inputTrackParticleMatching="kf_track_particle_matching", writeCovMat=True,
        filePath=str(args.output / "tracksummary_kf.root")))
    s.run()


def join_events(generated, requested):
    import numpy as np
    generated, requested = np.asarray(generated), np.asarray(requested)
    if len(np.unique(generated)) != len(generated):
        raise ValueError("Repeated generated event identity")
    order = np.argsort(generated)
    positions = np.searchsorted(generated[order], requested)
    if np.any(positions >= len(generated)):
        raise ValueError("Output contains unknown generated event")
    indices = order[positions]
    if not np.array_equal(generated[indices], requested):
        raise ValueError("Output contains unknown generated event")
    return indices


def reduce_case(args, sensors):
    """Keep every generated event; retain partial/unmatched native fits visibly."""
    import awkward as ak
    import numpy as np
    import uproot
    from metrics import classify_primary_barcodes, perigee_observables
    def flat(data, key):
        return ak.to_numpy(ak.flatten(data[key], axis=None))
    with uproot.open(args.output / "particles.root") as stream:
        g = stream["particles"].arrays(library="ak")
    events = ak.to_numpy(g["event_id"])
    n = len(events)
    if n != args.events or not np.all(ak.to_numpy(ak.num(g["pt"])) == 1):
        raise ValueError("Missing generated events or not exactly one muon per event")
    if (not np.all(np.abs(flat(g, "particle_type")) == 13)
            or not np.all(np.abs(flat(g, "q")) == 1)
            or any(np.any(flat(g, x) != 0) for x in ("vx", "vy", "vz"))
            or not np.allclose(flat(g, "pt"), args.pt, rtol=2.e-6, atol=1.e-7)):
        raise ValueError("Gun differs from the origin fixed-pT charged-muon contract")
    truth = np.column_stack([np.zeros(n), np.zeros(n), flat(g, "phi"), flat(g, "theta"), flat(g, "q_over_p")])
    # Prove pairing using the serialized physical hit payload, not ROOT-file
    # bytes (which also contain timestamps). Digitization must not alter Fatras.
    with uproot.open(args.output / "hits.root") as stream:
        hit_arrays = stream["hits"].arrays(library="np")
    hit_order = np.lexsort(tuple(hit_arrays[k] for k in
        ("barcode_sub_particle", "barcode_generation", "barcode_particle",
         "barcode_vertex_secondary", "barcode_vertex_primary", "geometry_id", "index", "event_id")))
    hit_primary = join_events(events, hit_arrays["event_id"])
    primary_mask = np.ones(len(hit_primary), dtype=bool)
    for key in BARCODE:
        primary_mask &= hit_arrays["barcode_" + key] == flat(g, key)[hit_primary]
    def hit_digest(mask=None):
        digest = hashlib.sha256()
        indices = hit_order if mask is None else hit_order[mask[hit_order]]
        for name in sorted(hit_arrays):
            values = np.ascontiguousarray(hit_arrays[name][indices])
            digest.update(name.encode()); digest.update(values.dtype.str.encode())
            digest.update(values.tobytes())
        return digest.hexdigest()
    transport_pairing = {"all_simhits": len(hit_order), "primary_simhits": int(primary_mask.sum()),
                         "all_payload_sha256": hit_digest(),
                         "primary_payload_sha256": hit_digest(primary_mask),
                         "method": "All scalar ROOT branches sorted by event/index/geometry/barcode; branch names, dtypes and exact stored bytes hashed"}
    with uproot.open(args.output / "audit.root") as stream:
        raw = stream["audit"].arrays(["event_nr", *AUDIT, "measurement_geometry_id", "measurement_dimension"], library="ak")
    audit_events = ak.to_numpy(raw["event_nr"])
    if len(audit_events) != n or len(np.unique(audit_events)) != n:
        raise ValueError("Audit lacks every independent generated event")
    order = join_events(audit_events, events)
    audit = {k: ak.to_numpy(raw[k])[order].astype(np.int64) for k in AUDIT}
    if (not np.all(audit["generated"] == 1) or np.any(audit["selected"] > 1)
            or np.any(audit["fit_attempts"] > audit["selected"])
            or np.any(audit["fit_tracks"] > audit["fit_attempts"])):
        raise ValueError("Native stage counts violate the one-primary truth campaign")
    sensor_system = {s["geometry_id"]: s["ids"]["system"] for s in sensors}
    systems = Counter()
    for gid, dim in zip(flat(raw, "measurement_geometry_id"), flat(raw, "measurement_dimension")):
        sy = sensor_system[int(gid)]
        if int(dim) != (1 if sy >= 6 else 2):
            raise ValueError("Native measured dimensionality differs from sensor contract")
        systems[str(sy)] += 1
    with uproot.open(args.output / "particles_selected.root") as stream:
        selected = stream["particles"].arrays(["event_id", *BARCODE], library="ak")
    selected_order = join_events(events, ak.to_numpy(selected["event_id"]))
    if len(selected) != n or not np.array_equal(ak.to_numpy(ak.num(selected["particle"])), audit["selected"][selected_order]):
        raise ValueError("Selected writer differs from audit")
    selected_events = ak.to_numpy(ak.flatten(ak.broadcast_arrays(selected["event_id"], selected["particle"])[0]))
    selected_primary = join_events(events, selected_events)
    if any(not np.array_equal(flat(selected, k), flat(g, k)[selected_primary]) for k in BARCODE):
        raise ValueError("Selected candidate is not the generated primary")
    branches = ["event_nr", "track_nr", "hasFittedParams", "nMeasurements", "trackClassification"]
    branches += ["majorityParticleId_" + k for k in BARCODE]
    branches += [k + "_fit" for k in PARAMETERS]
    branches += ["cov_" + a + "_" + b for a in PARAMETERS for b in PARAMETERS]
    with uproot.open(args.output / "tracksummary_kf.root") as stream:
        t = stream["tracksummary"].arrays(branches, library="ak")
    te = ak.to_numpy(ak.flatten(ak.broadcast_arrays(t["event_nr"], t["track_nr"])[0]))
    ti = join_events(events, te)
    multiplicity = np.bincount(ti, minlength=n)
    if np.any(multiplicity > 1) or not np.array_equal(multiplicity, audit["fit_tracks"]):
        raise ValueError("Fitted multiplicity conflicts with audit")
    if np.any(audit["selected"][ti] != 1) or np.any(audit["fit_attempts"][ti] != 1):
        raise ValueError("Fitted track lacks a unique primary-derived candidate")
    matched = classify_primary_barcodes(
        np.column_stack([flat(t, "majorityParticleId_" + k) for k in BARCODE]),
        np.column_stack([flat(g, k)[ti] for k in BARCODE]))
    classifications = flat(t, "trackClassification")
    if np.any(classifications[matched] != 1) or np.any(classifications[~matched] != 3):
        raise ValueError("Unexpected native matching classification")
    fit = np.column_stack([flat(t, k + "_fit") for k in PARAMETERS])
    covariance = np.empty((len(fit), 5, 5))
    for i, a in enumerate(PARAMETERS):
        for j, b in enumerate(PARAMETERS):
            covariance[:, i, j] = flat(t, "cov_" + a + "_" + b)
    values, flags = perigee_observables(fit, truth[ti], covariance)
    has = flat(t, "hasFittedParams").astype(bool)
    output = {"event": events, "eta": flat(g, "eta"), "pt_GeV": flat(g, "pt"),
              "charge": flat(g, "q"), "truth": truth, **{"audit_" + k: v for k, v in audit.items()}}
    for name, data, fill in (("fitted", fit, np.nan), ("covariance", covariance, np.nan),
                             ("has_fitted_parameters", has, False), ("native_primary_match", matched, False),
                             ("n_measurements", flat(t, "nMeasurements"), 0)):
        dest = np.full((n, *data.shape[1:]), fill, dtype=data.dtype)
        dest[ti] = data
        output[name] = dest
    for name, pair in values.items():
        for kind, data in pair.items():
            dest = np.full(n, np.nan)
            dest[ti] = np.where(has, data, np.nan)
            output[name + "_" + kind] = dest
    for name, data in flags.items():
        dest = np.zeros(n, dtype=bool)
        dest[ti] = data & has
        output[name] = dest
    np.savez_compressed(args.output / "events.npz", **output)
    sample = hashlib.sha256(np.column_stack([events, output["eta"], output["pt_GeV"], output["charge"], truth]).astype("<f8").tobytes()).hexdigest()
    schema = {k: {"dtype": str(v.dtype), "shape": list(v.shape)} for k, v in output.items()}
    measurement_diagnostics = {}
    if args.write_measurements:
        with uproot.open(args.output / "measurements.root") as stream:
            measured = stream["measurements"].arrays(
                ["volume_id", "clus_size", "clus_size_loc0", "clus_size_loc1",
                 "var_loc0", "var_loc1", "residual_loc0", "residual_loc1"], library="np")
        volume_system = {(s["geometry_id"] >> 56) & 255: s["ids"]["system"] for s in sensors}
        for system in (4, 5):
            use = np.isin(measured["volume_id"], [v for v, sy in volume_system.items() if sy == system])
            single = use & (measured["clus_size"] == 1)
            row = {"measurements": int(use.sum()), "single_cell_clusters": int(single.sum())}
            for index, pitch in enumerate((.075, args.pitch)):
                variance = measured[f"var_loc{index}"]
                expected = np.asarray(pitch*pitch/12, dtype=variance.dtype)
                if np.any(single) and not np.all(variance[single] == expected):
                    raise ValueError("Single-cell native geometric variance differs from actual pitch squared /12")
                residual = measured[f"residual_loc{index}"][use]
                residual = residual[np.isfinite(residual)]
                sizes, numbers = np.unique(measured[f"clus_size_loc{index}"][use], return_counts=True)
                row[str(index)] = {"pitch_mm": pitch, "single_cell_expected_variance_mm2": float(expected),
                    "single_cell_exact_stored_variance_check": "PASS" if np.any(single) else "no single-cell clusters",
                    "cluster_sizes": {str(int(x)): int(y) for x, y in zip(sizes, numbers)},
                    "local_residual_finite": len(residual),
                    "local_residual_mean_mm": float(np.mean(residual)) if len(residual) else None,
                    "local_residual_rms_mm": float(np.sqrt(np.mean(residual*residual))) if len(residual) else None}
            measurement_diagnostics[str(system)] = row
    return {"events": n, "counts": {k: int(v.sum()) for k, v in audit.items()},
            "native_matched": int(matched.sum()), "native_unmatched": int((~matched).sum()),
            "finite_fit": int(output["finite_fitted_parameters"].sum()),
            "measurement_counts_by_system": dict(systems), "generated_sample_sha256": sample,
            "transport_pairing": transport_pairing,
            "measurement_diagnostics": measurement_diagnostics,
            "event_array_schema": schema, "event_array_sha256": sha256(args.output / "events.npz")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, default=Path(__file__).with_name("campaign.json"))
    parser.add_argument("--pitch", type=float, required=True)
    parser.add_argument("--pt", type=float, required=True)
    parser.add_argument("--events", type=int, default=20000)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--nodd-dir", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--native-module-dir", type=Path, required=True)
    parser.add_argument("--observer-module-dir", type=Path, required=True)
    parser.add_argument("--material-module-dir", type=Path, required=True)
    parser.add_argument("--comparison-dir", type=Path)
    parser.add_argument("--write-measurements", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    campaign = load_campaign(args.campaign)
    config = case_config(campaign, args.pitch)
    if args.pt not in config["pt_GeV"] or args.events <= 0 or args.threads <= 0:
        parser.error("Require configured pT and positive event/thread counts")
    for name in ("campaign", "nodd_dir", "build_dir", "native_module_dir", "observer_module_dir",
                 "material_module_dir", "output", "comparison_dir"):
        if getattr(args, name) is not None:
            setattr(args, name, getattr(args, name).resolve())
    required_output_parent = (ROOT / "build/strixel-pitch-study").resolve()
    if not args.output.is_relative_to(required_output_parent):
        parser.error("Generated output must stay under ignored build/strixel-pitch-study")
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.glob("*.root")) or (args.output / "run-report.json").exists():
        parser.error("Choose a fresh output directory; existing evidence is immutable")
    report = {"schema_version": 1, "status": "PROTOTYPE", "outcome": "started",
              "campaign": config, "pitch_mm": args.pitch, "pt_GeV": args.pt,
              "requested_events": args.events, "threads": args.threads, "simulation": "fatras",
              "command": sys.argv, "scientific_input_revision": subprocess.check_output(
                  ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
              "response_limit": "Uncalibrated native geometric digital covariance; no empirical variance table; no electronics/noise/pileup model",
              "residual_convention": RESIDUAL_CONVENTION,
              "array_coordinate_order": ["d0_mm", "z0_mm", "phi_rad", "theta_rad", "qOverP_GeV_inv"]}
    start = time.monotonic()
    try:
        ROOTmod, acts, observer, detector, geometry, native, info = prepare(args, config)
        report["preparation"] = info
        report["prepare_seconds"] = time.monotonic() - start
        run_native(args, config, acts, observer, detector, geometry)
        report["native_seconds"] = time.monotonic() - start - report["prepare_seconds"]
        report["reduction"] = reduce_case(args, native["sensors"])
        names = ["particles.root", "particles_selected.root", "audit.root", "tracksummary_kf.root", "hits.root"]
        if args.write_measurements:
            names.append("measurements.root")
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
    print(json.dumps({"outcome": report["outcome"], "pitch_mm": args.pitch, "pt_GeV": args.pt,
                      "events": args.events, "wall_seconds": report["wall_seconds"],
                      "counts": report["reduction"]["counts"]}))


if __name__ == "__main__":
    main()
