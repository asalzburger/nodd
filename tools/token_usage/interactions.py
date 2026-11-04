"""Publish a narrow, validated projection of the checked-in PR interaction ledger."""

from datetime import datetime, timezone
import importlib.util
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote, urlsplit

REPOSITORY = 'https://github.com/asalzburger/nodd'
GROUPS = (
    ('recorded', 'Recorded messages',
     'User-visible messages grouped by recorded turn. Turn times are not individual message timestamps.'),
    ('github', 'GitHub discussion',
     'Public PR and linked-issue discussion at the captured revision and date.'),
    ('notes', 'Session notes',
     'Selected journal excerpts, assignments and outcomes; some summarize multiple inputs.'))


def ledger_module():
    path = Path(__file__).resolve().parents[1] / 'interactions' / 'ledger.py'
    spec = importlib.util.spec_from_file_location('pages_interaction_ledger', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_link(source, revision, fallback):
    """Only known public GitHub sources or safe repository paths become links."""
    if isinstance(source, str):
        parsed = urlsplit(source)
        if (parsed.scheme == 'https' and parsed.netloc == 'github.com'
                and (parsed.path.startswith('/asalzburger/nodd/')
                     or parsed.path.startswith('/user-attachments/'))):
            return source
        path, _, fragment = source.partition('#')
        parts = PurePosixPath(path).parts
        if (parts and parts[0] in {'logs', 'interactions', 'tools', 'docs', 'project'}
                and not path.startswith('/') and '..' not in parts
                and '\\' not in path and ':' not in path):
            return REPOSITORY + '/blob/' + revision + '/' + quote(path, safe='/') + (
                '#' + quote(fragment, safe='-_.') if fragment else '')
    return REPOSITORY + '/blob/' + revision + '/' + fallback


def message(event, category, revision, fallback):
    """No arbitrary source fields, client state or numeric token counters."""
    return {
        'id': event['id'], 'type': event['type'], 'direction': event['direction'],
        'actor': event['actor'], 'text': event['text'],
        'source_url': source_link(event['source'], revision, fallback),
        'source_label': {'github': 'GitHub source', 'recorded': 'Recorded message',
                         'notes': 'Session source'}[category],
        'reply_to': event['in_reply_to'], 'model': event['model'],
        'roles': list(event['agent_roles']),
        'timestamp': event.get('timestamp') if event['type'] != 'upload' else None,
    }


def turn_time(value):
    if type(value) in (int, float):
        return datetime.fromtimestamp(value, timezone.utc).isoformat().replace('+00:00', 'Z')
    return None


def project(root, snapshot, metadata, records, ledger):
    pr = snapshot['github']['pull_request']
    derived = snapshot['derived']
    revision = metadata['source_commit']
    fallback = f'interactions/pr-{pr["number"]:04d}.json'
    titles = {r['session_id']: r['title'] for r in records}
    for journal in derived['journals']:
        if journal['snapshot']:
            source = ledger.logger.read_json(ledger.logger.repo_path(root, journal['snapshot']))
            titles[source['session_id']] = source['title']
    visible = {}
    for item in derived['visible_sources']:
        turn = ledger.logger.read_json(ledger.logger.repo_path(root, item['path']))
        visible[item['path']] = {
            'id': 'turn:' + turn['thread_id'] + ':' + turn['turn_id'],
            'label': 'Recorded turn', 'timestamp': turn_time(turn['started_at'])}
    threads = {category: {} for category, _, _ in GROUPS}
    for event in derived['events']:
        if event['id'].startswith('github:'):
            category, key = 'github', 'github'
            info = {'id': key, 'label': 'PR and linked-issue discussion', 'timestamp': None}
        elif event['id'].startswith('codex-message:'):
            category, key = 'recorded', event['source']
            info = visible.get(key, {'id': key, 'label': 'Additional task-matched messages',
                                     'timestamp': None})
        else:
            category = 'notes'
            key = (event['token_accounts'] or ['notes'])[0]
            info = {'id': key, 'label': titles.get(key, 'Curated session evidence'), 'timestamp': None}
        thread = threads[category].setdefault(key, {**info, 'messages': []})
        thread['messages'].append(message(event, category, revision, fallback))
    groups = []
    for category, label, description in GROUPS:
        items = list(threads[category].values())
        if not items:
            continue
        if category == 'recorded':
            # Known turn starts can order turns; unknown times retain their
            # source order after them. Individual timestamps are never invented.
            items.sort(key=lambda t: (t['timestamp'] is None, t['timestamp'] or ''))
        groups.append({'id': category, 'label': label, 'description': description, 'threads': items})
    active = {e['actor'] for e in derived['events']}
    parties = [{k: p[k] for k in ('id', 'name', 'kind')}
               for p in derived['parties'] if p['id'] in active]
    agents, seen = [], set()
    for agent in derived['agents']:
        key = (agent['id'], agent['name'], agent['role'])
        if key not in seen:
            seen.add(key)
            agents.append({k: agent[k] for k in ('id', 'name', 'role', 'models')})
    tools = {}
    for category, entries in derived['tools'].items():
        unique = {}
        for entry in entries:
            key = (entry['name'], entry['version'])
            unique.setdefault(key, {'name': entry['name'], 'version': entry['version'],
                                    'source': source_link(entry['source'], revision, fallback)})
        tools[category] = list(unique.values())
    accounts = [{'id': a['id'], 'status': a['status'], 'turn_count': len(a['turns']),
                 'source': source_link(a['record'], revision, fallback)}
                for a in derived['token_accounts']]
    missing = len(derived['coverage']['unrecovered_account_turns'])
    detail = {
        'number': pr['number'], 'title': pr['title'], 'url': pr['url'], 'state': pr['state'],
        'captured_at': snapshot['github']['captured_at'], 'parties': parties,
        'agents': agents, 'tools': tools, 'accounts': accounts, 'groups': groups,
        'coverage': {'missing_turns': missing,
                     'recovered_turns': derived['coverage']['recovered_visible_turns'],
                     'note': 'Selected historical evidence; missing history and unreported models remain unknown. '
                     'Token accounts are references to broader sessions, not additive PR totals.'}}
    index = {k: detail[k] for k in ('number', 'title', 'state', 'url', 'captured_at')}
    index.update({'record_count': sum(len(t['messages']) for g in groups for t in g['threads']),
                  'parties': sorted({p['name'] for p in parties}), 'missing_turns': missing,
                  'sources': [{'id': g['id'], 'label': g['label'],
                               'count': sum(len(t['messages']) for t in g['threads'])} for g in groups],
                  'data': f'interactions/pr-{pr["number"]:04d}.json'})
    return index, detail


def collect(root, metadata):
    directory = root / 'interactions'
    if not directory.is_dir():
        raise ValueError('Missing interaction directory for the PR conversation view')
    ledger = ledger_module()
    records = ledger.logger.load_records(root)
    index, details = [], {}
    for path in sorted(directory.glob('pr-*.json')):
        if not re.fullmatch(r'pr-[0-9]+\.json', path.name):
            raise ValueError('Invalid interaction filename')
        snapshot = ledger.logger.read_json(path)
        ledger.validate_snapshot(snapshot, int(path.stem.removeprefix('pr-')))
        ledger.validate_derived(root, snapshot, records)
        item, detail = project(root, snapshot, metadata, records, ledger)
        index.append(item)
        details[item['data']] = detail
    index.sort(key=lambda item: item['number'], reverse=True)
    return {'schema_version': 1, 'metadata': metadata, 'pull_requests': index}, details
