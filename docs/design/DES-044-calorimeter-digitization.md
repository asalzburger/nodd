# DES-044 — Calorimeter digitization model reuse

- Status: DRAFT
- Type: PROTOTYPE
- Created / updated: 2026-11-05
- Author: Codex-assisted CaloTech proposal; coordinator owns integration and execution
- Human owner / technical reviewer / approver: unassigned; sign-off pending
- Issue: [#117](https://github.com/asalzburger/nodd/issues/117)
- Input baseline: `96dbf57d0da7f3027e59109c1846d992d68d4d44`
- Governing artifact policy: [ADR-003](../decisions/ADR-003-validation-and-artifact-policy.md)
- Parents: [DES-031](DES-031-siw-barrel-prototype.md), [DES-032](DES-032-allegro-lar-barrel.md), [DES-033](DES-033-allegro-lar-endcaps.md), [DES-036](DES-036-hcal-common-readout-module.md), [DES-039](DES-039-common-forward-calorimeter.md)
- Implementation / validation: [draft PR #118](https://github.com/asalzburger/nodd/pull/118); [validation plan](../validation/issue117/validation-plan.md); execution results must identify their actual source revision

## Scope and operating boundary

Issue117 explicitly requests a Si–W **PROTOTYPE** using existing ODD hits, before
DES sign-off. This document proposes model selections; it grants no production
integration or physics acceptance. Geometry, materials, segmentation and
sensitive-detector response stay at the input baseline. Source inspection below
establishes available operations, not a successful nODD benchmark or experimental
validation of an arbitrary parameter set.

**FACT about scope:** DES031 is silicon/tungsten; DES032/033 are inclined/turbine
LAr; DES036–038 use scintillator tiles with SiPMs; DES039 uses tungsten and
Cherenkov quartz fibres with rear SiPM readout. The existing FCAL is not an
independent scintillation/Cherenkov dual-readout calorimeter: its long/short fibre
populations provide depth weightings. Source-model technology compatibility must
be judged against these actual choices.

**NODD DESIGN CHOICE — proposed:** start with the MarlinReco silicon model,
retain a Key4hep original-processor comparison, then adapt one existing response
chain per other technology as listed below. All choices await human review.
The target 14 TeV, mean pileup μ=200 scenario is a requested validation context;
no reviewed source parameterization is automatically qualified for it.

## Source identities and exact inspected locators

Source catalogue entries use the following IDs. Pins identify the inspected
bytes, rather than a claim that the selected revisions are released packages.
All were accessed on 2026-11-05. Immutable links lead to the source files;
function names are the precise locators used below.

| Source ID | Exact source version and inspected files | What the inspection establishes |
| --- | --- | --- |
| SRC-MARLINRECO-DIGI-2026 | [MarlinReco `255967eb855ebbc8f75ebaac190b268b63332e8b`](https://github.com/iLCSoft/MarlinReco/tree/255967eb855ebbc8f75ebaac190b268b63332e8b/CaloDigi/Realistic): `src/RealisticCaloDigiSilicon.cc`, `src/RealisticCaloDigi.cc`, `src/RealisticCaloDigiScinPpd.cc`, `include/RealisticCaloDigi.h`; root `README.md` and `LICENCE` | Silicon and scintillator kernels; shared electronics, integration and sparse-hit loop; GPL-3.0-or-later declaration |
| SRC-K4RECCALORIMETER-DIGI-2026 | [k4RecCalorimeter `03b3676cecbdf85818f6de159ecf90ffe2482cec`](https://github.com/key4hep/k4RecCalorimeter/tree/03b3676cecbdf85818f6de159ecf90ffe2482cec): `RecCaloDigi/src/{DigitiserSiliconMip,DigitiserScinPpdNpe,BaseDigitiser}.cc`; `RecCalorimeter/src/components/{CreateCaloCells,CalibrateCaloHitsTool,NoiseCaloCellsFlatTool}.cpp`; `doc/RecCalorimeter.md` | Existing EDM4hep silicon/scintillator port, calibrated cell sums and all-cell Gaussian-noise baseline; timing and conditions limits |
| SRC-CMSSW-CALODIGI-2026 | [CMSSW `aae25e49c2a06291e6d00f85f45efb23f9ceef86`](https://github.com/cms-sw/cmssw/tree/aae25e49c2a06291e6d00f85f45efb23f9ceef86/SimCalorimetry): `HGCalSimProducers/plugins/{HGCDigitizerBase,HGCHEbackDigitizer}.cc`; `HcalSimAlgos/src/{HcalSiPM,HFSimParameters}.cc`; `SimG4CMS/Calo/src/HFShower.cc`; root `LICENSE` | Dose-aware silicon/tile paths, SiPM microcell recovery, HF optical-to-analogue boundary; Apache-2.0 root licence |
| SRC-ATHENA-CALODIGI-2026 | [official Athena `e33566adf2c8ad0e0d04878e1f8630b310376718`](https://gitlab.cern.ch/atlas/athena/-/tree/e33566adf2c8ad0e0d04878e1f8630b310376718): `LArCalorimeter/LArDigitization/src/{LArPileUpTool,LArHitEMapToDigitAlg}.cxx`; `LArCalorimeter/LArROD/src/LArRawChannelBuilderAlg.cxx`; `Calorimeter/CaloTools/src/CaloNoiseCondAlg.cxx`; `TileCalorimeter/TileSimAlgs/src/TileDigitsMaker.cxx`; root `LICENSE` | Timed bunch merging, sample shaping/covariance noise/ADC, OFC reconstruction and conditions noise; Apache-2.0 except separately licensed material |
| SRC-EICRECON-CALODIGI-2026 | [EICrecon `e6a7788e853f88b86183717f9c6bc694870b8ab2`](https://github.com/eic/EICrecon/tree/e6a7788e853f88b86183717f9c6bc694870b8ab2/src/algorithms/calorimetry): `CalorimeterHitDigi.cc`, `CalorimeterHitDigiConfig.h` | Generic energy/ADC/time baseline and photon/SiPM options; LGPL-3.0-or-later file notices |
| SRC-FCC-DUALREADOUT-DIGI-2026 | [HEP-FCC/dual-readout `a5ee3f319069a505e275747e37287adffade1cf2`](https://github.com/HEP-FCC/dual-readout/tree/a5ee3f319069a505e275747e37287adffade1cf2): `DRdigi/src/DigiSiPM.cpp`, root `LICENSE`; repository metadata | Photon-time SiPM waveform adapter; Apache-2.0 root licence; the repository is archived |

The initial `DDCaloDigi` lead needs care: no file with that name exists in the
inspected MarlinReco tree. `RealisticCaloDigi.h` explicitly describes a rewrite
of ILDCaloDigi/DDCaloDigi. Current verified Key4hep names are
`DigitiserSiliconMip`, `DigitiserScinPpdNpe` and `BaseDigitiser`. Do not write a
recipe invoking an unverified legacy component name.

## Candidate effects, coupling and reuse effort

Entries below are **FACT** about the inspected code unless marked as inference.
A time gate or an analytic fast/slow integration rule is not a validated pulse
response to overlapping bunches. Sampling fractions/calibration are external
inputs, not predictions of the response kernel.

| Technology / candidate | Sampling and sensor response | Noise, pulse and pileup | ADC, time and threshold | Coupling / reuse effort |
| --- | --- | --- | --- | --- |
| Si–W: MarlinReco `RealisticCaloDigiSilicon` + shared base | Deposited GeV → Poisson e–h pairs → MIP scale. No Birks/photostatistics or SiPM saturation applies to silicon. MIP calibration is configured. Optional gain/dead-cell effects; range clipping | Gaussian electronics noise; Standard time-window or ROC integration. Original loop visits populated hits only. No radiation map or bunch train/pulse-overlap model in this kernel | Continuous MIP output, configurable range and strict `>` threshold; integrated hit time with optional smearing, not an ADC/ToA electronics emulation | Marlin/LCIO, CLHEP; small reusable kernel, larger event/integration wrapper. GPL-3.0-or-later must be preserved |
| Si–W / tile: Key4hep `DigitiserSiliconMip` / `DigitiserScinPpdNpe` | Existing EDM4hep port of those technology kernels; silicon uses ROOT Poisson rather than CLHEP. Tile branch has finite-pixel saturation and binomial smearing | Base digitizer has integration/gain/noise operations and sparse-hit loop; no full sensor ageing or pileup qualification follows | MIP or photoelectron output, time and threshold; not a raw waveform/ADC chain | Gaudi MultiTransformer, GeoSvc, UniqueIDGenSvc, ROOT, EDM4hep. Best full-processor silicon reference if existing Key4hep is available; source redistribution provenance needs review |
| Si–W: CMSSW `HGCDigitizerBase` | Charge conversion, thickness metadata and charge-collection efficiency; sensor conditions are CMS-specific | Per-channel dose/leakage/noise/pulse settings through `HGCalSiNoiseMap`; all valid IDs considered | Front-end shaper receives gain/LSB, threshold, ADC pulse and ToA information | CMSSW geometry, DetId, accumulators, conditions, CLHEP, `HGCFEElectronics`; high adaptation cost, useful irradiated-silicon follow-up |
| LAr: Key4hep `CreateCaloCells` + calibration/noise tools | Sum deposited energies per cell; calibration tool multiplies by inverse sampling fraction; no charge drift/recombination model supplied by this operation | Geometry tool prepares empty cells, Gaussian flat/file noise and filtering. Inspected CreateCaloCells is energy-only; its documentation explicitly excludes timing treatment | Calibrated energy and zero suppression; no ADC pulse samples or OFC/ToA reconstruction | Gaudi/DD4hep/EDM4hep and geometry/conditions tools. Moderate reuse, aligned with ALLEGRO infrastructure; nODD geometry-specific maps remain required |
| LAr: Athena `LArPileUpTool` → `LArHitEMapToDigitAlg` → `LArRawChannelBuilderAlg` | Timed hit maps plus sampling/ADC calibration and conditions; no transplant of ATLAS detector constants | Bunch-time shifts, pulse/derivative sampling, covariance noise and overlay. `CaloNoiseCondAlg` distinguishes electronics, pileup and total noise; an RMS conditions object alone is not a pulse simulation | Gain selection and bounded ADC samples, followed by OFC amplitude/time/quality | Athena StoreGate, cabling IDs, conditions DB, geometry, random service; high extraction effort, essential pp pulse/OOT architectural reference |
| SiPM tile: CMSSW `HGCHEbackDigitizer::runRealisticDigitizer` | Configured keV/MIP and photoelectrons/MIP; Poisson photostatistics, finite SiPM pixels/crosstalk. Birks belongs in transport or step processing, not applied again to already quenched hits | Dose-aware `HGCalSciNoiseMap` adjusts signal, dark-current noise, gain and threshold; sample accumulators pass through the front-end shaper | ADC/threshold/ToA via shared electronics. Detailed detector parameterization must be supplied for nODD | CMSSW geometry/DetId/conditions; high whole-framework cost, bounded response-component reuse preferred |
| SiPM tile: MarlinReco `RealisticCaloDigiScinPpd` | Configured MIP→PE conversion, mean saturation, binomial pixel fluctuations, pixel-gain spread | Shared Gaussian electronics/noise and time gates; no radiation/current/recovery map in this compact model | Continuous PE output and threshold; not continuous pp readout | Smaller kernel than CMS; useful low-pileup control. Do not transfer CALICE settings to nODD unchanged |
| SiPM tile: Athena `TileDigitsMaker` | Tile sampling calibration and hit pulses, with dual-gain electronics | All-channel/noise and coherent covariance options, pulse samples and overlay | ADC sampling/saturation and gain handling | PMT Tile technology and ATLAS conditions; useful pulse/overlay control, not a direct SiPM-on-tile backend |
| W/quartz FCAL: CMS `HFShower` + fibre response; `HFSimParameters` | Cherenkov-sensitive G4 step kinematics, fibre transport and photoelectron→analogue calibration; not total quartz edep times a scintillation yield | Needs optical capture/attenuation and arrival-time distribution. HF constants/PMT conversion do not model nODD tungsten/fibre/SiPM geometry | HF analogue/digitizer boundary can guide calibration; no nODD ADC/threshold selected | Strong CMS geometry/conditions coupling; optical component adaptation is substantial and requires step/optical information |
| W/quartz FCAL SiPM: HEP-FCC `DigiSiPM` | Photon arrival times → SiPM sensor backend; detector optical/sampling calibration remains outside | Configures dark count, crosstalk, recovery, afterpulse, rise/fall times, sampling and SNR | Analogue gated integral, waveform and threshold ToA; source explicitly labels ADC conversion experimental | Gaudi/EDM4hep plus external `sipm` library. Moderate waveform-adapter effort once photons exist; archived source needs supported dependency pin |
| Any technology: EICrecon `CalorimeterHitDigi` | Generic resolution smearing, simple/Poisson-photon/SiPM readout and optional ID-field summing | Pedestal Gaussian noise on populated groups; no global empty-cell inventory, physical bunch train or technology-specific radiation model | ADC dynamic range/cap, pedestal and smeared digitized time | DD4hep, EDM4hep/EDM4eic, algorithm services/JANA integration; generic fallback, not evidence of realistic silicon or LAr response |

## Recommended chains and pp gaps

Each row is a **NODD DESIGN CHOICE — proposed, approval pending**. The effort
assessments are **INFERENCES** from the dependencies and operations inspected
above; they have no measured schedule or cost estimate.

| Technology | Recommended first reusable chain | Rationale and remaining μ=200 work |
| --- | --- | --- |
| Si–W | MarlinReco `RealisticCaloDigiSilicon` response and bounded shared electronics subset, with the existing Key4hep silicon processor as an alternative full reference | Small technology-specific kernel supports an auditable first port. Separate MIP calibration, charge-generation approximation, Gaussian-noise tests and detector response. Add regional radiation/temperature/CCE/noise inputs, common-mode correlations, acquisition/pulse/OOT behavior and occupancy/zero suppression before a pp claim |
| LAr | Key4hep ALLEGRO-oriented calibrated-cell/noise chain; use Athena sample/OFC chain for the later pulse-aware extension | Matches the initial geometry technology and data model. Needed for 14 TeV μ=200: actual drift/electrode/field response, bipolar shaping and sampling phase, correlated noise, bunch-train history, gain/ADC, OFCs and regional calibration. A flat noise RMS cannot replace out-of-time pileup |
| SiPM-on-tile HCAL | CMSSW `HGCHEbackDigitizer` realistic branch with its scintillator-noise map and front-end interface | Includes a directly relevant radiation/current/light-yield path and sampled electronics. Supply nODD tile/light-yield/PDE/pixel/recovery/temperature/EOL inputs, quenching ownership, pulse overlap and dark-current distributions; validate thresholds and saturation without borrowing CMS dose maps as nODD truth |
| W/quartz FCAL | Photon-time response with HEP-FCC `DigiSiPM`; adapt/compare CMS HF Cherenkov/fibre optics before the rear sensor | Directly matches rear SiPM waveforms once photons exist. Optical-generation/capture/transport, quartz attenuation versus dose, tungsten shower development, long/short depth weights and pixel/ferrule mapping precede digitization. Then add EOL dark current, recovery, pulse overlap and ADC/DAQ behavior. No existing inspected model is a drop-in full nODD FCAL implementation |

No sampling fraction, gain, noise, threshold or electronics number is selected
for production here. Upstream defaults are source facts, not nODD measurements.
For example, the Marlin silicon default pair energy of 3.6 eV is a source
parameter; its Poisson fluctuation is explicitly documented upstream as an
overestimate of Fano-suppressed fluctuations. This cannot establish irradiated
silicon charge collection or full calorimeter energy resolution.

## Si–W prototype contract

**NODD DESIGN CHOICE — proposed:** preserve deposited-energy provenance and
units at the native boundary. Input deposits use ACTS energy/time/position units;
64-bit cell IDs remain intact. The first energy-only adapter merges all contributions by cell without a
time gate; it preserves deposited-energy-weighted time. It does not reproduce
upstream Standard/ROC integration or time smearing. Apply the selected energy
operations in their documented order. Original Marlin electronics range clipping precedes Gaussian noise; a
noise sample may therefore exceed the configured pre-noise range. A final ADC
clip is a different model and must be labelled as such.

The explicit opt-in prototype must carry a source identifier and parameters;
configuration alone must not imply calibration validity. A reused kernel or
reduced harness must record its covered methods, disabled upstream options,
adapters and changes. Compiling an original method behind a stand-in class can
verify that method, but is not a full Marlin/Key4hep original-processor comparison
on identical ddsim events.

**NODD DESIGN CHOICE — proposed extension:** a supplied channel inventory is
required to generate noise in channels without deposits. Original Marlin/Key4hep
silicon processors visit populated simulation hits only; this extension requires
independent all-channel occupancy/RMS tests and an explicit output/noise policy.
Do not create fictitious zero-energy simulated hits or truth links for noise.
Deposited-energy fractions describe truth provenance, not a fraction of signal
amplitude after noise or saturation. An event-local deterministic generator must
avoid event-order/thread-state dependence; matching seeds across different
random libraries is not by itself a matched stochastic comparison.

**NODD DESIGN CHOICE — proposed converter option:** use the EDM4hep simulated-hit
position only through an explicit mode for datasets whose producer defines it
as the cell position. Default geometry callback remains available. Require finite
positions and consistent references for repeated cell IDs, convert EDM4hep mm to
ACTS mm, and retain the input collection/producer/geometry provenance. A contribution
or step position must not be silently treated as a cell centre.

MarlinReco is GPL-3.0-or-later. Preserve that identity in reused source/components
and document any combined distribution. The existing MPL file header cannot
relicense imported GPL source. Key4hep's inspected top-level tree contains no
`LICENSE` or `LICENCE`; its silicon port has Marlin ancestry. This proposal does
not infer a permissive licence from another Key4hep repository. External source
execution avoids checking these upstream sources into nODD; redistribution and
dependency notices must be resolved for the chosen implementation boundary.

## Validation requirements

The [independent validation plan](../validation/issue117/validation-plan.md)
owns benchmark details; these requirements set the claim boundaries.

| ID / classification | Required evidence | Acceptance / interpretation |
| --- | --- | --- |
| D44-U1 — NODD DESIGN CHOICE | Noise-only events across the supplied channel inventory: unthresholded mean/RMS and signed histogram, thresholded occupancy with event/channel denominators | Compare to configured Gaussian law with a predeclared statistical criterion; truncating negative samples before RMS changes the test. Synthetic parameters validate software, not detector noise |
| D44-U2 — NODD DESIGN CHOICE | Positive-energy conversion, units, boundaries, saturation/noise order, empty cells, invalid configs, deterministic event replay and truth/noise links | Numerical tolerances justified by source precision. Test zero-energy handling explicitly; upstream silicon formula divides by expected pair count |
| D44-R1 — NODD DESIGN CHOICE | Identical ODD ddsim events through the original full processor and the ACTS prototype, matched calibration/window/noise/threshold settings and detector inputs | Compare deterministic mode per cell first; then distributions or paired random draws with the statistical method specified in advance. Kernel-only/source-extraction comparisons are narrower and must say so |
| D44-M1 — NODD DESIGN CHOICE | Single-muon silicon deposition and digitized MIP spectrum with thickness, path/angle and fit definition; calibration and evaluation split | A delta-function one-MIP test is unit calibration arithmetic, not the transport MIP peak. Report MPV/mean distinction, uncertainty and threshold bias |
| D44-P1 — NODD DESIGN CHOICE | Single electrons and photons at multiple energies and signed η; deposited sampling fraction, fixed-calibration response/linearity, resolution and leakage with uncertainties | Use a held-out fixed calibration. Compare the scale/trends with a geometry-qualified published Si–W reference; ODD and CALICE/ILD geometry differ. A match of one tuned point is insufficient |
| D44-A1 — NODD DESIGN CHOICE | Plots, compact binwise outputs, exact source/config/input hashes, versions, seeds, generation/digitization/analysis commands | Keep full event payloads local/ignored per ADR003. Binwise edges/units/counts/normalization and sufficient statistics must support the stated uncertainty |

Geometry construction/overlap gates are unchanged by this response-only proposal;
existing geometry evidence cannot stand in for the response tests above. No
claim of passing reference comparison, MIP validation, shower response or μ=200
performance is made in this DRAFT. Missing runtime/data remain explicit.

## Follow-up issue drafts

The following are listed for maintainer triage; they are not represented as
already-created GitHub issues.

| Proposed title | Bounded scope / done criteria |
| --- | --- |
| Calorimeter: adapt ALLEGRO LAr digitization and validate pulse/OOT response | Pin the Key4hep calibration/noise tools and nODD cell maps; reproduce same-hit source baseline; define drift/shaping/ADC/OFC inputs using Athena as architectural reference; validate noise covariance, pulse/phase, bunch-train μ=0/200 controls, MIP and e/γ response. Separate energy-only baseline from pulse qualification |
| Calorimeter: reuse dose-aware SiPM-on-tile HCAL digitization | Port or externally run the CMSSW realistic tile response with preserved source identity; define quenching and light-yield ownership, regional dose/temperature/noise conditions and sampled front-end; compare source and adapter on shared inputs, test finite pixels/recovery/current/thresholds, then single-hadron and pileup response |
| Calorimeter: connect FCAL Cherenkov optics to existing SiPM waveform digitization | Produce photon-time spectra from actual W/quartz long/short fibres and ferrule mapping; benchmark optical approximations against CMS HF methods without borrowing steel/PMT calibration; pin supported HEP-FCC `DigiSiPM`/sensor dependency or equivalent maintained backend; validate attenuation, EOL dark current, recovery/saturation, pulse overlap, ADC and single-particle containment/linearity |

Technical/domain/validation reviewer assignments and exact reviewed revision are
pending. Only identified humans may sign off DES044 or accept detector response.

## Current execution disposition

On 2026-11-05 the user deferred the Marlin study until appropriate software is
installed. The isolated prototype and comparison capability are preparation,
not a completed original-framework or physics validation. See the
[preparation report](../validation/issue117/README.md). No study acceptance or
design sign-off is implied.
