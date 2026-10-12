"""DES-010 driver regression controls: repeatability, routing and fixed positions."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.module_layout import services
from tools.module_layout.services_geometry import support_envelopes
from tools.module_layout.test_services_geometry import disc_fixture


class ServiceDriverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = services.read(services.HERE/"services_config.json")
        cls.envelopes = services.ROOT/"docs/design/DES-003-envelopes.json"
        cls.baseline, cls.modified, cls.routes = services.build(
            cls.config, services.HERE/"review_models.json",
            services.ROOT/"docs/design/DES-006-named-layouts.json")

    def test_chosen_config_carves_without_position_or_identifier_changes(self):
        before, after = self.baseline, self.modified
        self.assertEqual(before["layers"], after["layers"])
        retained = {b["module_id"] for b in after["bodies"]}
        self.assertLess(len(retained), len(before["bodies"]))
        self.assertEqual(after["bodies"], [b for b in before["bodies"] if b["module_id"] in retained])
        self.assertEqual(after["modules"], [p for p in before["modules"] if p["module_id"] in retained])
        removed = {b["module_id"] for b in before["bodies"]}-retained
        self.assertEqual(removed, set(after["metadata"]["services"]["removed_module_ids"]))
        for record in after["metadata"]["services"]["removed_rows"]:
            expected = {b["module_id"] for b in before["bodies"]
                        if b["layer_id"] == record["layer_id"] and b["row"] == record["row"]}
            self.assertEqual(expected, set(record["module_ids"]))
            self.assertTrue(expected <= removed)
        # No eligible layer disappears; future coverage uses original denominators.
        self.assertEqual({b["layer_id"] for b in before["bodies"]},
                         {b["layer_id"] for b in after["bodies"]})

    def test_chosen_config_clears_bodies_supports_and_global_envelopes(self):
        diagnostics = self.modified["metadata"]["services"]["diagnostics"]
        for key in ("route_body_conflicts", "route_support_conflicts", "support_body_conflicts",
                    "support_pair_conflicts", "support_host_violations"):
            self.assertEqual(diagnostics[key], [], key)
        self.assertEqual(self.modified["metadata"]["host_diagnostics"]["host_overflow_modules"], 0)
        interface = services.interface_checks(self.routes, self.envelopes, self.config["clearance_mm"])
        self.assertEqual(interface["allocated_volume_conflicts"], [])
        self.assertEqual(interface["disconnected_from_handoff"], [])
        self.assertTrue(interface["proposed_beyond_tracker_host"],
                        "downstream proposed space must not be mislabeled existing allocation")

    def test_vessel_overshoot_is_detected(self):
        routes = copy.deepcopy(self.routes)
        trunk = next(r for r in routes if r["id"] == "common-bore-P")
        trunk["r_max_mm"] = 1245.  # Test-only 5 mm intrusion into DES-003 vessel.
        result = services.interface_checks(routes, self.envelopes, self.config["clearance_mm"])
        self.assertTrue(any(c["route"] == trunk["id"] and c["region"] == "magnet"
                            for c in result["allocated_volume_conflicts"]))

    def test_disconnected_tail_and_absent_handoff_are_detected(self):
        routes = [copy.deepcopy(r) for r in self.routes if r["id"] != "common-bore-P"]
        result = services.interface_checks(routes, self.envelopes, self.config["clearance_mm"])
        self.assertIn("pixel-trunk-P", result["disconnected_from_handoff"])
        for route in routes:
            route.pop("exit", None)
        result = services.interface_checks(routes, self.envelopes, self.config["clearance_mm"])
        self.assertEqual(set(result["disconnected_from_handoff"]), {r["id"] for r in routes})

    def test_incidental_contact_cannot_bypass_declared_routing_tree(self):
        def segment(name, r0, r1, targets, exit=False):
            return dict(id=name, subsystem="pixel", kind="axial", exit=exit,
                        r_min_mm=r0, r_max_mm=r1, z_min_mm=100., z_max_mm=200.,
                        connects_to=targets)
        # A touches the exit geometrically but declares a broken path through B.
        routes = [segment("test-a", 100., 120., ["test-b"]),
                  segment("test-b", 140., 160., ["test-exit"]),
                  segment("test-exit", 110., 130., [], exit=True)]
        result = services.interface_checks(routes, self.envelopes)
        self.assertEqual(result["disconnected_from_handoff"], ["test-a", "test-b"])
        routes[0]["connects_to"] = ["test-exit"]
        result = services.interface_checks(routes, self.envelopes)
        self.assertEqual(result["disconnected_from_handoff"], ["test-b"])

    def test_rear_collection_boundaries_follow_config(self):
        config = copy.deepcopy(self.config)
        config["trunks_mm"]["pixel"][0] = 180.
        config["trunks_mm"]["short_strip"][0] = 650.
        config["trunks_mm"]["long_strip"][:2] = [1150., 1230.]
        fixture = dict(layers=[], metadata=dict(services=dict(supports=[]),
                                               host=dict(abs_z_max_m=3.15)))
        routes = services.complete_routes(fixture, config, [])
        positive = {r["id"]: r for r in routes if r["side"] == "positive"}
        for name, bounds in (("rear-pixel-P", (180., 650.)),
                             ("rear-pixel-short-P", (650., 1150.)),
                             ("rear-all-P", (1150., 1230.))):
            self.assertEqual((positive[name]["r_min_mm"], positive[name]["r_max_mm"]), bounds)

    def test_collector_crossing_host_is_marked_conditional(self):
        fixture = disc_fixture()
        fixture["metadata"]["host"]["abs_z_max_m"] = .107  # Test-only host end.
        fixture["metadata"]["services"] = dict(supports=support_envelopes(fixture, {"pixel": 3.}))
        routes = services.complete_routes(fixture, self.config, [])
        collector = next(r for r in routes if r["id"] == "test-disc-1-collector-P")
        self.assertLess(collector["z_min_mm"], 107.)
        self.assertGreater(collector["z_max_mm"], 107.)
        self.assertTrue(collector["conditional_interface"])

    def test_interface_uses_supplied_host_and_clearance(self):
        envelopes = services.read(self.envelopes)
        next(e for e in envelopes["regions"] if e["id"] == "tracker")["z_max_m"] = 3.
        route = dict(id="test-only", subsystem="pixel", kind="axial", exit=True,
                     r_min_mm=1200., r_max_mm=1239., z_min_mm=3001., z_max_mm=3100.)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"envelopes.json"
            services.write(path, envelopes)
            zero = services.interface_checks([route], path)
            two = services.interface_checks([route], path, 2.)
        self.assertEqual(zero["proposed_beyond_tracker_host"], ["test-only"])
        self.assertEqual(zero["allocated_volume_conflicts"], [])
        self.assertTrue(any(c["region"] == "magnet" for c in two["allocated_volume_conflicts"]))

    def test_snapshots_preserve_source_bytes_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root/"original.json"
            content = b'{  "test_only" : 1,\r\n  "value" : [ 2 ] }\r\n'
            original.write_bytes(content)
            output = root/"run"; output.mkdir()
            hashes = services.snapshot_inputs({"config.json": original}, output)
            self.assertEqual((output/"config.json").read_bytes(), content)
            self.assertEqual(hashes["config.json"], hashlib.sha256(content).hexdigest())
            self.assertEqual(services.digest(output/"config.json"), hashes["config.json"])

    def test_geometry_gate_rejects_clashes_and_host_overflow(self):
        results = dict(services=dict(diagnostics={key: [] for key in (
            "route_body_conflicts", "route_support_conflicts", "support_body_conflicts",
            "support_pair_conflicts", "support_host_violations")}),
            body_diagnostics=dict(overlapping_body_pairs=0),
            host_diagnostics=dict(host_overflow_modules=0),
            interface=dict(allocated_volume_conflicts=[], disconnected_from_handoff=[]))
        self.assertEqual(services.geometry_failures(results), [])
        results["body_diagnostics"]["overlapping_body_pairs"] = 1
        results["host_diagnostics"]["host_overflow_modules"] = 1
        self.assertEqual(set(services.geometry_failures(results)),
                         {"overlapping_body_pairs", "host_overflow_modules"})


if __name__ == "__main__":
    unittest.main()
