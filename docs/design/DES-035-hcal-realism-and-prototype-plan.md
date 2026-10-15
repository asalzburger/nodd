# DES-035 — HCAL technology assessment and realism programme

- Status: **DRAFT**
- Created / updated: 2026-10-15
- Author: Codex-assisted investigation, with separate CaloTech, SysArch and PhysVal contributions
- Human owner / engineering approvers: unassigned; sign-off pending
- Scope: evidence and proposed isolated prototypes; no geometry or technology change
- Programme: [DES027](DES-027-calorimeter-description-assessment.md), [DES028](DES-028-calorimeter-cassettes.md), [DES029](DES-029-calorimeter-assemblies.md), [DES034](DES-034-siw-service-envelopes.md)
- Operating direction: [ADR006](../decisions/ADR-006-global-envelope-and-field-hypotheses.md); 14 TeV HL-LHC studies and calorimetry toward |eta| < 5
- Source snapshot: nODD `5b4e5d9e563505aea17e9b792458708c3175ec4a`; open ECAL source revisions below
- Evidence: [source identity and arithmetic](../validation/DES-035/baseline-evidence.json); [session and specialist handoffs](../../logs/codex/SESSION-2026-10-15-hcal-realism.md)
- Issue / implementation PR: none created by this investigation

## Assessment

**INFERENCE — technology:** retain steel–scintillator as a credible HCAL baseline, particularly in the barrel. It has a strong experimental basis. A finely segmented SiPM-on-tile implementation is also credible, provided the readout, radiation environment, cooling and data architecture are designed for the intended collision conditions. Evidence for a technology family does not qualify the present ODD stack or the nODD prototype electronics.

**INFERENCE — regional scope:** an identical warm tile package across barrel, endcap and forward regions is not yet justified. Decide scintillator/SiPM operating conditions and the endcap technology boundary from position-dependent dose, fluence, occupancy and end-of-life signal-to-noise. Keep silicon sampling or a separately designed forward technology as alternatives where the tile solution cannot meet those requirements. This does not reverse the recorded preference for steel–scintillator HCAL.

**INFERENCE — current model:** ODD is a useful ideal sampling detector. Its continuous sensitive sheets, effective electronics material and logical segmentation omit several mechanisms that govern construction, acceptance and response. The existing nODD physical prototypes improve this substantially, but their explicit components remain hypotheses and their complete assembly has serious geometric losses. Neither model has established realistic hadron-collider energy response in the evidence examined here.

**NODD DESIGN CHOICE — proposed priority:** develop a continuous-readout tile module and a shared-service carrier, then a barrel slab and an endcap wedge. Recalculate absorber depth when replacing effective material, and require shower and pileup evidence before choosing a complete HCAL envelope. Human approval remains pending.

## What “current HCAL” means

These three representations must remain distinct.

| Representation | Verified content | Applicability |
| --- | --- | --- |
| Upstream ODD HCAL | Canonical `OpenDataDetector/OpenDataDetector` main observed at `446d612dab5627e5849e1f01a1d3d9b633169218`; the HCAL XML, material XML, envelope XML and both factories match all five retained DES027 hashes | Current source audit; no new native ODD run |
| nODD DES028/029 | Physical tile/cassette and isolated complete barrel/endcap prototype, on main; retained geometry/mass/material/ID checks and sparse muon transport | Existing executed component evidence; unsigned engineering and response |
| Current LAYOUT001 / DES034 | Service-constrained enlarged HCAL contour around the selected Si–W ECAL candidate | Empty planning outline; the detailed DES029 placement inventory and totals have not been regenerated into it |

The separately pinned ODD submodule at `d70556f33b1c36abdf101a07ad8cf57eb56fbdf1` and the earlier study at `c167363f3d4ad1540a577af99071283caf54f3a6` remain comparison identities. Matching the five inspected files establishes only those files' equality. It does not establish whole-release equivalence. The maintained detector entry point does not thereby acquire a production HCAL.

### ODD sampling and material

**FACT — SRC-ODD-HCAL-CURRENT:** `xml/detectors/CalorimeterHCal.xml` lines 9–20, 42–59 and 63–85; material XML lines 30–39 and 127–135. Barrel and endcaps repeat the same 36-layer recipe:

