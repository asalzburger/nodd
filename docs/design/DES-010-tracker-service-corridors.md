# DES-010 — Tracker support and service corridors

- Status: DRAFT
- Created: 2026-09-29
- Human owner and technical approvers: unassigned
- Scope: **PROTOTYPE — unapproved working hypothesis**, not detector integration
- Origin: human request following [PR #24](https://github.com/asalzburger/nodd/pull/24)
- Related: [DES-005](DES-005-tracker-system-plan.md), [DES-009](DES-009-module-populated-layouts.md), [DES-003](DES-003-global-envelopes.md), [ADR-006](../decisions/ADR-006-global-envelope-and-field-hypotheses.md)

## Scope and approval boundary

The user explicitly states that PR #24 did **not approve** the tracker default.
Use `cobe-review_default-mixed` only as the starting working hypothesis. Merging
its prototype and evidence did not approve a layout, local support or services.

This task estimates supports, cables and cooling from public TDRs, reserves
continuous routes, removes complete module rows where needed, and draws routing
mockups. Layer radii and disc z positions are held fixed. Layer-position
optimization is a separate follow-up PR. No production DD4hep geometry, effective
material composition, reconstruction configuration or sign-off is introduced.

## Requirements and proposed method

All requirements and numerical reservations in this section are **NODD DESIGN
CHOICE**, directed by the user or proposed here; numerical approvers: none.

| ID | Requirement / proposed choice | Rationale and consequence |
| --- | --- | --- |
| SC-C01 | Pixel services between pixel and short-strip packages; short-strip services between short and long strips | Human-directed topology, using occupied module/support extents rather than ideal layer radii |
| SC-C02 | Long-strip services use the outer tracker interface reserve, conditional on vessel clearance | DES-003 reserves r=1140–1240 mm; this is not proof of a qualified service passage |
| SC-C03 | Barrel services turn radially through a barrel/endcap bay, then join their subsystem's axial trunk outside endcap rings | Reserve finite bend/connector space; a centreline alone is insufficient |
| SC-C04 | Remove complete original endcap radial rows or barrel end rows intersecting required reservations | Preserve retained module/sensor/patch IDs, transforms and nominal-layer denominators; report every removal and coverage cost |
| SC-C05 | Count power supply/return, data/control and cooling feed/return explicitly, with aggregation and uncertainty | TDR system totals and local pipe diameters cannot silently become nODD trunk dimensions |
| SC-C06 | Compare nominal and conservative inventories against a finite packing/azimuth allowance | An area inequality is necessary but insufficient; bends, discreteness and connected clearance must also be checked |
| SC-C07 | Reserve local support depth separately from the inherited electronics/module trial body | Source sandwich dimensions supply a space estimate, not a structural or thermal qualification; local cooling is contained in the support, not added twice |
| SC-C08 | Retain an explicit rear interface proposal beyond the `abs(z)=3150 mm` tracker host, if needed to reach the end of the vessel | The last long-strip disc leaves only 14.35 mm before the host boundary. Existing DES-003 service allocation ends there; any continuation is new, unapproved interface space |
| SC-C09 | Reuse the finite-module crossing workflow for a before/after loss check | This diagnoses removal costs; it does not optimize positions or simulate service material |

## Initial occupied-space audit

**SC-I01 — INFERENCE:** applying the DES-009 oriented-box bounds to the working
geometry gives pixel/short-strip endcap radial separation −3.991 mm and
short/long-strip separation −26.384 mm. These projected envelope overlaps explain
why no continuous annular route exists; they are not claims that boxes on
different z planes physically collide.

The pixel and short-strip barrel/endcap axial bays are about 92.5 and 109 mm.
The long-strip bay is only 7.890 mm. Removing one original row from each end
of each long-strip barrel gives about 120.556 mm while keeping retained module
positions. No measurement surface is clipped or silently repositioned.

The proposed route model will use conservative r–z bounds of full bodies and
separate support reservations. Full azimuthal exclusion envelopes deliberately
reserve all-phi clearance; capacity may use only a stated fraction of azimuth.
This can remove more modules than a later sector-specific engineered solution.

## Evidence and open engineering questions

The [pixel](inputs/DES-010-pixel-services.md) and
[strip](inputs/DES-010-strip-services.md) dossiers record exact public-source
pages, dimensions, electrical grouping, cooling topology and uncertainty.
The [numerical budget inputs](../../tools/module_layout/services_budget_inputs.json)
classify every adopted number, including TDR values used as nODD design choices.
Sources: SRC-ATLAS-TDR-025/030, SRC-CMS-TDR-014, and the three later pixel
status/services/cooling sources catalogued in `reference/manifest.yaml`.

**SC-I02 — INFERENCE:** the cited ATLAS strip stack needs 6.34–6.54 mm between
sensor midplanes, exceeding the frozen 5 mm long-strip sandwich. Reserve an
external carrier/cold-rail envelope rather than silently changing that sandwich.
Its attachment and thermal bridges to each staggered module are undefined;
annular keep-outs do not constitute a mechanical support solution or certify
that every cooling contact can be built.

**SC-I03 — INFERENCE:** the working 0.5 mm strixels have 122,880 channels per
module, about 4.068 times the CMS PS connected macropixel count. Scaling the
complete PS service load by this factor is a stress scenario, not a prediction
or a bound. Do not relabel an ATLAS strip-module power budget as nODD demand.

## Numerical routing hypothesis

All reservations are **NODD DESIGN CHOICE — unapproved**, SC-C10–17, with
per-field rationales in [services_config.json](../../tools/module_layout/services_config.json).
Lengths are mm. Local supports reserve 5 mm (pixels) and 6.6 mm (strips) beyond
the module trial body, and routes clear those envelopes by 2 mm. The nominal
inner pixel support clears the 25 mm host by only about 1 mm; assembly details
and a changed support depth must therefore be rechecked.

The initial pixel, short-strip and long-strip annuli are respectively
170–242, 635–805 and 1144–1220 mm. Barrel radial bays are initially
575–625, 1220–1300 and 1310–1400 mm in absolute z. The corresponding whole-row
removals preserve module transforms and ideal-layer denominators. These are
mechanical trial choices, not optimized layer radii, disc positions or pitches.

The reference capacity scenario uses 75% of azimuth and 50% packing, with pixel
data aggregation. An adverse scenario uses 50% azimuth, 40% packing, 25% spare
demand and one pixel uplink per chip; a further stress uses four uplinks per chip
and scaled strixel harnesses. Failures remain explicit. A route with available
space but inadequate cable cross-section is not certified usable.

Collectors behind each disc join the axial trunks. A new unapproved rear bay
and bore continuation beyond the tracker host are explicitly compared with
the coarse vessel and calorimeter reservations. The final vessel-end passage
is only a conditional handoff proposal, not a qualified feedthrough or a route
through the rest of the detector to the experimental cavern.

**SC-C18 — NODD DESIGN CHOICE, turn amendment:** the first capacity probe
passed route-area checks in the reference scenario but failed at finite joining
throats. Start each axial trunk at the beginning of its barrel radial bay and
continue the common bore envelope through the full vessel-end exit bay. This
increases actual turn space without moving sensors. Declare the intended flow
tree: barrel segments accumulate inner-layer traffic, collectors join their own
trunks, rear segments accumulate subsystem traffic, then reach the common exit.
Incidental geometric contacts stay visible but do not represent mandatory flow
paths. Every declared edge must physically connect and preserve all upstream
source modules; required small throats still fail. The rejected first probe is
retained separately, not overwritten.

Open: voltage drop/current capacity, connector and optical conversion placement,
hydraulic pressure drop/dry-out, thermal runaway margins, structural loads, mounting and access, field-vessel interfaces, radiation tolerance and material
composition. No service-material or performance acceptance is claimed.

## Validation contract

Check deterministic input hashes and retained identifiers; complete-row removals;
module/support exclusion from connected route envelopes; tracker/vessel boundary
conditions; conservative and nominal cable/pipe capacity at each route throat;
support extent and module counts/area; before/after crossings on identical
luminous-region straight/3 T samples. Keep failures and unresolved interface
conditions visible. Mockups must distinguish existing host space, new unapproved
interface proposals, physical module bodies, supports and service envelopes.

Human review of the routing budget and mechanical hypotheses is required before
the separate constrained layer-position optimization or production integration.

## Retained prototype evidence

The [service-gap report](../validation/DES-010-tracker-services.md) records the
source estimates, selected reservations, routing mockups, failed adverse budgets,
row-removal costs and native ACTS check. Reference capacity passing does not
approve the tracker or its interfaces. Optimization remains a separate follow-up.

## PR #25 review: comparison and accumulated loads

The [expert question](https://github.com/asalzburger/nodd/pull/25#issuecomment-5890301780)
asks for ATLAS/CMS gap comparisons and whether the final service bundle was
charged along the entire endcap route. The source comparison is retained in
[the upgrade-services dossier](inputs/DES-010-upgrade-service-comparison.md).
Its dimensioned engineering-envelope facts and derived widths are distinguished
from sensor-envelope separations and from usable cable capacity.

**SC-I04 — INFERENCE:** the original axial-trunk ledger carries the complete
signed-end subsystem inventory uniformly along the fixed corridor. Barrel radial
segments, individual disc collectors and rear owner combinations already select
local/accumulated source groups, but the axial trunks do not vary their load with
z. Thus the original reservations are a conservative geometric hypothesis, not
an estimate of the necessary width at every upstream disc.

**SC-C19 — NODD DESIGN CHOICE, unapproved diagnostic:** add a separate cumulative
profile without changing the retained geometry or reference evidence. Each direct
feeder contributes its whole original source groups at the near edge in absolute
z of its finite overlap with the axial trunk. This conservative pickup convention
is explicit; it does not locate connectors inside the pocket. Groups enter once,
with the inherited chain and per-layer manifold rounding, and the final load must
match the original whole-end budget. Both detector ends are profiled separately.
The area-equivalent annular width holds the original inner radius, packing,
azimuth occupancy and boundary allowances fixed; it is not a tapered design.
Full loads remain in rear/shared routes and through extraction pockets. Actual
tapering, row recovery and layer positioning remain a separate optimization PR.

## Reviewer-directed optimization follow-up

The [subsequent expert direction](https://github.com/asalzburger/nodd/pull/25#issuecomment-5891018641)
requests constant maximum service corridors, at least 10 mm barrel/first-disc
clearance, an optional final-disc downstream bypass, and new module placements
to improve coverage and inter-hit spacing. The separate
[DES-011 prototype](DES-011-service-constrained-tracker-optimization.md) records
and tests those constraints. This does not change the retained DES-010 geometry
or confer approval on PR #24, the service budget or the resulting placements.
