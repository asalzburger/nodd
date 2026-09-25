"""Boundary checks for the optional, externally supplied IdRes adapter."""
import copy
import json
from pathlib import Path
import unittest

from idres_adapter import convert, geometry


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.candidate = json.loads((Path(__file__).resolve().parents[2] /
            "docs/design/DES-006-layouts.json").read_text())["candidates"][0]

    def test_signed_surfaces_and_material_units(self):
        text = geometry(self.candidate, 3, .5)
        self.assertEqual(text.count("B 3 end"), 1)
        self.assertNotIn("B 2 3 4", text)
        numeric = [list(map(float, l.split())) for l in text.splitlines()
                   if l and l[0] in "0123456789-"]
        self.assertEqual(len(numeric), len(self.candidate["layers"]))
        # First pixel has1%X0 normal material, exported as0.5percent at scale0.5.
        self.assertEqual(numeric[0][3], .5)
        expected_negative = sum(l["kind"] == "disc" and l["z_m"] < 0
                                for l in self.candidate["layers"])
        self.assertEqual(sum(l[2] < 0 for l in numeric), expected_negative)

    def test_unsupported_models_fail(self):
        for field, material in [(0, 1), (3, 0), (3, -1), (float("nan"), 1)]:
            with self.subTest(field=field, material=material), self.assertRaises(ValueError):
                geometry(self.candidate, field, material)
        bad = copy.deepcopy(self.candidate)
        bad["layers"][0]["kind"] = "arbitrary_plane"
        with self.assertRaises(ValueError):
            geometry(bad, 3, 1)

    def test_inverse_momentum_units_and_strip_count_convention(self):
        row = dict(Eta=0, z=0, Pt=100, Sig_d0=10, Sig_z0=15,
                   Sig_phi=1e-4, Sig_cotT=2e-4, Sig_invPt=.146, LeverArm=.986)
        converted = convert(row, dict(nHits=16, nPixHits=4, nStripHits=12))
        self.assertAlmostEqual(converted["sigma_inverse_pt_GeV_inverse"], .000146)
        self.assertEqual(converted["upstream_hit_count"], 16)
        self.assertEqual(converted["effective_station_count"], 10)

    def test_invalid_identity_bounds_and_response_fail(self):
        for change in [{"r_m": -1}, {"z_min_m": 10}, {"sigma_rphi_m": 0},
                       {"x0_percent": float("inf")}]:
            bad = copy.deepcopy(self.candidate)
            bad["layers"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                geometry(bad, 3, 1)
        bad = copy.deepcopy(self.candidate)
        bad["layers"].append(bad["layers"][0])
        with self.assertRaises(ValueError):
            geometry(bad, 3, 1)


if __name__ == "__main__":
    unittest.main()
