"""Campaign isolation and all-generated event identity regression checks."""
import copy
import json
from pathlib import Path
import unittest

from truth import case_config, build_config, join_events, same_geometry, RESIDUAL_CONVENTION


class IsolationTest(unittest.TestCase):
    def setUp(self):
        self.campaign = json.loads(Path(__file__).with_name("campaign.json").read_text())
        self.sensors = [{"geometry_id": (system << 56) | (2 << 36) | (1 << 8),
                         "ids": {"system": system},
                         "size_mm": [48., 96., .2]} for system in range(1, 8)]

    def test_only_short_strip_second_coordinate_changes(self):
        original = copy.deepcopy(self.campaign)
        baseline, counts = build_config(self.sensors, case_config(self.campaign, .5)["digitization"])
        self.assertEqual(counts, {str(i): 1 for i in range(1, 8)})
        for pitch, bins in ((1., 96), (1.5, 64), (2., 48)):
            alternative, _ = build_config(self.sensors, case_config(self.campaign, pitch)["digitization"])
            for before, after in zip(baseline["entries"], alternative["entries"]):
                system = before["volume"]
                if system not in (4, 5):
                    self.assertEqual(before, after)
                    continue
                fixed_before, fixed_after = copy.deepcopy(before), copy.deepcopy(after)
                before_axes = fixed_before["value"]["geometric"]["segmentation"]["binningdata"]
                after_axes = fixed_after["value"]["geometric"]["segmentation"]["binningdata"]
                self.assertEqual(after_axes[1]["bins"], bins)
                self.assertEqual((after_axes[1]["max"] - after_axes[1]["min"]) / bins, pitch)
                self.assertEqual(after["value"]["geometric"]["indices"], [0, 1])
                self.assertNotIn("variances", after["value"]["geometric"])
                after_axes[1] = before_axes[1]
                self.assertEqual(fixed_before, fixed_after)
        self.assertEqual(self.campaign, original)

    def test_all_requested_pitches_exactly_tile_current_sensor(self):
        for pitch in self.campaign["short_strip_local_v_pitch_mm"]:
            self.assertEqual((96 / pitch) % 1, 0)
        with self.assertRaises(ValueError):
            case_config(self.campaign, 3.)

    def test_join_requires_exact_unique_events(self):
        self.assertEqual(join_events([9, 2, 5], [5, 9, 2]).tolist(), [2, 0, 1])
        for generated, requested in (([2, 2], [2]), ([2, 5], [3]), ([2, 5], [8])):
            with self.assertRaises(ValueError):
                join_events(generated, requested)

    def test_only_roundoff_tolerated_in_balanced_geometry_comparison(self):
        self.assertTrue(same_geometry({"x": [1.]}, {"x": [1. + 5.e-10]}))
        self.assertFalse(same_geometry({"x": [1.]}, {"x": [1. + 2.e-9]}))
        self.assertFalse(same_geometry({"x": [1.]}, {"x": [1.], "added": 1}))

    def test_shared_observable_sign_matches_declared_array_contract(self):
        import numpy as np
        from metrics import perigee_observables
        truth = np.array([[0., 0., 0., 1., .1]])
        fitted = np.array([[.2, .3, .4, 1.1, .11]])
        values, _ = perigee_observables(fitted, truth, np.eye(5)[None])
        self.assertIn("fitted minus truth", RESIDUAL_CONVENTION)
        for key in ("d0", "z0", "phi", "theta", "q_over_p"):
            self.assertGreater(values[key]["residual"][0], 0)
            self.assertGreater(values[key]["pull"][0], 0)
        expected = ((np.sin(1.1)/.11) - (np.sin(1.)/.1)) / (np.sin(1.)/.1)
        self.assertAlmostEqual(values["pt_relative"]["residual"][0], expected)


if __name__ == "__main__":
    unittest.main()
