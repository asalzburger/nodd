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
