#!/usr/bin/env python3
"""Create, validate and summarize curated nODD session records; no dependencies."""

import argparse
import copy
from collections import Counter
from datetime import datetime, timezone, date
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

SCHEMA_PATH = Path(__file__).with_name('session.schema.json')
TOKEN_FIELDS = ('input_tokens', 'cached_input_tokens', 'output_tokens',
                'reasoning_output_tokens', 'total_tokens')
SUPPORTED = {'$schema', 'title', 'type', 'properties', 'required',
             'additionalProperties', 'items', 'enum', 'const', 'minimum',
             'minLength', 'pattern', 'format'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp(value):
    require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', value)),
            f'expected UTC ISO timestamp ending in Z: {value}')
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def check_schema(schema):
    """Fail closed if a schema edit introduces unsupported validation keywords."""
    require(not (schema.keys() - SUPPORTED),
            f'unsupported schema keywords: {sorted(schema.keys() - SUPPORTED)}')
    if 'format' in schema:
        require(schema['format'] == 'date-time', 'unsupported schema format')
    for child in schema.get('properties', {}).values():
        check_schema(child)
    if 'items' in schema:
        check_schema(schema['items'])


def validate_value(value, schema, location='$'):
    kinds = schema['type']
    kinds = kinds if isinstance(kinds, list) else [kinds]
    matches = {
        'null': value is None, 'object': type(value) is dict,
        'array': type(value) is list, 'string': type(value) is str,
        'integer': type(value) is int,
        'number': type(value) is int or (type(value) is float and math.isfinite(value)),
    }
    require(any(matches.get(kind, False) for kind in kinds), f'{location}: expected {kinds}')
    if 'const' in schema:
        require(value == schema['const'], f'{location}: incorrect constant')
    if 'enum' in schema:
        require(value in schema['enum'], f'{location}: invalid value')
    if value is None:
        return
    if isinstance(value, dict):
        props = schema['properties']
        require(not (set(schema['required']) - value.keys()), f'{location}: missing fields')
        if schema.get('additionalProperties') is False:
            require(not (value.keys() - props.keys()), f'{location}: unknown fields')
        for key, item in value.items():
            validate_value(item, props[key], f'{location}.{key}')
    elif isinstance(value, list):
        for index, item in enumerate(value):
            validate_value(item, schema['items'], f'{location}[{index}]')
    elif isinstance(value, str):
        require(len(value.strip()) >= schema.get('minLength', 0), f'{location}: empty text')
        if 'pattern' in schema:
            require(re.search(schema['pattern'], value) is not None, f'{location}: invalid pattern')
        if schema.get('format') == 'date-time':
            timestamp(value)
    elif 'minimum' in schema:
        require(value >= schema['minimum'], f'{location}: below minimum')


def repo_path(root, value):
    path = Path(value)
    require(not path.is_absolute() and '..' not in path.parts and value != '.',
            f'expected repository-relative path: {value}')
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), f'path escapes repository: {value}')
    return resolved


