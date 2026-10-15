# DES-038 — Endcap HCAL from the common readout module

- Status: **DRAFT**; Type: **PROTOTYPE / design proposal**
- Date:2026-10-15
- Human direction: use DES036 common module; separate barrel/endcap PRs.
- Parent:[DES036](DES-036-hcal-common-readout-module.md),[DES035](DES-035-hcal-realism-and-prototype-plan.md),[DES034](DES-034-siw-service-envelopes.md),[packing diagnosis](DES-029-endcap-coverage-repair.md).
- Human engineering owner/sign-off: unassigned/pending. No production integration.

## Governing contract and provenance

**FACT about human direction:** use DES036 as the working common readout module for a14TeV hadron collider and produce separate barrel/endcap PRs. This selects a working design basis; it is not engineering sign-off. Preserve the184mm36tile board and380x240x12mm two-board carrier, including its material, channel, heat and service ledger. Other operating values remain the DES036 planning inputs.

**NODD DESIGN CHOICE — common depth amendment:** retain36sampling layers and30mm steel per layer, the12mm carrier,1mm installation allowance and10mm rear cover. Total depth is36*(30+12+1)+10=1558mm. DES034 allowed1495.9mm. Propose62.1mm more depth rather than silently compress hardware or reduce steel. Even36*(30+12) exceeds the old outline before covers/gaps. Alternatives35layers at1mmgap (1515mm total),36at0.5mmgap (1540mm), or reduced absorber require a separate reviewed sampling/mechanical decision. Existing FCal reservation is unchanged. The steel-only nuclear-interaction screening is inherited from DES035, not a shower-containment claim.

**NODD DESIGN CHOICE — unchanged cell hardware:** no cropped boards/tiles or fictitious continuous sensitive sheet. Source-backed package dimensions/material host and effective proxy details remain DES036. The common carrier has projected tile-core area72*29.7^2=63510.48mm2,69.64% of its91200mm2 face before external packing losses. Report this ceiling; staggerring changes directional sampling but not per-layer area. Regional layouts are analytical design prototypes, not new native whole-detector qualification.

## Endcap face, depth and mechanical grouping

All new dimensions below are **NODD DESIGN CHOICE — unsigned**. Retain frontabsz4883.2mm and polygonapertureapothem300mm; propose backabsz6441.2mm andouterapothem4148mm (bothgrow62.1mm relativeDES034; radialchoice keeps the prior10mm difference fromcompanionbarrel4158mm outercover). TheFCalemptyreservationR80..290,absz4533.2..6379.1 remains unchanged,with no extension or activecoverage claim. Minimumapertureclearance10mm tothatreservation is geometric only. Barrelendabsz4483.2/rearegressbreak400mm are not filled by this design.

Tile the full polygonface with intact380x240 pairedcarriers on a Cartesian grid. Mechanical grouping uses four supported quadrants, independent of16electronicsectoraddresses; do not force rectangles into narrow16wedge outlines. Outer carriercorners must beinside the regular16-gon minus20mm perimeterframe; carriers must not intersect theaperture plus10mm innerframe (exactconvexpolygon/rectangle separation required). No clipped boardsor tiles. Reserve20mm horizontal collectorstrips (gridpitchy260),1mm x-gaps; compare x/y phases to avoid repeating the same narrow board/tile seams. Any quadrantjoint/support strips must beexplicitly modeled asexcludedspace,not hidden in face fractions. Packing algorithm chooses and records quadrant seamwidths before construction. Samehardware andcomparisonmask replicate all36layers; selectedstagger pattern must beexactly specified andvalidated before claiming improvement.

Positiveend localcarrierbasis isglobal(+x,+y,+z). Negativeend usesproperglobalRx(pi),basis(+x,-y,-z), notazreflection. Reflect the wholepositiveassembly including serviceports and IDs; check determinant+1 andsamefacecounts/masses under proper rotation. Layerfrontsteps outward fromIP. Absorber is a singlecontinuous regularpolygonannulus per layer with declaredsector/quarterjointcuts; absorber ownership is independent of electronicsaddresses. Sharedperimeter/apertureframes andbackcover are owned once,neverpercarrier. Materialfullmasses must subtract realholes/strips where cut; emptyreservedservicecolumns are not assumed toremoveabsorber unless configuredexplicitly.

Useall72physicalcores perpair tocomputeactivefacefractions andfirstactiveradius. Reportfull-fiducialdenominator includingframe/seam loss aswellaspackableface denominator. Compare narrower16wedge control andglobalgrid; quantifyeffectiveinnerhole,notjustnominal300mm aperture. Standardpairedcarriers impose69.64% intrinsicfaceceiling and radiation/occupancy constraints; this design must exposeanyremaininginnerandseamblindregions. A laterinner/edgecarrier usingthesameboard couldbecomparedseparately; no silentmanufacture ofhalfboards/shapedscintillator.

## Services, interfaces and validation

Collectorstrips are namedemptyreservations, notinstalledmaterialorproof ofconnection. Transformfourwaterhandoffs/carrier andLV,bias,data,control endpoints; assignquadrant/perimeterhandoffs and aggregatecontinuousheat,stresscurrents,idealwaterandseparateDAQ/triggerlanes. Totals are partiallocalledgers: externalheaders,cables,connectorsandloads excludedexplicitly; no count-derived sustainedthroughput approval. Calorimetrytowardeta4/5 requires distinctforwarddesign: ateta4 rays remaininside the300mm aperture through theseendcaps. Do notextendtheFCalreservationor claim usefulforwarddepthbyassociation.

Require exactwholecarrier containment,polygonapertureexclusion,nonoverlapgrid/supportchecks,propernegativeendframes,identifieruniqueness andcapacity (system9,side1/2,sector0..15,layer0..35,carrier0..4095,module0..1,sensor0..35),sharedmass/absorberconservation andsourcebounddeterministicreport. Activecore IP maps giveper-layer crossings vs eta/phi including inneraperture,quarterseams,outeredge andtransitioneta0.9..1.4. Compareselectedphasesandaligned/narrowwedgecontrols; statefirst/lastactiveplane andpartiallysampledrays. Intersectactualtilecores andeffective recess ratherthancontinuous sheets. Negativecontrols reject olddepth,clippedcarriers,inneroverlap,improperreflection,IDcollision andcount/powerdoubling.

InheritedcommonmoduleDD4hep/Geant4checks proveonlyunitconstruction/smoke. Wholeendcapnativegeometry/transport,shower/digitization,pileup,regionalradiation/EOL,pressure-drop,thermalcontactandmechanicalstress remainlatergates. Analyticalmask/area/depthresults are not particleefficiency or14TeVcontainment. Independentreview follows fixedproposal/code revision. Humanapprove physicalchoices before fullintegration.

## Deliverables

Regionalconfig/layouttool,geometric/faultcontrols,face/section/RZdrawings,sourceboundvalidationreportandtracking accompany thisproposal. SeparatebarrelPR shares theproposedmodule/depthcontract butis independentlyreviewable. Candidatepage must show thisasopenproposal ratherthanreplace selectedroughoutline without approval.
