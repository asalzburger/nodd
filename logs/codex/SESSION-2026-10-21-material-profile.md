# SESSION-2026-10-21-material-profile — Profile matched ODD and nODD tracker material recording

## Scope and evidence

The user delegated the Software investigation of slow nODD beam-pipe/tracker material recording, requiring a matched100-event ×100-neutral-geantino comparison with ODD, native profiling, reproducible timing/CPU/RSS and a Software pull request. Preserve every passive constituent and identifier; no material simplification or detector retuning. This characterizes the existing DRAFT / PROTOTYPE models governed by DES-024/025 and ADR-008.

The task worktree starts at fetched main e980c41f47605091e94d85a463e31cf0bdf2edd8 with no changes. Executed runtime source/build is the separate existing530080cfe16c7513228bf60238b99d4b9938538a checkout; its two previous availability journal files remain untouched. Exact client version/start time and per-turn usage are unavailable. Collection is contemporaneous and incomplete for token coverage; no private client state was inspected.

## Selected conversation

User request, paraphrased: identify why nODD tracker material recording is much slower than ODD using the same100×100, seed228, uniform eta[-4,4]/phi[0,360degrees], origin, one-thread setup; separate construction, initialization, transport, stepping and output; propose and verify a safe software response and deliver a Software PR. The coordinator communicated the stale preflight limitation, recurring association-scan hotspot, runtime XML/bootstrap sensitivity and completed controls as evidence arrived.

## Decisions and outcomes

Keep detector geometry/materials/IDs and generator/run lifecycle unchanged. Use the existing build and pinned ODD source, rebuild only the task-local unchanged ODD factory, standardize DDG4-first initialization, and expose guarded association reuse solely as an opt-in immutable-geantino experiment. Keep initial startup variants and failed diagnostics distinct from the matched benchmark. No scientific design approval or production acceptance is recorded.

## Commands and validation

Actual checks and commands are listed in the paired JSON and the execution observations below. ROOT outputs/full profiles remain ignored under build/jobs/material-profile; portable summaries, source/binary/input hashes and reduced stacks are curated in docs/validation/material-recording-profile. Native adverse checks occur after the reported timing interval and transport no changed fixture.

## Changes and revision links

The paired JSON inventories changed files and existing result commits. Git history locates this record's enclosing commit. No changes are made to shared installations or the dirty sister ACTS checkout.

## Token accounting

Client-reported exact per-turn counters are unavailable. Usage remains empty: observed input/output coverage for this task is unknown, not zero. No estimates or parent/subagent totals are invented; project-wide observed totals are kept distinct in the logging summary.

## Specialist assignment MATPROF-SoftEng-01

Explicit generic-agent role assignment from software-layout profile at 530080c. Native profile loading is not claimed.

```json
{
  "id": "MATPROF-SoftEng-01",
  "role": "SoftEng",
  "input_revision": "530080cfe16c7513228bf60238b99d4b9938538a",
  "inputs": [
    "software/source/detectors/src/PixelComponents.cpp",
    "software/source/detectors/src/ShortStripBarrel.cpp",
    "software/source/detectors/src/ShortStripEndcap.cpp",
    "software/source/detectors/src/LongStrip.cpp",
    "software/running/nodd_material_recording.py"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Inspect source geometry hierarchy/volume reuse and material recorder setup. Identify measurable scaling risks without changing geometry or materials. Compare with existing ODD source in sibling software/submodules/OpenDataDetector. Establish tracker compact scope and how to exclude magnets/calorimeters/muons faithfully. No runtime benchmarking (coordinator owns those runs), no edits, no further delegation. Read git snapshots for assigned nODD inputs. Additional ODD checkout identity must be recorded.",
  "deliverable": "Return source locators, volume reuse and hierarchy risks, exact ODD tracker-only selection recommendation; coordinator retains curated result in this session.",
  "completion": "Report actual reads/checks, revision identities, limits and no invented performance claims."
}
```

