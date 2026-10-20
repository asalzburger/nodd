# SESSION-2026-10-20-pr90-endcap-wheels — Review decision

## Scope and evidence

Start5674a7688319d6dd5179c04cd381cb59f48d36bb, codex/muon-chamber-layout, clean worktree. User asks to address the agreed last PR90 comment6283618592 (2026-10-20): move outermost and innermost endcap wheels outside endcap toroids, adapt longitudinal length, no overlaps; produce newOBJ, full/endcap coverage, before/after endcap shape lists+2Dblue inventory and current barrel inventory. Governing DES040 remains DRAFT isolated PROTOTYPE, no human engineering acceptance. Preserve all original source/data/field/OBJ evidence and ACTS source edits.

## Initial method

Use repository coordinate/design-evidence/review-validation workflows. Before implementing, audit HCAL/coil/frame clearances and specify a bounded geometry/method amendment. Resolve physical ambiguities without silently changing magnets or source requirements. Three independent read-only specialist assignments follow, recorded before dispatch. Explicit prepared fallback mandates, not claimed native profile loading.

## Assignment W-A1

```json
{
  "id": "W-A1",
  "role": "SysArch",
  "input_revision": "5674a7688319d6dd5179c04cd381cb59f48d36bb",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Physical feasibility/interface audit of the latest agreed PR90 decision6283618592. Inner and outer endcap stations should lie longitudinally outside endcap toroids and become non-overlapping full wheels of trapezoids; adapt longitudinal length accordingly. Determine precise feasible z/r placements with unchanged HCAL, barrel/endcap coils and frame; compute full-envelope/clearance bounds, not just midplanes. Critical potential issue: ECTwarmfront6.55m versus HCALendcapback6.4412m cannot fit0.5m depth plus clearances. Identify whether a full radial wheel at rmin0.7 can exist with fixed magnets, and what exact minimal magnet or HCAL interface change would be required if impossible. Do not change magnets/fields or retune dimensions; return quantified options and ambiguity requiring human direction. Assess outerwheel beyondECT/BT and supportcarrier conflicts, barrel-length adaptation, field/world domain consequences. Read-only calculations/scratch only. No external messages, source/dependency modifications or nested agents.",
  "deliverable": "Quantified source-located physical interface/feasibility report in /private/tmp/pr90-wheels-A1-* with actual checks and viable bounded alternatives.",
  "completion": "Exact-revision interface assessment with no hidden clashes or implied approval."
}
```

## Assignment W-M1

```json
{
  "id": "W-M1",
  "role": "MuonTech",
  "input_revision": "5674a7688319d6dd5179c04cd381cb59f48d36bb",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Muon station/wheel concept for agreed PR90 comment6283618592. Independently inspect current panel inventory/packing and propose simple one-trapezoid-per-sector full inner/outer endcap wheels outside ECT, no overlaps, realistic fixed-clearance gap; preserve middle station unless justified. Investigate24vs12sectors, angular phase relativeBTlegs, radialextent/bore constraints and barrel longitudinal shortening needed. Do not silently change magnets, HCAL or chamber depth. SysArch independently audits global feasibility; if front wheel impossible fixed-coils+HCAL sayso. Suggest before/after shape inventory descriptors and 2D blue figures, current barrel inventory, combined/separate OBJ groupings. Read-only calculations/scratch only, no repo/dependency edits/nestedagents/externalmessages.",
  "deliverable": "Source-located chamber concept/inventory and bounded choices, exact quantitative constraints, in /private/tmp/pr90-wheels-M1-*.",
  "completion": "Actionable unclipped-trapezoid concept and explicit feasibility/coverage tradeoffs; no human acceptance."
}
```

## Assignment W-P1

```json
{
  "id": "W-P1",
  "role": "PhysVal",
  "input_revision": "5674a7688319d6dd5179c04cd381cb59f48d36bb",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/layout.py",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/acts/config.json",
    "tools/muon_layout/acts/propagate.cpp",
    "tools/muon_layout/acts/analyze.py",
    "docs/validation/DES-040/acts-propagation/summary.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Read-only benchmark/protocol proposal for PR90 agreed decision6283618592. Need new full/endcap coverage estimate after moving inner/outer endcap wheels outside ECT, no overlap and sector gaps explicit, before/after inventories +OBJ. Inspect old native ACTS benchmark masks/status/denominators and newdomainneeds; propose paired before/after native sampling with identical localp/charges/seeds/entrance and field, separate full4pi and exact endcapregion definitions not cherry-picked to improve. Distinguish geometric gap losses vs strict field-mask uncertainty vs transport. New positions may require extended field/world domains; assess whether unchanged 12.5mmap cansupportouterwheel and how to preserve original evidence if expanded. Consider full-wheel no radialtiling inventory+barrel length changes. Do not author implementation; future frozen-result review separate. No repo/dependency writes/nestedagents/externalmessages; scratch only.",
  "deliverable": "Concrete observables/controls/denominator plan with source locators in /private/tmp/pr90-wheels-P1-*, explicit limitations/choices.",
  "completion": "Meaningful unbiased comparable coverage plan, no invented scattering/efficiency or human signoff."
}
```

## Token accounting

Exact root/child per-turn counters unavailable; usage unknown, not zero. No estimates, overlapping totals or private client state retained.

## Clarification pending; independent work continues

