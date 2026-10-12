"""Synthetic geometry controls for coverage-guarded path-spacing measurements."""

import copy
import json
import math
import unittest

import numpy as np

from tools.module_layout.intersections import KAPPA_MM, evaluate, positions
from tools.module_layout.optimization_metrics import (coverage_strata_regressions,
    evaluate_spacing, summarize_cohort, summarize_coverage_strata)
from tools.module_layout.sampling import directions, tracks_for


def ray(**changes):
    return dict(dict(origin_mm=[0., 0., 0.], eta=0., phi=0., charge=1,
                     pt_GeV=1., field_T=0.), **changes)


def patch(identifier, center, *, station=None, subsystem="pixel", **changes):
    station = identifier if station is None else station
    return dict(dict(id=identifier, sensor_id=identifier, module_id=identifier,
                     center_mm=list(center), u=[0., 1., 0.], v=[0., 0., 1.],
                     half_u_mm=1., half_v_mm=1., layer_id=station, station_id=station,
                     subsystem=subsystem, region="barrel", face=0), **changes)


def cylinder(identifier, radius, subsystem="pixel"):
    return dict(id=identifier, kind="cylinder", subsystem=subsystem,
                r_m=radius/1000., z_min_m=-2., z_max_m=2.)


def coverage_row(index, stations, *, eta=0., z=0., phi=None, cohort="central_grid", ideal=2):
    """Test-only observed station counts, independent of any placement policy."""
    counts = dict(stations=stations, ideal_stations=ideal,
                  missing_stations=max(0, ideal-stations))
    return dict(track_index=index,
                track=ray(eta=eta, phi=float(index) if phi is None else phi,
                          origin_mm=[.5, .5, z], cohort=cohort),
                total=counts, per_subdetector={"long_strip": counts})


def local_report(records):
    return dict(local_coverage=summarize_coverage_strata(records))


