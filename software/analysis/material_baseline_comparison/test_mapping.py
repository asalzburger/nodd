"""Pure controls for current-geometry and recording identity gates."""

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("map_workflow", Path(__file__).with_name("map_workflow.py"))
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)


class MappingContracts(unittest.TestCase):
    def setUp(self):
        self.preparation = {"source_revision": "geometry-source", "geometry_inputs": [
            {"role": "tracker.xml", "path": "/geometry/tracker.xml", "sha256": "compact"},
            {"role": "materials.xml", "path": "/geometry/materials.xml", "sha256": "materials"},
            {"role": "factory", "path": "/geometry/libFactory.dylib", "sha256": "factory"}]}
        self.recording = {"completed": True, "source_revision": "recorder-source",
            "events": [{"event": 0}, {"event": 1}],
            "settings": {"events": 2, "tracks_per_event": 100, "seed": 228,
                "eta": [-4, 4], "eta_uniform": True, "phi_degrees": [0, 360],
                "vertex_mm": [0, 0, 0, 0], "threads": 1, "charge": 0, "pdg": 0,
                "recordElementFractions": False, "prePostStep": True,
                "recalculateTotals": True, "excludeMaterials": ["Air", "Vacuum"]},
            "compact_sha256": "compact", "materials_sha256": "materials",
            "factories": [{"path": "/other/libFactory.dylib", "sha256": "factory"}]}

    def test_recorder_revision_is_distinct_from_geometry_identity(self):
        checked = workflow.verify_recording_report(self.recording, self.preparation, 2, 100)
        self.assertEqual(checked["recording_source_revision"], "recorder-source")
        self.assertEqual(checked["geometry_source_revision"], "geometry-source")

    def test_incomplete_or_duplicate_events_rejected(self):
        for change in ({"completed": False}, {"events": [{"event": 0}]},
                       {"events": [{"event": 0}, {"event": 0}]}):
            record = {**self.recording, **change}
            with self.subTest(change=change), self.assertRaises(ValueError):
                workflow.verify_recording_report(record, self.preparation, 2, 100)

    def test_historical_eta_support_rejected_as_current_training(self):
        record = copy.deepcopy(self.recording)
        record["settings"]["eta"] = [-4.5, 4.5]
        with self.assertRaisesRegex(ValueError, "settings"):
            workflow.verify_recording_report(record, self.preparation, 2, 100)

    def test_compact_material_and_factory_switches_rejected(self):
        changes = [{"compact_sha256": "old-compact"}, {"materials_sha256": "old-materials"},
                   {"factories": [{"path": "/geometry/libFactory.dylib", "sha256": "old-factory"}]}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                workflow.verify_recording_report({**self.recording, **change}, self.preparation, 2, 100)

    def test_current_inventory_does_not_accept_old_planes(self):
        geometry = {"checks": {"sensitive_surfaces": 46682, "volumes": 120, "sensor_groups": 54}}
        workflow.check_current_geometry(geometry)
        for old in (45646, 46250):
            geometry["checks"]["sensitive_surfaces"] = old
            with self.subTest(old=old), self.assertRaises(ValueError):
                workflow.check_current_geometry(geometry)

    def test_geometry_changes_after_export_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "geometry"
            path.write_bytes(b"first")
            preparation = {"build_dir": temporary, "geometry_inputs": [workflow.identity(path, "compact")]}
            workflow.assert_same_geometry(preparation, temporary)
            path.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "changed"):
                workflow.assert_same_geometry(preparation, temporary)

    def test_sidecar_reuse_requires_binary_and_source_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            binary, source = Path(temporary) / "module.so", Path(temporary) / "module.cpp"
            binary.write_bytes(b"binary"); source.write_bytes(b"source")
            report = {"provenance": {"files": [workflow.identity(binary, "sidecar"),
                                                workflow.identity(source, "sidecar_source")]}}
            workflow.verify_sidecar_evidence(report, binary, source)
            source.write_bytes(b"new source")
            with self.assertRaisesRegex(ValueError, "sidecar_source"):
                workflow.verify_sidecar_evidence(report, binary, source)

    def test_native_reader_zero_steps_are_explicitly_accounted(self):
        workflow.check_reader_partition(8, 2, 5, 1)
        workflow.check_reader_partition(0, 0, 0, 0)
        for values in ((8, 2, 4, 1), (8, 2, 6, 1), (8, 9, 0, 0)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                workflow.check_reader_partition(*values)


if __name__ == "__main__":
    unittest.main()
