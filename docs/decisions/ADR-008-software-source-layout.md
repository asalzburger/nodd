# ADR-008 — Software source ownership and node-bound dependencies

- Status: DRAFT; implementation explicitly requested by the human on 2026-10-14
- Created: 2026-10-14
- Human approval evidence: none; this record does not grant detector sign-off
- Scope: repository/build refactoring; detector parameters and physics unchanged

The user requested pinned Git submodules under `software/submodules`, local
sources under `software/source`, ActsExamples as the processing framework,
self-contained DD4hep detector code, Python steering and separate analysis.
They explicitly directed retaining the `acts-mac-studio` Spack ACTS CI dependency
binding, and asked for a series of PRs restoring all existing functionality.

The implementation sequence is: (1) software source pins, directory ownership
and Makefiles; (2) detector encapsulation with compatibility paths for existing
validation/evidence; (3) local nODD ActsExamples adapter and jobs migrated from
`acts-nodd`; (4) existing calorimeter algorithms, EDM and persistency migrated
from the prepared ACTS calorimeter branch. The code is infrastructure migration,
not a new detector design or a scientific acceptance claim.

ACTS is pinned before nODD-specific additions; nODD changes are compiled after
the ACTS sources through local CMake targets. Upstream updates change one gitlink.
The regression build exposes API changes without rewriting local sources or
patching a checked-out dependency. Existing scientific evidence and input hashes
remain retained. Historical path compatibility is documented where necessary.

The existing Spack environment remains external and node-bound. Verification
on 2026-10-14 found DD4hep1.38, Geant4 11.4.2 and12 datasets, with working
DD4hep/DDG4 Python imports; the older node registry fingerprints are stale.
The new doctor command records the current fingerprints without editing that
shared installation. No additional node is implied to work.

The user supplied the CERN GitLab IdRes fork on 2026-10-14 and explicitly
requested using it. It contains the existing recorded revision d54d0e3c.
Clone access was verified with the current user's authorization; anonymous access
and redistribution remain separate from using a source-reference gitlink.

Validation must exercise detector exports/build, source identities, Gen3
conversion/navigation, Geant4 material recording and prepared calorimeter/EDM4hep
controls. Expected behavior and actually executed checks remain distinct.
