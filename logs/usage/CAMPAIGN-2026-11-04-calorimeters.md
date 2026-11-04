# Calorimeter campaign accounting — 2026-11-04

This is infrastructure evidence for the user-requested consolidation of ECAL
PRs #70, #71, #73, #74 and #75, issue #114, the earlier software stack #78–#80,
HCAL #81/#84/#85, and already-merged FCAL #88. Scientific source changes,
validation and engineering review remain in their own PRs. This recovery does
not authorize or record design sign-off.

## Recovery and ownership boundary

The [usage-only inventory](USAGE-2026-11-04-calorimeter-campaign.json) contains
16 explicitly selected historical root/child request streams. All **88 closed
turns** reconcile cumulative increases against each last-request observation;
**157 repeated snapshots** are excluded and there are **zero outside-turn
observations**. Exact counter evidence and per-turn SHA-256s remain available.
No raw conversation archive, hidden reasoning, command/output text, credentials,
model-state data or private URLs are retained.

The local client had compressed old `.jsonl` files into `.jsonl.zst` while the
thread database retained their earlier names. The recovery reader now streams
the exact compressed sibling when the recorded plain file is absent. Python
3.14's existing `compression.zstd` is used when available; an already-installed
`zstd` executable supplies the older-Python fallback. No package installation
or raw decompressed temporary file is needed. A changing or invalid archive
fails explicitly. Plain snapshots retain their original bounded-read behavior.

The campaign coordinator reviewed and accepted all sole-owner mappings,
including the shared-turn choices below. **54 new disjoint turns across 17
existing journal owners were imported**, supplying
**258,511,843 input + 1,432,322 output = 259,944,165 observed tokens**. Cached
input 251,152,640 and reasoning output 661,224 are subsets. Execution model,
client version, cost and billing equivalence remain unknown.

Twenty other observations match existing canonical counters byte-for-field;
they must not be imported again. Eleven are FCAL's previously recorded
40,263,905 tokens. The other nine belong to earlier calorimeter-software and
solenoid work. Fourteen earlier/predecessor turns remain explicitly excluded or
unassigned. These rows are accounting dispositions, not estimates of missing
work or proof of complete project coverage.

## Accepted sole owners

| Existing canonical session | New turns | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| `SESSION-2026-10-13-calorimeter-edge-sensors` | 1 | 17,776,027 | 163,609 | 17,939,636 |
| `SESSION-2026-10-13-calorimeter-wedge-correction` | 1 | 6,027,770 | 50,636 | 6,078,406 |
| `SESSION-2026-10-13-siw-barrel` | 4 | 22,142,443 | 165,477 | 22,307,920 |
| `SESSION-2026-10-13-layout002-lar-barrel` | 7 | 40,894,936 | 250,370 | 41,145,306 |
| `SESSION-2026-10-14-ecal-layout-review` | 5 | 24,138,489 | 94,393 | 24,232,882 |
| `SESSION-2026-10-14-ecal-review-envelope-update` | 2 | 10,403,418 | 64,735 | 10,468,153 |
| `SESSION-2026-10-14-pr75-transition-question` | 2 | 3,355,042 | 19,307 | 3,374,349 |
| `SESSION-2026-10-13-layout002-lar-endcaps` | 5 | 10,449,772 | 78,364 | 10,528,136 |
| `SESSION-2026-10-14-siw-service-envelopes` | 3 | 4,479,349 | 26,803 | 4,506,152 |
| `SESSION-2026-10-13-layout-main-page` | 1 | 1,272,058 | 12,826 | 1,284,884 |
| `SESSION-2026-10-14-software-layout` | 1 | 25,811,707 | 130,287 | 25,941,994 |
| `SESSION-2026-10-15-hcal-realism` | 4 | 15,344,953 | 62,182 | 15,407,135 |
| `SESSION-2026-10-15-hcal-common-module` | 8 | 31,031,357 | 123,037 | 31,154,394 |
| `SESSION-2026-10-15-hcal-module-pr` | 1 | 2,874,616 | 11,832 | 2,886,448 |
| `SESSION-2026-10-15-hcal-barrel-design` | 5 | 26,746,292 | 112,284 | 26,858,576 |
| `SESSION-2026-10-15-hcal-endcap-design` | 3 | 7,855,855 | 40,349 | 7,896,204 |
| `SESSION-2026-10-20-fcal-pr88-merge-ready` | 1 | 7,907,759 | 25,831 | 7,933,590 |

