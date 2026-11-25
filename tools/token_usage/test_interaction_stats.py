"""Synthetic evidence verifies counting units, attribution and publication limits."""

import json
import unittest

import build
import interaction_stats as stats
import test_interaction_export as export_fixture


class StatisticsTests(unittest.TestCase):
    setUp = export_fixture.InteractionExportTests.setUp
    add_record = export_fixture.InteractionExportTests.add_record
    add_interaction = export_fixture.InteractionExportTests.add_interaction

    def add_visible(self, number, *, text='Hello human', parent=None, calls=3):
        ledger = build.conversation_export.ledger_module()
        sid = 'SESSION-2026-09-16-one'
        path = ledger.path_for(self.root, number)
        snapshot = ledger.logger.read_json(path)
        turn = {'schema_version': 1, 'thread_id': 'synthetic-thread', 'turn_id': 'turn-one',
                'status': 'completed', 'started_at': None, 'completed_at': None,
                'token_accounts': [sid], 'source': 'Synthetic visible fixture',
                'messages': [{'id': 'shared-human', 'role': 'user', 'phase': None,
                              'text': text, 'redacted': 'no'},
                             {'id': 'shared-response', 'role': 'assistant', 'phase': 'final_answer',
                              'text': 'Here is the response', 'redacted': 'no'}],
                'native_tools': [{'name': 'commandExecution', 'calls': calls, 'failures': 1}],
                'subagents': [], 'limitations': ['Synthetic, not measured activity.']}
        if parent:
            turn['parent_thread_id'] = parent
        visible = self.root / f'interactions/pr-{number:04d}/turns/fixture.json'
        visible.parent.mkdir(parents=True, exist_ok=True)
        ledger.write(visible, turn)
        snapshot['derived'] = ledger.derive(self.root, snapshot, ledger.logger.load_records(self.root))
        ledger.write(path, snapshot)

    def test_unicode_word_definition(self):
        self.assertEqual(stats.word_count("don't l’air naïve 42 x_y foo-bar"), 7)
        self.assertEqual(stats.word_count('**two words**\nhttps://example.invalid/a'), 6)
        self.assertEqual(stats.word_count(''), 0)

    def test_shared_messages_turns_accounts_and_tools_count_once(self):
        self.add_interaction(1)
        self.add_interaction(2)
        self.add_visible(1)
        self.add_visible(2)
        result = stats.collect(self.root)
        recorded = result['sources'][0]
        self.assertEqual(recorded['events'], 2)
        self.assertEqual(recorded['words']['human'], 2)
        self.assertEqual(recorded['words']['agent_response'], 4)
        self.assertEqual(result['interactions']['visible_turns'], 1)
        self.assertEqual(result['interactions']['account_turns'], 1)
        self.assertEqual(result['work']['canonical_sessions'], 1)
        self.assertEqual(result['tools']['operation_calls'], 3)
        self.assertEqual(result['tools']['operations'][0]['failures'], 1)
        self.assertEqual(result['participants']['named_human_accounts'], ['fixture-reviewer'])
        self.assertEqual(result['participants']['exposed_agent_threads'], 2)
        self.assertIsNone(result['participants']['distinct_humans'])
        self.assertGreater(result['interactions']['duplicate_references_removed'], 0)
        self.assertEqual(result['words']['responses'], result['words']['agent_response']
                         + result['words']['published_response'])

    def test_conflicting_inherited_authorship_is_unresolved(self):
        self.add_interaction(1)
        self.add_interaction(2)
        self.add_visible(1)
        self.add_visible(2, parent='synthetic-parent')
        result = stats.collect(self.root)
        self.assertEqual(result['coverage']['ambiguous_primary_events'], 1)
        self.assertEqual(result['sources'][0]['words']['human'], 0)
        self.assertEqual(result['sources'][0]['words']['unresolved'], 2)
        self.assertEqual(result['participants']['exposed_child_threads'], 1)

    def test_agent_handoff_is_separate_from_human_words(self):
        self.add_interaction()
        self.add_visible(1, parent='synthetic-parent')
        result = stats.collect(self.root)
        self.assertEqual(result['sources'][0]['words']['agent_prompt'], 2)
        self.assertEqual(result['sources'][0]['words']['human'], 0)

    def test_conflicting_text_or_operation_counts_fail(self):
        for change in ('text', 'calls'):
            with self.subTest(change=change):
                self.add_interaction(1)
                self.add_interaction(2)
                self.add_visible(1)
                self.add_visible(2, **({'text': 'Conflicting message'} if change == 'text' else {'calls': 4}))
                with self.assertRaisesRegex(ValueError, 'Conflicting'):
                    stats.collect(self.root)

    def test_journal_excerpts_are_separate_and_generated_summaries_excluded(self):
        narrative = self.root / 'logs/codex/SESSION-2026-09-16-one.md'
        narrative.write_text(narrative.read_text() + '\n## Selected conversation\nUser: two selected words.\n')
        self.add_interaction()
        result = stats.collect(self.root)
        notes = next(row for row in result['sources'] if row['id'] == 'notes')
        self.assertGreater(notes['words']['human'], 0)
        self.assertEqual(result['words']['human'], result['sources'][1]['words']['human'])
        self.assertEqual(result['interactions']['generated_summaries_excluded'], 1)
        self.assertEqual(result['coverage']['account_turns_without_visible_snapshot'], 1)
        self.assertIsNone(result['work']['tracked_tasks'])

    def test_bodyless_review_is_an_event_without_authored_words(self):
        self.add_interaction()
        before = stats.collect(self.root)
        ledger = build.conversation_export.ledger_module()
        path = ledger.path_for(self.root, 1)
        snapshot = ledger.logger.read_json(path)
        review = dict(snapshot['github']['comments'][0], id=2,
                      url=build.REPOSITORY + '/pull/1#pullrequestreview-2', body='', review='APPROVED')
        snapshot['github']['comments'].append(review)
        snapshot['derived'] = ledger.derive(self.root, snapshot, ledger.logger.load_records(self.root))
        ledger.write(path, snapshot)
        after = stats.collect(self.root)
        self.assertEqual(before['words'], after['words'])
        self.assertEqual(after['interactions']['review_decisions_without_text'], 1)
        self.assertEqual(after['interactions']['message_events'], before['interactions']['message_events'] + 1)

    def test_html_navigation_counts_and_aggregate_privacy(self):
        self.add_interaction()
        self.add_visible(1)
        output = self.root / '_site/statistics'
        build.build(self.root, output, '2026-11-25T08:00:00Z')
        data = json.loads((output / 'statistics.json').read_text())
        page = (output / 'statistics.html').read_text()
        self.assertIn('aria-current="page">Statistics', page)
        for name in ('index.html', 'interactions.html'):
            self.assertIn('href="statistics.html"', (output / name).read_text())
        self.assertIn('Human words', page)
        self.assertIn('Download statistics JSON', page)
        self.assertIn('Journal excerpts', page)
        self.assertEqual(data['metadata']['built_at'], '2026-11-25T08:00:00Z')
        published = (output / 'statistics.json').read_text() + page
        for private in ('PRIVATE_THREAD_FIXTURE', 'synthetic-thread', 'turn-one',
                        'PRIVATE_USAGE_PROVENANCE_FIXTURE', 'Hello human', '<img src=x'):
            self.assertNotIn(private, published)


if __name__ == '__main__':
    unittest.main()
