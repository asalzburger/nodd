#!/usr/bin/env python3
"""DES042 PROTOTYPE: paired ttbar+200PU generation/Fatras and four GBTS replays."""
import argparse
import copy
from contextlib import contextmanager
import ctypes
import gzip
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import re
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
INPUT_REVISION = "a734cf0d718846af84f919575725b9c7f0eee731"
PITCHES = (0.5, 1., 1.5, 2.)
PROFILE = "pt4-nominal-triplet"
SAMPLE_SCHEMA = 1
UPSTREAM_PYTHIA_SHA256 = "9604bce7ab12e252d712470982148b8ddb1fade5998262f53c92023855798c51"
FATRAS_SOURCE_NAMES = ("CMakeLists.txt", "Binding.cpp", "TtbarSafeBetheHeitler.hpp",
                       "FailureAudit.hpp", "test_energy_loss.cpp", "test_failure_identity.cpp")
PYTHIA_OLD = "m_pythia8->next();"
PYTHIA_NEW = "noddRequirePythiaSuccess(m_pythia8->next());"


def load_base():
    path = ROOT / "software/analysis/strixel_reconstruction/runtime.py"
    spec = importlib.util.spec_from_file_location("_ttbar_frozen_composition", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base()
sha256, canonical, write_json = base.sha256, base.canonical, base.write_json


def campaign(events, seed, pitch=0.5):
    c, _ = base.configuration(dict(simulation="fatras", particle="muon", pt_GeV=1.,
                                    pitch_mm=pitch, events=events, seed=seed))
    c["ttbar_pileup"] = dict(input_revision=INPUT_REVISION, hard_scatter=1, pileup=200,
        hard_process=["Top:qqbar2ttbar=on"], pileup_process=["SoftQCD:all=on"],
        pdg_beams=[2212, 2212], cms_energy_GeV=14000., initialization_seed=42,
        vertex_mean_mm_ct=[0., 0., 0., 0.], vertex_sigma_mm=[0.0125, 0.0125, 55.5],
        vertex_sigma_time_ns=5., generator_selection=dict(rho_max_mm=24., abs_z_max_mm=1000.,
            eta_min=-3., eta_max=3., pt_min_GeV=0.15), fatras_p_min_GeV=0.5,
        reconstruction_hypothesis="muon", no_truth_filter_on_ckf=True,
        sample_replay="Lossless full native binary64 decimal JSON; every restored field reserialized and compared",
        digitization_seed=seed, events=events, seed=seed, pitch_mm=pitch)
    # The collision guide selects vertices over this region. Adapt the common
    # seeder window before validation, preserving every other profile/fit cut.
    zmax = c["ttbar_pileup"]["generator_selection"]["abs_z_max_mm"]
    profile = c["profiles"][PROFILE]
    profile["z0_range_mm"] = [-zmax, zmax]
    profile.setdefault("seed_finder", {}).update(minZ0=-zmax, maxZ0=zmax)
    profile.setdefault("tracking_filter", {})["maxZ0"] = zmax
    c["ttbar_pileup"]["gbts_z0_range_mm"] = [-zmax, zmax]
    c["ttbar_pileup"]["gbts_window_rationale"] = "Common guide-selected vertex-z region; pre-production scenario adaptation"
    c["strixel_crosscheck"]["input_revision"] = INPUT_REVISION
    return c


def check_fresh(path):
    if path.exists() and any(path.iterdir()):
        raise ValueError("Choose a fresh empty output directory; partial evidence is retained")
    path.mkdir(parents=True, exist_ok=True)


def check_disk(path):
    if shutil.disk_usage(path).free < 2 * 1024**3:
        raise RuntimeError("Less than 2 GiB available; partial evidence retained")


def fingerprints(supplier, runtime, native_dir, fatras_native_dir=None, gbts_native_dir=None):
    fatras_native_dir = fatras_native_dir or ROOT / "build/strixel-ttbar-safe-fatras"
    source = base.source_fingerprints(supplier)
    for p in (Path(__file__), Path(__file__).with_name("campaign.py")):
        if p.is_file():
            source[str(p.resolve())] = sha256(p)
    for p in (ROOT / "software/source/ActsExamples/StrixelPileup").iterdir():
        if p.is_file():
            source[str(p.resolve())] = sha256(p)
    for name in FATRAS_SOURCE_NAMES:
        path = ROOT / "software/source/ActsExamples/StrixelPileupSafeFatras" / name
        if not path.is_file():
            raise RuntimeError("Task-owned Fatras source is missing: " + name)
        source[str(path.resolve())] = sha256(path)
    native = base.supplier_fingerprints(supplier, runtime)
    native.update(fatras_native_fingerprints(fatras_native_dir, runtime))
    if gbts_native_dir is not None:
        for path in (ROOT / "software/source/ActsExamples/StrixelPileupSafeGbts").iterdir():
            if path.is_file():
                source[str(path.resolve())] = sha256(path)
        native.update(gbts_native_fingerprints(gbts_native_dir, runtime))
    for p in [*native_dir.glob("*.so"), native_dir / "CMakeCache.txt", native_dir / "build.ninja",
              native_dir / "GuardedPythia8ProcessGenerator.cpp", native_dir / "PythiaGenerationGuard.hpp",
              native_dir / "PythiaGuardProvenance.hpp"]:
        if not p.is_file():
            raise RuntimeError("Task-owned native sidecar is missing")
        native[str(p.resolve())] = sha256(p)
    cache = (native_dir / "CMakeCache.txt").read_text()
    for key in ("PYTHIA8_LIBRARY", "PYTHIA8_INCLUDE_DIR"):
        line = next((s.split("=", 1)[1] for s in cache.splitlines() if s.startswith(key + ":")), None)
        if not line:
            raise RuntimeError("Missing native dependency identity: " + key)
        path = Path(line)
        if path.is_file():
            native[str(path.resolve())] = sha256(path)
            # Bind the actual preinstalled generator data, not merely its headers.
            data = path.resolve().parents[1] / "share/Pythia8/xmldoc"
            if key == "PYTHIA8_LIBRARY":
                if not data.is_dir():
                    raise RuntimeError("Pythia XML data directory is unavailable")
                for xml in sorted(data.rglob("*.xml")):
                    native[str(xml.resolve())] = sha256(xml)
        else:
            for p in sorted(path.rglob("*.h")):
                native[str(p)] = sha256(p)
    # Native imported dependency locations are resolved through the already
    # configured package prefixes; the shared installation is never changed.
    for entry in cache.splitlines():
        if entry.startswith("HepMC3_DIR:") or entry.startswith("ZLIB_LIBRARY_RELEASE:"):
            value = Path(entry.split("=", 1)[1])
            candidates = [value] if value.is_file() else list(value.parents[2].glob("lib/libHepMC3*.dylib"))
            for dependency in candidates:
                if dependency.is_file():
                    native[str(dependency.resolve())] = sha256(dependency)
    acts_source = runtime / "software/submodules/acts"
    for name in ("Examples/Algorithms/GeneratorsPythia8/ActsExamples/Generators/Pythia8ProcessGenerator.cpp",
                 "Examples/Algorithms/GeneratorsPythia8/ActsExamples/Generators/Pythia8ProcessGenerator.hpp",
                 "Examples/Algorithms/Generators/ActsExamples/Generators/EventGenerator.cpp",
                 "Examples/Io/HepMC3/src/HepMC3InputConverter.cpp", "Examples/Io/HepMC3/src/HepMC3Util.cpp",
                 "Fatras/include/ActsFatras/EventData/Particle.hpp", "Fatras/include/ActsFatras/EventData/Hit.hpp"):
        p = acts_source / name
        source[str(p.resolve())] = sha256(p)
    return source, native


def fatras_native_fingerprints(directory, runtime):
    required = [directory / "CMakeCache.txt", directory / "build.ninja", directory / "generated/SafeFatrasProvenance.hpp"]
    modules = list(directory.glob("nodd_ttbar_safe_fatras*.so"))
    generated = [p for p in (directory / "generated").rglob("*") if p.is_file()]
    if len(modules) != 1 or len(generated) < 5 or not all(p.is_file() for p in required):
        raise RuntimeError("Isolated ttbar Fatras build is incomplete")
    paths = [*required, *modules, *generated]
    cache = (directory / "CMakeCache.txt").read_text()
    compiler = next((line.split("=", 1)[1] for line in cache.splitlines() if line.startswith("CMAKE_CXX_COMPILER:FILEPATH=")), None)
    if not compiler or not Path(compiler).is_file():
        raise RuntimeError("Isolated Fatras compiler identity is missing")
    paths.extend([Path(compiler), runtime / "build/acts/build.ninja", runtime / "build/acts/CMakeCache.txt"])
    for name in ("Examples/Algorithms/Fatras/include/ActsExamples/Fatras/FatrasSimulation.hpp",
                 "Examples/Algorithms/Fatras/src/FatrasSimulation.cpp",
                 "Fatras/include/ActsFatras/Physics/ElectroMagnetic/BetheHeitler.hpp",
                 "Fatras/include/ActsFatras/Physics/StandardInteractions.hpp", "Fatras/src/Physics/StandardInteractions.cpp",
                 "Fatras/include/ActsFatras/Utilities/detail/FpeSafeGammaDistribution.hpp",
                 "Fatras/include/ActsFatras/Kernel/MultiParticleSimulation.hpp"):
        paths.append(runtime / "software/submodules/acts" / name)
    return {str(p.resolve()): sha256(p) for p in sorted(set(paths))}


def gbts_native_fingerprints(directory, runtime):
    required = [directory / "CMakeCache.txt", directory / "build.ninja",
                directory / "generated/provenance.json", directory / "generated/GbtsProvenance.hpp"]
    modules = list(directory.glob("nodd_ttbar_gbts.*.so"))
    generated = [path for path in (directory / "generated").rglob("*") if path.is_file()]
    if len(modules) != 1 or not generated or not all(path.is_file() for path in required):
        raise RuntimeError("Isolated ttbar GBTS build is incomplete")
    provenance = json.loads((directory / "generated/provenance.json").read_text())
    paths = [*required, *modules, *generated,
             runtime / "build/acts/CMakeCache.txt", runtime / "build/acts/build.ninja",
             runtime / "build/acts/lib/libActsPluginFpeMonitoring.dylib"]
    paths += [runtime / "software/submodules/acts" / name for name in provenance["upstream_sha256"]]
    cache = (directory / "CMakeCache.txt").read_text()
    compiler = next((line.split("=", 1)[1] for line in cache.splitlines()
                     if line.startswith("CMAKE_CXX_COMPILER:FILEPATH=")), None)
    if not compiler or not Path(compiler).is_file():
        raise RuntimeError("Isolated GBTS compiler identity is missing")
    paths.append(Path(compiler))
    return {str(path.resolve()): sha256(path) for path in sorted(set(paths))}


def verify_gbts_module(module, directory, runtime):
    if Path(module.__file__).resolve().parent != directory.resolve():
        raise RuntimeError("Isolated ttbar GBTS module imported from unexpected location")
    provenance = json.loads(module.provenance_json())
    if json.loads((directory / "generated/provenance.json").read_text()) != provenance:
        raise RuntimeError("Compiled GBTS provenance differs from its build record")
    if (provenance["acts_revision"] != "355ea68493b326956756c9386d2fd9eaf9328568" or
            provenance.get("numerical_policy") != "select_denominator_before_division"):
        raise RuntimeError("Unexpected GBTS numerical implementation")
    for name, digest in provenance["upstream_sha256"].items():
        if sha256(runtime / "software/submodules/acts" / name) != digest:
            raise RuntimeError("Compiled GBTS upstream source changed: " + name)
    for name, digest in provenance["generated_sha256"].items():
        if sha256(directory / "generated" / name) != digest:
            raise RuntimeError("Compiled GBTS generated input changed: " + name)
    own = ROOT / "software/source/ActsExamples/StrixelPileupSafeGbts"
    local = {path.name: sha256(path) for path in own.iterdir() if path.is_file()}
    if provenance["local_source_sha256"] != local:
        raise RuntimeError("Compiled GBTS local source changed without rebuild")
    for key, name in (("compiler_cache_sha256", "CMakeCache.txt"), ("native_build_ninja_sha256", "build.ninja")):
        if sha256(runtime / "build/acts" / name) != provenance[key]:
            raise RuntimeError("Native GBTS build configuration changed: " + name)
    if module.pybind11_version != "3.0.4" or module.pybind11_internals_version != 11:
        raise RuntimeError("GBTS Python binding ABI differs")
    return {"module": str(Path(module.__file__).resolve()), "module_sha256": sha256(module.__file__),
            "provenance": provenance, "pybind11_version": module.pybind11_version,
            "pybind11_internals_version": module.pybind11_internals_version}


def failure_audit_summary(audit, events, complete=False):
    rows = audit["events"]
    indices = [row["event"] for row in rows]
    if len(set(indices)) != len(indices) or any(type(i) is not int or not 0 <= i < events for i in indices):
        raise RuntimeError("Duplicate or invalid event in native transport failure audit")
    if complete and set(indices) != set(range(events)):
        raise RuntimeError("Isolated Fatras failure-audit event coverage is incomplete")
    for row in rows:
        for failure in row["failures"]:
            if len(failure["initial_state"]["id"]) != 5 or type(failure["error_value"]) is not int:
                raise RuntimeError("Incomplete native failed-particle identity/error record")
    return dict(events=len(rows), failed_particles=sum(len(row["failures"]) for row in rows))


def verify_fatras_module(module, directory, runtime):
    if Path(module.__file__).resolve().parent != directory.resolve():
        raise RuntimeError("Isolated ttbar Fatras module imported from unexpected location")
    for name, digest in dict(module.upstream_sha256).items():
        if sha256(runtime / "software/submodules/acts" / name) != digest:
            raise RuntimeError("Compiled Fatras upstream source changed: " + name)
    for name, digest in dict(module.generated_sha256).items():
        if sha256(directory / "generated" / name) != digest:
            raise RuntimeError("Compiled Fatras generated input changed: " + name)
    local = dict(module.local_source_sha256)
    if set(local) != set(FATRAS_SOURCE_NAMES):
        raise RuntimeError("Compiled Fatras local source inventory is incomplete")
    for name, digest in local.items():
        if sha256(ROOT / "software/source/ActsExamples/StrixelPileupSafeFatras" / name) != digest:
            raise RuntimeError("Compiled Fatras local source changed without rebuild: " + name)
    return dict(module=str(Path(module.__file__).resolve()), module_sha256=sha256(module.__file__),
        upstream_sha256=dict(module.upstream_sha256), generated_sha256=dict(module.generated_sha256),
        local_source_sha256=local,
        native_compile_flags=module.native_compile_flags, native_compile_defines=module.native_compile_defines,
        native_flag_block_sha256=module.native_flag_block_sha256,
        pybind11_version=module.pybind11_version, pybind11_internals_version=module.pybind11_internals_version)


def pythia_data_directory(native_dir):
    cache = (native_dir / "CMakeCache.txt").read_text()
    line = next((s.split("=", 1)[1] for s in cache.splitlines() if s.startswith("PYTHIA8_LIBRARY:")), None)
    if not line:
        raise RuntimeError("Pythia library identity is missing from native build")
    data = Path(line).resolve().parents[1] / "share/Pythia8/xmldoc"
    if not data.is_dir():
        raise RuntimeError("Explicit installed Pythia XML data is unavailable")
    return data


def run_sequence(sequence, output):
    start = time.monotonic()
    try:
        sequence.run()
    except BaseException:
        write_json(output / "native-fpe-diagnostic.json", dict(native_fpe_result=str(sequence.fpeResult)))
        raise
    return time.monotonic() - start


@contextmanager
def native_log(path):
    """Capture native fd1/fd2 locally; restore both even when execution fails."""
    flush = ctypes.CDLL(None).fflush
    flush.argtypes = [ctypes.c_void_p]
    sys.stdout.flush(); sys.stderr.flush(); flush(None)
    saved = [os.dup(1), os.dup(2)]
    try:
        with Path(path).open("xb") as stream:
            os.dup2(stream.fileno(), 1); os.dup2(stream.fileno(), 2)
            try:
                yield
            finally:
                sys.stdout.flush(); sys.stderr.flush(); flush(None)
    finally:
        for fd, original in zip((1, 2), saved):
            os.dup2(original, fd); os.close(original)


def graph_audit(path, events, cap):
    """Join single-thread sequencer event boundaries to native graph diagnostics."""
    current, records = None, {}
    for line in Path(path).read_text().splitlines():
        begin = re.search(r"start processing event (\d+) on thread", line)
        if begin:
            event = int(begin[1])
            if current is not None or event in records:
                raise RuntimeError("Overlapping or duplicate graph event boundary")
            current = {"event": event, "warning_count": 0}
        graph = re.search(r"Created graph with (\d+) edges and (\d+) edge links", line)
        if graph:
            if current is None or "edges" in current:
                raise RuntimeError("Missing or duplicate graph event identity")
            current.update(edges=int(graph[1]), edge_links=int(graph[2]))
        warning = re.search(r"Maximum number of graph edges exceeded.*?(\d+)\s*$", line)
        if warning:
            if current is None:
                raise RuntimeError("Graph warning outside an identified event")
            current["warning_count"] += 1
            current["warning_edges"] = int(warning[1])
        end = re.search(r"finished event (\d+)\s*$", line)
        if end:
            if current is None or current["event"] != int(end[1]) or "edges" not in current:
                raise RuntimeError("Incomplete graph event diagnostics")
            reached = current["edges"] >= cap
            if current["warning_count"] != int(reached) or (reached and current["warning_edges"] != current["edges"]):
                raise RuntimeError("Graph edge count and native cap warning disagree")
            current["cap_reached"] = reached
            records[current["event"]] = current
            current = None
    if current is not None or set(records) != set(range(events)):
        raise RuntimeError("Incomplete generated-event graph coverage")
    return {"edge_cap": cap, "events": [records[i] for i in range(events)],
            "cap_reached_events": sum(r["cap_reached"] for r in records.values()),
            "log_file": Path(path).name, "log_sha256": sha256(path),
            "interpretation": "Cap reached indicates possible graph truncation; output-seed capping is a separate limit"}


def pythia_generation_provenance(native_dir, runtime, sidecar):
    original = runtime / "software/submodules/acts/Examples/Algorithms/GeneratorsPythia8/ActsExamples/Generators/Pythia8ProcessGenerator.cpp"
    generated = native_dir / "GuardedPythia8ProcessGenerator.cpp"
    guard = native_dir / "PythiaGenerationGuard.hpp"
    if sha256(original) != UPSTREAM_PYTHIA_SHA256 or sidecar.pythia_original_source_sha256 != UPSTREAM_PYTHIA_SHA256:
        raise RuntimeError("Original Pythia generator source hash changed")
    source = original.read_text()
    expected = '#include "PythiaGenerationGuard.hpp"\n' + source.replace(PYTHIA_OLD, PYTHIA_NEW)
    if source.count(PYTHIA_OLD) != 1 or generated.read_text() != expected:
        raise RuntimeError("Task-owned Pythia copy differs from the single reviewed success guard patch")
    if sha256(generated) != sidecar.pythia_generated_source_sha256 or sha256(guard) != sidecar.pythia_guard_header_sha256:
        raise RuntimeError("Compiled Pythia generated-source/header identity changed")
    return dict(original_source_sha256=UPSTREAM_PYTHIA_SHA256,
        generated_source_sha256=sidecar.pythia_generated_source_sha256,
        guard_header_sha256=sidecar.pythia_guard_header_sha256,
        patch=dict(old=PYTHIA_OLD, new=PYTHIA_NEW, prepend='#include "PythiaGenerationGuard.hpp"\n'),
        policy=sidecar.pythia_generation_success_policy)


def validate_full_generated_origins(row):
    expected = set(range(201))
    if set(row["interaction_origins"]) != expected or len(row["interaction_origins"]) != 201:
        raise RuntimeError("Generated interaction inventory is not exactly 1+200")
    labels = row["labels"]
    if {label["interaction"] for label in labels} != expected:
        raise RuntimeError("Full unfiltered generated truth does not cover all 201 origins")
    generated_ids = {tuple(p["initial"]["id"]) for p in row["generated"]}
    label_ids = {tuple(label["id"]) for label in labels}
    if len(generated_ids) != len(row["generated"]) or len(label_ids) != len(labels) or generated_ids != label_ids:
        raise RuntimeError("Full generated particle-to-origin label inventory is incomplete or duplicated")


def prepared(args, supplier, runtime, native_dir):
    runner, preparation, safe, analyzer = base.compose(supplier)
    rootmod, acts, observer, detector, geometry, native, info = preparation.prepare(args)
    binding = Path(importlib.import_module("acts.examples.ActsExamplesPythonBindings").__file__).resolve()
    if not binding.is_relative_to(runtime / "build/acts"):
        raise RuntimeError("ACTS binding lies outside the explicit runtime supplier")
    previous_pythia_data = os.environ.get("PYTHIA8DATA")
    data = pythia_data_directory(native_dir)
    os.environ["PYTHIA8DATA"] = str(data)
    sys.path.insert(0, str(native_dir))
    sidecar = importlib.import_module("nodd_strixel_pileup")
    if Path(sidecar.__file__).resolve().parent != native_dir:
        raise RuntimeError("Task sidecar imported from unexpected location")
    info.update(root_version=rootmod.gROOT.GetVersion(), acts_binding=str(binding),
                sidecar=str(Path(sidecar.__file__).resolve()), pythia_version=sidecar.pythia_version,
                pythia_version_integer=sidecar.pythia_version_integer,
                pythia_fpe_scope=sidecar.upstream_pythia_fpe_scope,
                pythia_generation_provenance=pythia_generation_provenance(native_dir, runtime, sidecar),
                effective_pythia_data_directory=str(data), prior_pythia_data_environment=previous_pythia_data)
    return runner, acts, observer, detector, geometry, native, info, sidecar


def begin(kind, output, events, seed, supplier, runtime, native_dir, pitch=None, fatras_native_dir=None, gbts_native_dir=None):
    fatras_native_dir = fatras_native_dir or ROOT / "build/strixel-ttbar-safe-fatras"
    check_fresh(output)
    report = dict(schema_version=1, status="PROTOTYPE", outcome="started", kind=kind,
        events=events, seed=seed, pitch_mm=pitch, profile=PROFILE, command=sys.argv,
        source_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        input_revision=INPUT_REVISION, python=sys.version, platform=platform.platform(),
        supplier_identity=dict(native_build_root=str(supplier), runtime_root=str(runtime), native_dir=str(native_dir), fatras_native_dir=str(fatras_native_dir)))
    write_json(output / "run-report.json", report)
    try:
        if gbts_native_dir is not None:
            report["supplier_identity"]["gbts_native_dir"] = str(gbts_native_dir)
        source, native = fingerprints(supplier, runtime, native_dir, fatras_native_dir, gbts_native_dir)
        report.update(source_sha256=source, runtime_sha256=native)
    except BaseException as error:
        report.update(outcome="failed", error=f"{type(error).__name__}: {error}")
        write_json(output / "run-report.json", report)
        raise
    write_json(output / "run-report.json", report)
    return report


def finish(output, report, start):
    report["wall_seconds"] = time.monotonic() - start
    report["process_peak_rss"] = dict(value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        unit="bytes" if sys.platform == "darwin" else "KiB", scope="whole native Python process")
    write_json(output / "run-report.json", report)
    print(json.dumps(dict(kind=report["kind"], pitch_mm=report["pitch_mm"], outcome=report["outcome"],
                          wall_seconds=report["wall_seconds"])), flush=True)


def complete(output, report):
    base.check_digests(report["source_sha256"], "Executing source")
    base.check_digests(report["runtime_sha256"], "Native runtime")
    for name, digest in report["prepared_input_sha256"].items():
        if sha256(output / name) != digest:
            raise RuntimeError("Prepared input changed: " + name)
    report["postrun_immutability"] = dict(source=True, native_supplier_runtime=True, prepared_inputs=True)
    report["output_sha256"] = {str(p.relative_to(output)): sha256(p) for p in output.rglob("*")
                               if p.is_file() and p.name != "run-report.json"}
    report["outcome"] = "completed"


def generate(output, events, seed, supplier, runtime, native_dir, fatras_native_dir=None):
    fatras_native_dir = fatras_native_dir or ROOT / "build/strixel-ttbar-safe-fatras"
    start = time.monotonic()
    report = begin("generate", output, events, seed, supplier, runtime, native_dir, fatras_native_dir=fatras_native_dir)
    try:
        args = SimpleNamespace(output=output, pt=1., events=events, threads=1, seed=seed, profile=PROFILE, phase="validation")
        runner, acts, observer, detector, geometry, native, info, sidecar = prepared(args, supplier, runtime, native_dir)
        report["preparation"] = info
        report["baseline_equivalence"] = base.baseline_gate(output, supplier)
        config = campaign(events, seed)
        report["campaign"] = config
        write_json(output / "campaign.json", config)
        level, u = acts.logging.WARNING, acts.UnitConstants
        field = acts.ConstantBField(acts.Vector3(0., 0., 3. * u.T))
        rnd = acts.examples.RandomNumbers(seed=seed)
        seq = acts.examples.Sequencer(events=events, numThreads=1, outputDir=str(output), logLevel=level)
        for decorator in detector.contextDecorators():
            seq.addContextDecorator(decorator)
        vtx = acts.examples.GaussianVertexGenerator(mean=acts.Vector4(0., 0., 0., 0.),
            stddev=acts.Vector4(.0125*u.mm, .0125*u.mm, 55.5*u.mm, 5.*u.ns))
        generators = [acts.examples.EventGenerator.Generator(
            acts.examples.FixedMultiplicityGenerator(n=n), vtx, sidecar.generator(hard, level))
            for hard, n in ((True, 1), (False, 200))]
        generator = acts.examples.EventGenerator(level=level, generators=generators,
            randomNumbers=rnd, outputEvent="pythia8-event", printListing=False)
        seq.addReader(generator)
        from acts.examples.hepmc3 import HepMC3InputConverter
        seq.addAlgorithm(HepMC3InputConverter(level=level, inputEvent="pythia8-event",
            outputParticles="particles_generated_all", outputVertices="vertices_generated",
            printListing=False, checkConsistency=False, mergePrimaries=True,
            primaryVertexSpatialThreshold=1.*u.nm, vertexSpatialThreshold=1.*u.um,
            mergeSecondaries=True, searchUpToHeavyFlavourQuark=False))
        seq.addAlgorithm(acts.examples.ParticleSelector(level=level,
            inputParticles="particles_generated_all", outputParticles="particles_generated",
            rhoMin=0., rhoMax=24.*u.mm, absZMin=0., absZMax=1.*u.m,
            etaMin=-3., etaMax=3., ptMin=.15*u.GeV))
        sys.path.insert(0, str(fatras_native_dir))
        safe = importlib.import_module("nodd_ttbar_safe_fatras")
        report["isolated_fatras_provenance"] = verify_fatras_module(safe, fatras_native_dir, runtime)
        report["transport_configuration"] = dict(safe.schedule(seq, geometry, field, rnd, level))
        report["transport_configuration"].update(numerical_sidecar=str(Path(safe.__file__).resolve()),
            source_revision=safe.source_revision, upstream_sha256=dict(safe.upstream_sha256),
            generated_header_sha256=safe.generated_header_sha256, generated_source_sha256=safe.generated_source_sha256,
            input_semantics="particles_generated is explicit guide-selected subset; all truth retained as particles_generated_all")
        seq.addAlgorithm(sidecar.SampleWriter(str(output / "sample")))
        report["prepared_input_sha256"] = {str(p.relative_to(output)): sha256(p) for p in output.rglob("*")
                                            if p.is_file() and p.name != "run-report.json"}
        write_json(output / "run-report.json", report)
        try:
            report["sequencer_seconds"] = run_sequence(seq, output)
        finally:
            failures = json.loads(safe.failure_audit_json())
            write_json(output / "transport-failures.json", failures)
            report["transport_failure_audit"] = dict(file="transport-failures.json", **failure_audit_summary(failures, events),
                observation="Initial state copied before erase; no simulation/queue/RNG/cut changes")
        failure_audit_summary(failures, events, complete=True)
        event_rows = []
        for event in range(events):
            path = output / "sample" / f"event{event:06d}.json.gz"
            with gzip.open(path, "rt") as stream:
                row = json.load(stream)
            validate_full_generated_origins(row)
            if row["event"] != event or row["interaction_origins"] != list(range(201)):
                raise RuntimeError("Generated event or interaction origin inventory mismatch")
            event_rows.append(dict(event=event, file=str(path.relative_to(output)), file_sha256=sha256(path),
                sample_fingerprints={key: hashlib.sha256(canonical(row[key])).hexdigest()
                    for key in ("generated", "selected", "simulated", "hits", "labels", "primary_vertices")},
                counts={key: len(row[key]) for key in ("generated", "selected", "simulated", "hits", "primary_vertices")},
                compressed_bytes=path.stat().st_size))
        write_json(output / "sample-manifest.json", dict(schema_version=SAMPLE_SCHEMA, events=events,
            event_rows=event_rows, note="Every particle initial/final field, origin tag and hit field retained at native binary64 precision"))
        report["sample_audit"] = dict(all_events_retained=True, all_201_interactions_verified=True,
            all_201_full_unfiltered_generated_origins_verified=True,
            unsuccessful_pythia_subevent_policy="Abort whole event without retry, filtering or resampling",
            event_rows=event_rows, native_roundtrip_gate="Every case reader restores all fields and requires exact native reserialization equality")
        complete(output, report)
    except BaseException as error:
        report.update(outcome="failed", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        finish(output, report, start)
    return report


def sample_report(sample):
    report = json.loads((sample / "run-report.json").read_text())
    if report["kind"] != "generate" or report["outcome"] != "completed":
        raise ValueError("Sample generation did not complete")
    for name, digest in report["output_sha256"].items():
        if sha256(sample / name) != digest:
            raise RuntimeError("Sample output changed: " + name)
    return report


def gbts_numerical_audit(audit, events):
    if audit.get("schema_version") != 1 or audit.get("numerical_policy") != "select_denominator_before_division":
        raise RuntimeError("Unexpected GBTS numerical audit policy")
    rows = audit["events"]
    if [row["event"] for row in rows] != list(range(events)):
        raise RuntimeError("GBTS numerical audit event coverage is incomplete")
    for row in rows:
        updates, affected = row["updates"], row["affected_updates"]
        if type(updates) is not int or type(affected) is not int or not 0 <= affected <= updates:
            raise RuntimeError("Invalid GBTS numerical update counts")
        if any(record["event"] != row["event"] or not 1 <= record["update"] <= updates for record in row["records"]):
            raise RuntimeError("GBTS numerical state has invalid event/update identity")
        if affected > len({record["update"] for record in row["records"]}):
            raise RuntimeError("GBTS affected numerical updates lack state records")
    return {**audit, "all_events_verified": True,
            "total_affected_updates": sum(row["affected_updates"] for row in rows)}


def schedule_gbts(args, runner, seq, acts, geometry, config):
    settings = config["profiles"][PROFILE]
    directory = getattr(args, "gbts_native_dir", None)
    if directory is None:
        return runner.gbts.schedule(seq, acts, geometry, args.output / "gbts", settings, acts.logging.DEBUG)
    prepared = args.output / "gbts"
    audit = json.loads((prepared / "audit.json").read_text())
    for name, digest in audit["files"].items():
        if sha256(prepared / name) != digest:
            raise RuntimeError("GBTS prepared input changed: " + name)
    if audit["configuration"] != runner.gbts.configuration(settings):
        raise RuntimeError("Scheduled GBTS settings differ from prepared configuration")
    sys.path.insert(0, str(directory))
    module = importlib.import_module("nodd_ttbar_gbts")
    verify_gbts_module(module, directory, args.runtime_root)
    algorithm = module.GbtsSeeding(str(prepared), acts.logging.DEBUG)
    seq.addAlgorithm(algorithm)
    return algorithm


def reconstruction_sequence(args, config, runner, acts, detector, geometry, observer, sidecar, sample):
    from acts.examples.reconstruction import addSpacePointsMaking
    level, u = acts.logging.WARNING, acts.UnitConstants
    field = acts.ConstantBField(acts.Vector3(0., 0., 3.*u.T))
    rnd = acts.examples.RandomNumbers(seed=args.seed)
    seq = acts.examples.Sequencer(events=args.events, numThreads=1, outputDir=str(args.output), logLevel=acts.logging.DEBUG)
    for decorator in detector.contextDecorators():
        seq.addContextDecorator(decorator)
    seq.addReader(sidecar.SampleReader(str(sample / "sample"), args.events, geometry))
    seq.addWhiteboardAlias("particles", "particles_simulated")
    seq.addWhiteboardAlias("particles_simulated_selected", "particles_simulated")
    runner.smearing.schedule_digitization(seq, acts, geometry, rnd, args.output / "digitization.json", observer, level)
    addSpacePointsMaking(seq, geometry, args.output / "pixel-selection.json", None, logLevel=level)
    seeder = schedule_gbts(args, runner, seq, acts, geometry, config)
    hypothesis = acts.ParticleHypothesis.muon
    p = config["parameter_estimation"]
    seq.addAlgorithm(acts.examples.TrackParamsEstimationAlgorithm(level=level,
        inputSeeds="seeds", outputTrackParameters="estimatedparameters", outputSeeds="estimatedseeds",
        trackingGeometry=geometry, magneticField=field, particleHypothesis=hypothesis,
        spacePointSelection=getattr(acts.examples.SeedSpacePointSelection, p["spacepoint_selection"]),
        initialSigmas=[p["sigma_loc0_mm"]*u.mm, p["sigma_loc1_mm"]*u.mm,
            p["sigma_phi_deg"]*u.degree, p["sigma_theta_deg"]*u.degree, 0., p["sigma_time_ns"]*u.ns],
        initialSigmaQoverPt=p["sigma_qoverpt_GeV_inv"]/u.GeV, initialSigmaPtRel=p["sigma_pt_relative"]))
    c, q = config["ckf"], config["quality"]
    seq.addAlgorithm(acts.examples.TrackFindingAlgorithm(level=level,
        inputMeasurements="measurement_subset", inputInitialTrackParameters="estimatedparameters",
        inputSeeds="estimatedseeds", outputTracks="ckf_tracks", trackingGeometry=geometry, magneticField=field,
        findTracks=acts.examples.TrackFindingAlgorithm.makeTrackFinderFunction(geometry, field, level),
        findTracksBrem=acts.examples.TrackFindingAlgorithm.makeBremTrackFinderFunction(geometry, field, level),
        measurementSelectorCfg=acts.MeasurementSelector.Config([(acts.GeometryIdentifier(),
            ([], [c["measurement_chi2"]], [c["outlier_chi2"]], [c["max_measurements_per_surface"]]))]),
        maxSteps=c["max_steps"], twoWay=c["two_way"], reverseSearch=False,
        seedDeduplication=c["seed_deduplication"], stayOnSeed=c["stay_on_seed"],
        trimTracks=True, recordMaterialStates=False, useJosephFormulation=True))
    a = config["ambiguity"]
    seq.addAlgorithm(acts.examples.GreedyAmbiguityResolutionAlgorithm(level=level,
        inputTracks="ckf_tracks", outputTracks="ambi_tracks", maximumSharedHits=a["maximum_shared_hits"],
        nMeasurementsMin=q["minimum_measurements"], maximumIterations=a["maximum_iterations"]))
    seq.addAlgorithm(sidecar.PileupAudit(str(args.output / "audit")))
    log = args.output / "native-sequencer.log"
    with native_log(log):
        seconds = run_sequence(seq, args.output)
    effective = json.loads(seeder.effective_configuration_json())
    graphs = graph_audit(log, args.events, effective["seed_finder"]["nMaxEdges"])
    statistics = dict(seeder.statistics())
    if getattr(args, "gbts_native_dir", None) is not None:
        statistics["numerical_audit"] = gbts_numerical_audit(json.loads(statistics.pop("numerical_audit_json")), args.events)
    return dict(statistics, sequencer_seconds=seconds, effective_configuration=effective, graph_audit=graphs,
                effective_two_way=c["two_way"], particle_configuration=dict(name="inclusive", hypothesis="muon"))


def audit_case(output, events, config, native, sample_inventory):
    sensors = {s["geometry_id"]: (s["ids"]["system"], s["ids"]["layer"]) for s in native["sensors"]}
    seen, maximum = set(), 0
    with gzip.GzipFile(filename=str(output / "events.jsonl.gz"), mode="wb", mtime=0) as target:
        for event in range(events):
            path = output / "audit" / f"event{event:06d}.json.gz"
            with gzip.open(path, "rt") as stream:
                row = json.load(stream)
            if row["event"] != event or row["event"] in seen:
                raise RuntimeError("Missing or duplicate reconstruction event")
            seen.add(event)
            if not row["sample_metadata"]["roundtrip_all_native_particle_and_hit_fields"]:
                raise RuntimeError("Native sample roundtrip was not verified")
            if row["ckf_input_measurements"] != len(row["measurements"]):
                raise RuntimeError("CKF did not receive all measurements")
            counts = {}
            for track in row["ambi"]:
                for index in set(track["shared_measurements"]):
                    counts[index] = counts.get(index, 0) + 1
            shared_max = max((sum(counts[i] > 1 for i in track["shared_measurements"]) for track in row["ambi"]), default=0)
            if shared_max >= config["ambiguity"]["maximum_shared_hits"]:
                raise RuntimeError(f"Unconverged native ambiguity survivors in event {event}: {shared_max}")
            maximum = max(maximum, shared_max)
            for point in row["spacepoints"]:
                if any(sensors[row["measurements"][i]["geometry_id"]][0] > 3 for i in point["measurements"]):
                    raise RuntimeError("GBTS consumed nonpixel spacepoints")
            row["sample_fingerprints"] = sample_inventory[event]["sample_fingerprints"]
            target.write(canonical(row) + b"\n")
            check_disk(output)
    if seen != set(range(events)):
        raise RuntimeError("All-event coverage failed")
    return dict(events=events, all_generated_events_retained=True, all_native_survivors_converged=True,
                maximum_shared_measurements=maximum, native_full_particle_hit_roundtrip=True,
                audit_chunks_retained=True)


def reconstruct(sample, pitch, output, supplier, runtime, native_dir, fatras_native_dir=None, gbts_native_dir=None):
    fatras_native_dir = fatras_native_dir or ROOT / "build/strixel-ttbar-safe-fatras"
    original = sample_report(sample)
    events, seed = original["events"], original["seed"]
    start = time.monotonic()
    report = begin("reconstruct", output, events, seed, supplier, runtime, native_dir, pitch,
                   fatras_native_dir=fatras_native_dir, gbts_native_dir=gbts_native_dir)
    try:
        report["sample_report_sha256"] = sha256(sample / "run-report.json")
        report["sample_sha256"] = dict(original["output_sha256"])
        args = SimpleNamespace(output=output, pt=1., events=events, threads=1, seed=seed, profile=PROFILE,
                               phase="validation", runtime_root=runtime, gbts_native_dir=gbts_native_dir)
        runner, acts, observer, detector, geometry, native, info, sidecar = prepared(args, supplier, runtime, native_dir)
        report["preparation"] = info
        if gbts_native_dir is not None:
            sys.path.insert(0, str(gbts_native_dir))
            report["gbts_numerical_implementation"] = verify_gbts_module(
                importlib.import_module("nodd_ttbar_gbts"), gbts_native_dir, runtime)
        report["baseline_equivalence"] = base.baseline_gate(output, supplier)
        for name in ("material-map.json", "error-table.json", "digitization.json", "pixel-selection.json", "native-report.json"):
            if json.loads((output / name).read_text()) != json.loads((sample / name).read_text()):
                raise RuntimeError("Replayed sample geometry/material/response preparation differs: " + name)
        config = campaign(events, seed, pitch)
        report["campaign"] = config
        widths = json.loads((output / "error-table.json").read_text())
        write_json(output / "baseline-error-table.json", widths)
        widths, volumes = base.scale_widths(widths, native["sensors"], pitch)
        write_json(output / "error-table.json", widths)
        digi, counts = runner.smearing.build_config(native["sensors"], dict(model="gaussian_smearing", merge=False,
            measured_coordinates_by_system=runner.smearing.COORDINATES), widths)
        write_json(output / "digitization.json", digi)
        report["response_scaling"] = dict(pitch_mm=pitch, baseline_pitch_mm=.5, factor_sigma_v=pitch/.5,
            systems=[4, 5], volumes=volumes, coordinate=1, doMerge=False, sensor_counts=counts)
        report["gbts_preparation"] = runner.gbts.prepare(native, output / "gbts", config["profiles"][PROFILE])
        write_json(output / "campaign.json", config)
        report["prepared_input_sha256"] = {str(p.relative_to(output)): sha256(p) for p in output.rglob("*")
                                            if p.is_file() and p.name != "run-report.json"}
        write_json(output / "run-report.json", report)
        report["gbts_statistics"] = reconstruction_sequence(args, config, runner, acts, detector, geometry, observer, sidecar, sample)
        manifest = json.loads((sample / "sample-manifest.json").read_text())
        report["event_audit"] = audit_case(output, events, config, native, manifest["event_rows"])
        # Verify the complete once-produced sample after native reconstruction too.
        sample_report(sample)
        complete(output, report)
    except BaseException as error:
        report.update(outcome="failed", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        finish(output, report, start)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in ("generate", "reconstruct"):
        p = sub.add_parser(name)
        p.add_argument("--output", type=Path, required=True)
        p.add_argument("--supplier-root", type=Path, default=ROOT.parent / "nodd-gen3-material-mapping")
        p.add_argument("--runtime-root", type=Path, default=ROOT.parent / "nodd-software-layout")
        p.add_argument("--native-dir", type=Path, default=ROOT / "build/strixel-ttbar-native")
        p.add_argument("--fatras-native-dir", type=Path, default=ROOT / "build/strixel-ttbar-safe-fatras")
        if name == "generate":
            p.add_argument("--events", type=int, default=100)
            p.add_argument("--seed", type=int, default=153042)
        else:
            p.add_argument("--sample", type=Path, required=True)
            p.add_argument("--pitch", type=float, choices=PITCHES, required=True)
            p.add_argument("--gbts-native-dir", type=Path, default=ROOT / "build/strixel-ttbar-safe-gbts")
    args = parser.parse_args()
    try:
        if args.operation == "generate":
            if args.events <= 0 or args.seed < 0:
                raise ValueError("Require positive event count and nonnegative seed")
            generate(args.output.resolve(), args.events, args.seed, args.supplier_root.resolve(),
                     args.runtime_root.resolve(), args.native_dir.resolve(), args.fatras_native_dir.resolve())
        else:
            reconstruct(args.sample.resolve(), args.pitch, args.output.resolve(), args.supplier_root.resolve(),
                        args.runtime_root.resolve(), args.native_dir.resolve(), args.fatras_native_dir.resolve(),
                        args.gbts_native_dir.resolve())
    except (ValueError, RuntimeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
