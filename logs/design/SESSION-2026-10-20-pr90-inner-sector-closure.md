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

## IC-P1 beforedispatch

{
  "id": "IC-P1",
  "role": "PhysVal",
  "input_revision": "0d7a815fc299c971be1c6af3911c50e9f0a9b585",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/inner-closure-2026-10-20/README.md",
    "docs/validation/DES-040/inner-closure-2026-10-20/review/module-check.py",
    "docs/validation/DES-040/inner-closure-2026-10-20/review/module-check.json",
    "docs/validation/DES-040/inner-closure-2026-10-20/review/interface-report.md",
    "docs/validation/DES-040/inner-closure-2026-10-20/review/interface-check.json",
    "docs/validation/DES-040/inner-closure-2026-10-20/views-provenance.json",
    "docs/validation/DES-040/inner-closure-2026-10-20/display-polygons.json",
    "docs/validation/DES-040/inner-closure-2026-10-20/unchanged-evidence.json",
    "docs/validation/DES-040/inner-closure-2026-10-20/inner-closure-comparison.png",
    "docs/validation/DES-040/inner-closure-2026-10-20/bt-clearance-detail.png",
    "tools/muon_layout/inner_closure_views.py",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independent final scientific/claim/figure assessment at exact0d7a815fc299c971be1c6af3911c50e9f0a9b585 forPR90comment6285814869. You didnotauthor closurestudy/implementation. Primarysourcefirst: current12longtraps fixed BT50mmclearance slots vs unavoidablegeometry; optional2bands24/end2families and3slot36/end3families notadopted. Independently derive full-depthsame-module straightIPsolidangle/planararea fromactualdimensions/bases, checkidealannulusdenominator/borderproxy/seamradialcrossing effects andclaimed30.1538/19.1703/27.9720percentloss. Sourceconstructvalidconvexfootprints; verifynegativewitness20mmseamclosingcollidesactualBT acrossdepth, distinctA1conservativeouterbandzero vsM1optimized0.410664 nonzero clearlylabelled. Reviewactualsourcehashes/polygons/PNG+SVG/provenance,3bandfailsold0.50minimum and2bandrequiresno-tiling/cassetteamendment, no newACTS/efficiency/engineeringclaim. Check350oldscientificsourceGitblobidentities andindexappendexception, DES040onlyunadoptedstudyappend. M1actualfullvolumecoil/SAT and1,048,576commonraybankpassed; A1independentinterfacepassed; no needbroadscientific/ACTSrerun. Usefocusedindependentmath/counterchecks (samplebankifneeded), selectedoccupiedcorner/fullvolumeboxchecks; visuallyinspectbothactualPNGs. Promptmaterialfindings to root; conciseMD/JSON andportablecheckerifneeded scratchonly /private/tmp/pr90-IC-P1-*, no absoluteprivatepaths inretainedoutputs. No repo/source/dependencyedits,nestedagents,externalmessages/approval. Futureeditonlydoclink/logcloseout withdata/sourcebyteproof; thisisFeasibilityQuestionanswer notchosennewcandidate.",
  "deliverable": "Exactrevision independentPhysValreport/JSON and actualfocusedcheck evidence, with findings/limits and no approval claim.",
  "completion": "Numbers, physicalcause/conditionalclosureanswer, unadoptedlimits anddrawings independently assessed; no unresolvedmaterialclaim defect."
}

## Independent IC-P1 outcome and publication preparation

Child contexts: `/root/inner_closure_modules` (IC-M1), `/root/inner_closure_interfaces` (IC-A1), and `/root/inner_closure_validation` (IC-P1). Complete fallback contracts preceded dispatch. IC-P1 did not author the closure study. At exact `0d7a815fc299c971be1c6af3911c50e9f0a9b585`, independent halfspace clipping and Green-theorem integration reproduce every headline area/ray/border value; the separate 65,536-ray bank agrees within 0.61 sigma. It confirms 864 BT-box separation checks, adverse occupied and rotated-bound fixtures, the distinct thin-band examples, actual display vertices/SVG transforms, all artifact/source hashes and 350 unchanged scientific blobs. Both actual PNGs were visually inspected. No material defect was found within this bounded technical assessment; this is not human sign-off.

The system-Python scratch rerender stopped because Matplotlib is absent; no dependency changed and direct SVG/PNG evidence checks completed. A transient capacity failure occurred after the completed check/results; the child was asked only to finish its concise report. The retained portable checker rerun passed. After the frozen target, README spacing was improved and the final denominator wording clarified: common across layouts for each metric, with distinct planar-area and whole-depth solid-angle denominators. Numeric evidence, plots, executed code and current geometry remain byte-identical to the reviewed target.

Normal push of `0d7a815` succeeded and GitHub metadata confirmed the exact PR head. The reviewer reply/body are prepared with immutable figure links; no adoption or ACTS efficiency claim.

IC-P1's concise report was successfully delivered after retry. The final portable checker explicitly includes M1 script hash and every A1 input identity; replay of this retained version passes with byte-identical result JSON. All five plot artifacts, six plot-source hashes and maintained links reconcile. Final technical assessment remains no unresolved material finding within scope. The denominator editorial observation is resolved in the study README without changing the numerical evidence.

## Published outcome and closeout

The separate study was pushed at `0d7a815`; independent evidence/clarified study index was pushed at `ae9141d95136cc20f853bbe3b234f5b1a8b5c634`. GitHub confirmed the published head. The existing PR body was fetched immediately before editing, retained and supplemented with the study/immutable comparison and BT-detail links. Reviewer reply: https://github.com/asalzburger/nodd/pull/90#issuecomment-6286412829. Complete closure at fixed BT legs is impossible; the checked two-band option recovers avoidable wedges and remains unadopted under the current whole-sector/no-radial-tiling and cassette rules. DES040, TASK-B-MUON-WHEELS and PR90 records link the evidence. No current geometry, OBJ, fields, native transport, or engineering status changed.

The last CI snapshot reports build IN_PROGRESS, token-site SUCCESS, deploy SKIPPED; no build pass is inferred. Closure recorded at 2026-10-20T08:06:50Z. This final record-only closeout commit is located by Git history after the listed result commits; exact root/child token counters remain unavailable, with usage empty rather than zero.

Final project/session validation passes: 69 tasks, 38 documents, 21 review rounds, 195 sessions. M1 usage summary and token preview build pass. The preview contains 210 historical disjoint turns and 624,299,405 observed tokens, not a measurement of this task; current root/child counters remain unavailable. After `ae9141d`, only this paired journal and project tracking changed.
