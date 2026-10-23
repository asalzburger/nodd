# Local token-usage recovery

## Issue95 / PR96 unrooted installation accounting — 2026-10-23

[The usage-only inventory](USAGE-2026-10-23-pr96-accounting.json) reconciles the
explicitly selected desktop chat for the original issue95 implementation and
PR96 creation/delivery. Those activities share **one completed turn**, covering
60 observed requests, and are counted once in the
[original journal](../codex/SESSION-2026-10-23-unrooted-install.md).

| Contribution | Closed turns | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| Issue95 implementation and PR96 delivery | 1 | 7,137,997 | 24,680 | **7,162,677** |

Cached input **7,031,040** and reasoning output **8,526** are subsets. Every
cumulative increase matches its last-request counters from zero; no repeated
snapshots, outside-turn events, existing canonical owners or child threads were
found. Dry-run/import/replay yields one addition followed by zero additions and
one unchanged entry. The inventory corroborates the journal and is not another
contribution to totals.

A later [closed-boundary capture](USAGE-2026-10-23-pr96-closeout.json) observes
the accounting follow-up complete: 7,262,523 input + 17,992 output = 7,280,515
additional tokens over 36 requests, owned by its existing accounting journal.
Together the two issue95/PR96 turns contain **14,400,520 input + 42,672 output =
14,443,192 tokens** across 96 requests. Cached 14,241,792 and reasoning 15,554 are
subsets. The original provisional snapshot remains historical evidence.

The new tracker-propagation task is separate. Its [specialist usage capture](USAGE-2026-10-23-tracker-propagation.json)
is owned by the tracker journal, with the active scientific parent excluded from
finalized totals. Execution model/client version, billing and other-device
completeness remain unknown.

## PR91 material-recording profiling accounting — 2026-10-21

[The usage-only inventory](USAGE-2026-10-21-pr91-accounting.json) reconciles the
explicitly selected PR91 desktop chat and its two recorded specialist children.
Eight completed turns cover 267 observed requests: the original profiling/PR
turn, two explanations, two SoftEng assignments and three PhysVal assessments.
Ten repeated cumulative snapshots are excluded; no usage falls outside persisted
turn boundaries. Each parent/child stream reconciles independently from zero;
no inherited prefix or parent aggregate is counted twice.

| Contribution | Closed turns | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| Main work and two explanations | 3 | 33,052,857 | 170,249 | 33,223,106 |
| SoftEng specialist | 2 | 3,828,921 | 17,317 | 3,846,238 |
| PhysVal specialist | 3 | 4,426,350 | 18,001 | 4,444,351 |
| **Total** | **8** | **41,308,128** | **205,567** | **41,513,695** |

Cached input 40,301,824 and reasoning output 100,184 are subsets. Input includes
repeated/cached context; this is observed client accounting, not a billing or
unique-text estimate. The [original journal](../codex/SESSION-2026-10-21-material-profile.md)
owns all eight entries once. The current accounting turn is active and excluded.
Dry-run/import/replay confirms eight additions and zero duplicate ownership.
Actual execution model/client version and other-device completeness remain
unknown. The inventory corroborates the journal; never add both to totals.

## PR88 FCAL accounting — 2026-10-20

The [usage-only inventory](USAGE-2026-10-20-pr88-accounting.json) reconciles
five explicitly selected threads: the parent FCAL chat and its four recorded
specialist children. Eleven completed turns add **40,048,091 input + 215,814
output = 40,263,905 observed tokens** from 262 requests. Cached input
39,084,928 and reasoning output 74,935 are subsets. Twenty-six repeated
cumulative snapshots are excluded; no usage event falls outside persisted
turn boundaries. Parent and child request streams reconcile separately from
zero; no parent aggregate or inherited prefix is added again.

