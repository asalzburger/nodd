"""Synthetic adverse tests for the isolated high-occupancy analysis contract."""
import copy
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

import analyze


CONFIG = {"matching": {"purity": .5, "completeness": .5},
          "quality": {"minimum_measurements": 7},
          "ambiguity": {"maximum_shared_hits": 3, "maximum_iterations": 4294967295}}


def pid(index):
    return [1, 0, index, 0, 0]


def particle(index, pt=5., hard_scatter=True, charge=1.):
    return {"id": pid(index), "pt": pt, "eta": .2, "charge": charge,
            "position_mm": [0., 0., 0.], "hard_scatter": hard_scatter}


def track(index, links, **updates):
    t = {"index": index, "measurements": list(links), "shared_measurements": list(links),
         "nMeasurements": len(set(links)), "nHoles": 0, "nOutliers": 0,
         "reference": True, "covariance_positive_definite": True, "chi2": 3., "ndf": 5,
         "hypothesis": {"absolute_pdg": 13, "mass_GeV": .105658},
         "parameters": [0., 0., .3, 1.4, .1, 0.], "variance": [1.] * 6}
    t.update(updates)
    return t


def fixture(event=0):
    particles = [particle(1), particle(2, hard_scatter=False), particle(3, pt=.2)]
    measurements, sensors = [], {}
    for owner in range(1, 5):
        for j in range(9):
            i = len(measurements); system = 1 + j % 7; layer = 1 + j % 3
            gid = (system << 56) | (i + 1)
            sensors[gid] = (system, layer)
            measurements.append({"index": i, "geometry_id": gid, "particles": [pid(owner)],
                                 "dimension": 1 if system >= 6 else 2,
                                 "values": [0.] if system >= 6 else [0., 0.],
                                 "variance": [.01] if system >= 6 else [.01, .01]})
    row = {"event": event, "generated": particles,
           "simulated_particles": [{"id": pid(i)} for i in range(1, 5)],
           "measurements": measurements, "ckf_input_measurements": len(measurements),
           "spacepoints": [], "seeds": [], "estimated_seeds": [], "estimated_hypotheses": [],
           "sample_fingerprints": {k: str(event % 10) * 64 for k in ("generated", "simulated", "hits")},
           "ckf": [track(0, range(9)), track(1, range(7)), track(2, range(9, 18)),
                   track(3, range(18, 27)), track(4, range(27, 36)),
                   track(5, [0, 1, 2, 9, 10, 11, 27, 28, 29]), track(6, range(6))],
           "ambi": [track(0, range(9)), track(2, range(9, 18)), track(3, range(18, 27)), track(4, range(27, 36))]}
    return row, sensors


