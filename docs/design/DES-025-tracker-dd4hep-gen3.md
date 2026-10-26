# DES-025 — BeamPipe + Tracker assembly and ACTS Gen3 conversion

- Status: DRAFT
- Date: 2026-10-08
- Scope: explicitly user-authorized integration for software review; no design sign-off.

Assemble DES024 pipe, DES019 trimmed mixed pixel, selected phi-tilted DES020
short-strip barrel, DES021 endcap and DES022/023 paired long strips. Keep all
sensor placements, signed local axes, bounds, disc datums and readout IDs unchanged.
No field or upstream ODD material map is introduced. Existing coverage, guard,
warm thermal, sag/joint and service-capacity qualifications remain limited.

NODD DESIGN CHOICES: one deterministic compact assembled from independently
exported inputs; shared natural elements and Air/Vacuum, otherwise namespaced
materials preserve each source recipe exactly. World half sizes take component
maxima; truth region encloses all sensors. The passive pipe reserves system0;
pixel systems1–3 retain their IDs. Standalone strips systems3–6 translate
losslessly to assembly systems4–7 to avoid the discovered system3 collision;
all other placement fields and all bit layouts are unchanged. Shared service corridors need one
physical carrier and a conserved constituent inventory; duplicated standalone
trunks must be reconciled explicitly and recorded, never silently overlapped.

ACTS Gen3 uses the native DD4hep backend and DD4hep-backed sensitive elements,
not a separately regenerated layout. Group actual sensitive DetElements by
system/layer placement IDs, retaining every pixel chip and both strip faces.
XYZ sensor axes follow local Box coordinates in these factories. ROOT centimetres
convert to ACTS millimetres. Group barrel and signed-z disc layers into radial
subsystem containers with connected Gen3 portals. Navigation envelopes are
software margins, not extra detector material or a physical clearance claim.

The pipe is represented by a thin cylindrical material surface at the wall
mid-radius27.4 mm, thickness0.8 mm, with native Be properties and finite half
length4000 mm. This is the usual tracking approximation to the physical shell;
DD4hep retains both exact wall boundaries. Sensor material can be native silicon;
passive tracker services require a dedicated material mapping campaign, no ODD
map is silently substituted. A correct geometry alone does not qualify material
mapping, alignment, field propagation or reconstruction performance.

Validate native construction, identifiers, per-source sensor centres/axes/bounds,
material preservation, cross-component overlaps, pipe clearance, Geant4 transport,
one ACTS surface per native sensitive element, cylindrical pipe material and
Gen3 navigation through all subsystems. Retain failure evidence and exact source,
input, factory and installed ACTS hashes; enclosing result commits are distinct.

The retained DES023 exporter already describes cumulative barrel+endcap service
loads. Its shared corridor replaces the DES022 standalone barrel trunk; keeping
both would double-count the same barrel payload. Short-strip standalone trunks
share identical radii/azimuths: partition at all source axial boundaries, sum
constituent payload volumes, retain one aluminium carrier, and count unused air
once. These integration ownership choices do not claim that fixed service
packing limits pass. Export fails on inconsistent carrier materials, excess
physical inventory or non-conserved payload. Source models/artifacts stay intact.

## Beam-pipe clearance amendment for review

The first combined audit found pipe/support and pipe/service intersections:
the old passive pixel apertures began at27mm, inside the27.8mm outer wall.
As a NODD DESIGN CHOICE within this user-authorized integration, the combined
compact opens only passive pixel annuli to28.8mm (1mm radial clearance). The
optional clarification was left open while independent software checks and the
explicit candidate were completed; this tested convention is the review proposal.
No maintainer sign-off is inferred. Original standalone producers/pins and their
retained artifacts remain unchanged. All sensor transforms, guard dimensions,
IDs and disc datums remain exact. The outer service radii remain fixed.

For homogenized core/skin plates retain non-filler cooling/spreader inventory
and subtract only foam/CFRP from the enlarged hole. For service cells retain all
non-air conductor, coolant and pipe volumes, remove unused air and renormalize
density/mass fractions to the new cell volume. Pure skins lose only the clipped
annulus. The candidate removes10.1283g across138 passive parts; no silicon loss.
No mechanical stiffness, vacuum support or service-packing pass is inferred.
`--keep-pixel-aperture` retains the unamended historical control, which must fail
clearance validation with the new pipe.

The centralized assembly truth region is r<1200mm, |z|<3600mm, a software
enclosure of all native sensitive nodes (not an acceptance specification).
World bounds use maxima of the standalone envelopes. Current1mm navigation
envelopes and the physical1mm pipe clearance are separate design choices.


## Configurable Gen3 portal material-mapping trial (2026-10-26)

