# SESSION-2026-10-13-layout002-lar-endcaps

Human requests two LAr alternative PRs and LAYOUT-002 on the layout main page.
This second branch contains endcap/turbine and complete candidate integration,
stacked on the barrel core879e836. First branch continues services/evidence and
will be normally merged into this branch before final PR review. Root retains
SiW LAYOUT-001, inner3T target and no muon system; forward coverage is marked
uncovered with a future FCal reservation. No new externals or human sign-off.
Current exact root/child counters unavailable; usage empty/unknown.

Primary-source and read-only SysArch/PhysVal handoffs are curated in the barrel
journal, with explicitly new gap/bath/envelope adaptations in DES033. Prototype
endcap source geometry facts are read independently from official k4geo e1ba7bc3
and actual primary publications; no external factory is imported.

Native role loading not claimed. Implementation contract follows below before
dispatch. Root owns endcap services/scalar config, DES/ADR/layout pages, project
records and publication; SoftEng owns only new model/export/factory/tests/audit.

## Prepared bounded implementation assignment

{
  "id": "LAYOUT002-SoftEng-endcaps",
  "role": "SoftEng",
  "input_revision": "de6ea8ce555bc541feb5b5540829a4b9e2f01eda",
  "inputs": [
    "docs/design/DES-033-allegro-lar-endcaps.md",
    "tools/lar_calorimeter/endcaps.json",
    "tools/lar_calorimeter/barrel_geometry.py",
    "tools/lar_calorimeter/barrel_export.py",
    "prototypes/calorimeter/LArBarrel.cpp"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/lar_calorimeter/endcap_geometry.py",
    "tools/lar_calorimeter/endcap_export.py",
    "tools/lar_calorimeter/endcap_native.py",
    "tools/lar_calorimeter/test_endcap.py",
    "prototypes/calorimeter/LArEndcap.cpp",
    "prototypes/calorimeter/CMakeLists.txt"
  ],
  "task": "Implement isolated DES033 turbine LAr endcaps in this separate worktree, using physical3wheel/384-720-1360 tilted plate periods, actual410-2790 radial blade bounds,49degree tilt,450mm depth,1.3mm inner lead/electrode,0.2totalsteel and0.1glue. Keep three wheel support strips, source lead taper architectural intent and real positive LAr gaps (no uniform sensitive envelope substitution). Own geometry, not imported/copied externalGPL source/factory. Pinned public source XML/driver in /tmp/nodd-allegro-source may be inspected for facts. One feasible own representation is convex tilted-face Arb8/intersection with radial annulus and z bounds; analytic capacities from integrating exact circular polygon cross-sections with a documented convergence check, never ROOT stochastic capacity as exact evidence. If planar taper uses local radialcoordinate rather than true cylindricalr, declare and quantify that NODD approximation; do not silently claim identical source fullsimulation. Need allphysicalwheel/plane/gap IDs, logical10/14/34 radial by10axial mapping (~601600gridaddresses/side), canonical inside-gap references and bound tests. Calibration geometry5/1/1 and readout10z are distinct; physical subdivisions may be virtual if explicitly identified. Use properdet+1 rotation for negative side, no negative-z reflections. Genericpassive(parent_name/exclusive/displaced accounting) protocol compatible with barrel helper so root can append rearboard/support/pipe daughters. Root owns scalarconfigs, services, pages,records. Explicitwarm/vac/cold enclosure front4900/back5860, sampling5010\u20135460, rearbath250mm; do not fill empty externalrouting/FCal reserves. EmptyPhi gaps/supportlosses are physical, noeta4/performance acceptance. Nativevalidator should audit actual primitive/CSGvertices/circlebounds/depths/poses/materials/composition, analytic mass, allrawIDcount, readoutreferenceinverseandboundaries, seededfull10nm overlaps and signedeta/phi material/LArpaths. Need source/tool/config hashes and actual mean vs support material separated. No native jobs/compilation (root runs), no commits/push/PR, no newdeps/install and noagents. Standard-library negative controls and export allowed. Coordinate early on shape/readoutschema. Known barrel C++ firstcompile failed ambiguousSegmentation base; root fixed with dd4hep::DDSegmentation::Segmentation alias in parent branch and will merge fix later, qualify your bases explicitly. Target your ownendcap library so stale parentcpp does not block independent source checks. Return exact bounded handoff.",
  "deliverable": "Owned endcap model/export/factory/native/test files, physical/readout semantics, source approximations and actual standard checks; root handles services, runtime and PR/main-page integration.",
  "completion": "Completewheel counts and positive physicalgaps, actual nativeaudit inputs/mass logic/readout cannot be replaced by broad envelope assertions. Report geometry/cell/representation blockers early; no engineering or response acceptance."
}

