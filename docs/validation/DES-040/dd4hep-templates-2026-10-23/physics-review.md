# Independent PhysVal review of the template refactor

Assignment `PR94-TEMPLATES-PhysVal`; exact reviewed revision `d5803de8bac013d918140585bd2c00de15632011`. The complete PhysVal mandate was explicitly passed to a separate generic agent context; native profile loading was not verified. The coordinator curated this report from the returned assessment. The reviewer changed no files and made no commits, new DDSim runs, shared installation changes or further delegations. No human approval is supplied.

**No actionable defects found for the bounded representation refactor.**

The reviewer inspected implementation before author conclusions, including `templates.py` factor/expand/XML routines, the native template and placement loops in `Muon.cpp`, and the source/native checks in `validate.py`. Actual source membership determines the recurrences; centring offsets preserve source frames; smaller hardware-clearance families remain distinct. No repacking or uniform eta grid is introduced.

Actual independent checks:

- Compared every original manifest entity with baseline `e168107549205d424d51077d31db6dbc64b72765`. All 936 source IDs, chamber/station/side IDs, vertices, origins, bases and depths are exactly unchanged. Toroid/material inputs, runner and empty-event-container action are unchanged.
- Verified source/test/compact bytes against the pinned revision and the loaded factory against the recorded digest.
- Ran `python3 -B -m unittest tools.muon_dd4hep.test_export tools.muon_dd4hep.test_run_validation -v`: all 15 tests passed, including rehashed XML mutations and template/recurrence/identity/native-gate/persisted-count controls.
- Independently re-executed the native audit without writing reports: 936 unique chamber placements, 22 shared Volume objects and 22 shared Solid objects, three warm groups, 288 CSG primitive instances, 25,248 occupancy probes, and zero overlaps/extrusions at 1e-5 mm. Maximum native world-vertex residual was 1.6852000649168165e-14 m; the existing 1e-10 m tolerance is unchanged.
- Confirmed XML decreases from 583,236 to 28,900 bytes, with 22 shape definitions, 21 phi orbits and 56 rows. Six longitudinal loops cover 288 placements; no explicit residual placements are needed by this source.
- Independently inspected both retained ROOT files. Original SHA256 `098ea5e0766a31295ee9a945a510e9d84b9cce3d9a58bc687c1c1845bb18e5f9`, 88,991 bytes; refactor SHA256 `42cfc82eca58469bd2734cd317a34dcf658855fbe36c505562fd497fcef584f3`, 88,765 bytes. Both match their recorded digests, have 1,000 EVENT entries and only an MCParticles event branch.
- Each event has one parentless PDG22 primary at 20 GeV. Primary momenta, starting vertices, times and masses match exactly event by event, as do particle multiplicities. This does not assert equality of every secondary trajectory.

Exact raw-source preservation is distinct from framework reconstruction residuals around 1.7e-14 m, well below the unchanged numerical tolerance. The clean transport replay is from implementation `237b54ce0fc346a918f077995aded5f54cea6295`; the review target includes its evidence at `d5803de8bac013d918140585bd2c00de15632011`. Scientific source geometry stays PR90 merge `cae3a72f3b1c98edaf9bc28a84d019142606ba25`.

The preflight again warned of changed setup/lock fingerprints; fresh activation and native execution verified DD4hep 1.38 / ROOT 6.40.04. Only the coordinator's journal Markdown was dirty. Air-envelope, flat-theta transport is a geometry smoke test; material response, full-system clearance, engineering sign-off and production integration remain outside this assessment.