Shared turns keep one whole-turn owner. In particular:

- The SiW barrel/main-page root belongs once to the barrel journal; the main-page
  PR references it, while its independently observed child has its own owner.
- The one root that created both LAr PRs belongs once to the barrel journal;
  the endcap journal/PR references that owner and retains its own child turns.
- The SiW parity root that creates service PR76 and updates overview PR75 belongs
  once to the overview-update journal. Child service assignments have separate
  exact owners. Both PRs can reference these shared accounts.
- The HCAL barrel/endcap root and joint SysArch/PhysVal regional reviews belong
  once to the barrel journal. Endcap-specific CaloTech/SoftEng turns belong to
  the endcap journal. PR85 must also reference the shared barrel owner.
- The software migration root belongs once to `SESSION-2026-10-14-software-layout`;
  #78–#80 references are relationships and must never be added as allocations.

These are explicit bookkeeping choices accepted by the campaign coordinator,
not historical per-PR cost splits. They use visible user requests matching existing
journal narratives, observed parent edges, named child assignments and exact
source revisions. No turn is matched by time proximity or message length alone.
The inventory retains each exact match basis and the coordinator decision.
Do not copy or split counters between owners.

The FCAL readiness turn previously excluded as active in its October 20 audit
now has a finalized closed boundary: **7,907,759 input + 25,831 output =
7,933,590 tokens**. Its canonical owner is the existing readiness journal.
The original 11-turn audit remains unchanged. The existing recommendation owner
also needs an explicit PR88 ledger link; it already has counters, so only its
relationship is missing.

## Source journals and import procedure

Thirteen original ECAL/HCAL journal pairs were branch-only on main. They were
restored byte-for-byte from the inventory's immutable source revisions before
usage import, preserving all original narrative text. A dated accounting
correction was appended afterward. The inventory records the original hashes
of all 26 restored pair files. The restored historical pairs are:

- `logs/codex/SESSION-2026-10-13-calorimeter-edge-sensors.json` and its paired `.md` narrative.
- `logs/codex/SESSION-2026-10-13-calorimeter-wedge-correction.json` and its paired `.md` narrative.
- `logs/design/SESSION-2026-10-13-siw-barrel.json` and its paired `.md` narrative.
- `logs/design/SESSION-2026-10-13-layout002-lar-barrel.json` and its paired `.md` narrative.
- `logs/design/SESSION-2026-10-14-ecal-layout-review.json` and its paired `.md` narrative.
- `logs/design/SESSION-2026-10-14-ecal-review-envelope-update.json` and its paired `.md` narrative.
- `logs/design/SESSION-2026-10-14-pr75-transition-question.json` and its paired `.md` narrative.
- `logs/design/SESSION-2026-10-13-layout002-lar-endcaps.json` and its paired `.md` narrative.
- `logs/codex/SESSION-2026-10-15-hcal-realism.json` and its paired `.md` narrative.
- `logs/codex/SESSION-2026-10-15-hcal-common-module.json` and its paired `.md` narrative.
- `logs/codex/SESSION-2026-10-15-hcal-module-pr.json` and its paired `.md` narrative.
- `logs/codex/SESSION-2026-10-15-hcal-barrel-design.json` and its paired `.md` narrative.
- `logs/codex/SESSION-2026-10-15-hcal-endcap-design.json` and its paired `.md` narrative.

For every accepted owner, the standard importer passed `--dry-run`, import and
identical replay. All 54 observations were added once; replay added zero. Turns
are now marked `imported`; prior existing observations remain `already_canonical`.
Affected local ledgers were synchronized, including shared-owner links for
PR72/74/76/85 and FCAL recommendation PR88. The campaign coordinator separately
refreshes public GitHub snapshots before publication. The inventory itself
contributes no additional token total.

The current campaign's root and active child turns are excluded. After those
turns finish, a later bounded capture can add their separately observed counters
with parent/child evidence. Missing current counters remain unknown.

