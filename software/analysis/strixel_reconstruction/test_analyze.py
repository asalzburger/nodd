"""Synthetic scientific/provenance controls for the isolated GBTS pitch replay."""
import copy
from concurrent.futures import Future
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

SPEC = importlib.util.spec_from_file_location("strixel_analysis", Path(__file__).with_name("analyze.py"))
a = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a)


def fixture(n=100):
    """Named test values, not a detector response or acceptance reference."""
    truth = np.tile([0., 0., .2, 1., .1, 0.], (n, 1))
    x = np.linspace(-1., 1., n)
    result = {"event": np.arange(n), "eta": np.linspace(-4, 4, n),
              "truth": truth, "pt": np.full(n, math.sin(1.) / .1), "charge": np.ones(n, dtype=int)}
    for key in ("primary_measurements", "primary_sensors", "pixel_groups", "seeds", "estimated_seeds", "pure_seed", "pure_estimated_seed", "reconstructable", "reconstructable4", "simhits", "measurements", "spacepoints"):
        result[key] = np.ones(n, dtype=int)
    for stage in ("ckf", "ambi"):
        for key in ("raw", "accepted", "matched", "inliers"):
            result[stage + "_" + key] = np.ones(n, dtype=int)
        for key in ("fake", "duplicates", "secondary", "wrong_charge", "fake_event", "duplicate_event", "quality_rejected", "invalid_covariance"):
            result[stage + "_" + key] = np.zeros(n, dtype=int)
        result[stage + "_reco"] = truth - x[:, None] * np.array([.01, .02, .001, .001, .001, 1.])
        residual = truth - result[stage + "_reco"]
        residual[:, 2] = (residual[:, 2] + math.pi) % (2 * math.pi) - math.pi
        result[stage + "_variance"] = np.ones((n, 6))
        result[stage + "_residual"] = residual
        result[stage + "_pull"] = residual
    for name in a.FINGERPRINTS:
        result["fingerprint_" + name] = np.asarray([a.fingerprint({"event": i, "role": name}) for i in range(n)])
    for name in a.PHYSICAL_INPUTS:
        result[name + "_count"] = np.ones(n, dtype=int)
        result[name + "_ambiguous_groups"] = np.zeros(n, dtype=int)
        result[name + "_duplicate_entries"] = np.zeros(n, dtype=int)
    return result


def configuration_fixture():
    configs, items = [], []
    hashes = {name: "same" for name in ("selection.json", "material-map.json", "native-report.json", "pixel-selection.json", "gbts/config.json", "gbts/mapping.csv", "gbts/layers.csv", "gbts/connections.csv")}
    for pitch in a.PITCHES:
        configs.append({"volume_system": {"27": 1, "68": 4}, "gbts/config.json": {"frozen": True},
                        "error-table.json": {"groups": [{"volume": 27, "index": 1, "sigma_mm": .1}, {"volume": 68, "index": 0, "sigma_mm": .2}, {"volume": 68, "index": 1, "sigma_mm": .3 * pitch / .5}]},
                        "digitization.json": {"entries": [{"volume": 27, "value": {"smearing": [{"index": 1, "stddev": .1}]}}, {"volume": 68, "value": {"smearing": [{"index": 0, "stddev": .2}, {"index": 1, "stddev": .3 * pitch / .5}]}}]}})
        items.append({"report": {"pitch_mm": pitch, "input_revision": a.INPUT_REVISION, "seed": 123042,
            "profile": "pt4-nominal-triplet", "campaign": {"simulation": "fatras", "particle": "muon", "strixel_crosscheck": {"pitch_mm": pitch}},
            "postrun_immutability": {k: True for k in ("native_supplier_runtime", "prepared_inputs", "source")},
            "baseline_equivalence": {k: {"matched": True} for k in ("selection.json", "material-map.json", "error-table.json", "digitization.json")},
            "event_audit": {"all_generated_events_retained": True, "all_native_survivors_converged": True},
            "source_revision": "source", "source_sha256": {}, "runtime_sha256": {}, "baseline_input_sha256": {}, "supplier_identity": {}, "prepared_input_sha256": hashes}})
    return items, configs


