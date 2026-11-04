"""Rendering contract tests without creating production evidence or PDF files."""
from pathlib import Path
import tempfile
import unittest

import numpy as np

import analyze
import plot
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from test_analyze import CONFIG, fixture


class PlotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        row, sensors = fixture()
        record = analyze.classify_event(row, sensors, CONFIG)
        names = sorted(record["counts"])
        arrays = {"event": np.asarray([0]), "metric_names": np.asarray(names),
                  "counts": np.asarray([[record["counts"][k] for k in names]])}
        cls.report = analyze.summarize_cases({pitch: arrays for pitch in analyze.PITCHES}, 10)
        cls.report["provenance"] = {"analyzer_sha256": analyze.sha256(analyze.__file__)}

    def test_actual_percentile_endpoints_can_exclude_observed_point(self):
        fig, ax = plt.subplots()
        try:
            plot.points(ax, [1.], [95.], 1., [[100., 110.]])
            bars = [item for item in ax.collections if isinstance(item, LineCollection)]
            self.assertEqual(len(bars), 1)
            np.testing.assert_array_equal(bars[0].get_segments()[0], [[1., 100.], [1., 110.]])
        finally:
            plt.close(fig)

    def test_undefined_bins_are_gaps_with_explicit_denominators(self):
        x, y, intervals, denominators = plot.profile(self.report, .5, "frozen", "eff", "pt", "hardscatter")
        self.assertEqual(sum(denominators), 1)
        self.assertTrue(any(np.isnan(v) for v in y))
        self.assertEqual(sum(v is not None for v in intervals), 1)

    def test_all_six_synthetic_canvases_render(self):
        for selection in ("frozen", "guide"):
            for maker in (plot.overview, plot.efficiency_profiles, plot.candidate_profiles):
                fig = maker(self.report, selection)
                try:
                    fig.canvas.draw()
                    self.assertEqual(len(fig.axes), 4)
                    self.assertEqual(len(fig.legends[0].get_texts()), 4)
                    self.assertTrue(all(ax.get_ylabel() for ax in fig.axes))
                    text = " ".join(t.get_text() for t in fig.texts)
                    self.assertIn("PROTOTYPE", text)
                    self.assertIn("paired event-block", text)
                    self.assertIn("Boundary retries", text)
                finally:
                    plt.close(fig)

    def test_source_mismatch_refuses_render_before_any_output(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "profiles.json.gz"
            report = dict(self.report); report["provenance"] = {"analyzer_sha256": "0"*64}
            analyze.write_json(data, report)
            with self.assertRaisesRegex(ValueError, "Analyzer source changed"):
                plot.render(report, data, Path(directory) / "plots")
            self.assertFalse((Path(directory) / "plots").exists())

    def test_graph_limit_qualification_is_on_exported_canvas(self):
        report = {**self.report, "benchmark": {"gbts_graph_audit": {
            f"{pitch:g}": {"edge_cap": 2000000, "events": 100, "cap_reached_events": 99}
            for pitch in plot.PITCHES}}}
        fig, _ = plot.frame(report, "Fixture", "guide")
        try:
            fig.canvas.draw()
            text = " ".join(item.get_text() for item in fig.texts)
            self.assertIn("2,000,000", text)
            self.assertIn("2 mm: 99/100 events", text)
            self.assertIn("Resource-limited chain", text)
        finally:
            plt.close(fig)


if __name__ == "__main__":
    unittest.main()
