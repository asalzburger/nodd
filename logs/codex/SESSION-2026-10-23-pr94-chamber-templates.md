# SESSION-2026-10-23-pr94-chamber-templates — PR94 chamber-template review response

## Scope and evidence

Started from clean `e168107549205d424d51077d31db6dbc64b72765` on existing `codex/muon-dd4hep-prototype` worktree. Re-read AGENTS/PROJECT and the DES039/040 implementation contract; no closer AGENTS files exist. PR94 is now ready for review by human action; preserve this state, reviewers and base branch.

## Decisions and outcomes

Address comment6360225046 as a software representation refactor:22 shared chamber shapes,21 phi orbits,56rows including6longitudinal loops,936unchanged placements/IDs. Source/world-vertex equivalence is checked at unchanged1e-10m tolerance; shape matching uses exact source representatives within1e-12m, with actual maximum1.77636e-15m. Smaller hardware-clearance shapes remain distinct templates. No material, sensitivity, magnet or engineering-signoff change.

Core XML decreases583236→28900bytes and5639→255lines. Initial native run verifies22sharedVolume/Solidobjects,936sourcevertex/ID/recoveredframe matches with max1.68520e-14m,288coil primitives,25248occupancy probes andzerooverlaps.1000persisted20GeVgamma events reproduce the prior primary bank and event-by-event particle multiplicities.

## Commands and checks

- Git fetch firstfailed sandboxDNS; approved network retry succeeded. No remote source changes; PRhead matches local start.
- acts-spack preflight warned changedsetup/lock fingerprints. Actual fresh activation verifiedDD4hep1.38/DDG4/ROOT6.40.04/Geant4 11.4.3 and12datasetpresence checks; no sharedinstallation changes. Sandboxsysctl/ps warnings retained.
- First build failed XML h.child plain-string/UTF16 mismatch; explicit xml::Strng_t fixed it. Rebuild and native run01 succeeded.
- Generated checked-incompact; all15focused export/native/runner tests pass. Tests mutate actualXML then recompute its hash to ensure semanticverification catches badrefs/counts/phase/pitches/units/vertices/identities.
- New source inventory/representation comparison verifies all originalmanifest entity fields, source hashes, counts, toroids and materials unchanged.
- Initial project/session validators pass; no designapproval supplied. Frozen-source replay and independent exact-revision assessment follow this snapshot.

## Source and changes

Scientific input stays PR90 mergecae3a72f3b1c98edaf9bc28a84d019142606ba25, geometrySHA7b2b0de109a5ec4a908e4f91a05e9caf9bdedfa6141b09d7c82a98b56e7cfc02. SoftEng implements5ownedfiles; coordinator owns regeneratedbundle, runtime/audits, docs/tracking/journal and PRmetadata. No nativeprofile loading claimed; rolemandate explicitly passed to genericagent.

## Usage and follow-up

Exact disjoint finalized per-turn client counters are not exposed for this active turn or specialist; usage remains empty, not zero. No estimates or privateclient state collected. Complete frozen-source replay, independentreview, mandatorymetadata/site checks and push the reviewresponse to PR94. No reviewer/issue messages authorized or sent.

## User request and review

User: “PR94has comments, and good ones!” Retrieved current PR/body/comment/reviewthreads. One top-level comment requests reusable shapes and phi/longitudinal loops; no inline threads or review submissions. Human changed PR fromdraft toready; preserve that state. Noauthorization to message reviewers inferred.

## Specialist assignment

```json
{
  "id": "PR94-TEMPLATES-SoftEng",
  "role": "SoftEng",
  "input_revision": "e168107549205d424d51077d31db6dbc64b72765",
  "inputs": [
    "docs/design/DES-040-muon-chambers-frame.md",
    "tools/muon_dd4hep/export.py",
    "tools/muon_dd4hep/validate.py",
    "tools/muon_dd4hep/test_export.py",
    "prototypes/muon/Muon.cpp",
    "docs/validation/DES-040/sketched-stagger-2026-10-20/candidate/geometry.json"
  ],
  "mode": "write",
  "writable_paths": [
    "tools/muon_dd4hep/export.py",
    "tools/muon_dd4hep/validate.py",
    "tools/muon_dd4hep/test_export.py",
    "tools/muon_dd4hep/templates.py",
    "prototypes/muon/Muon.cpp"
  ],
  "task": "Address PR94 comment6360225046: XML currently repeats936full shapes/matrices. Factor22centred shape templates(15barrel+7endcap), regular phi/z placement loops, explicit irregular/smaller chamber templates. Preserve actual936source prismatic worldvertex sets and chamber/source IDs; native tolerance1e-10m unchanged. Group matching tolerance<=1e-12m using exact unrounded source representative; source native transforms may require canonical offset/recovery. Reuse nativeSolid+Volume pertemplate, stable per-placementDetElement/node names and IDs. Derive recurrences from actual source; no naive eta regularization or repacking. Prefer readable compact schema: template definitions plus barrel/endcap orbits/rows with phase,pitch,count and ID/source-name pattern; explicit placements only for genuinely nonregular source. Failclosed expansion/native audits cover936sourcecells, duplicate/missing IDs, invalid refs/counts/phase/pitch/basis, rarecutcases; test equivalence and meaningful reduction. Keep exact source fields in expected manifest, add template/offset/loop provenance. Mainowns compact regeneration,runtimeexecution,docs/reports/logs/CI/PRmetadata. You own listed5files only; agree any extra paths. No changes toroids/physics/scientificsource; no commit, no furtherdelegation. Read uncommitted DES040 refactor contract explicitly as current authorized software plan; pinned scientific source stays e168/PR90. Communicate schema/nativevalidation changes early.",
  "deliverable": "Focused implementation +controls and handoff: schema, counts/reduction,actualtests,changedpaths,limits; coordinator regenerates compact and runs native checks.",
  "completion": "All936sourcechambers reproduced with22orjustifiedtemplatecount and substantial XML reduction; focused tests pass except committedbundle test until coordinator regenerates; no unrelated changes."
}
```
