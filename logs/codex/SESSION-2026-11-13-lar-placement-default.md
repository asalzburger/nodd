# SESSION-2026-11-13-lar-placement-default — Maintained LAr DD4hep hierarchy

## Scope and authority

Contemporaneous follow-up to PR138, starting at clean revision
`e91a1cb7099f830bf42e5fc63455344d2aa810fb`. New dedicated worktree and branch
`codex/lar-placement-default`; unrelated worktrees preserved. PR138 was observed
open and ready for review, with all three required CI jobs successful. This task
preserves that state and prepares a separate dependent draft PR.

Selected user request, exact: “Great, go ahead - and update the DD4hep description
of the ALLIGRO calorimeter.” Interpreted in context as authorization to adopt the
measured reusable hierarchy in the maintained LAYOUT-002 prototype. This grants
no engineering/response sign-off and does not resume the deferred 10k study.
The project's established spelling is ALLEGRO.

## Implementation and description

The baseline selector passes `--real-periods` to both LAr exporters together with
their existing local services. Its manifest records observed policies and counts;
a maintained export fails if the selected hierarchy is absent/unrecognized.
Standalone component defaults remain the legacy comparison controls. No factory,
physics parameter, material recipe, solid, physical placement or ID changed.
DES032/DES033, the integration contract and layout pages explain the hierarchy.
R–Z inputs/bounds remain unchanged; deterministic drawing check passed.

The coordinator used `nodd-coordinate`, `nodd-review-validation` and `acts-spack`.
The native profiles were not loaded by the client: full prepared role mandates
were supplied explicitly to the existing generic agents in this new checkout.

## Runtime and executed checks

Spack preflight returned2 for changed setup/lock fingerprints. The user was warned
before dependent work. Actual package/runtime checks passed through
`software/env/run.sh`: DD4hep1.38/3yd4hz3, Geant411.4.3/wfg55xi,
ROOT6.40.04/szgev3e, EDM4hep1.1.1/bsgcccc and podio1.8/hg64alv; all twelve
Geant4 datasets reported installed. No shared software was installed or modified.
The same setup/lock hashes as the prior investigation were retained.

The maintained export completed fresh tracker generation and both serviced ECAL
components, with system IDs0–7/10/11. All39LAr and8baseline controls passed.
Five tracker factories/component maps compiled freshly. The unchanged PR138 LAr
library artifacts were reused by exact hash, with source bytes unchanged.

`check_export.py` binds the fresh full compact to the retained full legacy model
and the measured ECAL-only candidate. An initial strict candidate comparison
failed solely because the variant helper appends each envelope after pieces,
while the standalone exporter emits it first. After explicitly normalizing only
that declaration's sibling position, both ECAL subtrees match. Removing only the
four envelopes restores the entire legacy tracker/ECAL XML; all materials are
byte-identical. The retained legacy exporter hash matches the starting revision.
All other attributes, ordering and text are compared, ignoring indentation.

A fresh serial seven-event probe extracted the ECAL from the maintained compact.
Its launch identity stayed unchanged. All43648sensitive IDs and274689terminal
material leaves reproduce the prior candidate dump hashes. Native/DDG4 transforms
meet the retained tolerances. Saved-hit readback passed canonical-ID/high-bit/
virtual-bin, primary, finite-energy and aimed barrel/wheel/signed-side checks.
This run overlapped the native scan and supplies no new comparative timing claim.
Full generated artifacts stay under ignored `build/lar-default/`.

The complete tracker/ECAL overlap scan is recorded separately once complete.

## Separate assessment and corrections

SoftEng `/root/larplace_softeng` completed the four-file implementation contract;
8baseline and39LAr controls passed. No factory/physics writes or native runs by
that agent. The coordinator reviewed the implementation and ran export/runtime.

PhysVal `/root/larplace_physval` reviewed exact implementation revision
`14db490a29d1b8835788e56a0dae99a514a8b7bd` read-only. It independently ran the
same8+39controls and found two wording issues: unqualified historical legacy
“default” and unqualified startup improvement. Both were corrected to distinguish
the historical/standalone control and the measured ECAL-only serial scope. It
required fresh full-model equivalence, full union overlaps and seven-event saved
readback; final evidence review will be recorded at its exact target revision.
No human design acceptance is inferred from agent assessment.

## Record checks and preserved failures

The first scientific-record validation rejected a task/stream role mismatch;
correcting the new WS-CALO task to its canonical Calorimeter technician role
resolved it. Inventory refresh/check, project records, session validation,
workflow assets, deterministic drawing and token-site build passed.
Sandbox network DNS failed for GitHub fetch/view; the authorized commands
succeeded through scoped elevated execution. No automatic approval rejection
occurred. The GitHub connector's previously observed write403 limitation makes
authenticated gh CLI the publication fallback.

## Tokens, artifacts and follow-up

Exact parent/child per-turn counters are unavailable. Usage stays empty, not
zero; no historical observations are copied. The site build sums existing
canonical observations only. Large XML/ROOT/dumps/logs stay local and ignored.
The PR must remain draft under repository policy. Review and merge of PR138 and
this adoption change are distinct from engineering qualification. Twelve-worker
initialization and the10k response comparison remain later work.