## Execution observations (ongoing)

- Preflight returned 2: changed setup/lock fingerprints; full DD4hep/Geant4 sources absent. Actual runtime verified: DD4hep1.38, Geant4 11.4.3, 12 installed dataset directories. Shared dependencies unchanged.
- Dedicated branch from fetched main e980c41f47605091e94d85a463e31cf0bdf2edd8. PRs77–80 are marked merged but main retains only the initial software layout; benchmark explicitly uses existing source/build at530080c. Previous untracked availability journals preserved.
- Primary nODD100-event ×100-track process started12:56:22 Europe/Zurich. Native samples use /usr/bin/sample (15s windows at2ms), attached with approved sandbox escalation after a restricted attach failed. One startup/first-event window and one steady-state window; raw profiles/ROOT remain ignored under build/jobs/material-profile.
- Separate diagnostic attempts retained: first native shim failed to link due unavailable dyld header, then library search/rpath issues corrected; RTLD_NEXT forwarding caused an ODD diagnostic crash and was replaced with normal dyld self-exempt direct forwarding. Derived ODD wrapper initially nested definitions too late for world material lookup, corrected by copying top-level definitions while preserving all original tracker includes except Solenoid. These attempts are not completed benchmark results.
- SoftEng read-only assignment confirms source-derived661,996 material volumes +18,703 assemblies; predicts flattening to649,614 world daughters. Runtime inventory is pending.
- Steady native sample:6192/6259 main-thread samples under UpdateCoupleTable;5471 exclusive ScanAndSetCouple;18 under event processing. This corrects the initial suspicion that steady15s/event was transport.

## Instrumentation correction

Early native timing trials exposed a measurement sensitivity: an early helper measured repeated cut scans around7.4s versus about15s in the original startup baseline; a hidden-inline control measured16.72s on its first scan. The initial attribution to changed weak accessor selection was provisional and is not established by the later native review. Final controls fix DDG4-first startup and use NDEBUG/hidden inline visibility; earlier startup variants are excluded from the matched comparison. A task-owned unfinished100-event instrumentation trial was stopped by approved SIGTERM; the primary100-event baseline continues. This correction changes no shared library.

The opt-in association-reuse prototype validates every logical volume's material, region, exact cuts pointer, registered region mapping and used couple, plus closed geometry, one tracking world, one active root region, unchanged cut status and table/material counts. It delegates to Geant4 on any failed precondition. Default benchmark behavior remains unchanged. Post-transport adverse controls temporarily replace a material pointer, region pointer and cuts pointer, then restore them; no altered fixture is transported or recorded.

## Specialist assignment MATPROF-PhysVal-01

```json
{
  "id": "MATPROF-PhysVal-01",
  "role": "PhysVal",
  "input_revision": "937422566fe0da577ec51862edf258631602026f",
  "inputs": [
    "tools/material_recording_profile/run.py",
    "tools/material_recording_profile/prepare_odd.py",
    "tools/material_recording_profile/native_timing.cpp",
    "tools/material_recording_profile/build_native.sh"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Independently assess matched benchmark protocol, scientific fidelity and the opt-in guarded reuse of Geant4 material-cut associations. Inspect the actual guard and possible invalidation gaps; assess what output equivalence and adverse tests must establish. No runtime jobs (coordinator has primary100-event runs active), no edits or further delegation. Additional immutable Geant4 v11.4.3 source may be read using official GitHub. Current ignored observations are supporting evidence only, identify them as such: build/jobs/material-profile/nodd-steady.summary.json and nodd-phases/inventory.json. Earlier unhidden native timing trials had a different observed cost and are excluded; the proposed weak-symbol cause was subsequently not established; current helper uses hidden inline visibility. Final100-event output/evidence is pending and will be sent for follow-up review.",
  "deliverable": "Return findings with severity/locators, validity limits and required corrections; coordinator retains assessment in session and report.",
  "completion": "Provide independent assessment of exact9374225 source, scientific claims and negative controls without granting sign-off."
}
```

