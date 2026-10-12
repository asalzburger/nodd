"""The retained pixel edition remains pinned across later live-model revisions."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('tdr_generate', Path(__file__).with_name('generate.py'))
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

class FrozenSnapshot(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((generator.ROOT / 'docs/publication/tdr/evidence.json').read_text())

    def test_original_source_pins_and_tables(self):
        generator.verify_sources(self.manifest)
        self.assertEqual(generator.table(), (generator.ROOT / 'docs/publication/tdr/generated/disc-inventory.tex').read_text())
        self.assertEqual(generator.facts(), (generator.ROOT / 'docs/publication/tdr/generated/pixel-facts.tex').read_text())

    def test_snapshot_mutation_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'snapshot'
            shutil.copytree(generator.SOURCE_ROOT, root)
            path = root / generator.SOURCES[0]
            path.write_bytes(path.read_bytes() + b'\n')
            with patch.object(generator, 'SOURCE_ROOT', root):
                with self.assertRaisesRegex(ValueError, 'Stale TDR evidence source'):
                    generator.verify_sources(self.manifest)

if __name__ == '__main__':
    unittest.main()
