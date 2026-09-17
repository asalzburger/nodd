"""Validate curated records and build the dashboard using the standard library."""
import argparse
from datetime import date, datetime, timezone
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE = ('DRAFT', 'TECHNICAL REVIEW', 'EXPERT REVIEW', 'SIGNED OFF',
             'IMPLEMENTED', 'VALIDATED', 'ACCEPTED')


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def schema_check(value, schema, at='record'):
    """Strict validator for the explicitly supported schema subset."""
    allowed = {'$schema', 'type', 'properties', 'required', 'additionalProperties',
               'items', 'enum', 'minLength'}
    require(not set(schema) - allowed, f'{at}: unsupported schema keywords')
    kinds = schema['type']
    kinds = [kinds] if isinstance(kinds, str) else kinds
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'boolean': bool, 'null': type(None)}
    require(any(type(value) is types[k] for k in kinds), f'{at}: expected {kinds}')
    if 'enum' in schema:
        require(value in schema['enum'], f'{at}: invalid value {value!r}')
    if isinstance(value, str):
        require(len(value.strip()) >= schema.get('minLength', 0), f'{at}: empty value')
    if isinstance(value, dict):
        require(not set(schema['required']) - value.keys(), f'{at}: missing fields')
        require(not set(value) - schema['properties'].keys(), f'{at}: unknown fields')
        for key, item in value.items():
            schema_check(item, schema['properties'][key], f'{at}.{key}')
    if isinstance(value, list):
        for index, item in enumerate(value):
            schema_check(item, schema['items'], f'{at}[{index}]')


def local_path(root, path):
    require(not urlsplit(path).scheme and not urlsplit(path).netloc,
            f'Expected repository path: {path}')
    require('\\' not in path and not Path(path).is_absolute(), f'Unsafe path: {path}')
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), f'Path escapes repository: {path}')
    require(not any(part.startswith('.') for part in Path(path).parts), f'Hidden path: {path}')
    require(resolved.is_file(), f'Missing evidence: {path}')
    require('TEMPLATE' not in resolved.name.upper(), f'Template is not evidence: {path}')
    return resolved


def evidence_path(root, path):
    parsed = urlsplit(path)
    if parsed.scheme or parsed.netloc:
        require(parsed.scheme == 'https' and parsed.hostname and not parsed.username
                and not parsed.password, f'Unsafe evidence URL: {path}')
        return None
    return local_path(root, path)


def iso_date(value, at):
    if value is not None:
        try:
            require(date.fromisoformat(value).isoformat() == value, f'{at}: use YYYY-MM-DD')
        except ValueError as exc:
            raise Invalid(f'{at}: invalid date') from exc


