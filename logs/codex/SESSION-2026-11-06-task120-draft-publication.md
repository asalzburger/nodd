# SESSION-2026-11-06-task120-draft-publication

## Scope and evidence

Publish the existing task #120 proposal as a draft PR. Source revision:
`2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7`. The original completed worker
worktree was preserved; its 18 modified/new files were copied to the dedicated
`codex/task120-cleanup-draft` worktree inside the project workspace.
The original worker session remains the canonical record of its implementation.

## Selected conversation

User, exact: "Make it a rule that tasks always end in a draft PR 0 and make one now"

Assistant, paraphrase: will publish task #120 now and implement the standing
rule and deterministic runner publication in a separate infrastructure draft PR.
The user explicitly authorizes pushing and creating draft PRs for task results.

## Decisions and outcomes

The proposal inventories historical output, schedules 122 files (193.6 MB)
conditionally, and adds conflict-resistant per-task logging/accounting helpers.
No evidence is deleted and no history is rewritten. Required consumer migration,
preservation and native reproduction remain prerequisites. ADR-003/ADR-004 stay
DRAFT; no scientific progress entry or human sign-off is added.
The individual PR interaction record is added after GitHub assigns its number.

## Commands and validation

Reran 79 Python tests: 37 session logging, 19 interactions, 3 cleanup audit and
20 token site tests; all passed. The immutable inventory check verified 145
triaged files. Both token-site JavaScript suites passed. Session/interaction
validation, resource-site build and staged/new-object inspection accompany
publication. These checks do not establish native reproduction or safe deletion.

## Token accounting

Exact client per-turn counters and identifiers were unavailable. Usage remains
empty; observed input/output for this publication task are unknown, not zero.
No counters from the original worker session were copied or allocated here.

## Follow-up

Review the draft PR's conditional cleanup and accounting changes. Execute any
future evidence removal only after the documented prerequisites. The separate
runner-rule PR governs future task delivery.
