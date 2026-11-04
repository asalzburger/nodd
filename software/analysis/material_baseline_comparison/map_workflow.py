#!/usr/bin/env python3
"""Map the maintained DES043 tracker and validate it with independent rays.

Run in the explicitly activated ACTS runtime. Native algorithms, count guards,
portal selection, midpoint convention and map audits stay in their maintained
implementations. This entry point binds their current geometry and outputs.
"""

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[3]
HELPERS = REPO / "software/analysis/gen3_material_mapping"
EXPECTED_PLANES = 46682
EXPECTED_VOLUMES = 120
EXPECTED_GROUPS = 54


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def identity(path, role):
    path = Path(path).resolve()
    return {"role": role, "path": str(path), "sha256": digest(path),
            "size_bytes": path.stat().st_size}


def check_current_geometry(geometry):
    checks = geometry["checks"]
    expected = {"sensitive_surfaces": EXPECTED_PLANES, "volumes": EXPECTED_VOLUMES,
                "sensor_groups": EXPECTED_GROUPS}
    if any(checks.get(k) != v for k, v in expected.items()):
        raise ValueError("Expected complete current DES043 geometry: " + str(expected))
    return expected


def verify_sidecar_evidence(report, binary_path, source_path):
    """Bind a reusable binary to source bytes from an actual prior native run."""
    files = report["provenance"]["files"]
    actual = {"sidecar": digest(binary_path), "sidecar_source": digest(source_path)}
    for role, value in actual.items():
        candidates = [item["sha256"] for item in files if item["role"] == role]
        if candidates != [value]:
            raise ValueError(f"Retained native evidence does not identify current {role}")
    return actual


def assert_same_geometry(preparation, build_dir):
    """Reject a source/build switch between export, mapping and validation."""
    for item in preparation["geometry_inputs"]:
        if digest(item["path"]) != item["sha256"]:
            raise ValueError("Geometry input changed since export: " + item["path"])
    if Path(preparation["build_dir"]).resolve() != Path(build_dir).resolve():
        raise ValueError("DD4hep build differs from the prepared geometry")


def verify_recording_report(report, preparation, events, tracks):
    """Require the finished current scan, independently of recorder source HEAD."""
    if report.get("completed") is not True:
        raise ValueError("Current recording has not completed")
    actual_events = [item["event"] for item in report.get("events", [])]
    if sorted(actual_events) != list(range(events)):
        raise ValueError("Recording event accounting is incomplete or duplicated")
    expected = {"events": events, "tracks_per_event": tracks, "seed": 228,
                "eta": [-4, 4], "eta_uniform": True, "phi_degrees": [0, 360],
                "vertex_mm": [0, 0, 0, 0], "threads": 1, "charge": 0, "pdg": 0,
                "recordElementFractions": False, "prePostStep": True,
                "recalculateTotals": True, "excludeMaterials": ["Air", "Vacuum"]}
    if any(report.get("settings", {}).get(k) != v for k, v in expected.items()):
        raise ValueError("Recording settings differ from the common training contract")
    inputs = {item["role"]: item for item in preparation["geometry_inputs"]
              if item["role"] != "factory"}
    if (report.get("compact_sha256") != inputs["tracker.xml"]["sha256"] or
            report.get("materials_sha256") != inputs["materials.xml"]["sha256"]):
        raise ValueError("Recording compact/materials differ from the current native export")
    expected_factories = {Path(item["path"]).name: item["sha256"]
                          for item in preparation["geometry_inputs"] if item["role"] == "factory"}
    actual_factories = {Path(item["path"]).name: item["sha256"] for item in report["factories"]}
    if actual_factories != expected_factories or len(report["factories"]) != len(expected_factories):
        raise ValueError("Recording factories differ from the current native export")
    return {"geometry_identity": "PASS: compact, materials and every factory SHA256 match the current native export",
            "recording_source_revision": report["source_revision"],
            "geometry_source_revision": preparation["source_revision"],
            "events": events, "tracks_per_event": tracks, "settings": report["settings"]}


