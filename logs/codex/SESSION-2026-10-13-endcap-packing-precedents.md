# SESSION-2026-10-13-endcap-packing-precedents — SiW/Si packing precedents

User exact request: “Understood, in other SiW or Si-based calorimeters (FCC,
HGCal CMS) - how is this packing problem solved?” Scope: primary-source
architecture review, versioned with the ongoing open PR69. Starting revision
4d9a8d701d7463e66097883a930c2b7349eda112, branch codex/calorimeter-assemblies,
clean. No geometry implementation, sensor adoption or design approval.

Research distinguishes FCC-ee CLD's simulated SiW concept from its ILD/CALICE
hardware precedent. Primary CLD v3 PDF section5.5 states continuous-operation
cooling redesign is unresolved; indexed2026 CLD slide7 still lists relevant
R&D. CALICE PDF4/6 describes quarter-endcap structures, compact ASUs and shared
slab-end readout. These do not qualify a complete continuously cooled CLD endcap.

Primary HGCal engineering publication metadata and indexed PDF2 sections2.3/2.4
show full/partial hexagonal modules on60-degree CE-E/30-degree CE-H cooled
cassettes, with electronics/services occupying layer depth. The partial-sensor
paper v1 HTML explicitly documents intended dicing lines and guard/HV
structures. Inspection of latest v4 (2026-07-24) retains these facts; precise
source version updated before committing. No arbitrary clipping of standard
silicon or exact global coverage/efficiency claim is supported.

Inference/proposal: many compact units per broad carrier, jointly designed inner
support/seams and shared services; preserve square sensors initially and study
small custom-board families. Custom partial silicon is a later engineering/
manufacturing decision. No change to SiW/steel-scintillator baseline or software
dependencies. Area losses remain explicit; staggering is an option to assess,
not a claimed current CMS specification or a cure for missing inner coverage.

Readable primary arXiv PDFs/HTML and indexed primary publication text supplied
usable evidence. CDS/EPJ PDFs were challenged/403; MDPI429; direct2026 slide
retrieval403; screenshot requests failed. Source catalogue and note distinguish
those limits from actual full-document inspection. A research JS tool call had
a syntax error and was corrected; an initial local search used the wrong DES027
filename, which was recovered using rg --files. No unsupported stagger claim
from secondary literature was transferred to the review.

Added a companion design note, link from the repair proposal, four source entries
and current CALICE locator, task evidence and this paired journal. Required
project/session/token-site checks and exact changed files appear in the JSON.
The initial completion journal incorrectly represented web inspection as a
shell PASS with no exit code; validator rejected it. The entry was removed;
source evidence remains in activities/catalogue and a failed-check record is
retained. No validation rule was changed.

No native geometry or physics-performance checks were needed for this prose
review. Token counters for this task are unavailable: usage is empty/unknown,
not zero; previous observations are not duplicated.

Repository summary/site retains209 disjoint observed turns and620812827
observed tokens; this task has no available observations and adds none.
