# SESSION-2026-11-09-reactive-agent-workflow — Reactive reviewer task proposal

## Scope and evidence

Issue [#127](https://github.com/asalzburger/nodd/issues/127), request
`127-35570260965`, asks for proposed workflow modifications for faster responses
to PR requests/updates while retaining final human sign-off. Started from clean
revision `61af5cd92cc651e9add100f8d9733f6e6c73d8bd` on assigned branch
`codex/agent-task-127-35570260965`. The host publisher owns commit, push and draft
PR creation; this sandboxed task prepares changes and a structured title/body.

Read AGENTS.md, PROJECT.md, the current runner and tests, ADR-002/003/004,
agent workflow, logging/interaction guides and applicable `nodd-coordinate`
procedure before editing substantive content. This is a small, dependent
infrastructure proposal kept with the main agent under that procedure; no
specialist delegation or separate agent review was performed. No physical
design, scientific result or TDR assessment requires a separate specialist here.
No detector DES or approval states change. Infrastructure work is excluded from
scientific project tracking.

The public task snapshot was provided by the runner. Connected GitHub read-only
tools retrieved the linked PR #118 example comment, public label events, PR
metadata and discussion. The
[selected evidence](SESSION-2026-11-09-reactive-agent-workflow/public-inputs.json)
retains resource IDs, GitHub logins, public URLs and timestamps, with summaries
of other comments. It excludes account metadata, HTML and raw client data.
PR #118 is context, not this task's implementation or accounting target; its
existing interaction ledger was not refreshed or modified.

## Selected conversation

- Public issue author `trahxam`, paraphrase: propose more reactive/instant
  responses, using the PR #118 follow-up as an example, while preserving final
  sign-off policy.
- Request event `35570260965`: `asalzburger-review` applied `agent_task` on
  2026-11-09 at 13:04:09 UTC. Requester and issue author are distinct parties.
- Scheduled user input, paraphrase: inspect governance and the captured revision,
  work only in this isolated worktree, prepare curated evidence and JSON PR
  title/body, and leave publication to the host. Comments, labels, machine
  configuration changes, merges and sign-off are forbidden in this task.
- Example public comment `6686211776`, exact quote by `trahxam`:
  “Get back to this now we have the dependencies from #123”. Its creation time
  was 2026-11-06 at 13:41:56 UTC.
- Assistant visible findings, paraphrase: comment-only follow-ups cannot request
  another run; the latest label actor is also outside the examined allowlist.
  Prepare a staged intake/queue proposal and preserve human approval boundaries.
- Assistant visible outcome, paraphrase: a concrete proposal covers one-minute
  independent intake, a single worker, trusted follow-up triage, deduplication,
  optional webhooks and separately authorized queue-status comments. No live
  workflow change or immediate public response is claimed.

## Decisions and outcomes

The implementation intentionally ignores comments as trigger events and keys
attempts by issue/label-event ID. It executes at most one request per hourly
tick and holds its lock through publication. The fetched public label history
for #118 ends with a `trahxam` application at 15:21:50 UTC on 2026-11-06; the
examined source allows only `asalzburger-review` and `asalzburger`. These code
and public-history facts support two separate causes of missed pickup. They do
not reconstruct actual host uptime, deployed configuration or prior attempts.
Private runner state was not read. The dependency study was not resumed.

Added [the proposal](../../tools/agent_tasks/reactive-intake-proposal.md) beside
the runner documentation, with a README entry that distinguishes proposed and
implemented behavior. It recommends separating collection from execution before
shortening the interval; a timer change alone would leave busy-worker intake
blocked. Trusted follow-ups during an explicitly enrolled task queue triage,
with source-key deduplication and bounded review-burst grouping. Deployment
cutoffs avoid replaying historical comments. A later webhook transport uses
authenticated durable receipt and the same queue identities, with reconciliation.

Current prohibitions on public comments remain in force. A narrowly scoped
host status-comment writer would need a separate human authorization. Adding
`trahxam` as a task requester is explicitly a human decision, unrelated to
`asalzburger-review` retaining final sign-off authority. Approvals/merges never
automatically grant design acceptance. No executable source, config, scheduler,
credentials or machine setting was changed; no new software integration was
introduced. The software inventory check confirms the existing reviewed inventory
remains consistent, so no fingerprint refresh or inventory edit was needed.

Official GitHub operational documentation was investigated when comparing
transport options. The first best-practices URL was inaccessible; its canonical
URL was subsequently read successfully. Inspection of the PR policy found that
`reference/manifest.yaml` changes are classified as scientific work. Removed
the provisional operational-source entries before publication and kept the
catalogue byte-identical to the starting revision. The final proposal grounds
its factual diagnosis in repository source and selected public task evidence;
intervals, queue semantics and transport requirements are explicitly proposed
project choices. Provider-specific API/protocol verification belongs with the
eventual implementation. No new detector source or external document copy is
introduced, and no PR policy check or scientific-tracking rule is weakened.

## Commands and validation

The paired JSON records actual commands, exits and results. Existing runner
and publisher tests use local temporary Git repositories and fake GitHub/Codex
responses; they do not execute paid models, publish remote PRs or load a
LaunchAgent. Passing these baseline tests does not validate the unimplemented
reactive design. No live scheduler, webhook, acknowledgement, latency pilot,
ACTS/DD4hep runtime or calorimeter study was run.

All 27 existing runner/publisher tests passed. Software inventory, session and
interaction validators, token-site validation/build, source-catalogue equality,
relative-link checks and infrastructure title/path checks passed. The ignored
preview is `_site/agent-task-127-preview`. The five deliverable files were
reviewed as ordinary UTF-8 text/JSON and are individually below 5 MiB; the largest
new document is about 16 kB. `git diff --check` passed. Host publication must
still inspect the subsequently staged files and any newly created Git objects.
An optional process-list probe was denied by the sandbox; no permission change
or workaround was attempted, and it is not required for this proposal.

## Changes and revision links

The paired JSON lists the proposal, runner README pointer, this session pair
and selected public-input evidence. There are no
result commits at agent closeout. Host publication must inspect staged/new Git
objects, commit/push the assigned branch, create a draft PR, capture its own
interaction record and verify its URL/head. No PR number or publication success
is invented here.

## Token accounting

Exact client per-turn token counters and stable thread/turn identifiers are not
exposed in this scheduled task. `usage` stays empty; observed input/output totals
for this session are unknown, not zero. No private client store was queried and
no parent/child counters were estimated or duplicated. `session_log.py summary`
reports cumulative observed project totals with missing coverage separately;
those totals must not be attributed to this task. The current active turn is
excluded from final-turn accounting.

At preparation closeout, the repository summary reports 262 sessions: 172 with
usage and 90 without. Its cumulative observed input/output totals are
2,118,614,183 / 9,835,233, from 441 disjoint recorded turns; all 441 have dates.
This task adds no numerical usage observation. Missing historical/current-turn
coverage remains explicit, and the project subtotals are not this session's
consumption.

## Follow-up

Human review should select requester/follow-up identities, triage scope,
comment-writing authorization, transport/hosting and operating budgets/targets.
Implementation, fixture cases and an explicit operator deployment follow that
decision. Final human sign-off remains with `asalzburger-review`; no human
sign-off is recorded or advanced. Host draft publication remains outstanding
at this sandboxed handoff.
