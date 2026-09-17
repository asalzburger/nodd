# DES-003 — Muon review round 1

- Status: DRAFT; dated 2026-09-17; no human design sign-off.
- Scope: response to [PR #4](https://github.com/asalzburger/nodd/pull/4), global envelopes and interfaces.
- Supersedes the recommendation to prioritize identification-only in the [initial muon input](DES-003-muon-envelope-input.md); preserves its historical evidence.
- Human direction: 14 TeV HL-LHC scenario; muon coverage `|η| < 3` baseline and `3.5` stretch; investigate all three magnet architectures, including standalone toroidal spectrometry; dedicated spectrometer-magnet design comes later; estimate punch-through before proposing added absorber steel.

## 1. What an outer solenoid can and cannot establish

**INFERENCE:** a coil outside the calorimeters can extend useful bending between tracker and outer muon measurements. Comparing the tracker trajectory with a measured outer segment can improve a combined fit if field, energy loss, scattering and alignment are controlled. That is a credible alternative to a separate spectrometer magnet for some physics objectives, but it is not automatically an independent muon momentum measurement.

If all muon stations sit outside the main bending region, they may measure mainly the outgoing direction. A tracker input then supplies the incoming trajectory. A beamspot constraint can add information for prompt particles, but its result must be distinguished from a fit independent of both tracker and vertex. Displaced muons make this distinction particularly important. Return/fringe fields may provide additional standalone leverage; only their vector field and station placement can establish how much.

**FACT — SRC-CMS-YOKE-COSMICS-2010, §§1–2, PDF3–5:** CMS measured bending between the tracker and first muon station, and also used yoke-field measurements for standalone reconstruction. The paper explicitly distinguishes fits with and without a vertex constraint and identifies alignment as critical to the combined high-momentum measurement. Thus it supports the measurement strategy, not an inference that an arbitrary outer coil provides adequate standalone resolution. [CMS operational field study](https://arxiv.org/abs/0910.5530v2)

**INFERENCE:** useful screening quantities are the signed bending components of `∫(t × B) ds`, their distribution between measured surfaces, and the displacement response to inverse momentum. A scalar integral of `|B|` misses direction changes and cancellations. In a small-angle, approximately constant-momentum segment, `Δθ ≈ 0.2998 q ∫B_perp ds / p`, with tesla, metres and GeV/c. This is a Lorentz-force approximation, not a resolution prediction. Field integral, station uncertainty, alignment and material covariance must be considered together.

## 2. Is an iron yoke required?

**INFERENCE:** iron is not a fundamental requirement for generating a solenoidal field. Flux can return through air or a deliberately arranged return-coil system. Removing iron changes the entire field solution, stray field, support and stored-energy problem; it does not preserve the original magnet's field while merely deleting material. Ferromagnetic calorimeter absorbers also contribute and must remain in the solution.

**FACT — SRC-CMS-YOKE-COSMICS-2010, §1/PDF3:** the CMS yoke contributes about 8% of its central field; its stated roles include field homogeneity, flux return/stray-field reduction and absorber material between muon stations. This is specific to CMS, not a universal fraction or a reason to copy its steel inventory.

**FACT — SRC-CMS-FIELD-MAP-2023, §§1–2/PDF2–3:** the operational CMS field-map description includes iron/air interfaces and geometrical asymmetries; sparse direct field measurements do not replace the calculated spatial map. Forward absorber and shielding structures appear in its magnet model. [Field-map paper](https://arxiv.org/abs/2401.01913v1)

| Architecture to retain | Principal benefit | Principal unresolved global consequence |
| --- | --- | --- |
| Iron-free inner/outer solenoid plus tracker-assisted muons | Avoids mandatory extra iron; outer coil offers a longer combined-measurement lever arm | Fringe/return flux, stray field, upstream material, independent-momentum capability and background rejection |
| Solenoid with instrumented iron return | Return flux can provide muon bending and steel can filter hadrons | Space, mass, saturation, scattering and field/material co-design; no steel amount chosen |
| Air-core toroidal standalone system | Bending among muon stations without a massive iron return | Coils/cryostats/support sectors, barrel/endcap transition and field integral; fit within ODD size unproven |

**NODD DESIGN CHOICE — proposed:** keep all three in the comparison. Preserve the outer muon host against unrelated claims until their minimum space requests are known. Do not label that host as a demonstrated toroid fit. The existing ATLAS evidence (SRC-ATLAS-JINST-2008 §6.1/PDF194–195) provides an engineered air-core precedent with substantially different dimensions. Dedicated magnet design is deferred; the need to reserve its interfaces is immediate.

## 3. Coverage-driven apertures and forward handoff

**INFERENCE:** for prompt straight rays from the nominal interaction point, `r = |z|/sinh(|η|)`. The following are arithmetic aperture constraints, not sensitive coverage results; bending, vertex extent, inactive edges and service/shielding clearance are omitted.

| Absolute z [m] | Ray radius at η=3 [m] | Ray radius at η=3.5 [m] |
| ---: | ---: | ---: |
| 7.200, host entrance | 0.7187 | 0.4352 |
| 7.580, inherited first station centre | 0.7566 | 0.4582 |
| 8.350, second | 0.8335 | 0.5048 |
| 9.120, third | 0.9104 | 0.5513 |
| 9.890, fourth | 0.9872 | 0.5978 |

The inherited third station inner radius of 0.946 m misses the η=3 ray at its centre. The existing 0.54073 m mother aperture excludes the η=3.5 ray at its entrance; the first two inherited station centres also miss that ray. Widening a mother volume alone fixes neither sensitive stations nor shielding conflicts.

**NODD DESIGN CHOICE — proposed:** retain barrel host `r=4.150–6.762 m, |z|≤7.200 m` and endcap host `|z|=7.200–10.270 m, r≤7.000 m` for the initial comparison; lower the endcap host inner radius to **0.400 m** as a stretch reservation. The new radius rounds below the derived 0.4352 m entrance constraint; its 0.0352 m difference is unvalidated space, not an engineering tolerance. Rework actual inner edges station by station against the table. Beam-pipe/shielding and rate feasibility are unresolved. No magnet/absorber mass is silently placed in this reservation.

**Coordinated calorimeter candidate:** detached forward calorimetry at `|z|=11.2–13.2 m, r=0.12–1.5 m` avoids the current muon host ending at 10.270 m. These are the calorimeter technician's proposed dimensions, not muon requirements. This removes the rectangle collision of a compact forward plug, but creates a performance interface: a calorimeter downstream of a muon station cannot filter hadrons before that station. For muons near η=3–3.5, establish adequate upstream endcap depth, tolerate and quantify the background, or study an additional downstream tagger. None is selected here; do not add steel to conceal the issue. At z=13.2 m the η=3/3.5 rays lie at r=1.3176/0.7979 m, illustrating the competing forward paths.

## 4. Catalogue requested at initial-input line 59

Interpretation: catalogue the proposed geometric-to-transport validation studies, rather than declare envelope counts to be hits. Physics and software should maintain the following evidence products:

| ID | Study/output | Inputs and limitation |
| --- | --- | --- |
| MU-V01 | Distinct station intersections, entrance/exit locations, path length versus η/φ/vertex | Actual active shapes and dead sectors; parent intersections are only preliminary |
| MU-V02 | Number and orientation of independent measurement coordinates, lever arms and transition gaps | Layer/readout contracts; multiple gas steps in one station are not independent stations |
| MU-V03 | Vector field samples, signed bending integrals and displacement response | Physical magnet scenario and material map; compare iron-free, yoked and toroidal hypotheses |
| MU-V04 | Material to/between stations, energy loss, scattering and stopping fractions | Component inventories and transport; report uncertainty scenarios |
| MU-V05 | Hadron leakage/punch-through, decay muons and backgrounds reaching stations | Calorimeter shower studies first, then 14 TeV collision/pile-up samples; no added-steel optimization before evidence |
| MU-V06 | True sensitive crossings → hits → segments, with inefficiency/occupancy variations | Explicit response assumptions; keep each denominator distinct |
| MU-V07 | Identification, fake rate, charge assignment and momentum resolution | Separate tracker-combined, muon-only with vertex constraint and unconstrained standalone; include displaced cases |
| MU-V08 | Field/alignment/material systematic variations and reconstruction consistency | One map identity in transport/reconstruction; no precision claim from field central value alone |

Record momentum/species, charge, η/φ, vertex, configuration hashes and random seeds. Numerical pass thresholds and spectrum/pile-up choices remain for the physicist and human review. MU-V01 can start now; later products require staged physical models. This catalogue does not authorize their production implementation.

## 5. Source additions and checks

New source metadata for the central catalogue:

- **SRC-CMS-YOKE-COSMICS-2010:** CMS Collaboration, *Precise Mapping of the Magnetic Field in the CMS Barrel Yoke using Cosmic Rays*, CMS-CFT-09-015; arXiv:0910.5530v2, 2010-01-04; JINST 5 T03021; DOI `10.1088/1748-0221/5/03/T03021`. Public URL above; PDF read and local copy downloaded; hash in central catalogue; access 2026-09-17; redistribution not assessed.
- **SRC-CMS-FIELD-MAP-2023:** Nicola Amapane and Vyacheslav Klyukhin, *Development of the CMS Magnetic Field Map*, arXiv:2401.01913v1, 2024-01-02; Symmetry 15 (2023) 1030; DOI `10.3390/sym15051030`. Public URL above; §§1–2 PDF inspected and local copy downloaded; hash in central catalogue; access 2026-09-17; redistribution not assessed.

Checked aperture arithmetic with Python standard-library `math.sinh`. No field solve, transport, geometry construction, new hit study or performance validation was run. Parent session records the review contribution. Global allocations and all physics conclusions beyond cited facts remain proposals/inferences pending review.
