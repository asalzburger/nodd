"""Focused regression gates; no detector or native installation required."""
import copy
from contextlib import redirect_stdout, redirect_stderr
import gzip
import io
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import campaign
import runtime


class RuntimeTests(unittest.TestCase):
    def test_matrix_identity_and_frozen_configuration(self):
        cases = runtime.cases()
        self.assertEqual(len(cases), 80)
        self.assertEqual(len({c["case_id"] for c in cases}), 80)
        self.assertEqual({c["events"] for c in cases}, {1000})
        for case in cases:
            config, path = runtime.configuration(case)
            frozen = json.loads(path.read_text())
            reconstructed = copy.deepcopy(config)
            reconstructed.pop("strixel_crosscheck")
            reconstructed["particle"] = frozen["particle"]
            reconstructed["simulation"] = frozen["simulation"]
            self.assertEqual(reconstructed, frozen)
            self.assertEqual(config["profiles"][runtime.PROFILE],
                {"seed_finder": {"minPt": .4, "minSeedLevel": 2, "addTriplets": True,
                 "maxAbsEtaAddTriplets": 4.1, "z0HistogramMaxBarrelOrder": -1}})

    def test_only_coarse_strixel_sigma_scales(self):
        sensors = [{"geometry_id": system << 56, "ids": {"system": system}} for system in range(1, 8)]
        table = {"groups": [{"volume": system, "index": index, "sigma_mm": .1 + system,
            "mean_mm": .25, "uncentered_rms_mm": 2.5, "entries": 20}
            for system in range(1, 8) for index in ([0, 1] if system < 6 else [0])]}
        original = copy.deepcopy(table)
        for pitch in runtime.PITCHES:
            scaled, volumes = runtime.scale_widths(table, sensors, pitch)
            self.assertEqual(volumes, [4, 5])
            for before, after in zip(table["groups"], scaled["groups"]):
                expected = copy.deepcopy(before)
                if before["volume"] in (4, 5) and before["index"] == 1:
                    expected["sigma_mm"] *= pitch / .5
                self.assertEqual(after, expected)
        self.assertEqual(table, original)
        self.assertEqual(runtime.scale_widths(table, sensors, .5)[0], original)

    def test_baseline_gate_requires_all_confirmation_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "output"; output.mkdir()
            supplier = root / "supplier"
            frozen = supplier / "build/tracker-resolution-optimization/confirmation/gaussian/balanced-pt10"
            frozen.mkdir(parents=True)
            for name in runtime.BASELINE_FILES:
                runtime.write_json(output / name, {"value": 2.})
                runtime.write_json(frozen / name, {"value": 2.})
            self.assertTrue(all(v["matched"] for v in runtime.baseline_gate(output, supplier).values()))
            (frozen / "digitization.json").unlink()
            with self.assertRaisesRegex(RuntimeError, "unavailable"):
                runtime.baseline_gate(output, supplier)
            runtime.write_json(frozen / "digitization.json", {"value": 3.})
            with self.assertRaisesRegex(RuntimeError, "before scaling"):
                runtime.baseline_gate(output, supplier)

    def test_baseline_geometry_tolerance_is_scoped(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); output = root / "output"; output.mkdir()
            supplier = root / "supplier"
            frozen = supplier / "build/tracker-resolution-optimization/confirmation/gaussian/balanced-pt10"
            frozen.mkdir(parents=True)
            for name in runtime.BASELINE_FILES:
                runtime.write_json(output / name, {"value": 2.})
                runtime.write_json(frozen / name, {"value": 2. + (1.e-10 if name == "selection.json" else 0)})
            runtime.baseline_gate(output, supplier)
            runtime.write_json(frozen / "error-table.json", {"value": 2. + 1.e-10})
            with self.assertRaisesRegex(RuntimeError, "error-table"):
                runtime.baseline_gate(output, supplier)

    def test_hit_writer_appends_without_moving_existing_slots(self):
        class Sequence:
            def __init__(self, **unused): self.calls = []
            def addWriter(self, writer): self.calls.append(writer)
            def addAlgorithm(self, algorithm): self.calls.append(algorithm)
            def run(self): return self.calls
        root = SimpleNamespace(RootSimHitWriter=lambda **settings: ("hits", settings))
        acts = SimpleNamespace(examples=SimpleNamespace(Sequencer=Sequence), logging=SimpleNamespace(WARNING=3))
        with patch.dict("sys.modules", {"acts.examples.root": root}):
            proxy = runtime.append_hit_writer(acts, Path("/test"))
            sequence = proxy.examples.Sequencer(events=1)
            sequence.addAlgorithm("gun"); sequence.addAlgorithm("digitizer")
            self.assertEqual(sequence.run(), ["gun", "digitizer", ("hits", {
                "level": 3, "inputSimHits": "simhits", "filePath": "/test/hits.root", "treeName": "hits"})])
        self.assertIs(acts.examples.Sequencer, Sequence)

    def test_all_event_and_ambiguity_gates_before_scoring(self):
        native = {"sensors": [{"geometry_id": 1, "ids": {"system": 1, "layer": 1}}]}
        config = {"ambiguity": {"maximum_shared_hits": 3}}
        analyzer = SimpleNamespace(species=SimpleNamespace(audit_event=lambda *a: None),
            classify_event=lambda *a: None, ambiguity_shared_max=lambda tracks: len(tracks))
        def row(event, tracks=0):
            return {"event": event, "ambi": [0] * tracks, "ckf": [], "measurements": [], "spacepoints": []}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "events.jsonl.gz"
            def save(rows):
                with gzip.open(path, "wt") as stream:
                    for item in rows: stream.write(json.dumps(item) + "\n")
            save([row(0), row(1)])
            self.assertTrue(runtime.audit_events(path, native, config, analyzer, 2, {})["all_generated_events_retained"])
            save([row(0), row(0)])
            with self.assertRaisesRegex(RuntimeError, "Duplicate"):
                runtime.audit_events(path, native, config, analyzer, 2, {})
            save([row(0)])
            with self.assertRaisesRegex(RuntimeError, "incomplete"):
                runtime.audit_events(path, native, config, analyzer, 2, {})
            save([row(0, 3), row(1)])
            with self.assertRaisesRegex(RuntimeError, "Unconverged"):
                runtime.audit_events(path, native, config, analyzer, 2, {})

    def test_resume_detects_changed_output_and_case_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary); case = runtime.cases(2)[0]
            self.assertEqual(campaign.status(directory, case), "absent")
            output = directory / case["case_id"]; output.mkdir()
            payload = output / "events.jsonl.gz"; payload.write_bytes(b"fixture")
            report = {**case, "outcome": "completed", "output_sha256": {payload.name: runtime.sha256(payload)}}
            runtime.write_json(output / "run-report.json", report)
            self.assertEqual(campaign.status(directory, case), "completed")
            report["events"] = 10
            runtime.write_json(output / "run-report.json", report)
            self.assertEqual(campaign.status(directory, case), "configuration-mismatch")
            report["events"] = 2
            runtime.write_json(output / "run-report.json", report)
            payload.write_bytes(b"changed")
            self.assertEqual(campaign.status(directory, case), "output-mismatch")

    def test_campaign_parallel_launch_and_verified_resume(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "campaign"
            selected = runtime.cases(2)[:2]
            policy = campaign.scheduling_policy()
            barrier = threading.Barrier(2)
            launched = []
            def native(command, **unused):
                case = next(c for c in selected if c["case_id"] == command[command.index("--case") + 1])
                launched.append(case["case_id"])
                barrier.wait(timeout=5)
                output = Path(command[command.index("--output") + 1]); output.mkdir()
                payload = output / "events.jsonl.gz"; payload.write_bytes(b"fixture")
                runtime.write_json(output / "run-report.json", {**case, "outcome": "completed",
                    "output_sha256": {payload.name: runtime.sha256(payload)}})
                return SimpleNamespace(returncode=0)
            arguments = ["campaign.py", "launch", "--output", str(directory), "--events", "2", "--jobs", "2"]
            for case in selected:
                arguments += ["--case", case["case_id"]]
            with patch("sys.argv", arguments), patch("campaign.scheduling_policy", return_value=policy), patch("campaign.subprocess.run", side_effect=native), redirect_stdout(io.StringIO()):
                campaign.main()
            self.assertCountEqual(launched, [c["case_id"] for c in selected])
            self.assertEqual(json.loads((directory / "campaign-plan.json").read_text())["max_parallel_processes"], 2)
            arguments[1] = "resume"
            with patch("sys.argv", arguments), patch("campaign.scheduling_policy", return_value=policy), patch("campaign.subprocess.run") as native, redirect_stdout(io.StringIO()):
                campaign.main()
                native.assert_not_called()
            # The same output can never be implicitly overwritten by launch.
            arguments[1] = "launch"
            with patch("sys.argv", arguments), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                campaign.main()

    def test_cost_order_is_deterministic_and_preserves_matrix(self):
        cases = runtime.cases()
        policy = campaign.scheduling_policy()
        ordered = campaign.ordered(cases, policy)
        self.assertCountEqual(ordered, cases)
        self.assertEqual(ordered, campaign.ordered(list(reversed(cases)), policy))
        self.assertTrue(all(c["simulation"] == "geant4" and c["particle"] == "electron" and
                            c["pt_GeV"] == 100 for c in ordered[:4]))
        self.assertEqual(len(policy["estimates"]), 20)


if __name__ == "__main__":
    unittest.main()
