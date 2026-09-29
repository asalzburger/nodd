"""DES-011 tests use small, explicitly artificial module inventories in mm."""
import copy
import math
import unittest

from tools.module_layout.optimization_services import build_optimized_services, default_policy
from tools.module_layout.services_budget import SUBSYSTEMS, _inventory, _selected, load_inputs
from tools.module_layout.services_geometry import route_connectivity


def fixture():
    """Test-only two barrel layers and two discs per subsystem and detector end."""
    bodies, layers, patches = [], [], []

    def body(lid, sub, region, r, z):
        mid = len(bodies)+1
        barrel = region == "barrel"
        b = dict(module_id=mid, layer_id=lid, station_id=lid, subsystem=sub,
                 region=region, family="single" if sub == "pixel" else sub,
                 row=0, col=0, level=0, center_mm=[r, 0., z], u=[0., 1., 0.],
                 v=[0., 0., 1.] if barrel else [1., 0., 0.],
                 n=[1., 0., 0.] if barrel else [0., 0., 1.],
                 half_u_mm=1., half_v_mm=5. if barrel else 10., half_w_mm=1.)
        bodies.append(b)
        patches.append(dict(b, id=mid, sensor_id=mid, face=0, patch=0,
                            active_area_mm2=10., sensor_area_mm2=12.))

    for sub, radii, disc_r in (("pixel", (31., 70.), 40.),
                               ("short_strip", (300., 420.), 340.),
                               ("long_strip", (850., 1000.), 900.)):
        for i, r in enumerate(radii):
            lid = f"test-{sub}-barrel-{i}"
            layers.append(dict(id=lid, subsystem=sub, kind="cylinder", r_m=r/1000,
                               z_min_m=-.11, z_max_m=.11))
            for sign in (-1, 1):
                body(lid, sub, "barrel", r, sign*100.)
        for sign in (-1, 1):
            for i, z in enumerate((350., 650.)):
                lid = f"test-{sub}-disc-{i}-{'P' if sign>0 else 'N'}"
                layers.append(dict(id=lid, subsystem=sub, kind="disc", z_m=sign*z/1000,
                                   r_min_m=(disc_r-10)/1000, r_max_m=(disc_r+11)/1000))
                body(lid, sub, "endcap", disc_r, sign*z)
    return dict(candidate="test-only", variant="test-only", bodies=bodies,
                modules=patches, layers=layers,
                metadata=dict(host=dict(r_min_m=.025, r_max_m=1.14, abs_z_max_m=3.15)))


