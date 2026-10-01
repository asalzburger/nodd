# DES-014 — Pixel endcap local disc support

- Status: DRAFT — isolated PROTOTYPE design and screening; no engineering sign-off.
- Created: 2026-10-01.
- Human request: design a low-material common local disc support, mounting rails,
  cable routing and cooling, using public literature where needed.
- Governing inputs: [DES-011](DES-011-service-constrained-tracker-optimization.md),
  [DES-013](DES-013-pixel-barrel-z-coverage.md),
  [DES-010](DES-010-tracker-service-corridors.md),
  [DES-002](DES-002-pixel-barrel-support-cooling.md), module issue
  [#7](https://github.com/asalzburger/nodd/issues/7).
- Scope: endcap passive-support design, original technical drawings and a repeatable
  screening model. Production geometry and baseline sensitive transforms stay fixed.
  Human review of this proposal is required before implementation.

## Contract before modelling

| ID | Classification | Requirement / rationale |
| --- | --- | --- |
| EC-C01 | NODD DESIGN CHOICE | Read the SHA-pinned `packed-200um` layout from DES013 (PR34, with PR35 barrel implementation). Keep the source baseline byte-for-byte unchanged; case A preserves every centre, rotation, bound and identifier. Check all 18 pixel discs for a common local pattern. EC-C06 separately defines a proposed placement amendment for B. |
| EC-C02 | NODD DESIGN CHOICE | Prefer carbon sandwich construction, thin titanium two-phase CO2 tubing and local flexes. Include realistic support-to-carrier load paths and service exits. Compare feasibility of supporting the existing eight stagger levels before choosing a common architecture; do not silently restagger modules. |
| EC-C03 | NODD DESIGN CHOICE | Minimize material subject to explicit geometric, thermal and stiffness screens. Numerical comparisons are design screening, not qualified thermal FEA, structural FEA, pressure certification, electrical design or detector acceptance. |
| EC-C04 | NODD DESIGN CHOICE | Reuse DES002 material and power assumptions as labelled provisional inputs. Count new passive components and reserve unresolved fittings/cables explicitly. Keep local disc inventory separate from shared rails, carrier and accumulated services. |
| EC-C05 | NODD DESIGN CHOICE | Preserve the DES010 r=190..234 mm pixel trunk and 50 mm collector depth. EC-C08 separately proposes a first-disc/collector translation; it is not adopted. Evaluate their remaining capacity with the current barrel inventory. Any failure is reported as an unresolved interface, not hidden by changing the baseline. |

Engineering dimensions, source facts and screening conclusions are added below
as the design is developed. None of these choices records human approval.

## Proposed architecture and comparison contract

**EC-C06 — NODD DESIGN CHOICE (proposed amendment, not adopted):** compare a
backplate retaining all baseline transforms (A) with a common annular sandwich
between alternating front/back radial rows (B). B preserves all x/y positions,
chip areas, module families and identifiers. It uses three phi heights on the
innermost row and two elsewhere. B changes sensor z and mounting face; its tracking
and material consequences require a follow-up coverage/ACTS study before adoption.
The existing layout file and production DD4hep configuration remain unchanged.

**EC-C07 — NODD DESIGN CHOICE:** B uses a 6.3 mm sandwich: 0.15 mm CFRP faces and
6.0 mm foam core. Two tube-routing planes at w=±1.5 mm separate radial transport
legs from azimuthal evaporators (2.8 mm OD, 0.15 mm Ti wall). Use common 18×8 mm
outer-edge support lands, centred 16 mm radially outside each module centre.
An 0.45 mm pickup stack comprises 0.30 mm graphite, 0.075 mm CFRP cradle,
0.025 mm electrical insulation, 0.025 mm TIM and 0.025 mm adhesive. Contact windows
bypass the cradle/skin in the thermal path. Raised graphite feet have an axial
conductivity target of 500 W/(m K); their grain must be oriented accordingly.
The skin/core interface, tube saddle and pedestal are not isotropic graphite.
Each insert has a machined 180-degree saddle around the Ti tube; count the
block to the tube centre minus its half-cylindrical bore, not a tangent-only contact.

**EC-C08 — NODD DESIGN CHOICE:** pickup-to-pickup steps are 1.65 mm: 1 mm
occupied module + 0.45 mm pickup + 0.20 mm nominal gap. Innermost columns use
`col % 3`; others use `col % 2`. Even radial rows face the IP, odd rows face away.
The common plate datum is the old nominal disc z, except the first disc on each
side moves 3.5 mm away from the IP, together with its collector bay, to preserve
clearance to the existing barrel turn. All dimensions are proposals, not approved
changes to DES011. Heights and interface positions must be derived from these
inputs, not separately tuned to a coverage result.

**EC-C09 — NODD DESIGN CHOICE:** ten independent half-ring evaporators/disc,
two per radial row. Nominal flows per half-ring, inner to outer, are
1.0, 1.3, 2.0, 2.3, 2.5 g/s. Reference coolant temperature −40 °C; retain
−35 °C sensitivity, inlet quality 0.10, ceiling 0.45 and 1.5× thermal load.
Use −15 °C hottest-sensor screening target, with explicit missing irradiated
sensor feedback. Flow/quality arithmetic does not establish hydraulic stability,
pressure loss, boiling coefficient or leak/pressure qualification.

**EC-C10 — NODD DESIGN CHOICE:** use one common full annular disc, three radial
mounting tongues and three longitudinal CFRP box rails on a thin closed CFRP
carrier tube. At each disc, a cone/slot/plane coupling defines six rigid-body
constraints without six rigid mounts. Shared rails need the carrier shell and
end flanges for stiffness; they are not unsupported 2.5 m beams. Whole endcap
installation is axial; no independent half-disc extraction around an installed
beam pipe is claimed. Shell split-line/access design remains open.

**EC-C11 — NODD DESIGN CHOICE:** route thin bus flexes on both plate faces around
thermal lands. Each module drops only to its own face through a side slot in its
foot. Flexes turn at the outer rim into the existing collector bay; none is
assumed to pass axially through an opposite-face module. Split electrical chains
at half-ring boundaries (at most 8 quads), separately from the ten hydraulic
circuits. Keep provisional cable fill/material and reference/conservative/stress
bandwidth hypotheses explicit. No full-area rigid PCB is selected.

**EC-C12 — NODD DESIGN CHOICE:** use orthotropic thermal screening with
1500 W/(m K) in-plane graphite and 7 W/(m K) through-plane, plus degraded
1000/500 W/(m K) cases. These are procurement/coupon hypotheses, not measured
nODD properties. Use a 2D finite-volume heat-spreader calculation, added lumped
contact/foot/tube resistances, heat-transfer coefficient sensitivity and a
uniform-load versus ASIC-periphery concentration comparison. Failure is retained.

## Complete provisional parameter register

The executable [input file](../../tools/pixel_endcap_support/inputs.json) is the
single parameter list for drawings and arithmetic. All proposed choices below
have **human approver: pending**. There is no implicit sign-off through this PR.

| ID | Classification | Parameters and rationale |
| --- | --- | --- |
| EC-C13 | NODD DESIGN CHOICE | Plate r27..188.5 mm preserves the beam-pipe aperture and stays below r190 services. Three tongues 10 mm wide, r186..228; three 8×8 mm rails with 0.4 mm walls at r223.7..231.7; closed 0.3 mm CFRP shell r231.7..232.0, |z|609..3136. End flanges 10 mm radial ×2 mm axial. Start after barrel turns and end before rear collection. These are a first stiffness/mass screen, not pressure vessel or shell-buckling specifications. |
| EC-C14 | NODD DESIGN CHOICE | Allow 12 g/disc Ti-equivalent mounting hardware, 0.10 g/module CFRP clips, 4 g/module payload and 5 kg/end external service load for gravity only. Use E=70/100/140 GPa, local 0.1 mm and carrier 0.25 mm deflection screens. These are not alignment tolerances or manufactured weights. Local flex estimate: 8×0.20 mm bus envelope per ring, three radial fan envelopes per face, 8×0.12 mm module tails with height+12 mm length. Provisional 10% Cu/40% polyimide/50% air by volume is inherited from the human-authorized barrel cable study; it is configurable and not a conductor schedule. |
| EC-C15 | NODD DESIGN CHOICE | Tube length = ten half-arcs + both radial legs per circuit +30 mm/leg bend allowance. 4 mm-OD feed and return transport reservations preserve DES010. A 10 mm bend-radius target and two routing planes reserve space but do not validate swept bends or weld access. Internal glue equivalent 0.08 mm replaces foam. Edge closeouts replace foam too. Material inventory assumes disjoint later pipe/insert routing and includes full-liquid mass. It is a parameterized estimate, not a solid-model volume measurement. |
| EC-C16 | NODD DESIGN CHOICE | Thermal calculation uses h=10/20/30 kW/(m² K), 16 W/(m K) Ti conductivity as a screening comparator, TIM k=1 and bond k=5 W/(m K); 2×25 µm narrow-contact bonds. The 0.30 mm graphite has separate normal conductivity. Heat is uniform or has 66.7% in 1.8 mm edge strips (hot-region sensitivity; no claim of the actual pad map). 1.0/0.5 mm finite-volume grids, CG relative residual 1e-10 and 1e-7 mm OBB tolerance are numerical settings. They are not construction tolerances. |

**Correction during design development, 2026-10-01:** an initial 3.5 mm plate
reservation was insufficient for two crossing 2.8 mm tube-routing planes. EC-C07
therefore uses 6.3 mm, as recorded before the retained report run. Each tube has
0.1 mm nominal core clearance to a skin; adjacent routing planes clear by 0.2 mm.
An initial two-height inner-row trial also collided with next-nearest neighbours;
EC-C08's three-height pattern is the retained proposal. These exploratory failures
are regression controls, not silently discarded accepted evidence.

## Recommendation and unresolved engineering

Develop **B: the common sandwich disc with alternating mounting faces, short
outboard thermal feet, three-point couplings and rails bonded to a closed carrier**.
The outer carrier is part of this recommendation: thin standalone long rails are
not a stable load path. Keep the local disc common on all 18 stations; use an
external adapter for the last-disc bypass. Axial assembly is the current access
assumption. Do not claim a removable half-disc around an installed beam pipe.

This is a recommendation for **mechanical development**, not construction or
layout adoption. The [retained results](../validation/DES-014-pixel-endcap-support/results.md)
show a thermal stress failure and little reference trunk headroom; the adverse
cabling cases fail. A facesheet/foam concept alone does not close those issues.
A broad thermal pickup or second pickup path needs measured coupon/3D analysis
before selecting the final module-support interface. The 0.2 mm gap must include
all assembly and thermal-motion errors; it has not been tolerance-qualified.

The proposed module z values and mounting faces alter the active geometry.
X/y positions, families, module counts, IDs and silicon area are retained, but
coverage and material-before-hit distributions are **not** guaranteed unchanged.
Rear-face rows see the plate before their sensor for outward tracks. A matched
ACTS coverage/material study is an explicit next step, after review of the
support-driven placement proposal. The first-disc/collector shift, 6.3 mm central
plate and equivalent material budget are proposed amendments to DES010/011;
none is applied to their accepted or working files in this PR.

See the [public evidence dossier](inputs/DES-014-literature.md),
[repeatable workflow](../../tools/pixel_endcap_support/README.md), and
[technical drawing book](../validation/DES-014-pixel-endcap-support/drawings.pdf).
