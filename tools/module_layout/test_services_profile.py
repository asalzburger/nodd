"""Cumulative-load contracts on explicit test-only branches and pickup pockets."""
import copy
import math
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.module_layout import services_budget as budget
from tools.module_layout.services_profile import axial_profiles, export, POLICY, HERE


def fixture(sides=(1,), *, positive_extra=False):
    inputs = budget.load_inputs()
    layout = dict(bodies=[], modules=[])
    routes = []
    for sign in sides:
        end = "P" if sign > 0 else "N"
        sub = "short_strip"
        def route(name, kind, z0, z1, targets, **extra):
            zz = sorted((sign*z0, sign*z1))
            return dict(id=name+end, subsystem=sub, kind=kind,
                        r_min_mm=100., r_max_mm=200., z_min_mm=zz[0], z_max_mm=zz[1],
                        side="positive" if sign > 0 else "negative",
                        connects_to=[x+end for x in targets], **extra)
        routes += [route("trunk", "axial", 5., 100., ["out"]),
                   route("barrel", "radial", 10., 20., ["trunk"], layer_ids=["B"+end]),
                   route("disc1", "radial", 30., 40., ["trunk"], layer_ids=["D1"+end]),
                   route("disc2", "radial", 70., 80., ["trunk"], layer_ids=["D2"+end]),
                   route("out", "radial", 90., 110., [], exit=True)]
        # Two partly filled same-layer half-staves must retain two independent
        # harnesses but share one manifold trunk. Each disc is a separate layer.
        specifications = [("B"+end, "barrel", col, 0, sign*10.) for col in (0, 1) for _ in range(5)]
        specifications += [("D1"+end, "endcap", 0, 0, sign*30.),
                           ("D2"+end, "endcap", 0, 0, sign*70.)]
        if positive_extra and sign > 0:
            specifications.append(("B"+end, "barrel", 0, 0, 0.))
        for layer, region, col, row, z in specifications:
            mid = len(layout["bodies"])+1
            layout["bodies"].append(dict(module_id=mid, subsystem=sub, region=region,
                                         layer_id=layer, family=sub, col=col, row=row,
                                         center_mm=[100., 0., z], half_u_mm=2., half_v_mm=3.))
    retained = budget.estimate_budget(layout, inputs, routes)
    return dict(budget=retained, services=dict(routes=routes)), inputs