def execute(command, output_root, label):
    """Retain exact commands, status and local logs, including failed attempts."""
    start = time.monotonic()
    record = {"command": list(map(str, command)), "cwd": str(REPO)}
    stem = label
    attempt = 1
    while (output_root / (stem + ".log")).exists():
        attempt += 1
        stem = f"{label}-attempt{attempt}"
    log = output_root / (stem + ".log")
    with log.open("w") as stream:
        result = subprocess.run(record["command"], cwd=REPO, stdout=stream,
                                stderr=subprocess.STDOUT, check=False)
    record.update(exit_code=result.returncode, wall_s=time.monotonic() - start,
                  log=str(log))
    write(output_root / (stem + "-command.json"), record)
    if result.returncode:
        raise RuntimeError(f"{label} failed with exit {result.returncode}; see {log}")
    return record


def baseline_files(build):
    detector = build / "detector"
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    paths = [(detector / "tracker" / name, name) for name in
             ("tracker.xml", "materials.xml", "expected.json")]
    paths += [(detector / ("lib" + name + suffix), "factory") for name in
              ("nODDBeamPipe", "nODDPixelBarrel", "nODDShortStripBarrel",
               "nODDShortStripEndcap", "nODDLongStrip")]
    return [identity(path, role) for path, role in paths]


def prepare(args):
    output = args.output
    report_path = output / "preparation-report.json"
    if report_path.exists():
        raise FileExistsError("Preparation already completed; select a fresh output root")
    initial = baseline_files(args.build_dir)
    command = execute([sys.executable, "-B", REPO / "tools/tracker_dd4hep/export_gen3.py",
                       "--build-dir", args.build_dir, "--output-dir", output / "geometry"],
                      output, "export")
    geometry_path = output / "geometry/geometry.json"
    geometry = read(geometry_path)
    check_current_geometry(geometry)
    selector = module(HELPERS / "select_surfaces.py", "current_portal_selector")
    config = read(args.config)
    selection = selector.select(geometry, config)
    selection["provenance"] = {
        "geometry_sha256": digest(geometry_path), "config_sha256": digest(args.config),
        "selector_sha256": digest(HELPERS / "select_surfaces.py"),
        "native_geometry_provenance": geometry["provenance"]}
    write(output / "selection.json", selection)
    report = {"schema_version": 1, "status": "PROTOTYPE", "stage": "prepared",
              "source_revision": subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
              "build_dir": str(args.build_dir), "checks": geometry["checks"],
              "geometry_inputs": initial, "selection": identity(output / "selection.json", "selection"),
              "geometry": identity(geometry_path, "native_geometry"),
              "binning_policy": identity(args.config, "mapping_config"),
              "selection_counts": selection["counts"], "command": command,
              "workflow": identity(Path(__file__), "workflow")}
    assert_same_geometry(report, args.build_dir)
    write(report_path, report)
    print(json.dumps({"stage": "prepared", **selection["counts"]}, indent=2))


def verify_native(args):
    # This helper preloads DDG4 before ROOT/ACTS and preserves the native ABI.
    sys.path.insert(0, str(HELPERS))
    import material_runtime as runtime
    ROOT, acts, sidecar = runtime.native_imports(args.native_module_dir)
    if sidecar.pybind11_internals_version != 11 or sidecar.pybind11_version != "3.0.4":
        raise ValueError("Expected the selected ACTS pybind11 3.0.4/internals11 sidecar")
    evidence = verify_sidecar_evidence(read(args.sidecar_evidence), Path(sidecar.__file__),
                                      REPO / "software/source/ActsExamples/MaterialMapping/PortalMaterial.cpp")
    report = {"ROOT": ROOT.gROOT.GetVersion(), "python": sys.version,
              "pybind11": sidecar.pybind11_version,
              "pybind11_internals_version": sidecar.pybind11_internals_version,
              "sidecar": identity(sidecar.__file__, "sidecar"),
              "source": identity(REPO / "software/source/ActsExamples/MaterialMapping/PortalMaterial.cpp", "sidecar_source"),
              "retained_evidence": identity(args.sidecar_evidence, "retained_native_run"),
              "verified_hashes": evidence}
    return ROOT, report


