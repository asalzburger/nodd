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
