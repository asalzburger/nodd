# ECAL PR133–137 merge and accounting record

This isolated **PROTOTYPE** study progresses from the100-electron benchmark
(PR133), through10k angular response and controls (134), continuous-silicon
control (135), module staggering/held-out calibration (136), to the frozen
100k-training/20k-validation staggered calibration and reuse interface (137).
DES-030/DES-031 approval states are unchanged. Merging grants no design sign-off.

The original stack was133 →134 →135 →136 →137. GitHub automatically marked
PR134 merged into the PR133 branch at2026-11-12T16:54:27Z after a publishing
race made its head reachable there; this was not a merge to main. The full10k
study is retained in PR133 with ordinary corrective history. PR134 is the
historical merged discussion/source record. Merge the remaining open PRs in
order **133 →135 →136 →137**, using ordinary merge commits and
retaining the recorded source commits. Retarget each dependent PR to main after
its predecessor merges and allow its checks to finish. Do not squash/rebase the
chain: calibration provenance names the actual freeze/results commits.
All five PRs carry `enhancement` and `campaign:calorimeters`.

The canonical sources remain `project/tracking.json`, the five individual
`interactions/pr-0133.json` through `pr-0137.json` records, and their referenced
paired session journals. Dated open/head snapshots describe observations, not
future merge outcomes. The source SHA in a self-referencing PR's record is its
last observed ancestor; recording a later metadata commit does not alter science.

## Accounting and labels

The retrospective inventory
[`USAGE-2026-11-12-ecal-chain-readiness.json`](../../../logs/usage/USAGE-2026-11-12-ecal-chain-readiness.json)
corroborates **51 closed turns /1299 requests /303,597,535 observed tokens**:
302,560,432 input +1,037,103 output. Cached input298,760,832 and reasoning
output540,004 are subsets. These are observed context/response counters, not
billing estimates. The earlier15 observations retain their original owners;
36 newly recovered observations were imported once into the corresponding task
owners. Selected app-visible prompts/responses, named specialist assignments and
operation metadata accompany all51 measured turns. The runner's injected
benchmark prompt does not establish another human identity.

One interrupted input has no increasing token-count snapshot and remains
unknown, not zero. The coordinating preparation turn was active at collection
and is excluded. It must be recovered in a later task after it closes; it must
never be estimated or split among PRs. The two completed SoftEng assignments
are counted separately in the preparation owner. Their parent is excluded.

Unique canonical thread/turn owners determine the total. A journal shared by
several PRs is referenced by each, without duplicating or allocating its tokens.
The usage inventory supplies dates/corroboration, not extra consumption.
Original dated journal statements about unavailable counters remain historical;
their dated corrections identify the new evidence.

After the complete chain reaches main, the existing push workflow validates and
publishes these committed observations to Pages. Daily work labels derive from
the same canonical titles, exact closed-turn dates and unique counters; all
12 contributing task owners therefore survive merging without editing a second
label registry. GitHub labels remain on the PRs. The separate curated feature
markers in `project/token-milestones.json` require real merge timestamps and
are not fabricated in advance.

## Validation and post-merge reconciliation

Both project validation and token Pages CI run the read-only chain guard:

```sh
python3 -B tools/project_records/check_ecal_chain.py
python3 -B -m unittest discover -s tools/project_records -p 'test_ecal_chain.py' -v
python3 -B tools/project_records/validate.py
python3 -B tools/session_logging/session_log.py validate
python3 -B tools/interactions/ledger.py validate
python3 -B tools/token_usage/build.py validate
python3 -B tools/token_usage/build.py build --output _site/pages
```

The guard requires all five tracking/discussion records, ordered retained heads,
the original calibration freeze/results commits and byte-identical coefficients
and numerical core. It reports unique account coverage without adding PR totals.
Synthetic Git tests cover a real ordinary-merge closeout, missing/reordered heads,
lost source commits, changed artifacts and detached merge evidence.

CI rebuilds committed records; it does not query live GitHub merge facts or local
client telemetry. In the next tracking update after the human merges, refresh
the five existing tracking entries with actual merged heads, merge SHAs/times
and collection time; refresh their public discussion snapshots, sync affected
sessions and validate. Add the final calibration feature marker using its actual
merge timestamp if selected for the curated timeline. Then run on updated main:

```sh
python3 -B tools/project_records/check_ecal_chain.py --require-merged
```

This strict mode requires **head →merge →checked main** ancestry for every PR.
It currently must fail while the remaining four records honestly remain open. No merge or future
CI/deployment outcome is claimed by this pre-merge record. Full simulation/event
payloads remain local; no new native transport run is needed for these metadata
and provenance checks.
