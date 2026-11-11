# SESSION-2026-11-11-tracker-placement-reuse — issue #130

## Request, starting state and interaction evidence

GitHub issue [#130](https://github.com/asalzburger/nodd/issues/130), authored by
`asalzburger-review`, exact public body: “Given the finding of #129 - can you
investigate if a similar placement strategy wtih reusing of repeated structures
can also be applied to the Tracker and lead to a similar G4 initialization
speedup ?” The same named reviewer applied `agent_task` at
2026-11-11T05:29:55Z, public event `35764571579`. Request `130-35764571579`.
The supplied snapshot has no issue comments. The runner's user instruction
requires isolated work, actual checks, curated evidence and a draft-PR title/body;
the host publisher owns commit/push/PR creation and interaction-ledger assignment.
No publication, comment, label, configuration change or design approval is performed
by this sandboxed session.

Selected visible assistant response, exact: “I’ll inspect #129’s findings, the
tracker construction code, and the applicable design constraints, then test what
I can in this worktree. I’ll prepare a draft-PR package with a clear distinction
between measured results and proposed optimizations.” Subsequent visible updates
report the runtime warning/re-verification, fresh baseline build and the strict
8,064-module repeat count. These are curated messages, not raw client rollouts.

The task branch is `codex/agent-task-130-35764571579`, starting clean at
`3dab2346c4a08fd24898a7842906601884708a7d`. Root AGENTS.md is the only applicable
AGENTS.md found. PROJECT.md, DES-025, DES-043, ADR-003, the current tracker
README/validator, PR129's maintained evidence and the historical material-profile
report were consulted. M0 remains unclosed. Work is limited to characterization
and an unsigned software-experiment recommendation; maintained geometry is unchanged.

## Public context and provenance

Read-only GitHub connector `github_get_pr_info` and `github_fetch_pr_comments`
refreshed PR129. It is merged at the input revision; its single public review is
`asalzburger-review` APPROVED, review `5854134448` at 2026-11-11T05:07:42Z.
That review belongs to PR129, not this investigation or a tracker design approval.
The retained report gives the ECAL-only map interval 3953.835→23.018 s. No tracker
speedup is inferred from it. Public GitHub identities are kept distinct from the
unnamed runner user and the publishing account `asalzburger`.

No external scientific source/parameter is introduced. Provenance added by this
session is the pinned source audit, strict XML recipe counts, current runtime
checks, locally built factory/input hashes and native phase/count observations.
Raw XML, expected inventories, sensor/event payloads, compiler outputs and full
logs remain ignored under build/issue130 or task-local temporary storage.

## Specialist assignment before dispatch

I130-SE01, explicitly selected SoftEng role, input revision
`3dab2346c4a08fd24898a7842906601884708a7d`. Read-only; owns no files.
Inputs: detector/src/PixelComponents.cpp, PixelBarrel.cpp, PixelEndcap.cpp;
prototypes/short_strip_barrel/ShortStripBarrel.cpp,
prototypes/short_strip_endcap/ShortStripEndcap.cpp,
prototypes/long_strip_barrel/LongStrip.cpp; DES-025, DES-043 and the PR129 report.
Question/deliverable: cited audit of all current reuse, assembly flattening,
identifier/DetElement/ACTS constraints and prioritized isolated prototypes.
Complete when every tracker factory family is assessed, without predicting timing
from source counts. The child read the complete prepared assignment and role
mandate. Native selection was exposed; actual profile loading is not independently
verified. No nested delegation or runtime activation was assigned.

Result: no tracker template cache found; the long-strip groups map only groups
placements. Real mothers, beyond assembly reuse, distinguish PR129. Prioritize
explicit local short-strip barrel or pixel recipes, retain instance DetElements
and packed IDs, and replace name-based validator associations with equally strong
instance-provenance checks if sharing is implemented. The report retains exact
source locators. Child actual checks: read-only Git verification and git-show
source/design/validation inspection at the full input revision; no timing claim.

## Commands, actual checks and limitations

Applied the nodd-coordinate, nodd-design-evidence, nodd-review-validation and
acts-spack skills. Preflight exited 2: changed/unreadable setup and lockfile
fingerprints. This warning was shown before dependent work. Actual activation
then identified DD4hep 1.38 /3yd4hz3 and Geant4 11.4.3 /wfg55xi; DD4hep/DDG4 imports
passed and all 12 dataset presence checks reported installed. Shell setup emitted
sandbox-denied sysctl/ps host-detection warnings. No shared dependencies were
installed or modified and registry fingerprints were not rewritten as a shortcut.

The first workflow prepare command used unsupported --output; rerunning with
stdout redirection validated the assignment. An initial source glob referenced
nonexistent detector/factories; the tracked detector/src and prototypes paths
were used thereafter. These were invocation/discovery errors, not geometry failures.

Fresh task-local CMake Release configuration and all five factory targets passed.
The existing macOS native timing helper built successfully. Static cut-couple reuse
is explicitly disabled in the DDSim probe. Its one geantino forces first-run
initialization; no physics-response claim follows from that event.

Three new controls pass: mapping interval extraction, rejection of missing/ambiguous
mapping records, and recipe keys retaining descendant IDs/materials/cuts. The
tracker suite and native measurements are recorded on completion below and in
the paired JSON. The full recipe and measurement definitions live in
[the report](../../docs/validation/tracker-placement-reuse/README.md).

## Outcome and next actions

The source audit and strict recipe screen establish concrete reuse opportunities,
not a speedup. The short-strip barrel has 8,064 identical strict local module
recipes with descendant IDs retained; unique instance names/outer poses are excluded.
The report proposes isolated assembly-caching and real-mother alternatives as
separate controls, with no maintained detector integration. A future real-mother
change needs SysArch containment/service assessment, native equivalence/material
checks and ACTS navigation checks. Human review decides whether to commission
that experiment. No human sign-off or acceptance is recorded.

## Token accounting and publication boundary

The client exposes no exact per-turn input/output counters, stable client turn/thread
IDs or actual execution-model evidence for this parent or its specialist. Usage
stays empty; this means unknown, not zero. No private client state is collected.
The session summary is run at closeout; repository-wide historical observed totals
must not be presented as consumption of this task. The host will assign the actual
new draft PR number and create/synchronize its individual interaction record;
issue130 is not treated as a PR ledger number.

## Additional execution and validation evidence

The initial native probe failed before construction (child exit -6): inserting
only libNativeTiming left an unresolved Xerces symbol. The maintained profiler
one.sh preloads DDG4 before the helper. probe.py now uses that explicit order,
records both library hashes and uses a fresh output directory. The failed log
is preserved locally; it contributes no timing result.

A first environment-provenance command looked for spack.lock below .spack-env;
the node registry identifies it at the environment root. The corrected command
succeeded and recorded current setup/lock/header hashes, ROOT 6.40.04, Python
3.14.5 and dataset presence. No dependency change followed the warning.

An initial inventory refresh rejected a documentation directory as a code family.
The existing inventory schema reserves paths for discovered families. The new
validation recipes are instead explicit evidence/source entries under CHECK-PROFILE;
no validator rule was changed. Refresh and check then passed for 68 components,
101 code families, 52 reviewed inputs and 12 source pins. nlohmann/json 3.12.0
is now listed for the existing native inventory helper's serialization dependency.
Refreshed fingerprints are not used as execution evidence.

Project-record validation fails because the isolated Git store lacks existing
historical merge commit 78bc60bb6da0c9d234baf00d37cadea9dd4964b4. The reference is
unchanged from the input revision. It is not deleted or fabricated to pass a gate;
the host needs full historical objects to rerun this validator. Interaction-ledger
validation passed for 111 PR records. Token data validated and the preview built
under _site/issue130-token-preview; these checks concern historical observed
accounting, not this task's unavailable usage and not detector performance.

Git diff confirms no changes to detector/, prototypes/ or software/running/ from
the input revision. Generated XML, expected inventories and local binaries are
confirmed ignored. No staged files, commits or publication actions are created
by the sandboxed agent; the host publisher owns those steps and their final
new-object inspection and per-PR interaction synchronization.

## Separate interpretation assignment before dispatch

I130-PV01, PhysVal, full source input 3dab2346c4a08fd24898a7842906601884708a7d.
Read-only; owns no files. Primary inputs: DES-025, DES-043, the retained ECAL
wedge report and the dated material-profile report. Secondary target: immutable
proposal/method snapshot i130-physval-v1 with per-file SHA-256, including README,
strict counts/provenance and probe/steering/recipe/test code. Native timings are
explicitly not yet supplied. Deliverable: benchmark/interpretation assessment,
unsupported claims and required corrections, without a gain or approval claim.
Completion: assess baseline/candidate requirements, ID/material safeguards and
uncertainty limits; return source revision and snapshot identity. Final results
will follow as a separate pinned handoff. The assignment helper passed before
spawn; the role is explicitly selected, without claiming verified profile loading.

I130-PV01 result: the separate PhysVal context found no blocking scientific claim
in its v1 snapshot. It verified six hashes and passed all three parser/recipe
controls; it performed no runtime measurement. It required one-diagnostic-run
wording, rounded prose, explicit concurrent-task/shared-host limits, distinct
inclusive phase observables and unchanged interpreter/DDG4-first loading order
in future A/B. Total path count is not full per-sensor identity equivalence.
Reviewed v1 README SHA-256 418be0b760d06bf7f3f820c89f27cfecd694680f397cb52dadb47c052f3fd747;
results 7aaaeda50fe4303d85549a276fdc2ea9857acf08ae029a86f8038cb4fc7daab9;
probe e969d2827ceaae2d12bcfc4960d61058d3b0e69c26c25712fec1996479a76a00.
Final native results are outside that snapshot and will have a separate handoff.

Because this is the next related tracking update after PR129's observed merge,
its PR metadata and stale ready-for-merge next action are reconciled from the
read-only connector response: final head 1fb0630ef4ef4dbc5d0f9dac5032ecedca258252,
merge 3dab2346c4a08fd24898a7842906601884708a7d at 2026-11-11T05:53:28Z.
No new human approval is inferred; recorded review/evidence revisions remain distinct.

## Final-results handoff before dispatch

I130-PV02, same separate PhysVal role, source input
3dab2346c4a08fd24898a7842906601884708a7d. Read-only; no owned files.
Primary governing inputs remain DES-025, DES-043, PR129's ECAL evidence and the
dated material profile. The immutable v2 snapshot contains ten hash-pinned files:
revised report/results and unchanged profiling/count/control code, plus native
timing.json, native-phases.jsonl, inventory.json and full probe.log for local
inspection. Raw log is not committed. Question/deliverable: assess the completed
one-event baseline, phase boundaries and limited closure/mapping conclusion,
examining raw evidence before the narrative. Complete when claims, concurrent-test
limits and absence of an A/B gain claim have been checked and corrections returned.
No runtime, writing, further delegation or approval is assigned. Helper preparation
passed before the follow-up dispatch.


## Completed local baseline and checks

The corrected probe-2 exits 0 and resolves 46,682 sensitive paths in 24.9798 s.
It observes one native event-manager interval, 0.1058 s. Native first closure/
voxelization is 186.6867 s, initial cut-table update 29.5030 s, inclusive first
RunInitialization 307.7468 s and inclusive Initialize 41.6447 s. Converter 14.8758 s;
two XML parse calls total 88.9557 s. Complete subprocess wall 553.0544 s includes
inventory/JIT/output/teardown. These are one instrumented observation, not means
or uncertainty estimates; repository export tests were active during early
startup, and other host load was not measured. Native counts are 617,019 logical
volumes and 604,000 world daughters. Inventory is pre-first-run, so its zero cut
couples precede the measured cut-table build; it does not imply absent cuts.

The completed 22-test tracker suite exits 0 in 651.047 s. Three new pure-Python
controls pass. All five fresh Release factory targets, native timing helper and
fresh maintained export succeeded. No full overlap, all-sensor transform/material,
ACTS conversion/navigation or response-equivalence rerun is claimed for this
unchanged-geometry characterization. Those gates remain required for a future
candidate. The paired JSON retains exact commands and statuses.

The result is an investigated, reviewable proposal: strict short-strip barrel
module caching is concrete; real-mother grouping deserves a controlled test of
closure/fanout. Neither a candidate nor its speedup is measured here. The legacy
ECAL multi-thousand-second map cost is not reproduced by this tracker observation.
No production integration or human approval follows from the source audit,
independent assessment or checks.

The session summary reports 280 repository sessions, 511 historical observed turns,
2,788,479,704 input + 12,147,127 output = 2,800,626,831 observed total tokens; 93 sessions
have no usage observations, including this task. Cached/reasoning counts are
subsets. These repository totals are not task consumption. Exact parent/specialist
turn counters remain unavailable and usage stays empty.


## Final independent assessment and artifact review

I130-PV02 independently verified all ten final snapshot hashes, examined raw
local scalar/log evidence before the narrative, and checked exact equality of
results.json with timing/native-phase/inventory artifacts and recipe histograms.
It confirmed one processed event, completion marker and exit 0. No blocking
scientific correction was found. The interpretation remains one diagnostic
baseline with no demonstrated gain; mapping lies inside geometry initialization,
and closure/cuts inside run initialization. No runtime, file edits or human
sign-off were performed by the reviewer.

Reviewed README SHA-256:
1fe62f7798a1b2448b9714d2f8f20c483b1f416ce00269dea05d89730b146102;
results 1f826c2f40a4ed46d1f689c9172daf87ecb9fed8973ee0210138bd1def8b9d2e;
native phases fd8c14b357d5c35ef01a40c9a355aaeda8d9283906da162ea1e214ff19ad4e4b.
The reviewed report/results bytes remain unchanged at local closeout.

New reviewable files were inspected as UTF-8 text with no binary/event payloads
or trailing whitespace. The largest new file is the curated narrative (under
20 kB); measured results are under 10 kB. Existing inventory/tracking diffs contain
only related metadata. git diff --check passes, production detector/prototype/
running source matches the input, and no files are staged. Raw compacts,
expected inventories, logs, event output, libraries and token preview remain
ignored. No new Git objects are introduced by this agent; the host owns final
staging/object inspection, commit/push, DRAFT PR creation and its ledger record.

Project-record validation was retried after the task tracking update and still
fails on the unchanged absent historical commit. The Git store reports it is
not shallow; the reference is demonstrably already present at the input revision.
The host must resolve/provide that historical object/reference before this gate
can be reported passing. Nothing is removed or weakened to bypass the failure.
