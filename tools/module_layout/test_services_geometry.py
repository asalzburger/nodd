"""DES-010 exclusion contracts; deliberately small test-only millimetre fixtures."""
import copy
import math
import unittest

from tools.module_layout import geometry
from tools.module_layout.services_geometry import (
    apply_reservations, body_envelope, reservation_diagnostics,
    route_connectivity, support_envelopes,
)


def fixture_body(mid, layer, row, center, *, region="endcap", half_v=4.):
    return dict(module_id=mid, layer_id=layer, station_id=layer, subsystem="pixel",
                region=region, family="single", row=row, col=0, level=0,
                center_mm=list(center), u=[0., 1., 0.],
                v=[1., 0., 0.] if region == "endcap" else [0., 0., 1.],
                n=[0., 0., 1.] if region == "endcap" else [1., 0., 0.],
                half_u_mm=1., half_v_mm=half_v, half_w_mm=1.)


def fixture_layout(bodies, layers):
    patches = []
    for b in bodies:
        # Two patches per one physical sensor verifies patch grouping, not just IDs.
        for patch in range(2):
            p = dict(b)
            p.update(id=10*b["module_id"]+patch, sensor_id=100+b["module_id"],
                     face=0, patch=patch, sensor_area_mm2=8., active_area_mm2=3.)
            patches.append(p)
    return dict(candidate="test-only", variant="test-only", bodies=bodies,
                modules=patches, layers=layers,
                metadata=dict(host=dict(r_min_m=0., r_max_m=.1, abs_z_max_m=.3),
                              model_sha256="test-model", layout_sha256="test-layout"))


def disc_fixture():
    bodies, layers = [], []
    for side in (-1, 1):
        lid = "test-disc-"+str(side)
        layers.append(dict(id=lid, kind="disc", subsystem="pixel", z_m=side*.1))
        for row, r in enumerate((10., 20., 30.)):
            bodies.append(fixture_body(len(bodies)+1, lid, row, [r, 0., side*100.]))
    return fixture_layout(bodies, layers)


def route(name="test-route", **overrides):
    result = dict(id=name, subsystem="pixel", kind="axial",
                  r_min_mm=0., r_max_mm=15., z_min_mm=90., z_max_mm=110.)
    result.update(overrides)
    return result


