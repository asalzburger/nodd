"""Synthetic conversation fixtures test publication boundaries and navigation data."""

import json
from pathlib import Path
import subprocess
import unittest

import build
import test_build as usage_fixture


class InteractionExportTests(unittest.TestCase):
    setUp = usage_fixture.UsageTests.setUp
    add_record = usage_fixture.UsageTests.add_record

    def add_interaction(self, number=1):
        ledger = build.conversation_export.ledger_module()
        path = self.root / 'logs/codex/SESSION-2026-09-16-one.json'
        record = json.loads(path.read_text())
        record['client']['thread_id'] = 'PRIVATE_THREAD_FIXTURE'
        record['usage'][0]['source'] = 'PRIVATE_USAGE_PROVENANCE_FIXTURE'
        record['activities'] = [{'kind': 'tool', 'name': 'Synthetic wrapper', 'version': None,
                                 'calls': None, 'failures': None, 'duration_seconds': None,
                                 'evidence': 'PRIVATE_ACTIVITY_ARGUMENT_FIXTURE'}]
        ledger.write(path, record)
        revision = subprocess.check_output(['git', '-C', str(self.root), 'rev-parse', 'HEAD'], text=True).strip()
        snapshot = {
            'schema_version': 1,
            'github': {'captured_at': '2026-10-24T10:00:00Z',
                       'pull_request': {'number': number, 'url': build.REPOSITORY + f'/pull/{number}',
                                        'title': 'Infrastructure: synthetic conversation', 'head': 'fixture-branch',
                                        'head_sha': revision, 'state': 'open', 'body': 'Published fixture',
                                        'actor': 'asalzburger', 'created_at': None},
                       'comments': [{'id': 1, 'url': build.REPOSITORY + f'/pull/{number}#issuecomment-1',
                                     'body': '<img src=x onerror="alert(1)"> literal fixture',
                                     'actor': 'fixture-reviewer', 'created_at': '2026-10-24T09:00:00Z',
                                     'updated_at': None, 'review': None, 'in_reply_to_id': None,
                                     'path': None, 'line': None}], 'issues': []},
            'curated': {'journal_links': [record['session_id']], 'agents': [], 'tools': [], 'events': []},
            'derived': {}}
        snapshot['derived'] = ledger.derive(self.root, snapshot, [record])
        ledger.write(ledger.path_for(self.root, number), snapshot)

    def test_lazy_pr_payloads_have_sources_and_no_raw_accounting_state(self):
        self.add_interaction()
        output = self.root / '_site/conversations'
        build.build(self.root, output, '2026-10-24T10:00:00Z')
        index = json.loads((output / 'interactions.json').read_text())
        self.assertEqual(index['pull_requests'][0]['data'], 'interactions/pr-0001.json')
        detail = json.loads((output / index['pull_requests'][0]['data']).read_text())
        self.assertEqual(detail['number'], 1)
        self.assertEqual({g['id'] for g in detail['groups']}, {'github', 'notes'})
        self.assertEqual(detail['accounts'][0]['turn_count'], 1)
        self.assertNotIn('input_tokens', json.dumps(detail))
        published = '\n'.join(p.read_text() for p in output.rglob('*') if p.is_file())
        for private in ('PRIVATE_THREAD_FIXTURE', 'PRIVATE_USAGE_PROVENANCE_FIXTURE',
                        'PRIVATE_ACTIVITY_ARGUMENT_FIXTURE'):
            self.assertNotIn(private, published)
        self.assertNotIn('<img src=x', (output / 'interactions.html').read_text())
        event = detail['groups'][0]['threads'][0]['messages'][1]
        self.assertIn('<img src=x', event['text'])  # Literal JSON text for safe DOM rendering.
        self.assertTrue(event['source_url'].startswith(build.REPOSITORY + '/'))

    def test_stale_ledger_stops_site_publication(self):
        self.add_interaction()
        narrative = self.root / 'logs/codex/SESSION-2026-09-16-one.md'
        narrative.write_text(narrative.read_text() + '\nChanged fixture narrative\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            build.build(self.root, self.root / '_site/stale', '2026-10-24T10:00:00Z')

    def test_navigation_and_empty_conversation_page(self):
        output = self.root / '_site/empty-interactions'
        build.build(self.root, output, '2026-10-24T10:00:00Z')
        usage = (output / 'index.html').read_text()
        conversations = (output / 'interactions.html').read_text()
        self.assertIn('href="interactions.html"', usage)
        self.assertIn('aria-current="page">Interactions', conversations)
        self.assertIn('id="pr-search"', conversations)
        self.assertIn('id="source-select"', conversations)
        self.assertIn('id="conversation"', conversations)
        self.assertEqual(json.loads((output / 'interactions.json').read_text())['pull_requests'], [])

    def test_safe_source_links_reject_escape_and_executable_schemes(self):
        revision, fallback = 'a' * 40, 'interactions/pr-0001.json'
        source = build.conversation_export.source_link
        expected = build.REPOSITORY + '/blob/' + revision + '/' + fallback
        for invalid in ('javascript:alert(1)', 'data:text/html,<script>', '../private.txt',
                        '/Users/fixture/private', 'https://example.invalid/private'):
            self.assertEqual(source(invalid, revision, fallback), expected)
        self.assertEqual(source('logs/codex/fixture.md#selected-conversation', revision, fallback),
                         build.REPOSITORY + '/blob/' + revision + '/logs/codex/fixture.md#selected-conversation')

    def test_index_is_newest_first_and_deterministic_nested_payloads(self):
        self.add_interaction(1)
        self.add_interaction(2)
        first, second = self.root / '_site/a', self.root / '_site/b'
        build.build(self.root, first, '2026-10-24T10:00:00Z')
        build.build(self.root, second, '2026-10-24T10:00:00Z')
        index = json.loads((first / 'interactions.json').read_text())
        self.assertEqual([p['number'] for p in index['pull_requests']], [2, 1])
        for path in first.rglob('*'):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (second / path.relative_to(first)).read_bytes())
        (first / 'interactions/unknown.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Unexpected'):
            build.build(self.root, first, '2026-10-24T10:00:00Z')


if __name__ == '__main__':
    unittest.main()
