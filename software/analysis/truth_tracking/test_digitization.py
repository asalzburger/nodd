import copy
import unittest
from digitization import build_config, geometry_fields, apply_variance_table


class DigitizationControls(unittest.TestCase):
    def setUp(self):
        self.settings={"pixel_pitch_mm":[.05,.05],"short_strip_pitch_mm":[.075,.5],
            "long_strip_pitch_mm":.08,"digital":True,"threshold":0.}
        self.sensors=[{"geometry_id":(system<<56)|(system<<8),"ids":{"system":system},
            "size_mm":[48.,96.,.3]} for system in range(1,8)]

    def test_exact_pitches_and_native_stereo_faces(self):
        config,counts=build_config(self.sensors,self.settings)
        self.assertEqual(counts,{str(i):1 for i in range(1,8)})
        for entry in config["entries"]:
            system=entry["volume"]
            geometric=entry["value"]["geometric"]
            expected=(self.settings["pixel_pitch_mm"] if system<=3 else
                self.settings["short_strip_pitch_mm"] if system<=5 else [.08])
            self.assertEqual(geometric["indices"],list(range(len(expected))))
            for axis,pitch in zip(geometric["segmentation"]["binningdata"],expected):
                self.assertAlmostEqual((axis["max"]-axis["min"])/axis["bins"],pitch,places=12)
            self.assertEqual(len(geometric["segmentation"]["binningdata"]),2)
            if system >= 6:
                self.assertEqual(geometric["segmentation"]["binningdata"][1]["bins"],1)
            self.assertNotIn("smearing",entry["value"])

    def test_reject_alias_or_missing_sensitive(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            build_config(self.sensors+[self.sensors[0]],self.settings)
        with self.assertRaisesRegex(ValueError,"not sensitive"):
            geometry_fields(1<<56)
        with self.assertRaisesRegex(ValueError,"complete"):
            build_config(self.sensors[:-1],self.settings)

    def error_table(self):
        return {"acts-geometry-hierarchy-map":{"format-version":0,"value-identifier":"hit-error-parametrisation"},
            "entries":[{"volume":i,"value":[{"index":j,"rms":[.01,.02]}
                for j in range(2 if i<6 else 1)]} for i in range(1,8)]}

    def test_variance_table_requires_exact_native_ids(self):
        config,_=build_config(self.sensors,self.settings)
        table=self.error_table();table["entries"][0]["volume"]=99
        with self.assertRaisesRegex(ValueError,"volume identities"):
            apply_variance_table(config,table)

    def test_variance_table_rejects_coordinate_or_nonfinite_values(self):
        config,_=build_config(self.sensors,self.settings)
        table=self.error_table();table["entries"][-1]["value"].append({"index":1,"rms":[.1]})
        with self.assertRaisesRegex(ValueError,"measured coordinates"):
            apply_variance_table(config,table)
        table=self.error_table();table["entries"][0]["value"][0]["rms"]=[float("nan")]
        with self.assertRaisesRegex(ValueError,"positive finite"):
            apply_variance_table(config,table)

    def test_variance_table_applies_cluster_tail_vector(self):
        config,_=build_config(self.sensors,self.settings)
        self.assertEqual(apply_variance_table(config,self.error_table())["entries"][-1]["value"]["geometric"]["variances"],
            [{"index":0,"rms":[.01,.02]}])

    def test_nondivisible_sensor_keeps_pitch(self):
        sensors=copy.deepcopy(self.sensors); sensors[0]["size_mm"][0]=48.013
        config,_=build_config(sensors,self.settings)
        axis=config["entries"][0]["value"]["geometric"]["segmentation"]["binningdata"][0]
        self.assertAlmostEqual((axis["max"]-axis["min"])/axis["bins"],.05)
        self.assertGreaterEqual(axis["max"]-axis["min"],48.013)

if __name__=="__main__":unittest.main()
