# OpenDataDetector — resource register and first reading route

- Created/accessed: 2026-09-16
- Phase: M0 resource discovery and source inspection
- Related: ADR-001 (baseline), ADR-003 (validation), ADR-005 (reading), all DRAFT
- Source metadata: [catalogue](../manifest.yaml)
- Study checkout evidence: [revision and file hashes](../odd-study-snapshot-2026-09-16.json)
- Reading/check evidence: [intake report](../../docs/validation/odd-resource-intake.md)

## What is available

The core public resources needed to start learning ODD are registered below.
This is a practical starting set, not a claim that every necessary baseline input
has been validated. No detector build, Geant4 run or ACTS conversion was performed.
The source checkout is an ignored study copy, not a selected nODD baseline/import.

### Primary implementation and history

| Source ID | Resource | How to use it / local status |
| --- | --- | --- |
| SRC-ODD-UPSTREAM | [CERN GitLab repository](https://gitlab.cern.ch/acts/OpenDataDetector) | Primary XML, C++ factories, materials, identifiers, config and CI. Clean shallow checkout downloaded to `reference/cache/upstream/OpenDataDetector`. |
| SRC-ODD-ZENODO-V2 | [Archived v2 release](https://zenodo.org/records/6445359) | Stable historical software citation, DOI 10.5281/zenodo.6445359. Archive registered, not downloaded. |
| SRC-ODD-CHEP-2023 | [CHEP 2023 presentation](https://indico.jlab.org/event/459/contributions/11546/) | Downloaded 18-page PDF; useful first overview of motivation, tracker detail, calorimetry and interfaces. |
| SRC-ODD-ACAT-2021 | [ACAT 2021 contribution](https://indico.cern.ch/event/855454/contributions/4596738/) | Historical lead. Direct access returned 403; attachment/title verification remains pending. Optional follow-up, not required to start from source and CHEP slides. |
| SRC-TRACKML-ACCURACY | [TrackML accuracy paper](https://arxiv.org/html/1904.06778) | Web-readable historical context for the predecessor detector/dataset. |
| SRC-TRACKML-THROUGHPUT | [TrackML throughput paper](https://arxiv.org/abs/2105.01160) | Downloaded 16-page PDF after HTML access failed; historical context, not current ODD parameters. |

### Reconstruction, material and simulation interfaces

| Source ID | Resource | How to use it / local status |
| --- | --- | --- |
| SRC-ACTS-REPO | [ACTS repository](https://github.com/acts-project/acts) | Match ACTS source to the chosen ODD baseline. Not cloned/built here. |
| SRC-ACTS-ODD-WALKTHROUGH | [Versioned full-chain walkthrough](https://acts.readthedocs.io/en/v46.8.0/examples/full_chain_odd.html) | HTML introduction to geometry, digitization, seeding and fitting. Its version is not the study checkout's CI version. |
| SRC-ACTS-ODD-TUTORIAL-2025 | [2025 example-chain tutorial](https://indico.cern.ch/event/1501989/contributions/6511364/) | Downloaded 50-page slide deck; environment and simulation/reconstruction walkthrough. |
| SRC-ACTS-MATERIAL-MAPPING | [Material mapping how-to](https://acts-project.github.io/material_mapping_howto.html) | HTML route through Geant4 recording, mapping and validation. Live documentation; version-match before running. |
| SRC-ACTS-PAPER | [ACTS paper](https://arxiv.org/html/2106.13593) | HTML background: §3.6 geometry/material, §4.2 example reconstruction chain. |
| SRC-ODD-CTD-2023 | [CTD GNN + CKF study](https://indico.cern.ch/event/1252748/contributions/5521546/) | Downloaded 23-page deck; application example, not a general detector specification. Actual title: “Studies on combined GNN + CKF tracking”. |
| SRC-DD4HEP-MANUALS | [DD4hep manuals index](https://dd4hep.web.cern.ch/dd4hep/page/users-manual/) | HTML manuals available: [DD4hep](https://dd4hep.web.cern.ch/dd4hep/usermanuals/DD4hepManual/DD4hepManual.html), [DDG4](https://dd4hep.web.cern.ch/dd4hep/usermanuals/DDG4Manual/DDG4Manual.html), [DDRec](https://dd4hep.web.cern.ch/dd4hep/usermanuals/DDRecManual/DDRecManual.html). No PDF download needed. |
| SRC-DD4HEP-REPO | [DD4hep source/releases](https://github.com/AIDASoft/DD4hep) | Factories, compact XML and simulation implementation; select version with environment. |
| SRC-GEANT4-DOCS | [Geant4 documentation](https://geant4.web.cern.ch/docs/) | HTML geometry/material, physics-list and application developer references. |
| SRC-KEY4HEP-DOCS | [Key4hep documentation](https://key4hep.github.io/key4hep-doc/) | Environment entry point; root redirects to main. No local recipe validation yet. |

### Modern dataset and production context

| Source ID | Resource | How to use it / local status |
| --- | --- | --- |
| SRC-COLLIDERML-PAPER | [ColliderML paper, v1](https://arxiv.org/html/2512.15230v1) | Web-readable description of the dataset and production chain; no PDF required. |
| SRC-COLLIDERML-REPO | [ColliderML library](https://github.com/OpenDataDetector/ColliderML) | Public data-access and workflow tooling; not installed. |
| SRC-COLLIDERML-PRODUCTION | [Production repository](https://github.com/OpenDataDetector/ColliderML-Production) | Stage scripts and configurations; registered, not executed. |
| SRC-COLLIDERML-SIMULATION | [Local simulation guide](https://opendatadetector.github.io/ColliderML/guide/simulation) | At access time names ODD v4.0.4; do not silently substitute current upstream. |
| SRC-COLLIDERML-DATA | [CERN dataset card](https://huggingface.co/datasets/CERN/ColliderML-Release-1) | DOI 10.57967/hf/7269, CC-BY-4.0 stated on card. No event dataset downloaded. |

## Inspected source revision and navigation

Study revision: `c167363f3d4ad1540a577af99071283caf54f3a6`, commit date 2026-04-29.
Use [this immutable tree](https://gitlab.cern.ch/acts/OpenDataDetector/-/tree/c167363f3d4ad1540a577af99071283caf54f3a6)
for every relative path below. The local snapshot records hashes of 77 relevant
tracked files. The root LICENSE states MPL-2.0; no upstream implementation is
vendored into the nODD source tree.

These are **FACT** observations about the inspected source files, not approved
nODD design choices or claims that the geometry passed runtime validation.

| Question | Paths in study revision |
| --- | --- |
| What is the complete detector entry point? | `xml/OpenDataDetector.xml` |
| How is it split into stages? | `xml/OpenDataDetectorDefs.xml`, `OpenDataDetectorTracker.xml`, `OpenDataDetectorCalorimeter.xml`, `OpenDataDetectorMuonSystem.xml`; README “Sub-detector layout” |
| Where are global dimensions/materials/IDs? | `xml/OpenDataDetectorEnvelopes.xml`, `OpenDataDetectorElements.xml`, `OpenDataDetectorMaterials.xml`, `OpenDataDetectorIdentifiers.xml` |
| Where are sensitive readout definitions? | Subsystem files under `xml/detectors/`; inspect their readouts with the corresponding factories |
| Where are tracker modules and services built? | `factory/tracker/ODDModuleHelper.cpp`, `ODDModuleHelper.hpp`, `ODDServiceHelper.hpp`, pixel/strip barrel/endcap factories |
| Where are calorimeter and muon assemblies built? | `factory/calorimeter/`, `factory/muons/`; XML `CalorimeterECal.xml`, `CalorimeterHCal.xml`, `MuonSystem.xml` |
| Where are field and solenoid settings? | Full steering XML `<fields>` and field constants; `xml/detectors/Solenoid.xml` |
| Where are reconstruction assumptions/assets? | `config/odd-digi-*.json`, `odd-seeding-config.json`, `odd-material-mapping-config.json`; `data/odd-material-maps.root` and classifier ONNX files |
| Where is the build contract? | `CMakeLists.txt`, `factory/CMakeLists.txt`, `setup.sh.in`, `.gitlab-ci.yml`, `ci/build_acts.sh` |
| Which existing checks should we reuse? | `ci/detector.yml`, `ci/tracking.yml`, `ci/calorimeter.yml`; material recording/plotting and export scripts under `ci/` |

### Version differences that matter

- The inspected source includes muon XML and barrel/endcap factories. The 2023
  conference abstract calls the muon system a possible future extension. These
  describe different source states, not evidence that one description is wrong.
- `.gitlab-ci.yml` names ACTS **v39.2.1** and LCG **107**. `CMakeLists.txt` requires
  DD4hep **1.27 or later**. These are observed upstream settings, not a tested nODD
  compatibility matrix or evidence that any later version works.
- The full steering XML defines a **3 T** nominal inner solenoid field and **0.5 T**
  outer value. The 2025 tutorial uses a **2 T** constant reconstruction field
  (PDF 24). Match geometry, transport and reconstruction fields deliberately;
  neither value is selected for nODD here.
- The material-map ROOT file exists and is hashed, but its suitability for this
  geometry revision was not tested. File presence is not compatibility evidence.
- The README's CMake example contains a repeated `cmake` token within a command.
  Use the actual CMake/CI files when preparing a reproducible build; the README
  command has not been executed or silently corrected upstream.

Observed remote tag targets include v2 `7041ae086dff4ee4a8d5b65f5d9559acc6dbec47`,
v4.0.4 peeled commit `b0992c148305224899a16d21fcd56406408bd393`, and v6.0.2
`d70556f33b1c36abdf101a07ad8cf57eb56fbdf1`. The study checkout is a different
revision. Tags were read with `git ls-remote --tags`; no release was selected.

## PDF reading map and coverage

All locators below are physical one-based PDF pages; slide numbers may differ.
All 107 pages across the four downloaded PDFs were extracted, not all read.

| Source | Priority locations | Reading coverage this pass |
| --- | --- | --- |
| ODD CHEP 2023 | 2–5 history/tracker/detail; 6–7 calorimeter evolution; 8 interfaces; 15–18 component tables | Read selected text on 3–8 and 14; visually inspected 1 and 5. Quantitative tables deferred. |
| CTD 2023 GNN + CKF | 5 detector context; 8 simulation/digitization setup; 19 geometric digitization | Read 5 and 8; visually inspected title 1. Study-specific settings are not universal ODD parameters. |
| ACTS tutorial 2025 | 3–13 setup; 15–24 geometry/config; 31–37 simulation/digitization; 41–48 reconstruction | Read 22, 24 and 31; visually inspected title 1. Version-sensitive commands not executed. |
| TrackML throughput | Title/abstract and detector-generation discussion; use search before detailed reading | Title text checked; cached for later reading. Full scientific review pending. |

No OCR, verified table transcription or digitization implementation was performed.
The three presentation titles were visually verified. Search snippets can mix
figure labels; inspect original pages for geometric claims.

## Suggested next pass

1. Read CHEP PDF 3–8 together with the pinned source README and steering XML.
2. Trace one pixel module from `TrackerPixels.xml` through its factory/helpers,
   recording explicit components and effective material representations.
3. Map the same path for strips, ECal/HCal and muons; distinguish available code
   from validated behavior and compare only simulation-relevant detail.
4. Prepare an ADR-001 baseline candidate with a full SHA, entry point, assets,
   ACTS/DD4hep/Geant4 environment and existing checks. Keep import strategy and
   human approval open until reviewed.
5. Execute the M0 baseline specification only after its prerequisites are resolved.

The remaining gaps are chiefly a coherent version/configuration selection and
runtime characterization. ACAT attachment access is an optional literature gap.
No claim of complete resources for every future detector-design question is made.

## Full-detector realism assessment

The [M0-ODD-REALISM assessment](../../docs/validation/ODD-realism-assessment.md)
now traces subsystem XML, factories, material definitions and response/CI
configuration at the study revision. It distinguishes implemented detail from
HL-LHC applicability and records prioritized gaps with closure evidence. Its
[static inventory](../../docs/validation/odd-realism-evidence.json) is not a
constructed geometry or performance report.
