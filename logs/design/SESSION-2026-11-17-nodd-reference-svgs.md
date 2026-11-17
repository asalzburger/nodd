# Standalone nODD response SVGs

User: "Looks good - leave the report as is, but make two separate SVGs: SD(R)/mean(R) as is, but remove the ODD, only keep nODD versions; Underneath: reference plots in [0,1][1,2][2,3] over the same width, showing where the SD(R)/mean(R) was drawn from."

Start source d04614575e8fc3aed41ed79798def3fc461e3dc6; separate codex/nodd-reference-svgs worktree. Existing PR145 remains open/ready on main; this is its authorized figure follow-up, without another geometry/report edit or GitHub merge. Freeze every existing tracked report-directory file and the PDF byte-for-byte. New outputs live in a standalone/ subdirectory.

Interpret the three intervals as absolute primary pseudorapidity bands [0,1),[1,2),[2,3], covering all matched10000primaries once. FirstSVG preserves the original three fine0.05-bin nODD curves/pointwise intervals and axes, removes only ODD reference elements, and repacks the legend. SecondSVG has the same1000unitwidth, three adjacent band reference histograms of R divided by its own model/band mean; raw meanR/sampleSD and CV/zero/overflow counts are reported. Unit-mean rescaling preserves each bandCV; no calibration/fits, no newMC/bootstrap. All-event normalization, explicit tails/overflow; log-y displays sparse tails without replacing empty bins with events. Broad-band referenceCVs are context, not the fine-curve point estimates.

Derive histograms from the exact original/staggered Si-W saved-signal and LAr400savedH ledgers already hash-bound in response_comparison.py. Preserve H/Etrue and every zero. Fixed display edges of normalized response0..3 in0.025steps; explicit overflow above3, no truncation in moments. Bin3 includes endpoint3. No accepted report/figure/source/provenance files are changed.

## Implemented source and actual checks

Source91f5e1b3 creates two1000unit SVGs only in new standalone/ directory. Firstreuses acceptedDrawing with assertions removing4ODDcircles/3ODDerrorbars/1legendlabel, repackingonlylegend anddroppingODDfooternote; all3nODDPolyline coordinates are exact. Second threepanels retain3331/3353/3316events; zeros42original/42staggered/0LAr globally, none lost. Reproducesall180existingfine-bin N/zeros/means/sampleSD/CVs; unitmeanrescaling preservesbroadCVs andcounts+flows equaldenominators. All10oldreportfiles/PDFhashes remainexact. Both1400pxpreviews inspected: legibleaxes/labels/legend/stats, no overlap/clipping. Project111/54/24 andinventory69/104/55/12 pass. No newMC/bootstrap/calibration/dependencies.

## Exact-source review contract before dispatch

Explicit genericPhysVal, not verifiednativeprofile loading; rootauthors newsource.

```json
{
  "id": "PR145-PhysVal-reference-svgs",
  "role": "PhysVal",
  "input_revision": "91f5e1b34df65580ad0549880c7a69268ed8f3db",
  "inputs": [
    "docs/publication/emcal-findings/standalone/make_svgs.py",
    "docs/publication/emcal-findings/standalone/reference-data.json",
    "docs/publication/emcal-findings/standalone/nodd-width.svg",
    "docs/publication/emcal-findings/standalone/nodd-response-distributions.svg",
    "docs/publication/emcal-findings/standalone/render.json",
    "docs/publication/emcal-findings/standalone/README.md",
    "docs/publication/emcal-findings/response-comparison.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Review only the requested two standaloneSVGs at exact revision. User says leave report asis, firstfineSDR/meanRas-is withoutODD; second below samewidth with reference distributions in eta[0,1][1,2][2,3]. Verify all existing10report files/PDF unchanged fromd0461457, exactly3nODD curve polylines/intervals/coordinates preserved, noODD graph elements, matching1000unit widths and three referencepanels. Independently check rawH/Etrue source/hash/cohort, broadbands halfopen exceptfinalclosed, N3331/3353/3316 all10000, all42/42/0zeros and moments/histcounts/normalization/overflow. Referencex=R/ownmodel/bandmean preservesCV; ypercent uses allbandN, logemptybins omitted without fakeevents; broadpooledCVs explicitly distinct fromfinecurvepoints. Sourceledgers samehashes/paths as priorreview, now checking newband/hist derivation only. FixedECAL#cccc00 withconfigstyles, unbinnedmoments/no fit orcalibration. Rootvisuallychecked both previews build/nodd-reference-svgs/*.png. No edits/native/MC/newbootstrap/delegation or broadoldreport/CI re-audit. Return actionablefindings or closure with exactsource/actualchecks/limits.",
  "deliverable": "Bounded independent scientific/representation/preservation assessment of two newSVGs.",
  "completion": "Stop once newbanddata/labels/curve/reportpreservation are assessed; no human design approval."
}
```

## Independent result and accounting

PhysVal closes exact91f5e1b34df65580ad0549880c7a69268ed8f3db with no actionable findings. It independently verifies all10oldreportfiles/PDF unchanged; all3widthpolylines and180intervalpaths exact; ODD elements removed; bothSVGwidth1000. Exact3ledgerhashes and10000identicalprimarycoordinates; all9histograms/unbinnedmoments/CVs/zeros/flows reproduce,3331/3353/3316events,42/42/0zeros, zero under/overflows. UnitmeanCVinvariance, all-event percentages/logemptybins, broadvsfine labels andreadability pass. No source edits/native/MC/newbootstrap or broadoldassumption audit.

Rootreplay produces byte-identicalSVGs, everyoldreporthash/PDF8e5e5b40... unchanged. Swapped-source negativecontrol rejects before output. One exactcompleted currentreviewturn01a1ea5d-23a8-70d0-8552-71ef3a4c2267 is recovered and matched to visibleassignment/result, not timestamps alone:1,649,199input+7,615output=1,656,814total; cached1,614,080/reasoning1,277subsets. Oldowners/turns excluded and unchanged; activecoordinatorunknown, models/providers/clientversionunknown. Selectedvisibletext/operationcounts are allowlisted/redacted; no reasoning/context/rawarguments/results. Parent interactions are not childspawns.

PR145 remains the explicitly authorized existing report/merge-preparation task; newbody links the two standaloneSVGs while retaining the report. Metadata uses authenticatedgh because the integration's write capability was already unavailable. No separate external messages, GitHubmerge, auto-merge orhumanapproval performed. Newtaskbranch/session isolates this follow-up; oldcanonicaljournals are not rewritten.

Final local closure: project111/54/24, session302, inventory69/104/55/12, interactions122 with retention against mainf3ece1d6, tokenpreview579disjointdatedturns/3,249,405,443cumulative observed tokens PASS. Existing reportfiles remain untouched; no old canonical token owner changed. Currentreview1,656,814 observed total, activecoordinatorunavailable. Final hosted current-head status is checked after publication without changing any report artifact.
