import copy
import json
from pathlib import Path
import unittest

from sampling import directions, tracks_for


class SamplingTests(unittest.TestCase):
    def test_luminous_boundaries_and_reproducibility(self):
        config = json.loads(Path(__file__).with_name("study_config.json").read_text())
        tracks = directions(config)
        self.assertEqual(tracks, directions(config))
        corners = {tuple(t["origin_mm"]) for t in tracks if t["cohort"] == "luminous_boundary_grid"}
        self.assertEqual(len(corners), 12)
        for track in tracks:
            x, y, z = track["origin_mm"]
            self.assertTrue(0 <= x <= 1 and 0 <= y <= 1 and -150 <= z <= 150)
        self.assertTrue(all(t["pt_GeV"] == 1. for t in tracks_for(tracks, "negative", config)))
        config = copy.deepcopy(config)
        config["momentum_convention"] = "p"
        bent = tracks_for([dict(origin_mm=[0, 0, 0], eta=2., phi=0.)], "positive", config)[0]
        self.assertAlmostEqual(bent["pt_GeV"], 0.2658022288340797)


if __name__ == "__main__":
    unittest.main()
