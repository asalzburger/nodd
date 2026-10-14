# nODD software

Dependencies remain bound to the existing ACTS Spack `ci-dependencies` installation
on `acts-mac-studio-01.cern.ch`. The Makefiles activate it; they never install,
concretize or rewrite it. `make doctor` checks actual imports, package hashes and
Geant4 datasets, and reports setup/lockfile fingerprints.

| Directory | Ownership |
| --- | --- |
| `submodules/acts` | ACTS framework, libraries and its existing vendored dependencies |
| `submodules/OpenDataDetector` | Existing ODD comparison source, pinned separately |
| `submodules/nodehammer` | Optional display toolkit |
| `submodules/IdRes` | Optional resolution tool, pending confirmed clone URL |
| `source/ActsExamples` | nODD algorithms, ACTS detector adapters and external glue |
| `source/detectors` | Self-contained DD4hep factories, materials and detector configuration |
| `source/EDM` | nODD event data extensions |
| `running` | Python job steering |
| `analysis` | Output inspection and analysis |

From the repository root use `make submodules`, `make doctor`, `make detector`
and `make detector-test`. Software submodule initialisation deliberately targets
only `software/submodules`; the existing Overleaf documentation is independent.
ODD LFS assets are not downloaded by this source-initialisation command. Existing
ACTS/ODD runtime data remains in the node installation; source pinning alone does
not claim that a new ODD field/material-map download works.
`make nodehammer` preserves the native viewer's existing Conan build and lock.
`make idres` builds a disposable source copy outside the submodule using GSL
from the active environment. Optional packages are not part of the default build.

ACTS starts at `355ea68493b326956756c9386d2fd9eaf9328568`, the parent of the
existing nODD adapter changes. The macOS compiler correction is retained.
nODD code is migrated separately and no patch is applied to this checkout.
An ACTS update is `git -C software/submodules/acts fetch`, followed by
`git -C software/submodules/acts checkout <revision>` and committing that gitlink.
Run the extension build and regression tests before accepting an update.
Detray/Traccc and other ACTS-owned sources remain under that ACTS revision;
DD4hep, Geant4, ROOT, podio, EDM4hep and GSL remain Spack dependencies.

The staged migration is recorded in
[ADR-008](../docs/decisions/ADR-008-software-source-layout.md).


## Local ActsExamples build and jobs

`make software` configures a clean ACTS build under `build/acts`, adding local
extensions through CMake's project hook. It creates `build/pyvenv` with the active
Spack Python interpreter. Generator dependencies follow the ACTS submodule's
requirements and its local codegen package; Python-only test/analysis tools are
recorded in a resolved build-local lock. Compiled dependencies remain in Spack.
A matching bootstrap fingerprint avoids repeated installation. `PYTHON`,
`BUILD_DIR`, `ACTS_BUILD_DIR`, `JOBS` and `CMAKE_ARGS` provide local overrides.

`make software-test` runs path guards, sensitive-surface controls, full tracker
Gen3 construction and a Geant4 material-recording smoke job. `make geometry`
executes128 deterministic straight tracks, `make analysis` compares its saved
surfaces with native DD4hep, and `make material` records8 geantino tracks.
`make all` builds detector and software; `make test` exercises both. Generated
outputs are kept under `build/jobs`. `make install` uses `build/installed` rather
than modifying the existing acts-nodd installation.

The algorithms retain ActsExamples framework interfaces. ACTS adapters live in
`source/ActsExamples`; Python job entry points live in `running`; the independent
geometry audit lives in `analysis` with a compatibility link from its old tools
path. Imported source notices and provenance are recorded in `source/NOTICE.md`.


## Prepared calorimeter functionality

The fourth migration step retains the prepared calorimeter, jet and EDM4hep
capabilities from ACTS fork8adca5eec. `source/Calorimeter` owns pure reconstruction,
`source/EDM` owns transient data, and `source/ActsExamples/Calorimeter` owns framework
algorithms/converters. `make calorimeter-test` runs the ten retained C++/pipeline
controls. `make calorimeter-run` steers the synthetic EDM4hep/jet example through
Python; `CALORIMETER_MODE=basic|jets|edm4hep|edm4hep-jets` selects the entry point.
`make calorimeter-analysis` lists persisted event/metadata entries.

These prototype algorithms and their existing limitations are retained. Moving
them does not change detector response, calibrate a calorimeter, or grant a design
review. Local options NODD_BUILD_CALORIMETER, NODD_BUILD_CALORIMETER_JETS and
NODD_BUILD_CALORIMETER_EDM4HEP can be overridden at software configuration time.
