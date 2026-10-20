# SS-A1 — Updated inward-intercoil B1 and rotated B2 interface assessment

Input revision: `a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f`.
Role: SysArch, explicitly supplied fallback mandate; repository read-only.
Status: DRAFT isolated unsigned outline assessment. No human acceptance,
production integration, native execution or performance qualification.

The updated sketch is geometrically feasible at the provisional inter-coil
B1 apothem **4.63 m** with the retained 500 mm depth. All 24 complete full-z
B1 templates pass actual-orientation full-volume coil checks, all 484 fixed
support envelopes at 50 mm, and actual finite HCAL steel/cover checks at 50 mm.
The known ECAL service water-jacket reservation also clears. The B2 7.5-degree
rotation requires fresh finite cuts around the existing ECT front spokes/lugs
and coils; a blind rotation/full-z chamber is obstructed in all 24 facets.

## Input identity and workflow

The executable checker extracts every source with `git show REV:path` into a
fresh temporary directory and imports only that extracted numerical source.
Its result records full commits, paths, blob IDs, SHA-256, byte counts and exact
extraction commands for 20 input files. The nine dispatch hashes are asserted.
The dirty working-tree DES040 updated-sketch append was read solely as the
preconstruction workflow contract; its numerical claims were independently
re-derived from pinned geometry. Current AGENTS/PROJECT/role instructions and
the nodd-design-evidence and nodd-review-validation skills were read. ADR002,
ADR003 and ADR006 govern human-only acceptance, retained evidence and envelope
scope. The coordinator curates this contribution into the project journal.

The exact additional HCAL source is
`0e8530d56d171f38c9d53d3c60c8b48803680bbd`, as recorded in pinned
`docs/validation/MUON-001/hcal-material.json:repo_head`. The checker verifies
that the three HCAL source hashes match that retained record:

| Source | Blob ID | SHA-256 |
| --- | --- | --- |
| `tools/hcal_barrel/design.py` | `1f9f1e99b6d0facadf2b9eb6b2ab529375661530` | `14692cff976bef5bdb19aa5d9897b5fd89297ecc9f9bb2e89cc1a69928a9d3e6` |
| `tools/hcal_barrel/config.json` | `a877b5e64eb9d30057b2814f52bfede04111ad71` | `969f05111039de2686d9454a29fe348c56a91a5316716515fdfedafea5479d64` |
| `docs/validation/DES-037/summary.json` | `d438422d2cea4ab47edd658758e977e28690c8c6` | `68c4aa00a43b4e813d6c88552e000caf67cdb178e668b223c21f377b88117753` |

Service evidence at the same HCAL commit is `tools/siw_services/inputs.json`
(blob `302287fe94971b6a143a6c64ede4700dd611b30f`, SHA-256
`ec72666b683a5c069d1f19e73ac03fadeb4a2d4819a5872d0965f2d45732860e`),
`tools/siw_services/study.py` (blob `d3acec5f3679356e5d6a536716d72dc9c8353ce9`,
SHA-256 `f31417c096885e48d0834b8f89ca6685da23d50e6d02514a4a3e25d8ee362701`)
and `docs/design/DES-034-siw-service-envelopes.md` (hash in result manifest).

## Whole-volume B1 inequalities

All proposed dimensions remain NODD DESIGN CHOICES, not public experimental
facts. The following are INFERENCES from those choices and the pinned solids.
Let h=0.25 m, border b=0.03 m, neighboring pitch p=15 degrees, and target angular
overlap 0.1 degree. Retained even half-width is

`w_even=(5.2−h)tan(7.5deg)−0.01=0.6416798630576094 m`.

Its limiting full-depth border angle is
`atan((w_even−b)/(5.2+h))=6.403783462153276 deg`.
The odd limiting angle is therefore `8.696216537846722 deg`, and

`w_odd(R)=(R+h)tan(8.696216537846722deg)+b`.

At R=4.63 m the odd full width is **1.552830294051612 m** and its outer
corner radius is **4.941378398840865 m**. The supporting plane normal to the
adjacent even facet gives the whole-prism physical gap

`G=4.95−[(R+h)cos(p)+w_odd(R)sin(p)]`.

At the chosen R this is **35.330940752995 mm**, exceeding 20 mm by 15.331 mm.
Requiring G>=20 mm gives **R<=4.645246881421718 m**. Conservative expanded-SAT
contact is rejected at equality; use a strict numerical guard at that boundary.
All 24 adjacent full-z template pairs independently pass the existing SAT at
20 mm. Packed subsets inherit this separation.