Root and SysArch independently derive HCALback6.4412m, ECTwarmfront6.55m, gross0.1088m; with existing0.05m coil clearance and a provisionally equal HCAL margin,0.0088m is available for0.500mdepth (0.4912m deficit). The HCAL margin is an open interface assumption; even zero margins cannot fit the chamber. User was asked asynchronously whether to adjust endcap-toroid axial extent/recalculate field or retain magnets and reduce the inner wheel radial reach around HCAL. No dependent magnet/HCAL/wheel geometry is changed pending that design choice. Baseline chamber inventories, shape-view tooling and domain/coverage planning proceed independently. PhysVal also identifies that the old entrance cap6.50m would launch beyond a before-ECT innerwheel, requiring common upstream seeds for both compared layouts; outerwheel exhausts currentmap/worlddomain. These are not detector inefficiencies.

## Prepared evidence and observed checks

W-A1/W-M1/W-P1 completed exact-revision read-only assessments; no candidate geometry implementation or engineering approval. Root retained curated reports and portable A1/P1 checks, distinguishing provisional HCAL margin and ECT-only versus full-frame rear bounds. A1 source roots/output became CLI arguments; HCAL back is read from the pinned magnetic input. Raw scratch filename/hash metadata in the P1 JSON remains explicitly historical. No private comment cache or signed image URL was retained.

Baseline inventory generation first failed with missing Matplotlib in both the default and bundled Python (exit1). acts-spack preflight exits2 because setup/lock fingerprints changed; this warning was given before dependent work. Fresh setup_spack verified the active environment and installed DD4hep1.38/Geant4 11.4.3, and the existing acts-nodd pyvenv imports NumPy2.5.4/Matplotlib3.11.2 (exit0). No shared dependency/source modifications. Inventory generation then passed using that Python and task-owned font/cache directories. Both sheets visually checked; title and barrel footer spacing corrected and generation repeated.

Current output is816barrel/6families and744endcap/18families. The independent footprint reconstruction covers all1560panels with maximum0.4973nm error within1nm grouping tolerance, plus CSV/quantity/station/hemisphere checks (exit0). Root reproduced the P1 pinned baseline output exactly and ran the unchanged portable ACTS evidence checker:148960tracks and native control/artifact hashes pass; no native rerun. The A1 interface check passed against pinned inputs and484support envelopes.

TASK-B-MUON-WHEELS remains blocked on the physical choice; the session stays open. NewOBJ, after-layout inventory, paired newcoverage, magnetic redesign/sizing and field generation are NOT RUN. These are not represented by the baseline-only artifacts. Existing baseline chamber/magnet/field/OBJ/native evidence remains unchanged.

## Prepared publication checks

Project validation passes69tasks/38documents/21reviewrounds; journal validation passes193records. M1summary reports80sessions/35withusage; currenttaskusage remains unavailable. Local token-site preview passes with210historical disjoint turns/624299405observed tokens, not current-task usage. Retained baseline/P1 reproduction and portable A1 outputs match their independent originals exactly (root set-e command exit0). Preparation manifest pins source and newartifact hashes; narrow text scan found no signed/private-image/token markers. Latest discussion rechecked through GitHub connector: agreed comment6283618592 remains last; PR90 still open, same5674head. Raw discussion payload was not retained in Git.

Staged whitespace check found default CSV CRLF line endings in new files. Generator now emits LF; inventories regenerated without numerical changes and footprint check repeated successfully. Original unstaged whitespace check had not covered untracked files.

Completed28project/documentation and33journal tests: all61pass. Expected unavailable-history negative fixture emits a git error before passing; it is not an unresolved remote failure. Final staged whitespace check passes after LF correction.

## Publication and still-pending work

Preparation commit6089993659d58ae46aa5fb7cb700e231535410f2 pushed and PRhead verified. GitHub connector comment write returned403integration-permission error; existing authorized GitHub CLI session posted the prepared partial-status reply athttps://github.com/asalzburger/nodd/pull/90#issuecomment-6283825776 (exit0). No automatic approval rejection occurred. The reply links the blue inventories and physical alternatives, expressly leaving candidate geometry/newOBJ/aftercoverage pending. Follow-up record-only commit retains this publication evidence. Session remains open and task blocked on the same physical choice. No design approval or task completion claimed.

Publication metadata validator rejected fractional seconds in the collection timestamp. The surrounding non-fail-fast command continued into record-only commit aaaf377; correction uses required UTC second precision, retained through an ordinary follow-up commit before final push. Scientific preparation6089993 is unchanged. No failing validation is claimed as passed; the corrected gate is rerun separately.

## Human physical choice; resumed implementation

User: “Let’s shorten the Endcap toroidal to make wheel fit.” This selects the proposed0.50m front-return shift, rear fixed. Starting resumption at clean a32558a419404dfe741182b6713ce1f31062fd37. Updated DES039/DES040 selected contracts before implementation: retained operating currents, fresh coupled energy/cold volume and joint field; innerwheel6.7456m, rear12.80m; explicit BT gaps and whole-sector envelopes; common entrance6.4684m/world13.30m/map14.3125m. No human engineering signoff. Prior blocked status is superseded by this choice; no repeat approval is needed.

## Assignment W-A2 (before dispatch)