def validate_record(record, root, path, schema):
    validate_value(record, schema)
    date.fromisoformat(record['session_id'][8:18])
    require(path.stem == record['session_id'], 'filename must match session_id')
    narrative = repo_path(root, record['narrative'])
    require(narrative == path.with_suffix('.md').resolve(), 'narrative must be paired beside JSON')
    require(narrative.is_file() and narrative.read_text().strip(), 'missing or empty narrative')
    if record['completeness'] == 'partial':
        require(record['limitations'], 'partial records need limitations')
    if not record['usage']:
        require(record['limitations'], 'missing usage needs an explanation in limitations')
    start, end = record['started_at'], record['ended_at']
    require(not (record['status'] == 'open' and end is not None), 'open session has ended_at')
    if start and end:
        require(timestamp(end) >= timestamp(start), 'ended_at precedes started_at')
    for field in ('initial_changes', 'changed_files'):
        for name in record['git'][field]:
            repo_path(root, name)
    for usage in record['usage']:
        if any(usage[key] is None for key in TOKEN_FIELDS):
            require(usage['limitations'], 'null token counters need limitations')
        for subset, whole in (('cached_input_tokens', 'input_tokens'),
                              ('reasoning_output_tokens', 'output_tokens')):
            if usage[subset] is not None and usage[whole] is not None:
                require(usage[subset] <= usage[whole], f'{subset} exceeds {whole}')
        if all(usage[key] is not None for key in ('input_tokens', 'output_tokens', 'total_tokens')):
            require(usage['total_tokens'] == usage['input_tokens'] + usage['output_tokens'],
                    'total_tokens must equal input_tokens plus output_tokens')
    for activity in record['activities']:
        if activity['calls'] is not None and activity['failures'] is not None:
            require(activity['failures'] <= activity['calls'], 'failures exceed calls')
    for check in record['checks']:
        if check['status'] == 'PASS':
            require(check['exit_code'] == 0, 'PASS requires observed exit code zero')
        if check['status'] == 'NOT RUN':
            require(check['exit_code'] is None, 'NOT RUN cannot have an exit code')


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=no_duplicates,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f'invalid JSON number: {value}')))


def load_records(root):
    schema = read_json(SCHEMA_PATH)
    check_schema(schema)
    records, ids, turns = [], set(), set()
    for category in ('codex', 'design'):
        directory = root / 'logs' / category
        paths = sorted(directory.glob('*.json'))
        for narrative in directory.glob('SESSION-*.md'):
            require(narrative.with_suffix('.json').is_file(), f'orphan narrative: {narrative.name}')
        for path in paths:
            try:
                repo_path(root, path.relative_to(root).as_posix())
                record = read_json(path)
                validate_record(record, root, path, schema)
                require(record['session_id'] not in ids, 'duplicate session_id')
                ids.add(record['session_id'])
                for usage in record['usage']:
                    key = (usage['client_thread_id'], usage['turn_id'])
                    require(key not in turns, f'duplicate usage turn: {key}')
                    turns.add(key)
                records.append(record)
            except (ValueError, OSError) as error:
                raise ValueError(f'{path.relative_to(root)}: {error}') from error
    return records


def observed(values):
    known = [value for value in values if value is not None]
    return {'sum': sum(known) if known else None, 'known': len(known), 'records': len(values)}


def import_usage(root, session_id, entries, dry_run=False):
    """Append curated, disjoint turns after validating the entire proposed change.

    Exact replays within the target session are harmless. Conflicting counters
    and turns already attributed to another session require explicit correction.
    No cumulative counters, client archives or private transcripts are read.
    """
    records = load_records(root)
    targets = [r for r in records if r['session_id'] == session_id]
    require(len(targets) == 1, 'target session does not exist; create it with new first')
    require(type(entries) is list and entries, 'usage import must be a nonempty JSON array')
    record = copy.deepcopy(targets[0])
    path = repo_path(root, record['narrative']).with_suffix('.json')
    original = path.read_bytes()
    schema = read_json(SCHEMA_PATH)
    existing = {(t['client_thread_id'], t['turn_id']): (r['session_id'], t)
                for r in records for t in r['usage']}
    added, skipped = 0, 0
    for entry in entries:
        validate_value(entry, schema['properties']['usage']['items'])
        require(any(entry[field] is not None for field in TOKEN_FIELDS),
                'usage entry has no observed counters; record missing data in limitations')
        key = (entry['client_thread_id'], entry['turn_id'])
        if key in existing:
            owner, previous = existing[key]
            require(owner == session_id, f'usage turn already belongs to session {owner}')
            require(previous == entry, 'conflicting usage turn; reconcile evidence explicitly')
            skipped += 1
            continue
        record['usage'].append(entry)
        existing[key] = (session_id, entry)
        added += 1
    validate_record(record, root, path, schema)
    if added and not dry_run:
        # Serialize importers across sessions so concurrent attribution cannot
        # insert the same turn twice. Never overwrite an existing lock.
        lock = root / 'logs' / '.usage-import.lock'
        with lock.open('x'):
            try:
                require(load_records(root) == records and path.read_bytes() == original,
                        'logs changed during import; retry against the new records')
                # Replace only after the complete batch passes; a failed import
                # must not leave partially written JSON or partially added turns.
                name = None
                try:
                    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent,
                                                     prefix='.usage-', suffix='.tmp',
                                                     delete=False) as handle:
                        name = handle.name
                        handle.write(json.dumps(record, indent=2) + '\n')
                    os.chmod(name, path.stat().st_mode & 0o777)
                    os.replace(name, path)
                finally:
                    if name is not None:
                        Path(name).unlink(missing_ok=True)
            finally:
                lock.unlink()
    return {'session_id': session_id, 'added': added, 'unchanged': skipped,
            'dry_run': dry_run,
            'tokens': summarize([record])['tokens']}


