# SESSION-2026-10-15-hcal-barrel-design — Common-module barrel HCAL

## Selected conversation and scope

Exact user direction: “Ok, let's assume this is the common readout module - can
you go on and design a Barrel and Endcap HCAL accordingly (separate PRs) please”.
This task develops the barrel proposal; the companion region has a separate
worktree/PR and journal. Both start from clean common-module head
`abd95bdc64b9d7971561d659bf953e71de4e7e99`, PR81. The human selected a working
basis at14TeV, not engineering sign-off. ParentPR81 remained OPEN/draft with
hosted build and token-site SUCCESS when checked. Proposals are sibling branches
against its head branch, so neither regional diff includes the other.

Read AGENTS/PROJECT and applicable design/ADR/layout/role instructions. Applied
nodd-coordinate, nodd-design-evidence and nodd-review-validation. Explicit
role-prompt fallback was used, with complete prepared prompts; native profile
loading was not verified. No production detector changes or dependency installs.
Exact start/client identity/per-turn usage were not exposed.

## Design decisions and outcomes

Draft DES037 before implementation. Preserve36tile/184mmboards and the
380x240x12mm pairedcarrier unchanged. CaloTech and SysArch bounded source and
physical-interface inputs. Recomputing36*(30steel+12carrier+1installation)+10cover
revealed a1558mm total,62.1mm larger thanDES034. The proposal exposes that
amendment rather than compressing hardware or secretly losing absorber/layers.
Barrelouterapothem4158mm andendcapouter4148/backabsz6441.2mm are proposals;
frontplanes,ECALbackbone/rearegress andFCalreservation stayfixed.

The sharedcarrier's projectedcoreceiling is69.6387%. Counts, completefiducial
faceareas and physicalcore-plane masks retain gaps. 54,912 carriers /3,953,664tiles /1,770.862t /326.143kW is a partial,
conditional model ledger, not a bill ofmaterials or plant certification.
The1MHz DAQ overload staysvisible. Regionalradiation/occupancy/EOL,rate,
optical/shower,thermal/hydraulic andstructuralqualification remainopen.

Main implements the barrel analytical model. SoftEng owns the four endcap
model/config/test/guide files, after DES038 is committed. Its follow-up makes
front origins explicit, checks retained common-module source identities and
clarifies the angular-boundary filter. No common-module hardware is edited.
Main adds regional drawings, reports, CI, layout proposal links and records.

PhysVal design review found the barrel's requested shifts could change column
count. The implementation retains maximal centred counts across controls and
explicitly bounds actual shifts to remaining edge margin minus1mm. PhysVal
review at the fixed code snapshots found no new scoped correctness/claim defect.
It ran15barrel and19endcap controls, plus3,105 independent global centre/near-edge
probes perregion, withzero lookup discrepancies. SysArch found no blocking
physical-interface defect in the bounded analytical scope. It retained the
endcap negative-y connector-facing/outwardstrip caveat; no connected network is
claimed. Reviewer scopes/exactrevisions are in the regional review reports.

## Executed checks and retained evidence

Source/model snapshot for this region: `c83e6f4eaebdaa354217b79b963df15c6c3c0a96`. Actual source-bound export,
15regionalcontrols,44common-module controls and14historicalcalorimeter
regressions passed. Exact command exits are in the pairedJSON. Coverage samples
physical29.7mmrectangles atlocalz2mm ahead oftherearrecess, notfullfinite-solid
navigation or response. Barrelsteelpaths are analytical; endcapsteelpaths
explicitlyNOT_RUN. Fullplacement/rawmask files stayignored andtheir hashes are
retained. Both regional PNG drawings were rendered fromexports and inspected.
Existing Matplotlib3.11.2 in the preinstalledACTSvenv was used; standard-library
work usedPython3.14.6. NoACTS/DD4hep/Geant4nativeactivation or new simulation.

The initial composite GitHub refresh hit sandboxed DNS failures (the wrapper
exited0 after an unrelated worktree listing); retrying fetch and PR81 view with
approved network access succeeded. Separate localworktrees/branches preserve
independentregiondiffs. Project/session/source/link/site checks and publication
outcomes are recorded after actual execution. No private client state/archive
or raw model rollout is collected. See [results](../../docs/validation/DES-037/results.md)
and [review](../../docs/validation/DES-037/review.md).

