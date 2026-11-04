# SESSION-2026-10-15-hcal-realism — ODD HCAL technology, realism gaps and prototype plan

## Scope and evidence

Contemporaneous curated investigation, 2026-10-15. Started from nODD main
`5b4e5d9e563505aea17e9b792458708c3175ec4a` in a new isolated worktree,
branch `codex/hcal-realism-assessment`; initial working tree clean. Existing
worktrees were inspected and unrelated modifications preserved. The exact
conversation start time and completed per-turn token counters were unavailable.

The authoritative current candidate is LAYOUT001 SiW. The initial SysArch
assignment mentioned both candidates; dispatch immediately clarified that the
LAr alternative is historical. Its examined revision was
`72d37ee9a56182e4ba974791a848a738c19cf092`. The coordinator inspected open
DES030/031 source revisions `654b85a48abeb38735ad7fe0866c5d1082882df7` and
`2776266570dda13386a16863e5b0e97432f27217`. GitHub confirmed PR70/71 still open
and PR69 merged; no PR status was inferred from stale tracking entries.

## Selected conversation

User request, exact quote:

> Investigate in detail the current HCAL of the ODD:
> - check appropriateness of technology for a hadron collider
> - check technology realism and gap of those regarding the current modeling
> - propose a plan to get it closer to realism and actual feasibility following the examples of the ECAL prototypes

Assistant outcome, paraphrase: investigated current public ODD files, existing
nODD physical prototypes and current selected outline separately; prepared
DES035 with hardware/operating/response gaps, source classifications and six
bounded work packages. Retained the existing steel/scintillator preference.
No implementation, technology switch, publication or human sign-off was requested
or performed.

## Decisions and outcomes

- DES035 distinguishes experimental technology evidence from nODD feasibility.
- The unsupported effective electronics allocation also affects absorber depth;
  replacement requires fresh material/containment comparisons.
- A continuous readout architecture, regional lifetime requirements, connected
  services and repaired carrier coverage precede a detailed complete HCAL.
- ECAL methods transfer through compact boards, shared services, manufactured
  boundary components and explicit seam/coverage controls.
- Detailed native and muon evidence is historical and configuration-specific;
  shower, pileup, radiation, thermal, structural and reconstructed-performance
  qualification remain future work.

## Curated specialist handoffs

Explicit profiles were supplied through prepared full prompts; native profile
loading is not claimed. All contributions were read-only against the pinned
nODD input revision; no specialist changed files or ran native simulation.

| Assignment / client task identifier | Contribution and reconciliation | Actual checks |
| --- | --- | --- |
| HCAL-20261015-CaloTech / /root/calotech | Supported baseline technology, identified acquisition/thermal/radiation/BOM gaps, supplied public source metadata. Component qualification and shared readout remain open. Findings incorporated in DES035. | Exact-revision source inspection, primary HTML/PDF reading, standard-library arithmetic. |
| HCAL-20261015-SysArch / /root/sysarch | Distinguished detailed hardware from enlarged outline, identified missing combined HCAL service budget and forward-depth/interface gaps. Independent outline arithmetic reconciled by coordinator. | Source/revision checks; service allocation replay and ten controls PASS; straight-ray outline arithmetic. |
| HCAL-20261015-PhysVal / /root/physval | Assessed baseline scientific claims separately from authors; supplied observables, controls and extrapolation limits. Did not review the final coordinator-authored report. | Exact-revision report/source inspection, primary reading and elemental screening arithmetic. |

Public literature facts used in the deliverable are retained by source ID and
precise locator in DES035/reference manifest. Broader unused research was not
copied into this journal. Agreement of agents grants no human acceptance.

## Commands and validation

- `git fetch origin`, source/status/worktree inspection, then ordinary
  `git worktree add -b codex/hcal-realism-assessment ... origin/main`.
- `tools/agent_workflow/workflow.py prepare` validated three contracts before
  dispatch; prompt files under /private/tmp are temporary.
- `gh api` inspected canonical ODD main/release metadata and retrieved five
  public source files. A sandboxed Python subprocess retrieval failed network
  access; the same command succeeded after explicit command approval. All five
  source SHA256 values equal the retained DES027 hashes. No upstream source or
  reference PDF is copied into Git.
- Standard-library parsing and arithmetic produced
  `docs/validation/DES-035/baseline-evidence.json`; formulas and operands are
  retained there. Values include the effective-material column, historical
  ledger totals and forward-outline ray arithmetic. They are not runtime or
  containment validation.
- Four calorimeter-audit controls PASS; fourteen cassette/assembly controls PASS;
  ten service-envelope controls PASS and service allocation replay PASS.
- Project record validation PASS (66 tasks, 37 documents, 21 review rounds).
- Session/schema (183 records), source/link/number consistency, whitespace and
  token-site validation/build all PASS; details are in the paired JSON.
- No new DD4hep/Geant4 run, dependency setup, optical simulation, hadron shower,
  irradiation, engineering calculation or jets/MET reconstruction was executed.

