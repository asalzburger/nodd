import copy
import unittest
from check_gen3 import compare


class ConversionControls(unittest.TestCase):
    def fixture(self):
        sensors = [
            dict(
                ids={"system": i, "layer": 0},
                center_mm=[i, 0, 0],
                normal=[0, 0, 1],
                u=[1, 0, 0],
                v=[0, 1, 0],
                size_mm=[10, 10, 0.3],
                role="sensitive",
                geometry_id=i,
            )
            for i in range(1, 8)
        ]
        expected = dict(
            entities=copy.deepcopy(sensors),
            beam=dict(
                config=dict(inner_radius_mm=27, wall_mm=0.8, half_length_mm=4000)
            ),
        )
        report = dict(
            generation=3,
            sensors=sensors,
            volumes=[dict(portals=2)],
            beampipe_portals=[
                dict(
                    radius_mm=27.4,
                    half_length_mm=4000,
                    thickness_mm=0.8,
                    elemental_Z=4,
                    radiation_length_mm=350,
                )
            ],
        )
        return report, expected

    def test_reflected_axis_and_duplicate_ids_fail(self):
        report, expected = self.fixture()
        self.assertEqual(compare(report, expected)["status"], "PASS")
        report["sensors"][0]["u"] = [-1, 0, 0]
        report["sensors"][0]["geometry_id"] = 2
        result = compare(report, expected)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("u axis mismatch" in e for e in result["errors"]))
        self.assertTrue(any("identifiers" in e for e in result["errors"]))

    def test_wrong_pipe_wall_fails(self):
        report, expected = self.fixture()
        report["beampipe_portals"][0]["thickness_mm"] = 0.7
        self.assertIn(
            "BeamPipe thickness_mm mismatch", compare(report, expected)["errors"]
        )


if __name__ == "__main__":
    unittest.main()
