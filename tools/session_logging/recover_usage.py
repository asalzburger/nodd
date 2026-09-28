#!/usr/bin/env python3
"""Export usage-only metadata from an explicitly selected local Codex store.

No conversation items are queried. Only token_count event lines are decoded.
The output is a recovery inventory, not automatically attributed project usage.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from session_log import TOKEN_FIELDS, require

FIELDS = (*TOKEN_FIELDS, 'cache_write_input_tokens')
TOKEN_EVENT = re.compile(r'"type"\s*:\s*"token_count"')


def counters(value, check_sum=True):
    require(type(value) is dict, 'missing counter object')
    result = {field: value.get(field) for field in FIELDS}
    # Older clients did not report cache writes; preserve that as unknown.
    for field in TOKEN_FIELDS:
        require(type(result[field]) is int and result[field] >= 0,
                f'invalid {field}')
    require(result['cache_write_input_tokens'] is None or
            (type(result['cache_write_input_tokens']) is int and
             result['cache_write_input_tokens'] >= 0), 'invalid cache-write counter')
    if check_sum:
        require(result['input_tokens'] + result['output_tokens'] == result['total_tokens'],
                'inconsistent total')
    require(result['cached_input_tokens'] <= result['input_tokens'], 'invalid cached subset')
    require(result['reasoning_output_tokens'] <= result['output_tokens'], 'invalid reasoning subset')
    return result


def extract_events(path):
    """Read up to the observed file size; never retain non-usage lines."""
    events = []
    with path.open('rb') as handle:
        limit = path.stat().st_size
        ordinal = 0
        while handle.tell() < limit:
            line = handle.readline(limit - handle.tell())
            if not line.endswith(b'\n'):
                break  # An actively written final line is not evidence yet.
            if TOKEN_EVENT.search(line.decode('utf-8')):
                obj = json.loads(line)
                payload = obj.get('payload', {})
                if obj.get('type') == 'event_msg' and payload.get('type') == 'token_count':
                    info = payload.get('info')
                    if info is not None:
                        events.append({'ordinal': ordinal, 'timestamp': obj['timestamp'],
                                       'total': counters(info['total_token_usage']),
                                       'last': counters(info['last_token_usage'], check_sum=False)})
            ordinal += 1
    return events


def reconcile(thread_id, turns, events):
    """Require every cumulative increase to equal one last-request observation."""
    require(events, 'no usage observations')
    previous = {field: 0 for field in FIELDS}
    result = {turn['turn_id']: dict(turn, events=[], tokens={f: 0 for f in TOKEN_FIELDS})
              for turn in turns}
    require(len(result) == len(turns), 'duplicate turn metadata')
    repeats, outside = 0, []
    for event in events:
        total, last = event['total'], event['last']
        known = [field for field in FIELDS if total[field] is not None]
        require(all(previous[field] is not None and last[field] is not None for field in known),
                'counter availability changed')
        delta = {field: total[field] - previous[field] for field in known}
        previous = total
        if all(value == 0 for value in delta.values()):
            repeats += 1
            continue
        # Context-accounting snapshots can change `last` without increasing
        # cumulative usage. Validate request totals only for real increases.
        counters(last)
        require(all(value >= 0 for value in delta.values()), 'cumulative counter reset/decrease')
        require(all(delta[field] == last[field] for field in known),
                'cumulative increase differs from last request; inherited or missing usage')
        owners = [turn for turn in result.values()
                  if turn['start_ordinal'] <= event['ordinal'] and
                  (turn['end_ordinal'] is None or event['ordinal'] <= turn['end_ordinal'])]
        require(len(owners) <= 1, 'overlapping turn boundaries')
        if not owners:
            outside.append(event)
            continue
        owner = owners[0]
        owner['events'].append(event)
        for field in TOKEN_FIELDS:
            owner['tokens'][field] += delta[field]
    observations = []
    for turn in result.values():
        selected = turn.pop('events')
        digest = hashlib.sha256(json.dumps(selected, sort_keys=True,
                                           separators=(',', ':')).encode()).hexdigest()
        turn.update(thread_id=thread_id, request_count=len(selected),
                    usage_sha256=digest,
                    first_usage_ordinal=selected[0]['ordinal'] if selected else None,
                    last_usage_ordinal=selected[-1]['ordinal'] if selected else None,
                    closed=turn['status'] in ('completed', 'interrupted', 'failed') and
                           turn['end_ordinal'] is not None)
        # No observed request means unknown usage, not a measured zero.
        if not selected:
            turn['tokens'] = {field: None for field in TOKEN_FIELDS}
        observations.append(turn)
    return {'thread_id': thread_id, 'usage_event_count': len(events),
            'repeated_snapshots': repeats, 'outside_turn_events': outside,
            'final_cumulative': previous, 'turns': observations}


def recover(client_home, project):
    def connect(name):
        db = sqlite3.connect((client_home / name).resolve().as_uri() + '?mode=ro', uri=True)
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        return db
    state, history = connect('state_5.sqlite'), connect('thread_history_1.sqlite')
    try:
        parents = dict(state.execute('SELECT child_thread_id,parent_thread_id FROM thread_spawn_edges'))
        # Exact path/descendant comparison avoids SQL LIKE wildcard ambiguities.
        threads = [dict(row) for row in state.execute(
            'SELECT id,rollout_path,cwd,agent_path,git_sha FROM threads ORDER BY created_at,id')
                   if Path(row['cwd']).resolve().is_relative_to(project.resolve())]
        inventory = []
        for thread in threads:
            turns = [dict(row) for row in history.execute(
                'SELECT turn_id,rollout_ordinal AS start_ordinal,'
                'rollout_end_ordinal AS end_ordinal,status,started_at,completed_at '
                'FROM thread_turns WHERE thread_id=? ORDER BY rollout_ordinal', (thread['id'],))]
            item = reconcile(thread['id'], turns, extract_events(Path(thread['rollout_path'])))
            item.update(parent_thread_id=parents.get(thread['id']),
                        agent_path=thread['agent_path'], initial_git_sha=thread['git_sha'])
            inventory.append(item)
        return {'format_version': 1, 'captured_at': datetime.now(timezone.utc).isoformat(),
                'scope': 'Explicit local project directory and descendants; other machines/worktrees not included.',
                'method': 'Cumulative increases verified against last-request counters, grouped by persisted turn ordinals; identical snapshots ignored.',
                'threads': inventory}
    finally:
        state.close()
        history.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = recover(args.codex_home, args.project)
    with args.output.open('x') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    stats = Counter(t['status'] for thread in report['threads'] for t in thread['turns'])
    print(json.dumps({'threads': len(report['threads']), 'turn_states': dict(stats),
                      'repeated_snapshots': sum(t['repeated_snapshots'] for t in report['threads']),
                      'outside_turn_events': sum(len(t['outside_turn_events']) for t in report['threads'])}))


if __name__ == '__main__':
    main()
