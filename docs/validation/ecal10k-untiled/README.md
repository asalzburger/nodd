# Continuous silicon ECAL control

**PROTOTYPE: deliberately unbuildable geometry control requested on
2026-11-12.** Compare the [original tiled 10k study](../ecal10k/README.md)
with continuous sensitive silicon across the existing DES-030/DES-031 sector
carrier faces. The [prospective protocol](protocol.md) fixes the intervention,
observable, paired uncertainty treatment and scope before production.

Review package: [draft PR135](https://github.com/asalzburger/nodd/pull/135),
stacked on the original study in draft PR134.

## Geometry intervention

Replace the original active and guard wafers with one 0.5 mm sensitive silicon
sheet per sector/layer: 768 barrel sheets and 1,536 sheets across both endcaps.
Keep the original 48-layer pitch, planes, 16-sector transforms, beam aperture,
negative-end rotations, tungsten, cooling, electronics, wafer films and other
nonintersecting passive pieces. Preserve the inherited 1 mm carrier half-seam;
this is continuous silicon **within each existing carrier**, not a closed
silicon cylinder with no mechanical sector seams.

The barrel sheets span |z| ≤ 3900 mm at radial x = 1702.5 + 10.9·l mm.
Endcap sheets span 100 ≤ x ≤ 2223.2 mm at local z = 2.5 + 10.9·l mm.
Both use the inherited sloping carrier face |y| ≤ x·tan(pi/16) − 1 mm.
Exact sloped Boolean faces preserve the barrel boundary through wafer thickness.

Full sheets fill guards, module/slab gaps and service margins together. Their
intersections with the barrel rails/slab-end frames and endcap supported frame
are subtracted from aluminium to avoid overlaps. The added silicon is
2,475.64 kg; removed aluminium is 447.43 kg. Guard silicon also becomes
sensitive. These material and coverage changes are intentional parts of the
counterfactual. Existing absorber/support structure elsewhere, sector seams and
barrel/endcap transitions remain. This does not isolate electronics or virtual
pad segmentation, for which no threshold/noise/readout model is applied.

Both readouts use virtual 5.5 mm Cartesian cells, with signed 12-bit X/Y fields
instead of the tile-local six-bit fields. Parent system/side/sector/layer/module
fields retain their offsets; the continuous sheet has module 0. Barrel local
readout axes are tangential and axial. Virtual edge-cell centres may fall
outside a clipped physical edge; physical sensitive deposition is still bounded
by the silicon shape. No response threshold or masked-edge cell rejection is used.

The unchanged native factory and audit libraries are reused byte for byte.
The XML-only transform rejects any source that differs from the retained tiled
compact, materials or exact primary files. [Compact geometry evidence](geometry-summary.json)
contains material changes, active/guard volumes, hashes and native results.
The full per-part/plane subtraction ledger remains local and reproducible.

## Validation before production

Ten geometry controls pass, including exact barrel faces, wafer/readout axes,
guard subtraction, touching boundaries, support cuts and rejection of unsupported
geometry. Three statistical controls pass, including multiplicative-response
cancellation under paired bootstrap and explicit undefined zero-signal bins.

Native construction finds all 2,304 sensitive sheets and unique volume IDs.
The 3,136 synthetic wide-address checks preserve both cell coordinates and
parent fields. ROOT reports zero overlaps/extrusions at 10⁻⁵ mm tolerance,
seed 135. This numerical tolerance is not an engineering clearance.

The 24-event, 12-worker pilot passes saved truth/hit and native worker audits.
It takes 24.118 s and produces 30,643,802 bytes, or 1,276,825 bytes/event.
Twice its 10k projection plus a 30 GiB reserve requires 53.783 GiB, versus
about 397 GiB available before the run. Retain all 10,000 events and keep the
runtime free-space guard; do not delete the original sample.

## Observable and paired comparison

Each geometry uses the identical retained primary-input file: 10,000 electrons,
independent uniform total energy 10–80 GeV, eta −3 to 3 and full phi, at the
origin. The input and truth-ledger files are copied byte for byte, not regenerated.
Transport uses 12 DDSim workers, seed 133812341 with per-event seeds,
FTFP_BERT, 0.7 mm cuts, 5 mm charged steps in sensitive silicon and zero field.
Source geometry/estimator revision is
`528db706de8a07c3cb39c2d12be758d8223fdd39`.

For each primary ID define R = sum(raw sensitive-silicon deposits)/true total
energy. The width is sample SD(R), ddof=1, divided by that geometry's own mean R.
All valid zero responses remain included. Keep ten equal |eta| bins over 0–3
and ten signed folded-phi bins over [−11.25,+11.25)° with period 22.5°.
The original tiled populations/moments must match all twenty published points.

Use 5,000 paired whole-event bootstrap replicas, seed 1335000, with common
resampled primary IDs across both geometries and both projections. Show 95%
percentile intervals for each width and the direct difference
w_tiled − w_continuous. Preserve joint 40-width and 20-difference covariance.
Equal seeds do not establish identical shower histories after material changes.

This is a broad-spectrum raw visible-response width, including losses, leakage
and within-bin variation. Mean response, absolute SD, quantiles, zero counts and
shared-bin response histograms accompany the overlay. Do not subtract widths or
variances in quadrature to infer an independent tiling term. The residual width
is not an intrinsic fixed-energy reconstructed resolution.

## Reproduce

Follow the existing [ACTS Spack workflow](../../../skills/acts-spack/SKILL.md)
and reverify changed setup fingerprints with the runtime doctor. The existing
installation provides DD4hep/DDG4 1.38, Geant4 11.4.3, ROOT 6.40.04,
EDM4hep 1.1.1 and podio 1.8. Plotting uses the existing Python with NumPy 2.5.4
and Matplotlib 3.11.2; set `ECAL10K_PLOT_PYTHON` to that executable.
No dependencies are installed or changed by this control.

First reproduce the original [tiled input/run and library build](../ecal10k/README.md#reproduce),
or use the exact retained local artifacts. Input hashes are pinned by the
control preparation script. Each output directory below must be fresh. The
local execution used `production-input`/`production12` in place of `repeat-*`.

```sh
python3 -B software/analysis/calorimeter_digitization/untiled_geometry.py \
  --source build/ecal10k/production-input \
  --output build/ecal10k-untiled/repeat-input
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/untiled_native.py \
  --sample build/ecal10k-untiled/repeat-input \
  --library build/ecal10k/calo/libnODDCalorimeterPrototype.dylib \
  --output build/ecal10k-untiled/repeat-native.json
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/angular_sample.py run \
  --sample build/ecal10k-untiled/repeat-input \
  --output build/ecal10k-untiled/repeat12 \
  --geometry-library build/ecal10k/calo/libnODDCalorimeterPrototype.dylib \
  --audit-library build/ecal10k/audit/libnODDAngularAudit.dylib \
  --events 10000 --threads 12 --bytes-per-event 1276825.0833333333
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/angular_analyze.py audit \
  --sample build/ecal10k-untiled/repeat-input --run build/ecal10k-untiled/repeat12
MPLCONFIGDIR="$PWD/build/ecal10k/mpl-cache" XDG_CACHE_HOME="$PWD/build/ecal10k/cache" \
  "$ECAL10K_PLOT_PYTHON" -B software/analysis/calorimeter_digitization/untiled_compare.py \
  --tiled build/ecal10k/production12 --continuous build/ecal10k-untiled/repeat12 \
  --reference docs/validation/ecal10k/summary.json \
  --output build/ecal10k-untiled/repeat-comparison
```

Use `--events 24` and a separate output directory for the pilot, audit it, then
substitute its actual bytes/event for disk planning. The displayed native
validation ran against `input-dev`, whose compact bytes match the frozen
production input exactly; the public native record pins both script and compact
hashes. Later provenance-only preparer changes did not alter the compact.

Mathematical tests need no native packages; run the three specific suites:

```sh
python3 -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_untiled_geometry.py' -v
"$ECAL10K_PLOT_PYTHON" -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_untiled_compare.py' -v
"$ECAL10K_PLOT_PYTHON" -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_angular_response.py' -v
```

Raw ROOT files, exact primary/event ledgers, caches, builds and bulky logs remain
local and ignored under `build/`. Only figures, recipes, provenance and compact
binwise evidence belong in this review package. No production detector,
engineering approval or design lifecycle state changes.
