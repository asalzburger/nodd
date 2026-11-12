"""Geometry controls independent of ROOT and of the ignored source samples."""
import copy
import math
import unittest
import xml.etree.ElementTree as ET

from untiled_geometry import (BARREL_FRAME, CUTTER_FRAME, IDENTITY, TANGENT, area,
    barrel_slab, bounds, canonical, cut_intersections, intersection, location,
    number, polygon, pose, primitive_volume, prism, rotation, wafer_volume, wedge)


def inside(point, vertices):
    # A separate cross-product test, used to inspect generated Boolean cuts.
    signs = [(b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
             for a, b in zip(vertices, vertices[1:] + vertices[:1])]
    return min(signs) >= -1e-10 or max(signs) <= 1e-10


def wafer_contains(piece, point):
    if any(abs(point[i]) > number(piece.get(k)) / 2 for i, k in enumerate(("sx", "sy", "sz"))):
        return False
    for cut in piece.findall("cut"):
        matrix = rotation(cut)
        # Orthogonal inverse, applied to the wafer-local query point.
        local = [sum(matrix[j][i] * (point[j] - location(cut)[j]) for j in range(3)) for i in range(3)]
        if abs(local[2]) <= number(cut.get("depth")) / 2 and inside(local[:2], polygon(cut)):
            return False
    return True


class GeometryControls(unittest.TestCase):
    def test_convex_clip_orientation_and_touching_boundary(self):
        square = [(0., 0.), (2., 0.), (2., 2.), (0., 2.)]
        cutter = [(1., -1.), (3., -1.), (3., 1.), (1., 1.)]
        self.assertAlmostEqual(area(intersection(square, cutter)), 1.)
        self.assertAlmostEqual(area(intersection(square, list(reversed(cutter)))), 1.)
        shifted = [(x + 2, y) for x, y in square]
        self.assertAlmostEqual(area(intersection(square, shifted)), 0.)

    def test_barrel_boolean_faces_match_sloping_carrier(self):
        for layer in (0, 23, 47):
            center = 1702.5 + layer * 10.9
            parent = ET.Element("board")
            piece = barrel_slab(parent, layer, center, "Silicon")
            for normal in (-.25, -.17, 0., .11, .25):
                limit = (center + normal) * math.tan(math.pi / 16) - 1.
                for along in (-3899.999, -20., 0., 3899.999):
                    for sign in (-1, 1):
                        self.assertTrue(wafer_contains(piece, [sign * (limit - 1e-6), along, normal]))
                        self.assertFalse(wafer_contains(piece, [sign * (limit + 1e-6), along, normal]))
                self.assertTrue(wafer_contains(piece, [0., 0., normal]))
            self.assertFalse(wafer_contains(piece, [0., 3900.001, 0.]))
            self.assertFalse(wafer_contains(piece, [0., 0., .251]))

    def test_barrel_cell_plane_normal_and_axes(self):
        # (u,v,w)=(10,20,.1) must be (x,y,z)=(r+.1,10,20).
        local = [10., 20., .1]
        global_point = [sum(BARREL_FRAME[i][j] * local[j] for j in range(3)) for i in range(3)]
        self.assertEqual(global_point, [.1, 10., 20.])
        for frame in (BARREL_FRAME, CUTTER_FRAME):
            for i in range(3):
                for j in range(3):
                    self.assertEqual(sum(frame[k][i] * frame[k][j] for k in range(3)), int(i == j))

    def test_guard_volume_excludes_existing_sensitive_area(self):
        parent = ET.Element("fixture")
        outer = [(-45., -45.), (45., -45.), (45., 45.), (-45., 45.)]
        active = [(-44., -44.), (44., -44.), (44., 44.), (-44., 44.)]
        guard = prism(parent, "piece", outer, .5)
        prism(guard, "cut", active, .5)
        self.assertAlmostEqual(wafer_volume(guard), (90**2 - 88**2) * .5)

    def test_support_cut_volume_and_parent_local_depth(self):
        root = ET.Element("fixture")
        carrier = [(0., 0.), (10., 0.), (10., 10.), (0., 10.)]
        hole = [(2., 2.), (8., 2.), (8., 8.), (2., 8.)]
        support = prism(root, "piece", carrier, 20., (0., 0., 10.), name="support")
        prism(support, "cut", hole, 20.)
        slab = dict(layer=3, polygon=carrier, z_interval_mm=[4.75, 5.25])
        edits = cut_intersections(support, [slab])
        self.assertEqual(len(edits), 1)
        self.assertAlmostEqual(edits[0]["volume_mm3"], (100. - 36.) * .5)
        added = support.findall("cut")[-1]
        self.assertEqual(location(added), (0., 0., -5.))
        self.assertEqual(number(added.get("depth")), .5)

    def test_nonintersecting_passive_is_unchanged(self):
        root = ET.Element("fixture")
        passive = pose(ET.SubElement(root, "piece", kind="box", sx="2*mm", sy="2*mm", sz="2*mm"), (0., 0., 100.))
        before = canonical(passive)
        slab = dict(layer=0, polygon=[(-2., -2.), (2., -2.), (2., 2.), (-2., 2.)], z_interval_mm=[-.25, .25])
        self.assertEqual(cut_intersections(passive, [slab]), [])
        self.assertEqual(canonical(passive), before)

    def test_touching_support_is_not_removed(self):
        root = ET.Element("fixture")
        poly = [(0., 0.), (1., 0.), (1., 1.), (0., 1.)]
        passive = prism(root, "piece", poly, 2., (0., 0., 1.))
        self.assertEqual(cut_intersections(passive, [dict(layer=0, polygon=poly, z_interval_mm=[-1., 0.])]), [])
        self.assertFalse(passive.findall("cut"))

    def test_unsupported_intersecting_primitive_fails(self):
        root = ET.Element("fixture")
        passive = pose(ET.SubElement(root, "piece", name="unsupported", kind="box", sx="2*mm", sy="2*mm", sz="2*mm"))
        slab = dict(layer=0, polygon=[(-2., -2.), (2., -2.), (2., 2.), (-2., 2.)], z_interval_mm=[-.25, .25])
        with self.assertRaisesRegex(ValueError, "Unsupported intersecting passive"):
            cut_intersections(passive, [slab])

    def test_original_carrier_seam_and_wedge_volume(self):
        center, thickness = 1702.5, .5
        poly = wedge(center - thickness / 2, center + thickness / 2)
        self.assertAlmostEqual(area(poly), thickness * 2 * (center * TANGENT - 1.), places=7)
        for x, y in poly:
            self.assertAlmostEqual(x * TANGENT - abs(y), 1.)

    def test_units_reject_expressions_and_nonfinite(self):
        self.assertEqual(number("0.5*mm"), .5)
        for invalid in ("1+1*mm", "nan", "inf*mm", "1*cm"):
            with self.assertRaises(ValueError):
                number(invalid)


if __name__ == "__main__":
    unittest.main()
