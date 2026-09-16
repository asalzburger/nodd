# DES-003 — Global detector envelopes and interfaces

- Status: **DRAFT — first proposal for discussion**, not approved geometry.
- Created / updated: 2026-09-16.
- Authors: AI-assisted project coordinator, System Architect, subsystem technicians, software engineer and Physics and Performance Validation.
- Human owner / technical reviewers / approving humans: TBD; no sign-off.
- Review issue: not separately created; the proposal PR is the initial discussion venue.
- Related decisions: [ADR-001](../decisions/ADR-001-upstream-baseline.md), [ADR-003](../decisions/ADR-003-validation-and-artifact-policy.md), [ADR-006](../decisions/ADR-006-global-envelope-and-field-hypotheses.md), all DRAFT.
- Implementation PR / sign-off record: pending; none authorized here.
- Governing context: [PROJECT](../../PROJECT.md), [development plan, stage B](../DEVELOPMENT_PLAN.md).

## 1. Proposal and scope

**NODD DESIGN CHOICE — proposed:** take candidate **E1** below as the first
concrete global envelope hypothesis. It keeps the recognizable ODD sequence of
silicon tracking, inner solenoid, electromagnetic and hadronic calorimetry, and
outer muon detection. It retains the tracker scale and outer detector scale while
enlarging integration and calorimeter reservations. The initial muon role is
tracker-assisted identification and trajectory matching. Independent muon momentum
measurement remains an alternative, not an implied capability.

E1 is selected for comparison and review, not demonstrated technical superiority.
The numbers let subsystem requests confront each other. They do not establish
buildability, adequate services, shower containment or detector performance.
Discussion may change the coil ordering, coverage and dimensions before sign-off.

This round covers global setup, enclosures and interfaces. It does not select
sensor/chamber technology, layer counts, materials, electronics or detailed routes,
and it changes no production DD4hep geometry or reconstruction. Stage A remains
complete for progression by human direction; these are tests of new choices, not a
request to repeat A. The study ODD revision and ColliderML production identity
must still be distinguished when making quantitative comparisons.

## 2. Team inputs and evidence

| Role / input | Main contribution |
| --- | --- |
| [Tracker technician](inputs/DES-003-tracker-envelope-input.md) | Keep ODD-scale assembly; investigate forward tracking; expose missing services/timing space |
| [Calorimeter technician](inputs/DES-003-calorimeter-envelope-input.md) | Depth/composition, polygon dimensions, packaging and coil-order alternatives |
| [Muon technician](inputs/DES-003-muon-envelope-input.md) | Correct translated parent envelopes; distinguish identification from independent spectrometry |
| [System Architect](inputs/DES-003-system-architecture-input.md) | Reconcile requests into E1, reserve shared interfaces and expose coupled tradeoffs |
| [Software engineer](inputs/DES-003-software-validation-input.md) | Staged allocation, active-surface, material and transport diagnostics; reuse DD4hep/Geant4/ACTS |
| [Physics and Performance Validation](inputs/DES-003-physics-input.md) | Challenge coverage, magnetic leverage, material accounting and containment claims |

The input memoranda preserve alternatives: their individual requests are not all
adopted simultaneously. E1 and the machine-readable allocation below are this
proposal's consolidated candidate. All source IDs resolve in the
[catalogue](../../reference/manifest.yaml); inputs retain precise PDF/factory locators.

