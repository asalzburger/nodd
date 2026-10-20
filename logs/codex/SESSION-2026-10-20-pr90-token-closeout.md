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
