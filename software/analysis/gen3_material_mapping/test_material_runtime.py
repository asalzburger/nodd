"""Native-independent checks of the external portal-selection contract."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from material_runtime import audit_material_inventory, load_manifest


class ManifestContractTest(unittest.TestCase):
    def setUp(self):
        self.record = {"geometry_id": 73183493944770560,
                       "material_key": "test-pipe", "type": "cylinder",
                       "rz_segment_mm": [[27.4, -4000.], [27.4, 4000.]],
                       "bins": {"phi": 1, "z": 500}}

    def read(self, records):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "selection.json"
            path.write_text(json.dumps({"schema_version": 1, "surfaces": records}))
            return load_manifest(path)

    def test_user_configurable_phi_and_longitudinal_bins(self):
        record = copy.deepcopy(self.record)
        record["bins"] = {"phi": 2, "z": 17}
        self.assertEqual(self.read([record])["surfaces"][0]["bins"], record["bins"])

    def test_reject_duplicate_surface_and_key(self):
        duplicate = copy.deepcopy(self.record)
        duplicate["material_key"] = "other"
        with self.assertRaisesRegex(ValueError, "Geometry IDs"):
            self.read([self.record, duplicate])
        duplicate["geometry_id"] += 1
        duplicate["material_key"] = self.record["material_key"]
        with self.assertRaisesRegex(ValueError, "Material keys"):
            self.read([self.record, duplicate])

    def test_reject_wrong_axis_and_noninteger_count(self):
        for bins in ({"phi": 1, "r": 50}, {"phi": 1, "z": 0},
                     {"phi": True, "z": 50}, {"phi": 1, "z": 2.5}):
            record = copy.deepcopy(self.record)
            record["bins"] = bins
            with self.subTest(bins=bins), self.assertRaisesRegex(ValueError, "bin counts"):
                self.read([record])

    def test_reject_nonfinite_or_incomplete_bounds(self):
        for segment in ([[27.4, float("nan")], [27.4, 4000.]], [[27.4], [27.4, 4000.]]):
            record = copy.deepcopy(self.record)
            record["rz_segment_mm"] = segment
            with self.subTest(segment=segment), self.assertRaises(ValueError):
                self.read([record])

    def test_disc_uses_radial_bins(self):
        record = copy.deepcopy(self.record)
        record.update(type="disc", bins={"phi": 1, "r": 50},
                      rz_segment_mm=[[28.8, 500.], [200., 500.]])
        self.assertEqual(self.read([record])["surfaces"][0]["bins"]["r"], 50)

    def test_one_by_one_finalizes_as_homogeneous_with_exact_identity(self):
        record = copy.deepcopy(self.record)
        record["bins"]["z"] = 1
        manifest = self.read([record])
        actual = {"geometry_id": record["geometry_id"], "type": "homogeneous",
                  "axis_bin_counts": [1, 1], "material_bins": 1, "empty_bins": 0}
        audit_material_inventory(manifest, [actual], "mapped")
        with self.assertRaisesRegex(RuntimeError, "identities/counts"):
            audit_material_inventory(manifest, [actual, actual], "mapped")
        actual["type"] = "binned"
        with self.assertRaisesRegex(RuntimeError, "type/binning"):
            audit_material_inventory(manifest, [actual], "mapped")

    def test_multibin_request_rejects_homogeneous_fallback(self):
        manifest = self.read([self.record])
        actual = {"geometry_id": self.record["geometry_id"], "type": "homogeneous",
                  "axis_bin_counts": [1, 1], "material_bins": 1, "empty_bins": 0}
        with self.assertRaisesRegex(RuntimeError, "type/binning"):
            audit_material_inventory(manifest, [actual], "mapped")
        actual.update(type="binned", axis_bin_counts=[1, 500], material_bins=500, empty_bins=501)
        with self.assertRaisesRegex(RuntimeError, "inventory is inconsistent"):
            audit_material_inventory(manifest, [actual], "mapped")


if __name__ == "__main__":
    unittest.main()
