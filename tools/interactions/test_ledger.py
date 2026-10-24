"""Synthetic fixtures: no real client observations or identities."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import ledger
from visible import curate_turn


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.narrative = self.root / 'logs/codex/SESSION-2026-10-24-fixture.md'
        self.narrative.parent.mkdir(parents=True)
        self.narrative.write_text('## Selected conversation\nUser: fixture input.\n')
        self.record = {'schema_version': 1, 'session_id': self.narrative.stem,
                       'title': 'Synthetic fixture', 'recorded_at': '2026-10-24T00:00:00Z',
                       'started_at': None, 'ended_at': None, 'status': 'open',
                       'collection': 'retrospective', 'completeness': 'partial',
                       'limitations': ['Synthetic fixture.'],
                       'client': {'name': 'fixture-agent', 'version': None, 'thread_id': 'fixture-thread'},
                       'git': {'start_commit': 'a' * 40, 'branch': 'fixture',
                               'initial_changes': [], 'result_commits': [], 'changed_files': []},
                       'work': {'milestone': 'M0', 'components': [], 'related_ids': []},
                       'narrative': self.narrative.relative_to(self.root).as_posix(),
                       'activities': [], 'usage': [], 'checks': []}
        self.record_path = self.narrative.with_suffix('.json')
        ledger.write(self.record_path, self.record)
        self.snapshot = {'schema_version': 1,
                         'github': {'captured_at': '2026-10-24T00:00:00Z',
                                    'pull_request': {'number': 1, 'url': ledger.BASE + '/pull/1',
                                                     'title': 'Infrastructure: fixture', 'head': 'fixture',
                                                     'head_sha': 'a' * 40, 'state': 'open', 'body': 'Fixture body',
                                                     'actor': 'asalzburger', 'created_at': None},
                                    'comments': [], 'issues': []},
                         'curated': {'journal_links': [], 'agents': [], 'tools': [], 'events': []},
                         'derived': {}}

    def sync(self):
        self.snapshot['derived'] = ledger.derive(self.root, self.snapshot, [self.record])
        return self.snapshot['derived']

    def turn(self):
        return {'client_thread_id': 'fixture-thread', 'turn_id': 'fixture-turn', 'model': None,
                'source': 'Synthetic', 'limitations': ['Unknown model.'],
                'input_tokens': 10, 'output_tokens': 2, 'total_tokens': 12,
                'cached_input_tokens': 5, 'reasoning_output_tokens': 1}

    def test_usage_change_fails_until_synced_and_never_copies_counters(self):
        self.sync()
        self.record['usage'] = [self.turn()]
        with self.assertRaisesRegex(ValueError, 'stale'):
            ledger.validate_derived(self.root, self.snapshot, [self.record])
        self.sync()
        ledger.validate_derived(self.root, self.snapshot, [self.record])
        self.assertEqual(self.snapshot['derived']['token_accounts'][0]['turns'][0]['model'], None)
        self.assertNotIn('input_tokens', json.dumps(self.snapshot['derived']))
        self.assertEqual(self.record['usage'][0]['total_tokens'], 12)

    def test_narrative_change_invalidates_fingerprint(self):
        self.sync()
        self.narrative.write_text('## Selected conversation\nCorrected fixture.\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            ledger.validate_derived(self.root, self.snapshot, [self.record])

    def test_shared_pr_references_keep_one_owner(self):
        self.record['usage'] = [self.turn()]
        first = self.sync()['token_accounts']
        other = copy.deepcopy(self.snapshot)
        other['github']['pull_request']['number'] = 2
        other['github']['pull_request']['url'] = ledger.BASE + '/pull/2'
        second = ledger.derive(self.root, other, [self.record])['token_accounts']
        self.assertEqual(first, second)
        self.assertEqual(len(self.record['usage']), 1)

    def test_human_names_remote_codex_input_and_upload(self):
        def comment(n, actor, text, reply=None):
            return {'id': n, 'url': ledger.BASE + f'/pull/1#issuecomment-{n}', 'body': text,
                    'actor': actor, 'created_at': None, 'updated_at': None, 'review': None,
                    'in_reply_to_id': reply, 'path': None, 'line': None}
        self.snapshot['github']['comments'] = [
            comment(1, 'fixture-reviewer', 'https://github.com/user-attachments/files/123/fixture.pdf'),
            comment(2, 'asalzburger', '@codex please assess', 1),
            comment(3, 'asalzburger', 'Delivered response', 1)]
        events = self.sync()['events']
        self.assertTrue(any(e['type'] == 'upload' for e in events))
        self.assertEqual(events[3]['type'], 'prompt')
        self.assertEqual(events[3]['direction'], 'action')
        self.assertEqual(events[4]['direction'], 'reaction')
        self.assertEqual(events[4]['in_reply_to'], events[1]['id'])

    def test_invalid_tool_category_and_unknown_fields_rejected(self):
        self.snapshot['curated']['tools'] = [{'name': 'fake', 'category': 'guessed'}]
        with self.assertRaises(ValueError):
            ledger.validate_snapshot(self.snapshot, 1)
        self.snapshot['curated']['tools'] = []
        self.snapshot['github']['credentials'] = 'fixture'
        with self.assertRaises(ValueError):
            ledger.validate_snapshot(self.snapshot, 1)

    def test_duplicate_usage_still_rejected_by_canonical_logger(self):
        self.record['usage'] = [self.turn(), self.turn()]
        ledger.write(self.record_path, self.record)
        with self.assertRaises(ValueError):
            ledger.logger.load_records(self.root)

    def test_sync_one_pr_is_idempotent_and_does_not_touch_other_file(self):
        self.sync()
        path = ledger.path_for(self.root, 1)
        other = ledger.path_for(self.root, 2)
        ledger.write(path, self.snapshot)
        other.write_text('Unrelated work remains untouched\n')
        before = path.read_bytes()
        self.assertEqual(ledger.main(['--repo', str(self.root), 'sync', '--pr', '1']), 0)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(other.read_text(), 'Unrelated work remains untouched\n')

    def test_missing_pr_and_bad_filename_identity_fail(self):
        self.assertEqual(ledger.main(['--repo', str(self.root), 'validate', '--pr', '9']), 1)
        self.snapshot['github']['pull_request']['number'] = 2
        with self.assertRaises(ValueError):
            ledger.validate_snapshot(self.snapshot, 1)

    def test_visible_turn_requires_exact_account_pair(self):
        self.record['usage'] = [self.turn()]
        turn = curate_turn('fixture-thread', {'id': 'wrong-turn', 'status': 'completed', 'items': []},
                           [self.record['session_id']])
        ledger.write(self.root / 'interactions/pr-0001/turns/fixture.json', turn)
        with self.assertRaisesRegex(ValueError, 'token account'):
            self.sync()

    def test_visible_allowlist_excludes_private_state_and_preserves_upload_type(self):
        turn = {'id': 'fixture-turn', 'status': 'completed', 'items': [
            {'type': 'reasoning', 'content': 'PRIVATE_REASONING_FIXTURE'},
            {'type': 'commandExecution', 'command': 'PRIVATE_COMMAND_FIXTURE',
             'output': 'PRIVATE_OUTPUT_FIXTURE', 'exitCode': 0},
            {'type': 'userMessage', 'id': 'fixture-message', 'content': [
                {'type': 'text', 'text': 'Use /Users/fixture/private and me@example.test'},
                {'type': 'image', 'data': 'PRIVATE_BINARY_FIXTURE'}]},
            {'type': 'agentMessage', 'id': 'fixture-reply', 'text': 'Visible response', 'phase': 'final_answer'}]}
        curated = curate_turn('fixture-thread', turn, [self.record['session_id']])
        text = json.dumps(curated)
        self.assertNotIn('PRIVATE_', text)
        self.assertNotIn('/Users/fixture', text)
        self.assertNotIn('me@example.test', text)
        self.assertEqual(curated['messages'][1]['phase'], 'upload')
        self.assertIn('Visible response', text)

    def test_unknown_tool_installation_is_not_assumed(self):
        self.record['activities'] = [{'kind': 'tool', 'name': 'fixture-binary', 'version': None,
                                     'calls': None, 'evidence': 'Fixture execution'}]
        tools = self.sync()['tools']
        self.assertEqual(len(tools['unresolved']), 1)
        self.assertEqual(tools['codex_installed'], [])


if __name__ == '__main__':
    unittest.main()
