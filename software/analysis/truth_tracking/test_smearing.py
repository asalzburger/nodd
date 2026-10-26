import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from smearing import COORDINATES, build_config, load_campaign, schedule_digitization


class SmearingControls(unittest.TestCase):
    def setUp(self):
        self.settings = {"model": "gaussian_smearing", "merge": False,
                         "measured_coordinates_by_system": copy.deepcopy(COORDINATES)}
        self.sensors = [{"geometry_id": (i << 56) | (i << 8), "ids": {"system": i}} for i in range(1, 8)]
        self.table = {"schema_version": 1, "status": "PROTOTYPE", "width_convention": "test centered SD",
            "groups": [{"volume": i, "index": j, "entries": 100, "mean_mm": .001,
                "sigma_mm": .01 * (j + 1), "uncentered_rms_mm": .021,
                "sensor_family": "pixel" if i < 4 else "short_strip" if i < 6 else "long_strip"}
                for i in range(1, 8) for j in COORDINATES[str(i)]]}

    def test_zero_mean_native_gaussian_and_single_coordinate_strips(self):
        config, counts = build_config(self.sensors, self.settings, self.table)
        self.assertEqual(counts, {str(i): 1 for i in range(1, 8)})
        for entry in config["entries"]:
            self.assertEqual(set(entry["value"]), {"smearing"})
            smearers = entry["value"]["smearing"]
            self.assertEqual([x["index"] for x in smearers], COORDINATES[str(entry["volume"])])
            for item in smearers:
                self.assertEqual(item["type"], "Gauss")
                self.assertEqual(item["mean"], 0.)
                self.assertFalse(item["forcePositiveValues"])
                self.assertEqual(item["stddev"], .01 * (item["index"] + 1))

    def test_reject_duplicate_sensor_missing_system_and_nonsensitive(self):
        for sensors in (self.sensors + [self.sensors[0]], self.sensors[:-1],
                        [{**self.sensors[0], "geometry_id": 1 << 56}] + self.sensors[1:]):
            with self.assertRaises(ValueError):
                build_config(sensors, self.settings, self.table)

    def test_reject_missing_extra_duplicate_and_wrong_family_widths(self):
        tables = [copy.deepcopy(self.table) for _ in range(4)]
        tables[0]["groups"].pop()
        tables[1]["groups"].append({**tables[1]["groups"][0], "volume": 99})
        tables[2]["groups"].append(copy.deepcopy(tables[2]["groups"][0]))
        tables[3]["groups"][0]["sensor_family"] = "long_strip"
        for table in tables:
            with self.assertRaises(ValueError):
                build_config(self.sensors, self.settings, table)

    def test_reject_invalid_sigma_and_second_long_strip_coordinate(self):
        for sigma in (0., -.1, float("inf"), float("nan")):
            table = copy.deepcopy(self.table); table["groups"][0]["sigma_mm"] = sigma
            with self.assertRaises(ValueError):
                build_config(self.sensors, self.settings, table)
        settings = copy.deepcopy(self.settings); settings["measured_coordinates_by_system"]["6"] = [0, 1]
        with self.assertRaises(ValueError):
            build_config(self.sensors, settings, self.table)

    def test_campaign_rejects_merging_or_non_gaussian_response(self):
        path = Path(__file__).with_name("smearing_campaign.json")
        config = load_campaign(path)
        for key, value in (("merge", True), ("model", "geometric")):
            broken = copy.deepcopy(config); broken["digitization"][key] = value
            with tempfile.TemporaryDirectory() as directory:
                p = Path(directory)/"campaign.json"; p.write_text(json.dumps(broken))
                with self.assertRaises(ValueError):
                    load_campaign(p)

    def test_schedule_disables_merging_and_has_no_covariance_adapter(self):
        class Algorithm:
            Config = staticmethod(lambda **kwargs: kwargs)
            def __init__(self, config, level):
                self.config = config
        algorithms = []
        acts_json = SimpleNamespace(readDigiConfigFromJson=lambda path: path)
        examples = SimpleNamespace(DigitizationAlgorithm=Algorithm, json=acts_json)
        acts = SimpleNamespace(examples=examples)
        observer = SimpleNamespace(UniqueAssociations=lambda: "unique", ClusterErrors=lambda: self.fail("Must not replace covariance"))
        with patch.dict("sys.modules", {"acts.examples": examples}):
            schedule_digitization(SimpleNamespace(addAlgorithm=algorithms.append), acts,
                SimpleNamespace(geoIdSurfaceMap=lambda: {}), "rng", "config.json", observer, 0)
        self.assertEqual(len(algorithms), 2)
        self.assertEqual(algorithms[1], "unique")
        self.assertFalse(algorithms[0].config["doMerge"])
        self.assertEqual(algorithms[0].config["outputMeasurements"], "measurements")


if __name__ == "__main__":
    unittest.main()
