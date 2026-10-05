# SESSION-2026-09-30-pixel-support-cooling — Two local support concepts

## Selected request and context

User asks for at most two pixel-barrel support/cooling candidates, minimizing
material while providing stability and sufficient cooling, with technical drawings
and literature cross-checks. The request cites PR26; inspection finds infrastructure
branch restoration there. The preceding human-selected baseline is PR28, and this
interpretation was communicated before continuing. The baseline is unchanged.

The branch starts from the PR28 merge on `study/tracker-service-corridors`; local
and remote main still contained the older PR25 geometry. Unrelated usage-summary
files were preserved. DES002 was planned in PROJECT but had no existing design
file; this task supplies it as DRAFT/PROTOTYPE, with no sign-off.

## Outcomes

Recommend A, a narrow CFRP/conductive-foam sandwich with two straight counterflow
CO2 circuits, and retain B, a hollow CFRP box with local foam saddles, as the only
second candidate. A literature-backed recipe is distinguished from proposed
thicknesses, operating targets and derived screening results. Counterflow changes
the earlier hydraulic grouping assumption but retains onefeed/onereturn perstave
perend; pressure drop and flow stability are not established by the energy balance.

Actual geometry contains82staves/2750modules/6206chips. Inheritedpower gives16.682kW
nominal,25.023kW at+50%. The initial full-width beam probe finds collisions under
radial staggering; narrow10/24mm spines and thin full-width plates pass a repeated
cross-section box screen. Actual baseline pixel support depth is5mm, not the older
DES0106mm default. Proposed stack4.725mm is not a full annular/support CAD check.

B saves only0.024/0.052percentagepoint X0 for singles/quads in the assumed model;
its optimistic30% foam saddle allowance requires demonstration. Glue and flex
control may be more valuable. A remains the first prototype recommendation.
Initial280mm bearing-spacing discussion was refined to a250mm screening bound,
with six proposed planes giving224mm spans. Static bending sensitivity stays
below50um in the limited model; dynamic5um stability, torsion and common-frame
compliance remain untested. Four intermediate ribs add estimated123g and local
material; this is not free support. No sensor/module positions are moved.

Two original dimensioned technical drawings are generated in PNG/PDF/SVG, together
with repeatable inputs, numerical output and source/artifact hashes. The literature
catalogue adds the constructed IBL stave, ITk support presentation, NIST properties
and PDG materials with precise locators. Existing TDR provenance is extended.
The drawings are code-native and conceptual, not manufacturing CAD.

## Validation and limitations

Commands/results are in the paired JSON. Four narrow tests pass; figures rendered
and inspected; dashboard validates/builds. PDFs remain in ignored cache. Some web
fetches failed; accessible primary files and tables were used instead. No ACTS,
DD4hep, Geant4, FEA or hydraulic solver was run. The sensitive baseline is unchanged.

## Usage and publication

Exact client per-turn counters are unavailable; usage remains empty. Historical
project summary totals are not this task's usage. Publication links and closeout
checks follow after the draft PR is created.

## Publication and closeout

Published [draft PR29](https://github.com/asalzburger/nodd/pull/29) at
`be0a47f345168220a365c30f4c2932e3ab5b0b9a`, based on the branch containing the PR28 merge.
The CI dashboard build was in progress when inspected. PR28 merge metadata was
reconciled in tracking, preserving its working-baseline selection and approval
limits. Added an explicit warning that floating ribs cannot create short beam
spans without an independently stiff global support structure.

Final dashboard metadata initially failed because the new PR referenced DES011
but the task did not. Added the governing baseline document to both task lists;
validation/build then passed (33tasks,13documents,13rounds). All63 local paired
session logs validate; usage summary generated, with current-task counters missing.