```json
{
  "id": "W-A2",
  "role": "SysArch",
  "mode": "read-only",
  "writable_paths": [],
  "task": "Audit newly human-selected0.50m ECT front-return shift with rear fixed; selected DES039/DES040 contract. Need independent cross-system check of full-bore innerwheel6.7456m outer12.8m, BT corridor geometry, framefrontlugs, B1halfz6.4456/B3extension12.5, retainedcurrents/newenergy/cold/warm boundaries, launch6.4684/world13.3/map14.3125. Read exact base sources via git show and current selected contract; no implementation, no repeated user permission. Return numerical pitfalls and source-located constraints promptly; scratch only, no nested agents/externalmessages/dependency changes.",
  "deliverable": "Read-only selected-interface audit in /private/tmp/pr90-W-A2-*.",
  "completion": "Quantified independent feasibility assessment of selected contract, no implied engineering approval.",
  "input_revision": "a32558a419404dfe741182b6713ce1f31062fd37",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/layout.py",
    "tools/toroid_prototype/system.py",
    "tools/toroid_prototype/energy.py",
    "docs/validation/DES-040/wheels-2026-10-20/coverage-plan.md"
  ]
}
```

## Assignment W-F1 (before dispatch)

```json
{
  "id": "W-F1",
  "role": "SoftEng",
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/wheels_field.py",
    "docs/validation/DES-040/wheels-2026-10-20/magnetic"
  ],
  "task": "Implement/reproduce shortenedECT magnetic candidate under selected DES039/DES040 contract. Own only new wheels_field.py and magnetic output directory, preserve old sources/artifacts. Read existing toroid finite-pack solver/energy/cold-union/map controls. Shorten ECT front0.50m keeprear: pluscentre9.5 halfz2.2, mirroredminus; keep exact existing operatingcurrents from retained results, allotherpack/radii/phases/warm dims. Recompute actual complete self/mutual vacuum energy with convergence/reciprocity and solenoidmutualcheck, global30MJ/m3 cold-union allocation, fitretainedwarm, centralcap5T. No old normalizer at superseded station positions and no currentretune; actualfieldresponsecanbe reported separately. Generate candidate jointmap plus old-baseline extended map common z\u00b114.3125 r9.5 phi30deg same0.0625m/0.625deg spacing; preserve oldmap nodes exactly for baselineextension. Oldfield/dataimmutable. Compile existing backend in task-owned cache; NumPy defaultpython available, plotting use installedacts-noddpyvenv ifneeded but preflight warning alreadyreported root handles nativeACTS. Avoid modifying shareddeps/sources, no nestedagents/externalmessages. Return candidate normalized configuration JSON ASAP before costlymap, then maps/energy/sourceprovenance JSON and controls, clear vacuum/nonlinear limits. Do not write DES/tracking/session files. Keep arrayfiles<100MB; use compressed npz.",
  "deliverable": "New reproducible magnetic script and magnetic/{configuration,energy,cold,map-metadata,baseline-extended-map,candidate-map,controls} artifacts with exact hashes and actual checks.",
  "completion": "Selected physical sources recomputed consistently, baselineextendedparity, allspaceenergy/cold/central cap and numerical controls; explicit remaining limitations.",
  "input_revision": "a32558a419404dfe741182b6713ce1f31062fd37",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/layout.py",
    "tools/toroid_prototype/system.py",
    "tools/toroid_prototype/energy.py",
    "docs/validation/DES-040/wheels-2026-10-20/coverage-plan.md"
  ]
}
```

## Assignment W-G1 (before dispatch)

```json
{
  "id": "W-G1",
  "role": "MuonTech",
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/wheels.py",
    "tools/muon_layout/wheels-config.json",
    "docs/validation/DES-040/wheels-2026-10-20/candidate"
  ],
  "task": "Implement selected DES040 whole-wheel chamber geometry + frameattachment amendment in newmodule/config/output directory only. Preserve all oldinputs/artifacts. HumanapprovedECTfront0.50shortening(rear fixed) and selectedcontract currentDES039/040 alreadyupdated. Read current geometry and sourcecontracts. Use warmdimensions retained0.5x0.6; magnetic source config oldgeometry plus ECTcentre\u00b19.5 halfz2.2; root/fieldagentwillprovide finalcoldcfg for synchronization. Innerwheelcentre\u00b16.7456,bore0.7,Rmax5.45,12wholetrapezoidscentres15+30k. Choose straightisoscelestrap edges to reserve BTlegs with50mmphysicalclearance, nonoverlap; prefer physically bounded affine widening gaps over unnecessary whole5deg angularwedge loss if full-volume proof possible. Record derivation/finalgapconfig before generating; no shapeclipping/radialadaptivefragments for newwheels. Outerwheelcentre\u00b112.8,Rmax8.45,24wholetraps20mmseams. Exempt these wheel-envelope/cassette outlines from old1.5m radialmodulelimit explicitly; no internals/manufacturing claim. Keepmiddle216panels ifcertifiedclear. B1halfz6.4456, B2same9.2; extendB3to12.5 with oldwholemodulepacking/clearancecertificates and exclusions toclosetransition. FrontECTframeattachments must contactnewfrontskin7.05 andstayconnected; preserve othermembers/feet. Need physicalclearancecertificates all panels/coils/supports/panelpairs, count/bore/HCALgeometrical bounds, connectedframe contacts. Return new geometry.json compatible oldschema + configuration/shapechange mapping, rejectedreasons and physicalviews/straightgeometrygapdiagnostics if practical. Do not editoldhelpers/export/native engine; root doesACTS/OBJ/inventories. No nestedagents, externalmessages or dependencies/source changes. Ask root promptly for implementationdetails, not user for previouslyauthorized choice.",
  "deliverable": "New wheels.py/config and candidate/{geometry.json,geometry-controls.json,...} with wholewheel IDs and provenclearances; exact parameters/provenance/changedfiles/checks.",
  "completion": "Source-reproducible selected wholewheel geometry and full-volume interfaces validated, frameconnected, newwheel trapezoids unfragmented, no engineering approval.",
  "input_revision": "a32558a419404dfe741182b6713ce1f31062fd37",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-040/support-input.json",
    "tools/muon_layout/design.json",
    "tools/muon_layout/geometry.py",
    "tools/muon_layout/layout.py",
    "tools/toroid_prototype/system.py",
    "tools/toroid_prototype/energy.py",
    "docs/validation/DES-040/wheels-2026-10-20/coverage-plan.md"
  ]
}
```

