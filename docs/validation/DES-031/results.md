# DES031 — Executed SiW barrel prototype checks

**2026-10-13 · PASS within the isolated geometry/readout scope · DRAFT / PROTOTYPE.**
Engineering qualification, production integration and realistic calorimeter response
remain open. No human approval is inferred from the checks.

## Revisions and reproduction

The geometry was exported from clean source
`3d95e0b4485783fd3f62712527adc5b49869d277`, stacked on PR70 at
`654b85a48abeb38735ad7fe0866c5d1082882df7`. The strengthened native validator
ran at `abb836f5fbf0a2141106d222e6950dc0473410f2`; the geometry and compiled
factory were unchanged. Its dirty flag records untracked documentation figures,
with producer, factory, validator and helper hashes retained explicitly.
The supplemental readout checker ran while its new file was uncommitted at the
geometry source revision; its hash matches the subsequently committed checker.

Fresh activation actually verified DD4hep 1.38 (/7deaacd), ROOT 6.40.04,
Geant4 11.4.2 (/cpge6jj), Python 3.14.5 and installed Geant4 datasets. Existing
Matplotlib 3.11.2 rendered the scientific figures. Registry preflight returned 2
because setup/lockfile fingerprints changed; the warning and actual runtime
re-verification are recorded in the [session](../../../logs/design/SESSION-2026-10-13-siw-barrel.md).
No external package was installed and no full toolkit source staging is claimed.

[Reproduction bindings](reproducibility.json) retain compact, inventory, native,
checker and helper hashes. The large generated compact/inventory and persisted
ROOT files remain ignored build artifacts. Exact runtime results are retained
as [native.json](native.json), [readout.json](readout.json),
[ray-comparison.json](ray-comparison.json), [fixtures.json](fixtures.json) and
[transport.json](transport.json). The weaker first audit is preserved in
[history/native-initial.json](history/native-initial.json); it is superseded by
strict prism section/offset/scale checks and explicit helper identity/seed checks.

After activating the verified existing Spack environment and its DD4hep/Geant4
setup in the same shell, the executed build and principal checks were:

```sh
python3 -B tools/calorimeter_hardware/barrel_export.py --output build/calorimeter/barrel
cmake -S prototypes/calorimeter -B build/calorimeter/barrel-factory
cmake --build build/calorimeter/barrel-factory
python3 -B tools/calorimeter_hardware/barrel_native.py \
  --compact build/calorimeter/barrel/calorimeter.xml \
  --expected build/calorimeter/barrel/expected.json \
  --library build/calorimeter/barrel-factory/libnODDCalorimeterPrototype.dylib \
  --output build/calorimeter/barrel/native.json --overlap-seed 31
python3 -B tools/calorimeter_hardware/barrel_readout.py \
  --compact build/calorimeter/barrel/calorimeter.xml \
  --expected build/calorimeter/barrel/expected.json \
  --library build/calorimeter/barrel-factory/libnODDCalorimeterPrototype.dylib \
  --output build/calorimeter/barrel/readout.json
python3 -B tools/calorimeter_hardware/barrel_compare.py \
  --expected build/calorimeter/barrel/expected.json \
  --native build/calorimeter/barrel/native.json \
  --output build/calorimeter/barrel/ray-comparison.json
python3 -B tools/calorimeter_hardware/barrel_fixture.py --directory build/calorimeter/barrel
python3 -B tools/calorimeter_hardware/barrel_transport.py \
  --directory build/calorimeter/barrel --output build/calorimeter/barrel/transport.json
python3 -B tools/calorimeter_hardware/barrel_plot.py \
  --directory build/calorimeter/barrel --output docs/design/figures/DES-031
python3 -B -m unittest discover -s tools/calorimeter_hardware -p 'test_*.py'
```

Linux uses the corresponding `.so`. Three DDSim runs between fixture creation
and saved-hit inspection used 10 GeV muons, FTFP_BERT, zero field, one event each,
seeds 45/46/47 and the fixture directions in `fixtures.json`. The hardware-tool
[README](../../../tools/calorimeter_hardware/README.md#detailed-siw-barrel-des031)
provides the full transport invocation. CMake reported existing upstream
policy/CLHEP warnings; these were retained without suppression.

## Results and physical interpretation

| Executed check | Result |
| --- | --- |
| Standard-library hardware controls | 32 passed: ten barrel controls and 22 inherited cassette/assembly/endcap controls |
| Native shapes / placements | 14,406 / 37,684 checks; centred, unscaled two-section prisms and restricted CSG checked explicitly |
| Full ROOT overlaps | Zero at `1e-5 mm` (10 nm), seed 31; 9,181,538 physical nodes and 9,792,627 candidates |
| Physical sensitive IDs | All 359,904 sensor-volume IDs round trip with distinct parents |
| Supplemental module electrodes | All 552 module addresses: 141,312 pad references and 4,416 closed-boundary tie points |
| Native mass / composition | 299.002914809496 t; agrees with analytic 299.002914809489 t; maximum composition delta 1.11e−16 |
| Independent finite silicon rays | All 60 agree with ROOT; five centre-plane approximations differ at finite-thickness boundaries |
| Saved Geant4 hits | Three fixtures, one positive-energy hit each with correct parent and pad IDs |

The native report includes every constituent mass and signed eta/phi material
ray. For example, the central `eta=0, phi=0.03` ray crosses all 48 sensitive
layers and 34.7771 radiation lengths. At the sector centre `phi=0`, the same eta
crosses only 22 layers because even-column boards leave a central gap. At
`eta=0.25, phi=0.03`, staggering gives 31 native finite-silicon crossings versus
the aligned control's zero centre-plane crossings; it still leaves significant
service/guard cracks. Sampled zero-crossing azimuths and active-face fractions
are geometric results, not efficiencies or validated acceptance requirements.
Only barrel material is plotted: tracker, solenoid, endcaps and external
services are excluded. No barrel crossings at eta ≥ 1.6 are a barrel-boundary
result and say nothing about combined barrel/endcap coverage.

Read-only SysArch and PhysVal reviews independently assessed the committed
geometry source `3d95e0b...`; their assignments, actual checks and limitations
are curated in the session. PhysVal identified the initial prism-contract and
helper-identity validation gaps. The strengthened audit and negative controls
address them without changing geometry, tolerances or inherited gates. These
reviews do not grant design sign-off.

The transport fixtures contain one selected board in one selected layer/sector,
with the remaining local layer hardware retained. They test conversion and
saved IDs/positive energies at central, positive-z and negative-z positions.
They do **not** establish complete-barrel transport, shower response, energy
resolution, calibration, jet or particle-flow performance. ACTS conversion,
hydraulic/thermal/load qualification, manufacturing tolerances and external
service routes remain future work.
