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
