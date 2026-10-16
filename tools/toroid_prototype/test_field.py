"""Independent identities for the polygon/finite-pack vacuum-field PROTOTYPE."""

import math
import unittest

import numpy as np

try:
    from .field import (K, MU0, SegmentSources, circular_loop_sources,
                        concatenate_sources, evaluate, filament_distance,
                        gauss_rule, load_cpp_backend, polyline_sources,
                        rounded_racetrack_sources, rounded_racetrack_vertices)
except ImportError:
    from field import (K, MU0, SegmentSources, circular_loop_sources,
                       concatenate_sources, evaluate, filament_distance,
                       gauss_rule, load_cpp_backend, polyline_sources,
                       rounded_racetrack_sources, rounded_racetrack_vertices)


def rotation_z(phi):
    return np.array([[math.cos(phi), -math.sin(phi), 0],
                     [math.sin(phi), math.cos(phi), 0], [0, 0, 1]])


class ExactSegmentTests(unittest.TestCase):
    def test_finite_wire_field_and_potential(self):
        # Analytic integral of a finite straight wire, independently specialized.
        wire = polyline_sources([[0, 0, -1], [0, 0, 1]], 1700, closed=False)
        rho = .73
        b, a = evaluate([[rho, 0, 0]], wire, quantity="both", backend="numpy")
        expected_b = K*1700*2/(rho*math.sqrt(rho*rho+1))
        expected_a = K*1700*2*math.asinh(1/rho)
        np.testing.assert_allclose(b, [[0, expected_b, 0]], rtol=2e-15, atol=1e-18)
        np.testing.assert_allclose(a, [[0, 0, expected_a]], rtol=2e-15, atol=1e-18)

    def test_axial_exterior_and_singularity_are_explicit(self):
        wire = polyline_sources([[0, 0, -1], [0, 0, 1]], 1700, closed=False)
        b, a = evaluate([[0, 0, 2], [0, 0, 0], [0, 0, 1]], wire,
                        quantity="both", backend="numpy")
        np.testing.assert_equal(b[0], [0, 0, 0])
        np.testing.assert_allclose(a[0], [0, 0, K*1700*math.log(3)], rtol=2e-15)
        self.assertTrue(np.isnan(b[1:]).all())
        self.assertTrue(np.isnan(a[1:]).all())
        zero = wire.scaled(0)
        for value in evaluate([[0, 0, 0]], zero, quantity="both", backend="numpy"):
            np.testing.assert_equal(value, np.zeros((1, 3)))

    def test_distance_to_finite_segment(self):
        wire = polyline_sources([[0, 0, -1], [0, 0, 1]], 1, closed=False)
        np.testing.assert_allclose(filament_distance([[.7, 0, 0], [0, 0, 2]], wire), [.7, 1])

    def test_invalid_geometry_and_inputs(self):
        with self.assertRaises(ValueError):
            polyline_sources([[0, 0, 0], [0, 0, 0]], 1)
        with self.assertRaises(ValueError):
            circular_loop_sources(0, 0, 1)
        with self.assertRaises(ValueError):
            rounded_racetrack_sources(3, 0, 1, 2, .01, 0, 1, pack_normal_m=.2)
        with self.assertRaises(ValueError):
            gauss_rule(1, 0)
        wire = polyline_sources([[0, 0, -1], [0, 0, 1]], 1, closed=False)
        with self.assertRaises(ValueError):
            evaluate([0, 0, 0], wire)
        with self.assertRaises(ValueError):
            wire.transformed(np.diag([-1, 1, 1]))


