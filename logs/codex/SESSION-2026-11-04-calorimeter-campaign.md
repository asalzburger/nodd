# SESSION-2026-11-04-calorimeter-campaign — Consolidate two ECAL baselines, restore issue114 EDM, and prepare HCAL/FCAL campaign

## Scope and evidence

State collection method, available context, limitations, related IDs and starting
revision. Identify uncommitted user changes present before work.

## Selected conversation

Attribute requests to the user and outcomes to the assistant. Mark exact quotes
and paraphrases explicitly. Include corrections and changes in direction.
Exclude private model state, confidential content, and irrelevant system context.

## Decisions and outcomes

State rationale, alternatives, consequences and what remains unresolved. Never
convert implementation authorization into human design sign-off.

## Commands and validation

Record relevant commands, actual exits/results, failed attempts and remedies.
Distinguish structural checks from detector acceptance.

## Changes and revision links

List changed files or refer to the paired JSON inventory. Result commits are
recorded only once they exist; Git history locates this record's enclosing commit.

## Token accounting

Record the client-provided per-turn usage source and import command, or state why
exact counters are unavailable. Report observed input/output sums and missing
coverage from `session_log.py summary`; empty usage means unknown, not zero.
Never copy raw client archives or private model state. Do not duplicate turns
across tasks or add cached/reasoning subsets to the input/output totals.

## Follow-up

List remaining work, missing measurements and any human review needed.

## Initial assignments

Using nodd-coordinate and nodd-review-validation through explicit generic-agent role instructions, not native profile loading. Full contracts and prepared prompts are retained under `logs/codex/assignments/calorimeter-campaign/`. Source main: `cd3ec20da56537617ac6fbbcf28bd6f28104cc64`. Child usage is unknown until closed counters are available.

- `CAL114-SoftEng`: SoftEng, write; Committed implementation on codex/calorimeter-edm114 with actual build/test results, SHA and remaining limitations.
- `CAL114-CaloTech`: CaloTech, read-only; Revision-specific HCAL/FCAL preparation report for coordinator.
- `CAL114-SysArch`: SysArch, read-only; Cited integration/interface report with necessary files, validation, risks and bounded baseline definition.

CaloTech initial read-only report retained by coordinator: HCAL original44/15/19 controls pass; FCAL88 already merged; LAr regional reparameterization is future work. Followup `CAL114-CaloTech-update` authorizes three isolated local ordinary-merge preparation histories under listed owned files. SoftEng license/notice ownership added explicitly.

`CAL114-Accounting` assigns SoftEng compressed usage-only archive support and evidence recovery in the isolated infrastructure worktree. Initial project-wide recovery failed because archived paths now have `.jsonl.zst` suffixes; no missing-token zeros inferred. Full contract and prompt retained. No raw rollouts are committed.

`CAL114-PhysVal` independently reviews committed integration ff8718384b4aff18e5f1fa0d5d8681615069e879 and reruns meaningful controls. Source contract and complete explicit role prompt retained. Root executes native union checks separately; no approval inferred.

## Selected human request and scope

The human requested a single main-targeted replacement for ECAL PR70/71/73/74/75,
including issue114 EDM support; a separate infrastructure PR preserving work,
tokens, interactions and labels; and refreshed HCAL/FCAL baseline design PRs.
The target is two ECAL-distinguished working baseline detectors with an initial
limited digitization interface, followed by physical response work.

The explicit implementation request authorizes this bounded restoration despite
the older M0/prototype default. No design lifecycle is advanced to sign-off or
acceptance. SysArch established that HCAL regions remain analytical and FCAL is
ROOT-only. The delivered selector records those design stages and constructs
actual maintained tracker+ECAL geometry; full detector/response qualification is
tracked separately rather than claimed.

## Integration and independent review

Ordinary merges retain all five ECAL source histories and original evidence;
shared JSON records were reconciled by stable ID. Main's tracker/FCAL drawings,
source records and palette remain. The duplicate historical aperture ADR008 is
now ADR011, with a source alias preserving prior provenance. Main's software
source-layout ADR008 is retained. PR75's eleven outstanding review questions
remain in the integration contract.

SoftEng implemented issue114 at8652406, finalized journal atb260305. Four native
CTest targets and wrong-source/wrong-build controls pass. CaloTech prepared
ordinary main/common merges for81/84/85 with44 common,15 barrel and19 endcap
controls. SysArch identified duplicate component IDs and physical construction
stages. PhysVal independently reran32 SiW+28 LAr+4 native CTests, found the
tracker material naming and stale-reuse problems, and rechecked their correction
at3f665f0 with5 composition controls and producer-failure adverse control.
No separate review implies human approval.

## Actual failures and corrections

- Historical project-wide usage recovery initially failed because DB paths now
  point to compressed archives. A bounded usage-only reader now streams those
  archives; raw rollouts are never retained in Git.
- One intermediate ordinary merge staged unresolved tracking markers after a
  helper rejected differing PR69 collection metadata. The immediately following
  commit reconstructs both histories by stable ID; current JSON validates.
- First new native union failed because namespacing tracker materials removed
  the BeamPipe factory's hardcoded Beryllium name. Tracker material/element names
  now remain unchanged; added ECAL recipes alone are namespaced. No tracker
  factory was modified.
- The next native construction succeeded but its auditor expected a BeamPipe
  assembly. The unchanged factory places bore/wall directly in world; the audit
  now checks that exact physical hierarchy and records launch source identity.
- An initial tracker build command named nonexistent separate LongStrip targets;
  the existing nODDLongStrip target was built successfully instead.

Final native overlap results and publication/accounting receipts are appended
when observed. Active root counters remain excluded until this turn closes.

## Completed specialist usage — 2026-11-04

Exact completed child counters are imported once from the usage-only campaign child inventory, matched through the observed parent/spawn edge and assignment. Shared HCAL/SysArch/PhysVal work belongs once to the campaign owner; the implementation child belongs to the EDM session. Current root and accounting turns remain active and excluded. These are observed counters, not per-PR allocations or billing.
