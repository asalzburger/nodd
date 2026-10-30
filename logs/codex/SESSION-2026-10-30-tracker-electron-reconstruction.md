# Single-electron tracker reconstruction extension

## Selected user request

“Can you please add single electrons and muons as well.” Muons already exist in
PR107; an optional clarification asks whether pions were intended. Default scope
is electrons alongside the existing muon benchmark at 1/5/10/100 GeV.

## Assignments and ownership

Main owns species steering, native audit, tests, execution, analysis, figures and
records. RECO-SPECIES-PhysVal-01 reads the aae2626 muon baseline and the working
DES041 electron amendment; independent protocol assessment, no writes or native
runs. Explicit prepared role instructions are used; native profile loading is
not claimed. No shared dependency or source changes.

## Environment and protocol

ACTS Spack preflight returns unverified: changed setup/lock fingerprints and
unverified full DD4hep/Geant4 sources. User warned before dependent work. Fresh
existing runtime imports ACTS/ROOT/DD4hep and exposes electron/muon/pion hypotheses.
Python3.14.5/ROOT6.40.04 and matching ACTS355ea684 runtime verified. Native source
selects brems-recovery CKF for electron hypotheses, not GSF. DES041 amendment
freezes electron validation133042, smoke133043, 5000events/pT, selected existing
GBTS profile and unchanged geometry/response/quality/matching before runs.

## User scope clarification

The human clarified that pions were intended and requests electrons in Fatras,
plus muons/electrons/charged pions with Geant4; smeared digitization remains.
All four momenta and the existing frozen GBTS settings carry forward.
RECO-SPECIES-SoftEng-01 owns only transport.py/test_transport.py, with prepared
explicit role instructions. Main retains all other writes. PhysVal will assess
the expanded transport comparison independently.

## Initial native smoke and compatibility fixes

At9f30a4f, muon Fatras100events/pT1 completes. Electron Fatras100events/pT1
fails strictFPE gate:26FLTDIV+26FLTINV in native multicomponent two-way
reverseTrackStates transport-Jacobian inversion. No masks/checks changed.
Geant4muon/pion10event setup stops at the mapping audit: all46250active
IDs are present, but24874have multiple volume mappings under broad silicon
material selection. Passive-silicon candidates are retained in failed mapping
JSON; no accepted Geant4 performance produced. Before validation, one-way
electron CKF and active-name mapping tokens are frozen; exact one-to-one full
sensor mapping remains required. Separate smoke seed and no GBTS retuning.

The intermediate active-name substring smoke still rejects duplicated long-strip
faces because `_F0` also selects `_F0_*` passive pieces. No Geant4 events are
accepted from either failed attempt. Replace this inference with an exact
DD4hep sensitivity whitelist and a detector-construction logical-name tag.
Physical geometry/material/IDs are preserved. A task-owned wrapper and native
coverage replay expose every mapped surface. Electron one-way100event Fatras
smoke completes with FPE checks; default muon100eventpT1 reproduces all35original
arrays exactly against the retained first100events, including seeds/fits/pulls.
SoftEng02 plot defaults similarly reproduce seven original PNGs/tailJSON exactly.

## Owned DD4hep instance and independent implementation assessment

Exact sensitivity wrapper caa5487 initially accessed the global DD4hep singleton,
which is not the ACTS-owned instance: all three Geant4 smoke initializations
fail with an invalid world handle before transport. Replace with checked
DD4hepDetectorBase::dd4hepDetector accessor and link existing detector/plugin
headers/libraries. Missing detector-common/Root-header build dependencies are
corrected locally; no shared dependencies changed. PhysVal03 retains caa's
P1 runtime defect and supports the owned-instance correction subject to new
mapping/event checks. Species launch guard/effective GBTS verifier addressesP3.

### Native smoke and pre-validation convergence correction

The typed DD4hepDetectorBase binding at dabb1cc resolves the cross-module cast
failure. Geant4 muon (2 events at 10 GeV), electron and pion (20 events each at
1 GeV), seed 143043, completed. Each maps exactly 46,250 sensitive surfaces,
without duplicate or missing IDs. Independent reduction verified native species,
all measurement dimensions/variances and full-event accounting.

A distinct 100-event Fatras electron smoke at 100 GeV, seed 133043, completed
without FPE but exposed ambiguity truncation: event 62 retained 2,653 candidates,
maximum 13 shared measurements. Raise the new campaigns' computational budget
from 1,000 to uint32 maximum before validation, keeping shared-hit threshold 3
and minimum hit count 7. Source inspection proves one removal per iteration or
termination. Independent reduction now rejects unconverged native survivors
before quality selection. This changes no GBTS setting or matching cut.
Geant4 dataset CLI installation checks passed for all 12 compiled-path datasets;
no shared dependency was installed or modified and no dataset content hash is
claimed. The original muon evidence remains unchanged.

