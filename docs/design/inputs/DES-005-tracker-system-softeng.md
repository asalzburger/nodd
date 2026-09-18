# DES-005 — SoftEng tracker-system planning input

- Status: **DRAFT**; planning only, no implementation or performance result.
- Date: 2026-09-18.
- Role: `SoftEng`; human owner and technical reviewers: pending.
- Parent: [DES-005](../DES-005-tracker-system-plan.md).
- Governance: [PROJECT](../../../PROJECT.md), [ADR-003](../../decisions/ADR-003-validation-and-artifact-policy.md).
- Coordination: [TrackTech](DES-005-tracker-system-tracktech.md), [PhysVal](DES-005-tracker-system-physval.md).
- Final human sign-off authority: `asalzburger-review`; no approval requested or recorded by this input.

## Position and argument

**NODD DESIGN CHOICE — proposed:** one versioned study description should feed
progressively more detailed adapters: analytic estimates, ACTS surfaces and fast
tracking, then signed-off DD4hep/Geant4 geometry. Stable identifiers and explicit
approximations make a change in performance traceable to the layer arrangement,
module assumptions, material, field or reconstruction configuration. Reimplementing
the same layout independently in each tool would make those causes harder to
separate. This is a proposed study contract, not selection of a production detector
generator or permission to integrate unsigned geometry.

Start with the working tracker envelope and ODD-inspired pixel, short-strip and
stereo long-strip sequence. Timing remains an explicit alternative with sensor,
material, services and response costs. Software should expose all of these choices
to review; it should not select layer positions or acceptance thresholds.

`SysArch` owns placement constraints and interfaces; `TrackTech` owns sensor and
assembly meaning; `PhysVal` owns observables, sampling and scientific gate criteria;
`SoftEng` owns reproducible execution, adapters and numerical validation. Each
receives a reviewable input/output contract before a stage begins.

## Existing capability and remaining intake

The [DES-003 software input](DES-003-software-validation-input.md) and
[envelope tool](../../../tools/envelope_study/README.md) provide allocation
diagnostics. Rectangular hosts are not tracker sensitive surfaces.