| Canonical task owner | Closed turns | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| Common FCAL recommendation | 1 | 1,592,557 | 13,860 | 1,606,417 |
| Common design, including eight specialist turns | 9 | 35,895,875 | 178,317 | 36,074,192 |
| LAYOUT-001 SVG and summary | 1 | 2,559,659 | 23,637 | 2,583,296 |

The original recommendation journal pair was copied from its existing authored
record in the sister checkout without changing that checkout; original hashes
are retained. Existing unknown-usage statements remain with dated corrections.
Dry-run/import/replay confirms 11 additions and no duplicate ownership.
The current accounting/conflict-resolution turn remains active and excluded.
These are client observations, not a billing estimate or complete device history.

## Remaining-device audit — 2026-10-12

The [audit inventory](USAGE-2026-10-12-device-audit.json) checks 16 local project
threads and 69 turns, including a former checkout location. All 1,110 usage
events reconcile; 51 repeated snapshots are ignored and no usage falls outside
persisted turn boundaries. Twenty-six existing observations match exactly.

Twenty-four additional closed turns add **61,905,180 input** and **230,774
output** tokens, bringing the observed project subtotal to **615,073,285**
(611,570,792 input plus 3,502,493 output), across **207 turns**. Three of the
new turns are separately verified PubDoc child turns. Shared multi-PR turns
have one owner and companion journal references, with no token allocation by PR.

Eight historical publication journal pairs were restored from local branch
revision `7ec9d05dc5ee9aefdf6c0da30549615ebc06a0b0`; original file hashes are
retained. Only journals and accounting evidence were restored. The full
[session record](../codex/SESSION-2026-10-12-device-accounting-audit.md)
documents attribution, checks and limits.

One closed token-gate turn has **1,758,566 input** and **14,946 output** tokens
retained as import-ready evidence; it is not added to the subtotal because its
journal is pre-existing untracked user work, preserved byte-for-byte. Thirteen
orientation/discussion or early scaffold turns still lack a confident bounded
record match. Four failed turns have no observations, and the current active
turn remains uncounted. The prior desktop recovery ran against another device
history, so its then-active October 12 turn cannot be finalized here. These are
partial client observations, not complete project usage or billing.

### Audit closeout during PR preparation

The [follow-up inventory](USAGE-2026-10-12-device-audit-closeout.json) captures
the audit turn after completion: **3,103,786 input + 19,016 output = 3,122,802
tokens**. This adds one disjoint observation to the audit's own journal while
preserving the original snapshot. The two device inventories therefore add
**65,008,966 input + 249,790 output = 65,258,756 tokens**, bringing the project
to **618,196,087 observed tokens across 208 turns**. The new PR-publication turn
remains active and uncounted; all other exclusions above remain in force.

### Publication closeout and PR63 compatibility

The [publication closeout inventory](USAGE-2026-10-12-pr62-publication-closeout.json)
adds the now-completed PR62 publication turn: **2,607,532 input + 9,208 output =
2,616,740 tokens**. PR62 now contributes **67,616,498 input + 258,998 output =
67,875,496 tokens**, bringing the observed project subtotal to **620,812,827**
across **209 turns**. The current compatibility-check turn remains uncounted.

The token dashboard introduced by PR63 now accepts retained, explicitly
in-progress snapshots as lower-bound evidence for later finalized observations.
Such snapshots supply no final counters or completion date. Provisional counters
above final counters and all conflicting finalized evidence still fail validation.
The September 25 historical inventory is preserved byte-for-byte. See the
[synchronization record](../codex/SESSION-2026-10-12-pr62-main-sync.md).

## Canonical synchronization — 2026-10-07

The [audit](AUDIT-2026-10-07.md) and [new curated inventory](USAGE-2026-10-07-synchronization.json)
consolidate the available branch/local journals without importing unrelated
scientific work. All 67 previously pending-branch entries from the two older
inventories now have their exact original observations/source in canonical
records; 12 were already present in the selected branch variants and 55 were
newly imported. Eighteen additional completed app turns were recovered.

