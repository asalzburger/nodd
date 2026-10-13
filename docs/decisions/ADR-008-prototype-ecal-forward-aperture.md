# ADR-008 — Prototype ECAL forward aperture and carrier boundaries

- Status: **DRAFT**
- Created: 2026-10-13
- Human owner: TBD
- Author: Codex, AI-assisted proposal
- Related designs: [DES030](../design/DES-030-ecal-edge-sensors.md), DES029
- Human approval evidence: user authorized extending the **prototype target**
  toward |eta|4; engineering sign-off and production acceptance remain pending.

## Context and evidence

**FACT:** DES029 places the ECAL front at z=3950mm and gives the endcap a300mm
inner apothem. Its large cassette packer further postpones sensitive material
to approximately909mm. **INFERENCE:** a straight |eta|4 ray has front radius
3950/sinh(4)=144.7421mm. The historical aperture itself must change to explore
that target; custom perimeter sensors alone do not resolve it.

**NODD DESIGN CHOICE proposal:** DES030 uses a90mm-apothem square aperture,
5mm surrounding support, four quadrant carriers and the retained sixteen-sided
outer envelope. The supported corner is95×sqrt(2)=134.35mm, leaving approximately
10.39mm to the target front radius. Five-mm side reserves and25mm outer service
bands remain. The first compact-square grid begins outside these reservations.
This allows instrumented directions near eta4 but does not eliminate seams.

## Options and consequences

| Option | Benefit | Cost / limitation |
| --- | --- | --- |
| Retain300mm hole | Preserves previous interface hypothesis | Blocks front-plane eta4 regardless of packing improvement |
| Smaller square aperture and four carriers | Repeated compact grid and compatible prototype forward target | Changes inner support/services and machine interface; needs review |
| Smaller polygon/circular hole with custom inner masks | More freedom to optimize inner material and boundaries | Additional shapes, readout/edge termination and mechanics beyond this first prototype |

The human clarification authorizes exploration of the second option. It does
not establish beam-pipe, shielding, forward detector, thermal or structural
clearance, or set a production detector acceptance requirement. Existing DES029
and its evidence are retained, so the comparison is reversible and auditable.
No tracker/magnet/HCAL envelope or production compact entry point is changed.

## Validation and open questions

Compare square-only and custom-edge masks with identical new reservations;
audit all native shapes, material, IDs/electrode mapping and overlaps. Publish
active-layer counts versus eta/phi, including narrow cracks and zero-hit rays.
Required human work includes machine/forward integration, support stiffness,
service headers/ports, sensor process/HV design and numerical coverage criteria.
No human review outcome or formal sign-off is recorded here.
