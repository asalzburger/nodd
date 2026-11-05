# nODD tiled-endcap raw electron response protocol

- Status: **PROTOTYPE characterization protocol; no detector acceptance**
- Date: 2026-11-06
- Assignment: I118-Response-CaloTech
- Scientific source revision: `ad5c45293a306864c8ec34332df9bfab0a553e53`
- Governing design: [DES-030](../../design/DES-030-ecal-edge-sensors.md)
- Context: [issue117 report](README.md), [response validation boundaries](validation-plan.md)
- Authorization: current user direction to scan raw Geant4 electrons in the nODD tiled endcap against an idealized continuous-silicon control. Marlin study remains deferred.
- Technical / scientific human acceptance: pending

## Question and frozen hypotheses

Measure the spatial dependence of **raw sensitive-silicon deposited energy**
in the current 112-sensor/wedge DES030 endcap, and compare it with a continuous
sensitive-silicon plane in the same retained absorber/hardware stack. This is an
isolated transport experiment. It does not measure reconstructed resolution,
digitization, shower clustering, full-detector performance or HL-LHC pileup.
An ODD-versus-nODD comparison changes too many ingredients to isolate this question.

**FACT — inspected source:** `edge_layout.py::build/pack` supplies 76 square plus
36 custom sensors per wedge/layer; `edge_export.py::hardware/export` supplies all
48 layers, 16 sectors, local material and supported wedge frames. Use the current
PR115-derived source/inventory, identified by the full scientific revision above
and exact hashes in the executed fixture manifest. The earlier three-layer,
one-wedge muon display is not the geometry of this response scan.

**NODD DESIGN CHOICE — study hypotheses:** tile centres, guards/gaps/corners,
custom edges and mechanical seams may have different visible-silicon response.
A shower spreads across neighboring sensors and changes its radial impact through
depth, so geometrical primary-crossing fractions alone cannot predict that response.
The continuous control tests an idealized upper-coverage plane while retaining
wedge support/seam losses. Its response need not be spatially uniform.

## The two geometry cases

Both cases retain **side 1 (+z), all 16 sectors and all 48 layers**, the complete
local absorber, skins, sensor films, glue/pads, PCBs, ASIC/material stacks, common
cooling and supported frame/back cover. The opposite endcap and the other detector
subsystems are absent. World material, field, transport physics/cuts, gun and
sensitive-hit collection settings are identical between cases. This is the
isolated factory's system 8, not the LAYOUT-001 remapped root ID.

The tiled case uses the unchanged `nODDEcalEdgePrototype` and current masks,
electrode mapping and guard sensitivity. Do not edit that factory or production
geometry to create the control.

**NODD DESIGN CHOICE — continuous control:** in a separately named task-owned
fixture/factory, remove every original silicon `sensitive` and `sensor_edge`
primitive from each layer; replace their union with **one 0.5 mm sensitive Si
sheet per wedge/layer**, centered at the same layer-local depth, 2.5 mm. Its exact
transverse polygon is `expected.layout_report.carrier_face_mm`, not the full
absorber plate and not the full mechanical carrier:

```text
x_inner = 100 + 30 = 130 mm
x_outer = 2223.2 - 5 - 120 = 2098.2 mm
t = tan(pi/16)
|y| <= x*t - 6 mm
vertices (mm):
(130,   -19.858607759355536)
(2098.2,-411.3579292359983)
(2098.2, 411.3579292359983)
(130,    19.858607759355536)
```

These numbers are **INFERENCES** from the pinned unsigned geometry choices:
`edge_layout.pack()` uses inner support, outer support/service bay and the
1 mm half-seam plus 5 mm side reserve. The board-envelope polygon remains inside
the full plate polygon subtracted from the supported frame. Keep that frame,
the service bay and physical wedge gaps unchanged.

**Source-based nonoverlap check:** `cassettes.json` and `edge_export.hardware()`
place the sheet at local z = 1.9 + 0.6 mm, spanning [2.25,2.75] mm. The front
skin ends at 2.1 mm, bias Cu ends at 2.218 mm, original glue begins at 2.75 mm,
and PCB begins at 2.83 mm. Retaining these films/hardware does not cause a
positive-volume z overlap with the proposed sheet; the original same-depth
active/guard Si must be removed. Native construction/containment and overlap
checks are still required before bulk transport; this arithmetic is not their
replacement.

Use a control readout able to cover this whole sheet. The original EdgeGrid
active-mask check cannot simply be applied to previously inactive space, and
its module-local signed six-bit pad coordinates cannot encode a 2 m-wide sheet
at the original pitch. Preserve side/sector/layer identity and verify sufficient
coordinate capacity or use an explicitly documented coarse scoring segmentation.
No cross-case per-pad correspondence is needed for summed raw energy.

