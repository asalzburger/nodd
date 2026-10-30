# Tracker GBTS reconstruction

## Selected user request

Use the current baseline, Fatras, smeared digitization and single muons at
pT1/5/10/100GeV; implement full tracker reconstruction with ACTS GBTS seeding
and tune for efficiency/fake rate. Existing3T/origin/uniform eta[-4,4]/random
charge benchmark carries forward. Geometry and response are frozen.

## Assignments and ownership

RECO-SoftEng-01 at616fd2a owns gbts.py/test_gbts.py and the separate native
TrackerGbts sidecar. Main owns campaign/design/records, full simulation/CKF/
ambiguity steering, material/error identity preparation, native audit, metrics
and plotting. No shared source/install changes. RECO-PhysVal-01 independently
reads exactsource and proposes metric/selection/validation protocol, read-only.
Both receive prepared explicit role mandates, not claimed native-profile loads.
Source implementation is a user-authorized isolated PROTOTYPE under DES041.

## Environment and initial checks

Merged PR104b4928ac is current baseline; newbranch codex/tracker-gbts-reconstruction.
Spack preflight warns changedsetup/lock andunverifiedfullDD4hep/G4sources.
User warned before dependent execution. Fresh existingruntime imports DD4hep,
DDG4,ROOT,ACTS and exposes nativeGBTS/spacepoint/CKF/ambiguitybindings.
DD4hep1.38,ROOT6.40.04,Geant411.4.3,Python3.14.5; all12G4datasets installed.
Matching source355ea in sibling software-layout; later devcheckout555c isdirty
and preserved. No shared installs/source patches. Initialprojectvalidator found
newtaskrole mismatch; maincorrected it to authoritativeworkstreamrole.

## Initial implementation and native smoke

RECO-SoftEng-01 delivered the physical-layer GBTS adapter, six Python controls
and40synthetic native helix checks, all PASS. Matching pybind11 3.0.4/ABI11 was
selected explicitly after the current shared3.1/ABI12 headers were rejected.
No shared package or ACTS source was changed. RECO-PhysVal-01 returned a separate
read-only protocol assessment at616fd2a and ACTS355ea; its denominator, secondary,
uncertainty, field and geometry findings are incorporated in DES041.

Native smoke attempts1–6 failed during initialization: wrong generated compact
location; overly strict selection-coordinate equality (one2.84e-14mm radius
roundoff; material/response payloads exact); C++Audit name collision; geometry
selection JSON shape; MeasurementContainer vs native MeasurementSubset alias;
and incorrect seed-selection enum name. These are retained in ignored native
attempt reports/logs. Corrections preserve baseline geometry/material/response.
Attempt7 completed10pT10GeV events through Fatras, smearing, measured pixel SPs,
actual CoreGBTS, parameter estimation, CKF, greedy ambiguity resolution, native
ROOT writers and all-event audit. Initial default control seeds forward events
but misses barrel events; this is a diagnostic, not a performance claim.
The native in-memory measurement covariance is double; ROOT persistence is
float32. Independent analyzer checks double sigma² and separately the established
ROOT float32 audit, without changing frozen errors.

## Pre-scan review and correction

RECO-PhysVal-02 atd166334 identified internal CKF quality selection concealing
rejected completed candidates, ordered seed provenance, ct time units, fair
runtime comparison and missing output/input/runtime closure checks. Main removed
the internal selector, retained raw completed outputs and fixed the audit and
analysis. RECO-SoftEng-02 measured-SP replay isolated the optional innermost z0
histogram; disabling it restores four-layer barrel seed chains. The pre-scan
amendment keeps13profiles and the unchanged control; no held-out sample was used.
The native SP closure is exact after the documented float32 conversion; frozen
native measurement variances remain double sigma², ROOT persistence float32.

Source review further qualified full covariance vs diagonal variances. The
native observer now checks finite symmetric covariance with successful LLT;
analysis requires this, finite chi2 and positive ndf. No response is rescaled.
Optional z0 histogram boundary sensitivity is demonstrated by +/-0.1mm measured
z translations recovering otherwise lost four-layer barrel seeds; rotations,
reflections and input reorderings do not. No histogram plus minSeedLevel2 also
recovers the three-group smoke event. This is diagnostic replay only; retained
full performance comes from subsequent native Fatras runs.

