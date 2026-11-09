# Issue #120 — Repository cleanup schedule

- Request: [#120](https://github.com/asalzburger/nodd/issues/120),
  `120-35337160503`, 2026-11-06.
- Inventory revision: `2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7`.
- Scope: infrastructure audit and a conditional deletion schedule. No detector
  parameters, scientific results, acceptance states or published history change.
- Status: prepared for human review. No scheduled evidence has been deleted.

The [machine-readable inventory](issue-120-inventory.json) identifies exact paths,
Git blob IDs, SHA-256, byte sizes and triage states. It contains metadata, not
copies of the numerical data. It is a retained plan against an immutable source
revision; a later removal records which entries were acted on rather than
rewriting this snapshot. The [session journal](../../logs/codex/SESSION-2026-11-06-repository-cleaning.md)
records task inputs, assignments, actual checks and limitations.

## Size and scope

The captured tree has **4,727 ordinary files, 569,769,442 bytes (569.8 MB)**;
477,698,204 bytes are under `docs/validation`. Unique blobs in this tree total
551,773,583 bytes. These are uncompressed tracked file sizes, not packfile,
transfer, clone or full-history sizes. Submodule contents, ignored files and
symlink payloads are outside this inventory. MB denotes 1,000,000 bytes.

| Triage state | Files | Bytes | Disposition |
| --- | ---: | ---: | --- |
| `scheduled_after_prerequisites` | 122 | 193,586,653 | Execute the staged removal work below after its checks |
| `retain_dependency` | 1 | 2,324,679 | Frozen input still consumed by maintained prototypes |
| `retain_unknown_input` | 1 | 6,537,331 | Exact original recording cannot currently be regenerated |
| `review_required` | 21 | 48,117,302 | Generated evidence with unresolved consumers/retention needs |

The 122 scheduled files represent **34.0% of the captured checkout bytes**.
This is a potential tree reduction, not a completed saving. Remaining files are
not all raw data: plots, configs, manifests, compact binwise evidence, source
snapshots and narrative reports are retained. The size-based triage also lists
other numerical files of at least 1 MB; that threshold is only an audit filter,
not a retention rule. Small files have not been exhaustively classified by
scientific meaning. A small file can still contain event-level data.

Deleting tracked paths in a future ordinary commit reduces later checkouts;
existing reachable blobs remain in Git history and ordinary full clones.
History rewriting, force-pushing, Git LFS migration and artifact uploads are
outside this request. No clone-size reduction is claimed.

## Scheduled work, in dependency order

All rows are conditional. Keep existing reports, plots, recipes, exact producer
revisions, input/configuration snapshots and original artifact manifests.
Regenerate into ignored `build/` or `reference/cache/`, never over the retained
run. Preserve adverse/rejected controls and their meaning. Follow
[ADR-003](../decisions/ADR-003-validation-and-artifact-policy.md) and the
[repository artifact rules](../../AGENTS.md#reference-run-artifacts-and-pr-contents).

| Stage / inventory group | Files | Bytes | Required work before removal |
| --- | ---: | ---: | --- |
| 1 / `test-stdout` | 5 | 17,026 | Retain command, source/build identity, exit status, test counts and caveats in a concise report; repair references to stdout files |
| 2 / `historical-tracker-studies` | 41 | 138,484,673 | Extract reviewable compact numerical comparisons and provenance, preserve rejected-control conclusions, replay reports/figures and migrate consumers |
| 3 / `reconstruction-event-arrays` | 76 | 55,084,954 | Preserve bins, denominators, uncertainties and correlations needed by every observable; migrate replay/verifiers/bridges and compare with the existing event-level analysis |

### Stage 1: small repeatable test output

Exact paths are `DES-012/ctest.txt`, `DES-012/PR34/ctest.txt`,
`DES-012/PR34/support-tests.txt`, `DES-019/main-integration/ctest.log` and
`ODD-idres/build.log`, relative to `docs/validation/`.
These are execution transcripts, not test source or measured detector inputs.
The associated [DES-012 validation](../validation/DES-012),
[DES-019 integration](../validation/DES-019/main-integration) and
[IdRes recipe](../../tools/odd_idres/README.md) remain the entry points. A new
execution needs its own source/environment identity; rerunning a command does
not reproduce the historical stdout bytes or retroactively certify that run.

### Stage 2: historical tracker studies

The inventory enumerates `summary.json`, `layout.json.gz`, `study.json[.gz]` and
`local-coverage-audit.json` output in DES-009 coverage/review controls, DES-010
services, and the three distinct DES-011 searches. The [DES-009 report](../validation/DES-009-module-populated-layouts.md#retained-results-and-reproduction),
[DES-010 report](../validation/DES-010-tracker-services.md) and
[DES-011 report](../validation/DES-011-service-constrained-optimization.md)
describe the runs; the [module-layout workflow](../../tools/module_layout/README.md)
provides generation and report/plot commands. Each retained run has separate
input snapshots/manifests. Historical rejected searches must use their own
producer versions and inputs, including the rejected constraint semantics.

Known source revisions for the three DES-011 searches are:

- Even-row rejection: `6c882257c368927732315dbc756f1b89263d95af`.
- Routing-pocket rejection: `10203d9a3f41d82cb467a7deb75e8293b0f1cc95`.
- Corrected follow-up: `ac61f766b34f9bb60748e8fc4258a41037ca1e33`.

For DES-009, retain main/offgrid/total-p configs and the actual step-binding
runtime/overlay manifest. For the corrected DES-011 follow-up use
`optimization_envelope_followup_config.json`; the default 216-case domain is a
different study. Native ACTS target checks and seeded dense/random cohorts are
separate checks. Current-source reruns alone do not reproduce the older searches.
The recipe must pin all inputs and seeds from the original manifest before any
removal; recipe inspection in this task is not execution verification.

**Dependency hold:**
`docs/validation/DES-011-optimization/cases/p190-s680-b1-l1287.33-front_loaded-original-pockets/layout.json.gz`
is excluded from deletion. It is a frozen input to pixel support/z coverage,
short/long strip inputs and coverage comparisons, and forward-calorimeter context.
See, for example, `tools/pixel_support/inputs.json`,
`tools/pixel_z_coverage/config.json`, `tools/long_strip_barrel/coverage.py`,
`tools/long_strip_endcap/coverage.py` and
`tools/forward_calorimeter/layout-contexts.json`. Replacing that input requires a
separate compatibility change, exact content/identifier comparison and existing
regressions. Generated output can become a required input.

### Stage 3: reconstructed event arrays

All scheduled NPZ paths are named `events.npz` under
`docs/validation/tracker-reconstruction/` or
`docs/validation/tracker-reconstruction-species/`. They are per-event/per-track
reductions, including tuning and frozen validation samples. Their small file
sizes do not make them binwise evidence. The [reconstruction recipe](../../software/analysis/tracker_reconstruction/README.md)
identifies generation, campaign configs, seeds, native module requirements,
reduction, report, plot and integrity commands.

These arrays currently feed `verify.py`, `species_evidence.py`,
`species_report.py`, plotting, and the
[strixel bridge](../../software/analysis/strixel_reconstruction/bridge.py).
The validation workflow invokes the species verifier and both report/plot
replays. Blind deletion would break those consumers and remove information
used for bootstrap statistics, quantiles, tails and matched-parameter checks.

Create a compact replay contract that preserves each required comparison:
counts/denominators, bin edges/units, normalization, statistical intervals and
any cross-observable or event correlations needed for the stated inference.
Compare the new summaries and resulting tables/figures against the existing
full analysis, including tails and failed populations. Some native event/ROOT
audits must continue to require the local full dataset and say so explicitly;
compact-only replay cannot substitute for them. Keep native provenance, failed
attempt diagnostics, frozen profile/configuration and exact run hashes. Do not
merely gzip, split or rename event arrays. Only then remove the scheduled
arrays and add scoped ignore rules to prevent their return.

## Retained evidence and unresolved candidates

`review_required` includes DES-006 optimization output, DES-011 bypass training,
DES-013 layouts, DES-022/023 inventories and adverse expected fixtures,
DES-040 geometry/native reports, ODD IdRes resolutions, the material survey,
tracker performance/native reports and resolution-optimization exploration.
Assess consumers before deciding whether each is an input, compact evidence or
replaceable diagnostic output. In particular:

- `tools/pixel_detector_dd4hep/test_export.py` reads the packed-200um DES-013
  layout. `tools/long_strip_endcap/inputs.json` pins the DES-022 inventory.
  These need compatibility work before removal.
- DES-023 `*expected.json.gz` files are controls. Their names and size do not
  establish that they are dispensable; preserve identifier and regression checks.
- `gen3-material-mapping/scatter.npz` is a portable plot input. Its
  [report](../validation/gen3-material-mapping/README.md#input-identity-and-checks)
  states that the original 100,000-geantino recording lacks source geometry,
  seed and generation command. Exact original regeneration is blocked. Retain
  the scatter and compact occupancy data unless equivalent retained evidence
  and an explicitly documented replacement resolve this gap. Do not describe
  a new sample as the historical recording.
- Keep compact material profiles/maps and frozen sensitive layouts used by CI.
  There is no blanket `*.npz`, `*.json.gz` or inventory deletion rule.

## Accounting changes that reduce concurrent PR conflicts

The existing journal and interaction stores are already one file pair per
session and one ledger per PR. Preserve that structure and the existing
canonical owners rather than introducing a shared mutable index or a migration
of historical tokens.

The implementation adds `session_log.py new --pr N` and
`ledger.py sync --session SESSION-ID`. The latter selects current **and former**
links, including reassigned/removed associations, and leaves unrelated PR files
untouched. Tests cover isolation, idempotence, shared references, invalid
selectors and lost links. Fingerprint checks, global turn deduplication and
remote-refresh requirements remain in force. See the
[logging workflow](../../logs/README.md#add-token-accounting) and
[interaction workflow](../../interactions/README.md#keep-synchronized-with-pr-token-accounting).

Create a fresh bounded session for each PR task or accounting pass. Use distinct
branches, because legacy branch matching remains additive to explicit PR links.
Previously unowned recovered turns can be recorded once in the bounded
accounting session with explicit original-task evidence. Existing owned turns
stay in their canonical journal; factual corrections still refresh every PR
that references them. New dated, task-named usage inventories are immutable;
explain them beside the evidence or in the owning session instead of growing
`logs/usage/README.md` or campaign journals on every PR. Global summaries and
site exports are generated into ignored directories. Existing historical files
are retained, with no accounting reallocation or mass ledger rewrite.

Issue #120 is not a PR. This task retains its selected public interaction
evidence with the session; it does not fabricate `interactions/pr-0120.json`.
After a real PR number exists, capture its public discussion, add the explicit
session link and prepare its separate ledger before publication. This task does
not authorize that publication.

## Additional cleaning options

1. Retain plots but inspect the largest SVGs for oversized embedded raster or
   path data; simplify export settings only after visual/numerical comparison
   and provenance updates. Avoid adding alternate formats unless they serve a
   reader or publication need. No figure was regenerated in this task.
2. Preserve frozen publication source snapshots. The two duplicate blobs of at
   least 1 MB in the audit save about 4.7 MB of checkout space if path copies
   disappear, but Git already shares their blob storage. The pixel TDR's
   self-contained snapshot is required by `tools/tdr_baseline/generate.py
   --check`; deduplication must not break that contract. Across all sizes the
   current tree has about 18.0 MB of repeated blob payloads, not additional
   unique-object storage.
3. Keep builds, caches, downloaded references, event samples and temporary
   reports in the already ignored `build/`, `reference/cache/` and `_site/`.
   Add specific ignore rules when each scheduled migration is implemented.
   A blanket data-file ignore could hide legitimate compact evidence or inputs.
4. If full-clone size remains a problem after future output restraint, separately
   measure reachable historical blob/pack sizes in an authorized maintenance
   checkout and propose a retention/history plan to humans. An ordinary cleanup
   commit cannot reclaim reachable history; no destructive maintenance or
   storage-service migration is authorized here.

## Reproduce and verify this audit

Python standard library and Git are sufficient. No detector runtime is loaded.

```sh
python3 -B tools/repository_cleanup/audit.py \
  --revision 2ce4e9c81006a3779e89a3cedc3a45a7f1bf72d7 \
  --output docs/maintenance/issue-120-inventory.json --check
python3 -B -m unittest discover -s tools/repository_cleanup -p 'test_*.py' -v
```

To create a separate audit, omit `--check` and choose a new output filename.
The tool reads Git objects at the full commit SHA, disregards dirty working-tree
bytes, refuses to overwrite an audit and has no deletion operation. CI checks
this immutable inventory and the tool's safety boundaries. This verifies file
identity, triage rules and arithmetic; it does not prove native reproducibility.

No ACTS/DD4hep/Geant4 jobs were run in this infrastructure task. Before executing
any scheduled native reproduction, run the required node preflight, verify all
original source/runtime/input identities, and retain the new run's commands,
seeds, versions, tolerances and results. Human review must resolve the retention
and consumer changes before a deletion patch is considered ready.
