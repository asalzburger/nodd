# DES-003 input — Software and validation tools

- Status: DRAFT; stage-B architecture input, not approved geometry.
- Date: 2026-09-16.
- Role: Project Software Engineer; human owner and approving humans: pending.
- Scope: global envelopes, interfaces and tests of their implications.
- Governance: [PROJECT](../../../PROJECT.md), [development plan](../../DEVELOPMENT_PLAN.md), [ADR-003](../../decisions/ADR-003-validation-and-artifact-policy.md).
- Sources: identifiers below resolve in the [catalogue](../../../reference/manifest.yaml).

Stage A is considered complete for progression under the user's instruction.
This work proposes tests of new architecture choices; it does not reopen that
decision or claim a new ODD runtime validation.

Review round 1 adds the [study catalogue](../../validation/DES-003-study-catalogue.md),
including mandatory later full field propagation. The current prototype also
reports full/partial axial allocation traversal.

## Recommendation and division of responsibility

**NODD DESIGN CHOICE — proposed:** use a small analytic allocation tool now,
then reuse DD4hep/Geant4 and ACTS infrastructure when actual component geometry
exists. Avoid building a competing transport engine. The System Architect owns
envelopes and handoffs; subsystem agents supply active-surface and material
assumptions; Physics and Performance Validation owns observable definitions and
acceptance recommendations; software owns reproducible execution and reporting.
Human approval remains pending.

There are three different questions:

1. **Allocation:** can a prompt straight ray enter the intended subsystem boxes,
   and are the proposed allocations mutually consistent?
2. **Geometry:** how many distinct active surfaces/stations does a particle cross,
   and which materials does it traverse?
3. **Performance:** are energy deposits detected, reconstructed and useful?

An affirmative answer to the first does not establish the others. In particular,
an r–z drawing cannot establish hermeticity in azimuth or over a luminous region.

## Existing tools: verified documentation, not executed software