| Slice per layer | Thickness | Representation |
| --- | ---: | --- |
| Steel235 | 30 mm | Density 7.85 g/cm³, Fe 99.8% / C 0.2% by mass |
| siPCBMix | 16 mm | Density 5.050769 g/cm³; copper mass fraction 0.818763 |
| Sensitive “Polystyrene” | 3 mm | Density 1.032 g/cm³; inherited C19H21 recipe |
| Air | 2 mm | Commented as services; no routed hardware inventory |
| Total | 51 mm | 1,836 mm normal stack over 36 layers |

**FACT:** logical cells are 30 × 30 mm; the barrel uses CartesianGridXY and the endcaps CartesianGridXZ. The factories make sensitive trapezoidal sheets. They do not place individually wrapped tiles or photodetectors. The 16-sector barrel has zero nominal stave gap; the endcap factory receives a 2.5 mm half-gap.

**INFERENCE — constructed bounds:** source dimensions and layer sums imply barrel apothems 1.600–3.436 m, outer corner 3.503315 m, half-length 3.450 m; endcap front/back |z| = 3.600/5.436 m, inner apothem 0.355 m and outer corner 3.436 m. These bounds follow the audited factory conventions.

**INFERENCE — the PCB is also substantial absorber:**

\[
36(1.6\,\mathrm{cm})(5.050769\,\mathrm{g/cm^3})
=290.9243\,\mathrm{g/cm^2},\qquad
m_{\rm Cu}/A=238.1982\,\mathrm{g/cm^2}.
\]

That copper corresponds to 265.846 mm of solid Cu distributed through the stack. Using the PDG nuclear interaction length for Cu, 137.3 g/cm², its elemental contribution is approximately **1.735 interaction lengths**. For scale, 1,080 mm of pure iron divided by the PDG 167.7 mm nuclear interaction length is about **6.44 interaction lengths**. These are elemental screening estimates, not native Steel235/mixture depths, pion interaction lengths, or containment predictions. Sources: SRC-PDG-CU-2025 and SRC-PDG-FE-2026, density and nuclear-interaction-length rows.

Replacing this mixture changes the absorber distribution, sampling fraction, shower start and leakage. Retaining 36 × 30 mm steel does not preserve ODD's interaction depth. Do not silently interpret 1.6 cm as a typographical 1.6 mm, or recover containment by tuning an electronics mixture. Specify electronics from hardware and choose any additional absorber through a separate, justified depth study. The inherited scintillator recipe also needs a composition/dopant review; a material name is insufficient optical provenance.

**FACT / static software concern:** both `placeStaves` loops number modules 1–16, while XML reserves four unsigned module bits. **INFERENCE:** 16 is outside the declared 0–15 field range. Require native encoding/decoding and collision checks before reusing that scheme; this investigation reports a range inconsistency, not an observed runtime collision. New prototypes should retain the existing nODD zero-based hierarchy and verify physical tile-to-cell mapping.

## Hadron-collider technology evidence

All entries in the following table are **FACT** about their named experimental systems. The following recommendations are **INFERENCE**, not adopted dimensions or operating points.

