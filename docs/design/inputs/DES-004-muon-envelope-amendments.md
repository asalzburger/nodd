# DES-004 — Candidate-specific muon envelope requests

**2026-09-22 scope update:** MAG-06 is withdrawn from active study following
[expert review](DES-004-magnet-expert-review.md). New main-solenoid studies use
finite homogeneous winding packs; the earlier sheet calculations and MAG-06
recommendations below are historical. Enclosure allowances remain unverified.

- Date: 2026-09-18; status: DRAFT; approving humans: pending.
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

| Candidate | Barrel r [m]; max absolute z [m] | Upstream endcap r [m]; absolute z [m] | Wide endcap r [m]; absolute z [m] |
| --- | --- | --- | --- |
| MAG-01 | 4.35–6.762; 7.2 | 0.4–4.2; 6.35–7.2 | 0.4–7; 7.2–10.27 |
| MAG-02 | 4.35–7.5; 8 | 0.4–4.2; 6.35–8 | 0.4–7.5; 8–10.9 |
| MAG-03 | 4.95–7.5; 8 | 0.4–4.8; 6.95–8 | 0.4–7.5; 8–10.9 |
| MAG-04 | 4.95–10; 9 | 0.4–4.8; 6.95–9 | 0.4–10; 9–10.9 |
| MAG-05 | 4.35–9; 9 | 0.4–4.2; 6.35–9 | 0.4–9; 9–10.9 |
| MAG-06 | 4.95–8.85; 9 | 0.4–4.8; 6.95–9 | 0.4–8.85; 9–10.9 |

MAG-01 keeps its prior outer bounds and adds the upstream endcap step. Rounded expansions
provide visible resource costs for alternatives; no optimum is asserted. All
expanded endcaps stop 0.300 m before the unchanged detached forward-calorimeter
front at |z|=11.200 m. That interval is an integration reservation, not established
installation or shielding clearance. Barrel/endcap host faces touching does not
mean actual solids may be coincident without reviewed tolerances.

## Candidate budgets and rationale

**MAG-01:** retain the reference outer bounds with the new upstream step. Establish available fringe-field
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

### Stepped-endcap revision — 2026-09-18

**NODD DESIGN CHOICE — unsigned:** following PR #6 comments
[4040667425](https://github.com/asalzburger/nodd/pull/6#discussion_r4040667425),
[4040694164](https://github.com/asalzburger/nodd/pull/6#discussion_r4040694164) and
[4040721189](https://github.com/asalzburger/nodd/pull/6#discussion_r4040721189),
and the user's explicit instruction, decouple the endcap front from barrel length.
Represent each endcap as the union of two non-overlapping radial/axial sections.
The narrower upstream section sits inside the barrel; the downstream section
widens to the previous outer radius. Their common face is a bookkeeping boundary
inside one composite host, not two coincident physical solids.

The proposed inner-solenoid front is |z|=6.35 m: HCal back 6.20 m plus a trial
0.15 m interface allowance. Its outer radius 4.20 m leaves 0.15 m to the barrel
inner radius 4.35 m. Outer-solenoid options start at |z|=6.95 m: coil-assembly
back 6.80 m plus the same trial allowance; r=4.80 m leaves 0.15 m to their
4.95 m barrel. These allowances are project choices, not validated routing,
shielding or installation clearances. The upstream face is now independent of
barrel length; the wide section currently starts at the barrel back because it
shares its radial range. Moving either requires checking actual intersections,
not enforcing equality. Outer radii, barrel lengths and endcap back faces stay
at the prior candidate values for this isolated comparison.

**INFERENCE:** the former HCal-to-endcap gaps of 1.0–2.8 m become 0.15 m for
inner-solenoid options. Outer-solenoid options retain 0.75 m from HCal back to
endcap front, determined here by the coil's axial extent plus 0.15 m; this is
not a claim that the coil fills the entire intervening bore. Shared services and
end structures still need explicit allocations. The new host is not automatically
available in full for both chambers and magnetic closure.

Keep the 0.40 m aperture. For a straight prompt eta=3.5 ray, r=6.35/sinh(3.5)
≈0.384 m at the inner-family front: it enters the radial host only at
|z|=0.4*sinh(3.5)≈6.617 m. Thus the earlier front does not guarantee a first
station at that eta. The outer-family front gives r≈0.420 m. Eta=3 rays enter
both families at their upstream face. These are allocation crossings, not hit
counts, detector efficiency or a validated beam-line/shielding aperture.

MAG-04/06 still have only 1.90 m of **full-radius** endcap space, but now also
have an upstream inner-radius extension. No end-flux solution has yet been shown
to fit their stepped union. More space alone does not resolve field topology,
material or measurement leverage. Earlier rectangular requests remain in Git at
`10a918e835eb2d74a16990980bdc68bcebb99e58`; E1-R2 is unchanged.

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
