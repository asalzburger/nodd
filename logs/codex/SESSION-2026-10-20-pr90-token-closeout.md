# PR90 token accounting and B2 scope closeout

User requests updating token accounting for PR90 work before merge. User also confirms middle barrel B2 only; the physical candidate already matches. This is accounting/documentation closeout, no detector or field change or merge authorization. Starting clean f1089e3ece830dbbb2bdaaf86ade19e13585a471. Apply authorized usage-only recovery in logs/README.md: read selected client metadata/token_count observations only, no conversation items/private model state; disjoint closed turns only. Root current active accounting turn stays provisional.

## TA-A1 before dispatch

```json
{
  "id": "TA-A1",
  "role": "SoftEng",
  "input_revision": "f1089e3ece830dbbb2bdaaf86ade19e13585a471",
  "inputs": [
    "logs/README.md",
    "logs/usage/README.md",
    "tools/session_logging/recover_usage.py",
    "tools/session_logging/session_log.py",
    "tools/token_usage/README.md",
    "logs/design/SESSION-2026-10-20-pr90-sketched-stagger.json",
    "logs/design/SESSION-2026-10-19-pr90-acts-propagation.json",
    "logs/design/SESSION-2026-10-19-muon-chambers-frame.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Audit PR90 accounting ownership and recovery expectations from pinned repository records. Identify all PR90 session JSON/Markdown pairs and existing usage entries, parent/client IDs, task boundaries, existing source Git revisions and exact evidence that could map local closed turns/children without time-only guesses. Read other relevant journal/usage files from same exact revision and report locators. Check existing duplicate ownership/exclusions and accounting-site semantics. No private client-store or raw conversation/rollout access; root handles opt-in usage-only recovery. No source/file edits, commits, native/dependency work, nestedagents or externalmessages. Ownscratch /private/tmp/pr90-TA-A1-* only. Return session-scope map/report plus risks; can assess later root-provided sanitized usage inventory with exact hash under supplemental assignment. Do not invent counts/turn IDs, allocate shared multi-PR totals by time or treat missing aszero. No human design acceptance ormerge.",
  "deliverable": "Pinned read-only PR90 session/ownership inventory and evidence map, with observed gaps and required disjoint attribution checks.",
  "completion": "Root can reconcile recovered usage against existing owners and identify confident PR90 records versus excluded/shared/unknown work."
}
```

## Recovery and first import

Authorized opt-in recovery selected parent thread01a142fe-aeff-7a72-a51f-edbcc74643b8 and17PR90 specialist threads plus the accounting specialist. Earlier PR86/87 children/turns were excluded. The helper decodes only token_count events; attribution separately reads only indexed visible user request/command metadata and recorded parent edges/root-turn IDs, never reasoning or agent-message items. Direct SESSION-ID commands plus pinned narratives distinguish tasks; two retry turns with no first-user item match their exclusive canonical task-ID metadata. The late HCAL/ECT answer matches endcap-wheels journal:93; next-comment+updated-comment match sketched-stagger:3.

All cumulative increases reconcile to last-request observations and persisted turn boundaries. The first scientific/delivery backfill is39closedturns (16root/23child):244250248input+1100633output=245350881tokens. Failed/interrupted attempts with actual counters are included. One finalized accounting-audit child adds2333510input+9582output=2343092tokens. First import40turns/247693973tokens in11canonical records; each batch dry-run then imported sequentially. No existing ownership overlaps and no currentactiveparent count is finalized. Models/clientversion/cost areunknown. Alltenhistorical narratives receive datedcorrections preserving original unavailability notes.

TA-A1 independent pinned f1089e3 audit reproduces199originaljournals/210turns/624299405tokens and finds tenPR90emptyusage records. Prepared contract textual repetitions are not assumed child turns. The retained session audit maps original scope/assignment locators without privateclientaccess.

After firstimport, logger validates200records; token-site validates/builds250disjointdatedturns/871993378observedtokens. No accountingsoftware/source changes needed. B2-only scope confirmed byuser and docsupdated; science/rawdata are not regenerated. Further independent exact-snapshot ownership audit precedes final publication.

## TA-A2 before dispatch

First-import source/accounting snapshot committed before separate assessment.

