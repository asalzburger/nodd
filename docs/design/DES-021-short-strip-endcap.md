# DES-021 — Detailed short-strip endcap petals

- Status: DRAFT
- Created: 2026-10-06
- Scope: isolated PROTOTYPE; engineering reviewers and sign-off pending.

The user requested a separate design/implementation PR at the same detail as the
short-strip barrel. This authorizes exploration, not sign-off or production
integration. The governing module contract is [DES-007](DES-007-short-strip-modules.md),
the architecture control [DES-011](DES-011-service-constrained-tracker-optimization.md),
and the selected barrel [DES-020](DES-020-short-strip-barrel.md). Approving humans:
none recorded. This prototype is stacked on PR50; no production compact uses it.

## Public evidence and interpretation

| ID | Classification | Evidence / consequence |
| --- | --- | --- |
| SE-F01 | FACT | SRC-ATLAS-STRIP-PETAL-2026, section1: radial carbon-fibre petals, copper/polyimide bus tapes, embedded titanium cooling tubes in conductive foam, CO2 cooling and outer EoS interfaces. These support the topology, not nODD dimensions or module compatibility. |
| SE-F02 | FACT | Same source section1.1: cold sensor cracking and PCB/sensor CTE mismatch; adhesive and loading pattern matter. A cold thermal screen does not qualify mechanical stress. |
| SE-F03 | FACT | DES-010 strip-services dossier SS-F01..12 retains precise historical TDR support, routing and comparator-power locators. Historical TDR and 2026 petal module counts differ by version; neither defines this strixel arrangement. |
| SE-I01 | INFERENCE | The old first disc at1295.5mm intersects the barrel collector ending1310mm. New disc datum must exceed1310+10 clearance+13.5 upstream frame depth=1333.5mm. Round to1335mm: actual minimum gap11.5mm. |
| SE-I02 | INFERENCE | Rectangular modules need axial staggering in both ring and phi because projected overlap is required at their corners. Fine tangential / coarse radial axes preserve the intended cylindrical-coordinate measurement. |

## Central choices (every numerical group below is a NODD DESIGN CHOICE)