class ClosedLoopTests(unittest.TestCase):
    def setUp(self):
        # Test-only dimensions; no detector design is selected here.
        self.coil = rounded_racetrack_sources(4.1, .4, 1.1, 2.8, .45, .2, 8e5,
                                              .16, .22, quadrature_order=2,
                                              corner_segments=12)
        self.points = np.array([[3.7, .4, .1], [.2, .3, 0], [7, 2, 4], [2, -4, -3.]])

    def test_circular_loop_axis_analytic_and_polygon_convergence(self):
        radius, current = 1.7, 2.3e5
        z = np.array([0, .3, 2., 8.])
        points = np.column_stack((np.zeros_like(z), np.zeros_like(z), z))
        expected = MU0*current*radius**2/(2*(radius**2+z*z)**1.5)
        errors = []
        for n in (128, 256, 512):
            value = evaluate(points, circular_loop_sources(radius, 0, current, n), backend="numpy")
            np.testing.assert_allclose(value[:, :2], 0, atol=2e-16)
            errors.append(np.max(np.abs(value[:, 2]/expected-1)))
        self.assertLess(errors[-1], 2.4e-5)
        self.assertGreater(errors[0]/errors[1], 3.9)
        self.assertGreater(errors[1]/errors[2], 3.9)

    def test_positive_racetrack_polarity_and_current_closure(self):
        phi = .2
        center = [[4.1*math.cos(phi), 4.1*math.sin(phi), .4]]
        b = evaluate(center, self.coil, backend="numpy")[0]
        self.assertGreater(b @ np.array([-math.sin(phi), math.cos(phi), 0]), 0)
        np.testing.assert_allclose(np.sum((self.coil.b-self.coil.a)*self.coil.current_Aturn[:, None], axis=0),
                                   0, atol=1e-8)

    def test_linearity_polarity_groups(self):
        second = circular_loop_sources(1.4, -.3, 2e5, 64, "solenoid")
        combined = concatenate_sources([self.coil, second])
        b, a = evaluate(self.points, combined, quantity="both", by_group=True, backend="numpy")
        self.assertEqual(combined.group_names, ("coil", "solenoid"))
        for index, source in enumerate((self.coil, second)):
            expected_b, expected_a = evaluate(self.points, source, quantity="both", backend="numpy")
            np.testing.assert_allclose(b[:, index], expected_b, rtol=2e-14, atol=1e-15)
            np.testing.assert_allclose(a[:, index], expected_a, rtol=2e-14, atol=1e-15)
        for total, groups in zip(evaluate(self.points, combined, quantity="both", backend="numpy"), (b, a)):
            np.testing.assert_allclose(total, groups.sum(axis=1), rtol=2e-14, atol=1e-15)
        np.testing.assert_allclose(evaluate(self.points, self.coil.scaled(-2.7), backend="numpy"),
                                   -2.7*b[:, 0], rtol=2e-14, atol=1e-15)

    def test_rigid_rotation_and_translation(self):
        rotation = rotation_z(.67) @ np.array([[1, 0, 0], [0, .6, -.8], [0, .8, .6]])
        translation = np.array([.2, -.5, .3])
        shifted = self.coil.transformed(rotation, translation)
        for original, transformed in zip(
                evaluate(self.points, self.coil, quantity="both", backend="numpy"),
                evaluate(self.points@rotation.T+translation, shifted, quantity="both", backend="numpy")):
            np.testing.assert_allclose(transformed, original@rotation.T, atol=2e-15, rtol=2e-12)

    def test_vector_potential_curl_and_vacuum_divergence(self):
        h = 2e-5
        derivatives_b, derivatives_a = [], []
        for axis in np.eye(3):
            bp, ap = evaluate(self.points+h*axis, self.coil, quantity="both", backend="numpy")
            bm, am = evaluate(self.points-h*axis, self.coil, quantity="both", backend="numpy")
            derivatives_b.append((bp-bm)/(2*h))
            derivatives_a.append((ap-am)/(2*h))
        dx, dy, dz = derivatives_a
        curl_a = np.column_stack((dy[:, 2]-dz[:, 1], dz[:, 0]-dx[:, 2], dx[:, 1]-dy[:, 0]))
        reference = evaluate(self.points, self.coil, backend="numpy")
        np.testing.assert_allclose(curl_a, reference, rtol=3e-8, atol=4e-10)
        divergence = sum(derivatives_b[j][:, j] for j in range(3))
        np.testing.assert_allclose(divergence, 0, atol=2e-9)

    def test_twelvefold_covariance(self):
        toroid = concatenate_sources([self.coil.transformed(rotation_z(i*math.pi/6))
                                      for i in range(12)])
        rotation = rotation_z(math.pi/6)
        for original, transformed in zip(
                evaluate(self.points, toroid, quantity="both", backend="numpy"),
                evaluate(self.points@rotation.T, toroid, quantity="both", backend="numpy")):
            np.testing.assert_allclose(transformed, original@rotation.T, atol=1e-14, rtol=2e-11)

    def test_finite_pack_quadrature_converges_away_from_pack(self):
        field = []
        for order in (2, 3, 4):
            coil = rounded_racetrack_sources(4.1, .4, 1.1, 2.8, .45, .2, 8e5,
                                               .16, .22, quadrature_order=order,
                                               corner_segments=12)
            field.append(evaluate(self.points, coil, backend="numpy"))
        self.assertLess(np.linalg.norm(field[2]-field[1]),
                        np.linalg.norm(field[1]-field[0])/100)


class CppBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This test intentionally requires the backend to build, rather than
        # silently passing through the NumPy fallback.
        load_cpp_backend()

    def test_cpp_matches_numpy_including_grouped_potential(self):
        sources = concatenate_sources([
            rounded_racetrack_sources(4, .2, 1, 2.5, .4, .3, 4e5, .2, .25,
                                       quadrature_order=2, group="barrel"),
            circular_loop_sources(1.3, .1, -1.2e5, 48, "solenoid")])
        points = np.random.default_rng(26).uniform(-7, 7, (103, 3))
        for by_group in (False, True):
            expected = evaluate(points, sources, quantity="both", backend="numpy", by_group=by_group,
                                point_chunk=17, segment_chunk=23)
            actual = evaluate(points, sources, quantity="both", backend="cpp", by_group=by_group, threads=3)
            for a, b in zip(actual, expected):
                np.testing.assert_allclose(a, b, atol=2e-15, rtol=2e-11)

    def test_cpp_wire_special_cases(self):
        wire = polyline_sources([[0, 0, -1], [0, 0, 1]], 1700, closed=False)
        points = [[.7, 0, 0], [0, 0, 2], [0, 0, 0], [0, 0, 1]]
        for actual, expected in zip(evaluate(points, wire, quantity="both", backend="cpp"),
                                    evaluate(points, wire, quantity="both", backend="numpy")):
            np.testing.assert_allclose(actual, expected, atol=1e-18, rtol=2e-15, equal_nan=True)
        for value in evaluate(np.empty((0, 3)), wire, quantity="both", backend="cpp"):
            self.assertEqual(value.shape, (0, 3))


if __name__ == "__main__":
    unittest.main()
