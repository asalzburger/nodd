"""Validate scientific project/review records without building a website."""
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

from check_update import is_chore

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
        require(item.get('category', 'project') != 'chore', 'Chore tasks must not enter project progress tracking')
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
        require(pr.get('category', 'project') != 'chore' and not is_chore(pr['title']),
                'Chore PRs must not enter project progress tracking')
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


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=ROOT)
    args=parser.parse_args()
    try:
        data=normalize(args.repo.resolve())
        print(f"Validated {len(data['tracking']['tasks'])} tasks, {len(data['tracking']['documents'])} documents and {len(data['reviews']['rounds'])} review rounds.")
    except (Invalid,ValueError,OSError,subprocess.CalledProcessError) as error:
        print(str(error),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    sys.exit(main())
