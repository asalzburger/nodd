# SESSION-2026-10-12-device-accounting-pr — Synchronize token accounting by PR

## Request and scope

User: “Make a PR with this in order to synchronize the token business”.
This authorizes committing and publishing the preceding accounting changes.
Started on main at `fdfa09a0fb58dd29af467054f9a7dc0b023e30f1`, with the prior
40-file audit change and four unrelated untracked token-gate files present.
Created `infrastructure/device-accounting-sync-20261012`; the token-gate files
remain untouched and excluded. ADR-004 governs the infrastructure workflow.
No scientific progress entry or approval is created.

## Accounting and synchronization

The prior audit recovered 24 turns (62,135,954 tokens) and restored eight
publication journal pairs from their exact local-branch revision. This new task
also recovered the now-completed audit turn: 3,122,802 tokens across 35 requests,
imported into the audit's own record after a successful dry-run. The original
inventory remains unchanged and a separate usage-only closeout snapshot records
the new boundary. No active publication-turn counters are imported here.

The PR therefore adds 25 disjoint observations: **65,008,966 input + 249,790
output = 65,258,756 tokens**. The resulting observed project subtotal is
**614,674,578 input + 3,521,509 output = 618,196,087 tokens across 208 turns**.
Cached input and reasoning output remain subsets. The 1,773,512-token gate turn
is retained as pending evidence; 13 historical turns remain unassigned and four
failed turns lack observations. Current publication usage and other-device
coverage remain unknown.

Fetched current main and inspected the other open accounting PR #61. That PR
only moves eight existing calorimeter entries unchanged, adding no usage; this
PR's additions are disjoint. Our README section precedes the existing sections,
leaving PR61's appended ownership correction independent. The local validation
includes the pre-existing untracked gate journal; committed-tree session counts
are one lower. Exact observed token totals are the same.

## Validation and publication

The preceding task's 33 logger/recovery tests and 31 dashboard tests passed;
no software changed since those checks. This task reruns structural validation,
summary, dashboard validation/build, PR naming/scope checks and whitespace checks.
The initial GitHub PR61 read failed under sandbox networking; approved retry
succeeded. Actual results, commit and PR identifiers are recorded below and in
the paired JSON after observation. No scientific tests or source claims change.