## Specialist follow-up MATPROF-PhysVal-02

```json
{
  "id": "MATPROF-PhysVal-02",
  "role": "PhysVal",
  "input_revision": "f9826ca004a7d61c01a057472a975d28cfb0a602",
  "inputs": [
    "tools/material_recording_profile/native_timing.cpp",
    "tools/material_recording_profile/run.py",
    "tools/material_recording_profile/compare_output.py",
    "docs/validation/material-recording-profile/README.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Reassess corrections to your findings at9374225: energy-vector sentinel, table index/membership checks, in-place cut/null-couple/extra-region/open-geometry controls, and explicit original-update/energy-value fallback verification. Review report scope and exact-output comparison. No runtime jobs or edits. The ignored final guard evidence will be supplied once the active100-event baseline and final candidate close. Earlier eleven-control run passed, while final thirteen-control fallback test is running. Assess immutable single-world geantino harness only; do not generalize to arbitrary mutable Geant4 use.",
  "deliverable": "Return findings with severity/locators, validity limits and required corrections; coordinator retains assessment in session and report.",
  "completion": "Return fixed/unfixed findings, exact source revision, conditions on final evidence and scientific limits; no design acceptance."
}
```

## Independent review and diagnostic correction

PhysVal reviewed937422566fe0da577ec51862edf258631602026f and found a broader-use energy-vector invalidation gap and insufficient adverse controls. The f9826ca004a7d61c01a057472a975d28cfb0a602 response adds the sentinel, exact table membership and index checks, in-place cuts, null/stale couples, extra-region/open-geometry checks, and normal-update fallback instrumentation. Its thirteen-control diagnostic passed twelve checks but initially asserted an incorrect energy expectation: this geantino-only physics list has no gamma converter, so native Geant4 intentionally retains gamma energy cuts at-1 even after a user vector. The failed check is retained; the corrected test matches actual Geant4 v11.4.3 semantics instead of adding photon physics.

PhysVal's follow-up accepted the immutable-harness source scope conditionally and requested proof of ordinary API redirection, rather than calling the wrapper directly. A separate client dylib now calls public SetEnergyCutVector through normal linkage; the final sentinel control counts that interception. No altered fixture is transported. Final guard revalidation is running.

## Corrected guard result

All14 final native controls pass in nodd-validated-guard, including actual ordinary SetEnergyCutVector interception through a separate client image, fallback execution and Geant4-native absent-gamma energy values. All32 ROOT branches from the200-probe stepping diagnostic match the uncached control at zero numeric tolerance. Native phase intervals are retained before the explicit post-transport marker; the earlier incorrect postcheck expectation remains recorded separately.

## ODD runtime mismatch found and isolated rebuild

The queued unprofiled ODD benchmark failed during XML parsing (exit129). Its stack contained two Xerces3.3 installations with different Spack hashes. Earlier native preload controls had hidden that load-order failure. The source pin and advertised DD4hep/ROOT versions were insufficient to establish runtime compatibility. Built the unchanged pinned ODD factories locally under build/odd, using the same existing dependency view and RelWithDebInfo flags;12 build steps passed. No shared install or dependency was changed. The matched ODD benchmark is rerun with that explicit factory. The existing nODD baseline has completed100 events; all10000 probes and32 output branches exactly match the guarded result.

## Common bootstrap repeat

A fresh ODD factory alone did not resolve the mixed-Xerces parsing failure. Explicitly loading the existing DDG4 library before PyROOT succeeded: the task-local ODD factory completed100 events ×100 probes in13.5347s. The launcher now uses that bootstrap for both detectors. A complete nODD100-event repeat is running with the identical common bootstrap; earlier1569.917s nODD output remains a separately labelled diagnostic reference. No shared dependencies, materials or geometry changed. Final ODD native and guarded controls use the task-local factory.