## Assignment W-S1 (before dispatch)

```json
{
  "id": "W-S1",
  "role": "SoftEng",
  "input_revision": "a32558a419404dfe741182b6713ce1f31062fd37",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "docs/validation/DES-040/wheels-2026-10-20/coverage-plan.md",
    "tools/muon_layout/acts/analyze.py",
    "tools/muon_layout/acts/draw.py",
    "tools/muon_layout/acts/test_analysis.py",
    "tools/muon_layout/geometry.py"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/wheels_acts/analyze.py",
    "tools/muon_layout/wheels_acts/draw.py",
    "tools/muon_layout/wheels_acts/compare.py"
  ],
  "task": "Implement new isolated native-result postprocessing/draw/pairedcomparison only for PR90 shortenedECT/wheels. Do not alter any legacy sources/artifacts or root-owned nativecontrols/preparation/runner. Root will generate WORK/primaries.npz, inputs.json {configuration:{geometry,map,geometry_sha256,map_sha256,...sameoldscanparams},files:{...}} and raw RUN/{hits.csv,tracks.csv,geometry.csv,geometry-corners.csv,metadata.json}; API analyze.py --work WORK --run RUN --output OUTPUT. Use current legacy lower-level face_catalog/read_hits/count_events for realnativeevent audit, no trajectoryfabrication. Preserve every denominator, raw finitepositions/IDs/events/status and currentthresholds/numericalgates; no loosening. Need globalall-family6faces/3pairedstations outer+30mmborder AND endcap-only equivalents (same logical3stations, usefamilyby panelkind), retainsides/tangents/reentries/orphans/navigationambiguity uncertainty. Data has sample0 eta_display,1 fulliid4pi4096,2 iidpositivecap4096,3 iidnegativecap4096 at frozen |eta|\u22651.191571051278059, seed906269; original display/fullbankseed906268 directions retained, commonentryR4.35/H6.4684, all5localp/2charges repeated. Fullsample sphere all generated including masks; caps pooled/side and sphere endcap subset separate, no doubleweighting. Before/after fieldgeometrybothchange; compare paired matchingtrack/direction IDs/configcommonlaunch/worldsame, differencesbounds mean(Lafter-Ubefore)..mean(Uafter-Lbefore), definitelygained/lost, statuscontingency, conservativepaired sampling errors not confidence on unresolved events. Storetypedtracks/hits compressed arrays under OUTPUT eachfile<100MB with complete source/field/input/rawdatahashes. Summary+portabletable/plot usefulfull/endcap3stationavailability and6facebounds, charge/momentum separate, XY/RZactualnativepositions and phi/eta maps representative2.65/100/1000GeV. Sameexistingblueforchambers ifdrawn, meaningfullegends/axes; no reconstructed efficiency/material/installedfieldclaim. Freezeactualsourcehashes/currentHEAD and scope sourcechanges/cleanliness honestly; do not writecandidategeometry/field, DES/logs/tracking. Can testcounterhelpers with fixture input but actual scanrootlater. AskrootforAPIclarifications quickly. No nestedagents/externalmessages/dependency/sourceinstallation changes.",
  "deliverable": "Three isolated Python modules implementing realnativeaudit, pairedphysicscomparison and staticfigures/reportoutputs; documentedCLI/API, actual checks and limitations.",
  "completion": "Unbiasedpaired full/endcap failure-aware availability with raw-native-event traceability, no newefficiencyorapprovalclaims; boundedfilesonly."
}
```

## Assignment W-O1 (before dispatch)

