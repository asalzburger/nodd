# Calibration and gap-staggering options

Status: **PROTOTYPE recommendations**, 2026-11-12. No calibration has been fitted
and no geometry change or performance improvement is claimed. Inputs are
DES-030/DES-031 and the completed [matched-input control](README.md), inspected
at `951d7b286c47882dc8068056e59d39abac1f31a4`. The user asks for potential
calibration and layout approaches, rather than another transport run.

## What the control establishes

**FACT — executed evidence:** continuous silicon substantially narrows the raw
response distributions, while changing their means and filling guards, module
gaps and service regions together. It also adds silicon and removes intersecting
aluminium. This does not isolate a single mechanical contribution or establish
an attainable calibrated resolution. Exact zero responses change from 42 to 37.

**FACT — current prototype:** barrel slab phases are −96/+96 mm, with 96 mm
board pitch (90 mm wafer + two 2 mm PCB margins + 2 mm board gap). The active
wafer width is 88 mm. Endcap mask layouts repeat through all 48 layers.
Source: `barrel.json`, `barrel_layout.py::panel_layout/build`,
`edge_layout.py::pack/build`, DES-030/031.

**INFERENCE:** the barrel slab phases differ by two board pitches. They stagger
slab/service joints but preserve corresponding full-slab interior lattice phase.
Their benefit does not establish that narrow inter-board gaps are decorrelated.
The nominal active gap is 96 − 88 = 8 mm, distinct from wider service regions.

## Suggested calibration: reconstruct local response variations

**NODD DESIGN CHOICE — proposed test only:** start with a smooth, low-parameter
position correction fitted on tiled-geometry training events:

`E_corr = S / f_hat(q)`, where `S = sum(raw silicon deposits)` and
`f_hat(q) = mean_training(S/E_true | q)`.

Begin with barrel/endcap identity, reconstructed impact position and distances
to sensor/module edges, slab service bays and sector boundaries. Pool equivalent
geometry where justified, retaining proper signed-end local transforms. Project
the shower axis through the actual layer masks; an exposure variable should
account for shower footprint and longitudinal weighting, rather than just the
number of central-ray silicon crossings.

For this ECAL-only run, a map using true impact coordinates is an **oracle
diagnostic** until repeated with a calorimeter-reconstructed centroid/axis.
Future tracking can supply an independent impact estimate. True energy supplies
training labels and validation denominators; it must not be an inference input.
Use an independent event-ID holdout or out-of-fold predictions. Add measured
longitudinal energy fractions/lateral width, then an energy proxy only if
energy-sliced closure requires it. Check sensitivity to the training spectrum.

Ten thousand electrons support a first coarse demonstration, not an unrestricted
eta × phi × module × depth × energy lookup table. Use parameter sharing and
regularisation, with fit complexity selected outside the final test sample.
Channel/MIP gain equalisation is a separate future step once electronics and
digitisation enter the observable; these raw deposits already bypass that chain.

**INFERENCE — exact scaling identity:** multiplying every response in a displayed
angular bin by one positive constant leaves its own `SD(R)/mean(R)` unchanged.
The correction needs finer, event-dependent information to reduce within-bin
variation. It can remove predictable mean response variation; it cannot restore
the actual unobserved shower fluctuation. A finite multiplicative correction
also leaves a zero signal at zero. Report uncertainty/inefficiency for such
events rather than hiding them with response cuts or unconstrained inverse gains.

**FACT — public precedent:** CALICE used shower-barycentre response maps and
reciprocal corrections, while noting residual individual gap fluctuations.
Its quoted intrinsic-resolution study used a gap-excluded fiducial selection.
This supports the method, without transferring that detector's achieved numbers
to nODD. [SRC-CALICE-SIW-ELECTRONS-2008, section 5.2, equations 3–4 and
figures 4–7, PDF pages 7–10](https://arxiv.org/pdf/0811.2354).

## Suggested layout: independent board phases through depth

**NODD DESIGN CHOICE — illustrative scan:** retain the existing slab-joint
stagger and introduce independent board-grid phases. Half the inherited pitch
is 48 mm. A useful four-layer starting pattern, in local tangential/axial
coordinates, is:

| Layer modulo four | Tangential phase [mm] | Axial phase [mm] |
| --- | ---: | ---: |
| 0 | 0 | 0 |
| 1 | 48 | 0 |
| 2 | 0 | 48 |
| 3 | 48 | 48 |

These are proposed test phases, not approved construction parameters or an
optimised pattern. Their aim is to place active silicon behind a preceding gap.

For full barrel slabs, apply the axial half-phase away from the service bay on
the half-phased layers. The current nine-row centres span −384..384 mm; moving
them 48 mm away from a positive-end bay gives PCB extent −479..383 mm inside
the ±495 mm cavity. This source-level packing example retains nine boards;
short end slabs need separate repacking. All physical films, PCB, ASIC/thermal
parts and identifiers must follow their modules and pass native validation.

Tangential half-phase translation is not a drop-in change: current PCB side
clearance reaches about 1.44 mm, so edge-board families, column counts or service
allocations must change. Use physically defined partial sensors/PCBs with guards
and electronics, rather than clipping a standard active sensor computationally.
Recompute active area, material, channels, power and cooling demand.

For endcaps, generate complementary layer-dependent radial/tangential packing
and edge-mask families instead of repeating one layout at every depth. Preserve
the aperture and service allocations and repeat all mask/electrode/identifier,
ASIC-placement, clearance and overlap checks.

Full-depth carrier cracks remain a separate problem. Internal board phases do
not move sector rails or absorber boundaries. A stepped/nonprojective joint,
or independently supported radial sub-stacks with offset joints, is a larger
interface proposal requiring new mothers, support and service-routing assessment.
No relative rotation inside the existing full-depth wedge mothers is assumed
valid. The present control remains inside the existing ECAL carrier envelopes;
it does not validate tracker/HCAL interfaces or a full-detector redesign.

## Recommended next comparison

First evaluate held-out calibration on the existing tiled sample. Separately
screen real staggered-module candidates using dense impact maps of minimum
shower-weighted coverage, missing-layer streaks, seams and transitions. Preserve
absorber/silicon/material budgets wherever possible and document every change.
Geometric coverage is a screening tool, not a predicted energy resolution.

Then compare baseline/raw, baseline/calibrated, staggered/raw and
staggered/calibrated on matching test inputs and event-ID splits. Fit each
geometry's calibration on its own training set. Retain the continuous control
as a separate diagnostic reference. Measure energy-scale closure in narrow
true-energy slices, inclusive width, central quantile width, low-side tails,
zero/failed-reconstruction fractions and uncertainty. Keep every generated
event in the stated denominators; conditional positive-signal plots may only
supplement the inclusive result.

For uncertainty, resample raw/corrected versions of each held-out event together.
Propagate training uncertainty separately, or refit the calibration inside an
outer bootstrap; fixed fitted parameters alone omit that contribution.

Separate read-only CaloTech and PhysVal inputs are recorded in the
[session journal](../../../logs/codex/SESSION-2026-11-12-ecal-calibration-layout-options.md).
These suggestions require implementation and validation before a performance
claim; they grant no design or engineering sign-off.