| FACT: documented capability | Precise source locator | Proposed use and limitation |
| --- | --- | --- |
| DD4hep provides overlap/geometry checks and material-scan utilities. | SRC-DD4HEP-MANUALS, [User Manual chapter 2, “Tools and Utilities”](https://dd4hep.web.cern.ch/dd4hep/usermanuals/DD4hepManual/DD4hepManualch2.html), “Overlap checking”, “Geometry checking”, “Material scans”. | Reuse against constructed compact geometry. Tool defaults are not nODD acceptance tolerances. Confirm available executables against the chosen installation. |
| DDRec's MaterialScan scans material along a line and can restrict the scan to a detector, material or region. | SRC-DD4HEP-REPO, `DDRec/include/DDRec/MaterialScan.h`; [class documentation](https://dd4hep.web.cern.ch/dd4hep/reference/classdd4hep_1_1rec_1_1MaterialScan.html). | Produce direction-dependent budgets from actual volumes. Straight lines do not model bending or showers. |
| Geant4 supplies placed-volume overlap tests and configurable field propagation. | SRC-GEANT4-DOCS, Book for Application Developers, [“Detecting Overlapping Volumes”](https://geant4.web.cern.ch/documentation/dev/bfad_html/ForApplicationDevelopers/Detector/Geometry/geomOverlap.html) and [“Electromagnetic Field”](https://geant4.web.cern.ch/documentation/dev/bfad_html/ForApplicationDevelopers/Detector/electroMagneticField.html), including propagation accuracy. | Check converted transport geometry and charged-particle navigation. Sampling-based overlap searches are not exhaustive proofs; propagation tolerances need convergence studies. |
| ACTS provides material recording, mapping and validation examples, with ODD as a documented application. | SRC-ACTS-MATERIAL-MAPPING, [“Material mapping”](https://acts-project.github.io/material_mapping_howto.html), steps 2–5; `Examples/Scripts/Python/material_recording.py`, `material_mapping.py`, `material_validation.py`. | Reuse for tracking material representation after selecting a compatible ACTS revision and geometry conversion. Material mapping is not calorimeter shower simulation. |

These live documentation routes were inspected on 2026-09-16. The Geant4 pages
identify version 11.4; that is documentation provenance, not a dependency choice.
No DD4hep, Geant4 or ACTS executable was run for this input. Pin compatible source,
build options and docs before execution; do not mix the latest examples with an
older ODD environment without checking their interfaces.

## Minimal staged toolkit

### B1 — allocation diagnostics, available in this proposal

The isolated [envelope tool](../../../tools/envelope_study/study.py) accepts JSON
rectangles in metres, draws a symmetric r–z allocation and reports rectangle
intersections and straight-ray entry/exit distances. Run its existing interface:

```sh
python3 tools/envelope_study/study.py <envelopes.json> --report <report.json>
python3 -B -m unittest discover -s tools/envelope_study -p 'test_*.py'
```

The first command is a recipe with placeholders, not a claim of execution here.
Optional `--figures <directory>` requires the plotting environment; the report
path uses the standard library. The parent proposal records the actual candidate
file, command, dependencies and execution results.

**INFERENCE:** box intersections can reveal competing reservations, and ray paths
can expose a missing allocation in a tested direction. Neither proves a physical
overlap or inefficiency. Unoccupied space has no demonstrated service capacity.
No sensitive layers or material composition are provided by these rectangles.

### B2 — layout and budget scenarios, proposed follow-up tooling

**NODD DESIGN CHOICE — proposed:** extend only after agreeing these inputs:

- Active cylinders/disks or finite module surfaces, grouped by measurement layer
  and station; inactive edges and service masks, with identifiers and provenance.
- Vertex distribution and deterministic stress vertices; η, φ, charge and momentum
  grids, including both detector sides and barrel/endcap boundaries.
- Separate material scenarios for beam pipe, local modules, supports, cooling,
  cables, magnet and cryostat, with explicit uncertainty and ownership.

Outputs should separate raw surface crossings, unique layers, paired strip
measurements and distinct muon stations. Later simulated hits and digitized hits
must have different names and denominators. A track curling back through one
sensor must not artificially improve independent layer coverage.

**INFERENCE:** given physical path lengths and material properties in consistent
units, crude budgets are `Σ length/X0` and `Σ length/λI`. Report upstream,
within-subsystem and total contributions separately. Empty reservations must
remain unknown; do not fill a tracker box with silicon or a calorimeter box with
solid absorber. Effective mixtures require density, composition/fill fraction and
preserved quantities. Scenario bounds describe assumed alternatives, not measured
uncertainties. Shower containment is not established by an interaction-length sum.

Initially compare prompt straight rays and simple uniform-field trajectory
scenarios only as explicitly labelled analytic approximations. A shared field
contract must specify units, coordinates, sign, spatial support and map identity.
The architect and physicist must define relevant bending paths; a central field
value alone does not specify the muon bending power or forward tracker behavior.

### B3 — actual geometry and transport, after the relevant approval

Use DD4hep construction and ROOT-based checks, then independently inspect the
converted Geant4 geometry. Scan material and sensitive crossings over η, φ and
vertex. Add charged particles in the same field used by reconstruction; record
field vectors and relevant bending integrals, including coil/endcap transitions.
Test numerical convergence at boundaries before attributing failures to layout.

Geant4 single-particle studies then test calorimeter containment/leakage, energy
deposition and muon penetration. Physics must first select particle species,
energies, physics list and performance observables. ACTS navigation/material
comparisons apply to the tracking representation. None is implemented by this
envelope-only proposal.

## Required report contract and decisions

Follow ADR-003: record input and script hashes; repository revision and dirty-state
identity; upstream comparison identity; units; software/build versions; commands;
seeds or deterministic sampling; field/material configurations; numerical controls;
raw counts and denominators; unavailable checks; and small reviewable summaries.
Preserve large artifacts with checksums under the eventual retention policy.

Keep numerical boundary epsilon distinct from physical clearance and acceptance
tolerance. Numerical settings need convergence evidence; physical tolerances and
coverage targets require review. With none agreed, results are descriptive,
not pass/fail acceptance.

Before the next study, resolve: vertex/displaced-particle scope; momentum and
angular grid; definitions of redundancy and hermeticity; segmentation versus layer
counting; material scenario ownership; magnet representation; and compatible
runtime versions. No new framework, detector build or production geometry change
is needed to discuss the present envelope proposal.
