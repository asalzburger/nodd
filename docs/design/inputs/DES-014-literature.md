# DES-014 — Public engineering evidence

- Status: DRAFT research input; accessed 2026-10-01.
- PDF page numbers below are one-based. The catalogue records identity, hashes
  and redistribution limits. Drawings in DES014 are original, not copied figures.
- Selection: built/tested carbon supports and evaporative CO2 engineering are
  more useful here than adopting an experiment's detector dimensions wholesale.

| Fact ID | Source and exact locator | FACT | Use / boundary |
| --- | --- | --- | --- |
| EC-F01 | SRC-CMS-TEPX-DESIGN-2019, §3 PDF3; §4 PDF4 and Fig2 PDF5 | The historical design describes extraction rails and composite half-disc supports with graphite, embedded titanium cooling and electrical boards. | Supports a common composite carrier with deliberate installation interfaces. Its rail trajectory and board stack are CMS-specific; they do not establish nODD clearance. |
| EC-F02 | SRC-CMS-TEPX-THERMAL-2023, §2 PDF2; §3/Figs3–6 PDF3–4 | The study uses roughly 10 W/module and −35 °C CO2. Its titanium alternative approximately halves tube mass with similar simulated thermal performance; coating changes module temperature. | Motivate thin Ti and explicit interfaces. Transfer neither measured nODD power nor a universal thermal margin. |
| EC-F03 | SRC-CMS-TEPX-SYSTEM-2026, §1/Fig1 PDF2; §5 PDF5–6 | The support combines carbon fibre, foam and titanium pipes. With about 10 N clamping, dry contact was insufficient even at partial power; tested 25–40 µm grease improved temperature by at least 6 °C. | A controlled TIM and clamp/handling scheme are necessary. The reported −3 °C CMS criterion is not substituted for nODD's −15 °C screening target. |
| EC-F04 | SRC-ATLAS-ITK-LOCAL-SUPPORTS-2022, slide8 | Half-rings have carbon faces, foam, embedded Ti pipe, insulation/bus tape, fixation lugs and support cylinders. | Local sandwich and shared carrier are one load path. Public slide inspected locally, including the drawing. |
| EC-F05 | SRC-ATLAS-ITK-PIXEL-COOLING-2024, §1 PDF1; §2–4/Figs1/3 PDF2 | The preprint describes Grade-2 Ti welded/brazed systems, capillaries and exhaust manifolds. A 300 W evaporator example, ≈0.9 m evaporator and up to 2 m exhaust were tested; −40 °C coolant and −15 °C sensor targets are stated. | Engineering precedent for independent half-ring circuits, joints and pressure-drop tests. Ten nODD circuits and their flows remain design choices. This is the June preprint, not an inferred final production specification. |
| EC-F06 | SRC-MINTEQ-GRAPHITE-2011, slide6/PDF6 | Vendor reports 1700 W/(m K) in-plane versus 7 W/(m K) through-plane for its engineered graphite; density 2.22 g/cm³. | Do not use an isotropic 1500 W/(m K) block. These are historical vendor values, not a guarantee for a 0.30 mm bonded irradiated coupon at −40 °C. |
| EC-F07 | SRC-MINTEQ-GRAPHITE-PRODUCT, product description | Current product page advertises 1500 W/(m K) in-plane. | Sets a plausible procurement sensitivity; nODD's 1500/1000/500 cases and oriented-foot 500 target remain assumptions. No vendor selection or purchase is made. |
| EC-F08 | SRC-PDG-COPPER-2025, density and radiation-length rows | Copper density 8.960 g/cm³; X0 = 1.436 cm. | Convert X0 to 14.36 mm for the provisional flex inventory. Copper fraction is a design choice. |

Sources: [CMS design](https://pos.sissa.it/350/061/pdf),
[CMS thermal study](https://arxiv.org/pdf/2301.10567),
[CMS system tests](https://doi.org/10.1088/1748-0221/21/02/C02027),
[ATLAS local supports](https://indico.cern.ch/event/829863/contributions/5059040/attachments/2567661/4427072/Carbon%20based%20local%20supports%20for%20the%20ATLAS%20ITk-pixel%20detector_fmunoz.pdf),
[ATLAS cooling preprint](https://cds.cern.ch/record/2901596/files/ATL-UPGRADE-PROC-2024-001.pdf),
[graphite workshop](https://www.mineralstech.com/docs/default-source/refractories-documents/pyrogenics/pyroid/high-performance-pyrolytic-graphite-composite-heat-spreaders.pdf?sfvrsn=50359b20_2),
[graphite product](https://www.mineralstech.com/minteq/minteq-product-catalog/pyroid-ht),
[PDG copper](https://pdg.lbl.gov/2025/AtomicNuclearProperties/HTML/copper_Cu.html).

## Inferences and inherited inputs

**EC-I01 — INFERENCE:** the SHA-pinned active layout has 18 discs ×112 quads
×4 chips =2016 modules and 8064 active chip patches. Five row counts are
12,16,24,28,32. Commonality is verified from x/y coordinates, orientations and
bounds, not guessed from a drawing. Current staggering occupies eight levels
spaced 1.2 mm, leaving 0.2 mm between 1 mm body envelopes.

**EC-I02 — INFERENCE:** at 2.688 W/chip (DES010 PX-SF03's historical power-density
proxy), each disc dissipates 1204.224 W, before the 1.5 stress multiplier. The
power includes the inherited sensor/services proxy; it is not just measured ASIC
power. EC-C09 flow quality follows x_out=x_in+Q/(mass-flow×latent-heat), with
313.18 J/g inherited from DES002's −35 °C NIST table. Its use at the proposed
−40 °C setpoint is a fixed-property screening choice, not a fresh
fluid-property calculation. Temperature-dependent enthalpy must be updated for
hydraulic design. No pressure drop or saturation-temperature uniformity is proven.

**EC-I03 — INFERENCE:** clearance, sheet-resistance, mass, equivalent X0 and beam
numbers in the generated report follow the equations and assumptions in
`tools/pixel_endcap_support/`. The numerical heat solver conserves unit power,
uses adiabatic plate edges and a finite isothermal contact, and retains a mesh
comparison. Its output is a pickup-temperature proxy; die/sensor coupling,
leakage feedback and detailed cold-plate thermal spreading remain unresolved.

Reused material densities, X0 comparators, CO2 liquid bound, gravity, modulus
sensitivity and module payload originate in DES002's parameter contract and
`tools/pixel_support/inputs.json`. The 28.3 W/(m K) foam comparator comes from
SRC-ATLAS-IBL-PRODUCTION-2018 Table10. The current screen uses graphite inserts
instead of relying on that foam value for the narrow heat path. CFRP 0.15 mm
skins, bonding allowances, densities and laminate moduli are nODD choices;
no literature source is said to specify this nODD disc.

The literature does **not** establish the proposed phi staggering, three-point
kinematic coupling dimensions, rail section, shell thickness, cable grouping,
boiling coefficient, 0.2 mm assembly gap or acceptable tracking loss. Those are
explicit project hypotheses requiring review and tests.
