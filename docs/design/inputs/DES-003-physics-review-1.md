# DES-003 — Physics review 1: field, timing and applicability

- Date: 2026-09-17; status: **DRAFT**, no human sign-off.
- Role: Physics and Performance Validation; scope: global setup only.
- Context: [DES-003](../DES-003-global-envelopes.md), [first physics input](DES-003-physics-input.md).
- Human-directed scope for this review: 14 TeV proton collisions, tracker |η|≈4,
  calorimetry |η|≈5, muons |η|≈3 with 3.5 as a stretch goal. These specify the
  investigation; they do not assert achieved performance.
- FACT locators below use one-based PDF pages; source IDs resolve in the
  [catalogue](../../../reference/manifest.yaml). NODD DESIGN CHOICE entries are
  proposals with approving humans pending.

## 1. What field can reasonably be proposed?

**Answer — INFERENCE:** retain **3 T central field as a credible NbTi study
hypothesis**, bracket it with 2 T and 4 T, but do not call 3 T demonstrated within
E1's 0.20 m total coil/cryostat allocation. Field strength is not determined by
shell dimensions alone. Winding current density, peak conductor field, operating
temperature/margin, mechanical reinforcement, vacuum walls, insulation, cooling,
quench protection and the return system must share that space.

**FACT — SRC-ATLAS-SOLENOID-2007**, abstract/Table I/PDF1: the commissioned ATLAS
central solenoid produced 2 T at 7730 A, with 39 MJ stored energy, 2.3 m warm-bore
diameter and 5.3 m length. Its 45 mm cold-mass thickness corresponds to 0.66 X0;
it uses aluminium-stabilized NbTi and shares its cryostat with the calorimeter.
That 45 mm is not an independent complete cryostat envelope.
[Commissioning paper](https://cds.cern.ch/record/1102026/files/04277684.pdf).

**FACT — SRC-CMS-JINST-2008**, §2.1/PDF33, Table2.1/PDF35: CMS's built NbTi
solenoid was designed/tested for 4 T, with 6 m free-bore diameter, 12.5 m length,
41.7 MA-turns, 2.6 GJ stored energy, 312 mm cold-mass thickness and 3.9 X0.
Its peak conductor field is 4.6 T. These different dimensions and material budgets
cannot be scaled by field alone. They do establish that 2–4 T does not inherently
require a higher-field conductor family. Nb3Sn/HTS would require a separate
technology/risk/material justification; it is not a shortcut to a thin cryostat.

### Quantitative screen, with explicit assumptions

**INFERENCE — Biot–Savart and magnetic-energy relations:** model a uniform thin
current sheet of radius R=1.34 m and length L=6.70 m, the midpoint and full length
of E1's reservation. These are diagnostic assumptions, not winding dimensions.
Ignore iron, penetrations, end reinforcement and winding optimization. At the centre,

`B0 = μ0 NI / (2 sqrt(R²+(L/2)²))`, with `μ0≈4π×10⁻⁷ H/m`.

Use `p_mag=B0²/(2μ0)` as a magnetic-pressure scale and
`U_proxy=p_mag π(1.24 m)²L` as the energy of an imagined uniform bore field.
This is **not total stored energy or a rigorous bound**: actual interior field
varies and exterior energy is omitted. A thin pressure-vessel scale is
`σ_hoop≈p_mag R/t_load`; use **illustrative** t_load=0.050 m, distinct from the
0.20 m total cryostat allocation. It is not a material allowable stress.

| Central B | Required NI in model | Magnetic pressure | Uniform-bore energy proxy | Hoop scale, 50 mm load-bearing thickness |
| --- | --- | --- | --- | --- |
| 2 T | 11.48 MA-turn | 1.59 MPa | 51.5 MJ | 42.7 MPa |
| 3 T | 17.23 MA-turn | 3.58 MPa | 115.9 MJ | 96.0 MPa |
| 4 T | 22.97 MA-turn | 6.37 MPa | 206.0 MJ | 170.6 MPa |

At fixed geometry, 3→4 T increases pressure/energy by 78%, while magnetic
leverage improves by 33%. Local/end stresses, fatigue, preload and quench loads
are absent. No comparison with a room-temperature material strength certifies
safe cryogenic design.

The same model has axial field proportional to

`f(z)=(z+L/2)/sqrt(R²+(z+L/2)²) − (z−L/2)/sqrt(R²+(z−L/2)²)`.

With B(0)=3 T, **B(2.40 m)=2.51 T and B(3.15 m)=1.82 T on axis**.
The tracker end is close to the coil end: a uniform 3 T tracker model hides a
large forward-field issue. This toy result is not a field-map prediction, but
is sufficient to require a finite-solenoid study including return iron and the
actual active surfaces before adopting uniform-field tracking estimates.

**NODD DESIGN CHOICE:** use 3 T at the origin in comparison plots, show the
finite-length variation separately, and keep conductor/cryostat decomposition
open. Prioritize coil length, end geometry and upstream ECal material together.
Do not use all 200 mm as load-bearing conductor or silently put the cryostat
outside the registered shell.

## 2. Timing: where, and why not simply the outermost silicon layer?

**Answer — INFERENCE:** timing needs its own sensor/readout/support concept.
An outer strip layer is well placed for track association, but ordinary spatial
readout does not acquire precision timing merely because it is outermost. A
separate outer barrel timing assembly plus forward disks is the most direct
well-precedented comparison. An integrated timing/tracking layer remains an
alternative requiring technology evidence and material/power tradeoffs.

**FACT — SRC-CMS-TDR-020**, §1.4.1/PDF21, §2.1/PDF29: the dated CMS MTD design
reserves r=1.148–1.188 m, a 40 mm radial envelope, for barrel timing to |η|=1.48.
Its sensitive technology is LYSO:Ce plus SiPM, **not a silicon tracking layer**.
PDF11 discusses beginning-of-life 30–40 ps, degradation to 50–60 ps and physics
benefit through |η|=3. PDF20/Table1.4 reports strongly increasing forward fluence.
Those resolutions are CMS design studies, not an nODD promise or present operating
measurement. Cooling/electronics and end-of-life response belong in the model.

**FACT — SRC-ATLAS-TDR-031**, abstract/PDF5, §2.2/PDF31–32: HGTD targets
2.4<|η|<4 with LGAD timing, about 30 ps per track initially and 50 ps at end of
life. Its vessel is 125 mm thick axially, including a 50 mm neutron moderator,
at z≈3.5 m. Active radii are 0.120–0.640 m, whereas the vessel spans
0.110–1.000 m; peripheral electronics explain part of that difference. Thus
thin sensors do not imply thin complete timing assemblies.

**INFERENCE:** E1's r=1.14–1.24 m shared interface can geometrically contain a
CMS-scale 40 mm timing allocation, leaving 60 mm gross for other interfaces;
it does not prove supports/services fit. A barrel at r≈1.18 m needs
|z|≈2.51 m for |η|=1.5, from z=r sinhη. To reach η=4 at z=3.30 m, forward
active coverage must approach r=0.121 m. A full 125 mm HGTD-like axial
reservation could lie geometrically between tracker end 3.15 m and ECal start
3.45 m, but competes with service exits and supports; its moderator role must
be revisited with the new calorimeter/shielding arrangement.

**NODD DESIGN CHOICE:** reserve distinct barrel and forward timing hypotheses
and compare a forward-only option. For 14 TeV high-pileup physics, timing from
barrel through the forward tracker is scientifically motivated by track-to-vertex
association and jet/lepton isolation. Full |η|<4 timing is a new combined nODD
ambition, not something demonstrated by either cited system. Require timing
association efficiency, low-pT reach, radiation ageing and vertex-time modelling;
do not transplant their resolution or physics improvements.

## 3. How small can the first tracker radius be?

**FACT — SRC-CMS-TDR-014**, §4.4/PDF85: the historical Phase-2 barrel pixel
proposal starts near r=29 mm. **FACT — SRC-ATLAS-IBL-OPERATION-2016**, abstract:
the IBL was installed in 2014 near r=33 mm and operated at the LHC, around a
new smaller beam pipe. [Operational account](https://arxiv.org/abs/1610.01994v3).
These anchor a **roughly 30–35 mm first-sensitive-layer comparison range**;
they do not establish an accelerator-independent minimum.

**INFERENCE:** E1/ODD's 25 mm tracker container boundary is not a justified
25 mm sensor radius. The inherited 24.4 mm outer pipe leaves only 0.6 mm to
that container, without module/support, alignment, motion or installation
allowance. Distinguish beam clear aperture, vacuum wall/coating/thermal layers,
mechanical clearance, nearest module surface and active measurement radius.
The beam envelope depends on optics, emittance, orbit/excursions and crossing
angle; pipe stability, vacuum impedance and bakeout are additional constraints.
An experiment-independent project must state a reference aperture model rather
than assume 14 TeV alone fixes it.

For fixed particle flux per solid angle, a crude local rate/fluence comparison
scales approximately as 1/r²: moving 33→25 mm increases this proxy by 74%.
This is not a radiation transport prediction; secondaries, angular distribution,
shielding and integrated luminosity matter. Smaller radius improves extrapolation
leverage but increases rate, dose, cooling and replacement demands.

**NODD DESIGN CHOICE:** screen first active radii around 30–35 mm while retaining
the inherited pipe as a labelled hypothesis. No “minimum achievable” radius is
accepted until pipe/support and lifetime assumptions are explicit.

## 4. Does later operation support the historical calorimeter scale?

**Answer:** yes as a starting architecture scale, **not as a universal containment
certificate**. **FACT — SRC-ATLAS-EGAM-RUN2-2024**, §2.1, §3.3, §8.2 and
conclusion: the Run-2 calibration paper uses 140 fb⁻¹ at 13 TeV, describes
upstream-material and shower-tail corrections and validates calibration with
independent resonances. It quotes energy-scale uncertainties, not complete shower
containment probabilities. [Primary paper](https://arxiv.org/html/2309.05471v2).
**FACT — SRC-CMS-HCAL-CALIBRATION-2020**, abstract: collision-data calibration at
13 TeV uses isolated charged hadrons and covers the forward calorimeter to
|η|=5.19. [Primary paper](https://arxiv.org/abs/1910.00079v2).

**INFERENCE:** these operational results support using built ATLAS/CMS depths
and forward coverage as anchors, but do not validate a new sampling mixture,
coil material or service crack. Retain the earlier 24–30 X0 and 9–11 λI bands
as screening ranges with separate instrumented/dead-material accounting.
At fixed transverse energy, E=ET coshη; a 100 GeV transverse-energy deposit at
η=5 corresponds to about 7.42 TeV, beyond the approximate single-particle energy
available from one 7 TeV beam in a simple massless two-body collision. Forward
tests must respect event kinematics rather than copying central energy grids.
Use physically populated forward energy spectra and explicit leakage-tail
criteria; 14 TeV collision energy is not a 14 TeV single-hadron requirement.

## Verification and immediate consequences

Python arithmetic verified the field/pressure/energy/hoop and η examples. Local
TDR/overview passages and primary public papers were inspected. No engineering
finite-element model, field solver, radiation simulation or shower simulation was
run. Parent session records the contribution and adds source metadata.

The next envelope revision should expose finite-length field uncertainty, named
barrel/forward timing reservations, a first-sensitive-radius hypothesis separate
from its container, and dedicated forward calorimetry for |η|≈5. Muon coverage
and field alternatives are addressed by the muon review. All numerical design
recommendations above remain unsigned.
