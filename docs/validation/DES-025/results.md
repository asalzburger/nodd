# DES-025 — Complete DD4hep tracker and native Gen3 conversion

Date: 2026-10-08. Design status: DRAFT. User-authorized software integration;
no engineering acceptance or human sign-off is inferred.

The assembly includes the DES-024 beampipe, DES-019 trimmed mixed pixel baseline,
selected phi-tilted DES-020 short-strip barrel, DES-021 short-strip endcap and
DES-022/023 paired long strips. The companion adapter is
[ACTS fork PR3](https://github.com/asalzburger/acts/pull/3), based on the existing
fork build-fix branch. [nODD PR57](https://github.com/asalzburger/nodd/pull/57)
provides the independent pipe first. The source models and old evidence remain
available; the assembly changes are explicit in [integration.json](integration.json).

## Actual results

- Full build and 10/10 CTests passed in 256.03 s. This includes six pixel export,
  native and ROOT roundtrip controls, two pipe controls, six pure integration
  guard tests in one CTest, and the complete native tracker audit.
- [Native audit](native.json): 680,700 physical nodes; 45,646 sensitive elements;
  unique globally packed DD4hep volume IDs and decode roundtrips. All 50 source
  role counts match the 680,292 expected entities; extra world/assembly nodes
  account for the difference. Sensitive centre residual ≤5.22e-13 mm and normal
  residual ≤2.49e-16; signed in-plane axes and dimensions also match.
- 1,156 named material inventories match their exclusive expected volume and
  mass at relative tolerance 1e-6 (absolute tolerance 1e-6). Full ROOT overlap
  audit at 1e-5 mm found zero overlaps/extrusions. Minimum analytical passive
  pixel clearance to the pipe is exactly 1 mm. Twenty-seven ROOT rays over
  eta [-4,4] and three azimuths reproduce the Be path 0.8*cosh(eta) mm within
  1e-7 mm and retain actual material/crossing records.
- [Gen3 comparison](gen3.json): all 45,646 sensitive surfaces match native
  source identities, centres, XYZ frames and bounds; geometry IDs are unique
  and nonzero. There are 117 volumes with connected portals. System counts are
  pixel barrel 6,794; negative/positive pixel endcaps 2,506 each; short barrel
  8,064 and endcap 4,320; long barrel 13,968 and endcap 7,488.
- The actual shared Be portal has radius 27.4 mm, half length 4,000 mm, Z=4,
  thickness 0.8000000119 mm and X0=352.7598267 mm. The small deviations from
  native shell thickness/X0 reflect ACTS material float storage; native X0 is
  352.7598205 mm. The cylinder represents the wall at its mid-radius.
- [Saved Gen3 propagation](navigation.json): all 128 seeded 10 GeV straight
  probes completed (seed42, one event/thread, uniform eta [-4,4]). Each has
  11–26 sensitive crossings, at least 26 portal crossings and 12 material
  crossings. All seven systems are crossed collectively. Saved ROOT steps are
  matched back to reported geometry IDs. No field, energy loss or scattering
  is enabled for this software navigation check.
- ACTS adapter built/installed; 385/385 C++ tests passed in 75.65 s. Six focused
  Python tests passed in 106.60 s, including a Geant4 material-recording event
  with eight probes (seed228), saved ROOT entries and finite positive X0 totals.
- Scoped ACTS pre-commit passed. Required whole-repository pre-commit ran and
  failed only on existing zizmor findings in unmodified workflows: final summary
  one low, two medium and one high; all other hooks passed. No gate was weakened.

## Integration amendments and controls

Pipe convention: inner radius 27 mm, outer 27.8 mm, provisional ±4 m extent.
The optional radius clarification was unanswered while independent work
continued; these values are explicit review assumptions, not inferred approval.

The old 27 mm passive pixel apertures intersect the new pipe. The combined
entry point enlarges only 138 passive annuli to 28.8 mm, removing 10.128297365 g
of support filler/unused air. No silicon, transform, ID or disc datum changes.
Non-filler conductor/coolant/pipe and spreader inventories are preserved;
effective mixtures are renormalized. Original standalone inputs and artifacts
remain unchanged. Outer service limits are unchanged. This is a documented
DES-025 amendment for review, with no mechanical-clearance qualification.

Pixel system IDs 1–3 remain. Standalone strip root systems 3–6 translate to 4–7
in the assembly to resolve the pixel/short-strip system3 collision. Every other
placement field and readout bit layout is unchanged; original system IDs are
retained in the expected inventory. No sensor is dropped or moved.

DES-023 already includes cumulative long-strip barrel/endcap trunk loads; the
assembly removes the duplicated standalone barrel trunk and retains its collector.
Overlapping short-strip trunk corridors are partitioned at all source axial
boundaries, summing payload and retaining one carrier/unused-air inventory.
Largest constituent roundoff residual is 2.12e-6 mm³ (relative ≤1e-10).
This does not establish that existing fixed service packing constraints pass.

[Failed controls](failed-controls.json) preserve the initial 14 pipe overlaps
and the later zero-overlap run which still failed material accounting: pixel
cooling used untranslated `tube_material`/`coolant_material` attributes. Both
references now follow the same namespace translation as `material`; a regression
test catches this error. Negative controls also catch excess service payload,
reflected sensor axes, duplicate ACTS IDs and incorrect pipe thickness.

Early ACTS attempts exposed changed surface/visitor APIs and off-axis layer
centres from asymmetric sensor extents. Current APIs are used; cylindrical
containers remain coaxial while native sensor frames remain exact. Pipe material
is assigned to the one shared portal after volume construction, preserving it
through portal fusion. Early writer imports were corrected to the ROOT namespace.
Earlier setup, loader and ROOT cleanup failures are retained in DES-024 results.

## Reproduction and execution provenance

Use the activated compatible ACTS/DD4hep runtime described in the
[tools README](../../../tools/tracker_dd4hep/README.md). Core commands:

```sh
cmake --build build/dd4hep -j 8
ctest --test-dir build/dd4hep --output-on-failure
python /path/to/acts/Examples/Nodd/Scripts/nodd_geometry_validation.py \
  --nodd-dir "$PWD" --output build/gen3 --tracks 128
python tools/tracker_dd4hep/check_gen3.py --report build/gen3/surfaces.json \
  --expected build/dd4hep/detector/tracker/expected.json --output build/gen3-check.json
python tools/tracker_dd4hep/check_navigation.py --directory build/gen3 \
  --tracks 128 --output build/navigation-check.json
```

Native execution was dirty nODD7926b800 plus the exact exporter, compact,
expected-inventory and factory hashes in native/integration reports. ACTS
execution was dirty555c66e71 plus exact source and installed library hashes.
The inherited unrelated local binding edits were preserved. Publication commits
are distinct from these executions and never replace their hashes. Runtime:
ROOT6.40.04, DD4hep1.38, Geant4 11.4.2 and Python3.14.5. Persisted native,
Gen3 and ROOT-output hashes identify actual artifacts; large generated XML,
ROOT and detailed surface arrays remain ignored local build products.

These checks establish construction, source conservation and sparse software
navigation. Original coverage/guard, warm thermal, sag/joint and fixed service
packing limitations remain. Try-all navigation needs later acceleration study.
Passive supports/services need dedicated material mapping; no ODD map is used.
Luminous-region acceptance, magnetic-field propagation, alignment, response and
reconstruction performance remain separate validation work. Length, vacuum,
pipe supports/flanges and engineering clearance remain provisional/unqualified.