Status: **PROTOTYPE / DRAFT**, explicitly requested by the human in PR100's
local task. These are NODD DESIGN CHOICES for an isolated mapping campaign;
no engineering sign-off or production acceptance is recorded.

Select one physical portal for each native sensitive layer: the outer cylinder
for pixel barrels (material after the sensitive layer), and the inner cylinder
or upstream signed-z disc for all other sensitive layers. Additional carriers
are the beam pipe, inner/outer cylinders at each pixel–short-strip and
short–long-strip gap, two barrel/endcap separator discs per subdetector,
and the outer tracker cylinder plus both outer shell discs. Deduplicate
shared physical portals while retaining all logical roles. The existing
geometry has52 signed sensitive layers; this literal scheme is expected to
have about65 unique carriers, rather than forcing the approximate50 target
by dropping layers. The selection manifest records the actual count.

All counts are configurable. Initial phi bins=1. The other axis is z for
cylinders and r for discs:

| Carrier | z/r bins |
| --- | ---: |
| Pixel barrel; short-strip barrel | 250 |
| Long-strip barrel | 100 |
| Beam pipe; full gap cylinders | 500 |
| Pixel endcap; pixel barrel/endcap separators | 50 |
| Short-strip endcap; short-strip barrel/endcap separators | 100 |
| Long-strip endcap; long-strip barrel/endcap separators | 50 |
| Full outer shell discs | 250 |
| Full outer shell cylinder | 500 (explicit full-cylinder default) |

The side selection above specifies carrier placement relative to the native
sensitive layer. Use the pinned ACTS mapping/validation algorithms and disclose
their actual material-assignment rule. The current upstream assignment code
uses closest intersected surfaces; a MappingType field alone does not impose
strict per-step before/after assignment.

Map the complete recorded material inventory, including silicon and the pipe,
onto these selected portals. Clear existing native material slabs in the
mapping/validation geometry before assigning ProtoSurfaceMaterial or loading
the map, so no sensor or pipe material is counted twice. DD4hep solids, physical
materials and sensor transforms remain unchanged. Keep the native-slab survey
geometry as a separate control. No ODD material map is introduced.

Read the existing100k recording, run native mapping, serialize/reload the map,
then run validation with an explicit independent random seed and the same
eta/phi support. Overlay the validation total X0/lambdaI profile on the existing
Geant4 component stack. Retain empty bins, missed surfaces, unmapped material,
profile differences and all source/input/runtime identities. A visually close
curve is not a material-order, tracking-performance or design acceptance claim.


The native outer pixel-barrel cylinder is a merged full-length portal shared
with the inner pixel–short-strip gap cylinder. It requests250 z bins as a layer
and500 as a full gap. The configurable `maximum_requested` shared-portal policy
uses500 on this one physical portal and retains both requested roles in the
manifest;an `error` policy or explicit per-portal override is also available.
Current selection is66 logical roles on65 physical portals (15 cylinders,
50 discs),8550 nominal bins. No duplicate material map is installed on the
shared boundary. Native shell choice is the existing World exterior:its
outer cylinder and two end discs;the separator discs are the native barrel-end
portals. These exact choices and counts are an implementation of this trial,
not a new physical envelope.

## Cumulative material diagnostic requested in PR100 expert review

