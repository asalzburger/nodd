# DES-005 input — Tracker technician

- Status: DRAFT planning input; no layer or component design sign-off.
- Date: 2026-09-18.
- Role: `TrackTech`; AI-assisted technical contribution, not human review.
- Context: [PROJECT](../../../PROJECT.md), [development plan](../../DEVELOPMENT_PLAN.md),
  [DES-003](../DES-003-global-envelopes.md),
  [ADR-006](../../decisions/ADR-006-global-envelope-and-field-hypotheses.md).
- Existing pixel work: [issue #7](https://github.com/asalzburger/nodd/issues/7),
  [PR #8](https://github.com/asalzburger/nodd/pull/8), inspected at
  `d237f146b578915cc032b30efa50044cf6344d5f`.
- Human review coverage: see the [DES-005 reviewer map](../DES-005-tracker-system-plan.md#human-reviewer-coverage--2026-09-18);
  component-specific assignments beyond those topics remain open. Final sign-off authority where required:
  `asalzburger-review`; no sign-off is recorded here.

## Position and constraints

**NODD DESIGN CHOICE — human-directed investigation:** retain the reviewed
tracker assembly envelope and the fixed tracking requirement `|eta| < 4`; use
ODD's progression from pixels through short strips/strixels to stereo outer long
strips as the initial architecture. The coverage requirement applies to the
tracker as a system, not automatically to every technology. Internal subsystem
boundaries, active radii, disk positions, layer counts and module assignments
remain to be studied. The innermost host boundary is not an active sensor radius.

**NODD DESIGN CHOICE — proposed; approving humans pending:** develop a small
ODD-like candidate family jointly with component and services work. Compare
layouts on demonstrated performance and credible material/engineering content.
Allow well-motivated departures, including timing, through explicit comparisons.
Do not delay all layer studies until complete module qualification, but do not
freeze a layout whose module outlines, services or measured coordinates exist
only as ideal assumptions.

TrackTech's principal challenge to a radius-only optimization is that module
edges, stereo pairs, repeated supports and service exits consume the same space
and material that determine the apparent physics advantage. These effects must
enter the early candidate definition, with explicit uncertainty where unfinished.

## Evidence and boundaries

Public source IDs resolve in the [catalogue](../../../reference/manifest.yaml).
Source facts below describe the inspected ODD revision, not adopted nODD values.

| ID / classification | Observation | Precise locator / consequence |
| --- | --- | --- |
| TT-F01 — FACT | ODD separates pixels, short strips and long strips, including barrel and endcap structures with sensitive and passive components. | `SRC-ODD-UPSTREAM`, revision `c167363f3d4ad1540a577af99071283caf54f3a6`, `xml/detectors/TrackerPixels.xml`, `TrackerShortStrips.xml`, `TrackerLongStrips.xml`: readouts, modules, rings, layers and detector assemblies. Extract this as a comparison layout; do not transfer unsupported engineering claims. |
| TT-F02 — FACT | ODD long-strip modules have paired sensitive sensors with relative rotations, while their XML readouts use `CartesianGridXY`; the geometric ACTS digitization configuration supplies a single measured coordinate for long strips. | Same source/revision, `TrackerLongStrips.xml`: `LongStripBarrelReadout`, `LongStripEndcapReadout`, `SensorS`/`SensorA` and endcap sensor components; `config/odd-digi-geometric-config.json`, entries for volumes 23–25 and 28–30. See retained [assessment E03/E04](../../validation/ODD-realism-assessment.md#outer-tracker-real-stereo-structure-ambiguous-measurement-contract). Audit these distinct contracts before quoting resolution or channel counts. |
| TT-F03 — FACT | The ODD tracker includes support, cooling-pipe and cable representations; they are not a validated complete services budget. | Same source/revision, tracker XML module/support/cooling/cable elements; [assessment E02/E03/E09](../../validation/ODD-realism-assessment.md). Retain inspected passive structures in the comparison and identify replacements explicitly. |

The [pinned DES-001 proposal](https://github.com/asalzburger/nodd/blob/d237f146b578915cc032b30efa50044cf6344d5f/docs/design/DES-001-rd53-pixel-modules.md)
is an existing **NODD DESIGN CHOICE — proposed**, not a public hardware fact or
approved module. Its “Scope and exclusions”, “Dimensions, material table and
cross-sections”, and PM3-I02 define the interface used here:

- A1, A2 and B4 are single-, two- and four-chip assembly alternatives. Their
  nominal readout areas are not certified active footprints or finished outlines.
- The boundary ends at the module electrical termination and bare die backs.
  Mounting adhesive, supports, cooling and external power/data distribution are
  deliberately excluded and need separate owners below.
- The `0.5884% X0` subtotal is a **partial local reference path** through selected
  constituents. It is neither a complete module budget, an area average nor a
  bound. Never populate a complete layer-material field with that value.
- The compact-module qualification sequence does not decide which module family
  tiles the tracker. Layer suitability must feed back into the module comparison.

## Component and interface work packages

Every package below is **NODD DESIGN CHOICE — proposed**, with expert reviewers
and numerical acceptance criteria pending. Package IDs identify planning scope;
they do not allocate new design-document numbers or assert that work has started.

| Package | Deliverable and arguments | Dependencies / handoff |
| --- | --- | --- |
| TT-P01 — Existing pixels | Continue DES-001 A1/A2/B4 comparison. Supply physical outline including flex/bonds/termination, active matrix and guard/seam masks, allowable assembly orientations, spatial material constituents, measured coordinates and response assumptions. Prefer the fewest justified module types; a larger nominal area alone proves neither lower material nor better coverage. | Existing issue #7 / PR #8; consume successive pinned revisions without duplicating that design. Provisional outlines carry explicit uncertainty until qualified. |
| TT-P02 — Short strips / strixels | Establish a public-source sensor/readout/module proposal. Define physical segment length and pitch, sensor shape, measured coordinates, electronics topology, inactive edges, response covariance, operating assumptions, power/data load and complete module boundary. Compare true segmented measurements with any proposed effective representation. | Can start beside pixel work. Depends on PhysVal occupancy and resolution use cases; no inherited ODD name or Cartesian cell setting is a hardware selection. |
| TT-P03 — Stereo long strips | Define sensor axes, relative rotation, separation, mechanical pair, readout measurement dimension, covariance and ambiguities. Describe pair failure and misalignment assumptions, seams, hybrid/readout footprints and material. Compare stereo precision, pairing ambiguity, support thickness and channel/load consequences together. | Shares requirement inputs with TT-P02. Deliver independent sensor identities plus physical pairing/grouping; do not call a paired module two independent spatial points. |
| TT-P04 — Local supports and repeated structures | Draft module attachment, mounting glue, stave/petal/ring support, local cabling and cooling interfaces; account for joints, end structures and dead regions. Define which repeated structures can plausibly carry each module option. | Starts from provisional TT-P01–03 interfaces; final dimensions depend on completed outlines and loads. Feed mounting/clearance constraints back before layer freeze. |
| TT-P05 — Cooling and thermal assumptions | Specify the thermal path from module/die to local carrier and coolant, pipe wall and coolant inventory, manifold transitions and exit ownership. Link heat loads and operating scenarios to material/space hypotheses; identify missing thermal engineering evidence. | Joint with TT-P01–04 and TT-P06. No coolant, mounting contact or manifold may disappear between the module and tracker budgets. |
| TT-P06 — Power, readout and service distribution | Draft power topology, conductor/insulator inventories, data aggregation and electrical/optical conversion placement, connectors and cable bundles. Carry load and routing uncertainty; define barrel/endcap exits and the handoff into common corridors. | Module electrical terminations are inputs, not complete distributions. SysArch owns common interfaces, TrackTech owns tracker-side paths, SoftEng retains explicit accounting identities. |
| TT-P07 — Barrel/endcap tiling and layer candidates | Produce candidate layer/ring layouts with full module outlines, active masks, overlaps, staggering, support footprints and service routes. Compare pixel extent, technology transitions and endcap arrangements. Preserve both detector sides and azimuthal gaps; avoid treating ideal disks as a tiled solution. | Starts with provisional TT-P01–06 scenarios, improves iteratively through parametric and ACTS studies. Fit inside DES-003; any necessary expansion becomes an explicit amendment. |
| TT-P08 — Timing alternatives | Investigate timing capability of the outermost tracker layer as directed in DES-003 review round 2. Define sensor/readout basis, measured time response, efficient coverage, radiation/operating assumptions and added support/services. Compare separate timing structures or multiple layers only where justified by performance. | Coordinate with PhysVal and SysArch. A barrel option needs a separately demonstrated forward strategy; ordinary spatial readout or a simulated time field is not timing hardware. |

Separate support/cooling/power/data packages are necessary because their omission
from DES-001 was intentional scope control. They must not be silently inserted
into the pixel module BOM or assigned to a generic unowned material allowance.

## Progressive layer study and component feedback

1. **Extract the comparison.** SoftEng and TrackTech inventory the pinned ODD
   study layout, sensor axes, active/passive boundaries and digitization choices.
   Mark its study identity separately from the eventual approved comparison
   baseline. Check dimensions in the factories as well as XML parameters.
2. **Prepare the first candidate inputs.** TT-P07 proposes ODD-like barrel and
   endcap arrangements with hypotheses for changed pixel extent, transitions and
   timing. Keep internal boundaries variable inside the retained full envelope.
   TT-P01–06 provide provisional geometry/material/response ranges with sources
   or explicit design rationale. Unknown contributions stay unknown.
3. **Run inexpensive estimates.** Parametric studies compare spatial resolution,
   transverse lever arm and scattering sensitivity using a common set of
   component, material and field scenarios. Feed deficiencies back to layer
   positions, measurement axes and module choices. A missing endcap or stereo
   capability in an estimator limits the conclusion; it must not remove that
   region or measurement from requirements.
4. **Replace ideal surfaces by modules in ACTS.** Test finite active bounds,
   seams, stereo pairs, overlaps, supports and service footprints. Evaluate
   hermeticity and independent measurement information versus vertex, momentum,
   eta and phi in shared field scenarios. Include beam-spot sensitivity before
   freezing disk positions, then use the agreed beam-spot distribution in final
   coverage validation. An origin-only ray plot is a preliminary diagnostic.
5. **Close physical budgets before selection.** Reconcile module counts and area,
   component material inventories, local support and routed services for the
   shortlisted layouts. Compare directional material with realistic incidence,
   including peaks and transitions. Send a candidate back for redesign if its
   apparent performance advantage relies on omitted services or impossible fit.
6. **Advance through human review and later full simulation.** Pin the selected
   layout and component/interface proposals for technical, expert and final
   human review. DD4hep construction and later Geant4 transport validate the
   actual assembly and physics claims when that backend is available. Any
   unsigned executable study remains an isolated `PROTOTYPE`.

The stages are iterative: component changes may invalidate a previous layer
ranking. Material and field scenario identifiers must accompany every comparison
so that a better curve cannot be attributed to layout when it came from a lighter
budget, ideal response or a different field.

## Material and measurement handoff

**NODD DESIGN CHOICE — proposed:** each component/interface record supplies a
stable identity, owner, source/revision, physical and active bounds, composition,
density, thickness/volume or coverage description, uncertainty and physical
placement. State the reference area for area averages. Keep local hotspots,
off-normal paths, inactive material and services outside sensor footprints.
Maintain a ledger linking the same constituents through explicit geometry and
any effective material; preserve the declared mass/material integral and avoid
double counting when explicit components replace an allowance.

Early material machinery may use separately labelled test fixtures and bounded
design scenarios. A fixture tests integration and mapping; it supplies no evidence
for the physical tracker budget. For study scenarios list omitted constituents
and their unresolved consequences; a scenario with missing material cannot pass
the complete-budget gate.

The measurement contract supplies local axes, dimensionality, covariance,
physical sensor separation, active mask, sensor/module/pair identifiers and
assumed efficiency. PhysVal should report sensor crossings, grouped pairs,
independent information and fit conditioning separately. Timing comparisons
should include a spatial baseline, the candidate's extra material with timing
information disabled, and the same candidate with its stated timing response.
This exposes the cost and benefit of timing without silently crediting either.

## Questions the other roles must challenge

| Role | TrackTech request | Consequence if unresolved |
| --- | --- | --- |
| SysArch | Own beam-pipe clearance, support hierarchy, assembly boundaries and local-to-shared service handoffs. Judge timing competition and proposed envelope amendments explicitly. | Active first radius, forward apertures and service fit cannot be frozen. |
| PhysVal | Set benchmark conditions, beam-spot assumptions, required independent measurements and performance criteria before ranking. Quantify stereo ambiguity, forward lever arm, material sensitivity and whether timing compensates its cost. | Good crossing counts or ideal covariances cannot select a physical tracker. |
| SoftEng | Preserve physical module and sensor identities, axis conventions, material accounting and scenario provenance across parametric, ACTS and DD4hep representations. Expose unsupported response/readout features rather than silently idealizing them. | The stages may compare different detectors despite using the same layout name. |

No new detector number, numerical performance target, layer count, material
allowance, stereo angle or timing resolution is selected by this input. The only
material subtotal quoted above explains the limitation of existing DES-001 work.
No detector build, propagation, material scan or simulation was performed here.
