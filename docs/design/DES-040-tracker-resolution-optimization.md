# DES-040 — Tracker resolution optimisation within fixed envelopes

Status: **DRAFT / isolated PROTOTYPE**. Date: 2026-10-27.
Governing issue: [#103](https://github.com/asalzburger/nodd/issues/103). Coordinator: Codex; engineering approval open.

The human task authorises a constrained optimisation study following merged
PR #101 (`04b5ee2e408803eac836eee0b48a1635dcbbe201`). It does not sign off a new
production layout. Candidate compacts, reconstruction and material files stay
under a separate study directory; the DES-025 assembly remains the reference.

## Scope and physical motivation

**NODD DESIGN CHOICE (human constraint):** vary barrel radii and endcap disk
longitudinal positions, preserving subsystem envelopes, module types and local
stave structures. Stave counts may change. One additional pixel disk per end is
allowed, with an effective homogeneous material disk behind it. Preserve or
increase hit coverage, targeting at least ten physical measurements across
`-4 <= eta <= 4`. Improve d0 and z0 resolution while preserving or improving
momentum resolution. All candidates are proposals requiring human review.

**FACT (repository reference):** PR #101's campaign uses origin single muons,
random charge, full phi, pT 1/10/100 GeV and constant 3 T. Pixel digitisation
is 50 x 50 micrometres; short strips use 75 micrometres x 0.5 mm and long strips
measure one coordinate per physical face with 80 micrometre pitch. Locators:
`software/analysis/truth_tracking/campaign.json`, `digitization.py`, and
`docs/validation/truth-tracking-baseline/`. Native Fatras and the corrected
unique-hit truth finder/Kalman chain remain the performance experiment.

**INFERENCE (physical rationale):** shortening the distance to the first barrel
measurement can improve impact-parameter extrapolation, subject to beam-pipe,
stave body and neighbour clearances. Keeping outer lever arms is a conservative
starting point for momentum resolution. At eta=4 a sensor at radius 31 mm
requires z approximately 846 mm (`z=r*sinh(eta)`); an added early disk alone
cannot make all existing disks contribute at that angle. Forward schedules must
therefore be screened alongside the extra disk. This straight-ray calculation
is a feasibility screen, not a Fatras resolution prediction.

## Frozen physical interfaces and candidate family

**FACT (current compact, not the ACTS world box):** physical beam-pipe radii are
27.0--27.8 mm, with the passive pixel aperture at 28.8 mm. Pixel barrel nominal
radii are 34/60/106/182 mm with 12/22/18/30 alternating-radius staves. Existing
pixel disk datums are |z|=615/795/1046/1333/1645/1977/2328/2692/3070 mm.
Evidence is the source-hash-matched DES-025 compact and specialist assessments
recorded in the task journal. The reconstruction truth region and navigation
margins are not mechanical envelopes.

**NODD DESIGN CHOICE (screening family):** start with the existing layout as a
control; move the first pixel barrel nominal radius to 32 or 31.5 mm while
preserving its alternating offsets and count; examine an additional disk near
900--1000 mm; compare a schedule that moves early disks beyond the eta=4 inner
aperture threshold. Outer barrel lever arms are initially fixed. These are
screening coordinates, not an asserted optimum. Further radius/z/count trials
must be recorded before their results are used to select a candidate.

Preserve all local module/slab/pipe/foot dimensions and orientations. Translate
complete repeated assemblies, not just sensor centres. Retain fixed cage,
transport trunk and handoff envelopes; move layer-associated local structures
consistently where required. Reject a trial that exceeds the baseline physical
allocation, collides with the pipe or adjacent structures, changes segmentation,
or overflows readout ID fields. Analytic clearance and active-area screens must
be labelled with their limitations; construction/navigation and targeted native
overlap checks remain separate evidence. New disk service capacity is an open
engineering qualification even when the effective material approximation runs.

## Effective material and measurement errors

**NODD DESIGN CHOICE (prototype approximation):** do not remap Geant4 material
for every trial. Regenerate each candidate's native Gen3 portal inventory and
join retained material carriers by complete logical roles, never by numeric
geometry IDs alone. Carry the existing phi=1 slab profile onto its corresponding
candidate portal, updating transforms and radial/longitudinal bin coordinates.
State the mapping and any thickness/area scaling in a machine-readable audit.
Reject missing, duplicate or ambiguous joins. Shared layer/gap carriers represent
an indivisible effective profile; changes to their physical interpretation must
be explicit and cannot be called a new Geant4 material map.

Preserve retained material inventory under the declared area measure when a
carrier's area changes, or report an explicitly justified alternative linked to
the unchanged stave count. Added-disk material is an area-weighted homogeneous
slab derived from a specified existing pixel disk profile, placed downstream of
the new sensitive disk, and counted as additional inventory. Its mean material
properties must use the pinned ACTS slab-combination convention. Expose X0/L0,
areal mass and the source disk, and audit that native sensor slabs are cleared
before loading the effective map to prevent double counting. This approximation
requires a later material-remapping check before production integration.

**NODD DESIGN CHOICE (comparison control):** primary runs use geometric
digitisation and the independently trained PR #101 cluster-size error table,
frozen across candidates. Remap calibration keys through physical system/layer
identity if Gen3 IDs change; new disks inherit the explicitly named template
layer's calibration. A Gaussian-smearing crosscheck may use the frozen pooled
table. No candidate-specific error retraining or pull-width rescaling is allowed
in the layout comparison. Track time is prior-dominated, not a timing result.

## Experiment and decision record

1. Screen active-area coverage and mechanical feasibility over signed eta/phi
   with deterministic rays. Record every tested configuration and rejection.
2. Run native Fatras truth tracking for control and feasible candidates at
   1/10/100 GeV with common configured seeds and identical reconstruction. Use
   modest exploratory samples first; preserve all failures and sample counts.
3. Freeze a candidate before an independent-seed confirmation against a fresh
   baseline. Random streams can diverge when geometry changes; common event
   numbers alone do not establish paired fluctuations. State whether generated
   eta/phi/charge are in fact identical before using paired uncertainties.
4. Report residual median, untrimmed RMS/standard deviation, central 68.27%
   half-width and event-bootstrap uncertainties for d0, z0 and relative pT,
   integrated and versus signed eta. Also retain full pull distributions, fit
   efficiency, failed/invalid covariance counts and outliers. Do not hide tails
   or accept a global improvement that conceals a resolved regional regression.
5. Count physical sensor measurements once (a pixel/short-strip 2D measurement
   is one hit; each distinct long-strip face is one hit). Coverage denominators
   include every generated event, including zero-hit and failed-fit events.
   Separate incident, created, input-to-fit and fit-used counts where available.
   Show >=10 fractions with binomial intervals, hit quantiles, signed eta and
   phi dependence. A fit-selection threshold of seven is not ten-hit coverage.
6. Present the non-dominated tradeoffs and any unmet target candidly. A finite
   study may identify a preferred feasible candidate, not a mathematical global
   optimum or an engineering-approved detector. No numerical pass grants signoff.

Native input/source/library hashes, compact and effective map hashes, seeds,
commands, events and analysis source identity belong in every retained report.
Use the original PR #101 data as contextual evidence and a freshly executed
control when comparing a modified runtime. Separate SysArch physical assessment
and PhysVal scientific assessment accompany the final recommendation.


## Preregistered exploratory configurations

The `software/analysis/tracker_optimization/variants/` JSON files are explicit
prototype coordinates. `baseline`, `inner32`, `mild` and `forward` isolate the
first-layer and added-disk effects. `compact-forward` tests the hypothesis that
concentrating pixel barrels can recover intermediate-eta measurements while
placing ten disks within the high-eta aperture. Its barrel radii32/42/53/70mm
and even counts12/16/10/12 are initial screening proposals, not qualified choices.
Disk datums900/1090/1180/1270/1355/1440/1860/2350/2440mm plus the new1000mm disk
satisfy necessary eta4 radial bounds and77.636mm conservative axial spacing.
Full finite-module coverage, stave clearance and resolution may reject it.
Every subsequent trial is recorded with its reason before performance ranking.

For an axisymmetric ring, changing the mean radius changes both rmin and rmax
by the same offset; its radial width, wall thickness and longitudinal dimensions
remain fixed. This preserves its local cross-section rather than translating a
whole circle in the transverse plane. Layer feet and local service bands follow
that radial offset; global cage/trunks stay fixed. Curved support circumference
and physical ring inventory changes must be reported. The transported effective
map conserves the declared carrier inventory; it is not a component-resolved
recalculation of the altered support mass.

The human confirmed geometric primary and Gaussian crosscheck on2026-10-27.


### Physical screening dispositions before Fatras ranking

`compact-forward`32/42/53/70mm was rejected: annular supports intersect outer
modules near |z|546mm. A ring-clearing alternative32/44/56/70mm was also
rejected before performance: retained layer cable bands intersect outer staves.
SysArch verified interior intersection points, not only radial projections.
The whole-band candidate32/57/85/106mm, counts12/22/16/18, passes limited local
box/ring/foot/cable radial screens, but reducing the outermost pixel barrel would
split the original shared layer/gap material carrier. To retain unambiguous
material correspondence, `inner-family` keeps the outermost pixel radius182mm
and count30, using32/57/85mm and12/22/16 for the first three layers. This is a
new preregistered trial, preserving the outer pixel lever arm and shared carrier.
The tight first two cable radial clearances0.45866/0.76808mm remain unqualified
engineering tolerances; full native overlap checks are separate.

A finite-pixel-patch straight-ray schedule screen may use the old100GeV Fatras
sample's unchanged strip counts and an explicit fixed subset. It ignores
curvature/material and does not produce tracking resolutions. Search ranks its
worst quarter-eta ten-hit fraction, then the global fraction, only to select a
small number of disk schedules for native testing. This ranking is not an
engineering acceptance score. Keep the grid, seeds, all improving schedules,
source/input hashes and limitations; confirm with independent native samples.


### Candidate chosen by the geometric screen, before native performance

`coverage-candidate` uses the `inner-family` barrels and original disks1..9 at
|z|=865/1090/1180/1270/1355/1440/1977/2350/2465mm, plus a copy of disk2 at1000mm.
The finite-patch screen used3000 historical100GeV reference events,16000
proposals and fixed subset/search seeds407042/408042. The retained full trial
ledger includes spacing rejections. Its best proxy ten-hit fraction is99.433%,
worst absolute-eta quarter-bin96.875%. These are selection statistics only;
they ignore material and curvature and are not native candidate measurements.

The added disk deliberately uses disk2 as donor: PR100 area-mean normal X0 is
0.03091 for positive disk2 and0.03149 for disk3, while disk1 carries0.10363,
including barrel-transition aggregate material. A disk2 donor avoids copying
that exceptional transition inventory into a standalone new disk. This physical
choice is made before any native performance ranking; earlier donor1 smokes
remain development controls, not selected performance evidence. The same donor
sets the finite module layout, homogeneous mixture and inherited error table.

Retained profiles are indivisible effective carriers: relocating disk1 also
relocates its aggregate transition inventory, although the detailed physical
service model is more complex. This can bias comparisons and must remain a
limitation of this exploratory map approximation, requiring candidate-specific
material validation/remapping before interpreting improvements as a detector
performance guarantee.


### First native exploratory comparison and balanced alternative

All15 exploratory2000-event geometric cases completed at source4b009b2 before
physical collector/rail correction. The coverage candidate gives99.2/99.2/98.95%
ten-hit coverage at1/10/100GeV versus86.7/87.3/87.8% control. It is not selected
as a complete solution: in3.5<|eta|<4 its d0 widths grow by21/54/26%, and its
signed-curvature widths by36/79/72%. Nonlinear pT can conceal this regression.
Moving the final pixel plane3070->2465mm reduces the forward lever arm; moving
the aggregate first-disk material from608 to858mm also changes the forward
material seen before the first measurement. These are physical hypotheses,
not isolated causal diagnoses. Preserve all native results and failed overlap
audits; no design is accepted on the basis of global coverage.

`balanced` is registered before its Fatras results: barrel nominalr31.5/57/96/
182mm with baseline stave counts12/22/18/30; existing disks615/865/1115/1333/
1565/1780/2090/2440/3070mm and one donor2 disk at950mm. Disk1 and the farthest
disk retain their original datums; shifting disk2 beyond its eta4 inner-aperture
threshold supplies an earlier thin first measurement. The closer intermediate
disks improve availability near eta3 without shortening the maximum forward
lever arm. Keeping baseline counts isolates placement from inventory reductions.
Native mechanical checks, coverage and residuals will test these hypotheses.
This is a follow-up exploratory trial; it does not use the confirmation seed.

The full physical compact audit found13486 overlaps in the initial coverage
compact (13378collector conflicts,108rail conflicts). Top-level per-disk
collectors and rail cutouts must follow disk station positions. Correcting
these passive attachments does not change Fatras sensitive surfaces/effective
map by construction, but final confirmation uses the corrected source and a
new full native overlap check. Fixed global trunk inventory remains a reference
control; new service capacity/density is not engineering-qualified.


### Confirmation lock

After18geometric exploratory cases (36000events), lock baseline, mild-donor2 and
balanced for10000events each at1/10/100GeV, seed52042, independently of the
exploratory seed42042. Run both geometric primary and Gaussian crosscheck:
180000confirmationevents. Balanced exploratory ten-hit coverage is98.35/98.85/
98.75%, with all6000fits and no invalid covariance. Its global d0 width ratios
are0.923/0.988/0.951 and z0 ratios0.950/0.974/0.972; relative-pT ratios1.065/
0.977/1.063. Thus momentum preservation is not yet established. Compare the
mild alternative as a second tradeoff, preserve regional regressions and tails,
and do not retune layouts on confirmation data. The Gaussian native retry
contract is recorded explicitly (verified algorithm minimum10, up to11draws);
adding this metadata does not change its digitisation schedule.


### Added-material control, registered before confirmation results are read

The exploratory balanced pT1GeV regression motivates two further42042-seed
controls: `balanced-nine` omits the new disk, isolating the added material;
`late-disk` keeps the nine balanced disk positions but places the new donor2
disk at2900mm, behind most measured curvature lever arm. The latter retains
170mm clearance to the last3070mm disk and preserves all module types, layers,
staves and envelopes. Hypothesis: a late measurement can improve curvature
without scattering before most of the available measurements, at the cost of
transition-region hit coverage. This is registered before any52042confirmation
residuals are reduced/read. Neither control is chosen using confirmation data.
If selected for final comparison it uses another independent seed62042 and a
fresh baseline, leaving the original52042campaign as its own locked comparison.
