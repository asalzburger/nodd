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

## Publication and local closeout

Source/data/review/accounting pushed atc27c598;reply published at
https://github.com/asalzburger/nodd/pull/100#issuecomment-6416359932,linking
all three requested observables and five figures,methods,counts and discrepancy.
Connector comment-write returned403;authorized gh pr comment fallback succeeded.
Sandbox DNS push failure was retried with network-enabled execution. No review
thread was auto-resolved and no expert approval was inferred.

Local project/session/interaction validators and token-site validate/build pass:
75tasks/39documents/21rounds,203session records,93PRledgers,245disjoint finalized
all-project turns. This is not a PR-specific additive total. Current parent
remains excluded;final publication/CI messages require later turn closure.
Final hosted checks will run after the public-discussion snapshot commit;no
pending hosted result is claimed as passed here.


## Expert feedback and merge preparation

The user requested token accounting, interaction recording and preparation for
merge after the expert was satisfied. This continues the same root turn and
review closeout; its usage must not be split into a second account.

Public feedback from noemina on 2026-10-26 at 12:52:54 UTC:
[“Good enough at the time being.”](https://github.com/asalzburger/nodd/pull/100#issuecomment-6416466956)
The refreshed public snapshot retains all three comments. No formal review
submission or inline review thread is present. Record this positive conversation
feedback as such; DES-025 remains a prototype without design sign-off.

The selected visible parent snapshot now contains 18 messages, including the
published-response and CI progress updates and the user's merge-preparation
request. Only allowlisted visible text is retained. Later final messages and
the final parent counters require a subsequent closed-turn capture.

Usage-only recovery at 12:56:14 UTC shows no newly closed PR100 root turn. Both
previous PR100 root turns have unique canonical owners; the current cumulative
and merge-preparation turn remains active and unaccounted. Older PR99 turns
also occur in this thread; they are outside this PR's accounting boundary.
The three PR100 canonical sessions contain eight disjoint finalized turns:
59,409,013 input + 267,649 output = **59,676,662 observed tokens**. Cached input
57,717,632 and reasoning output 91,950 are subsets, not additions. This is
partial completed-turn coverage, not a complete final PR total. No usage entry
was added or copied during this refresh.

Both hosted workflows passed at 568d8a4de98e57eee15e7ba0c8801b7d1d637da2:
[Project validation](https://github.com/asalzburger/nodd/actions/runs/40325511409)
and [Token usage Pages](https://github.com/asalzburger/nodd/actions/runs/40325511665).
PR100 was open, non-draft and mergeable at that observed revision. The current
update changes only accounting, interaction and tracking records. New hosted
checks after this record commit must finish before reporting final readiness.
The user requested preparation; no merge has been performed.

Initial record validation rejected a PASS check with no observed process exit
code for the remote-workflow observation. The remote CI result remains in the
narrative with its exact run URLs; the malformed check entry was removed.

After correcting that record entry, all local gates pass: 75 tasks, 39 documents,
21 review rounds; 203 session records; 93 interaction ledgers with base-history
preservation. Session summary and token-site validation/build pass for 245
disjoint finalized project turns (808,026,328 observed tokens). This project
total is distinct from the PR100 total above. Git diff --check passes.
