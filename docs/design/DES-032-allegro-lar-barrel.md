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
solenoid proxy. Keep ALLEGRO's material proxies explicitly identified. The physical prototype adopts0.1mm steel per face (0.2mm total), following
the published cold-test baseline rather than the thinner XML proxy. This is an
explicit **NODD DESIGN CHOICE**: fixed radius/count/angle reduce the initial
gap to approximately1.196mm per side. The PCB
proxy omits actual patterned electrode metallization, so realistic response and
its material amendment remain open. No published22X0 or resolution is transferred
without a native scan and response validation.

**INFERENCE:** plane path length follows intersection of a straight line from
the inner cylinder at the selected inclination with the outer cylinder:
`L=-r0*cos(alpha)+sqrt(r1²-r0²*sin²(alpha))=573.937151mm`. The tabulated segment
sum573.9371mm differs by only0.000051mm; a named final-segment remainder closes
the boundary rather than overlapping it. The thinner source-XML steel control gives an initial
single LAr gap of approximately1.246mm. The adopted0.2mm steel prototype
gives approximately1.196mm per side, growing outward. Newly generated
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
The axial warm half-length is4100mm. Warm30mm/vacuum49mm/cold3.8mm end layers
and107.2mm cold access/bath at each end leave3910mm sampling half-length. The
rear bath is enlarged to170mm to contain the120mm H-ring precedent, two35mm
cold-board banks and a separate exchanger lane, including corner clearance for
flat sector grids. The warm outer radius is2830mm. These are new nODD choices,
not an ALLEGRO mechanical qualification.

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
volume IDs and prototype factory remain isolated from production. Source path endpoints define named annular compartment boundaries in this
prototype. This is an explicit NODD segmentation-boundary convention; exact
annular clipping preserves plate/gap ownership without claiming the source
factory's segmentation implementation. Cells group
two neighbouring electrodes in phi and use the pinned10mrad-scale theta grid
with fourfold-finer layer1 strips, extended to the nODD axial extent. Raw parent
volume IDs stay distinct; any grouped-cell mapping must declare its canonical
volume/reference point and prove every reported reference lies in active LAr.
The source theta origin may be retained with a signed12-bit index, explicitly
handling negative bins in the longer nODD barrel; it must not reuse the source
unsigned10-bit field. Channel counts are derived from the constructed boundaries rather than rounded
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

## Service packing and amended HCAL interface

**FACT:** SRC-ALLEGRO-COOLING-20250714 p7/p9 provides a studied H-ring
120mm radial height,100mm axial width,12mm flanges,20mm web and500mm spacing.
Page44 supplies a350×75mm CFEB footprint and a120kW/1.07kg/s nitrogen study
with18mm-ID exchangers. Page20 excludes global cooling. These are R&D
precedents. SRC-ALLEGRO-READOUT-20260129 p11 distinguishes warm millions of
analog cables from cold electronics; its ASIC analog power is not whole-chain
power. SRC-ALLEGRO-FEEDTHROUGH-202509 p38 describes20k-wire R&D feedthroughs,
not installed nODD vacuum flanges.

**NODD DESIGN CHOICES:** use16 aluminium-equivalent H-rings at500mm pitch,
two35mm radial CFEB banks in16 sectors,350mm axial board length,75mm
tangential width,80mm column pitch. Fifteen board rows fit *between* the100mm
rings; end-bath slots turn boards tangentially. This provides5760 rear slots
and128 end slots,5888 total. At the explicitly hypothetical512channels/board,
capacity is3,014,656channels, above the3million planning allowance and the
2,285,568 physical-grid-derived channels. The radial/end-bath mother
volumes retain LAr after daughter displacement; individual CFEB envelopes are
wet, not fictitious air boxes. PCB,0.105mm equivalent Cu, eight20×20×1mm silicon
package proxies and5mm Al spreaders represent material only. ASIC selection,
electrode metallurgy, connectors and thermal coupling remain unresolved.

**NODD DESIGN CHOICES:**96 cooling half-branches use18mm bore/20mm OD tubes
at radius2735.3mm. Effective two-phase N2 density0.02g/cm3 is a provisional
mass hypothesis, not a pressure/temperature equation-of-state result. Branch
headers, cryostat ports, seals and manifolds are absent. The170mm rear bath
permits rings, flat-board corner radii and a separate pipe lane; tube materials
displace the parent LAr exactly. The cold test's0.2mm total steel is retained
separately from the source XML0.1mm proxy.

