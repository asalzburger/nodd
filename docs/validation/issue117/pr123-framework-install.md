# PR #123 — original digitization framework installation

Date: 2026-11-06. Scope: user-authorized local software installation for
DES-044 / issue #117. Detector geometry and response settings are unchanged.

Installation is feasible. The earlier [blocked task](pr118-review-request.md)
probed only preinstalled packages and did not attempt a build. Its restricted
scope and the then-missing runtime did not establish technical impossibility.
The subsequent user instruction authorizes source acquisition and installation
against the existing ACTS Spack environment.

## Source identity and build boundary

| Submodule | Exact source revision | Role |
| --- | --- | --- |
| `software/submodules/Gaudi` | `bdbe77445b2e1f4168de88a080945b491d133d5b` | Gaudi41.0 event framework |
| `software/submodules/k4FWCore` | `f95187d5cd69d1e079e170e4e2e7f6d828e6a92d` | k4FWCore1.8 I/O and ID services |
| `software/submodules/k4RecCalorimeter` | `03b3676cecbdf85818f6de159ecf90ffe2482cec` | Original RecCaloDigi algorithms |
| `software/submodules/k4SimGeant4` | `339b3842109f45a269929d9896c3d8279e69b83c` | Original GeoSvc and GeoConstruction |
| `software/submodules/boost` | `1bed2b0712b2119f20d66c5053def9173c8462a5` | Boost1.90 required component build |
| `software/submodules/range-v3` | `5ba39112d2eafbb3c851a16a537f29b445022998` | Range headers with modern libc++ compatibility |
| `software/submodules/GSL` | `2828399820ef4928cc89b65605dca5dc68efca6e` | Microsoft GSL4.2 headers, distinct from GNU GSL |
| `software/submodules/MarlinReco` | `255967eb855ebbc8f75ebaac190b268b63332e8b` | Original selected source for the nODD silicon helper |

The wrapper includes the unchanged upstream RecCaloDigi CMake file and the
complete original algorithm sources. The original geometry service is compiled
from k4SimGeant4 without its unrelated simulation actions. A digitization job
uses `GeoSvc.EnableGeant4Geo=False`. Other calorimeter reconstruction packages
and their k4geo/sipm/FastJet/ONNX dependencies are outside this minimal runtime.
No Marlin/LCIO installation or format bridge is needed for the EDM4hep-native
reference. MarlinReco's gitlink separately makes the existing helper source
reproducible. All submodules retain their upstream sources unchanged.

The external Spack environment supplies DD4hep1.38, Geant4 11.4.3,
ROOT6.40.04, EDM4hep1.1.1, podio1.8, TBB, CLHEP, fmt and nlohmann/json.
Its Boost1.90 build omits Python/fiber/thread/log components required by Gaudi,
so those and their Boost dependencies are built in the local installation,
from the same Boost release. Range-v3 and Microsoft GSL are also local.
Optional Gaudi AIDA/HepPDT/XercesC/ZSTD, examples and upstream test suites are
disabled; none is required by the exercised original digitizer. This is not
a claim that every optional Gaudi or Key4hep feature has been qualified.

The node is `acts-mac-studio-01.cern.ch`; AppleClang21 and C++20 are used for
Gaudi/Key4hep. Python3.14.5 and CMake4.4 come from the existing environment.
The initial stale-fingerprint warning was reported before actual verification.
DD4hep/DDG4 imports and all twelve Geant4 dataset presence checks passed.
The setup SHA-256 is
`53ed8ad1854b592a01f6b9f9d3b8b49dbbb8a06bddb6677805d4099af2432a97`;
the Spack lock SHA-256 is
`d51753ae83a710850d06413f3dc0a6bf6ad18554d3911108774c48671dda2cde`.
No shared Spack package, setup, lockfile or registry was modified.

## Reproduction and verification

From the repository root:

```sh
make key4hep-submodules
make doctor
make key4hep JOBS=12
make key4hep-test
software/env/key4hep_run.sh python3 software/build/key4hep/install/bin/k4run /absolute/reference_digi.py
```

The install is under ignored `software/build/key4hep/install`; build logs and
source-pin receipts are beside it. The synthetic test retains full ROOT files
and steering only in ignored local outputs. It refuses to overwrite a previous
fixture. [Build instructions](../../../software/source/Key4hepReference/README.md)
explain activation, partial-stage resumption and repeat-test paths.

The build/install completed successfully. The executed Make smoke command was:

```sh
make key4hep-test KEY4HEP_TEST_WORK="$PWD/build/key4hep-smoke-5"
```

It passed with **two events, two input cells, one accepted cell, one rejected
cell and one empty event**. The accepted energy agrees with **2 MIP** (maximum
absolute residual 0.0000002384185791015625 MIP; predeclared tolerance
0.000002 MIP). Full 64-bit cell
ID, event header, original SimHits/contributions, truth-link endpoints/weight,
position and earliest-contribution timing checks passed. Original Gaudi
initialization, processing, finalization and output persistence succeeded.
The geometry is a world-only software fixture with copied, hashed DD4hep
material/element catalogues; no production geometry is involved.

The compact [runtime receipt](pr123-runtime.json) records source pins,
installed library hashes, fixture hashes, denominators and checks. It contains
no event-level payload. The full local events and k4run log remain ignored.
Upstream Gaudi/Key4hep test suites and nODD's physics campaign were not run.

## Remaining scientific gates

The installation smoke uses synthetic values; it does not satisfy the full
ODD same-hit comparison, noise-on distribution agreement, digitized muon MIP
spectrum/threshold efficiency or e/gamma linearity/resolution request. Those
remain separate follow-up work using the preserved
[original-framework comparison recipe](../../../software/analysis/calorimeter_digitization/reference.md).
DES-044 stays DRAFT/PROTOTYPE. Endcap geometry issue/PR disposition remains a
maintainer decision. No physics or detector-design acceptance is inferred.

The [paired session record](../../../logs/codex/SESSION-2026-11-06-pr123-framework-install.md)
retains failed setup/build attempts and corrections. Six source-catalogue
entries document newly introduced build tools; existing RecCaloDigi and
MarlinReco source entries retain their selected identities.