class StatisticalTests(unittest.TestCase):
    def test_exact_zero_event_bound_and_empty_bin(self):
        rate = a.rate(0, 1000)
        self.assertAlmostEqual(rate["zero_one_sided95_upper"], 1 - .05 ** .001)
        self.assertIsNone(a.rate(0, 0)["value"])
        self.assertEqual(a.rate(1000, 1000)["wilson95"][1], 1.)

    def test_width_minimum_preserves_tails_and_low_count_mean(self):
        stats = a.distribution(np.r_[np.arange(29), np.nan], (10.,))
        self.assertIsNone(stats["width68"])
        self.assertEqual(stats["finite_entries"], 29)
        self.assertEqual(stats["nonfinite_entries"], 1)
        self.assertEqual(stats["absolute_tail_counts"]["10.0"], 18)
        self.assertEqual(stats["mean"], 14.)
        self.assertIsNotNone(a.distribution(np.arange(30))["width68"])
        json.dumps(stats, allow_nan=False)

    def test_exact_central_probability_and_scaled_paired_ratio(self):
        x = np.linspace(-2, 2, 100)
        indices = np.random.default_rng(3).integers(0, 100, (40, 100))
        stats = a.paired_widths(np.stack([x, 2 * x, 3 * x, 4 * x]), indices)
        self.assertAlmostEqual(stats[0]["width68"], (np.quantile(x, a.QUANTILES[1]) - np.quantile(x, a.QUANTILES[0])) / 2)
        for i, stat in enumerate(stats):
            self.assertAlmostEqual(stat["ratio_to_baseline"], i + 1.)
            np.testing.assert_allclose(stat["ratio_interval68"], [i + 1., i + 1.])

    def test_bootstrap_cannot_define_low_count_point_width(self):
        values = np.tile(np.r_[np.arange(29.), np.full(11, np.nan)], (4, 1))
        # A deliberate all-finite 40-entry resample must not rescue the 29-point
        # original bin's undefined width or publish a ratio interval.
        indices = np.tile(np.arange(40) % 29, (10, 1))
        for stat in a.paired_widths(values, indices):
            self.assertIsNone(stat["width68"])
            self.assertIsNone(stat["width_interval68"])
            self.assertIsNone(stat["ratio_interval68"])

    def test_paired_efficiency_contingency_and_repeatability(self):
        arrays = [fixture(40) for _ in range(4)]
        for arr in arrays:
            arr["ambi_matched"][:5] = 0
        arrays[1]["ambi_matched"][0] = 1
        arrays[1]["ambi_matched"][5] = 0
        result = a.paired_bin(arrays, np.ones(40, dtype=bool), 20, 17)
        diff = result[1]["stages"]["ambi"]["efficiency_difference_to_baseline"]
        self.assertEqual((diff["gain"], diff["loss"], diff["both_success"], diff["both_failure"]), (1, 1, 34, 4))
        self.assertEqual(diff["value"], 0.)
        self.assertEqual(a.canonical(result), a.canonical(a.paired_bin(arrays, np.ones(40, dtype=bool), 20, 17)))

    def test_zero_discordance_does_not_claim_equivalence(self):
        arrays = [fixture(40) for _ in range(4)]
        result = a.paired_bin(arrays, np.ones(40, dtype=bool), 10, 17)
        diff = result[1]["stages"]["ambi"]["efficiency_difference_to_baseline"]
        self.assertEqual(diff["paired_bootstrap95"], [0., 0.])
        self.assertTrue(diff["empirical_bootstrap_degenerate"])
        upper = 1 - .05 ** (1 / 40)
        self.assertAlmostEqual(diff["zero_discordance_one_sided95_upper"], upper)
        self.assertEqual(diff["conservative_difference95_if_zero_discordance"], [-upper, upper])
        reference = result[0]["stages"]["ambi"]["efficiency_difference_to_baseline"]
        self.assertTrue(reference["reference_identity"])
        self.assertEqual(reference["conservative_difference95_if_zero_discordance"], [0., 0.])
        self.assertIsNone(reference["zero_discordance_one_sided95_upper"])

    def test_common_success_exposes_survival(self):
        arrays = [fixture(100) for _ in range(4)]
        for stage in ("ckf", "ambi"):
            arrays[1][stage + "_residual"][:40, 0] = np.nan
        result = a.paired_bin(arrays, np.ones(100, dtype=bool), 20, 1)
        own = result[0]["stages"]["ambi"]["quantities"]["d0"]
        self.assertEqual(own["common_success_events"], 60)
        self.assertLess(own["common_success_residual"]["width68"], own["residual"]["width68"])

    def test_relative_pt_uses_truth_theta_qoverp_and_sign(self):
        arrays = fixture(40)
        arrays["pt"][:] = 1000.  # Deliberately inconsistent test metadata.
        arrays["ambi_reco"][:, 4] = arrays["truth"][:, 4] * 2
        arrays["ambi_reco"][:, 3] = arrays["truth"][:, 3]
        np.testing.assert_allclose(a.observables(arrays, "ambi")[:, 6], .5)
        np.testing.assert_allclose(a.observables(arrays, "ambi")[:, 5], arrays["ambi_residual"][:, 5] / 299.792458)

    def test_candidate_bootstrap_uses_event_blocks(self):
        arrays = fixture(40)
        arrays["ambi_accepted"][0] = 1000
        arrays["ambi_fake"][0] = 1000
        indices = np.vstack([np.ones(40, dtype=int), np.zeros(40, dtype=int)])
        result = a.stage_summary(arrays, np.ones(40, dtype=bool), "ambi", indices)
        self.assertGreater(result["fake_candidate_fraction"]["event_bootstrap95"][1], .9)
        self.assertLess(result["fake_candidate_fraction"]["event_bootstrap95"][0], .1)


