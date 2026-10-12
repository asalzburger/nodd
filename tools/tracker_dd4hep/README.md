# BeamPipe + complete Tracker DD4hep entry point

DES025 composes the existing maintained selected subsystem exporters. All
geometry inputs remain owned by their original DES019–023 producers; standalone
controls stay available. The user-requested DES024 beampipe is included.

```sh
cmake -S . -B build/dd4hep -G Ninja -DBUILD_TESTING=ON
cmake --build build/dd4hep -j 8
python tools/tracker_dd4hep/validate.py \
  --compact build/dd4hep/detector/tracker/tracker.xml \
  --expected build/dd4hep/detector/tracker/expected.json \
  --library-dir build/dd4hep/detector --output build/tracker-native.json
```

Use the verified ACTS Spack/DD4hep runtime. All five factory libraries and their
DD4hep component registries are built in `build/dd4hep/detector`. The default
compact is `build/dd4hep/detector/tracker/tracker.xml`; source compacts and exact
source hashes are preserved in its `components/` directory. Material names are
scoped where recipes conflict. Pixel IDs1–3 remain; standalone strip root system
IDs3–6 translate to4–7 in the assembly, all other fields unchanged. The combined
expected inventory records each original strip system ID.

The DES023 cumulative long-strip corridor replaces the standalone barrel trunk.
Shared short-strip trunks partition at source boundaries, conserve payload
constituents and keep one carrier/unused-air volume. This does not qualify
service-capacity limits. No sensor or carrier datum is moved.

ACTS: use the companion `Examples/Nodd` Gen3 adapter in acts-nodd. Its default
`getNoddDetector(nodd_dir=..., gen3=True)` reads this compact, obtains sensitive
planes directly from native DD4hep and builds connected Gen3 volumes/portals.
`gen3=False` supports DD4hep-only material recording. `geometryReport()` exposes
actual source identities, transforms and bounds for validation. Try-all per-layer
navigation prioritizes correctness for staggered chips/paired tilted strips;
acceleration binning is a future performance task. Native Be/silicon materials
are represented as thin surface slabs; remaining services require a dedicated
material mapping campaign. No ODD material map or field is substituted.

The review proposal uses27mm inner/27.8mm outer pipe radii and opens only passive
pixel apertures to28.8mm: old27mm apertures intersect the pipe.138 parts change;
10.13g of foam/CFRP/unused air is removed, all non-filler service and cooling
inventory retained. Sensor geometry and outer service bounds remain unchanged.
The choice is centralized in `detector/config/tracker.json` and documented in
DES025. `--keep-pixel-aperture` exports the unamended control, whose overlap test
must fail. `--pixel-aperture-mm` produces an explicit alternative for review.

After activating ACTS, run its `Examples/Nodd/Scripts/nodd_geometry_validation.py`
with `--nodd-dir "$PWD" --output build/gen3 --tracks 128`. Independently compare
and inspect the saved ROOT crossings:

```sh
python tools/tracker_dd4hep/check_gen3.py --report build/gen3/surfaces.json \
  --expected build/dd4hep/detector/tracker/expected.json --output build/gen3-check.json
python tools/tracker_dd4hep/check_navigation.py --directory build/gen3 \
  --tracks 128 --output build/navigation-check.json
```

[DES025 results](../../docs/validation/DES-025/results.md) retain actual native,
Gen3, Geant4 and regression checks. The adapter is in
[ACTS fork PR3](https://github.com/asalzburger/acts/pull/3). DD4hep native validation
is registered as a CTest; Gen3 validation requires the separately built ACTS runtime.