## Native load-order sensitivity

The common DDG4-first baseline repeats around7.4s/event, compared with15s/event in the original startup sequence. Matching common library UUIDs establish binary identity; they do not establish the unresolved cause of runtime timing sensitivity. The final native helper is now loaded after DDG4 too, and an ODD five-event control confirms recurring cut-table interception and reuse still work. New matched-order nODD100-event reuse and two-event phase controls are running; final comparisons will use these rather than combining startup orders.

## Specialist follow-up MATPROF-SoftEng-02

```json
{
  "id": "MATPROF-SoftEng-02",
  "role": "SoftEng",
  "input_revision": "e2a01ae90f376914d53942ef81d64d424d2d13f1",
  "inputs": [
    "tools/material_recording_profile/one.sh",
    "tools/material_recording_profile/build_native.sh",
    "tools/material_recording_profile/native_timing.cpp"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Investigate observed native load-order performance sensitivity without running simulations or changing files. Original nODD100 startup without preload took15s/event in cut scans; DDG4-first bootstrap takes7.4s/event with the same G4run/G4processes_core/DDCore UUIDs. Earlier public-inline helper also took7.4; hidden-inline helper before DDG4 took16.5; final launcher places DDG4 first even with helper. Inspect native symbols/weak definitions and profile ownership using existing task artifacts and installed library metadata. Do not claim a precise weak-symbol mechanism without evidence. Source model/geometry is unchanged and final matched-bootstrap100-event run is active. The fresh ODD factory alone did not fix a two-Xerces parsing crash; DDG4-first fixes it. Additional source is read-only authorized runtime under sibling nodd-software-layout; no dependencies installed or modified. Supporting profiles: build/jobs/material-profile/nodd-steady.sample.txt and nodd-bootstrap-steady.sample.txt (new profile may finish shortly).",
  "deliverable": "Return measured versus inferred explanation and exact evidence locators/commands; assess loader claims for report.",
  "completion": "Clarify what symbol ownership/load-order evidence actually establishes and remaining limits; no simulations, edits or further delegation."
}
```

## MATPROF-SoftEng-02 result

The read-only review ofe2a01ae90f376914d53942ef81d64d424d2d13f1 finds the same association-scan hotspot before and after bootstrap (6192/6259 and5816/5881 main-thread samples). `nm -m`, `llvm-objdump --macho --bind/--weak-bind` and bounded disassembly show `GetMaterial()` is a strong external definition in libG4geometry, explicitly bound by processes_core; both profiles execute it with TLS access. The hot daughter reads are inlined. No precise weak-symbol mechanism is established. Both profiles retain two Xerces UUIDs,30F031B1-48B2-3379-908B-9AB81CA3BBCD andD3A4DD97-84D9-3E03-87E4-2B5366A307EB, in reversed load order. DDG4-first avoids the observed parsing crash; it does not remove duplicate Xerces. Report wording was corrected accordingly. Profile SHA-256: original68e764bac6dd226462fb6d44370f4df570c2f8c2ac60255a543da7954904f493; bootstrap ea5366782eb4bb6cf3725fc0b802c32e833c0d4f0f65ae3d5bc859e34c6f34d0. No new simulation or dependency change was made by the reviewer.

## Completed matched evidence

Both DDG4-first100×100 baselines completed successfully: ODD13.534724875s wall/13.956790s cumulative CPU/857407488 peak-RSS bytes; nODD810.953075875s wall/809.666490s CPU/7146323968 bytes. nODD steady99-event median7.425466625s. Final guarded nODD101.904982375s wall/102.289775s CPU/7165394944 bytes, steady median0.150192750s; ODD guard14.507962625s wall. Both detectors pass all14 post-transport guard controls. Initial candidate scan16.506s remains explicitly reported against7.409s uncached control; no unresolved startup penalty is subtracted.

