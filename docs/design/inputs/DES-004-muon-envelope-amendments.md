# DES-004 — Candidate-specific muon envelope requests

- Date: 2026-09-17; status: DRAFT; approving humans: pending.
- Review: [PR #6](https://github.com/asalzburger/nodd/pull/6).
- Scope: user-authorized adaptation of research envelopes to magnetic candidates.
- Context: [candidate cards](../DES-004-magnetic-configurations.md),
  [muon measurement definitions](DES-004-muon.md),
  [reference E1-R2](../DES-003-global-envelopes.md).

## Decision and ownership

**NODD DESIGN CHOICE — proposed:** compare each magnet with a stated muon host
instead of rejecting it solely for exceeding the inherited ODD-sized allocation.
The System Architect and muon engineer reconciled the following requests with
coordinator input. They are comparative space budgets, not signed-off detector
geometry. Keep E1-R2 and the earlier fixed-host diagnostics intact as reference
artifacts. Open the eventual baseline-amendment issue only after a configuration
has been chosen, as directed by the user.

All numerical allocations below are **NODD DESIGN CHOICE**, with rationale and
uncertainties stated. Coordinates are metres; endcaps reflect through z=0. A
host includes space for stations, magnet structures and services: its entire
volume is neither sensitive gas nor iron. Internal suballocations are alternative
uses within that host, not overlapping independent detector mothers.

## Proposed research allocations

| Candidate | Barrel r min–max | Barrel maximum absolute z | Endcap r min–max | Endcap absolute z min–max |
| --- | --- | --- | --- | --- |
| MAG-01 | 4.350–6.762 | 7.200 | 0.400–7.000 | 7.200–10.270 |
| MAG-02 | 4.350–7.500 | 8.000 | 0.400–7.500 | 8.000–10.900 |
| MAG-03 | 4.950–7.500 | 8.000 | 0.400–7.500 | 8.000–10.900 |
| MAG-04 | 4.950–10.000 | 9.000 | 0.400–10.000 | 9.000–10.900 |
| MAG-05 | 4.350–9.000 | 9.000 | 0.400–9.000 | 9.000–10.900 |
| MAG-06, outer-main variant | 4.950–8.850 | 9.000 | 0.400–8.850 | 9.000–10.900 |

The inherited MAG-01 boundaries preserve the compact control. Rounded expansions
provide visible resource costs for alternatives; no optimum is asserted. All
expanded endcaps stop 0.300 m before the unchanged detached forward-calorimeter
front at |z|=11.200 m. That interval is an integration reservation, not established
installation or shielding clearance. Barrel/endcap host faces touching does not
mean actual solids may be coincident without reviewed tolerances.

## Candidate budgets and rationale

**MAG-01:** retain the reference space. Establish available fringe-field
information without silently adding a magnet or independent-momentum claim.

**MAG-02:** increase outer radius to 7.500 m and half-length to 8.000 m to permit
interleaved return/station alternatives and end-service studies. A diagnostic
barrel partition reserves measurement/service bands 4.350–4.850, 5.350–5.950,
and 6.450–7.050 m, magnetic-structure slots 4.850–5.350 and 5.950–6.450 m,
and outer support/routes 7.050–7.500 m. These are reservations, not prescribed
filled steel plates. Actual station placement and plate fraction remain open.

**MAG-03:** move the first permitted barrel host radius to 4.950 m, outside the
proposed outer assembly at 4.300–4.800 m. Expanding to 7.500 m restores room for
separated measurements rather than compressing them into the old outer radius.
Reserve three broad measurement/service bands 4.950–5.450, 5.750–6.250 and
6.550–7.050 m; the intervening/outer space remains for supports and routes.
The common 4.500 m diagnostic cylinder is still not a physical station in this
candidate. MAG-03 performance cannot borrow it after this amendment.

**MAG-04:** enlarge to 10.000 m for the outer coil's greater return-flux demand.
For a transparent capacity test, reserve magnetic-structure slots at
5.300–6.100, 6.700–7.500 and 8.100–9.300 m; their complementary gaps
4.950–5.300, 6.100–6.700, 7.500–8.100 and 9.300–9.700 m allow measurement,
local electronics and service studies. Reserve 9.700–10.000 m for outer support
and routes. No magnetic slot is automatically filled, and no plate thickness is
selected for absorption or punch-through improvement.

**INFERENCE — diagnostic flux arithmetic:** the prior flat-3-T bore fixture for
R=4.500 m has flux 190.85 Wb. Returning all of it at trial average flux density
1.5 T requires 127.23 m² cross-section; 2 T requires 95.43 m². These values are
not steel grades or saturation limits. The enlarged full annulus provides
237.18 m²; the three hypothetical magnetic slots provide 129.94 m². Thus the
radial budget can accommodate that illustrative area while leaving gaps. It
establishes neither field at stations nor physical flux closure. Real plate
packing, leakage, HCal return paths and endcap bottlenecks change the result.

**MAG-05:** enlarge to 9.000 m and half-length 9.000 m to study a distinct
standalone air-core layout. Reserve broad measurement regions 4.350–4.950,
6.100–6.700 and 7.850–8.450 m. The spaces between them and outer
8.450–9.000 m band allow coil/support/service proposals, but toroid legs and
cryostats must occupy explicit azimuthal sectors, with chamber coverage reviewed
around them. This r–z budget cannot be interpreted as homogeneous toroid shells
or a proven three-station acceptance. The barrel-to-endcap transition and its
shared support structure remain major constraints. This is the first air-core
standalone candidate alongside MAG-02, not a demonstrated performance preference.

**MAG-06:** define this request for the **outer-main-solenoid branch only**.
Reserve 4.950–8.100 m for return-field measurements and their supports/services,
8.100–8.600 m for an active return-coil assembly, and 8.600–8.850 m for outer
routes/supports. The return-field annulus has area 129.14 m²; the all-flux fixture
would average about 1.478 T there. This is a capacity comparison, not a computed
field or specified return current. Measurement locations must be chosen after
that field is known. An end-return assembly study may use the peripheral annulus
8.100–8.600 m at |z|=8.000–9.000 m inside the overall barrel host. It does not
close the magnetic circuit by declaration. Coil coupling, supports, end-turn
geometry and stray-field objectives remain unresolved; an inner-main variant
needs its own budget.

## Endcaps, forward aperture and remaining gates

**INFERENCE:** moving the endcaps outward eases the ray aperture for a fixed
inner radius, but does not prove chamber coverage or momentum measurement.
The shared 0.400 m aperture preserves the earlier η=3.5 investigation reservation;
beamline/shielding, inactive edges and displaced tracks still require studies.
Endcap allocations must jointly accommodate independent measurements, return or
toroid structures, and service exits. In particular, **MAG-04 and MAG-06 do not
yet have a demonstrated end-flux solution inside 9.000–10.900 m**. If a physical
solution needs more length, propose an explicit stepped endcap or relocation,
including the forward calorimeter, rather than concealing the conflict.

Keep tracker |η|<4, calorimetry |η|<5 and muon |η|<3/3.5 goals visible. Forward
calorimetry downstream of the muon hosts cannot provide upstream hadron filtering.
No extra absorber steel is authorized before leakage/punch-through evidence.
Station information, scattering, alignment and services must accompany any field
comparison; enlarged hosts alone establish none of them.

## Evidence and checks

Experimental precedent remains SRC-ATLAS-JINST-2008 §6.1/PDF194–195 and
SRC-CMS-YOKE-COSMICS-2010 §§1–2/PDF3–5, as located in the prior muon input and
[source catalogue](../../../reference/manifest.yaml). New dimensions are explicitly
project choices, not extracted experimental facts. Flux/area arithmetic was run
with Python standard-library `math`; no magnetic solve, engineering fit,
transport or performance study was performed for this memo. Parent-session
logging and dashboard updates record the contribution.
