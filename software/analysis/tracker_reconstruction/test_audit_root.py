"""A missing campaign must never produce a successful persistence audit."""
from pathlib import Path
import tempfile
import unittest
from audit_root import audit


class PersistenceControls(unittest.TestCase):
    def test_empty_or_broken_staging_is_rejected_without_a_pass_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);output=root/"audit.json"
            with self.assertRaisesRegex(ValueError,"No native ROOT cases"):
                audit(root/"missing",root/"analysis",output)
            self.assertFalse(output.exists())
