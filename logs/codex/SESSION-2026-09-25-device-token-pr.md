# SESSION-2026-09-25-device-token-pr — Publish second-device token recovery

## Scope and selected request

User (exact): “Ok, make the PR”. This authorizes committing, pushing and opening
an infrastructure PR for the completed second-device recovery. Starting revision
is `7c0b8f51c41191e413a752c4297f9cdbdae6cca5` on
`infrastructure/device-token-accounting`. The preceding recovery edits were
present and are included; unrelated tracker bytecode is excluded.

## Outcome and provenance

The [recovery session](SESSION-2026-09-25-device-token-backfill.md) records the
implementation and checks: four dashboard sessions receive 8,515,036 input and
64,602 output tokens, with 22 branch-only turns retained for later import.
PR #18's evidence and original narratives remain intact. No scientific design,
source catalogue, progress record or human approval state changes.

Publication commit, PR and hosted-check results are appended when observed.
This task changes only its session pair; the PR includes the preceding task's
13-file recovery change. Related governance: ADR-004; preceding PR: #18.

## Validation

The recovery task ran 32 logging/recovery tests and 27 dashboard tests successfully.
This publication task checks the final records, summary, dashboard build, PR naming
and staged changes; actual results are in the paired JSON. Remote main is checked
before publication. No detector execution or scientific acceptance is claimed.

## Token accounting and follow-up

No completed-turn counters are exposed for the current publication turn; usage
is empty rather than estimated. The observed project total remains 98,045,726
input and 477,200 output tokens from 67 turns. This publication record adds one
session without measurements; pending branch and unassigned usage remain excluded.
Human PR review and merge are subsequent actions, not performed by this task.

## Publication

Committed `3e594e265011c868dfebcf35894192a691d527ac`, pushed the branch, and opened
[PR #19](https://github.com/asalzburger/nodd/pull/19),
“Infrastructure: Recover second-device token usage”. Verified the open PR title
and exact head. Hosted checks were not yet listed at that observation; local
results remain as recorded above. The final logging commit records publication.
No merge or approval was performed.
