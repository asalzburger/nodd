import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from compare import binned_moments, index, load_run, moments, sha


class ComparisonControls(unittest.TestCase):
    def test_bootstrap_multiplicity_matches_explicit_repeated_sample(self):
        values = np.array([0., .01, .3, 2., .6])
        categories = np.array([0, 0, 0, 1, 1])
        weights = np.array([2, 1, 4, 3, 2])
        means, widths = binned_moments(values, categories, weights, 2)
        for i in range(2):
            explicit = np.repeat(values[categories == i], weights[categories == i])
            self.assertAlmostEqual(means[i], explicit.mean())
            self.assertAlmostEqual(widths[i], explicit.std(ddof=1) / explicit.mean())

    def test_scaling_retains_width_zeros_and_own_mean_tail(self):
        values = np.array([0., 1., 2., 2., 5.])
        a, b = moments(values), moments(values * .01)
        for key in ("fractional_width", "below_half_mean_fraction", "zero_events"):
            self.assertAlmostEqual(a[key], b[key])
        self.assertEqual(a["events"], 5)

    def test_bin_boundaries_and_outside_rejection(self):
        np.testing.assert_equal(index(np.array([0., 1., 2.]), np.array([0., 1., 2.])), [0, 1, 1])
        with self.assertRaises(ValueError): index(np.array([3.]), np.array([0., 1., 2.]))

    def test_ledger_tampering_and_duplicate_ids_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = {"exit_code": 0, "disk_abort": False, "events": 2, "skip": 0}
            (root / "receipt.json").write_text(json.dumps(receipt))
            rows = [dict(event=i, energy_GeV=20., eta=0., phi=0., signal_GeV=.2, response=.01) for i in (0, 1)]
            def save():
                (root / "event-summary.jsonl").write_text("\n".join(map(json.dumps, rows)))
                proof = {"status": "PASS", "receipt_sha256": sha(root / "receipt.json"), "event_summary_sha256": sha(root / "event-summary.jsonl"), "root_sha256": "fixture"}
                (root / "readback.json").write_text(json.dumps(proof))
            save(); self.assertEqual(len(load_run(root)[0]), 2)
            rows[1]["event"] = 0; save()
            with self.assertRaisesRegex(ValueError, "duplicate"): load_run(root)
            rows[1]["event"] = 1; save()
            (root / "event-summary.jsonl").write_text("tampered")
            with self.assertRaisesRegex(ValueError, "Changed"): load_run(root)


if __name__ == "__main__": unittest.main()