| Evidence | What it establishes | Limit on transfer to nODD |
| --- | --- | --- |
| [ATLAS Tile operating experience](https://arxiv.org/html/2401.16034v2), SRC-ATLAS-TILE-RUN2, §§2, 5, 7 | Steel/scintillator sampling can operate in pp collisions with a complete calibration, monitoring and reconstruction system | Tile uses its own optical and photodetector architecture; its performance is not a measurement of 30 mm direct-SiPM tiles |
| [CALICE AHCAL](https://arxiv.org/html/2209.15327v1), SRC-CALICE-AHCAL-2022, §§2.2–2.8 | Built SiPM-on-tile hardware: 360 mm HBU, 144 channels, 3 mm tiles, four 36-channel SPIROC2E ASICs, reflectors, cassettes and interfaces | Intended for electron–positron collider conditions; acquire/store/read operation and power pulsing require a different rate/trigger assessment |
| [CMS HGCAL readout-chain validation](https://indico.cern.ch/event/1502285/contributions/6554663/), SRC-CMS-HGCAL-TILE-CHAIN-2025, Summary | SiPM-on-tile modules, motherboards, data concentration, optical links and cooled system tests provide a modern pp architecture precedent | Prototype/system tests qualify their tested setup, not the present nODD modules or an entire operating detector |
| [HGCROC3/H2GCROC3](https://inspirehep.net/files/46efed0e0c590d31e496b6f11bdbe675), SRC-CMS-HGCROC3-2026, §1/PDF2 | Dedicated tile-compatible readout, bunch-crossing trigger sums, latency buffering and radiation-aware electronics; the stated power target is below 15 mW/channel | ASIC requirements are not tile timing resolution or measured nODD power; package, channels, latency and links must be evaluated together |
| [HGCAL cold structural test](https://cms.cern/news/hgcal-keeps-its-cool-major-testing-milestone), SRC-CMS-HGCAL-COLD-2026 | A major steel structure was tested cold, with controlled thermal conditions and dry-air protection | Mechanical test milestone; not proof that nODD needs exactly the same temperature, vessel or coolant |

The realistic technology question is therefore regional and architectural. Steel is an economical, structurally useful absorber but needs a specified magnetic grade and load path. Scintillator plus SiPM is compact and compatible with granular imaging, but light yield, radiation aging, dark current, gain drift, saturation and recovery time affect usable signals. A front end must handle acquisition, shaping, trigger latency, buffering, output bandwidth and synchronization under the selected bunch structure. Adding cooling alone cannot establish those capabilities.

**FACT — CALICE §2.3:** SPIROC2E stores signals in 16 analog-memory cells and switches between acquisition and digitization/readout. Its clock distribution is not evidence of continuous bunch-by-bunch digitization. **INFERENCE:** the nODD four-package footprint and power allowance can remain a packaging control, but the eventual electronics need an appropriate acquisition architecture. H2GCROC-class functionality is a useful comparison, not an automatic part substitution.

CMS places silicon in higher radiation/pileup regions and scintillator in lower exposure regions (SRC-CMS-HGCAL-TILE-CHAIN-2025, Summary). Use that as evidence for zoning, without transplanting a CMS eta boundary or dose map. SiPM cooling can control noise but does not automatically restore irradiated scintillator light transmission. Establish end-of-life MIP separation, dynamic range and stability together.

**FACT — SRC-CMS-SIPM-UPGRADE-2026, §3.1/PDF4–6:** a recent CMS component study examines selected HGCAL SiPMs through 5 × 10^13 n_eq/cm², with cold measurements around −35 °C. These are device/test conditions, not a universal fluence limit or an nODD operating requirement. **FACT — SRC-CMS-SCINT-DOSE-2020, §§6–7:** measured scintillator damage depends on dose rate as well as dose in the studied systems. **INFERENCE:** qualify the complete optical chain against dose rate, fluence, temperature and elapsed operation; a generic polystyrene lifetime number is insufficient.

The 30 mm transverse pitch is a defensible granularity study point. Its suitability requires occupancy, channel/power/cost and reconstruction comparisons. Constant physical pitch does not give constant angular granularity, occupancy or radiation tolerance across a detector. Compare coarser outer/back layers with finer high-occupancy regions if the results justify it; retain sufficient longitudinal information for shower separation and calibration.

The architectural alternatives below are **INFERENCE / comparison scope**, not new selections:

| Alternative | Useful role | Consequence to assess |
| --- | --- | --- |
| Direct SiPM-on-tile with embedded continuous readout | Preferred granular central-HCAL development path | Local radiation, heat, power/data concentration and maintainability |
| Scintillator with fibre export to accessible photosensors/readout | Credible alternative if moving electronics solves a regional constraint; ATLAS/CMS provide differing examples | Fibres, optical attenuation, routing space, aggregation and achievable granularity must be counted |
| Silicon sampling in the most exposed endcap regions | Conditional option when tile EOL noise/light yield is inadequate; HGCAL supplies precedent | Different cost, cooling, bias/readout, active material and response; explicit regional transition |
| LAr or another separately justified forward calorimeter | Option for a region requiring a distinct radiation/coverage solution | Cryostat, services, depth and interfaces need their own design; warm HCAL does not inherit the historical LAr ECAL vessel |

The Run-3 CMS electronics provide another concrete comparison: QIE11 integrates in 25 ns buckets and combines photodetector bias/current and temperature control with optical data export (SRC-CMS-RUN3-2024, §5.2 named readout/control subsections). Reproduce the needed functions, rather than only their geometric package outline.

## How far the nODD prototypes already progress

**FACT about repository prototypes — DES028:** one HCAL unit has 144 physical 29.7 mm tiles on 30 mm pitch, 3 mm thickness, reflector shells, SiPM recesses/packages, calibration LEDs, a PCB with explicit copper, four ASIC packages, steel skins, a copper spreader and Ti/water tubes. The body is 400 × 380 × 10.275 mm. A 30 mm absorber plus 1 mm assembly gap gives 41.275 mm pitch and a 1,485.9 mm sampling stack. Its 20 °C, 55 V bias, 2 µA/channel dark current, 5 mW/channel, 2 W/interface and water budget are **unsigned design choices**, not measured device specifications. This already replaces the opaque ODD material allocation with a component ledger.

**FACT about DES029:** the old full HCAL arrangement has 36,416 cassettes and 5,243,904 tile channels. Its ledger predicts about 2,099.816 t, 110.634 kW and 5.2935 kg/s ideal water for a 5 K rise. These are calculated consequences of the old dimensions and hypotheses, including their low coverage. The active face fraction is 52.9–78.3% by barrel layer and 38.8% in endcaps. They are face-area fractions, not particle efficiencies. Preserve these figures as a historical control; they cannot size the enlarged outline's final plant or support.

**INFERENCE:** the assumed 2 W interface per cassette alone contributes 72.832 kW before conversion loss. Carrier-level aggregation can therefore matter as much as channel power. It must account for the relocated circuitry and links rather than delete that heat by assumption. The unchanged four-by-36-channel packaging is a hypothesis; a different ASIC changes powered/unbonded channel counts, support electronics and cooling.

**FACT — retained execution:** DES028/029 native checks cover geometry, counts, masses, IDs and overlaps. DES029's sampled IP rays expose zero active crossings at |eta| ≥ 2.4 in the tested directions. Three sparse-sector 10 GeV muon events validate saved hits and hierarchy. Those are valuable checks of the implementation; no hadron-shower resolution, digitization, pileup, jet or missing-transverse-momentum qualification follows from them.

### The remaining realism gaps

| Priority | Gap and physical consequence | Minimum faithful next representation / evidence |
| --- | --- | --- |
| P0 | Continuous pp electronics unselected; a channel-power number cannot establish rate capability | Named candidate front-end architecture and measured/required noise, charge range, shaping, latency, buffering, trigger/DAQ bandwidth, synchronization and radiation behavior; matching package and carrier layout |
| P0 | End-of-life environment unspecified by position | Dose, neutron-equivalent fluence and hit spectrum/occupancy map for the chosen luminosity and shielding; device light-yield/dark-current tests and temperature/bias scenario |
| P0 | Effective absorber removal changes containment | Native material paths for old/new stacks, then high-energy hadron leakage and tail comparison; choose absorber/depth independently of electronics |
| P0 | Large empty regions in rectangle-packed endcaps; correlated barrel seams | Supported inner/edge tile and board families on carriers, explicit wraps/gaps/service bays; layer-dependent seam placement; dense eta/phi depth maps |
| P0 | Enlarged outline is not a regenerated subsystem | Repack all layers, recalculate channels, material, mass and services, then construct and validate that exact inventory |
| P0 | Cooling flow is an energy balance only | Thermal path resistance and hot-spot temperatures, circuit pressure drop, manifolds, connectors, operating and failure cases; select warm/cold operation from end-of-life requirements |
| P0 | HCAL steel is neither a qualified support structure nor a field model | Grade/composition and B–H data or stated uncertainty; supported plate segmentation, gravity/magnetic force paths, deflection and access; consistent complete installed field |
| P1 | Geant4 deposited energy is not a tile signal | Validated scintillation/quenching and collection parameterization, SiPM PDE/gain/noise/crosstalk/afterpulsing/saturation/recovery, electronics shaping/thresholds/time and calibration; optical photons only where needed to constrain it |
| P1 | LED/gain calibration does not fully monitor scintillator aging | Separate electronics/SiPM gain, optical yield and collision-response monitoring; channel equalization and uncertainty propagation |
| P1 | Missing trigger, power/data and replaceability architecture | Shared motherboard/concentrator, connector and cable inventories, current/voltage-drop/loss and bandwidth budgets, slow control, fault domains and extraction procedure |
| P1 | Whole-detector interfaces incomplete | Actual ECAL dead material, coil/cryostat, HCAL/FCal transition, services and downstream leakage included in transport; physically feasible forward hadron coverage toward the existing eta direction |

## System interfaces in the selected layout

**FACT — DES034:** the HCAL barrel outline has inner/outer apothems 2.600/4.0959 m, half-length 4.4832 m; endcap front/back |z| = 4.8832/6.3791 m. The maximum HCAL corner is 4.176143 m. Preserve apothems, corner radii and cylindrical clearances as separate quantities. A 400 mm barrel/endcap rear break is a service allocation with potential shower consequences.

**INFERENCE:** these dimensions change footprint, plate spans, packing and support loads. The ECAL external lane checks budget ECAL services; they do not demonstrate spare capacity for HCAL cooling and cables. Add HCAL loads to shared routes explicitly. Both absorber steel and support steel enter the installed field/force problem, even without a dedicated return yoke. The low-permeability HGCAL force study (SRC-CMS-HGCAL-FORCES-2024, abstract) illustrates why a material label alone does not settle forces. Do not copy its magnetic properties onto Steel235.

**FACT — forward interfaces:** DES034 reserves a 0.300 m HCAL inner apothem and an empty FCal insertion, R = 0.080–0.290 m and |z| = 4.5332–6.3791 m. **INFERENCE:** HCAL's aperture excludes an eta = 4 IP ray throughout this outline; r = |z|/sinh(eta) gives approximately 0.179–0.234 m through its endcap. At eta = 5 the ray enters the FCal reservation's inner radius only at |z| ≈ 5.9363 m, leaving about 0.4428 m axial intersection, while eta = 5.2 misses it. An accommodation check at eta = 4 cannot establish the ADR006 calorimetry direction toward eta = 5, or sufficient hadronic depth. A separate forward design and transition study is required.

## Following the ECAL prototype method

**FACT about the open Si–W prototypes:** DES030 at `654b85a48abeb38735ad7fe0866c5d1082882df7` replaces large endcap cassettes with compact boards and custom edge/inner sensor profiles on wedge carriers. DES031 at `2776266570dda13386a16863e5b0e97432f27217` uses common barrel boards, axial slabs, shared interfaces and staggered service joints. Both report material/power and native coverage, with remaining gaps visible. DES034 then exposes external service demand and port/collector limitations. These revisions are linked from [LAYOUT001](../layouts/LAYOUT-001-tracker-3t-siw.md); neither is engineering sign-off.

**NODD DESIGN CHOICE — proposed transfer:** use the same hierarchy and evidence discipline for HCAL. A full/half/edge tile family needs manufacturable scintillator profiles, reflector/SiPM coupling and carrier layouts; it should not be produced merely by clipping ideal sensitive solids. Share readout and cooling at carrier level to limit duplicated service margins. Stagger seams where mechanically feasible and retain an aligned-seam control. Preserve sector-owned absorber exactly once. Report improvement in directional active depth as well as face area, then test showers across residual cracks. This transfers a design method; HCAL optical response, sampling depth and electronics still require their own design.

## Proposed bounded work packages

Every row is a **NODD DESIGN CHOICE — proposed programme, approval pending**. The existing technology preference persists. No package authorizes production integration or silent envelope changes.

| Gate / bounded deliverable | Work and ownership | Exit evidence |
| --- | --- | --- |
| H0 — operating and material contract | CaloTech with PhysVal: retain 14 TeV study direction; specify bunch spacing, pileup range, integrated luminosity, energy/eta cases, environmental maps and EOL criteria. Reconcile ODD mixture and nODD material changes. SysArch owns boundary contracts. | Requirements-to-observables table, source/device ledger and documented unknowns; no unsupported radiation boundary or resolution claim |
| H1 — one continuous-readout tile module | CaloTech: one sourced tile/SiPM family, reflector/dimple, PCB, selected front-end concept, gain/temperature sensing, LED and connectors. SoftEng: independent geometry and identifier export. Reuse DES028 where valid. | BOM/volume/mass/channel/power agreement; all cells/IDs and negative controls; native overlaps; representative laboratory/irradiation evidence or explicit missing qualification |
| H2 — shared-service carrier | One barrel carrier and one endcap inner/edge carrier; concentrate readout, define real cooling contacts and routed ports; separate absorber and support ownership | Connected interface graph, packing and active-depth maps, complete power/bandwidth/thermal/hydraulic budgets, extraction clearance; no unexplained mixture or unconnected pipe endpoints |
| H3 — layer and sector | Repeat carrier families; common full tiles plus sourced edge shapes; stagger seams. Choose steel pitch and layer count using H0 containment cases, then reconcile current outline | Full sector native dimensions/overlaps/IDs, constituent mass, directional X0/lambdaI and sensitive crossings; nominal/adverse tolerance and seam controls; support/magnetic loads and routes assessed |
| H4 — full barrel/endcaps/forward interface | Regenerate into the selected layout; jointly own ECAL transition, external services, beam aperture, FCal and muon boundary | Recalculated whole-system counts/mass/heat/services; combined geometry and field-consistent transport; installation and forward-depth evidence; remaining acceptance losses explicitly mapped |
| H5 — physics feasibility | PhysVal defines comparisons; SoftEng supplies reproducible full transport/digitization. CaloTech supplies parameterization/calibration provenance. | Test-beam-anchored response and uncertainty, single-hadron and pileup cases, jets/MET/leakage tails; exact configurations, seeds and tolerances; human review of the achieved operating envelope |

Run H0 and initial H1 literature/component work first. Do not wait for complete electronics production to study conditional geometry, but label alternative power/noise/rate scenarios and propagate their consequences. Study response at unit/sector scale before scaling expensive full transport. Thermal/mechanical feasibility and scientific performance are separate gates; neither substitutes for the other.

## Validation requirements

The following are **NODD DESIGN CHOICE — proposed acceptance topics**. Numerical acceptance thresholds must be agreed against H0 requirements before tuning. Illustrative tests are not detector specifications.

| Requirement | Observable and method | Discriminating control / acceptance decision |
| --- | --- | --- |
| Faithful hardware | Native dimensions, volumes, elemental mass, IDs, tile/cell positions and overlaps | Analytic ledger versus persisted native geometry; invalid IDs, duplicated absorbers and blocked ports must fail |
| Directional depth and acceptance | IP eta/phi maps of active-layer count, first/last active layer, X0/lambdaI; fine scans at seams, inner rims, service breaks and transitions | ODD sheets; DES029 large cassettes; new carrier; aligned versus staggered joints with declared boundaries |
| Hadronic response and containment | Electrons, muons, charged pions/protons and neutral hadrons over the required spectrum; response, core width, low-side tails, shower profiles and escaped energy | Truth energy in active/passive/escaped components before calibration; ODD versus physically replaced material; ECAL+HCAL versus standalone HCAL |
| Compensation and sampling | e/h or e/pi behavior, nonlinear response and energy dependence; quenching/time-window sensitivity | Fixed physically sourced materials; independently calibrated test-beam comparison; software compensation evaluated separately |
| Tile and SiPM behavior | MIP light yield, spatial uniformity, noise, dynamic range and saturation/recovery versus dose/fluence, temperature and bias | Beginning/end-of-life device data; optical/response model uncertainty; no guaranteed MIP separation from bulk polystyrene alone |
| Timing and pileup | Pulse shape, bunch assignment, time slewing, late hadronic energy, occupancy, buffer/link losses and trigger primitives | In-time and out-of-time pileup; thresholds/time windows varied within sourced ranges; early timing cuts must retain assessed hadronic response |
| Calibration and stability | Channel equalization, gain and light-yield drift, dead/noisy channels, scale/resolution uncertainty | LED/electronics checks separated from scintillator aging and collision-energy calibration |
| Physics reconstruction | Jet scale/resolution and tails, MET response/fake tails, neutral-hadron efficiency, punch-through and PF confusion where PF is used | Fixed event samples, tracks, clustering and calibration first; separate geometry, digitization and reconstruction changes |
| Engineering operation | Hot-spot temperatures, circuit pressure/drop, LV current/drop, data rate, plate deflection, magnetic forces and maintenance space | Worst credible steady/fault/EOL conditions; geometry/contact/ideal-flow checks alone do not pass these criteria |

Record exact component/configuration hashes, environment, field/physics list, Geant4 datasets, seeds, pileup construction, reconstruction settings and calibration training/validation split. Compare hadronic-model alternatives and propagate measured device uncertainty. Enforce collision kinematics at each eta; a fixed high-pT sample cannot exceed the selected beam energy. Agree statistical precision before claiming tail performance. ACTS tracking geometry alone does not model showers; its contribution is the downstream track/PF interface when applicable.

## Evidence and review status

Public source metadata and locators live in `reference/manifest.yaml`; new IDs used here are listed in the evidence JSON. Current source hashes and screening arithmetic were checked in this task. Four existing audit controls, fourteen existing cassette/assembly controls, ten service-envelope controls and the service-allocation replay passed. Historic native results were inspected; DD4hep/Geant4, thermal, structural, radiation and performance studies were not rerun in this documentation investigation.

CaloTech supplied technology/readout evidence; SysArch separately assessed physical interfaces; PhysVal independently assessed the baseline scientific claims and validation needs. These contributions do not constitute expert certification or human sign-off. Human reviewers for technology/electronics, calorimeter response and system integration remain unassigned. The first concrete review decision is the H0/H1 scope and operating contract, followed by the exact proposed module/carrier design.
