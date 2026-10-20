# ACTS dependency rebuild — 2026-10-19

The user requested rebuilding the existing acts-nodd checkout before continuing PR90. Source HEAD remains `555c66e71d0639665c2fa3d5574a0fe7f3f62cde`, with all15 pre-existing changed-file hashes preserved. No source, dependency requirements or tests were changed. This is a dirty-source installation, not a release build.

The prescribed `acts build acts-nodd 8` first encountered stale cached EXPAT2.8.5. Saved the old cache and used `cmake --fresh` with the same github-ci preset, RelWithDebInfo, C++20, ODD, Python executable and install prefix, followed by the full install target with8workers. Fresh configuration resolved EXPAT2.9.0, vecmem1.28.0 and current ROOT/Python installation hashes. The regenerated ActsConfig pins DD4hep1.38 and vecmem1.28.0. No plugin was disabled. The CLHEP warning compares two paths resolving to the same installation.

Executed checks:

- Full build/install: passed.
- `acts test acts-nodd` with8parallel test workers:385/385 passed.
- `RunIntegrationTestNavigatorConsistency`, `RunIntegrationTestPropagationBentTracks`, `RunIntegrationTestPropagationCompareAtlasEigenConstant`: all passed.
- Python surface, blueprint, field, navigation and existing nODD tests:28passed,2skipped because optional external nODD inputs were unset.
- Prescribed `acts run acts-nodd`: installed ACTS, DD4hep, DDG4, Geant4 and nODD imports passed in the refreshed Python3.14.5 venv. Geant4 reports11.4.3 and all12datasets installed; this is a presence check, not dataset checksumming or full simulation qualification.

The library, source-patch, setup, lock and execution-log fingerprints are retained in [rebuild.json](rebuild.json). Raw build logs remain task-local scratch. The custom muon executable must be reconfigured/rebuilt and pass its own field and boundary controls before scientific use; these ACTS tests alone do not validate that policy. `VersionInfo::fromLibrary()` has no commit hash at this revision, so library identity relies on the recorded dylib SHA256 rather than an invented clean-source commit.
