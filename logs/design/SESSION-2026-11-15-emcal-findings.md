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

## User steering before report authoring

Literal: "Handle the routing prototype with reduced gap as merged." Report will treat routing plus400mm warmgap as the merged/adopted working configuration by explicit user direction, while separating this editorial baseline from formal engineering/signoff/physics qualification. No GitHub merge/readiness mutation requested or performed. Earlier live public draft-state snapshot stays historical audit evidence, not adoption-pending prose in the PDF. Both specialists informed before final memos. Source-era800mm remains the comparison reference; underlying measurements and unresolved integrated-service/forward/readout qualification remain accurate.

## Authored review and preliminary QA

Source ac399749 builds exactly8pages; current PDF SHA256 4bde70621975ad5cad70b7779fd04732655bfcfda0ec6cd26b3856cd7fcae77b,72042bytes. ReportLab4.4.9/pypdf6.21.4 in existing bundled Python3.12 and Poppler26.05.0, no installation. PDF skill operation marker succeeded exactly once before authoring. First routing-schematic layout put lower axis labels into caption; root corrected Flowable extent and panel separation, then rendered again. Both statistical figures were redrawn as readable vectors directly from retained bin values/CI endpoints; no fits/bootstrap or simulations rerun. Eight-page overflow/footer checks PASS. Final visual/claim assessment still follows.

Initial inventory refresh rejected docs/publication/emcal-findings as an unknown automatic code family. Kept external INF-REPORTLAB paths empty (as its historical convention), recorded document builder/dependencies/version via evidence/recipe instead. No discovery gate bypass or fingerprint-only execution claim. The failed refresh was not reported as passing; subsequent corrected refresh is required.

## Final exact-document review contracts before dispatch

Explicit generic PubDoc/PhysVal, report root-authored; no native role loading.

```json
[
  {
    "id": "EMCAL-REPORT-PubDoc-final",
    "role": "PubDoc",
    "input_revision": "38bc3b6b36dc4bad30a2a368ae92f5c5e73e8c3f",
    "inputs": [
      "docs/publication/emcal-findings/review.pdf",
      "docs/publication/emcal-findings/build_report.py",
      "docs/publication/emcal-findings/evidence.json",
      "docs/publication/emcal-findings/README.md"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess all8pages exact PDF/source for concise user-requested ODD->realisticSiW->ALLEGRO-styleLAr findings/recommendations. Check source/claim/cohort/version correspondence using prior evidence memo and source manifest; references, phase/status and recommendations. User explicitly says treat routing+400mmgap as merged/adopted: no adoption-pending wording, but no fabricated integrated-fit/engineering qualification. Historical chronology is requested, so this is not a baseline-only TDR. Verify exactpagecount<=10 and readable report prose; root owns visualQA and rendering. Identify actionable factual or publication issues, not broadrestyling. Use installed bundledpypdf ifextractPDF: /Users/salzburg/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3. No edits/runtime/delegation.",
    "deliverable": "Exact reviewedrevision/PDFhash, findings/severity or noactionablefindings, actualclaim/source/observable checks and limitations; no humanapproval.",
    "completion": "Bounded final report assessment sufficient for finalPDF delivery/draftPR; no newdesign/runtime work or unrelatedreviews."
  },
  {
    "id": "EMCAL-REPORT-PhysVal-final",
    "role": "PhysVal",
    "input_revision": "38bc3b6b36dc4bad30a2a368ae92f5c5e73e8c3f",
    "inputs": [
      "docs/publication/emcal-findings/review.pdf",
      "docs/publication/emcal-findings/build_report.py",
      "docs/publication/emcal-findings/evidence.json",
      "docs/publication/emcal-findings/README.md"
    ],
    "mode": "read-only",
    "writable_paths": [],
    "task": "Assess exact8page PDF/source scientific claims against pinned sources and prior independent numerical memo. Verify fixed20GeV/c ODD/nODD independentcohort, matched10k H/E four-row own-globaltail/CI definitions, separate100ktrain+20kcalibration, LArcompleteA/E fixed999/commoncut/pairedCIs/U precision, preserved materialvsserviceengineering and relevantrecommendations. Vectorchartfunctions drawretainedvalues/CIendpoints with correctdegreefolding, preserveallbins/noinference. User explicitly directs routing+400mmgap treatedmerged/adopted workingcase; accept thiseditorialbaseline while retaining actualECAL-only/noexternalpipeoverlay scope and knownfitissue. No newMC/native/ROOT/bootstraps or edits/delegation; this is docclaimreview notrerunscientificcampaign. Use bundledpypdf ifneeded. RootvisualQA owns allrenderedpages. Return only actionable corrections or nofindings plusactualchecks/limitations.",
    "deliverable": "Exact reviewedrevision/PDFhash, findings/severity or noactionablefindings, actualclaim/source/observable checks and limitations; no humanapproval.",
    "completion": "Bounded final report assessment sufficient for finalPDF delivery/draftPR; no newdesign/runtime work or unrelatedreviews."
  }
]
```

## Final independent findings and visual closeout

PubDoc and PhysVal exact38bc3b6b36dc4bad30a2a368ae92f5c5e73e8c3f reviews found no actionable findings in eight-page PDF4bde7062.... Both extracted allpages and verified20inputhashes/builder/provenance. PubDoc checked10pinnedlinks/cohort/status/claimcorrespondence; PhysVal checked numerical tables, H/A/U and tail definitions, independent20k calibration, native vector-chart coordinates/CI endpoints/radian-degree folding and relevant underlying primary inputs. PhysVal also visually checked pages4-6; no native/ROOT/bootstrap/refits or source edits. Root inspected all8latestPNG pages/montages, then shortened only page7 priority labels to eliminate mid-word wraps.

Cosmetic source6804f5e30e0218a9ff61904b4d29bca900cf1c8b changes labels only:4Comparable reconstruction→4Response;5Hadron-collider relevance→5Collider. Delivered PDF SHA0d53bb50b7b8be68f84612a385e0ac12d791f8b92d0c472c05473e21cd108d6b,72041bytes; exact other7pagecontentstreams byte-identical to reviewed version. review-delta.json records scoped review identity; root visually rechecked finalpage7 and no scientific claims/data/charts changed.

Automatic final artifact checks:8pages<=10, expected footer numbers,10immutable reference links, character page bounds/glyphs and delivered/curated PDF hash equality; no layout overflow. Project validator initially rejected the newtask role/workstream mismatch; corrected this documentation task to existing WS-PUB /Publication-documentation office rather than weakening validation. No engineering/design signoff advance.
