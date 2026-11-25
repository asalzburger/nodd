# SESSION-2026-11-25-interaction-statistics — Merged interaction statistics and GitHub Pages tab

## Scope and evidence

Contemporaneous infrastructure work from merged main
`78bef505c4e623739da204ce92e3aa7bc6f931c5`, isolated on
`codex/interaction-statistics`. The worktree was clean at creation. Only retained
public/curated repository evidence was read; no private conversation store was
collected. ADR-004 remains draft; implementation does not grant design sign-off.

## Selected conversation

Human request, paraphrased: count human and response words, interactions, tasks,
different humans and agent instances across all merged recorded interaction
accounts (Codex/prompts, GitHub, CLI and other evidence), and open an
Infrastructure PR adding a GitHub Pages tab if possible.

Assistant outcome: implemented a Statistics tab, aggregate JSON export and CLI
counter using validated records. Stable message IDs, event URLs and turn/thread
IDs remove repeated PR/fork references. Authorship conflicts remain unresolved.
Journal excerpts and manually curated records have separate subtotals.

## Decisions and outcomes

An independent extraction of the tracked evidence at the starting main revision
gave 15,132 human words; 205,404 agent response words and 71,615 publishing-account
response words (277,019 combined); 3,077 message/discussion/review events; 304
canonical bounded sessions (299 closed, 5 open); 111 scientific registry tasks;
123 PR records; 7 named human accounts plus unnamed local speakers; 134 exposed
agent threads; 589 canonical usage turns; 522 retained visible-turn snapshots;
and 24,355 exposed operation calls. This task's new session and PR subsequently
increase the live source-revision counts, so these baseline numbers are not
hard-coded into the site.

The initial human subtotal of 15,193 included 61 bodyless review-state labels.
These labels are metadata rather than authored text; their events remain counted
but their words are excluded. A regression covers the correction. Seven inherited
messages disagree on human/agent authorship and remain unresolved.

The count covers all evidence retained on main, including dated snapshots whose
PR state may be stale and explicitly pinned branch-only references. No live merge
status is inferred. Numbers/code/URL components count literally; upload events and
generated references add no words. Named accounts do not establish distinct people.
Threads are the instance proxy; sessions, role assignments and physical processes
are not interchangeable. Tool metadata is deduplicated by turn without adding
journal aggregates or assuming wrapper calls equal individual program executions.

## Commands and validation

- Token-site unittest discovery: 28 tests passed, including 8 statistics controls.
- Interaction-ledger unittest discovery: 19 tests passed.
- Both Node suites passed: chart controls and PR conversation/navigation behavior.
- Session validator, ledger validator against the full starting revision, token
  validator, complete Pages build and whitespace checks passed.
- A sandboxed HTTP bind failed with PermissionError; the approved localhost server
  ran successfully outside the sandbox. Sandboxed curl could not reach it; the
  approved request returned HTTP 200. The owned server was stopped afterward.
- Visual browser QA was unavailable: no connected browser surface, unavailable
  in-app browser, and Firefox/Safari computer-use calls returned cgWindowNotFound.
  No visual-rendering pass is claimed. Static HTML, navigation, deterministic
  output, escaping and aggregate-publication boundaries are covered by tests.

The project-progress dashboard is retired; its required successor checks are the
token-site validator/build and interaction ledger. No detector validation applies
to this infrastructure-only change. Hosted check results are recorded separately
after the PR is opened.

## Changes and revision links

The paired JSON lists the implementation, tests, method guide, shared navigation
styling and this session pair. Generated outputs remain ignored under `_site/`.
No scientific task/progress entries were added for infrastructure work.

## Token accounting

This active task exposes no exact finalized client per-turn token counters or
stable accounting IDs. Its usage remains empty and unknown. No estimate or
copied historical observation was added. The canonical summary at implementation
verification retained 589 observed turns: 3,319,239,723 input and 13,881,824 output
tokens, 3,333,121,547 combined. Coverage was 205/305 canonical sessions, with 100
sessions lacking observations; this includes the new task. Cached/reasoning
subsets were not added again.

## Follow-up

Opened [Infrastructure PR #159](https://github.com/asalzburger/nodd/pull/159).
The connector's create action returned FORBIDDEN because its integration lacked
creation permission; the authenticated CLI created the PR successfully. Connector
reads confirmed the open, non-draft main-targeting PR and an empty discussion/review
timeline. Its selected public GitHub snapshot and canonical session links are
retained in `interactions/pr-0159.json`. The implementation commit is
`e6ffd0a76fd0d3f855895a99c4a956066d58c615`. The initial hosted token-site job
failed because `interactions/pr-0159.json` could only be created after the PR
number was assigned. This closeout adds that required ledger; the full 124-record
validator, PR159/base-preservation validator, 305-session validator and complete
site build passed locally afterward. The following push reruns hosted checks.

Review and merge the Infrastructure PR to publish the new tab through the existing
main-branch Pages workflow. Historical message coverage, distinct human identities,
physical agent processes, complete CLI output and this active task's final token
counters remain unknown. Infrastructure implementation creates no scientific
approval or detector sign-off.