**Intentional confound:** the continuous case adds silicon where intersensor
space was air and makes previous guard silicon sensitive. It changes both
material transport and energy scoring, while original module electronics/films
remain spatially nonuniform. The result is an **idealized continuous-plane versus
real tiled-layout comparison**, not a pure rebinning or an isolated electronic
segmentation effect. Report the added Si volume/mass and active area separately.
A guard-only or material-preserving scoring control would be a further study.

## Beam and frozen spatial grid

**NODD DESIGN CHOICE — illumination:** monoenergetic `e-` from (0,0,0), zero
magnetic field, one primary/event. Use the same physics list (initial choice
FTFP_BERT), production/range cuts and hit thresholds in both cases, recording
all effective settings. Normalize by the generated primary energy verified from
truth; state whether the gun request denotes kinetic or total energy. No
Marlin/digitizer, smearing, noise, gain or threshold model is added.

Coordinates below are in sector-0 radial-x/tangential-y axes, which coincide with
world x/y for the positive-end sector-0 placement. Define all targets on the
**first sensitive-plane center at z = 3952.5 mm**, not on the front absorber face.
A point (x,y) means the fixed gun direction `(x,y,3952.5)/norm`; do not aim at a
pad reference instead of that physical point. Record θ=atan2(hypot(x,y),3952.5),
φ=atan2(y,x) and η=asinh(3952.5/hypot(x,y)) in the run manifest. No beam spot or
random angular spread is used in this first point scan.

The main radius is approximately 1.14 m, safely separated from the 130 mm inner
supported rim and 2098.2 mm board-envelope outer boundary. The centre point has
η≈1.95663. The unscattered ray's radial x moves from 1139 mm at layer 0 to
1286.63054 mm at layer 47 (147.63054 mm increase). Thus point labels describe
**first-plane impact only**; they do not promise a centre/edge trajectory in every
layer. This natural IP incidence is held identical between geometries and is
part of the response question. Do not keep a ray artificially at fixed x/y
through the stack.

| Point ID | First-plane (x,y), mm | Definition / physical question |
| --- | --- | --- |
| C | (1139,48) | Centre of square module 115 |
| E-in | (1139,4.5) | 0.5 mm inside its lower active edge |
| E-boundary | (1139,4) | Exact lower active boundary; explicitly retain as a boundary/numerical diagnostic |
| E-guard | (1139,3.5) | 0.5 mm outside active edge, within silicon guard |
| G | (1139,0) | Midpoint of the central tangential gap between square modules 114 and 115 |
| K-in | (1095.5,4.5) | 0.5 mm inside both lower-left active boundaries of module 115 |
| K-gap | (1091,0) | Midpoint of radial/tangential intersensor-gap crossing near that corner |
| U | (1139,206.74141090233807) | Midpoint of custom module 117 active cross-section at x=1139 |
| U-in | (1139,216) | Inside its sloped upper active edge |
| U-out | (1139,217) | Outside that active edge, in the custom sensor guard |
| S-minus | (1139,224.56118644543045) | 2 mm below mechanical sector seam, in common support strip |
| S | (1139,226.56118644543045) | Exact sector-0/sector-1 seam direction |
| S-plus | (1139,228.56118644543045) | 2 mm beyond seam, testing the neighboring sector support |

**INFERENCE — exact boundaries:** module 115 has active x=[1095,1183],
y=[4,92] mm. At x=1139, module 117 has active y=[197,216.48282180467614]
mm, obtained from its exported sloped polygon. The board-envelope upper edge
is y=220.56118644543045 mm, and the physical sector bisector is
1139 tan(pi/16)=226.56118644543045 mm. These definitions use physical mask
polygons, not logical pixel boundaries. Verify each classification against the
exported inventory in fixture preparation and fail if a future source update
changes it. Exact-boundary points must not drive a claim without their neighboring
finite offsets and the applicable geometry tolerance.

## Execution stages and statistics

1. Run the authorized **20-event, 20 GeV tiled pilot at C** (a prior module-27
   centre at (371,0) is also a valid software smoke pilot if already executed).
   Verify primary generation, all-event accounting, full intended geometry,
   positive saved energy, parent IDs and longitudinal activity. A pilot is not
   response validation and its events are excluded from bulk estimates.
2. After source/fixture and pilot checks pass, freeze the actual implementation
   revision/hash and bulk manifest. Generate an **independent 100-event
   continuous-C sample at 20 GeV**, with a disjoint recorded seed. Exclude these
   events from every bulk response estimate. Freeze one dimensionless tail cut
   `f_cut = 0.8 * mean(f_visible)` from this calibration sample before analyzing
   the bulk results; use this same cut for all energies, points and geometries.
3. Run **200 events per point, per case at
   20 GeV**, all 13 points: 5,200 events. Give every case/energy/point a disjoint,
   recorded RNG seed. Equal seed integers alone do not make shower histories
   paired after materials diverge. Use independent samples for the quoted
   cross-case errors unless actual covariance is retained and justified.
4. Run **5 and 50 GeV at C, G and S**, 200 events per point/case: 2,400 events.
   The first campaign is 7,600 bulk shower events, plus the separate 100-event
   calibration and 20-event software pilot. Keep energy/position/species
   populations separate and retain their denominators.