## Changes and revision links

See paired JSON changed-file inventory: DES035, its evidence JSON, source
catalogue, documentation index, scientific tracking and this session pair.
No result commit or pull request has been created; deliverables are local files
in the isolated worktree. No existing geometry/evidence/approval state changed.

## Token accounting

No exact completed per-turn client counters were exposed, for parent or children.
`usage` remains empty; unknown is not zero. Closeout summary: 210 disjoint recorded turns supply observed input 620,754,236
and output 3,545,169 tokens (total 624,299,405). Of 183 sessions, 65 have no
usage, including this task. These are incomplete cumulative project observations,
not the token cost of this task. No estimates or private client-store collection
were performed.

## Follow-up

Review H0/H1 scope and appoint technology/electronics, physics-response and
system-interface human owners. Numerical requirements, operating details,
regional radiation exposure, module/carrier design and future engineering
qualification remain open. The requested investigation is complete; no sign-off
is inferred from its delivery.

## Bounded specialist assignments

Explicit role mandates passed through prepared prompt files; native profile loading is not claimed. Workflow instructions at 5b4e5d9e563505aea17e9b792458708c3175ec4a. All assignments are read-only with no owned write paths.

```json
{
  "id": "HCAL-20261015-CaloTech",
  "role": "CaloTech",
  "input_revision": "5b4e5d9e563505aea17e9b792458708c3175ec4a",
  "inputs": [
    "docs/design/DES-027-calorimeter-description-assessment.md",
    "docs/design/DES-028-calorimeter-cassettes.md",
    "docs/design/DES-029-calorimeter-assemblies.md",
    "docs/layouts/README.md",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Investigate whether the ODD steel-scintillator HCAL technology and the existing nODD DES028/DES029 HCAL prototypes are appropriate for a continuously running hadron collider. Inspect actual primary public sources (CALICE AHCAL, ATLAS Tile, CMS HCAL/HGCAL); distinguish demonstrated hardware from extrapolation. Identify exact stack/BOM/electronics/radiation/thermal/segmentation realism gaps and propose a bounded component-to-cassette prototype path learning from existing ECAL prototypes. Do not assume a collider luminosity or qualification. Return evidence URLs and exact section/page locators, with FACT/INFERENCE/proposed NODD DESIGN CHOICE labels. Read-only; no dependency setup or simulation needed.",
  "deliverable": "Return a cited technical contribution to the coordinator for the HCAL assessment and curated session record.",
  "completion": "Report findings, exact examined source revisions, primary-source locators, actual checks and unresolved questions; no sign-off, no further delegation, no file edits."
}
```

```json
{
  "id": "HCAL-20261015-SysArch",
  "role": "SysArch",
  "input_revision": "5b4e5d9e563505aea17e9b792458708c3175ec4a",
  "inputs": [
    "docs/design/DES-027-calorimeter-description-assessment.md",
    "docs/design/DES-028-calorimeter-cassettes.md",
    "docs/design/DES-029-calorimeter-assemblies.md",
    "docs/layouts/README.md",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess current HCAL physical interfaces and feasibility in both SiW LAYOUT001 and LAr LAYOUT002 using pinned repository evidence. Inspect source quantities, boundary conventions, current HCAL prototype applicability, containment/depth/coverage, steel field-force/support issues, cooling/services and assembly access. Identify which interfaces are still placeholders or absent and propose review gates for barrel, endcap, forward regions. Use actual source locators. Do not select new numerical detector requirements. Read-only; no runtime setup needed.",
  "deliverable": "Return a cited technical contribution to the coordinator for the HCAL assessment and curated session record.",
  "completion": "Report findings, exact examined source revisions, primary-source locators, actual checks and unresolved questions; no sign-off, no further delegation, no file edits."
}
```

```json
{
  "id": "HCAL-20261015-PhysVal",
  "role": "PhysVal",
  "input_revision": "5b4e5d9e563505aea17e9b792458708c3175ec4a",
  "inputs": [
    "docs/design/DES-027-calorimeter-description-assessment.md",
    "docs/design/DES-028-calorimeter-cassettes.md",
    "docs/design/DES-029-calorimeter-assemblies.md",
    "docs/layouts/README.md",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess what can and cannot be concluded about current ODD HCAL hadron-collider suitability from pinned geometry and existing nODD prototype evidence. Develop requirements-to-observables and validation matrix covering containment/tails, noncompensation, pileup and timing, dose/fluence and aging, SiPM saturation/noise, calibration, cracks, jets/MET and reconstruction. Read actual primary sources as needed; record precise citations. Identify invalid extrapolations from CALICE/e+e- hardware to continuous pp and what tests discriminate options. Do not review a proposed report not yet provided, and do not claim runtime/performance validation. Read-only.",
  "deliverable": "Return a cited technical contribution to the coordinator for the HCAL assessment and curated session record.",
  "completion": "Report findings, exact examined source revisions, primary-source locators, actual checks and unresolved questions; no sign-off, no further delegation, no file edits."
}
```
