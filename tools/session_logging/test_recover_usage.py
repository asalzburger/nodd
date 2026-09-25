"""Synthetic token fixtures only; no real client history is used by tests."""
import json
from pathlib import Path
import tempfile
import unittest

import recover_usage as recovery
import session_log as log


class RecoveryTests(unittest.TestCase):
    def usage(self, input_tokens=100, output_tokens=20):
        return dict(input_tokens=input_tokens, output_tokens=output_tokens,
                    cached_input_tokens=input_tokens // 2, reasoning_output_tokens=0,
                    cache_write_input_tokens=0, total_tokens=input_tokens + output_tokens)

    def turn(self, id='test-turn', start=1, end=10, status='completed'):
        return dict(turn_id=id, start_ordinal=start, end_ordinal=end,
                    status=status, started_at=1, completed_at=2)

    def event(self, ordinal=2, total=None, last=None):
        return dict(ordinal=ordinal, timestamp='2026-09-24T00:00:00Z',
                    total=total or self.usage(), last=last or self.usage())

    def test_disjoint_turns_and_repeat_do_not_double_count(self):
        events = [self.event(), self.event(3),
                  self.event(12, self.usage(200, 40), self.usage())]
        result = recovery.reconcile('test-thread', [self.turn(), self.turn('next', 11, 20)], events)
        self.assertEqual(result['repeated_snapshots'], 1)
        self.assertEqual([t['tokens']['input_tokens'] for t in result['turns']], [100, 100])
        self.assertEqual(sum(t['tokens']['total_tokens'] for t in result['turns']), 240)

    def test_repeated_context_snapshot_is_not_a_request(self):
        repeated = self.event(3)
        repeated['last'] = self.usage(0, 0)
        repeated['last']['total_tokens'] = 1234  # Synthetic context-only figure.
        result = recovery.reconcile('test-thread', [self.turn()], [self.event(), repeated])
        self.assertEqual(result['turns'][0]['tokens']['total_tokens'], 120)
        self.assertEqual(result['repeated_snapshots'], 1)

    def test_decrease_missing_request_or_inherited_counter_rejected(self):
        with self.assertRaisesRegex(ValueError, 'reset/decrease'):
            recovery.reconcile('test', [self.turn()], [self.event(), self.event(3, self.usage(50, 10))])
        with self.assertRaisesRegex(ValueError, 'differs'):
            recovery.reconcile('test', [self.turn()], [self.event(total=self.usage(200, 40))])

    def test_invalid_request_total_rejected(self):
        event = self.event()
        event['last']['total_tokens'] += 1
        with self.assertRaisesRegex(ValueError, 'inconsistent total'):
            recovery.reconcile('test', [self.turn()], [event])

    def test_unclosed_and_unobserved_turns_are_not_complete_zero_usage(self):
        result = recovery.reconcile('test', [self.turn(end=None, status='inProgress')], [self.event()])
        self.assertFalse(result['turns'][0]['closed'])
        result = recovery.reconcile('test', [self.turn(), self.turn('empty', 11, 20)], [self.event()])
        self.assertIsNone(result['turns'][1]['tokens']['input_tokens'])

    def test_unknown_boundaries_remain_unassigned(self):
        result = recovery.reconcile('test', [self.turn(start=3)], [self.event()])
        self.assertEqual(len(result['outside_turn_events']), 1)
        self.assertIsNone(result['turns'][0]['tokens']['input_tokens'])
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            recovery.reconcile('test', [self.turn(), self.turn('overlap')], [self.event()])

    def test_only_usage_is_exported_and_partial_final_line_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.jsonl'
            secret = {'type': 'response_item', 'payload': {'text': 'SYNTHETIC_PRIVATE_CONTENT'}}
            usage = {'type': 'event_msg', 'timestamp': '2026-09-24T00:00:00Z',
                     'payload': {'type': 'token_count', 'info': {
                         'total_token_usage': self.usage(), 'last_token_usage': self.usage()}}}
            path.write_text(json.dumps(secret) + '\n' + json.dumps(usage) + '\n' + '{"unfinished":')
            result = recovery.extract_events(path)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['ordinal'], 1)
            self.assertNotIn('SYNTHETIC_PRIVATE_CONTENT', json.dumps(result))

    def test_digest_is_stable_and_changes_with_counter_evidence(self):
        first = recovery.reconcile('test', [self.turn()], [self.event()])
        again = recovery.reconcile('test', [self.turn()], [self.event()])
        self.assertEqual(first['turns'][0]['usage_sha256'], again['turns'][0]['usage_sha256'])
        other = recovery.reconcile('test', [self.turn()], [self.event(total=self.usage(200,40), last=self.usage(200,40))])
        self.assertNotEqual(first['turns'][0]['usage_sha256'], other['turns'][0]['usage_sha256'])

    def test_retained_inventory_reconciles_and_imported_entries_match_logs(self):
        for name in ['USAGE-2026-09-24-local.json', 'USAGE-2026-09-25-device.json']:
            with self.subTest(inventory=name):
                self.check_retained_inventory(name)

    def check_retained_inventory(self, name):
        # Audit retained numeric evidence; do not access any client data directory.
        root = Path(__file__).resolve().parents[2]
        path = root / 'logs/usage' / name
        report = json.loads(path.read_text())
        recorded = {(u['client_thread_id'], u['turn_id']): (r['session_id'], u)
                    for r in log.load_records(root) for u in r['usage']}
        seen = set()
        for thread in report['threads']:
            self.assertEqual(thread['outside_turn_events'], [])
            for field in log.TOKEN_FIELDS:
                self.assertEqual(sum(t['tokens'][field] or 0 for t in thread['turns']),
                                 thread['final_cumulative'][field])
            for turn in thread['turns']:
                key = (thread['thread_id'], turn['turn_id'])
                self.assertNotIn(key, seen)
                seen.add(key)
                if turn['disposition'] == 'imported':
                    self.assertTrue(turn['closed'])
                    self.assertEqual(recorded[key], (turn['target_session_id'], turn['usage_entry']))
        for state, summary in report['summary'].items():
            turns = [t for thread in report['threads'] for t in thread['turns']
                     if t['disposition'] == state]
            self.assertEqual(summary['turns'], len(turns))
            self.assertEqual(summary['sessions'],
                             len({t['target_session_id'] for t in turns
                                  if t['target_session_id'] is not None}))
            for field in log.TOKEN_FIELDS:
                self.assertEqual(summary['tokens'][field],
                                 log.observed([t['tokens'][field] for t in turns])['sum'])

    def test_second_device_is_disjoint_and_child_attribution_has_parent_evidence(self):
        root = Path(__file__).resolve().parents[2]
        first = json.loads((root / 'logs/usage/USAGE-2026-09-24-local.json').read_text())
        second = json.loads((root / 'logs/usage/USAGE-2026-09-25-device.json').read_text())
        first_keys = {(th['thread_id'], t['turn_id'])
                      for th in first['threads'] for t in th['turns']}
        second_turns = {(th['thread_id'], t['turn_id']): t
                        for th in second['threads'] for t in th['turns']}
        self.assertFalse(first_keys & second_turns.keys())
        for th in second['threads']:
            for turn in th['turns']:
                if not th['parent_thread_id'] or not turn['target_session_id']:
                    continue
                evidence = turn['parent_activity']
                self.assertEqual(evidence['thread_id'], th['parent_thread_id'])
                parent = second_turns[evidence['thread_id'], evidence['turn_id']]
                self.assertEqual(parent['target_session_id'], turn['target_session_id'])
                self.assertGreaterEqual(evidence['tool_call_ordinal'], parent['start_ordinal'])
                self.assertLessEqual(evidence['tool_call_ordinal'], parent['end_ordinal'])
                self.assertEqual(evidence['target_agent'], th['agent_path'])


if __name__ == '__main__':
    unittest.main()