```json
{
  "id": "W-O1",
  "role": "SoftEng",
  "input_revision": "a32558a419404dfe741182b6713ce1f31062fd37",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/export_obj.py",
    "tools/muon_layout/wheel_inventory.py",
    "tools/muon_layout/obj_writer/writer.cpp",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/wheels-2026-10-20/magnetic/configuration.json"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/wheels_artifacts.py",
    "docs/validation/DES-040/wheels-2026-10-20/obj-revised",
    "docs/validation/DES-040/wheels-2026-10-20/inventory-comparison"
  ],
  "task": "Produce new reviewable OBJ and before/after shape inventories from final candidate geometry1344panels, no geometry/field/native actor changes. Own only new wheels_artifacts.py and two output dirs. Candidate generationfinalizing sourcecfgSHAe2e9eb50...; wait finalgeometryifneeded and sourcehash actualinput. Reuse existing native inspection/exactcorner export through old helperchambers(native,panels), coils(c), write_input and nativeActs::ObjVisualization3D writer; default oldhelperconfiguration pinsoldinputs so calllowerhelperswithnewc only. Nativepropagator reference/cache/pr90-wheels/build/nodd-muon-wheels-propagate must receive --world-radius-m9.1 --world-half-z-m13.3 --entrance-radius-m4.35 --entrance-half-z-m6.4684 for zeroB inspect. Existing nativewriter reference/cache/pr90-obj/build/nodd-muon-obj and installedCoreSHAf4c040... verified, no needrebuild. Produce combined chambers+coils portableOBJ/MTLZIP blue(0,96,255)/grey(160,160,160), plus separatebarrel,one+endcap,toroids+frame views eachwithportableMTL andcombinedcomponentsZIP asreviewerrequestedearlier. Framevisualizationusesactualsupportouterprism reservations, explicitnotRHSmaterialormassunion; samegrey, cavityomissiondeclared. Verifyclosure/orientationafter1nmpositionwelding and native/sourcevertices, roundtrip/materialcolors, allcounts, no world/visual clipping, zipbytesmatch. Coils exactoldwarm sweep discretization64stepsperquadrant/chordsagitta withnewECT coordinates. PreserveoldOBJimmutable. Previewactualgeometrywithdynamicfullbounds inclouterwheel13.05m/framefeet, sameblue; inspectPNG visually. Inventory use wheel_inventory.write lowerAPI with sourcegeometrypaths; new inventory-comparison before-endcap and after-endcap sheets commonmetriclimits, plus current-barrel afterrepacking, optionallybeforebarrelcontext. Do not overwrite retainedbefore-inventory files/manifests. Fullsourcepanel\u2192shapeIDs/unroundeddims CSVJSONMD and actualbefore-aftercounts shapechange mapping/station/side plusplots, sameblueKd. Geometryagentreportsinner1+middle6+outer1=8endcapfamiliesexpected but verifyactual. Include provenance/sourceandbinaryhashes, objectcounts/roles/units/limits and conciseREADME. RuntimeMatplotlibexisting /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python with MPLCONFIGDIR=/private/tmp/pr90-wheels-matplotlib XDG_CACHE_HOME=/private/tmp/pr90-wheels-cache; rootpreflightwarningandruntime verificationdone. No installers/sharedsourcechanges,nestedagents or externalmessages. Root owns fullrunresults/newtopreport/logs/tracking.",
  "deliverable": "Source-reproducible wheels_artifacts.py, revised nativeOBJ/MTL/ZIP and separatecomponentviews, visuallycheckedpreviews, before/afterendcap andcurrentbarrelshape inventories, provenance/verificationJSON andREADMEs.",
  "completion": "Allrequestedgeometryreviewassets faithfullyreflectfinalcandidate withblue/grey, source/nativechecks and no oldartifactmutation; no physicalresponseorengineeringapprovalclaim."
}
```

W-O1 first prepare attempt rejected generated candidate/magnetic outputs as absent from the base revision (exit1); these are current generated dependencies, not historical input files. Corrected pinned inputs to the original geometry/results; W-O1 must record actual generated input hashes before using them. No agent dispatched with the rejected contract.

Corrected W-O1 assignment:

```json
{
  "id": "W-O1",
  "role": "SoftEng",
  "input_revision": "a32558a419404dfe741182b6713ce1f31062fd37",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/export_obj.py",
    "tools/muon_layout/wheel_inventory.py",
    "tools/muon_layout/obj_writer/writer.cpp",
    "docs/validation/DES-040/geometry.json",
    "docs/validation/DES-039/results.json"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_layout/wheels_artifacts.py",
    "docs/validation/DES-040/wheels-2026-10-20/obj-revised",
    "docs/validation/DES-040/wheels-2026-10-20/inventory-comparison"
  ],
  "task": "Produce new reviewable OBJ and before/after shape inventories from final candidate geometry1344panels, no geometry/field/native actor changes. Own only new wheels_artifacts.py and two output dirs. Candidate generationfinalizing sourcecfgSHAe2e9eb50...; wait finalgeometryifneeded and sourcehash actualinput. Reuse existing native inspection/exactcorner export through old helperchambers(native,panels), coils(c), write_input and nativeActs::ObjVisualization3D writer; default oldhelperconfiguration pinsoldinputs so calllowerhelperswithnewc only. Nativepropagator reference/cache/pr90-wheels/build/nodd-muon-wheels-propagate must receive --world-radius-m9.1 --world-half-z-m13.3 --entrance-radius-m4.35 --entrance-half-z-m6.4684 for zeroB inspect. Existing nativewriter reference/cache/pr90-obj/build/nodd-muon-obj and installedCoreSHAf4c040... verified, no needrebuild. Produce combined chambers+coils portableOBJ/MTLZIP blue(0,96,255)/grey(160,160,160), plus separatebarrel,one+endcap,toroids+frame views eachwithportableMTL andcombinedcomponentsZIP asreviewerrequestedearlier. Framevisualizationusesactualsupportouterprism reservations, explicitnotRHSmaterialormassunion; samegrey, cavityomissiondeclared. Verifyclosure/orientationafter1nmpositionwelding and native/sourcevertices, roundtrip/materialcolors, allcounts, no world/visual clipping, zipbytesmatch. Coils exactoldwarm sweep discretization64stepsperquadrant/chordsagitta withnewECT coordinates. PreserveoldOBJimmutable. Previewactualgeometrywithdynamicfullbounds inclouterwheel13.05m/framefeet, sameblue; inspectPNG visually. Inventory use wheel_inventory.write lowerAPI with sourcegeometrypaths; new inventory-comparison before-endcap and after-endcap sheets commonmetriclimits, plus current-barrel afterrepacking, optionallybeforebarrelcontext. Do not overwrite retainedbefore-inventory files/manifests. Fullsourcepanel\u2192shapeIDs/unroundeddims CSVJSONMD and actualbefore-aftercounts shapechange mapping/station/side plusplots, sameblueKd. Geometryagentreportsinner1+middle6+outer1=8endcapfamiliesexpected but verifyactual. Include provenance/sourceandbinaryhashes, objectcounts/roles/units/limits and conciseREADME. RuntimeMatplotlibexisting /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python with MPLCONFIGDIR=/private/tmp/pr90-wheels-matplotlib XDG_CACHE_HOME=/private/tmp/pr90-wheels-cache; rootpreflightwarningandruntime verificationdone. No installers/sharedsourcechanges,nestedagents or externalmessages. Root owns fullrunresults/newtopreport/logs/tracking.",
  "deliverable": "Source-reproducible wheels_artifacts.py, revised nativeOBJ/MTL/ZIP and separatecomponentviews, visuallycheckedpreviews, before/afterendcap andcurrentbarrelshape inventories, provenance/verificationJSON andREADMEs.",
  "completion": "Allrequestedgeometryreviewassets faithfullyreflectfinalcandidate withblue/grey, source/nativechecks and no oldartifactmutation; no physicalresponseorengineeringapprovalclaim."
}
```

