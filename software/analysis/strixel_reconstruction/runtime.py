#!/usr/bin/env python3
"""DES042 PROTOTYPE: compose frozen DES041 helpers without changing their files."""
import argparse
import copy
import gzip
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
INPUT_REVISION = "4ea4af17727020bac2ba8f5e2f6172378711c15a"
PROFILE = "pt4-nominal-triplet"
PITCHES = (0.5, 1., 1.5, 2.)
PTS = (1., 5., 10., 100.)
POPULATIONS = (("fatras", "muon", 123042), ("fatras", "electron", 133042),
               ("geant4", "muon", 143042), ("geant4", "electron", 143042),
               ("geant4", "pion", 143042))
FROZEN = ("software/running/nodd_tracker_reconstruction.py",
          "software/running/nodd_tracker_safe_fatras.py",
          *("software/analysis/tracker_reconstruction/" + name for name in
            ("prepare.py", "gbts.py", "species.py", "transport.py", "analyze.py",
             "campaign.json", "electron_campaign.json", "geant4_campaign.json")))
BASELINE_FILES = ("selection.json", "material-map.json", "error-table.json", "digitization.json")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def case_id(simulation, particle, pt, pitch):
    return f"{simulation}-{particle}-pt{pt:g}-pitch{pitch:g}"


def cases(events=1000):
    if type(events) is not int or events <= 0:
        raise ValueError("Require positive integer events")
    return [{"case_id": case_id(sim, particle, pt, pitch), "simulation": sim,
             "particle": particle, "pt_GeV": pt, "pitch_mm": pitch,
             "events": events, "seed": seed}
            for sim, particle, seed in POPULATIONS for pt in PTS for pitch in PITCHES]


def configuration(case):
    """Keep the converged species protocol and exact selected profile for all cases."""
    filename = "geant4_campaign.json" if case["simulation"] == "geant4" else "electron_campaign.json"
    path = ROOT / "software/analysis/tracker_reconstruction" / filename
    config = json.loads(path.read_text())
    config.update(particle=case["particle"], simulation=case["simulation"])
    if config["selected_profile"] != PROFILE or config["ambiguity"] != {
            "maximum_shared_hits": 3, "maximum_iterations": 4294967295}:
        raise ValueError("Frozen profile or converged ambiguity contract changed")
    config["strixel_crosscheck"] = {"pitch_mm": case["pitch_mm"], "baseline_pitch_mm": 0.5,
        "response": "Only systems4/5 local-v Gaussian sigma scales by pitch/0.5; doMerge=False",
        "input_revision": INPUT_REVISION, "events": case["events"], "seed": case["seed"]}
    return config, path


def verify_frozen(root=ROOT):
    result = {}
    for name in FROZEN:
        expected = subprocess.check_output(["git", "show", INPUT_REVISION + ":" + name], cwd=root)
        actual = sha256(root / name)
        if hashlib.sha256(expected).hexdigest() != actual:
            raise RuntimeError("Frozen input changed: " + name)
        result[str((root / name).resolve())] = actual
    return result


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def compose(supplier):
    """Only newly loaded module objects receive adapted ROOT/dependency globals."""
    running = ROOT / "software/running"
    analysis = ROOT / "software/analysis"
    for directory in (running, analysis / "tracker_reconstruction", analysis / "gen3_material_mapping",
                      analysis / "truth_tracking", analysis / "tracker_optimization"):
        sys.path.insert(0, str(directory))
    runner = load_module("_des042_frozen_runner", running / "nodd_tracker_reconstruction.py")
    preparation = load_module("_des042_frozen_prepare", analysis / "tracker_reconstruction/prepare.py")
    seeder = load_module("_des042_frozen_gbts", analysis / "tracker_reconstruction/gbts.py")
    for module in (runner, preparation, seeder):
        module.ROOT = supplier
    runner.gbts = seeder
    # SafeFatras imports the runner by its original name; give it this isolated
    # object only for the import, then restore the process's import table.
    previous = sys.modules.get("nodd_tracker_reconstruction")
    sys.modules["nodd_tracker_reconstruction"] = runner
    try:
        safe = load_module("_des042_frozen_safe_fatras", running / "nodd_tracker_safe_fatras.py")
    finally:
        if previous is None:
            sys.modules.pop("nodd_tracker_reconstruction", None)
        else:
            sys.modules["nodd_tracker_reconstruction"] = previous
    analyzer = load_module("_des042_frozen_classifier", analysis / "tracker_reconstruction/analyze.py")
    return runner, preparation, safe, analyzer