class MatchingTest(unittest.TestCase):
    def test_exhaustive_many_particle_partition_and_duplicate_overlap(self):
        row, sensors = fixture()
        result = analyze.classify_event(row, sensors, CONFIG)
        counts = result["counts"]
        key = lambda kind: analyze.count_name("frozen", "ckf", kind)
        self.assertEqual(counts[key("raw")], 7)
        self.assertEqual(counts[key("accepted")], 6)
        self.assertEqual(counts[key("quality_rejected")], 1)
        self.assertEqual(counts[key("eligible_generated")], 3)
        self.assertEqual(counts[key("out_of_scope_generated")], 1)
        self.assertEqual(counts[key("simulated_secondary")], 1)
        self.assertEqual(counts[key("fake")], 1)
        self.assertEqual(counts[key("duplicates")], 1)
        self.assertEqual(counts[key("fake_event")], 1)
        self.assertEqual(sum(counts[key(c)] for c in analyze.CATEGORIES), counts[key("accepted")])
        stem = analyze.count_name("frozen", "ckf", "eff", "inclusive", "fiducial")
        self.assertEqual((counts[stem + "/num"], counts[stem + "/den"]), (2, 2))
        for scope in ("hardscatter", "pileup"):
            stem = analyze.count_name("frozen", "ckf", "eff", scope, "fiducial")
            self.assertEqual((counts[stem + "/num"], counts[stem + "/den"]), (1, 1))

    def test_deterministic_overlap_and_representative_ties(self):
        row, sensors = fixture()
        # Two 9-hit particles: 5+5 inliers meet both inclusive 0.5 thresholds.
        row["ckf"] = [track(9, [0, 1, 2, 3, 4, 9, 10, 11, 12, 13]),
                      track(8, range(9), chi2=10.), track(7, range(9), chi2=10.)]
        result = analyze.classify_event(row, sensors, CONFIG)
        by_index = {t["index"]: t for t in result["candidates"]["ckf"]}
        self.assertEqual(by_index[9]["winner"], pid(1))
        self.assertTrue(by_index[9]["representative"]["frozen"])  # most inliers wins
        row["ckf"] = row["ckf"][1:]
        result = analyze.classify_event(row, sensors, CONFIG)
        by_index = {t["index"]: t for t in result["candidates"]["ckf"]}
        self.assertTrue(by_index[7]["representative"]["frozen"])  # stable index final tie

    def test_guide_selection_reselects_representative_without_changing_frozen_chain(self):
        row, sensors = fixture()
        row["ckf"] = [track(0, range(9), nHoles=3), track(1, range(8))]
        result = analyze.classify_event(row, sensors, CONFIG)
        by_index = {t["index"]: t for t in result["candidates"]["ckf"]}
        self.assertTrue(by_index[0]["representative"]["frozen"])
        self.assertFalse(by_index[0]["guide"])
        self.assertTrue(by_index[1]["representative"]["guide"])
        self.assertEqual(result["counts"]["guide/ckf/selection_rejected"], 1)

    def test_zero_track_event_stays_in_truth_denominator(self):
        row, sensors = fixture()
        row["ckf"] = []; row["ambi"] = []
        result = analyze.classify_event(row, sensors, CONFIG)
        self.assertEqual(result["counts"]["frozen/ambi/eff/inclusive/fiducial/den"], 2)
        self.assertEqual(result["counts"]["frozen/ambi/eff/inclusive/fiducial/num"], 0)
        self.assertEqual(result["counts"]["frozen/ambi/fake_event"], 0)

    def test_pure_seed_coverage_is_unique_particle_and_requires_three_pixel_groups(self):
        row, sensors = fixture()
        row["seeds"] = [{"measurements": links} for links in ([0, 1, 2], [0, 1, 2], [0, 10, 20], [0, 1])]
        row["estimated_seeds"] = [{"measurements": [9, 10, 11]}]
        result = analyze.classify_event(row, sensors, CONFIG)
        self.assertEqual(result["counts"]["seeding/seeds/raw"], 4)
        self.assertEqual(result["counts"]["seeding/seeds/eff/inclusive/fiducial/num"], 1)
        self.assertEqual(result["counts"]["seeding/seeds/eff/hardscatter/fiducial/num"], 1)
        self.assertEqual(result["counts"]["seeding/seeds/eff/pileup/fiducial/num"], 0)
        self.assertEqual(result["counts"]["seeding/estimated_seeds/eff/pileup/fiducial/num"], 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "event.npz"; analyze.pack_event(row, path)
            replay = analyze.classify_event(analyze.unpack_event(path), sensors, CONFIG)
            self.assertEqual(result, replay)

    def test_seed_control_rejects_nonpixel_or_absent_source_links(self):
        row, sensors = fixture()
        for links in ([0, 1, 3], [99999]):
            row["seeds"] = [{"measurements": links}]
            with self.assertRaisesRegex(ValueError, "Nonpixel seed|absent measurement"):
                analyze.classify_event(row, sensors, CONFIG)

    def test_fiducial_before_hits_and_conditional_controls(self):
        row, sensors = fixture()
        row["generated"].append(particle(5))  # no measurements
        row["generated"].append(particle(6, charge=0.))
        result = analyze.classify_event(row, sensors, CONFIG)
        self.assertEqual(result["counts"]["frozen/ambi/eff/inclusive/fiducial/den"], 3)
        self.assertEqual(result["counts"]["frozen/ambi/eff/inclusive/guide9/den"], 2)
        self.assertEqual(result["counts"]["frozen/ambi/eff/inclusive/reconstructable/den"], 2)

    def test_truth_profile_overflow_remains_in_global_denominator(self):
        row, sensors = fixture()
        row["generated"][0]["pt"] = 2000.
        result = analyze.classify_event(row, sensors, CONFIG)
        self.assertEqual(result["counts"]["frozen/ambi/eff/hardscatter/fiducial/den"], 1)
        self.assertEqual(result["counts"]["frozen/ambi/effprofile/hardscatter/pt/outside/den"], 1)
        self.assertEqual(result["counts"]["frozen/ambi/effprofile/hardscatter/pt/outside/num"], 1)

    def test_invalid_covariance_and_wrong_charge_retained(self):
        row, sensors = fixture()
        row["ckf"] = [track(0, range(9), covariance_positive_definite=False),
                      track(1, range(9), parameters=[0., 0., .3, 1.4, -.1, 0.])]
        result = analyze.classify_event(row, sensors, CONFIG)
        self.assertEqual(result["counts"]["frozen/ckf/quality_rejected"], 1)
        self.assertEqual(result["counts"]["frozen/ckf/wrong_charge"], 1)

    def test_native_count_mismatch_allowed_only_after_frozen_quality_rejection(self):
        row, sensors = fixture()
        row["ckf"] = [track(0, range(6), nMeasurements=7)]
        result = analyze.classify_event(row, sensors, CONFIG)
        self.assertEqual(result["counts"]["frozen/ckf/quality_rejected"], 1)
        self.assertEqual(result["counts"]["frozen/ckf/raw_inlier_count_mismatch"], 1)
        self.assertEqual(result["counts"]["frozen/ckf/quality_rejected_inlier_count_mismatch"], 1)
        row["ckf"] = [track(0, range(9), nMeasurements=10)]
        with self.assertRaisesRegex(ValueError, "Accepted candidate nMeasurements"):
            analyze.classify_event(row, sensors, CONFIG)

    def test_ambiguity_checked_before_quality_and_repeated_links(self):
        row, sensors = fixture()
        row["ambi"] = [track(0, range(9), reference=False), track(1, range(9))]
        with self.assertRaisesRegex(ValueError, "Unconverged"):
            analyze.classify_event(row, sensors, CONFIG)
        row["ambi"] = [track(0, [0, 1, 2, 3, 4, 5, 6], shared_measurements=[0, 0, 0]),
                       track(1, [0, 9, 10, 11, 12, 13, 14], shared_measurements=[0])]
        self.assertEqual(analyze.shared_max(row["ambi"]), 3)

    def test_missing_unknown_or_duplicate_inputs_rejected(self):
        row, sensors = fixture()
        for mutate in (lambda r: r.update(ckf_input_measurements=0),
                       lambda r: r["measurements"][0].update(particles=[pid(999)]),
                       lambda r: r["generated"][0].pop("hard_scatter"),
                       lambda r: r["ckf"][0].update(nMeasurements=10)):
            modified = copy.deepcopy(row); mutate(modified)
            with self.assertRaises((ValueError, KeyError)):
                analyze.classify_event(modified, sensors, CONFIG)

    def test_numeric_event_chunk_replays_all_classifications(self):
        row, sensors = fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "event.npz"
            analyze.pack_event(row, path)
            unpacked = analyze.unpack_event(path)
            self.assertEqual(analyze.classify_event(row, sensors, CONFIG), analyze.classify_event(unpacked, sensors, CONFIG))
            with np.load(path, allow_pickle=False) as arrays:
                self.assertTrue(all(array.dtype.kind != "O" for array in arrays.values()))

    def test_numeric_chunk_decompresses_each_array_once(self):
        row, _ = fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "event.npz"; analyze.pack_event(row, path)
            original_load = np.load; reads = {}
            class CountingArchive:
                def __enter__(self):
                    self.archive = original_load(path, allow_pickle=False)
                    self.files = self.archive.files
                    return self
                def __exit__(self, *args):
                    self.archive.close()
                def __getitem__(self, key):
                    reads[key] = reads.get(key, 0) + 1
                    return self.archive[key]
            with mock.patch.object(analyze.np, "load", return_value=CountingArchive()):
                analyze.unpack_event(path)
            self.assertTrue(reads)
            self.assertTrue(all(count == 1 for count in reads.values()))

    def test_case_accumulator_discards_candidate_and_particle_payloads(self):
        row, sensors = fixture()
        full = analyze.classify_event(row, sensors, CONFIG)
        compact = analyze.sufficient_record(full)
        self.assertEqual(set(compact), {"event", "counts", "ambiguity_shared_max"})
        self.assertIs(compact["counts"], full["counts"])
        self.assertNotIn("candidates", compact); self.assertNotIn("particles", compact)


class InferenceTest(unittest.TestCase):
    def test_ratio_of_sums_and_event_block_weights(self):
        weights = analyze.bootstrap_weights(2, 2000)
        self.assertTrue(np.all(weights.sum(axis=1) == 2))
        result = analyze.ratio_estimate([1, 90], [1, 100], weights)
        self.assertAlmostEqual(result["value"], 91/101)
        self.assertNotAlmostEqual(result["value"], (.9 + 1)/2)
        np.testing.assert_array_equal(weights, analyze.bootstrap_weights(2, 2000))

    def test_joint_pairing_preserves_difference_and_flags_degeneracy(self):
        weights = analyze.bootstrap_weights(3, 2000)
        result = analyze.ratio_estimate([1, 5, 3], [2, 10, 6], weights, ([0, 0, 0], [2, 10, 6]))
        self.assertEqual(result["paired_delta"]["event_bootstrap95"], [.5, .5])
        self.assertTrue(result["paired_delta"]["bootstrap_degenerate"])
        self.assertFalse(result["paired_delta"]["reference_self"])

    def test_empty_candidate_denominator_and_zero_fake_event_limit(self):
        weights = analyze.bootstrap_weights(100, 2000)
        result = analyze.ratio_estimate(np.zeros(100, dtype=int), np.zeros(100, dtype=int), weights)
        self.assertIsNone(result["value"]); self.assertIsNone(result["event_bootstrap95"])
        self.assertEqual(result["defined_resamples"], 0)
        self.assertAlmostEqual(1 - .05**.01, .029513049607039932)
        self.assertIsNotNone(analyze.wilson(0, 100))

    def test_full_metric_matrix_and_incomplete_pairing_rejection(self):
        row, sensors = fixture()
        records = [analyze.classify_event(row, sensors, CONFIG)]
        row = copy.deepcopy(row); row["event"] = 1; row["ckf"] = []; row["ambi"] = []
        records.append(analyze.classify_event(row, sensors, CONFIG))
        names = sorted(records[0]["counts"])
        arrays = {"event": np.array([0, 1]), "metric_names": np.array(names),
                  "counts": np.array([[r["counts"][n] for n in names] for r in records])}
        cases = {pitch: copy.deepcopy(arrays) for pitch in analyze.PITCHES}
        report = analyze.summarize_cases(cases, 2000)
        self.assertEqual(report["cases"]["2"]["metrics"]["frozen/ambi/eff/inclusive/fiducial"]["value"], .5)
        self.assertTrue(report["cases"]["2"]["metrics"]["frozen/ambi/fake_event"]["bootstrap_degenerate"])
        self.assertAlmostEqual(report["cases"]["2"]["metrics"]["frozen/ambi/fake_event"]["zero_event_one_sided95_upper"], 1 - .05**.5)
        self.assertIn("candidate fake fractions", analyze.markdown(report))
        cases[2.]["event"] = np.array([0, 2])
        with self.assertRaisesRegex(ValueError, "pairing"):
            analyze.summarize_cases(cases, 10)

    def test_pairing_source_mismatch_fails_and_noise_coupling_is_counted(self):
        row, sensors = fixture()
        controls = {"event": 0, **analyze.fingerprints(row, sensors)}
        summaries = {p: {"fingerprints": [copy.deepcopy(controls)], "invariant_input_sha256": {},
                        "native_report": {"campaign": CONFIG, "source_revision": "a"*40,
                            "source_sha256": {}, "runtime_sha256": {}, "sample_report_sha256": "b"*64,
                            "seed": 153043, "profile": "pt4-nominal-triplet", "pitch_mm": p}} for p in analyze.PITCHES}
        for summary in summaries.values():
            summary["original_native_identity_sha256"] = analyze.native_identity(summary["native_report"])
        summaries[2.]["fingerprints"][0]["non_target"] = "a" * 64
        result = analyze.check_pairing(summaries)
        self.assertEqual(result["cases"]["2"]["control_changed_events"]["non_target"], 1)
        summaries[2.]["fingerprints"][0]["source_hits"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "pairing"):
            analyze.check_pairing(summaries)

    def test_logical_paths_distinguish_roots_and_external_basenames(self):
        paths = [str(analyze.ROOT / 'build/x.so'), str(analyze.ROOT.parent / 'sibling/build/x.so'),
                 '/external-a/build/x.so', '/external-b/build/x.so']
        clean = analyze.sanitize({p: 'digest' for p in paths})
        self.assertEqual(len(clean), 4)
        self.assertIn('repository/build/x.so', clean)
        self.assertIn('workspace/sibling/build/x.so', clean)
        self.assertEqual(len({k for k in clean if k.startswith('external/')}), 2)
        self.assertEqual(analyze.sanitize('--input=' + paths[0]), '--input=repository/build/x.so')

    def test_original_identity_binds_paths_before_sanitation(self):
        report = {'source_revision':'a'*40,'source_sha256':{'/external-a/x.so':'b'*64},
                  'runtime_sha256':{},'sample_report_sha256':'c'*64,'seed':153043,
                  'profile':'pt4-nominal-triplet','campaign':CONFIG}
        changed = copy.deepcopy(report); changed['source_sha256'] = {'/external-b/x.so':'b'*64}
        self.assertNotEqual(analyze.native_identity(report), analyze.native_identity(changed))


class RetentionTest(unittest.TestCase):
    def native_case(self, directory, pitch=.5):
        row, sensors = fixture()
        native_sensors = [{"geometry_id": gid, "ids": {"system": s, "layer": layer},
                           "center_mm": [0., 0., 0.], "u": [1., 0., 0.], "v": [0., 1., 0.]} for gid, (s, layer) in sensors.items()]
        widths = {"groups": [{"volume": s, "index": i, "sigma_mm": .1}
                              for s in range(1, 8) for i in range(1 if s >= 6 else 2)]}
        scaled = copy.deepcopy(widths)
        for group in scaled["groups"]:
            if group["volume"] in (4, 5) and group["index"] == 1:
                group["sigma_mm"] *= pitch / .5
        # Native sigma**2 rather than rounded decimal .01 is the exact gate.
        for m in row["measurements"]:
            m["variance"] = [.1**2] * m["dimension"]
            if sensors[m["geometry_id"]][0] in (4, 5):
                m["variance"][1] = (.1 * pitch / .5)**2
        analyze.write_json(directory / "native-report.json", {"sensors": native_sensors})
        analyze.write_json(directory / "error-table.json", scaled)
        analyze.write_json(directory / "baseline-error-table.json", widths)
        analyze.write_json(directory / "material-map.json", {"fixture": "fixed"})
        analyze.write_json(directory / "pixel-selection.json", {"fixture": "pixel-only"})
        (directory / "events.jsonl.gz").write_bytes(gzip.compress(analyze.canonical(row) + b"\n", mtime=0))
        fixture_config = copy.deepcopy(CONFIG)
        fixture_config["ttbar_pileup"] = {"hard_process": ["fixture_process"], "pileup": 200,
            "cms_energy_GeV": 14000., "vertex_sigma_mm": [.0125, .0125, 55.5],
            "reconstruction_hypothesis": "muon"}
        report = {"outcome": "completed", "events": 1, "campaign": fixture_config, "pitch_mm": pitch,
                  "gbts_statistics": {"effective_configuration": {"z0_range_mm": [-15., 15.]},
                      "graph_audit": {"edge_cap": 2000000, "cap_reached_events": 1,
                          "log_sha256": "d"*64, "events": [{"event": 0, "edges": 2000000,
                              "edge_links": 12346, "cap_reached": True}]}},
                  "source_revision": "a"*40, "source_sha256": {}, "runtime_sha256": {},
                  "sample_report_sha256": "b"*64, "seed": 153043, "profile": "pt4-nominal-triplet",
                  "output_sha256": {name: analyze.sha256(directory / name) for name in ("native-report.json", "error-table.json", "events.jsonl.gz")}}
        analyze.write_json(directory / "run-report.json", report)

    def test_actual_synthetic_retention_audit_replay_and_tamper_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"; source.mkdir()
            target = Path(directory) / "retained"
            self.native_case(source)
            result = analyze.retain_case(source, target, 1)
            self.assertEqual(result["events"], 1)
            self.assertGreater(result["measurement_audit"]["variance_marginals"], 0)
            self.assertEqual(analyze.replay_case(target), result)
            with (target / "audit/event-000000.npz").open("ab") as stream:
                stream.write(b"tamper")
            with self.assertRaisesRegex(ValueError, "chunk changed"):
                analyze.replay_case(target)

    def test_four_case_statistics_markdown_exact_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for pitch in analyze.PITCHES:
                source = root / f"native{pitch:g}"; source.mkdir(); self.native_case(source, pitch)
                analyze.retain_case(source, root / "data" / f"pitch{pitch:g}", 1)
            report = analyze.campaign(root / "data", root / "results", 10)
            self.assertEqual(report["bootstrap"]["replicates"], 10)
            self.assertEqual(report["benchmark"]["gbts_z0_range_mm"], [-15., 15.])
            self.assertEqual(report["benchmark"]["hard_process"], ["fixture_process"])
            self.assertEqual(report["benchmark"]["gbts_graph_audit"]["2"]["cap_reached_events"], 1)
            self.assertEqual(report["benchmark"]["gbts_graph_audit"]["0.5"]["edge_links_min"], 12346)
            self.assertEqual(analyze.campaign(root / "data", root / "results", 10, verify=True), report)
            (root / "results/results.md").write_text("tamper")
            with self.assertRaisesRegex(ValueError, "replay differs"):
                analyze.campaign(root / "data", root / "results", 10, verify=True)


if __name__ == "__main__":
    unittest.main()
