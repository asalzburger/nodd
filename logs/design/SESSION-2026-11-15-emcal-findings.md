# EM calorimeter findings report

User request (2026-11-15): summarize ODD ECAL, realistic nODD Si-W, its shortcomings, ALLEGRO-style LAr and updated service routing/performance of all three; concise PDF <=10pages including results and recommendations. User spelling ALLIGRO refers to ALLEGRO-style LAr candidate.

New dedicated worktree/branch codex/emcal-findings-report from79a967aa3fe78a525f15ede780c26be0cd73aeae, stacked on current draftPR144. Main worktree has unrelated edits and is untouched. Documentation-only synthesis; no new simulation/geometry or design approval. PDF skill plus repository coordinate/design-evidence/review-validation procedures apply. Exact sources/versions and incomparable cohorts remain explicit.

GitHub verified currenttask: PR137 and140 merged;142/143/144 remain open drafts. PR136 merged but historical calibration/staggering reports retained at3eb path, absent current79a working tree; cite immutable revision rather than silently substituting latest files.

## Specialist contracts before dispatch

Explicit generic role fallback, not native profile loading. All read-only.

```json
[
  {
    "id": "EMCAL-REPORT-PubDoc-evidence",
    "role": "PubDoc",
    "input_revision": "3ebafd340b0e084c5e42e57123de115e3f489244",
    "inputs": [
      "docs/validation/ODD-realism-assessment.md",
      "docs/validation/issue117/nodd-digitization-results.md",
      "docs/validation/ecal-staggering/README.md",
      "docs/validation/ecal10k-untiled/README.md",
      "docs/design/DES-030-ecal-edge-sensors.md",
      "docs/design/DES-031-siw-barrel-prototype.md"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "task": "Build a concise claim/source contribution for user-requested <=10page PDF historical EM calorimeter findings: original ODD ECAL, realistic nODD SiW mechanics/material/readout, observed shortcomings, continuous-silicon diagnostic versus physical staggering and held-out calibration. This is a historical review, not current-baseline TDR; user explicitly requests chronology. Inspect exact pinned Git sources; report evidence-backed ODD dimensions/layer/material/segmentation approximations and comparable ODD/nODD fixed-direction raw performance numbers from source tables, not merged PR descriptions alone. Historical3eb contains ecal-staggering/untiled documents absent from current79a tree; use git show3eb:path explicitly. Need5-10 main facts/numbers with exact file/section and relevant JSON sources, caveats, concise physical explanation of aligned board gaps/full-depth seams/service bays, and defensible recommendations. Current study/report base79a includes newer LAr/gap data handled by parent/PhysVal. No writing/native/MC/delegation; no human approval or newdesignchoice.",
    "deliverable": "Concise evidence memo with source-revision locators, exact numerical comparators/settings and what cannot be compared. Identify publication traps/remaining gaps. No report authoring yet.",
    "completion": "Bounded source synthesis sufficient for8-9page review; do not inspect unrelated full logs/raw ROOT or rerun studies."
  },
  {
    "id": "EMCAL-REPORT-PhysVal-evidence",
    "role": "PhysVal",
    "input_revision": "79a967aa3fe78a525f15ede780c26be0cd73aeae",
    "inputs": [
      "docs/validation/lar10k/README.md",
      "docs/validation/lar10k/summary.json",
      "docs/validation/lar-gap10k/README.md",
      "docs/validation/lar-gap10k/summary.json",
      "docs/validation/issue117/nodd-digitization-results.md",
      "docs/validation/ecal10k/README.md"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "task": "Prepare independent comparison/claim constraints for concise <=10page PDF ODD -> realistic nODD SiW -> ALLEGRO-style LAr, including revised services and conditional400mm gap. Read pinned79a actual compact stats/reports. Supplemental immutable source3ebafd340b0e084c5e42e57123de115e3f489244: docs/validation/ecal-staggering/README.md, results/summary.json; docs/validation/ecal10k-untiled/README.md. These historical reports are absent currenttree; use exact gitshow. Extract defensible 3-technology comparison: ODD vs nODD zero-field fixed-energy/direction raw/PN study as separate cohort; exact10k SiW original/staggered/LAr800 and conditionalLAr400, fixed999transition, zeros, tails/thresholds, CIs. Explain no matched10k ODD run and no intrinsic-resolution/electronics/engineering comparison. Need concise quantitative table(s) and recommended caveats. Preserve H saved vs A complete distinction and tinyU issue. No newMC/native/ROOT/edits/delegation; no claim of redoing prior validation. Return exactsource/JSONkeys and settings, enough for report evidence QA.",
    "deliverable": "Independent numerical/comparability memo with exactsource locators and publication pitfalls; identify any needed corrections before report drafting.",
    "completion": "Bounded comparison only. Final exact draft report review will be a separate assignment after root writes it."
  }
]
```
