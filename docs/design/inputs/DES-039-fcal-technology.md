# DES-039 input — common tungsten/fused-silica forward calorimeter

- Status: **DRAFT — PROTOTYPE evidence and technology input**, 2026-10-17.
- Assignment: `FCAL-CaloTech-01`; explicitly supplied CaloTech mandate; no native profile loading claimed.
- Input revision: `33a607b70214532cd265623241b0c250ca0da361`.
- Author: Codex, acting as CaloTech; human owner, technology reviewer and approver: TBD.
- Governing records: [ADR-006](../../decisions/ADR-006-global-envelope-and-field-hypotheses.md), [DES-034](../DES-034-siw-service-envelopes.md); parent proposal DES-039.
- Write ownership: this input only. Source catalogue integration and global geometry/routing belong to the coordinator. No runtime, production implementation or sign-off is supplied here.

## Recommendation and its limits

**NODD DESIGN CHOICE C01:** investigate a common **warm tungsten absorber with longitudinal fused-silica Cherenkov fibres**, read at its downstream face by compact cooled SiPM arrays. Use two interleaved fibre populations: full-depth `L`, and `S` beginning 100 mm behind the sampling front. This replaces the previously suggested plate arrangement with a physical route that uses rear space. It keeps the tungsten/quartz technology family while deliberately changing its sampling geometry.

The readout provides two overlapping depth weightings. It does **not** directly measure separate front EM and rear hadronic compartments. An EM-sensitive combination such as calibrated `L − kS`, and a hadron-sensitive sum, are response-model hypotheses requiring simulation and beam evidence. Neither coefficients nor energy resolution, compensation, timing, jet performance, pileup rejection or containment efficiency are specified by the envelope.

The proposed total package length is 1800 mm, including a 1200 mm sampling block and 580 mm behind that block. The installed radial envelope is R=50–290 mm, with sampling R=55–270 mm. Reducing the previous R=80 mm bore is an explicit **unsigned machine-interface amendment**; the existing beam-pipe description stops at |z|=4 m. The longitudinal package fits both reservations arithmetically. A qualified downstream pipe, shielding and heat/background assessment are still required.

## Pinned input evidence

These are **FACTS about repository proposals**, not facts establishing constructed detector performance:

| Input | Exact revision and locator | Relevant statement |
| --- | --- | --- |
| Si–W alternative | `33a607b70214532cd265623241b0c250ca0da361:docs/design/DES-034-siw-service-envelopes.md`, “Forward reservation” | R=80–290 mm, |z|=4533.2–6379.1 mm is empty; machine/pipe, shielding and supports unresolved. |
| LAYOUT-001 | Same revision, `docs/layouts/LAYOUT-001.json`, `forward_reservations[0]`, `beam_pipe` | Reservation matches DES-034; pipe R_outer=27.8 mm, described only to |z|=4000 mm. |
| LAr alternative | `72d37ee9a56182e4ba974791a848a738c19cf092:docs/design/DES-033-allegro-lar-endcaps.md`, “Forward region and response limits” | Empty insert R=80–290 mm, |z|=4850–7855.9 mm; separate prospective collar R=80–450 mm, |z|=4400–4850 mm. |
| Coverage direction | Input revision, `docs/decisions/ADR-006-global-envelope-and-field-hypotheses.md`, “Context” and proposed decision 6 | Investigate calorimetry to |eta|<5; drawings do not establish installed coverage or services. |
| Source catalogue | Input revision, `reference/manifest.yaml`, `SRC-PDG-TUNGSTEN-2025` and `SRC-CMS-HCAL-CALIBRATION-2020` | Existing source IDs inspected; new source metadata below is for coordinator integration. |

Working-tree `AGENTS.md`, `PROJECT.md`, `.agents/skills/nodd-design-evidence/SKILL.md`, complete saved assignment prompt and JSON contract were read. The workflow instructions are distinct from the pinned scientific/layout evidence.

## Public primary evidence and source metadata

Sources were inspected on 2026-10-17. No local source PDF was retained by this assignment; local filename and SHA-256 are therefore null. Links identify the actually inspected public versions. New IDs below are proposed catalogue IDs, except the already existing PDG tungsten ID. Publication day is left unspecified where the source supplies only a month or collection year.

