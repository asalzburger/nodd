# DES-034 - LAYOUT-001 Si-W service and forward envelope prototype

- Status: **DRAFT**
- Type: **PROTOTYPE**
- Date: 2026-10-14
- Human direction: bring LAYOUT-001 service/cooling/HCAL routing and prospective FCal envelopes to the same allocation level as LAYOUT-002; update the central reviewer entry.
- Parent: DES029 layout outline, open Si-W DES030/031; comparison DES032/033.
- Engineering, magnetic and performance approval: pending.

## Scope and evidence

This isolated envelope study retains the open Si-W ECAL package, local sensors,
supports, readout and cooling plates. It adds named external collection, routing,
access and forward reservations and adjusts the rough HCAL envelope to contain
them. It is not a redesign of the cassettes or a detailed HCAL/FCal detector.
Production geometry is unchanged. Source revisions are retained in
[DES-034-sources.json](inputs/DES-034-sources.json).

**FACT:** DES031 records 188.401 kW continuous barrel heat and 9.014 kg/s ideal
water at a 5 K rise, 92,135,424 logical channels, 15,648 shared interfaces and
46,944 local Ti/water pipe runs. It explicitly excludes external headers,
connectors and routed cables and warns that current side/end reservations contain
absorber/support. DES030 provides the corresponding endcap inventory and limits.
These are facts about unsigned earlier prototype choices, not operating approval.

**NODD DESIGN CHOICE:** retain continuous power as the planning case; a low duty
factor is not assumed. Reserve an external route rather than declare existing
material-filled cassette setbacks empty. Define station counts, cable and water
cross sections, bend/access clearances, nominal/adverse scenarios and interfaces
before selecting HCAL bounds. Forward insertion is technology-unassigned and
empty, with no active coverage claim. Quantities and validation follow the
bounded SysArch assessment and reproducible allocation tool.

## External backbone and HCAL interfaces

**NODD DESIGN CHOICES:** reserve a circular R=2.300-2.600 m external backbone
outside the unchanged 16-gon ECAL. Its barrel maximum corner is 2.276951 m,
leaving 23.049 mm. Use 32 barrel stations (16 sectors, two ends) and 16 stations
per endcap under a balanced-routing hypothesis. Existing cassette side/end bays
contain material, and local tubes stop 5 mm inside cold plates: these allocations
do not cut them open or establish a connected local hydraulic network.

Retain HCAL's 1.4959 m sampling/cover depth but move the barrel inner/outer
apothems to 2.600/4.0959 m, and extend its half-length to 4.4832 m, wrapping the
ECAL endcaps. A 400 mm rear break sets HCAL endcap front/back |z|=4.8832/6.3791 m;
inner/outer apothems are 0.300/4.0859 m. HCAL corners reach R=4.176143 m;
full axial length is 12.7582 m. The original 30 mm ECAL front seam is installation
space only. No Si-W package, sensor, cooling plate or placement changes.

**INFERENCE:** routes proceed axially in the annulus beside the HCAL, then turn
radially outward through the rear break to a chosen R=4.300 m handoff. This
avoids requiring a drilled path through active HCAL. A 50 mm external water
jacket at chosen bend radius 4xOD=200 mm needs 245 mm for one 90-degree elbow,
including half-OD and 20 mm installation clearance. The 400 mm break passes this
single-pipe bound and the sampled backbone sweep; it does not prove a two-elbow
S-bend, connector/tool access or all junction bends. HCAL load paths and a
complete field/return-steel solution require reassessment; outline volume rises
x1.241 from the previous LAYOUT-001. These are size indicators, not HCAL masses.

## Cable, water, power and support budget

**FACT about the pinned model:** native role counts include passive shared PCBs.
Barrel 22,560 = 15,648 powered interface chips + 6,912 PCBs; both endcaps 6,144
= 4,608 powered chips + 1,536 PCBs. Exporter locators are retained in the source
catalogue. The powered chips, not the complete role count, govern external links.

**NODD DESIGN CHOICES:** each interface receives four 2.5 mm data-pair paths and
four 2 mm fibres, including spare paths. Each barrel/endcap station adds 12/20 HV
cables (3 mm), four power (12 mm), two grounds (8 mm), four controls (3 mm), and
two 50 mm supply/return water jackets with chosen 25 mm water bore. This is a
conservative digital-export envelope, not a selected Si-W ASIC, protocol,
throughput or cryogenic architecture. Warm analog export is not assumed.

| Allocation | Barrel station | Each endcap station | Merged rear station |
| --- | ---: | ---: | ---: |
| Powered interfaces (balanced hypothesis) | 489 | 144 | 633 |
| Data pairs / fibres | 1,956 / 1,956 | 576 / 576 | 2,532 / 2,532 |
| Nominal packed area, 40% fill | 50,849 mm2 | 23,216 mm2 | 74,065 mm2 |
| Double links, 30% fill | 120,286 mm2 | 46,412 mm2 | 166,698 mm2 |
| Reserved cross section | 900x150 mm | 900x150 mm | 880x220 mm |