For the BT inner legs, the closest complete odd prism is outside each adjacent
warm tangential slab by

`(R−h)sin(p)−w_odd(R)cos(p)−0.30=83.667975114791 mm`.

That exceeds the 50 mm coil requirement; its sufficient lower bound is only
R>=4.326894898160221 m. The complete B1 z interval is ±6.4456 m; the ECT warm
front is at |z|=7.05 m, leaving 604.4 mm before the coil, not a central-slice-only
claim. Actual-orientation adaptive distance certificates independently pass
all 24 full-z B1 templates, using 58,344 cells in total. No unresolved cell is
accepted and no cached historical coil certificate is loaded.

The known water-jacket all-azimuth outer bound is R=4.325 m. A sufficient
50 mm radial clearance plus the 250 mm chamber half-depth gives **R>=4.625 m**.
Together these give the conservative whole-prism feasible interval
**4.625 < R < 4.645246881421718 m**, with the lower equality mathematically
providing exactly 50 mm. The selected R4.63 has **55 mm** jacket clearance,
5 mm above the requirement. This is a sufficient interval for the named
reservation, not a certification of unimplemented services or proof that all
smaller radii collide with installed material. R4.60 has only a 25 mm radial
bound to that reservation and cannot pass this 50 mm sufficient check.

## HCAL actual material and service reservations

The actual finite steel bands are reconstructed from all 36 layer records in
DES037 summary, steel thickness 30 mm, sector half-angle pi/16, 21 mm edge
inset and usable |z|<=4.4632 m. The rear aluminium covers span local normal
4.148–4.158 m, 1 mm seam inset and the same usable axial interval. The checker
constructs all **592 finite steel/cover prisms**, then checks each against all
24 full-z B1 prisms with the conservative 50 mm SAT expansion: **zero conflicts**.
Their actual maximum corner radius is 4.239265058964133 m.

This verifies physical solids rather than interpreting a bounding cylinder as
filled steel. All other regional barrel material and endcap material are
contained by the retained 4.23946/4.229264124248104 m corner bounds. The new B1
inner radial plane at 4.38 m is at least **140.54 mm** outside the larger bound,
so their entire finite z extents clear at 50 mm as well.

The R4.300 m egress and 25 mm jacket radius in DES037 configuration refer to
**DES034 ECAL external water egress through the HCAL barrel/endcap break**.
The route goes axially in the R2.45 m backbone, bends with 200 mm radius and
ends at R4.300 m, |z|=4.6832 m. Its 50 mm diameter jacket has conservative
R<=4.325 m and |z|<=4.7082 m. The checker reconstructs all 70 route vertices;
this radial bound also encloses the intervening straight segments and circular
elbow. DES034 explicitly describes empty corridor reservations with no installed
material. The existing route-study extra 20 mm installation sweep is not a
second material jacket; the new 50 mm chamber-to-reservation gap is a separate
interface requirement.

Do not call R4.325 the complete installed HCAL service envelope. DES037
`services.implementation` explicitly says its 20 mm row strips are empty
reservations; collectors, frame penetrations, cabling, pressure drop and plant
are unimplemented and excluded from mass. The cable egress/local collector
arrangement, mounting, and any future HCAL external route remain unqualified.
Source distinctions preserve the existing known reservation without inventing
installed tubes or silently dropping an open interface.

## Changed B2 and actual symmetry

The chamber pitch is 15 degrees; a 15-degree rotation preserves the 24-facet
edge set. The directed 7.5-degree phase de-aligns it, with every actual transform
freshly checked. At R6.7 m, 500 mm depth, the inherited tangent width formula
remains unchanged. Magnetic source geometry truly has C12 symmetry: twelve BT
planes at 0+30k degrees and each ECT at 15+30k degrees. A coil cache may reduce
actual phase modulo30 degrees while retaining radius, vertices, depth and
configuration identity.

The complete support geometry is **not** C12. A 30-degree rotated multiset test
on all eight world vertices per member maps 444/484 supports back to the
original set. The remaining **40** are the ten four-part feet. HCAL has sixteen
sectors, so coil C12 cannot certify HCAL or all supports. Every actual chamber
orientation must be tested against all 484 finite fixed support envelopes.