def summarize(records):
    usage = [turn for record in records for turn in record['usage']]
    activities = {}
    for record in records:
        for activity in record['activities']:
            key = f"{activity['kind']}:{activity['name']}"
            activities.setdefault(key, []).append(activity)
    return {
        'sessions': len(records),
        'closed_sessions': sum(r['status'] == 'closed' for r in records),
        'partial_sessions': sum(r['completeness'] == 'partial' for r in records),
        'sessions_with_usage': sum(bool(r['usage']) for r in records),
        'sessions_without_usage': sum(not r['usage'] for r in records),
        'usage_turns': len(usage),
        'tokens': {key: observed([turn[key] for turn in usage]) for key in TOKEN_FIELDS},
        'models_by_recorded_turn': dict(sorted(Counter(t['model'] or '(unknown)' for t in usage).items())),
        'components_by_session': dict(sorted(Counter(c for r in records for c in set(r['work']['components'])).items())),
        'checks': dict(sorted(Counter(c['status'] for r in records for c in r['checks']).items())),
        'activities': {name: {key: observed([a[key] for a in entries])
                              for key in ('calls', 'failures', 'duration_seconds')}
                       for name, entries in sorted(activities.items())},
    }


def markdown_summary(report):
    lines = ['# Session journal summary', '',
             f"Sessions: {report['sessions']} ({report['closed_sessions']} closed; {report['partial_sessions']} partial).",
             f"Usage coverage: {report['sessions_with_usage']}/{report['sessions']} sessions; {report['usage_turns']} recorded turns.",
             '', '| Token field | Observed sum | Known / recorded turns |', '| --- | ---: | ---: |']
    for name, metric in report['tokens'].items():
        value = 'unknown' if metric['sum'] is None else str(metric['sum'])
        lines.append(f"| {name} | {value} | {metric['known']} / {metric['records']} |")
    lines += ['', 'Cached input and reasoning output are subsets, not additional tokens.',
              'Missing observations are not zero. Coverage does not establish full client telemetry.', '']
    for key in ('models_by_recorded_turn', 'components_by_session', 'checks', 'activities'):
        lines += [f'## {key}', '', '```json', json.dumps(report[key], indent=2, sort_keys=True), '```', '']
    return '\n'.join(lines)


def git(root, *args):
    output = subprocess.check_output(['git', '-C', str(root), *args], text=True)
    return output if '-z' in args else output.strip()


