"""Scientific boundary checks; no IdRes binary or plotting dependency required."""
import copy
import math
import unittest

from prepare import OUT, patch_bounds, read
from run import check_keys, convert, eta_grid, geometry, profile, validate_config


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = read(OUT/"geometries.json")

    def test_original_source_radii_and_counts(self):
        odd = self.config["candidates"][0]
        self.assertEqual(len(odd["layers"]), 48)
        self.assertEqual([l["r_m"] for l in odd["layers"] if l["kind"] == "cylinder" and l["subsystem"] == "pixel"], [.034, .07, .116, .172])
        self.assertEqual(len([l for l in odd["layers"] if l["kind"] == "disc" and l["subsystem"] == "pixel"]), 14)

    def test_binary_pitch_and_stereo_pair_covariance(self):
        r = self.config["response"]
        self.assertAlmostEqual(r["pixel"]["sigma_rphi_m"], .00005/math.sqrt(12))
        self.assertAlmostEqual(r["short_strip"]["sigma_rphi_m"], .000075/math.sqrt(12))
        a = r["long_strip"]["full_stereo_angle_rad"]/2
        sigma = .00008/math.sqrt(12)
        self.assertAlmostEqual(r["long_strip"]["sigma_rphi_m"], sigma/(math.sqrt(2)*math.cos(a)))
        self.assertAlmostEqual(r["long_strip"]["sigma_second_m"], sigma/(math.sqrt(2)*math.sin(a)))

    def test_technology_counts_independent_of_idres_heuristic(self):
        p = profile(self.config["candidates"][1], 0, 0)
        self.assertEqual((p["pixel_hits"], p["short_strip_hits"], p["long_strip_stations"]), (4,4,2))
        self.assertEqual((p["sensor_hits"], p["measurement_stations"]), (12,10))
        self.assertEqual((p["idres_nPixHits"], p["idres_nStripHits"]), (8,4))
        self.assertAlmostEqual(p["material_percent_x0"], 14)

    def test_cylinder_and_disc_incidence(self):
        cylinder = dict(id="barrel", subsystem="pixel", kind="cylinder", r_m=.1,
                        z_min_m=-10, z_max_m=10, x0_percent=1,
                        sigma_rphi_m=1e-5, sigma_second_m=1e-5)
        disc = dict(id="disc", subsystem="pixel", kind="disc", r_min_m=.01,
                    r_max_m=10, z_m=1, x0_percent=2,
                    sigma_rphi_m=1e-5, sigma_second_m=1e-5)
        p = profile(dict(id="test", layers=[cylinder, disc]), 1, 0)
        self.assertAlmostEqual(p["material_percent_x0"], math.cosh(1)+2/math.tanh(1))
        self.assertEqual(profile(dict(id="test", layers=[disc]), 0, 0)["sensor_hits"], 0)

    def test_rectangle_radial_bounds(self):
        lo, hi = patch_bounds([dict(center_mm=[10,0,1], u=[1,0,0], v=[0,1,0], half_u_mm=2, half_v_mm=3)])
        self.assertAlmostEqual(lo, .008)
        self.assertAlmostEqual(hi, math.sqrt(12**2+3**2)/1000)

    def test_aperture_changes_only_outer_pixel_inner_radii(self):
        full, adapted = self.config["candidates"][1:]
        changes = []
        for a,b in zip(full["layers"], adapted["layers"]):
            x,y = dict(a),dict(b)
            x.pop("source_locator"); y.pop("source_locator")
            if x != y:
                self.assertEqual(a["subsystem"], "pixel")
                self.assertEqual(a["kind"], "disc")
                self.assertGreater(b["r_min_m"], a["r_min_m"])
                x.pop("r_min_m"); y.pop("r_min_m")
                self.assertEqual(x,y)
                changes.append(a["id"])
        self.assertEqual(len(changes), 10)
        for z in (-.15,0,.15):
            for eta in eta_grid(self.config["scan"]):
                a,b = profile(full, eta,z),profile(adapted,eta,z)
                for k in ("sensor_hits", "measurement_stations", "material_percent_x0", "layer_ids"):
                    self.assertEqual(a[k],b[k], (eta,z,k))

    def test_missing_duplicate_and_nonfinite_inputs_rejected(self):
        expected = {(0,0,1,0), (0,0,1,1)}
        row = dict(B=0,z=0,Pt=1,Eta=0)
        for rows in ([row], [row,row]):
            with self.assertRaises(ValueError):
                check_keys(rows, expected)
        bad = copy.deepcopy(self.config)
        bad["candidates"][0]["layers"][0]["sigma_rphi_m"] = math.nan
        with self.assertRaises(ValueError):
            validate_config(bad)

    def test_one_field_per_process_and_momentum_units(self):
        text = geometry(self.config["candidates"][0], self.config["scan"], 3)
        self.assertIn("B 3 end\n", text)
        with self.assertRaises(ValueError):
            geometry(self.config["candidates"][0], self.config["scan"], 3, 0)
        row = dict(Sig_invPt=2,z=0,Pt=100,Eta=4,Sig_d0=1,Sig_z0=2,Sig_phi=.01,Sig_cotT=.01,LeverArm=.1)
        out = convert(row,"test",3)
        self.assertEqual(out["sigma_inverse_pt_GeV_inverse"], .002)
        self.assertEqual(out["linearized_relative_pt_percent"], 20)


if __name__ == "__main__":
    unittest.main()
