# DES-020 — Longitudinal packing review supplement

- Status: DRAFT; documentary supplement, no design sign-off
- Date: 2026-10-07
- Related: [pinned barrel design](DES-020-short-strip-barrel.md)

The PR49 packing review below is preserved from main. It is separated from the
exact DES020 input pinned by the selected DES021 model so that both contributions
remain available without changing source pins, geometry or native execution
identities. The retained [measurements](../validation/DES-020/z-packing.json),
[report](../validation/DES-020/z-packing.md) and drawing remain unchanged.

## Longitudinal packing of both prototypes — PR49 review, 2026-10-07

SB-I04 — **INFERENCE** from the unchanged SB-C01..08/C14 input choices and
exported compact solids: both prototypes have the same axial schedule in every
layer/stave. The phi tilt rotates U and N around global z, leaving V along z;
it changes stave populations and transverse placement, not row pitch or end
allocation. The [packing report](../validation/DES-020/z-packing.md) and
[machine-readable measurements](../validation/DES-020/z-packing.json) retain the
source hashes and comparison against every frozen axial placement.

| Quantity | Tangential control | +15° phi-tilted alternative |
|---|---:|---:|
| Staves / modules | 284 / 7,952 | 288 / 8,064 |
| Rows per stave; per end's service group | 28; 14 | 28; 14 |
| Row centre range | −1152..+1152 mm | −1152..+1152 mm |
| Row pitch `(2400−96)/27` | 85.333333 mm | 85.333333 mm |
| Adjacent active overlap `96−pitch` | 10.666667 mm | 10.666667 mm |
| Die length including guards; projected overlap | 97 mm; 11.666667 mm | 97 mm; 11.666667 mm |
| Front body including flex; projected overlap | 103 mm; 17.666667 mm | 103 mm; 17.666667 mm |
| Alternating row lift along local N | 1.5 mm | 1.5 mm |
| Gap between overlapping front stacks along N | 0.5 mm | 0.5 mm |
| Same-height front-body gap `2×pitch−103` | 67.666667 mm | 67.666667 mm |
| Pickup length; next front-body axial gap | 64 mm; 1.833333 mm | 64 mm; 1.833333 mm |

The sum of active lengths is `28×96 = 2688 mm` per stave, with a projected
union of 2400 mm. The 27 seams duplicate 288 mm, or **10.7143% of summed active
length**. This is axial redundancy, not a whole-barrel silicon-area overlap
fraction. The silicon planes have 1.3 mm separation between their nearest faces;
the broader front-stack envelopes run from −0.9..+0.1 mm for low rows and
+0.6..+1.6 mm for raised rows, leaving the 0.5 mm gap. Pickups need a shorter
length because the high pickup shares the low module's normal-depth range:
`pitch−(103+64)/2 = 1.833333 mm` clears that neighbour in z. These nominal gaps
do not include manufacturing, assembly or thermal-cycle tolerances.

At z=0, row13 (raised) and row14 (low) overlap actively from −5.333333 to
+5.333333 mm. There is no central active cut or split cold plate. Row centres
assign 14 modules to each end's services even though the two central modules
extend across z=0. The half-stave cooling circuits remain independent: straight
legs occupy |z|16..1210 mm and the inward 12 mm-radius returns have swept outer
envelopes −17.25..−2.75 and +2.75..+17.25 mm, a 5.5 mm central axial gap.
Support/buses are continuous; the central bearing station supplies the proposed
axial datum. Bearings at 0, ±250, ±550, ±850 and ±1150 mm occupy 8 mm each,
with a maximum 300 mm centre spacing and 60 mm from the last centre to the
stave end. Seating, clamps and the other sliding/compliant joints are unqualified.

| Positive end allocation (negative end mirrors the z bounds) | z [mm] |
|---|---:|
| Active silicon / guarded die outer edge | 1200 / 1200.5 |
| Front body and edge flex outer edge | 1203.5 |
| Cold plate, local buses and cooling-leg end | 1210 |
| End-board envelope | 1215..1245 |
| Sector collector | 1245..1310 |
| Downstream trunk | 1310..3500 |

Thus the support extends 10 mm beyond active silicon and 6.5 mm beyond the
front-body/flex edge; the support-to-board axial gap is 5 mm and front-body-to-board
gap 11.5 mm. The board meets the collector's axial boundary, giving no additional
axial connector allowance at that interface. These are occupied bounds and route
allocations, not qualified fittings or connected cable/manifold CAD. The old
1295.5 mm endcap datum is 14.5 mm inside the collector's outer boundary; its
conflict and the mean packing failure remain explicit. This figure preserves the
PR49 control interface; later endcap work is a separate revision.

The projected active union has no axial hole, but tilted/displaced finite planes
still lose some eligible nominal-cylinder crossings near the ends. The retained
coverage failures and unchanged denominator in both reports remain applicable.
Nominal seams, native zero-overlap checks and a drawing do not establish
full-track hermeticity, mechanics or service qualification.

![Longitudinal packing, central seam and barrel-end allocation](figures/DES-020-z-packing.svg)
