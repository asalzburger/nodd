#!/usr/bin/env python3
"""Read committed, sanitized PR90 accounting evidence; write scratch results only."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

FIELDS = ('input_tokens', 'cached_input_tokens', 'output_tokens',
          'reasoning_output_tokens', 'total_tokens')
INV = 'logs/usage/USAGE-2026-10-20-pr90.json'
ROOT_THREAD = '01a142fe-aeff-7a72-a51f-edbcc74643b8'
ACCOUNTING = 'SESSION-2026-10-20-pr90-token-closeout'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--revision', default='a52d1cbd55a680e4bfc8a89219cd45819fa57506')
    parser.add_argument('--baseline', default='f1089e3ece830dbbb2bdaaf86ade19e13585a471')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo, rev, base = args.repo.resolve(), args.revision, args.baseline
    findings, checks, hashes = [], [], {}

    def run(*items):
        return subprocess.check_output(['git', '-C', str(repo), *items])

    def blob(p, at=rev):
        data = run('show', at + ':' + p)
        hashes[at + ':' + p] = hashlib.sha256(data).hexdigest()
        return data

    def obj(p, at=rev):
        return json.loads(blob(p, at))

    def check(ok, description):
        if not ok:
            raise AssertionError(description)
        checks.append(description)

    def tree(at):
        return {line.split(b'\t', 1)[1].decode(): line.split(b'\t', 1)[0].decode()
                for line in run('ls-tree', '-r', '-z', at).split(b'\0') if line}

    def journal(at):
        result = {}
        for p in tree(at):
            if p.endswith('.json') and p.startswith(('logs/codex/', 'logs/design/')):
                d = obj(p, at)
                result[d['session_id']] = (p, d)
        return result

    def owners(records):
        result = {}
        for session, (_, record) in records.items():
            for entry in record['usage']:
                key = (entry['client_thread_id'], entry['turn_id'])
                if key in result:
                    raise AssertionError('Duplicate canonical owner: ' + repr(key))
                result[key] = (session, entry)
        return result

    def sums(entries):
        entries = list(entries)
        return {'turns': len(entries), **{f: sum(e[f] for e in entries) for f in FIELDS}}

    before, after = journal(base), journal(rev)
    old_owners, new_owners = owners(before), owners(after)
    check(len(old_owners) == 210 and len(new_owners) == 250, '210 baseline and 250 target canonical observations, all uniquely owned')
    check(all(new_owners.get(k) == v for k, v in old_owners.items()), 'All original 210 observations and owners remain exact')
    added = {k: v for k, v in new_owners.items() if k not in old_owners}
    check(len(added) == 40, 'Exactly 40 canonical observations added')
    inventory = obj(INV)
    summary = obj('logs/usage/PR90-2026-10-20-summary.json')
    capture = datetime.fromisoformat(inventory['captured_at'])
    imported, active, roots, children = {}, [], {}, []
    statuses, by_session, dates = Counter(), defaultdict(list), {}
    thread_rows = []
    for thread in inventory['threads']:
        tid = thread['thread_id']
        rows = thread['turns']
        intervals = sorted((t['start_ordinal'], t['end_ordinal'], t['turn_id']) for t in rows)
        for left, right in zip(intervals, intervals[1:]):
            check(left[1] is not None and left[1] < right[0], 'Disjoint persisted turn intervals: ' + tid + ':' + right[2])
        if thread['parent_thread_id'] is not None:
            check(thread['parent_thread_id'] == ROOT_THREAD, 'Explicit parent edge for ' + tid)
            check(all(t['closed'] for t in rows), 'Selected child turns all closed: ' + tid)
            check(all(sum(t['tokens'][f] for t in rows) == thread['final_cumulative'][f] for f in FIELDS), 'Child turn sums independently equal final child cumulative counters: ' + tid)
            check(sum(t['request_count'] for t in rows) == thread['usage_event_count'] - thread['repeated_snapshots'], 'Child request/repeated-snapshot counts reconcile: ' + tid)
        else:
            check(tid == ROOT_THREAD, 'Only selected PR90 root thread included')
            for exclusion in thread['excluded_prior_turns']:
                check((tid, exclusion['turn_id']) not in new_owners, 'Earlier PR86/87 root observation excluded: ' + exclusion['turn_id'])
        for turn in rows:
            key = (tid, turn['turn_id'])
            token = turn['tokens']
            if not turn['closed']:
                active.append(key)
                check(turn['status'] == 'inProgress' and turn['end_ordinal'] is None and turn['completed_at'] is None, 'Active turn has no finalized boundary/date')
                check(key not in new_owners and turn['disposition'] == 'in_progress_excluded', 'Active parent observation absent from canonical usage')
                continue
            check(key not in imported, 'Unique sanitized imported pair: ' + repr(key))
            imported[key] = turn
            check(turn['status'] in ('completed', 'failed', 'interrupted'), 'Terminal closed status for ' + turn['turn_id'])
            check(turn['end_ordinal'] is not None and turn['completed_at'] is not None, 'Closed boundary and exact completion supplied for ' + turn['turn_id'])
            check(turn['start_ordinal'] <= turn['first_usage_ordinal'] <= turn['last_usage_ordinal'] <= turn['end_ordinal'], 'Usage ordinals inside persisted turn for ' + turn['turn_id'])
            check(re.fullmatch('[0-9a-f]{64}', turn['usage_sha256']) is not None and turn['request_count'] > 0, 'Canonical event digest and observed requests retained for ' + turn['turn_id'])
            check(all(type(token[f]) is int and token[f] >= 0 for f in FIELDS), 'Five nonnegative integer counters for ' + turn['turn_id'])
            check(token['total_tokens'] == token['input_tokens'] + token['output_tokens'] and token['cached_input_tokens'] <= token['input_tokens'] and token['reasoning_output_tokens'] <= token['output_tokens'], 'Total/subset arithmetic for ' + turn['turn_id'])
            check(key in added and added[key][0] == turn['target_session_id'], 'Source observation matches sole new canonical owner for ' + turn['turn_id'])
            entry = added[key][1]
            check(entry == turn['usage_entry'] and all(entry[f] == token[f] for f in FIELDS), 'All five counters and complete curated entry exactly match canonical usage for ' + turn['turn_id'])
            check(entry['model'] is None and bool(entry['limitations']), 'Unknown execution model/client/billing limitations retained for ' + turn['turn_id'])
            check(inventory['captured_at'] in entry['source'] and turn['usage_sha256'] in entry['source'], 'Uniform capture header and event digest match canonical evidence source for ' + turn['turn_id'])
            at = datetime.fromtimestamp(turn['completed_at'], timezone.utc)
            check(at <= capture and turn['started_at'] <= turn['completed_at'], 'Actual turn completion precedes capture for ' + turn['turn_id'])
            dates[key] = at
            statuses[turn['status']] += 1
            by_session[turn['target_session_id']].append(entry)
            if tid == ROOT_THREAD:
                roots[turn['turn_id']] = turn
            else:
                children.append((thread, turn))
        thread_rows.append({'thread_id': tid, 'agent_path': thread['agent_path'], 'closed_turns': sum(t['closed'] for t in rows), 'requests': sum(t['request_count'] for t in rows)})
    check(set(imported) == set(added), 'Sanitized imported pairs equal all new canonical pairs exactly')
    check(len(active) == 1 and len(roots) == 16 and len(children) == 24, '16 closed roots, 23 scientific children, one accounting child; active parent excluded')
    for thread, turn in children:
        evidence = turn['attribution_evidence']
        parent = turn['root_turn_id']
        if turn['target_session_id'] == ACCOUNTING:
            check(any(key[1] == parent for key in active), 'Accounting child tied to active accounting parent without counting parent')
        else:
            check(parent in roots and roots[parent]['target_session_id'] == turn['target_session_id'], 'Child root-turn ID ties to same canonical parent-task owner: ' + turn['turn_id'])
        check(evidence['root_turn_id'] == parent and evidence['parent_thread_id'] == thread['parent_thread_id'] and evidence['agent_path'] == thread['agent_path'] and evidence['parent_task_owner'] == turn['target_session_id'], 'Child persisted relationship/agent-path fields agree for ' + turn['turn_id'])
    expected_all = sums(v[1] for v in added.values())
    expected_science = sums(v[1] for v in added.values() if v[0] != ACCOUNTING)
    check(expected_all == inventory['observed_closed_subtotal'] == summary['observed_closed_subtotal'], 'Independent all-five-counter 40-turn subtotal equals both reports')
    check(expected_science == inventory['design_validation_publication_subtotal'] == summary['design_validation_publication_subtotal'], 'Independent 39-turn scientific/delivery subtotal equals both reports')
    check(expected_all['total_tokens'] == 247693973 and expected_science['total_tokens'] == 245350881, '247693973 first-import / 245350881 scientific observed totals')
    for row in summary['rows']:
        check(sums(by_session[row['session_id']]) == {k: row[k] for k in ('turns', *FIELDS)}, 'Independent per-session subtotal: ' + row['session_id'])
    global_totals = sums(v[1] for v in new_owners.values())
    check(all(global_totals[f] == summary['global_after_first_import'][f] for f in ('turns', 'input_tokens', 'output_tokens', 'total_tokens')), 'Global 250-turn first-import totals match independent canonical sums')

    # Validate attribution evidence against the pinned primary journals, not dates.
    for turn in roots.values():
        session = turn['target_session_id']
        text = blob(before[session][0][:-5] + '.md', base).decode()
        evidence = turn['attribution_evidence']
        check(evidence['canonical_journal_at'].split(':')[1] == before[session][0][:-5] + '.md', 'Root attribution points to correct bounded journal: ' + turn['turn_id'])
        if evidence['session_ids_in_command_metadata']:
            check(session in evidence['session_ids_in_command_metadata'], 'Direct canonical session ID occurs in retained command metadata: ' + turn['turn_id'])
        else:
            check(turn['turn_id'] in ('01a15880-c9f7-77c0-93d7-114c97170351', '01a15931-c350-7d01-b73a-27a6c686167c'), 'Only explicitly reconciled delayed/superseding requests lack direct command IDs')
        if turn['turn_id'].startswith('01a15880'):
            check('HCALback6.4412m, ECTwarmfront6.55m' in text and 'asked asynchronously whether to adjust endcap-toroid axial extent/recalculate field' in text, 'Delayed HCAL/ECT answer matches exact recorded asynchronous question')
        if turn['turn_id'].startswith('01a15931'):
            check('asked to address the next PR90 comment and then said the comment was updated' in text, 'Interrupted next-comment request matches superseding sketch journal')
    for path, d in before.values():
        now = after[d['session_id']][1]
        if path in [after[s][0] for s in by_session if s != ACCOUNTING]:
            check(all(d[k] == now[k] for k in d if k not in ('usage', 'limitations')), 'Historical session scientific/source metadata preserved: ' + d['session_id'])
            check(blob(path[:-5] + '.md', rev).startswith(blob(path[:-5] + '.md', base)), 'Original historical narrative preserved with append-only correction: ' + d['session_id'])

    old_tree, new_tree = tree(base), tree(rev)
    changed = sorted(p for p in old_tree.keys() | new_tree.keys() if old_tree.get(p) != new_tree.get(p))
    doc_exceptions = {'docs/design/DES-040-muon-chambers-frame.md', 'docs/validation/DES-040/sketched-stagger-2026-10-20/README.md'}
    check(all(p.startswith('logs/') or p == 'project/tracking.json' or p in doc_exceptions for p in changed), 'Entire Git tree diff restricted to accounting/records and two scope prose documents')
    science = [p for p in old_tree if p.startswith(('tools/muon_layout/', 'tools/toroid_prototype/', 'docs/validation/DES-040/', 'docs/validation/DES-039/')) and p not in doc_exceptions]
    check(all(old_tree[p] == new_tree.get(p) for p in science), 'All ' + str(len(science)) + ' checked implementation, field, geometry, native, OBJ, figure and science-source blobs unchanged')
    check(hashes[rev + ':logs/usage/PR90-2026-10-20-session-audit.json'] if rev + ':logs/usage/PR90-2026-10-20-session-audit.json' in hashes else hashlib.sha256(blob('logs/usage/PR90-2026-10-20-session-audit.json')).hexdigest() == '2f8d2ab208fbbedd53099f21a064e0d855f26bfe6aa4961ce93149736da3bde2', 'Retained A1 baseline audit is byte-exact')

    # Execute exact committed tools against a minimal, pinned scratch projection.
    scratch = Path(tempfile.mkdtemp(prefix='pr90-TA-A1-check2-'))
    for p in new_tree:
        if (p.startswith(('logs/codex/', 'logs/design/', 'logs/usage/', 'tools/session_logging/', 'tools/token_usage/')) and p.endswith(('.json', '.md', '.py', '.css', '.js'))) or p == 'project/token-milestones.json':
            target = scratch / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob(p))
    gitdir = run('rev-parse', '--absolute-git-dir').decode().strip()
    env = dict(os.environ, GIT_DIR=gitdir, GIT_WORK_TREE=str(scratch), PYTHONDONTWRITEBYTECODE='1')
    executions = []
    for command in [
        ['python3', '-B', str(scratch / 'tools/session_logging/session_log.py'), '--repo', str(scratch), 'validate'],
        ['python3', '-B', str(scratch / 'tools/token_usage/build.py'), 'validate', '--repo', str(scratch)],
        ['python3', '-B', str(scratch / 'tools/token_usage/build.py'), 'build', '--repo', str(scratch), '--output', str(scratch / '_site/review'), '--built-at', '2026-10-20T13:00:58Z'],
    ]:
        completed = subprocess.run(command, env=env, capture_output=True, text=True)
        executions.append({'command': command, 'exit_code': completed.returncode, 'stdout': completed.stdout, 'stderr': completed.stderr})
        check(completed.returncode == 0, 'Pinned scratch tool succeeds: ' + ' '.join(command))
    site = json.loads((scratch / '_site/review/usage.json').read_text())
    check(site['dated_turns'] == 250 and site['undated_turns'] == 0, 'Global curve has exact closed completion dates for all 250 canonical observations')
    # Independently build date ownership from all inventory shapes, then compare the curve.
    all_dates = {}
    for p in new_tree:
        if not p.startswith('logs/usage/') or not p.endswith('.json'):
            continue
        inv = obj(p)
        turns = [(t, inv.get('thread_id')) for t in inv.get('completed_turns', [])]
        turns += [(t, th.get('thread_id')) for th in inv.get('threads', []) for t in th.get('turns', [])]
        for turn, thread in turns:
            entry = turn.get('usage_entry') or {}
            key = (entry.get('client_thread_id') or turn.get('thread_id') or thread, entry.get('turn_id') or turn.get('turn_id'))
            if key not in new_owners or turn.get('completed_at') is None:
                continue
            value = turn['completed_at']
            date = (datetime.fromtimestamp(value, timezone.utc) if isinstance(value, (int, float)) else datetime.fromisoformat(value.replace('Z', '+00:00'))).date().isoformat()
            check(key not in all_dates or all_dates[key] == date, 'Independent UTC inventory date evidence agrees for ' + repr(key))
            all_dates[key] = date
    expected_daily = defaultdict(list)
    for key, (_, entry) in new_owners.items():
        expected_daily[all_dates[key]].append(entry)
    cumulative = dict.fromkeys(FIELDS, 0)
    for point in site['series']:
        daily = sums(expected_daily[point['date']])
        check(daily['turns'] == point['turns'] and all(daily[f] == point['daily'][f]['sum'] for f in FIELDS), 'Independent UTC-day totals equal built curve: ' + point['date'])
        for f in FIELDS:
            cumulative[f] += daily[f]
        check(cumulative == point['cumulative'], 'Independent cumulative curve totals: ' + point['date'])
    check(cumulative['total_tokens'] == 871993378, 'Global curve terminates at 871993378 observed tokens')
    spec = importlib.util.spec_from_file_location('review_logger', scratch / 'tools/session_logging/session_log.py')
    logger = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(logger)
    replay = []
    for session, entries in by_session.items():
        result = logger.import_usage(scratch, session, entries, dry_run=True)
        check(result['added'] == 0 and result['unchanged'] == len(entries), 'Idempotent exact replay: ' + session)
        replay.append(result)
    sample_key, (owner, entry) = next(iter(added.items()))
    wrong_owner = next(s for s in by_session if s != owner)
    try:
        logger.import_usage(scratch, wrong_owner, [entry], dry_run=True)
    except ValueError as error:
        check('already belongs' in str(error), 'Cross-owner duplicate import rejected')
    else:
        raise AssertionError('Cross-owner duplicate accepted')
    changed_entry = dict(entry, source=entry['source'] + ' conflicting replay')
    try:
        logger.import_usage(scratch, owner, [changed_entry], dry_run=True)
    except ValueError as error:
        check('conflicting usage turn' in str(error), 'Conflicting same-owner replay rejected')
    else:
        raise AssertionError('Conflicting replay accepted')
    check(all((scratch / p).read_bytes() == blob(p) for p in new_tree if p.startswith(('logs/codex/', 'logs/design/')) and p.endswith('.json')), 'Scratch canonical JSON unchanged by all import replays')
    result = {'assignment': 'TA-A2', 'role': 'SoftEng explicit fallback', 'reviewed_revision': rev, 'baseline_revision': base,
              'status': 'PASS', 'material_findings': findings, 'checks_passed': len(checks), 'checks': checks,
              'observed_closed_subtotal': expected_all, 'scientific_delivery_subtotal': expected_science,
              'global_canonical_totals': global_totals, 'closed_statuses': dict(statuses),
              'new_dates_utc': dict(Counter(at.date().isoformat() for at in dates.values())),
              'unique_owner_pairs': len(new_owners), 'selected_threads': thread_rows,
              'changed_paths': changed, 'unchanged_science_blob_count': len(science),
              'tool_executions': executions, 'idempotent_import_replays': replay, 'scratch_projection': str(scratch),
              'source_sha256': hashes, 'files_changed_in_repository': [],
              'limits': ['No private client DB, conversation, raw rollout or reasoning access; no physics/native/dependency execution.',
                         'Cumulative-to-request event reconciliation cannot be rerun from sanitized totals/hashes alone. It is recorded by the recovery execution and pinned recovery implementation; this audit independently checks retained boundaries, per-child cumulative sums, hashes and canonical counter equality.',
                         'Root total includes excluded earlier work and the active turn, so it is not a PR90 subtotal and is not added to child totals.',
                         'Agent aliases and persisted relationship fields are accepted as sanitized recovery metadata; raw source metadata is not reopened.',
                         'A1 baseline audit was authored by this same agent. This separate turn reviews coordinator-owned imports and attribution, not independent authorship of A1 itself.',
                         'Current parent and current supplemental audit turns are not finalized by this assessment. No complete-device, billing or engineering acceptance claim.',
                         'Scratch site metadata uses the repository Git directory with scratch working tree; its dirty flag reflects the intentionally partial scratch projection.']}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'observations': expected_all, 'global': global_totals, 'science_blobs_unchanged': len(science), 'output': str(args.output), 'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}, indent=2))


if __name__ == '__main__':
    main()
