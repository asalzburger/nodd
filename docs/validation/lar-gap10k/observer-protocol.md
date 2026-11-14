# Complete active-deposit accounting for the matched gap experiment

2026-11-14. **PROTOTYPE / prospective diagnostic extension before observer data.**
Parent: [frozen gap protocol](protocol.md), DES-032/DES-033.

## Observed integrity failure

Both the retained 800 mm reference and the first 400 mm diagnostic run contain
rare endcap cellID exceptions. The configured DD4hep scintillator action applies
the positive-edep filter, then skips accumulation on segmentation exceptions.
The missing step contributions cannot be recovered from accepted ROOT hits or
assigned reliably to primary events from interleaved log adjacency.

Exact DD4hep v01-38 source, commit
`142cbb7eb29ec4feafb1af9317fac38775872085`, identifies:

- `DDG4/plugins/Geant4SensDetFilters.cpp`: the edep0 predicate accepts positive
  total deposited energy.
- `DDG4/plugins/Geant4SDActions.cpp`: scintillator contribution extraction and
  catch/return occur before accumulation and track marking.
- `DDG4/src/Geant4SensDetAction.cpp`: classification uses the step midpoint in
  the pre-step touchable frame.

The representative-point issue is not purely display precision: a midpoint of
two points in a non-convex annulus can lie inside its hole. The largest inspected
reference deficit is about 0.001066 mm. Error count or geometric deficit alone
does not bound omitted deposited energy. Installed header/Python evidence and
exact upstream sources are distinct from unavailable installed plugin sources.

## Frozen physical and numerical policy

**NODD DESIGN CHOICE — diagnostic observation:** retain both exact compacts,
all three original geometry/worker-audit library bytes, segmentation, the
existing 1e-8 mm guard, filters, Birks=0, FTFP_BERT, cuts, five-millimetre cap,
RNG/event seeding, twelve workers and the same ten thousand primary records.
No geometry, cell membership rule, tolerance, sensitive response or transport
parameter is changed. Keep all previous runs and their incomplete-hit status.

Add an independent stepping/event observer in its own library and steering
wrapper. It must make no RNG calls and match the actual scintillator action's
filter and `Hit::extractContribution(step,true)` semantics. Tally every accepted
native sensitive-step contribution, identifying the actual run/event/track/step,
collection and raw volume. Classify success/failure using the same midpoint,
pre-touchable transforms, native volume manager and unchanged segmentation.
The contribution is unweighted; audit track weights as one and reject unexpected
biasing. Reject unmodelled optical/fast-simulation paths rather than applying
ordinary-step semantics to them. Audit round-to-nearest output conversion.

Record every failed-ID contribution explicitly as **unassigned**, including
PDG, raw ID, native volume, pre/post/midpoint local coordinates, relevant guard
deviations, total edep and accepted contribution. Do not fabricate canonical cells
for failures. Keep per-event/per-collection and successful-cell accounting local.
Event/step payloads remain ignored; commit only aggregate summaries and bindings.

## Gates before response inference

Use fresh observed outputs. Require serial/MT 24-event controls with exact saved
cell/energy/position agreement and observer equality, a 100-event pilot, and
complete saved-data/worker/primary checks. Original native construction and the
complete 10 nm overlap/rigid-shape proof still apply, since geometry libraries
and compacts are unchanged; bind those exact artifacts to the observed runs.

Then replay all ten thousand primary records in **each** geometry. Establish
per primary and collection:

`A = S + U`, with `H = round32(S_cell)` summed over saved cells,

where A is all accepted native-step deposit, S is successfully classified native
deposit, H is saved hit deposit and U is failed-ID deposit. Check successful
cells individually. Account
for actual EDM energy field precision and round-to-nearest conversion; derive
closure bounds from per-cell output precision, not an arbitrary relaxed error.
The installed energy field is binary32: prefer exact saved-cell equality to
float32(native successful cell sum/GeV). If accumulation differs, use asymmetric
neighbour-midpoint rounding intervals with binary64 summation/division bounds
(gamma_n=n*u/(1-n*u), u=2^-53) and explicit subnormal handling.
Match failed observer counts/coordinates to the original action error records.
Reject duplicate/missing events or steps, unexpected collections, nonfinite or
negative energies, unbound artifacts, filter mismatches and failed closure.

Test full-population replay equivalence of saved signals/cells to original runs
before adding U to a retained H. Otherwise use the fresh matched diagnostic A
vectors for both geometries and retain their distinct provenance. Do not assume
that a passive observer leaves transport unchanged without checking.

## Response comparison and uncertainty

Report both saved-hit response H/E and complete accepted sensitive-deposit
response A/E. The latter answers the inclusive energy-deposit gap question; it
does not validate cell readout. Show U/E, affected primary and failed-step counts,
and per-region missing-energy fractions explicitly.

Keep the same fixed binning, common-primary event bootstrap (1000 replicates,
seed13001000) and conditional interpretation as the parent protocol. Preserve
the original fixed common tail threshold
`R < 0.07966135709622409`, derived from the retained standard-global saved-hit
mean, for the primary sensitivity comparison. Label any recalculated threshold
as a separate diagnostic; do not silently replace the frozen threshold.
Share every bootstrap multiplicity across both geometries and all accounting
streams. Retain one explicitly ordered joint principal-width covariance for
the four H/A series (84 variables), preserving correction/gap correlations.
Name both aggregate missing fractions (sum U/sum A) and mean(U/E), with primary
eta/phi/energy projections; failure-side/wheel metadata does not define cells.

Recompute means, SD/mean, tails, paired differences and principal covariance
from the full per-primary vectors. For delta=U/E, the shift from native S/E to
A/E is mean(delta), and the sample variance shift is
var(delta)+2cov(S/E,delta); verify this identity within the derived binary64
arithmetic bound. H/E differs additionally by the explicitly measured output
rounding residual. Do not force A=H+U exactly or redefine A from rounded H.
Error counts alone are insufficient to bound widths or tails.
No calibration, electronics model, technology selection, engineered routing
fit or intrinsic-resolution acceptance follows. The independent observer
measures complete raw deposits while retaining the unresolved readout issue.
