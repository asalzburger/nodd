"""Independent physical controls of complete finite-pack J dot A energy."""

import math
import unittest

import numpy as np

try:
    from .energy import integrate_current_dot_potential, magnetic_energy, rescale_energy
    from .field import (K, MU0, circular_loop_sources, concatenate_sources,
                        polyline_sources, rounded_racetrack_sources)
except ImportError:
    from energy import integrate_current_dot_potential, magnetic_energy, rescale_energy
    from field import (K, MU0, circular_loop_sources, concatenate_sources,
                       polyline_sources, rounded_racetrack_sources)


def fixture_coil(name, order, phi=0):
    """Test-only dimensions and current, independent of the detector proposal."""
    return rounded_racetrack_sources(3.2, 0, 1.2, 2., .5, phi, 1e5,
                                       .12, .18, order, 8, name)


def round_wire_loop(radial_order, angular_order, offset):
    """Uniform round cross-section (R=1 m, wire radius=0.02 m), positive J_phi."""
    nodes, weights = np.polynomial.legendre.leggauss(radial_order)
    rho = .02*(nodes+1)/2
    # Integral rho d(rho) d(theta)/(pi a^2), normalized to one.
    area_weights = weights*(nodes+1)/2
    return concatenate_sources(circular_loop_sources(
        1+r*math.cos(theta), r*math.sin(theta), 1e5*weight/angular_order,
        128, "round_wire") for r, weight in zip(rho, area_weights)
        for theta in (np.arange(angular_order)+offset)*2*math.pi/angular_order)


