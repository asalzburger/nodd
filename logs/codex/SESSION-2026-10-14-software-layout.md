# SESSION-2026-10-14-software-layout — Software ownership migration

## Selected request and scope

On 2026-10-14 the user requested node-bound Spack dependencies, Git submodules
under software/submodules, local ActsExamples algorithms, self-contained detector
sources, Python steering, analysis, Makefiles and stepwise PRs preserving current
functionality including acts-nodd. This record covers the entire staged migration.

## Initial state and preservation

Started from origin/main b4387ae in an isolated nodd-software-layout worktree.
Existing nODD and acts-nodd worktrees contain unrelated/uncommitted work and are
preserved. Relevant local nODD adapter modifications are copied into owned source
code, never removed from their original checkout. Existing calorimeter branch
8adca5eec is included as a subsequent migration stage. No geometry values change.

## Dependencies and first stage

ACTS is pinned to355ea68493b326956756c9386d2fd9eaf9328568 before nODD-specific
additions; nodehammer30b19dcb and ODDd70556f3 retain earlier tested source states.
ODD's acts-project mirror lacks the comparison revision and has LFS disabled;
the verified OpenDataDetector/OpenDataDetector origin supplies that revision.
Source initialisation skips LFS data; existing node runtime assets stay external.
The IdRes intake pin has no publishable URL; a question remains pending.

The existing Spack environment was reverified after the preflight reported stale
fingerprints: DD4hep1.38/DDG4 imports, Geant4 11.4.2 and12 datasets work. The new
make doctor records current setup/lock fingerprints without changing Spack.
Sandbox sysctl/ps warnings are separate from successful runtime availability.
Makefiles, directory ownership and the optional viewer's source default now use
the software tree. Runtime setup is performed in the same shell as each command.

## Checks and corrections

make help, make doctor, make check and the nodehammer safeguard tests ran.
The first wrapper attempt used nounset/errexit before sourcing user helpers;
this exposed unset guard and sandbox ps behavior. External setup runs with its
normal shell semantics, followed by an explicit active-environment check.
A token preview path under build/ was rejected by the existing policy; the
correct _site/software-layout output is used. Full build checks are recorded in
later stage updates. This is infrastructure work and grants no design sign-off.

## Usage and limitations

Exact client per-turn counters are unavailable. usage is empty; no estimate or
private client-state collection was performed. IdRes access and all unexecuted
capabilities stay explicit. ADR-008 records the human-requested source ownership.

## Detector encapsulation stage

Moved detector factories/configuration into software/source/detectors, including
all existing strip and calorimeter prototype factories. Relative compatibility
symlinks retain the historical detector directory and prototype factory paths.
The detector CMake project now configures independently of ACTS and still uses
the retained repository design/validation resources for compact generation.
Five standalone libraries compiled and linked; before/after root builds passed.
All16 tracker XML files and680292 entity records matched exactly. Full CTest
was still running at this commit;9 checks had passed and the complete tracker
validator was pending. The final result is recorded by a later stage.