## Executed checks

- Python 3.14.6: 36 session-logging tests passed, including 14 recovery controls.
- Python 3.11: the 14 recovery controls passed using the existing zstd CLI.
- Plain/compressed event ordinals, all counters and evidence digests agree.
- Synthetic private/non-UTF8 lines are neither decoded nor retained; malformed
  archives, missing decoders and changed compressed inputs are rejected.
- Read-only selected recovery: 16 streams, 88 completed turns, all cumulative
  counts reconcile; 157 repeats and zero outside-turn events.
- Canonical session validation and token-site validation/build passed before
  import and are rerun after all 54 finalized historical observations. This establishes infrastructure
  consistency, not calorimeter correctness or engineering acceptance.


## Consolidation, merge order and labels

[Replacement ECAL PR115](https://github.com/asalzburger/nodd/pull/115) targets main
and preserves original branch ancestry through ordinary merges. It restores the
Si–W and LAr component designs and standalone issue114 EDM4hep support. It carries
scientific tracking, validation and the unresolved eleven-question PR75 review.
This infrastructure PR preserves accounting and interactions; it is excluded
from scientific progress. Both PRs target main to avoid the earlier merged-parent
stack failure. Merge this accounting record first, then115 after its current
checks pass; use an ordinary retarget to main when HCAL dependencies land.

| Original PR | Original source head | Campaign disposition / task |
| --- | --- | --- |
|70 |654b85a48abeb38735ad7fe0866c5d1082882df7 | Superseded by115; Si–W endcaps / TASK-B-CALO-EDGE-SENSORS |
|71 |2776266570dda13386a16863e5b0e97432f27217 | Superseded by115; Si–W barrel / TASK-B-CALO-BARREL |
|73 |48e97256f8badd75c022a84ab1c4ff71977c56a2 | Superseded by115; LAr barrel / TASK-B-CALO-LAR-BARREL |
|74 |72d37ee9a56182e4ba974791a848a738c19cf092 | Superseded by115; LAr endcaps / TASK-B-CALO-LAR-ENDCAPS |
|75 |7c7f847bc5a5d52c091c1d2f32203d20f70c27f9 | Superseded by115; reviewer overview and all open human review inputs retained |
|81 |abd95bdc64b9d7971561d659bf953e71de4e7e99 | Refreshed common HCAL baseline design / TASK-B-HCAL-REALISM, TASK-B-HCAL-COMMON-MODULE |
|84 |0e8530d56d171f38c9d53d3c60c8b48803680bbd | Refreshed Si–W barrel HCAL design / TASK-B-HCAL-BARREL-DESIGN |
|85 |c1f11013b03391a4f09d86b39dff57e6c3f58ab2 | Refreshed Si–W endcap HCAL design / TASK-B-HCAL-ENDCAP-DESIGN |
|88 |8e5e056a70691f3f653064d4f37567ec218433c7 | Already merged at91235ecf904a33770f4a7bc60a64b43aaaec59ae; retain common FCAL / TASK-B-CALO-FCAL |

The old ECAL branches, commits, journals, figures, public discussions and formal
review decisions remain available after closure. Supersession is an administrative
handover, not approval or a claim that PR75's engineering questions were solved.
The new baseline selector has distinct tracker/ECAL construction, HCAL/FCAL/magnet
design, calibrated digitization and full detector qualification gates.

The human requested PR labelling. Four additive repository labels were created:
`campaign:calorimeters` (campaign membership), `status:superseded` (linked replacement),
`scope:baseline-design` (working design, no sign-off) and `scope:edm-io` (data/persistence
interfaces). Apply campaign+superseded to70/71/73/74/75; campaign+baseline-design to
81/84/85/88; campaign+baseline-design+edm-io to115 and issue114 as appropriate.
Original labels are retained. Current exact remote state is a dated snapshot in
individual interaction ledgers; publication receipts follow once observed.

Public snapshots for70/71/73/74/75/76/78/79/80/81/84/85/88 were refreshed via the
connected GitHub reader on2026-11-04. PR75 includes the October19 human questions;
none was treated as resolved by closure. The GitHub app denied PR creation with
403, so publication uses the existing authenticated gh CLI without changing credentials.