| ID | Parameters and rationale | Alternatives / consequences |
| --- | --- | --- |
| SE-C01 | Six discs per end, at1335,1534.173414846085,1863.1642461939208,2237.8356365846863,2645.6407210129336,3080mm. Nominal active annulus243.5..670.0571931578914mm, inherited selected DES011 artifact. Only first datum shifts39.5mm outward. | Retain old schedule as coverage control. This is an unsigned amendment; no claim of improved acceptance. |
| SE-C02 | Twelve removable30degree petals/disc. Five radial rings centred289.5..624.0571931578914mm, evenly spaced83.63929828947285mm. Radial active margin2mm, tangential reserve3mm; counts rounded to multiples12 for equal groups/petal:48/60/72/84/96. | 360modules/disc,30/petal. Large projected silicon redundancy is retained rather than hiding gaps. Wedge sensors would reduce overlap but break the shared rectangular module contract. |
| SE-C03 | Sensor48x96x0.2mm,0.5mm guards,0.075x0.5mm cells; eight23.4x23.4x0.15mm ASIC fixtures and all module backing/glue/flex layers exactly DES020. FineU tangential, coarseV inward radial, N outward from IP. Four elevations0/1.5/3/4.5mm. Negative end uses a proper180degree rotation about x, never an improper reflection. | This is a strixel fixture, not an available qualified ASIC/sensor. No stereo angle is added to a two-coordinate cell. IDs are system4/layer4bits/petal4/ring3/module4/sensor1/x signed11/y signed10. |
| SE-C04 | Annular petal236..685mm,0.6mm inter-petal gap at236mm. Stack: CFRP0.15mm skins,0.1mm glue each,5mm carbon foam. Same densities/compositions as DES020; CO2 density1g/cm3 is a transport proxy. Narrow two6x60mm graphite pickups atU+/-5mm reach raised modules. | Smaller pickup area720mm2 increases thermal resistance. No unverified thermal benefit is claimed. |
| SE-C05 | One serpentine loop/petal; ten circular legs at ring radius+/-20mm, nominal endpoints6/24degrees, alternating semicircular radial U turns. Feed at29degrees and return28degrees end at678mm; tangential entry fillets10mm radius. TubeOD2.5mm,wall0.14mm,centre w=-4.05mm. Core subtracts full envelopes. | The entry bend is a native geometry fixture requiring tube forming review; external25/50mm bending is screened separately. No hydraulic/dry-out qualification. |
| SE-C06 | Inner236..250mm and outer674..700mm CFRP frames,3mm thick centred w=-12mm. Three8x6x3.7mm lugs/petal meet back skin and frames (inner10degrees; outer10/26degrees). Outer end board52x20x8mm at r695mm. | Proposed fixed inner datum and two outer constrained/sliding seats accommodate radial contraction. Fastener preload, adhesive shear, FEA and removal sequence remain unqualified. All local corners stay inside710mm trunk. |
| SE-C07 | Back LV carrier26mm wide, two12x0.2mm Cu rails with0.15mm PI; signal/HV/control8x0.1mm flex at22degrees. Separate30module network/petal, three <=12module harnesses. Front fanout represented by constituent-conserving effective sector cells at w9..9.5mm, above modules and board, with lengths from each module edge to outer interface. | Individual module flex ledges are explicit. The effective fanout conserves flex material and approximate routing length, but omits individual connectors, vias and vertical transitions; no continuous cable installation claim. Front/back routing and connector penetrations require detailed review. |
| SE-C08 | Outer fan/turn collection685..710mm at disc+15..85mm; downstream fixed trunk710..783mm to3500mm. phi allocation0.75, packing0.50,0.5mm tray walls. Endcap transport cells carry cumulative endcap-only constituents; capacity ledger adds actual barrel demand without allocating the corridor twice. | Endcap standalone material is not an integrated barrel/endcap compact. Combined native service replacement needs a subsequent integration PR. Fixed envelopes never expand to make a screen pass. |
| SE-C09 | Inherit comparator7.8W/module+2W leakage and channel-scaled proxy;12V,Copper resistivity0.0175ohm mm2/m,5W/board,-35/-25C coolant, sensor goal-20C,flows3/7g/s,latent200J/g,quality0.35. kEpoxy1/PI0.12/CFRP0.5/foam20/graphite pickup100 and spreading400W/m/K;contactR0.25K/W. | Screening hypotheses only, no worst-case bounds. Electrical gates<1V round trip/<0.2V return. Enthalpy omits pressure loss. Thermal spreading and CTE remain expert gates. |
| SE-C10 | Coverage: fixed nominal annuli, first outward traversal, axial fields0/4T,charges+/-1,pT1/10GeV,z0=-150/0/+150mm,eta-4..4 and uniform phi samples. Compare old/new datums and active patches, count disc hits once even in overlaps; finite-plane oracle cross-check. Native overlap tolerance1e-5mm; mass1e-6relative, axes1e-9, cell centre1e-9native units; seeded10GeV muon DDSim smoke. | Finite vacuum sample has no scattering/energy loss/dead channels. Strip endcap alone does not provide all-|eta|<4 coverage; preserve missing ideal intersections and transition losses. |

## Routing and assembly recommendation

Assemble and test each cold petal before mounting. The front face carries the
sensor/ASIC stacks on isolated graphite pickups; the sandwich embeds a single
serpentine tube. Run distributed LV and HV/control independently to the outer
board; fibre and power harnesses join the outer fan, then longitudinal trunks.
Cooling supply follows the petal perimeter to the inner leg, traverses all rings,
and returns at the outer edge to the manifold. A single failed loop disables a
petal, so bypass/segmentation and pressure-drop review precede a working baseline.

Locate petals on three seats, with one reference and sliding/compliant outer
constraints. Mount the frames to the endcap cage; cage and fastener material are
outside this local prototype. Avoid bonding rigid service boards across sensor
edges; qualify the actual adhesive/interposer under cold cycles. Retain separate
installation space for connectors and bends. Resolve combined service capacity,
thermal contact and mechanical risks before full-detector integration.

