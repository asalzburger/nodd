# DES-017 — Eight chip-row pixel discs: single and mixed module supports

- Status: DRAFT — isolated PROTOTYPE; human engineering approval pending.
- Created: 2026-10-05.
- Human request: retain the eight-ring option and replace its outer four single
  rings by two quad-module rings; propose local support, cooling and mounting for both.
- Parent: [DES-016 service-radius revision](../validation/DES-016/service-radius/results.md),
  [DES-014](DES-014-pixel-endcap-support.md), issue [38](https://github.com/asalzburger/nodd/issues/38).
- Scope: a new comparison and passive-support proposal. Existing inputs, evidence,
  production detector, PR40 positioning and formal design lifecycles stay unchanged.

## Contract recorded before implementation

| ID | Classification | Requirement and rationale |
| --- | --- | --- |
| SV-C01 | NODD DESIGN CHOICE | “4 + 4” means four single-module rings plus two quad-module rings: six physical rings and eight radial chip rows. Preserve the first four nominal single-ring radii, populations, phases and radial/tangential axes. Keep the original eight-ring artifact as a frozen control. |
| SV-C02 | NODD DESIGN CHOICE | Retain the original active annulus r32.3..181.4550267061104 mm, luminous z±150 mm, conditional 0.1 mm guard, explicit 0.2 mm inactive inter-chip seams and 20% maximum silicon overlap (15% preferred). Count one shared sensor outline per quad. No change of target to conceal edge losses. |
| SV-C03 | NODD DESIGN CHOICE | The common plate ends at r188.5, service boundary at190, effective trunk at192..231.7 and flange neck at222 mm. No radius expansion. Scan two quad radii/populations within those bounds, retaining failed candidates and reporting coverage loss. Scan values are bounded exploration choices, not manufactured dimensions. |
| SV-C04 | NODD DESIGN CHOICE | Screen outward-face mounting first: preserve the existing disc datums and nominal ring pattern; increase axial level spacing from1.20 to1.65 mm to include1.00 mm body,0.45 mm pickup and0.20 mm nominal gap. Recompute the existing luminous-vertex xy compensation explicitly; do not describe these new transforms as the unchanged PR41 layout. Require clearance to the inherited collector starting at local z11.7 mm. |
| SV-C05 | NODD DESIGN CHOICE | Common6.3 mm sandwich (0.15 mm CFRP skins,6 mm foam), Ti CO2 tubing OD2.8/wall0.15 mm in routing planes±1.5 mm, and inherited three tongues/box rails/closed carrier. These DES014 dimensions are proposals, not qualified parts. Full annulus installs axially; no independent half-disc extraction is claimed. |
| SV-C06 | NODD DESIGN CHOICE | Each chip gets a centred6×8 mm axial graphite stem beneath a broad0.30 mm pickup sheet. Single: one stem; quad: four stems at the chip centres. The remaining0.15 mm pickup comprises0.075 cradle and three0.025 layers (insulator,TIM,bond). Cradle/skin thermal windows bypass poor transverse CFRP conduction. Check stems against every lower module/pickup; a bound within the host body alone is insufficient. |
| SV-C07 | NODD DESIGN CHOICE | Eight radial evaporator tracks in both variants. Split each into two independently served halves:16 circuits,32 feed/return legs. Quad chip rows share a physical mounting assembly but each has its own cooling track. Flows rounded upward to0.1 g/s with1 g/s floor follow stress power, inlet quality0.10 and ceiling0.45. Properties remain the inherited conditional DES002 proxy; this is not a hydraulic solution. |
| SV-C08 | NODD DESIGN CHOICE | Thermal screen uses the inherited2.688 W/chip,1.5× stress, coolant−40°C (−35 sensitivity), sensor−15°C screen, graphite k in-plane1500/1000/500 and normal7 W/(m K), stem axial500, h10/20/30 kW/(m² K), finite-volume grids0.5/1 mm. Test edge-concentrated and uniform heat. Preserve failures; no irradiated leakage feedback or boiling qualification. |
| SV-C09 | NODD DESIGN CHOICE | Use a fixed datum and a sliding second location with spring preload per module; four quad thermal stems are compliant thermal contacts, not four rigid alignment datums. Retain three-point cone/slot/plane disc coupling to rails bonded to the closed carrier. Quantify material/load proxies and local clearances; clamp preload, CTE accommodation, modal response and swept service routes require engineering review. |
| SV-C10 | NODD DESIGN CHOICE | Recompute chains, links, both pipe legs and fixed trunk/neck capacity from actual module/chip counts. Fewer physical modules do not imply less silicon power or a halved cooling system. Keep inherited bandwidth uncertainties and packing failures visible. |

All new choices have **human approver: pending**. The executable parameter register
is [inputs.json](../../tools/pixel_disc_support_variants/inputs.json). Inherited
material constants and service hypotheses retain their classifications and source
locators in [DES014 public dossier](inputs/DES-014-literature.md),
[DES002](DES-002-pixel-barrel-support-cooling.md) and
[service inputs](../../tools/module_layout/services_budget_inputs.json).

## Public basis and limits

**FACT, SRC-CMS-TEPX-THERMAL-2023**, §2.2 PDF3 and Fig5: carbon faces/foam,
embedded CO2 pipes, conductive bonds and thermal paste form a working endcap
support concept; §3 PDF4 reports titanium as a mass-saving option in its model.
**FACT, SRC-CMS-TEPX-DESIGN-2019**, §3 PDF3, §4 PDF4 and Fig2 PDF5: carbon disc
supports and longitudinal supply/support structures motivate the load path.
The public papers were re-read on2026-10-05; the existing source catalogue entries
remain authoritative. No experiment's thermal result qualifies this smaller disc.

**INFERENCE:** modular thermal pickups directly above each chip-row cooling track
reduce heat spreading distance and avoid concentrating four-chip power in one foot.
The mixed option exchanges many small mounting operations for fewer, larger
assemblies with more demanding tolerance, seam and thermal-contact control.
Executable screens and dimensioned proposal drawings will quantify these tradeoffs.

## Results and recommendation

**Design amendment SV-C11, NODD DESIGN CHOICE, recorded before the revised run:**
the initial centred stems collide with18 lower-body neighbours in the eight-single
nearest disc, and70 in a nominal123/160 mm,23/29-quad control. Preserve these
failures. Shift single contacts4 mm radially outward and quad contacts5 mm
tangentially toward the module centre, still within their own chip pickup.
Recompute thermal spreading and cooling-track radii from these contacts; central
contact thermal estimates cannot qualify the shifted version. Approver pending.

**Design amendment SV-C12, NODD DESIGN CHOICE, recorded before modelling:**
the global offset trial also interferes with neighbouring radial rings, so it is
rejected rather than used. Use both sandwich faces: alternate columns between
front/back, then colour the padded body-conflict graph separately on each face.
Centred per-chip stems are reinstated. Sensor centres are at signed
±(4.1+level×1.65) mm; compensate xy with that signed offset using the existing
luminous-vertex formula. This changes only new prototype transforms. Preserve
all source disc datums, including615.2 mm on the first plate, and test the actual
barrel-turn end at605 mm. Reassess original-annulus coverage, collector clearance
and all18 stations. The outward-face control is retained with its failed stems.
Approver pending; front/back flex artwork and clamp envelopes remain to be qualified.

**SV-C13, NODD DESIGN CHOICE:** the124/161 mm,22/28 two-face control leaves six
outer-quad inner-chip stems too close to lower inner-quad bodies (0..0.181 mm).
Shift each quad chip contact1 mm radially toward the quad centre. Keep single
contacts centred; retain6×8 mm contacts and the0.45 mm stack. Compute the two
quad cooling-track radii from the resulting contacts (nominal offsets±8.7 mm,
not±9.7 mm). The thermal screen includes this1 mm source/contact displacement.
No sensitive centre or active seam is moved by this amendment. Approver pending.

**SV-C14, NODD DESIGN CHOICE:** one round in-plane datum and one radial slot in
the module cradle constrain x/y/yaw; three cradle seats constrain the plane.
Retaining springs apply2 N/chip (2 N single,8 N quad), shared through the thermal
pads rather than four rigid alignment fixings. The4 quad pads must accommodate
flatness via TIM and compliant cradle webs; their load sharing is a coupon/FEA
requirement. A±0.10 mm slot travel is proposed. A deliberately adverse20 µm/(m K)
differential CTE control over60 K and43.2 mm gives51.84 µm motion; this supports
the nominal travel but does not qualify laminate CTE, friction or tolerances.
The [mounting inputs](../../tools/pixel_disc_support_variants/mounting-inputs.json)
record these hypotheses separately from the tested occupied-body/stem geometry.
Clips, spring travel, locator heads and flex swept volumes are **unqualified**.

**SV-C15, NODD DESIGN CHOICE:** azimuthal evaporators are in the+1.5 mm routing
plane, radial fan-outs in−1.5 mm, joined by end-of-arc risers. Front-face contacts
have the longest reach; use that far-plane reach for both faces in the conservative
thermal/insert-mass estimate. Nominal plane separation addresses crossings, but
port allocation, bends, riser unions and weld access still need swept CAD. No
complete routed-pipe overlap certificate is claimed.

## Retained recommendation

Develop the **four-single plus two-quad** option as the next working prototype:
102 singles plus22/28 quads at nominal124/161 mm,152 modules and302 chips.
Use the common two-face sandwich, per-chip thermal pickups and kinematic mounting.
It reduces handling operations48.65%, uses two axial levels rather than three,
and lowers reference cable demand. Retain eight singles as the modularity/yield
control. The [comparison report](../validation/DES-017/results.md) contains exact
screens, dimensioned drawings, per-circuit flows, material estimates and reasoning.

The remaining gaps are substantial review gates: neither layout is hermetic over
the original annulus; the mixed layout has more transition misses in the finite
native sample despite less total uncovered area. Both exceed20% silicon overlap
under the0.5 mm guard control, fail degraded thermal conditions at−35°C coolant,
and fail fixed trunk/flange packing. The next prototype needs coverage/service
work and cold mechanical/thermal coupons before adoption. No design approval or
production geometry change is recorded here.

Pending the executable comparison. Production integration, pressure/leak testing,
irradiated thermal stability, detailed collision routing and structural/thermal
FEA remain outside this prototype. Passing a geometric screen supplies no sign-off.
