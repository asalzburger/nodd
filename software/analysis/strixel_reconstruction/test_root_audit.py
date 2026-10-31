"""Synthetic ROOT composition and adverse provenance/coverage checks."""
from contextlib import redirect_stderr, redirect_stdout
import copy
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import awkward as ak
import numpy as np
import uproot

import root_audit


class RootAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root_audit.source_gate()
        cls.analysis = root_audit.validator_module()
        cls.runtime = root_audit.load_module("root_audit_fixture_runtime",
            root_audit.ROOT / "software/analysis/strixel_reconstruction/runtime.py")
        cls.contract = cls.analysis.frozen_contract()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="root-audit-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.native, self.data = self.base / "native", self.base / "data"
        self.native.mkdir(); self.data.mkdir()
        self.inventory = {"schema_version": 1, "input_revision": self.analysis.INPUT_REVISION,
            "retention_source_sha256": root_audit.SOURCES["software/analysis/strixel_reconstruction/analyze.py"],
            "native_analyzer_sha256": self.analysis.NATIVE_ANALYZER_SHA256,
            "frozen_contract": self.contract, "reports": []}
        for pitch in self.runtime.PITCHES:
            self.make_case(pitch)
        self.save_inventory()

    def write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(root_audit.canonical(value) + b"\n")

    def write_gzip(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(root_audit.canonical(value) + b"\n", mtime=0))

    def save_inventory(self):
        self.write_gzip(self.data / "native-reports.json.gz", self.inventory)

    def make_case(self, pitch):
        case = next(c for c in self.runtime.cases(2) if c["simulation"] == "fatras" and
                    c["particle"] == "muon" and c["pt_GeV"] == 10 and c["pitch_mm"] == pitch)
        name = case["case_id"]; native = self.native / name; native.mkdir()
        target = self.data / "cases" / name; target.mkdir(parents=True)
        config, unused = self.runtime.configuration(case)
        widths = {"groups": [{"volume": 1, "index": 0, "sigma_mm": .1}]}
        configs = {"error-table.json": widths, "digitization.json": {"fixture": "unchanged"},
                   "gbts/config.json": {}, "volume_system": {"1": 1}}
        prepared_names = ("selection.json", "material-map.json", "native-report.json", "pixel-selection.json",
                          "gbts/config.json", "gbts/mapping.csv", "gbts/layers.csv", "gbts/connections.csv")
        for filename in prepared_names:
            self.write_json(native / filename, configs.get(filename, {"fixture": "fixed"}))
        for filename in ("error-table.json", "digitization.json"):
            self.write_json(native / filename, configs[filename])
        (native / "events.jsonl.gz").write_bytes(gzip.compress(b"{}\n", mtime=0))
        truth = np.asarray([[0., 0., 0., 1., .1, 0.]] * 2)
        reco = truth.copy(); reco[1] = np.nan
        variance = np.ones((2, 6)); variance[1] = np.nan
        arrays = {"event": np.arange(2), "truth": truth}
        for stage in ("ckf", "ambi"):
            arrays.update({stage + "_raw": np.asarray([1, 0]), stage + "_matched": np.asarray([1, 0]),
                stage + "_reco": reco, stage + "_variance": variance,
                stage + "_residual": truth - reco, stage + "_pull": (truth - reco) / np.sqrt(variance)})
            tracks = {"event_nr": np.asarray([0, 1], dtype=np.uint32),
                      "track_nr": ak.Array([[0], []])}
            for index, parameter in enumerate(("LOC0", "LOC1", "PHI", "THETA", "QOP", "T")):
                tracks["e" + parameter + "_fit"] = ak.values_astype(ak.Array([[truth[0, index]], []]), np.float32)
                tracks["err_e" + parameter + "_fit"] = ak.values_astype(ak.Array([[1.], []]), np.float32)
            with uproot.recreate(native / ("tracksummary_" + stage + ".root")) as output:
                output["tracksummary"] = tracks
        for key in self.analysis.FINGERPRINTS:
            arrays["fingerprint_" + key] = np.asarray(["0" * 64] * 2)
        np.savez_compressed(target / "events.npz", **arrays)
        with uproot.recreate(native / "hits.root") as output:
            output["hits"] = {"event_id": np.arange(2, dtype=np.uint32)}
        self.write_measurements(native, .1 ** 2)
        report = {**case, "outcome": "completed", "source_revision": root_audit.INPUT_REVISION,
            "input_revision": self.analysis.INPUT_REVISION, "profile": self.runtime.PROFILE,
            "campaign": config, "source_sha256": {str(root_audit.ROOT / relative): root_audit.SOURCES[relative]
                for relative in ("software/analysis/strixel_reconstruction/runtime.py",
                                 "software/analysis/strixel_reconstruction/campaign.py")},
            "runtime_sha256": {}, "baseline_input_sha256": {}, "supplier_identity": {},
            "postrun_immutability": {key: True for key in ("source", "native_supplier_runtime", "prepared_inputs")},
            "baseline_equivalence": {key: {"matched": True} for key in self.runtime.BASELINE_FILES},
            "event_audit": {"all_generated_events_retained": True, "all_native_survivors_converged": True},
            "gbts_statistics": {"particle_configuration": self.contract["species"]["muon"],
                "effective_configuration": self.contract["effective_gbts_configuration"],
                "effective_two_way": True, "events": 2, "mapped_spacepoints": 0, "input_spacepoints": 0},
            "prepared_input_sha256": {filename: root_audit.digest(native / filename)
                for filename in (*prepared_names, "error-table.json", "digitization.json")},
            "output_sha256": {p.name: root_audit.digest(p) for p in native.iterdir() if p.is_file()}}
        self.write_json(native / "run-report.json", report)
        summary = {"events": 2, "pt_GeV": 10., "seed": case["seed"], "profile": self.runtime.PROFILE,
            "native_source_revision": report["source_revision"],
            "run_report_sha256": root_audit.digest(native / "run-report.json"),
            "events_sha256": report["output_sha256"]["events.jsonl.gz"],
            "stage_counts": {"measurements": 2},
            "stages": {stage: {"counts": {"raw": 1, "matched": 1}} for stage in ("ckf", "ambi")}}
        self.write_gzip(target / "summary.json.gz", summary)
        self.write_gzip(target / "configuration.json.gz", configs)
        self.inventory["reports"].append({"case": name, "report": self.analysis.sanitize(report),
            "run_report_sha256": root_audit.digest(native / "run-report.json"),
            "native_summary_sha256": self.analysis.fingerprint(summary),
            "events_file": f"cases/{name}/events.npz", "summary_file": f"cases/{name}/summary.json.gz",
            "configuration_file": f"cases/{name}/configuration.json.gz",
            "files": {str(path.relative_to(self.data)): root_audit.digest(path) for path in target.iterdir()}})

    def write_measurements(self, native, variance):
        with uproot.recreate(native / "measurements.root") as output:
            output["measurements"] = {"volume_id": np.ones(2, dtype=np.uint32),
                "var_loc0": np.full(2, variance, dtype=np.float32),
                "var_loc1": np.full(2, np.nan, dtype=np.float32), "clus_size": np.zeros(2, dtype=np.uint32)}

    def rebind_root_file(self, item, filename):
        native = self.native / item["case"]
        report = json.loads((native / "run-report.json").read_text())
        report["output_sha256"][filename] = root_audit.digest(native / filename)
        self.write_json(native / "run-report.json", report)
        item["run_report_sha256"] = root_audit.digest(native / "run-report.json")
        item["report"] = self.analysis.sanitize(report)
        summary = root_audit.read_gzip(self.data / item["summary_file"])
        summary["run_report_sha256"] = item["run_report_sha256"]
        self.write_gzip(self.data / item["summary_file"], summary)
        item["native_summary_sha256"] = self.analysis.fingerprint(summary)
        item["files"][item["summary_file"]] = root_audit.digest(self.data / item["summary_file"])
        self.save_inventory()

    def test_composed_frozen_audit_preserves_zero_track_events_and_inputs(self):
        before = {str(path): root_audit.digest(path) for root in (self.native, self.data)
                  for path in root.rglob("*") if path.is_file()}
        with redirect_stdout(io.StringIO()):
            result = root_audit.compose_audit(self.native, self.data, pilot=True)
        self.assertEqual(result["case_count"], 4)
        self.assertEqual(result["status"], "PASS")
        for case in result["frozen_audit"]["cases"].values():
            self.assertEqual(case["checked_variance_marginals"], 2)
            self.assertEqual(case["stages"]["ckf"]["events"], 2)
            self.assertEqual(case["stages"]["ckf"]["candidates"], 1)
            self.assertEqual(case["stages"]["ckf"]["matched_parameter_marginals"], 6)
        self.assertEqual(before, {path: root_audit.digest(path) for path in before})

    def test_production_rejects_incomplete_matrix_before_root_audit(self):
        with self.assertRaisesRegex(ValueError, "exact 80-case"):
            root_audit.compose_audit(self.native, self.data)

    def test_bad_native_report_reference_binding_is_rejected(self):
        self.inventory["reports"][0]["run_report_sha256"] = "0" * 64
        self.save_inventory()
        with self.assertRaisesRegex(ValueError, "reference binding"):
            root_audit.compose_audit(self.native, self.data, pilot=True)

    def test_missing_root_and_unreported_root_are_rejected(self):
        item = self.inventory["reports"][0]
        case = self.native / item["case"]
        (case / "unreported.root").write_bytes(b"fixture")
        with self.assertRaisesRegex(ValueError, "ROOT output coverage"):
            root_audit.compose_audit(self.native, self.data, pilot=True)
        (case / "unreported.root").unlink()
        (case / "tracksummary_ambi.root").unlink()
        with self.assertRaisesRegex(ValueError, "ROOT output coverage"):
            root_audit.compose_audit(self.native, self.data, pilot=True)

    def test_rebound_wrong_variance_still_fails_frozen_independent_audit(self):
        item = self.inventory["reports"][0]
        self.write_measurements(self.native / item["case"], .02)
        self.rebind_root_file(item, "measurements.root")
        with self.assertRaisesRegex(ValueError, "Persisted ROOT variance changed"), redirect_stdout(io.StringIO()):
            root_audit.compose_audit(self.native, self.data, pilot=True)

    def test_current_source_is_checked_against_declared_native_commit(self):
        report = copy.deepcopy(self.inventory["reports"][0]["report"])
        # Restore an absolute path because the actual native report is checked.
        report["source_sha256"] = {str(root_audit.ROOT / relative): value for relative, value in
            root_audit.SOURCES.items() if relative.endswith(("runtime.py", "campaign.py"))}
        self.assertEqual(root_audit.declared_source_binding([report]), root_audit.INPUT_REVISION)
        report["source_sha256"][str(root_audit.ROOT / "software/analysis/strixel_reconstruction/runtime.py")] = "0" * 64
        with self.assertRaisesRegex(ValueError, "declared commit"):
            root_audit.declared_source_binding([report])

    def test_cli_refuses_overwrite_and_verifies_exact_reaudit(self):
        output = self.base / "audit.json"
        arguments = ["root_audit.py", "--native", str(self.native), "--data", str(self.data),
                     "--output", str(output), "--pilot"]
        with patch("sys.argv", arguments), redirect_stdout(io.StringIO()):
            root_audit.main()
        with patch("sys.argv", arguments), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            root_audit.main()
        with patch("sys.argv", arguments + ["--verify"]), redirect_stdout(io.StringIO()):
            root_audit.main()
        payload = json.loads(output.read_text()); payload["case_count"] = 80
        self.write_json(output, payload)
        with patch("sys.argv", arguments + ["--verify"]), redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "Exact ROOT re-audit"):
            root_audit.main()


if __name__ == "__main__":
    unittest.main()