def utc_timestamp(value, at):
    require(isinstance(value,str) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',value)), f'{at}: use UTC YYYY-MM-DDTHH:MM:SSZ')
    try:
        datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as exc:
        raise Invalid(f'{at}: invalid timestamp') from exc


def index(items):
    found = {}
    for item in items:
        require(re.fullmatch(r'[A-Za-z][A-Za-z0-9-]*', item['id']), 'Invalid stable ID')
        require(item['id'] not in found, f'Duplicate ID: {item["id"]}')
        found[item['id']] = item
    return found


def acyclic(items, key='dependencies'):
    visiting, done = set(), set()
    def visit(identifier):
        require(identifier in items, f'Unknown dependency: {identifier}')
        require(identifier not in visiting, f'Dependency cycle: {identifier}')
        if identifier in done:
            return
        visiting.add(identifier)
        for dep in items[identifier][key]:
            visit(dep)
        visiting.remove(identifier)
        done.add(identifier)
    for identifier in items:
        visit(identifier)


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    require(result.returncode == 0, 'Cannot resolve Git evidence: ' + ' '.join(args))
    return result.stdout


def document_state(text):
    match = re.search(r'^- Status:\s*(.+)$', text, re.M)
    require(match, 'Unsupported document: missing Status field')
    declared = re.sub(r'\*\*|__', '', match[1]).strip()
    status = next((s for s in LIFECYCLE if declared == s or declared.startswith(s + ' —')
                   or declared.startswith(s + ' –') or declared.startswith(s + ';')), None)
    require(status is not None, f'Unsupported document status: {declared}')
    return status


def normalize(root):
    records = {}
    for name in ('tracking', 'reviews'):
        data = json.loads((root / f'project/{name}.json').read_text())
        schema = json.loads((ROOT / f'project/{name}.schema.json').read_text())
        schema_check(data, schema, name)
        records[name] = data
    t, r = records['tracking'], records['reviews']
    iso_date(t['updated'], 'tracking.updated')
    stages, milestones, streams, tasks, documents = [index(t[k]) for k in
        ('stages', 'milestones', 'workstreams', 'tasks', 'documents')]
    all_ids = [item['id'] for key in ('stages','milestones','workstreams','tasks','documents')
               for item in t[key]] + [item['id'] for item in r['rounds']] + [item['id'] for item in t.get('pull_requests', [])]
    require(len(all_ids) == len(set(all_ids)), 'IDs must be globally unique')
    acyclic(stages)
    acyclic(tasks)
    paths = set()
    for group in (t['stages'], t['milestones'], t['tasks']):
        for item in group:
            for path in item['evidence'] + item.get('deliverables', []):
                evidence_path(root, path)
                paths.add(path)
    for item in t['evidence']:
        evidence_path(root, item['path'])
        paths.add(item['path'])
    for item in t['stages']:
        require(set(item['milestones']) <= milestones.keys(), 'Unknown stage milestone')
    for item in t['tasks']:
        require(item['stage'] in stages and item['workstream'] in streams, 'Unknown task stage/stream')
        require(set(item['milestones']) <= milestones.keys(), 'Unknown task milestone')
        require(set(item['documents']) <= documents.keys(), 'Unknown task document')
        require(item['role'] == streams[item['workstream']]['role'], 'Task/stream role mismatch')
        iso_date(item['updated'], item['id'])
        require(item['state'] != 'blocked' or bool(item['blocker']), 'Blocked task needs a reason')
        require(item['state'] != 'completed' or (item['deliverables'] and item['disposition']),
                'Completed task needs deliverables and disposition')
        require(item['state'] != 'cancelled' or item['disposition'], 'Cancelled task needs disposition')
        if item['state'] in ('ready', 'active'):
            require(all(tasks[d]['state'] == 'completed' for d in item['dependencies']),
                    'Ready/active task has unfinished dependencies')
    for doc in t['documents']:
        path = local_path(root, doc['path'])
        require(re.fullmatch(r'(ADR|DES)-\d{3}', doc['id']), 'Unsupported document ID')
        require(path.name.startswith(doc['id'] + '-'), 'Document ID/path mismatch')
        doc['state'] = document_state(path.read_text())
        doc['content_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        doc['warnings'] = []
        paths.add(doc['path'])
        for report in doc['validation_reports']:
            local_path(root, report)
            require(report.startswith('docs/validation/'), 'Wrong validation-report directory')
            paths.add(report)
    for pr in t.get('pull_requests', []):
        require(pr['number'] > 0, 'PR number must be positive')
        evidence_path(root, pr['url'])
        require(urlsplit(pr['url']).scheme == 'https' and
                urlsplit(pr['url']).path.endswith('/pull/' + str(pr['number'])), 'PR URL/number mismatch')
        require(pr['task'] in tasks and set(pr['documents']) <= documents.keys(), 'Unknown PR task/document')
        require(set(pr['documents']) <= set(tasks[pr['task']]['documents']), 'PR documents not linked to task')
        require(re.fullmatch(r'[0-9a-f]{40}', pr['head_revision']), 'PR needs full head SHA')
        utc_timestamp(pr['collected_at'], 'PR collection time')
        if pr['state'] == 'merged':
            require(pr['merge_commit'] and re.fullmatch(r'[0-9a-f]{40}', pr['merge_commit']), 'Merged PR needs full merge SHA')
            utc_timestamp(pr['merged_at'], 'PR merge time')
            require(pr['merged_at'] <= pr['collected_at'], 'PR collection predates merge')
            git(root, 'cat-file', '-e', pr['merge_commit'] + '^{commit}')
            require(subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',
                                    pr['head_revision'],pr['merge_commit']], capture_output=True).returncode == 0,
                    'PR merge does not include head revision')
        else:
            require(pr['merge_commit'] is None and pr['merged_at'] is None, 'Unmerged PR has merge metadata')
    rounds = index(r['rounds'])
    for review in r['rounds']:
        require(review['task'] in tasks and review['document'] in documents, 'Unknown review target')
        require(review['document'] in tasks[review['task']]['documents'], 'Review document not linked to task')
        require(re.fullmatch(r'[0-9a-f]{40}', review['target_revision']), 'Review needs full commit SHA')
        iso_date(review['requested_at'], review['id'])
        iso_date(review['completed_at'], review['id'])
        require(review['state'] not in ('requested','open') or
                (review['outcome'] == 'pending' and review['completed_at'] is None),
                'Open review cannot have completed outcome')
        require(review['state'] != 'closed' or
                (review['outcome'] != 'pending' and review['completed_at']), 'Closed review needs outcome/date')
        require(review['state'] != 'withdrawn' or review['outcome'] == 'pending',
                'Withdrawn round cannot confer approval')
        if review['requested_at'] and review['completed_at']:
            require(review['completed_at'] >= review['requested_at'], 'Review dates are reversed')
        if review['supersedes']:
            require(review['supersedes'] in rounds, 'Unknown superseded round')
            old = rounds[review['supersedes']]
            require(old['document'] == review['document'] and old['task'] == review['task'],
                    'Superseded round has different target')
        for path in review['evidence']:
            evidence_path(root, path)
            paths.add(path)
        doc = documents[review['document']]
        historical = git(root, 'show', f'{review["target_revision"]}:{doc["path"]}')
        review['target_matches_current'] = historical == (root / doc['path']).read_bytes()
        review['approval_supported'] = False
        review['warnings'] = []
        if review['outcome'] in ('approved','conditional'):
            require(review['state'] == 'closed', 'Approval must be a closed review')
            require(review['reviewers'] and all(x['human'] for x in review['reviewers']),
                    'Approval requires identified human reviewers')
            require(review['evidence'], 'Approval requires evidence')
            require(review['outcome'] != 'conditional' or review['conditions'],
                    'Conditional review needs conditions')
            if review['type'] in ('sign-off','acceptance'):
                require(review['approval_record'], 'Sign-off/acceptance needs formal record')
                path = local_path(root, review['approval_record'])
                require(review['approval_record'].startswith('docs/signoff/'), 'Wrong approval-record directory')
                record = path.read_text()
                require(review['target_revision'] in record and doc['id'] in record,
                        'Approval record does not identify target')
                require(all(person['name'] in record for person in review['reviewers']),
                        'Reviewer not identified in approval record')
                require(all(link in record for link in review['evidence']),
                        'Approval evidence not linked from formal record')
                require(re.search(r'Review date.*' + review['completed_at'], record),
                        'Approval date missing from formal record')
                outcome = re.findall(r'^- Outcome:\s*(.+)$', record, re.M)
                require(any(x.strip().lower() in ('approved','conditional','signed off','accepted')
                            for x in outcome), 'Formal record lacks human approval outcome')
                paths.add(review['approval_record'])
                review['approval_supported'] = (review['outcome'] == 'approved' and
                                               (not review['conditions'] or review['conditions_resolved']))
                if review['conditions_resolved'] and review['conditions']:
                    require(re.search(r'Human confirmation of resolution:\s*\S', record),
                            'Resolved conditions lack human confirmation')
        if not review['target_matches_current']:
            if any(x['supersedes'] == review['id'] for x in r['rounds']):
                review['warnings'].append('Historical review target differs from current content; a later round is recorded.')
            else:
                review['warnings'].append('Reviewed document differs from current content; current revision needs review.')
        if review['conditions'] and not review['conditions_resolved']:
            review['warnings'].append('Approval conditions remain open.')
        elif review['outcome'] == 'conditional':
            review['warnings'].append('Conditional outcome requires final human approval.')
    acyclic({k: {'dependencies': [v['supersedes']] if v['supersedes'] else []}
             for k,v in rounds.items()})
    for doc in t['documents']:
        if doc['state'] == 'DRAFT' and any(x['document'] == doc['id'] and x['outcome'] == 'approved'
                and x['target_matches_current'] for x in r['rounds']):
            doc['warnings'].append('Human review approval is recorded; the document still declares DRAFT. Formal sign-off is not established.')
        supporting = [x for x in r['rounds'] if x['document'] == doc['id'] and
                      x['approval_supported'] and x['target_matches_current']]
        if doc['state'] in LIFECYCLE[3:] and not any(x['type'] == 'sign-off' for x in supporting):
            doc['warnings'].append('Declared lifecycle lacks current-revision human sign-off evidence.')
        if doc['state'] in ('VALIDATED', 'ACCEPTED') and not doc['validation_reports']:
            doc['warnings'].append('Declared validation lacks a linked validation report; execution and acceptance are not established.')
        if doc['state'] == 'ACCEPTED' and not any(x['type'] == 'acceptance' for x in supporting):
            doc['warnings'].append('Declared acceptance lacks current-revision human acceptance evidence.')
    records['paths'] = sorted(paths)
    return records


