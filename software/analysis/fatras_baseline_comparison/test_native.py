"""Portable scientific identity gates; no ACTS import required."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location("fatras_run_native",Path(__file__).with_name("run_native.py"))
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


class NativeContracts(unittest.TestCase):
    def test_generator_field_and_training_are_matched(self):
        old,current=runner.campaign("old"),runner.campaign("current")
        runner.check_settings(old);runner.check_settings(current)
        for name in ("seed","field_Bz_T","eta_range","phi_range_rad","vertex_mm","truth_tracking"):
            self.assertEqual(old[name],current[name])
        self.assertEqual(old["pt_GeV"],[1.,5.,10.,100.])
        self.assertEqual(old["digitization"]["short_strip_pitch_mm"],[.075,.5])
        self.assertEqual(current["digitization"]["short_strip_pitch_mm"],[.075,2.])

    def test_sampling_drift_rejected(self):
        for key,value in (("seed",228),("field_Bz_T",2.),("eta_range",[-4.5,4.5]),("particles_per_event",2)):
            config=runner.campaign("current");config[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):runner.check_settings(config)

    def test_old_errors_rejected_for_current_pitch(self):
        with tempfile.TemporaryDirectory() as temp:
            table=Path(temp)/"errors.json";table.write_text('{}')
            old=runner.campaign("old")
            audit={"table_sha256":runner.sha(table),"configuration":old,"training":old["error_training"]}
            runner.check_error_identity(old,audit,table)
            with self.assertRaisesRegex(ValueError,"different response"):
                runner.check_error_identity(runner.campaign("current"),audit,table)
            table.write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError,"hash"):
                runner.check_error_identity(old,audit,table)

    def test_geometry_binary_change_rejected(self):
        actual=[{"path":"/task/libTracker.dylib","sha256":"new"}]
        with self.assertRaisesRegex(ValueError,"differs"):
            runner.verify_named_files(actual,[{"name":"libTracker.dylib","sha256":"old"}])


if __name__=="__main__":unittest.main()
