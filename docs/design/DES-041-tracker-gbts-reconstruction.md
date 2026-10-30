# DES-041 — Full tracker reconstruction with GBTS

- Status: DRAFT; explicitly user-authorized isolated PROTOTYPE.
- Date: 2026-10-30. Human owner/sign-off: pending; no lifecycle acceptance inferred.
- Baseline: merged PR104 at b4928ac87a223dc4a749e8d8a05dc3cc4a78558d.

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
