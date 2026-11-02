import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("ttbar_campaign", Path(__file__).with_name("campaign.py"))
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)


class CampaignBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.expected = {"events": 100, "seed": 153042, "source_revision": "a" * 40}

    def case(self, name, pitch=None):
        directory = self.root / name
        directory.mkdir()
        data = directory / "audit.dat"
        data.write_bytes(b"retained native evidence\n")
        report = {**self.expected, "outcome": "completed",
                  "output_sha256": {"audit.dat": campaign.sha256(data)}}
        if pitch is not None:
            report.update(pitch_mm=pitch,
                          sample_report_sha256=campaign.sha256(self.root / "sample/run-report.json"))
        campaign.write_json(directory / "run-report.json", report)
        return directory, report

    def test_complete_pairing_and_tampered_native_evidence(self):
        self.case("sample")
        for pitch in campaign.PITCHES:
            self.case(f"pitch{pitch:g}", pitch)
        self.assertEqual(campaign.verify(self.root, self.expected)["status"], "PASS")
        (self.root / "pitch1/audit.dat").write_bytes(b"altered")
        with self.assertRaisesRegex(ValueError, "Output hash differs"):
            campaign.verify(self.root, self.expected)

    def test_rebound_to_different_shared_sample_rejected(self):
        self.case("sample")
        for pitch in campaign.PITCHES:
            directory, report = self.case(f"pitch{pitch:g}", pitch)
        report["sample_report_sha256"] = "0" * 64
        campaign.write_json(directory / "run-report.json", report)
        with self.assertRaisesRegex(ValueError, "another sample"):
            campaign.verify(self.root, self.expected)

    def test_external_sample_preserves_generation_revision_and_binds_report(self):
        directory, report = self.case("sample")
        report["kind"] = "generate"
        campaign.write_json(directory / "run-report.json", report)
        shared = {"directory": str(directory), "source_revision": report["source_revision"],
                  "report_sha256": campaign.sha256(directory / "run-report.json")}
        self.expected["source_revision"] = "b" * 40
        expected = {**self.expected, "shared_sample": shared}
        for pitch in campaign.PITCHES:
            self.case(f"pitch{pitch:g}", pitch)
        self.assertEqual(campaign.verify(self.root, expected)["source_revision"], "b" * 40)
        self.assertEqual(json.loads((directory / "run-report.json").read_text())["source_revision"], "a" * 40)
        report["new_metadata"] = "changed after plan"
        campaign.write_json(directory / "run-report.json", report)
        with self.assertRaisesRegex(ValueError, "External sample report changed"):
            campaign.checked_sample(self.root, expected)

    def test_external_sample_never_launches_generation_and_still_checks_seed(self):
        directory, report = self.case("sample")
        report["kind"] = "generate"
        campaign.write_json(directory / "run-report.json", report)
        expected = {**self.expected, "source_revision": "b" * 40,
                    "supplier_root": "/tmp/supplier", "runtime_root": "/tmp/runtime",
                    "native_dir": "/tmp/native", "fatras_native_dir": "/tmp/fatras",
                    "source_sha256": {}, "shared_sample": {
                        "directory": str(directory), "source_revision": "a" * 40,
                        "report_sha256": campaign.sha256(directory / "run-report.json")}}
        new = self.root / "fresh"
        launched = []
        def native(command, log):
            launched.append(command)
            self.assertIn("reconstruct", command)
            self.assertEqual(command[command.index("--sample") + 1], str(directory))
            raise RuntimeError("fixture stops after first reconstruction")
        args = SimpleNamespace(action="launch", output=new, jobs=1)
        with patch.object(campaign, "plan", return_value=expected), patch.object(campaign, "launch_process", side_effect=native):
            with self.assertRaisesRegex(RuntimeError, "fixture stops"):
                campaign.execute(args)
        self.assertEqual(len(launched), 1)
        with self.assertRaisesRegex(ValueError, "identity differs"):
            campaign.checked_sample(new, {**expected, "seed": 153043})

    def test_failed_wrong_seed_and_missing_outputs_rejected(self):
        directory, report = self.case("sample")
        for key, value, message in (("outcome", "failed", "Failed/incomplete"),
                                    ("seed", 153043, "identity differs"),
                                    ("output_sha256", {}, "Missing output")):
            changed = {**report, key: value}
            campaign.write_json(directory / "run-report.json", changed)
            with self.assertRaisesRegex(ValueError, message):
                campaign.report_check(directory, self.expected)

    def test_output_path_cannot_escape_case(self):
        directory, report = self.case("sample")
        report["output_sha256"] = {"../outside": "0" * 64}
        campaign.write_json(directory / "run-report.json", report)
        with self.assertRaisesRegex(ValueError, "Output hash differs"):
            campaign.report_check(directory, self.expected)

    def test_native_failure_preserves_log_and_refuses_overwrite(self):
        log = self.root / "failed.log"
        with patch.object(campaign.shutil, "disk_usage", return_value=SimpleNamespace(free=10 * 1024**3)):
            with self.assertRaisesRegex(RuntimeError, "exited3"):
                campaign.launch_process([sys.executable, "-c", "print('failure evidence');raise SystemExit(3)"], log)
        self.assertIn("failure evidence", log.read_text())
        with patch.object(campaign.shutil, "disk_usage", return_value=SimpleNamespace(free=10 * 1024**3)):
            with self.assertRaises(FileExistsError):
                campaign.launch_process([sys.executable, "-c", "pass"], log)

    def test_low_disk_refuses_launch_before_creating_log(self):
        log = self.root / "capacity.log"
        with patch.object(campaign.shutil, "disk_usage", return_value=SimpleNamespace(free=5 * 1024**3 - 1)):
            with self.assertRaisesRegex(RuntimeError, "Less than5GiB"):
                campaign.launch_process([sys.executable, "-c", "raise SystemExit(99)"], log)
        self.assertFalse(log.exists())

    def test_isolated_fatras_source_mutations_change_campaign_identity(self):
        for name in campaign.SOURCES:
            item = self.root / name
            item.parent.mkdir(parents=True, exist_ok=True)
            item.write_text("original source\n")
        original = campaign.source_identity(self.root)
        directory = "software/source/ActsExamples/StrixelPileupSafeFatras/"
        for name in ("CMakeLists.txt", "Binding.cpp", "TtbarSafeBetheHeitler.hpp",
                     "FailureAudit.hpp", "test_energy_loss.cpp", "test_failure_identity.cpp"):
            item = self.root / directory / name
            item.write_text("changed source\n")
            self.assertNotEqual(original, campaign.source_identity(self.root), name)
            item.write_text("original source\n")

    def test_gbts_source_inventory_additions_and_mutations_change_identity(self):
        for name in campaign.SOURCES:
            item = self.root / name
            item.parent.mkdir(parents=True, exist_ok=True)
            item.write_text("original source\n")
        directory = self.root / "software/source/ActsExamples/StrixelPileupSafeGbts"
        directory.mkdir()
        original = campaign.source_identity(self.root)
        item = directory / "Binding.cpp"
        item.write_text("compiled source\n")
        added = campaign.source_identity(self.root)
        self.assertNotEqual(original, added)
        item.write_text("unrebuilt source\n")
        self.assertNotEqual(added, campaign.source_identity(self.root))

    def test_no_later_case_submitted_after_first_failure(self):
        expected = {**self.expected, "supplier_root": "/tmp/supplier",
                    "runtime_root": "/tmp/runtime", "native_dir": "/tmp/native",
                    "fatras_native_dir": "/tmp/fatras-native"}
        launched = []
        def native(command, log):
            if "generate" in command:
                self.case("sample")
            else:
                launched.append(log.name)
                raise RuntimeError("preserved failed case")
        args = SimpleNamespace(action="launch", output=self.root, jobs=1, events=100, seed=153042)
        with patch.object(campaign, "plan", return_value=expected), patch.object(campaign, "launch_process", side_effect=native):
            with self.assertRaisesRegex(RuntimeError, "preserved failed case"):
                campaign.execute(args)
        self.assertEqual(launched, ["pitch0.5.log"])


if __name__ == "__main__":
    unittest.main()
