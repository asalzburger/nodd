# PR #118 — nODD geometry and digitization comparison protocol

- Status: **PROTOTYPE; frozen study proposal, no detector acceptance**
- Prepared: 2026-11-09, assignment `I118-NODD-CaloTech`
- Scientific input revision: `29a8632eed6c8aeda554e3327e7242c470594881`
- Request: [add nODD geometry validation/comparison](https://github.com/asalzburger/nodd/pull/118#issuecomment-6744059438)
- Governing designs: [DES-030](../../design/DES-030-ecal-edge-sensors.md), [DES-031](../../design/DES-031-siw-barrel-prototype.md), [DES-044](../../design/DES-044-calorimeter-digitization.md)
- Predecessor: [frozen ODD digitization protocol](digitization-protocol.md) and its [executed results](digitization-results.md), preserved unchanged as historical evidence
- Freeze: commit the exact protocol, study configuration and executable producer before new scientific outputs. Record deviations prospectively; retain failures. Technical preparation does not grant design sign-off.
- Pre-execution amendment, 2026-11-09: before any new outputs, the coordinator added bounded η=−2 electron/muon/reference populations so both constructed endcaps receive direct transport/ID coverage. This prospectively expands coverage; it changes no gate in response to an outcome.

## Actual geometry boundary

**FACT — inspected at the input revision:**
`tools/calorimeter_baselines/export.py::OPTIONS/export/compose` is the maintained
selectable baseline exporter. Select **LAYOUT-001**, which freshly exports the
maintained DES043 tracker and composes the complete Si–W barrel and both endcaps.
The [baseline guide](../../../tools/calorimeter_baselines/README.md) and
[integration contract](../../design/inputs/ECAL-baseline-integration-2026-11-04.md)
distinguish this constructed stage from remaining detector design allocations.

| Constructed component | Source / integrated system IDs | Readout and relevant scope |
| --- | --- | --- |
| Beam pipe and maintained DES043 tracker | 0–7, unchanged | Actual tracker factories/materials, not an empty inner region |
| Complete DES031 Si–W barrel | 8 → 8 | `BARRELHits`, `nODDEcalBarrelPrototype`; all sectors/layers/slabs and local hardware |
| Complete DES030 tiled Si–W endcaps | standalone 8 → integrated 9 | `EDGEHits`, `nODDEcalEdgePrototype`; both ends, all sectors/layers, custom sensors and local hardware |
| Solenoid/field, HCAL, FCAL and muon systems | **not constructed by this baseline exporter** | Solenoid allocation, HCAL design options and ROOT-only FCAL remain design records; no active surrogate volumes or field are inserted |

Both ECAL readouts retain
`system:8,side:2,sector:4,layer:6,module:10,x:-6,y:-6`.
Side 0 denotes barrel, sides 1/2 the positive/negative endcaps; the endcap root
system is 9 only after composition. Preserve high ID bits, module-local pad
coordinates, merged custom electrodes and proper end transforms. Material names
are consistently component-prefixed by composition; tracker material names are
retained. Inspect actual constructed root IDs, readouts and resolved materials.

`barrel_layout.py::build` requires 48 **nominal** layers in this source;
`edge_export.py` exports 48 per endcap. Actual sensitive placement counts and
per-direction active-layer opportunities must come from the fresh model/native
inventory. Do not assume every nominal barrel/endcap layer is crossed in active
silicon: slab bays, guards, board gaps and sector cracks are physical features.
DES031 explicitly records a φ-dependent active-layer pattern. Geometry losses
are not automatically digitizer inefficiency.

`compose()` rejects component field blocks and emits none.
`tools/calorimeter_baselines/native.py` explicitly names the absent field and
remaining systems. The intended transport study is therefore **zero magnetic
field in the constructed tracker+ECAL stage**. Do not call it a complete fielded
nODD detector. A future complete field/magnet/HCAL/FCAL integration is outside
this response comparison.

The previous `build/nodd-tiling-response` samples are complete **positive-endcap
only**, 16 sectors/48 layers, without tracker, barrel, negative end, field or
digitization. Their continuous-Si control changes material/scoring. They remain
valuable [local tiling evidence](tiling-response.md), but must not be relabelled
as this integrated-baseline sample or substituted for new barrel data.

## Geometry preparation and software boundary

Use fresh ignored output directories. A recipe sketch using the existing exporter
and build targets is:

```sh
python3 -B tools/calorimeter_baselines/export.py \
  --layout LAYOUT-001 --output build/issue117/nodd-validation/layout001
software/env/run.sh cmake -S prototypes/calorimeter \
  -B build/issue117/nodd-validation/calo-factories -G Ninja
software/env/run.sh cmake --build build/issue117/nodd-validation/calo-factories \
  --target Components_nODDCalorimeterPrototype --parallel 3
```

Build/load the maintained tracker factory libraries using the existing baseline
recipe; do not replace their geometry with ODD. The native union audit accepts
all required libraries explicitly and checks exact root mapping, compact/material
hashes and overlaps at the retained 1e-5 mm tolerance. Record construction and
complete-overlap results separately; an old isolated-component pass is not a
new union pass. Missing runtime, unresolved overlaps, failed containment or ID
instability must remain blockers or explicit unexecuted gates, not success.
The independent zero-field ODD control may execute while the full nODD overlap
audit is pending. Its input/source configuration is frozen separately from the
future audit result; every nODD transport and final index must bind an actual
native PASS to the unchanged compact/material/library/root/tolerance identities.
Pending metadata is never a nODD geometry pass or permission to run nODD events.

The available worktree has source recipes and old isolated-endcap exports;
no cached integrated `baseline.json` was found during this protocol inspection.
No integrated transport/runtime pass is claimed by this document. Reverify Spack,
DD4hep/DDG4, datasets and the actual factory registrations before dependent work.
Record every executed source/library/compact/material hash and namespace mapping.

### Pre-output PhysVal clarifications — 2026-11-09

The separate assessment of `554b087c3c0088773199466a779a580a25841017`
identified three implementation definitions, frozen here before transport:

1. A native intersection of the initial IP ray predicts geometric active layers;
   it is a separately labelled straight-ray diagnostic. Multiple scattering and
   secondary production mean it cannot certify the transported muon's crossing.
   Primary-associated deposits identify observed active crossings. A nominal
   layer without such a deposit remains an **unknown transported crossing**,
   unless independently persisted trajectory information resolves it. Neither
   a missing hit nor a predicted gap is silently promoted to a known zero signal.
   Target nominal trials are BARREL/side0 at η0, EDGE/side1 at η2 and EDGE/side2
   at η−2, with the corresponding ODD descriptor/placement identities. Derive
   each target's layer inventory from construction; retain other-region primary
   deposits separately rather than merging equal numeric layer labels.
2. A centroid chord uses the immediately previous and next **constructed physical
   layer**, within the same region and side. The native inventory defines this
   adjacency, including each geometry's different layer-number origin. Both
   neighbours must have qualified centroids; never bridge an unobserved layer.
3. Installed DDSim explicitly adds `G4StepLimiterPhysics`; the ODD sensitive-Si
   `cal_limits` maximum of 5 mm is therefore an effective transport setting,
   whereas the maintained nODD factories attach no corresponding limit.
   **NODD DESIGN CHOICE — matched transport fixture:** before any event, apply
   and audit a 5-mm maximum charged-particle step in sensitive ECAL silicon for
   **both** geometries. Preserve other existing user limits. The task-owned
   DDSim initialization callback changes only that transport fixture, not any
   TGeo geometry, material, sensitive mask, identifier or source factory.
   Record the actual Geant4 StepLimiter processes, field samples, material Birks
   constants and effective region production cuts before the first event. Require
   zero sampled field and the same ECAL 5-mm limit; retain source-specific cuts
   elsewhere explicitly rather than asserting unmeasured equivalence.

Create a task-local original-Key4hep compact wrapper for the **same nODD geometry**
containing only the required named encoding constants and resolved references.
The Key4hep full processor reads `BARRELHits` and `EDGEHits`, with the shared
nODD descriptor above; its geometry service must load the same custom factories.
Audit that a wrapper changes no volumes, materials, readout or root IDs. The
native comparator/converter uses explicit nODD collection names, geometry and
producer provenance. Neither ODD collection names nor the standalone endcap
system 8 may silently survive as integrated mappings.

## Matched physical comparison and fixed settings

**NODD DESIGN CHOICE — reference geometry:** generate a **new zero-field ODD
control** from unchanged ODD `d70556f33b1c36abdf101a07ad8cf57eb56fbdf1` geometry
using a task-owned field-off steering/wrapper. Only field selection changes;
verify the actual transported field is zero. Audit original geometry/material
identity and record the field-off difference. Preserve the earlier fielded ODD
results; they are historical context, not this matched-field control.

The comparison intentionally changes detector geometry/material distribution:
upstream tracker, barrel/endcap dimensions, segmentation, local hardware and
other ODD systems may differ. Keep the ODD control's original component scope
and list its actual constructed roots. Zero field controls one confound; it does
not make the two geometry scopes identical. This is a **baseline-stage response
comparison**, not an isolated measurement of tiling loss or a detector technology
ranking. The earlier same-stack local tiling experiment addresses a narrower
question.

Keep the same physical species, momentum/direction, FTFP_BERT, generation origin,
transport/range/hit cuts and stored-energy convention across geometries. Use
one primary at (0,0,0), fixed φ=0.123 rad and the main η=0/1/2 grid, plus
the separately labelled η=−2 mirror controls below. Do not move a gun direction
after seeing a gap or a low signal. The requested values denote momentum magnitude.
The native Geant4 gun is given momentum directly with `/gun/momentumAmp p GeV`;
validate persisted momentum, direction and **total energy**. Record the ROOT PDG
mass and corresponding kinetic-energy calculation as metadata. Normalize
by persisted primary total energy, not by the requested momentum or gun kinetic
energy. This native-gun convention differs from the earlier DDSim Python-gun
setting; its actual macro/configuration is part of the run identity.

**Pre-output technical correction, 2026-11-09:** excluded two-block pilot04
showed the kinetic-energy macro path rounded a 9.894899769296881-GeV setting
to 9.8949 GeV, producing a 2.0e-7-GeV momentum/energy discrepancy caught by the
unchanged 1e-7 truth guard. Use the native momentum-amplitude command to preserve
the intended integer-GeV/c beam values; no truth tolerance or response criterion
is relaxed. Origin and block identities in that pilot were correct. Pilots and
their failed verification remain excluded from all response populations.

The unchanged unsigned response comparator uses:

| Stage | Pair energy | Gaussian electronics RMS | Strict threshold / pre-noise range |
| --- | ---: | ---: | --- |
| Raw | none | none | All stored sensitive-Si deposits |
| D | 0 eV | 0 MIP | >0.6 MIP / 2500 MIP |
| P, conditional replay only | 3.6 eV | 0 MIP | same |
| PN | 3.6 eV | 0.13 MIP | same |

Use **0.00014875 GeV/MIP** for both geometries, all cells and stages. Retain its
historical calibration/quantization caveats; do not derive an nODD scale to force
its muon peak to one. Gain variation/dead cells/time smearing are off; integrate
all contributions inside the same wide numerical time window. Clipping precedes
noise. Original earliest-contribution and native weighted times remain different;
energy/selection agreement makes no timing claim. Common per-cell noise is a
software comparator setting despite different pad area/capacitance and custom
pads; it is not an engineered nODD electronics model.

## Frozen sample matrix and seeds

All listed raw populations are newly generated for this zero-field comparison;
all recorded events, including zeros, enter the response denominators. Use the
same native Geant4 gun/macro-block approach for both geometries, with FTFP_BERT
and a 0.7 mm range cut. Record all effective region/particle cuts as well as that
default. Each block resets a disjoint RNG seed pair, without EventSeeder.
Within each listed shower block use order species `(e-,gamma)`, momentum
`(5,20,50) GeV/c`, η `(0,1,2)`; index starts at zero. Append the bounded
negative-endcap electron control as shower index 18; append negative muons as
direction index 2 and negative calibration as reference direction index 3.

| Raw population | Per geometry / point | Initial transport seed |
| --- | --- | --- |
| nODD LAYOUT-001 showers | 18 points × 200 events = 3600 | 120000 + shower-point index |
| Zero-field ODD showers | same 18 × 200 = 3600 | 121000 + shower-point index |
| Negative-endcap e- control, 20 GeV/c, η=−2 | 200 per geometry, separate from the 18-point matrix | nODD 120018; ODD 121018 |
| nODD detailed mu- at 10 GeV/c, η=0/2 | 2 × 250 = 500 | 122000 + direction index |
| Zero-field ODD detailed mu- at 10 GeV/c, η=0/2 | 2 × 250 = 500 | 123000 + direction index |
| Negative-endcap detailed mu- control, 10 GeV/c, η=−2 | 250 per geometry | nODD 122002; ODD 123002 |
| Independent zero-field ODD 20 GeV/c electron calibration, η=0/1/2/−2 | 4 × 100 = 400, excluded from validation | 124000 + reference direction index |

The 18-point main shower matrix and positive/central muons still total 4100
events per geometry. The negative-endcap controls append 450 events in two
files per geometry: **4550 validation events in 22 files per geometry**,
**9100 validation events plus 400 independent calibration events = 9500 total**.
Thus nODD contributes 4550 events and zero-field ODD contributes 4950 including
its calibration. The η=−2 electron point is a bounded mirror control, not a full
negative-η energy/species matrix; do not imply negative-photon or 5/50-GeV/c
coverage. Each table seed
is the first of the block pair `(seed,seed+1000003)`; record both and the actual
block boundaries/order. Detailed
shower persistence is required at least for all muons; record the actual setting
and truth metadata in every manifest. Each geometry's raw/D/PN outputs use the
same generated events. Different geometry transports use disjoint seeds and are
**independent populations**, not event-paired shower histories.

Use native response streams `125500 + 100*population_index` in fixed manifest
order nODD showers, ODD showers, nODD muons, ODD muons, ODD calibration. Explicitly
record collection/mode stream offsets and verify they are distinct; no reseeding
to favor a result. Input-generator batching may avoid repeated initialization
only if each event's frozen point identity/truth/settings remain verifiable.
Do not reduce tracker, endcaps, sectors, layers or local hardware for runtime.
A separately labelled software pilot is excluded from these populations.

## nODD original/native software gates

First run the full original Key4hep D algorithm and the native adapter on **all
new nODD raw files** (4550 events in 22 files), including all three
detailed-muon files and the negative-endcap electron control. Preserve unchanged
SimHits/contributions/MC relations and ordered unique EventHeaders. Require
exact accepted-cell sets and per-cell MIP energies within
`1e-5 + 5e-6*abs(E_reference_MIP)`, as in the existing frozen protocol; no selection
mismatch is excused by an energy tolerance. Empty events/collections count;
an entirely empty study cannot establish the gate. Verify custom-mask merged
IDs, integrated systems 8/9 and saved cell-position contracts.

Then prepare two 1000-copy conditional replays from fixed new nODD inputs:
first detailed central muon event (index 0) and first 20 GeV/c η=2 photon event
(index 0). Preserve complete event payloads; only unique EventHeader run/event
IDs change, with original/native reading the **same hashed replay**. Audit actual
ROOT low-32-bit seeds for uniqueness/nonzero values and retain header-only
round-trip checks. These are conditional software tests, not extra independent
showers.

Run P and PN, original seed `125200+2*fixture+mode`, native
`125300+2*fixture+mode`; fixture=0/1, mode=P/PN=0/1. Replay copy i uses
EventHeader run number `125800+1000*fixture+i` and event number i (i=0..999).
This prescribed mapping must still pass the actual effective-seed uniqueness
audit; its arithmetic alone is not proof of distinct ROOT draws. The deterministic
original run may use seed 125000 with all random effects disabled.
Use analysis seed `126000+2*fixture+mode`, split into permutation/bootstrap
substreams. Apply unchanged prior gates to event total accepted MIP energy and
accepted-cell multiplicity: mean difference within five combined SE, 10,000
whole-event label-permutation CDF test p≥0.001, and event-energy SD-ratio 95%
bootstrap interval wholly inside [0.85,1.15], 10,000 replicas. Preserve prior
constant/undefined-variance handling and never pool cells as independent trials.
Failures are investigated and retained before a claim of nODD software agreement.

## Held-out nODD/ODD muons and geometric opportunity accounting

All new muons are held out from the frozen MIP scale. Verify detailed PDG=13,
primary ancestry and relation endpoints. Audit actual sensor normals, thickness,
module/layer transforms and cell references against each geometry's native
inventory; do not assume ODD normals/thin axes apply to nODD EdgeGrid.

Build physical event/layer opportunities from the actual model and geometry/
trajectory audit, before digitization/threshold cuts. Retain separately nominal
constructed layers, primary geometric active crossings, gaps/guards/passive
misses, known zero signal, unknown truth, split cells and contaminated trials.
Derive counts from actual layer IDs/model, rather than hardcoding 48 crossings
or multiplying retained hits. At a geometry gap, “no active crossing” is distinct
from failure of a crossed MIP to pass an electronic threshold. Do not invent a
missing cell's ID, signal or primary truth.

Report both generated-event/nominal-layer yield and conditional identified-
active-crossing yield, with their exact denominators and unknown fractions.
For split crossings use the same per-cell rule as the ODD protocol: any identified
primary-crossed cell above threshold passes; do not sum split pulses first.
Unseen/unknown crossing inventory prevents a complete detector-efficiency claim.

Use the prior threshold-independent clean single-cell/primary category for
spectra, with local adjacent-layer centroid chords and actual slab normals.
Path `0.5 mm/abs(n·u_chord)` remains an approximation, checked against thickness
and initial-ray estimates; true step-length precision is not inferred from step
positions. Freeze `abs(n·u)>=0.9` and retain angle/chord/endpoint, contamination
and split rejections. No pulse-amplitude selection enters path qualification.

Use the unchanged 0.025-MIP binning, [0.25,2.5]-MIP Landau–Gaussian fit,
finite-range bin-integrated likelihood and separate Landau-component MPV versus
numerical convolved mode. Whole-event bootstrap: 1000 replicates, seeds 126100
through 126103 in order nODD η0, nODD η2, ODD η0, ODD η2; append seeds
126104/126105 for nODD/ODD η−2 respectively, preserving the existing sequence. Preserve fit-failure,
parameter-boundary/shape and undefined-category reporting; do not refit the
MIP scale or silently enlarge a fit range. If a clean nODD category is too small,
report that limitation and descriptive spectra rather than invent a fit.

Reuse the already measured signed 0.13-MIP model pedestal only after checking the
same backend/config identity, or repeat the same 200,000-draw signed audit with
recorded disjoint seed 126200. SNR is the path-normalized Landau-component MPV
(as clarified in the completed ODD study) divided by pedestal RMS, with independent
noise and event-fit errors. Scan the same strict thresholds
`0/0.2/0.4/0.6/0.8/1/1.2/1.5/2 MIP` on each trial's same unnormalized D/PN pulses.
Report counts, conditional Wilson95% bounds and whole-event bootstrap errors/
covariance; rare categories with undefined replicas retain null errors.
Sparse occupied-cell processing still cannot establish full-channel noise occupancy.

## Common calibration and paired response statistics

**NODD DESIGN CHOICE — common geometry comparison calibration:** from each
independent **zero-field ODD** electron reference at 20 GeV/c, including its
separate η=−2 reference, freeze
`C_eta = mean(E_generated)/mean(S_D_ODD_reference)`.
Do not assume the negative-endcap factor equals C_eta2: measure the independent
reference C_minus2 and share it across the two geometries' negative controls.
Record numerical factors, hashes and statistical uncertainty before evaluating
new test samples. The same η factor is used for **both geometries**, both species,
all energies and raw/D/PN. No nODD-specific, species-specific, per-energy or
per-stage retuning/offset is allowed. Do not reuse the old fielded ODD factors
as though they came from this zero-field reference.

Primary comparison panels show the **unscaled** silicon visible fraction
`S_raw/E_generated`, D/E_generated and PN/E_generated, their mean and SD/mean,
so calibration cannot hide an absolute nODD response deficit. Supplement with
`E_cal=C_eta*S_stage`, response mean(E_cal/E_generated), residual to unity, and
nODD/ODD mean ratios at each matched gun point. A common factor cancels from that
matched-η geometry ratio and from each population's SD/mean.

Also show stage changes D−raw and PN−D paired **within each geometry/event**,
zero counts, longitudinal Si sums by actual region/layer, and the shared
low-response diagnostic `C_eta*S_stage/E_generated < 0.8`. Record means/SEM,
sample SD, SD/mean, quantiles and all-event histograms/underflow/overflow. The
spread is raw/digitized visible-response spread, not a fitted Gaussian core or
reconstructed calorimeter energy resolution. Silicon-only visible energy is
not active/(active+passive) sampling fraction, and late-layer energy is not a
measured escaping-energy leakage fraction.

Use **5000 whole-event bootstrap replicates**, analysis seed 126300. Resample
raw/D/PN jointly within a population, independently across geometry/energy/
species populations. Independently resample each ODD calibration, reusing its
same resampled C_eta across **both geometries** and every associated η population
in each replicate. Retain paired-stage and common-calibration covariance with
axis labels, along with conditional Wilson and joint-reference tail intervals.
Do not treat matched seeds/point indices as a paired cross-geometry event history.
Undefined widths/ratios at all-zero or sparse samples remain null with counts;
do not discard bootstrap replicas until an apparently precise error emerges.

## Execution evidence and interpretation

The runner must anchor source/dirty status, complete baseline/component hashes,
exact factory libraries, runtime/build identity, fields/cuts/physics/actions,
raw/config/original/native/log hashes, truth gun definitions, seed streams and
requested/read counts. The runner input manifest is `build/issue117/nodd/reference-input.json`; retain
its exact hash and resolved source/configuration/library paths. The actual
transport and original-framework recipes are written by SoftEng/main and frozen
before bulk; the source recipe above is not
an execution claim. Preserve original ODD and isolated-endcap records as separate
sample families. Keep full ROOT/replay/JSONL payloads and logs ignored/local;
commit plots, compact binwise/sufficient-statistic/covariance evidence and exact
reproduction recipes per ADR003.

Report independently: (1) integrated geometry construction/overlap/ID scope,
(2) nODD same-hit and stochastic software gates, (3) held-out muon characterization
and opportunity limitations, and (4) matched-field raw/digitized baseline response
comparison, with negative-endcap electron/muon controls explicitly identified. A blocker in one remains explicit even if another succeeds. These
measurements do not accept the unsigned geometry or qualify engineering, complete
fielded-detector containment, charge sharing/pulses/ADC/timing, pileup, radiation,
jets/MET or reconstruction. No dimension, material or response parameter is tuned
to flatten a result. Only identified humans may approve the detector design.