Root ordinary parent merge of5f8c505 produced a tracking-only conflict.
Resolved by stable task/document/PR IDs, preserving the parent review records
and separate DES033 task/document; no history rewriting. SoftEng returned six
owned files, nine tests passed and explicit Cartesian-taper/readout limits.
Root compiled the endcap plugin and actually ran the complete endcap including
cold services:9856raw IDs,1,203,200logicalcells,139.557395t,zero10nm overlaps.

The newly authored bath-accounting test initially used a seven-decimal absolute
comparison for6e9mm³. It failed on6.68e-6mm³ floating summation difference,
about1.1e-15 relative. Corrected that new assertion to1e-12 relative, stricter
than the existing1e-10 mother-conservation gate; no established physical gate
or overlap tolerance changed. The actual failed check remains recorded.

## Prepared SysArch endcap review

```json
{
  "id": "LAYOUT002-SysArch-endcap-review",
  "role": "SysArch",
  "input_revision": "44ddd54aef096cff9d019dd6b9ee55c06f7b9d7b",
  "inputs": [
    "docs/design/DES-033-allegro-lar-endcaps.md",
    "tools/lar_calorimeter/endcap_geometry.py",
    "tools/lar_calorimeter/endcap_services.py",
    "tools/lar_calorimeter/endcap_native.py",
    "prototypes/calorimeter/LArEndcap.cpp"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review the exact committed endcap implementation and service/material/readout/forward/interface claims under your existing profile. Also inspect remediation of your previous barrel findings at exact parent5f8c505e26f0f325f17d801583042849f06f62a2. SysArch focuses physical placement/service/cable/HCAL/cryostat/forward interfaces; PhysVal on faces/circular capacities/readout/rawIDs/gates/claim consistency and taper limits. Complete endcap native pass observed0overlaps10nm; exact44ddd54 rerun underway. No editing/native jobs/install/signoff/delegation. Return concrete severity findings and actual checks, identify exact revisions assessed.",
  "deliverable": "Read-only exact-revision findings plus recheck of barrel corrections; no human approval.",
  "completion": "Actual defects corrected or bounded engineering/performance limitations retained before ready."
}
```

## Prepared PhysVal endcap review

```json
{
  "id": "LAYOUT002-PhysVal-endcap-review",
  "role": "PhysVal",
  "input_revision": "44ddd54aef096cff9d019dd6b9ee55c06f7b9d7b",
  "inputs": [
    "docs/design/DES-033-allegro-lar-endcaps.md",
    "tools/lar_calorimeter/endcap_geometry.py",
    "tools/lar_calorimeter/endcap_services.py",
    "tools/lar_calorimeter/endcap_native.py",
    "prototypes/calorimeter/LArEndcap.cpp"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review the exact committed endcap implementation and service/material/readout/forward/interface claims under your existing profile. Also inspect remediation of your previous barrel findings at exact parent5f8c505e26f0f325f17d801583042849f06f62a2. SysArch focuses physical placement/service/cable/HCAL/cryostat/forward interfaces; PhysVal on faces/circular capacities/readout/rawIDs/gates/claim consistency and taper limits. Complete endcap native pass observed0overlaps10nm; exact44ddd54 rerun underway. No editing/native jobs/install/signoff/delegation. Return concrete severity findings and actual checks, identify exact revisions assessed.",
  "deliverable": "Read-only exact-revision findings plus recheck of barrel corrections; no human approval.",
  "completion": "Actual defects corrected or bounded engineering/performance limitations retained before ready."
}
```

## Prepared transport/combination assignment

```json
{
  "id": "LAYOUT002-SoftEng-transport-combination",
  "role": "SoftEng",
  "input_revision": "44ddd54aef096cff9d019dd6b9ee55c06f7b9d7b",
  "inputs": [
    "tools/lar_calorimeter/endcap_geometry.py",
    "tools/lar_calorimeter/endcap_export.py",
    "tools/lar_calorimeter/run_transport.py",
    "tools/lar_calorimeter/check_transport.py"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/lar_calorimeter/endcap_transport.py",
    "tools/lar_calorimeter/combined_native.py",
    "tools/lar_calorimeter/test_endcap_transport.py"
  ],
  "task": "Implement bounded reproducible signed-endcap sparse saved-hit fixtures/runner/checker and actual combined LAr ECAL-only native envelope/overlap/ray audit. Retain all3 wheels but one physical period perwheel perend, omit cryostat/services; generate side1/2 fixtures, startmuon inside middle-wheel gap, proper transformed point/direction. Runner bindsexactargv/exit/artifact/sourcehash; checkerrequiresfinished1event, observedseed42/FTFP_BERT, actual savedpositivefiniteenergy IDs with system11/side/wheel/plane/gap/rho/z validconstructedcells, no highunusedbits, requestparticle/energy labeledrequested. Testghostboundaries. Combined toolmerges actualbarrel/endcapcompact inreadout/detector lists withidentical materialdefinitions, loads both factorylibraries, fromXML buildswholeECAL, full10nmoverlap seed43 andsigneddenseeta/fixedphi native rays, activepaths via native sensitive flags (separatelybarrel/endcap). Hashbindcompacts/materials/libraries/model scientificsources. Gatefinite/nonnegativerays, active<=LAr; eta4activezero, no extrapolatedefficiency. Otherdetector/HCAL/field absent. No newexternals/install/nativejobs/commit/delegation; rootrunsevidence. Root owns allotherfiles.",
  "deliverable": "Ownedfiles with standard-library tests/AST and exactCLI, rootexecutesnative/Geant4.",
  "completion": "Correctsignedfixturehitvalidation and boundednativeECAL-onlycombination ready; no production/performanceapproval."
}
```