## Token accounting

No exact client per-turn counters for the shared parent turn or specialists are
available. `usage` stays empty: unknown, notzero. No token total is estimated or
allocated betweenregions. Completion summaries report observed project totals
andmissingcoverage; duplicated historical observations are not newtaskusage.

## Follow-up

Publish a separate draft regionalPR, link it to the task, and retain source-bound
results. Review the depth amendment, residual seams/inneracceptance, transition,
services and mechanical/forward interfaces before adopting or integrating it.
Only identified humans may grant engineering sign-off or detector acceptance.

## Bounded specialist assignment

Explicit role-prompt fallback; native profile loading unverified.

```json
{
  "id": "HCALASSEMBLY-20261015-CaloTech",
  "role": "CaloTech",
  "input_revision": "abd95bdc64b9d7971561d659bf953e71de4e7e99",
  "inputs": [
    "docs/design/DES-036-hcal-common-readout-module.md",
    "docs/design/DES-035-hcal-realism-and-prototype-plan.md",
    "docs/design/DES-029-endcap-coverage-repair.md",
    "docs/design/DES-034-siw-service-envelopes.md",
    "docs/layouts/LAYOUT-001.json",
    "tools/hcal_readout/config.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "User now takes DES036 common module as working basis and requests separate barrel and endcap HCAL design PRs at14TeV. Read-only propose concrete endcap architecture using unchanged36tile/184mm board and preferably existing380x240x12 paired carrier; distinguish module standardization from carrier redesign. Keep DES034 envelope frontabsz4883.2,back6379.1,innerapothem300,outerapothem4085.9 and existing FCal/RZ services constraints unless explicit amendment. Compare full-face Cartesian/quadrant and16narrowsector packing; quantify inner deadregion and coverage vs eta/phi with real boards/carriers, explain why standard pairedcarrier may not fill inneraperture. Recommend 36layers/30mmsteel sampling closure with12mmcarrier and installation gaps, support/ownership/services and credible counts/IDs. Avoid inventing custom edgeboards/tiles or blanket coverage claims; no EOL/rate/physics certification. Use existing source references or inspect actual primary sources if needed. Return a concrete prioritized design and mathematical packing/clearance conditions within about8minutes. No writes, runtime activation, delegation or remote publication.",
  "deliverable": "Endcap packing/stack/service design input, alternatives, explicit parameters and quantitative diagnostic requirements.",
  "completion": "Return exact examined revision, factual locators vs choices/inferences, recommendation and unresolved innercoverage/radiation/service concerns; no engineering signoff."
}
```

## Bounded specialist assignment

Explicit role-prompt fallback; native profile loading unverified.

```json
{
  "id": "HCALASSEMBLY-20261015-SysArch",
  "role": "SysArch",
  "input_revision": "abd95bdc64b9d7971561d659bf953e71de4e7e99",
  "inputs": [
    "docs/design/DES-036-hcal-common-readout-module.md",
    "docs/design/DES-035-hcal-realism-and-prototype-plan.md",
    "docs/design/DES-029-endcap-coverage-repair.md",
    "docs/design/DES-034-siw-service-envelopes.md",
    "docs/layouts/LAYOUT-001.json",
    "tools/hcal_readout/config.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "User requests separate barrel/endcap HCAL designs based on unchanged DES036 module at14TeV. Read-only assess common envelope/service/structural interface contract before layout generators. Preserve DES034 LAYOUT001 barrel apothem2600..4095.9,halfz4483.2,endcapsfront4883.2/back6379.1,inner300/outer4085.9,ECALserviceannulus2300..2600 and400mmrearbreak; discuss polygoncorners vs circularclearance, layerdepth36x(30+12+installation), residualsupportbudget, radialfixedrectangularcarrierfit atlayerfront and barrel axialdivisions/midplanecrack. Propose maintainable sector/row organization, loadpaths/steelownership and named internalcollector strips/endhandoffs preserving ECALegress, no secretlymaterialemptyrouting. Unchanged commoncarrier tubes exit along itsy onbothfaces, so rowsneedports/collectors and boardserviceconnectors reserved near+y; do not claim connected network. Endcapbeamaperture/FCal/negativeendright-handedframes and forwardcoverage provisional. Return concrete cross-PR invariantregister, likely geometricfailures and recommended exposedtradeoffs within8minutes. No writes/runtime/delegation/publication.",
  "deliverable": "Bounded common physical/service interface contract and measurable clearance/containment/ownership checks for both PRs.",
  "completion": "Return exact input revision and recommendations with source locators, derivations, risks and open engineering decisions; no human approval."
}
```