def common_native_args(args):
    return ["--manifest", args.output / "selection.json", "--nodd-dir", args.runtime,
            "--build-dir", args.build_dir, "--native-module-dir", args.native_module_dir]


def check_reader_partition(source_steps, zero_steps, mapped_steps, unmapped_steps):
    """Account only for the exact-zero omission made by the pinned native reader."""
    if not 0 <= zero_steps <= source_steps:
        raise ValueError("Invalid zero-length step count")
    if mapped_steps + unmapped_steps != source_steps - zero_steps:
        raise ValueError("Mapping failed to partition every nonzero recorded slab")


def reader_partition(ROOT, original, mapped, unmapped):
    """Strict per-ray closure at the actual native ROOT-reader boundary.

    ACTS355ea684 RootMaterialTrackIo::read explicitly skips s==0 at lines317–320.
    Preserve the historical raw-step guard and account for that behavior here.
    """
    import numpy as np
    import material_runtime as runtime
    columns = ("event_id", "v_px", "v_py", "v_pz", "nodd_x0", "nodd_l0",
               "nodd_steps", "nodd_zeros")

    def table(path):
        frame = runtime.root_budget_frame(ROOT, path).Define(
            "nodd_zeros", "static_cast<unsigned long long>(ROOT::VecOps::Sum(mat_step_length == 0.f))")
        arrays = frame.AsNumpy(list(columns))
        keys = np.rec.fromarrays([arrays[name] for name in columns[:4]], names=columns[:4])
        order = np.argsort(keys, kind="stable")
        keys = keys[order]
        if np.unique(keys).size != keys.size:
            raise ValueError("Duplicate event/momentum ray identity")
        return keys, {name: arrays[name][order] for name in columns[4:]}

    keys, source = table(original)
    assigned_keys, assigned = table(mapped)
    other_keys, other = table(unmapped)
    if not np.array_equal(keys, assigned_keys) or not np.array_equal(keys, other_keys):
        raise ValueError("Mapping changed individual ray identities")
    for source_n, zero_n, assigned_n, other_n in zip(
            source["nodd_steps"], source["nodd_zeros"], assigned["nodd_steps"], other["nodd_steps"]):
        check_reader_partition(int(source_n), int(zero_n), int(assigned_n), int(other_n))
    if np.any(assigned["nodd_zeros"]) or np.any(other["nodd_zeros"]):
        raise ValueError("Unexpected zero-length slabs after native reader filtering")
    result = {"tracks": int(keys.size), "step_partition": "PASS: every nonzero recorded slab partitioned per ray",
              "identity": "Exact event_id and recorded float momentum tuple; duplicate identities rejected",
              "reader_zero_length_omission": {"source_steps": int(source["nodd_steps"].sum()),
                  "exact_zero_steps": int(source["nodd_zeros"].sum()),
                  "affected_tracks": int(np.count_nonzero(source["nodd_zeros"])),
                  "mapped_steps": int(assigned["nodd_steps"].sum()),
                  "unmapped_steps": int(other["nodd_steps"].sum()),
                  "source": "ACTS355ea684 Plugins/Root/src/RootMaterialTrackIo.cpp:317–320 skips exactly s==0; raw recording unchanged"}}
    for axis in ("x0", "l0"):
        name = "nodd_" + axis
        residual = assigned[name] + other[name] - source[name]
        maximum = float(np.max(np.abs(residual), initial=0.))
        if not math.isfinite(maximum) or maximum > 1.e-10:
            raise ValueError(f"Per-ray {axis} budget does not close: {maximum}")
        result["max_absolute_" + axis + "_residual"] = maximum
    return result