All 95 existing observations reconcile. The 73 additions produce 168 disjoint
observed turns in 93 of 145 paired records, with no duplicate ownership and
all five observed counters. Every import passed dry-run first. The original
inventories remain byte-identical; their pending labels describe the old capture
and are superseded only by this dated correction.

The current cleanup turn remains uncounted while active. The expressly excluded
illustration/history turn cannot be split exactly, so it stays wholly excluded.
Older unattributed turns and unobserved store/device history remain gaps; empty
usage arrays are not zeros. Model/client identity and billing equivalence are
unestablished. These are observed partial subtotals, not complete project usage.

## Second-device recovery — 2026-09-25

At the user's request, [the second-device inventory](USAGE-2026-09-25-device.json)
extends PR #18's recovery. It contains 12 project threads (9 child threads) and
37 turns. All 529 token-count events reconcile: 14 repeated cumulative snapshots
are excluded, leaving 515 request increases and no outside-turn observations.
The capture timestamp is retained in the inventory. No thread/turn pair overlaps
the first inventory or previously imported session usage.

| Disposition | Turns | Task records | Input tokens | Output tokens |
| --- | ---: | ---: | ---: | ---: |
| Imported into existing dashboard session logs | 4 | 4 | 8,515,036 | 64,602 |
| Matched to records on other cached Git branches | 22 | 10 | 39,680,436 | 189,890 |
| Closed turns without a bounded task assignment | 6 | — | 881,455 | 4,508 |

The second-device **observed closed-turn subtotal** is **49,076,927 input** and
**259,000 output** tokens. Four failed child turns have no observations and are
not treated as zero. One current recovery turn has only an incomplete snapshot
and is not imported. Requested model names do not establish execution identity;
model fields remain null.

This fills all four dashboard gaps listed in the first recovery. Each root turn
matches its user-visible request, existing narrative and session-ID tool activity.
Child assignments additionally retain the recorded parent edge, parent turn,
spawn/followup ordinal and target agent. Parent and child counters reconcile
independently from zero against their own last-request observations.

Pending entries cover six pixel-module sessions, two PR #13 tracker-review
sessions, the PR #6 conflict repair and the magnetic-expert response. Exact cached
branch revisions and record paths are retained with each entry. They are ready
for import when those session records are present in the target checkout; no
scientific branch content was copied or merged. Six orientation or short
discussion turns remain unassigned instead of being attached by time alone.

After import, the normal session summary reports **98,045,726 input** and
**477,200 output** tokens across **67 turns in 38 of 41 sessions**. Cached input
is 94,477,952 and reasoning output is 68,817; both are subsets, not extra tokens.
The physics-role session shares a turn already counted in stage-b-roles. The
first and second recovery tasks themselves still lack completed-turn accounting.
These totals exclude pending-branch and unassigned turns and do not establish
complete project usage or billing.

The first inventory below is preserved as a historical snapshot. Its statement
that dashboard usage was missing is superseded by this dated update. For pending
entries from this device, use the extraction example below with
`USAGE-2026-09-25-device.json` as the input inventory. Import replay was checked
for all four dashboard sessions and added no duplicate observations.

## First-device recovery — 2026-09-24

The user authorized recovery on 2026-09-24 from this local machine and stated that
another computer may hold missing sessions. This is infrastructure accounting,
not scientific progress or design approval.

The [usage-only inventory](USAGE-2026-09-24-local.json) is a snapshot taken at
2026-09-24T15:32:06Z. It covers 18 project threads, including 15 child threads,
and 1,735 token-count events. Removing 60 repeated cumulative snapshots leaves
1,675 reported requests. Every increase reconciles with its last-request
counters; all requests fall within persisted turn boundaries. No cumulative
reset or inherited counter prefix was observed.

| Disposition | Turns | Task records | Input tokens | Output tokens |
| --- | ---: | ---: | ---: | ---: |
| Imported into the current branch's session logs | 63 | 34 | 89,530,690 | 412,598 |
| Matched to records on other cached Git branches | 45 | 13 | 89,902,706 | 370,599 |
| Closed turns without a confident task assignment | 11 | — | 2,915,502 | 8,423 |

