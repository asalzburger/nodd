"""Gaussian control isolation, dimensions and covariance coupling regressions."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import gaussian_control as control


class GaussianControlTest(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(Path(__file__).with_name("campaign.json").read_text())
        self.sensors = [{"geometry_id": (system << 56) | (2 << 36) | (1 << 8),
                         "ids": {"system": system}} for system in range(1, 8)]

    def build(self, pitch):
        with patch.dict(control.frozen.EXPECTED_SENSORS, {str(i): 1 for i in range(1, 8)}, clear=True):
            return control.gaussian_config(self.sensors, control.control_campaign(self.base, pitch))

    def test_control_campaign_canonical_except_short_strip_pitch(self):
        original = copy.deepcopy(self.base)
        reference = control.control_campaign(self.base, .5)
        for pitch in [1., 1.5, 2.]:
            actual = control.control_campaign(self.base, pitch)
            self.assertEqual(actual["digitization"]["short_strip_pitch_mm"], [.075, pitch])
            actual["digitization"]["short_strip_pitch_mm"][1] = .5
            self.assertEqual(actual, reference)
        self.assertEqual(self.base, original)

    def test_only_short_strip_coarse_sigma_changes_no_fine_covariance_coupling(self):
        baseline, _ = self.build(.5)
        for pitch in [1., 1.5, 2.]:
            actual, audit = self.build(pitch)
            self.assertEqual(audit["geometric_entries"], 0)
            for before, after in zip(baseline["entries"], actual["entries"]):
                self.assertNotIn("geometric", after["value"])
                smearers = after["value"]["smearing"]
                self.assertEqual(len(smearers), 1 if after["volume"] >= 6 else 2)
                self.assertEqual(smearers[0], before["value"]["smearing"][0])
                if after["volume"] in [4, 5]:
                    self.assertAlmostEqual(smearers[1]["stddev"]**2, pitch*pitch/12)
                    after["value"]["smearing"][1] = before["value"]["smearing"][1]
                self.assertEqual(after, before)

    def test_duplicate_sensor_and_invalid_pitch_rejected(self):
        with self.assertRaises(ValueError):
            control.gaussian_config([self.sensors[0], self.sensors[0]], control.control_campaign(self.base, .5))
        altered = control.control_campaign(self.base, .5)
        altered["digitization"]["short_strip_pitch_mm"][1] = float("nan")
        with self.assertRaises(ValueError):
            control.gaussian_config(self.sensors, altered)


if __name__ == "__main__":
    unittest.main()