def text(value):
    return escape(str(value if value is not None else 'Unassigned'), quote=True)


def evidence_name(path):
    return hashlib.sha256(path.encode()).hexdigest()[:20] + '.html'


def href(path):
    return path if urlsplit(path).scheme else 'evidence/' + evidence_name(path)


def links(paths):
    return ' · '.join(f'<a href="{text(href(p))}">{text(p)}</a>' for p in paths) or 'None recorded'


def badge(state):
    return f'<span class="badge {text(state.lower().replace(" ", "-"))}">{text(state)}</span>'


def warnings(items):
    return ''.join(f'<p class="warning">{text(w)}</p>' for w in items)


def render(records, metadata):
    t, r = records['tracking'], records['reviews']
    parts = []
    def add(s):
        parts.append(s)
    add('<section id="overview"><p class="eyebrow">PROJECT CONTROL ROOM</p><h1>A coherent detector.<br>A traceable programme.</h1>')
    add('<p class="lead">Track architecture, parallel work and human review across the ODD → nODD programme.</p>')
    add(f'<p class="notice">{text(t["note"])}</p><div class="metrics">')
    for title, count, detail in [('Active tasks',sum(x['state']=='active' for x in t['tasks']),f'of {len(t["tasks"])} tracked tasks'),('Blocked tasks',sum(x['state']=='blocked' for x in t['tasks']),'Reasons and next actions below'),('Open reviews',sum(x['state'] in ('requested','open') for x in r['rounds']),'Formal recorded rounds only'),('Draft decisions',sum(x['state']=='DRAFT' for x in t['documents']),f'of {len(t["documents"])} tracked documents')]:
        add(f'<article><strong>{count}</strong><h2>{title}</h2><p>{detail}</p></article>')
    add('</div><h2>Current focus</h2><div class="cards">')
    for stage in t['stages']:
        if stage['state'] == 'active':
            add(f'<article><p class="eyebrow">STAGE {text(stage["id"])}</p><h3>{text(stage["title"])}</h3>{badge(stage["state"])}<p>{text(stage["disposition"])}</p>{links(stage["evidence"])}</article>')
    add('</div>')
    add('<h2>Recorded pull requests</h2>')
    if not t.get('pull_requests'):
        add('<p class="empty">No pull request snapshots recorded.</p>')
    for pr in t.get('pull_requests', []):
        related = [x for x in r['rounds'] if x['task'] == pr['task'] and x['outcome'] == 'approved'
                   and x['target_matches_current'] and x['target_revision'] == pr['head_revision']]
        approval_badge = badge('Review approved') if related else ''
        add(f'<article id="{text(pr["id"])}"><p class="eyebrow">PR #{pr["number"]}</p><h3><a href="{text(pr["url"])}">{text(pr["title"])}</a></h3>{badge(pr["state"])} {approval_badge}<p>{text(pr["scope"])}</p><p><a href="#{text(pr["task"])}">Work item &amp; deliverables</a></p><dl><dt>Recorded approval</dt><dd>'+(' · '.join(f'<a href="#{text(x["id"])}">{text(x["type"])} review approved</a>' for x in related) or 'None recorded')+f'</dd><dt>Merged at</dt><dd>{text(pr["merged_at"] or "Not merged")}</dd><dt>Merge commit</dt><dd>{text(pr["merge_commit"] or "None")}</dd><dt>Snapshot collected</dt><dd>{text(pr["collected_at"])}</dd></dl><p class="notice">Merge state and review outcome are distinct from the declared design lifecycle.</p></article>')
    add('</section><section id="programme"><p class="eyebrow">DIRECTION & GATES</p><h2>Programme</h2><p>Stages describe execution. Milestones describe deliverables and acceptance; their completion is tracked separately.</p><div class="stage-grid">')
    for stage in t['stages']:
        stage_dependencies = ' · '.join(f'<a href="#stage-{text(d)}">{text(d)}</a>' for d in stage['dependencies']) or 'None'
        add(f'<article id="stage-{text(stage["id"])}"><p class="eyebrow">STAGE {text(stage["id"])}</p><h3>{text(stage["title"])}</h3>{badge(stage["state"])}<p>{text(stage["disposition"])}</p><dl><dt>Milestones</dt><dd>{text(", ".join(stage["milestones"]))}</dd><dt>Depends on</dt><dd>{stage_dependencies}</dd><dt>Entry</dt><dd>{text(stage["entry"])}</dd><dt>Exit / disposition</dt><dd>{text(stage["exit"])}</dd></dl>{links(stage["evidence"])}</article>')
    add('</div><h3>Milestones</h3><div class="table-wrap"><table><thead><tr><th>ID</th><th>Milestone</th><th>State</th><th>Disposition</th></tr></thead><tbody>')
    for m in t['milestones']:
        add(f'<tr><th scope="row">{text(m["id"])}</th><td>{text(m["title"])}</td><td>{badge(m["state"])}</td><td>{text(m["disposition"])} {links(m["evidence"])}</td></tr>')
    add('</tbody></table></div></section><section id="work"><p class="eyebrow">PARALLEL DELIVERY</p><h2>Workstreams</h2><p>Role mandates are proposed assignments. Human owners and running agents are not inferred.</p><form class="filters" id="work-filters">')
    for key,label,values in [('stage','Stage',[x['id'] for x in t['stages']]),('milestone','Milestone',[x['id'] for x in t['milestones']]),('role','Role',[x['role'] for x in t['workstreams']]),('subsystem','Subsystem',sorted({x['subsystem'] for x in t['tasks']})),('state','Work state',['planned','ready','active','blocked','completed','cancelled'])]:
        add(f'<label>{label}<select name="{key}"><option value="">All</option>'+''.join(f'<option>{text(v)}</option>' for v in values)+'</select></label>')
    add('<label>Search<input name="q" type="search" placeholder="Task, scope or ID"></label><button type="reset">Reset</button></form><p id="work-count" role="status"></p><div class="lanes">')
    for stream in t['workstreams']:
        add(f'<section class="lane"><h3>{text(stream["title"])}</h3>')
        for task in t['tasks']:
            if task['workstream'] != stream['id']:
                continue
            attrs = ' '.join(f'data-{k}="{text(v)}"' for k,v in [('stage',task['stage']),('milestone',' '.join(task['milestones'])),('role',task['role']),('subsystem',task['subsystem']),('state',task['state'])])
            add(f'<article class="task" id="{text(task["id"])}" {attrs}><p class="eyebrow">{text(task["id"])}</p><h4>{text(task["title"])}</h4>{badge(task["state"])}<p>{text(task["scope"])}</p><p class="next">Next: {text(task["next_action"])}</p><details><summary>Details & evidence</summary><dl>')
            for key,value in [('Owner',task['owner']),('Subsystem',task['subsystem']),('Stage / milestones',task['stage']+' / '+', '.join(task['milestones'])),('Last record update',task['updated']),('Blocker',task['blocker'] or 'None recorded'),('Disposition',task['disposition'] or 'None recorded')]:
                add(f'<dt>{key}</dt><dd>{text(value)}</dd>')
            deps=' · '.join(f'<a href="#{text(d)}">{text(d)}</a>' for d in task['dependencies']) or 'None'
            document_links = links([d['path'] for d in t['documents'] if d['id'] in task['documents']])
            add(f'<dt>Dependencies</dt><dd>{deps}</dd><dt>Deliverables</dt><dd>{links(task["deliverables"])}</dd><dt>Evidence</dt><dd>{links(task["evidence"])}</dd><dt>Documents</dt><dd>{document_links}</dd><dt>Review rounds</dt><dd>')
            add(' · '.join(f'<a href="#{text(x["id"])}">{text(x["id"])}</a>' for x in r['rounds'] if x['task']==task['id']) or 'None recorded')
            add('</dd></dl></details><a class="permalink" href="#'+text(task['id'])+'">Link to task</a></article>')
        add('</section>')
    add('</div><p class="empty" id="work-empty" hidden>No tasks match these filters.</p></section><section id="reviews"><p class="eyebrow">HUMAN REVIEW</p><h2>Review queue & archive</h2><p>Review closure, task completion and human sign-off have independent meanings.</p><form class="filters" id="review-filters">')
    for key,label,values in [('review-type','Review type',['technical','expert','sign-off','validation','acceptance']),('review-state','Round state',['requested','open','closed','withdrawn'])]:
        add(f'<label>{label}<select name="{key}"><option value="">All</option>'+''.join(f'<option>{text(v)}</option>' for v in values)+'</select></label>')
    add('<button type="reset">Reset</button></form><p id="review-count" role="status"></p>')
    add(f'<p class="notice">{text(r["note"])}</p>')
    for title,states in [('Open queue',('requested','open')),('Closed / withdrawn archive',('closed','withdrawn'))]:
        add(f'<h3>{title}</h3>')
        group=[x for x in r['rounds'] if x['state'] in states]
        if not group:
            add('<p class="empty">No recorded rounds.</p>')
        for rev in group:
            add(f'<article class="review" id="{text(rev["id"])}" data-review-type="{text(rev["type"])}" data-review-state="{text(rev["state"])}"><h4>{text(rev["id"])} · {text(rev["document"])}</h4>{badge(rev["state"])} {badge(rev["outcome"])}<p>{text(rev["type"])} review · <a href="#{text(rev["task"])}">{text(rev["task"])}</a></p><dl>')
            for label,value in [('Scope',rev.get('scope','See review evidence')),('Review summary',rev.get('summary','See review evidence')),('Exact target revision',rev['target_revision']),('Requested',rev['requested_at'] or 'Unknown'),('Completed',rev['completed_at'] or 'Not recorded'),('Reviewers',', '.join(x['name']+' ('+x['role']+')' for x in rev['reviewers']) or 'Unassigned'),('Conditions','; '.join(rev['conditions']) or 'None recorded'),('Supersedes',rev['supersedes'] or 'None'),('Formal approval support','Recorded for target revision' if rev['approval_supported'] else 'Not established')]:
                add(f'<dt>{label}</dt><dd>{text(value)}</dd>')
            add(f'</dl>{warnings(rev["warnings"])}{links(rev["evidence"] + ([rev["approval_record"]] if rev["approval_record"] else []))}</article>')
    add('<p class="empty" id="review-empty" hidden>No review rounds match these filters.</p><h3>Document lifecycle</h3><div class="cards">')
    for doc in t['documents']:
        validation_links = links(doc['validation_reports'])
        add(f'<article><h4>{text(doc["id"])}</h4>{badge(doc["state"])}{warnings(doc["warnings"])}<p>{links([doc["path"]])}</p><p>Validation reports: {validation_links}</p></article>')
    add('</div></section><section id="evidence"><p class="eyebrow">CANONICAL RECORD</p><h2>Evidence & history</h2><p>Selected evidence pointers; this is not an exhaustive claim or TDR coverage audit. Check execution and scientific acceptance in the linked reports.</p><div class="cards">')
    for ev in t['evidence']:
        add(f'<article><p class="eyebrow">{text(ev["kind"])}</p><h3>{text(ev["title"])}</h3>{links([ev["path"]])}</article>')
    add('</div></section>')
    return '\n'.join(parts)


