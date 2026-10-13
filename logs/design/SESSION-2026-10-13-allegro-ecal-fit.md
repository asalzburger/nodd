# SESSION-2026-10-13-allegro-ecal-fit — ALLEGRO LAr ECAL space assessment

## Scope and evidence

Contemporaneous curated research record. The repository is canonical. Initial
context was the completed PR67 conflict-resolution checkout at
5bf0839f88ffcf7f3892795aebe0cfb2cdaa85b1 on codex/calorimeter-cassettes, clean.
For the current volume, the maintained DES029/030 prototype at
5664d16aea2df36222dc0099ba18594cf506304d was selected. A clean dedicated
codex/allegro-ecal-fit-assessment branch was created from that revision.
This does not merge or alter the stacked geometry proposals.

Public k4geo main was observed at e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb.
Latest ALLEGRO configurations include v03 ECAL. Exact primary-source locators
and limitations are in the comparison note and source catalogue. Scalar evidence
pins source hashes. No external factory, package, PDF or source image was adopted.

## Selected conversation

Exact user request: “In the current volume for the EM calorimeter, would a LAr
based one, e.g. the ALLIGRO design fit as well ?”

Assistant outcome, paraphrase: ALLEGRO sampling fits nominal depth, but full
non-coil allocated packaging needs about67 mm extra barrel radius and117 mm
extra endcap depth. A tailored barrel merits study; turbine endcap forward
coverage requires redesign. This answer does not change the Si–W baseline.

## Prepared bounded contributions and handoffs

The initial checkout's AGENTS/role workflow required separate cross-interface
and physical-validation contributions. Instructions were prepared at5bf0839
using tools/agent_workflow/workflow.py prepare. Explicit read-only generic
subagent assignments LARFIT-SysArch and LARFIT-PhysVal targeted5664d16;
this is not a claim of verified native profile loading.

Inputs were tools/calorimeter_hardware/assemblies.json, assembly.py,
edge_sensors.json; DES029, DES030 and ADR008. No writable paths, dependency
installation, further agents or technology sign-off were authorized.

SysArch returned: distinguish the included70 mm outer coil from nODD's inner
coil; retain cryostat vessel gaps, interfaces and readout space; do not equate
16-gon apothems with round radii. The coilless allocation is600 mm, not the
502 mm simplified shell alone. Existing endcap radial/forward bounds cannot
be copied unchanged. Result independently checked by coordinator.

PhysVal returned: independently confirmed405.5/450 mm sampling depths,
600/650 mm relevant package budgets and66.8/116.8 mm shortfalls. Published
22 X0 is total sampling stack, not pure LAr. Shrinking radius changes plate/gap
geometry; shrinking material changes X0. Published performance and older turbine
parameters must not be transferred to a new nODD configuration. Cryostat/readout
and complete particle-flow integration still need work. Both contributions
completed without repository edits.

## Decisions and outcomes

Assessment remains DRAFT/INFERENCE. Source-based dimensions are FACTS about
public simulation parameters, not engineering qualification. Existing nODD
inputs remain unsigned prototype choices. No human technology/design sign-off
or accepted envelope amendment was inferred.

Removing the70 mm outer-coil proxy is an explicit repackaging hypothesis.
ALLEGRO's other allocated margins remain necessary study space. A circular
cryostat between unchanged16-gon boundaries has a conservative499.90 mm slot;
actual containment needs native geometry and agreed interfaces. Eta4 at the
translated sampling front is146.94 mm, inside the410 mm first turbine wheel.
Shrinking the aperture alone is insufficient, including the driver's49 degree
blade constraint. HCAL forward aperture remains an independent issue.

## Commands and validation

- Official GitHub API/raw source reads identified the pinned configuration,
  inclusion chain, constants and actual turbine driver. XML/C++ hashes retained.
- Primary INSPIRE PDF copies of the CALOR2024/EPJ2025 and EPS2025 publications
  were read. Some direct CERN/official web requests were inaccessible to automated
  access; primary public mirrors and official GitHub sources resolved the needed
  facts. Exact source identity and access limits remain in the catalogue.
- Inline Python using a restricted AST arithmetic parser evaluated named XML
  constants, rather than executing arbitrary expressions; exit0. Current
  assembly.inventory() independently confirmed523.2/533.2 mm depths.
- Independent inline Python re-evaluated11 retained bounds from named constants,
  checked both nODD depths and four current input hashes, and ran inventory;
  exit0. Formulas and numeric results are retained in allegro-fit.json.
- python3 -B tools/project_records/validate.py: exit0;
  63 tasks,36 documents and19 review rounds.
- Native LAr geometry, overlap, mass/material, transport and structural/thermal
  cryostat studies: NOT RUN. No LAr detector was implemented.

## Changes and revision links

Added the bounded comparison note and scalar evidence; registered three public
sources; attached evidence to the existing calorimeter hardware-assessment task.
Only records changed. The paired JSON inventories all six paths. Git history
locates this record's enclosing commit without a self-referential hash.
Dedicated branch is pushed to origin (asalzburger/nodd) for versioning under
standing user authorization. No new PR or external-software adoption requested.

## Token accounting

Exact client-reported per-turn counters for this root turn and the two
contributions were unavailable. Usage remains empty/unknown, never estimated.
Existing branch-snapshot totals are neither usage for this task nor a claim of
complete current project accounting. Journal summary reports observed counters
and missing coverage; no private client state was collected here.

## Follow-up

If pursued, first agree the cryostat/magnet/HCAL interface budgets and full
service envelope; then design an adapted barrel and inner-endcap/forward section.
Native containment, material and cryostat engineering must precede any performance
or technology decision. Published resolutions cannot establish nODD performance.

## Record validation

Journal validation passed for177 session pairs; project records passed for63
tasks,36 documents and19 review rounds. Branch-snapshot summary contains209
observed turns:617282110 input +3530717 output =620812827 total tokens, with60
sessions lacking observations. None of those counters measures this task.
Tracked diff whitespace check passed; final staged check is run before commit.
