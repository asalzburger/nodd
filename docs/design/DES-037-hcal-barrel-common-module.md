# DES-037 — Barrel HCAL from the common readout module

- Status: **DRAFT**; Type: **PROTOTYPE / design proposal**
- Date:2026-10-15
- Human direction: use DES036 common module; design barrel and endcaps in separate PRs.
- Parent:[DES036](DES-036-hcal-common-readout-module.md),[DES035](DES-035-hcal-realism-and-prototype-plan.md),[DES034](DES-034-siw-service-envelopes.md).
- Human engineering owner/sign-off: unassigned/pending. Production integration absent.

## Governing contract and provenance

**FACT about human direction:** use DES036 as the working common readout module for a14TeV hadron collider and produce separate barrel/endcap PRs. This selects a working design basis; it is not engineering sign-off. Preserve the184mm36tile board and380x240x12mm two-board carrier, including its material, channel, heat and service ledger. Other operating values remain the DES036 planning inputs.

**NODD DESIGN CHOICE — common depth amendment:** retain36sampling layers and30mm steel per layer, the12mm carrier,1mm installation allowance and10mm rear cover. Total depth is36*(30+12+1)+10=1558mm. DES034 allowed1495.9mm. Propose62.1mm more depth rather than silently compress hardware or reduce steel. Even36*(30+12) exceeds the old outline before covers/gaps. Alternatives35layers at1mmgap (1515mm total),36at0.5mmgap (1540mm), or reduced absorber require a separate reviewed sampling/mechanical decision. Existing FCal reservation is unchanged. The steel-only nuclear-interaction screening is inherited from DES035, not a shower-containment claim.

**NODD DESIGN CHOICE — unchanged cell hardware:** no cropped boards/tiles or fictitious continuous sensitive sheet. Source-backed package dimensions/material host and effective proxy details remain DES036. The common carrier has projected tile-core area72*29.7^2=63510.48mm2,69.64% of its91200mm2 face before external packing losses. Report this ceiling; staggerring changes directional sampling but not per-layer area. Regional layouts are analytical design prototypes, not new native whole-detector qualification.

## Barrel geometry and service ownership

All new dimensions below are **NODD DESIGN CHOICE — unsigned**. Inherit innerapothem2600mm,half-length4483.2mm and16sectors from DES034/029. Propose outerapothem4158mm including10mm backcover; outercorner is4158/cos(pi/16)=4239.460mm. Preserve ECAL serviceannulusR2300..2600 and the400mm rearbreak toendcapfront4883.2. At theR4300 handoff, after25mm water-jacket radius and20mm clearance,15.540mm remains beyond the HCALcorner; this is a narrow geometric allowance, not space certification for HCALservices.

Use carrierx tangent,y axial,z outward. A sector atphi has local basisx=(-sinphi,cosphi,0),y=(0,0,1),z=(cosphi,sinphi,0), determinant+1. Carrierfront is layerfront+30mm; absorber occupies layerfront..+30, carrier..+42, installation gap..+43. Carrier centres include+6mm localdepth. Cover follows the36th full pitch. Steel absorber plates are sector-owned once per layer, not repeated per carrier. Aluminium20mm edge rails and20mm endflanges own disjoint reserved strips;10mm backcover is separate. Structural sizing/buckling/lifting/loadtransfer remains unqualified.

Pack33axial rows,240mm carrierheight with20mm named empty collector strips between rows (260mm pitch),1mm tangential gaps. Reserve20mm edge rails and20mm flanges inside the recorded envelope. Carrier-count at each layer follows the narrow carrierfront face, with all8corners checked through carrierdepth. Recompute tangential counts with depth. Apply layer offsets tangent[-90,-35,35,90]mm andaxial[-60,-20,20,60]mm; offset arithmetic is a choice, and every placement must remain inside its steel/structural boundaries. Compare exactsame33rows with aligned tangent0/axial130mm as a deliberately adverse control; it places a service gap at the IP midplane. Do not call phase0 an all-empty-midplane control because an odd centred row count includes an active row.

Collector strips are empty allocations,not zero-mass installedmanifolds. DES036 has two parallel waterbranches andfour externalports per carrier. Group rows/sector into named handoffs at both barrelends with endpoint counts and ideal flow; do not claim a connected collector/pressure-drop network. LV,bias,data,trigger/control egress follow the same ownership boundary; chip-lane sum is not a qualified carrier/sector concentrator. Preserve open extraction: disconnectendservices and removebackcover/coldplates as necessary; pulloutfromclosedsectors is not established. External supportandserviceplant are excluded and listed.

## Required calculations and gates

Provide deterministic layout/count/ownership/constituent mass roll-up, all-channel continuous heat/current stresses, links and ideal coolant. Derive face fractions using the complete geometric sectorface and its explicit support/empty strips; do not shrink denominator to activepack. Compare aligned and staggered masks using actual29.7mm tilecores andeffective rearrecess, with layercrossings andmaterial-depth bounds versuseta/phi, includingsectorseams,midplane,barrelends andtransitioneta0.9..1.4. Identifiers retain DES036 descriptor/system9/side0/sector0..15/layer0..35/carrier0..4095/module0..1/sensor0..35; encode/decode uniqueness andproperframes needcontrols. Coordinate/cellmask checks are analytical, distinctfrom prior nativeunit evidence. At boundaries, report missesratherthaninterpolate acrossphysicalgaps.

Independent review assesses counts, transforms, geometric claims, envelopeamendment and limitations at exactrevision. Negativecontrols reject compresseddepth,oversizedoffsets,duplicateIDs,absorberdoublecount,wrongpoweredchannels andhiddenservicegaps. Full-DD4hep assemblies,showerresponse,pileup/digitization,sustainedrates,radiation,EOLandthermal/structuralqualification follow review. The common module native smoke is inherited evidence only. No detectoracceptance from projectedarea or samplingcounts.

## Deliverables and review questions

A regional layout tool/config and bounded tests, dimensioned transverse/axial andRZ drawings, source-bound report andprojecttracking will accompany this proposal. Review the62.1mm envelopeamendment,real service routing and residual cracks before promoting it into the selectedcandidate. Separate endcap proposalDES038 retains the same module/depth contract; merging one PR doesnotaccept the other.