**INFERENCE:** 700x150 mm fails the barrel adverse case. Each ordinary lane fits
its sector with at least 20 mm clearance. A joint 900x150 mm would fail the
merged case, so reserve 880x220 mm at R=2.430 m. Its far corner is 2.577829 m;
HCAL clearance 22.171 mm and sector-edge clearance 21.064 mm preserve the chosen
20 mm margin. The wider radial joint fits 193,600 mm2. Area/rectangle bounds do
not demonstrate an installed bundle arrangement or a balanced collector graph;
simultaneous station imbalance and doubled link demand are not qualified.

**INFERENCE / length hypotheses:** 20 m per barrel station and 12 m per endcap
station give 1,251.840 km each of barrel data pairs and fibres, and 110.592 km
each per endcap. This large count exposes the cost of exporting each existing
interface without further aggregation. Length uncertainty is +/-50%, including
paths beyond the detector handoff. Connector/HV counts are planning hypotheses,
not selected bills. Multiplexing/optical alternatives need their own power and
bandwidth assessment; no external package is adopted here.

**INFERENCE from retained power hypotheses:** local ECAL heat is 259.452 kW;
ideal water at 4,180 J/(kg K) and 5 K rise is 12.414 kg/s. Barrel/endcap branch
speeds in the chosen 25 mm bores are 0.574/0.216 m/s. A 1.5x heat scenario gives
389.178 kW and 18.621 kg/s, before pumping/static/environment heat. Source heat
already includes converter losses; they are not counted twice. All 51,552
local coolant runs (103,104 endpoints) still need hierarchical collection,
connections, pressure-drop and thermal-contact design.

**NODD DESIGN CHOICES / INFERENCE:** a 48 V input, two parallel 25 mm2 Cu
conductors per polarity, 40 m supply-plus-return loop and rho=1.72e-8 ohm m give
122.66/46.26 A per station, 1.688/0.636 V drop and 207.0/29.4 W loss. Nominal
external cable loss totals 7.567 kW, additional to local ECAL heat; heat-removal
ownership and warm conversion remain open. Hypothetical feed copper is 0.918 t
at the inherited 8.96 g/cm3 density, and filled external water is 1.005 t under
the length hypotheses. These are partial planning inventories, not native or
installed mass; jacket, other cables, collectors, racks and supports remain
unassigned. Ampacity, temperature dependence and supply segmentation are not
qualified. Current native ECAL masses remain 299.003 t barrel / 98.949 t both ends.

Support ownership is ECAL for cassette collectors/attachments and station
handoffs; HCAL for preserving access around its barrel/endcap supports; common
services for external trays, plant feeds and the R=4.300 m handoff. No support
steel or bearing mass is inserted into the empty reservations. Structural loads,
mounting, isolation, emergency/drain provisions and installation sequence remain
open, as external engineering does in LAYOUT-002.

## Forward reservation

**NODD DESIGN CHOICE:** reserve an empty technology-unassigned FCal insertion
R=0.080-0.290 m, |z|=4.5332-6.3791 m. It begins 50 mm behind the unchanged Si-W
endcap and clears HCAL's minimum circular aperture by 10 mm. It is distinct from
installed calorimeter hardware. Do not copy the LAr upstream collar, which would
intersect this Si-W endcap. A wider future collar would need a non-overlapping
split of the rear break and FCal; no such hardware is selected here.

**INFERENCE:** eta=4 IP rays have r=166.11/233.75 mm at the reservation front/back,
inside those radii. This checks geometric accommodation, not acceptance,
containment, forward shielding or a solution to the Si-W seams. Beam pipe beyond
its current 4 m end, machine clearance, shower depth and FCal supports/services
remain unresolved. No FCal or muon system is installed.

## Reproducibility and scope of executed checks

[inputs.json](../../tools/siw_services/inputs.json) separates inherited facts and
new planning choices; [allocation report](../validation/DES-034/allocations.json)
retains producer/input hashes, area/flow/power/volume arithmetic, corner bounds,
forward intervals and a 70-point single-pipe backbone sweep. Eight negative
controls reject the old 30 mm turn gap, apothem-as-radius clearance, overlapping
sector lanes, undersized adverse/merged lanes, FCal/HCAL intrusion and powered-
interface double counting. The candidate RZ input and SVG reproduce exactly.

These are analytic envelope/packing checks; no DD4hep/Geant4/native combined
geometry, pressure-vessel, cable-routing, load, field or response qualification
is claimed. Existing isolated ECAL native evidence still describes PR70/71.
The retained input values and new derived HCAL bounds are not silently applied
to production or to those standalone component exports.
