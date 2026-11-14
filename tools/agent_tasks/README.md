# Hourly reviewer task pickup

A reviewer applies `agent_task` to an open issue or PR in `asalzburger/nodd`.
The LaunchAgent on **acts-mac-studio-01** checks at minute 7 of every hour and
once when loaded. Each tick picks up at most one new request, oldest issue first,
and runs Codex in a separate Git worktree. Every completed task ends in a
**draft PR** for human review. The host commits
and pushes the task branch, creates the draft PR, records its interactions and
verifies the remote draft/head before marking the task complete. It does not
merge changes or grant scientific approval.

For issue #127, see the [reactive-intake proposal](reactive-intake-proposal.md)
for faster collection, trusted follow-up comments and visible queue status.
It is a proposal for review; the hourly, label-event-only behavior below remains
the implemented workflow.

## Reviewer workflow

1. Describe the bounded task in the issue body or PR review/discussion, including
   its expected result and relevant design/validation references.
2. Apply `agent_task`. The latest application must be by one of the explicit
   `reviewers` in [config.json](config.json): `asalzburger-review` or the repository
   publishing account `asalzburger`. GitHub requires triage access or higher to
   apply labels; this PR does not change repository permissions.
3. The runner records the label event ID before starting. Edits, comments,
   task completion and subsequent hourly checks do not run that request again.
4. To request another attempt, remove and reapply the label. This works even if
   both actions happen between polls. Remove the label or close the issue/PR to
   cancel a queued request; doing so does not interrupt a task already running.

The runner paginates the issue and event APIs, accepts issues and same-repository
PRs, and skips external-fork PRs. It rechecks state and label history immediately
before claiming. PR tasks use the captured head SHA and include review submissions
and inline comments; issue tasks start from the latest fetched `main`. A changed
PR head during fetch fails the attempt rather than silently changing its target.

## One-time repository setup

The label is GitHub repository metadata, not something a Git commit can create.
It was created for this infrastructure request on 2026-11-06. To restore it on a
new repository (or if deleted), a maintainer with write access runs:

```sh
gh label create agent_task --repo asalzburger/nodd --color 6F42C1 \
  --description 'Reviewer requests agent work; picked up hourly on mac-studio-01'
```

Queue discovery reads GitHub. The host publisher pushes only the assigned task
branch and creates its draft PR; it never adds/removes labels, posts comments,
marks a PR ready, merges or changes repository permissions.

## Deploy after review and merge

Use a stable checkout on `acts-mac-studio-01`, not a temporary PR worktree.
Python 3.11+, Git, GitHub CLI and Codex CLI must be installed. The observed
Codex version during implementation was `0.166.0`; verify supported flags after
CLI upgrades. Authenticate interactively once as the same macOS user that will
run the job (`gh auth login`, `codex login`) and verify Git fetch/push access
and permission to create draft PRs. Do not
put tokens or auth files in Git or in the plist. Existing credentials are reused.

From that checkout, inspect the read-only pickup preview first:

```sh
python3 -B tools/agent_tasks/poll.py \
  --state-dir "$HOME/Library/Application Support/nodd-agent-tasks" --dry-run
```

No output means no new eligible task. Dry-run never claims tasks, starts Codex,
or creates a worktree; it may create the local lock directory/file. It still
validates the actual host, origin, label actor and public task context.

Generate and inspect the LaunchAgent, then load it explicitly:

```sh
python3 -B tools/agent_tasks/launchd.py \
  --output "$HOME/Library/LaunchAgents/org.nodd.agent-tasks.plist"
plutil -lint "$HOME/Library/LaunchAgents/org.nodd.agent-tasks.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.nodd.agent-tasks.plist"
launchctl print "gui/$(id -u)/org.nodd.agent-tasks"
```

`RunAtLoad` makes loading the agent eligible to start real work immediately.
The generator only writes the plist; it does not install/load a live scheduler.
It records absolute executable, checkout and configuration paths and the current
PATH because launchd does not load interactive shell startup files. Use Homebrew
Python 3.11+ if the system Python is older. macOS may require access to the
checkout under Documents for the chosen Python/terminal account; verify the
first scheduled run through its logs.