| Claim | Classification | Evidence and consequence |
| --- | --- | --- |
| F1 | FACT | SRC-ODD-UPSTREAM at `c167363f3d4ad1540a577af99071283caf54f3a6`, `xml/OpenDataDetectorEnvelopes.xml`: tracker allocation r=0.025–1.140 m, half-length 3.150 m; calorimeter and muon allocations are tabulated in the inputs. These are source definitions, not new runtime checks. |
| F2 | FACT | Same source, `factory/calorimeter/ODDPolyhedraBarrelCalorimeter_geo.cpp` / `ODDPolyhedraEndcapCalorimeter_geo.cpp`: barrel radial parameters describe face geometry; endcap outer input is a circumradius. A common radial conversion is incorrect. |
| F3 | INFERENCE | Same source, `xml/detectors/CalorimeterECal.xml` / `CalorimeterHCal.xml`: summing the sourced layer repeats and slices gives normal sampling-stack thicknesses 0.2424 / 1.836 m. HCal contains substantial dense effective PCB material; depth cannot be inferred from steel alone. |
| F4 | FACT | SRC-ATLAS-TDR-030 §2.1, PDF25–26 and SRC-CMS-TDR-014 §2.2/PDF19, §3.1/PDF25: historical upgrade designs motivate investigating tracking near absolute eta 4. They do not establish nODD coverage or redundancy. |
| F5 | FACT | SRC-ATLAS-JINST-2008 §1.3/PDF38, SRC-CMS-JINST-2008 §5.1/PDF150 and SRC-CMS-TDR-019 §1.4/PDF17–19 provide calorimeter-depth precedents with different accounting boundaries. Their details and dates are retained in the calorimeter input. |
| F6 | FACT | SRC-CMS-TDR-016 §1.5.3/PDF39 and SRC-ATLAS-TDR-026 §1.4.4/PDF31 distinguish forward muon identification from standalone spectrometry; the latter describes a deferred proposed tagger. |

The 2008 overviews and dated upgrade TDRs are historical evidence, not assertions
about final installed systems. Their hardware choices are not copied wholesale.

## 3. E1 allocation and r–z drawing

Canonical numerical input: [DES-003-envelopes.json](DES-003-envelopes.json).
All table rows are **NODD DESIGN CHOICE, proposed; approving humans: none**.
Coordinates use metres, a beam-axis z and cylindrical radius r. Positive-z
allocations reflect through z=0; a row with z minimum zero spans both sides.
These plotting conventions do not settle a full DD4hep/field coordinate ADR.

| Allocation | r min [m] | r max [m] | absolute z min [m] | absolute z max [m] |
| --- | ---: | ---: | ---: | ---: |
| Tracker assembly | 0.025 | 1.140 | 0 | 3.150 |
| Tracker interface reserve | 1.140 | 1.240 | 0 | 3.150 |
| Coil / cryostat reserve | 1.240 | 1.440 | 0 | 3.350 |
| ECal barrel | 1.500 | 1.860 | 0 | 3.300 |
| ECal endcaps | 0.315 | 1.860 | 3.450 | 3.810 |
| HCal barrel | 1.960 | 4.000 | 0 | 3.810 |
| HCal endcaps | 0.355 | 4.000 | 3.960 | 6.000 |
| Muon barrel allocation | 4.150 | 6.762 | 0 | 7.200 |
| Muon endcap allocation | 0.54073 | 7.000 | 7.200 | 10.270 |

![DRAFT E1 global envelope drawing; allocations are not sensitive volumes](figures/DES-003-envelope-rz.png)

[Vector drawing](figures/DES-003-envelope-rz.svg).
Outer radii bound all polygon corners; inner radii bound the closest permitted
radial extent. These are axisymmetric enclosures, not imported polygon parameters,
active surfaces or uniformly filled material. Touching allocation boundaries
transfer ownership; actual geometry still needs reviewed tolerances and clearances.

### Rationale, concessions and omissions

- **NODD DESIGN CHOICE:** retain tracker size while adding a shared 0.100 m radial
  support/service reservation. Timing remains **UNALLOCATED**; a possible claim
  on this space requires a fit study. Local supports inside the tracker and shared
  outgoing services must be counted separately.
- **NODD DESIGN CHOICE:** reserve 0.200 m radially for coil/cryostat study and move
  ECal outward. This replaces ODD's thin-shell approximation with visible space
  for a proposal; it is not a derived magnet thickness or validated material model.
- **NODD DESIGN CHOICE:** enlarge calorimeters, keep the inherited endcap inner
  apertures provisionally, and move the muon barrel start outward. Keeping the
  muon outer radius costs 0.614 m of its previous radial host space. Stations and
  any return material must be reconsidered together; do not compress them blindly.
- **NODD DESIGN CHOICE:** leave timing active volumes, beam-pipe profile, forward
  calorimetry, return/shielding structures and exact shared support/service
  footprints open. Their absence from the drawing does not mean zero material.

**INFERENCE:** in an ODD-like 16-sided barrel, available face-normal depth is
`r_max*cos(pi/16) - r_min`. The proposed enclosures allow approximately 0.3243 m
ECal and 1.9631 m HCal normal thickness, only about 0.0819 / 0.1271 m above the
inherited stacks. These differences are not certified packaging margins. Endcap
geometry needs its own radius convention. Containment also depends on composition,
upstream material and direction, not just depth in metres.

