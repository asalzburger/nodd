# DES-009 — Finite modules in cobe and pint

- Status: DRAFT
- Created: 2026-09-28
- Updated: 2026-09-29
- Author: Codex with three delegated implementation/validation agents
- Human owner: unassigned
- Issue: no separate issue; requested continuation of PRs #8, #14, #21 and #22
- Governing designs: [DES-005](DES-005-tracker-system-plan.md), [DES-006](DES-006-first-tracker-layouts.md)
- Governing ADRs: no new architecture decision
- Sign-off record: pending; no design approval asserted
- Implementation PR: [#24](https://github.com/asalzburger/nodd/pull/24) (isolated prototype and evidence)
- Validation evidence: [completed comparison and retained bundles](../validation/DES-009-module-populated-layouts.md); 477,312 numerical trajectories and 32 passing native audit cases

## Scope and authorization

**PROTOTYPE.** The human requested populating the proposed `cobe` and `pint`
layers with the current working sensor/module models, comparing staggering and
tilts, measuring reachable hits and silicon area, and publishing a PR. This
authorizes an isolated numerical exploration. It does not authorize production
DD4hep integration, detector design sign-off, or a reconstruction change.

The additional request to make the workflow repeatable governs its interface:
module dimensions, active masks, placement controls, layer geometry, sampling,
and output location are explicit inputs. A new input revision must produce a
new evidence directory with recorded hashes. Existing evidence is not silently
replaced. Unimplemented shapes must fail explicitly; rectangular active patches
can represent disconnected readout islands on one physical sensor.

## Requirements

| ID | Requirement | Classification | Measurement and acceptance |
| --- | --- | --- | --- |
| MP-C01 | Populate both named proposals, preserving their ideal-layer definitions | NODD DESIGN CHOICE | Deterministic finite-module construction; compare to the unchanged ideal layers |
| MP-C02 | Compare flat, staggered, staggered plus tilt, and a simpler barrel/staggered endcap hybrid | NODD DESIGN CHOICE | Retain all controls, including coverage failures and body clashes |
| MP-C03 | Allow single, double and quad pixels; favour fewer assemblies/families when coverage permits | NODD DESIGN CHOICE | Report module, sensor, chip and family counts with active and gross sensor areas |
| MP-C04 | Straight lines and 1 GeV tracks in constant axial 3 T, with x/y in [0,1] mm and z in [-150,150] mm | NODD DESIGN CHOICE | Main interpretation is **pT = 1 GeV**, both charges; total momentum is pT cosh(eta). A config option permits a separate total-p study |
| MP-C05 | Measure total and per-subdetector hits and sampled hermeticity | NODD DESIGN CHOICE | Finite active intersections; physical sensors, complete stereo pairs and distinct stations reported separately |
| MP-C06 | Check the numerical intersection calculation against native ACTS propagation | NODD DESIGN CHOICE | Exact active-patch/sensor IDs must agree on the retained validation sample; discrepancies fail validation |
| MP-C07 | Permit future module/layer updates without changing the sampling/report machinery | NODD DESIGN CHOICE | External JSON inputs, deterministic sampling, input/code hashes, saved configuration and a documented rerun command |

No quantitative detector acceptance threshold has been approved. These are
execution and traceability criteria, not scientific acceptance criteria.

## Input provenance

The source snapshots are public **draft proposals**, not qualified hardware
specifications. Their exact revisions and byte hashes are embedded in
[`sensor_models.json`](../../tools/module_layout/sensor_models.json). The nominal
layers come from [the DES-006 catalogue](DES-006-named-layouts.json).
Catalogue IDs are `SRC-DES009-PIXEL-SNAPSHOT`,
`SRC-DES009-SHORT-STRIP-SNAPSHOT`, `SRC-DES009-LONG-STRIP-SNAPSHOT`,
and the inherited public `SRC-RD53-OVERVIEW-2023`. ACTS binding provenance
is `SRC-ACTS-PYTHON-SENSITIVITY`; the source/install states remain distinct.
Target-step control is `SRC-ACTS-PYTHON-STEP-SIZE`, supplied by draft
[ACTS PR #6178](https://github.com/acts-project/acts/pull/6178). The temporary
overlay records reused objects and the new propagation binding separately.

| Input | Pinned revision | Precise locator / content used |
| --- | --- | --- |
| Pixel PR #8 | `214747a3c83c140caa6c4ae9c3fb6486ac5cb825` | DES-001 PM3-F01/PM3-I01, compact A3-I01, quad B-I20/B-I21/B-C22; one, two or four RD53 matrices |
| Short-strip PR #21 | `13ad65a981a8e00a1e5d43e82be94ccdee8419d5` | DES-007 C02–C06 and `tools/short_strip/inputs.json`; 48 × 96 mm active working model |
| Long-strip PR #22 | `0d49d04f5bfe56007ba023d2d563f4363c3f9c7c` | DES-008 C02–C08/I03 and `tools/long_strip/inputs.json`; two 96 × 96 mm sensors, 5 mm separation, 40 mrad relative stereo |
| Named proposals | catalogue bytes hashed per run | DES-006 R-C09; cylindrical cobe and pint with inclined short-strip ends |

**MP-F01 — FACT:** the public RD53 reference used in DES-001 specifies a
400 × 384 matrix of 50 × 50 micrometre cells (SRC-RD53-OVERVIEW-2023, slide 5).
**MP-I01 — INFERENCE:** multiplication gives a 20 × 19.2 mm active matrix,
384 mm² per chip; two/four matrices give 768/1536 mm². This is readout area,
not a verified finished sensor outline or an efficiency measurement.

All inherited strip dimensions remain **NODD DESIGN CHOICE**, as classified in
the unsigned proposals. Their electronic feasibility is not established here.

## Explicit placement hypotheses

The executable numerical register is `sensor_models.json`. Each of the following
is a new **NODD DESIGN CHOICE**, with human approvers pending:

- **MP-C08, conditional pixel outline:** 0.5 mm trial guard and 0.2 mm interchip
  gap. Separate active chip islands share a physical sensor identifier. Approximate
  die periphery and trial service allowances enter the occupied body, while gross
  sensor area counts the assumed sensor outline once. These unknowns need a
  sensitivity variation, not an assertion of a seamless multi-chip sensor.
- **MP-C09, flat control:** pitches use trial occupied-body dimensions plus
  0.2 mm clearance. Bodies sit without radial/z staggering. This exposes the
  inactive area cost of simple supports rather than assuming active tiles touch.
- **MP-C10, staggering:** active overlap allowances are (u,v) = (1,2) mm for
  pixels, (2,8) mm for short strips, and (6,24) mm for long strips. They reserve
  geometric coverage around seams and stereo/normal offsets. Adjacent rows
  shift by half an azimuthal pitch, columns have alternating meridional offsets,
  and four normal levels use 1.2/3/8 mm spacing respectively. Endcap long strips
  retain the proposed six rings and 16 mm radial margin. Other endcaps use a
  2 mm trial edge margin. These values are hypotheses to test, not optimised
  engineering dimensions or promised clearances.
- **MP-C11, tilt control:** an additional 12 degree rotation about the local
  meridional axis changes the normal and projected azimuthal width; pitched
  overlap and body collisions must both be evaluated. Pint inclined rings keep
  their prescribed normals, without an additional artificial tilt.
- **MP-C12, simpler hybrid:** flat cylindrical barrels plus staggered endcaps
  and inclined rings. Its coverage penalty quantifies the possible price of
  reducing support complexity in the barrel.
- **MP-C13, mixed pixels:** single chips at barrel radii below 80 mm (the first
  two proposed layers), quads elsewhere. This compares a two-family policy to
  uniform single/double/quad controls; it does not assert mechanical fitness.
- **MP-C14, clearance amendment:** preliminary occupied-body SAT exposed clashes
  in the first four controls. Preserve those failures. Add `hybrid_clearance`
  and `staggered_clearance`, using four azimuthal colours × two radial parities
  for pixel endcaps (eight normal levels, with azimuthal counts rounded to the
  four-colour period). For staggered barrels, use normal spacing
  `max(inherited spacing, body thickness + 2*(hypot(radius, body width/2)-radius)
  + 0.2 mm)`. The added term reserves curvature sagitta on both bodies plus
  clearance. This is a mechanical exclusion hypothesis, not a coverage fit.
  Re-evaluate occupied-body intersections, host containment and coverage after
  changing the placement. The hybrid retains flat barrels.

No module is cropped to an ideal layer or host boundary. Full short-strip
modules can overhang pint's finite inclined segments. Overhangs, host violations
and trial occupied-body intersections must remain visible. An arrangement with
clashing trial bodies is a rejected mechanical candidate even if it has better
hit coverage. Resolving such conflicts requires a reviewed placement amendment.

## Reviewer-directed default — 2026-09-29

The [expert comment on PR #24](https://github.com/asalzburger/nodd/pull/24#issuecomment-5886458913)
requests a concrete default for further work and transverse barrel/endcap views.
This is direction for the isolated **PROTOTYPE**, not formal detector sign-off.
The prior comparison and its adverse controls remain unchanged.

**MP-C15 — NODD DESIGN CHOICE:** use independent barrel placement controls for
each subsystem, replacing the earlier all-subsystem pattern as the next-study
default. Pixel barrels stagger in phi, with no z staggering by default and a
separate z-staggered option. Short-strip barrels stagger in phi and z, using
tangential modules at different radii by default and a local-tilt alternative.
Long-strip barrels stagger in phi with local module tilt, without z staggering.
All endcaps retain the tested clearance staggering pending engineering review.
The third unnamed barrel bullet is interpreted as long strips; this inference
is recorded explicitly rather than treated as a separate approval.

**MP-C16 — NODD DESIGN CHOICE:** interpret “no tilt section” as no inclined
barrel-end sections in the default, distinct from the explicitly requested
local module tilts. Use the existing cobe nominal layers for that default;
retain pint and its inclined sections as historical alternatives. An optional clarification
was requested and remained unanswered while the study proceeded. This is the
stated working interpretation for human re-review, not inferred sign-off.

All new numeric controls must remain in a separate review-model JSON input,
with placement and clearance rationale. Retain the inherited sensor dimensions,
the mixed single/quad pixel policy, and nominal layers. Assess body intersections,
host containment, hit coverage and silicon area before presenting a placement
as mechanically cleared. No-z staggering means fixed phi/radius along each
stave with nonintersecting consecutive occupied bodies; any remaining inactive
longitudinal seam must be measured rather than hidden by body overlap.

**MP-C17 — NODD DESIGN CHOICE:** show actual x-y barrel sections with the slice
position stated, and x-y tiling of representative endcap layers. Distinguish
active patches, occupied bodies and normal placement levels. The view generator
must use the retained run inputs and be repeatable after shape revisions.

The [executed review-default study](../validation/DES-009-review-default.md)
retains the default, the two independent options, coverage and transverse views.

**MP-C18 — NODD DESIGN CHOICE, end-fit amendment:** a preliminary no-z placement
using the minimum occupied-body pitch and enough rows to exceed both nominal
barrel ends produced 328 long-barrel/first-disc occupied-body intersections.
Retain this rejected control. The default instead fits full rows between the
nominal active-envelope endpoints, using the largest row count whose uniform
pitch is at least the occupied-body extent plus 0.2 mm clearance. This preserves
the barrel/endcap interface without shortening sensors or moving ideal layers;
the wider inactive seams are an explicit cost to measure. For the present long
strips this gives 25 rows at 112.667 mm pitch rather than 26 at 109.121 mm.
Stereo-rotated active corners and body extents still require the complete
three-dimensional checks. This rule applies to all no-z-stagger barrels and is
an explicit parameterized hypothesis, not an approved engineering dimension.

## Coordinates, identifiers and metrics

Lengths in the study are mm, momentum GeV, magnetic field T. A right-handed
local frame `(u,v,n=u×v)` and finite half-widths define each active rectangle.
Pixel readout islands have separate patch IDs but share a sensor ID. Long-strip
faces have separate sensor IDs and share a module ID. Stable IDs are deterministic
within a given input configuration; a changed population may renumber modules.
IDs are not asserted stable across different shape/pitch revisions.

A long-strip complete pair requires both faces of the **same** module. Orphan
faces remain one-dimensional sensor hits. Pint inclined and parent barrel
segments share the existing `station_group` when supplied. Distinct station
counts therefore do not reward redundant surfaces from the same station.

The ideal-layer comparison reports eligible stations along the same trajectory.
Missing eligible stations are coverage losses; extra intersections from finite
module overhang are separately observable. High-|eta| tracks are not penalised
for a subsystem whose nominal layers they never reach. Track fractions refer
to the declared numerical sampling measure, not a physics event distribution.

Straight lines and uniform-field helices stop at the first outer host exit (or
first transverse half-turn for curling inputs). There is no scattering, energy
loss, material, charge sharing, efficiency, digitisation or reconstruction.
Silicon surface is the sum of physical sensor-face areas; long-strip sandwiches
count twice. Active readout area excludes guard regions and pixel seams.

## Validation and review boundaries

1. Unit checks cover transforms, counts, area accounting, shape changes, finite
   boundaries, analytic helices and charge symmetry where applicable.
2. Repeatable angular/luminous samples include boundaries and seeded off-grid
   tracks. Report minima, means, distributions, missing-station fractions and
   subsystem/region breakdowns. A finite scan establishes **sampled** coverage,
   never a proof of continuous hermeticity.
3. Native ACTS sensitive planes and EigenStepper propagation supply an independent
   check of finite intersections, including tilted surfaces, both charges and
   displaced luminous origins. A full Navigator check is also attempted and its
   failures retained. The initial single-large-leaf navigation experiment misses
   bent-track candidates; direct ACTS target-surface propagation is a separate
   intersection audit and does not turn that navigation failure into a pass.
   Record source/install provenance and runtime limitations; ACTS propagation
   is not Geant4 transport.
4. Trial occupied boxes undergo separating-axis overlap checks; host and ideal
   overhang diagnostics are independent of active intersections. This does not
   certify actual support/services clearance. Full DD4hep overlap, material,
   mass and Geant4 tests are excluded because no production solid/material model
   is introduced.
5. Retain code/input hashes, seed, configuration, tool versions, commands and
   tolerances with generated results; a rerun writes a new directory. Public
   summary/report artifacts are selected explicitly for review.

The recommendation must relate measured coverage gains to module count, families,
stagger levels, tilt and clearance. No currency or engineering labour estimate is
available. Human tracker, module and support experts remain unassigned. All
layout choices, physical outlines, electronics qualification and support design
remain open for review before production implementation.
