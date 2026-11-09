# Reactive reviewer task intake — issue #127

- Status: PROPOSAL; implementation and deployment pending human direction.
- Date: 2026-11-09.
- Task: [#127](https://github.com/asalzburger/nodd/issues/127), request
  `127-35570260965`.
- Examined source: `61af5cd92cc651e9add100f8d9733f6e6c73d8bd`.
- Governing policy: [AGENTS.md](../../AGENTS.md),
  [ADR-002](../../docs/decisions/ADR-002-review-and-signoff-policy.md) and the
  [current runner contract](README.md).

Recommend a short, independent intake process every minute, followed by an
optional webhook receiver for near-immediate intake. Let trusted reviewer
follow-ups on an enrolled issue/PR request triage without toggling the label.
Keep one execution worker and the existing host draft publisher. Distinguish
receiving a request, starting work and producing a verified draft PR.

This document proposes operating choices, not a new deployed service or design
approval. All intervals below are proposed settings, not measured latency or
guarantees. No software dependency or permission change is implemented here.

## What the example establishes

**FACT — repository source:** [launchd.py](launchd.py) schedules minute 7 of
each hour. [poll.py](poll.py), `latest_request`, `candidates` and `poll`, only
recognizes label applications, remembers each issue/label-event pair, and runs
at most one attempt per tick. One lock spans discovery, execution and
publication; changing the timer alone leaves intake blocked while work runs.
Comments and PR reviews enter the execution snapshot but never request a run.

**FACT — public history, read 2026-11-09:** the
[example comment](https://github.com/asalzburger/nodd/pull/118#issuecomment-6686211776)
by `trahxam` was created on 2026-11-06 at 13:41:56 UTC. The public label history
shows an application by `asalzburger` at 11:50:20, another at 14:16:54, and the
latest application by `trahxam` at 15:21:50 UTC that day. The examined
[configuration](config.json) permits `asalzburger-review` and `asalzburger`,
but excludes `trahxam`. Selected event IDs, timestamps, public discussion and
retrieval provenance are retained in the
[task evidence](../../logs/codex/SESSION-2026-11-09-reactive-agent-workflow/public-inputs.json).

**INFERENCE:** that comment alone cannot enqueue another attempt. The latest
label application would also be skipped by the examined allowlist. Public
history does not establish which attempts ran, the deployed source/configuration,
host availability or whether a prior attempt had already consumed its event.
Private runner state was not inspected. These are independent causes to address;
an hourly delay is not the sole supported explanation.

## Delivery options

| Option | Expected improvement | Limits and decision |
| --- | --- | --- |
| Shorten the existing poll interval only | Reduces idle label-pickup delay | Still ignores comments, blocks intake during execution and handles one task per invocation. Insufficient alone. |
| Separate one-minute collector and single worker | Fast intake using the existing outbound GitHub access; no inbound endpoint | Recommended first implementation. Requires scheduler/state migration and API-budget checks. Mac must be awake, logged in and online. |
| Webhook receiver plus reconciliation polling | Receives supported GitHub events as they arrive | Recommended later when near-immediate receipt is required. Requires an approved endpoint, secret, hosting/retention owner and host handoff. |
| GitHub Actions event relay | Avoids exposing the Mac as a public HTTP server | Alternative transport; hosted-runner queue latency and authenticated delivery to a durable inbox remain. Do not execute PR code on a privileged self-hosted runner. |
| GitHub Actions scheduled polling | Moves the clock off the Mac | Still polling and adds another scheduling/worker queue; does not resolve comment eligibility or busy-worker intake by itself. |

An Actions relay, if selected, must use trusted default-branch handler code and
pass identifiers as data. It must not interpolate comment bodies into shell
commands or check out/run the requesting PR. Transport-specific API behavior,
permissions and current delivery limits need source verification in the eventual
implementation PR; this proposal does not establish a runnable transport recipe.

## Proposed request rules

Keep an explicit human requester allowlist, separate from final sign-off roles.
Retain `agent_task` as opt-in for an open issue or same-repository PR. A label
application must still be by an allowed requester. Its event ID starts an
enrollment period, ending on label removal or closure.

| Input during an enrollment period | Proposed handling |
| --- | --- |
| Allowed human applies/reapplies `agent_task` | Queue the bounded task using the existing label-event identity. |
| New allowed-human conversation comment or inline review comment | Queue triage, including ordinary language such as the PR #118 example. No special command required. |
| Allowed-human submitted review with comments or `changes_requested` | Queue triage; group the review and its inline comments into one request. |
| Approved/dismissed review, PR synchronization or dependency merge | Refresh context/invalidation information; do not authorize implementation, acceptance or a new task automatically. |
| Edit/delete of an existing comment | Invalidate or refresh pending context; do not launch a new paid attempt solely because text changed. New intent uses a new comment or label application. |
| Unknown actor, bot, publishing-account output or agent-generated status/draft | No automatic work; retain an operator-visible reason. Never infer authorization from `COLLABORATOR` alone. |
| Label removal or issue/PR closure | Cancel pending work in that enrollment period. An active attempt remains separately recorded and is not silently interrupted. |

For comment-triggered work, require both a valid enrollment event and a trusted
human follow-up author. Publishing-account comments are excluded even though
the current account can explicitly request work by applying the label. A bot
exclusion, publisher identity and an agent-output marker prevent feedback loops.
Coalesce review bursts for a proposed 15 seconds, retaining every source ID and
URL. Coalescing must not postpone collection or acknowledgement of later items.

Triage interprets a question, correction, resume request or ambiguous message
against the captured discussion and repository instructions. It may answer,
prepare a bounded authorized change, or identify a blocker in its draft. It must
not treat every comment as authority to execute arbitrary instructions. A merged
dependency is context: installation, source pins and actual runtime still need
verification before dependent validation can run.

Adding `trahxam` as a task requester/follow-up author is a specific human decision,
not an automatic consequence of this issue or collaborator status. With that
authorization and an active enrollment, a **new** equivalent comment would queue
triage. Existing comments must not all replay on rollout; resuming #118 requires
an explicit fresh request or a reviewed import of that one source ID. This task
does not resume the calorimeter study.

## Collector, queue and worker contract

1. The collector reads labels, issue/PR conversation comments, submitted reviews
   and inline comments through their distinct APIs; all collections paginate.
   Do not use only issue `updated_at`, which omits event identity and can include
   agent changes. Use persisted per-resource cursors plus an overlap scan and
   deduplication; advance cursors only after durable intake. Back off on API/rate
   failures without consuming a request, and record a heartbeat and last error.
2. Use one normalized key across polling and webhooks:
   `(repository, issue/PR, enrollment-label-event-ID, resource-kind, resource-ID)`.
   Store delivery IDs separately for webhook replay checks. Grouped requests
   retain their constituent keys. Preserve existing `NUMBER-EVENT` attempt and
   publication identities; do not reinterpret completed or failed history.
3. A short intake lock protects atomic inbox/cursor writes. A separate worker
   lock permits one active worktree/model/publisher sequence. Neither process
   may overwrite the other's state. Persist the claim before execution. A
   follow-up arriving during work stays pending for the next attempt rather than
   modifying the active task's frozen prompt. Fair order uses durable request
   receipt time, not issue creation date.
4. Before claiming, re-fetch actor authorization, current enrollment, open state
   and same-repository PR origin. Verify comment existence/content and bind the
   PR head or fetched issue base to the snapshot. A queued head change requires
   a fresh snapshot and recorded revision; a change during execution stops
   publication under the existing publisher rule. Never silently retarget work.
5. After publication, drain the next pending request promptly without waiting
   another hour. Keep one worker, the configured model timeout and host command
   bounds. Intake continues while it is busy. Failed/interrupted attempts require
   an explicit new request or inspected publication-only recovery; no automatic
   paid retry. Publication recovery reuses its draft and never reruns the model.
6. Migrate under a stopped worker: back up local state, import existing attempts,
   establish an explicit activation cutoff and mark older discussion as seen.
   Preserve local evidence. For rollback, disable new intake, finish or inspect
   active work and restore the reviewed scheduler/source while retaining the new
   inbox separately; do not reset history and replay requests.

For webhooks, the proposed subscriptions cover only the needed issue/PR labels,
lifecycle changes, conversation comments and review activity. Require authenticated
HTTPS delivery, signature checking before processing and secrets outside Git.
Persist before returning a prompt transport success, then process asynchronously.
Validate delivery identity and reject unsupported repositories/actions; re-fetch
public context before any worker launch. A transport acknowledgement means
delivery was stored, not that a task is authorized or complete. Verify the
provider's exact event/action names, signature protocol and response deadline
against current official documentation when implementing the selected transport.

Keep a proposed five-minute reconciliation scan using the same keys for missed
deliveries; record cursors and backoff. A webhook does not wake the Mac or remove
worker backlog. Selecting a relay/inbox host and secure Mac handoff remains a
deployment decision; no endpoint, token or new machine setting is configured.

## Visible responses and approval boundaries

Propose one idempotent host-generated status comment per request, updated for
`queued`, `running`, `blocked/failed` and `draft available`, with source links,
target revision, timestamps and the verified draft URL when available. A minimal
queue acknowledgement can say: “Request received; queued for triage. Human
review and any required design sign-off remain pending.” Keep this publisher
path independent of a busy model worker; do not promise a completion time.

**This would be a new, narrowly scoped comment-writing permission.** The current
runner/publisher explicitly forbids comments, and this task retains that rule.
Before enabling it, humans must authorize the publishing identity, repository,
template and update policy. Until then expose local queue/result status and
draft-PR output, and state that immediate public replies are unavailable. A lost
comment-creation response must be reconciled by request marker before retrying;
if identity is uncertain, stop rather than duplicate comments. Status updates
must never themselves enqueue another attempt.

Task-request permission grants no engineering approval. The human final sign-off
authority remains `asalzburger-review`, as assigned in ADR-002; reviewer allowlist
changes do not alter it. Agents must not sign off designs, record human approval,
advance documents to `SIGNED OFF`/`ACCEPTED`, mark PRs ready or merge. An approval
event is not automatically translated into a sign-off record. Exact-revision
human evidence, design-before-production rules and prototype isolation still
apply. The workspace sandbox, no-approval execution, origin/head checks, artifact
limits, curated logging and host-verified **draft PR** completion remain gates.
Even blocked/no-code work produces a curated draft through the host publisher.

## Implementation sequence and acceptance evidence

First review request semantics and identities, implement normalized intake and
queue migration, then split collection/execution and render a one-minute
scheduler for inspection. Update the software inventory with actual new usage
at implementation time. Start with a no-execution preview; compare discovered
keys to manually inspected public events. Separately approve and implement
public status comments and, if needed, webhook transport. Deploy only reviewed
source through an explicit operator action; never self-update from PR content.

The implementation PR should exercise the following with synthetic APIs and
local Git fixtures before any live pilot:

| Case | Required result |
| --- | --- |
| PR #118-style trusted follow-up with active enrollment | Exactly one triage request; no label toggle. Untrusted author or enrollment fails closed with a reason. |
| Label and follow-up supplied by different trusted humans | Both identities checked; enrollment retained and source links recorded. |
| Duplicate delivery, polling overlap, review plus inline burst | One durable request/attempt per key; every constituent source retained. |
| Concurrent intake, worker execution, restart and lost acknowledgement | Intake persists while worker is busy; no duplicate model, draft or status comment. |
| More than one API page, missed webhook, API outage/rate limit | Eventual reconciliation without skipped sources or consumed failed reads. |
| Removed label, deleted/edited comment, closed/fork PR, changed head | Pending work canceled/refreshed as specified; stale active work cannot publish as current. |
| Bot/publisher output, approvals, dependency merges | No self-trigger or inferred design approval. |
| Failed model/publication and legacy-state migration/rollback | Existing attempts preserved; retries explicit; existing draft reused only by inspected recovery. |
| Missing sign-off or forbidden ready/merge/sign-off request | Stop or prepare an allowed draft/prototype; never cross the human approval boundary. |

For an approved live pilot, measure event-to-durable-intake, intake-to-visible
acknowledgement, queue wait, model time and draft-publication time separately.
Record host uptime, API errors and measured distributions. Proposed healthy-host
intake targets are within two minutes with polling and within 30 seconds with
webhooks; these are review targets, not observed results or service guarantees.
Receipt latency says nothing about science-validation duration. Queue depth and
stale heartbeats must be visible to the operator, including allowlist rejection.

Human decisions remaining: requester/follow-up allowlists (especially `trahxam`),
automatic triage scope, public-comment authorization, deployment ownership and
chosen transport/hosting, API/model budgets and latency targets. No detector
DES status, ADR approval or scientific tracking entry changes in this proposal.

## Evidence and verification limits

The factual diagnosis is bounded to the examined repository revision and selected
public task history linked above. Proposed request semantics, queue contracts,
intervals and transport requirements are project operating choices pending human
review. No detector parameter, new detector source, deployed API capability or
measured latency is established here. The implementation PR must supply its own
version-specific transport evidence, software inventory and execution results.