The [2026-10-26 expert comment](https://github.com/asalzburger/nodd/pull/100#issuecomment-6415806657)
requests mean accumulated X₀/λI versus barrel radius, forward |z| and flight
distance d=√(r²+z²), comparing the existing Geant4 recording with ACTS validation.
This is a diagnostic of the isolated prototype, with no detector change.

NODD DESIGN CHOICES for display: |η| intervals of width 0.5 over 0…4.5;
radius for |η|<0.5, |z| for |η|≥1.5, and d for every interval. Sampling grids
initially extend to 1200/4200/4500 mm with 2/5/5 mm spacing respectively;
all choices are configurable and carry no accuracy acceptance criterion.

For origin straight rays, integrate the recorded Geant4 step budget uniformly
between its physical pre/post coordinates, clipping partial steps at each
coordinate threshold. Keep mapped validation material as a thin interaction
at its recorded portal position. Compute cumulative values per ray first,
then the slice mean and population SEM over every ray, including zeros.
Preserve material totals at the final threshold; show separate sample counts
and source hashes. Finite checkpoint spacing limits the displayed localization.
These curves diagnose longitudinal/radial shifts and do not establish material
order relative to every sensor, curved-track performance or design acceptance.

## Initial truth-tracking performance baseline (2026-10-26)

Governing work item: [issue #102](https://github.com/asalzburger/nodd/issues/102);
implementation and evidence: [PR #101](https://github.com/asalzburger/nodd/pull/101).

Status: **PROTOTYPE / DRAFT**. The human requested an ACTS truth-tracking
baseline for both Geant4 and Fatras, using the Gen3 geometry and the material
map merged in PR100, with single muons at fixed transverse momenta 1, 10 and
100 GeV. This is a characterization campaign, without design acceptance or
a production detector change. Here the requested ODD baseline denotes this
PR100 Gen3 nODD tracker; an untouched upstream ODD geometry has incompatible
surface identities and must not receive this map.

FACT: PR100 supplies the retained 65-portal material map and exact manifest.
Reapply it through the same native keyed-surface controls, clearing original
silicon/pipe tracking slabs to avoid double counting. Geant4 transports through
the unchanged detailed DD4hep physical material; Fatras and the track fit use
the mapped ACTS material. Record both physical and tracking geometry identities.
The material-map locality/one-phi-bin qualifications remain applicable.

NODD DESIGN CHOICES for the first campaign, centralized and configurable:
20,000 one-particle events per backend/momentum; uniform eta over [-4,4], full
azimuth, origin vertex, randomized muon charge, deterministic recorded seeds.
Start with a small pilot for each backend. The human selected a constant 3 T
field for an ideal-field nODD baseline on 2026-10-26. This fixture replaces the
2 T initial suggestion from the ACTS full_chain_odd.py example; it is not
the finite DES-026 solenoid or an installed field-map claim. Record the actual
selected field identically in simulation and fit. No pileup, misalignment,
dead-channel or radiation-damage model is introduced.

Geometric digitization uses the human-requested 50 micrometre by 50 micrometre
pixel cells. FACT: DES007 C01 selects 75 micrometre by 0.5 mm two-coordinate
short-strip cells. FACT: DES008 C05 and measurement contract select 80 micrometre
single-coordinate long-strip measurements on each actual sensor face. The
native paired-sensor rotations provide stereo; do not add a synthetic second
coordinate or apply a second stereo rotation. Use geometric charge deposition,
segmentation and clustering through ACTS, rather than replacing this request
with a Gaussian position-smearing digitizer. Inspect local sensor-axis mapping
and actual sensitive IDs before constructing per-surface digitization entries.
NODD DESIGN CHOICE: use native digital cell-centre clustering, exact path-length
charge, zero threshold, and no added drift/diffusion. Before the human requested
error training, pilots used the native pitch-squared/12 covariance. For the
performance baseline train a common empirical hit-error table with an independent
50,000-event Fatras sample, log-uniform pT from 1 to 100 GeV and seed 142042,
using the same eta/phi, geometry, segmentation and field. Use the pinned ACTS
Digitization/error_parameterisation.py script (SRC-ACTS-TRUTH-TRACKING-355EA684
in [the source catalogue](../../reference/manifest.yaml)), retain its raw result, and audit
cluster-size groups and overflow handling against the measurement residuals.
Apply one frozen table to both validation backends; training events must not
contribute to reported performance. Any upstream table correction needs exact
source/error evidence and a task-local implementation, with raw evidence kept.
This idealized binary response does not emulate calibrated RD53 electronics.

Use the ACTS truth-associated Kalman tracking route corresponding to
truth_tracking_kalman.py: a truth initial trajectory with finite, explicitly
recorded covariance, truth measurement association and a native Kalman fit.
No pattern-recognition or CKF efficiency claim follows. Retain primary-muon
identities, generated denominators, measurement multiplicity, attempted fits,
failed fits and covariance failures. A minimum measurement requirement may
match the example's seven measurements but must be explicit and its losses
shown; no cut at nominal 1 GeV may silently remove rounded 1 GeV particles.

Characterize perigee d0, z0, wrapped phi, theta and q/p residuals and pulls,
and relative transverse-momentum residual. Means, full RMS and central
68.27-percent half-widths distinguish bias, tails and core width. Pulls divide
by the fitted marginal standard deviation; invalid/non-positive covariance is
counted separately. Any derived pT pull uses the full theta/qOverP covariance,
including its cross term. Show signed-eta profiles separately for each momentum
and backend, and the three momentum points in explicit eta slices. Retain
counts and uncertainty method; empty or undersampled bins are missing evidence,
not zero resolution. Do not tune or truncate residual tails to obtain unit pulls.

Keep the full native outputs outside Git, with hashes and replayable retained
summary data/figures. Meaningful analytic controls and an independent PhysVal
assessment must check the fixed source/evidence revision before interpretation.

The human authorized long-strip smearing as a temporary fallback if native 1D
geometric digitization is unavailable. Corrected native pilots demonstrate 1D
measurements with a second physical segmentation axis containing one full-length
bin; only loc0 is measured. Thus the geometric implementation remains applicable
and no smearing fallback is selected at this point.

The pinned ACTS TruthTrackFinder uses a second measurement-map lookup on an
already resolved sim-hit index. Geant4 can create several hits per measurement,
so these index spaces differ and the pilot exposes missing-hit warnings. The
isolated task-local adapter may replace that lookup with the direct sim-hit
index, retaining native truth association, hit-time sorting and the unchanged
Kalman fitter. Preserve source locators, original/corrected counts and a
non-identity-map control. No shared ACTS source or installed library is changed.

A merged Geant4 cluster can also have repeated primary-to-measurement map
entries, one per contributing sim-hit. The isolated truth adapter must use
each physical measurement once per primary before sorting by hit time; retain
original/unique counts and duplicate controls. This preserves truth association
without pattern recognition or repeated counting of the same measurement.

Pinned ModuleClusters::squash recomputes geometric cluster variances from
cell weights and widths, discarding earlier GeometricConfig variance-map values
when merging. Therefore applying the trained table requires an isolated
post-clustering adapter: preserve measurement IDs, positions and associations,
and set measured-coordinate variances from the frozen per-volume cluster-size
RMS table (square RMS, clamp overflow to final entry). The table describes
independent marginal errors and carries no coordinate correlation. Validate
actual output covariance against the table before fitting. No shared ACTS
source, transport, clustering positions or Kalman fitter is modified.

For this large detailed geometry, the pinned ACTS Geant4 helper calls BeamOn(1)
for every ACTS event and repeatedly constructs material-cut couples. An isolated
run-manager adapter may hold one ordinary Geant4 run open across the case:
initialize physics/run/event-loop once, then call standard ProcessOneEvent and
TerminateOneEvent once per independent ACTS event, retaining per-event RNG
seeding, hit collection and native event-store reset, and terminate the run at
closeout. Do not combine muons into one Geant4 event. The FTFP_BERT model, cuts,
physical geometry and stepping are unchanged. Require an explicit small-sample
comparison against the standard lifecycle (particles, hit identities/positions/
energy and event counts) before production. Record any mismatch rather than
assuming equivalence; no unvalidated lifecycle result is baseline evidence.

Deduplicate primary/measurement association pairs before native particle
selection and truth matching as well as proto-track construction: the seven-hit
requirement counts unique physical measurements, not repeated contributions from
Geant4 steps. Preserve the complete measurement-to-simhit map for truth position
averages. Only the measurement-to-particle map and its inverse lose duplicate
pairs; IDs, truth labels, measurement values and hit contributions stay intact.

The original faulty TruthTrackFinder must not run as a reference algorithm in
production: the first campaign exposed invalid double-index pointers during
sorting and two Geant4 cases terminated. Preserve those incomplete outputs as
excluded controls. Construct the same native ParticleTrackParamExtractor and
TrackParameterSmearing seed stages directly, then the corrected unique proto
finder and unchanged Kalman fitter. No transport, digitizer, error table, seed
configuration or fit settings change. Repeat all six performance cases at one
fixed source revision; earlier completed cases remain historical controls.

The default native Kalman writer uses double truth matching, including at least
half of the primary's total measurements. Three final single-candidate fits fall
below that completeness condition and have zero-barcode/NaN native truth fields.
For this truth-associated characterization, retain them using the unique input
primary/proto-track identity, explicitly counting native-unmatched fits and their
event IDs. Require exactly one generated primary, matching selected-particle
barcode, one attempted candidate and at most one fitted track (index0). A valid
nonzero mismatching barcode is an error, not an inferred association. Verify
writer truth on native-matched tracks; compute every residual from independently
joined generated truth. This preserves poor/partial fits rather than removing
tails through the native completeness match. Matching efficiency remains a
separate diagnostic and no pattern-recognition claim follows.

### Full pull distributions requested on 2026-10-26

The human requests all-eta distributions with1/10/100GeV overlaid per track
parameter, using (truth−reconstructed)/fitted sigma. Preserve the earlier
profile sign convention and label the new sign explicitly. Include all six
bound parameters d0,z0,phi,theta,q/p,time; time has no measured response here
and must be labeled an unconstrained seed/fitter-prior diagnostic. Include
derived pT separately with the full theta–q/p covariance. Use the same guarded
primary-derived cohort, including the three nativeFake partialfits. No quality
or tail cuts. Count missing fits/nonfinite pulls separately.

NODD DESIGN CHOICES for configurable display binning: common edges across all
six samples per quantity,0.1-wide bins inside±5 and16logarithmic bins/decade
outside, extended to encompass every finite observed pull. Normalize density
by all finite pulls and bin width; require zero full-range under/overflow and
exact count closure. Full views use a symmetric-log pull axis and logarithmic
density, with a companion±5 view reporting its omitted-tail fraction. Store
all bin counts, extrema, moments and tail counts; no finite tail disappears
from the full view or normalization. Assess fixed-source/data/figures
independently before final interpretation; no native rerun or calibration.