def scale_widths(table, sensors, pitch):
    """Return a copy: native ACTS volume identity is derived from physical system."""
    if pitch not in PITCHES:
        raise ValueError("Unsupported longitudinal strixel pitch")
    systems = {}
    for sensor in sensors:
        volume = (sensor["geometry_id"] >> 56) & 255
        system = sensor["ids"]["system"]
        if volume in systems and systems[volume] != system:
            raise ValueError("ACTS volume maps to more than one physical system")
        systems[volume] = system
    result = copy.deepcopy(table)
    scaled = []
    for group in result["groups"]:
        if group["volume"] not in systems:
            raise ValueError("Pooled width has no native sensor volume")
        if systems[group["volume"]] in (4, 5) and group["index"] == 1:
            group["sigma_mm"] *= pitch / 0.5
            scaled.append(group["volume"])
    if not scaled:
        raise ValueError("No strixel local-v groups found")
    return result, sorted(scaled)


def baseline_gate(directory, supplier):
    previous = supplier / "build/tracker-resolution-optimization/confirmation/gaussian/balanced-pt10"
    result = {}
    def equal(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
        if isinstance(a, list) and isinstance(b, list):
            return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
        if isinstance(a, float) and isinstance(b, float):
            return abs(a - b) < 1.e-9
        return a == b
    for name in BASELINE_FILES:
        reference = previous / name
        if not reference.is_file():
            raise RuntimeError("Required frozen confirmation unavailable: " + str(reference))
        current, frozen = json.loads((directory / name).read_text()), json.loads(reference.read_text())
        matched = equal(current, frozen) if name == "selection.json" else current == frozen
        result[name] = {"matched": matched, "reference": str(reference), "reference_sha256": sha256(reference),
                        "prepared_sha256": sha256(directory / name),
                        "comparison": "geometry tolerance 1e-9 mm" if name == "selection.json" else "exact parsed JSON"}
        if not matched:
            raise RuntimeError("Prepared baseline differs before scaling: " + name)
    return result


class _Proxy:
    def __init__(self, target, **overrides):
        self._target, self._overrides = target, overrides

    def __getattr__(self, name):
        return self._overrides[name] if name in self._overrides else getattr(self._target, name)


def append_hit_writer(acts, output):
    """Append after every frozen algorithm, so no existing random stream slot moves."""
    from acts.examples.root import RootSimHitWriter
    def sequencer(**kwargs):
        sequence = acts.examples.Sequencer(**kwargs)
        def run():
            sequence.addWriter(RootSimHitWriter(level=acts.logging.WARNING,
                inputSimHits="simhits", filePath=str(output / "hits.root"), treeName="hits"))
            return sequence.run()
        return _Proxy(sequence, run=run)
    return _Proxy(acts, examples=_Proxy(acts.examples, Sequencer=sequencer))


def source_fingerprints(supplier):
    result = verify_frozen()
    directories = ("software/analysis/gen3_material_mapping", "software/analysis/truth_tracking",
                   "software/analysis/tracker_optimization", "software/source/ActsExamples/TrackerGbts",
                   "software/source/ActsExamples/TrackerReconstruction", "software/source/ActsExamples/SafeFatras")
    for root in (ROOT, supplier):
        for directory in directories:
            for path in (root / directory).rglob("*"):
                if path.is_file() and (path.suffix in (".py", ".hpp", ".cpp", ".json") or path.name == "CMakeLists.txt"):
                    result[str(path.resolve())] = sha256(path)
    for path in (Path(__file__), Path(__file__).with_name("campaign.py"), ROOT / "software/env/truth_tracking.sh"):
        result[str(path.resolve())] = sha256(path)
    return result


def supplier_fingerprints(supplier, runtime):
    paths = []
    for directory in ("gen3-material-map-run/native", "truth-tracking-baseline/native",
                      "tracker-resolution-optimization/native", "tracker-reconstruction/native-audit",
                      "tracker-reconstruction/native-gbts", "tracker-reconstruction-species/native-safe-fatras"):
        modules = sorted((supplier / "build" / directory).glob("*.so"))
        if not modules:
            raise RuntimeError("Native supplier unavailable: " + directory)
        paths.extend(modules)
        paths.extend((supplier / "build" / directory).glob("CMakeCache.txt"))
    paths.extend((supplier / "build/balanced-baseline/dd4hep/detector").rglob("*.xml"))
    paths.extend((supplier / "build/balanced-baseline/dd4hep/detector").rglob("*.dylib"))
    paths.extend((runtime / "build/acts/lib").glob("libActs*.dylib"))
    paths.extend((runtime / "build/acts/Examples/Detectors/DD4hepDetector").glob("*.dylib"))
    paths.extend((runtime / "build/acts/python").rglob("*.so"))
    for name in ("docs/validation/gen3-material-map-run/selection.json",
                 "docs/validation/gen3-material-map-run/material_map.json.gz",
                 "docs/validation/truth-tracking-baseline/smearing/pooled-widths.json",
                 "docs/validation/gen3-material-mapping/geometry-summary.json",
                 "software/analysis/tracker_optimization/variants/balanced.json"):
        paths.append(supplier / name)
    for name in BASELINE_FILES:
        paths.append(supplier / "build/tracker-resolution-optimization/confirmation/gaussian/balanced-pt10" / name)
    return {str(p.resolve()): sha256(p) for p in sorted(set(paths))}


def check_digests(mapping, label):
    for name, digest in mapping.items():
        if not Path(name).is_file() or sha256(name) != digest:
            raise RuntimeError(label + " changed: " + name)


def audit_events(path, native, config, analyzer, count, identity):
    sensors = {s["geometry_id"]: (s["ids"]["system"], s["ids"]["layer"]) for s in native["sensors"]}
    seen, maximum, ckf_candidates = set(), 0, 0
    with gzip.open(path, "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["event"] in seen:
                raise RuntimeError("Duplicate event in all-event audit")
            seen.add(row["event"])
            analyzer.species.audit_event(row, identity)
            analyzer.classify_event(row, sensors, config)
            shared = analyzer.ambiguity_shared_max(row["ambi"])
            maximum = max(maximum, shared)
            ckf_candidates = max(ckf_candidates, len(row["ckf"]))
            if shared >= config["ambiguity"]["maximum_shared_hits"]:
                raise RuntimeError("Unconverged native ambiguity survivors")
            if row.get("ckf_input_measurements", len(row["measurements"])) != len(row["measurements"]):
                raise RuntimeError("CKF measurement subset is incomplete")
            if any(sensors[m["geometry_id"]][0] > 3 for point in row["spacepoints"]
                   for index in point["measurements"] for m in [row["measurements"][index]]):
                raise RuntimeError("Nonpixel spacepoint reached GBTS")
    if seen != set(range(count)):
        raise RuntimeError("All-generated event audit is incomplete")
    return {"events": count, "all_generated_events_retained": True,
            "all_native_survivors_converged": True, "maximum_shared_measurements": maximum,
            "maximum_raw_ckf_candidates": ckf_candidates,
            "old_1000_budget_provably_nonlimiting": ckf_candidates <= 1000,
            "old_budget_test": "Each iteration removes one candidate or stops; <=1000 raw candidates is sufficient"}


def execute(case, output, supplier, runtime, write_root=False):
    if output.exists() and any(output.iterdir()):
        raise ValueError("Choose a fresh empty case directory; no native output is overwritten")
    output.mkdir(parents=True, exist_ok=True)
    config, campaign_path = configuration(case)
    start = time.monotonic()
    report = {"schema_version": 1, "status": "PROTOTYPE", "outcome": "started",
        **case, "profile": PROFILE, "phase": "validation", "command": sys.argv,
        "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "input_revision": INPUT_REVISION, "campaign": config, "campaign_sha256": sha256(campaign_path),
        "supplier_identity": {"native_build_root": str(supplier), "runtime_root": str(runtime)},
        "python": sys.version, "platform": platform.platform()}
    write_json(output / "run-report.json", report)
    try:
        report["source_sha256"] = source_fingerprints(supplier)
        report["supplier_sha256"] = supplier_fingerprints(supplier, runtime)
        runner, preparation, safe, analyzer = compose(supplier)
        args = SimpleNamespace(output=output, pt=case["pt_GeV"], events=case["events"], threads=1,
            seed=case["seed"], profile=PROFILE, phase="validation", write_root=write_root)
        rootmod, acts, observer, detector, geometry, native, info = preparation.prepare(args)
        binding = Path(importlib.import_module("acts.examples.ActsExamplesPythonBindings").__file__).resolve()
        if not binding.is_relative_to(runtime / "build/acts"):
            raise RuntimeError("Imported ACTS binding is outside the explicit runtime supplier")
        report["root_version"] = rootmod.gROOT.GetVersion()
        report["acts_binding"] = str(binding)
        report["preparation"] = info
        report["baseline_equivalence"] = baseline_gate(output, supplier)
        report["baseline_input_sha256"] = {name: sha256(output / name) for name in BASELINE_FILES}
        baseline_widths = json.loads((output / "error-table.json").read_text())
        write_json(output / "baseline-error-table.json", baseline_widths)
        widths, volumes = scale_widths(baseline_widths, native["sensors"], case["pitch_mm"])
        write_json(output / "error-table.json", widths)
        settings = {"model": "gaussian_smearing", "merge": False,
                    "measured_coordinates_by_system": runner.smearing.COORDINATES}
        digi, counts = runner.smearing.build_config(native["sensors"], settings, widths)
        write_json(output / "digitization.json", digi)
        report["response_scaling"] = {"pitch_mm": case["pitch_mm"], "baseline_pitch_mm": 0.5,
            "factor_sigma_v": case["pitch_mm"] / 0.5, "systems": [4, 5], "volumes": volumes,
            "coordinate": 1, "unchanged_fine_coordinate": True, "doMerge": False, "sensor_counts": counts}
        report["gbts_preparation"] = runner.gbts.prepare(native, output / "gbts", config["profiles"][PROFILE])
        if case["simulation"] == "fatras" and case["particle"] == "electron":
            runner.transport = SimpleNamespace(schedule=safe.schedule)
        libraries = dict(report["supplier_sha256"])
        if case["simulation"] == "geant4":
            program = shutil.which("geant4-config")
            if program is None:
                raise RuntimeError("Geant4 CLI identity unavailable")
            libraries.update({str(p.resolve()): sha256(p) for p in
                (Path(program).resolve().parents[1] / "lib").glob("libG4*.dylib")})
        libraries[str(binding)] = sha256(binding)
        report["runtime_sha256"] = libraries
        write_json(output / "campaign.json", config)
        report["prepared_input_sha256"] = {str(p.relative_to(output)): sha256(p)
            for p in output.rglob("*") if p.is_file() and p.name != "run-report.json"}
        write_json(output / "run-report.json", report)
        report["gbts_statistics"] = runner.run(args, config, append_hit_writer(acts, output), detector, geometry, observer)
        for name, digest in report["prepared_input_sha256"].items():
            if sha256(output / name) != digest:
                raise RuntimeError("Prepared scientific input changed during execution: " + name)
        with (output / "events.jsonl").open("rb") as source, gzip.GzipFile(
                filename=str(output / "events.jsonl.gz"), mode="wb", mtime=0) as target:
            shutil.copyfileobj(source, target)
        (output / "events.jsonl").unlink()
        report["event_audit"] = audit_events(output / "events.jsonl.gz", native, config, analyzer,
            case["events"], report["gbts_statistics"]["particle_configuration"])
        check_digests(report["source_sha256"], "Frozen or executing source")
        check_digests(report["runtime_sha256"], "Native supplier/runtime")
        report["postrun_immutability"] = {"source": True, "native_supplier_runtime": True, "prepared_inputs": True}
        report["hit_retention"] = {"file": "hits.root", "tree": "hits",
            "writer_position": "Appended after frozen audit; all prior algorithm RNG slots unchanged",
            "purpose": "Full simulated-hit payload for independent exact per-event transport fingerprints"}
        report["output_sha256"] = {str(p.relative_to(output)): sha256(p)
            for p in output.rglob("*") if p.is_file() and p.name != "run-report.json"}
        report["outcome"] = "completed"
    except BaseException as error:
        report.update(outcome="failed", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        report["wall_seconds"] = time.monotonic() - start
        write_json(output / "run-report.json", report)
    print(json.dumps({"case_id": case["case_id"], "outcome": report["outcome"],
                      "wall_seconds": report["wall_seconds"]}), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, choices=[c["case_id"] for c in cases()])
    parser.add_argument("--events", type=int, default=1000)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--supplier-root", type=Path, default=ROOT.parent / "nodd-gen3-material-mapping")
    parser.add_argument("--runtime-root", type=Path, default=ROOT.parent / "nodd-software-layout")
    parser.add_argument("--write-root", action="store_true", help="Also retain CKF/ambiguity and measurement ROOT summaries")
    args = parser.parse_args()
    try:
        case = next(c for c in cases(args.events) if c["case_id"] == args.case)
        execute(case, args.output.resolve(), args.supplier_root.resolve(), args.runtime_root.resolve(), args.write_root)
    except (ValueError, RuntimeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