class EnergyTests(unittest.TestCase):
    def test_parallel_wire_neumann_integral_analytic(self):
        # This checks longitudinal integration independently of closed-loop
        # energy. NBS Circular 544 (1954), sec. 2.2h, printed p.28, eq.2.18.
        length, separation, current = 2., .11, 1e5
        source = polyline_sources([[0, 0, 0], [0, 0, length]], current, closed=False)
        target = polyline_sources([[separation, 0, 0], [separation, 0, length]], current, closed=False)
        expected = K*current**2*2*(length*math.asinh(length/separation)
                                    - math.sqrt(length**2+separation**2)+separation)
        actual = integrate_current_dot_potential(target, source, line_order=64,
                                                backend="cpp", by_group=False)
        self.assertAlmostEqual(actual/expected, 1., delta=2e-13)

    def test_round_wire_loop_matches_uniform_dc_thin_wire_reference(self):
        # NBS Circular 544, sec.2.2e, printed p.26, eq.2.15, b=0,
        # leading thin-wire term. Uniform volume current includes the internal
        # inductance: -7/4, rather than the surface-current constant -2.
        # R/a=50; the thin-wire and polygon approximations are explicit.
        source = round_wire_loop(3, 16, 0)
        target = round_wire_loop(4, 17, .5)
        result = magnetic_energy(source, [target], symmetry_multiplicity=1,
                                 line_order=8, backend="cpp")
        expected = .5*1e10*MU0*(math.log(8/.02)-1.75)
        self.assertAlmostEqual(result["total_energy_J"]/expected, 1., delta=.003)

    def test_all_self_mutual_terms_and_reciprocity(self):
        # Orthogonal meridional planes have a nonzero general mutual energy;
        # retain the complete ordered matrix, including both diagonal entries.
        source = concatenate_sources([fixture_coil("one", 2, 0), fixture_coil("two", 2, .7)])
        target = {"one": fixture_coil("one", 3, 0), "two": fixture_coil("two", 3, .7)}
        result = magnetic_energy(source, target, symmetry_multiplicity=1,
                                 line_order=12, reference_currents_Aturn=[1e5, 1e5], backend="cpp")
        matrix = np.array(result["energy_matrix_J"])
        self.assertTrue((matrix.diagonal() > 0).all())
        self.assertGreater(abs(matrix[0, 1]), 1)
        self.assertGreater(result["total_energy_J"], 0)
        self.assertAlmostEqual(matrix.sum(), result["total_energy_J"])
        self.assertLess(result["reciprocity_max_relative"], 1e-12)
        inductance = np.array(result["inductance_matrix_H_per_Aturn_basis"])
        np.testing.assert_allclose(inductance*1e10, 2*matrix, rtol=2e-15)
        # Independently integrate the complete two-coil target without reducing
        # by representative families; it must retain the same total energy.
        complete_target = concatenate_sources(target.values())
        direct = .5*integrate_current_dot_potential(complete_target, source, line_order=12,
                                                   backend="cpp", by_group=False)
        self.assertAlmostEqual(direct/result["total_energy_J"], 1, delta=2e-14)

    def test_symmetry_reduction_and_current_squared_scaling(self):
        one_source = fixture_coil("one", 2, 0)
        one_target = fixture_coil("one", 3, 0)
        rotate = np.diag([-1., -1., 1.])
        source = concatenate_sources([one_source, one_source.transformed(rotate)])
        complete_target = concatenate_sources([one_target, one_target.transformed(rotate)])
        result = magnetic_energy(source, [one_target], symmetry_multiplicity=2,
                                 line_order=12, backend="cpp")
        direct = .5*integrate_current_dot_potential(complete_target, source, line_order=12,
                                                   backend="cpp", by_group=False)
        self.assertAlmostEqual(result["total_energy_J"]/direct, 1, delta=2e-14)
        scaled = magnetic_energy(source.scaled(-2.3), [one_target.scaled(-2.3)],
                                 symmetry_multiplicity=2, line_order=12, backend="cpp")
        self.assertAlmostEqual(scaled["total_energy_J"]/direct, 2.3**2, delta=1e-12)

    def test_singular_target_and_invalid_contracts_rejected(self):
        source = fixture_coil("one", 2)
        with self.assertRaisesRegex(ValueError, "singular"):
            magnetic_energy(source, [source], symmetry_multiplicity=1, backend="cpp")
        with self.assertRaises(ValueError):
            magnetic_energy(source, {}, backend="cpp")
        with self.assertRaises(ValueError):
            magnetic_energy(source, [fixture_coil("one", 3)], symmetry_multiplicity=0, backend="cpp")

    def test_exact_matrix_rescaling_including_reversed_and_zero_current(self):
        source = concatenate_sources([fixture_coil("one", 2, 0), fixture_coil("two", 2, .7)])
        targets = {"one": fixture_coil("one", 3, 0), "two": fixture_coil("two", 3, .7)}
        original = magnetic_energy(source, targets, symmetry_multiplicity=1,
                                   line_order=12, reference_currents_Aturn=[1e5, 1e5], backend="cpp")
        rescaled = rescale_energy(original, {"one": 1.6e5, "two": -.6e5})
        actual_sources = concatenate_sources([fixture_coil("one", 2, 0).scaled(1.6),
                                               fixture_coil("two", 2, .7).scaled(-.6)])
        actual_targets = {"one": targets["one"].scaled(1.6), "two": targets["two"].scaled(-.6)}
        actual = magnetic_energy(actual_sources, actual_targets, symmetry_multiplicity=1,
                                 line_order=12, reference_currents_Aturn=[1.6e5, -.6e5], backend="cpp")
        np.testing.assert_allclose(rescaled["energy_matrix_J"], actual["energy_matrix_J"],
                                   atol=1e-10, rtol=2e-14)
        zero = rescale_energy(original, [0, 1e5])
        np.testing.assert_equal(np.array(zero["energy_matrix_J"])[0], [0, 0])
        self.assertEqual(zero["total_energy_J"], original["energy_matrix_J"][1][1])
        again = rescale_energy(zero, [1e5, 1e5])
        np.testing.assert_allclose(again["energy_matrix_J"], original["energy_matrix_J"], rtol=2e-15)


if __name__ == "__main__":
    unittest.main()
