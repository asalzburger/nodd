"""Fault-injection controls for saved-run provenance, without ROOT dependency."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from transport import positive_finite_hit, provenance, sha


class SavedRunProvenance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name).resolve()
        d = self.directory
        for name, content in (("readout.xml", "<lccdd/>"), ("materials.xml", "<materials/>"),
                              ("library", "compiled factory"), ("ddsim", "DDSim script"),
                              ("runner", "runner script"), ("python_executable", "python binary")):
            (d / name).write_text(content)
        self.expected = {"export_sha256": {name: sha(d / name) for name in ("readout.xml", "materials.xml")},
                         "parts": [{"role": "sensitive", "module": module, "sensor": 0,
                                    "center_mm": [module * 30, 0, 2]} for module in (0, 1)]}
        (d / "expected.json").write_text(json.dumps(self.expected))
        self.native = {"status": "PASS", "execution": {"expected_sha256": sha(d / "expected.json"),
                        "compact_sha256": sha(d / "readout.xml"), "library_sha256": sha(d / "library")}}
        inputs = {name: {"path": str(d / filename), "sha256": sha(d / filename)}
                  for name, filename in (("expected", "expected.json"), ("compact", "readout.xml"),
                                         ("materials", "materials.xml"), ("library", "library"),
                                         ("ddsim", "ddsim"), ("runner", "runner"),
                                         ("python_executable", "python_executable"))}
        self.records = []
        for module in (0, 1):
            stem = d / f"module{module}-smoke"
            for suffix in (".root", ".log"):
                stem.with_suffix(suffix).write_text(f"saved output {module} {suffix}")
            x, y = module * 30, 0
            self.records.append({"schema_version": 1, "module": module, "exit_code": 0,
                                 "finished_at": "2026-10-15T00:00:00Z", "inputs": copy.deepcopy(inputs),
                                 "factory_search_prefix": str(d),
                                 "settings": {"events": 1, "particle": "mu-", "gun_energy_argument": "10*GeV",
                                              "position_mm": [x, y, -50], "direction": [0, 0, 1],
                                              "seed": 42, "physics_list": "FTFP_BERT",
                                              "field_definition": "absent from compact; no field CLI override"},
                                 "command": [str(d / "python_executable"), str(d / "ddsim"), "--compactFile", str(d / "readout.xml"),
                                             "--runType", "batch", "--numberOfEvents", "1", "--enableGun",
                                             "--gun.particle", "mu-", "--gun.energy", "10*GeV",
                                             f"--gun.position={x} {y} -50", "--gun.direction", "0 0 1",
                                             "--random.seed", "42", "--physics.list", "FTFP_BERT",
                                             "--part.userParticleHandler", "", "--outputFile", str(stem.with_suffix(".root"))],
                                 "outputs": {name: {"path": str(stem.with_suffix(suffix)), "sha256": sha(stem.with_suffix(suffix))}
                                             for name, suffix in (("root", ".root"), ("log", ".log"))}})

    def check(self):
        (self.directory / "smoke-commands.json").write_text(json.dumps(self.records))
        return provenance(self.directory, self.expected, self.native)

    def test_consistent_saved_run_identities(self):
        self.assertEqual(len(self.check()), 2)

    def test_substituted_saved_root_is_rejected(self):
        (self.directory / "module0-smoke.root").write_text("another run with the same IDs")
        with self.assertRaisesRegex(ValueError, "saved output"):
            self.check()

    def test_changed_compact_is_rejected(self):
        (self.directory / "readout.xml").write_text("<lccdd><changed/></lccdd>")
        with self.assertRaisesRegex(ValueError, "export"):
            self.check()

    def test_other_library_even_with_updated_metadata_is_rejected(self):
        (self.directory / "library").write_text("another factory")
        for record in self.records:
            record["inputs"]["library"]["sha256"] = sha(self.directory / "library")
        with self.assertRaisesRegex(ValueError, "native input mismatch"):
            self.check()

    def test_wrong_recorded_seed_is_rejected(self):
        self.records[0]["settings"]["seed"] = 17
        with self.assertRaisesRegex(ValueError, "settings"):
            self.check()

    def test_wrong_executed_seed_is_rejected(self):
        command = self.records[0]["command"]
        command[command.index("--random.seed") + 1] = "17"
        with self.assertRaisesRegex(ValueError, "executed command"):
            self.check()

    def test_failed_job_is_rejected(self):
        self.records[1]["exit_code"] = 1
        with self.assertRaisesRegex(ValueError, "failed simulation"):
            self.check()

    def test_duplicate_job_is_rejected(self):
        self.records[1] = copy.deepcopy(self.records[0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check()

    def test_finite_positive_energy_and_positions_required(self):
        self.assertTrue(positive_finite_hit(0.001, [0, 1, 2]))
        for energy in (0, -1, float("nan"), float("inf")):
            self.assertFalse(positive_finite_hit(energy, [0, 1, 2]))
        self.assertFalse(positive_finite_hit(0.001, [0, float("nan"), 2]))


if __name__ == "__main__":
    unittest.main()
