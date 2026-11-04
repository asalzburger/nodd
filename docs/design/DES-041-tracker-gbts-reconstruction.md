# DES-041 — Full tracker reconstruction with GBTS

- Status: DRAFT; explicitly user-authorized isolated PROTOTYPE.
- Date: 2026-10-30. Human owner/sign-off: pending; no lifecycle acceptance inferred.
- Baseline: merged PR104 at b4928ac87a223dc4a749e8d8a05dc3cc4a78558d.

Human technical approval: `asalzburger-review` approved reconstruction revision
78d22297e2518ef674ebf1601215fd17c6b93b71 as the current tracker reconstruction
baseline in [PR107](https://github.com/asalzburger/nodd/pull/107#pullrequestreview-5713182516)
on 2026-10-30. The [approval scope](../validation/tracker-reconstruction-approval.md)
preserves the recorded performance limitations and keeps formal detector-design
sign-off separate. Historical pending-review statements below describe the
pre-approval protocol and execution record.

## Scope and requirements

**NODD DESIGN CHOICE (explicit human request):** construct an end-to-end native
ACTS tracker reconstruction pipeline on the current balanced geometry, Fatras and
smeared digitization, for single muons at pT1/5/10/100GeV. Use and tune ACTS GBTS
to improve efficiency while reducing fakes. Keep the established constant3T,
origin vertex, randomized charge and uniform signed eta[-4,4]/full phi benchmark.
This extends the approved layout's reconstruction study, without changing the
geometry, field, material prescription or frozen response to improve a plot.

**FACT (retained repository inputs):** PR104 has46250sensitive planes,54signed
logical groups and120Gen3volumes. Existing role-transported material and frozen
pooled Gaussian errors preserve physical donor semantics;602ACTS IDs in added
disks are permuted. Recreate payloads through physical identities and verify
rather than copying numeric IDs or applying the old PR100 map directly.
Detailed DD4hep construction does not establish fresh mapped material. Retain
homogeneous added-disc material as qualified by DES040.

**FACT (installed matching source):** the available native ACTS runtime is built
from355ea68493b326956756c9386d2fd9eaf9328568, with GBTS, space-point, CKF and
ambiguity bindings. The separate development checkout has later source/dirty
patches; do not equate its HEAD with the installed runtime or overwrite it.
Use task-owned sidecars/builds against the matching runtime if an adapter is
needed. Standard GBTS example helpers contain experiment-specific layer rules;
they must be audited for Gen3 and ten pixel disks before use.

## Reconstruction contract

Create space points from measured pixel coordinates and native sensor frames.
GBTS must consume measured hit coordinates, not truth trajectory groups.
Initialize parameters from hit-based seeds, then use native CKF over pixel,
short-strip2D and long-strip1D measurements. Keep ambiguity resolution and the
track-quality configuration explicit. Truth associations are reserved for
independent connection training, fixed matching and evaluation. No truth-smeared
seed may masquerade as full reconstruction. Retain stage counts and failures,
seeds/duplicates, track states/parameters and truth associations for auditing.

## Tuning and evaluation

**NODD DESIGN CHOICE (study protocol):** separate connection-training, tuning
and untouched validation seeds. Freeze one configuration across all four pT
samples before validation. Retain every attempted configuration and rejection.
Compare untuned and selected GBTS with a common configured simulation/response.
Choose the efficiency/fake/duplicate tradeoff on tuning data only; report
validation outcomes even when they degrade. Additional tuning after inspecting
validation requires a new untouched sample and explicit record.

Report all-generated primary efficiency versus signed eta/pT and separate
conditional efficiency on an exact reconstructable denominator; never silently
remove failures or forward acceptance holes. Report fake rate, duplicate rate,
seed efficiency, wrong charge, fit failures, hit counts and runtime. Freeze
matching thresholds before scans. Binomial intervals accompany rates, including
upper limits for zero fakes. Keep full residuals/pulls for all bound parameters,
with time understood as prior-dominated. PhysVal independently assesses exact
metric definitions and final evidence. No numerical target is invented as a
human acceptance requirement; maximise measured efficiency subject to the
observed fake/duplicate tradeoff and report limits honestly.

## Validation and boundaries

Run meaningful geometry-map, measurement-dimension, configuration, matching and
provenance controls, then native smoke and tuning/validation samples. Check all
generated events are retained in denominators, no truth algorithm initializes
the reconstruction seeds, all seven detector systems are considered by CKF, and
native covariance/source identities match frozen response. Fingerprint compiled
runtime, actual source/configs/inputs and outputs at launch/close. Keep raw ROOT
outputs ignored and retain compact reproducible tables/distributions/reports.

Single-muon efficiency/fakes are a first target, not a high-occupancy or pile-up
fake-rate claim. Material approximations, coverage gaps, fixed response and
engineering limitations remain. No new DD4hep/Geant4/material campaign or TDR
publication is required by this bounded reconstruction task.

## Frozen metric protocol (RECO-PhysVal-01)

**NODD DESIGN CHOICE:** match using unique inlier measurement indices with
purity >=0.5 and completeness >=0.5. Completeness counts every unique measurement
associated with that particle before reconstruction. Classify every accepted
candidate; missing native classifications cannot disappear from denominators.
Separate real secondary matches, unmatched candidates, and additional matches
beyond one representative. Choose the representative deterministically by most
inliers, then lowest chi2/ndf, then stable track index. Quality requires at least
seven measurements, a reference surface and finite positive bound variances.
Also retain raw CKF/ambiguity candidates rejected by that quality contract.

Conditional primary efficiency requires at least six unique sensor measurements
and three distinct physical pixel groups; also show the nested four-group set.
Headline efficiency always includes every generated muon. Report all six bound
residuals/pulls, wrapped phi, truth-minus-reconstruction sign and uncut tails.
Without timing measurements the time result remains prior dominated.

Use Wilson68/95 intervals for independent event rates. Quote candidate fractions
with event-block bootstrap uncertainty; for zero fake events use the exact
one-sided95 bound `1 - 0.05**(1/N_generated_events)`, including zero-track events.
Single-muon events cannot establish high-occupancy fake performance.

The geometry adapter initially uses all176 physically outward pixel-layer links,
with native eta compatibility pruning, rather than a truth-trained connector.
Connection training is therefore unnecessary for this initial control. It stays
available as a separate future procedure; no training seed enters the measured
reconstruction. Tune at most12 additional profiles on500events/pT and validate
one frozen profile on5000independent events/pT. Pick highest worst-pT generated
efficiency, then highest equally weighted mean efficiency, then lower fake-event
incidence, duplicates and runtime. Keep CKF and ambiguity settings fixed while
scanning GBTS. One configuration is used across all four momenta. These are study
choices and technical recommendations, not human acceptance/sign-off.

### Pre-scan smoke correction

The10-event pT10 smoke and measured-SP replay found that the optional stock
innermost-barrel z0 histogram rejects otherwise viable barrel connections.
All12candidate profiles explicitly disable that histogram, while the untouched
initial nODD adapter control remains. This amendment precedes the500-event tuning
sample and all held-out runs. Scan minPt0.4/0.6/0.8GeV, nominal/doubled coherent
tau cuts and confirmed/three-group recovery settings. No ACTS Core source or
physical input changes. Runtime tie-break uses sequencer/event-stage time,
excluding one-time geometry preparation charged only to the first batch case.

The audit keeps every *completed native CKF output*, before analysis quality
selection, and all ambiguity survivors. Native propagation errors with no
output object are not retained as candidate tracks. Estimated-seed and stage
no-output counts remain failure diagnostics; they are not exact per-seed fit
failure counts when CKF seed deduplication is enabled. Ordered seed source links
and complete CKF-input subset membership are retained/checked natively.
Native measurement covariance uses double sigma-squared; ROOT writers persist
float32. Native pixel global space points use float32, verified by independent
measured local-to-global conversion and exact float32 equality. Bound time uses
native ct[mm]; public time axes convert by299.792458mm/ns, with pulls unchanged.

## Single-electron extension (2026-10-30)

**NODD DESIGN CHOICE (explicit user request):** add single electrons alongside
the existing single-muon benchmark at pT 1/5/10/100 GeV, with both charge signs,
the same balanced geometry, 3 T, Fatras interactions and frozen Gaussian response.
The request repeats muons, which are already present; an optional clarification
asks whether pions were intended. Proceed with electrons and existing muons
unless the human clarifies otherwise.

Freeze the already selected muon GBTS profile, CKF/ambiguity/quality/matching
settings before electron validation. Set the gun and seed-estimation particle
hypotheses consistently from a named species; record and verify actual PDG and
mass in native output. The installed ACTS TrackFindingAlgorithm at source
355ea684, lines 500–508, selects its existing bremsstrahlung-recovery finder for
electron hypotheses. Keep that native multicomponent CKF behavior explicit; no separate GaussianSumFitter refit is scheduled.
Keep Fatras electromagnetic scattering, ionization, radiation and conversion
enabled through its existing addFatras helper. Do not silently substitute muon
energy-loss or mass assumptions. No new GBTS tuning uses electron validation.

Retain 5,000 generated electrons per momentum with seed 133042, fixed before
launch. Smoke uses a distinct seed 133043. Reuse the immutable published muon
validation as the comparison; compare populations, without assuming event-level
pairing across species. All generated primaries remain in denominators; all
secondaries, incomplete matches, charge failures and residual/pull tails remain
visible under the existing matching contract. Report non-Gaussian electron
energy-loss tails honestly. An isolated generic species interface must preserve
the default muon chain, with a native regression against its retained events.
The DES remains DRAFT; no new human acceptance is inferred.

**FACT (pinned ACTS355ea source):** Fatras StandardInteractions.hpp explicitly
notes that its Bethe-Bloch ionization does not correctly describe electrons,
and radiation follows ionization. The unchanged native 0.5 GeV absolute-momentum
threshold affects survivors and secondaries. This is a qualified Fatras electron
benchmark, not a precision electron-response or full-shower validation. Native
electron CKF uses multicomponent stepping (12 components, weight cutoff 1e-4,
max-weight stored-state merge and default Bethe-Heitler approximation), whereas
muons use the ordinary CKF. These source defaults are recorded, not tuned.

### Clarified Geant4 species matrix

**NODD DESIGN CHOICE (human clarification):** the intended additional species
was pions. Add electrons in Fatras and muons/electrons/charged pions in Geant4,
keeping smeared digitization. The original muon Fatras result remains the
reference. All four momenta use the frozen selected GBTS configuration.
Geant4 validation uses 5,000 events per species/momentum, seed 143042; separate
smoke seed 143043. These seeds and settings precede validation. No new seeder
tuning is performed on these comparisons.

Use the existing FTFP_BERT Geant4 physics list and validated persistent native
lifecycle adapter. Keep secondaries and particles without hits, record charged
secondary hits, map Silicon/pixel_Silicon sensors, and preserve the existing
25 ns simulation limit and outer tracking-volume kill boundary. Retain all
generated primary events regardless of interaction, decay or reconstruction
outcome. Charged-pion decay/interaction products remain distinct secondaries;
no descendant grouping or truth-derived reconstruction input is introduced.

Geant4 transports the maintained detailed DD4hep geometry. Fatras and the CKF
use the retained role-transported effective ACTS material prescription. This
comparison therefore tests the actual simulation/reconstruction representations,
including their material approximation difference; it does not certify a fresh
Geant4 material map. Species PDG/mass and electron multicomponent versus ordinary
pion/muon CKF behavior are audited explicitly. Human acceptance remains pending.

### Pre-validation compatibility corrections

Electron Fatras 100-event smoke at9f30a4f completed event processing but failed
FPE checks (26 divide-by-zero and26 invalid operations) in native two-way
multicomponent CKF `reverseTrackStates`, which inverts singular transport
Jacobians. Use one-way native multicomponent CKF for electrons in both transports,
recorded explicitly in the frozen species campaigns; retain ordinary two-way
muon/pion reconstruction. This changes an electron-specific fit setting before
validation, not GBTS tuning or an FPE mask. Preserve failed smoke evidence.

The first Geant4 mapping audit found all46250active surfaces, but24874geometry
IDs had multiple mappings when all Silicon/pixel_Silicon volumes were considered.
Passive silicon can share sensor centers in the detailed geometry. Restrict
Geant4 hit mapping to maintained sensitive-volume name tokens `_sensor_`,
`_active`, `_F0`, `_F1`, retaining DD4hep native sensitive-detector matches.
Verify exact active-surface set, one mapping each, all seven systems and no
missing active surface before running validation. This changes hit attribution
to actual sensors, not physical geometry/material or truth-based hit selection.

The intermediate `_F0`/`_F1` substring attempt also matched long-strip passive
components (`_F0_pickup`, `_F0_spreader`, etc.) and failed the unchanged exact
one-to-one gate. Replace substring inference with canonical DD4hep sensitivity:
a task-owned detector-construction wrapper collects exact logical-volume names
from `DetElement.volume().isSensitive()` and tags only those converted Geant4
logical volumes with `nodd_active::`. The generic ACTS mapper selects that tag.
This is sensitivity metadata, without changing solids, placement, material,
DD4hep IDs or the hit-based reconstruction input contract. Require full
46,250-sensor mapping with no duplicate or missing active IDs.

### Converged ambiguity resolution before species validation

**NODD DESIGN CHOICE:** raise only the new campaigns' ambiguity iteration
budget from 1,000 to the native uint32 maximum, 4,294,967,295. In a separate
100-event electron Fatras 100 GeV smoke (seed 133043), event 62 retained 2,653
tracks with up to 13 shared measurements after exhausting the old removal
budget. Pinned ACTS GreedyAmbiguityResolution removes one track per iteration
or terminates, so execution remains bounded by the initial candidate count.
Keep the original maximum-shared-hit threshold 3 and minimum hit count 7.
Independent reduction checks every native survivor, before quality selection,
against the source algorithm's strict fewer-than-3 shared-measurement condition.
An incomplete solver run is rejected rather than scored as physics fakes.
This amendment precedes the held-out species matrix and performs no GBTS tuning.
The original muon Fatras reference and its 1,000-iteration setting remain intact.

The working sensitivity wrapper receives the registered DD4hepDetectorBase
instance directly across the Python binding. The muon, electron and pion native
Geant4 smoke tests pass the exact 46,250-sensor mapping and independent event
count checks. Installed Geant4 11.4.3 reports all twelve versioned datasets
present through its compiled data paths; record this separately from unset
optional environment variables. Installation checks do not hash dataset contents.

### Fatras numerical repair after the initial validation launch

**NODD DESIGN CHOICE:** preserve the failing 5,000-event Fatras electron
attempts, and replay the same frozen seeds/settings with a task-owned numerical
sidecar. The initial 1/5/10 GeV runs completed all events but failed the FPE gate
on underflow in native BetheHeitler's `std::exp(-u)`. No FPE mask is permitted.
For binary64 `u > 40`, `exp(-u) - 1` rounds exactly to −1, which is the only
use of that exponential in the sampled energy loss. Skip that unnecessary
exponential in this branch, retaining all random draws, sampled loss and physics
parameters. A newly named algorithm/interaction type avoids symbol interposition;
compile from revision- and hash-checked matching ACTS source into task-owned
build output. Do not patch the shared runtime. Prove bitwise loss equivalence
and absence of the underflow, then compare replayed event outputs and keep every
original failed run's hashes. This is a numerical repair, not seed/profile or
physics-cut selection on validation performance. All Geant4 cases continue with
the original frozen implementation; their native source pin remains explicit.

The first local sidecar guarded only large u. Full replay exposed the same
underflows at tiny u: a standalone native-libm check gives `exp(-1e-300)-1 = +0`
while raising underflow. Add the second exactly rounded branch
`0 <= u < 2^-54 -> +0`; no early return skips subsequent random draws. Since
`exp(-u) > 1-u > 1-2^-54`, binary64 round-to-nearest returns exactly 1 before
the subtraction. Preserve both failed local attempts. Match the original native
Fatras -O2 configuration rather than comparing an unoptimized/LTO sidecar with
an optimized runtime; require full native-event regression after rebuilding.
No FPE mask, transport cut or reconstruction parameter is changed.
