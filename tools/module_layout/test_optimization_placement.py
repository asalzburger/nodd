"""Finite-body fitting contracts for the isolated DES-011 refill helper."""
import copy
import json
import math
import unittest

from tools.module_layout import geometry
from tools.module_layout.optimization_placement import refill_candidate
from tools.module_layout.services_geometry import body_envelope


def candidate():
    return next(c for c in json.loads(geometry.LAYOUTS_PATH.read_text())["candidates"]
                if c["id"] == "cobe")


class RefillTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = geometry.load_models(geometry.REVIEW_MODELS_PATH)
        cls.candidate = candidate()
        # Explicit test-only physical bounds, not production detector settings.
        cls.bounds = {"pixel": [27., 188.], "short_strip": [240., 658.],
                      "long_strip": [740., 1138.]}
        cls.filled = refill_candidate(cls.candidate, cls.models, cls.bounds)

    def test_complete_bodies_fit_physical_bounds_and_sat_clears(self):
        layout = self.filled["layout"]
        actual = {sub: [math.inf, 0.] for sub in self.bounds}
        for body in layout["bodies"]:
            if body["region"] != "endcap":
                continue
            low, high = self.bounds[body["subsystem"]]
            envelope = body_envelope(body)
            self.assertGreaterEqual(envelope["r_min_mm"], low-1e-7)
            self.assertLessEqual(envelope["r_max_mm"], high+1e-7)
            seen = actual[body["subsystem"]]
            seen[0] = min(seen[0], envelope["r_min_mm"])
            seen[1] = max(seen[1], envelope["r_max_mm"])
        # Bodies reach both specified edges: fitting did not silently discard
        # outer rows, replace rectangles with wedges, or clip their corners.
        for sub in self.bounds:
            for got, expected in zip(actual[sub], self.bounds[sub]):
                self.assertAlmostEqual(got, expected, places=6)
        self.assertEqual(geometry.body_overlap_diagnostics(layout)["overlapping_body_pairs"], 0)

    def test_input_models_and_barrel_placements_are_preserved(self):
        self.assertEqual(self.candidate, candidate())
        self.assertEqual(self.models, geometry.load_models(geometry.REVIEW_MODELS_PATH))
        expected_models = copy.deepcopy(self.models)
        expected_models["long_strip"]["endcap_rings"] = 5
        self.assertEqual(self.filled["models"], expected_models)
        original = geometry.generate_layout(self.candidate, "review_default", models=self.models)
        # Endcap counts can shift global IDs if layer order changes; identity
        # here is the unchanged physical barrel, its layer, row and column.
        fields = ("layer_id", "row", "col", "family", "center_mm", "u", "v", "n",
                  "half_u_mm", "half_v_mm", "half_w_mm")
        def barrels(layout):
            return [{k: b[k] for k in fields} for b in layout["bodies"]
                    if b["region"] == "barrel"]
        self.assertEqual(barrels(original), barrels(self.filled["layout"]))
        for layer in self.filled["candidate"]["layers"]:
            old = next(x for x in self.candidate["layers"] if x["id"] == layer["id"])
            self.assertEqual(layer.get("z_m"), old.get("z_m"))

    def test_changed_module_outline_is_refilled_without_shape_substitution(self):
        models = copy.deepcopy(self.models)
        models["pixel"]["body_service_v_mm"] += 3.
        models["long_strip"]["body_service_u_mm"] += 2.
        result = refill_candidate(self.candidate, models, self.bounds)
        self.assertNotEqual(result["layout"]["metadata"]["model_sha256"],
                            self.filled["layout"]["metadata"]["model_sha256"])
        for body in result["layout"]["bodies"]:
            if body["region"] != "endcap":
                continue
            shape = geometry._shape(body["family"], models)
            self.assertEqual(body["half_u_mm"], shape["body_u"]/2)
            self.assertEqual(body["half_v_mm"], shape["body_v"]/2)
            bounds = self.bounds[body["subsystem"]]
            envelope = body_envelope(body)
            self.assertGreaterEqual(envelope["r_min_mm"], bounds[0]-1e-7)
            self.assertLessEqual(envelope["r_max_mm"], bounds[1]+1e-7)

    def test_narrow_long_disc_reduces_rows_and_remains_collision_free(self):
        trial = copy.deepcopy(self.candidate)
        trial["layers"] = [l for l in trial["layers"] if l["id"] == "A-long_strip-P6"]
        result = refill_candidate(trial, self.models, {"long_strip": [902., 1138.]})
        self.assertLess(result["models"]["long_strip"]["endcap_rings"],
                        self.models["long_strip"]["endcap_rings"])
        self.assertEqual(geometry.body_overlap_diagnostics(result["layout"])["overlapping_body_pairs"], 0)
        count = len({b["row"] for b in result["layout"]["bodies"]})
        self.assertEqual(count, result["diagnostics"]["subsystems"]["long_strip"]["rows"])

    def test_infeasible_or_invalid_annuli_fail_without_mutating_inputs(self):
        for bounds in ([27., 30.], [188., 27.], [float("nan"), 188.]):
            annuli = copy.deepcopy(self.bounds)
            annuli["pixel"] = bounds
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                refill_candidate(self.candidate, self.models, annuli)
        with self.assertRaisesRegex(ValueError, "missing"):
            refill_candidate(self.candidate, self.models, {})
        self.assertEqual(self.models, geometry.load_models(geometry.REVIEW_MODELS_PATH))


if __name__ == "__main__":
    unittest.main()