### Initial matrix launch and Fatras numerical failure

The frozen 16-case matrix launched at e71ecd0, 5,000 events/case, with four fresh
subprocess workers. Fatras electrons at 1/5/10 GeV completed event processing
but failed the unchanged FPE gate on `FLTUND` inside BetheHeitler `exp(-u)`.
The failing attempts are retained, not accepted as completed validation.
Geant4 jobs continue without changing their executing source or binaries.

SPECIES-SoftEng-03 owns only five new SafeFatras sidecar files. The bounded
assignment implements a guard where u>40 already makes exp(-u)-1 round exactly
to -1 in binary64, preserving sampled loss and RNG. It must keep FPE checks,
use a distinct algorithm/interaction type, pin source hashes and build only in
task-owned output. Integration and same-seed replay follow numerical tests.
No shared ACTS source/runtime, model cut, GBTS setting or seed may be changed.


The initial Fatras100GeV process alone was terminated (exit-15) while still
incomplete; its partial output and explicit external-interruption record remain.
The other three original attempts retain all5,000raw events for same-seed replay.
Final Fatras replay uses b8b8697 and the SafeFatras launcher. It injects only the
task-owned runner's transport dependency, schedules one algorithm in the same
slot, and fingerprints its launcher/source/binary. Original Geant4 runs retain
their unchanged executing files. Final native staging uses backend symlinks to
original Geant4 and safe Fatras outputs; no raw evidence is overwritten.

The initial orchestration analysis inherited Spack Python3.14 PYTHONPATH into a
Python3.11 analysis environment and failed imports. Native runs were unaffected.
A separate clean analysis worker uses Python -E; completed muon cases reduce
successfully. This is an analysis environment correction, not a native rerun.

### Tiny-argument underflow and production build correction

The first SafeFatras replay still fails with11/5/12underflows at1/5/10GeV;
all5,000events were written and remain excluded. Its100GeV attempt alone was
terminated before completion. Standalone system-libm proof shows exp(-1e-300)-1
returns exact+0 while setting underflow, so a large-u guard alone is insufficient.
SPECIES-SoftEng-04 owns the same five source files and adds the exact tiny branch
0<=u<2^-54 -> +0, with no skipped gamma/angle draws or FPE masking.

Complete-event comparison also found small floating-point differences in the
first sidecar: initial difference at event13 in measurements/simulated particles
and later track states. Original Fatras is built -O2 -g -DNDEBUG; the first
sidecar used default unoptimized plus pybind LTO. The correction matches native
numerical flags and removes optional pybind LTO extras. Its tests must exercise
production-equivalent compilation and both tiny/large hardware FPE controls.
The first module binary is preserved in ignored task diagnostics. Original
Geant4 executing source/runtime remains unchanged.


SafeFatras v2 at b9fc3aa completes5,000events each at1/5/10GeV with the FPE
gate active and passing. Separate PhysVal06 verifies every native audit byte
across all15,000events against original failed-but-full outputs, plus all branch
buffers in9ROOT files (322,624measurement rows; both99branch track trees).
Thus the numerical correction preserves actual recorded physics and RNG streams.
The100GeV cases remain running and outside that assessment.

An incorrectly relative temporary staging link initially made ROOT audit find
zero cases. Its vacuous PASS was discarded immediately. Added a nonempty-case
guard/control in1f92f14, fixed the link, and audited all4Geant4 muon cases:
event/candidate/measurement counts and float32 perigee/sigma/variance tuples pass.
All26reconstruction controls pass. Final combined persistence audit will require
exactly the declared16cases and bind every ROOT hash to its native report.

## Completed-case independent checks and remaining execution

PhysVal07 independently reclassifies14cases/70,000events with exact agreement
in counts, denominators, full residual/pull arrays, species/parents, outcomes and
source/runtime identities. Its findings are retained in the paired result. The
report now explicitly describes mixed-candidate matching, electron timecut limits,
missing Fatras transport records, unmerged response and pion charge/momentum tails.
SafeFatras100GeV completes5,000events with strict FPE checks in1399.06seconds;
reduction continues. Original60case reconstruction and balancedbaseline verifiers
still pass, as do26unitcontrols.

SoftEng05 finds unproven Geant4 fresh-range equivalence and localG4eventcounters
that skip would not advance. Coordinator preserves the serial100GeV Geant4
electron run; no batch implementation, physics change or partialsample substitution.
SoftEng06 separately assesses final source/evidence integrity at228edf1.

