"""Negative controls for the construction audit, independent of DD4hep runtime."""

import copy
import math
import unittest

from validate import compare_entities, compare_sensors, exclusive_volume, ray_direction


class ValidationTests(unittest.TestCase):
    def setUp(self):
        # Explicit test fixtures, unrelated to detector dimensions.
        self.sensor = {
            "name": "test_sensor",
            "role": "sensitive",
            "ids": {"system": 1, "layer": 2, "stave": 3, "module": 4, "sensor": 5},
            "center_mm": [10.0, 20.0, 30.0],
            "normal": [1.0, 0.0, 0.0],
            "material": "test_silicon",
            "mass_g": 2.0,
            "volume_mm3": 100.0,
        }

    def test_complete_identity_and_signed_transform(self):
        self.assertTrue(compare_sensors([self.sensor], [self.sensor])["passed"])
        changed = copy.deepcopy(self.sensor)
        changed["normal"] = [-1.0, 0.0, 0.0]
        self.assertFalse(compare_sensors([changed], [self.sensor])["passed"])
        changed = copy.deepcopy(self.sensor)
        changed["center_mm"][0] += 0.01
        self.assertFalse(compare_sensors([changed], [self.sensor])["passed"])

    def test_duplicate_missing_and_changed_ids_detected(self):
        self.assertFalse(
            compare_sensors([self.sensor, self.sensor], [self.sensor])["passed"]
        )
        self.assertFalse(compare_sensors([], [self.sensor])["passed"])
        changed = copy.deepcopy(self.sensor)
        changed["ids"]["module"] += 1
        result = compare_sensors([changed], [self.sensor])
        self.assertEqual(len(result["errors"]), 2)

    def test_mass_and_material_changes_detected(self):
        self.assertTrue(compare_entities([self.sensor], [self.sensor])["passed"])
        for field, value in [
            ("mass_g", 4.0),
            ("volume_mm3", 110.0),
            ("material", "test_wrong"),
        ]:
            changed = dict(self.sensor, **{field: value})
            self.assertFalse(compare_entities([changed], [self.sensor])["passed"])

    def test_displaced_material_is_not_double_counted(self):
        self.assertEqual(exclusive_volume(100.0, [25.0, 35.0]), 40.0)
        with self.assertRaises(ValueError):
            exclusive_volume(10.0, [11.0])

    def test_eta_direction_and_normalization(self):
        self.assertEqual(ray_direction(0.0, 0.0), [1.0, 0.0, 0.0])
        for eta in (-3.0, -1.0, 0.0, 1.0, 3.0):
            direction = ray_direction(eta, 0.37)
            self.assertAlmostEqual(sum(v * v for v in direction), 1.0)
            theta = math.acos(direction[2])
            self.assertAlmostEqual(-math.log(math.tan(theta / 2)), eta)


if __name__ == "__main__":
    unittest.main()
