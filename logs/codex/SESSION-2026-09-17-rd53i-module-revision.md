# SESSION-2026-09-17-rd53i-module-revision — Module-only Astra rewrite

## Scope and selected conversation

Contemporaneous curated record. User instruction (paraphrase): define RD53i as
the selected chip once and use RD53i consistently; focus on the module itself,
exclude mounting/cooling infrastructure; make component thickness/material/X0
tables and cross-section drawings; redo both proposals with Astra rather than Sol.
Starting branch/revision and clean initial tree are in paired JSON. Exact client
identity, conversation start time and token counts are unavailable.

## Decisions and outcomes

Commissioned two independent gpt-6-astra alternative agents with explicit model
override as requested. Both initially failed capacity, and each first retry failed;
the next retries ran successfully. No substitute model wrote either rewrite.
A separate Astra Project Coordinator reviewed the module-only material assumptions
and both final alternatives. Model labels describe requested/configured delegation,
not token/cost measurements. Root integrated shared glossary/main/ADR/provenance.

RD53i definition appears once in DES-001 glossary; current designs use that alias.
Stable file paths retained. Compact A1/A2 and quad B4 now stop at module electrical
termination and bare die backs. Removed external structure, cooling hardware,
mounting adhesive and allocated service material from designs/figures/budgets.
Prior draft claims remain traceable in Git; new PM3/A3/B20 claim IDs avoid reusing
changed fact identities. Pixel volume remains open; no production geometry changed.

Added proposed common stack with explicit choices: sensor/chip silicon150um each,
polyimide core25um plus2x12.5um coverlay films, two18um copper layers,25um epoxy
bondline,20um bump standoff and25um aluminum bond-wire diameter. Thicknesses are
not certified stock. PDG materialX0 values are sourced facts; calculated0.5884%X0
is a partial local reference crossing, not complete budget/average/bound. Unknown
adhesives, bumps, films, wires and local BOM remain explicit, not zero. No module
material winner, hardware qualification or human approval claimed.

## Sources and commands

Opened public PDG2025silicon/copper/aluminum Radiation length rows and PDG2020
polyimide-film row.2025polyimide URL failed; preserved verified2020edition rather
than claiming a newer table. Catalogue adds four precise material entries. Public
module-material paper2412.04686 temporarily downloaded/text inspected as background,
without adopting experiment budget. No PDFs committed or local checksum invented.

Read repository/project/design/ADR rules; inspected clean tree and PR8 (draft,
no human reviews returned). Root and Astra reviewed physical layer topology,
partial arithmetic, unresolved constituents and module scope. Both SVGs rendered
with rsvg-convert and visually inspected; clarified quad section cut through
chips0and2 with labeled A–A line. Original SVGs remain schematic, not dimensioned
manufacturing drawings. Relevant final checks and PR outcomes recorded in JSON.

## Changes, reviews and follow-up

Main/alternative/coordinator proposals, both figures, common study JSON, ADR007,
indexes, source catalogue, tracking/reviews and session pair changed. Retain old
pending review history as withdrawn because scope changed; request exact committed
rewrite revision in new rounds. PR8 remains draft for first human review.

Resolve chip/pad/bump and delivered thinning evidence; sensor process/bias and
operating requirements; glue/laminate grades, metal/film stacks, routed coverage,
wire loops, local parts and qualification. Pixel volume is separate and remains
open. Designs/ADR stay DRAFT; identified humans own full design review/sign-off.

Final local suites passed: dashboard25tests and logging15tests; naming/link/XML
and unitconversion audits, visual SVG review and whitespace checks pass.
Published rewritece99de4, updated PR8 title/body and verified OPEN/isDraft=true.
Recorded new pending exact-revision review rounds for DES001/ADR007, superseding
withdrawn broader requests. No reviewer decision or human sign-off invented.

Hosted rewrite CI passed: https://github.com/asalzburger/nodd/actions/runs/35241157461
(policy/records, dashboard/docs tests, browser tests, static build and preview).
A duplicate run was cancelled by workflow concurrency; successful run inspected.
Final review-metadata checks validate11tasks/9documents/7rounds and33sessionrecords,
build succeeds and whitespace checks pass. Pages deployment skipped for PR.