## Bounded scientific design review

```json
{
  "id": "HCALASSEMBLY-20261015-PhysVal-Design",
  "role": "PhysVal",
  "input_revision": "871176aeaad8e31dcb1ad3373cf60552b6cf12de",
  "inputs": [
    "docs/design/DES-037-hcal-barrel-common-module.md",
    "tools/hcal_readout/config.json",
    "docs/design/DES-034-siw-service-envelopes.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review newdraft HCALbarrel design DES037 in <barrel-worktree> and endcap DES038 atsecondaryfixedrevision516151c6e962d481efffde95eea9a9ab0f162098 in sibling <endcap-worktree>. User takes DES036commonmodule asworkingbasis at14TeV andrequests separatePRs. Read actualfull primarybarrel HEAD from git if givenSHA doesnotexist andreportcorrection; no substitute neweruncommittedproposal. Checkdepthamend62.1mm(36*(30+12+1)+10=1558),mass/coverageprovenance,wholecarrierinsteadnarrowwedges endcap,alignedversusstagger controls,frames/IDs/servicereservation vsconnected claims,20mm endcaprowandcolumntrunks,apertureadaptiveoriginandstaggerrotations0/22.5/45/67.5deg withrotatedsteeljoints. Assessqualifiedcore-plane samplesatlocalz2(physical29.7rects,aheadofrecess) versusfinitevolume/response,steelpathscreenifreported,unchangedFCalnoncoverageeta4. No genericdemandfor finishedengineering outsideprototype; concrete bugs,math/semantic errors and necessary limitationcorrections only. Currentcompactdraftprose will beformattedlater, do notspendtime styleediting. Read sources beforeauthorconclusions. No files/runtime/delegation/publication. Later exact code review followsseparately. Return initialfindings withinabout5minutes.",
  "deliverable": "Independent bounded design/claim findings for bothregions with exactrevisions and locators; noapproval.",
  "completion": "Concrete actionablefindings orno findings within assignedscope; actualchecks/limitations explicit."
}
```

## Exact implementation review assignment

```json
{
  "id": "HCALASSEMBLY-20261015-PhysVal-Code",
  "role": "PhysVal",
  "inputs": [
    "docs/design/DES-037-hcal-barrel-common-module.md",
    "tools/hcal_barrel/config.json",
    "tools/hcal_barrel/design.py",
    "tools/hcal_barrel/test_design.py",
    "tools/hcal_readout/config.json"
  ],
  "task": "Review completed analytical barrel/endcap HCAL design source at exact revisions: primarybarrelc83e6f4eaebdaa354217b79b963df15c6c3c0a96 in <barrel-worktree>; secondaryendcap7c7f0ba96b69dd754d6e25bd97cef4cfe502bcae in siblingnodd-hcal-endcap. Inspect source via gitshow/pinnedworkingbytes beforeauthorreports. Assess counts,sharedmaterialmass/steelownership,channelpowerstress/DAQscale,cornerandaperturecontainment,frame/IDmasks andcomparisonclaims. Barrelfixretainsmaxcentredcounts acrossphasecontrols byboundingactualrequestedshift; reportsactualvsrequested. Core-plane samplesatlocalz2 are explicit; no fullsolid/recess/nativewholeassembly/showerclaims. Scalarsteellengthbarrelanalytical;endcapsteelpathNOTRUN. Checkactualcorelookup againstindependentdirectpoints/finiteframes, signedeta andpropernegativeend mirror. Rerunonlyappropriatestandardlibchecks; no native/runtime/dependencies. Main addingdrawings/reports/governance withsamecode, notyetpresent linksdonot bythemselvesconstitutescientificfinding. Report concretecorrectness/claim bugs andscope limits withinabout8minutes; noedits/delegation/publication/humansignoff.",
  "deliverable": "Exact-revision independent code/scientific findings for bothnewregionaldesigns andactual controls run.",
  "completion": "Actionable findings orno findings withprecise source/impact andreview limits; noengineeringapproval.",
  "input_revision": "c83e6f4eaebdaa354217b79b963df15c6c3c0a96",
  "mode": "read-only",
  "writable_paths": []
}
```

