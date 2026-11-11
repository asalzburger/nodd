# SESSION-2026-11-11-pr129-merge-readiness — PR129 merge preparation and accounting

## Request and scope

User, exact: “That’s great, please pack up for merging - token accounting, etc.”

Starting revision `9f2e135ca4c31264248efe2250334d76d2b741cd`, initially clean checkout on the existing PR129 branch. The independent local accounting branch is `codex/pr129-merge-accounting`. This prepares the existing PR; no actual merge is requested. Geometry, source, runtime and scientific evidence retain the previously validated revision.

## Recovery and work labels

App metadata identifies **Plan EM calorimeter symmetry sample**, parent thread `01a1c4f8-21c7-7ff0-9fb7-6eaacb9d06a4`. Nine completed requests match the sample discussion, pilot, clarifications, profiling, geometry recommendation, prototypes and default implementation. Read-only spawn metadata and matching parent activity identify exactly two children, SysArch and PhysVal. Their source revisions and assessments match the implementation journal.

The opt-in `recover_usage.py` reads only selected thread/turn metadata and token_count events. Each cumulative increase equals the corresponding last-request counters. One repeated snapshot is ignored; there are no resets or outside-turn events. Parent and child streams reconcile independently. The [closed inventory](../usage/USAGE-2026-11-11-pr129-siw-wedges.json) retains 11 completed turns and 261 requests: **73,207,934 input + 149,934 output = 73,357,868 total observed tokens**. Cached input 72,145,920 and reasoning output 56,505 are subsets. These are client observations, not billing or a complete PR consumption total.

| Canonical work label | Turns | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| [Sample and 100-electron compute pilot](SESSION-2026-11-10-siw-ecal-compute-pilot.md) | 4 | 11,440,266 | 33,509 | 11,473,775 |
| [DDG4 profiling and geometry recommendation](SESSION-2026-11-10-ddg4-startup-profile.md) | 2 | 7,177,323 | 19,999 | 7,197,322 |
| [Barrel wedge prototype](SESSION-2026-11-10-siw-barrel-real-wedge-prototype.md) | 1 | 7,838,297 | 20,950 | 7,859,247 |
| [Endcap wedge prototype](SESSION-2026-11-10-siw-endcap-real-wedge-prototype.md) | 1 | 6,059,362 | 18,019 | 6,077,381 |
| [Default implementation and specialist reviews](SESSION-2026-11-10-siw-real-wedge-default.md) | 3 | 40,692,686 | 57,457 | 40,750,143 |

All observations were previously unowned. Five import previews/imports/replays added 11 observations and replayed with zero additions. Four original paired records are copied from the preserved pilot checkout, whose files remain unchanged. Historical provenance, findings and limits remain; dated corrections add attribution and usage. The pilot recipe remains local; its corrected journal link identifies the maintained follow-up recipe. Original closed-turn dates determine the timeline, independently of this accounting date.

Eleven curated app snapshots retain user inputs, selected first/final assistant messages, operation counts and verified parent/child identities through `visible.py`. Reasoning, command arguments/results, images, raw archives and private client state are omitted. Child assignment text is in the original journal; separate child user messages were not exposed. Reported roles do not prove profile loading. Actual models and client version are unknown. This active preparation turn, other devices and automated reviewer-task history remain excluded.

## Readiness and publication boundary

GitHub reports PR129 ready for review, MERGEABLE/CLEAN, with all three hosted checks passing at `9f2e135ca4c31264248efe2250334d76d2b741cd`. Human `asalzburger-review` approved that revision at 2026-11-11T05:07:42Z, review 5854134448. There are no inline threads. No redundant ready transition, merge or design sign-off occurs. Subsequent records commits require their own checks. The native overlap, all-sensor, material-ray and electron smoke checks remain historical scientific evidence; no new native run is claimed. Shower equivalence and the angular resolution campaign remain follow-ups.

The first import preview rejected integer epoch session timestamps. Converting the exposed seconds to UTC ISO 8601 fixed the schema issue; counters and inventory dates are unchanged. No validator was weakened. Subsequent import/preview/replay sequences passed. The paired JSON records repository checks after execution.

Automatic approval review rejected the connector's PR-body update, citing public disclosure of private client token/accounting metadata without destination-specific approval. The body was not changed. Accounting publication is held; no alternate route bypasses the rejection. The proposed body stays in ignored build storage. The local package is prepared for concrete user approval before push; PR129 remains open at its existing approved head.

## Local package checks

All 76 tests pass (37 session/recovery, 19 interaction, 20 token-site), plus both Node chart/conversation checks. Validators pass for 279 sessions, 111 PR ledgers and 102 tasks/54 documents/24 review rounds. The preview builds under `_site/pr129-token-preview`; its first attempt under `build/` was rejected by the output-directory guard and corrected. The five work labels match exactly 11 recovered turns and 73,357,868 observed tokens, all dated 2026-11-10. The repository summary contains 510 disjoint dated turns and 2,797,710,376 observed total tokens; 93 sessions still have no usage. These global figures include earlier work and are not PR129 totals. Source, scientific documentation/results and software dependencies match the approved head. This record stays open because public accounting publication is pending approval.
