"""Geometry-contract checks independent of the native ACTS runtime."""

import copy
import math
import unittest

from export_geometry import build_export, link_surface_ids, surface_geometry


class FiniteGeometryTests(unittest.TestCase):
    def cylinder(self):
        return {"type": "CylinderSurface", "bounds": {"type": "CylinderBounds",
                "values": [42., 15., math.pi, 0.]},
                "transform": {"translation": [0., 0., -100.],
                              "rotation": [0., -1., 0., 1., 0., 0., 0., 0., 1.]}}

    def test_yaw_rotated_finite_cylinder_keeps_axial_translation(self):
        result = surface_geometry(self.cylinder())
        self.assertEqual(result["rz_segment_mm"], [[42., -115.], [42., -85.]])

    def test_flipped_disc_normal_preserves_finite_annulus(self):
        disc = {"type": "DiscSurface", "bounds": {"type": "RadialBounds",
                "values": [10., 90., math.pi, 0.]},
                "transform": {"translation": [0., 0., -20.],
                              "rotation": [1., 0., 0., 0., -1., 0., 0., 0., -1.]}}
        self.assertEqual(surface_geometry(disc)["rz_segment_mm"], [[10., -20.], [90., -20.]])

    def test_off_axis_tilted_and_partial_phi_portals_fail(self):
        off_axis = self.cylinder()
        off_axis["transform"]["translation"][0] = 1.
        tilted = self.cylinder()
        tilted["transform"]["rotation"] = [1., 0., 0., 0., 0., -1., 0., 1., 0.]
        partial = self.cylinder()
        partial["bounds"]["values"][2] = math.pi / 2.
        with self.assertRaisesRegex(ValueError, "Off-axis"):
            surface_geometry(off_axis)
        with self.assertRaisesRegex(ValueError, "Tilted"):
            surface_geometry(tilted)
        with self.assertRaisesRegex(ValueError, "Partial-phi"):
            surface_geometry(partial)

    def test_nonfinite_and_zero_length_bounds_fail(self):
        for index, value in ((0, math.nan), (1, 0.)):
            surface = self.cylinder()
            surface["bounds"]["values"][index] = value
            with self.assertRaises(ValueError):
                surface_geometry(surface)


class NativeIdentityTests(unittest.TestCase):
    def test_grid_artifact_link_surface_references_are_preserved(self):
        link = {"surface_id": 1, "children": [{"surface_id": 2}],
                "artifact_links": [{"surface_id": 3, "children": [{"surface_id": 4}]}]}
        self.assertEqual(link_surface_ids(link), {1, 2, 3, 4})

    def fixture(self):
        # Test values only: two owners of the same native finite portal and two
        # opposing signed sensor faces in one layer. These are not nODD inputs.
        surface = {"surface_id": 0, "geo_id": {"volume": 1},
                   "type": "CylinderSurface", "bounds": {"type": "CylinderBounds",
                   "values": [42., 15., math.pi, 0.]},
                   "transform": {"translation": None, "rotation": None}}
        native = {"root_volume_id": 0, "surfaces": [surface],
                  "portals": [{"portal_id": 0, "surface_id": 0,
                               "along_normal": None, "opposite_normal": None}],
                  "volumes": []}
        report = {"sensors": [], "beampipe_portals": [], "volumes": []}
        for index, name in enumerate(("World", "System1Layer0")):
            native["volumes"].append({"volume_id": index, "name": name,
                "geometry_id": {"volume": index + 1}, "portal_ids": [0],
                "children": [1] if index == 0 else [],
                "surface_id": [] if index == 0 else [1, 2],
                "transform": {"translation": None, "rotation": None},
                "bounds": {"kind": "Cylinder", "values": [0., 50., 20., math.pi, 0.]}})
            report["volumes"].append({"name": name, "geometry_id": index + 1,
                                      "portals": 1, "surfaces": 0 if index == 0 else 2})
        for index, normal_z in enumerate((-1., 1.)):
            native["surfaces"].append({"surface_id": index + 1, "sensitive": True,
                "geo_id": {"volume": 101 + index},
                "transform": {"translation": [30., 0., 10.],
                              "rotation": [1., 0., 0., 0., normal_z, 0., 0., 0., normal_z]}})
            report["sensors"].append({"geometry_id": 101 + index,
                "source_path": f"/sensor{index}", "ids": {"system": 1, "layer": 0},
                "center_mm": [30., 0., 10.], "normal": [0., 0., normal_z]})
        return native, report

    def test_shared_native_portal_is_once_with_both_owners_and_signed_faces(self):
        native, report = self.fixture()
        result = build_export(native, report, lambda encoded: encoded["volume"])
        self.assertEqual(len(result["portals"]), 1)
        self.assertEqual([owner["volume_name"] for owner in result["portals"][0]["owners"]],
                         ["World", "System1Layer0"])
        self.assertEqual(result["sensor_groups"][0]["normal_z_sign_counts"],
                         {"negative": 1, "positive": 1})
        self.assertEqual(result["volumes"][1]["portal_surface_ids"], [0])

    def test_sensor_frame_mismatch_between_native_exports_fails(self):
        native, report = self.fixture()
        report["sensors"][0]["center_mm"][2] += 1.
        with self.assertRaisesRegex(ValueError, "sensor frame"):
            build_export(native, report, lambda encoded: encoded["volume"])

    def test_duplicate_native_ids_or_sensor_ids_fail(self):
        native, report = self.fixture()
        native["surfaces"].append(copy.deepcopy(native["surfaces"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate native"):
            build_export(native, report, lambda encoded: encoded["volume"])
        native, report = self.fixture()
        report["sensors"][1]["geometry_id"] = report["sensors"][0]["geometry_id"]
        with self.assertRaisesRegex(ValueError, "Duplicate sensor"):
            build_export(native, report, lambda encoded: encoded["volume"])


if __name__ == "__main__":
    unittest.main()
