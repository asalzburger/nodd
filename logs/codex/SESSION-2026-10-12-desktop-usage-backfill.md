# SESSION-2026-10-12-desktop-usage-backfill — Desktop usage recovery after workspace migration

## Scope and evidence

On October 12 the user asked why resource accounting stopped after the move to
the ChatGPT desktop app and Codex workspace, and requested correct project usage.
Read-only metadata inspection found exact `token_count` events beyond October 6.
The former directory filter omitted chats whose cwd was the parent workspace;
the latest committed inventory was also a stale October 7 snapshot.

The recovery tool now supports explicit thread selection without opening
neighbouring chats or querying conversation-item storage. Only numeric usage
events are decoded; raw rollouts and private model state are not retained.

## Attribution and outcomes

The [curated inventory](../usage/USAGE-2026-10-12-desktop.json) records 15
new closed turns, persisted boundaries, request digests and task match bases.
Five entries augment the original cleanup, beampipe/Gen3 and TDR records.
This record owns ten otherwise unlogged turns: nODD material run instructions,
material mapping/CPU plots, and eight nODD calorimeter research/prototype turns
in the ACTS sister repository. Those prototypes correspond to ActsExamples
foundation, clustering, jets and EDM4hep persistence, including ACTS PR4–8.
No scientific software, design status, published sources or approval is changed.

All 34 previously owned turns in the inspected desktop history agree exactly
with the recovered counters. Duplicate snapshots are ignored; cumulative totals
are never entered as per-turn observations. New input + output totals are
93,944,184 + 619,669 = 94,563,853.
The resulting observed project subtotal is 552,937,331.
Cached input and reasoning output remain subsets.

## Checks and limitations

Recovery and 33 logger/recovery tests passed. Every import passed dry-run first.
Explicit no-counting illustration, comparison and realism tasks remain excluded;
internal approval-review threads and uncertain task matches remain unallocated.
The active October 12 turn has no final boundary and is not imported. This is
recoverable local client accounting, not a complete project or billing total.
Actual model/client version remain unknown. See paired JSON for final validation.

## Calorimeter ownership correction — 2026-10-12

The eight calorimeter observations originally imported here now belong solely
to [SESSION-2026-10-10-calorimeter-software-chain](SESSION-2026-10-10-calorimeter-software-chain.md), with identical IDs, counters and source evidence. This record
retains the two material-tool turns. The [dated transfer inventory](../usage/USAGE-2026-10-12-calorimeter-accounting.json)
supersedes the original ownership labels only; the original inventory and
project totals remain unchanged. The earlier narrative describes the initial
import snapshot.
