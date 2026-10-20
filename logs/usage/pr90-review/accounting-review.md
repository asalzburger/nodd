# TA-A2 — PR90 first-import accounting assessment

Role: SoftEng, explicit supplied fallback mandate; native profile loading is not asserted.

Reviewed source: `a52d1cbd55a680e4bfc8a89219cd45819fa57506`.
Comparison baseline: `f1089e3ece830dbbb2bdaaf86ade19e13585a471`.

Outcome: PASS within the bounded sanitized-evidence assessment. No material finding.
Repository files changed: none. No private client DB, raw rollout, conversation,
reasoning or assistant-message content was accessed. No physics/native run,
dependency change, commit, publication, merge or human approval was performed.

## Independent accounting result

The 40 imported `(client_thread_id, turn_id)` pairs exactly equal the new
canonical journal observations, with one owner each and no overlap with the
210 baseline observations. Every original baseline observation and owner is
unchanged. All five fields and the entire curated usage-entry objects match
the sanitized inventory exactly. Event digests and the uniform capture header
also match the canonical evidence descriptions.

| Scope | Turns | Input | Cached input (subset) | Output | Reasoning output (subset) | Total |
|---|---:|---:|---:|---:|---:|---:|
| PR90 scientific work and delivery | 39 | 244,250,248 | 239,658,880 | 1,100,633 | 408,646 | 245,350,881 |
| Finalized accounting A1 specialist | 1 | 2,333,510 | 2,218,240 | 9,582 | 1,684 | 2,343,092 |
| First import | 40 | 246,583,758 | 241,877,120 | 1,110,215 | 410,330 | 247,693,973 |
| Global canonical subtotal after import | 250 | 867,337,994 | 841,088,000 | 4,655,384 | 1,587,868 | 871,993,378 |

All eleven per-session summary rows independently reproduce. Totals use input
plus output only; cached input and reasoning output satisfy their subset bounds.
All imported models remain null with explicit execution/client/billing limitations.

The selected closed observations comprise 16 science/delivery root turns,
23 science/delivery child turns, and one accounting child turn. Terminal states
are 35 completed, two interrupted and three failed. The failed/interrupted
turns contain actual observations and valid closing boundaries; they are not
discarded merely because the attempt did not complete successfully.

The six explicitly excluded earlier PR86/87 root turns and the active accounting
parent are absent from canonical ownership. The parent cumulative header includes
earlier excluded work and the active snapshot and is not used as a PR90 subtotal.
Each selected child thread's sum of all five per-turn counters equals its own
final cumulative counters independently; request counts equal observed events
minus repeated snapshots.

## Attribution and dates

Root task owners match the pinned journal scopes and retained canonical session
IDs in command metadata. Two identified roots require direct request evidence
rather than a command ID: delayed HCAL/ECT answer `01a15880-c9f7-77c0-93d7-114c97170351`
matches the exact asynchronous question at baseline
`logs/design/SESSION-2026-10-20-pr90-endcap-wheels.md:93`; interrupted next-comment
request `01a15931-c350-7d01-b73a-27a6c686167c` matches the superseding updated
sketch request at baseline
`logs/design/SESSION-2026-10-20-pr90-sketched-stagger.md:3`.

For every selected child, the retained parent edge, persisted root-turn ID,
agent path and recorded parent-task owner agree. Science children point to a
root observation owned by the same bounded task. The finalized accounting child
points to the active accounting root without importing that root. Retries and
follow-ups retain their own actual IDs. Time proximity is not used to allocate
or split tokens. Historical journals remain append-only narratives; their
source/result revisions and other scientific metadata are preserved.

All new observations have recorded terminal completion timestamps preceding the
capture. Four close on 2026-10-19 UTC and 36 on 2026-10-20 UTC. Independent UTC-day
and cumulative sums match the built global curve for all five fields. The site
has 250 dated and zero undated observations and ends at 871,993,378 observed
tokens. No session creation, import or commit time substitutes for usage time.

## Immutable scientific evidence

Comparison of the entire Git trees restricts changed paths to accounting,
journals, project records and two documented B2 scope prose files. All 661
checked implementation, field, geometry, native, OBJ, figure and scientific
source blobs under `tools/muon_layout`, `tools/toroid_prototype`,
`docs/validation/DES-039` and `docs/validation/DES-040` are byte-identical, except
the explicitly reviewed scope README. Existing scientific execution-source and
artifact identities therefore remain unchanged. DES040 and that README only
confirm B2 barrel scope and describe the accounting update. No fresh acquisition
or acceptance is inferred. The retained A1 audit matches its original SHA-256.

## Actual execution

A portable independent checker ran 1,082 assertions against exact Git blobs.
The pinned logger and token builder ran against an extracted scratch projection:

- Logger validation: exit 0, 200 records.
- Token validation: exit 0, 250 unique dated turns, 871,993,378 observed tokens.
- Token build: exit 0, same totals and date coverage.
- All eleven exact import dry-run replays: zero additions, 40 unchanged.
- Cross-owner duplicates and conflicting same-owner evidence were rejected.
- Scratch canonical JSON stayed byte-identical after replay checks.

Command:

```text
python3 -B /private/tmp/pr90-TA-A1-supplemental-check.py --repo REPOSITORY --output RESULTS_JSON
```

Python 3.14.6; Git 2.54.0 (Apple Git-157). No additional package was required.

Checker SHA-256: `eef2d00fcfb4080fc74ee5f06bf0b5ff87685ca752367ec3fd2ad82e55db377d`.
Results SHA-256: `5fa56765f76cdab7ea1b42099846c1fc74676e8c0c0a947456703d202e686915`.
Sanitized input inventory SHA-256:
`35d4bd6bc86c5734529b20ac243f862e6c76eaaa65ef2c110deb73a292df9af2`.

## Limits and handoff

Per-request cumulative-to-last-request reconciliation cannot be independently
rerun from retained totals and hashes without reopening the private inputs.
That reconciliation is supported by the recorded recovery execution and pinned
recovery implementation. This assessment independently checks the retained
boundaries, child cumulative arithmetic, request/repeat counts, digests,
counter equality, ownership and completion dates. Persisted relationship and
request summaries are accepted as sanitized recovery metadata; their private
source store was not reopened.

This same agent authored A1's baseline inventory. The present turn assesses
coordinator-owned recovery/import changes and does not claim independent
authorship of A1 itself. The current supplemental audit turn and current parent
remain outside the finalized snapshot. Their future usage requires a later
closed capture. Coverage remains partial across devices and unobserved child
history; observed counters do not establish complete project usage or billing.

The scratch site's dirty flag reflects the intentionally partial scratch working
tree; its contents and date arithmetic use pinned accounting data. This artifact
is a review preview, not deployment evidence.
