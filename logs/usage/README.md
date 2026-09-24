# Local token-usage recovery

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
| Imported into the current branch's session logs | 61 | 33 | 86,460,827 | 389,669 |
| Matched to records on other cached Git branches | 47 | 14 | 92,972,569 | 393,528 |
| Closed turns without a confident task assignment | 11 | — | 2,915,502 | 8,423 |

The recovered **closed-turn local subtotal** is **182,348,898 input** and
**791,620 output** tokens. It includes the three disjoint rows above. It is not
a full project total: other-machine usage is unknown. One interrupted turn has
no token observations, and the ongoing recovery turn is excluded from this
subtotal. Its inventory counters are an explicitly incomplete snapshot.

For the imported row, 83,298,944 input tokens were reported cached and 51,409
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

The 14 pending task records belong to magnetic-configuration research, first
tracker layouts, pyacts studies and TDR publication work. Their exact cached Git
revisions and repository paths are recorded in each `target_record`. This PR
does not merge those branches or copy their scientific documents into main.
Their usage entries are retained for import once the appropriate records are
available in the target checkout.

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