class OptimizationMetricsTests(unittest.TestCase):
    def test_central_hole_fails_despite_improved_overall_station_mean(self):
        baseline = [coverage_row(0, 2), coverage_row(1, 2),
                    coverage_row(2, 0, eta=1.), coverage_row(3, 0, eta=1.)]
        candidate = [coverage_row(0, 0), coverage_row(1, 0),
                     coverage_row(2, 3, eta=1.), coverage_row(3, 3, eta=1.)]
        self.assertGreater(sum(r["total"]["stations"] for r in candidate),
                           sum(r["total"]["stations"] for r in baseline))
        result = coverage_strata_regressions(local_report(candidate), local_report(baseline))
        self.assertFalse(result["passed"])
        self.assertFalse(result["central_pass"])
        self.assertFalse(result["no_new_blind_strata_pass"])
        central = next(c for c in result["central_failures"] if c["subsystem"] == "long_strip")
        self.assertEqual(central["station_sum_delta"], -4)
        self.assertEqual(central["zero_station_tracks_delta"], 2)
        self.assertEqual(central["mean_stations_delta"], -2.)

    def test_central_mean_and_zero_fraction_are_independent_strict_guards(self):
        baseline = local_report([coverage_row(0, 1), coverage_row(1, 1)])
        # Unchanged mean must not excuse introducing zero-hit central rays.
        redistributed = local_report([coverage_row(0, 0), coverage_row(1, 2)])
        result = coverage_strata_regressions(redistributed, baseline)
        self.assertFalse(result["central_pass"])
        self.assertTrue(result["no_new_blind_strata_pass"])
        self.assertEqual(result["central_failures"][0]["station_sum_delta"], 0)
        # A mean loss with no newly zero-hit ray also fails, without a tolerance.
        reduced = local_report([coverage_row(0, 1), coverage_row(1, 1)])
        higher = local_report([coverage_row(0, 1), coverage_row(1, 2)])
        self.assertFalse(coverage_strata_regressions(reduced, higher)["central_pass"])
        self.assertTrue(coverage_strata_regressions(higher, reduced)["passed"])

    def test_smaller_local_losses_reported_but_only_new_blind_strata_rejected(self):
        baseline_rows = [coverage_row(0, 2), coverage_row(1, 2, eta=-1., z=150.),
                         coverage_row(2, 1, eta=-1., z=150., ideal=0)]
        baseline = local_report(baseline_rows)
        smaller_rows = [baseline_rows[0], coverage_row(1, 0, eta=-1., z=150.), baseline_rows[2]]
        smaller = coverage_strata_regressions(local_report(smaller_rows), baseline)
        self.assertTrue(smaller["passed"])
        self.assertTrue(smaller["local_regressions"])
        self.assertGreater(smaller["local_regressions"][0]["zero_station_tracks_delta"], 0)
        blind_rows = [*smaller_rows[:2], coverage_row(2, 0, eta=-1., z=150., ideal=0)]
        blind = coverage_strata_regressions(local_report(blind_rows), baseline)
        self.assertTrue(blind["central_pass"])
        self.assertFalse(blind["no_new_blind_strata_pass"])
        # Ideal eligibility cannot erase a previously reached physical station.
        extra_baseline = local_report([coverage_row(0, 2), coverage_row(1, 1, eta=1., ideal=0)])
        extra_candidate = local_report([coverage_row(0, 2), coverage_row(1, 0, eta=1., ideal=0)])
        self.assertFalse(coverage_strata_regressions(extra_candidate, extra_baseline)["passed"])

    def test_strata_bin_endpoints_planes_interior_and_sample_accounting(self):
        etas = [-4.1, -4., -.5, -1e-12, 0., .5, 4., 4.1]
        rows = [coverage_row(i, 1, eta=eta, z=-150.) for i, eta in enumerate(etas)]
        rows += [coverage_row(8, 2), coverage_row(9, 1, eta=.1, z=12.),
                 coverage_row(10, 0, eta=.1, z=0., cohort="off_grid")]
        result = summarize_coverage_strata(rows)
        strata = result["strata"]
        self.assertEqual(strata["grid/eta_00/vertex_0"]["tracks"], 1)
        self.assertEqual(strata["grid/eta_07/vertex_0"]["tracks"], 2)
        self.assertEqual(strata["grid/eta_08/vertex_0"]["tracks"], 1)
        self.assertEqual(strata["grid/eta_09/vertex_0"]["tracks"], 1)
        self.assertEqual(strata["grid/eta_15/vertex_0"]["tracks"], 1)
        self.assertTrue(strata["grid/eta_15/vertex_0"]["identity"]["upper_endpoint_included"])
        self.assertEqual(strata["grid/below_range/vertex_0"]["tracks"], 1)
        self.assertEqual(strata["grid/above_range/vertex_0"]["tracks"], 1)
        self.assertEqual(strata["other_interior/eta_08"]["tracks"], 1)
        self.assertEqual(strata["off_grid/eta_08"]["tracks"], 1)
        self.assertEqual(strata["central_eta0_z0"]["tracks"], 1)
        self.assertEqual(sum(s["tracks"] for key, s in strata.items() if key != "central_eta0_z0"), len(rows))
        json.dumps(result, allow_nan=False)

    def test_offgrid_losses_reported_without_plane_guard_and_empty_central_untested(self):
        baseline = [coverage_row(0, 2), coverage_row(1, 2, eta=1., z=42., cohort="off_grid")]
        candidate = [baseline[0], coverage_row(1, 0, eta=1., z=42., cohort="off_grid")]
        result = coverage_strata_regressions(local_report(candidate), local_report(baseline))
        self.assertTrue(result["passed"])
        self.assertTrue(result["local_regressions"])
        for rows in ([], [baseline[1]]):
            report = local_report(rows)
            missing = coverage_strata_regressions(report, report)
            self.assertFalse(missing["central_tested"])
            self.assertFalse(missing["passed"])
            self.assertTrue(missing["no_new_blind_strata_pass"])
            json.dumps(missing, allow_nan=False)

    def test_strata_comparison_rejects_unpaired_tracks_modes_and_membership(self):
        rows = [coverage_row(0, 2), coverage_row(1, 2)]
        baseline = local_report(rows)
        for field, value in (("phi", .3), ("charge", -1), ("field_T", 3.),
                             ("pt_GeV", 2.), ("origin_mm", [1., .5, 0.]),
                             ("cohort", "luminous_boundary_grid")):
            changed = copy.deepcopy(rows)
            changed[0]["track"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "paired"):
                coverage_strata_regressions(local_report(changed), baseline)
        with self.assertRaisesRegex(ValueError, "paired"):
            coverage_strata_regressions(local_report(rows[::-1]), baseline)
        altered = copy.deepcopy(baseline)
        altered["local_coverage"]["strata"]["central_eta0_z0"]["sample_sha256"] = "bad"
        with self.assertRaisesRegex(ValueError, "paired stratum"):
            coverage_strata_regressions(altered, baseline)
        for options in (dict(eta_bin_edges=[0., 0.]), dict(eta_bin_edges=[0., float("nan")]),
                        dict(vertex_z_planes_mm=[0., 0.]), dict(vertex_z_planes_mm=[])):
            with self.assertRaises(ValueError):
                summarize_coverage_strata(rows, **options)

    def test_oracle_local_coverage_retained_without_per_track_and_stereo_usable(self):
        modules = [patch("a0", [100., 0., 0.], station="a", subsystem="long_strip", module_id="a", face=0),
                   patch("a1", [105., 0., 0.], station="a", subsystem="long_strip", module_id="a", face=1)]
        layout = dict(modules=modules, layers=[cylinder("a", 100., "long_strip")])
        tracks = [ray(phi=0.), ray(phi=.1)]
        detailed = evaluate_spacing(layout, tracks)
        compact = evaluate_spacing(layout, tracks, return_per_track=False)
        self.assertNotIn("per_track", compact)
        self.assertEqual(compact["local_coverage"], detailed["local_coverage"])
        central = compact["local_coverage"]["strata"]["central_eta0_z0"]["per_subdetector"]["long_strip"]
        self.assertEqual(central["station_sum"], 1)
        self.assertEqual(central["zero_station_tracks"], 1)
        orphan = evaluate_spacing(dict(layout, modules=modules[:1]), tracks, return_per_track=False)
        guard = coverage_strata_regressions(orphan, compact)
        self.assertFalse(guard["passed"])
        self.assertEqual(guard["central_failures"][0]["candidate"]["station_sum"], 0)

    def test_cohort_matches_fresh_subset_without_another_oracle_pass(self):
        layout = dict(modules=[patch("a", [100., 0., 0.]), patch("b", [200., 0., 0.])],
                      layers=[cylinder("a", 100.), cylinder("b", 200.)])
        tracks = [ray(phi=phi) for phi in (0., .002, .5, .004)]
        report = evaluate_spacing(layout, tracks)
        whole = summarize_cohort(report["per_track"])
        self.assertEqual(whole["total"], report["total"])
        self.assertEqual(whole["per_subdetector"], report["per_subdetector"])
        subset = summarize_cohort(report["per_track"][1::2])
        fresh = evaluate_spacing(layout, tracks[1::2])
        self.assertEqual(subset["total"], fresh["total"])
        self.assertEqual(subset["per_subdetector"], fresh["per_subdetector"])
        self.assertEqual(subset["track_indices"], [1, 3])
        with self.assertRaisesRegex(ValueError, "homogeneous"):
            summarize_cohort([report["per_track"][0], dict(report["per_track"][1], per_subdetector={})])
        self.assertEqual(summarize_cohort([])["total"]["tracks"], 0)

    def test_straight_arc_chord_boundary_and_subsystem_distances(self):
        track = ray(eta=math.asinh(1.))
        paths = [100., 200., 450.]
        layout = dict(modules=[patch(str(s), positions(track, s)) for s in reversed(paths)],
                      layers=[cylinder(str(s), s) for s in paths])
        report = evaluate_spacing(layout, [track], host_radius_mm=500.)
        row = report["per_track"][0]["total"]
        spacing = row["station_spacing"]
        np.testing.assert_allclose(spacing["path_mm"], np.array(paths)*math.sqrt(2))
        np.testing.assert_allclose(spacing["inter_hit_chords_mm"], spacing["inter_hit_gaps_mm"])
        self.assertAlmostEqual(spacing["max_inter_hit_gap_mm"], 250*math.sqrt(2))
        self.assertAlmostEqual(spacing["origin_to_first_mm"], 100*math.sqrt(2))
        self.assertAlmostEqual(spacing["last_to_exit_mm"], 50*math.sqrt(2))
        self.assertEqual(report["total"]["missing_ideal_station_fraction"], 0.)
        self.assertEqual(report["total"], report["per_subdetector"]["pixel"])

    def test_both_curvature_signs_use_arc_not_chord_or_radius_order(self):
        for charge in (-1, 1):
            with self.subTest(charge=charge):
                track = ray(field_T=3., charge=charge, eta=.7, origin_mm=[1., .5, -150.])
                paths = [100., 400., 800.]
                layout = dict(modules=[patch(str(s), positions(track, s)) for s in reversed(paths)])
                row = evaluate_spacing(layout, [track])["per_track"][0]["total"]
                spacing = row["station_spacing"]
                np.testing.assert_allclose(spacing["path_mm"], np.array(paths)*math.cosh(.7), atol=1e-6)
                for arc, chord in zip(spacing["inter_hit_gaps_mm"], spacing["inter_hit_chords_mm"]):
                    self.assertGreater(arc, chord)
                self.assertEqual(spacing["ids"], [str(s) for s in paths])

    def test_sensor_islands_and_overlaps_do_not_inflate_stations(self):
        modules = [patch("island-a", [100., 0., 0.], station="a", sensor_id="one", module_id="one"),
                   patch("island-b", [100., 0., 0.], station="a", sensor_id="one", module_id="one"),
                   patch("overlap", [101., 0., 0.], station="a"),
                   patch("next", [200., 0., 0.], station="b")]
        row = evaluate_spacing(dict(modules=modules), [ray()])["per_track"][0]["total"]
        self.assertEqual(row["sensor_hits"], 3)
        self.assertEqual(row["stations"], 2)
        self.assertEqual(row["sensor_spacing"]["path_mm"], [100., 101., 200.])
        self.assertEqual(row["station_spacing"]["path_mm"], [100., 200.])

    def test_same_module_stereo_pair_midpoint_and_orphan_faces(self):
        modules = [patch("pixel", [50., 0., 0.])]
        for module_id, paths in (("complete", [100., 106.]), ("later", [104., 110.])):
            for face, path in enumerate(paths):
                modules.append(patch(f"{module_id}-{face}", [path, 0., 0.], station="long",
                                     subsystem="long_strip", module_id=module_id, face=face))
        modules += [patch("left", [150., 0., 0.], station="orphan", subsystem="long_strip", face=0),
                    patch("right", [156., 0., 0.], station="orphan", subsystem="long_strip", face=1)]
        layout = dict(modules=modules)
        row = evaluate_spacing(layout, [ray()])["per_track"][0]["total"]
        self.assertEqual(row["complete_long_strip_pairs"], 2)
        self.assertEqual(row["orphan_long_strip_faces"], 2)
        self.assertEqual(row["station_spacing"]["ids"], ["pixel", "long"])
        self.assertEqual(row["station_spacing"]["path_mm"], [50., 103.])
        existing = evaluate(layout, [ray()])["per_track"]
        for key in ("sensor_hits", "stations", "complete_long_strip_pairs", "orphan_long_strip_faces"):
            self.assertEqual(row[key], existing[key][0])

    def test_hit_loss_retains_missing_penalty_and_boundary_gap(self):
        layers = [cylinder(str(s), s) for s in (100., 200., 300.)]
        full = dict(modules=[patch(str(s), [s, 0., 0.]) for s in (100., 200., 300.)], layers=layers)
        baseline = evaluate_spacing(full, [ray()], reference_layers=layers, host_radius_mm=400.)
        for keep in ([0, 1], [1, 2], [0, 2], [1], []):
            with self.subTest(keep=keep):
                reduced = dict(modules=[full["modules"][i] for i in keep], layers=layers)
                report = evaluate_spacing(reduced, [ray()], reference_layers=layers, host_radius_mm=400.)
                self.assertGreater(report["total"]["missing_ideal_station_fraction"], 0.)
                self.assertGreaterEqual(report["total"]["station_spacing"]["max_boundary_gap_mm"]["max"],
                                        baseline["total"]["station_spacing"]["max_boundary_gap_mm"]["max"])
                if len(keep) < 2:
                    self.assertIsNone(report["total"]["station_spacing"]["max_inter_hit_gap_mm"]["mean"])
                    self.assertEqual(report["total"]["tracks_with_at_least_two_stations"], 0)
        zero = evaluate_spacing(dict(modules=[], layers=layers), [ray()], host_radius_mm=400.)
        self.assertEqual(zero["total"]["station_spacing"]["max_boundary_gap_mm"]["max"], 400.)

    def test_fixed_reference_hole_cannot_be_hidden_by_moved_layer_or_extra_hit(self):
        reference = [cylinder("a", 100.), cylinder("b", 200.)]
        moved = [dict(reference[0], z_min_m=1., z_max_m=2.), reference[1]]
        layout = dict(layers=moved, modules=[patch("b", [200., 0., 0.]), patch("extra", [300., 0., 0.])])
        local = evaluate_spacing(layout, [ray()])
        fixed = evaluate_spacing(layout, [ray()], reference_layers=reference)
        self.assertEqual(local["reference_basis"], "candidate_local")
        self.assertEqual(local["total"]["missing_ideal_station_fraction"], 0.)
        self.assertEqual(fixed["reference_basis"], "external_fixed")
        self.assertEqual(fixed["total"]["missing_ideal_station_fraction"], .5)
        self.assertEqual(fixed["per_track"][0]["total"]["missing_station_ids"], ["a"])
        self.assertEqual(fixed["per_track"][0]["total"]["extra_station_ids"], ["extra"])

    def test_repeated_plane_crossing_retains_first_sensor_encounter(self):
        # Test-only radius100 mm curl: x=50 is crossed twice before the half-turn.
        track = ray(field_T=1., pt_GeV=100*KAPPA_MM)
        first, second = 100*math.pi/6, 100*5*math.pi/6
        layout = dict(modules=[patch("late", positions(track, second), station="same",
                                    module_id="one", sensor_id="one"),
                               patch("early", positions(track, first), station="same",
                                     module_id="one", sensor_id="one")])
        report = evaluate_spacing(layout, [track])
        row = report["per_track"][0]
        self.assertAlmostEqual(row["traversal_path_mm"], 100*math.pi)
        self.assertEqual(row["total"]["sensor_hits"], 1)
        self.assertAlmostEqual(row["total"]["sensor_spacing"]["path_mm"][0], first, places=6)
        self.assertIsNone(row["total"]["station_spacing"]["max_inter_hit_gap_mm"])

    def test_empty_and_ineligible_samples_stay_null_and_json_safe(self):
        layout = dict(modules=[])
        empty = evaluate_spacing(layout, [], return_per_track=False)
        self.assertNotIn("per_track", empty)
        self.assertEqual(empty["total"]["tracks"], 0)
        self.assertIsNone(empty["total"]["missing_ideal_station_fraction"])
        self.assertIsNone(empty["total"]["worst_boundary_gap_track_index"])
        ineligible = evaluate_spacing(layout, [ray()])
        self.assertEqual(ineligible["total"]["eligible_tracks"], 0)
        self.assertIsNone(ineligible["total"]["fraction_all_ideal_stations_hit"])
        json.dumps([empty, ineligible], allow_nan=False)

    def test_inconsistent_identity_and_invalid_host_rejected(self):
        modules = [patch("one", [100., 0., 0.]), patch("two", [200., 0., 0.],
                                                                      station="one", subsystem="short_strip")]
        with self.assertRaisesRegex(ValueError, "subsystems"):
            evaluate_spacing(dict(modules=modules), [ray()])
        with self.assertRaisesRegex(ValueError, "Host"):
            evaluate_spacing(dict(modules=[]), [ray()], host_radius_mm=float("nan"))

    def test_sampling_three_modes_and_separate_offgrid_holdout(self):
        config = dict(eta_max=4., eta_points=3, phi_points=4, z_vertices_mm=[-150., 0., 150.],
                      xy_center_mm=[.5, .5], stress_eta_points=3, stress_phi_points=4,
                      xy_corner_values_mm=[0., 1.], seed=101, random_tracks=8,
                      momentum_convention="pt", momentum_GeV=1., field_T=3.)
        training = directions(config)
        held_config = dict(config, seed=102)
        holdout = [t for t in directions(held_config) if t["cohort"] == "off_grid"]
        self.assertEqual(holdout, [t for t in directions(held_config) if t["cohort"] == "off_grid"])
        self.assertTrue(all(t not in training for t in holdout))
        for mode, charge, field in (("straight", 1, 0.), ("positive", 1, 3.), ("negative", -1, 3.)):
            tracks = tracks_for(holdout, mode, config)
            for track in tracks:
                self.assertEqual((track["charge"], track["field_T"], track["pt_GeV"]), (charge, field, 1.))
                x, y, z = track["origin_mm"]
                self.assertTrue(0. <= x <= 1. and 0. <= y <= 1. and -150. <= z <= 150.)


if __name__ == "__main__":
    unittest.main()