## Frozen tuning decision

At08c1241828c38b39ff26eec712d95aa538a91124, all52native500-event cases
completed (13profiles ×4momenta). Independent reduction verified every generated
muon, native full measurement subset, source identities, frozen double variances,
exact float32 measured SP closure, output hashes and matching. Common simulation/
measurement/SP sample hashes agree across all13profiles at each momentum.
The predeclared selection picks pt4-nominal-triplet: efficiencies1/5/10/100GeV
0.966/1/0.998/1;0fake/secondary/duplicate candidates;12wrong-charge fits at100GeV,
allfar-forward. Looser tau cuts do not improve this result;0.8GeV thresholds
severely reduce1GeV efficiency. Retain all13profiles, the Pareto ranking and
paired control outcomes. Run-report wall time includes setup only forfirstcase;
selection uses separate sequencer execution time (tie-break not reached forwinner).

Frozen selection/config and all tuning arrays/summaries retained before launching
held-out5000events/pT, seed103042, forselected anduntouchedcontrol. Noheld-out
results enterselection. An initial analysis-launch ProcessPool defaultspawn could
not execute a stdin main; explicitanalysis-only fork fixed it. No nativejob was
lost or changed by this orchestration correction.

## Optional ROOT state-writer failure and isolated repair

The first5000-event validation jobs (seed103042, frozen config) completed event
processing but failed the native FPE gate:159/93/55/4FLTINV forpT1/5/10/100.
No physics summaries from these failed jobs enter selection or performance.
An independent1000-event diagnostic (seed113042) retained the native stack,
identifying22FLTINV exclusively inRootTrackStatesWriter::writeT. Existing ACTS
source documents NaN state-covariance diagnostics; no shared source is changed,
no FPE mask expanded and no check disabled. The optional failing writer is
removed; the task-owned native audit now retains predicted/filtered/smoothed
state parameters and diagonal variances (nonfinite entries explicit nulls).
ROOT track summaries/full perigee covariance and measurement output remain.
Reconstruction algorithm/cuts are unchanged. Quarantined rawfailed outputs stay
underbuild/tracker-reconstruction/aborted-validation-103042; report/FPE evidence
is retained publicly. Freeze a fresh untouched validation seed123042 before
launch, preserving the original selection/config and explicitly recording the
I/O-only repair. This avoids reusing the aborted sample for final performance.

## Final held-out execution and evidence

All eight final5000-event selected/control runs at0e3b921e703390adf5c7889e5e364a7991e09ce6
completed with strict native FPE checks. Freshseed123042. Selected efficiencies
1/5/10/100GeV:4859/5000,4964/5000,4965/5000,4972/5000. Fourunmatchedaccepted
candidates(1/1/2/0), allpure-primary incomplete trajectories underfixed50% double
matching;0secondary/ambiguityduplicate candidates. NativeCKFduplicates24at1GeV,
5at100GeV are removed. Wrongcharge95/4972at100GeV;1GeVq/ppullSD1.766 and60entries
beyond5sigma are retained; no error rescaling or held-out retuning.

Independent reduction checks source/output/input identities, exact frozen native
variances, float32 measured SP closure and full measurement subset, all7systems,
full tails, allgenerated denominators and paired sample hashes. ROOTcross-audit
passes8cases: all5000evententries, allmeasurement/candidatecounts, exactfloat32
frozenvariances andmatched perigee/sigma tuples, joiningmultipleCKFcandidates.
An initial ROOTcross-audit assumption ofonecandidate/event failed correctly;
explicitperigee+sigma tuplejoin fixed analysisonly. Plotting initiallyhit a tiny
negative y-error atp=1 fromWilsonroundoff; display-errorlengthsclampedtozero while
retained intervals unchanged. Workspace-owned font/MPL caches used. SevenPNG/PDF
figure sets generated; efficiency/pulls/resolutioneta visuallyinspected, full
numerical tails/source/config/failed output evidence retained. Compressedsummary
bytes preserve frozen hashes. Artifact verifierPASS60cases/66000processedentries,
which includes deliberately repeated/paired samples and is not an independent
trial count. New12meaningful controls pass; final independent assessment pending.