class ProvenanceTests(unittest.TestCase):
    def test_frozen_engine_native_configuration_gate(self):
        contract = a.frozen_contract()
        report = {"events": 40, "campaign": {**copy.deepcopy(contract["campaign_fields"]),
            "simulation": "fatras", "particle": "muon", "tuning_protocol": {"eta_edges": contract["eta_edges"]}},
            "gbts_statistics": {"effective_configuration": contract["effective_gbts_configuration"],
                "particle_configuration": contract["species"]["muon"], "effective_two_way": True,
                "events": 40, "input_spacepoints": 100, "mapped_spacepoints": 100}}
        a.validate_engine(report, contract)
        bad = copy.deepcopy(report)
        bad["campaign"]["ckf"]["measurement_chi2"] *= 2
        with self.assertRaisesRegex(ValueError, "Frozen engine"):
            a.validate_engine(bad, contract)
        bad = copy.deepcopy(report)
        bad["gbts_statistics"]["effective_configuration"]["seed_finder"]["minPt"] *= 2
        with self.assertRaisesRegex(ValueError, "Effective native GBTS"):
            a.validate_engine(bad, contract)

    def test_strict_complete_matrix_and_explicit_pilot(self):
        reports = [{"campaign": {"simulation": "fatras", "particle": "muon"}, "pt_GeV": 10, "pitch_mm": pitch, "events": 2} for pitch in a.PITCHES]
        a.validate_matrix(reports, pilot=True)
        with self.assertRaisesRegex(ValueError, "80-case"):
            a.validate_matrix(reports)
        with self.assertRaisesRegex(ValueError, "Repeated"):
            a.validate_matrix(reports + reports[:1], pilot=True)
        with self.assertRaisesRegex(ValueError, "four pitches"):
            a.validate_matrix(reports[:3], pilot=True)

    def test_transport_mismatch_stops_pixel_difference_reported(self):
        arrays = [fixture(40) for _ in range(4)]
        arrays[1]["fingerprint_pixel_measurements"][0] = "different"
        result = a.compare_pairing(arrays)
        self.assertFalse(result["pixel_measurements"]["all_pitches_equal"])
        self.assertIn("cannot", result["measurement_noise_attribution"])
        arrays[2]["fingerprint_simhits_payload"][2] = "different"
        with self.assertRaisesRegex(ValueError, "Transport pairing failed"):
            a.compare_pairing(arrays)

    def test_non_target_noise_changes_flagged_with_identical_pixels_and_seeds(self):
        arrays = [fixture(40) for _ in range(4)]
        same = a.compare_pairing(arrays)
        self.assertTrue(same["non_target_realized_inputs"]["all_pitches_equal"])
        arrays[3]["fingerprint_strixel_fine_u"][:2] = "different"
        arrays[3]["fingerprint_long_strip_physical"][1] = "different"
        changed = a.compare_pairing(arrays)
        self.assertTrue(changed["pixel_measurements"]["all_pitches_equal"])
        self.assertTrue(changed["seeds"]["all_pitches_equal"])
        self.assertEqual(changed["non_target_realized_inputs"]["changed_events_by_pitch"], [0, 0, 0, 2])
        self.assertIn("cannot be attributed uniquely", changed["measurement_noise_attribution"])

    def test_index_free_physical_comparison_preserves_multiplicity(self):
        measurement = {"index": 1, "geometry_id": 9, "particles": [[1]], "dimension": 2, "values": [.1, .2], "variance": [.01, .02]}
        renamed = {**measurement, "index": 99}
        first, counts = a.physical_measurements([measurement], {9: (4, 1)}, (4,), True)
        second, _ = a.physical_measurements([renamed], {9: (4, 1)}, (4,), True)
        self.assertEqual(first, second)
        self.assertEqual(first[0]["values"], [.1])
        duplicated, counts = a.physical_measurements([measurement, renamed], {9: (4, 1)}, (4,), True)
        self.assertEqual(counts, (2, 1, 1))
        self.assertNotEqual(a.fingerprint(first), a.fingerprint(duplicated))

    def test_only_longitudinal_error_changes_permitted(self):
        items, configs = configuration_fixture()
        a.validate_configurations(items, configs)
        configs[1]["error-table.json"]["groups"][1]["sigma_mm"] *= 2
        with self.assertRaisesRegex(ValueError, "beyond systems4/5"):
            a.validate_configurations(items, configs)

    def test_digitization_and_material_mismatch_stops(self):
        items, configs = configuration_fixture()
        configs[1]["digitization.json"]["entries"][0]["value"]["smearing"][0]["stddev"] *= 2
        with self.assertRaisesRegex(ValueError, "beyond local-v"):
            a.validate_configurations(items, configs)
        items, configs = configuration_fixture()
        items[1]["report"]["prepared_input_sha256"] = dict(items[1]["report"]["prepared_input_sha256"], **{"material-map.json": "changed"})
        with self.assertRaisesRegex(ValueError, "material-map"):
            a.validate_configurations(items, configs)

    def test_sanitized_native_paths_remain_distinct(self):
        value = {"/opt/a/module.so": "first", "/opt/b/module.so": "second", "command": ["--output=/private/tmp/case"]}
        clean = a.sanitize(value)
        self.assertEqual(len(clean), 3)
        self.assertNotIn("/private", json.dumps(clean))
        self.assertNotIn("/opt", json.dumps(clean))

    def test_native_classifier_rejects_invalid_covariance(self):
        module = a.native_analyzer()
        track = {"measurements": list(range(7)), "reference": True, "covariance_positive_definite": False,
                 "chi2": 1., "ndf": 1, "parameters": [0.] * 6, "variance": [1.] * 6}
        primary = {"id": [1], "eta": 0., "pt": 1., "charge": 1., "truth": [0., 0., 0., 1., 1., 0.]}
        row = {"event": 0, "generated": [primary], "simulated_ids": [[1]], "measurements": [
            {"index": i, "geometry_id": i, "particles": [[1]]} for i in range(7)], "simhits": 7,
            "spacepoints": [], "seeds": [], "estimated_seeds": [], "ckf": [track], "ambi": [track]}
        config = {"matching": {"reconstructable_measurements": 6, "reconstructable_pixel_groups": 3}, "quality": {"minimum_measurements": 7}}
        result = module.classify_event(row, {i: (1, i) for i in range(7)}, config)
        self.assertEqual((result["ambi"]["raw"], result["ambi"]["accepted"], result["ambi"]["quality_rejected"]), (1, 0, 1))

    def test_float32_root_payload_and_empty_events(self):
        try:
            import uproot
        except ImportError:
            self.skipTest("uproot unavailable in this Python")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hits.root"
            with uproot.recreate(path) as output:
                tree = output.mktree("hits", {"event_id": "uint32", "tx": "float32", "geometry_id": "uint64"})
                tree.extend({"event_id": np.array([0, 0], dtype="u4"), "tx": np.array([1., 1000.], dtype="f4"), "geometry_id": np.array([1, 2], dtype="u8")})
            hashes, meta = a.simhit_fingerprints(path, np.arange(2))
            self.assertNotEqual(hashes[0], hashes[1])
            self.assertEqual(meta["hits_by_event"], {"0": 2, "1": 0})
            self.assertEqual(meta["branches"]["tx"]["dtype"], "float32")
            self.assertEqual(meta["branches"]["tx"]["maximum_float32_ulp"], float(np.spacing(np.float32(1000))))