## Validation and unresolved gates

Implementation will generate deterministic placements, material/route ledgers,
engineering screens and drawings from a single pinned input. Native audits must
check all sensitive/passive placements, signed axes, IDs, masses, overlaps,
material navigation, ROOT persistence and Geant4 saved hits. Coverage and
engineering failures remain visible independently of software pass/fail. Results:
[DES021 report](../validation/DES-021/results.md). DRAFT remains after a successful
build or a PR merge; no human sign-off has been entered.

### Construction-driven amendment before publication

The first456module candidate used8mm reserve and rounding to24. Native checks
found45,504 overlaps, predominantly pickups through lower module stacks.
[Rejected evidence](../validation/DES-021/rejected-456.json) retains the exact
input/native hashes and failure. The revised3mm reserve /12-count rounding is
a mechanical-clearance choice, not performance tuning. The resulting
48/60/72/84/96 rings have4/5/6/7/8 modules/petal. Global azimuth-index parity
sets the1.5mm elevation, including odd-sized groups at petal boundaries.
The0/3mm ring alternation remains. Both coverage and support clearance must
be rechecked; the reduced redundancy is never assumed to prove hermeticity.

The revised count-only run retained3,888 overlaps:3,168 pickup/flex interactions
at adjacent rings and720 caused by an incorrectly composed radial-tube rotation.
The cooling centreline itself passed independent containment/separation controls.
Native tube-axis inspection identified the rotation error; explicit Rz*Ry*Rx
composition replaces the Euler constructor and native pipe-axis comparisons
are now required. Pickups shorten64→60mm to clear the rotated radial flex
ledges. Thermal area720mm2 and spreading length60mm are updated together;
the failed64mm attempt remains logged. No tolerance is changed.

### Screening scope additions

SE-C11 (NODD DESIGN CHOICE): normal-to-petal1g distributed-load screen using
the minimum inner-petal width, two0.15mm CFRP skins separated by the5.2mm
core/glue stack, a simply supported435mm radial span, E=70/100/140GPa and
0.05mm displacement goal inherited from DES020. This is a conservative beam
fixture, not the installed gravity direction or a shell FEA; frame joints,
in-plane stiffness and service loading remain unqualified. Native local-petal
mass supplies the load; remote fan/trunk material is excluded from this fixture.

SE-C12 (NODD DESIGN CHOICE): bandwidth sensitivity carries the DES020
1/40MHz accepted-event rates, occupancy1e-5/1e-4/1e-3,32bits/hit,20percent
packet margin and8.96Gbps usable link comparator to30modules/petal. Fibres per
harness stay unqualified. The thermal series includes module plus front-skin
CFRP0.35mm and module plus front-core adhesive0.3mm, PI0.025mm and the5mm
foam path; a20mm in-plane spreading screen precedes the coolant. Conductivities
are hypotheses. ASIC/sensor internal heat sharing and tube/contact spreading
require FEA; failed screen values are not nominal operating temperatures.

### Outer interfaces and bend reservation

SE-C13 (NODD DESIGN CHOICE): two4x8x10.5mm CFRP board columns at tangential
+/-15mm,r695mm meet the outer frame at w=-10.5mm and board back at w=0.
They stay below the board and outside all module envelopes; bolts/clamps and
board thermal straps remain effective/omitted. Local cooling entry fillets
increase3→10mm (four tube diameters) before final validation. This avoids the
initial severe1.2-diameter forming fixture; the10mm bend still needs forming
and hydraulic qualification. Independent containment/separation and native
construction must pass again. External power bends require both axial and
radial space: the25mm radial outer fan fails the25/50mm bend scenarios even
though its70mm axial height fits. Do not call those routes installation-ready.
A reviewed entry through the existing trunk allocation is a follow-up option,
not additional space silently allocated by this prototype.

Negative-end petal p joins global trunk sector11-p under the proper x-axis
half-turn; positive-end petal p joins sector p. The route ledger records this
crosswalk and3D waypoints as well as r-z waypoints. Uniform30module petal
traffic gives identical combined worst-sector demand on both ends.
