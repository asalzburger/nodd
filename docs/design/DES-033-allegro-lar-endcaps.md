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
1.3mm inner total absorber and1.3mm electrode thickness and increasing lead thickness across each
wheel. The source driver subtracts0.1mm glue and0.1mm steel from that absorber
value, leaving1.1mm inner lead. Radial support tubes occupy the intervening10mm strips. Nominal XML
400–2750mm is not the full constructed blade envelope. Readout has10/14/34
radial bins and10 axial bins, giving601600 combinatorial addresses per side;
this is a grid count, not a qualified installed electronics bill. Source
calibration subdivisions5/1/1 are not universal longitudinal shower layers.
Different older papers use different wheel counts/angles and are not combined.

**NODD DESIGN CHOICE:** retain actual wheel/period geometry, sampling depth450mm
and source electrode thickness. Retain1.1mm lead core after the source glue/steel subtraction.
Adopt0.2mm total steel (100um per face) and0.1mm
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

## Physical approximation and cold services

**NODD DESIGN CHOICE:** lead thickness varies linearly in local Cartesian
radial x within each tilted blade, rather than cylindrical radius rho. Sampled
maximum thickness differences from the latter intent are recomputed in the
source-bound validation inventory
for inner/middle/outer wheels; this is an explicit approximation, especially
for the inner wheel. This independently written physical model is ALLEGRO-style,
not a byte-identical reproduction of the external factory. Faces have positive
sampled LAr gaps, recomputed after the lead/cladding amendment, with circular clipping and conserved
annular partition. Axial volume quadrature refines to64–128 slices with2e-9
relative convergence. Source5/1/1 calibration compartments are distinct from
our virtual radial×axial readout grids.

**NODD DESIGN CHOICES:** each rear bath begins with10mm LAr access then30mm
Al-equivalent rear support. Three35mm board planes with10mm gaps follow.
Six radial rows of350×75mm faces,5mm radial gaps and80mm tangential pitch fit
16 wedges, with1/3/5/6/8/10 slots per row per wedge. This gives528 slots/plane,
1584 per endcap, or811,008-channel slot capacity at the hypothetical512 channels
per CFEB. Material-filled PCB/Cu/silicon-package/Al-spreader proxies represent
all slots conservatively; a selected ASIC, package/HV connections and cold
thermal contact are not engineered. Installed readout has601,600 geometric
cells;650,000 planning channels govern the external cable allowance.

Each endcap has48 radial18mm-ID/20mm-OD N2 branch proxies, separated axially
from boards. The remaining bath permits access and headers, but headers, wall
penetrations/seals and a valid hydraulic return circuit are not implemented.
All service daughters displace bath LAr explicitly, including nested wet-board
envelopes. The effective N2 density0.02g/cm3 is the common nODD mass choice;
no temperature/quality equation-of-state inference is claimed.

**INFERENCE / unresolved scenario:** with all811,008 slot channels powered,
20/40/60mW/channel gives16.22/32.44/48.66kW per endcap. The48.66kW case
exceeds the provisional40kW/endcap cooling allocation before static heat.
The650k cable budget, board spare capacity and source120kW barrel scenario
must not be confused with a qualified electronics/cryogenics bill. Common
cable/fibre/HV/power estimates, warm-cable comparison, bend-radius and adverse
power cases are defined in DES032 and shared services.json.

## Forward and transition geometry interpretation

**INFERENCE:** the actual sampling envelopes admit any intersection roughly
1.348<|eta|<3.284; full axial-depth annular containment requires approximately
1.424<|eta|<3.198. Radial10mm support strips and turbine faces still change
the active path; these envelope bounds are not efficiency thresholds.
The barrel's full radial depth ends around|eta|1.204, while any barrel
intersection ends around1.350. Thus the barrel/endcap transition contains
partial-depth directions despite an almost touching envelope intersection
range. It needs a later response/material design; the800mm routing gap
does not establish seamless calorimeter depth.

**INFERENCE:** HCAL sampling/cover envelope volume grows from224.78 to432.76m³
for the barrel (×1.925), and from66.49 to101.01m³ per endcap (×1.519) versus
LAYOUT-001. The total outline grows×1.774. These16-gon calculations retain
the same1495.9mm depth and300mm endcap inner apothem; they are size/load
indicators, not an installed HCAL mass or strength prediction. A detailed
HCAL cassette count, material, support and complete field solution is pending.
