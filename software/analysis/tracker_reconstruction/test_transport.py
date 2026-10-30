"""Dependency-free transport routing and native-lifecycle boundary controls."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("nodd_transport", Path(__file__).with_name("transport.py"))
transport = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transport)


class TransportControls(unittest.TestCase):
    def setUp(self):
        # Deliberately non-unit synthetic conversion factors catch bare cuts.
        self.acts = SimpleNamespace(UnitConstants=SimpleNamespace(GeV=7., ns=11.))
        self.seq, self.detector, self.field, self.rnd, self.level = (object() for _ in range(5))
        self.geometry = SimpleNamespace(highestTrackingVolume=object())
        self.handle = object()
        self.observer = SimpleNamespace(persistent_handle=Mock(return_value=self.handle), finish_persistent=Mock())
        self.simulation = SimpleNamespace(addFatras=Mock(), addGeant4=Mock())
        setattr(self.simulation, "__geant4Handle", None)
        self.imports = patch.object(transport.importlib, "import_module", side_effect=lambda name: {
            "acts.examples.simulation": self.simulation, "acts.examples.geant4": SimpleNamespace()}[name])
        self.importer = self.imports.start()
        self.addCleanup(self.imports.stop)
        self.environment = patch.object(transport, "_geant4_environment", return_value={"datasets": {}, "geant4_config_version": None})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def schedule(self, backend="geant4", **overrides):
        return transport.schedule(self.seq, self.acts, self.detector, self.geometry,
            self.field, self.rnd, self.observer, {"simulation": backend, **overrides}, 19, self.level)

    def test_fatras_preserves_interactions_and_native_absolute_momentum_cut(self):
        settings, cleanup = self.schedule("fatras")
        self.simulation.addFatras.assert_called_once_with(self.seq, self.geometry, self.field,
            rnd=self.rnd, inputParticles="particles_generated", outputParticles="particles_simulated",
            outputSimHits="simhits", logLevel=self.level, enableInteractions=True, pMin=3.5)
        self.assertIsNone(settings["truth_selection"])
        self.assertEqual(settings["pMin_GeV"], 0.5)
        cleanup(); cleanup()
        self.simulation.addGeant4.assert_not_called()
        self.observer.persistent_handle.assert_not_called()
        self.importer.assert_called_once_with("acts.examples.simulation")
        json.dumps(settings, allow_nan=False)

    def test_geant4_explicit_cuts_mapping_and_persistent_cleanup(self):
        def inspect_schedule(*args, **kwargs):
            self.assertIs(getattr(self.simulation, "__geant4Handle"), self.handle)
        self.simulation.addGeant4.side_effect = inspect_schedule
        settings, cleanup = self.schedule()
        self.simulation.addGeant4.assert_called_once_with(self.seq, self.detector, self.geometry, self.field,
            rnd=self.rnd, inputParticles="particles_generated", outputParticles="particles_simulated",
            outputSimHits="simhits", logLevel=self.level, killVolume=self.geometry.highestTrackingVolume,
            killAfterTime=275., keepParticlesWithoutHits=True, recordHitsOfSecondaries=True,
            materialMappings=["Silicon", "pixel_Silicon"], volumeMappings=[],
            killSecondaries=False, physicsList="FTFP_BERT")
        self.observer.persistent_handle.assert_called_once_with(19)
        self.assertEqual(settings["lifecycle"]["expected_events"], 19)
        self.assertEqual(settings["physicsList"], "FTFP_BERT")
        self.assertTrue(settings["recordHitsOfCharged"])
        self.assertFalse(settings["recordHitsOfNeutrals"])
        json.dumps(settings, allow_nan=False)
        cleanup(); cleanup()
        self.observer.finish_persistent.assert_called_once_with(self.handle)
        self.assertIsNone(getattr(self.simulation, "__geant4Handle"))
        self.simulation.addFatras.assert_not_called()

    def test_scheduling_failure_finishes_and_preserves_original_exception(self):
        original = RuntimeError("synthetic construction failure")
        self.simulation.addGeant4.side_effect = original
        self.observer.finish_persistent.side_effect = RuntimeError("synthetic finish failure")
        with self.assertRaises(RuntimeError) as caught:
            self.schedule()
        self.assertIs(caught.exception, original)
        self.assertIn("cleanup also failed", caught.exception.__notes__[0])
        self.observer.finish_persistent.assert_called_once_with(self.handle)
        self.assertIsNone(getattr(self.simulation, "__geant4Handle"))

    def test_cleanup_releases_helper_reference_even_when_finish_fails(self):
        _, cleanup = self.schedule()
        self.observer.finish_persistent.side_effect = RuntimeError("synthetic finish failure")
        with self.assertRaisesRegex(RuntimeError, "synthetic finish"):
            cleanup()
        cleanup()
        self.observer.finish_persistent.assert_called_once_with(self.handle)
        self.assertIsNone(getattr(self.simulation, "__geant4Handle"))

    def test_existing_foreign_handle_is_never_overwritten(self):
        foreign = object()
        setattr(self.simulation, "__geant4Handle", foreign)
        with self.assertRaisesRegex(RuntimeError, "fresh process"):
            self.schedule()
        self.assertIs(getattr(self.simulation, "__geant4Handle"), foreign)
        self.observer.persistent_handle.assert_not_called()
        self.simulation.addGeant4.assert_not_called()

    def test_missing_observer_or_helper_contract_fails_before_scheduling(self):
        del self.observer.finish_persistent
        with self.assertRaisesRegex(RuntimeError, "observer unavailable"):
            self.schedule()
        delattr(self.simulation, "__geant4Handle")
        with self.assertRaisesRegex(RuntimeError, "interface unavailable"):
            self.schedule()
        self.observer.persistent_handle.assert_not_called()
        self.simulation.addGeant4.assert_not_called()

    def test_unsupported_backend_and_unreviewed_cut_overrides_fail(self):
        for backend, changes in (("unknown", {}), (None, {}), ("geant4", {"geant4_run_mode": "standard"}),
                                 ("geant4", {"transport": {"killSecondaries": True}})):
            with self.subTest(backend=backend, changes=changes), self.assertRaises(ValueError):
                self.schedule(backend, **changes)
        self.importer.assert_not_called()
        for events in (0, -1, True, 1.5):
            with self.subTest(events=events), self.assertRaises(ValueError):
                transport.schedule(self.seq, self.acts, self.detector, self.geometry,
                    self.field, self.rnd, self.observer, {"simulation": "fatras"}, events, self.level)
        self.importer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
