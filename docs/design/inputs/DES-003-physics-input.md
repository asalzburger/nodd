# DES-003 input — Physics and Performance Validation

> First-round input retained for traceability. The [2026-09-17 review update](DES-003-physics-review-1.md) supersedes conflicting recommendations.

- Date: 2026-09-16
- Status: DRAFT; independent architecture critique, no human approval
- Scope: global envelopes, field/material interfaces and screening tests only
- Context: [PROJECT](../../../PROJECT.md), [tracker](DES-003-tracker-envelope-input.md), [calorimeter](DES-003-calorimeter-envelope-input.md), [muons](DES-003-muon-envelope-input.md); ADR-001/003 remain DRAFT.
- Source IDs: [manifest](../../../reference/manifest.yaml). PDF pages are one-based.

## Assessment

**INFERENCE:** the inherited ODD scale is a useful reference, but neither that
scale nor the existence of ColliderML performance studies justifies every nODD
coverage, material or field choice. The three subsystem requests are reasonable
architecture hypotheses. They are not yet one physically closed design: larger
calorimeters, an external coil and the inherited muon inner boundary conflict.
A drawing must expose these alternatives rather than imply they all fit.

**NODD DESIGN CHOICE — proposed, approving humans pending:** compare an
ODD-like inner-solenoid option with an expanded-calorimeter/external-solenoid
option. Keep tracker scale initially; negotiate muon/yoke space jointly with
coil position. Freeze neither option before reporting material and coverage
consequences. An external coil exchanges pre-ECal material for larger magnet,
support and return-field demands; it is not an automatic realism improvement.

## 1. Tracking: coverage and magnetic leverage

**FACT — SRC-ATLAS-TDR-030**, §2.1, PDF25–26: the historical ITk proposal extends
pixel tracking to |η|<4, with strip coverage to |η|<2.7. **FACT —
SRC-CMS-TDR-014**, §3.1, PDF25: its outer tracker provides at least six module
layers to |η|<2.4 for a specified luminous region, except a transition near
|η|≈1 averaging five. These establish credible precedents, not universal nODD
hit requirements; trigger architecture and measurement independence differ.

**INFERENCE — geometry:** for a prompt straight ray, `r = |z|/sinh(|η|)`.
At η=4 the radius is 0.088 m at z=2.400 m and 0.115 m at z=3.150 m.
Thus an ODD-sized box can intersect a forward trajectory without giving it
many separated measurements or a large transverse lever arm. Forward precision
cannot be inferred from the outer barrel radius. Use `z-z_vertex` for displaced
longitudinal origins; curved low-momentum tracks need transport.

**INFERENCE — Lorentz-force/circle geometry:** for unit charge in uniform axial
field, transverse curvature radius is `ρ[m] = pT[GeV/c]/(0.299792458 B[T])`.
For a short transverse chord L, the sagitta is `s ≈ L²/(8ρ)`. Consequently the
measurement-limited momentum uncertainty scales approximately as
`σ(pT)/pT ∝ pT σs/(B L²)`, holding measurement layout and errors fixed.
An **illustrative calculation, not a requirement**, using B=3 T, L=1 m and
pT=100 GeV/c gives s=1.12 mm; halving L reduces it by four. Alignment,
multiple scattering, hit count, orientation and field gradients are absent.
This is not a resolution prediction. B alone is not a performance target.

**NODD DESIGN CHOICE — proposed, approving humans pending:** retain |η|≈4 as a
forward-tracking investigation goal, while specifying central and forward
performance separately. Demand crossing multiplicity and transverse-leverage
maps before accepting layer-envelope choices; do not count paired strip sensors
as fully independent modules without a measurement definition.

## 2. Calorimetry: depth is composition and direction

**FACT — SRC-ATLAS-JINST-2008**, §1.3, printed8/PDF38: its historical design
has >22 X0 barrel ECal, approximately 9.7 nuclear interaction lengths of barrel
calorimetry, and 11 including outer support. **FACT — SRC-CMS-JINST-2008**,
§5.1, printed123/PDF150: central HB absorber is 5.82 interaction lengths,
preceding ECal adds about 1.1, and the full arrangement includes an outer
calorimeter. Accounting boundaries differ; HB alone is not a full-depth benchmark.

**INFERENCE:** the calorimeter technician's 24–30 X0 ECal and 9–11 interaction
length combined-calorimeter screening bands are defensible comparison ranges,
not demonstrated containment requirements. Report instrumented material,
upstream dead material and downstream shielding separately. Choose particle
energies, leakage fractions and tail quantiles before selecting acceptance limits.