## Resumed runtime and early execution evidence

Spack preflight again flags changed setup/lock; warned before dependent work. Fresh setup verifies activeci-dependencies,DD4hep1.38,Geant4 11.4.3; installedacts-noddPython imports NumPy2.5.4/Matplotlib3.11.2. ActsCoreSHA remainsf4c040fa6c331fca6180dc75589fbc95ec30fc485c2edbefb891fda46cdf7088. ACTS sister checkout's15pre-existing dirty/untrackedfiles preserved; no ACTS/dependency rebuild or source edits needed for the newdriver. Normalfind_package(ActsCONFIGCore) configure/build passed for newdomainparameter variant, with existing CMakepolicy/CLHEP/sysctl warnings retained.

Generated C++ source is a deterministic SHA-guarded transformation of frozen1215ae28... source, limited to world/virtualentrance CLI dimensions andmetadata; nativealgorithmunchanged. Actual original-vs-variant defaultdomain regression uses40original tracks/138nativeevents and agrees exactly (0position delta); native-variant-controls.json retains actual source transformations and binary hashes. Originaldirectionbank14896directions percase is preserved exactly in new23088directionbank, with8192additional capdirections separately weighted and commonstartsurfacechanged.

Baseline preparation produced230880primaries. All12newbefore-nativecontrol gates pass, including inheritedstrictfieldparity/geometry/zero-clips/helix/finite-owner/navigation/refinements/negativecontrols and newexpandedworld/commonlaunch/actualwheel-edge fixtures. Developmentcontrolreport is in ignoredruntimecache; final scan will require committed sources and this exact passingbinary/source/input gate.

## Scientific source/input freeze before paired acquisition

W-F1 reports complete fixed-current vacuum energy4.598715882532644GJ, cold0.29738663007522614×0.43368883552637144m, fits0.50×0.60warm, global30MJ/m³.40solvercontrols pass; both153×459×49×3maps generated. All original401zplanes/fields/masks retained byte-for-byte in baselineextension. Sampled complete centralmax3.024372329376175T; interpolation/source-discretization/seam/mask controls retained. Obsolete station/fieldtarget auxiliary metadata moved under explicit historicalreference with separate chamber owner; metadata-only refresh preserves map hashes and numericalenergy digest, original numerical-execution sourceSHA retained.

W-G1 finalsource/inputsfrozen:1344panels=1056barrel+288endcap; B1/B2/B3=168/360/528 andinner/middle/outer=24/216/48 overbothends. All1344individualcoil/supportcertificates, no pair/HCALconflicts/unresolvedacceptedcells,36groundedcases; unchangedframebytes copiedexactly, only48frontlugreplacements. Newwheeltrapsgapderivationrecordedbeforegeneration;72independentfullvolume analytic/adaptive cross-checks plus adverse fixtures and21inheritedcontrols pass. FinalgeometrySHA621b5cb9d45906b338251d527d932abd6b9aca86c84ffaa0918c7e535a17781f. MaxchamberR8.513349341m/z13.05m insidecommonworld9.1/13.3.

W-S1 sourcefrozen after11inheritedcountertests, CLI/syntax and focusedstratified-paired-bound/typedCSV/NPZ/negative-metadata/syntheticfigure checks. Plain/bundled Python lackedMatplotlib; installedPython plotted successfully. Synthetic fixtures remain in scratch and are not scientific ACTS evidence. Root acquires real native arrays next.

## Assignment W-P2 (before dispatch)

```json
{
  "id": "W-P2",
  "role": "PhysVal",
  "input_revision": "22a3f8c113a276b1321adeb9b994107594eb3c7d",
  "inputs": [
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_layout/wheels.py",
    "tools/muon_layout/wheels-config.json",
    "tools/muon_layout/wheels_field.py",
    "tools/muon_layout/wheels_acts/variant.py",
    "tools/muon_layout/wheels_acts/controls.py",
    "tools/muon_layout/wheels_acts/prepare.py",
    "tools/muon_layout/wheels_acts/analyze.py",
    "tools/muon_layout/wheels_acts/compare.py",
    "docs/validation/DES-040/wheels-2026-10-20/magnetic/configuration.json",
    "docs/validation/DES-040/wheels-2026-10-20/magnetic/energy.json",
    "docs/validation/DES-040/wheels-2026-10-20/magnetic/controls.json",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry.json",
    "docs/validation/DES-040/wheels-2026-10-20/candidate/geometry-controls.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independent source/input assessment at exact frozen22a3f8c revision before/alongside real paired nativeacquisition. You previously authored P1protocol and A2selected-interfaceplanning; disclose overlap, no implementationauthorship. Reviewprimarysources first, newECT geometry/current policy/coupledenergy/coldvolume/centralcap/maps truejointvacuum andbaselineextendedparity; allsource/quantity/mask semantics, actualwholewheel shapes andframephysicalcertificates includingB2extendedfrontlugs/B3returnexclusions, fullboreHCALmargins, nooverlaps/newwheelunfragmented. ReviewSHAguarded C++domainvariant for unchangedroot/actorcode andexplicitworld/entry, seedpreservation/capdenominators/strictfailureunknownbounds, eventpair/counterpostprocessing/pairedchangesstratifiederrors. Numericalgates/tolerancesmustnotbeweakened. Rootbeforedevelopment12nativegatespass (cache report); fullscan source willbe thiscommit withnewcontrols/outputs retainedlater. Actualfinalartifacts willbe a separate frozen W-P3followup; do not reviewlive-uncommitted outputs as ifatthiscommit. Need prompt materialfindings with reproducible independent focusedcalculations/controls; scratchonly /private/tmp/pr90-W-P2-*. No repo/source/dependency edits,nestedagents,externalmessages or humanapprovalclaim.",
  "deliverable": "Exact-revision PhysVal source/input report+JSON and portablefocusedindependentchecks in /private/tmp/pr90-W-P2-*; materialfindingsorboundedno-findings and limitations.",
  "completion": "Independent scientificsource/input assessment ofselectedcontract with actualcheckevidence, laterfrozenrealnativeartifactsreview explicitlypending."
}
```

