#!/usr/bin/env python3
"""Curate PR interaction evidence; reference, never reallocate, canonical usage."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/session_logging'))
import session_log as logger

REPO = 'asalzburger/nodd'
BASE = 'https://github.com/' + REPO
ROLES = ('ProRes', 'SysArch', 'TrackTech', 'CaloTech', 'MuonTech',
         'SoftEng', 'PhysVal', 'PubDoc')
CATEGORIES = ('native_codex', 'codex_installed', 'instructed_software', 'unresolved')
TYPES = ('comment', 'issue', 'prompt', 'upload', 'response', 'review', 'reaction')
NATIVE = ('exec_command', 'apply_patch', 'view_image', 'write_stdin',
          'web.run', 'clock.curr_time', 'collaboration', 'spawn_agent',
          'followup_task', 'send_message', 'functions.exec')
INSTRUCTED = {'DD4hep', 'ROOT', 'Geant4 DDSim', 'ACTS native Python',
              'ACTS standard helper', 'ACTS C++ CTest',
              'acts-nodd finite-surface propagation', 'ACTS EigenStepper finite-plane audits',
              'native DD4hep/ROOT/Geant4', 'DD4hep/ROOT/Geant4 validation',
              'DD4hep/ROOT/Geant4 and nodehammer'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    ensure_ascii=False).encode()).hexdigest()


def write(path, value):
    text = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    if not path.exists() or path.read_text() != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def path_for(root, number):
    logger.require(type(number) is int and number > 0, 'invalid PR number')
    return root / 'interactions' / f'pr-{number:04d}.json'


def sections(text):
    """Keep curated visible conversation and assignment sections, not rollouts."""
    for block in re.split(r'(?m)(?=^## )', text):
        heading = block.split('\n', 1)[0]
        if re.search(r'conversation|request|prompt|assignment|handoff|'
                     r'user.visible outcome|decisions and outcomes', heading, re.I):
            yield heading.removeprefix('## '), block.partition('\n')[2].strip()


def journal_links(root, snapshot, records):
    number = snapshot['github']['pull_request']['number']
    branch = snapshot['github']['pull_request']['head']
    explicit = set(snapshot['curated']['journal_links'])
    links = []
    for record in records:
        reasons = []
        if record['session_id'] in explicit:
            reasons.append('curated_session_link')
        if branch and record['git']['branch'] == branch:
            reasons.append('recorded_branch')
        if any(re.fullmatch(rf'PR[- #]?0*{number}', s, re.I)
               for s in record['work']['related_ids']):
            reasons.append('explicit_PR_reference')
        if reasons:
            links.append((record, reasons))
    logger.require(explicit <= {r['session_id'] for r in records},
                   'curated link references an absent canonical session')
    canonical = {r['session_id'] for r in records}
    for path in sorted((root / 'interactions' / f'pr-{number:04d}' / 'journals').glob('*.json')):
        source = logger.read_json(path)
        if source['session_id'] in canonical:
            continue
        logger.require(re.fullmatch('[0-9a-f]{40}', source['source_revision']) is not None
                       and source['source_record'].startswith(BASE + '/blob/' + source['source_revision'] + '/')
                       and source['source_narrative'].startswith(BASE + '/blob/' + source['source_revision'] + '/'),
                       'branch journal needs immutable source revision links')
        record = {'session_id': source['session_id'], 'title': source['title'],
                  'client': source['client'], 'narrative': source['source_narrative'],
                  'activities': source['activities'], 'usage': source['usage_refs'],
                  '_source': source, '_snapshot_path': path.relative_to(root).as_posix()}
        links.append((record, ['pinned_branch_journal_snapshot']))
    return links


def derive(root, snapshot, records):
    github = snapshot['github']
    curated = snapshot['curated']
    events, accounts, journals, agents, tools = [], [], [], [], []
    parties = {}

    def party(name, kind='account'):
        key = ('github:' + name) if name else 'unknown:project-user'
        parties[key] = {'id': key, 'name': name or 'Project user (name unrecorded)',
                        'kind': kind}
        return key

    def event(identifier, kind, direction, actor, text, source, **extra):
        item = {'id': identifier, 'type': kind, 'direction': direction,
                'actor': actor, 'recipients': [], 'text': text,
                'source': source, 'in_reply_to': None, 'model': None,
                'agent_roles': [], 'token_accounts': [], **extra}
        events.append(item)
        for index, url in enumerate(dict.fromkeys(re.findall(
                r'https://(?:github\.com/user-attachments/|user-images\.githubusercontent\.com/)[^\s)>]+', text))):
            events.append({**item, 'id': identifier + f':upload:{index}',
                           'type': 'upload', 'text': url,
                           'in_reply_to': identifier})
        return item

    def public(item, fallback, issue=False, body=False):
        name = item.get('actor')
        bot = bool(name and (name.endswith('[bot]') or name.startswith('chatgpt-codex')))
        actor = party(name, 'agent' if bot else
                      ('human' if name and name != 'asalzburger' else 'account'))
        text = item.get('body') or item.get('review') or '(empty review)'
        remote = bool(re.search(r'@codex\b', text, re.I))
        kind = ('prompt' if remote else 'issue' if issue else 'review'
                if item.get('review') else 'response' if bot or body or name == 'asalzburger'
                else 'comment')
        direction = 'action' if remote or (name != 'asalzburger' and not bot
                                          and not item.get('review')) else 'reaction'
        url = item.get('url') or fallback
        result = event('github:' + url, kind, direction, actor, text, url,
                       timestamp=item.get('created_at'),
                       remote_input='codex_mention' if remote else None,
                       in_reply_to=(f'github-comment:{item["in_reply_to_id"]}'
                                    if item.get('in_reply_to_id') else None))
        if bot:
            result['recipients'] = ['unknown:project-user']
        return result

    party(None, 'human')
    pr = github['pull_request']
    public(pr, pr['url'], body=True)
    for item in github['comments']:
        public(item, pr['url'])
    for issue in github['issues']:
        public(issue, issue['url'], issue=True)
        for item in issue['comments']:
            public(item, issue['url'])

    # Resolve only explicit GitHub replies/links. Adjacency is not causality.
    by_comment = {str(c.get('id')): 'github:' + c['url']
                  for c in github['comments'] +
                  [c for i in github['issues'] for c in i['comments']]}
    known_events = {e['id'] for e in events}
    for item in events:
        reply = item['in_reply_to']
        if reply and reply.startswith('github-comment:'):
            item['in_reply_to'] = by_comment.get(reply.split(':', 1)[1])
        if item['in_reply_to'] is None:
            urls = re.findall(re.escape(BASE) + r'/pull/\d+#(?:issuecomment|discussion_r|pullrequestreview)-?\d+', item['text'])
            item['in_reply_to'] = next(('github:' + u for u in urls
                                        if 'github:' + u in known_events), None)

    for record, reasons in journal_links(root, snapshot, records):
        sid = record['session_id']
        external = record.get('_source')
        narrative = (None if external else logger.repo_path(root, record['narrative']).read_text())
        json_path = external['source_record'] if external else str(Path(record['narrative']).with_suffix('.json'))
        journals.append({'session_id': sid, 'record': json_path,
                         'attribution': reasons,
                         'snapshot': record.get('_snapshot_path'),
                         'snapshot_sha256': digest(external) if external else None,
                         'record_sha256': external['record_sha256'] if external else digest(record),
                         'narrative_sha256': external['narrative_sha256'] if external else hashlib.sha256(narrative.encode()).hexdigest()})
        accounts.append({'id': sid, 'record': json_path,
                         'scope': ('pinned_branch_reference; not imported into main accounting' if external
                                   else 'canonical_session; shared PR references are not allocations'),
                         'status': 'observed' if record['usage'] else 'unobserved',
                         'usage_sha256': external['usage_sha256'] if external else digest(record['usage']),
                         'turns': [{'client_thread_id': u['client_thread_id'],
                                    'turn_id': u['turn_id'], 'model': u['model']}
                                   for u in record['usage']]})
        agent = 'agent:' + sid
        parties[agent] = {'id': agent, 'name': record['client']['name'], 'kind': 'agent'}
        models = sorted({u['model'] for u in record['usage'] if u['model']})
        agents.append({'id': agent, 'name': record['client']['name'],
                       'role': 'session_agent', 'thread_id': record['client']['thread_id'],
                       'models': models, 'source': json_path,
                       'limitation': 'Usage may include children; model/role is not assigned to every response.'})
        party(None, 'human')
        selected = external['sections'] if external else list(sections(narrative))
        for heading, text in selected:
            # Sections remain exact curated excerpts. They may contain several
            # inputs; their original narrative is the authority for sequence.
            assignment = bool(re.search(r'assignment|handoff', heading, re.I))
            outcome = bool(re.search(r'outcome|decisions', heading, re.I))
            roles = [role for role in ROLES if re.search(r'\b' + role + r'\b', text + heading)]
            source = record['narrative'] + '#' + re.sub(r'[^\w -]', '', heading.lower()).replace(' ', '-')
            fragments = ([text] if assignment or outcome else re.split(
                r'(?m)(?=^(?:[-*] )?(?:User|Human|Assistant|Codex|Prompt|Response)\b)', text))
            for fragment in filter(str.strip, fragments):
                response = outcome or bool(re.match(r'(?:[-*] )?(?:Assistant|Codex|Response)\b', fragment))
                event('journal:' + sid + ':' + digest([heading, fragment])[:16],
                      'response' if response else 'prompt',
                      'reaction' if response else 'action',
                      agent if assignment or response else 'unknown:project-user',
                      fragment, source, agent_roles=roles, token_accounts=[sid],
                      recipients=[agent] if not assignment and not response else [],
                      content_kind='curated_excerpt; retain original qualifiers and speaker labels')
            for role in roles if assignment else []:
                agents.append({'id': agent + ':' + role + ':' + digest(heading)[:8],
                               'name': role, 'role': 'reported_specialist_assignment',
                               'thread_id': None, 'models': [], 'source': source,
                               'limitation': 'Role contract is recorded; native profile loading and process identity are not inferred.'})
        # A durable outcome reference exists even when no conversation section
        # survived. It is explicitly a summary, not invented assistant text.
        event('journal:' + sid + ':outcome', 'response', 'reaction', agent,
              record['title'] + ' — see the canonical narrative for outcomes and checks.',
              record['narrative'], token_accounts=[sid], content_kind='reference_summary')
        for activity in record['activities']:
            if activity['kind'] != 'tool':
                continue
            name = activity['name']
            # Combined activity labels stay unresolved; a shell wrapper does
            # not establish the provenance of programs executed through it.
            category = ('native_codex' if name in NATIVE or name.startswith('collaboration.')
                        else 'instructed_software' if name in INSTRUCTED else 'unresolved')
            tools.append({'name': name, 'category': category,
                          'version': activity['version'], 'calls': activity['calls'],
                          'source': json_path, 'evidence': activity['evidence'],
                          'token_account': sid,
                          'provenance': ('Native API name' if category == 'native_codex'
                                         else 'User-directed runtime: AGENTS.md#node-specific-software-workflows'
                                         if category == 'instructed_software' else
                                         'Operation recorded; installation provenance needs explicit evidence.')})

    agents.extend(curated['agents'])
    tools.extend(curated['tools'])
    for item in curated['events']:
        events.append(item)
    visible_sources, recovered = [], set()
    account_map = {a['id']: a for a in accounts}
    turn_paths = sorted((root / 'interactions' / f'pr-{pr["number"]:04d}' / 'turns').glob('*.json'))
    parents = {child['thread_id']: turn['thread_id']
               for turn in (logger.read_json(p) for p in turn_paths)
               for child in turn['subagents'] if child['thread_id']}
    for path in turn_paths:
        turn = logger.read_json(path)
        validate_visible(turn)
        key = (turn['thread_id'], turn['turn_id'])
        logger.require(key not in recovered, 'duplicate visible turn snapshot')
        recovered.add(key)
        for sid in turn['token_accounts']:
            logger.require(sid in account_map and any(
                (u['client_thread_id'], u['turn_id']) == key
                for u in account_map[sid]['turns']), 'visible turn does not match its token account')
        source = path.relative_to(root).as_posix()
        visible_sources.append({'path': source, 'sha256': digest(turn)})
        agent = 'codex-thread:' + turn['thread_id']
        parties[agent] = {'id': agent, 'name': 'Codex thread ' + turn['thread_id'], 'kind': 'agent'}
        agents.append({'id': agent, 'name': 'Codex', 'role': 'recorded_thread',
                       'thread_id': turn['thread_id'], 'models': [], 'source': source,
                       'limitation': 'Execution model is retained only when reported by the canonical account.'})
        previous_input = None
        sender = 'unknown:project-user'
        if turn['thread_id'] in parents:
            parent = parents[turn['thread_id']]
            sender = 'codex-thread:' + parent
            parties[sender] = {'id': sender, 'name': 'Codex parent thread ' + parent, 'kind': 'agent'}
        for message in turn['messages']:
            user = message['role'] == 'user'
            identifier = 'codex-message:' + message['id']
            event(identifier, 'upload' if message['phase'] == 'upload' else
                  'prompt' if user else 'response', 'action' if user else 'reaction',
                  sender if user else agent, message['text'], source,
                  recipients=[agent] if user else [sender],
                  in_reply_to=None if user else previous_input,
                  token_accounts=turn['token_accounts'],
                  content_kind='visible_message; conservative redactions recorded in source')
            if user:
                previous_input = identifier
        for operation in turn['native_tools']:
            tools.append({'name': operation['name'], 'category': 'native_codex',
                          'version': None, 'calls': operation['calls'],
                          'source': source, 'evidence': 'Exposed operation metadata for exact recorded turn; '
                          + str(operation['failures']) + ' failures reported.',
                          'token_account': turn['token_accounts'][0],
                          'provenance': 'Codex-exposed operation or integration API. Executed software is classified separately.'})
        for child in turn['subagents']:
            agents.append({'id': 'codex-child:' + str(child['thread_id']),
                           'name': child['name'] or 'Unnamed subagent',
                           'role': 'subagent', 'thread_id': child['thread_id'],
                           'models': [], 'source': source,
                           'limitation': 'Parent thread ' + turn['thread_id'] + '; activity ' + str(child['activity'])
                           + '. Agent path is not proof of native role-profile loading.'})
    expected_turns = {(u['client_thread_id'], u['turn_id']) for a in accounts for u in a['turns']}
    # Context references do not establish per-message accounting or causality.
    # Preserve ordering from sources; reject duplicate IDs rather than guessing.
    return {'parties': sorted(parties.values(), key=lambda p: p['id']),
            'journals': journals, 'token_accounts': accounts, 'visible_sources': visible_sources,
            'agents': agents, 'tools': {c: [t for t in tools if t['category'] == c]
                                      for c in CATEGORIES},
            'events': events,
            'coverage': {
                'github_captured_at': github['captured_at'],
                'prompts': 'Available account-matched user-visible messages, public Codex inputs and curated journal excerpts. Historical full input coverage is unknown.',
                'recovered_visible_turns': len(recovered),
                'unrecovered_account_turns': [{'thread_id': t, 'turn_id': u} for t, u in sorted(expected_turns - recovered)],
                'responses': 'Public responses and recorded outcomes; no private model state or hidden reasoning.',
                'token_accounting': 'References only. Never sum accounts across PRs or assign a shared turn by text length.',
                'unknowns': 'Unrecorded names, models, tools, subagent identities and response links remain unknown; empty lists are not zero activity.',
                'remote': 'Snapshot, not live synchronization; deleted/edited history and emoji reactions are not recovered.',
                'branch_only': 'Pinned branch journal snapshots are references, not imported counters. Unretained or other-device inputs remain unknown.'}}


def snapshot_journals(root, snapshot):
    """Retain selected visible evidence from pinned PR journals absent on main."""
    pr = snapshot['github']['pull_request']
    revision = pr['head_sha']
    number = pr['number']
    canonical = {r['session_id'] for r in logger.load_records(root)}
    names = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-r', '--name-only',
                                     revision, '--', 'logs/codex', 'logs/design'], text=True).splitlines()
    count = 0
    for name in names:
        if not name.endswith('.json') or not Path(name).name.startswith('SESSION-') or Path(name).stem in canonical:
            continue
        raw = subprocess.check_output(['git', '-C', str(root), 'show', f'{revision}:{name}'], text=True)
        record = json.loads(raw)
        if 'git' not in record or 'session_id' not in record:
            continue
        if record['git']['branch'] != pr['head'] and not any(
                re.fullmatch(rf'PR[- #]?0*{number}', s, re.I) for s in record['work']['related_ids']):
            continue
        narrative = subprocess.check_output(['git', '-C', str(root), 'show',
                                            f'{revision}:{record["narrative"]}'], text=True)
        source = {'session_id': record['session_id'], 'title': record['title'],
                  'client': record['client'], 'source_revision': revision,
                  'source_record': BASE + f'/blob/{revision}/{name}',
                  'source_narrative': BASE + f'/blob/{revision}/{record["narrative"]}',
                  'record_sha256': digest(record),
                  'narrative_sha256': hashlib.sha256(narrative.encode()).hexdigest(),
                  'sections': list(sections(narrative)), 'activities': record['activities'],
                  'usage_sha256': digest(record['usage']),
                  'usage_refs': [{k: u[k] for k in ('client_thread_id', 'turn_id', 'model')}
                                 for u in record['usage']]}
        write(root / 'interactions' / f'pr-{number:04d}' / 'journals' /
              f'{record["session_id"]}.json', source)
        count += 1
    return count


def validate_snapshot(snapshot, number):
    schema = logger.read_json(Path(__file__).with_name('interaction.schema.json'))
    # Derived fields are checked by deterministic recomputation, below.
    logger.validate_value({**snapshot, 'derived': {}}, schema)
    logger.require(set(snapshot) == {'schema_version', 'github', 'curated', 'derived'},
                   'unexpected ledger fields')
    logger.require(snapshot['schema_version'] == 1, 'unsupported ledger version')
    github = snapshot['github']
    logger.timestamp(github['captured_at'])
    pr = github['pull_request']
    logger.require(pr['number'] == number and pr['url'] == BASE + f'/pull/{number}',
                   'filename/PR identity mismatch')
    logger.require(pr['head'] is None or isinstance(pr['head'], str), 'invalid source branch')
    logger.require(re.fullmatch('[0-9a-f]{40}', pr['head_sha'] or '') is not None,
                   'full captured PR head required')
    logger.require(set(snapshot['curated']) == {'journal_links', 'agents', 'tools', 'events'},
                   'unexpected curation fields')


def validate_derived(root, snapshot, records):
    derived = snapshot['derived']
    logger.require(derived == derive(root, snapshot, records),
                   'stale interaction/accounting evidence; run ledger.py sync')
    ids = [e['id'] for e in derived['events']]
    logger.require(len(ids) == len(set(ids)), 'duplicate interaction ID')
    parties = {p['id'] for p in derived['parties']}
    account_ids = {a['id'] for a in derived['token_accounts']}
    for item in derived['events']:
        logger.require(item['type'] in TYPES and item['direction'] in ('action', 'reaction'),
                       'invalid interaction type/direction')
        logger.require(item['actor'] in parties, 'unknown interaction party')
        logger.require(set(item['recipients']) <= parties, 'unknown recipient')
        logger.require(set(item['token_accounts']) <= account_ids, 'unknown token account')
        logger.require(item['in_reply_to'] is None or item['in_reply_to'] in ids,
                       'unresolved response link')
    for category, activities in derived['tools'].items():
        for tool in activities:
            logger.require(tool['category'] == category and tool['evidence'] and tool['source'],
                           'tool category needs operation evidence and source')
            logger.require(category != 'codex_installed' or tool['provenance'],
                           'Codex-installed tool needs explicit installation evidence')
            logger.require(tool['token_account'] is None or tool['token_account'] in account_ids,
                           'tool references unknown token account')


def validate_visible(turn):
    logger.require(set(turn) == {'schema_version', 'thread_id', 'turn_id', 'status',
                                'started_at', 'completed_at', 'token_accounts', 'source',
                                'messages', 'native_tools', 'subagents', 'limitations'},
                   'unexpected visible-turn fields; private state is not supported')
    logger.require(turn['schema_version'] == 1 and turn['token_accounts'], 'invalid visible-turn snapshot')
    for message in turn['messages']:
        logger.require(set(message) == {'id', 'role', 'phase', 'text', 'redacted'}
                       and message['role'] in ('user', 'assistant')
                       and isinstance(message['text'], str), 'only visible user/assistant messages supported')
    for operation in turn['native_tools']:
        logger.require(set(operation) == {'name', 'calls', 'failures'}
                       and type(operation['calls']) is int and operation['calls'] > 0
                       and type(operation['failures']) is int
                       and 0 <= operation['failures'] <= operation['calls'], 'invalid native operation metadata')
    for child in turn['subagents']:
        logger.require(set(child) == {'thread_id', 'name', 'activity'}, 'invalid child metadata')


def gh(endpoint):
    return json.loads(subprocess.check_output(
        ['gh', 'api', '--paginate', '--slurp', endpoint], text=True))


def capture(number):
    """Explicit network capture. gh is a maintenance fallback, not telemetry."""
    def actor(item):
        return (item.get('user') or {}).get('login')

    def comment(item, review=False):
        return {'id': item['id'], 'url': item['html_url'],
                'body': item.get('body') or '', 'actor': actor(item),
                'created_at': item.get('created_at') or item.get('submitted_at'),
                'updated_at': item.get('updated_at'),
                'review': item.get('state') if review else None,
                'in_reply_to_id': item.get('in_reply_to_id'),
                'path': item.get('path'), 'line': item.get('line')}

    prefix = f'repos/{REPO}'
    pr = gh(f'{prefix}/pulls/{number}')[0]
    comments = [comment(c) for page in gh(f'{prefix}/issues/{number}/comments?per_page=100') for c in page]
    comments += [comment(c) for page in gh(f'{prefix}/pulls/{number}/comments?per_page=100') for c in page]
    comments += [comment(c, True) for page in gh(f'{prefix}/pulls/{number}/reviews?per_page=100') for c in page]
    # Linked issues are explicit and belong to this repository. No scraping of
    # arbitrary links or private upload payloads.
    text = pr.get('body', '') + '\n' + '\n'.join(c['body'] for c in comments)
    numbers = set(map(int, re.findall(re.escape(BASE) + r'/issues/(\d+)\b', text)))
    numbers.update(map(int, re.findall(r'\bissue\s*#\s*(\d+)\b', text, re.I)))
    issues = []
    for n in sorted(numbers):
        i = gh(f'{prefix}/issues/{n}')[0]
        if 'pull_request' in i:
            continue
        issues.append({'number': n, 'url': i['html_url'], 'title': i['title'],
                       'body': i.get('body') or '', 'actor': actor(i),
                       'created_at': i.get('created_at'),
                       'comments': [comment(c) for page in gh(f'{prefix}/issues/{n}/comments?per_page=100') for c in page]})
    return {'captured_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'pull_request': {'number': number, 'url': pr['html_url'],
                             'title': pr['title'], 'head': pr['head']['ref'],
                             'head_sha': pr['head']['sha'], 'state': pr['state'],
                             'body': pr.get('body') or '', 'actor': actor(pr),
                             'created_at': pr['created_at']},
            'comments': sorted(comments, key=lambda c: (c['created_at'] or '', c['url'])),
            'issues': issues}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('command', choices=('sync', 'validate', 'capture', 'snapshot-journals'))
    parser.add_argument('--pr', type=int)
    parser.add_argument('--snapshot', type=Path,
                        help='public, sanitized GitHub snapshot supplied by a connector')
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    try:
        records = logger.load_records(root)
        if args.command == 'capture':
            logger.require(args.pr is not None, 'capture requires --pr')
            path = path_for(root, args.pr)
            snapshot = logger.read_json(path) if path.exists() else {
                'schema_version': 1, 'curated': {'journal_links': [], 'agents': [], 'tools': [], 'events': []}}
            snapshot['github'] = logger.read_json(args.snapshot) if args.snapshot else capture(args.pr)
            snapshot['derived'] = {}
            validate_snapshot(snapshot, args.pr)
            snapshot['derived'] = derive(root, snapshot, records)
            validate_derived(root, snapshot, records)
            write(path, snapshot)
        else:
            paths = [path_for(root, args.pr)] if args.pr else sorted((root / 'interactions').glob('pr-*.json'))
            logger.require(paths, 'no PR interaction records found')
            for path in paths:
                number = int(path.stem.removeprefix('pr-'))
                snapshot = logger.read_json(path)
                validate_snapshot(snapshot, number)
                if args.command == 'snapshot-journals':
                    snapshot_journals(root, snapshot)
                if args.command in ('sync', 'snapshot-journals'):
                    snapshot['derived'] = derive(root, snapshot, records)
                validate_derived(root, snapshot, records)
                if args.command in ('sync', 'snapshot-journals'):
                    write(path, snapshot)
            print(f'{args.command}: {len(paths)} PR interaction records; canonical usage unchanged')
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError, KeyError, TypeError) as error:
        print(f'Interaction ledger: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
