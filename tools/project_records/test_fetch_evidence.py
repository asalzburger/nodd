"""Fresh single-branch fixtures reproduce missing historical merge evidence."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import fetch_evidence


class HistoricalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'source'
        self.source.mkdir()
        self.git(self.source, 'init', '-q', '-b', 'main')
        self.git(self.source, 'config', 'user.name', 'Synthetic fixture')
        self.git(self.source, 'config', 'user.email', 'fixture@example.invalid')
        self.commit('baseline')
        self.base = self.git(self.source, 'rev-parse', 'HEAD')
        self.git(self.source, 'switch', '-q', '-c', 'topic')
        self.commit('historical implementation')
        self.head = self.git(self.source, 'rev-parse', 'HEAD')
        self.git(self.source, 'switch', '-q', 'main')
        self.git(self.source, 'merge', '-q', '--no-ff', 'topic', '-m', 'Historical merge')
        self.merge = self.git(self.source, 'rev-parse', 'HEAD')
        self.git(self.source, 'switch', '-q', '-c', 'current', self.base)
        self.commit('rebased implementation')
        self.repo = Path(self.tmp.name) / 'checkout'
        self.git(self.source, 'clone', '-q', '--no-local', '--single-branch',
                 '--branch', 'current', str(self.source), str(self.repo))
        (self.repo / 'project').mkdir()
        self.tracking = {'pull_requests': [{'state': 'merged',
                         'head_revision': self.head, 'merge_commit': self.merge}]}
        self.reviews = {'rounds': [{'target_revision': self.base}]}
        self.save()

    def git(self, root, *args):
        return subprocess.check_output(['git', '-C', str(root), *args],
                                       text=True, stderr=subprocess.PIPE).strip()

    def commit(self, value):
        (self.source / 'fixture.txt').write_text(value)
        self.git(self.source, 'add', 'fixture.txt')
        self.git(self.source, 'commit', '-qm', value)

    def save(self):
        for name, record in (('tracking', self.tracking), ('reviews', self.reviews)):
            (self.repo / f'project/{name}.json').write_text(json.dumps(record))

    def test_fresh_clone_recovers_exact_merge_and_review_evidence(self):
        self.assertEqual(set(fetch_evidence.missing_revisions(
            self.repo, [self.head, self.merge])), {self.head, self.merge})
        # A review may also depend on a historical commit outside the current branch.
        self.reviews['rounds'].append({'target_revision': self.head})
        self.save()
        self.assertEqual(set(fetch_evidence.fetch_evidence(self.repo)),
                         {self.head, self.merge})
        self.git(self.repo, 'merge-base', '--is-ancestor', self.head, self.merge)
        with patch.object(fetch_evidence.subprocess, 'run', wraps=subprocess.run) as run:
            self.assertEqual(fetch_evidence.fetch_evidence(self.repo), [])
            self.assertFalse(any('fetch' in call.args[0] for call in run.call_args_list))

    def test_open_pr_snapshot_is_not_required_git_evidence(self):
        self.tracking['pull_requests'].append({'state': 'open', 'head_revision': '0' * 40})
        self.save()
        self.assertNotIn('0' * 40, fetch_evidence.required_revisions(self.repo))

    def test_invalid_revision_fails_before_fetch(self):
        self.reviews['rounds'].append({'target_revision': '--invalid-test-revision'})
        self.save()
        with patch.object(fetch_evidence.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'full 40-character commit SHAs'):
                fetch_evidence.fetch_evidence(self.repo)
            run.assert_not_called()

    def test_unavailable_commit_fails_without_skipping_validation(self):
        self.tracking['pull_requests'][0]['merge_commit'] = '0' * 40
        self.save()
        with self.assertRaises(subprocess.CalledProcessError):
            fetch_evidence.fetch_evidence(self.repo)


if __name__ == '__main__':
    unittest.main()
