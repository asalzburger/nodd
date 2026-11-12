"""Read-only provenance guard for the ECAL PR133→137 chain.

This checks retained Git/record identity, not live GitHub readiness, usage
completeness, scientific acceptance or approval. Full record/ledger validators
remain separate. Only an explicitly requested new JSON report is written.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CHAIN = tuple(range(133, 138))
ARTIFACT = 'docs/validation/ecal-highstat/frozen'
CORE = 'software/analysis/calorimeter_digitization/highstat_model.py'
COUNTERS = ('input_tokens', 'cached_input_tokens', 'output_tokens',
            'reasoning_output_tokens', 'total_tokens')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    require(result.returncode == 0, 'Cannot resolve Git evidence: ' + ' '.join(args))
    return result.stdout


def commit(repo, value, label):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{40}', value), label + ' requires a full commit SHA')
    git(repo, 'cat-file', '-e', value + '^{commit}')
    return value


def is_ancestor(repo, earlier, later):
    result = subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', earlier, later], capture_output=True)
    require(result.returncode in (0, 1), 'Cannot inspect Git ancestry: ' + earlier + ' → ' + later)
    return result.returncode == 0


def ancestor(repo, earlier, later, label):
    require(is_ancestor(repo, earlier, later), label + ': expected ' + earlier + ' to be an ancestor of ' + later)


def chain_link(repo, earlier_head, later_head, later_record, label):
    if is_ancestor(repo, earlier_head, later_head):
        return 'forward'
    # A dependent PR can already have been merged into its predecessor's
    # branch. Accept reversed heads only with that recorded merge proof.
    require(later_record['state'] == 'merged', label + ': reversed heads require a recorded merged dependent')
    merged = commit(repo, later_record['merge_commit'], label + ' absorbed merge')
    ancestor(repo, later_head, merged, label + ': absorbed dependent head is absent from its merge')
    ancestor(repo, merged, earlier_head, label + ': dependent merge was not absorbed by the earlier head')
    return 'absorbed_dependent'


def read(repo, path):
    return json.loads((repo / path).read_text())


def coverage(repo, ledgers):
    """Reference unique canonical owners without adding PR-linked token totals."""
    owners = {}
    external = set()
    for number, ledger in ledgers.items():
        for account in ledger.get('derived', {}).get('token_accounts', []):
            if not account.get('scope', '').startswith('canonical_session'):
                external.add(account['id'])
                continue
            identifier, path = account['id'], account['record']
            resolved = (repo / path).resolve()
            require(not Path(path).is_absolute() and resolved.is_relative_to(repo)
                    and path.startswith(('logs/codex/', 'logs/design/')) and path.endswith('.json'),
                    'Unsafe canonical account path: ' + path)
            if identifier not in owners:
                record = json.loads(resolved.read_text())
                require(record['session_id'] == identifier, 'Canonical account identity mismatch: ' + identifier)
                usage = record['usage']
                owners[identifier] = dict(session_id=identifier, title=record['title'], record=path,
                    pull_requests=[], observed_turns=len(usage),
                    counters_known={field: sum(entry.get(field) is not None for entry in usage) for field in COUNTERS})
            require(owners[identifier]['record'] == path, 'Conflicting canonical account paths: ' + identifier)
            if number not in owners[identifier]['pull_requests']:
                owners[identifier]['pull_requests'].append(number)
    return dict(canonical_owners=[owners[k] for k in sorted(owners)],
        noncanonical_references=sorted(external),
        definition='Unique canonical owners referenced by the retained ledgers; known counter fields per owned turn. No PR token totals are added. Completeness/arithmetic are checked by the existing usage and ledger validators.')


def check(repo=ROOT, require_merged=False):
    repo = Path(repo).resolve()
    head = git(repo, 'rev-parse', 'HEAD').decode().strip()
    tracking = read(repo, 'project/tracking.json')
    selected, ledgers = {}, {}
    for number in CHAIN:
        matches = [pr for pr in tracking['pull_requests'] if pr['number'] == number]
        require(len(matches) == 1, f'Require exactly one tracking entry for PR{number}')
        pr = matches[0]
        selected[number] = pr
        recorded = commit(repo, pr['head_revision'], f'PR{number} tracking head')
        ancestor(repo, recorded, head, f'PR{number} tracking head is not retained in checked HEAD')
        ledger = read(repo, f'interactions/pr-{number:04d}.json')
        observed = ledger['github']['pull_request']
        require(observed['number'] == number, f'PR{number} interaction identity differs')
        captured = commit(repo, observed['head_sha'], f'PR{number} interaction head')
        ancestor(repo, captured, head, f'PR{number} interaction head is not retained in checked HEAD')
        ledgers[number] = ledger
        require(pr['state'] in ('open', 'closed', 'merged'), f'PR{number} has unsupported recorded state')
        require(not require_merged or pr['state'] == 'merged', f'PR{number} is not recorded merged')
        if pr['state'] == 'merged':
            merged = commit(repo, pr['merge_commit'], f'PR{number} merge')
            ancestor(repo, recorded, merged, f'PR{number} recorded merge does not include its head')
            ancestor(repo, captured, merged, f'PR{number} recorded merge does not include its captured interaction head')
            ancestor(repo, merged, head, f'PR{number} recorded merge is detached from checked HEAD')
        else:
            require(pr.get('merge_commit') is None and pr.get('merged_at') is None,
                    f'PR{number} has merge metadata despite an unmerged state')
    links = []
    for earlier, later in zip(CHAIN, CHAIN[1:]):
        tracking_link = chain_link(repo, selected[earlier]['head_revision'], selected[later]['head_revision'],
                                   selected[later], f'Tracking chain PR{earlier}→PR{later} is reordered or incomplete')
        interaction_link = chain_link(repo, ledgers[earlier]['github']['pull_request']['head_sha'],
                                      ledgers[later]['github']['pull_request']['head_sha'], selected[later],
                                      f'Interaction chain PR{earlier}→PR{later} is reordered or incomplete')
        links.append(dict(earlier=earlier, later=later, tracking=tracking_link, interaction=interaction_link))
    manifest = read(repo, ARTIFACT + '/manifest.json')
    require(manifest['schema_version'] == 1 and manifest['coefficients_file'] == 'models.json',
            'Unsupported frozen calibration artifact')
    freeze = commit(repo, manifest['freeze_commit'], 'Calibration freeze')
    validated = commit(repo, manifest['validated_results_commit'], 'Validated results')
    ancestor(repo, freeze, validated, 'Validated results do not retain the calibration freeze')
    ancestor(repo, freeze, head, 'Calibration freeze is not retained in checked HEAD')
    ancestor(repo, validated, head, 'Validated results are not retained in checked HEAD')
    coefficient_path = ARTIFACT + '/models.json'
    coefficients = (repo / coefficient_path).read_bytes()
    require(digest(coefficients) == manifest['coefficients_sha256'], 'Current coefficient hash differs from the frozen manifest')
    require(coefficients == git(repo, 'show', freeze + ':' + coefficient_path),
            'Current coefficient bytes differ from the Git freeze')
    model = json.loads(coefficients)
    core = (repo / CORE).read_bytes()
    require(digest(core) == model['core_sha256'], 'Current numerical core differs from the frozen core hash')
    require(core == git(repo, 'show', freeze + ':' + CORE), 'Current numerical core bytes differ from the Git freeze')
    return dict(status='PASS', checked_head=head, require_merged=require_merged, chain_links=links,
        chain=[dict(number=n, state=selected[n]['state'], head_revision=selected[n]['head_revision'],
                    interaction_head=ledgers[n]['github']['pull_request']['head_sha'],
                    merge_commit=selected[n].get('merge_commit'), merged_at=selected[n].get('merged_at')) for n in CHAIN],
        calibration=dict(freeze_commit=freeze, validated_results_commit=validated,
                         coefficients_sha256=digest(coefficients), core_sha256=digest(core)),
        record_hashes={path: digest((repo / path).read_bytes()) for path in
                      ['project/tracking.json', ARTIFACT + '/manifest.json'] +
                      [f'interactions/pr-{n:04d}.json' for n in CHAIN]},
        work_coverage=coverage(repo, ledgers),
        scope='Retained source/record integrity only. No live GitHub readiness, automatic metadata capture, usage completeness, design sign-off or detector acceptance.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--require-merged', action='store_true', help='Require all five existing records to report merged')
    parser.add_argument('--output', type=Path, help='Optional new compact JSON report; parent directory must exist')
    args = parser.parse_args(argv)
    try:
        result = check(args.repo, args.require_merged)
        payload = json.dumps(result, separators=(',', ':'), allow_nan=False) + '\n'
        if args.output:
            with args.output.open('x') as stream:
                stream.write(payload)
        print(payload, end='')
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('ECAL chain: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
