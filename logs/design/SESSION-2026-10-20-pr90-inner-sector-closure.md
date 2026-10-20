# SESSION-2026-10-20-pr90-inner-sector-closure

User requests addressing PR90 comment6285814869: why inner-wheel sectors do not close up, can we achieve that? Starting clean15015d378b5b77b3bb11698809d1680d12b8a91c, codex/muon-chamber-layout, PR head matches. Study requiredBTslots versus full-length trapezoid excess gaps. Existing geometry/maps/OBJ/native evidence remains immutable. Use nodd-design-evidence/nodd-coordinate/review-validation with explicitfallback role mandates; no native profile or human approval claim.

## IC-M1 before dispatch

{
  "input_revision": "15015d378b5b77b3bb11698809d1680d12b8a91c",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/wheels.py",
    "tools/muon_layout/wheels-config.json",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/support.py",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/wheels-2026-10-20/xy-sections/sections.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "id": "IC-M1",
  "role": "MuonTech",
  "task": "Assess PR90 comment6285814869: why inner-wheel sectors do not close up, can we achieve closure? Current inner12 full-length affine-gap trapezoids at abs(z)6.7456,500mmdepth,bore0.7/Rvertex5.45. Magnets/frame/HCAL/depth/50mmclearance fixed. Distinguish unavoidable BT-leg slots (local u4.35..4.85,abs(v)<=0.3 with50mmclearance) from excess triangular gaps forced by one whole trap per sector. Investigate concrete two/three radial-band simple trapezoid option,12sectors per band,20mmseams, with no overlap/coil/support conflicts. Derive bounds using actual rotated source boxes, not radial-radius approximations. Use existing10mmcertification margin. Current contract forbids radial tiling: any alternative must be explicitly unadopted feasibility concept, not replacement geometry or ACTS performance. Need source-based dimensions/count/family tradeoff, fullvolume proof strategy, actual scratch checks and limits. Scratch only /private/tmp/pr90-IC-M1-*. No repo/dependency/source edits, nestedagents, externalmessages or approval.",
  "deliverable": "Bounded MuonTech report/JSON with concrete optional packing recipe and physically required versus avoidable gaps.",
  "completion": "Root can explain why, complete-closure boundary, and reviewable recovery tradeoff without adopting it."
}

## IC-A1 before dispatch

{
  "input_revision": "15015d378b5b77b3bb11698809d1680d12b8a91c",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/wheels.py",
    "tools/muon_layout/wheels-config.json",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/support.py",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/wheels-2026-10-20/xy-sections/sections.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "id": "IC-A1",
  "role": "SysArch",
  "task": "Independent fixed-interface assessment for PR90 comment6285814869. Prove physical BT occupied slots across innerwheel depth and whether full azimuthal closure can exist with unchanged magnets/frame/HCAL/depth. Quantify 50mm clearance versus actualwarmboxes and10mmextra margin, axial gap HCAL6.4412/wheel6.4956..6.9956/ECT7.05. Need exact occupied witness showing no-gap trap intersects BT, constraints for closing outer circumference, and source-derived sufficient radial-band boundaries. Do not invent filled annular cryostats. Assess support/barrel conflicts and one-whole-trap restriction; root/MuonTech explore optional threebands. This is feasibility only; no current geometry changes or engineering approval. Scratch only /private/tmp/pr90-IC-A1-*. No repo/dependency/source edits, nestedagents or externalmessages.",
  "deliverable": "Exactrevision SysArch report/JSON with physical witnesses, actual bounded checks, limitations and constraints.",
  "completion": "Physical impossibility/tradeoff boundary independently clear; no detector change or human approval inferred."
}

## Input evidence and feasibility views

IC-M1at15015 complete: portablemodulecalculation/reportsretained. FullvolumeECT/BTplanes+all12rotatedclearanceboxSAT,484supportsat50mm/1320otherchambers andalloptionpairs pass. OccupiedandnaiveR-to-u boundnegativefixturesrejected. CurrentXYfootprintstoactualcorners≤6.14e−11m.1,048,576commoniiddirections(seed409090) agreewithanalyticwholedepthlosses within1.34sigma.2bandoption24/end2families/area77.5533m²/geometricfull-depthloss19.1703% vs12/1/63.1668m²/30.1538%current.3slotdiagnostic36/end3families/78.6884m²/27.9720%, outerspan0.410664<0.50m: notadmissibleundertheminrule.2bandlowercassette3.350m needs explicitcap/tilingamendment; noneadopted.4thrawdiagnostic3splitinnerretainednotheadline.

IC-A1source15015independentlyproveslocalBTwarm[4.35,4.85]×±.30and50mmreserved[4.30,4.90]×±.35 throughout500mmwheeldepth.20mmseamcounterfactualcontainsBTwitness(4.6,.1,z)at6.4956/6.7456/6.9956. Axialslotallowscentre6.7412..6.7500 only. Conservative3bandexample34848support/76032barrel/2556pairSATpass but0.336875mouterbandhaszeroIPraydoublefacecone; exactrotated-planeboundexample0.436875mouterbandstillfails0.50min. TheseareseparaterecipesfromMuonTech0.410664m, notcontradictorysamecase. Source/checks/reportsportableandretained; no humanacceptance.

Beforeviewimplementation, DES040andstudypagerecordoptional2band/3diagnosticrules,classificationsandlimits. Newinner_closure_views.py usesretainedcheckdimensions andSHA-guardedcurrentphysics, outputsseparatedisplaypolygons/PNG/SVG/provenance only. BothPNGsrootvisuallyinspected, labelcontrastfixedbeforefreeze. Comparisonclearlylabelsunadoptedandfailedminspan; planarareaandfull-depthraylossdifferentdenominators, noACTS/efficiencyclaim. NegativeclosinggapfixturefailsBTcertificateasexpected.350oldscientific/sourceblobsexactlyunchanged; onlyoldindexappendlinkandDES040unadopted-studycontractarechangesoutsidethenewdirectory.

InitialassignmentJSwrapperhadsyntaxerrorbeforeanymutation, retriedsuccessfully. Nodepreflightagainwarnssetup/lockfingerprints; warnedbeforefreshsetupverification andplottingruntimeNumPy2.5.4/Matplotlib3.11.2. Nonfatalsysctlrestriction; cachesprivate/tmp. NoACTStransport/build/source/shareddependencychanges.
