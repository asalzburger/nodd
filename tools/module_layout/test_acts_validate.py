"""Native integration controls; explicitly skipped without the ACTS runtime."""

import importlib.util
import math
import tempfile
import unittest

import numpy as np

from acts_validate import validate


def fixture():
    """Named synthetic mm dimensions, unrelated to a detector design."""
    modules = []
    for i, (center, u, v) in enumerate([
        ([50., 0., 0.], [0., 1., 0.], [0., 0., 1.]),
        ([100., 0., 0.], [-math.sin(.2), math.cos(.2), 0.], [0., 0., 1.]),
        ([-50., 0., 0.], [0., -1., 0.], [0., 0., 1.]),
        ([-100., 0., 0.], [math.sin(.2), -math.cos(.2), 0.], [0., 0., 1.]),
        ([0., 0., 180.], [1., 0., 0.], [0., 1., 0.]),
        ([0., 0., -180.], [1., 0., 0.], [0., -1., 0.]),
    ]):
        disc = i >= 4
        modules.append(dict(id=i + 1, sensor_id=i + 1, module_id=i + 1,
                            center_mm=center, u=u, v=v, n=np.cross(u, v).tolist(),
                            half_u_mm=160. if disc else 22., half_v_mm=160. if disc else 75.))
    return dict(modules=modules, status="SYNTHETIC TEST FIXTURE")


@unittest.skipUnless(importlib.util.find_spec("acts"), "Native ACTS Python runtime unavailable")
class NativeAuditTests(unittest.TestCase):
    def test_exhaustive_straight_both_charges_tilts_and_phi_wrap(self):
        tracks = [dict(origin_mm=[1., .5, z], eta=eta, phi=phi, charge=q,
                       pt_GeV=1., field_T=b)
                  for eta, z, phi in [(0., 0., .05), (0., 0., 3.25),
                                      (1.2, -150., .2), (-1.2, 150., 6.1)]
                  for b, q in [(0., 1.), (3., 1.), (3., -1.)]]
        with tempfile.TemporaryDirectory() as work:
            exhaustive = validate(fixture(), tracks, work, host_radius_mm=200.,
                                  host_half_z_mm=300., exhaustive=True)
            indexed = validate(fixture(), tracks, work, host_radius_mm=200., host_half_z_mm=300.)
        self.assertTrue(exhaustive["passed"], exhaustive["mismatches"])
        self.assertTrue(indexed["passed"], indexed["mismatches"])
        self.assertEqual(exhaustive["tested_candidate_targets"], len(tracks) * 6)
        self.assertGreater(exhaustive["reached_native_targets"], 0)
        self.assertLess(exhaustive["reached_native_targets"], exhaustive["tested_candidate_targets"])
        self.assertEqual([t["observed_patch_hits"] for t in exhaustive["per_track"]],
                         [t["observed_patch_hits"] for t in indexed["per_track"]])

    def test_deliberately_wrong_expected_ids_are_rejected(self):
        tracks = [dict(origin_mm=[0., 0., 0.], eta=0., phi=0., charge=1., pt_GeV=1., field_T=3.)]
        with tempfile.TemporaryDirectory() as work:
            result = validate(fixture(), tracks, work, expected_patch_hits=[[999]],
                              host_radius_mm=200., host_half_z_mm=300., exhaustive=True)
        self.assertFalse(result["passed"])
        self.assertEqual(result["mismatches"][0]["missing"], [999])
        self.assertTrue(result["mismatches"][0]["extra"])


if __name__ == "__main__":
    unittest.main()
