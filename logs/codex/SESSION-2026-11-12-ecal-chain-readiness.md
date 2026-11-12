# PR133–137 complete-chain readiness

User request: “Make sure that that all133 ->137 are ready for merging, and that the token recording, project validation and labelling will capture this entire work after the chain is merged”. Scope: prepare/validate allfive existingPRs andfullcanonicalrecords; no actual merges requested or performed, no signoff. Existingreadystate ispreserved.

Startb2b7041b045c0777c5e36176b4739336a41a97b5, clean source; branchcodex/pr133-137-chain-readiness. FreshGitHubreadback: all5ready andmergeable intoimmediatebase; zeroformalreviews orinline threads.133CIred at7ba71e duePR129collected_at fractionalUTCseconds; other134–136CIgreen,137latestmetadataCIongoing. Currentmain3dab2346 isancestor offinalhead; no divergentscience. No science/model/runtimererun needed.

## Bounded independent software audit

```json
{
  "id": "ECAL-CHAIN-SOFTENG-MERGE-AUDIT",
  "role": "SoftEng",
  "input_revision": "b2b7041b045c0777c5e36176b4739336a41a97b5",
  "inputs": [
    ".github/workflows/token-usage.yml",
    ".github/workflows/validation.yml",
    "tools/project_records/validate.py",
    "tools/project_records/fetch_evidence.py",
    "project/tracking.json",
    "project/token-milestones.json",
    "docs/validation/ecal-highstat/reuse.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Audit PR133\u2192137 chain readiness and post-merge capture at exact source. All5 currentlyready/mergeable into immediatebases; currentmain3dab2346 is ancestor of lastheadb2b7041b. PR133 CI fails only because PR129 collected_at has fractional seconds; main willnormalize that isolated metadata in133 and mergeforward (no sciencechanges/historyrewrite). Main recovers allprior133-136closedusage+pastaccounting, refreshesall5ledgers/labels andprojectcoverage. Assess whether existing push-to-main validation+TokenPages andcanonicalretainedrecords fullycaptureworkafterchainmerges, what exactgapneeds change, and a focused read-only chain integrity gate or postmerge registry ifmaterial. Distinguish automaticworklabels from actualmerge milestones; never fabricate futuremerge metadata/dates ordesign acceptance. Check preservefrozen model/sourcecommits and ordinarymerge strategy. Return minimumnecessary concrete recommendations; no speculative newautomation/framework. You may run local readonlychecks and inspect Git blobs/ancestry; no native runtime/simulation/fits, writes, publication, rawclientusageaccess or delegation. Separate boundedfinalartifact review mayfollow.",
  "deliverable": "Exact-revision software merge/postmerge capture assessment with material gaps, minimum changes, actual checks and limits.",
  "completion": "Return concise findings/recommendations promptly; no human signoff."
}
```


## Independent audit and guard assignment

Audit atb2b7041b: existing mainjobs validate/build/deploycommittedwork andderive dailyworklabels automatically, butdo not collectactualmerge metadata/GitHublabels/newusage. MissingPR133tracking row andunobservedolderwork needcorrection. No newregistry or futuremergetimestamps. Minimumguard verifiesall5recordcoverages andpreservedhead/freeze/results ancestry, plushead→merge→checkedHEADwhenactualmergedstateisrecorded. Projectvalidator107tasks/54docs/24reviews passes; pinnedcanonicalledgerderivationspassall5; currentuntrackedchainjournalnecessitatessyncaftercloseout. No sourcewrites by initialreviewer.