class ParallelRetentionTests(unittest.TestCase):
    @staticmethod
    def native_reports(source):
        """Small scheduling fixtures; no native physics execution is substituted."""
        for pitch in a.PITCHES:
            report = {"campaign": {"simulation": "fatras", "particle": "electron"},
                      "pt_GeV": 100., "pitch_mm": pitch, "events": 1000, "outcome": "completed"}
            report["case_id"] = a.case_name(a.case_identity(report))
            directory = source / report["case_id"]
            directory.mkdir(parents=True)
            (directory / "run-report.json").write_text(json.dumps(report))

    def test_parallel_completion_order_is_stable_and_submission_bounded(self):
        futures, counts, shutdown = [], [], []

        class Executor:
            def __init__(self, max_workers, mp_context):
                self.max_workers = max_workers
                self.context = mp_context.get_start_method()

            def submit(self, function, index):
                future = Future()
                future.set_result("case" + str(index))
                futures.append(future)
                return future

            def shutdown(self, **kwargs):
                shutdown.append(kwargs)

        executor = Executor(3, a.multiprocessing.get_context("spawn"))

        def out_of_order(active, return_when):
            counts.append(len(active))
            self.assertEqual(return_when, a.FIRST_COMPLETED)
            chosen = max(active, key=futures.index)
            return {chosen}, set(active) - {chosen}

        with mock.patch.object(a, "ProcessPoolExecutor", return_value=executor) as pool, mock.patch.object(a, "wait", side_effect=out_of_order):
            result = a.retain_cases([(i,) for i in range(8)], 3)
        self.assertEqual(result, ["case" + str(i) for i in range(8)])
        self.assertEqual(max(counts), 3)
        self.assertEqual(pool.call_args.kwargs["max_workers"], 3)
        self.assertEqual(pool.call_args.kwargs["mp_context"].get_start_method(), "spawn")
        self.assertEqual(shutdown, [{"wait": True, "cancel_futures": True}])

    def test_worker_failure_cancels_pending_and_stops_new_submissions(self):
        futures = []
        shutdown = []

        class Executor:
            def submit(self, function, index):
                future = Future()
                if index == 0:
                    future.set_exception(ValueError("synthetic worker failure"))
                futures.append(future)
                return future

            def shutdown(self, **kwargs):
                shutdown.append(kwargs)

        with mock.patch.object(a, "ProcessPoolExecutor", return_value=Executor()):
            with self.assertRaisesRegex(ValueError, "synthetic worker failure"):
                a.retain_cases([(i,) for i in range(80)], 3)
        self.assertEqual(len(futures), 3)
        self.assertTrue(all(future.cancelled() for future in futures[1:]))
        self.assertEqual(shutdown, [{"wait": True, "cancel_futures": True}])

    def test_default_serial_path_uses_no_executor(self):
        with mock.patch.object(a, "retain_case", side_effect=lambda index: index * 2), mock.patch.object(a, "ProcessPoolExecutor") as pool:
            self.assertEqual(a.retain_cases([(i,) for i in range(4)], 1), [0, 2, 4, 6])
        pool.assert_not_called()

    def test_invalid_jobs_fail_before_source_or_output_access(self):
        for jobs in (0, -1, True, 1.5):
            with self.subTest(jobs=jobs), self.assertRaisesRegex(ValueError, "positive integer"):
                a.retain("missing-source", "missing-output", jobs=jobs)

    def test_wrapper_import_snapshot_and_current_bytes_must_both_match(self):
        a.assert_source_unchanged(a.LOADED_SOURCE_SHA256)
        with self.assertRaisesRegex(ValueError, "wrapper source changed"):
            a.assert_source_unchanged("different import snapshot")
        with mock.patch.object(a, "digest", return_value="edited on disk"):
            with self.assertRaisesRegex(ValueError, "wrapper source changed"):
                a.assert_source_unchanged(a.LOADED_SOURCE_SHA256)

    def test_worker_rejects_source_or_report_change_before_reduction(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            report_path = Path(directory) / "run-report.json"
            report_path.write_text("{}")
            with mock.patch.object(a, "native_analyzer") as kernel:
                with self.assertRaisesRegex(ValueError, "wrapper source changed"):
                    a.retain_case(report_path, {}, output, "old wrapper", a.digest(report_path))
                with self.assertRaisesRegex(ValueError, "report changed after retention preflight"):
                    a.retain_case(report_path, {}, output, a.LOADED_SOURCE_SHA256, "old native report")
            kernel.assert_not_called()
            self.assertFalse(output.exists())

    def test_matrix_preflight_precedes_worker_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source", Path(directory) / "output"
            self.native_reports(source)
            path = next(source.glob("*/run-report.json"))
            report = json.loads(path.read_text())
            report["events"] = 999
            path.write_text(json.dumps(report))
            with mock.patch.object(a, "retain_cases") as workers:
                with self.assertRaisesRegex(ValueError, "Pilot denominators differ"):
                    a.retain(source, output, pilot=True, jobs=3)
            workers.assert_not_called()
            self.assertFalse(output.exists())

    def test_existing_case_artifacts_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source", Path(directory) / "output"
            self.native_reports(source)
            target = output / "cases" / "fatras-electron-pt100-pitch1"
            target.mkdir(parents=True)
            marker = target / "keep.txt"
            marker.write_text("existing partial evidence")
            with mock.patch.object(a, "frozen_contract", return_value={}), mock.patch.object(a, "validate_engine"), mock.patch.object(a, "retain_cases") as workers:
                with self.assertRaisesRegex(ValueError, "Refusing to overwrite retained case"):
                    a.retain(source, output, pilot=True, jobs=3)
            workers.assert_not_called()
            self.assertEqual(marker.read_text(), "existing partial evidence")
            self.assertFalse((output / "native-reports.json.gz").exists())

    def test_source_change_at_close_preserves_partial_files_without_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "source", Path(directory) / "output"
            self.native_reports(source)
            marker = output / "cases" / "partial-worker-output.txt"

            def complete_cases(tasks, jobs):
                marker.parent.mkdir(parents=True)
                marker.write_text("preserve completed case evidence")
                return [{"case": "synthetic-completed-case"}]

            with mock.patch.object(a, "frozen_contract", return_value={}), mock.patch.object(a, "validate_engine"), mock.patch.object(a, "retain_cases", side_effect=complete_cases), mock.patch.object(a, "assert_source_unchanged", side_effect=[None, ValueError("wrapper source changed at close")]):
                with self.assertRaisesRegex(ValueError, "wrapper source changed at close"):
                    a.retain(source, output, pilot=True, jobs=3)
            self.assertTrue(marker.exists())
            self.assertFalse((output / "native-reports.json.gz").exists())


if __name__ == "__main__":
    unittest.main()
