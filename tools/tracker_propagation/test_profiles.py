"""Synthetic population-profile controls, independent of native ACTS availability."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


def module():
    spec = importlib.util.spec_from_file_location(
        "tracker_profile_plot", Path(__file__).with_name("plot.py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class ProfileTests(unittest.TestCase):
    def test_failed_case_cannot_be_replotted(self):
        plot = module()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            case = directory / "pt_1GeV"
            case.mkdir()
            (case / "run.json").write_text(json.dumps({"status": "FAIL"}))
            with self.assertRaisesRegex(ValueError, "failed accounting"):
                plot.validate_cases(directory, {"pt_GeV": [1]})

    def test_zero_crossing_probes_stay_in_profile_denominator(self):
        import numpy as np
        import uproot
        from unrooted.io.root import load
        from unrooted.io.root.tree import load_branch
        plot = module()
        eta = np.array([-.75, -.25, .25, .75])
        count = np.array([0., 2., 0., 4.])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.root"
            with uproot.recreate(path) as root_file:
                root_file["profile"] = plot.root_profile(
                    eta, count, np.array([-1., 0., 1.]), "Synthetic profile")
                tree = root_file.mktree("tracks", {"eta": "float64", "count": "float64"})
                tree.extend({"eta": eta, "count": count})
            profile = load(path, "profile")
            branch = load_branch(path, "tracks", "eta", "count", n_bins=2, range=(-1, 1))
            np.testing.assert_array_equal(profile.values, [1., 2.])
            np.testing.assert_allclose(profile.variances, [.5, 2.], rtol=0, atol=1e-14)
            np.testing.assert_array_equal(profile.values, branch.values)
            np.testing.assert_allclose(profile.variances, branch.variances, rtol=0, atol=1e-14)

    def test_missing_tracks_and_split_count_mismatch_are_rejected(self):
        plot = module()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.csv"
            header = "event_nr,track_nr,eta,phi,pt_GeV,charge,nSensitives,"
            header += ",".join(f"nSensitives_system{i}" for i in range(1, 8))
            path.write_text(header + "\n0,0,0,0,1,1,2,1,0,0,0,0,0,0\n")
            with self.assertRaisesRegex(ValueError, "expected 2"):
                plot.load_counts(path, 2, (-4, 4))
            with self.assertRaisesRegex(ValueError, "do not close"):
                plot.load_counts(path, 1, (-4, 4))

    def test_duplicate_probe_ids_are_not_a_complete_sample(self):
        plot = module()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.csv"
            header = "event_nr,track_nr,eta,phi,pt_GeV,charge,nSensitives,"
            header += ",".join(f"nSensitives_system{i}" for i in range(1, 8))
            row = "0,0,0,0,1,1,1,1,0,0,0,0,0,0\n"
            path.write_text(header + "\n" + row + row)
            with self.assertRaisesRegex(ValueError, "exactly once"):
                plot.load_counts(path, 2, (-4, 4))


if __name__ == "__main__":
    unittest.main()