## 4. Field, coverage and alternatives

**NODD DESIGN CHOICE:** retain **3 T** as a nominal tracker comparison hypothesis,
inherited from SRC-ODD-UPSTREAM `xml/OpenDataDetector.xml`, `Field_nominal_value`.
No spatial field extent, fringe field, outer-field value or return system is
approved. The drawing and straight-ray diagnostic contain no magnetic transport.
The architect owns the magnet/return concept; software must use one field identity
for transport and reconstruction, including units, coordinates, sign and validity.

**INFERENCE:** entrance-edge geometry `eta = asinh(z/r)` gives approximately 3.09
for ECal and 3.11 for HCal, while the muon parent entrance reaches about 3.28.
These are not acceptance limits: a ray can miss an entrance but graze a later
boundary. Investigating tracking near eta 4 therefore exposes a significant
forward-calorimetry/muon mismatch. Forward-jet or missing-momentum applicability
requires either additional forward systems or explicit restrictions.

**INFERENCE:** the experimentally motivated screening ranges of about 24–30
radiation lengths for ECal and 9–11 interaction lengths for combined calorimetry
are comparison bands, not requirements. Neither EM shower maximum nor an
interaction-length sum establishes containment. The physics input explains
composition, leakage tails and upstream/dead-material accounting.

| Candidate | Description and benefit | Principal cost / unresolved question |
| --- | --- | --- |
| E0 | Inherited ODD allocation control | Narrow service/magnet space and effective materials remain unjustified; compare actual polygon enclosures |
| **E1** | Expanded inner-solenoid candidate above; preserves ODD ordering | Pre-ECal magnet material; larger calorimeters reduce muon room; magnet/service adequacy open |
| E2 | External solenoid with expanded calorimeters, based on calorimeter input C1 | Coil beyond calorimeters requires new dimensions, support/return study and revised muon layout |
| E3 | Independent external muon spectrometer | Needs bending integral, coils/return/supports and lever arm; not demonstrated to fit inherited scale |

E2/E3 are architecture alternatives without complete global numerical allocations.
Compare their physical consequences before approving E1. Tracker-assisted muon
identification itself still requires leakage, background and matching studies.

## 5. Interface register

The System Architect coordinates physical interfaces; subsystem owners provide
local inventories and requirements. The software engineer owns representations;
Physics and Performance Validation independently challenges the implications.
The coordinator routes coupled tradeoffs to the human reviewer.

| ID | Endpoint owners | Initial contract and unresolved handoff |
| --- | --- | --- |
| IF-01 | Architect / tracker | Beam pipe, first active radius, supports and forward aperture; pipe profile not assigned by tracker box |
| IF-02 | Tracker / architect | Shared r=1.140–1.240 m band; define local-to-shared cable/cooling/power handoff and timing competition |
| IF-03 | Architect / calorimeter | Coil/cryostat ends and material; r=1.440–1.500 m radial interface is proposed space, not demonstrated clearance |
| IF-04 | ECal / HCal, architect coordinating | r=1.860–1.960 m interface; packaging, electronics, shared supports and staggered transitions |
| IF-05 | Calorimeter / muon / architect | r=4.000–4.150 m interface, leakage, first station, return material and service routes |
| IF-06 | Architect / software | Units, enclosure conventions, field identity, geometry/version mapping; no implicit physical defaults |
| IF-07 | Subsystems / physics | Active surfaces, independent measurement counts, material scenarios and observable definitions |

The tracker-to-ECal axial gap at absolute z=3.150–3.450 m remains unassigned
integration space, including competing coil-end and service needs. ECal and HCal
barrel/endcap transitions at 3.300–3.450 and 3.810–3.960 m, respectively, require
joint support/routing proposals. Space behind HCal endcaps is not assumed empty
or wholly usable. Muon barrel/endcap reservations meet at 7.200 m without certified
installation clearance. A two-dimensional drawing cannot allocate azimuthal routes.

Each material contribution must have exactly one owner. No return steel or cable
mass may also remain hidden in a calorimeter mixture. Shared-interface changes
require both endpoint owners to review the resulting proposal.

## 6. Validation and present evidence

