# Original Key4hep digitization reference runtime

This optional build installs the original Gaudi `DigitiserSiliconMip` processor
from pinned Key4hep sources over the existing ACTS Spack dependencies. It enables
the DES-044/issue #117 independent reference; it grants no physics acceptance.

```sh
make key4hep-submodules
make doctor
make key4hep JOBS=6
make key4hep-test
software/env/key4hep_run.sh python3 software/build/key4hep/install/bin/k4run /absolute/reference_digi.py
```

Sources are pinned by gitlinks and `software/env/key4hep-pins.json`. The build
verifies those revisions and rejects modified tracked sources. Boost's nested
source pins must be initialized by the explicit source target. Dependencies
already supplied by Spack, including DD4hep, Geant4, ROOT, EDM4hep, podio, TBB,
CLHEP, fmt and nlohmann/json, stay in the existing external environment. The
local Boost 1.90 build supplies the Python, thread, log and fiber components
missing from that environment's Boost configuration. It uses the same Boost
release as Spack. Range-v3 and Microsoft GSL supply missing headers.

All build products, installation, diagnostics and smoke events remain ignored
under `software/build/key4hep/` or `build/key4hep-smoke/`. No `spack install`,
concretization or shared-environment edit is performed. Activation applies only
to the command passed to `key4hep_run.sh`; use it for each reference command.
Gaudi and downstream packages explicitly share `python/` and `lib/` install
directories so activation and component discovery agree. Build logs are named `<package>-configure.log`, `-build.log`, `-install.log`.
To resume one failed stage, use `software/env/run.sh python3
software/env/build_key4hep.py --stage Gaudi` (or `boost`, `headers`, `k4FWCore`,
`reference`). Existing successful stages are preserved.

The wrapper includes upstream `RecCaloDigi/CMakeLists.txt` unchanged. It omits
unrelated clustering/reconstruction packages and their k4geo/sipm/FastJet/ONNX
dependencies. Runtime geometry uses the original `GeoSvc` and `GeoConstruction`
sources from k4SimGeant4, without its unrelated simulation actions. Set
`GeoSvc.EnableGeant4Geo=False` for digitization. All original physics algorithm
sources remain in their submodules. MarlinReco is also pinned for nODD's existing
standalone silicon backend; a separate Marlin/LCIO installation is unnecessary
for the EDM4hep-native reference route.

`make key4hep-test` creates a new synthetic two-event fixture, invokes the
original Gaudi processor, then checks persisted MIP energy, threshold selection,
64-bit cell IDs, truth links, event identity and retained simulation inputs.
It refuses to overwrite an existing work directory. Override `KEY4HEP_TEST_WORK`
when rerunning the Make target. A later rerun can use a new
path via `software/env/key4hep_run.sh python3 software/env/key4hep_smoke.py
--work /absolute/new/path`. This tests installation and processing, not the ODD
same-hit comparison, stochastic agreement or detector response.

For the full deferred comparison, follow
[the original-framework recipe](../../analysis/calorimeter_digitization/reference.md).
Source/build identity, steering and input/output hashes must accompany each
run. Keep original-framework output independent of the nODD helper.
