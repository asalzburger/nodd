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

## Local ActsExamples, steering and analysis stage

The full detector suite completed:10/10 passed. The independent XML/entity
comparison and direct detector build results remain unchanged. The clean ACTS
build links the local adapter after upstream targets are configured through the
CMake project hook. Deferred includes with absolute source paths are used;
CMake disallows creating subdirectories during deferred execution. ACTS source
and its package commit metadata stay independent of the parent project.

The build-owned Python environment now follows upstream's pinned codegen
requirements and installs the ACTS-local codegen package, rather than the
unrelated PyPI package with the same name. The initial bootstrap was corrected
and synchronized before building. No shared Spack or acts-nodd install changed.
The local Python sensitivity helper and its four controls are migrated out of
Core bindings. DD4hep dictionaries must be initialized before downstream
factory loading on this node; that runtime order is now explicit in the helper.

10 adapter/sensitivity tests passed in107.83s, including complete tracker Gen3
construction and8-track Geant4 recording. The128-track navigation job produced
45646 sensors and117 volumes; independent native comparison returned PASS,
0 errors and all7 tracker systems. Analysis code now has one owner under software/
analysis and retains a compatibility symlink from its old tool path. Source/MPL
notices, job steering and Makefiles are retained. Project-record28 tests and
token-usage10 tests passed; all relevant validators and token preview build pass.
The user supplied the IdRes fork while this stage ran; its first-PR completion
and downstream merges follow separately.

## Calorimeter/EDM parity stage

Copied the existing ACTS fork8adca5eec calorimeter reconstruction, FastJet, hit/
cluster/jet persistence and their controls into nODD-owned sources. Core helpers
live in software/source/Calorimeter; framework algorithms/converters under
ActsExamples/Calorimeter; transient data headers under EDM. All40 C++/header
files, including the retained tests, are byte-identical to that source revision.
Only ownership/build paths and documentation are adapted. Source/MPL notices
and the original prototype/response-calibration limitations are preserved.

The local build completed46 steps. All10 calorimeter tests passed in1.60s,
including digitization, clustering, jet finding, EDM4hep persistence and relation/
metadata roundtrips. The Python-steered EDM4hep jet pipeline passed; saved input
and output ROOT files each have3 events and1 metadata entry. Six standalone
header-check targets compiled13 header translation units. The original upstream
header helper uses directory-relative paths; local includes require a wrapper to
keep generated stubs inside the build directory. The first generated stubs were
preserved under build/legacy-generated-headers after correcting the local helper.

The user-provided IdRes fork is pinned at the original d54d0e3c state in PR77.
Its dedicated paired session record retains the clean build and22x729-row run
checks. Downstream branches receive that addition via ordinary merges.

## External glue and current node verification

The remaining IdRes adapter and nodehammer native-build/display glue are owned
under software/source/externals, with compatibility links at the former tools
paths.17 boundary controls passed after relocation. The optional native
nodehammer build also completed against the current Spack runtime:602/602
upstream tests passed in24.04s, and its source submodule remained clean.

The repository node registry now records the reverified current setup/lock
fingerprints, DD4hep1.38 and Geant4 11.4.2 package hashes. Its preflight returns
prerequisites-present with no warnings;5 node preflight unit tests pass. Geant4
simulation capability is explicitly limited to the observed8-track material
recording smoke. No shared installation or installed personal skill copy was
changed. Previous verified snapshot evidence remains in Git history.

## Directory marker correction

The stage-one detector directory README shadowed the destination filename of the
real detector README. Git consequently classified the later move as deleting a
scientific-path README rather than a rename, and PR78's existing policy gate
rejected it. The marker is now .gitkeep; the actual detector README remains in the
next stage. No policy gate is changed or weakened. Downstream ordinary merges
retain the real README and make Git's source relocation visible as a rename.
