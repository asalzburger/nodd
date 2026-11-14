# SESSION-2026-11-14-lar-routing-dd4hep — native service routing prototype

## Scope and selected requests

User requested a DD4hep version of the routing, allowing bend approximation while
keeping material. On explicit clarification selected existing steel/N2 pipe
materials and retained cable envelopes. New isolated implementation branch/worktree
starts at3fca74b70709345a9440b17cf23acb40aab1f945, stacked on the existing proposal
branch; production geometry and sign-off states remain unchanged.

Read governing AGENTS/PROJECT/design docs. Using nodd-coordinate/design-evidence/
review-validation and acts-spack. Preflight reported changed setup/lock fingerprints;
warned before dependency use and verified current DD4hep/DDG4 imports, ROOT6.40.04,
Geant411.4.3 and installed datasets. Fresh software/env/run.sh activation used;
sandbox sysctl/ps warnings did not prevent successful runtime checks. Fingerprints
are captured in ignored build/lar-routing/environment-observation.json. No shared
installation or source download changed.

Initial design input records the user-selected material boundary, common-endpoint
mass matching, proposed mitered CutTube approximation and separate native versus
integrated-fit gates. No guessed cable/jacket material is introduced.
