import hashlib
from pathlib import Path
import tempfile
import unittest

from preflight import inspect


class NodePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'synthetic-setup'
        self.path.write_text('synthetic fixture')
        self.registry = {'nodes': [{'hostname': 'synthetic-node', 'verified_at': '2026-09-22',
            'required_files': [str(self.path)],
            'fingerprints': {'setup': {'path': str(self.path),
                'sha256': hashlib.sha256(self.path.read_bytes()).hexdigest()}},
            'source_trees': {'dd4hep': None, 'geant4': None}}]}

    def test_known_matching_node(self):
        result = inspect(self.registry, 'synthetic-node')
        self.assertEqual(result['status'], 'prerequisites-present')
        self.assertFalse(result['warnings'])

    def test_unknown_node_warns(self):
        result = inspect(self.registry, 'other-node')
        self.assertEqual(result['status'], 'unverified')
        self.assertTrue(result['warnings'])

    def test_removed_prerequisite_warns(self):
        self.path.unlink()
        self.assertEqual(inspect(self.registry, 'synthetic-node')['status'], 'unavailable')

    def test_changed_environment_warns(self):
        self.path.write_text('changed fixture')
        result = inspect(self.registry, 'synthetic-node')
        self.assertEqual(result['status'], 'unverified')
        self.assertTrue(result['warnings'])

    def test_sources_are_separate_from_libraries(self):
        result = inspect(self.registry, 'synthetic-node', require_sources=True)
        self.assertEqual(len(result['warnings']), 2)
        source = Path(self.temp.name)/'source'
        source.mkdir()
        (source/'CMakeLists.txt').write_text('# synthetic fixture')
        self.registry['nodes'][0]['source_trees'] = {'dd4hep': str(source), 'geant4': str(source)}
        self.assertFalse(inspect(self.registry, 'synthetic-node', True)['warnings'])
