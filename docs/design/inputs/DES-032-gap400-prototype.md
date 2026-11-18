# DES032/033 — conditional 400 mm barrel/endcap gap prototype

2026-11-18. **DRAFT / isolated PROTOTYPE**, explicitly requested as a separate
PR above the 1 m-gap restored LAr working baseline. Parent implementation source:
`7a9da4490f3bbe89f9d55fbfcadc795a3889139b`; baseline selection is PR150.
No engineering sign-off or physical side-port connection is implied.

**NODD DESIGN CHOICE:** translate both complete restored endcaps 600 mm toward
the IP, retaining barrel geometry, 650 mm endcap depth, all materials, local
solids, readout and vessel/bath/wall budgets. Warm endcaps become abs(z)=4500–5660
mm; cold bounds4600–5510 mm; sampling4610–5260 mm. The warm barrel ends4100 mm,
giving400 mm clearance and700 mm separation of sampling axial bounds. Keep HCAL
context fixed at barrel half-length6260 mm and endcap front6760 mm. Thus the
endcap-back-to-HCAL interval is1100 mm, while the radial exit window remains
6260–6760 mm,500 mm. HCAL construction is absent from this ECAL study.

## Explicit route-reservation hypothesis

**FACT about the parent model:** external routes are empty reservations, not
native pipe/cable material. The restored model's front S-bend screens are
834.082/854.082 mm for80/100 mm jackets at R400; they cannot fit400 mm.
The896.8/916.8 mm numbers belong to its earlier dense compact control.

**NODD DESIGN CHOICE:** add an opt-in `pre_end_side_neck_reservation` policy.
Retain the original front-S-bend validator as the default. Check the same actual
R400 bends against a mirrored pre-end band abs(z)=3000–4000 mm; never simply
disable the bend guard. Add two20 mm face clearances to the new screen. Ports,
cold headers, pressure/vacuum penetrations and swept support/board clearances
remain unconstructed. The band intersects populated board rows and H-rings at
3250/3750 mm: a reservation pass is not a connected physical-route pass.

**NODD DESIGN CHOICE:** centre the outer bus at R3039.5 mm and use140 mm-high
annular-sector lanes. Between the endcap2949 mm and HCAL3130 mm boundaries,
R2969.5–3109.5 mm leaves20.5 mm on each face. Lane width means centre-radius
arc length, not a flat box whose corners could intrude. Preserve ordinary700 mm
and utility1100 mm widths,16station sectors per end, all pipe ODs, cable counts,
packing fill and electronics/channel hypotheses. Barrel/endcap utility stations
use distinct sectors0/8; both ordinary bundles share the other sectors.

**INFERENCE**, independently screened by CaloTech from the pinned source:
ordinary/utility areas are98,000/154,000 mm². The worst mixed utility+ordinary
station uses about139,843 mm²; two coincident utility bundles would exceed the
available area and must fail. Minimum angular-face margins are240.856/45.725 mm,
above20 mm. Revised radial shift492.5 mm gives858.542/878.542 mm S-bend bounds
with two clearances, leaving121.458 mm in the1000 mm pre-end band for OD100.
The conservative OD100 rear elbow occupies490 mm of the500 mm exit window.
These are reservation and area checks, not individual bundle packing or mechanics.

## Forward interface and validation boundary

Preserve the prospective FCAL/collar source and flag its conflict explicitly:
the moved warm endcap intersects the [historical prospective collar reservation](../../layouts/LAYOUT-002.json) over R301–450
mm and abs(z)=4500–4850 mm. The forward system is absent from this native ECAL
stage; its prior clearance result does not transfer. No reservation is silently
deleted or claimed integrated.

Before drawing conclusions, require unchanged barrel XML/material and local
endcap shapes/materials/masses/IDs, mirrored signed translations, native
construction/overlap controls and transport/readback smoke checks with recorded
scope. Response comparisons must state that external ports/necks/buses add no
new native material in this conditional study. No precision improvement, complete
containment or physically routed services is inferred from moving an envelope.
The selected1m-gap baseline remains available unchanged.
