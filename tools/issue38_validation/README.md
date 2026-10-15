# Issue #38 native tracker characterization

**PROTOTYPE; no design sign-off.** This tool answers the request for active
crossings and holes versus eta/phi and stacked material versus eta using the
complete DES025 tracker plus beam pipe. It reads the actual DD4hep/ROOT geometry,
including passive modules, supports, cooling, services and effective materials.
It does not use the incomplete ACTS thin-surface material representation.

The [retained results](../../docs/validation/issue38-review/results.md) identify
the executed configuration, checks and remaining scientific limits. No detector
geometry or material definitions are changed by this tool.

## Reproduce

Run the existing [ACTS Spack preflight](../../skills/acts-spack/SKILL.md) first.
Use a fresh export and output directory; native runs reject an existing summary
or ray archive. In the same activated DD4hep shell:

```sh
python3 -B tools/tracker_dd4hep/export.py --output /tmp/NEW-issue38-compact
python -B tools/issue38_validation/scan.py \
  --compact /tmp/NEW-issue38-compact/tracker.xml \
  --expected /tmp/NEW-issue38-compact/expected.json \
  --library-dir build/dd4hep/detector \
  --factory-source "$PWD" \
  --output /tmp/NEW-issue38-results
```

The runtime needs PyROOT, DD4hep, NumPy and Matplotlib. `--factory-source`
checks the associated factory source against the current checkout and records
its revision/status separately from binary hashes. It does not establish a
rebuild or silently rebuild shared dependencies. The actual run reused verified
local libraries, with matching factory source and a byte-identical compact.

The default sample has 41 eta values from −4 to +4, 64 uniform phi values with
phase 0.371 bins, and x=y=0 at z=−150,0,+150 mm: 7,872 straight rays. A separate
576-ray half-phi-bin control uses z=0 and integer eta values from −4 to +4.
The control is retained separately and excluded from plotted means. There is no
random seed. Grid counts can be changed with `--eta-bins` / `--phi-bins`.

Replot retained evidence without simulation imports:

```sh
python -B tools/issue38_validation/scan.py \
  --output docs/validation/issue38-review --plot-only
python3 -B -m unittest discover -s tools/issue38_validation -p 'test_*.py' -v
```

`summary.json` contains provenance, checks, ideal station definitions and
aggregates by eta, phi and vertex. `rays.json.gz` retains every ray's counts,
component material integrals and aggregate path length by native material;
its SHA-256 is verified before plotting. No millions of individual boundary
segments are stored. Compression is deterministic. `coverage.png` shows
vertex-averaged and z=0 maps plus count profiles; `material.png` stacks the
seven subsystem/service ownership categories recorded in the summary.

## Definitions and checks

- **Active patches:** unique native sensitive-volume crossings.
- **Physical sensors:** pixel chip islands deduplicate to their shared module
  substrate; short-strip sensors and each long-strip face count separately.
- **Logical stations:** system/layer with any pixel/short-strip active crossing,
  or both long-strip faces of the same module. Faces in different modules do
  not form a pair. Orphan faces and complete pairs are retained separately.
- **Holes:** ideal station-ID set minus reached station-ID set. Extra stations
  are reported separately and cannot compensate a hole elsewhere.

The ideal reference keeps declared active bounds and nominal barrel radii,
including the pixel B1 radius of 34 mm, and uses **present endcap disc datums**.
Pixel active radial bounds are 32.3–181.4550267061104 mm, distinct from passive
support/service bounds. This denominator differs from the frozen earlier
coverage studies; it must not be used as a numerical before/after comparison.
Sensor staggering and datum-to-active-plane offsets can produce holes/extras
at ideal boundaries. They are not all chip-seam losses.

ROOT integrates the exclusive deepest-volume boundary segments until the first
r=1200 mm or |z|=4100 mm boundary, enclosing all represented tracker services
and the full finite beam pipe. World air is excluded; component-enclosed
air/vacuum is included. Material lengths come from the native ROOT materials.
The scan fails on an unclassified volume, nonpositive material length,
invalid/zero navigation step, native sensitive-inventory mismatch or failed
closure/pipe control. No fixed spatial step or boundary nudge is used.

All native sensitive centres, local u/v axes where specified, and bounds are
compared with the export inventory. Tolerances are 1e−7 mm for centres/bounds
and 1e−9 for axes. Material stacks must close and their totals must equal
independent reintegration of aggregate material paths within 1e−12. The beam
wall path must equal wall_thickness×cosh(eta) within 1e−6 mm. These are software
checks, not physical acceptance criteria; ideal-bound tolerance is 1e−6 mm.

This is B=0 geometric coverage with a finite sampling measure. It excludes
detector response, digitization, alignment, field bending, scattering, energy
loss and reconstruction. It does not prove continuous luminous-volume
hermeticity, material-model correctness, or engineering feasibility. Existing
service-packing and engineering limitations remain open.
