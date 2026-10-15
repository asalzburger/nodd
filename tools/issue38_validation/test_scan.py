"""Small controls for counting semantics and the independent ideal denominator."""

import math
import unittest

from scan import direction, hit_metrics, ideal_crossings, ideal_reference


def sensor(system, layer, module, face=0, stave=0):
    return dict(ids=dict(system=system, layer=layer, stave=stave, module=module, sensor=face))


class CountingTests(unittest.TestCase):
    def test_pixel_islands_are_one_physical_sensor(self):
        got = hit_metrics([sensor(1, 1, 10, i) for i in range(4)], {"1:1"})
        self.assertEqual((got["active_patches"], got["physical_sensors"], got["stations"], got["holes"]), (4, 1, 1, 0))

    def test_long_strip_requires_same_module_pair(self):
        got = hit_metrics([sensor(6, 0, 10, 0), sensor(6, 0, 11, 1)], {"6:0"})
        self.assertEqual((got["physical_sensors"], got["complete_long_strip_pairs"], got["orphan_long_strip_faces"], got["holes"]), (2, 0, 2, 1))
        got = hit_metrics([sensor(6, 0, 10, 0), sensor(6, 0, 10, 1)], {"6:0"})
        self.assertEqual((got["complete_long_strip_pairs"], got["stations"], got["holes"]), (1, 1, 0))

    def test_extra_station_does_not_cancel_hole(self):
        got = hit_metrics([sensor(4, 0, 10), sensor(4, 0, 11)], {"4:1"})
        self.assertEqual((got["stations"], got["holes"], got["extra_stations"]), (1, 1, 1))


class ReferenceTests(unittest.TestCase):
    def test_declared_pixel_active_bounds_and_frozen_barrel_radius(self):
        refs = {r["id"]: r for r in ideal_reference()}
        self.assertEqual(refs["1:1"]["radius_mm"], 34.)
        self.assertEqual(refs["3:1"]["z_mm"], 615)
        self.assertAlmostEqual(refs["3:1"]["r_min_mm"], 32.3)
        self.assertAlmostEqual(refs["3:1"]["r_max_mm"], 181.4550267061104)
        self.assertEqual(refs["5:0"]["z_mm"], 1335)
        self.assertEqual(refs["5:6"]["z_mm"], -1335)
        self.assertEqual(refs["7:0"]["z_mm"], 1470)
        self.assertEqual(refs["7:6"]["z_mm"], -1470)

    def test_mirrored_disc_eligibility(self):
        refs = [dict(id="positive", kind="disc", z_mm=10., r_min_mm=9., r_max_mm=11.),
                dict(id="negative", kind="disc", z_mm=-10., r_min_mm=9., r_max_mm=11.)]
        eta = math.asinh(1)
        self.assertEqual(ideal_crossings(refs, [0, 0, 0], direction(eta, .3)), {"positive"})
        self.assertEqual(ideal_crossings(refs, [0, 0, 0], direction(-eta, .3)), {"negative"})

    def test_analytic_cylinder_and_off_axis_origin(self):
        refs = [dict(id="barrel", kind="cylinder", radius_mm=10., z_min_mm=-2., z_max_mm=2.)]
        self.assertEqual(ideal_crossings(refs, [1, 1, 0], direction(0, 0)), {"barrel"})
        self.assertEqual(ideal_crossings(refs, [1, 1, 0], direction(1, 0)), set())


if __name__ == "__main__":
    unittest.main()
