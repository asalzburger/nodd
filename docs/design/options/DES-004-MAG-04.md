# MAG-04 — Outer solenoid with instrumented iron return

- Date: 2026-09-17; status: DRAFT, unsigned candidate assessment.
- Parent: [DES-004](../DES-004-magnetic-configurations.md).
- Recommendation: retain as the built-topology comparison; compare changed return
  paths, station allocations and outer radius before detailed chamber layout.

## Evidence and physical benefit

**FACT:** SRC-CMS-JINST-2008 §2.1/PDF33, Table2.1/PDF35 describes the CMS
solenoid and return structure. SRC-CMS-YOKE-COSMICS-2010 §§1–2/PDF3–5 and
SRC-CMS-FIELD-MAP-2023 §§1–2/PDF2–3 establish operational measurement and
geometry-dependent field modelling in the iron/air system. These support the
architecture, not a scale copy or automatic standalone momentum performance.

**INFERENCE:** placing the coil outside central ECal/HCal avoids an inner-coil
material boundary before barrel shower measurement. An instrumented return can
supply additional bending, absorber/filtering and mechanically supported chamber
gaps. Its scattering, energy loss, saturation and alignment costs must accompany
that benefit. Adding steel does not automatically improve a muon fit, and energy
absorbed in uninstrumented return steel is not recovered calorimeter energy.

Shared arithmetic record: [option screen](../../validation/DES-004-option-screen.json).

## Space and flux screen

**NODD DESIGN CHOICE — proposed:** start from MAG-03's R=4.5 m, half-length
6.5 m diagnostic coil and possible assembly r=4.3–4.8 m, half-length 6.8 m;
renormalize current after solving the return geometry. Its envelope amendment
moves the inner muon host to 4.95 m. Keep all central endcap calorimeters inside;
the detached forward calorimeter remains outside.

**INFERENCE — deliberately crude diagnostic:** approximate bore flux by a
uniform 3 T over radius 4.5 m: `Phi = 3*pi*4.5² = 190.85 Wb`. Assigning all
that flux to the annulus 4.95–6.762 m gives area 66.67 m² and average return
field **2.86 T even if the annulus were solid iron**. Chamber gaps, supports and
services reduce available steel. This warns against the old fixed host; the enlarged request below supplies
trial return slots. It is not proof of saturation or
a solved minimum thickness: actual bore flux is nonuniform, some return lies in
air, and calorimeter steel redistributes it. No B–H curve or allowable steel
field is selected by this arithmetic.

**Showstopper for an unchanged envelope:** the proposed outer-coil assembly
already occupies the existing 4.35 m muon-host entrance. A return-plus-chambers
arrangement cannot be declared to fit by drawing it inside an unchanged host.
An explicit amendment resolving that coil/host conflict is required. The full
return may require larger radius, changed return paths or changed station/gap
allocations; the flux screen does not choose between them. This is not a
showstopper for the topology itself.

## Cross-system uncertainties and next decision

Tracker performance benefits from the longer field region only after transport
and measurement studies. Forward standalone muons need actual endcap steel,
radial field, station gaps and apertures; nominal barrel return field says little
about eta 3–3.5. Endcap return/support cannot silently consume the service and
forward-calorimeter interfaces. Calorimeter steel changes the field even inside
the coil; its effective mixtures are not a validated magnetic medium.

Produce one coarse barrel/endcap plate-and-gap allocation with source-backed
steel B–H data, masses, service exits and station coordinates. Solve nonlinear
fields and compare useful bending with scattering using common fit assumptions.
Then vary outer radius and plate/gap allocation explicitly. Geant4 leakage and
punch-through follow separately. Advance MAG-04 if useful standalone information
survives those material and envelope costs; otherwise retain it as a control,
not the default because CMS used the topology.

No detector construction, nonlinear field or fitted performance was run here.

**Current host request:** barrel r=4.95–10 m, |z|≤9 m;
stepped endcap: upstream r=0.4–4.8 m, |z|=6.95–9 m;
wide r=0.4–10 m, |z|=9–10.9 m.
[Budget](../inputs/DES-004-muon-envelope-amendments.md),
[PNG](../figures/DES-004-mag-04-muon-envelope-rz.png) /
[SVG](../figures/DES-004-mag-04-muon-envelope-rz.svg). Unsigned; baseline issue after selection.