5. Report uncertainty from the actual distributions. For an approximately Gaussian
   width, 200 events suggest about 5% relative statistical width error, but shower
   tails invalidate using this estimate as the final error. If a stated tail has
   too few events, report its interval/upper bound; expand to 1,000 events for
   relevant points with independent seeds only when needed for the claimed
   comparison. Retain the initial sample and document the extension rule; never
   select a favorable subset or move the coordinates after inspecting results.

## Observables and retained evidence

For every generated event, sum all saved positive Si deposited energies over
**all 16 sectors and all 48 layers**, including energy that spreads outside the
incident wedge. No hit, cell or event-energy threshold is applied in analysis.
Count complete zero-hit events as zero; reject incomplete/missing events rather
than silently dropping them. Verify exactly the requested number of events and
one intended primary/event. Record intrinsic simulation collection/transport cuts.

For each case/energy/point retain and plot:

- `f_visible = E_Si/E_generated`: event mean with standard error `s/sqrt(N)`;
  distributions with explicit units/edges/underflow/overflow and all-event counts.
  This is not the physical active/(active+passive) sampling fraction because
  passive deposition is not scored here.
- Raw distribution sample RMS/mean, with bootstrap standard error over whole
  generated events, including zero response. Retain bootstrap quantiles and
  resampling seed. A fourth-moment delta-method error is an optional cross-check,
  not the primary reported uncertainty. Report the RMS and mean separately. Label this
  **raw visible-response spread**, not calibrated/reconstructed energy resolution.
  For highly non-Gaussian/zero-heavy points display quantiles and zero fraction too.
- Tiled/control mean ratio at each matched point, with the uncertainty of both
  independent samples. An energy-independent calibration is not introduced by
  normalizing this ratio. Report mean ratios even where width comparisons are weak.
  If a mean is zero, retain its zero response and event denominator: RMS/mean
  is undefined for that population, and a tiled/control ratio is undefined when
  the control mean is zero. Store these undefined values as `null`, never as
  zero or infinity. Record the count of bootstrap replicates with undefined
  ratios/relative widths; do not silently drop them. Mark unconditional width
  uncertainty undefined if such replicates prevent its definition, or explicitly
  label any conditional summary. This is particularly relevant to exact seam S,
  where the physical gap remains in both geometry cases.
- A common low-response tail: use `f_visible < f_cut`, where `f_cut` is fixed
  by the separate 100-event continuous-C 20 GeV calibration, for **both cases,
  all energies and every point**. The factor 0.8 is an explicit study choice, not
  an accepted detector requirement. Do not recalibrate by energy or point. Show
  the numerical cut, numerator/denominator and conditional 95% Wilson interval
  with this cut held fixed. Also bootstrap the independent calibration sample
  and each response population, reusing the same resampled reference cut across
  all populations in each replicate, so the reference uncertainty and induced
  correlation remain explicit. Retain that evidence where feasible; if missing,
  label intervals as conditional and state the missing reference uncertainty.
  This cut defines a common visible-fraction diagnostic, not a detector energy
  calibration or an expected energy-invariant response.
- Per-layer mean `E_Si(layer)/E_generated` with standard errors over all events;
  their sum must reproduce the total mean. Record the per-event longitudinal
  covariance or required summed statistics when interpreting layer differences.
  Late-layer deposited energy is a shower-development/containment diagnostic,
  not a measured escaping-energy leakage fraction.

Use fixed distribution bins for each energy across cases and points. Save counts,
normalization, moments through fourth order and bootstrap summaries/seed, enough
for inspecting means/spreads and replotting; retain cross-sample covariance only
where it actually exists. Bootstrap replicates operate on local full-event data;
a stored histogram alone does not reproduce arbitrary event correlations.

Keep full EDM4hep/ROOT samples, detailed logs and generated bulk geometry local
and ignored. Commit only plots, compact binwise/sufficient-statistic summaries
and the reproduction recipe, per [ADR-003](../../decisions/ADR-003-validation-and-artifact-policy.md).
The executed report must provide exact source/config/compact/material/library
hashes, environment versions, commands, seeds, primary definitions, cuts,
requested/read event counts and check exit codes. Do not replace missing evidence
with a geometry pass or a sparse display sample.

## Required interpretation and next boundaries

The comparison can characterize spatial response and stochastic raw shower spread
for this isolated, unsigned prototype. It cannot uniquely decompose guard scoring,
added-Si material, physical gaps and retained nonuniform electronics; cannot
transfer ODD/CALICE test-beam calibration; and cannot establish full-detector
acceptance, jets/MET, pileup/radiation response or reconstructed resolution.
No absorber/material dimension is retuned to flatten the result. Any unexpected
energy/ID behavior, overlap or source/fixture mismatch is investigated before
bulk generation or physics interpretation. Human design sign-off remains pending.
