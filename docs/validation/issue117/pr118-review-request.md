# PR #118 — digitization review request: blocked execution

Date: 2026-11-06. Status: **BLOCKED**, isolated **PROTOTYPE** remains unsigned.
Examined source: `da94b693a0034cb211e96f42dee83970deb59886`.
Task request: `118-35344007412`.

The [reviewer request](https://github.com/asalzburger/nodd/pull/118#issuecomment-6684090541)
asks for Key4hep agreement before further digitization plots, and proposes moving
the endcap geometry investigation to a separate issue. This follow-up records
the runtime blocker and outstanding evidence. It does not satisfy the reference
or physics gates of [issue #117](https://github.com/asalzburger/nodd/issues/117)
or [DES-044](../../design/DES-044-calorimeter-digitization.md).

## Runtime checks actually run

The node is `acts-mac-studio-01.cern.ch`. The registry preflight
`python3 skills/acts-spack/scripts/preflight.py` returned **2**: its recorded
setup and Spack lockfile fingerprints differ. The warning was reported before
dependent checks. Read-only re-verification then ran:

```sh
software/env/run.sh python3 software/env/doctor.py
```

This returned **0**: actual DD4hep/DDG4 imports passed, DD4hep is 1.38
(`/3yd4hz36kt6sj5eyvpgdlbi2aaux6ghv`), Geant4 is 11.4.3
(`/wfg55xionuknvzyoc24tu7er2xhapk2z`), and all twelve Geant4 datasets reported
installed. Presence checks do not establish simulation readiness. Current
setup SHA-256 is
`53ed8ad1854b592a01f6b9f9d3b8b49dbbb8a06bddb6677805d4099af2432a97`;
Spack lock SHA-256 is
`d51753ae83a710850d06413f3dc0a6bf6ad18554d3911108774c48671dda2cde`.
No registry or machine configuration was changed.

In the activated environment, `spack env status` identified the existing
`ci-dependencies` environment; `spack find --format '{name}@{version} /{hash:7}'
gaudi k4fwcore k4reccalorimeter marlin marlinreco lcio` reported no matching
package. The surrounding diagnostic shell returned 0 because it continued to
other probes; that status is not a successful package-availability check.
The separate required-runtime probe was:

```sh
software/env/run.sh python3 - <<'PY'
import importlib.util
import json
import shutil
import sys
commands = {name: shutil.which(name) for name in ('k4run', 'gaudirun.py', 'Marlin', 'ddsim')}
modules = {name: importlib.util.find_spec(name) is not None for name in ('Gaudi', 'k4FWCore', 'Configurables')}
print(json.dumps({'commands': commands, 'modules': modules}, indent=2))
sys.exit(0 if commands['k4run'] and all(modules.values()) else 2)
PY
```

It returned **2**: `k4run`, `gaudirun.py` and `Marlin` were absent; `Gaudi`,
`k4FWCore` and `Configurables` were unavailable. `ddsim` was found in the
existing Spack view. This establishes a missing reference runtime in the
configured environment, not the absence of every possible external installation.
Sandbox `sysctl` and `ps` denials occurred during setup; they were retained as
limitations and no permissions were changed. No transport, digitization, CTest,
original-framework execution or new physics plot was run for this request.

## Outstanding reviewer evidence

The following is a disposition of the request, not an executed campaign or new
detector acceptance criteria. The existing [validation plan](validation-plan.md)
and [reference recipe](../../../software/analysis/calorimeter_digitization/reference.md)
remain the preparation for resumed work.

| Requested result | Required evidence on resumption | Current disposition |
| --- | --- | --- |
| Noise-off Key4hep cell agreement | Identical hashed ODD SimHits and ordered events; pinned full `DigitiserSiliconMip` processor; matched MIP scale, integration, range and threshold; accepted-cell and per-cell energy comparison | Blocked by missing original runtime. The synthetic comparator and shared-kernel tests do not establish this agreement. |
| Noise-on distribution agreement | Same input and response settings, independent ensembles for ROOT versus CLHEP random engines, declared statistical comparison and uncertainty; do not require equal seeds to give equal draws | Not run; deterministic full-processor check comes first. |
| Digitized single-muon MIP spectrum | Held-out single-crossing/path-qualified muons; raw and digitized spectra in MIP units; fitted MPV and uncertainty with a frozen independent calibration; separate noise-off/on and threshold effects | Not run for this request. Existing binned pre-deferral spectra do not provide the full requested validation. |
| Signal/noise and MIP efficiency versus threshold | State signal definition (e.g. fitted MIP MPV) and signed prethreshold pedestal RMS; efficiency denominator includes all selected primary crossings, including rejected/zero-signal trials; report threshold units, counts and uncertainties, with noise occupancy separately | Missing evidence; the configured unit-noise fixture cannot supply a detector measurement. |
| Single e/gamma linearity and resolution | Separate species, energy and direction; paired raw, noise-off and noise-on digitized distributions on the same events; one held-out fixed calibration, all-event denominators and uncertainties | Not run; existing electron-only previews omit photon and complete paired controls. Raw silicon energy and its RMS/mean alone do not establish calibrated shower resolution. |
| Endcap geometry scope | Maintainer-selected separate issue and disposition of existing tiling evidence | Proposed split remains unresolved. No issue was opened, existing evidence was not removed and no endcap geometry was changed. |

The raw tiled-endcap/control results remain in the separate
[geometry-response report](tiling-response.md). They cannot satisfy a digitizer
reference gate. No response parameter, geometry or calibration was retuned.

## Inputs and human decisions needed

Provide an authorized, accessible runtime containing the pinned
`k4RecCalorimeter` `RecCaloDigi` plugin (or identify and review a replacement
revision), with compatible Gaudi/k4FWCore/DD4hep/EDM4hep/podio, its exact build
identity and setup instructions. The prepared recipe pins
`03b3676cecbdf85818f6de159ecf90ffe2482cec`; merely finding `k4run` would not
verify that plugin. An independently executed same-hit reference with full
input/output hashes, retained SimHits/EventHeaders, steering and runtime
identity is another possible handoff, subject to provenance review.

The required software input must be available before the previously deferred
study can resume. A maintainer must decide the endcap issue/PR split. This task
does not authorize installing shared dependencies, opening issues, or deleting
prior evidence.
DES-044 remains DRAFT; no human sign-off or acceptance is inferred.

The [paired session record](../../../logs/codex/SESSION-2026-11-06-pr118-review-request.md)
records commands and repository checks. Public discussion was refreshed through
the read-only GitHub connector and curated in `interactions/pr-0118.json`.
No new literature source or detector-parameter provenance was introduced.

The required project-record validator returned **1** because this isolated Git
store cannot resolve pre-existing merge evidence
`78bc60bb6da0c9d234baf00d37cadea9dd4964b4`. The reference is present in the
captured input's tracking record; no historical record or gate was weakened to
remove the failure. Full project-record verification remains required in a
checkout containing that evidence.
