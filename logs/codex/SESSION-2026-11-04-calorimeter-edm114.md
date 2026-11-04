# SESSION-2026-11-04-calorimeter-edm114 — issue #114 I/O restoration

## Scope and evidence

Bounded explicit SoftEng assignment `CAL114-SoftEng`, starting clean at main
`cd3ec20da56537617ac6fbbcf28bd6f28104cc64` on `codex/calorimeter-edm114`.
The coordinator's persisted assignment and prepared prompt live in the sibling
campaign worktree under `logs/codex/assignments/calorimeter-campaign/` and will
be retained with the integrated campaign. Native role loading is not claimed.
No further delegation occurred. Read AGENTS, PROJECT, ADR008, the Spack skill,
source/build conventions and current public issue #114 before implementation.

## Selected visible requests and responses

- User request, paraphrase: consolidate two ECAL options and restore EDM support
  from issue #114 in a single PR on main, retain historical accounting/interactions,
  then prepare HCAL/FCAL baseline design options.
- Coordinator assignment, paraphrase: implement issue #114 exactly in an isolated
  worktree; restore only hit/cluster structs, EDM4hep converters/metadata/fixtures,
  standalone build and algorithm I/O skeletons. No toy response, clustering,
  jets, build hook or tracker relocation. Commit locally; do not push. Coordinator
  owns tracking, interactions and GitHub updates.
- SoftEng response, paraphrase: ACTS 355ea684 pristine source and matching build
  exist in nodd-software-layout; the unrelated dirty dev/acts-nodd checkout is
  preserved. Both skeletons will fail explicitly, avoiding fabricated empty
  output. Attribution files require expanded ownership.
- Coordinator authorized `software/source/NOTICE.md` and
  `software/source/LICENSE-ACTS-MPL-2.0`, plus individual test files needed under
  ActsExamples/Calorimeter/tests.
- SoftEng progress, paraphrase: all four CTest targets pass; final source/build
  guards, documentation and journal curation underway.

## Decisions and outcomes

Restored the transient hit/cluster schema and original converters from nODD
PR #80 head `530080cfe16c7513228bf60238b99d4b9938538a`, originally ACTS fork
`8adca5eec180515a23d58d132a1e17e317a59e67`, retaining MPL 2.0 attribution.
The two wrapper configs now contain only collection names; execute throws
`std::logic_error` and creates no output. The fixture supplies fixed synthetic
hits/clusters directly. No simulated response, thresholds, topology algorithm,
FastJet, jets, externals/detectors relocation or ACTS injection is restored.

Metadata version 2 drops retired physics settings and explicitly identifies
unimplemented stages. Existing units/provenance, collection mapping and
float-range checks are retained. No transient EDM fields are added. The
standalone CMake project uses the TrackerGbts source/build pattern and rejects
a wrong ACTS revision, modified tracked source or mismatched build source.

## Commands and actual validation

The [executed report](https://github.com/asalzburger/nodd/blob/b260305b4dc091e89c611632c2c941961f7e2bdd/docs/validation/issue114/README.md) records exact
setup/build/test commands, installed versions, source origins and limits.
Spack preflight returned 2 (stale fingerprints/full-source warnings), communicated
before dependent work. Existing installed packages, ACTS source/build and actual
native compilation were then reverified without shared dependency changes.

The first example build failed on PodioUtil pulling tracker-generated headers;
it now uses podio ROOT I/O directly. No tracker header or source was changed.
Final native rebuild and all 4 CTest targets pass after formatting:9 hit tests,
8 cluster/metadata tests,2 skeleton tests and a 3-event actual ROOT round trip
through ActsExamples with complete persistent relations. Both deliberate source/
build mismatch configurations reject with exit 1. `otool -L` finds no old
calorimeter algorithm or FastJet libraries. Raw ROOT files stay under `/tmp`.

Repository session, project-record, interaction and token-site checks are
recorded in the paired JSON. The coordinator will rerun after integration and
supply campaign tracking/PR interactions; this child does not claim those
unassigned writes are complete.

## Changes and revision links

The paired JSON inventories the exact scoped source/CMake/docs/journal files.
No tracker, detector, external build or Makefile paths changed. Native software
can be merged with the broader ECAL consolidation through the local branch.

## Token accounting

Exact final per-turn child counters/model/client version are unavailable while
this child turn is active. `usage` remains empty/unknown, never zero. No raw
client store or hidden reasoning was collected. Later canonical recovery belongs
to the coordinator and must count this child independently without parent overlap.
Before closeout the project summary observed 1,817,405,271input + 8,258,578output
across 378 turns in 151/234 sessions; these are historical project subtotals, not
usage allocated to this assignment. Cached/reasoning counters are subsets.

## Follow-up

Issue114 software done conditions are verified in this scope. The coordinator
owns scientific tracking, exact PR/task identification and interaction/accounting
synchronization. Realistic response/clustering, calibrated clusters/jets,
cell-ID service and full-detector acceptance remain follow-up work. No human
engineering approval or design lifecycle advancement is recorded.

Implemented source and validation snapshot: `8652406ec992178a16f419b41d95aed73f40f1bc`. This later logging update records the already existing commit; it introduces no code or physics change.

## Completed specialist usage — 2026-11-04

Exact completed child counters are imported once from the usage-only campaign child inventory, matched through the observed parent/spawn edge and assignment. Shared HCAL/SysArch/PhysVal work belongs once to the campaign owner; the implementation child belongs to the EDM session. Current root and accounting turns remain active and excluded. These are observed counters, not per-PR allocations or billing.

Execution-report link pinned to the final immutable implementation journal revision for portability across the infrastructure and scientific PRs.