class AxialProfileTests(unittest.TestCase):
    def test_load_increases_only_at_near_edges_and_reaches_retained_maximum(self):
        summary, inputs = fixture()
        original = copy.deepcopy(summary)
        result = axial_profiles(summary, inputs, pickup_policy=POLICY)
        profile = result["profiles"][0]
        self.assertEqual(summary, original)
        self.assertEqual(profile["reserved_width_mm"], 100.)
        self.assertEqual([e["pickup_abs_z_interval_mm"] for e in profile["pickup_events"]],
                         [[10., 20.], [30., 40.], [70., 80.]])
        self.assertEqual([(s["abs_z_min_mm"], s["abs_z_max_mm"], s["module_count"])
                          for s in profile["segments"]],
                         [(5., 10., 0), (10., 30., 10), (30., 70., 11), (70., 100., 12)])
        self.assertEqual(profile["full_load_from_abs_z_mm"], 70.)
        self.assertEqual(profile["downstream_handoff_abs_z_interval_mm"], [90., 100.])
        self.assertTrue(profile["matches_retained_maximum"])
        for name, scenario in profile["terminal"]["scenarios"].items():
            retained = summary["budget"]["routes"][0]["scenarios"][name]
            self.assertEqual(scenario["demand_mm2"], retained["demand_mm2"])
            self.assertEqual(scenario["capacity_mm2"], retained["capacity_mm2"])

    def test_partial_groups_round_locally_and_manifolds_do_not_double_count(self):
        summary, inputs = fixture()
        segments = axial_profiles(summary, inputs)["profiles"][0]["segments"]
        initial = segments[1]
        self.assertEqual(initial["counts"]["harnesses"], 2)  # not ceil(10/12)=1
        self.assertEqual(initial["counts"]["cooling_leaf_loops"], 2)
        self.assertEqual(initial["counts"]["cooling_trunk_pairs"], 1)  # not one per group
        self.assertEqual([s["counts"]["cooling_trunk_pairs"] for s in segments], [0, 1, 2, 3])
        expected = 2*math.pi/4*(13.4**2+3.6**2)+math.pi/4*(8**2+12**2)
        self.assertAlmostEqual(initial["scenarios"]["reference"]["demand_mm2"], expected)
        # Stress rounds each half-stave's expanded harness separately.
        expected_stress = (10*math.pi/4*(13.4**2+3.6**2)+math.pi/4*(8**2+12**2))*1.25
        self.assertAlmostEqual(initial["scenarios"]["stress"]["demand_mm2"], expected_stress)

    def test_negative_end_uses_increasing_absolute_z_and_keeps_actual_counts(self):
        summary, inputs = fixture((1, -1), positive_extra=True)
        profiles = {p["side"]: p for p in axial_profiles(summary, inputs)["profiles"]}
        self.assertEqual([e["pickup_abs_z_interval_mm"] for e in profiles["positive"]["pickup_events"]],
                         [e["pickup_abs_z_interval_mm"] for e in profiles["negative"]["pickup_events"]])
        self.assertEqual(profiles["positive"]["terminal"]["module_count"], 13)
        self.assertEqual(profiles["negative"]["terminal"]["module_count"], 12)
        self.assertEqual(profiles["negative"]["segments"][1]["module_count"], 10)

    def test_equivalent_width_inverts_reserved_cross_section_with_both_boundaries(self):
        summary, inputs = fixture()
        profile = axial_profiles(summary, inputs)["profiles"][0]
        for segment in profile["segments"]:
            for name, record in segment["scenarios"].items():
                b = inputs["capacity"]["boundary_allowance_mm"]
                width = record["required_annular_width_mm"]
                inner = profile["r_min_mm"]
                area = math.pi*((inner+width-b)**2-(inner+b)**2)
                scenario = inputs["scenarios"][name]
                self.assertAlmostEqual(area*scenario["available_phi_fraction"]*scenario["packing_fraction"],
                                       record["demand_mm2"], places=8)
        self.assertEqual(profile["segments"][0]["scenarios"]["reference"]["required_annular_width_mm"], 4.)

    def test_missing_and_duplicate_incoming_groups_fail(self):
        summary, inputs = fixture()
        missing = copy.deepcopy(summary)
        missing["services"]["routes"] = [r for r in missing["services"]["routes"] if r["id"] != "disc2P"]
        with self.assertRaisesRegex(ValueError, "missing incoming"):
            axial_profiles(missing, inputs)
        duplicate = copy.deepcopy(summary)
        branch = copy.deepcopy(next(r for r in duplicate["services"]["routes"] if r["id"] == "disc1P"))
        branch["id"] = "duplicateP"
        duplicate["services"]["routes"].append(branch)
        with self.assertRaisesRegex(ValueError, "duplicate incoming"):
            axial_profiles(duplicate, inputs)

    def test_partial_groups_and_partial_module_selectors_fail(self):
        summary, inputs = fixture()
        corrupt = copy.deepcopy(summary)
        corrupt["budget"]["local_groups"][0]["module_ids"].pop()
        with self.assertRaisesRegex(ValueError, "every unique module"):
            axial_profiles(corrupt, inputs)
        branch = next(r for r in summary["services"]["routes"] if r["id"] == "barrelP")
        branch["module_ids"] = [1]
        with self.assertRaisesRegex(ValueError, "partial per-module"):
            axial_profiles(summary, inputs)

    def test_stale_final_budget_and_inputs_fail(self):
        summary, inputs = fixture()
        stale = copy.deepcopy(summary)
        stale["budget"]["routes"][0]["scenarios"]["reference"]["demand_mm2"] += 1.
        with self.assertRaisesRegex(ValueError, "final load/capacity"):
            axial_profiles(stale, inputs)
        changed = copy.deepcopy(inputs)
        changed["capacity"]["boundary_allowance_mm"] += 1.
        with self.assertRaisesRegex(ValueError, "budget inputs"):
            axial_profiles(summary, changed)

    def test_wrong_end_disconnected_pickup_and_cycle_fail(self):
        summary, inputs = fixture()
        wrong = copy.deepcopy(summary)
        branch = next(r for r in wrong["services"]["routes"] if r["id"] == "disc1P")
        branch.update(z_min_mm=-40., z_max_mm=-30.)
        with self.assertRaisesRegex(ValueError, "side contradicts"):
            axial_profiles(wrong, inputs)
        separated = copy.deepcopy(summary)
        branch = next(r for r in separated["services"]["routes"] if r["id"] == "disc1P")
        branch.update(r_min_mm=10., r_max_mm=20.)
        with self.assertRaisesRegex(ValueError, "pickup interval"):
            axial_profiles(separated, inputs)
        cycle = copy.deepcopy(summary)
        next(r for r in cycle["services"]["routes"] if r["id"] == "outP")["connects_to"] = ["trunkP"]
        with self.assertRaisesRegex(ValueError, "acyclic"):
            axial_profiles(cycle, inputs)

    def test_export_preserves_snapshot_bytes_and_rejects_reuse_or_tampering(self):
        summary, inputs = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); run = root/"run"; run.mkdir()
            raw = (json.dumps(inputs, indent=3)+"\r\n").encode()
            (run/"budget_inputs.json").write_bytes(raw)
            summary.update(source_commit="test-only-retained-source",
                           inputs_sha256={"budget_inputs.json": hashlib.sha256(raw).hexdigest()},
                           code_sha256={name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                                        for name in ("geometry.py", "services_geometry.py", "services.py", "services_budget.py")})
            (run/"summary.json").write_text(json.dumps(summary))
            output = root/"out"
            result = export(run, output, pickup_policy=POLICY)
            self.assertEqual((output/"budget_inputs.json").read_bytes(), raw)
            self.assertEqual(result["provenance"]["source_summary_sha256"],
                             hashlib.sha256((run/"summary.json").read_bytes()).hexdigest())
            retained = (output/"profile.json").read_bytes()
            with self.assertRaises(FileExistsError):
                export(run, output, pickup_policy=POLICY)
            self.assertEqual((output/"profile.json").read_bytes(), retained)
            (run/"budget_inputs.json").write_bytes(raw+b" ")
            with self.assertRaisesRegex(RuntimeError, "input hash mismatch"):
                export(run, root/"tampered", pickup_policy=POLICY)
            self.assertFalse((root/"tampered").exists())

    def test_policy_and_explicit_graph_are_required(self):
        summary, inputs = fixture()
        with self.assertRaisesRegex(ValueError, "explicit near-edge"):
            axial_profiles(summary, inputs, pickup_policy="somewhere-in-the-pocket")
        for route in summary["services"]["routes"]:
            route.pop("connects_to")
        with self.assertRaisesRegex(ValueError, "explicit connects_to"):
            axial_profiles(summary, inputs)


if __name__ == "__main__":
    unittest.main()