The recovered **closed-turn local subtotal** is **182,348,898 input** and
**791,620 output** tokens. It includes the three disjoint rows above. It is not
a full project total: other-machine usage is unknown. One interrupted turn has
no token observations, and the ongoing recovery turn is excluded from this
subtotal. Its inventory counters are an explicitly incomplete snapshot.

For the imported row, 86,221,568 input tokens were reported cached and 53,704
output tokens were reported reasoning. These are subsets, not additional usage.
These figures are client-reported accounting, not a billing statement. Actual
per-turn model identity was not established and remains null.

## Attribution and gaps

Primary turns were matched by reviewing user-visible requests against the
existing curated narratives and session-ID references in tool activity. The
inventory retains the turn IDs, boundaries, timestamps, target session and match
basis. Child turns were matched through recorded parent/child edges and the
parent turn's activity targeting that child; timestamps only corroborate those
relationships. Each thread's counters reconcile independently against its own
reported requests; no unexplained parent/child aggregate was observed.

The physics-validation-role request and naming correction occurred as steering
inside the stage-b-roles turn. All of that turn's tokens are attributed once to
`SESSION-2026-09-16-stage-b-roles`; the physics-role record cross-references it
without adding the same turn again.

Four existing dashboard records have no matched local turn:

- `SESSION-2026-09-17-dashboard-plan`
- `SESSION-2026-09-17-dashboard-implementation`
- `SESSION-2026-09-17-dashboard-pr4`
- `SESSION-2026-09-17-dashboard-pages`

The other computer may supply these; absence here does not prove where the work
ran. Eleven short orientation, status or discussion turns remain unassigned
rather than being allocated to nearby tasks by time alone. No usage entry is
inserted for a turn without observed counters, and no active turn is imported.

The 13 pending task records belong to magnetic-configuration research, first
tracker layouts and pyacts studies. Their exact cached Git
revisions and repository paths are recorded in each `target_record`. This PR
does not merge those branches or copy their scientific documents into main.
Their usage entries are retained for import once the appropriate records are
available in the target checkout. After fetching and merging main at
`d449b7033561472a16a016bfdaf2549d34339372`, the TDR publication-plan record became available; its two matched
turns are included in the imported row. The source snapshot stays unchanged.

## Continue on another branch or computer

