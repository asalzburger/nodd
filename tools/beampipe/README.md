# Straight beampipe (DES-024)

The user-requested 0.8 mm Be wall has provisional inner radius27 mm, outer
radius27.8 mm and half length4000 mm. Edit `detector/config/beampipe.json`.
The wall is passive and tagged BEAMPIPE; the numerical vacuum bore is separate.

```sh
cmake -S . -B build/dd4hep -G Ninja -DBUILD_TESTING=ON
cmake --build build/dd4hep --target nODDBeamPipe Components_nODDBeamPipe nodd-beampipe-compact
ctest --test-dir build/dd4hep -R '^beampipe-' --output-on-failure
```

Use the verified DD4hep environment. The compact is
`build/dd4hep/detector/beampipe/beampipe.xml`. On macOS load the absolute factory
library in Python before parsing; changing a loader variable after startup is
insufficient. Native checks independently verify dimensions, elemental density,
mass, zero overlaps, bore contents and15 material rays. No vacuum or structural
qualification is claimed. See the retained DES-024 report.
