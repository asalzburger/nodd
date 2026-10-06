# DES-019 — Trimmed mixed-module preliminary pixel model

- Status: DRAFT — isolated PROTOTYPE; engineering approval pending.
- Created: 2026-10-06.
User-selected preliminary baseline; no engineering sign-off or production ODD integration.

The user requests two follow-up PRs: implement the DES018 trimmed mixed endcap
in DD4hep, then describe that baseline in self-contained TDR sources in nodd.
The existing DES013 barrel is unchanged. PR43 merged into the prototype parent
`codex/issue38-disc-overlap` at `7057861fa3c8c137833ecedddcae0856ebd91e4c`.

## Contract and provenance

All inherited dimensions/material hypotheses retain their classifications and
source locators in DES012–018 and ADR006. No new public technology claim is made.

| ID | Classification | Parameter and rationale |
|---|---|---|
| PM-C01 | NODD DESIGN CHOICE | User selects DES018 `four-single-two-quad` survivors as preliminary default. Keep the old `pixel-detector.json` byte-for-byte as a legacy control because prior studies pin it. New default is `pixel-detector-trimmed.json`. |
| PM-I01 | INFERENCE | Reconstruct module centres from DES017 raw template and its frozen face/colour: `anchor=(z²−150²)/z`, `xy=raw_xy*(1+local_z/anchor)`, sensor plane `z+local_z`. Filter exactly DES018 removed rows; reflect negative z. Never recolour or compact survivors. |
| PM-I02 | INFERENCE | Per positive disc modules/chips: 152/302 four times, 134/284 twice, 112/262 once, 84/234 twice. Both ends: 2312/5012. Unchanged barrel: 3050/6794. Combined: 5362/11806. |
| PM-C02 | NODD DESIGN CHOICE | Lossless simulation ID encoding uses module `template_id−200000`, sensor `template_patch_id−300000`; retain gaps. Descriptor `system:5,layer:4,stave:6,module:10,sensor:10,x:-9,y:-9` accommodates columns up to33. Source IDs are preserved in the inventory with disc offsets of10000. Barrel descriptor remains unchanged. |
| PM-I03 | INFERENCE | Proper DD4hep frame: U=`side*mount_face*raw_u`, V=`raw_v`, W=`−side*mount_face*z`. Reverse local U offsets by the same sign. This preserves every active centre and the tangential/radial axes, including rectangular-pixel interpretation; signs only establish handedness and support-facing ASICs. |
| PM-C03 | NODD DESIGN CHOICE | Reuse DES012 sensor/ASIC/flex stack. Active areas20×19.2mm; DES016 guard0.1mm and seam0.2mm. Shared single/quad silicon outlines20.2×19.4 and40.4×38.8mm. ASIC20×21mm with outward0.9mm radial periphery. Occupied body stays DES016. |
| PM-C04 | NODD DESIGN CHOICE | Use DES017 per-chip384mm² pickups and6×8mm graphite stems, with quad stem moved1mm toward module centre. Stem height is frozen colour×1.65mm. Retain full r27..188.5mm,6.3mm sandwich and three inherited mounting tongues/carrier. Removed pickups and cooling rows are deleted; empty-window manufacturing closure is unqualified. |
| PM-C05 | NODD DESIGN CHOICE | Explicit full Ti/CO2 tori reproduce summed retained half-ring evaporator lengths at+1.5mm. Effective core contains radial-leg Ti/CO2 and graphite thermal insert inventory; tori displace the core. Each stem has a48mm² core insert of4.65mm. Replace one skin window per chip with graphite; cradle window48mm² also uses graphite. Remaining core is foam with0.08mm-equivalent internal glue; subtract constituent volumes before filling. This is an explicit simulation allocation, not a CAD claim or identity with DES017's approximate mass proxy. |
| PM-C06 | NODD DESIGN CHOICE | External bend allowances, inherited0.1g/module clips and12g/disc mount hardware, and retained-ring two-face flex buses/tails/radial fans are volume-normalized into the inherited local service cell. No fittings, contacts, hydraulic connectivity or assembly tolerance is inferred from homogenization. |
| PM-I04 | INFERENCE | Heterogeneous service collectors/trunks use actual retained module chains/links and radial chip-row cooling circuits. First eight discs join the fixed trunk, last disc uses inherited bypass. Fixed r192..231.7mm trunk, r222mm neck and collector r27..190mm remain. All DES018 adverse packing scenarios remain failures where recorded. A constructible effective volume is not a packing pass. |

Collector cable inventory uses the mean takeoff radius of the retained chip rows
of each physical ring (one for singles, two for quads). Each chip row has four
feed/return legs. This PM-C06 effective path convention preserves each disc's
actual chain/link count; detailed cable endpoints and coolant manifolds remain
unqualified. The effective core's rectangular insert reservation deliberately
does not reproduce the approximate saddle-bore subtraction in DES017's budget;
its constituent volume ledger is recorded independently.

## Validation and boundaries

Pin frozen layout, screening and parameter inputs. Check stale-pin and malformed
composition rejection, survivor centres against the independent frozen first-disc
patches and direct equations on other discs, complete source-ID mapping, proper
frames, original barrel identity, and retained per-disc cooling/transport inventories.
Native ROOT/DD4hep checks must cover all11806 sensitive centres, signed axes and
dimensions, exclusive material volumes/masses, unique IDs/readouts, overlaps at
1e−5mm and directional radiation/interaction-length scans. Run ROOT roundtrip
and Geant4 initialization with seed42/FTFP_BERT; no event-transport/performance
claim follows from initialization. Preserve actual source/dirty-state hashes.

DES018 analytic/ACTS evidence is inherited, not regenerated or relabelled as
DD4hep navigation. The eta/pT envelope is |eta|≤4, pT≥1GeV, luminous z±150mm,
x/y±1mm, uniform |B|≤4T, first outward half-turn in vacuum. Coverage gaps,
0.5mm guard failure, warm-coolant thermal failure, service overpacking, manifold,
mount coupling, bypass routing and empty-window closure remain unresolved.
TDR sources must report these boundaries and distinguish baseline selection from
design approval. Production geometry and earlier scientific evidence stay unchanged.