## Exact implementation review assignment

```json
{
  "id": "HCALASSEMBLY-20261015-SysArch-Code",
  "role": "SysArch",
  "inputs": [
    "docs/design/DES-037-hcal-barrel-common-module.md",
    "tools/hcal_barrel/config.json",
    "tools/hcal_barrel/design.py",
    "tools/hcal_readout/config.json",
    "docs/design/DES-034-siw-service-envelopes.md"
  ],
  "task": "Read-only exactimplementationinterface review: barrelc83e6f4eaebdaa354217b79b963df15c6c3c0a96 in <barrel-worktree> andendcap7c7f0ba96b69dd754d6e25bd97cef4cfe502bcae in siblingnodd-hcal-endcap. Inspect physicaldomain/clearance/serviceownershipsource againstyourpreviousenvelopecontract. BarrelAlrails/endflanges/backcover disjoint fromsectorsteel/carriers,depth1558,corner4239.46,emptyrowcollector20mm andmatchedphaseclamping. Endcapannularframes,steelquarterjoint20mm vsrowstripsdoNOTremovesteel,adaptiveaperturepacking no clipping,properport/originRx(pi)androtatedlayerjoints. Quantitativepartial mass anddefaultcollectoractualunconnected versus claimedfeasible mustbeconsistent. Fullnativeengineeringnotrequiredatdesignstage. Readsourceatcommit, notuncommittednewdrawings; report realbugs/semanticinterface issues,notgenericfuturework alreadyexplicit. Noedits/delegation/runtime/publication. About6minutes.",
  "deliverable": "Exact-revision physical/service interface findings forbothregionalproposals.",
  "completion": "Concrete defects orboundedno-findings withactualcheckscope; noengineeringorhumanapproval.",
  "input_revision": "c83e6f4eaebdaa354217b79b963df15c6c3c0a96",
  "mode": "read-only",
  "writable_paths": []
}
```


## Local design closeout before publication

Exact source/config/export/figure hashes, source-ID and local-link audit passed.
Project validator:68tasks,39documents,21reviewrounds. Session validator:186pairs.
The existing selectedcandidate SVG remains deterministic and unchanged; the
regional overlay is separate. Token validation and local preview build pass.
Observed project tokens:620,754,236 input /3,545,169 output, total624,299,405 across
210recordedturns. This checkouthas186sessionrecords,68withoutusage. Currenttask
and specialist usage remainunknown; these are partial project observations.

Regional implementation/evidence is ready. Publication and final PRnumber/state
will be appended after the actual create/attach/push operations.


## Published regional PR

Created [draft PR84](https://github.com/asalzburger/nodd/pull/84),
“Calorimeter: design a barrel HCAL around the common readout module”, based on
`codex/hcal-realism-assessment` (common-module PR81). Attached it to this task.
Companion [PR85](https://github.com/asalzburger/nodd/pull/85) is a sibling,
not included in this diff. Published design/evidence head`9141a49cddc554adbf72187aed0dc3ef8ca2d233`.
GitHub reportedOPEN,draft,MERGEABLE,token-siteSUCCESS,deploySKIPPED andProject
validationIN_PROGRESS at that snapshot. This is not final-head hosted acceptance.

Tracking and candidateproposal links now record actualPR identifiers. The bounded
regionaldesign task is complete; engineering/detectoracceptance remainsopen.
Retarget regionalPRs to main afterPR81 merges, preserving bothindependent
contributions. Record-only publicationcloseout is located by this journal's
enclosingcommit. Local checkoutpaths inassignmenttext are normalized aliases;
full prepared prompts remained in tasktemporaryfiles.
