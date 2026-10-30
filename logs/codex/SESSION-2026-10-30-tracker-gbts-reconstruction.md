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
