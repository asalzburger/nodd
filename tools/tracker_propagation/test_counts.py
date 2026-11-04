"""Identity and native-sensitive accounting controls without ACTS dependencies."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("tracker_counts", Path(__file__).with_name("counts.py"))
counts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(counts)


class AccountingTests(unittest.TestCase):
    def test_complete_identity_does_not_hide_step_limit_termination(self):
        world = {"r_max_mm": 1000, "half_z_mm": 4000, "volume_id": 117}
        step = {"g_r": [800], "g_z": [0], "volume_id": [116], "boundary_id": [0]}
        with self.assertRaisesRegex(ValueError, "did not terminate"):
            counts.require_world_exit(step, world)
        step.update(g_r=[1000.0001], volume_id=[117], boundary_id=[3])
        counts.require_world_exit(step, world)

    def test_missing_failed_probe_and_duplicate_survivor_are_rejected(self):
        for events, tracks in (([0, 2], [0, 0]), ([0, 0, 2], [0, 0, 0]), ([0, 1, 2], [0, 1, 0])):
            with self.assertRaisesRegex(ValueError, "incomplete probe identities"):
                counts.complete_order(events, tracks, 3, "fixture")
        self.assertEqual(counts.complete_order([2, 0, 1], [0, 0, 0], 3, "fixture"), [1, 2, 0])

    def test_zero_crossings_and_repeated_native_crossings_are_preserved(self):
        names = ("volume_id", "boundary_id", "layer_id", "approach_id", "sensitive_id", "extra_id")
        empty = {name: [] for name in names}
        self.assertEqual(counts.count_systems(empty, {}), ([0] * 7, 0))
        fields = (100, 0, 0, 0, 31, 0)
        steps = {name: [value, value] for name, value in zip(names, fields)}
        identifier = counts.geometry_id(*fields)
        self.assertGreater(identifier, 2 ** 53)
        self.assertEqual(counts.count_systems(steps, {identifier: 7}), ([0] * 6 + [2], 1))
        with self.assertRaisesRegex(ValueError, "absent from DD4hep"):
            counts.count_systems(steps, {})


if __name__ == "__main__":
    unittest.main()
