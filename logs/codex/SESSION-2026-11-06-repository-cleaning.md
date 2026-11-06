# SESSION-2026-11-06-repository-cleaning — Issue 120

## Scope and evidence

Issue [#120](https://github.com/asalzburger/nodd/issues/120), request
`120-35337160503`, supplied public snapshot dated 2026-11-06. Starting revision:
`2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7`, branch
`codex/agent-task-120-35337160503`; initial worktree clean. Infrastructure only;
no detector design or scientific tracking changes. Work remains in this isolated
worktree. No publication, GitHub mutations, history rewrite or machine changes.

## Selected conversation

User (public issue, exact): “identify files that represented data output from
tests that could be repeated (and hence the data deleted), schedule those files
for deletion”; “rationalize the logging and accounting infrastructure such that
individual PRs would not easily create merge conflicts.” Also requested other
cleaning options aimed at reducing repository size.

User (runner request, paraphrase): work at the captured input revision, prepare
checks, curated journal and interaction evidence, leave local changes for human
review without pushing or changing GitHub state.

Assistant (paraphrase): audit tracked outputs, retain traceability and prepare a
deletion schedule; improve bounded accounting rather than rewriting evidence.

## Specialist assignments and handoffs

Assignment `CLEAN120-SoftEng`, role SoftEng, input revision
`2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7`, write mode. Inputs:
`tools/session_logging/session_log.py`, `tools/interactions/ledger.py`,
`tools/session_logging/test_session_log.py`, `tools/interactions/test_ledger.py`,
`logs/README.md`, `interactions/README.md`,
`docs/decisions/ADR-004-session-logging-and-traceability.md`.
Owned files: the first six named inputs only. Deliver a backwards-compatible
way to create explicitly PR-scoped bounded session records and synchronize
only records affected by a named session, with regression tests and workflow
guidance avoiding shared growing journals and inventories. Preserve canonical
turn ownership and existing fingerprints/validation. Completion: report exact
changes, test commands/results and limitations. No delegation, commits, remote
mutations or historical evidence regeneration. Main agent owns cleanup audit,
policy reconciliation, this journal and final checks.

## Decisions and outcomes

Prepared the [cleanup schedule](../../docs/maintenance/issue-120-repository-cleanup.md)
and [immutable inventory](../../docs/maintenance/issue-120-inventory.json).
The captured tree contains 4,727 files / 569,769,442 bytes. Conditional removal
covers 122 files / 193,586,653 bytes: 41 historical study outputs, 76 event-array
files and five execution transcripts. One frozen layout (2,324,679 bytes) and
material scatter with incomplete original-recording provenance (6,537,331 bytes)
are explicit holds; 21 other large numerical files need further consumer review.
No numerical evidence was removed. Existing plots, recipes, input snapshots,
rejected controls and manifests remain intact. Removal prerequisites include
compact comparisons, preserved correlations where needed, exact original-source
reproduction checks, compatibility migrations and relevant regressions. Ordinary
future deletions reduce checkout size, not reachable full-clone history.

Added repeatable `session_log.py new --pr N` and `ledger.py sync --session ID`.
The selector handles both current and previously linked PRs without modifying
unrelated records. Workflow updates use independent bounded sessions/branches
and uniquely named immutable inventories, avoiding routine growth of shared
campaign journals and usage README files. Legacy branch matching stays additive.
Canonical token ownership, exact counters, schemas, fingerprint checks and all
104 historical PR ledgers remain unchanged. No project progress/tracking entry
was added for this infrastructure task. ADR-004 has an implementation note and
remains DRAFT; ADR-003 is referenced but unchanged. No DES was modified.

Selected public issue/request evidence is retained in
[request.json](SESSION-2026-11-06-repository-cleaning/request.json). This issue
has no assigned new PR number; no fictitious PR120 ledger was created. No
GitHub writes, pushes, commits, published artifacts, machine changes or raw
private client data collection occurred.

## Commands and validation

Initial inspection: `git status --short`, branch and HEAD, `git ls-tree -r -l
HEAD`, relevant instructions, ADR-003/004, linked recipes and test/workflow
sources. Environment observed: Python 3.14.6, Apple Git 2.54.0 (Apple Git-157),
Node v26.7.0. No shared dependency/runtime setup was executed.

- `python3 -B -m unittest discover -s tools/session_logging -p 'test_*.py' -v`:
  SoftEng ran 37 tests, PASS / exit 0.
- `python3 -B -m unittest discover -s tools/interactions -p 'test_*.py' -v`:
  SoftEng ran 19 tests, PASS / exit 0; includes nonempty-usage isolation,
  idempotence, current/former associations, shared references and invalid selectors.
- `python3 -B -m unittest discover -s tools/repository_cleanup -p 'test_*.py' -v`:
  3 tests, PASS / exit 0. Covers immutable revision reads despite dirty files,
  preserved files, duplicate arithmetic, binary/space paths, overwrite refusal,
  tamper detection and exact commit identity.
- `python3 -B tools/repository_cleanup/audit.py --revision
  2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7 --output
  docs/maintenance/issue-120-inventory.json --check`: PASS / exit 0;
  145 triaged files verified against original Git bytes. Generation used the
  same command without `--check`, writing only the compact audit.
- `python3 -B -m unittest discover -s tools/token_usage -p 'test_*.py' -v`:
  20 tests, PASS / exit 0.
- `node tools/token_usage/test_app.js` and
  `node tools/token_usage/test_interactions.js`: both PASS / exit 0.
- `python3 -B tools/interactions/ledger.py validate --base-ref
  2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7`: PASS / exit 0,
  104 retained PR records, canonical usage unchanged. SoftEng also ran the
  full validator without a base selector, PASS / exit 0.
- `python3 -B tools/interactions/ledger.py sync --session
  SESSION-2026-11-06-repository-cleaning`: PASS / exit 0; zero PR associations
  and zero PR ledger changes, appropriate to this issue-only task.
- `python3 -B tools/token_usage/build.py validate` and `build --output
  _site/pages`: both PASS / exit 0; 438 disjoint dated turns and unchanged
  2,123,088,062 observed input-plus-output tokens. Generated site stays ignored.
- `python3 tools/session_logging/session_log.py validate`: PASS / exit 0;
  254 paired records. `session_log.py summary --format json`: PASS / exit 0.
- `python3 -B tools/agent_workflow/workflow.py validate`: PASS / exit 0;
  eight role profiles and three skills. Assignment preparation also passed.
- `git diff --check`, new document local-path link existence check and
  inventory-state byte/count reconciliation: PASS / exit 0.

No unit-test failures occurred. The first finalized-record validation failed
because new activity entries omitted required `version`/`evidence` fields and
included an unsupported `components` field. Corrected only this new record to
the existing schema, preserving the failure in JSON. Final session validation,
summary and token-site validation/build reruns passed; no validation failure
remains unresolved.
Early read commands tried nonexistent per-run
README paths before the actual top-level validation reports were located;
these were inspection misses, not validation results. No native detector
construction, physical reproduction or full project CI run was attempted;
those are not established by the infrastructure checks.

## Changes and revision links

See paired JSON for final changed paths. No result commit created.

## Token accounting

Exact client per-turn counters and stable turn/thread IDs are unavailable in
this task, including specialist counters. Usage remains empty; no estimates or
private client archives are collected. Active-turn final counters unavailable.
Project summary at closeout has 438 observed turns across 171/254 sessions:
2,113,297,698 observed input and 9,790,364 observed output tokens; cached/reasoning
figures are subsets. 83 sessions, including this task, have no usage observations.
These are unchanged cumulative project observations, not this task's consumption
or a complete project total.

## Follow-up

Human review of infrastructure changes and the conditional deletion schedule is
next. Implement each removal stage only after its compact-evidence, original
reproduction/retention and consumer-migration prerequisites. Exact reproduction
of the old material recording remains blocked by missing provenance. No native
reproduction claim or design approval is requested or inferred. A future PR needs
its actual PR-numbered interaction record and public discussion capture before
publication; issue #120 is not a PR. No PR was created or modified here.

## Audit review assignment

Assignment `CLEAN120-AuditReview`, SoftEng, read-only. Source baseline
`2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7`; review explicitly includes the
uncommitted audit implementation and report at these SHA-256 identities:

- `tools/repository_cleanup/audit.py`: `de96aa1c5431b0ddb2ff5cdbf74701f73aa84f19060ea216e37f7af69da89fea`.
- `tools/repository_cleanup/test_audit.py`: `566bdf49b8401223aad4e6aab9039752e487f397567bdca186ffc8af59e9b553`.
- `tools/repository_cleanup/README.md`: `fb8b75f5ef3d4b915f19bfbb24e3f1e9714726d25d4dfb44ac3a81a22924a910`.
- `docs/maintenance/issue-120-repository-cleanup.md`: `c15c053bb4fa45be26c554921c32211a24e64c99223ff08ff0595128964f963a`.
- `docs/maintenance/issue-120-inventory.json`: `eebc06f1fd41eb22644cc0127869ff17b3749bd6644c46ca98b55b5000edb341`.

Inputs include AGENTS, PROJECT, ADR-003/004 and linked repository recipes.
No owned write files. Deliver findings on arithmetic, safety, reproduction
claims and dependency/retention boundaries; completion is a cited result with
actual checks and limitations. This specialist authored the accounting changes,
so that part has author/reviewer overlap; the audit was authored by the main
agent. No scientific acceptance assessment or human approval is requested.

## Accounting implementation handoff

`CLEAN120-SoftEng`, child `/root/accounting_cleanup`, reported the six owned
files changed, 37 logging tests, 19 interaction tests, all 104 PR ledgers validated
and `git diff --check` passing. Main agent inspected the implementation and its
regressions, then ran token-site integration checks. Native role selection was
requested through the exposed SoftEng role and the prepared full role text was
supplied; no claim of independently verified model/provider or human expertise
is made. The accounting author and its narrow test executor are the same agent.
Exact child usage counters are unavailable.

## Audit review handoff

`CLEAN120-AuditReview`, SoftEng child `/root/accounting_cleanup`: no blocking
findings in the five assigned files; SHA-256 identities matched before and after
review. Independently recomputed Git arithmetic: 4,727 files, 569,769,442 bytes,
551,773,583 unique-blob bytes; scheduled groups 122 files / 193,586,653 bytes
(33.9763%). Verified immutable Git reads, exclusive output creation/check-only
mode, named frozen-layout and event-array consumers, historical configuration
distinctions, missing material-recording provenance, conditional removal
requirements and checkout/history size distinctions. No edits or native jobs.
The main-authored audit received a separate assessment; the specialist-authored
accounting implementation was inspected by the coordinator, without a separate
independent reviewer. Native regeneration and deletion readiness remain unverified
prerequisites, not findings resolved by the infrastructure tests.

Final content inspection found eight new files totaling 119,665 bytes at that
inspection, with the largest the 71,922-byte metadata inventory. No staged files,
new numerical run payloads or scientific-evidence/production-input edits were
present. This journal grows slightly as closeout checks are recorded.
