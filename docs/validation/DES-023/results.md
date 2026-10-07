# DES-023 — actual long-strip endcap prototype results (2026-10-07)

DRAFT, isolated PROTOTYPE stacked on the separate DES-022 barrel PR52. Production
and historical DES008/011/020/021/022 artifacts are unchanged. Native execution
is dirty2c6567871ae0117b6a8a0a6484f0cebb0f2f5dee plus exact source/input/compact/
plugin hashes in the receipts. The later enclosing commit does not replace it.
DD4hep1.38, ROOT6.40.04, Geant411.4.2 were actually run on the existing installation.

## Placement and structural recommendation

Six discs per end; four rings with72/72/84/84 pairs,312/disc,26/petal,
12 petals/disc:3744 complete stereo pairs and7488 independent1D sensor faces.
Each96×96×0.3 mm face has1200 strips at80 µm pitch, with ±20 mrad physical axes.
The common5 mm carbon-foam core,0.1 mm glue and0.3 mm CFRP skins IS the petal
carrier; four full-height integral webs replace foam. Outward staggering gives
6.9/9.9/12.9/15.9 mm face separation. No duplicate carrier or hidden rail is added.

The inner key and two outer contacts transfer load through potted lands, shoes
and grounded rings. One outer contact fixes in-plane position, the other slides
tangentially; the inner key slides radially. The ±0.3 mm slot is an effective
assembly allowance, not machined CAD. Short-service outer radius783 mm is kept;
the inner ring begins783.5 mm. This0.5 mm clearance and narrow key need review.
Outer carrier1130 mm, bearing ring1140 mm and service outer1169 mm stay fixed.

Worst full petal mass1.4950 kg, span338.1 mm, E70 GPa/G5 MPa hypotheses:
0.25g axial screen gives14.40 µm bending +19.41 µm core shear +10 µm joints
=43.82 µm, below the50 µm fixture limit. A1g horizontal handling screen gives
145.26 µm and fails; even E140/G20 gives58.22 µm. Use a temporary handling
frame. The installed disc's in-plane gravity proxy is reported separately.
These beam screens assume full-width distributed rim reactions: three discrete
contacts, thin inner key, plate twisting, local indentation, rings, interfaces,
thermal bow and cold bond/PCB stresses require plate/joint/global-frame FEA.
A software pass is not a qualification of those joints or material moduli.

## Defined cooling, cable and common routing

Six U-loops per petal distribute12 Ti legs across the carrier, replacing the
retained three-loop control. OD2.5 mm, wall0.14 mm,10 mm centre-radius returns;
legs run local radial805–1105 mm. Nearest-leg assignment gives4/4/6/4/4/4 complete
pairs per circuit (both faces counted once), no group exceeds12. Four embedded
CFRP webs end at maximum r1114 mm; collection buses begin1115 mm, with explicit
contained/disjoint foam cutouts and insulated face buses. Hybrid support lands
are placed at sensor corners after rejected neighbouring-pickup collisions.

Three ≤12-pair LV/HV/fibre harnesses leave each outer board: groups12/12/2.
The inherited conductor-sized6 mm power cable has6.14 mm² Cu and5.24 mm²
insulation per unit length;3.6 mm data bundle contains48 coated fibres. Inherited
11 V/88.8 W/4.1 m fixture loop/return drops0.397/0.199 V pass;1.4× warm
resistivity fails the return limit. Dielectric, termination and leakage are not
qualified by these numbers. Curated DES022 remains the electrical comparator.

Core buses and outer EoS boards connect to a r1100–1169 mm fan, normal+20..130 mm,
with R50 cable/R25 pipe bend reservations. Cumulative services then pass through
r1144–1169 mm to |z|3500 mm. This standalone corridor includes the pinned barrel
loads PLUS every upstream disc. It REPLACES the standalone barrel-only corridor;
blindly overlaying both compacts would double-count services.