def map_current(args):
    preparation = read(args.output / "preparation-report.json")
    assert_same_geometry(preparation, args.build_dir)
    if (args.output / "mapping/mapping-report.json").exists():
        raise FileExistsError("Mapping already completed; select a fresh output root")
    ROOT, native = verify_native(args)
    recording_checks = verify_recording_report(read(args.recording_report), preparation,
                                               args.events, args.tracks)
    recording = identity(args.recording, "current_recording")
    # Reuse the maintained native algorithm setup, without changing its legacy
    # main() raw-step audit. New recordings may contain exact zero-length slabs
    # which the native ROOT reader deliberately omits.
    import material_runtime as runtime
    from types import SimpleNamespace
    import acts
    import nodd_portal_material as sidecar
    native_args = SimpleNamespace(manifest=args.output / "selection.json", nodd_dir=args.runtime,
        build_dir=args.build_dir, native_module_dir=args.native_module_dir,
        input=args.recording, output=args.output / "mapping", events=args.events)
    native_args.output.mkdir(parents=True, exist_ok=True)
    manifest = runtime.load_manifest(native_args.manifest)
    start = time.monotonic()
    detector, geometry, context, surfaces, decoration = runtime.prepare_geometry(
        native_args, manifest, acts, sidecar)
    runner = module(REPO / "software/running/nodd_material_mapping.py", "current_native_mapping")
    runner.run_mapping(native_args, detector, geometry, context, surfaces, acts, sidecar)
    map_path = native_args.output / "material_map.json"
    reload_report = runtime.apply_saved_map(geometry, manifest, acts, map_path, sidecar)
    summaries = {"input": runtime.root_summary(ROOT, args.recording),
                 "mapped": runtime.root_summary(ROOT, native_args.output / "mapped.root"),
                 "unmapped": runtime.root_summary(ROOT, native_args.output / "unmapped.root")}
    closure = {axis: summaries["mapped"]["sum_" + axis] + summaries["unmapped"]["sum_" + axis]
               - summaries["input"]["sum_" + axis] for axis in ("X0", "L0")}
    if any(abs(value) > 1.e-5 * max(1., summaries["input"]["sum_" + axis]) for axis, value in closure.items()):
        raise ValueError("Global material budget does not close")
    if any(item["tracks"] != args.events * args.tracks for item in summaries.values()):
        raise ValueError("Input/mapped/unmapped outputs did not retain every ray")
    partition = reader_partition(ROOT, args.recording, native_args.output / "mapped.root",
                                 native_args.output / "unmapped.root")
    report = {"schema_version": 1, "status": "PROTOTYPE", "algorithm": "ACTS MaterialMapper + IntersectionMaterialAssigner + BinnedSurfaceMaterialAccumulator",
              "position_convention": "Native midpoint adapter; original Geant4 recording unchanged",
              "empty_bin_correction": True, "events_requested": args.events,
              "native_decoration": decoration, "serialized_reload": reload_report,
              "track_budgets": summaries, "budget_closure_absolute": closure,
              "per_track_budget_partition": partition, "wall_seconds": time.monotonic() - start,
              "provenance": runtime.provenance(native_args, sidecar, [
                  ("recording", args.recording), ("material_map", map_path),
                  ("mapped_tracks", native_args.output / "mapped.root"),
                  ("unmapped_tracks", native_args.output / "unmapped.root")])}
    runtime.write_report(native_args.output / "mapping-report.json", report)
    tracks = report["track_budgets"]["input"]["tracks"]
    if tracks != args.events * args.tracks:
        raise ValueError("Training recording track count differs from requested events × tracks")
    if report["per_track_budget_partition"]["tracks"] != tracks:
        raise ValueError("Per-ray conservation did not cover every training ray")
    assert_same_geometry(preparation, args.build_dir)
    if digest(args.recording) != recording["sha256"]:
        raise ValueError("Recording changed during material mapping")
    result = {"schema_version": 1, "status": "PROTOTYPE", "stage": "mapped",
              "preparation": identity(args.output / "preparation-report.json", "preparation"),
              "native_support": native, "recording": recording,
              "recording_checks": recording_checks,
              "training": recording_checks["settings"],
              "selection_counts": preparation["selection_counts"],
              "track_budgets": report["track_budgets"],
              "budget_closure_absolute": report["budget_closure_absolute"],
              "per_track_budget_partition": report["per_track_budget_partition"],
              "serialized_reload": report["serialized_reload"],
              "native_decoration": report["native_decoration"],
              "material_map": identity(args.output / "mapping/material_map.json", "current_material_map"),
              "legacy_provenance_note": "The reused runner records unknown historical recording revision; this workflow binds the fresh current geometry by file hashes. No old map IDs are transplanted."}
    result["recording_report"] = identity(args.recording_report, "recording_report")
    write(args.output / "current-mapping-report.json", result)
    print(json.dumps({"stage": "mapped", "tracks": tracks,
                      "closure": result["budget_closure_absolute"]}, indent=2))


