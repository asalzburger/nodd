# SESSION-2026-10-20-pr90-endcap-wheels — Review decision

## Scope and evidence

Start5674a7688319d6dd5179c04cd381cb59f48d36bb, codex/muon-chamber-layout, clean worktree. User asks to address the agreed last PR90 comment6283618592 (2026-10-20): move outermost and innermost endcap wheels outside endcap toroids, adapt longitudinal length, no overlaps; produce newOBJ, full/endcap coverage, before/after endcap shape lists+2Dblue inventory and current barrel inventory. Governing DES040 remains DRAFT isolated PROTOTYPE, no human engineering acceptance. Preserve all original source/data/field/OBJ evidence and ACTS source edits.

## Initial method

Use repository coordinate/design-evidence/review-validation workflows. Before implementing, audit HCAL/coil/frame clearances and specify a bounded geometry/method amendment. Resolve physical ambiguities without silently changing magnets or source requirements. Three independent read-only specialist assignments follow, recorded before dispatch. Explicit prepared fallback mandates, not claimed native profile loading.

## Assignment W-A1

```json
{
  "id": "W-A1",
  "role": "SysArch",
  "input_revision": "5674a7688319d6dd5179c04cd381cb59f48d36bb",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Physical feasibility/interface audit of the latest agreed PR90 decision6283618592. Inner and outer endcap stations should lie longitudinally outside endcap toroids and become non-overlapping full wheels of trapezoids; adapt longitudinal length accordingly. Determine precise feasible z/r placements with unchanged HCAL, barrel/endcap coils and frame; compute full-envelope/clearance bounds, not just midplanes. Critical potential issue: ECTwarmfront6.55m versus HCALendcapback6.4412m cannot fit0.5m depth plus clearances. Identify whether a full radial wheel at rmin0.7 can exist with fixed magnets, and what exact minimal magnet or HCAL interface change would be required if impossible. Do not change magnets/fields or retune dimensions; return quantified options and ambiguity requiring human direction. Assess outerwheel beyondECT/BT and supportcarrier conflicts, barrel-length adaptation, field/world domain consequences. Read-only calculations/scratch only. No external messages, source/dependency modifications or nested agents.",
  "deliverable": "Quantified source-located physical interface/feasibility report in /private/tmp/pr90-wheels-A1-* with actual checks and viable bounded alternatives.",
  "completion": "Exact-revision interface assessment with no hidden clashes or implied approval."
}
```

## Assignment W-M1

```json
{
  "id": "W-M1",
  "role": "MuonTech",
  "input_revision": "5674a7688319d6dd5179c04cd381cb59f48d36bb",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Muon station/wheel concept for agreed PR90 comment6283618592. Independently inspect current panel inventory/packing and propose simple one-trapezoid-per-sector full inner/outer endcap wheels outside ECT, no overlaps, realistic fixed-clearance gap; preserve middle station unless justified. Investigate24vs12sectors, angular phase relativeBTlegs, radialextent/bore constraints and barrel longitudinal shortening needed. Do not silently change magnets, HCAL or chamber depth. SysArch independently audits global feasibility; if front wheel impossible fixed-coils+HCAL sayso. Suggest before/after shape inventory descriptors and 2D blue figures, current barrel inventory, combined/separate OBJ groupings. Read-only calculations/scratch only, no repo/dependency edits/nestedagents/externalmessages.",
  "deliverable": "Source-located chamber concept/inventory and bounded choices, exact quantitative constraints, in /private/tmp/pr90-wheels-M1-*.",
  "completion": "Actionable unclipped-trapezoid concept and explicit feasibility/coverage tradeoffs; no human acceptance."
}
```

## Assignment W-P1

```json
{
  "id": "W-P1",
  "role": "PhysVal",
  "input_revision": "5674a7688319d6dd5179c04cd381cb59f48d36bb",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/acts/config.json",
    "tools/muon_layout/acts/propagate.cpp",
    "tools/muon_layout/acts/analyze.py",
    "docs/validation/DES-040/acts-propagation/summary.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Read-only benchmark/protocol proposal for PR90 agreed decision6283618592. Need new full/endcap coverage estimate after moving inner/outer endcap wheels outside ECT, no overlap and sector gaps explicit, before/after inventories +OBJ. Inspect old native ACTS benchmark masks/status/denominators and newdomainneeds; propose paired before/after native sampling with identical localp/charges/seeds/entrance and field, separate full4pi and exact endcapregion definitions not cherry-picked to improve. Distinguish geometric gap losses vs strict field-mask uncertainty vs transport. New positions may require extended field/world domains; assess whether unchanged 12.5mmap cansupportouterwheel and how to preserve original evidence if expanded. Consider full-wheel no radialtiling inventory+barrel length changes. Do not author implementation; future frozen-result review separate. No repo/dependency writes/nestedagents/externalmessages; scratch only.",
  "deliverable": "Concrete observables/controls/denominator plan with source locators in /private/tmp/pr90-wheels-P1-*, explicit limitations/choices.",
  "completion": "Meaningful unbiased comparable coverage plan, no invented scattering/efficiency or human signoff."
}
```

