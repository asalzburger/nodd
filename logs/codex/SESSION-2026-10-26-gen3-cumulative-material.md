# PR100 expert review: cumulative material

Starting clean1320a0e9b836c84b2d769a613dda526e54356e32 on
codex/tracker-gen3-material-mapping. User requests addressing expert comments.
Public noemina comment6415806657 requests accumulated meanX0/L0 versusr for
small|eta|,versus|z| inforward slices,andversusd=sqrt(r²+z²) inall slices.
No inline threads or review submissions are currently present.

Use nODD coordination/review/evidence workflows. Main owns new diagnostic
reduction/plotting and tests;independent PhysVal assesses a fixed commit.
Design amendment precedes implementation. Reuse immutable existing Geant4
recording and native validation ROOT outputs with exact hashes. Integrate
Geant4 partial physical steps;validation budgets jump at thin portal positions.
Compute per-ray cumulative curves before per-slice means and SEM;include zeros.
No new geometry,material-map,validation rays or human sign-off. Diagnostic
slices/grids are configurable choices,not acceptance thresholds.

Full reduction completed:100000Geant4rays/17137021steps and100000validationrays/
1417441interactions. Every endpoint conserves the per-ray step sum;native ROOT
reported-total residuals are retained rather than forced to zero. Source/input
hashes match the authoritative parent reports. Seven analytic controls and
full36-test suite pass;retained source/count/monotonicity/endpoint audit passes.

Five PNG/PDF/SVG figures compare rcentral,forwardzX0/L0 andall-slicedX0/L0.
Initial legend overlap and histogram endpoint closure were corrected before
retention. The pinned unrooted styled line rejects a baseline keyword;use its
Histogram/SEM band with an open-ended Matplotlib stair line to avoid a false
return to zero at the final checkpoint. No dependency change.

Largest sampled cumulative differences:centralr826mm0.0379205X0/0.0133170L0;
forwardz1330mm,eta1.5–2.0,0.362677X0/0.0476333L0;d1385mm sameeta,
0.266984X0/0.0345065L0. These show spatial differences hidden byclosefinaltotals.
No acceptance/significance or unique cause inferred. Full profile data compressed
losslessly with deterministicgzip;summaryCSV retains32slice/axis/quantitycases.

CUMULATIVE-PhysVal-01 was prepared before dispatch atbffaba61f2d243ac2025de2476b34411437798fa
and read-only child01a17838-6a10-7d90-97e4-72586f074dd1 completed with no blockers.
Independent direct fractions/per-ray sums match38checkpoint+18endpointcases per
sample within2.89e-15mean/8.15e-19SEM²;all32CSVcases and5PNGschecked. Full result
is retained. Native physics not rerun;no human approval.

Observed new-sessionusage:one completed PhysVal turn,1,748,569input+10,305output
=1,758,874total;cached1,646,848and reasoning2,686are subsets. Current cumulative
parentactive01a1782a-3d7d-7b93-935f-cd0bbe5c90a8 is excluded. The previous mapping
parent's22,820,376tokens were recovered into that previous account only;its
4completedturn total is39,396,650. Full completed-visible snapshot replaces
its old active curated events;historical snapshot remains. No estimates.

Final vector figures use losslessSVGZ to avoid286k generated-path diff lines;
PDF/PNG remain directly viewable. Plot data and five displayed curves are
unchanged. PRbody links the cumulative report;public response is the remaining
publication step before final hosted checks.

Post-review coordinator fix:the replay now accepts the exact custom --config
path used by the reducer and checks both its hash and embedded configuration.
Default retained audit,byte-identical custom-path audit and changed-config
rejection pass. This CLI/provenance guard is outside the exactbffaba61 review;
reduction formulas,retained numerical data and displayed figures are unchanged.