**FACT — SRC-PDG-TUNGSTEN-2025**, table rows radiation length/nuclear interaction
length/critical energy: pure W has X0=0.3504 cm, λI=9.946 cm and electron critical
energy 7.97 MeV. **FACT — SRC-PDG-IRON-2025**, corresponding rows: pure Fe has
X0=1.757 cm and λI=16.77 cm. These are elemental properties, not verified
properties of ODD tungsten alloy, steel or PCB mixtures. [W table](https://pdg.lbl.gov/2025/AtomicNuclearProperties/HTML/tungsten_W.html), [Fe table](https://pdg.lbl.gov/2025/AtomicNuclearProperties/HTML/iron_Fe.html).

**INFERENCE — screening arithmetic:** ODD's 91.2 mm absorber would give about
26.0 X0 **if pure tungsten**; its 36×30 mm HCal plates give about 6.44 λI
**if pure iron**. Neither is the full stack depth. The thick, dense PCB mixture
makes material composition a first-order uncertainty; removing it requires
physical accounting, not simply relabelling the freed space as services.

**FACT — SRC-PDG-PASSAGE-2025**, §34.5, Eq.(34.36), PDF28: the approximate
EM shower maximum is `tmax = ln(E/Ec)+C`, in radiation lengths, with C=−0.5
for electrons and +0.5 for photons. **INFERENCE:** a 100 GeV electron in
pure tungsten peaks around 8.94 X0. This is the maximum, not containment;
fluctuating tails, sampling structure and cracks require simulation. Do not
use this expression to claim hadronic containment.
[PDG review](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-passage-particles-matter.pdf).

**INFERENCE:** the proposed endcap ECal entrance z=3.40 m, rmin=0.30 m reaches
η≈3.12 geometrically. That does not support calorimeter performance to η=4.
For forward-jet and missing-transverse-momentum studies, either reserve dedicated
forward calorimetry or explicitly bound applicability. A shallow grazing
intersection is not adequate depth or hermeticity.

## 3. Muons and field topology

**FACT — SRC-CMS-TDR-016**, §1.5.3, PDF39: the proposed ME0 station behind
HGCAL extends muon coverage to |η|=2.8. **FACT — SRC-ATLAS-TDR-026**,
§1.4.4, printed11/PDF31: the proposed 2.7<|η|<4 tagger relies on ITk momentum
in a region without significant magnetic field; its approval was deferred.
Neither precedent grants nODD a forward standalone spectrometer.

**INFERENCE:** muon identification, tracker-matched momentum measurement and
standalone momentum measurement are different architecture requirements.
Station spacing alone is insufficient: field orientation/integral, return
material, scattering and alignment govern bending information. ODD's nominal
outer field cannot substitute for a physical return-field model. Adding yoke
steel changes both flux return and particle penetration; count it once.

## 4. Review of the architect’s inner-coil candidate

**NODD DESIGN CHOICE — proposed by the System Architect, approving humans
pending:** expand coil/cryostat allocation to r=1.24–1.44 m, ECal to
r=1.50–1.86 m, HCal to r=1.96–4.00 m, and move the muon barrel start to
r=4.15 m. The 0.20 m magnet allocation and 0.06 m pre-ECal separation
reserve space; they do not establish a credible cryostat/support bill of materials.

**INFERENCE:** candidate endcap entrances at (z,rmin)=(3.45,0.315) m and
(3.96,0.355) m correspond to |η|≈3.09 and 3.11 respectively. The inherited
muon parent entrance (7.20,0.54073) m reaches approximately 3.28, not 4;
station/chamber coverage may be narrower. Keep the different subsystem goals
visible. Barrel tails can intercept rays missing an endcap entrance, but may
supply inadequate material depth. Coil end, calorimeter transition and service
exits require directional material scans before the candidate can be preferred
on physics grounds. Moving the muon inner boundary also changes station spacing;
the old station arrangement cannot be assumed to survive that move.

## 5. Minimum evidence and decisions for this round

**NODD DESIGN CHOICE — proposed, approving humans pending:** produce diagnostic
maps without premature pass/fail thresholds:

1. Ray intersections, minimum path lengths and uncovered directions versus η,
   vertex and, once sectors exist, φ; distinguish allocation from active coverage.
2. Tracker layer/station multiplicity and lever arm; later helical transport with
   an identical field identity in simulation and reconstruction.
3. Line-integrated X/X0 and λI with composition scenarios and ownership of all
   supports/services; do not treat every envelope as uniformly solid.
4. For calorimeters, flag transition corridors and low-depth directions before
   shower studies. Subsequently scan species/energy/angle and report leakage tails.
5. For muons, report required station combinations and upstream absorber separately
   from identification efficiency or momentum resolution.

Human decisions needed: energy/use-case range; coverage by observable; forward
calorimeter need; inner versus outer coil; standalone muon requirement; timing
allocation; luminous-region and displaced-particle scope; service routes; accepted
material uncertainty. No numerical performance target is accepted in this pass.

Verification: read local TDR/overview passages, inspected subsystem evidence,
checked PDG primary sources and evaluated analytic examples with Python. No
DD4hep construction, Geant4 transport, field solution or performance validation
was run. Parent session records this contribution and catalogue changes.
