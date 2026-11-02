"""Adverse publication checks with synthetic byte/hash fixtures."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from verify_plots import verify_family


class PublicationChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.figures = self.root / "figures"
        self.figures.mkdir()
        self.source = self.root / "plot.py"
        self.source.write_text("# synthetic plotting-source fixture\n")
        self.manifest = {"files_sha256": {}, "plot_sha256": self.digest(self.source),
                         "profiles_sha256": "0" * 64}
        for suffix in ("png", "pdf"):
            p = self.figures / f"fixture.{suffix}"
            p.write_bytes(b"synthetic export hash fixture")
            self.manifest["files_sha256"][p.name] = self.digest(p)
        self.write_manifest()

    def digest(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_manifest(self):
        (self.figures / "manifest.json").write_text(json.dumps(self.manifest))

    def verify(self):
        return verify_family(self.figures, self.source, 1)

    def test_published_pair_needs_no_local_dataset(self):
        self.assertEqual(self.verify(), 2)

    def test_changed_export_is_rejected(self):
        (self.figures / "fixture.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "changed figure"):
            self.verify()

    def test_missing_export_is_rejected(self):
        (self.figures / "fixture.pdf").unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.verify()

    def test_unsafe_inventory_is_rejected(self):
        self.manifest["files_sha256"]["../escape.png"] = self.manifest["files_sha256"].pop("fixture.png")
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            self.verify()

    def test_source_change_is_rejected(self):
        self.source.write_text("# different source\n")
        with self.assertRaisesRegex(ValueError, "Plot source"):
            self.verify()

    def test_available_local_data_is_still_hash_checked(self):
        (self.root / "profiles.json.gz").write_bytes(b"different profile fixture")
        with self.assertRaisesRegex(ValueError, "Local profile"):
            self.verify()

    def test_unlisted_export_is_rejected(self):
        (self.figures / "extra.png").write_bytes(b"unlisted")
        with self.assertRaisesRegex(ValueError, "Unlisted"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
