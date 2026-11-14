"""Adverse controls for exact serial/MT equivalence and policy identity."""
from copy import deepcopy
import unittest
import controls


def events():
    return {i: {"primary": (11, 20., 1., 2., 3., 0., 0., 0.),
                "cells": {"LArBarrelHits": [(100, .1, 1., 2., 3.)],
                          "LArEndcapHits": []}} for i in range(24)}


class Controls(unittest.TestCase):
    def test_all_events_and_empty_collections_retained(self):
        self.assertEqual(controls.compare_events(events(), events()),
                         {"LArBarrelHits": 24, "LArEndcapHits": 0})

    def test_missing_event_rejected(self):
        parallel = events(); del parallel[23]
        with self.assertRaises(ValueError):
            controls.compare_events(events(), parallel)

    def test_extra_event_rejected(self):
        parallel = events(); parallel[24] = deepcopy(parallel[0])
        with self.assertRaises(ValueError):
            controls.compare_events(events(), parallel)

    def test_changed_cell_energy_position_or_primary_rejected(self):
        for row in ((101, .1, 1., 2., 3.), (100, .2, 1., 2., 3.),
                    (100, .1, 1., 2., 3.000000000001)):
            with self.subTest(row=row):
                parallel = events(); parallel[1]["cells"]["LArBarrelHits"] = [row]
                with self.assertRaises(ValueError):
                    controls.compare_events(events(), parallel)
        parallel = events(); parallel[0]["primary"] = (11, 21., 1., 2., 3., 0., 0., 0.)
        with self.assertRaises(ValueError):
            controls.compare_events(events(), parallel)

    def test_wrong_policy_or_failure_rejected(self):
        receipt = dict(events=24, skip=0, threads=12, seed=133812341,
                       max_step_mm=5., exit_code=0, disk_abort=False)
        controls.check_policy(receipt, 12)
        for key, value in dict(events=23, skip=1, threads=1, seed=7,
                               max_step_mm=0., exit_code=1, disk_abort=True).items():
            with self.subTest(key=key), self.assertRaises(ValueError):
                controls.check_policy(dict(receipt, **{key: value}), 12)


if __name__ == "__main__":
    unittest.main()