def new_record(root, session_id, title, category, milestone):
    schema = read_json(SCHEMA_PATH)
    check_schema(schema)
    validate_value(session_id, schema['properties']['session_id'])
    date.fromisoformat(session_id[8:18])
    load_records(root)
    for existing in (root / 'logs').glob('*/*.json'):
        require(existing.stem != session_id, 'session ID already exists')
    relative = Path('logs') / category / session_id
    json_path = root / relative.with_suffix('.json')
    md_path = json_path.with_suffix('.md')
    repo_path(root, relative.as_posix())
    require(not json_path.exists() and not md_path.exists(), 'record already exists')
    changed = set()
    for args in (('diff', '--name-only', '-z', 'HEAD'), ('ls-files', '--others', '--exclude-standard', '-z')):
        changed.update(name for name in git(root, *args).split('\0') if name)
    record = {
        'schema_version': 1, 'session_id': session_id, 'title': title,
        'recorded_at': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'started_at': None, 'ended_at': None, 'status': 'open',
        'collection': 'contemporaneous', 'completeness': 'partial',
        'limitations': ['Actual conversation start time, client identity details and token usage have not been recorded.'],
        'client': {'name': 'unspecified', 'version': None, 'thread_id': None},
        'git': {'start_commit': git(root, 'rev-parse', 'HEAD'),
                'branch': git(root, 'branch', '--show-current') or None,
                'initial_changes': sorted(changed), 'result_commits': [], 'changed_files': []},
        'work': {'milestone': milestone, 'components': [], 'related_ids': []},
        'narrative': relative.with_suffix('.md').as_posix(),
        'activities': [], 'usage': [], 'checks': [],
    }
    validate_value(record, schema)
    template = (Path(__file__).resolve().parents[2] / 'logs' / 'TEMPLATE.md').read_text()
    narrative = template.replace('<session ID>', session_id).replace('<title>', title)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also protects against a concurrent writer.
    with md_path.open('x') as handle:
        handle.write(narrative)
    with json_path.open('x') as handle:
        handle.write(json.dumps(record, indent=2) + '\n')
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('new', help='create paired curated session records')
    create.add_argument('--id', required=True)
    create.add_argument('--title', required=True)
    create.add_argument('--category', choices=('codex', 'design'), default='codex')
    create.add_argument('--milestone', default='M0')
    commands.add_parser('validate', help='validate all session records')
    summary = commands.add_parser('summary', help='report observed usage and coverage')
    summary.add_argument('--format', choices=('json', 'markdown'), default='markdown')
    summary.add_argument('--milestone')
    ingest = commands.add_parser('import-usage', help='import curated per-turn usage JSON; no client archives')
    ingest.add_argument('--id', required=True, help='existing project session ID')
    ingest.add_argument('--file', type=Path, required=True, help='JSON array of usage entries')
    ingest.add_argument('--dry-run', action='store_true', help='validate and preview without writing')
    usage = commands.add_parser('record-usage', help='record one client-reported, disjoint turn')
    usage.add_argument('--id', required=True, help='existing project session ID')
    usage.add_argument('--thread-id', required=True)
    usage.add_argument('--turn-id', required=True)
    usage.add_argument('--model', help='reported execution model, if available')
    usage.add_argument('--source', required=True, help='curated evidence description; no secrets')
    usage.add_argument('--limitation', action='append', default=[])
    usage.add_argument('--dry-run', action='store_true')
    for field in TOKEN_FIELDS:
        usage.add_argument('--' + field.replace('_', '-'), type=int)
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    try:
        if args.command == 'new':
            record = new_record(root, args.id, args.title, args.category, args.milestone)
            print(f"Created {record['narrative']} and paired JSON; complete and review before committing.")
        elif args.command in ('import-usage', 'record-usage'):
            if args.command == 'import-usage':
                entries = read_json(args.file)
            else:
                entries = [{
                    'client_thread_id': args.thread_id, 'turn_id': args.turn_id,
                    'model': args.model, 'source': args.source,
                    'limitations': args.limitation,
                    **{field: getattr(args, field) for field in TOKEN_FIELDS},
                }]
            print(json.dumps(import_usage(root, args.id, entries, args.dry_run), indent=2))
        else:
            records = load_records(root)
            if args.command == 'validate':
                print(f'Validated {len(records)} session records.')
            else:
                selected = [r for r in records if not args.milestone or r['work']['milestone'] == args.milestone]
                report = summarize(selected)
                print(json.dumps(report, indent=2, sort_keys=True) if args.format == 'json' else markdown_summary(report))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