Summarize.py verifies10000 probes per detector,100 per event, matching generated-bank hashes, origin, finite positive totals and sums recomputed from all steps. Compare_output.py passes all32 scalar/jagged branches at zero numeric tolerance for nODD baseline/reuse, ODD baseline/reuse and original-startup/final-bootstrap nODD. ROOT bytes differ by metadata and are not claimed equal. Native steady profile5816/5881 main samples under UpdateCoupleTable. Final two-event timers separate12.576s parsing,24.329s containing DD4hep build,2.870s conversion,35.748s voxelization,7.368s recurring cut update and0.0622s transport/recording; ROOT writer0.888s for the primary100-event nODD job.

The total CPU counter includes interpreter/preload startup before Python wall START; phase/event CPU values are interval differences. Timing ends before post-run loaded-library audit hashing, inventory and adverse checks; initial source/factory hashes remain included. Final report preserves these boundaries and the unresolved load-order mechanism. Geometry/materials/identifiers remain unchanged, DES-024/025 stay DRAFT.

## Specialist follow-up MATPROF-PhysVal-03

```json
{
  "id": "MATPROF-PhysVal-03",
  "role": "PhysVal",
  "input_revision": "25fa2d01ca9b135f070a8549d50dfe3b5af4ced2",
  "inputs": [
    "tools/material_recording_profile/native_timing.cpp",
    "tools/material_recording_profile/run.py",
    "tools/material_recording_profile/compare_output.py",
    "docs/validation/material-recording-profile/README.md",
    "docs/validation/material-recording-profile/results.json",
    "docs/validation/material-recording-profile/reuse-results.json",
    "docs/validation/material-recording-profile/guard-checks.json",
    "docs/validation/material-recording-profile/nodd-exact-output.json",
    "docs/validation/material-recording-profile/odd-exact-output.json",
    "docs/validation/material-recording-profile/bootstrap-output-equality.json",
    "docs/validation/material-recording-profile/provenance.json",
    "docs/validation/material-recording-profile/native-phases.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Final independent assessment of completed matched100\u00d7100 scientific evidence and immutable-harness guard. Inspect committed primary source/data before conclusions. Reassess prior conditions: separate ordinary SetEnergyCutVector client interception, fallback and native absent-gamma semantics; exact all32-branch numeric equivalence across all10000 probes for both detectors; integrity and source/binary/bootstrap identity; accurately qualified timing boundaries and load-order mechanism. Final DDG4-first baseline ODD13.5347s/nODD810.9531s; guarded nODD101.9050s. Guarded first scan remains16.506s versus7.409s native uncached; report states this unresolved sensitivity. Native review did NOT establish weak-accessor cause; both orders retain two Xerces libraries. No runtime simulations, edits, installations or further delegation. Review current committed revision using git show, no substituted working tree. Scope is an opt-in immutable single-world neutral-geantino harness only; no general mutable Geant4 claim or detector sign-off.",
  "deliverable": "Return findings with severity and exact locators, fixed/unfixed earlier review conditions, actual read-only checks and scope limits. Coordinator curates result into existing journal.",
  "completion": "Assess whether committed source and completed evidence support reported scoped results; identify material corrections needed without granting design/production acceptance."
}
```

## Publishing and repository checks

All28 project-record tests passed (115.921s), all33 logging/document controls passed after evidence curation, and session/project validators pass. Final loaded-image comparison finds all81 shared image names have equal SHA-256 between the two baseline processes. Tool integration creation returned GitHub403 Resource not accessible by integration; the authenticated local gh CLI is the fallback. This is a connector permission limitation, not an automatic approval-review rejection. No dependency or account permission was changed.

PR91 opened as a draft while final independent assessment completes: https://github.com/asalzburger/nodd/pull/91 . It is attached to this chat. PhysVal-03 confirms complete evidence checks and requests a timing-boundary clarification: initial steering/runtime and factory hashes occur inside total timing, while post-run loaded-library audit hashing is excluded. Report, tool guide, provenance and journal now state the actual boundary; measured values are unchanged.