def validate_current(args):
    preparation = read(args.output / "preparation-report.json")
    assert_same_geometry(preparation, args.build_dir)
    mapped = read(args.output / "current-mapping-report.json")
    map_path = args.output / "mapping/material_map.json"
    if digest(map_path) != mapped["material_map"]["sha256"]:
        raise ValueError("Material map changed since mapping audit")
    if (args.output / "validation/validation-report.json").exists():
        raise FileExistsError("Validation already completed; select a fresh output root")
    ROOT, native = verify_native(args)
    execute([sys.executable, "-B", REPO / "software/running/nodd_material_validation.py",
             *common_native_args(args), "--map", map_path, "--events", args.events,
             "--tracks", args.tracks, "--threads", 1, "--seed", 43,
             "--eta-range", -4, 4, "--phi-range", -math.pi, math.pi,
             "--output", args.output / "validation"], args.output, "validation")
    report = read(args.output / "validation/validation-report.json")
    if report["track_budgets"]["tracks"] != args.events * args.tracks:
        raise ValueError("Independent validation lost rays")
    # Check the promised origin from actual output rather than only gun defaults.
    frame = ROOT.RDataFrame("material_tracks", str(args.output / "validation/material_validation.root"))
    nonzero = int(frame.Filter("v_x != 0 || v_y != 0 || v_z != 0").Count().GetValue())
    if nonzero:
        raise ValueError("Validation rays did not start at the origin")
    assert_same_geometry(preparation, args.build_dir)
    result = {"schema_version": 1, "status": "PROTOTYPE", "stage": "validated",
              "preparation": identity(args.output / "preparation-report.json", "preparation"),
              "mapping": identity(args.output / "current-mapping-report.json", "mapping_report"),
              "native_support": native, "sampling": report["sampling"],
              "origin_check": {"nonzero_starting_vertices": nonzero, "status": "PASS"},
              "track_budgets": report["track_budgets"],
              "native_decoration": report["native_decoration"],
              "validation_tracks": identity(args.output / "validation/material_validation.root", "independent_validation"),
              "scope": "Independent ACTS straight-ray sampling of the current portal map, not an independent Geant4 transport sample or detector acceptance."}
    write(args.output / "current-validation-report.json", result)
    print(json.dumps({"stage": "validated", "tracks": report["track_budgets"]["tracks"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "map", "validate"))
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True,
                        help="Checkout supplying the verified installed ACTS adapter")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=HELPERS / "mapping_config.json")
    parser.add_argument("--native-module-dir", type=Path)
    parser.add_argument("--sidecar-evidence", type=Path,
                        help="Prior actual native run report identifying the reusable binary and source hashes")
    parser.add_argument("--recording", type=Path)
    parser.add_argument("--recording-report", type=Path)
    parser.add_argument("--events", type=int, default=1000)
    parser.add_argument("--tracks", type=int, default=100)
    args = parser.parse_args()
    if args.events <= 0 or args.tracks <= 0:
        parser.error("Events and tracks must be positive")
    if args.stage != "prepare" and (not args.native_module_dir or not args.sidecar_evidence):
        parser.error("Map/validate require native-module-dir and matching sidecar-evidence")
    if args.stage == "map" and (not args.recording or not args.recording_report):
        parser.error("Mapping requires a completed current recording and its run report")
    for key in ("build_dir", "runtime", "output", "config", "native_module_dir",
                "sidecar_evidence", "recording", "recording_report"):
        value = getattr(args, key)
        if value is not None:
            setattr(args, key, value.expanduser().resolve())
    args.output.mkdir(parents=True, exist_ok=True)
    {"prepare": prepare, "map": map_current, "validate": validate_current}[args.stage](args)


if __name__ == "__main__":
    main()
