"""Count retained interaction evidence once, without inferring missing people or work."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

import interactions

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {'recorded': 'Recorded messages', 'github': 'GitHub discussion',
           'notes': 'Journal excerpts', 'curated': 'Additional curated records'}
BUCKETS = ('human', 'agent_response', 'published_response', 'agent_prompt', 'unresolved')
WORD = re.compile(r"\w+(?:['’]\w+)*", re.UNICODE)


def word_count(text):
    """Unicode word runs, with internal apostrophes; count the retained text literally."""
    return len(WORD.findall(text))


def source_kind(event):
    if event['id'].startswith('github:'):
        return 'github'
    if event['id'].startswith(('codex-message:', 'visible-unmeasured:')):
        return 'recorded'
    if event['id'].startswith('journal:'):
        return 'notes'
    return 'curated'


def collect(root, metadata=None):
    """Validate canonical inputs, then deduplicate references by their exposed IDs.

    Journal excerpts and manually curated records may repeat or paraphrase actual
    messages. They get separate subtotals and never inflate the message headline.
    Conflicting actor kinds on inherited messages remain unresolved. Conflicting
    message text/type or per-turn tool counts fail instead of picking a PR copy.
    """
    root = Path(root)
    ledger = interactions.ledger_module()
    records = ledger.logger.load_records(root)
    snapshots = []
    for path in sorted((root / 'interactions').glob('pr-*.json')):
        snapshot = ledger.logger.read_json(path)
        ledger.validate_snapshot(snapshot, int(path.stem.removeprefix('pr-')))
        ledger.validate_derived(root, snapshot, records)
        snapshots.append(snapshot)
    events = {}
    threads, children, visible_turns, account_turns = set(), set(), {}, set()
    humans, publishing, unknown_humans, assignments = set(), set(), set(), set()
    canonical_ids = {r['session_id'] for r in records}
    pinned_ids, linked_ids = set(), set()
    for record in records:
        if record['client']['thread_id']:
            threads.add(record['client']['thread_id'])
        for usage in record['usage']:
            key = usage['client_thread_id'], usage['turn_id']
            account_turns.add(key)
            threads.add(key[0])
    captures = []
    event_references = 0
    summary_ids, upload_ids = set(), set()
    for snapshot in snapshots:
        derived = snapshot['derived']
        bodyless_reviews = {'github:' + comment['url'] for comment in snapshot['github']['comments']
                            if comment.get('review') and not comment.get('body')}
        captures.append(snapshot['github']['captured_at'])
        parties = {p['id']: p for p in derived['parties']}
        for agent in derived['agents']:
            if agent['thread_id']:
                threads.add(agent['thread_id'])
                if agent['role'] == 'subagent':
                    children.add(agent['thread_id'])
            elif agent['role'] == 'reported_specialist_assignment':
                assignments.add(agent['id'])
        for account in derived['token_accounts']:
            linked_ids.add(account['id'])
            if account['id'] not in canonical_ids:
                pinned_ids.add(account['id'])
            for turn in account['turns']:
                key = turn['client_thread_id'], turn['turn_id']
                threads.add(key[0])
                account_turns.add(key)
        for source in derived['visible_sources']:
            turn = ledger.logger.read_json(ledger.logger.repo_path(root, source['path']))
            key = turn['thread_id'], turn['turn_id']
            tools = sorted((t['name'], t['calls'], t['failures']) for t in turn['native_tools'])
            if key in visible_turns and visible_turns[key] != tools:
                raise ValueError('Conflicting operation counts for a repeated visible turn')
            visible_turns[key] = tools
            if turn.get('parent_thread_id'):
                threads.add(turn['parent_thread_id'])
                children.add(turn['thread_id'])
        for event in derived['events']:
            event_references += 1
            identifier = event['id']
            if event['type'] == 'upload':
                upload_ids.add(identifier)
                continue
            if event.get('content_kind') == 'reference_summary':
                summary_ids.add(identifier)
                continue
            party = parties.get(event['actor'], {})
            kind = party.get('kind', 'unknown')
            if kind == 'human':
                if event['actor'].startswith('unknown:'):
                    unknown_humans.add(event['actor'])
                else:
                    humans.add(party['name'])
            elif kind == 'account':
                publishing.add(party['name'])
            # Review decision labels (APPROVED, etc.) are event metadata. They
            # remain interactions but are not words written by the reviewer.
            word_text = '' if identifier in bodyless_reviews else event['text']
            item = events.setdefault(identifier, {'text': event['text'], 'word_text': word_text, 'type': event['type'],
                                                  'source': source_kind(event), 'kinds': set()})
            if (item['text'], item['word_text'], item['type'], item['source']) != (
                    event['text'], word_text, event['type'], source_kind(event)):
                raise ValueError('Conflicting text/type for repeated interaction ID: ' + identifier)
            item['kinds'].add(kind)

    sources = {name: {'id': name, 'label': label, 'events': 0,
                      'words': dict.fromkeys(BUCKETS, 0), 'types': Counter(),
                      'ambiguous_events': 0} for name, label in SOURCES.items()}
    for item in events.values():
        row = sources[item['source']]
        kinds = item['kinds']
        # The publishing account's operator is unknown, even when it posts an
        # @codex input. A parent's assignment is not a human-authored prompt.
        bucket = ('human' if kinds == {'human'} else
                  'agent_prompt' if kinds == {'agent'} and item['type'] == 'prompt' else
                  'agent_response' if kinds == {'agent'} and item['type'] == 'response' else
                  'published_response' if kinds == {'account'} and item['type'] == 'response'
                  else 'unresolved')
        text = '' if item['word_text'] == '(empty review)' else item['word_text']
        row['events'] += 1
        row['types'][item['type']] += 1
        row['words'][bucket] += word_count(text)
        row['ambiguous_events'] += len(kinds) > 1
    primary = [sources['recorded'], sources['github']]
    words = {bucket: sum(row['words'][bucket] for row in primary) for bucket in BUCKETS}
    words['responses'] = words['agent_response'] + words['published_response']
    operations = Counter()
    failures = Counter()
    for tools in visible_turns.values():
        for name, calls, failed in tools:
            operations[name] += calls
            failures[name] += failed
    tracking_path = root / 'project/tracking.json'
    tasks = ledger.logger.read_json(tracking_path)['tasks'] if tracking_path.exists() else None
    task_states = Counter(task['state'] for task in tasks) if tasks is not None else {}
    missing = account_turns - visible_turns.keys()
    return {
        'schema_version': 1, 'metadata': metadata or {},
        'scope': 'Evidence retained in this source revision, including snapshots of open/closed PRs '
                 'and explicitly pinned branch references; no live or private-client collection.',
        'words': words, 'sources': list(sources.values()),
        'interactions': {
            'message_events': sum(row['events'] for row in primary),
            'types': dict(sum((row['types'] for row in primary), Counter())),
            'all_unique_text_records': len(events), 'raw_event_references': event_references,
            'duplicate_references_removed': event_references - len(events) - len(upload_ids) - len(summary_ids),
            'uploads': len(upload_ids), 'generated_summaries_excluded': len(summary_ids),
            'review_decisions_without_text': sum(item['type'] == 'review' and not item['word_text']
                                                for item in events.values()),
            'visible_turns': len(visible_turns), 'account_turns': len(account_turns),
            'canonical_usage_turns': sum(len(r['usage']) for r in records),
        },
        'work': {
            'canonical_sessions': len(records),
            'session_states': dict(Counter(r['status'] for r in records)),
            'sessions_with_usage': sum(bool(r['usage']) for r in records),
            'sessions_without_client_thread': sum(r['client']['thread_id'] is None for r in records),
            'pr_records': len(snapshots), 'canonical_sessions_linked_to_prs': len(linked_ids & canonical_ids),
            'pinned_branch_only_sessions': len(pinned_ids),
            'tracked_tasks': len(tasks) if tasks is not None else None,
            'tracked_task_states': dict(task_states),
        },
        'participants': {
            'named_human_accounts': sorted(humans), 'named_human_account_count': len(humans),
            'unnamed_human_placeholders': len(unknown_humans),
            'publishing_accounts': sorted(publishing),
            'exposed_agent_threads': len(threads), 'exposed_child_threads': len(children),
            'unidentified_specialist_assignments': len(assignments),
            'distinct_humans': None, 'physical_agent_processes': None,
        },
        'tools': {
            'visible_turns': len(visible_turns), 'operation_calls': sum(operations.values()),
            'operations': [{'name': name, 'calls': calls, 'failures': failures[name]}
                           for name, calls in sorted(operations.items(), key=lambda x: (-x[1], x[0]))],
        },
        'coverage': {
            'account_turns_without_visible_snapshot': len(missing),
            'ambiguous_primary_events': sum(row['ambiguous_events'] for row in primary),
            'earliest_github_capture': min(captures) if captures else None,
            'latest_github_capture': max(captures) if captures else None,
            'limitations': [
                'Word totals cover recorded messages and GitHub discussion only. Journal excerpts and '
                'additional curated records are separate because they can paraphrase or repeat messages.',
                'Words are Unicode \\w+ runs with internal straight/curly apostrophes. Numbers, code and '
                'URL components count; Markdown is not stripped. Upload events, generated outcome '
                'references, bodyless review decision labels and empty-review placeholders contribute no words.',
                'Stable event IDs remove repeated PR/fork references. Different IDs and channels remain '
                'distinct events even when text matches; a quotation inside a message counts as retained text.',
                'Mixed human/agent attribution in inherited messages is unresolved, not silently assigned. '
                'Agent prompts are handoffs, separate from human words and responses.',
                'Responses combine agent responses and publishing-account responses, shown separately. '
                'The publishing account does not establish its operator or an extra human/agent instance.',
                'Named accounts are not verified distinct people. Unnamed users cannot be identified '
                'with reviewers or counted as one extra person. Agent threads are the observable instance '
                'proxy; role names, sessions and processes are not interchangeable.',
                'Tasks mean bounded canonical session records; tracked scientific tasks and pinned '
                'branch-only session references are reported separately. These counts are not additive.',
                'CLI/tool operations use exposed per-turn metadata once. Journal call counts and '
                'software invocations are not added to wrapper counts; complete CLI output is unavailable.',
                'Historical evidence is partial. Capture dates and PR states are snapshots, not current '
                'merge status. Missing words, turns, identities and operations remain unknown.',
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    args = parser.parse_args()
    metadata = {
        'source_commit': subprocess.check_output(['git', '-C', str(args.repo), 'rev-parse', 'HEAD'], text=True).strip(),
        'working_tree_dirty': bool(subprocess.check_output(['git', '-C', str(args.repo), 'status', '--porcelain'], text=True).strip()),
        'built_at': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
    }
    print(json.dumps(collect(args.repo, metadata), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
