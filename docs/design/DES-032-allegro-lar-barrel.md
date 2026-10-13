# DES-032 — ALLEGRO-style LAr ECAL barrel for LAYOUT-002

- Status: **DRAFT**
- Type: **PROTOTYPE**
- Date: 2026-10-13
- Human instruction: prepare an ALLEGRO-style LAr alternative to SiW, enlarge HCAL/service envelopes as needed, retain the separate SiW candidate.
- Candidate: LAYOUT-002; tracker and conditional inner3T solenoid retained.
- Engineering/performance approval: pending; production unchanged.

## Governing reference and retained geometry

**FACT:** SRC-ALLEGRO-K4GEO-2026 pins official k4geo commit
e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb. Its v03 inclined barrel XML defines
sampling radii2172.8–2578.3mm,1536 planes,50.18degree inclination, eleven
longitudinal electrode segments with lengths23.3596,47.5685,48.9843,50.4,
52.0989,53.6562,55.4966,57.3371,59.4607,61.5843,63.9909mm. Absorbers contain
1.8mm Pb, total0.1mm steel and0.1mm glue; electrodes are1.2mm thick. The first
compartment substitutes passive LAr for the lead core. XML definitions and
material recipes are public simulation facts rather than construction approval.
The CALOR2025 paper's rounded dimensions and older turbine geometry must not
be mixed with these pinned simulation inputs.

**NODD DESIGN CHOICE:** retain these sampling radii/plane counts instead of
shrinking gaps to the SiW slot. Replace the SiW technology only within this
separate candidate; retain nODD's inner3T magnet and omit ALLEGRO's outer70mm
solenoid proxy. Keep ALLEGRO's material proxies explicitly identified. The PCB
proxy omits actual patterned electrode metallization, so realistic response and
its material amendment remain open. No published22X0 or resolution is transferred
without a native scan and response validation.

**INFERENCE:** plane path length follows intersection of a straight line from
the inner cylinder at the selected inclination with the outer cylinder:
`L=-r0*cos(alpha)+sqrt(r1²-r0²*sin²(alpha))=573.937151mm`. The tabulated segment
sum573.9371mm differs by only0.000051mm; a named final-segment remainder closes
the boundary rather than overlapping it. A1536-plane period gives an initial
single LAr gap of approximately1.246mm, growing outward. Newly generated
polygons must reproduce real adjacent plate/electrode faces and be checked
independently; the external factory is not imported.

## Cryostat, supports and services

**FACT:** the pinned simulation uses front warm/cold wall equivalents10/3.8mm,
rear cold/warm equivalents30/2.7mm,49mm vessel-gap placeholders on each radial
side, front/rear bath10/40mm and side warm/cold equivalents30/3.8mm. It lumps
walls and a70mm outer coil in its simplified allocation. Source geometry does
not qualify a fabricated vacuum vessel.

**NODD DESIGN CHOICE:** split warm wall, vacuum and cold wall explicitly in
LAYOUT-002, retaining their radial totals and the sampling front. The warm bore
begins at2100mm, then10mm warm wall,49mm vacuum,3.8mm cold wall and10mm front
bath. Rear bath may increase to fit cold boards, heat spreaders and exchangers;
its final ledger is established by the service packing study, before final
geometry export. The ordinary coilless rear radial budget is40mm bath,30mm cold
wall,49mm vacuum,2.7mm warm wall: outer radius2700mm before service enlargement.
The axial warm half-length is3900mm. Warm30mm/vacuum49mm/cold3.8mm end layers
leave3817.2mm half-length for sampling; the explicit vacuum allowance is a new
nODD choice rather than an ALLEGRO mechanical qualification.

Published mechanical/source studies and a separate SysArch assignment inform
support/electronics/cooling and external cable-service reservations. Counts,
channel-capacity, cable diameters/fill, heat margin and route lengths must be
named hypotheses with nominal and adverse scenarios. Separate cold and warm
options; digital multiplexing cannot be assumed free of powering, bandwidth or
cold-heat cost. Physical wall feedthrough engineering and thermal/load proof
remain open. HCAL starts outside the complete allocated cryostat and an empty
external service corridor; retain its original sampling thickness when moving
its envelopes. No new magnetic field solution is implied by changing HCAL.

## Readout and implementation contract

**NODD DESIGN CHOICE:** independently generated polygon/extrusion primitives
represent complete inclined absorber/electrode periods and two active LAr gaps
per electrode per longitudinal segment. Material definition, segmentation,
volume IDs and prototype factory remain isolated from production. Cells group
two neighbouring electrodes in phi and use the pinned10mrad-scale theta grid
with fourfold-finer layer1 strips, extended to the nODD axial extent. Raw parent
volume IDs stay distinct; any grouped-cell mapping must declare its canonical
volume/reference point and prove every reported reference lies in active LAr.
Channel counts are derived from the constructed boundaries rather than rounded
2million source counts. This is readout geometry, not charge transport,
digitization or calibrated calorimeter response.

## Validation requirements and interpretation

Require compact construction; explicit native shape/transform/material/mass
agreement; full overlaps and containment at10nm with a recorded seed; sensitive
and raw-volume ID counts; interior pad/cell reference and boundary controls;
barrel eta/phi material/sensitive scans; saved-hit sparse Geant4 checks; separate
service packing/empty-corridor envelope checks. Retain ignored compact/ROOT
hashes and source/tool/config identities with executed results. Do not report
unexecuted gates as passed. Combined field, full shower response, ACTS conversion,
manufacturing/cooling/structural qualification and forward coverage are separate.

The endcap/turbine and forward insertion are the second PR under DES033. The
LAYOUT-002 main-page status must distinguish barrel-only work from the completed
candidate. LAYOUT-001 remains the separate SiW candidate.