The unmerged magnetic work is a dependency, not tooling already on `main`.
Its inspected immutable revision is
`040337c2d6129014655a7534e0ea79c6ef693bc2` on PR #6. The retained
[ACTS setup report](https://github.com/asalzburger/nodd/blob/040337c2d6129014655a7534e0ea79c6ef693bc2/docs/validation/DES-004-acts-setup.md)
reports seven synthetic propagation checks and an ideal-solenoid axis comparison.
Reuse that harness and environment after an explicit dependency landing or pinned
isolated checkout; do not copy a competing version into this plan.

**Executed local inventory, 2026-09-18:** `import acts` and `acts.examples` succeed
in `reference/cache/acts-venv`; installed distribution `pyacts` is version `47.7.0`.
Top-level `ConstantBField` and `SolenoidBField` exist; a top-level attribute named
`InterpolatedBFieldMap` was not found. That attribute check does not establish
that a usable map interface is unavailable. Confirm the exposed factory/binding
API and perform an adapter fixture before selecting a Python or C++ bridge.
No nODD active-surface propagation, material mapping, fitting or full simulation
was run for this input. Existing magnetic fixture results were read, not rerun.

**IdRes intake:** user-authorized read-only access succeeded and an isolated
temporary checkout was inspected. Anonymous public access was not established;
license, public reproducibility and numerical validity remain unresolved. No
installation, compilation or physics run was attempted. No private endpoint,
source content, example detector or private-only detector fact is incorporated
into this proposal. Treat IdRes as an optional adapter pending public-source and
license intake plus a pinned, reproducible benchmark. Do not promise arbitrary
3D fields, general beamspot sampling, correct stereo covariance or timing without
testing the actual tool. A documented, publicly reproducible analytic covariance
estimate with explicit measurement and scattering assumptions is the fallback;
IdRes availability does not block contract or layout work.

**FACT — public software documentation:** ACTS describes separate propagation
steppers and geometry navigators, including a straight-line control; see
SRC-ACTS-REPO, [v47.7.0 propagation guide](https://acts.readthedocs.io/en/v47.7.0/core/propagation.html),
“Overview”, “Navigators” and “Steppers”. Its
[field guide](https://acts.readthedocs.io/en/latest/core/magnetic_field.html),
“Magnetic field provider interface” and “Field provider implementations in Core”,
documents constant and interpolated vector fields and lookup failures. The latter
is unpinned documentation accessed 2026-09-18, not proof of wheel API compatibility.
SRC-ACTS-MATERIAL-MAPPING,
[official mapping guide](https://acts-project.github.io/material_mapping_howto.html),
steps 1–5, requires a detailed simulation geometry for physical material recording.
Synthetic slab tests before that backend lands are a separate validation stage.

## Shared contracts before adapters

All contracts below are **NODD DESIGN CHOICE — proposed**, with human approval
pending. A schema version, immutable configuration ID/hash, units, coordinate and
sign conventions, source/design classifications, uncertainty/omission fields,
owner and validity domain are mandatory. Unknown inputs remain unknown. Fixture
values cannot silently become candidate defaults. Schema changes require a
migration note and comparison of regenerated representations.

| Contract | Required content and owning input | Adapter invariant |
| --- | --- | --- |
| Layout | `SysArch` envelope revision, candidate ID, technology regions, finite barrel/disk or module surfaces, placements, inactive edges, overlaps, service masks and stable physical/layer IDs | Counts, bounds, transforms, axes and containment agree across adapters; physical overlaps differ from navigational envelopes |
| Sensor/measurement | `TrackTech` sensor family and module revision, active bounds, pitch, spatial response assumptions, local axes, measured dimensions, covariance, strip pairing/stereo rotation and efficiency assumptions; timing response separately | One-dimensional strip measurements stay one-dimensional; paired sensors and revisits do not create fictitious independent layers; covariance rank/correlations survive conversion |
| Material | Module, support, cooling, power, data, readout and shared-service component ledgers; composition/density/thickness or a declared effective representation, areal mass, X/X0 and interaction-length normalization, allocation and uncertainty | Each contribution counted once; projected path budget differs from normal-incidence thickness; unknown components cannot become zero |
| Field | Magnetic candidate ID and geometry revision, provider type, vector components/units, coordinate transform, normalization, grid/domain, interpolation, symmetry and checksum; provenance/validation status | Same field samples and polarity across adapters; no silent zero fill, extrapolation or renormalization beyond declared domain; candidate layout compatible with map host |
| Beamspot and sample | `PhysVal` vertex distribution and stress vertices, correlations/truncation, momentum, charge, species, eta/phi bins, random seed or deterministic grid, truth selection and weights | Distinguish a point vertex from luminous-region coverage; retain all generated denominators, including losses and failed fits |
| Result | Input identities, truth-to-crossing-to-measurement associations, distinct-layer counts, parameter/covariance convention, fit validity and failure codes, material categories, field lookups, timing observables when enabled | Every absent result is classified; skipped tracks, singular covariances, map-domain misses and numerical failures stay visible |

The pixel-module work provides the first versioned sensor/material payload. It
must remain replaceable as that design matures; no waiting for every module
detail is required to test these interfaces. Each provisional short-strip,
long-strip, support and service payload needs a named responsible role, rationale
and scenario range before candidate comparisons use it.

## Work packages, dependencies and completion evidence

These are proposed software contributions to the parent work breakdown, not
claims that any package has been implemented.

| ID | Deliverable | Dependencies | Completion evidence |
| --- | --- | --- | --- |
| TRK-SE01 | Versioned contracts, exact ODD comparison extraction, tool/adapter capability matrix and isolated environment recipe | `SysArch` reference envelope; `TrackTech` ODD/module inventory; `PhysVal` observable draft | Round-trip schema/units/ID tests, unknown-field rejection, upstream revision/configuration recorded; IdRes public/license gate resolved or fallback named |
| TRK-SE02 | Tool-neutral analytic estimate runner and optional IdRes adapter | SE01; provisional measured-coordinate covariance and material/field assumptions | Independently checked simple fit/covariance fixture; unsupported features explicit; same candidate/sample report from reference calculation and adapter where comparable |
| TRK-SE03 | ACTS finite active-surface conversion, crossing/navigation recorder and interchangeable field adapter | SE01; pinned PR #6 reuse; `TrackTech` tiling assumptions | Unit/transform/ID tests, straight/helix reference intersections, boundary/gap/strip-pair/revisit fixtures, field-domain failures and convergence report |
| TRK-SE04 | Material ledger aggregation and directional scans, then ACTS material representation | SE01 and synthetic machinery first; actual pixel, strip, support/service inputs incrementally | Synthetic path integrals and category closure; explicit estimate scenarios; later comparison against detailed geometry and map binning/sampling convergence |
| TRK-SE05 | Truth-associated fast measurements/fits followed by seeding/pattern-recognition studies | SE02–04; `PhysVal` samples and metrics; `TrackTech` response contract | Residual/pull and failure accounting, occupancy/inefficiency assumptions, fake/duplicate/efficiency denominators, reconstruction settings kept separate from layout changes |
| TRK-SE06 | DD4hep/Geant4 landing, sensitive/readout/ID conversion and independent material/field comparisons | Supported backend environment; signed-off component/system designs and integration authorization | Construction, overlap, counts/transforms/mass, hit smoke tests, material recording/mapping, ACTS navigation and response comparisons with retained earlier predictions |

SE03 and synthetic SE04 can proceed while module and magnet research develops.
Start candidate field studies with explicit zero/uniform-field controls; add
validated finite-solenoid providers/maps first, then the available magnetic
candidate maps. A provider that is not ready produces an unavailable comparison,
not a fictitious approximation bearing that candidate's name. Iron and non-axisymmetric
options retain their solver/domain requirements from the
[magnetic software review](https://github.com/asalzburger/nodd/blob/040337c2d6129014655a7534e0ea79c6ef693bc2/docs/design/inputs/DES-004-option-software-review.md).
First compare fields on identical tracker surfaces and identical samples; evaluate
any layout adjustment as a separately identified second comparison.

## Machinery checks before candidate claims

**NODD DESIGN CHOICE — proposed:** name fixtures `TEST-TRK-*`, explicitly mark
their numbers as test values and keep them separate from `ESTIMATE-TRK-*` design
scenarios. Define justified numerical tolerances before using these as gates.

- `TEST-TRK-UNITS`: length/field conversions, handedness, rotations and serialization;
  duplicate IDs, invalid bounds, non-finite values and inconsistent units fail.
- `TEST-TRK-CROSSINGS`: finite cylinder/disk/plane intersections, known module gaps,
  both endcaps, tangencies and curling revisits; compare ACTS with independent
  analytic straight-line/helix results and vary propagation tolerances.
- `TEST-TRK-STEREO`: paired one-dimensional axes and a zero-stereo rank-deficient
  control; verify the reported covariance and layer counting do not manufacture
  an extra coordinate. Timing-disabled response must leave spatial assumptions explicit.
- `TEST-TRK-MATERIAL`: a known slab at normal/oblique incidence, a finite service
  patch and a multilayer sum; compare exact path-length budgets, areal mass and
  contribution totals. Refine binning/sampling at boundaries and expose empty bins.
- `TEST-TRK-FIELD`: zero/uniform controls, charge/field reversal, vector interpolation,
  symmetry boundaries and out-of-domain queries; compare field samples independently
  before trajectory comparisons. Reuse PR #6 fixtures where applicable.
- `TEST-TRK-DENOMINATOR`: intentionally missed surfaces, rejected measurements,
  failed fits and unknown inputs must survive into reports with distinct statuses.

Estimate scenarios then replace fixture values with public-source-backed facts,
documented inferences or explicit nODD trial choices. Scan the material categories
independently and with stated correlations. Fixed geometry with variable material,
fixed material with variable layout, and fixed surfaces with variable field expose
different effects. Preserve the old estimate when module/support revisions arrive,
rerun affected scenarios and explain ranking changes before promotion.

Beamspot stress vertices enter the early geometry checks to avoid a point-vertex
layout that later fails at the edges. Final coverage claims still require the
reviewed full distribution and response definition from `PhysVal`. Ideal crossings,
truth-associated fits and reconstructed-track efficiency remain separate outputs.

## Reproduction, integration and unresolved decisions

Every run records project/upstream revisions and dirty patch identity; contract,
adapter and input hashes; environment/platform and dependency pins; executable
commands; seeds/sample definitions; numerical settings; status and rejection
counts; raw artifact checksums; and limitations. Keep compact summaries in Git
and use the eventual ADR-003 retention policy for large artifacts. A fresh-checkout
reproduction is part of each adapter landing, not a promise inferred from a local
import. Separate inexpensive fixture CI from scheduled grids and later full-simulation
runs; retain unavailable stages explicitly.

Before adapter implementation, agree measurement/beamspot contract details,
public tool intake and exact ODD reference configuration. Before quantitative
selection, agree `PhysVal` acceptance criteria and scenario ranges with human
review. Before full simulation, land compatible DD4hep/Geant4/ACTS tooling and
the signed-off physical designs; revisit approximate predictions against detailed
material, field and response without overwriting their historical evidence.
