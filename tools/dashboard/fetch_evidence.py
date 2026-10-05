"""Fetch recorded historical Git evidence before offline dashboard validation."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def required_revisions(root):
    tracking = json.loads((root / 'project/tracking.json').read_text())
    reviews = json.loads((root / 'project/reviews.json').read_text())
    revisions = [review['target_revision'] for review in reviews['rounds']]
    for pr in tracking.get('pull_requests', []):
        if pr['state'] == 'merged':
            revisions.extend((pr['head_revision'], pr['merge_commit']))
    for revision in revisions:
        if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-f]{40}', revision):
            raise ValueError('Historical evidence requires full 40-character commit SHAs')
    return sorted(set(revisions))


def missing_revisions(root, revisions):
    return [revision for revision in revisions if subprocess.run(
        ['git', '-C', str(root), 'cat-file', '-e', revision + '^{commit}'],
        capture_output=True).returncode != 0]


def fetch_evidence(root, remote='origin'):
    # Collect and validate every requested SHA before making any network request.
    revisions = required_revisions(root)
    missing = missing_revisions(root, revisions)
    if missing:
        subprocess.run(['git', '-C', str(root), 'fetch', '--no-tags',
                        '--no-write-fetch-head', '--', remote, *missing], check=True)
        unresolved = missing_revisions(root, revisions)
        if unresolved:
            raise ValueError('Historical Git evidence is still missing: ' + ', '.join(unresolved))
    return missing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--remote', default='origin', help='Existing Git remote to fetch from')
    args = parser.parse_args()
    try:
        fetched = fetch_evidence(args.repo.resolve(), args.remote)
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print('Historical Git evidence: ' + str(error), file=sys.stderr)
        return 1
    print(f'Fetched {len(fetched)} missing historical commit(s).')
    for revision in fetched:
        print(revision)
    return 0


if __name__ == '__main__':
    sys.exit(main())