PhysVal exact44ddd54 review independently integrates24 volumes to1.007e-10
relative agreement and60 native active paths/counts to2.99e-11mm. It found
two P2 corrections: source1.3mm absorber includes glue/steel, leaving1.1mm
lead (driver line114); adopt that lead core with the already deliberate0.2mm
total steel. Recompute all material/ray/transport evidence. Add independent
straight-face/cylinder ray-interval gates, finite/nonnegative and active<=LAr
controls to endcap native PASS. First combined run at the prior lead value
passed0overlaps/405rays; it is superseded, not presented as final evidence.
Initial endcap DDSim run failed1: building only the library target omitted
DD4hep's plugin component map. Build all isolated CMake targets before retry;
no external installation or geometry gate changed.

SysArch exact44ddd54 assessment found no P1 default placement defect;10endcap
and12parent tests pass.139128 board separating-axis comparisons in one repeated
plane findzero overlaps; board corners reach2565.976mm, with6mm clearance to
radial cooling and59mm rear-wall clearance. P2 disposition: explicitly declare
30mm unported full Al rear annulus (1.953598t/end) as a new conservative proxy;
it blocks direct signal/HV routes and has no openings/attachments. This does
not reproduce source rings/spokes or preserve their mass. P3 corrected:
1495.9mm is1485.9mm sampling+10mm cover. All previously identified barrel
corrections at5f8c505 are rechecked by both roles. No design/engineering signoff.

## Actual final execution and visual integration

Corrected endcap source464e3937808e8427f27ad2dcb3bed1bc717cb763:
131.172858t bothends withservices,9856raw IDs,1,203,200logicalcells,zero10nm
overlaps,60 native rays pass independent physical-face/cylinder intervals.
Source1.1mm lead keeps all3 wheels. Taper deviations0.11685/0.03442/0.00968mm,
minimum gaps0.99488/1.15426/1.20102mm. Complete build includescomponentmaps;
both signed sparse DDSim fixtures save one valid positive-energy LAr hit,
with exactargv/source/artifacts and observed42/FTFP_BERT controls.

Ordinary finalparent merge7894524 contains unchanged scientific producers.
Actual complete ECAL-only native audit passeszero10nm overlapsseed43 and405
signed material rays. It excludestracker/magnet/HCAL/FCal/muons/field. Dirty
execution flags refer to ongoing documentation/figure work; perfile scientific
hashes match. All28 standard-library controls pass. Own plots and002RZ were
rendered and inspected; gaps/collar/FCal are explicitlyempty, paired001 preserved.
README/index featurepage, ADR009 and source-pinned JSON supportthealternative.

PR73 isready, mainprojectvalidationandtokensiteCI passedat48e9725.
Currentroot/childusage remainsunexposed, no newcountersestimated or historical
observationsduplicated. The separateendcapjournal preserves assignmentcontracts,
sourcecorrections, actual failures and bounded checks; nohumanapprovalrecorded.

## Prepared final correction recheck

```json
{
  "id": "LAYOUT002-PhysVal-final-corrections",
  "role": "PhysVal",
  "input_revision": "cbb129f1e611909ebe1eb3bfc60f3f3383a8a727",
  "inputs": [
    "tools/lar_calorimeter/endcaps.json",
    "tools/lar_calorimeter/endcap_ray_reference.py",
    "tools/lar_calorimeter/endcap_native.py",
    "docs/validation/DES-033/native.json",
    "docs/validation/DES-033/combined.json",
    "docs/validation/DES-033/transport-positive.json",
    "docs/validation/DES-033/transport-negative.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Narrow recheck of your two previousP2 corrections: source lead1.1mm and actual independentface/cylinder ray PASS gates. Verify retained final geometry/readout/material evidence and sourcehash correspondence; inspect signed savedhit andcombined scope claims. No broad repeat ofpassedtests, no edits/nativejobs/acceptance. Exactcbb129f includes scientific producer464e393 plus normal parentmerge anddocs. Return remaining concrete defects or confirmation of addressed findings and actualboundedchecks.",
  "deliverable": "Fixed-revision review of sourcecorrection andregressiongates, with artifactscope consistency.",
  "completion": "Finalsource corrections assessed, no humanapprovalclaim."
}
```