class OptimizationServicesTests(unittest.TestCase):
    def setUp(self):
        self.layout = fixture()
        self.inputs = load_inputs()

    def build(self, policy=None, **kwargs):
        return build_optimized_services(self.layout, self.inputs, policy, **kwargs)

    def test_pure_repeatable_builder_preserves_every_body_patch_and_layer(self):
        before, inputs = copy.deepcopy(self.layout), copy.deepcopy(self.inputs)
        result = self.build()
        self.assertEqual(self.layout, before)
        self.assertEqual(self.inputs, inputs)
        self.assertEqual(result, self.build())
        self.assertEqual(result["failures"], [])
        self.assertTrue(result["sizing"]["all_sizing_capacities_pass"])
        self.assertEqual(result["diagnostics"]["route_body_conflicts"], [])
        self.assertEqual(result["diagnostics"]["route_support_conflicts"], [])
        self.assertTrue(result["budget"]["routing_graph"]["connected_per_signed_end"])

    def test_reflected_geometry_has_signed_bounds_and_identical_loads(self):
        result = self.build(diagnostics=False)
        routes = {r["id"]: r for r in result["routes"]}
        for r in routes.values():
            if r["side"] != "positive":
                continue
            # Disc names themselves encode the side as well as the route suffix.
            other = routes[r["id"].replace("-P-", "-N-").removesuffix("-P")+"-N"]
            self.assertEqual((r["r_min_mm"], r["r_max_mm"]),
                             (other["r_min_mm"], other["r_max_mm"]))
            self.assertEqual((r["z_min_mm"], r["z_max_mm"]),
                             (-other["z_max_mm"], -other["z_min_mm"]))
        for sub in SUBSYSTEMS:
            self.assertEqual(result["budget"]["ends"]["positive"][sub]["counts"],
                             result["budget"]["ends"]["negative"][sub]["counts"])

    def test_sizing_has_both_boundary_skins_margin_and_upward_rounding(self):
        result = self.build(diagnostics=False)
        for trunk in result["sizing"]["trunks"].values():
            self.assertGreaterEqual(trunk["width_mm"]+1e-8, trunk["unrounded_width_mm"])
            self.assertLess(trunk["width_mm"]-trunk["unrounded_width_mm"], 1.+1e-8)
            self.assertEqual(trunk["width_mm"], math.ceil(trunk["width_mm"]))
        self.assertEqual(result["sizing"]["boundary_allowance_mm"], 2.)
        for check in result["sizing"]["capacity_checks"]:
            self.assertAlmostEqual(check["required_capacity_mm2"], 1.1*check["demand_mm2"])
            self.assertGreaterEqual(check["capacity_mm2"]+1e-8, check["required_capacity_mm2"])
        # Decreasing one whole width quantum violates the active analytic bound.
        for trunk in result["sizing"]["trunks"].values():
            self.assertLess(trunk["width_mm"]-1., trunk["unrounded_width_mm"])

    def test_barrel_throat_can_set_width_above_full_trunk_area_minimum(self):
        p = default_policy()
        p["trunk_r_min_mm"]["pixel"] = 50.  # Test-only anchor inside outer barrel.
        result = self.build(p, diagnostics=False)
        trunk = result["sizing"]["trunks"]["pixel"]
        limits = trunk["limiting_requirements"]
        inventory = max(r["required_outer_mm"] for r in limits if "main_inventory" in r["source"])
        join = max(r["required_outer_mm"] for r in limits if "barrel_join" in r["source"])
        self.assertGreater(join, inventory+10.)
        self.assertTrue(result["sizing"]["all_sizing_capacities_pass"])

    def test_first_disc_constraint_accounts_for_service_bay_and_physical_offset(self):
        p = default_policy()
        p["barrel_bay_floor_mm"] = dict.fromkeys(SUBSYSTEMS, 10.)
        p["disc_collector_floor_mm"] = dict.fromkeys(SUBSYSTEMS, 10.)
        result = self.build(p, diagnostics=False)
        for side in ("positive", "negative"):
            for sub, c in result["placement_constraints"][side].items():
                self.assertGreaterEqual(c["minimum_first_disc_body_abs_z_mm"]-c["barrel_end_abs_z_mm"], 10.)
                self.assertGreaterEqual(c["minimum_first_disc_body_abs_z_mm"], c["barrel_bay_abs_z_mm"][1]+2.)
                self.assertAlmostEqual(c["minimum_first_disc_center_abs_z_mm"],
                                       c["minimum_first_disc_body_abs_z_mm"]+1.)
                for disc in c["disc_layers"]:
                    self.assertAlmostEqual(disc["minimum_gap_to_next_body_mm"],
                        disc["collector_depth_mm"]+p["support_depths_mm"][sub]+4.)
        # The unqualified 10 mm bay itself needs assembly clearance on both sides.
        c = result["placement_constraints"]["positive"]["pixel"]
        self.assertGreater(c["minimum_first_disc_body_abs_z_mm"]-c["barrel_end_abs_z_mm"], 10.)

    def test_bypass_partitions_inventory_without_losing_or_double_counting_cooling(self):
        plain = self.build(diagnostics=False)
        policy = default_policy()
        policy["bypass_last_disc"] = True
        bypass = self.build(policy)
        self.assertEqual(bypass["failures"], [])
        self.assertEqual(plain["budget"]["ends"], bypass["budget"]["ends"])
        for side in ("positive", "negative"):
            for sub in SUBSYSTEMS:
                partition = next(p for p in bypass["sizing"]["source_partitions"]
                                 if p["side"] == side and p["subsystem"] == sub)
                self.assertEqual(partition["main_modules"], 3)
                self.assertEqual(partition["bypass_modules"], 1)
                self.assertEqual(partition["all_modules"], 4)
                trunk = next(r for r in bypass["routes"] if r["side"] == side and
                             r["subsystem"] == sub and r["role"] == "subsystem_trunk")
                shadow = next(r for r in bypass["routes"] if r["side"] == side and
                              r["subsystem"] == sub and r["role"] == "last_disc_bypass")
                self.assertNotIn(partition["bypass_layer_id"], trunk["layer_ids"])
                self.assertEqual(shadow["layer_ids"], [partition["bypass_layer_id"]])
                self.assertLessEqual(shadow["r_max_mm"]+2., trunk["r_min_mm"])
            terminal = next(r for r in bypass["budget"]["routes"] if r["side"] == side
                            and r["id"].startswith("vessel-end-handoff"))
            baseline = next(r for r in plain["budget"]["routes"] if r["id"] == terminal["id"])
            self.assertEqual(terminal["modules_carried"], 12)
            for scenario in ("reference", "conservative", "stress"):
                self.assertEqual(terminal["scenarios"][scenario]["demand_mm2"],
                                 baseline["scenarios"][scenario]["demand_mm2"])
        # Every bypass has two explicit connections; incidental contacts are not
        # substituted for the declared tree or treated as extra source traffic.
        for r in bypass["routes"]:
            if r["role"] == "last_disc_bypass":
                self.assertEqual(len(r["connects_to"]), 1)
                target = next(t for t in bypass["routes"] if t["id"] == r["connects_to"][0])
                self.assertEqual(target["role"], "last_disc_bypass_turn")
                self.assertEqual(len(target["connects_to"]), 1)

    def test_every_declared_handoff_has_finite_contact_and_verified_margin(self):
        p = default_policy()
        p["bypass_last_disc"] = True
        result = self.build(p, diagnostics=False)
        contacts = {frozenset(pair) for pair in route_connectivity(result["routes"])["edges"]}
        declared = {frozenset((r["id"], t)) for r in result["routes"] for t in r["connects_to"]}
        tested = {frozenset(t["routes"]) for t in result["budget"]["throats"]}
        self.assertLessEqual(declared, contacts)
        self.assertEqual(declared, tested)
        self.assertTrue(result["sizing"]["all_sizing_capacities_pass"])

    def test_bypass_preserves_per_layer_manifold_rounding_for_many_local_groups(self):
        # Inventory-only fixture: nine final-disc radial groups, each with one
        # leaf, require two eight-leaf manifold banks. No geometry claim here.
        lid = "test-short_strip-disc-1-P"
        source = next(b for b in self.layout["bodies"] if b["layer_id"] == lid)
        patch = next(p for p in self.layout["modules"] if p["module_id"] == source["module_id"])
        for row in range(1, 9):
            mid = max(b["module_id"] for b in self.layout["bodies"])+1
            added = copy.deepcopy(source)
            added.update(module_id=mid, row=row)
            self.layout["bodies"].append(added)
            added_patch = copy.deepcopy(patch)
            added_patch.update(module_id=mid, id=mid, sensor_id=mid, row=row)
            self.layout["modules"].append(added_patch)
        policy = default_policy()
        policy["bypass_last_disc"] = True
        result = self.build(policy, diagnostics=False)
        groups = result["budget"]["local_groups"]
        branch = next(r for r in result["routes"] if r["id"] == "short_strip-last-disc-bypass-P")
        main = next(r for r in result["routes"] if r["id"] == "short_strip-trunk-P")
        bypass_inventory = _inventory(_selected(groups, branch), self.inputs)
        main_inventory = _inventory(_selected(groups, main), self.inputs)
        full = result["budget"]["ends"]["positive"]["short_strip"]
        self.assertEqual(bypass_inventory["counts"]["cooling_leaf_loops"], 9)
        self.assertEqual(bypass_inventory["cooling_trunk_pairs"], 2)
        self.assertEqual(main_inventory["cooling_trunk_pairs"]+bypass_inventory["cooling_trunk_pairs"],
                         full["cooling_trunk_pairs"])
        self.assertAlmostEqual(main_inventory["scenarios"]["reference"]["reserved_demand_mm2"]
                               +bypass_inventory["scenarios"]["reference"]["reserved_demand_mm2"],
                               full["scenarios"]["reference"]["reserved_demand_mm2"])

    def test_single_disc_per_end_can_bypass_while_barrel_uses_main_trunk(self):
        removed = {l["id"] for l in self.layout["layers"] if "-disc-0-" in l["id"]}
        self.layout["layers"] = [l for l in self.layout["layers"] if l["id"] not in removed]
        self.layout["bodies"] = [b for b in self.layout["bodies"] if b["layer_id"] not in removed]
        self.layout["modules"] = [m for m in self.layout["modules"] if m["layer_id"] not in removed]
        p = default_policy()
        p["bypass_last_disc"] = True
        result = self.build(p)
        self.assertEqual(result["failures"], [])
        self.assertEqual(sum(r["role"] == "disc_collector" for r in result["routes"]), 0)
        self.assertEqual(sum(r["role"] == "last_disc_bypass" for r in result["routes"]), 6)

    def test_unsafe_global_space_is_explicit_failure_without_weakening_demand(self):
        normal = self.build(diagnostics=False)
        p = default_policy()
        p["outer_radius_limit_mm"] = 1148.  # Test-only limit below required trunk.
        p["exit_abs_z_window_mm"] = [3555., 3556.]  # Test-only impossible 1 mm window.
        result = self.build(p, diagnostics=False)
        self.assertTrue(any(f.startswith("outer_radius_limit:") for f in result["failures"]))
        self.assertIn("exit_window_capacity:positive", result["failures"])
        self.assertEqual(result["budget"]["ends"], normal["budget"]["ends"])
        self.assertEqual(result["policy"]["capacity_factor"], 1.1)

    def test_support_and_module_clearance_are_not_exempted_for_own_routes(self):
        # Move the first pixel disc directly into its own radial barrel bay.
        lid = "test-pixel-disc-0-P"
        layer = next(l for l in self.layout["layers"] if l["id"] == lid)
        layer["z_m"] = .12
        for collection in (self.layout["bodies"], self.layout["modules"]):
            for b in collection:
                if b["layer_id"] == lid:
                    b["center_mm"][2] = 120.
        result = self.build()
        self.assertIn("first_disc_clearance:pixel:positive", result["failures"])
        self.assertIn("route_body_conflicts", result["failures"])
        self.assertIn("route_support_conflicts", result["failures"])

    def test_sizing_only_output_cannot_claim_checked_geometry(self):
        result = self.build(diagnostics=False)
        self.assertTrue(result["diagnostics"]["skipped"])
        self.assertIn("unvalidated", result["diagnostics"]["reason"])

    def test_defaults_are_independent_and_invalid_policies_fail(self):
        p = default_policy()
        p["trunk_r_min_mm"]["pixel"] = 999.
        self.assertEqual(default_policy()["trunk_r_min_mm"]["pixel"], 170.)
        for key, value in (("capacity_factor", .9), ("clearance_mm", -1.),
                           ("rounding_mm", 0.), ("minimum_barrel_disc_clearance_mm", 9.),
                           ("bypass_last_disc", "yes")):
            with self.subTest(key=key):
                p = default_policy()
                p[key] = value
                with self.assertRaises(ValueError):
                    self.build(p, diagnostics=False)


if __name__ == "__main__":
    unittest.main()
