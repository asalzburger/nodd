# Compact LAr diagnosis and underlying distributions

Bounded follow-up to PR148 at f638698dda59769c0823cba2d23bf7cba80841ea; clean
starting worktree. User asks why barrel performance worsens, whether it can be
mitigated, and for the underlying raw distributions. Interpret the last phrase
as the distributions underlying the width curves; also show the shifted endcap
shoulder explicitly. No new geometry, transport or calibration fit is requested
or performed here. Existing strict-ratio controls remain unchanged.

Use nodd-coordinate, nodd-design-evidence and nodd-review-validation for bounded
scientific evidence and independent claim assessment. Do not silently select a
thicker annulus while the relative-radius interpretation remains unresolved.

## Diagnostic method and limits

Recheck saved event-ledger/receipt/readback hashes against both frozen summaries,
physical primary pair and saved five-fold model identity. Apply the evaluated
OOF gains to their excluded folds; require exact old broad-region statistics.
No ROOT rehash, native runtime, transport, gain fitting or new bootstrap.
Histogram raw S/Etrue and shape divided by each regional mean. The latter is
only a display normalization. Show absolute held-out Ehat/Etrue separately.
All zeros/tails enter reported widths; histogram flow and axis exclusions stay
explicit. No Gaussian fits or tail cuts.

Retain original broad regions and additionally split endcap at abs(eta)=1.8,
a pre-existing ten-bin edge, to describe where the new tail lies. Show original
45–50GeV energy slice within barrel. These focused views are post-hoc descriptive
controls, not new primary tests or an optimized region/calibration family.

## Initial evidence and interpretation

Barrel Pb1.8→2.6mm, inner LAr gap~1.196→0.484mm, central active chord~209.65→
107.72mm and mean broad-barrel R0.141925→0.057901. Mean loss alone is removable
by gain calibration; broader relative shape at fixed energy remains. This is
consistent with degraded sampling fraction/frequency and stronger longitudinal
sampling variation, not a measured one-parameter causal decomposition. ECAL-only
B0 ideal deposits contain no electronics noise/charge-collection model.

PDG2024 Particle Detectors at Accelerators, section35.10.2/PDF85–86, describes
sampling-fraction/frequency effects and approximate stochastic scaling with
sqrt(plate thickness/sampling fraction). This is qualitative support, not a
numerical prediction for our changed geometry or mixed-spectrum CV.

Conditional mitigation: retain thin Pb/~1.2mm initial gaps by allowing a thicker
annulus (already screened at Rin1772.8/Rout2350, warmouter2641.7mm), then rerun
native/10k controls. Layer-dependent forward sampling corrections could address
longitudinal response/nonlinearity, but cannot be promised to recover lost
sampling information. No new mitigation result is claimed.

## Commands, review and accounting

Actual helper analyze reconstituted saved predictions and all broad raw/OOF
statistics; histogram population/flow invariants passed. Three scientific plot
groups exported PNG/PDF/SVG. First visual inspection found a legend overlapping
axis-flow text in one panel; moved the flow annotation and fixed legend placement.
Final rerender and independent revision-specific review follow.

Current parent turn active: exact usage unknown, excluded. Separate review usage
will be recorded only after closure. Earlier compact-study parent has closed and
belongs solely to its original session if exact counters can be recovered.


LAR-COMPACT-PHYSVAL-DIAGNOSIS; PhysVal; exact
0613fe1459e84bb89c7f459232ed97d4842b86c6; read-only/owned files none. Inputs:
diagnosis report/binwise/material summaries, helper and three PNGs, with existing
raw/OOF/model proofs as needed. Assess causal-inference boundary, faithful old
widths, shoulder/bulk counts/widths, fixed-energy barrel shape and histogram/plot
normalizations. No new native/transport/fits/bootstrap/writes/private usage,
publication or further delegation. Completion: bounded findings/actual checks
and limitations returned; no design or precision acceptance.


## Final outcome and independent review

PhysVal assessed0613fe1459e84bb89c7f459232ed97d4842b86c6 plus the explicit
working cut-convergence remedy (diagnosis SHAa9adadbeaae2a3ca61049eeef201907ada12946482fe326402eb1f8a70b553bc).
No material findings remain.60focused statistics/18histograms match, with
unchanged broad-region moments, saved-fold/source/ledger/model bindings,
208-probe native active-chord summaries and all3figure groups. No new fits,
bootstrap or native execution. Common0.7mm production cuts do not establish
convergence for0.484mm gaps; officialFAQ distinguishes secondary production
thresholds from geometry-boundary-aware tracking. This remains unquantified.

Measured core sampling changes support the leading mechanism; a causal partition
or measured mitigation is not available. New endcap shoulder/bulk held-out CVs:
2.00→15.30% and3.31→2.87%; fixed45–50GeV barrel1.97→3.92%. All3PNG/PDF/SVG
sets, compact exact histograms, reproduction recipe and calibration source gates
retained in draftPR148. Figure normalization and all-event denominators explicit.
Fortyanalysis unit tests pass, including two new scientific guard tests. Initial
legend overlap remedied and final PNGs inspected. No maintained geometry change,
new transport, ready-for-review promotion, merge or engineering sign-off.

Exact usage for this follow-up: one closed review/11requests;
3,254,156input +9,304output =3,263,460observedtokens. Cached3,223,296 and reasoning
5,916 are subsets. Current parent active/unknown. Previous compact parent has
closed but strict counter recovery fails a cumulative/request consistency guard;
that previous parent remains unknown in its original owner, no estimates. No
historical/parent counter duplication, private reasoning or raw app payloads.


Final required checks passed: project109tasks/54documents/24reviews;295paired
journals; inventory68components/102families/53reviewedinputs/12pins;119PR
interaction records with base retention; token validate/build556disjoint dated
turns. Publication payload/source/render audit passes27paths, no new raw events,
libraries, private home paths or introduced blob above2MB. Draft state/labels
retained. PR public metadata snapshot records observed0613head, not a recursive
self-reference to the final metadata commit. Current task usage remains partial.
