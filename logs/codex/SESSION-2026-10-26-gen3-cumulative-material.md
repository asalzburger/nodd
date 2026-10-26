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
