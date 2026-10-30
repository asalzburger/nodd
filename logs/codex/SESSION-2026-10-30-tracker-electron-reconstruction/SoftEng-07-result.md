# SPECIES-SoftEng-07 — ROOT integrity findings closed

Separate read-only assessment at9e6a2bf921656b6c389bf51c6391758996a25487.
Agent `/root/reco_species_softeng`, thread01a18c71-68a7-70e0-bd48-4f5e3e7a9ccf.
The agent authored other transport/plot/SafeFatras code; coordinator-authored
ROOT corrections are separately assessed. No source/native/canonical/job changes.

All4existing pinnedROOT controls pass, plus3isolated additional controls.
Duplicate ROOT zero-track IDs, duplicate NPZeventIDs, unknownmeasurementvolumes
and incorrectdeclaredcoordinatevariance nowreject without aPASSartifact.
Validzero-trackevents pass bothstages with complete unique event-IDcoverage
and every expectedvariance marginal checked. Staticinspection confirms species
verify requires newcoverageflags. Both06P2 findings are resolved atthispin.
Full16caseactualROOTvalidation and humanacceptance remain separate.

Subsequent coordinator change vectorizes the same-event complete6parameter plus
6sigma tuple comparison to avoid per-candidate Python access over606,308CKF
candidates inFatras e100. An explicit crossed-candidate/changed-sigma control
checks that parameters and uncertainty must match the same completecandidate.
The slow optional4caseaudit alone was stopped(exit143,noPASSartifact) before
editingits source; nativeG4processing continued. Rerun uses committedupdatedsource.
All30analysiscontrols pass; later vectorized bytes are outside the07pin.