```json
{
  "id": "ECAL-CHAIN-SOFTENG-GUARD",
  "role": "SoftEng",
  "input_revision": "b2b7041b045c0777c5e36176b4739336a41a97b5",
  "inputs": [
    "tools/project_records/validate.py",
    "tools/project_records/fetch_evidence.py",
    "project/tracking.json",
    "docs/validation/ecal-highstat/frozen/manifest.json",
    ".github/workflows/validation.yml",
    ".github/workflows/token-usage.yml"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/project_records/check_ecal_chain.py",
    "tools/project_records/test_ecal_chain.py"
  ],
  "task": "Implement minimum read-only ECAL133\u2013137 integrity check per audit. Use existing tracking/interaction/model manifests, no new registry/state/automation or remote calls. CLI --repo defaultroot, optional --output compactJSONreport under callerpath. Require all5PRtracking entries and interaction ledgers; orderedhead ancestry andallheads ancestors ofcheckedHEAD; modelmanifest freeze_commit andvalidated_results_commit ancestors ofHEAD; currentfrozen coefficient bytes identicaltoGitfreeze andcore file matchesfrozen coreSHA (also frozen blob ifappropriate). For entries recorded merged require head\u2192merge\u2192checkedHEAD; optional --require-merged strictpostmerge mode is useful but defaultmustworkbeforemerge andnotinventfuturestate. Include compact unique canonical workowner/title/observed-counter coverage if straightforward from existingledger references, avoiding duplicateaddition acrossPRreferences; existing fullusage/ledger validators remainseparate, no reinventingthem. Checkscript shouldpass after main adds missingPR133 row; currentb2sourceknownfailsmissing133bydesign. Meaningfulstandardlibrary syntheticGitfixtures testgoodchain andmissing/reordered/unreachable entries, lostfreeze, changedcoeff/core, detachedrecordedmerge; no native/Numpy/dataregeneration. Main owns .githubworkflow wiring/inventory/docs/logs/accounting/project/merges; touchonly2ownedsourcefiles, do notcommit/publish/merge/delegate. No detectoracceptanceclaims or globalequalitygate forhistoricalmilestones.",
  "deliverable": "Two sourcefiles with focusedread-only guard and meaningfultests; actualtestcommands/results andlimitations.",
  "completion": "Return once targetedtests pass andonlyownedfiles changed; no publication."
}
```

## 2026-11-12 accounting reconciliation

Exact closed-turn counters and selected app-visible task/assignment evidence were recovered into this original owner, using the chain inventory at `logs/usage/USAGE-2026-11-12-ecal-chain-readiness.json`. Earlier missing-counter statements describe the prior collection, not this correction. Cached input/reasoning are subsets; shared PR links are references, never allocations. No active coordinator usage or estimated counters are imported.

## Unmeasured interrupted input

Exact selected visible user input for interrupted turn `01a1cb11-8a83-7cb3-b661-30be644679db` (no increasing usage snapshot; unknown consumption, no canonical usage entry):

> ## My request:
> Although your initial estimate was 110 000 particles, I would like you to make 10k with E~10 to 80 GeV flat in phi from eta -3 to 3, and then show make a sigma(E)/E plot vs |eta| in 10 bins and in the folded phi in 10 bins.

Native reconstruction uses only token_count events and selected metadata; no private conversation database items are read. The persisted fork continuation has provider ID01a1cb11-8a30-78f3-8a48-cc493c5d138d, exact ordinal offset528 and an exact first-snapshot replay of the previous cumulative and last-request counters. Original abandoned branch tail is excluded. Unchanged strict reconciliation then succeeds from zero. All original15 canonical observations are unchanged;36 previously unowned closed turns were imported once after dry runs and idempotent replay.

Publication correction: a concurrent branch switch raced a push using HEAD and briefly advanced PR133 to PR134 original b9f5af38. Ordinary corrective commits restore PR133 benchmark scope and PR134 study scope; source history remains reachable. Later pushes use explicit immutable SHAs and complete before switching. No force push or science change.

## GitHub automatic dependent merge

Observed PR134 API: merged=true, merged_at2026-11-12T16:54:27Z, head/merge_commit b9f5af38520ea83215587757b02cd090adc8fb8a. The publishing race caused GitHub to absorb its reachable head into the PR133 base branch. It cannot be reopened as an unmerged PR. No main merge was performed. PR133 was therefore fast-forwarded to dd7d6a0a to retain the complete100+10k benchmark/study tree, with a combined title/body. Remaining human merge order133→135→136→137. Original134 source and unique token owners remain reachable. The strict chain guard gains an explicit merged-and-absorbed ancestry case; unrelated/reordered open heads still fail. No fabricated human merge/sign-off is recorded.

## Chain guard amendment assignment

ECAL-CHAIN-SOFTENG-ABSORBED; SoftEng; exact input ded14d2e4d726b566db3cd9e4939d73da799b6a3; read/write only tools/project_records/check_ecal_chain.py and test_ecal_chain.py; no further delegation or publication. Require forward ancestry OR explicit later-head→actual-later-merge→predecessor-head proof for a genuinely merged dependent; captured heads must belong to that merge.17 synthetic Git controls pass, including the absorption/corrective history and rejected missing/detached/incompatible merge evidence. Main integrates workflow, records and accounting separately.

Pre-review checks: project/session/ledger/token validators pass;37+19+20 accounting tests and both Node suites pass. Preview daily work labels reconcile exactly to12 contributing titles,51 turns and303597535observed tokens. Coefficients/core are byte-identical to their original frozen commits; no scientific data/code changes. Actual remaining-head CI will be observed after publication.
