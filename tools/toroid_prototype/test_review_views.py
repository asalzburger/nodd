"""Scientific controls of finite slices and the distinct coverage criteria."""

import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from . import geometry as g
from .map import FieldMap
from .review_views import (classify_rays, coverage_scan, interstation_blocked,
                           interpolate_field_partial, load_inputs,
                           ray_station_points, slice_masks)


def fixture_config():
    """Test-only dimensions; no detector geometry is selected by these controls."""
    return {"folds": 1, "pack": {"normal_m": .1, "tangent_m": .1},
            "cold": {"normal_m": .15, "tangent_m": .15},
            "warm": {"normal_m": .2, "tangent_m": .2},
            "coil_groups": {"test_coil": {"center_r_m": 3., "center_z_m": 0.,
                             "half_r_m": 1., "half_z_m": 2., "corner_radius_m": .4,
                             "phi_offset_deg": 0.}},
            "stations": {"barrel_radii_m": [2.2, 3.2, 4.2],
                         "disk_abs_z_m": [3., 4., 5.], "disk_inner_radius_m": .01,
                         "outline_thickness_m": .5, "barrel_end_shortening_m": .5}}


class ReviewViewTests(unittest.TestCase):
    def test_executed_cold_allocation_is_used(self):
        config = fixture_config()
        config["cold"] = {"normal_m": .1234, "tangent_m": .1678}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/"results.json"
            path.write_text(json.dumps({"configuration": config}))
            _, loaded, field, field_path = load_inputs(path)
            self.assertEqual(loaded["cold"], config["cold"])
            self.assertIsNone(field)
            self.assertIsNone(field_path)

    def test_slice_is_not_a_coil_projection(self):
        config = fixture_config()
        points = [[2, 0, 0], [2, 0, 6], [2, .08, 0], [2, .11, 0]]
        masks = slice_masks(points, config)
        np.testing.assert_equal(masks["pack"], [True, False, False, False])
        np.testing.assert_equal(masks["warm"], [True, False, True, False])
        for key in ("pack", "cold", "warm"):
            np.testing.assert_equal(masks[key], g.coil_mask(points, config, width=key))

    def test_barrel_full_depth_can_exclude_a_clear_centre(self):
        config = fixture_config()
        point = [[2.2, 0, 0]]
        self.assertFalse(g.coil_mask(point, config, clearance=.05)[0])
        masks = slice_masks(point, config)
        self.assertTrue(masks["chamber_nominal"][0])
        self.assertTrue(masks["chamber_excluded"][0])
        self.assertFalse(masks["chamber_retained"][0])

    def test_disk_depth_is_axial_and_survives_slice_offset(self):
        config = fixture_config()
        config["stations"]["disk_abs_z_m"][0] = 0.
        config["stations"]["barrel_end_shortening_m"] = 1.
        # The whole disk depth stays radially outside the r=2 m coil leg.
        # Inflating its radial width by half a chamber would wrongly exclude it.
        for z in (0., .24):
            masks = slice_masks([[2.2, 0, z]], config)
            self.assertTrue(masks["chamber_nominal"][0])
            self.assertTrue(masks["chamber_retained"][0])

    def test_vector_station_intersections_match_geometry_reference(self):
        config = fixture_config()
        eta = np.array([0., .6, .9, 1.2, 2.5, -1.2])
        phi = np.array([0., 5., 50., 90., 160., 90.])
        points, kinds = ray_station_points(eta, phi, config)
        classified = classify_rays(eta, phi, config, path_step_m=.1)
        for index, (e, p) in enumerate(zip(eta, phi)):
            reference = g.station_intersections(e, p, config, check_path=False)
            present = kinds[index] != "-"
            self.assertEqual("".join(kinds[index, present]), reference["hit_types"])
            np.testing.assert_allclose(points[index, present], reference["points_m"], rtol=2e-15, atol=2e-15)
            self.assertEqual(classified["retained_count"][index],
                             sum(not hit["excluded"] for hit in reference["hits"]))

    def test_upstream_shadow_is_separate_from_three_hit_clear_path(self):
        config = fixture_config()
        config["stations"].update(barrel_radii_m=[5., 6., 7.], disk_abs_z_m=[10., 11., 12.])
        result = classify_rays([0., 0.], [0., 90.], config, path_step_m=.1)
        np.testing.assert_equal(result["status"], [3, 3])
        np.testing.assert_equal(result["upstream_blocked"], [True, False])
        np.testing.assert_equal(result["path_blocked"], [False, False])

    def test_half_step_guard_covers_narrow_between_sample_crossing(self):
        config = fixture_config()
        config["coil_groups"]["test_coil"]["center_r_m"] += .11
        samples = [[1, 0, 0], [2, 0, 0], [3, 0, 0]]
        self.assertFalse(g.coil_mask(samples, config, clearance=0).any())
        self.assertTrue(interstation_blocked([[1, 0, 0]], [[3, 0, 0]], config,
                                             clearance_m=0, step_m=1.)[0])

    def test_invalid_map_stencils_and_outside_points_remain_nan(self):
        field = FieldMap.__new__(FieldMap)
        field.r = np.array([0., 1., 2.]); field.z = np.array([-1., 0., 1.])
        field.phi = np.array([0., 15., 30.])
        field.valid = np.ones((3, 3, 3), bool)
        field.b = np.zeros((3, 3, 3, 3)); field.b[..., 2] = 3.
        field.valid[0, 0, 0] = False; field.b[0, 0, 0] = np.nan
        got = interpolate_field_partial(field, [[.5, 0, -.5], [1.5, 0, .5], [3, 0, 0]])
        self.assertTrue(np.isnan(got[0]).all())
        np.testing.assert_equal(got[1], [0, 0, 3])
        self.assertTrue(np.isnan(got[2]).all())

    def test_cell_centres_and_exact_solid_angle_weight(self):
        config = fixture_config()
        config["coil_groups"]["test_coil"]["center_z_m"] = 1000
        config["stations"]["barrel_end_shortening_m"] = 0
        report, rows = coverage_scan(config, eta_step=.5, phi_step_deg=15., path_step_m=.1)
        self.assertEqual(report["summary"]["ray_count"], 12)
        self.assertTrue(all(row["phi_deg"] in (7.5, 22.5) for row in rows))
        self.assertEqual(report["summary"]["three_clear_path_count"], 12)
        self.assertAlmostEqual(report["summary"]["solid_angle_sr"], np.pi/6*np.tanh(3), places=14)
        self.assertAlmostEqual(report["summary"]["solid_angle_weighted_three_clear_path_fraction"], 1.)


if __name__ == "__main__":
    unittest.main()
