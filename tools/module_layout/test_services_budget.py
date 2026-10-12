"""Synthetic controls for service ownership, local rounding and bottlenecks."""
import copy
import math
import unittest

from services_budget import estimate_budget, load_inputs


def layout_fixture(specs):
    """Named test values: (subsystem, region, layer, col, row, z, chips)."""
    layout = dict(bodies=[], modules=[])
    pid = 0
    for mid, (sub, region, layer, col, row, z, chips) in enumerate(specs, 1):
        family = {1:"single", 2:"double", 4:"quad"}.get(chips, sub)
        layout["bodies"].append(dict(module_id=mid, subsystem=sub, region=region,
                                     layer_id=layer, family=family, col=col, row=row,
                                     center_mm=[100., 0., z], half_u_mm=2., half_v_mm=3.))
        for _ in range(chips if sub == "pixel" else 2 if sub == "long_strip" else 1):
            pid += 1
            layout["modules"].append(dict(id=pid, module_id=mid, subsystem=sub))
    return layout


def route_fixture(name="route", subsystem="pixel", **changes):
    route = dict(id=name, subsystem=subsystem, kind="axial",
                 r_min_mm=100., r_max_mm=200., z_min_mm=10., z_max_mm=30.)
    route.update(changes)
    return route


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.inputs = load_inputs()

    def test_short_partial_groups_keep_independent_harnesses(self):
        layout = layout_fixture([("short_strip", "barrel", "B", col, 0, 10., 0)
                                 for col in range(2)])
        result = estimate_budget(layout, self.inputs, [])
        inventory = result["ends"]["positive"]["short_strip"]
        self.assertEqual(inventory["counts"]["harnesses"], 2)
        self.assertEqual(inventory["counts"]["cooling_leaf_loops"], 2)
        self.assertEqual(inventory["cooling_trunk_pairs"], 1)
        scenario = inventory["scenarios"]["reference"]
        self.assertAlmostEqual(scenario["cables_mm2"], 2*math.pi*(13.4**2+3.6**2)/4)
        self.assertAlmostEqual(scenario["feed_mm2"], math.pi*8**2/4)
        self.assertAlmostEqual(scenario["return_mm2"], math.pi*12**2/4)

    def test_manifold_does_not_cross_layer_or_signed_end(self):
        specs = [("long_strip", "endcap", layer, 0, 0, z, 0)
                 for layer, z in (("P1", 10.), ("P2", 20.), ("N1", -10.))]
        result = estimate_budget(layout_fixture(specs), self.inputs, [])
        positive = result["ends"]["positive"]["long_strip"]
        negative = result["ends"]["negative"]["long_strip"]
        self.assertEqual(positive["cooling_trunk_pairs"], 2)
        self.assertEqual(negative["cooling_trunk_pairs"], 1)
        self.assertEqual(positive["counts"]["modules"], 2)  # four faces, two pairs
        self.assertAlmostEqual(positive["reference_power_W"], 10.8)

    def test_pixel_chain_both_limits_and_supply_return_counted_once(self):
        specs = [("pixel", "barrel", "B1", 0, row, 10.+row, 1) for row in range(32)]
        specs += [("pixel", "barrel", "B2", 0, row, 10.+row, 4) for row in range(9)]
        result = estimate_budget(layout_fixture(specs), self.inputs, [])
        pix = result["ends"]["positive"]["pixel"]
        self.assertEqual(pix["counts"]["power_chains"], 4)  # two single + two quad chains
        self.assertEqual(pix["counts"]["chips"], 68)
        ref = pix["scenarios"]["reference"]
        upper = pix["scenarios"]["conservative"]
        self.assertEqual(ref["cables_mm2"], 4*35+2*41)
        self.assertEqual(upper["cables_mm2"], 4*35+68+41)
        self.assertEqual(ref["feed_mm2"], ref["return_mm2"])
        self.assertAlmostEqual(ref["feed_mm2"]+ref["return_mm2"], 2*2*math.pi*4**2/4)

    def test_pixel_cooling_splits_power_and_local_groups(self):
        specs = [("pixel", "barrel", "B", 0, row, 10.+row, 4) for row in range(30)]
        specs.append(("pixel", "barrel", "B", 1, 0, 10., 1))
        result = estimate_budget(layout_fixture(specs), self.inputs, [])
        self.assertEqual(result["ends"]["positive"]["pixel"]["counts"]["cooling_leaf_loops"], 3)

    def test_central_body_routes_positive_without_forced_symmetry(self):
        layout = layout_fixture([("long_strip", "barrel", "B", 0, row, z, 0)
                                 for row, z in enumerate((-1., 0., 1.))])
        result = estimate_budget(layout, self.inputs, [])
        self.assertEqual(result["ends"]["positive"]["long_strip"]["counts"]["modules"], 2)
        self.assertEqual(result["ends"]["negative"]["long_strip"]["counts"]["modules"], 1)

    def test_axial_radial_capacity_uses_correct_orientation_and_skins(self):
        routes = [route_fixture(), route_fixture("radial", kind="radial")]
        result = estimate_budget(layout_fixture([]), self.inputs, routes)
        axial, radial = result["routes"]
        self.assertAlmostEqual(axial["usable_geometric_cross_section_mm2"], math.pi*(198**2-102**2))
        self.assertAlmostEqual(radial["usable_geometric_cross_section_mm2"], 2*math.pi*100*16)
        self.assertAlmostEqual(axial["scenarios"]["reference"]["capacity_mm2"],
                               math.pi*(198**2-102**2)*.75*.5)

    def test_shared_trunk_accumulates_owners_but_branch_throat_only_its_traffic(self):
        specs = [(sub, "endcap", sub+"P", 0, 0, 10., 1 if sub == "pixel" else 0)
                 for sub in ("pixel", "short_strip", "long_strip")]
        routes = [route_fixture("branch", z_max_mm=20.),
                  route_fixture("shared", "shared", z_min_mm=20., z_max_mm=40.)]
        result = estimate_budget(layout_fixture(specs), self.inputs, routes)
        demand = result["routes"][1]["scenarios"]["reference"]["demand_mm2"]
        expected = sum(result["ends"]["positive"][s]["scenarios"]["reference"]["reserved_demand_mm2"]
                       for s in ("pixel", "short_strip", "long_strip"))
        self.assertAlmostEqual(demand, expected)
        self.assertEqual(result["throats"][0]["owners"], ["pixel"])
        self.assertEqual(result["throats"][0]["modules_carried"], 1)
        self.assertAlmostEqual(result["throats"][0]["scenarios"]["reference"]["demand_mm2"],
                               result["routes"][0]["scenarios"]["reference"]["demand_mm2"])

    def test_layer_filter_and_owner_subset_recompute_local_manifolds(self):
        specs = [("short_strip", "endcap", layer, 0, 0, 10., 0) for layer in ("P1", "P2")]
        specs.append(("pixel", "endcap", "XP1", 0, 0, 10., 4))
        route = route_fixture("filtered", "shared", owners=["short_strip"], layer_ids=["P1"])
        result = estimate_budget(layout_fixture(specs), self.inputs, [route])
        self.assertEqual(result["routes"][0]["modules_carried"], 1)
        expected = math.pi/4*(13.4**2+3.6**2+8**2+12**2)
        self.assertAlmostEqual(result["routes"][0]["scenarios"]["reference"]["demand_mm2"], expected)

    def test_skin_closed_route_records_capacity_failure_without_infinity(self):
        layout = layout_fixture([("pixel", "endcap", "P", 0, 0, 10., 1)])
        route = route_fixture(r_max_mm=103.)
        result = estimate_budget(layout, self.inputs, [route])
        for scenario in result["routes"][0]["scenarios"].values():
            self.assertEqual(scenario["capacity_mm2"], 0)
            self.assertEqual(scenario["status"], "FAIL")
            self.assertIsNone(scenario["utilization"])

    def test_adverse_demand_includes_spares_and_strixel_stress_remains_visible(self):
        layout = layout_fixture([("short_strip", "endcap", "P", 0, 0, 10., 0)])
        result = estimate_budget(layout, self.inputs, [route_fixture(subsystem="short_strip")])
        scenarios = result["ends"]["positive"]["short_strip"]["scenarios"]
        self.assertEqual(scenarios["stress"]["harnesses"], 5)
        self.assertAlmostEqual(scenarios["conservative"]["reserved_demand_mm2"],
                               scenarios["reference"]["bare_demand_mm2"]*1.25)
        self.assertEqual(scenarios["stress"]["return_mm2"], scenarios["reference"]["return_mm2"])

    def test_declared_path_keeps_incidental_small_contact_informational(self):
        layout = layout_fixture([("pixel", "endcap", "P", 0, 0, 10., 1)])
        routes = [route_fixture("A", connects_to=["B"]),
                  route_fixture("B", r_max_mm=300., z_min_mm=30., z_max_mm=60., connects_to=["C"]),
                  route_fixture("C", r_min_mm=199., r_max_mm=300., z_min_mm=29., z_max_mm=60., connects_to=[])]
        result = estimate_budget(layout, self.inputs, routes)
        self.assertEqual(result["routing_graph"]["mode"], "declared")
        self.assertEqual(len(result["potential_contacts"]), 3)
        self.assertEqual(len(result["throats"]), 2)
        incidental = next(c for c in result["potential_contacts"] if c["routes"] == ["A", "C"])
        self.assertFalse(incidental["required"])
        self.assertEqual(incidental["scenarios"]["reference"]["status"], "FAIL")
        self.assertTrue(result["all_routes_and_throats_pass"]["reference"])

    def test_declaring_same_small_contact_preserves_capacity_failure(self):
        layout = layout_fixture([("pixel", "endcap", "P", 0, 0, 10., 1)])
        routes = [route_fixture("A", connects_to=["B", "C"]),
                  route_fixture("B", r_max_mm=300., z_min_mm=30., z_max_mm=60., connects_to=["C"]),
                  route_fixture("C", r_min_mm=199., r_max_mm=300., z_min_mm=29., z_max_mm=60., connects_to=[])]
        result = estimate_budget(layout, self.inputs, routes)
        self.assertEqual(len(result["throats"]), 3)
        self.assertFalse(result["all_routes_and_throats_pass"]["reference"])
        bottleneck = next(c for c in result["throats"] if c["routes"] == ["A", "C"])
        self.assertEqual(bottleneck["usable_geometric_cross_section_mm2"], 0.)
        self.assertEqual(bottleneck["scenarios"]["reference"]["status"], "FAIL")

    def test_declared_downstream_scope_cannot_drop_upstream_sources(self):
        layout = layout_fixture([("pixel", "endcap", layer, 0, 0, 10., 1)
                                 for layer in ("P1", "P2")])
        routes = [route_fixture("upstream", connects_to=["downstream"]),
                  route_fixture("downstream", z_min_mm=30., z_max_mm=60.,
                                layer_ids=["P1"], connects_to=[])]
        with self.assertRaisesRegex(ValueError, "declared flow loses 1 source modules"):
            estimate_budget(layout, self.inputs, routes)
        routes[0]["layer_ids"] = ["P1"]
        routes[1]["layer_ids"] = ["P1", "P2"]
        result = estimate_budget(layout, self.inputs, routes)
        self.assertEqual(result["throats"][0]["modules_carried"], 1)
        self.assertEqual(result["routes"][1]["modules_carried"], 2)
        self.assertTrue(result["stress_cooling"]["reference_counts_and_pipe_sizes_retained"])
        self.assertFalse(result["stress_cooling"]["thermal_load_rescaled"])

    def test_declared_graph_rejects_unknown_missing_contact_and_disconnection(self):
        empty = layout_fixture([])
        bad_cases = [
            ([route_fixture("A", connects_to=["unknown"])], "unknown route"),
            ([route_fixture("A", connects_to=["B"]), route_fixture("B")], "every route"),
            ([route_fixture("A", connects_to=[]), route_fixture("B", connects_to=[])], "disconnected"),
            ([route_fixture("A", connects_to=["B"]),
              route_fixture("B", z_min_mm=100., z_max_mm=120., connects_to=[])], "no finite geometric contact"),
            ([route_fixture("A", connects_to=["A"])], "itself"),
        ]
        for routes, message in bad_cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                estimate_budget(empty, self.inputs, routes)

    def test_invalid_values_and_duplicate_ids_rejected(self):
        for group, key, value in (("strip", "max_modules_per_harness", -1),
                                  ("pixel", "cooling_power_per_circuit_W", 0),
                                  ("capacity", "boundary_allowance_mm", float("nan"))):
            inputs = copy.deepcopy(self.inputs)
            inputs[group][key] = value
            with self.assertRaises(ValueError):
                estimate_budget(layout_fixture([]), inputs, [])
        with self.assertRaises(ValueError):
            estimate_budget(layout_fixture([]), self.inputs, [route_fixture(z_min_mm=-1.)])
        layout = layout_fixture([("pixel", "endcap", "P", 0, 0, 10., 1)])
        with self.assertRaises(ValueError):
            estimate_budget(layout, self.inputs, [route_fixture(layer_ids=["typo"])])
        layout["bodies"].append(copy.deepcopy(layout["bodies"][0]))
        with self.assertRaises(ValueError):
            estimate_budget(layout, self.inputs, [])


if __name__ == "__main__":
    unittest.main()