## Real paired acquisition and export results

Both real native scans executed frozen source22a3f8c113a276b1321adeb9b994107594eb3c7d with230880 tracks each, after12/12before and12/12after numerical gates. Before662154raw/656276unique events; after805628raw/unique. All native finitepositions/64bitIDs retained;0orphan/parallel/navigation-uncertain/tangent rows, finiteface residual<10nm. Both allgenerateddenominators include actual fieldmaskstates (131587before/127018after) and one20kstep_limit each. Before88059/after28149 are reproducible nativecorrection cycles, not proven physicalorbits. Supplemental original/exhaustive, halfstep, tighter surface and RK reruns executed; only tighterRK resolves cycles (beforemasked/aftercompleted), no primaryreplacement. Complete deterministicgz nativeaudits/metadata/commands retained. Earlier scratch diagnostic print failed indexing61etaedges asiftrackarray; corrected extracting actualinputrow; no scientific scan altered.

Analyze/compare/draw completed for actual arrays:9figuresperlayout+pairedchange, full/endcap/side/wheel/p/q uncertaintybounds and separate iidSE. Root inspected combined/positiveendcapOBJ previews, revisedendcapshapes, actualnativehitpositions/endcapmap andpairedchange plot; no visualclipping. Fieldmasks dominatewidebounds, so no overallreconstruction/coverageimprovement claim. At100GeV,+e active3station4pi26.32–61.45%before/25.46–59.52%after; endcapcap5.20–63.28%/10.06–65.66%. Geometryandfieldbothchange.

W-O1complete: nativeOBJ1344bluechambers+36greycoils, separatecomponentOBJpairs/ZIP, before18/current8endcap andcurrent7barrelfamilies; exactnativecorners≤3.56e−15m, closed/orientedweldedmeshes, relativeMTLs/colors/roundtrip/ZIPchecks pass. Regenerable27MBinspection/writerstaging ignored, canonicalexports/checks retained. OldOBJ/scientificevidence unchanged; originalacts/check.py passes148960tracks/artifacthashes afternewwork.

W-P2source/inputassessment at22a3f8c found no materialphysical/software defect. IndependentSAT1512panelpairs/1692expandedsupports,216middleexact/48changedlugs, oldfieldnodeparity,23088validlaunchstencils persystem,4096independentmaskqueries/map, original14896directions and16pairedBooleanboundcontrols passed. Scope excludes newnativeartifacts reservedforW-P3. Minorprovenance finding clarified by W-G1 exacthashproof: DES040generationhash differs fromfreezeonlyby8lineaffinecorridor/basedimensionrestatement alreadyinconfig/geometry.11/12sourcematchesplusseparatemagnetichash; do notcallallhashmatch. Rootretains originalcontrolsunchanged and portablehashproof. Laterdoccleanup labels originalpre-shortening sections historical.

Initial staged whitespacecheck flagged nativeMTLtrailingformat and standardPythonCSVCRLF. Added scoped artifactformat attributes to preserve actualnativeMTL/ZIPbytes and CSVhashes; no numericalgate or data altered.

## Assignment W-P3 (before dispatch)