## Assignment before dispatch

Explicit generic SoftEng assignment, profile/skills from the clean starting revision; no native profile loading claimed.

```json
{
  "id": "LAR-DEFAULT-SoftEng-implementation",
  "role": "SoftEng",
  "input_revision": "e91a1cb7099f830bf42e5fc63455344d2aa810fb",
  "inputs": [
    "tools/calorimeter_baselines/export.py",
    "tools/calorimeter_baselines/test_export.py",
    "tools/calorimeter_baselines/README.md",
    "tools/lar_calorimeter/README.md",
    "docs/design/inputs/DES-032-lar-placement-initialization.md",
    "docs/validation/lar-placement/README.md"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/calorimeter_baselines/export.py",
    "tools/calorimeter_baselines/test_export.py",
    "tools/calorimeter_baselines/README.md",
    "tools/lar_calorimeter/README.md"
  ],
  "task": "Implement user-authorized adoption of reusable real periods for the maintained LAYOUT-002 DD4hep baseline export, analogous to LAYOUT-001 real wedges. Standalone component defaults remain legacy for control/validation. Record selected placement policy in baseline manifest if appropriate. Add meaningful regression coverage of actual baseline export selection and document usage. Do not change physics/parameters/IDs/materials/factories. Do not commit; coordinator will integrate and commit. No further delegation.",
  "deliverable": "Return focused implementation in owned files, actual tests and limitations. Coordinator owns layout/design/evidence/session/inventory/tracking and runtime validation.",
  "completion": "LAYOUT-002 baseline selects --real-periods for both LAr components; tests verify exporter path and retain SiW selection. Docs accurately separate maintained prototype default, standalone controls and physics acceptance."
}
```

## Separate scientific review assignment

Recorded before dispatch; explicit generic PhysVal profile, read-only.

```json
{
  "id": "LAR-DEFAULT-PhysVal-review",
  "role": "PhysVal",
  "input_revision": "14db490a29d1b8835788e56a0dae99a514a8b7bd",
  "inputs": [
    "tools/calorimeter_baselines/export.py",
    "docs/design/DES-032-allegro-lar-barrel.md",
    "docs/design/DES-033-allegro-lar-endcaps.md",
    "docs/design/inputs/ECAL-baseline-integration-2026-11-04.md",
    "docs/layouts/LAYOUT-002-tracker-3t-lar.md",
    "docs/validation/lar-placement/README.md",
    "docs/validation/lar-placement/results.json",
    "docs/validation/lar-placement-default/README.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess the user-authorized maintained LAYOUT-002 reusable-period default and updated DD4hep description. Identify any scientific scope errors, ungrounded claims, lifecycle/approval overreach, or missing validation needed to adopt the already measured candidate through this export route. Coordinator is generating a fresh maintained export, checking XML equivalence against prior candidate/legacy, running a complete tracker+ECAL 10nm overlap scan and fresh ECAL-only seven-event probe/readback. results.json in the new report is pending and is not input at this revision. Do not review own code as independent evidence; this change authored by coordinator and separate SoftEng. No writes or further delegation.",
  "deliverable": "Return revision-specific findings, source locators, actual checks and limits to coordinator. Coordinator retains result in the new task session.",
  "completion": "Assess the description and validation plan with findings or bounded no-findings conclusion; distinguish existing evidence, prospective checks, and human-only design/response acceptance."
}
```

## Follow-up evidence review assignment

Recorded before dispatch.

```json
{
  "id": "LAR-DEFAULT-PhysVal-evidence",
  "role": "PhysVal",
  "input_revision": "a630e9385821f5359f587c203b34ce4e72ed3d72",
  "inputs": [
    "docs/validation/lar-placement-default/check_export.py",
    "docs/validation/lar-placement-default/README.md",
    "docs/validation/lar-placement-default/results.json",
    "docs/validation/lar-placement/results.json",
    "docs/design/DES-032-allegro-lar-barrel.md",
    "docs/validation/lar-placement/README.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess bound fresh maintained-export XML and smoke evidence and the two prior wording corrections. Input records explicitly leave the full native union scan pending; do not treat it as passed. Inspect local ignored build/lar-default/xml-comparison.json, smoke/timing.json and smoke/smoke-readback.json and raw hashes as needed, with source records distinguishing those from pinned input. Check comparator envelope sibling normalization preserves all physics-relevant bytes. No writes, runtime activation or further delegation. Coordinator will provide full native result separately on completion.",
  "deliverable": "Return revision-specific findings, actual checks and remaining evidence gap to coordinator for session curation.",
  "completion": "Assess XML/material/sensitive/terminal-leaf/saved-hit bindings and scope; identify P2+ gaps or a bounded no-findings result, explicitly retaining pending native-union requirement."
}
```

## Draft publication

Created [draft PR139](https://github.com/asalzburger/nodd/pull/139) stacked on
PR138 branch `codex/lar-geant4-placement`. Its initial body and evidence explicitly
mark the complete native union overlap scan pending. No PR was merged or marked
ready by this task. Largest new committed blob290738bytes at initial publication;
no generated XML/ROOT/event dumps were committed.
