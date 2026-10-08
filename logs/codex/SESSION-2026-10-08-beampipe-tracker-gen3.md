# Beryllium beampipe and DD4hep-driven ACTS Gen3 tracker

User request2026-10-08: first PR for a0.8mm Be wall at27mm, then complete
BeamPipe+Tracker DD4hep and derived ACTS Gen3 tracking geometry. Work isolated
from all pre-existing primary/ACTS edits on remote main3e0e706. Optional radius
clarification pending; using inner radius27mm, outer27.8mm and inherited±4m
straight extent. No human engineering sign-off inferred.

The acts-spack skill preflight found changed setup/lock fingerprints. Actual
runtime imports verified ACTS, ROOT6.40.04, DD4hep and DDG4. Component implementation
and failed/successful native and DDSim attempts are retained in DES024 results.
No scientific transforms/services changed. Task remains open for the assembly
and Gen3 conversion. Exact current-turn tokens unavailable, never estimated or
partially recovered. This pair is the one shared task owner across dependent PRs.

## Complete tracker and Gen3 follow-up — 2026-10-08

Complete assembly now includes all selected tracker subsystems plus the pipe.
Pixel IDs1–3 remain; strips translate root systems3–6 to4–7, retaining all other
fields. No sensor moves or silicon loss. Shared service trunks are reconciled
with conserved payload. The optional clarification remained unanswered; the
review proposal uses inner27/outer27.8mm and only passive pixel apertures28.8mm.
138 parts lose10.128297365g of support filler/unused air; non-filler inventories
remain. Standalone artifacts/producers, outer service limits and disc datums
are unchanged. DES025 remains DRAFT; no human approval is recorded.

Actual checks:10/10 nODD CTests,385/385 ACTS C++ tests,6 focused Python tests
including8 Geant4 material probes, all45646 native sensors/1156 material
inventories,zero overlaps,117 Gen3 volumes,128 saved navigation probes. Native
and Gen3 execution source/library hashes are distinct from publication commits.
ACTS fork PR3 contains the complete Examples/Nodd foundation and Gen3 capability.
First pipe PR57 is separate. Required full ACTS pre-commit failed existing zizmor
findings only; scoped hooks passed. Native failed controls and API/alignment
corrections remain documented. Unrelated primary and ACTS edits were preserved.

This pair remains the single canonical owner for the bounded task across the
linked PRs. Exact active-turn counters and client completion time are unavailable;
usage stays empty. No partial import, token estimate or new accounting schedule.
Passive mapping, field/acceptance/reconstruction and engineering qualifications
remain open.

PR57 was merged by the maintainer at2026-10-08T11:49:26Z as0050cb80; its
hosted build passed at11:43:31Z. Normal receiving-main merge1d69d004 preserved
all science and logs. PR58 now targets main; ACTS fork PR3 is its companion.
ACTS initial title check rejected the nODD prefix, corrected to its conventional
feat title. First follow-up logger check rejected a null exit code for a PASS
entry; the actual successful metadata-query exit was recorded. Generated
bytecode was removed and ignored in ordinary corrective commits.
Publication snapshot 2026-10-08T12:32:23Z: hosted PR58 checks pending; local checks passed.
