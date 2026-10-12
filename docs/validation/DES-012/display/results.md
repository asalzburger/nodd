# DES-012 — ROOT display persistence

2026-09-30; visual-only follow-up in PR #30, starting at
`0a65fa5` (source hashes below identify the implementation).

A material-family palette in `detector/config/display.json` supplies standard
ROOT indices and opacity. DD4hep RGB matching alone selected a nearby blue,
so the shared C++ display helper assigns the exact configured index to each
TGeoVolume's line and fill attributes. Tube and coolant daughters now receive
explicit styles. Materials and geometry are unchanged.

CMake build and CTest passed **3/3** (17.48 s). The new test exports geometry,
then imports it in a fresh ROOT-only process without loading the detector factory,
creating custom colours or executing a recolouring macro.

[Round-trip results](roundtrip.json): **36550 placed solid
volume styles checked**, including exact indices, RGB, transparency, fill colour,
visibility and daughter visibility. ROOT version 6.40.04.
The generated binary is ignored and reproducible at
`build/dd4hep/detector/pixel-barrel.root`; its SHA-256 is retained in the report.
Interactive GUI rendering was not tested.

[Physics comparison](physics-comparison.json) against the retained nominal run
is exact for counts, total mass, every material's properties/inventory, all75
navigation rays, IDs, sensor/entity residuals and overlap results. The new
[geometry report](geometry.json) records the executed source/library hashes.
Previous evidence and its artifact manifest were not replaced.

Initial test corrections: limit the display audit to physically placed volumes
(DD4hep also registers unused Air defaults), decode PyROOT's Char_t transparency
as a byte, and replace approximate RGB lookup with explicit standard colour
indices. No geometry or numerical tolerance was changed.