## Token accounting

Exact root/child per-turn counters unavailable; usage unknown, not zero. No estimates, overlapping totals or private client state retained.

## Clarification pending; independent work continues

Root and SysArch independently derive HCALback6.4412m, ECTwarmfront6.55m, gross0.1088m; with existing0.05m coil clearance and a provisionally equal HCAL margin,0.0088m is available for0.500mdepth (0.4912m deficit). The HCAL margin is an open interface assumption; even zero margins cannot fit the chamber. User was asked asynchronously whether to adjust endcap-toroid axial extent/recalculate field or retain magnets and reduce the inner wheel radial reach around HCAL. No dependent magnet/HCAL/wheel geometry is changed pending that design choice. Baseline chamber inventories, shape-view tooling and domain/coverage planning proceed independently. PhysVal also identifies that the old entrance cap6.50m would launch beyond a before-ECT innerwheel, requiring common upstream seeds for both compared layouts; outerwheel exhausts currentmap/worlddomain. These are not detector inefficiencies.

## Prepared evidence and observed checks

W-A1/W-M1/W-P1 completed exact-revision read-only assessments; no candidate geometry implementation or engineering approval. Root retained curated reports and portable A1/P1 checks, distinguishing provisional HCAL margin and ECT-only versus full-frame rear bounds. A1 source roots/output became CLI arguments; HCAL back is read from the pinned magnetic input. Raw scratch filename/hash metadata in the P1 JSON remains explicitly historical. No private comment cache or signed image URL was retained.

Baseline inventory generation first failed with missing Matplotlib in both the default and bundled Python (exit1). acts-spack preflight exits2 because setup/lock fingerprints changed; this warning was given before dependent work. Fresh setup_spack verified the active environment and installed DD4hep1.38/Geant4 11.4.3, and the existing acts-nodd pyvenv imports NumPy2.5.4/Matplotlib3.11.2 (exit0). No shared dependency/source modifications. Inventory generation then passed using that Python and task-owned font/cache directories. Both sheets visually checked; title and barrel footer spacing corrected and generation repeated.

Current output is816barrel/6families and744endcap/18families. The independent footprint reconstruction covers all1560panels with maximum0.4973nm error within1nm grouping tolerance, plus CSV/quantity/station/hemisphere checks (exit0). Root reproduced the P1 pinned baseline output exactly and ran the unchanged portable ACTS evidence checker:148960tracks and native control/artifact hashes pass; no native rerun. The A1 interface check passed against pinned inputs and484support envelopes.

TASK-B-MUON-WHEELS remains blocked on the physical choice; the session stays open. NewOBJ, after-layout inventory, paired newcoverage, magnetic redesign/sizing and field generation are NOT RUN. These are not represented by the baseline-only artifacts. Existing baseline chamber/magnet/field/OBJ/native evidence remains unchanged.

## Prepared publication checks

Project validation passes69tasks/38documents/21reviewrounds; journal validation passes193records. M1summary reports80sessions/35withusage; currenttaskusage remains unavailable. Local token-site preview passes with210historical disjoint turns/624299405observed tokens, not current-task usage. Retained baseline/P1 reproduction and portable A1 outputs match their independent originals exactly (root set-e command exit0). Preparation manifest pins source and newartifact hashes; narrow text scan found no signed/private-image/token markers. Latest discussion rechecked through GitHub connector: agreed comment6283618592 remains last; PR90 still open, same5674head. Raw discussion payload was not retained in Git.

Staged whitespace check found default CSV CRLF line endings in new files. Generator now emits LF; inventories regenerated without numerical changes and footprint check repeated successfully. Original unstaged whitespace check had not covered untracked files.

Completed28project/documentation and33journal tests: all61pass. Expected unavailable-history negative fixture emits a git error before passing; it is not an unresolved remote failure. Final staged whitespace check passes after LF correction.

## Publication and still-pending work

Preparation commit6089993659d58ae46aa5fb7cb700e231535410f2 pushed and PRhead verified. GitHub connector comment write returned403integration-permission error; existing authorized GitHub CLI session posted the prepared partial-status reply athttps://github.com/asalzburger/nodd/pull/90#issuecomment-6283825776 (exit0). No automatic approval rejection occurred. The reply links the blue inventories and physical alternatives, expressly leaving candidate geometry/newOBJ/aftercoverage pending. Follow-up record-only commit retains this publication evidence. Session remains open and task blocked on the same physical choice. No design approval or task completion claimed.
