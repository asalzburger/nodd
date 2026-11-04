# Two ECAL working baselines — validation campaign

Date:2026-11-04. [PR115](https://github.com/asalzburger/nodd/pull/115) restores the
ECAL source histories and issue114 EDM/I/O. [PR116](https://github.com/asalzburger/nodd/pull/116)
retains infrastructure, source/interaction provenance and exact unique token owners.
All design documents remain DRAFT/PROTOTYPE; results grant no human sign-off.

## Executed scope and environment

Both fresh CLI exports compose the maintained DES043 tracker with the complete
selected ECAL barrel/endcaps and local services. Tracker source/configuration
files are unchanged. Integrated IDs preserve pipe0, tracker1–7, SiW barrel8,
LAr10/11; standalone SiW endcap8 maps to9 only in the union. Material names and
recipes from the tracker remain intact; added ECAL definitions are namespaced.
The world has no magnetic field, HCAL, FCAL or solenoid volumes.

Executed node:acts-mac-studio-01.cern.ch; DD4hep1.38, ROOT6.40.04, Geant411.4.3,
EDM4hep1.1.1 and podio1.8 from the existing Spack environment. Setup/lockfile
fingerprints had changed, so actual imports/package identities were rechecked.
No shared installation or source checkout was modified. EDM build uses pristine
ACTS355ea68493b326956756c9386d2fd9eaf9328568 and its existing matching build.

## Results and retained failures

-32 SiW hardware controls and28 LAr geometry/service/transport controls pass.
-Five composition controls pass, including ID collisions, material/reference
 preservation, tracker names/beam0 and fail-closed component dependencies.
-Independent PhysVal reran those controls and four native EDM4hep CTest targets.
 The19 hit/cluster/skeleton cases and three-event ROOT round trip pass. Incorrect
 ACTS pin and mismatched ACTS build are rejected. See the [issue114 report](../issue114/README.md).
-28 project-record controls and36 session-logging controls pass locally after
 source/metadata integration; historical links were subsequently pinned to exact
 Git revisions to make each separate PR portable.

The first native construction failed because the composer renamed the tracker
factory’s hardcoded Beryllium. Only ECAL recipes are now namespaced. The next
construction succeeded but the auditor incorrectly expected an Assembly for
BeamPipe; the existing factory actually places bore and wall directly in world.
Both corrections are independently reviewed and have focused regression controls.

Both initial complete ROOT scans find zero overlaps/extrusions at1e-5mm (10nm),
with seed114 and unchanged default sampling. Their unmodified compact reports
are retained under `history/scan-before-cleanup-LAYOUT-001.json` and
`history/scan-before-cleanup-LAYOUT-002.json`. Launch source is60061f5. SiW scans
13,506,030 nodes with16,946,408 broad-phase candidates; LAr scans926,676 nodes
with39,244,493 candidates. ROOT mesh generation is the expensive stage; no
sampling/tolerance reduction was applied.

Those first processes abort at interpreter shutdown after saving their geometric
PASS reports: ROOT’s ClearThreadData throws `mutex lock failed: Invalid argument`.
The auditor now explicitly deletes the remaining TGeoManager before interpreter
thread teardown, matching the maintained tracker validator. A native BeamPipe
fixture exercises the exact auditor with24 checker threads and exits0. The
complete clean-exit replays use auditor source 6fdf31c3bd8e4c824106986914a316686cde5a06; both complete replays now pass with process exit0. The final compact reports are [LAYOUT-001](native-LAYOUT-001.json) and [LAYOUT-002](native-LAYOUT-002.json). Each checks10 native root system IDs and reports zero overlaps at1e-5mm. Mesh generation/checking took1402.14/37.2101s for01 and1413.04/36.1379s for02 on this node. The first geometric PASS reports remain separate from these successful end-to-end executions.

## Reproduction and artifact policy

Use the exact export, factory-build and full audit commands in the
[baseline tool README](../../../tools/calorimeter_baselines/README.md). Both
CLI invocations regenerate the maintained tracker; arbitrary reused tracker
compacts are unsupported. Manifests bind producer/configuration, expected,
compact and material hashes. Audit reports bind launch source/dirty state,
auditor bytes, compiled libraries, system IDs, overlap tolerance/seed and result.

Raw generated XML/expected maps, native geometry, event fixtures, caches and
bulky logs remain ignored under build or temporary storage. Only concise JSON
results/provenance and this reproduction recipe are retained. Git object review
finds no new event/ROOT payloads; the larger historical objects are figures.

## Scientific and engineering limits

The selectable packages are runnable tracker/ECAL stages within two shared
working design baselines. HCAL81/84/85 and merged FCAL88 retain their own design
and validation scopes. LAr HCAL regional adaptation, FCAL DD4hep/readout, magnetic
field/solenoid, connected services, machine pipe/shielding and complete detector
integration remain follow-up work. Neither geometry scans nor I/O tests establish
response, resolution, containment, jets, particle flow or engineering acceptance.

Digitization/clustering wrappers deliberately throw before writing outputs. The
initial capability is EDM4hep hit/cluster data, persistence and configuration
plumbing. Realistic calibrated digitization/clustering is tracked separately.
The [integration contract](../../design/inputs/ECAL-baseline-integration-2026-11-04.md)
retains all eleven outstanding PR75 review questions and follow-up gates.
