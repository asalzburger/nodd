# SESSION-2026-11-06-hourly-agent-tasks — Hourly reviewer-labeled task pickup on mac-studio-01

## Scope and evidence

Contemporaneous curated record for the infrastructure request below. Work starts
from `96dbf57d0da7f3027e59109c1846d992d68d4d44` on
`codex/hourly-agent-tasks` in a new, initially clean worktree. The original
checkout has unrelated edits, which were preserved. No detector runtime or
scientific design work is required. ADR-003 and ADR-004 remain DRAFT.

## Selected conversation

User, exact request: "I need a new infratructure PR: The git repository needs to
have label \"agent_task\" which the reviewer can set. Then on mac-studio-01 we
need to hourly check if there are new tasks to pick up. Can this work ?"

Assistant, paraphrase: confirmed feasibility of a local macOS LaunchAgent,
inspected repository governance and existing workflow, asked whether issues,
PRs or both should be eligible, and proceeded with both when no answer was
available. Reported creating the label and verifying reviewer access. Explained
that worker results remain local for review and scheduler loading follows PR
review and merge.

## Decisions and outcomes

Created the GitHub `agent_task` label (purple `6F42C1`) with the requested queue
meaning. GitHub CLI confirmed `asalzburger-review` has write access. No repository
permission was changed. The connector's collaborator permission endpoint returned
403, so the authenticated GitHub CLI was used for that read and label creation.

Added a Python standard-library poller and explicit LaunchAgent generator. The
schedule is once hourly at minute 7 and at load, restricted to the verified host
`acts-mac-studio-01`. The allowlist contains the established reviewer and repository
publishing accounts. One task is attempted per tick, using a separate worktree.
Each label event is claimed durably before starting; repeated ticks, comments and
failed/interrupted attempts do not duplicate execution. Removing/reapplying the
label requests a fresh attempt. A local lock prevents overlapping workers using
the same state directory. This is not a distributed queue.

Both issues and same-repository PRs are supported. PRs include public review
context and are tied to the captured head revision; external-fork PRs are skipped.
Codex uses `workspace-write` and never requests interactive approval. The prompt
requires repository governance, tests and curated reporting, and leaves local
changes/results for human review without pushing, publishing, commenting, label
mutation, merging or human sign-off. Missing permissions remain blockers.

The generator writes a reviewable plist with absolute executable paths and shell
PATH but never loads a job. No live scheduler or paid Codex task was started in
this implementation session. Deployment after merge uses the documented stable
checkout, logged-in macOS user and existing CLI authentication. Sleeping/offline
machines cannot provide an exact wall-clock hourly service.

## Commands and validation

- `git fetch origin main`: initial sandbox attempt failed DNS resolution; the
  authorized network retry succeeded.
- `gh label create agent_task ...`: exit 0; subsequent label listing verified the
  name, description and color. Reviewer permission lookup returned `write`.
- Official OpenAI documentation and installed `codex exec --help` were checked;
  observed CLI version was `0.166.0`. No model inference was invoked for testing.
- First queue test run: one failure exposed acceptance of a `../bad` repository
  selector. Tightened configuration validation; all 15 tests then passed.
- `python3 -B -m unittest discover -s tools/agent_tasks -p 'test_*.py' -v`:
  exit 0, 15 tests. Includes real local Git fetch/worktree creation with a fake
  Codex executable, deduplication, failure retention, dry-run, paging, actor
  allowlist, closure/removal/relabel races, fork rejection, PR head changes,
  exclusive locking, timeout cleanup and plist serialization.
- `python3 -B tools/agent_tasks/poll.py --state-dir <temporary-state> --dry-run`:
  exit 0 on the real host against GitHub; no new eligible tasks. No claim or
  worktree/model job was created.
- Rendered a plist to a temporary path; `plutil -lint` exited 0. Job not loaded.
- `python3 -B tools/project_records/validate.py`: exit 0, 101 tasks, 53 documents
  and 24 review rounds validated. No progress entry was added for this PR.
- `python3 -B tools/token_usage/build.py build --output _site/agent-tasks-preview`:
  exit 0. This verifies the existing resource site still builds.
- `git diff --check`: exit 0.

Session/interaction validation and final resource summary are recorded in the
paired JSON. These checks do not imply detector acceptance or design sign-off.

## Changes and revision links

See the paired JSON inventory: poller, configuration, LaunchAgent generator,
tests and operations guide; root README link; CI test step; this session pair;
and the individual PR interaction record once its number is assigned. No
scientific tracking or reference catalogue parameters were changed. Technical
documentation sources are linked in the operations guide.

## Token accounting

Exact per-turn client counters and stable turn identifiers were unavailable in
the active session, so `usage` remains empty. This task has no observed input or
output token sums; missing coverage is unknown, not zero. No private client
archives or raw model rollouts were collected. Existing project-wide observed
totals are not attributed to this task. The summary command is run at completion.

## Follow-up

Review and merge the infrastructure PR, then deploy from a stable checkout using
the operations guide. Review the initial real task result and local logs. The
scheduler requires the macOS user to remain logged in and the machine to be awake
and online. Confirm task scope or publishing policy in a later change if broader
automation is wanted. No formal design approval was requested or created.