## ROOT integrity and efficient persistence replay

SoftEng06 exposes two P2audit holes with syntheticROOTcontrols: duplicate
zero-trackeventIDs and unknown measurementvolumes. Coordinator adds fullunique
event-IDset checks and complete declaredvariancecoverage in9e6a2bf; separate
SoftEng07 verifies bothfindingsclosed. All29controls pass.

The optional Fatras4caseROOTaudit proved slow against606,308CKFcandidates in
electron100. Only that analysisprocess was stopped(exit143,noPASSoutput);
G4nativeexecution was untouched. Coordinator vectorizes exactsame-event
6parameter+6sigma matching, adds a crossed-candidate/changed-sigma control and
reruns from committedsource. All30controls pass. This changes auditcost, not
physics, matching tolerances, nativeoutputs or ROOT numerical precision.

## Fatras100 assessment and final-matrix execution gate

PhysVal08 independently reproduces all5000Fatras100GeVevents, bothstages, full
uncut arrays,102bootstrap intervals and actual ROOTtuples. Its substantial
charge/momentum limitations are explicit in the report generator. All4Fatras
actualROOTaudits pass after the exacttuple vectorization. Original interrupted
100GeVattempts contain1329and200complete diagnosticrows; their partialfilehashes
are retained with NOTVALIDATEDstatus and no invented launchpin/finalFPEclaim.

PhysVal09 permits provisional read-only processing of complete Geant4electron100
rows to overlap the remaining serialrun. Prefixdigests/offsets/rowhashes must bind
those checks to the eventualclosedstream. No prefix substitutes for final5000,
completednative/FPE/source-runtime/outputhash closure or finalNPZ/ROOTchecks.

An active-task build/tracker-reconstruction-species/finalize_matrix.py process
waits for all16completed nativecases and their reductions. It freezes the six
postprocessors by SHA, then runs retain, all16ROOTaudits, report, figures, manifest
and fullspeciesverify in order with fail-fast exit handling. Its log and receipt
remain ignored; actualcanonicaloutputs are retained only after the fullmatrix
gates. This is one current-task job, without recurring scheduling or physics
changes. RootREADME links the coming speciesreport; no partialresult is published.

Interaction/accounting validators pass after synchronization; the dashboard
preview builds from existing canonicalobservations. No current-task exacttoken
counters are exposed or estimated. Baseline/TDR sourcefingerprints stillpass.

## Native matrix completion and analysis environment correction

All16accepted nativecases now complete:80,000retained generated events. The last
Geant4electron100case closes at5736.1187seconds from source
e71ecd03d1c54ccd84bcefaa3b7ef04f1fb01a50, including the55,771,625,259byte
native eventaudit and gzip/hash closure. Independent PhysVal09 has classified
all5000rows provisionally, verified actual source/runtime/input/output closure,
and checked actualROOT:794154measurements/1274968variancemarginals,2172914CKF
and7004ambiguitycandidates, all5000uniqueeventIDs and all4441/3934representative
fit+sigma tuples. Finalclosedstream identity and analysis comparisons remain.

The original matrixdriver exits1 because it retains initialfailedFatras attempts
and analysis-import failures. Its inherited SpackPYTHONPATH points the Python3.11
analysis interpreter at nativePython3.14packages. The clean analysis watcher uses
python-E; its first11G4cases allreduce successfully, and the last isrunning.
Originaldriver failure is preserved and does not replace accepted-case native
reports or the required final16case postprocessing receipt.

The waiting finalizer was restarted before retention to require the explicit
successful-analysis log marker, preventing a race with a just-created NPZfile.
No nativejob/input or frozenpostprocessor changed. Root/childusage remains
unobserved; selectedvisible discussion additions are retained and synchronized.

## Closed-stream independent completion

The clean Geant4electron100 reduction exits0. PhysVal09 independently compares
all5000finalevents, bothstages, fullarrays,16etabins,Wilson and102bootstrapintervals
with exactagreement. All per-row and contiguousbyte-range hashes prove the
provisionalstream is exactly the finalclosedgzip, not an acceptedprefix. Its
actualROOT/source/runtime/outputchecks pass. The full16case canonicalretention
andROOTaudit nowrun; report/figures/manifest/verify follow only after thosegates.

Geant4electron100 has523/3934wrongcharges and2099pTerrors>50%, centralrelative-pT
width82.04%, wrongcharges down to|eta|0.0075. Fifteenq/p pulls exceed5sigma;
one lies outside displayed−6 and remains retained. This reinforces the explicit
electronmomentum/charge limitation; no profile or quality tuning follows results.

## Final retained matrix and report

