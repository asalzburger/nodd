"""All model names, token counts and IDs below are synthetic test fixtures."""

import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import session_log as log


class SessionLoggingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / 'logs' / 'codex'
        self.directory.mkdir(parents=True)
        self.path = self.directory / 'SESSION-2026-09-15-test.json'
        self.path.with_suffix('.md').write_text('# Synthetic test session\n')
        self.record = {
            'schema_version': 1, 'session_id': self.path.stem, 'title': 'Synthetic test fixture',
            'recorded_at': '2026-09-15T12:00:00Z', 'started_at': None, 'ended_at': None,
            'status': 'closed', 'collection': 'retrospective', 'completeness': 'partial',
            'limitations': ['Synthetic fixture: no actual client observations.'],
            'client': {'name': 'test-client', 'version': None, 'thread_id': None},
            'git': {'start_commit': 'a' * 40, 'branch': 'test', 'initial_changes': [],
                    'result_commits': [], 'changed_files': []},
            'work': {'milestone': 'M0', 'components': ['test-component'], 'related_ids': []},
            'narrative': self.path.with_suffix('.md').relative_to(self.root).as_posix(),
            'activities': [], 'usage': [], 'checks': [],
        }
        self.schema = log.read_json(log.SCHEMA_PATH)

    def save(self):
        self.path.write_text(json.dumps(self.record))

    def validate(self):
        log.validate_record(self.record, self.root, self.path, self.schema)

    def turn(self):
        return {'client_thread_id': 'test-thread', 'turn_id': 'test-turn', 'model': 'test-model',
                'source': 'Synthetic test values, not observed usage.', 'limitations': [],
                'input_tokens': 100, 'cached_input_tokens': 80, 'output_tokens': 20,
                'reasoning_output_tokens': 10, 'total_tokens': 120}

    def test_unknown_is_not_zero(self):
        self.validate()
        report = log.summarize([self.record])
        self.assertIsNone(report['tokens']['input_tokens']['sum'])
        self.assertEqual(report['sessions_with_usage'], 0)
        self.assertIn('unknown', log.markdown_summary(report))

    def test_subsets_are_not_double_counted(self):
        self.record['usage'] = [self.turn()]
        self.validate()
        report = log.summarize([self.record])
        self.assertEqual(report['tokens']['total_tokens']['sum'], 120)
        self.assertEqual(report['models_by_recorded_turn'], {'test-model': 1})

    def test_zero_and_partial_coverage(self):
        turn = self.turn()
        for field in log.TOKEN_FIELDS:
            turn[field] = 0
        self.record['usage'] = [turn]
        other = copy.deepcopy(self.record)
        other['usage'][0]['input_tokens'] = None
        report = log.summarize([self.record, other])
        self.assertEqual(report['tokens']['input_tokens'], {'sum': 0, 'known': 1, 'records': 2})

    def test_invalid_counters(self):
        for field, value in [('input_tokens', -1), ('input_tokens', True),
                             ('cached_input_tokens', 101), ('reasoning_output_tokens', 21),
                             ('total_tokens', 210), ('output_tokens', 1.5)]:
            with self.subTest(field=field, value=value):
                turn = self.turn()
                turn[field] = value
                self.record['usage'] = [turn]
                with self.assertRaises(ValueError):
                    self.validate()

    def test_null_counters_need_reason(self):
        turn = self.turn()
        turn['reasoning_output_tokens'] = None
        self.record['usage'] = [turn]
        with self.assertRaises(ValueError):
            self.validate()
        turn['limitations'] = ['Test client does not expose reasoning usage.']
        self.validate()

    def test_duplicate_turns_across_sessions(self):
        self.record['usage'] = [self.turn()]
        self.save()
        other = copy.deepcopy(self.record)
        other['session_id'] = 'SESSION-2026-09-15-other'
        other_path = self.directory / (other['session_id'] + '.json')
        other['narrative'] = other_path.with_suffix('.md').relative_to(self.root).as_posix()
        other_path.with_suffix('.md').write_text('# Another synthetic test record\n')
        other_path.write_text(json.dumps(other))
        with self.assertRaisesRegex(ValueError, 'duplicate usage turn'):
            log.load_records(self.root)

    def test_usage_import_preview_write_and_replay(self):
        self.save()
        original = self.path.read_bytes()
        narrative = self.path.with_suffix('.md').read_bytes()
        result = log.import_usage(self.root, self.path.stem, [self.turn()], dry_run=True)
        self.assertEqual(result['added'], 1)
        self.assertEqual(result['tokens']['input_tokens']['sum'], 100)
        self.assertEqual(self.path.read_bytes(), original)
        result = log.import_usage(self.root, self.path.stem, [self.turn()])
        self.assertEqual(result['added'], 1)
        imported = self.path.read_bytes()
        result = log.import_usage(self.root, self.path.stem, [self.turn()])
        self.assertEqual((result['added'], result['unchanged']), (0, 1))
        self.assertEqual(self.path.read_bytes(), imported)
        self.assertEqual(self.path.with_suffix('.md').read_bytes(), narrative)
        self.assertEqual(log.load_records(self.root)[0]['usage'], [self.turn()])

    def test_usage_import_failures_leave_files_untouched(self):
        self.save()
        original = self.path.read_bytes()
        invalid = self.turn()
        invalid['turn_id'] = 'test-invalid'
        invalid['total_tokens'] = 999  # Deliberately inconsistent synthetic total.
        for entries in ([], {}, [self.turn(), invalid], [{'private_text': 'test'}]):
            with self.subTest(entries=entries):
                with self.assertRaises(ValueError):
                    log.import_usage(self.root, self.path.stem, entries)
                self.assertEqual(self.path.read_bytes(), original)
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            log.import_usage(self.root, 'SESSION-2026-09-15-missing', [self.turn()])

    def test_usage_import_rejects_conflicts_and_other_session_attribution(self):
        self.record['usage'] = [self.turn()]
        self.save()
        original = self.path.read_bytes()
        conflict = self.turn()
        conflict['source'] = 'Different synthetic evidence needs reconciliation.'
        with self.assertRaisesRegex(ValueError, 'conflicting usage'):
            log.import_usage(self.root, self.path.stem, [conflict])
        other = copy.deepcopy(self.record)
        other['session_id'] = 'SESSION-2026-09-15-other'
        other['usage'] = []
        other_path = self.directory / (other['session_id'] + '.json')
        other['narrative'] = other_path.with_suffix('.md').relative_to(self.root).as_posix()
        other_path.with_suffix('.md').write_text('# Synthetic other session\n')
        other_path.write_text(json.dumps(other))
        with self.assertRaisesRegex(ValueError, 'already belongs'):
            log.import_usage(self.root, other['session_id'], [self.turn()])
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(log.read_json(other_path)['usage'], [])

    def test_usage_import_missing_fields_and_zero(self):
        self.save()
        turn = self.turn()
        for key in log.TOKEN_FIELDS:
            turn[key] = None
        turn['limitations'] = ['Synthetic missing measurements.']
        with self.assertRaisesRegex(ValueError, 'no observed counters'):
            log.import_usage(self.root, self.path.stem, [turn])
        turn['input_tokens'] = 0
        result = log.import_usage(self.root, self.path.stem, [turn])
        self.assertEqual(result['tokens']['input_tokens']['sum'], 0)
        self.assertIsNone(result['tokens']['output_tokens']['sum'])

    def test_usage_import_lock_preserves_existing_writer(self):
        self.save()
        lock = self.root / 'logs' / '.usage-import.lock'
        lock.write_text('Synthetic active writer')
        with self.assertRaises(FileExistsError):
            log.import_usage(self.root, self.path.stem, [self.turn()])
        self.assertEqual(lock.read_text(), 'Synthetic active writer')
        self.assertEqual(log.read_json(self.path)['usage'], [])

    def test_usage_import_write_failure_preserves_record_and_cleans_lock(self):
        self.save()
        original = self.path.read_bytes()
        with patch.object(log.os, 'replace', side_effect=OSError('Synthetic write failure')):
            with self.assertRaisesRegex(OSError, 'Synthetic write failure'):
                log.import_usage(self.root, self.path.stem, [self.turn()])
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse((self.root / 'logs' / '.usage-import.lock').exists())
        self.assertEqual(list(self.directory.glob('.usage-*.tmp')), [])

    def test_usage_cli_import_and_record(self):
        self.save()
        cli = [sys.executable, '-B', str(Path(log.__file__).resolve()), '--repo', str(self.root)]
        exported = self.root / 'usage-test.json'
        exported.write_text(json.dumps([self.turn()]))
        result = subprocess.run(cli + ['import-usage', '--id', self.path.stem,
                                      '--file', str(exported)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(cli + ['record-usage', '--id', self.path.stem,
                                      '--thread-id', 'test-thread', '--turn-id', 'test-second',
                                      '--source', 'Synthetic client fixture', '--input-tokens', '50',
                                      '--output-tokens', '5', '--total-tokens', '55',
                                      '--limitation', 'Synthetic missing subset counters.'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = log.summarize(log.load_records(self.root))
        self.assertEqual(report['tokens']['input_tokens']['sum'], 150)
        self.assertEqual(report['tokens']['output_tokens']['sum'], 25)
        self.assertEqual(report['tokens']['total_tokens']['sum'], 175)
        self.assertEqual(report['sessions_without_usage'], 0)

    def test_duplicate_session_ids_across_categories(self):
        self.save()
        directory = self.root / 'logs' / 'design'
        directory.mkdir()
        other = copy.deepcopy(self.record)
        other['narrative'] = 'logs/design/' + self.path.with_suffix('.md').name
        (directory / self.path.name).write_text(json.dumps(other))
        (directory / self.path.with_suffix('.md').name).write_text('# Test duplicate\n')
        with self.assertRaisesRegex(ValueError, 'duplicate session_id'):
            log.load_records(self.root)

    def test_missing_unknown_and_duplicate_json_fields(self):
        for transform in (lambda r: r.pop('usage'), lambda r: r.update(raw_rollout='forbidden')):
            original = copy.deepcopy(self.record)
            transform(self.record)
            with self.assertRaises(ValueError):
                self.validate()
            self.record = original
        self.path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            log.read_json(self.path)
        self.path.write_text('{"value": NaN}')
        with self.assertRaisesRegex(ValueError, 'invalid JSON number'):
            log.read_json(self.path)

    def test_schema_changes_fail_closed(self):
        log.check_schema(self.schema)
        self.schema['properties']['usage']['uniqueItems'] = True
        with self.assertRaisesRegex(ValueError, 'unsupported schema'):
            log.check_schema(self.schema)

    def test_missing_and_escaping_narrative(self):
        for name in ('../outside.md', '/tmp/outside.md', 'logs/codex/missing.md'):
            self.record['narrative'] = name
            with self.assertRaises(ValueError):
                self.validate()
        outside = self.root.parent / 'outside-test-narrative.md'
        self.path.with_suffix('.md').unlink()
        self.path.with_suffix('.md').symlink_to(outside)
        self.record['narrative'] = 'logs/codex/' + self.path.with_suffix('.md').name
        with self.assertRaisesRegex(ValueError, 'escapes repository'):
            self.validate()

    def test_invalid_date_and_time_order(self):
        self.record['recorded_at'] = '2026-02-30T00:00:00Z'
        with self.assertRaises(ValueError):
            self.validate()
        self.record['recorded_at'] = '2026-09-15T12:00:00Z'
        self.record['started_at'] = '2026-09-15T13:00:00Z'
        self.record['ended_at'] = '2026-09-15T12:00:00Z'
        with self.assertRaisesRegex(ValueError, 'precedes'):
            self.validate()

    def test_failed_and_unrun_checks(self):
        self.record['checks'] = [{'command': 'synthetic-test', 'status': 'PASS',
                                  'exit_code': 1, 'result': 'Synthetic failure'}]
        with self.assertRaises(ValueError):
            self.validate()
        self.record['checks'][0]['status'] = 'FAIL'
        self.validate()
        self.record['checks'][0]['status'] = 'NOT RUN'
        with self.assertRaises(ValueError):
            self.validate()

    def test_cli_create_validate_summary_and_no_overwrite(self):
        self.path.with_suffix('.md').unlink()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit',
                        '--allow-empty', '-qm', 'synthetic test baseline'], check=True)
        (self.root / 'user-change.txt').write_text('Preserve this synthetic user file.\n')
        cli = [sys.executable, '-B', str(Path(log.__file__).resolve()), '--repo', str(self.root)]
        create = cli + ['new', '--id', self.path.stem, '--title', 'CLI synthetic test']
        result = subprocess.run(create, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        original = self.path.read_bytes()
        created = json.loads(original)
        self.assertIn('user-change.txt', created['git']['initial_changes'])
        self.assertEqual(subprocess.run(create, capture_output=True).returncode, 1)
        self.assertEqual(self.path.read_bytes(), original)
        result = subprocess.run(cli + ['validate'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(cli + ['summary', '--format', 'json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['sessions'], 1)
        result = subprocess.run(cli + ['summary', '--format', 'json', '--milestone', 'M1'], capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)['sessions'], 0)
        self.path.write_text('{}')
        result = subprocess.run(cli + ['summary', '--milestone', 'M1'], capture_output=True)
        self.assertEqual(result.returncode, 1)  # Invalid unselected records still fail.

    def test_orphan_narrative_rejected(self):
        with self.assertRaisesRegex(ValueError, 'orphan narrative'):
            log.load_records(self.root)

    def test_repository_documentation_links(self):
        repository = Path(log.__file__).resolve().parents[2]
        for path in sorted(repository.rglob('*.md')):
            if '.git' in path.relative_to(repository).parts:
                continue
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                with self.subTest(document=str(path.relative_to(repository)), target=target):
                    self.assertTrue((path.parent / target.split('#', 1)[0]).exists())


if __name__ == '__main__':
    unittest.main()
