"""Controls preventing transverse cuts from becoming misleading projections."""

import math
import tempfile
import json
from pathlib import Path
import unittest

import numpy as np

from views import box_section, box_vertices, convex_hull, sensor_section, load_case, _adjacent_row_slice


class SectionTests(unittest.TestCase):
    def test_box_cut_differs_from_projected_tilted_silhouette(self):
        # Synthetic cuboid rotated 45 degrees around y, lengths 4 x 6 x 2 mm.
        q = math.sqrt(.5)
        body = dict(center_mm=[0., 0., 0.], u=[q, 0., q], v=[0., 1., 0.], n=[-q, 0., q],
                    half_u_mm=2., half_v_mm=3., half_w_mm=1.)
        section = box_section(body, 0.)
        projection = convex_hull(box_vertices(body)[:, :2])
        self.assertEqual(len(section), 4)
        self.assertAlmostEqual(max(abs(section[:, 0])), math.sqrt(2.))
        self.assertAlmostEqual(max(abs(projection[:, 0])), 3. * q)
        self.assertAlmostEqual(max(abs(section[:, 1])), 3.)

    def test_longitudinal_gap_is_empty_and_boundary_section_is_retained(self):
        body = dict(center_mm=[5., 0., 3.], u=[0., 1., 0.], v=[0., 0., 1.], n=[1., 0., 0.],
                    half_u_mm=2., half_v_mm=1., half_w_mm=.2)
        self.assertEqual(len(box_section(body, 0.)), 0)
        self.assertEqual(len(sensor_section(body, 0.)), 0)
        self.assertEqual(len(box_section(body, 2.)), 4)
        np.testing.assert_allclose(sorted(map(tuple, sensor_section(body, 3.))), [(5., -2.), (5., 2.)])

    def test_coplanar_sensor_retains_rectangle(self):
        sensor = dict(center_mm=[0., 0., 3.], u=[1., 0., 0.], v=[0., 1., 0.],
                      half_u_mm=2., half_v_mm=1.)
        self.assertEqual(len(sensor_section(sensor, 3.)), 4)
        self.assertEqual(len(sensor_section(sensor, 3.001)), 0)

    def test_changed_geometry_code_refuses_retained_run(self):
        with tempfile.TemporaryDirectory() as work:
            Path(work, "run.json").write_text(json.dumps(dict(code_sha256={"geometry.py": "not-the-current-code"})))
            with self.assertRaisesRegex(RuntimeError, "Geometry code differs"):
                load_case(work, "unused")

    def test_second_slice_uses_distinct_row_not_shifted_central_ledge(self):
        bodies = [dict(row=row, center_mm=[0., 0., z]) for row, z in ((0, -22.3), (1, .9), (2, 24.1))]
        self.assertEqual(_adjacent_row_slice(bodies), 24.1)


if __name__ == "__main__":
    unittest.main()