Use [the logging guide](../README.md#authorized-local-historical-recovery) to
create a fresh usage-only inventory from the other local store. Do not collect
raw conversations or private model state. Verify counter semantics and review
task assignments before importing. The `(client_thread_id, turn_id)` pair is the
deduplication key across machines and project sessions. Copied or synchronized
history must not be counted twice.

To extract a pending session's already curated entries from this inventory,
set the target ID and a new temporary output filename, then run:

```sh
python3 -B - "$project_session_id" "$new_usage_batch_file" <<'PY'
import json
from pathlib import Path
import sys

report = json.loads(Path('logs/usage/USAGE-2026-09-24-local.json').read_text())
entries = [turn['usage_entry']
           for thread in report['threads'] for turn in thread['turns']
           if turn['target_session_id'] == sys.argv[1]
           and turn['disposition'] == 'pending_branch']
if not entries:
    raise SystemExit('No pending entries for this session')
with Path(sys.argv[2]).open('x') as handle:
    json.dump(entries, handle, indent=2)
    handle.write('\n')
PY
python3 tools/session_logging/session_log.py import-usage \
  --id "$project_session_id" --file "$new_usage_batch_file" --dry-run
python3 tools/session_logging/session_log.py import-usage \
  --id "$project_session_id" --file "$new_usage_batch_file"
```

The target session must already exist in that checkout. Append a dated narrative
correction and retain the inventory's exact evidence source. Identical replays
do not change totals; conflicting observations require reconciliation, not
overwriting. Once imported elsewhere, record that later disposition in a new
dated update; this snapshot describes the state of this recovery.

Only `logs/codex/` and `logs/design/` usage entries feed the normal project
summary. This directory retains evidence copies and pending data. **Never add
the inventory's imported row to the session-summary total again.**

## Reproducibility

`tools/session_logging/recover_usage.py` reads selected client metadata with
read-only SQLite connections and decodes only token-count event lines. It takes
a bounded file-size snapshot and ignores any partially written final line.
Per-turn SHA-256 values cover canonical JSON of the contributing usage events
(ordinal, timestamp, cumulative counters and last-request counters), excluding
repeated snapshots. This permits comparison against a future extraction without
retaining raw client content. Model names, costs and missing usage are not
inferred. Historical narratives remain intact with dated token-accounting
corrections appended.

## Desktop workspace backfill — 2026-10-12

The [new inventory](USAGE-2026-10-12-desktop.json) adds 15 exact closed turns
through October 10 and verifies 34 existing desktop observations unchanged.
The project subtotal rises by 94,563,853 to **552,937,331 observed tokens**.
This includes explicitly nODD calorimeter prototype work in the ACTS sister
checkout; it excludes prior no-counting scopes and the active October 12 turn.

Directory-based recovery can miss desktop chats opened at a parent workspace.
Use the opt-in explicit-thread mode, then curate project/task ownership. A stale
inventory cutoff does not imply lost counters or zero subsequent consumption.
The [backfill record](../codex/SESSION-2026-10-12-desktop-usage-backfill.md) documents scope and gaps.

## Dedicated calorimeter accounting — 2026-10-12

The [calorimeter record](../codex/SESSION-2026-10-10-calorimeter-software-chain.md) owns the eight
October 10 software-chain observations already imported via PR59. Their subtotal
is **27,882,303 input + 195,220 output = 28,077,523 tokens**. The
[dated ownership correction](USAGE-2026-10-12-calorimeter-accounting.json)
records the unchanged transfer from the mixed desktop backfill record.
The original inventory remains intact; global totals stay at 552,937,331 across
183 disjoint turns. Never add this subtotal to the project total again.

## PR6 conflict-resolution audit — 2026-10-12

[The PR6 audit](USAGE-2026-10-12-pr6-accounting-audit.json) verifies both known
local project locations (16 threads, 72 turns) against canonical owners. All
52 already recorded local observations match their five counters. The normal
main merge brings 36 historical observations across eleven magnetic-research
session records into PR6: input 56,250,297, output 211,577, total 56,461,874.
These were already in main and must not be imported or counted again.

No additional historical PR6 counters could be confidently attributed locally.
The September 28 PR6 merge-maintenance task still has unknown usage. The
current PR6 update turn is active and excluded. One newly closed preceding
PR62 synchronization turn was imported into its own original record, adding
3,472,126 input and 14,452 output tokens (3,486,578 total) to project accounting.
Unassigned historical observations retain their earlier disposition.


## PR89 IdRes study accounting — 2026-10-20

[The PR89 inventory](USAGE-2026-10-20-pr89-accounting.json) recovers three closed
turns from the explicitly selected desktop chat:67 observed requests, with two
repeated cumulative snapshots excluded and no outside-turn observations.
All three turns belong to the original IdRes comparison and its continuation;
none had an existing canonical owner. Interrupted/failed client statuses retain
their observed consumption.

The [original IdRes session](../codex/SESSION-2026-10-19-odd-idres-comparison.md)
now owns **12,783,549 input + 53,939 output = 12,837,488 observed tokens**.
Cached input12,530,816 and reasoning output15,583 are subsets, not additions.
Dry-run/import/replay verified unique ownership; replay adds nothing.
The active accounting/readiness follow-up remains excluded until it closes.
The inventory is supporting evidence and must never be added again to the
journal subtotal. Client version and actual execution model remain unknown.