The final segment reference demand is3469.83 mm²/sector versus5449.88 mm² capacity
(75% phi/50% packing). Adverse reduced space plus25% spare fails:
4337.28 versus2906.60 mm². The13.4 mm gross power-cable comparator also fails.
These fixed envelopes were not enlarged. Individual elbows, connector heads,
assembly access, manifold balancing, pressure drop and two-phase stability remain
unqualified. Sensitive datums remain ≤3120 mm; the passive service handoff is
outside the active |z|3150 mm host by design.

Worst pair centre is30 mm from a pipe leg. At3.7 W/face, the normal foam slab
lower bound is1.05/0.52/0.26 K for k5/10/20 W/m/K. The deliberately pessimistic
single lateral path gives105.71/52.86/26.43 K and fails all sensor-temperature
fixtures. It omits beneficial parallel spreading, while the normal lower bound
omits lateral spreading/contact resistance. Neither certifies cooling. Recommend
an anisotropic thermal simulation and qualified graphite-to-pipe heat bridges or
closer pipes before baseline adoption; do not hide this unresolved thermal gate.
The200 kJ/kg enthalpy-derived flow is a proxy, not a hydraulic calculation.

## Actual native and transport checks

Nine positive/negative controls passed: pinned drift, fixed envelope/collector
rejection, proper stereo frames, local IDs, torus OD containment, web/collector
clearance, complete circuit assignment and overfill rejection.
Final CTest native construction returns0:7488 true1D sensors, unique face/strip
IDs, exact roles/positions/axes/constituent mass, zero overlaps at1e-5 mm,
210 ROOT navigation/material rays exercising all12 layers.
Fresh ROOT import preserves all7488 sensors and constituent inventories/axes.

Two actual zero-field DDSim10 GeV muons start at(1000,0,0) mm and travel±z,
seed42, FTFP_BERT. Each saved25 positive-energy sensitive hits; complete SAME
module pairs occur in all six target layers per signed end. This displaced gun
is a transport fixture, not an IP efficiency or physics-performance measurement.
No ACTS conversion or calibrated strip response was run. Separated stereo
measurements require transport to a common plane in reconstruction.

## Fixed old-reference coverage losses

The first datum moves1403.65→1470 mm (+66.35 mm) to clear the barrel collector
ending1435 mm. Other disc datums and the original annulus are fixed.116640 first-
traversal vacuum tracks use eta−4..4 step0.1,96 off-grid phi bins, luminous
z−150/0/+150 mm, B0/4 T, pT1/10 GeV and both signs.148 tracks including displaced
vertices agree with an independent finite-plane oracle; immutable historical
finite planes are compared on the identical subset. BOTH faces must belong to
the SAME pair. Software PASS leaves the hermeticity gate FAIL.

| B [T] | pT [GeV] | q | Missing intersections / fixed old ideal | Missing at new datum | Old-datum tracks losing every hit |
| --- | --- | --- | --- | --- | --- |
| 0 | 1 | + | 192 /10368 | 0 | 192 |
| 4 | 1 | + | 576 /12096 | 192 | 384 |
| 4 | 1 | − | 576 /12096 | 192 | 384 |
| 4 | 10 | + | 192 /10368 | 0 | 192 |
| 4 | 10 | − | 192 /10368 | 0 | 192 |

The same-layout old-datum control already misses192 intersections per1 GeV sign;
those are layout losses, distinct from the shifted-first-disc losses. The gate
is not made to pass by removing old crossings from the denominator. Scattering,
energy loss, continuum coverage, hit inefficiency and reconstruction remain absent.

## Failed attempts and retained controls

Initial electronics/web collisions:15408 overlaps. Full extended foil/platform:
16992; corner platform with wide tail:9072; narrow tail with low platform edge:
1584. Final corner land starts beyond neighbouring pickups and below the next
sensor elevation; integral webs stop before the collector bus. No tolerance was
weakened and no sensor transform was moved to make passive collisions disappear.
The six-loop geometry passed scientific checks but initially aborted on ROOT's
multithreaded teardown mutex. One overlap worker and explicit pool shutdown
restore a successful process exit; final native/root runs passed. Initial three-
loop native PASS is retained as a control, not substituted for the final model.