This is a per-user LaunchAgent: the user must be logged in. The Mac must be
awake and online to check GitHub. Missed calendar events while asleep coalesce
into a wakeup check; the schedule does not wake or power on the Mac. The model phase is
bounded to 3300 seconds by default. Publication follows with a 180-second timeout
per host command; the same process lock covers both phases and all manual and
scheduled calls. Pending tasks beyond the one-per-tick limit wait for later
hours. This is a single-machine queue; do not run a second independent worker
with another state directory.

## Results, failures and maintenance

The private local state directory contains `state.json`, `runs/NUMBER-EVENT/`
(public input snapshot, prompt, structured `result.json`, final `result.md`,
publication/size manifests and operational stderr), and
`worktrees/NUMBER-EVENT/` on branches named `codex/agent-task-NUMBER-EVENT`.
`completed` requires a zero model exit, a pushed branch, its individual PR
interaction record, and a verified open **draft** PR at the final pushed SHA.
After a push, the publisher allows five head-confirmation reads with bounded
backoff (7.5 seconds of total delay). A closed/ready PR or wrong branch fails
immediately; a persistently wrong SHA still fails and reports both revisions.
The state contains `draft_pr_url`/`draft_pr_number`, and `result.md` starts with
the clickable PR link. Inspect the draft for actual validation and limitations;
completion is not human approval. For a task on an existing PR, the new draft
targets that PR's captured head branch so it contains only the follow-up delta.
The source PR must still be open at its captured SHA before publication.

Codex runs with `workspace-write` and `approval_policy="never"`; existing sandbox
network and writable-directory restrictions still apply. Access requiring
approval must be reported as a blocker. The sandboxed agent returns a JSON PR
title/body under
[the final-response schema](pr-response.schema.json) and leaves reviewable changes,
including a curated session record for investigations, blocked or no-code tasks.
The host publisher performs commit/push/draft creation outside that sandbox using
the operator's existing GitHub login. The prompt forbids the agent from publishing
itself, posting comments, changing labels/machine configuration or granting human
sign-off. The host checks branch/origin, title, curated records, staged paths and
new Git blobs. Credential paths and new/staged blobs above 5 MiB fail unattended
publication and require manual review. These checks complement the repository
artifact rules; they are not a full content/secret scanner.
Use bounded, reviewed tasks on this workstation. Dependencies are not installed
automatically and submodules are not initialized automatically. Follow the
repository's ACTS preflight whenever a task actually requires that environment.

A failed/timed-out attempt, missing/invalid PR response or publication failure
is retained and returns a nonzero exit; it cannot be reported as completed.
If draft creation succeeded before a later failure, `publication.json` and state
retain its URL so the operator can inspect that draft. Retrying publication on
the same assigned branch reuses its existing draft rather than creating another.
An interrupted poller can leave `started` in state. Failed and interrupted
attempts are suppressed on future ticks; inspect
the worktree and logs, then remove/reapply the label if a fresh attempt is needed.
Do not delete the state directory to retry: that loses deduplication history.
Network/API failures before claiming consume no request and retry next hour.

Stop scheduling before maintenance:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/org.nodd.agent-tasks.plist"
```

Review any active attempt after stopping. Keep state and worktrees until their
results are reviewed. Update the stable checkout explicitly after future merges;
the poller does not update its own code. To change executable paths or schedule,
render a new plist to a temporary path, inspect it, replace the unloaded plist
and bootstrap again. Apply local log retention as appropriate; never commit
private operational logs, prompts, task state or raw client rollouts.

## Verification and sources

```sh
python3 -B -m unittest discover -s tools/agent_tasks -p 'test_*.py' -v
```

Tests use local Git repositories and fake Codex/GitHub responses. They make no
paid model calls and do not load a LaunchAgent. Publisher integration tests use
a real local bare Git remote and a fake GitHub CLI; they verify draft creation,
interaction follow-up, remote SHA checks, idempotence and failure paths.

For the existing installation, deploy the reviewed `poll.py`, `publish.py` and
`pr-response.schema.json` together. Preserve the local permission-list config,
state and completed worktrees. Source updates at the same program path do not
require another `launchctl bootstrap`; inspect the next scheduled result.

- [GitHub label permissions](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [Apple LaunchAgent and timed-job guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- [Codex non-interactive jobs and workspace-write sandbox](https://learn.chatgpt.com/docs/non-interactive-mode)
