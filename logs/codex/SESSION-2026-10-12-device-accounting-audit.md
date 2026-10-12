# SESSION-2026-10-12-device-accounting-audit — Remaining local token accounting

## Request and scope

The user asked whether this device retained token accounting that should be
updated in the nODD repository. This infrastructure audit follows ADR-004 and
the authorized recovery workflow; no design/ADR approval or scientific source
changes are made. Started on `main` at
`fdfa09a0fb58dd29af467054f9a7dc0b023e30f1`. The four pre-existing untracked
token-gate journal/tool files are preserved byte-for-byte. No commit or push
is part of this task.

## Recovery and attribution

Read repository instructions, PROJECT, ADR-004, logging and dashboard workflows.
Inspected the selected local client store with read-only SQLite connections and
ran the existing usage-only recovery tool for the current project directory and
one explicit thread at its former location. The capture covers 16 threads and
69 turns: 1,110 numeric events, 51 repeated snapshots excluded, and no outside-turn
usage. Each cumulative increase equals its last-request counters. All 26 locally
available observations already owned by canonical records match exactly.

Task matching separately inspected selected visible user requests, session IDs
in command metadata, existing narratives and parent/child activity. No reasoning
items were queried; no raw conversations, commands or private model state are
retained. The first attempted visible-message lookup found no matching messages
in rollout files; the indexed userMessage/commandExecution metadata supplied
attribution. Numeric recovery continued to use the unchanged recovery tool.

The [curated inventory](../usage/USAGE-2026-10-12-device-audit.json) retains exact
boundaries, hashes, request counts, ownership and exclusions. It records 24 new
closed observations across 15 task records: short-strip research and agreement,
PR13 reconciliation, September accounting, October publication and multi-PR
conflict work. Three PubDoc child turns have independently reconciled counters,
a recorded parent edge and an exact child completion ID in the owning parent
turn. Two shared multi-PR turns have one canonical owner each, with companion
journal references; counters are never divided between tasks.

Eight original publication journal pairs absent from main were restored from
local branch revision `7ec9d05dc5ee9aefdf6c0da30549615ebc06a0b0`. The inventory
retains their original SHA-256 values. Original narrative/check evidence remains
intact, followed by dated accounting corrections. Historical publication assets,
scientific changes and task-progress entries are not imported by this audit.

## Outcome and remaining coverage

Added **61,905,180 input** and **230,774 output** tokens, or **62,135,954 total**.
The resulting observed subtotal is **611,570,792 input + 3,502,493 output =
615,073,285 tokens**, across **207 turns in 114 of 161 session records**.
Cached input is 590,254,592 and reasoning output 1,168,047; these are subsets.
The existing 183 observations remain unchanged.

One additional closed token-gate turn has **1,758,566 input + 14,946 output =
1,773,512 tokens** retained as import-ready evidence. Its existing journal is
untracked user work and was not edited; these counters are outside the subtotal.
Thirteen historical orientation/discussion or early scaffold turns lack a
confident matching bounded record. Four failed turns have no observations.
The current audit turn is active and remains uncounted. The earlier October 12
desktop recovery ran against a different device history, so its then-active turn
cannot be finalized from this store. Forty-seven records still have empty usage;
this includes shared-turn companions and does not mean zero consumption.

Execution model/client version, other device coverage and billing equivalence
remain unknown. All numbers are exact observed counters, not estimated totals.

## Commands and validation

- `recover_usage.py --codex-home <selected store> --project <checkout>` and a
  separate `--thread-id` capture: both passed reconciliation.
- `session_log.py import-usage --dry-run`, followed by import: all 15 batches
  passed, adding exactly 24 disjoint turns.
- Logger tests: 22 passed; recovery tests: 11 passed.
- Initial session validation found a missing nullable `version` activity field
  in this new record; supplying `null` corrected it. Validation then passed for
  161 pairs, and `session_log.py summary --format json` produced the totals above.
- Initial dashboard validation and one of 31 dashboard tests failed because ten
  recorded historical commits were absent locally. The evidence fetch first
  failed under sandbox network restrictions; its approved retry fetched all ten.
  Git reported an unavailable historical TDR submodule, but all required parent
  commits resolved and the dashboard does not require that submodule.
- Dashboard validation then passed for 58 tasks, 31 documents and 19 review rounds;
  the build succeeded in a temporary directory. All 31 dashboard tests passed
  on rerun. The synthetic all-zero Git ref failure is an expected test fixture.
- Original usage preservation, restored-journal provenance, untracked-file hash
  checks and `git diff --check` verify the accounting-only change.

Changed paths and actual check results are in the paired JSON. Related governance
is ADR-004 (unchanged, DRAFT); no detector design, source manifest or human sign-off
is changed. Importing the retained token-gate entry belongs with reconciliation
of that pre-existing work; ambiguous historical turns remain unassigned.

## Closed-turn accounting correction — 2026-10-12

During the separately authorized PR-publication task, this audit turn acquired
its persisted completed boundary. The [closeout inventory](../usage/USAGE-2026-10-12-device-audit-closeout.json)
verifies 35 request increases and adds **3,103,786 input + 19,016 output =
3,122,802 tokens** to this record. The original inventory remains unchanged.
The observed project subtotal is now **618,196,087 tokens across 208 turns**.
Earlier active-turn statements describe the first capture; the new publication
turn is distinct and still excluded. No counters are counted twice.