```json
{
  "id": "W-P3",
  "role": "PhysVal",
  "input_revision": "0576b7a615c81d1687f0cf7a3ceb0ca310478481",
  "inputs": [
    "docs/validation/DES-040/wheels-2026-10-20/README.md",
    "docs/validation/DES-040/wheels-2026-10-20/propagation/before/summary.json",
    "docs/validation/DES-040/wheels-2026-10-20/propagation/before/tracks.npz",
    "docs/validation/DES-040/wheels-2026-10-20/propagation/before/hits.npz",
    "docs/validation/DES-040/wheels-2026-10-20/propagation/after/summary.json",
    "docs/validation/DES-040/wheels-2026-10-20/propagation/after/tracks.npz",
    "docs/validation/DES-040/wheels-2026-10-20/propagation/after/hits.npz",
    "docs/validation/DES-040/wheels-2026-10-20/propagation/comparison/comparison.json",
    "docs/validation/DES-040/wheels-2026-10-20/propagation/failure-audit/audit.json",
    "docs/validation/DES-040/wheels-2026-10-20/obj-revised/export.json",
    "docs/validation/DES-040/wheels-2026-10-20/inventory-comparison/comparison.json",
    "docs/validation/DES-040/wheels-2026-10-20/magnetic/controls.json",
    "tools/muon_layout/wheels_acts/analyze.py",
    "tools/muon_layout/wheels_acts/compare.py",
    "tools/muon_layout/wheels_acts/failure_audit.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Final actualartifact assessment at exact commit 0576b7a615c81d1687f0cf7a3ceb0ca310478481. Continue prior W-P2scope/disclose P1/A2planning overlap; no implementationauthorship or nativeprofileclaim. Inspect actual committedtypednative arrays/64bitIDs/status/source/hashmetadata and rawboundarycoordinates, recompute meaningful nativecount/station/event/border/paireduncertainty controls from actual arrays with independent arithmetic, denominator/p/q/seeds/bankweights and source22 acquisition identity. Check both12gate reports, no loosened numericalgates, quantify before88059 andafter28149 step_limit and frozenretention; inspect actualcompressedrootaudit diagnosis for original/exhaustive/halfstep/tightsurface/tightRK no primaryreplacement. Fieldmaskedunknownbounds dominate; no overall improvementclaim and no scattering/eloss/MDTresponse. Inspect candidateOBJ actualvertices/material/closure/orientation and ZIPbytes/inventories/shapecounts, geometry/field/energy consistency using P2 frozeninputs and new actualassets. W-P2DEShashnote reconciled by 8lineproof (11/12sources+separatemagnetichash). Source22, artifactfreeze0576b7a615c81d1687f0cf7a3ceb0ca310478481 distinct; laterdocs/review/trackingedits mustnotalter scientificsource/data. Return prompt materialfindings to root; retained reportJSON/MD+portablechecker scratch /private/tmp/pr90-W-P3-* only. No repo/dependency/source edits,nestedagents,externalmessages or engineeringapproval. Visualinspection of selected actualfigures when useful. Can access original raw CSVs in ignored reference/cache/pr90-wheels/{before,after}-run as supplementalhashverified evidence, not claim tracked. Must state actualchecks vs recorded solver/nativeexecution and limits. Do not rerun all simulations; relevantindependent counters/geometry proofs appropriate.",
  "deliverable": "Exactrevision actualartifact PhysVal report/JSON and portableindependentchecks with source/filehashes in scratch; findings and limitations.",
  "completion": "Independent assessment of actual pairednative/OBJ/inventory/field evidence with failure/uncertainty honest; no unresolved materialclaim defect."
}
```

Scientific/artifactfreeze0576b7a615c81d1687f0cf7a3ceb0ca310478481 pushed and open/non-draft PR90head verified.28projecttests pass in251.882s;33journal+11countertests pass. Remoteghprchecks reports no checks (exit1), connectorstatuses empty; no remoteCIpass claim. ExacthistoricalpreparationREADME at6089993 reproduces its manifestSHA; currentREADME supersedes that page. Rootmanifestchecks194canonicalfiles/sourcehashes pass.

## Final actual-artifact assessment

W-P3 exacttarget0576b7a615c81d1687f0cf7a3ceb0ca310478481 complete, no unresolvedmaterialfinding. Separateagent authoredP1/A2planning butnone oftheimplementation; fallbackmandateandplanningoverlap disclosed. All26counterarrays agreeindependently,2240availabilitymetric-regionchecks and1120pairedchecks includingendpoint/conservativeSE pass; all actualrawCSVevent/trackpayloads hashverified/exactlycompared and64bitIDs preserved. Compressedfailureauditrawidentities/hashchecks pass. All4OBJexports/materials/closures/ZIPmembers and744/288/1056inventoryentries pass.6actualfigures inspected. Limits: recordedsolver/nativeexecutionsnotrerunbyreviewer, installedmaterial/response/engineeringnotqualified, masksdominatewidebounds. Portablecode/reports copiedunchanged toreview/. RootlaterREADMEonlylinksfinalreport andpreserveshistoricalpreparationREADMEbyteexact; no scientificdata/sourcechanges afterreview. Canonicalmanifestrefreshedwithlaterreviewdocs explicitlylisted.

## Publication and bounded closeout

Publishedsource/input22a3f8c, actualartifact0576b7a, assessment/reportba1f44632bdf5b813856c6cd057356e11fe02510 are distinct. PR90open/non-draft verified withnewtitle/body andartifact/review links. Finalreviewerreply: https://github.com/asalzburger/nodd/pull/90#issuecomment-6284526380 . Asobserved2026-10-20T06:02:53Z, token-site remotecheck IN_PROGRESS; no remote scientificCIpass inferred. Local69task/38document/21reviewround and193session validators pass;28project/33journal/11countertests pass, specialistfield/geometry/nativegates andindependentW-P3actualartifacts pass. Canonical202filemanifest and182reviewedscience/sourcebyteidentity checked; historicalpreparationREADMEhashreproduced.

TASK-B-MUON-WHEELS completeddenotesdeliveryofunsignedprototypeandevidence. DES039/DES040 remainDRAFT; requiredetaacceptance/sectorlossjudgment, cassetteinternals/precision, magneticmaterial/forces/conductor/quench/thermal/structuralqualification andnewmomentumresolutiondesign remainfuturehumanreview/implementation. No mergeorhumanapproval. Source artifactsandexternalACTS15pre-existingchanges preserved. Exactcurrentroot/childtokencounters unavailable; usageempty, notzero. Tokenpreviewshows210historicaldisjointturns/624299405observedtokens, notcurrenttaskusage. Finalrecord-onlycommit follows; locate itsownSHA throughGit history toavoidself-referentialrecording.