```json
{
  "id": "TA-A2",
  "role": "SoftEng",
  "input_revision": "a52d1cbd55a680e4bfc8a89219cd45819fa57506",
  "inputs": [
    "logs/usage/USAGE-2026-10-20-pr90.json",
    "logs/usage/PR90-2026-10-20-summary.json",
    "logs/usage/PR90-2026-10-20.md",
    "logs/usage/PR90-2026-10-20-session-audit.json",
    "logs/codex/SESSION-2026-10-20-pr90-token-closeout.json",
    "tools/session_logging/session_log.py",
    "tools/session_logging/recover_usage.py",
    "tools/token_usage/build.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independent exact-snapshot check of completed first-import PR90 accounting at a52d1cbd55a680e4bfc8a89219cd45819fa57506 against baselinef1089e3. Read additional canonical journals/executionevidence only from exacttarget. Verify39scientific/deliveryclosedturns(16root/23child)245350881tokens andonefinalizedaccountingchild2343092=>40/247693973; allfivecounters sourceinventory exactlymatchcanonicalusageentries/uniqueowners, baseline210recordsusage +40=250 andtotal624299405+247693973=871993378. Correctcached/reasoning subsets, actualclosedcompletiondates/globalcurve, nullmodel limitations. Review taskmappingdirectrequest/session-ID narrativeevidence incl retries, failed/interruptedcounterturns and delayedwheelquestion/supersedingcomment; childparentedge/root_turn_id+agentpath matchtaskowner, no timestamp-only allocations orparentaggregatedoublecount. EarlierPR86/87excluded andactivecurrentparentunimported. Recoverytool semantics reviewed; no privateclientDB/rolloutaccess or modelcontent. Independently run pinnedlogger/tokenbuilder againstscratch extractedsources/journals/evidence; verifyidempotentimportreplay/dedup withouteditingrepo iffeasible. Verify source/field/geometry/native/OBJ/figures unchanged vsf108 asideREADME/DESscopeconfirmation anddocumentation/records; confirmactualsourceidentitiespreserved. No newnative/dependencies/merge/commits/nestedagents/externalmessages. Ownscratch/private/tmp/pr90-TA-A1-* only. Return portablechecker/report/JSON, exacthashes/checks/materialfindings; stopafterboundedassessment. Yournewcurrentauditturn remainsprovisional untilrootcapturesclosedcounterlater; do not inventselfusage.",
  "deliverable": "Exactsnapshot independent accounting/disjointness and immutable-science assessment with portablechecker and actual structured results, scratchonly.",
  "completion": "40observations/canonicaltotals/datecoverage/uniqueness and taskownership supported or specificcorrection reported; no unsupportedcompletebilling/activeparentusage claim."
}
```

## Focused verification

Existing logger/recovery tests33/33 and token-site tests10/10 pass. Node chart mode/keyboard tooltip checks pass. Projectrecords69tasks/38documents/21reviewrounds and8roles/3skills validate. First-import curve has250datedobservations/0undated and matches871993378headline; no premature PR90merge milestone marker is added. Identical import dry-runs are no-ops acrossall11batches:0new/40unchanged. These are data/ingestion checks, not a repeat of detector validation.

## TA-A2 result and final closed capture

TA-A2 passes at exact first-import revision a52d1cbd55a680e4bfc8a89219cd45819fa57506, with no material finding. Retained report/checker/original JSON and coordinator replay live in logs/usage/pr90-review/. Both executions pass 1,082 assertions. Original result SHA256 5fa56765f76cdab7ea1b42099846c1fc74676e8c0c0a947456703d202e686915; checker eef2d00fcfb4080fc74ee5f06bf0b5ff87685ca752367ec3fd2ad82e55db377d. The independent assessment checks retained metadata and arithmetic, without reopening private client sources. All 661 scoped science/source blobs are unchanged.

After A2 completed, explicit usage-only recovery of its named thread reconciles 43 events with one repeated snapshot, zero outside-boundary events and two closed turns. A1 matches its original digest/counters exactly. A2 turn01a15969-48f9-7c92-8f73-7c6d534fa9da has18request increases at persisted177..304, with3305551input/3251200cached/15287output/4487reasoning/3320838total. Its parent edge, matching agent path and indexed root_turn_id tie it to the recorded TA-A2 assignment. Separate closeout inventory preserves the original first snapshot. Dry-run then actual import add only A2; all historical entries stay unchanged.

Final PR90 closed subtotal41turns249889309input+1125502output=251014811tokens, including39scientific/delivery and2accountingreviewturns. Global251observations870643545input+4670671output=875314216tokens. The current parent turn remains active and uncounted; no final estimate is invented. The accounting record can close as delivered data/documentation while this explicit current-turn limit remains. The B2-only scope confirmation matches the geometry; no engineering acceptance or merge is inferred.

## Record closeout

Final logger/project/workflow/token validation passes: 200 journals, 69 tasks, 38 documents, 21 review rounds, eight roles and three skills. Dashboard builds with251dated/0undated observations and875314216tokens. Final coordinator reconciliation (logs/usage/pr90-review/final-coordinator-check.json) verifies all210previous observations exact, 41new unique observations matching both inventories and canonical owners across allfivefields, original firstinventory unchanged, and A2 replay0new/1unchanged. This last delta is coordinator-checked; independent assessment remains pinned to first40. No detector rerun is needed for accounting/data-only edits. Publication uses the existing PR90 branch; remote readback/CI are reported with delivery, without merging.