All 24 unsplit full-z B2 prisms at phase7.5 degrees are obstructed by the ECT
front return; an example occupied witness for F00 is
`(6.560531437735499,1.4985101062785415,7.1875) m`.
All 24 also conflict at 50 mm with their adjacent fixed ECT front spoke and
radius6.8 m lug on **both z sides**. For F00/F01 the IDs are
`ECTM-front/SPOKE00`, `ECTM-front/LUG00-1`, `ECTP-front/SPOKE00`,
`ECTP-front/LUG00-1`; other facets map to successive coil indices.
The spoke occupies |z|6.15–6.45 m and the front lug occupies6.45–7.05 m.
Where their finite XY footprints overlap a panel, the corresponding expanded
axial exclusion reaches6.10–6.50 and6.40–7.10 m respectively. Coil return cuts
also remain. These localized cuts require finite repacking and fresh
certificates, not moving the frame or wheel. The coordinator/MuonTech final
candidate audit owns its exact accepted leaves; these full-z adverse controls
show why recomputation is necessary.

## Retained native entrance and negative witness

The selected **R4.35 m, half-z6.4684 m, 10 micrometre forward offset** entrance
is valid for R4.63 B1 and can be retained for direction-bank continuity.
A sufficient open radial interval is
`4.325 < Rentrance < 4.38−0.00001=4.37999 m`.
A sufficient cap interval is
`6.4412 < Hentrance < 6.4956−0.00001=6.49559 m`.
The retained radius is 25 mm outside the known jacket bound. Every barrel
point has r>=4.38 m and every first-endcap point has |z|>=6.4956 m; a unit-vector
10 micrometre offset can increase radius or |z| by at most10 micrometres.
Thus **the entire closed entrance surface plus offset** remains before every
finite chamber, over the full z range and both ends. Reserves are at least
**29.99 mm radially** and **27.19 mm axially**. The fact that the cap is outside
B1's |z|6.4456 endpoint causes no skipped B1 hit: its r<=4.35 m remains below
all B1 material before the cap.

The prompted inside-start issue occurs for the **R4.60 diagnostic**, whose
inner face equalsR4.35, not for the selectedR4.63. A negative actual containment
fixture takes phi15 degrees and entrance z=1 m. Its outward unit direction is
`(0.9413716547534359,0.2522397746687328,0.22404129909872567)` and offset start is
`(4.201786758073994,1.125865368593712,1.000002240412991) m`.
This point is inside the diagnostic R4.60 odd panel with z0.01–3.2178 m; it is
outside the selectedR4.63 panel. Both predicates are asserted. No unnecessary
entrance change is selected. This is a geometric start-bound proof, not an
ACTS/DD4hep propagation run or a strict-map validity certificate.

## Checks, portable execution, files and limits

Executed successfully:

```sh
python3 -B /private/tmp/pr90-SS-A1-check.py \
  --repo /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout \
  --revision a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f \
  --output /private/tmp/pr90-SS-A1-check.json
```

Python3.14.6, NumPy2.5.1; initial bounded run2.769s, exit0. A fresh extraction/CLI rerun took3.004s, exit0; all scientific fields and source manifests matched exactly after excluding runtime metadata. `/private/tmp/pr90-SS-A1-portability-check.json` records the comparison. No framework runtime
or dependency installation. Source extraction automatically starts fresh; no
pre-existing scratch tree is needed. Optional `--candidate PATH` audits every
B1/B2 candidate barrel with fresh actual-orientation coil and all484 support
checks and records retained magnetic/support/B3/endcap equality. It does not
write or adopt that candidate.

Repository files changed by SS-A1: **none**. Scratch deliverables:
`/private/tmp/pr90-SS-A1-check.py`, `/private/tmp/pr90-SS-A1-check.json`,
`/private/tmp/pr90-SS-A1-report.md`, `/private/tmp/pr90-SS-A1-portable-recheck.json`, and `/private/tmp/pr90-SS-A1-portability-check.json`. Additional scratch extracted read inputs in
`/private/tmp/pr90-SS-A1-inputs/` are supporting material, not prerequisites.
The result JSON includes a physical interface register with both endpoint
owners, coordinate conventions, margins, exact input revisions and methods.

Unresolved: complete external HCAL/ECAL collectors and cables, mounts and local
chamber services; mechanical sag, construction/readout/chamber internals;
material transport and installed ferromagnetic-field solution; native numerical
validation of a changed candidate. Endcaps/B3/484supports/HCAL/magnets/maps
remain fixed. The middle-wheel uniform eta3 gap remains open. Changed planar
coverage or phase cannot establish a constant lever arm, MDT momentum resolution,
material qualification, reconstructed efficiency or engineering acceptance.