The isolated **PROTOTYPE** [allocation tool](../../tools/envelope_study/study.py)
and [diagnostic report](../validation/DES-003-envelope-diagnostics.json) address
only rectangles and prompt straight rays. The report retains input/script hashes,
software versions, command and deterministic sampling. No acceptance tolerances
have been selected.

Recorded observations: the listed rectangles have no positive-area pair overlaps.
At eta 3, the ray intersects ECal, HCal and muon endcap allocations. At eta 3.5 it
misses ECal and traverses only about 0.128 m of HCal allocation; at eta 4 it crosses
only the tracker allocation. These are allocation path lengths, not material
budgets, layer/hit counts, efficiency or shower leakage. No phi cracks, displaced
vertices, bending, active boundaries or response are represented.

| Question / proposed requirement | Classification | Next measurement and acceptance state |
| --- | --- | --- |
| R1: coherent allocations and reproducible conventions | NODD DESIGN CHOICE | Rectangle and polygon checks now; actual clearances/overlaps after geometry exists; tolerances pending |
| R2: adequate tracking/muon measurement coverage | NODD DESIGN CHOICE | Count distinct surfaces/stations versus vertex, eta, phi and momentum; redundancy definition and target pending |
| R3: credible material and calorimeter depth | NODD DESIGN CHOICE | Component scenarios, directional X/X0 and interaction lengths; species/energy/angle shower studies later; leakage limits pending |
| R4: coherent magnet and field | NODD DESIGN CHOICE | Physical magnet/return proposal; field vectors/integrals and transport/reconstruction identity; accuracy pending |
| R5: physically connected services without double counting | NODD DESIGN CHOICE | Named handoffs, route sectors, component loads and aggregate material; capacities pending |

Software recommends a staged progression: allocation diagnostics now; active
surfaces and material scenarios next; then approved DD4hep geometry with DDRec
material scans, Geant4 transport/showers and ACTS tracking conversion/navigation.
Use existing tools where suitable rather than creating a competing transport
framework. DD4hep construction, physical overlap checks, Geant4 simulation, field
solutions and performance validation have **not** been run for this proposal.

## 7. Prioritized follow-up questions

| Priority / ID | Decision or evidence needed | Owner | Needed before |
| --- | --- | --- | --- |
| P0 / Q1 | E1 inner coil or E2 outer coil? Credible coil/cryostat/return and upstream-material scenarios | Architect, calorimeter, physics | Architecture sign-off |
| P0 / Q2 | Identification only or independent muon momentum? Can chambers and return structures share reduced host? | Coordinator, muon, architect, physics | Architecture sign-off |
| P0 / Q3 | Which forward-jet, missing-momentum and tracking use cases require coverage beyond the drawn apertures? | Coordinator, physics, all subsystems | Coverage decision |
| P0 / Q4 | What supports/services/timing fit, where do they leave, and what material is counted once? | Architect and subsystem owners | Interface acceptance |
| P1 / Q5 | What does dense HCal effective material represent; does a credible inventory preserve depth? | Calorimeter, physics | Calorimeter envelope acceptance |
| P1 / Q6 | Which active layouts provide independent measurements across transitions and displaced vertices? | Tracker, muon, software, physics | Layer/station design |
| P1 / Q7 | What species, energies, vertex distribution and leakage observables define sufficient containment? | Physics, coordinator | Quantitative acceptance limits |
| P1 / Q8 | What coordinate/field/readout contracts and compatible tool versions govern execution? | Software, architect | Transport/reconstruction studies |
| P1 / Q9 | Which exact ODD/ColliderML configuration is used for each comparison? | Software | Any baseline-dependent comparison |

## 8. Review and implementation boundary

The PR is the initial proposal and discussion record. Human comments may change
the numbers and alternatives; the JSON, drawing and diagnostics must then be
regenerated consistently. Review must distinguish agreement to continue studying
E1 from sign-off of an implementable architecture.

Human technical, domain, validation and approval assignments remain **TBD**.
Approval requires an identified reviewer, exact revision, conditions and explicit
sign-off record using the [template](../signoff/TEMPLATE.md). Merging a draft or
an agent's recommendation is not sign-off. Detailed component implementation
remains a separate authorized stage. DES-001/002 retain their proposed pixel and
support meanings; this document does not implement or approve them.