class ServiceGeometryTests(unittest.TestCase):
    def test_cylindrical_bounds_use_edge_minimum_and_corner_maximum(self):
        b = fixture_body(1, "test", 0, [10., 0., 5.], half_v=2.)
        b["half_u_mm"] = 3.
        envelope = body_envelope(b)
        self.assertEqual(envelope["r_min_mm"], 8.)
        self.assertAlmostEqual(envelope["r_max_mm"], math.hypot(12., 3.))
        self.assertEqual((envelope["z_min_mm"], envelope["z_max_mm"]), (4., 6.))

    def test_projection_containing_axis_has_zero_radial_minimum(self):
        b = fixture_body(1, "test", 0, [0., 0., 5.])
        self.assertEqual(body_envelope(b)["r_min_mm"], 0.)

    def test_reflected_carving_retains_exact_ids_transforms_and_denominators(self):
        original = disc_fixture()
        snapshot = copy.deepcopy(original)
        routes = [route(), route("test-negative", z_min_mm=-110., z_max_mm=-90.)]
        result = apply_reservations(original, routes, {"pixel": 2.}, .5)
        expected_ids = {2, 3, 5, 6}
        self.assertEqual(original, snapshot)
        self.assertEqual(result["layers"], original["layers"])
        self.assertEqual(result["bodies"], [b for b in original["bodies"] if b["module_id"] in expected_ids])
        self.assertEqual(result["modules"], [p for p in original["modules"] if p["module_id"] in expected_ids])
        self.assertEqual(result, apply_reservations(original, routes, {"pixel": 2.}, .5))
        report = result["metadata"]["services"]
        self.assertEqual(report["removed_module_ids"], [1, 4])
        self.assertEqual(report["removed_summary"]["total"]["modules"], 2)
        self.assertEqual(report["removed_summary"]["total"]["sensors"], 2)
        self.assertEqual(report["removed_summary"]["total"]["patches"], 4)
        self.assertAlmostEqual(report["removed_summary"]["total"]["sensor_area_m2"], 16e-6)
        self.assertEqual(report["diagnostics"]["route_body_conflicts"], [])
        self.assertEqual(report["diagnostics"]["route_support_conflicts"], [])
        result["bodies"][0]["center_mm"][0] = 999.
        self.assertEqual(original, snapshot, "returned bodies must not alias caller's input")

    def test_support_reflects_outwards_and_spans_retained_radial_body_extent(self):
        supports = support_envelopes(disc_fixture(), {"pixel": 3.})
        self.assertEqual([(s["z_min_mm"], s["z_max_mm"]) for s in supports],
                         [(-104., -101.), (101., 104.)])
        for s in supports:
            self.assertEqual(s["r_min_mm"], 6.)
            self.assertAlmostEqual(s["r_max_mm"], math.hypot(34., 1.))

    def test_support_only_collision_triggers_whole_row_carving(self):
        # This reservation misses sensor bodies (z<=101), but cuts their support.
        result = apply_reservations(disc_fixture(),
                                    [route(z_min_mm=102., z_max_mm=105.)], {"pixel": 3.})
        self.assertEqual(result["metadata"]["services"]["removed_module_ids"], [4])
        self.assertEqual(result["metadata"]["services"]["removed_rows"][0]["reasons"],
                         ["support:test-route"])

    def test_barrel_support_clearance_trims_only_original_end_rows(self):
        lid = "test-barrel"
        bodies = [fixture_body(i+1, lid, i, [30., 0., z], region="barrel", half_v=3.)
                  for i, z in enumerate((-20., 0., 20.))]
        fixture = fixture_layout(bodies, [dict(id=lid, kind="cylinder", subsystem="pixel",
                                           r_m=.03, z_min_m=-.025, z_max_m=.025)])
        # Inward support is r25..29; bodies begin at29, so only support conflicts.
        routes = [route(r_min_mm=24., r_max_mm=28., z_min_mm=18., z_max_mm=25.)]
        result = apply_reservations(fixture, routes, {"pixel": 4.})
        self.assertEqual([b["row"] for b in result["bodies"]], [0, 1])
        support = result["metadata"]["services"]["supports"][0]
        self.assertEqual((support["r_min_mm"], support["r_max_mm"]), (25., 29.))
        self.assertEqual(support["z_max_mm"], 3.)

    def test_empty_layer_is_rejected_instead_of_silently_deleted(self):
        with self.assertRaisesRegex(ValueError, "every row"):
            apply_reservations(disc_fixture(), [route(r_max_mm=40.)], {"pixel": 3.})

    def test_manual_row_exclusion_is_explicit_and_validated(self):
        result = apply_reservations(disc_fixture(), [], {}, removed_rows=[("test-disc-1", 2)])
        self.assertEqual(result["metadata"]["services"]["removed_module_ids"], [6])
        with self.assertRaisesRegex(ValueError, "unknown"):
            apply_reservations(disc_fixture(), [], {}, removed_rows=[("test-disc-1", 99)])

    def test_internal_support_hole_cannot_masquerade_as_continuous_corridor(self):
        with self.assertRaisesRegex(ValueError, "interior hole"):
            apply_reservations(disc_fixture(),
                               [route(r_min_mm=18., r_max_mm=22., z_min_mm=102., z_max_mm=105.)],
                               {"pixel": 3.})

    def test_clearance_changes_exclusion_at_exact_boundary(self):
        routes = [route(r_max_mm=6.)]
        self.assertEqual(apply_reservations(disc_fixture(), routes, {})["metadata"]["services"]["removed_module_ids"], [])
        self.assertEqual(apply_reservations(disc_fixture(), routes, {}, .1)["metadata"]["services"]["removed_module_ids"], [4])

    def test_connections_allow_finite_face_and_reject_corner_only_contact(self):
        a = route("a", r_min_mm=1., r_max_mm=10., z_min_mm=1., z_max_mm=10.)
        b = route("b", r_min_mm=5., r_max_mm=15., z_min_mm=10., z_max_mm=20., exit=True)
        self.assertTrue(route_connectivity([a, b])["all_connected_per_subsystem_side"])
        c = route("c", r_min_mm=10., r_max_mm=20., z_min_mm=10., z_max_mm=20.)
        self.assertFalse(route_connectivity([a, c])["all_connected_per_subsystem_side"])
        neg = route("negative", z_min_mm=-20., z_max_mm=-10.)
        self.assertTrue(route_connectivity([a, b, neg])["all_connected_per_subsystem_side"])

    def test_diagnostics_do_not_hide_own_collector_or_support_conflicts(self):
        layout = disc_fixture()
        supports = support_envelopes(layout, {"pixel": 3.})
        support = copy.deepcopy(supports[-1])
        support["id"] = "test-duplicate-support"
        supports.append(support)
        d = reservation_diagnostics(layout, [route(z_min_mm=102., z_max_mm=105.)], supports)
        self.assertEqual(len(d["route_support_conflicts"]), 2)
        self.assertTrue(all(x["own_subsystem"] for x in d["route_support_conflicts"]))
        self.assertEqual(d["support_pair_conflicts"], [["support:test-disc-1", "test-duplicate-support"]])
        supports[-1]["z_min_mm"] = 99.
        self.assertTrue(reservation_diagnostics(layout, [], supports)["support_body_conflicts"])

    def test_support_host_overflow_is_reported(self):
        layout = disc_fixture()
        layout["metadata"]["host"]["abs_z_max_m"] = .102
        d = reservation_diagnostics(layout, [], support_envelopes(layout, {"pixel": 3.}))
        self.assertEqual(len(d["support_host_violations"]), 2)
        self.assertEqual(d["support_host_violations"][0]["excess_inner_outer_z_mm"], [0., 0., 2.])

    def test_bad_reservations_fail_before_mutation(self):
        fixture = disc_fixture()
        for routes, depth, clearance in (([route(), route()], {}, 0.),
                                         ([route(r_max_mm=float("nan"))], {}, 0.),
                                         ([route()], {"pixel": -1.}, 0.),
                                         ([route()], {}, -.1)):
            with self.subTest(routes=routes, depth=depth, clearance=clearance):
                with self.assertRaises(ValueError):
                    apply_reservations(fixture, routes, depth, clearance)


if __name__ == "__main__":
    unittest.main()
