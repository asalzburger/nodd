# SESSION-2026-09-17-itkpix-baseline — ITkPix chip-family selection

## Scope and evidence

Contemporaneous curated record; starting revision and initial changes captured in
paired JSON. Continues design/rd53-pixel-modules. No unrelated changes discarded.
Exact client identity, conversation start and token counts unavailable. Related:
DES-001, ADR-007, ADR-006, issue #7. M0 remains uncompleted; drafting only.

## Selected conversation

User exact instruction: “Let's take ITkPix then”. This resolves the chip-family
question after discussing RD53A/ITkPix/CROC consequences. Exact ITkPix revision,
physical inventory verification and qualification remain unresolved.

## Decisions and outcomes

Tracking Engineer revised the main design, two independent alternative inputs
and SVG labels. Historical RD53A FACT/INFERENCE claims retain IDs and become
explicitly superseded benchmarks. New ITkPix facts/derivations use new IDs.
Coordinator independently reassesses the larger chip and quad footprint.
ADR-007 records technology direction in DRAFT; user choice is not full design
sign-off. Dashboard TASK-C-PIX and document register include the selected family.

Public source SRC-RD53-OVERVIEW-2023 slide5/PDF5 verified visually after temporary
download/rasterization: matrix400x384 and50micrometre chip pitch; approximate die
20x21mm and generation identities. These values do not freeze mechanical,
power, pads or qualification. Nominal areas are readout arithmetic, not seamless
sensitive efficiency. Public overview requirements not adopted as operating limits.

## Commands and validation

- Read repository instructions, PROJECT, DES-001, ADR-006, validation catalogue
  and issue #7; working tree inspection.
- `gh issue view7 --json title,body`: sandbox network failure, escalated retry
  succeeded. No external issue modification.
- Public overview web fetch succeeded; screenshot failed. Public PDF downloaded
  temporarily with curl, page5 rasterized with pdftoppm and inspected visually.
  No PDF committed; no retained local checksum invented.
- Actual final checks are recorded in paired JSON below; no geometry, hardware,
  thermal, irradiation or performance validation claimed.

## Changes and revision links

Paired JSON inventories design/input/drawing updates, ADR/register/index,
source catalogue, project tracking and this session pair. Git history locates the
result revision; result SHA recorded only once it exists.

## Follow-up

Confirm exact ITkPix revision/drawing/thinning and load model. Define host volume,
radiation/rate/lifetime, sensor mapping and shared services. Quantify full material,
thermal and useful-coverage comparisons; assign human reviewers and obtain exact
revision sign-off before production integration.

Final checks: dashboard25tests and logging15tests passed; dashboard validates
11tasks/9documents/3existingrounds and builds successfully; five design/ADR
local-link audits, bothSVGXMLparses and git diff --check pass. Session validator
passes all30records. Coordinator retains A1firstqualification and reopens A2
versusB coverage selection; no demonstrated installed-material winner.

## Resource synchronization — 2026-10-07

The authorized cleanup imported 3 exact completed turn(s), after dry-run validation, into this canonical owner. Earlier narrative and original inventory sources remain intact; pending/unknown token statements above are historical and superseded for these observations only.

| Client turn | Input | Cached input | Output | Reasoning output | Total | Requests |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 01a0afe5-220a-7af0-9b65-999d7dccfdc6 | 1741636 | 1650560 | 6304 | 410 | 1747940 | 18 |
| 01a0afe5-5302-71e1-8a45-b73bce3e7f0d | 395586 | 384640 | 2879 | 109 | 398465 | 6 |
| 01a0afe6-5c35-7db1-a54a-b2e4ef371c42 | 309998 | 297344 | 2067 | 0 | 312065 | 6 |

Persisted turn/usage ordinals, request counts, timestamps, verified usage-event hashes and original recovery sources are retained in [the synchronization inventory](../usage/USAGE-2026-10-07-synchronization.json). Each turn is counted once; cached input and reasoning output are subsets. No scientific input, execution hash or approval state changed. The current cleanup turn, explicitly excluded illustration/history turn and unassigned historical/internal review turns are excluded; this is partial project coverage, not billing.
