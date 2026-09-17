"""Require progress updates in non-chore PRs; keep chores out of scientific work."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

CHORE_TITLE = re.compile(r'^chore(?:\([^)]+\))?:\s+\S', re.I)
TRACKING = {'project/tracking.json', 'project/reviews.json'}
PROJECT_PATHS = ('docs/design/', 'docs/signoff/', 'docs/validation/',
                 'src/', 'xml/', 'geometry/', 'detector/', 'config/')
PROJECT_FILES = {'PROJECT.md', 'docs/DEVELOPMENT_PLAN.md', 'reference/manifest.yaml'}


def is_chore(title):
    return bool(CHORE_TITLE.match(title))


def check(title, paths):
    paths = set(paths)
    if is_chore(title):
        scientific = sorted(p for p in paths if p in PROJECT_FILES or p.startswith(PROJECT_PATHS))
        if scientific:
            raise ValueError('Chore PR changes project/scientific evidence; use a project PR and update tracking: '
                             + ', '.join(scientific))
        return 'Chore PR: excluded from progress tracking; dashboard build still required.'
    if not paths & TRACKING:
        raise ValueError('Non-chore PR must update project/tracking.json or project/reviews.json '
                         'with work, review or evidence changes.')
    return 'Project PR includes a tracking update; record accuracy still requires review.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event', type=Path, required=True)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        event = json.loads(args.event.read_text())
        pr = event.get('pull_request')
        if not pr:
            print('Not a pull request: update policy is checked before merge.')
            return 0
        for revision in (pr['base']['sha'], pr['head']['sha']):
            if not re.fullmatch(r'[0-9a-f]{40}', revision):
                raise ValueError('PR event must identify full base/head SHAs')
        result = subprocess.run(['git', '-C', str(args.repo), 'diff', '--name-only', '-z',
                                 pr['base']['sha'] + '...' + pr['head']['sha']],
                                capture_output=True, check=True)
        paths = result.stdout.decode().split('\0')
        print(check(pr['title'], filter(None, paths)))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print('Dashboard update policy: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
