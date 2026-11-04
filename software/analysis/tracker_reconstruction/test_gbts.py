"""Native-independent GBTS geometry/configuration boundary controls."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location("nodd_gbts_configuration",Path(__file__).with_name("gbts.py"))
gbts=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(gbts)


def fixture():
    # Synthetic placements are test values; cardinalities deliberately enforce
    # the actual balanced geometry contract, without using local build outputs.
    sensors=[]
    for system in (1,2,3):
        for layer in range(1,5 if system==1 else 11):
            count=500 if system==1 else (521 if layer==10 else 520)
            for _ in range(count):
                sensors.append({"geometry_id":len(sensors)+1,"ids":{"system":system,"layer":layer},
                    "center_mm":[30.*layer if system==1 else 80.,0.,0. if system==1 else (-1 if system==2 else 1)*(1000.+(2.5 if layer==10 else layer)*100.)],
                    "u":[0.,1.,0.],"v":[0.,0.,1.] if system==1 else [1.,0.,0.],"size_mm":[20.,20.,0.15]})
    # 4*500+2*(9*520+521)=12402; add eight barrel patches.
    for _ in range(8):
        entry=copy.deepcopy(sensors[0]);entry["geometry_id"]=len(sensors)+1;sensors.append(entry)
    while len(sensors)<46250:
        sensors.append({"geometry_id":len(sensors)+1,"ids":{"system":4,"layer":1}})
    return {"sensors":sensors}


class GbtsControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=fixture()

    def test_exact_pixel_coverage_physical_station_order_and_direction(self):
        with tempfile.TemporaryDirectory() as directory:
            audit=gbts.prepare(self.report,directory)
            self.assertEqual((audit["pixel_sensors"],audit["pixel_layers"],audit["connections"]),(12410,24,176))
            self.assertEqual(audit["physical_disk_order"]["2"],[1,2,10,3,4,5,6,7,8,9])
            mapping=[list(map(int,line.split(','))) for line in (Path(directory)/"mapping.csv").read_text().splitlines()]
            self.assertEqual(len({row[0] for row in mapping}),12410)
            self.assertEqual(len({row[1] for row in mapping}),24)
            links=[tuple(map(int,line.split(','))) for line in (Path(directory)/"connections.csv").read_text().splitlines()]
            self.assertIn((210,202),links)
            self.assertIn((203,210),links)
            self.assertIn((310,104),links)
            self.assertNotIn((201,301),links)

    def test_deterministic_order_and_exact_input_fingerprint(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            first=gbts.prepare(self.report,a)
            second=gbts.prepare({"sensors":list(reversed(self.report["sensors"]))},b)
            # The mean reference accumulation uses sensor-ID order for exact
            # reproducibility even when the producer container order changes.
            self.assertEqual(first["files"],second["files"])
            self.assertEqual(first["geometry_sensor_fingerprint"],second["geometry_sensor_fingerprint"])

    def test_rectangle_radial_bound_checks_edge_interior(self):
        sensor={"center_mm":[10.,0.,0.],"u":[0.,1.,0.],"v":[0.,0.,1.],"size_mm":[4.,6.,0.1]}
        extent=gbts._extent(sensor)
        self.assertEqual(extent[0],10.)
        self.assertAlmostEqual(extent[1],math.sqrt(104.))
        self.assertEqual(extent[2:],(-3.,3.))

    def test_duplicate_and_missing_native_geometry_fail(self):
        bad=copy.deepcopy(self.report);bad["sensors"][-1]["geometry_id"]=1
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            gbts.prepare(bad,"unused")
        bad=copy.deepcopy(self.report);bad["sensors"][0]["ids"]["system"]=7
        with self.assertRaisesRegex(ValueError,"12410"):
            gbts.prepare(bad,"unused")

    def test_cluster_cut_unknown_setting_and_roi_mismatch_fail(self):
        for bad in ({"seed_finder":{"useClusterWidthCuts":True}},
                    {"seed_finder":{"typoCut":1}}, {"made_up":1},
                    {"z0_range_mm":[-50.,50.]}, {"b_field_T":float("nan")},
                    {"max_seeds_per_event":-1}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                gbts.configuration(bad)

    def test_schedule_rejects_changed_prepared_input_before_native_import(self):
        with tempfile.TemporaryDirectory() as directory:
            gbts.prepare(self.report,directory)
            with (Path(directory)/"mapping.csv").open("a") as stream:stream.write("1,101\n")
            with self.assertRaisesRegex(ValueError,"prepared input changed"):
                gbts.schedule(None,None,None,directory)


if __name__=="__main__":
    unittest.main()