**INFERENCE with planning assumptions:** cold cable counts per barrel station
are92 data pairs,92 fibres (including100% spare fibres),12 HV,4 power,2 grounds
and4 controls. Bundle diameters2.5/2/3/12/8/3mm and40% fill are choices.
Each station also reserves two80mm N2 jackets and two25mm warm-water pipes.
At32 barrel stations the ordinary footprint is31,104mm², within a700×150mm
lane. One utility station at each end additionally reserves four100mm LAr
fill/return/purge/relief jackets:109,644mm² within1100×150mm. An endcap's
16 stations require30,199mm² each, with analogous utility reservation. Packed
area includes pipe jackets and installation void; it is not copper area.

A20m cable length per barrel station gives58.9km of data-pair cable,58.9km
of fibre,7.68km HV,2.56km power,1.28km ground and2.56km controls. Per endcap,
12m/station gives7.68/7.68/3.84/0.768/0.384/0.768km respectively. These are
route budgets with±50% length uncertainty; packed cable volumes are2.25m³
for barrel and0.50m³ per endcap. Boards have capacity, but no installed cable
routing graph or feedthrough bill is claimed. A warm analog alternative
(1.2mm cable per channel) needs265,072mm² per barrel station for3million
channels, exceeding this cold-option lane. It is not interchangeable without
redesign.

**INFERENCE:** service centres atR3029mm clear the endcap's2949mm outer wall
by20mm for100mm utility jackets. Minimum bend radius4×OD and20mm installation
clearance give an approximately740mm axial S-bend for100mm pipe and470mm
rear turn. Thus reserve800mm before the endcap and500mm behind it, rather
than the SiW's small installation gaps. External lanes are empty reservations;
wall penetrations and cryogenic connections are not modelled as valid routes.

**NODD DESIGN CHOICES:** move HCAL barrel front apothem to3130mm, retain
1495.9mm sampling/cover depth, extend barrel half-length to5860mm. Its outer
apothem is4625.9mm (16-gon corners reach farther). Endcap front is6360mm,
back7855.9mm, inner radius/apothem300mm and outer apothem4615.9mm. The
barrel–ECAL corridor is300mm at barrel outer wall2830mm; beside the LAr
endcap it is181mm wide. Both800mm front and500mm rear endcap gaps are
reserved for cable/pipe bends and access. These are HCAL envelopes only;
cassette counts, structural mass, showers, field/return-steel and corner
interfaces require the detailed HCAL follow-up. The enlarged iron must be
included in a new complete magnetic solution before claiming3T operation.

**INFERENCE / scenarios:**20/40/60mW whole-chain power per planning channel
gives86/172/258kW for3million barrel plus650k per endcap. Source120kW barrel
plus a new40kW/endcap allowance gives200kW planning cooling, and a purely
proportional1.783kg/s nitrogen flow. The258kW adverse case exceeds200kW by58kW (29%); fully populated
barrel slots need180.879kW at60mW and120.586kW at40mW, exceeding
the120kW reference even before bath heat. These are unmet scenarios.
No hydraulic proof or bath-static heat budget is implied. Conversion is
provisionally warm; locating90%-efficient converters cold would add13.3kW
for120kW delivered power and requires a new cooling allocation. Chip proxies
and spreaders do not implement a qualified thermal contact. A48V,90%-efficient barrel supply at120kW gives86.8A per
station; a40m room-temperature supply-plus-return loop (20m one way) with two parallel25mm² Cu conductors
has1.19V drop and103.7W dissipation. The assumed3million channels at the source maximum50k hits/channel/s and
a chosen64bit/hit payload need9.6Tbit/s before overhead/compression;4096-channel
aggregation needs13.1Gbit/s. The4×5Gbit/s electrical and2×10Gbit/s optical
capacity hypotheses need protocol, radiation and cryogenic qualification.

All values and arithmetic are reproducible through
[services.json](../../tools/lar_calorimeter/services.json) and
[services.py](../../tools/lar_calorimeter/services.py). Source parameters,
new choices and uncertainty remain separate. No new external software is
adopted; k4geo is read as a public parameter reference, not imported.

## Executed prototype checks

The native isolated barrel with supports/boards/pipes has252.508t total model
mass; this is a material ledger with equivalent walls/PCB/packages, not a
fabricated mass prediction. All33,792 raw sensitive IDs,2,976 canonical
reference keys and2,285,568 logical channels were checked. Full ROOT overlaps
at10nm found zero;45 fixed eta/phi rays traverse actual native boundaries.
The eta0/phi0 ray has22.639X0 across the entire isolated package, including
passives; it does not establish a universal22X0 sampling depth or response.
Saved Geant4 hit checks, executed source identities and review findings are
recorded in the validation report. Combined detector overlaps, forward
response, field and production/ACTS integration remain open.
