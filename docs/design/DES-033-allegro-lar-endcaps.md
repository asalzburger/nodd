# DES-033 — ALLEGRO-style turbine LAr endcaps for LAYOUT-002

- Status: **DRAFT**
- Type: **PROTOTYPE**
- Date: 2026-10-13
- Parent: DES032; alternative LAYOUT-002, with a later forward insertion.
- Engineering, performance and machine-interface approval: pending.

## Primary geometry and deliberate adaptations

**FACT:** official k4geo e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb turbine v03
uses three wheels with actual blade radial intervals410–764.260mm,
774.260–1460.235mm and1470.235–2790mm,49degree tilt,384/720/1360 periods,
1.3mm inner lead/electrode thickness and increasing lead thickness across each
wheel. Radial support tubes occupy the intervening10mm strips. Nominal XML
400–2750mm is not the full constructed blade envelope. Readout has10/14/34
radial bins and10 axial bins, giving601600 combinatorial addresses per side;
this is a grid count, not a qualified installed electronics bill. Source
calibration subdivisions5/1/1 are not universal longitudinal shower layers.
Different older papers use different wheel counts/angles and are not combined.

**NODD DESIGN CHOICE:** retain actual wheel/period geometry, sampling depth450mm
and source electrode thickness. Adopt0.2mm total steel (100um per face) and0.1mm
total glue, explicitly distinguishing mechanical precedent from the thinner
simulation cladding. Own tilted-face/annular geometry is implemented without
importing the external GPL factory or FCC software. Any planar taper convention
and virtual readout boundaries must be declared rather than presented as an
identical reproduction of ALLEGRO full simulation. Canonical positions, complete
wheel counts and positive gaps are required; a silently omitted wheel is failure.

## Cryostat, electronics space and HCAL interfaces

**NODD DESIGN CHOICE:** reserve800mm between the barrel warm end4100mm and
endcap warm front4900mm for cryogenic bends, connector/tool access and cables.
Sampling starts5010mm and ends5460mm. A250mm rear bath contains existing rear
support allowance (10mm gap plus30mm support), three35mm provisional cold-board
banks, heat-spreader/22mm-pipe allocations and access. Front/rear closures are
100/150mm. Package back5860mm; rear routing gap500mm places HCAL front6360mm.
The front closure preserves50mm Al-equivalent wall material with50mm vacuum;
rear preserves100mm Al-equivalent material with50mm vacuum. These explicit
dewar proxies and split thicknesses are not a pressure-vessel or thermal design.

The cold bore/outer radius are400/2800mm. Inner radial closure has25mm cold,
49mm vacuum and25mm warm material, giving301mm warm bore. Outer closure has
50mm cold,49mm vacuum and50mm warm material, giving2949mm warm outer radius.
Supports, absorbers/electrodes, active gaps and passive baths have distinct
owners. The expanded rear bath and external corridor must contain board/pipe
reservations separately from actual installed material. Wall ports, seals,
headers and hydraulic/thermal/load qualification remain open.

Retain the steel/scintillator HCAL sampling thickness1495.9mm. Its barrel starts
at3130mm apothem, ends at4625.9mm apothem and extends to|z|5860mm, wrapping the
LAr endcaps while leaving an external routing annulus. HCAL endcaps start at
6360mm, end7855.9mm, retain300mm aperture and4615.9mm outer apothem (10mm
corner/seam convention from DES029). These are new envelope choices; associated
mass, iron/field response and structural interfaces need reassessment.
Circular LAr radii and polygon HCAL apothems must remain distinct.

## Forward region and response limits

**INFERENCE:** for IP rays, r=z/sinh|eta|. At eta4 the sampling front/rear radii
are approximately183.58/200.08mm, far inside the410mm first wheel. Larger z
positions do not make this a continuous forward calorimeter. The tilted-plane
constraint ri>=450/(2tan49degree)=195.59mm and positive-gap checks prevent
simply removing the inner support/hole to claim eta4.

**NODD DESIGN CHOICE:** show a technology-unassigned forward EM collar
r80–450mm,|z|4400–4850mm and an empty FCal insertion reservationr80–290mm,
|z|4850–7855.9mm. These are prospective interfaces only, not physical calorimeter
or active acceptance. Beam pipe currently ends at4m; downstream machine/pipe,
shielding and containment constraints are unresolved. Even eta4 at the rear
reservation edge has only a few millimetres radial margin, so do not advertise
the reservation as a qualified eta4 detector.

Native signed eta/phi finite-volume/material scans, actual wheel/readout counts,
raw-ID and canonical-cell references, full overlaps/containment and sparse saved
Geant4 hits are required. Envelope fractions, calibration subdivisions and
readout addresses are distinct from efficiency, shower containment, noise,
resolution, jets or particle-flow performance. Retained3T is the inner-coil
target from PR64; source2T field is not copied and enlarged HCAL needs MagSys
reassessment. Production remains unchanged. Add this candidate to the layout
main page alongside LAYOUT-001 with concise status and reproducible RZ input.