## MATPROF-PhysVal-03 result and remediation

The separate read-only review assessed25fa2d01ca9b135f070a8549d50dfe3b5af4ced2 and supports the scoped immutable-geantino characterization. Earlier review conditions are resolved: four100×100 outputs, matching settings/generated banks, both detectors plus startup-order full10000-track ×32-branch exact numeric comparison records, all14 controls, separate ordinary energy-vector API interception, original fallback and absent-gamma semantics. Recalculated ratios59.916× baseline detector ratio,7.958× total reuse improvement and49.440× steady improvement agree. No remaining P1/P2 blocker was found within this scope.

Reviewer checked committed JSON, arithmetic/RSS/native summaries, frozen-helper source hash, shared image hashes and retained hashes of seven metric files, four ROOT files and four native timing files. No simulations or ROOT comparisons were rerun by the reviewer; no files changed. Working-tree journal/library-check additions were explicitly excluded from that reviewed snapshot. The added library-check JSON records the coordinator's separately executed81-image check.

The only P3 finding is corrected in the final report/tool guide/provenance/journal: post-run loaded-library audit hashing is outside timing; initial source/factory hashes remain included. Native helper and generator/recorder code are unchanged from the reviewed revision. The unresolved bootstrap mechanism, two Xerces images, first-cut16.506s versus7.409s and shared-host limits remain explicit. This assessment supplies no mutable-Geant4, production or detector approval.

## Journal schema correction

The first manual-review closeout incorrectly encoded the assessment as a PASS command with no exit code. Session validation rejected it, and two session/document tests errored for the same metadata issue. The dependent shell sequence continued and committeda145727; this mistake is corrected in a normal follow-up commit rather than rewriting history. The assessment belongs in activities/narrative, without an invented process exit. The actual failed validator/test outcomes are retained and checks are rerun. Benchmark numbers, comparisons and source are unchanged.

## Closeout

Corrected session validation and all33 logging/document tests pass. Local tool controls3/3, project-record controls28/28, project validator70 tasks/39 documents/21 reviews, workflow validation and observed-token dashboard validate/build pass. Session summary contains193 partial-coverage records and225 observed project turns (688392720 input,3924118 output); this task's exact input/output remain unknown and are not inferred from those historical totals.

Software PR91 contains the completed report/tools/evidence and paired journal, with independent review target25fa2d0 and normal metadata corrections retained in history. Tracking marks the requested capability/evidence task completed; no design states advance. Initial hosted token-site succeeded and project build was still running when this journal closed. Final metadata push will rerun checks; no unobserved hosted success is recorded. No runtime jobs remain active. Human PR review and optional upstream/environment/factory follow-ups remain separate from this completed measurement.

## Token-accounting correction — 2026-10-21

The user requested token accounting on PR91 before their merge. Exact closed-turn usage is now recovered through the authorized read-only local workflow from this chat and its two recorded specialist children. This supersedes the original unknown-usage statements for eight completed turns; the original narrative is retained as the historical closeout state. Original profiling/PR delivery and the two explanation follow-ups contribute three parent turns; recorded SoftEng assignments contribute two turns, and PhysVal assessments contribute three. Parent/child edges, exact agent paths and the retained assignment contracts establish attribution; timestamps only corroborate it.

The [inventory](../usage/USAGE-2026-10-21-pr91-accounting.json) records267 verified requests, ten ignored repeated snapshots and no outside-turn events. All streams reconcile independently from zero; eight disjoint entries are imported exactly once through the logging CLI. Observed input41,308,128 + output205,567 = total41,513,695; cached input40,301,824 and reasoning output100,184 are subsets. Replaying the import adds zero entries. The current accounting turn remains active and excluded. Model/client version, complete device history and billing equivalence remain unknown. This is accounting only; all benchmark/scientific results and DRAFT boundaries are unchanged.