The one-shot finalizer exits0: all16accepted5000event cases retained, actual
ROOT4Fatras+12Geant4 audits pass, report/30PNG+30PDF figures/manifest andspecies
verification pass. Its measured ROOTreplay199.5481s andplotting16.0052s are
execution timings, not simulationperformance. Canonical arrays retain all80000
new generated events, with immutable originalFatrasmuon references separate.

Coordinator visually checks combined efficiency versuseta/pT, Geant4electron
fullpulls/resolutions/momentum-hit-fake panels andpionpulls. Moves the combined
efficiency legend below the panels to avoid covering low-efficiency electron
points, then replays figures/manifest/verify. Adds computed Geant4electron100
523wrong/2099large-momentum-error/82.04%centralwidth warning toreport, without
changing any numerical statistics, simulation or reconstruction. The native and
ROOTaudit producerpins remain distinct from this final presentation amendment.

Originalbalancedbaseline/TDRfingerprints,30reconstruction controls androle/skill
contracts pass again. PublicPRdiscussion refreshed withconnectedGitHubtools:
no comments/reviews returned; remoteheadaae2626 anddraftstate verified beforepush.
No new externalmessage or reviewerrequest is made. Current-task exactroot/child
tokenusage remains unavailable and is not replaced by historicalproject totals.

SPECIES-PhysVal-10 prepared before followup: read-only final canonicalintegration at
157994cbcbc2ec3551dc6bcbad51b3fc9c0a212e, reusing07/08/09 all80k independent
classification; temporaryreplay permitted, no canonicalwrite/acceptance.

## Final independent integration and PR publication

PhysVal10 completes read-only assessment at157994c, with no newblocking finding.
All130manifest entries and16retained summaries/NPZ/reports bind to independently
checked outputs; twelveG4 mappings andoriginalmuon reference hold. All120pull
normalizations/fullstatistics pass. Fresh report,30PNG and4tailJSON are exact;
30PDF differ only CreationDate. SixactualPDF renders andcorrespondingplots pass
visualQA. No native/rebuild/LLT repeat or humanacceptance is inferred.

Normalpush publishes throughc851eb4. ConnectedGitHubPRmetadata edit returns403
(Resource not accessible by integration); authenticatedgh pr edit with the exact
preparedbodyfile succeeds. Connectedreads verify the newtitle/body, actualhead,
draftstate and no comments/reviews. No externalmessage/reviewerrequest is sent.
CI starts; finalchecks/closeout remain pending.

## Closeout

All three PR107 CI jobs pass at
c851eb46063d7b6b7173b39157bc0bebca8e35f0: [project and scientific replay](https://github.com/asalzburger/nodd/actions/runs/41063873743),
[token/interaction preview](https://github.com/asalzburger/nodd/actions/runs/41063819714).
The earlier project run was superseded when the PR title/body edit triggered a
fresh run; no test failure is inferred from that cancellation. Final follow-on
changes contain review, interaction, tracking and session records only.

The delivered prototype includes Fatras electrons and Geant4 muons/electrons/
charged pions at1/5/10/100GeV,5000events pernewcase, with originalFatrasmuon
reference preserved. All80000new nativeevents, fulluncut residuals/pulls, ROOT
persistence, provenance and separatepopulations pass the bounded independent
checks. DES041 remainsDRAFT; humanexpert review and acceptance are pending.
Electron momentum/charge and pion tails remain adverse results, not acceptance.

Public discussion is refreshed at closeout: no comments/reviews returned and the
PR remains draft. Selected visible user requests, root responses and the closed
PhysVal10 handoff are retained separately from publicGitHub discussion. Exact
root/child perturn token counters remain unavailable. The completed child API
also exposes no counters. Usage stays empty/unobserved; no historical project
total is presented as this task's usage and active-root usage is excluded.

The bounded implementation/validation record closes at its observed timestamp;
this does not close the chat, merge the PR or grant detector acceptance.

## 2026-10-30 — Exact closed-turn accounting backfill

The earlier missing-usage statements describe the original capture. Usage-only
local recovery now verifies 19 completed turns, attributed through exact
root/child identities, parent activities and canonical scoped assignments.
Observed input 79,405,999 plus output 251,963 equals **79,657,962 tokens**.
Cached input 77,774,336 and reasoning output 117,831 are subsets.
Counters are owned only in this journal; the usage inventory corroborates them
and is not added again. The current root turn remains in progress and excluded.
Actual model/client version and complete current-task usage remain unknown.
Source: [usage-only inventory](../usage/USAGE-2026-10-30-pr107-accounting.json);
[explicit attribution](SESSION-2026-10-30-tracker-gbts-merge-preparation/turn-attribution.json).