def build(root, output, built_at):
    root, output = root.resolve(), output.resolve()
    # Never let a caller overwrite canonical input with generated files.
    if output.is_relative_to(root):
        rel = output.relative_to(root)
        require(rel.parts and rel.parts[0] == '_site', 'Repository output must be inside _site/')
    require(not root.is_relative_to(output), 'Output cannot contain the repository')
    data = normalize(root)
    sha = git(root, 'rev-parse', 'HEAD').decode().strip()
    dirty = bool(git(root, 'status', '--porcelain').strip())
    metadata = {'source_commit':sha,'working_tree_dirty':dirty,'built_at':built_at,
                'data_updated':data['tracking']['updated'],'external_snapshot_at':None}
    template = (root / 'dashboard/index.html').read_text()
    require(template.count('{{CONTENT}}') == template.count('{{METADATA}}') == 1,
            'Invalid dashboard template')
    footer = (f'Source <code>{sha}</code> · {"Working tree includes uncommitted changes" if dirty else "Clean checkout"}'
              f'<br>Built {text(built_at)} · Tracking last updated {text(metadata["data_updated"])}'
              '<br>Git-backed snapshot; external GitHub collection is not enabled. '
              '<a href="snapshot.json">Download snapshot</a>')
    # Only generated allowlisted files are part of this snapshot. Reusing an output
    # directory must not retain superseded evidence or unexpected files.
    expected = {'index.html','style.css','app.js','snapshot.json'} | {
        'evidence/'+evidence_name(p) for p in data['paths'] if not urlsplit(p).scheme}
    for existing in output.rglob('*'):
        require(not existing.is_symlink(), 'Symlink in output')
        if existing.is_file() and existing.relative_to(output).as_posix() not in expected:
            raise Invalid('Unexpected/stale output file; use a fresh output directory: '+str(existing))
    source_pages = {}
    for path in data['paths']:
        source = evidence_path(root, path)
        if source is not None:
            require(source.suffix in ('.md','.json','.yaml'), 'Only curated text evidence can be exported')
            source_pages[path] = source.read_text()
    output.mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(template.replace('{{CONTENT}}',render(data,metadata)).replace('{{METADATA}}',footer))
    for name in ('style.css','app.js'):
        (output / name).write_bytes((root / 'dashboard' / name).read_bytes())
    evidence_dir = output / 'evidence'
    evidence_dir.mkdir(exist_ok=True)
    for path in data['paths']:
        source = evidence_path(root, path)
        if source is None:
            continue
        content = source_pages[path]
        page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="../style.css"><title>'+text(path)+' · nODD</title><body><main><a href="../index.html#evidence">← Dashboard</a><h1>'+text(path)+'</h1><p class="notice">Escaped source document from this build. Relative Markdown links remain source text.</p><pre class="source">'+text(content)+'</pre><footer>'+footer.replace('href="snapshot.json"','href="../snapshot.json"')+'</footer></main></body></html>'
        (evidence_dir / evidence_name(path)).write_text(page)
    (output / 'snapshot.json').write_text(json.dumps({'metadata':metadata,**data},indent=2)+'\n')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('validate','build'))
    parser.add_argument('--repo',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,default=ROOT / '_site/dashboard')
    parser.add_argument('--built-at',default=None,help='Fixed UTC timestamp for reproducible builds')
    args=parser.parse_args()
    try:
        if args.command == 'validate':
            data=normalize(args.repo)
            print(f'Validated {len(data["tracking"]["tasks"])} tasks, {len(data["tracking"]["documents"])} documents and {len(data["reviews"]["rounds"])} review rounds.')
        else:
            timestamp=args.built_at or datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
            require(timestamp.endswith('Z'), 'Build time must be UTC with Z suffix')
            datetime.fromisoformat(timestamp.replace('Z','+00:00'))
            print('Built '+str(build(args.repo,args.output,timestamp)))
    except (Invalid,ValueError,OSError,KeyError) as exc:
        print('Dashboard error: '+str(exc),file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
