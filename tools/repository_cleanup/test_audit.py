"""Meaningful boundaries for immutable cleanup triage."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import audit


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        # Repo-local test identity, without changing any machine configuration.
        self.git('config', 'user.name', 'Test fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.write('docs/validation/tracker-reconstruction/tuning/a b/events.npz', b'\x00original')
        self.write(audit.BASELINE, b'frozen input')
        self.write('docs/validation/DES-011-optimization/cases/a/summary.json', b'{"test": true}')
        self.write('docs/validation/gen3-material-mapping/scatter.npz', b'unknown recording')
        self.write('docs/validation/DES-019/ctest.log', b'test stdout')
        self.write('source.dat', b'x' * audit.LARGE_BYTES)
        self.write('copy.dat', b'x' * audit.LARGE_BYTES)
        self.git('add', '.')
        self.git('commit', '-qm', 'test fixture')
        self.rev = self.git('rev-parse', 'HEAD').decode().strip()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args])

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def test_dirty_files_are_not_substituted_and_inventory_does_not_mutate(self):
        before = audit.inventory(self.root, self.rev)
        self.write(audit.BASELINE, b'changed later')
        status = self.git('status', '--porcelain')
        after = audit.inventory(self.root, self.rev)
        self.assertEqual(before, after)
        self.assertEqual(self.git('status', '--porcelain'), status)
        self.assertEqual(after['tracked_files'], 7)
        self.assertEqual(after['tracked_bytes'] - after['unique_blob_bytes'], audit.LARGE_BYTES)
        self.assertEqual(len(after['large_duplicate_blobs']), 1)
        states = {row['path']: row['state'] for row in after['files']}
        self.assertEqual(states[audit.BASELINE], 'retain_dependency')
        self.assertEqual(states['docs/validation/gen3-material-mapping/scatter.npz'], 'retain_unknown_input')
        self.assertEqual(states['docs/validation/tracker-reconstruction/tuning/a b/events.npz'],
                         'scheduled_after_prerequisites')
        self.assertNotIn('source.dat', states)

    def test_check_fails_for_tampered_inventory_and_creation_does_not_overwrite(self):
        output = self.root / 'inventory.json'
        args = ['--repo', str(self.root), '--revision', self.rev, '--output', str(output)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(audit.main(args), 0)
            self.assertEqual(audit.main(args + ['--check']), 0)
            self.assertEqual(audit.main(args), 1)
            saved = json.loads(output.read_text())
            saved['files'][0]['sha256'] = '0' * 64
            output.write_text(json.dumps(saved))
            self.assertEqual(audit.main(args + ['--check']), 1)
        self.assertEqual(json.loads(output.read_text()), saved)

    def test_requires_a_commit_sha(self):
        for rev in ('HEAD', self.rev[:12], '--help', '0' * 40):
            with self.subTest(rev=rev), self.assertRaises((ValueError, subprocess.CalledProcessError)):
                audit.inventory(self.root, rev)
        blob = self.git('rev-parse', self.rev + ':source.dat').decode().strip()
        with self.assertRaisesRegex(ValueError, 'commit'):
            audit.inventory(self.root, blob)


if __name__ == '__main__':
    unittest.main()