| Source ID | Bibliographic metadata and primary URL | Precise locator and supported FACT |
| --- | --- | --- |
| `SRC-CMS-CASTOR-2021` | CMS Collaboration, *The very forward CASTOR calorimeter of the CMS experiment*, JINST 16 (2021) P02010; CERN-EP-2020-180, CMS-PRF-18-002; arXiv:2011.01185v2, 2021-02-10; DOI `10.1088/1748-0221/16/02/P02010`; [PDF](https://arxiv.org/pdf/2011.01185v2). PDF cover: CC-BY-4.0. | Section 3, printed pp6–9/PDF pp8–11, Fig4: tungsten/quartz plates at 45°, grouped five pairs per optical module; installed radius400 mm, length1600 mm; 20X0 EM, total10 nuclear interaction lengths; 16phi×14depth channels. Section1, printed p2/PDF4: usefulness at approximately one simultaneous interaction. Sections3–4: PMT radiation aging, magnetic sensitivity and pulse/readout limitations. These do not qualify high-pileup operation. |
| `SRC-CMS-HF-WEDGES-2008` | CMS-HCAL Collaboration (S. Abdullin et al.), *Design, performance, and calibration of CMS forward calorimeter wedges*, Eur.Phys.J.C53 (2008)139–166; published online2007-11-15; DOI `10.1140/epjc/s10052-007-0459-4`; [publisher PDF](https://link.springer.com/content/pdf/10.1140/epjc/s10052-007-0459-4.pdf). Copyright Springer/SIF2007; public reading only, redistribution not assessed. | Section2, printed pp141–143/PDF3–5, Figs1–2/Table1: steel absorber, beam-parallel fibres, rear bundles, independently read full/short populations;600µm core,630µm hard-clad,800µm protective buffer; source pitch5mm and short start220mm in1650mm absorber. Rear shielding/light guides are substantial. Abstract/section2: Cherenkov response is strongly noncompensating; quartz radiation hardness is not immunity. |
| `SRC-PDG-TUNGSTEN-2025` | Particle Data Group, *Atomic and nuclear properties of tungsten (W)*, 2025 table collection; precise publication date unknown; [official table](https://pdg.lbl.gov/2025/AtomicNuclearProperties/HTML/tungsten_W.html). Public reading; redistribution terms not assessed. | Rows density, nuclear/pion interaction length and radiation length:19.30g/cm³,99.46mm nuclear lambda,113.2mm pion lambda,3.504mm X0. |
| `SRC-PDG-FUSED-QUARTZ-2019` | Particle Data Group, *Atomic and nuclear properties of silicon dioxide (fused quartz)*, 2019 table collection; precise publication date unknown; [official table](https://pdg.lbl.gov/2019/AtomicNuclearProperties/HTML/silicon_dioxide_fused_quartz.html). Public reading; redistribution terms not assessed. | Rows density, nuclear interaction length and radiation length:2.200g/cm³,444.7mm and122.9mm. The analogous2025 HTML URL was inaccessible; the explicitly dated2019 table is used without pretending live2025 verification. |
| `SRC-HAMAMATSU-S14161-KAPD1064E04` | Hamamatsu Photonics, *MPPC S14160/S14161 series*, Cat.No.KAPD1064E04, November2024; [manufacturer PDF](https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/ssd/s14160_s14161_series_kapd1064e.pdf). Manufacturer copyright; no redistribution assessed. | Printed p1: magnetic-field immunity and sixteen6×6mm pixels for S14161-6050HS-04. Printed p8, drawingKAPDA0201EA:25×25mm package, nominal1.35mm thickness. Printed p2:38V typical breakdown, recommended+2.7V overvoltage,34mV/°C temperature coefficient. These catalogue values are not radiation qualification or an installed bias setting. |
| `SRC-HAMAMATSU-R7600U-M4-TPMH1318E` | Hamamatsu Photonics, *Multianode photomultiplier tube R7600U-M4 series*, documentTPMH1318E; precise issue date not independently established; [manufacturer PDF](https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/etd/R7600U-M4_TPMH1318E.pdf). Manufacturer copyright; no redistribution assessed. | Dimensional-outline drawing:25.7mm metal body is accompanied by30mm insulation-cover dimensions. Thus a26mm full PMT installation slot is not justified by quoting the metal body alone. |
| `SRC-MPPC-RADIATION-2019` | G.Blazey et al., *Radiation Tests of Hamamatsu Multi-Pixel Photon Counters*, NIM A927(2019)463–470; DOI `10.1016/j.nima.2018.12.050`; arXiv:1906.07237v1,2019-06-17; [PDF](https://arxiv.org/pdf/1906.07237v1). Public manuscript; redistribution terms not assessed. | Abstract and section4, especially4.2/4.5: irradiated S13360-2050VE devices exhibit increased noise/current and lost photoelectron peak separation at higher tested doses. Different device/application: a caution against transferring catalogue performance, not an FCAL fluence limit. |

## Sampling and material definition

All entries in this table are **NODD DESIGN CHOICES C02–C05**, subject to human review. Values taken from source fibre dimensions are deliberate adaptations; no off-the-shelf tungsten module is implied.

| Parameter | Proposed value | Physical role / rationale |
| --- | ---: | --- |
| Absorber | Pure tungsten,19.30g/cm³ screening representation | Compact depth without ferromagnetic steel; actual manufactured grade, purity, joints and magnetic susceptibility require review. A heavy alloy must receive its own composition/density calculation. |
| Sampling block |1200mm axial, R55–270mm | Leaves credible rear readout volume within01. |
| Transverse fibre lattice |3.0mm square pitch | Higher optical sampling density than the source HF design; selected for a small tungsten insert. |
| Fibre passage |0.900mm round-equivalent diameter | Gives50µm nominal radial insertion allowance around an800µm buffered fibre; groove shape and tolerances remain manufacturing work. |
| Fibre materials |600µm fused-silica core;630µm hard-clad outside;800µm buffered outside | Silica is sensitive optical medium; polymer cladding/buffer are passive and must be included explicitly or with declared composition. |
| Depth populations |AlternatingL/S lattice sites;L starts at0,S starts at100mm | First100mm has half the fibre population; S holes in that region are unfilled passage allowance in the screening model. |
| Tower partition |16phi sectors; radial boundaries55,125,195,270mm |48transverse towers, each withL/S outputs:96optical tower signals/end. This is a physical radial partition, not equalDeltaeta segmentation. |
| Supports / services |R50–55inner wall/clearance;R270–280outer support allowance;R280–290axial services | Proposed allocations. Constituent masses, real load paths and machine clearances remain unresolved. |

**INFERENCE I01:** the bulk lattice cell fractions downstream of the S start are

`fW = 1 − pi*(0.900 mm)^2 / (4*(3.0 mm)^2) = 0.9293141653`,

`fcore = pi*(0.600 mm)^2 / (4*(3.0 mm)^2) = 0.0314159265`.

Hard-clad polymer, buffer and residual passage void fractions are respectively0.0032201325,0.0212144771 and0.0148352986. At the front, half of the fibre/core/clad/buffer area is absent; the corresponding holes remain void. This is an areal average for screening, not a universal ray material depth. Clad and buffer chemistry/densities are not sourced here and must not silently become SiO2.

**INFERENCE I02:** using the tungsten contribution only, a homogenized axial crossing gives1200fW/99.46=**11.2123 nuclear interaction lengths**, or1200fW/113.2=**9.8514 pion interaction lengths**. It gives318.258X0; the100mm front weighting corresponds to26.5215X0 of tungsten. The distinction between nuclear and pion interaction lengths matters. The silica core adds approximately0.08124 nuclear interaction lengths and0.29397X0 when its reduced front occupancy is included. These numbers omit polymer, closures, seams, support plates and directional channeling; they are not containment claims.

**INFERENCE I03:** the sampling annulus is219,518.787mm². Before edge clipping, azimuthal construction gaps and joints, the block contains approximately**4724.68kg of tungsten** and17.45kg of silica core per end. About24,391lattice sites and28.05km of active fibre length/end follow from the continuum area estimate. Exact integral counts must come from the finite lattice, clearances and tower boundary ownership. Rear tails add length and are optically passive for reconstruction even though particles can also generate unwanted light there.

The lattice orientation, groove cross sections, laminate thickness, positive module seams, retention and tungsten fabrication technique require a manufacturing study. A continuous homogenized block may be used only as an explicitly approximate layout/material proxy. A fibre-sensitive response simulation needs actual sampled fibres or a validated directional parameterization. Paths approximately parallel to a fibre/hole can differ greatly from I02, and3mm pitch is comparable to tungsten's short radiation length. Neither absorber fraction nor core volume fraction is the calorimeter's energy sampling fraction.

## Exact installed allocation and optical path

**NODD DESIGN CHOICE C06:** use the same1800mm per-end assembly in both layouts. Local coordinateu increases downstream from the front package face; the negative-z assembly is reflected as a whole.

| u interval / mm | Depth / mm | Allocation |
| --- | ---: | --- |
|0–20|20|Front closure, alignment and installation interface; no claimed active depth.|
|20–1220|1200|Tungsten/fibre sampling; S begins at u120mm.|
|1220–1520|300|Dark optical fan-out enclosure with continuous buffered fibre tails.|
|1520–1610|90|SiPM ferrules, carriers, temperature sensors, thermal contact and dry enclosure.|
|1610–1710|100|Front ends, summing/ADC allocation, cold plates and local headers.|
|1710–1780|70|Service breakout, connector access and strain relief.|
|1780–1800|20|Rear closure / support interface.|

**INFERENCE I04:** positioning at the reservation fronts would give installed spans|z|=4533.2–6333.2mm in01 and4850–6650mm in02, leaving45.9/1205.9mm to their respective reservation backs. Sampling spans4553.2–5753.2mm and4870–6070mm follow. These are dimensions, not clearances for a complete support/withdrawal mechanism. The separate02collar remains a separate subsystem; it does not turn this insert into a verified transition calorimeter.

**NODD DESIGN CHOICE C07 — physical light route:** each fibre stays axial through the entire absorber and exits downstream. It then follows a smooth three-dimensional tail in its ownphi-sector loom, sorting into its original radial band andL/Spopulation. It ends in a black ferrule at the sensor plane; there is no90-degree extraction inside tungsten, wavelength-shifting conversion, side air-core guide or implied optical concentration. Ends are polished; removable ferrules and alignment/black separators permit replacement and light injection. Fibre-bend transmission, surface finish and adhesive irradiation are qualification items.

The two populations remain interleaved spatially until the rear fan-out. A calibrated light-injection fibre and a dark reference are reserved per sensor cartridge. Transporting calibration light to the SiPM face alone monitors electronics/gain; it cannot independently identify loss along irradiated active fibres. A separate through-fibre transmission monitor and particle calibration are required.

**INFERENCE I05 — routing bound:** a cubic S-route across axial lengthL=300mm with lateral displacementDelta is `x=Delta(3t²−2t³)`,t=u/L. It has zero end slopes and a conservative minimum radiusL²/(6Delta). EvenDelta=220mm givesR>=68.18mm. This is an explicitly chosen geometrical bound, not a fibre supplier bend specification. Tail looms must demonstrate no crossings/interference and measured losses at the actual minimum bend radius before mechanical qualification; a free-area calculation alone does not prove every fibre route.

## Sourced photosensor footprint and electronics

**NODD DESIGN CHOICE C08:** use S14161-6050HS-04 as the concrete footprint reference, one array perL/S tower output. It establishes a physically compact SiPM option, not a purchase decision or irradiation-certified sensor. The reference module has sixteen sensor pixels; therefore the complete count is**96arrays/end,1536SiPM pixel channels/end,96calorimetric tower outputs/end**. Both ends double those counts. A sensor-array pixel is distinct from a fibre site or calorimeter tower.

Reserve a**30×30×90mm custom cartridge** around each array, including the rear carrier/thermal path rather than merely fitting its bare silicon. Arrange six rows of16cartridges, at radii95,130,165,200,235,270mm, each centered in the16phi sectors. Pair the first/second row with the inner band'sL/S, the third/fourth with the middle band and the fifth/sixth with the outer band. Common rear boards and coolant headers occupy their separately allocated100mm; the30mm square is not a complete stand-alone digitizer.

**INFERENCE I06:** for radially aligned squares, the outermost corner is`hypot(270+15,15)=285.394mm`, insideR290. The closest inner-row square corner remains inside itsphi wedge: `(95−15)tan(pi/16)−15=0.913mm` transverse margin. Radial center separation35mm leaves5mm between nominal cartridges. These small numerical margins are allocation checks only; dimensional tolerances, connectors, cold-plate paths and different thermal contraction must be budgeted before freezing hardware.

**INFERENCE I07:** continuum site counts perpopulation pertower are137.4/244.3/380.4 in the three radial bands. A whole circular bundle of the largest population, using800µm fibre outside diameter and a chosen65% packing fraction, would be19.35mm in diameter. Instead split it among the sixteen sensor pixels: at most24fibres/pixel in this continuum bound gives`0.8sqrt(24/0.65)=4.86mm` circular subbundles. They fit a6mm pixel without optical compression and avoid directing light onto interpixel gaps. Integer clipped-lattice counts must be checked and accommodated; a spare-hole/fibre allocation may increase this bound. Optical cross talk, epoxy, connector ferrules and alignment consume the remaining per-pixel margin.

**NODD DESIGN CHOICE C09:** each pixel has gain/bias trim and a low-noise front-end input; calibrated groups form the96tower signals before bulk digital export. Retain slow individual-pixel diagnostic/calibration access. Simply paralleling16large-areaSiPMs is not an established fast circuit; capacitance, signal-to-noise, dynamic range, microcell recovery/saturation and failure isolation require a circuit prototype. The power allocation below is a budget for that circuit, not an assertion that an existing ASIC meets it.

A40MHz,12bit stream for96outputs is46.08Gbit/s/end before encoding, framing or additional gains. Keeping all1536pixel samples would be737.28Gbit/s/end. These **INFERENCES** expose the aggregation requirement; neither a DAQ protocol nor link count is selected by these arithmetic examples. Pulse integration time and sampling rate must follow the final response/occupancy study.

## Power, thermal and local service assumptions

**NODD DESIGN CHOICES C10–C12:** plan continuous power; evaluate0.1mA/pixel nominal and1.0mA/pixel adverse total bias current at the manufacturer-reference40.7V room-temperature bias. Use0.05/0.20W perSiPM pixel for front-end electronics and10/20W perend for shared control/ADC/data circuitry. These currents include whatever dark plus signal current the operating scenario permits; they are stress assumptions, not measured sensor values or fluence predictions. Use85% local conversion efficiency for an additional conservative heat allowance. Bias compensation at the selected temperature requires measured per-device breakdown voltages.

| Quantity per end | Nominal | Adverse |
| --- | ---: | ---: |
|SiPM bias heat at40.7V|6.252W|62.515W|
|1536pixel front-end allocation|76.800W|307.200W|
|Shared electronics allocation|10.000W|20.000W|
|Detector subtotal|93.052W|389.715W|
|Heat including85% conversion assumption|109.472W|458.488W|
|Ideal water-equivalent flow for5K rise,cp4180J/(kgK)|0.005238kg/s|0.021937kg/s|
|Ideal water-equivalent flow for3K rise|0.008730kg/s|0.036562kg/s|

**INFERENCE I08:** the table follows `P=Npixels*Ibias*Vbias + Npixels*pFE + Pshared`, then `Pthermal=P/0.85` and `mdot=Pthermal/(cp*DeltaT)`. It excludes absorbed beam/shower heat, leakage/static environmental heat, external cable losses and plant/pump power. At a given temperature, a bias-current scenario is not an end-of-life prediction. The block's deposited beam heat is unbounded until a regional particle-flux/energy-deposition calculation exists.

**NODD DESIGN CHOICE C13:** nominally target a+5°C sensor assembly,0°C coolant supply and a3K loop rise, with a dry nitrogen enclosure whose dew point is below−20°C. These are planning conditions. Pure-water arithmetic does not select a safe0°C coolant formulation; freezing margin, inhibitor/glycol composition, heat capacity, compatibility and actual plant operation require engineering review. A5K coolant rise leaves no nominal sensor-to-return temperature margin at the+5°C target, so its table entry is only an ideal flow comparison. No thermal-resistance calculation, EOL noise target or cold-operating certification is claimed. Radiation may require substantially colder operation and a different package/plant.

The **baseline thermal accounting choice is the 3 K ideal-flow case with 85% conversion efficiency**, preserving a nominal 2 K sensor-to-return temperature difference. That difference is an allocation for a future thermal-resistance calculation, not evidence that the current carrier can remove the heat. The 5 K values remain comparisons only.

**NODD DESIGN CHOICE C14:** reserve supply/return tubes8mmOD/6mmID inR280–290mm, with rear headers in the100mm boards/cooling plus70mm breakout space. At3K water-equivalent flow, nominal/adverse6mm-bore mean speeds are0.309/1.293m/s. These are flow-area calculations; headers, parallel branches, contact resistance, pressure drop, leak containment and freeze protection remain unresolved. Do not add an unbounded heater/cooler or thermoelectric load to these totals without updating the budget.

Bring low voltage, bias, control, data and purge in axially through the outer service annulus to the rear breakout. The local package ends at its rear face; continuation beside the HCAL bore and the subsequent outward turn are a SysArch interface. They need named physical routes in both layouts. The10mm radial strip cannot itself host a90-degree coolant elbow. No external route, beam pipe, collimator, shielding, insertion rail or load-bearing connection is certified by this dossier. A roughly4.7tonne tungsten mass/end requires explicit mounting and withdrawal design.

## Alternatives and unresolved physical gates

| Alternative | What it offers | Why it is not the proposed common package |
| --- | --- | --- |
|Tilted tungsten/quartz plates with side air guides|Directly sampled longitudinal compartments and a built tungsten/quartz precedent.|The source outer radius400mm exceeds290mm. Side guide volume, collection étendue and sensor/shield space must be redesigned; a1600mm source length alone does not establish fit.|
|Two physically separated fibre EM/HAD blocks|Independent physical front/rear channels.|The front block's fibres need a transverse extraction tray, service passages or a sacrificial rear conduit through the hadronic block. Those costs are absent from a simple stack; an unsigned alternative if independent compartments are essential.|
|Compact PMTs at the rear|Established Cherenkov calorimeter readout and high gain.|Full insulation/base/shield dimensions, direction-dependent field response and radiation protection are unresolved. Quoting a25.7mm metal body as an installed26mm package is insufficient.|
|Remote shielded PMTs with extended optical tails|Can remove active electronics from the hottest/strongest-field region.|Needs a separately fitted external route and shield volume; attenuation, tail backgrounds and timing spread need measurement. Retain as fallback if local SiPM irradiation fails.|
|Cooled SiPM array reference|Actual small manufacturer package and an explicit per-pixel optical map.|Selected only as the proposed layout footprint. Irradiation, background current and electronics tests can still reject it.|

The choice of Cherenkov-only active medium entails noncompensation and a reduced response to slow shower components. Source performance numbers cannot be transferred to this tungsten/fibre pitch or the current geometry. Required gates are: downstream machine aperture and protection approval; background/radiation and deposited-power maps; finite-lattice material/acceptance scans versus signedeta/phi; optical capture, bend and irradiated attenuation studies; SiPM leakage/noise/dynamic-range tests after relevant irradiation; full analogue summing/digitizer prototype; thermal/hydraulic/load assessment; and joint shower/leakage simulations including the separate02collar and surrounding calorimeters. Electronics should be tested against both empty-bunch and high-occupancy conditions. Nothing here establishes HL-LHC pileup compatibility.

## LAYOUT-002 compact EM collar adaptation

**NODD DESIGN CHOICE C15 — separate 02 prototype component:** adapt the same absorber, buffered fibre family, L/S principle and rear SiPM arrays to a short EM collar in the existing upstream collar reservation. This is an additional component for the LAr layout, intended to investigate its forward EM transition. It does not add a second 1200 mm hadronic block. Human engineering/physics approval remains pending.

| Collar parameter | Proposed value / rationale |
| --- | --- |
| Installed envelope | |z| = 4400–4840 mm, R = 50–448 mm; 440 mm total length, 2 mm outer allowance inside the R450 mm reservation and 10 mm to the main insert front. |
| Sampling | 100 mm axial; R55–430 mm; 5.0 mm transverse pitch, 0.900 mm passages, same 600/630/800 µm core/clad/buffer dimensions. The pitch is the source HF scale deliberately adapted to tungsten. |
| Longitudinal weighting | L spans all 100 mm; S begins 50 mm behind the sampling front. The start is a project choice; L/S remain overlapping measurements. |
| Transverse towers | 16 phi sectors and radial edges 55,185,315,430 mm; 48 towers × 2 populations = 96 optical signals per end. |
| Readout | 96 reference SiPM arrays, 1536 sensor pixel channels per end, with the same 30 × 30 mm footprint. The collar uses a separate, shorter 40 mm sensor cassette whose thermal/ferrule construction requires qualification. |
| Sensor rows | R = 95,160,225,290,355,420 mm; first/second, third/fourth and fifth/sixth rows pair L/S for the three radial bands. |
| Radial allowances | R50–55 mm inner wall/clearance, R430–438 mm support allowance and R438–448 mm local service strip; constituent hardware and external handoff remain to be designed. |

**NODD DESIGN CHOICE C16 — collar axial allocation:** from its |z|=4400 mm package front, allocate 10 mm front interface, 100 mm sampling, 220 mm optical fan-out, 40 mm sensor cassette, 40 mm electronics/cooling, 20 mm service/interface space and 10 mm rear closure. These add exactly to 440 mm. The sampling lies at |z|=4410–4510 mm. The shorter boards/cold assembly is an allocation change from the main insert and is not an interchangeable qualified readout module.

**INFERENCE I09 — collar material:** the same area-cell expression with 5 mm pitch gives `fW = 0.9745530995`. Over 100 mm this contributes **27.8126 X0**, **0.97984 nuclear interaction lengths**, or **0.86091 pion interaction lengths**, before seams and other materials. The pure-tungsten screening mass for R55–430 mm is **1074.70 kg per collar/end**. First-50-mm occupancy is half the rear occupancy; no full-core area fraction should be silently applied across the whole block. Neither a 28 X0 material scale nor overlap of envelope rays proves EM containment or closes a measured efficiency gap.

**INFERENCE I10 — collar readout and fibre tail bound:** the outer sensor-cartridge corner is `hypot(420+15,15) = 435.259 mm`, below R448 mm. Each band gives continuum fibre counts per population and phi tower of 122.5,255.3,336.4; distributing the largest group across sixteen 6 mm pixels is no harder by count than the main insert, subject to the exact lattice. For a sector-edge incoming fibre and the assigned row pair, the worst transverse source-to-sensor displacement is **126.922 mm** (outer band), rather than an assumed 100 mm.

For this shorter fan-out use the geometric cosine route `x = Delta[1 − cos(pi u/L)]/2` in each displacement plane. Its conservative curvature bound is `Rmin >= 2L²/(pi² Delta)`. With L=220 mm and Delta=126.922 mm, the bound is **77.28 mm**, so a chosen 70 mm bend-radius floor is geometrically plausible. The earlier cubic bound would give only 63.56 mm here and would fail that floor. Smooth end transitions, real fibre minimum bend radius, ferrule extent, loom congestion and measured transmission must be checked; this calculation is not a completed route qualification.

**NODD DESIGN CHOICE C17 — collar cooling and power:** initially allocate the same per-pixel current/electronics scenarios, 40.7 V reference bias, 85% conversion efficiency and 3 K water-equivalent rise as for the main insert. This means another 109.472/458.488 W and 0.008730/0.036562 kg/s per end in the nominal/adverse cases. LAYOUT-002 therefore has **3072 SiPM pixel channels, 192 tower signals, 218.945/916.977 W electronics heat and 0.017460/0.073124 kg/s ideal flow per end** when collar and main insert are combined. The larger collar area does not establish its radiation or beam-deposited heat; both remain additional unknown loads. The 40 mm cold-board space needs its own thermal/contact/header validation.

**INFERENCE I11 — interface concern:** local services at R438–448 mm cannot simply continue axially with the narrow insert: the LAr endcap has a proposed R301 mm warm bore and |z|=4900 mm warm front. Such a straight route would meet the cryostat. SysArch must assign a pre-endcap outward handoff or a qualified inward transfer into the narrow insert's service corridor, including bends and connections. The 10 mm collar-to-insert gap is not itself an elbow/tool allowance. This external connection and the collar's roughly 1.1 tonne tungsten load/end remain explicit integration gates.

## Actual checks and handoff

Executed checks: pinned `git show` reads; branch/HEAD/working-tree inspection; actual public primary PDF/HTML inspection; standard-library Python arithmetic for annular area, fibre fractions, tungsten/silica mass, interaction/radiation lengths, bundle counts, cartridge corners/sector margin, heat/flow and placement lengths. The public CASTOR/HF screenshot requests failed in the browsing backend; their text and labelled figure descriptions were inspected instead. No detector construction, native overlap check, Geant4 shower transport, optical ray tracing, circuit test, thermal analysis or irradiation test was run.

Only this owned file was written. The coordinator must add the new catalogue metadata, reconcile DES-039 with SysArch and PhysVal, preserve the explicit draft bore amendment, and retain open human review/sign-off. Session/token accounting and repository-wide checks are coordinator-owned; exact subagent token counters were unavailable and must not be estimated.
