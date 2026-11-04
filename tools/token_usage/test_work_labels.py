"""Work labels must reconcile to the same disjoint counters as each graph step."""

import json
import shutil
import unittest

import build
import test_build as fixtures


class WorkLabelTests(unittest.TestCase):
    setUp = fixtures.UsageTests.setUp
    add_record = fixtures.UsageTests.add_record

    def test_same_day_sessions_reconcile_without_replayed_inventory(self):
        self.add_record('SESSION-2026-09-16-two', 'turn-two', 200, 40, 180, 10,
                        '2026-09-16T18:00:00Z')
        shutil.copy(self.root / 'logs/usage/turn-one.json', self.root / 'logs/usage/replay.json')
        data = build.collect(self.root)
        point = data['series'][0]
        self.assertEqual(point['step'], 1)
        self.assertEqual(point['turns'], 2)
        self.assertEqual(len(point['work']), 2)
        self.assertEqual(point['work'][0]['session_id'], 'SESSION-2026-09-16-two')
        self.assertIn('+ 1 more session', build.work_label(point))
        for field in build.FIELDS:
            self.assertEqual(sum(w['tokens'][field]['sum'] for w in point['work']), point['daily'][field]['sum'])
        self.assertEqual(data['summary']['tokens']['total_tokens']['sum'], 360)

    def test_one_session_across_days_uses_only_each_days_turns(self):
        path = self.add_record('SESSION-2026-09-17-two', 'turn-two', 200, 40, 180, 10,
                               '2026-09-17T18:00:00Z')
        first = self.root / 'logs/codex/SESSION-2026-09-16-one.json'
        owner, other = json.loads(first.read_text()), json.loads(path.read_text())
        owner['usage'].extend(other['usage'])
        other['usage'] = []
        first.write_text(json.dumps(owner))
        path.write_text(json.dumps(other))
        points = build.collect(self.root)['series']
        self.assertEqual([p['work'][0]['tokens']['total_tokens']['sum'] for p in points], [120, 240])
        self.assertEqual([p['work'][0]['turns'] for p in points], [1, 1])
        self.assertEqual([p['step'] for p in points], [1, 2])

    def test_unknown_and_undated_usage_do_not_gain_fabricated_labels_or_totals(self):
        self.add_record('SESSION-2026-09-17-two', 'unknown-output', 200, None, 180, None,
                        '2026-09-17T18:00:00Z')
        self.add_record('SESSION-2026-09-18-undated', 'undated', 300, 60, 200, 5, None)
        data = build.collect(self.root)
        self.assertEqual(len(data['series']), 2)
        point = data['series'][1]
        self.assertIsNone(point['work'][0]['tokens']['total_tokens']['sum'])
        self.assertEqual(point['work'][0]['tokens']['input_tokens']['sum'], 200)
        self.assertEqual(data['undated_turns'], 1)
        self.assertEqual(data['undated_tokens']['total_tokens']['sum'], 360)
        data['metadata'] = {'source_commit': 'a'*40}
        html = build.work_breakdown(data)
        self.assertIn('0/1 turns measured', html)
        self.assertNotIn('usage-step-2026-09-18', html)

    def test_labels_and_links_are_escaped_and_shared_prs_do_not_split_tokens(self):
        path = self.root / 'logs/codex/SESSION-2026-09-16-one.json'
        record = json.loads(path.read_text())
        record['title'] = '<script>literal title</script> & tracker'
        record['work']['related_ids'] = ['PR-96', 'PR96', 'PR #97', 'ACTS-PR-4']
        path.write_text(json.dumps(record))
        data = build.collect(self.root)
        work = data['series'][0]['work'][0]
        self.assertEqual(work['prs'], [96, 97])
        self.assertEqual(work['tokens']['total_tokens']['sum'], 120)
        self.assertEqual(set(work), {'session_id', 'title', 'narrative', 'prs', 'turns', 'tokens'})
        output = self.root / '_site/work-labels'
        build.build(self.root, output, '2026-10-30T12:00:00Z')
        html = (output / 'index.html').read_text()
        self.assertNotIn('<script>literal', html)
        self.assertIn('&lt;script&gt;literal title', html)
        self.assertIn('PR #96</a>', html)
        self.assertEqual(html.count('href="#usage-step-2026-09-16"'), 3)
        self.assertEqual(html.count('id="usage-step-2026-09-16"'), 1)

    def test_real_work_subtotals_cover_every_step_and_counter(self):
        data = build.collect(build.ROOT)
        for step, point in enumerate(data['series'], 1):
            self.assertEqual(point['step'], step)
            self.assertTrue(point['work'])
            self.assertEqual(sum(item['turns'] for item in point['work']), point['turns'])
            for field in build.FIELDS:
                measured = [item['tokens'][field]['sum'] for item in point['work']
                            if item['tokens'][field]['sum'] is not None]
                self.assertEqual(sum(measured) if measured else None, point['daily'][field]['sum'])
                self.assertEqual(sum(item['tokens'][field]['known'] for item in point['work']), point['daily'][field]['known'])


if __name__ == '__main__':
    unittest.main()
