# SESSION-2026-09-16-odd-realism — Full-detector ODD realism assessment

## Scope and evidence

Contemporaneous curated record, 2026-09-16. Starting branch `main`, commit
`2f1cd77357568412780f53fef387693e23326330`. Prior resource-intake and PROJECT
scope changes were preserved; the paired JSON records their initial inventory.
Exact token counts, client version and conversation start are unavailable.

## Selected conversation

User (exact quote): “In that sense, make an assessment of the OpenDataDetector - how realistic is it (and thus how usefuel as a HL-LHC reference), identify gaps, be critical, document this clearly”

Assistant outcome (summary): produced a critical, full-detector source assessment
with subsystem evidence, bounded applicability judgments and ten prioritized gaps.
Distinguished existing geometry, response configurations, external production and
runtime validation. Replaced the broad PROJECT motivation claim with a link to
this evidence and a more precise summary.

## Decisions and outcomes

- ODD is useful for algorithm/simulation development but quantitative HL-LHC
  applicability must be established per observable and exact configuration.
- Credit explicit tracker supports/services, stereo structure, calorimeter
  sampling, muon gas/walls, and existing CI; avoid claiming these are absent.
- Highlight missing pixel-chip representation, divergent XML/ACTS readout
  contracts, timing absence, material-accounting questions, effective solenoid
  and missing physical closure of magnet/services/response.
- Derive the repeated HCal PCB-mixture normal-path thickness and areal mass as
  an accounting question, not a proven typo or measured material defect.
- Include versioned ColliderML evidence to avoid wrongly claiming that ODD
  cannot support high-pile-up production or digitization. Its chain is separate
  from this source checkout and this pass did not execute it.
- No detector configuration changed; no design, ADR or issue approval advanced.
  M0-ODD-REALISM remains DRAFT. No commit, PR or issue was created.

## Commands and validation

Inspected AGENTS, PROJECT, ADR-001/003, M0-BASELINE, prior reading guides and
upstream XML, factories, materials, digitization and CI. One initial ADR filename
lookup was incorrect; read the actual ADR-003-validation-and-artifact-policy.md.
Public GitLab web rendering returned 403; the existing clean local checkout was
available. The versioned ColliderML HTML paper was accessible and read in relevant
sections. No download or environment installation was needed.

- Verified upstream HEAD and clean working tree.
- Python SHA-256 assertions checked all 77 snapshot files.
- ElementTree parsed 20 XML files. Attribute inspection produced six subsystem
  inventories; JSON arithmetic extracted nine ACTS digitization entries. Evidence
  records formulas and interpretation limits for reproduction from the pinned source.
- Logging/documentation suite: 15 tests passed.
- `git diff --check`: passed.
- Final session-schema validation result is recorded in the paired JSON.

No build, overlaps, material scan, field sampling, Geant4 or ACTS execution was
performed. Static checks are not detector acceptance or accuracy validation.

## Changes and provenance

See the paired JSON file inventory. Added M0-ODD-REALISM Markdown and static JSON
evidence, linked it from PROJECT and the ODD guide, and added supported observations
to SRC-ODD-UPSTREAM and SRC-COLLIDERML-PAPER in the source manifest. No new
scientific source or selected nODD parameter was introduced.

## Follow-up

Human/domain review of the assessment is pending. Select the baseline/environment,
then measure full-detector material, fields, coverage and readout consistency.
Use ODD-G01–G10 closure artifacts to guide subsequent design and validation.
Quantitative TDR/production comparisons, tolerances and technology choices remain
open. No review or sign-off was manufactured.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **1,149,393 input** and **11,880 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
