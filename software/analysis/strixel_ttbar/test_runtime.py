"""Protocol and adverse provenance/convergence tests; native smoke is separate."""
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("ttbar_runtime_under_test", Path(__file__).with_name("runtime.py"))
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class RuntimeTest(unittest.TestCase):
    def test_gbts_numerical_audit_requires_all_events_and_recorded_updates(self):
        audit = {"schema_version": 1, "numerical_policy": "select_denominator_before_division",
                 "events": [{"event": 0, "updates": 25, "affected_updates": 1,
                             "records": [{"event": 0, "update": 7}]},
                            {"event": 1, "updates": 0, "affected_updates": 0, "records": []}]}
        self.assertEqual(runtime.gbts_numerical_audit(audit, 2)["total_affected_updates"], 1)
        changed = copy.deepcopy(audit); changed["events"].pop()
        with self.assertRaisesRegex(RuntimeError, "coverage"):
            runtime.gbts_numerical_audit(changed, 2)
        changed = copy.deepcopy(audit); changed["events"][0]["records"] = []
        with self.assertRaisesRegex(RuntimeError, "lack state"):
            runtime.gbts_numerical_audit(changed, 2)
        changed = copy.deepcopy(audit); changed["events"][0]["records"][0]["event"] = 1
        with self.assertRaisesRegex(RuntimeError, "event/update"):
            runtime.gbts_numerical_audit(changed, 2)
        changed = copy.deepcopy(audit); changed["events"][0]["affected_updates"] = 26
        with self.assertRaisesRegex(RuntimeError, "counts"):
            runtime.gbts_numerical_audit(changed, 2)

    def test_compiled_gbts_source_generated_native_and_policy_bindings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            own = root / "software/source/ActsExamples/StrixelPileupSafeGbts"; own.mkdir(parents=True)
            (own / "fixture.cpp").write_text("local source")
            directory = root / "native"; (directory / "generated").mkdir(parents=True)
            (directory / "generated/fixture.hpp").write_text("generated source")
            module_path = directory / "nodd_ttbar_gbts.fixture.so"; module_path.write_bytes(b"module")
            native = root / "runtime/build/acts"; native.mkdir(parents=True)
            for name in ("CMakeCache.txt", "build.ninja"):
                (native / name).write_text(name)
            provenance = {"acts_revision": "355ea68493b326956756c9386d2fd9eaf9328568",
                          "numerical_policy": "select_denominator_before_division", "upstream_sha256": {},
                          "local_source_sha256": {"fixture.cpp": runtime.sha256(own / "fixture.cpp")},
                          "generated_sha256": {"fixture.hpp": runtime.sha256(directory / "generated/fixture.hpp")},
                          "compiler_cache_sha256": runtime.sha256(native / "CMakeCache.txt"),
                          "native_build_ninja_sha256": runtime.sha256(native / "build.ninja")}
            (directory / "generated/provenance.json").write_text(json.dumps(provenance))
            module = type("Module", (), {"__file__": str(module_path), "provenance_json": staticmethod(lambda: json.dumps(provenance)),
                                        "pybind11_version": "3.0.4", "pybind11_internals_version": 11})
            with patch.object(runtime, "ROOT", root):
                runtime.verify_gbts_module(module, directory, root / "runtime")
                (own / "fixture.cpp").write_text("unrebuilt source")
                with self.assertRaisesRegex(RuntimeError, "local source changed"):
                    runtime.verify_gbts_module(module, directory, root / "runtime")
                (own / "fixture.cpp").write_text("local source")
                (directory / "generated/fixture.hpp").write_text("unrebuilt generated source")
                with self.assertRaisesRegex(RuntimeError, "generated input changed"):
                    runtime.verify_gbts_module(module, directory, root / "runtime")
                (directory / "generated/fixture.hpp").write_text("generated source")
                (native / "build.ninja").write_text("changed flags")
                with self.assertRaisesRegex(RuntimeError, "build configuration changed"):
                    runtime.verify_gbts_module(module, directory, root / "runtime")

    def graph(self, text, events=2):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "native.log"
            path.write_text(text)
            return runtime.graph_audit(path, events, 2000000)

    @staticmethod
    def graph_lines():
        return ("DEBUG start processing event 0 on thread 0\n"
                "DEBUG Created graph with 1500000 edges and 80000 edge links\n"
                "DEBUG finished event 0\n"
                "DEBUG start processing event 1 on thread 0\n"
                "WARNING Maximum number of graph edges exceeded - possible efficiency loss 2000000\n"
                "DEBUG Created graph with 2000000 edges and 90000 edge links\n"
                "DEBUG finished event 1\n")

    def test_graph_cap_has_complete_event_identity_and_separate_counts(self):
        result = self.graph(self.graph_lines())
        self.assertEqual(result["cap_reached_events"], 1)
        self.assertEqual([r["edges"] for r in result["events"]], [1500000, 2000000])
        self.assertEqual([r["cap_reached"] for r in result["events"]], [False, True])

    def test_graph_missing_duplicate_and_unbound_diagnostics_rejected(self):
        text = self.graph_lines()
        for changed in (text.replace("DEBUG finished event 1\n", ""),
                        text + text,
                        text.replace("DEBUG start processing event 1 on thread 0\n", ""),
                        text.replace("WARNING Maximum number of graph edges exceeded - possible efficiency loss 2000000\n", ""),
                        text.replace("loss 2000000", "loss 1999999")):
            with self.assertRaises(RuntimeError):
                self.graph(changed)

    def test_zero_edge_event_still_has_graph_diagnostics(self):
        result = self.graph("DEBUG start processing event 0 on thread 0\n"
                            "DEBUG Created graph with 0 edges and 0 edge links\n"
                            "DEBUG finished event 0\n", events=1)
        self.assertEqual(result["cap_reached_events"], 0)
        self.assertEqual(result["events"][0]["edges"], 0)

    def test_native_descriptor_capture_restores_stdout_and_stderr_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "native.log"
            script = ("import importlib.util,os,sys\n"
                      f"s=importlib.util.spec_from_file_location('capture_test',{str(Path(__file__).with_name('runtime.py'))!r})\n"
                      "m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n"
                      "try:\n"
                      f" with m.native_log({str(path)!r}):\n"
                      "  os.write(1,b'native stdout\\n');os.write(2,b'native stderr\\n');print('python stdout')\n"
                      "  raise RuntimeError('retained failure')\n"
                      "except RuntimeError: pass\n"
                      "os.write(1,b'stdout restored\\n');os.write(2,b'stderr restored\\n')\n")
            result = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "stdout restored\n")
            self.assertEqual(result.stderr, "stderr restored\n")
            self.assertEqual(set(path.read_text().splitlines()), {"native stdout", "native stderr", "python stdout"})

    def test_common_collision_window_preserves_other_reconstruction_settings(self):
        for pitch in runtime.PITCHES:
            config = runtime.campaign(100, 153042, pitch)
            baseline, _ = runtime.base.configuration(dict(simulation="fatras", particle="muon",
                pt_GeV=1., pitch_mm=pitch, events=100, seed=153042))
            expected = copy.deepcopy(baseline["profiles"])
            profile = expected[runtime.PROFILE]
            profile["z0_range_mm"] = [-1000., 1000.]
            profile.setdefault("seed_finder", {}).update(minZ0=-1000., maxZ0=1000.)
            profile.setdefault("tracking_filter", {})["maxZ0"] = 1000.
            self.assertEqual(config["profiles"], expected)
            self.assertEqual(config["ttbar_pileup"]["gbts_z0_range_mm"], [-1000., 1000.])
            for key in ("ckf", "matching", "quality", "ambiguity", "parameter_estimation"):
                self.assertEqual(config[key], baseline[key])

    def test_frozen_profile_and_inclusive_hypothesis(self):
        for pitch in runtime.PITCHES:
            c = runtime.campaign(100, 153042, pitch)
            self.assertEqual(c["selected_profile"], "pt4-nominal-triplet")
            self.assertEqual(c["particle"], "muon")
            self.assertEqual(c["simulation"], "fatras")
            self.assertEqual(c["ambiguity"], dict(maximum_shared_hits=3, maximum_iterations=4294967295))
            self.assertEqual(c["strixel_crosscheck"]["pitch_mm"], pitch)
            self.assertEqual(c["ttbar_pileup"]["hard_process"], ["Top:qqbar2ttbar=on"])
            self.assertEqual(c["ttbar_pileup"]["pileup"], 200)
            self.assertTrue(c["ttbar_pileup"]["no_truth_filter_on_ckf"])

    def test_fresh_directory_preserves_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "failure.txt").write_text("keep")
            with self.assertRaises(ValueError):
                runtime.check_fresh(p)
            self.assertEqual((p / "failure.txt").read_text(), "keep")

    def test_sample_integrity_rejects_mutation_and_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "input").write_text("original")
            report = dict(kind="generate", outcome="completed", output_sha256={"input": runtime.sha256(p / "input")})
            runtime.write_json(p / "run-report.json", report)
            self.assertEqual(runtime.sample_report(p), report)
            (p / "input").write_text("changed")
            with self.assertRaises(RuntimeError):
                runtime.sample_report(p)
            report["outcome"] = "failed"
            runtime.write_json(p / "run-report.json", report)
            with self.assertRaises(ValueError):
                runtime.sample_report(p)

    @staticmethod
    def row():
        return dict(event=0, sample_metadata=dict(roundtrip_all_native_particle_and_hit_fields=True),
                    ckf_input_measurements=0, measurements=[], spacepoints=[], ambi=[])

    def audit(self, row, events=1):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "audit").mkdir()
            with gzip.open(p / "audit/event000000.json.gz", "wt") as stream:
                json.dump(row, stream)
            # This tiny synthetic audit tests event/shared-link semantics.
            # Host capacity is controlled here and tested separately below.
            ample_test_disk_bytes = 4 * 1024**3
            with patch.object(runtime.shutil, "disk_usage",
                              return_value=type("Usage", (), dict(free=ample_test_disk_bytes))):
                return runtime.audit_case(p, events, dict(ambiguity=dict(maximum_shared_hits=3)),
                                          dict(sensors=[]), [dict(sample_fingerprints={})])

    def test_zero_track_event_retained(self):
        r = self.audit(self.row())
        self.assertEqual(r["events"], 1)
        self.assertEqual(r["maximum_shared_measurements"], 0)
        self.assertTrue(r["native_full_particle_hit_roundtrip"])

    def test_repeated_link_in_one_track_is_not_shared(self):
        row = self.row()
        row["ambi"] = [dict(shared_measurements=[7, 7, 7])]
        self.assertEqual(self.audit(row)["maximum_shared_measurements"], 0)

    def test_native_shared_occurrences_preserved(self):
        row = self.row()
        row["ambi"] = [dict(shared_measurements=[7, 7, 7]), dict(shared_measurements=[7])]
        with self.assertRaisesRegex(RuntimeError, "Unconverged"):
            self.audit(row)

    def test_reject_missing_roundtrip_or_subset(self):
        row = self.row()
        row["sample_metadata"]["roundtrip_all_native_particle_and_hit_fields"] = False
        with self.assertRaisesRegex(RuntimeError, "roundtrip"):
            self.audit(row)
        row = self.row()
        row["ckf_input_measurements"] = 1
        with self.assertRaisesRegex(RuntimeError, "all measurements"):
            self.audit(row)

    def test_reject_event_identity_mismatch(self):
        row = self.row()
        row["event"] = 1
        with self.assertRaisesRegex(RuntimeError, "Missing or duplicate"):
            self.audit(row)

    def test_disk_guard(self):
        required_disk_bytes = 2 * 1024**3
        for free in (1, required_disk_bytes - 1):
            with patch.object(runtime.shutil, "disk_usage", return_value=type("Usage", (), dict(free=free))):
                with self.assertRaisesRegex(RuntimeError, "partial evidence retained"):
                    runtime.check_disk(Path("."))
        with patch.object(runtime.shutil, "disk_usage",
                          return_value=type("Usage", (), dict(free=required_disk_bytes))):
            runtime.check_disk(Path("."))

    def test_begin_fingerprint_failure_is_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "failed"
            with patch.object(runtime, "fingerprints", side_effect=RuntimeError("missing native")):
                with self.assertRaisesRegex(RuntimeError, "missing native"):
                    runtime.begin("generate", p, 1, 153043, Path("."), Path("."), Path("."))
            report = json.loads((p / "run-report.json").read_text())
            self.assertEqual(report["outcome"], "failed")
            self.assertIn("missing native", report["error"])

    def test_native_failure_keeps_fpe_diagnostic(self):
        class Sequence:
            fpeResult = "synthetic FPE evidence"
            def run(self):
                raise RuntimeError("native failure")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, "native failure"):
                runtime.run_sequence(Sequence(), p)
            report = json.loads((p / "native-fpe-diagnostic.json").read_text())
            self.assertEqual(report["native_fpe_result"], "synthetic FPE evidence")

    def test_explicit_pythia_data_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            library = p / "prefix/lib/libpythia8.dylib"
            library.parent.mkdir(parents=True)
            library.write_text("fixture")
            data = p / "prefix/share/Pythia8/xmldoc"
            data.mkdir(parents=True)
            (p / "CMakeCache.txt").write_text("PYTHIA8_LIBRARY:FILEPATH=" + str(library) + "\n")
            self.assertEqual(runtime.pythia_data_directory(p), data.resolve())
            data.rmdir()
            with self.assertRaisesRegex(RuntimeError, "XML data"):
                runtime.pythia_data_directory(p)

    @staticmethod
    def full_origin_fixture():
        ids = [[i+1, 0, 1, 0, 0] for i in range(201)]
        return dict(interaction_origins=list(range(201)),
                    generated=[dict(initial=dict(id=pid)) for pid in ids],
                    labels=[dict(id=pid, interaction=i) for i, pid in enumerate(ids)])

    def test_full_unfiltered_origin_gate(self):
        row = self.full_origin_fixture()
        runtime.validate_full_generated_origins(row)
        row["labels"][-1]["interaction"] = 0
        with self.assertRaisesRegex(RuntimeError, "all 201 origins"):
            runtime.validate_full_generated_origins(row)

    def test_origin_labels_must_cover_every_generated_particle(self):
        row = self.full_origin_fixture()
        row["generated"].append(dict(initial=dict(id=[202, 0, 1, 0, 0])))
        with self.assertRaisesRegex(RuntimeError, "label inventory"):
            runtime.validate_full_generated_origins(row)
        row = self.full_origin_fixture()
        row["labels"].append(dict(row["labels"][0]))
        with self.assertRaisesRegex(RuntimeError, "label inventory"):
            runtime.validate_full_generated_origins(row)

    def test_extra_or_duplicate_interaction_inventory_rejected(self):
        row = self.full_origin_fixture()
        row["interaction_origins"].append(201)
        with self.assertRaisesRegex(RuntimeError, r"1\+200"):
            runtime.validate_full_generated_origins(row)
        row = self.full_origin_fixture()
        row["interaction_origins"].append(0)
        with self.assertRaisesRegex(RuntimeError, r"1\+200"):
            runtime.validate_full_generated_origins(row)

    def test_generated_pythia_copy_and_binary_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "software/submodules/acts/Examples/Algorithms/GeneratorsPythia8/ActsExamples/Generators/Pythia8ProcessGenerator.cpp"
            original.parent.mkdir(parents=True)
            original.write_text("fixture: " + runtime.PYTHIA_OLD + "\n")
            generated = root / "GuardedPythia8ProcessGenerator.cpp"
            generated.write_text('#include "PythiaGenerationGuard.hpp"\n' + original.read_text().replace(runtime.PYTHIA_OLD, runtime.PYTHIA_NEW))
            guard = root / "PythiaGenerationGuard.hpp"
            guard.write_text("synthetic header fixture")
            sidecar = type("Sidecar", (), dict(pythia_original_source_sha256=runtime.sha256(original),
                pythia_generated_source_sha256=runtime.sha256(generated), pythia_guard_header_sha256=runtime.sha256(guard),
                pythia_generation_success_policy="abort"))
            with patch.object(runtime, "UPSTREAM_PYTHIA_SHA256", runtime.sha256(original)):
                runtime.pythia_generation_provenance(root, root, sidecar)
                generated.write_text(generated.read_text() + "unreviewed mutation")
                with self.assertRaisesRegex(RuntimeError, "single reviewed"):
                    runtime.pythia_generation_provenance(root, root, sidecar)

    def test_complete_failure_audit_and_rejections(self):
        audit = dict(events=[dict(event=0, failures=[]), dict(event=1, failures=[
            dict(initial_state=dict(id=[1, 0, 7, 0, 0]), error_value=2)])])
        self.assertEqual(runtime.failure_audit_summary(audit, 2, complete=True), dict(events=2, failed_particles=1))
        self.assertEqual(runtime.failure_audit_summary(dict(events=[]), 2), dict(events=0, failed_particles=0))
        with self.assertRaisesRegex(RuntimeError, "coverage"):
            runtime.failure_audit_summary(dict(events=[]), 2, complete=True)
        with self.assertRaisesRegex(RuntimeError, "Duplicate"):
            runtime.failure_audit_summary(dict(events=[audit["events"][0]]*2), 2)
        audit["events"][1]["failures"][0]["initial_state"]["id"] = [1]
        with self.assertRaisesRegex(RuntimeError, "identity/error"):
            runtime.failure_audit_summary(audit, 2)

    def test_isolated_fatras_generated_input_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            generated = directory / "generated"
            generated.mkdir()
            (generated / "fixture.hpp").write_text("reviewed generated source")
            native = directory / "module.so"
            native.write_text("native artifact fixture")
            source = directory / "software/source/ActsExamples/StrixelPileupSafeFatras"
            source.mkdir(parents=True)
            for name in runtime.FATRAS_SOURCE_NAMES:
                (source / name).write_text("compiled local fixture")
            module = type("Module", (), dict(__file__=str(native), upstream_sha256={},
                local_source_sha256={name: runtime.sha256(source / name) for name in runtime.FATRAS_SOURCE_NAMES},
                generated_sha256={"fixture.hpp": runtime.sha256(generated / "fixture.hpp")},
                native_compile_flags="-O2", native_compile_defines="fixture", native_flag_block_sha256="fixture",
                pybind11_version="3.0.4", pybind11_internals_version=11))
            with patch.object(runtime, "ROOT", directory):
                runtime.verify_fatras_module(module, directory, directory)
                (source / "FailureAudit.hpp").write_text("unrebuilt local mutation")
                with self.assertRaisesRegex(RuntimeError, "local source changed without rebuild"):
                    runtime.verify_fatras_module(module, directory, directory)
            (generated / "fixture.hpp").write_text("changed")
            with self.assertRaisesRegex(RuntimeError, "generated input changed"):
                runtime.verify_fatras_module(module, directory, directory)

    def test_prepared_input_immutability(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "config").write_text("value")
            report = dict(source_sha256={}, runtime_sha256={}, prepared_input_sha256={"config": "wrong"})
            with self.assertRaisesRegex(RuntimeError, "Prepared input changed"):
                runtime.complete(p, report)


if __name__ == "__main__":
    unittest.main()
