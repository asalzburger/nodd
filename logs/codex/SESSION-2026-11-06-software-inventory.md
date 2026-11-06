# SESSION-2026-11-06-software-inventory — Issue 124 software inventory and maintenance

## Scope and evidence

Contemporaneous, curated record for issue #124 and label request
`124-35358784063`. Started from clean branch
`codex/agent-task-124-35358784063` at
`4497737721d35df1e8971d5d01e8a5727def14aa`. No unrelated user edits were present.
The runner supplied the public issue body and empty discussion snapshot; no
remote refresh or remote mutation was performed. The selected request, named
parties, response summaries and tool provenance are retained in
[request.json](SESSION-2026-11-06-software-inventory/request.json). Raw client
state, raw run data and hidden reasoning are not retained.

Read AGENTS.md, PROJECT.md, ADR-003, ADR-004, ADR-008, the logging and interaction
workflows, existing software/build/runtime recipes and the applicable
nodd-coordinate/nodd-review-validation skills. This is infrastructure upkeep,
excluded from scientific progress tracking. No DES, ADR status, detector source,
configuration, design acceptance or human sign-off was changed.

## Selected conversation

- Public reviewer **asalzburger-review**, exact issue request retained in the
  selected input evidence: requested tables of pre-existing Spack externals,
  agent-added ActsExamples/cross-validation software, test/validation and
  analysis software; keywords, integration/installation methods and PR links;
  a page linked from the main page and continued updates when software is added.
- Local user relay, selected paraphrase: implement issue124 in the isolated
  task worktree, run checks and prepare records; leave publication to the host,
  with no pushes, remote writes, design approvals or machine changes.
- Coordinator, selected paraphrase: trace committed software evidence, distinguish
  historical installations from runtime qualification, add a generated inventory
  and offline upkeep checks, and return a structured draft-PR handoff.
- SoftEng child `/root/inventory_evidence`, selected handoff: identified exact
  software pins, recorded Spack/native/analysis environments and source/PR
  provenance at the starting revision. It found no baseline Marlin/LCIO
  integration evidence and identified current calorimeter processing skeletons.

## Decisions and outcomes

- Added `software/inventory.json` and generated `docs/software-inventory.md`:
  **56 components, 99 maintained code families, 51 reviewed dependency/build
  inputs and four software gitlinks**. Tables separate Spack externals,
  external validation software, local ActsExamples source, cross-validation,
  analysis and repository/build/documentation tooling. Root/software README
  links make the page directly accessible.
- Every component has usage keywords, integration, installation/use procedure,
  version/status, repository evidence and known related PRs or explicit unknown
  PR status. Local source includes upstream-migrated code with retained notices;
  it is not all attributed as newly invented by agents.
- Historical DD4hep/Geant4 versions and package hashes are kept with their
  individual receipts. No live Spack/runtime activation, native build, package
  installation, scheduler change or machine configuration occurred. The page
  is not an exhaustive transitive Spack lock export; no complete committed lock
  snapshot exists in the reviewed inputs.
- ACTS is a pinned source submodule with an explicitly selected matching existing
  build, separate from the Spack dependencies. The MaterialMapping adapter
  requirement remains explicit. Current calorimeter EDM4hep I/O is distinguished
  from unimplemented digitization/clustering and historical FastJet work.
- Added an offline standard-library inventory checker/renderer. CI and
  `make check` detect missing code families/submodules, changed dependency/build
  recipes, stale indexed source pins and stale generated page content. Refresh
  requires reviewing inventory descriptions and receipts; it is not evidence of
  installation. New externals imported within an existing family still require
  author/reviewer semantic review. Scope and exclusions are documented.
- Updated AGENTS.md and the PR template to require inventory maintenance in the
  same PR as software additions/removals, dependency, integration or usage changes.
- Publication is owned by the scheduled-task host. No PR number exists in this
  worker context, so no fabricated `interactions/pr-NNNN.json` was created.
  The host publisher captures that record after creating the required draft.

## Specialist assignment


```json
{
  "id": "SW124-SoftEng-evidence",
  "role": "SoftEng",
  "input_revision": "4497737721d35df1e8971d5d01e8a5727def14aa",
  "inputs": [
    "software/README.md",
    "software/analysis/README.md",
    "software/Makefile",
    "docs/decisions/ADR-008-software-source-layout.md",
    "skills/acts-spack/references/nodes.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "For issue 124, identify traceable software inventory entries: historical Spack externals and versions, ACTS/IdRes/Marlin and validation chain, analysis packages and install methods, nODD ActsExamples additions and cross-validation families. Read source at the input revision; inspect additional relevant committed paths and name them. Find introducing/integration PR numbers from repository history/records, distinguishing integration from author or install evidence. No runtime activation, install, network, or machine changes. You are not alone in this worktree; do not modify or revert any files. Do not delegate further.",
  "deliverable": "Return a compact cited table or structured list with component, keywords, integration, install/version evidence, related PR and limitations; coordinator retains curated findings in the paired session narrative.",
  "completion": "Return assignment ID, exact revision, source paths, actual read-only commands, missing evidence and a useful software coverage list."
}
```

## Specialist handoff and reconciliation

The assignment was recorded before dispatch and validated with
`tools/agent_workflow/workflow.py prepare`. The native tool selected SoftEng
and the child was directed to read the complete prepared mandate, checkout
instructions and review skill. Client child path:
`/root/inventory_evidence`. No execution-model identifier or token counters
were supplied. The child remained read-only and did not delegate further.

The child examined committed source using `git show REV:path`, `git ls-tree`,
`git log --first-parent`, `git log --diff-filter=A`, `rg` and committed interaction
metadata. Its sources included software/README.md, software/Makefile,
.gitmodules, software/source/NOTICE.md, local ActsExamples/analysis READMEs,
DES-012/DES-042 environment receipts, issue114 I/O report, unrooted installation
receipt, nodehammer report and the IdRes-submodule journal. A follow-up checked
additional tool-family PR mappings at the same exact revision.

Reconciliation preserved these findings:

- Pins: ACTS `355ea68493b326956756c9386d2fd9eaf9328568`, ODD
  `d70556f33b1c36abdf101a07ad8cf57eb56fbdf1`, IdRes
  `d54d0e3c465cc0308becb737b04364ce5c68ce16`, nodehammer
  `30b19dcbd9329b742d98b1383a1484600fc3e0c3`.
- Source PR77 is distinct from staged migration PR78/79/80. The current I/O
  restoration is PR115; it does not make historical full calorimeter processing
  available on main. PR links do not imply current remote states or sign-off.
- Tracker/beampipe implementation provenance uses PR57/58; selected strips
  retain PR49–53 and consolidation PR55. Incorrect tentative PR61/65 associations
  were corrected before the retained inventory; those are unrelated accounting/
  calorimeter-assessment work. Group rows flag related integration/source work,
  not an exact per-file authorship allocation.
- No live tests, installs or native qualification by the child. This was a
  separate baseline evidence assessment, not an independent review of the new
  implementation. The coordinator authored and self-reviewed the implementation.

## Commands and validation

- `python3 -B -m unittest discover -s tools/software_inventory -p 'test_*.py' -v`:
  **10 passed**, including unknown family, changed/removed dependency manifest,
  changed build/CI recipe, source gitlink addition/update without source fetching,
  stale page, ignored build outputs, unsafe/missing evidence, duplicate ownership
  and malformed PR URL. Repeated after final data changes: **10 passed**.
- `python3 -B tools/software_inventory/inventory.py refresh` then `check`:
  **passed**, 56 components / 99 code families / 51 reviewed inputs / four pins.
- `make check`: **failed, exit 2** after the software layout, inventory and
  257-session validation passed. Existing project-record validation cannot
  resolve historical Git commit `78bc60bb6da0c9d234baf00d37cadea9dd4964b4`.
  No historical object was fetched and no gate/record was weakened. Token
  validation was not reached through make; it was run separately below.
- `python3 -B tools/interactions/ledger.py validate`: **passed**, 106 existing PR
  records. New task input evidence awaits association by the host-created PR.
- `python3 -B tools/token_usage/build.py validate`: **passed**, 438 canonical
  disjoint historical turns. `build --output _site/software-inventory`:
  **passed**; output stays ignored and local.
- `python3 -B tools/session_logging/session_log.py validate`: **passed**,
  257 sessions. `summary --format json`: **passed**; output kept local in /tmp.
- `git diff --check`: **passed** for tracked edits. Final untracked-text whitespace,
  path/size, generated-link and publication-boundary inspection is recorded in
  the paired checks. An initial whole-file whitespace scan flagged two inherited
  README trailing spaces outside this diff; these were preserved, and the final
  check covers tracked diffs and all new text files. No staged files or new commits were created by the worker;
  the host publisher owns their final inspection before pushing.

These are infrastructure/metadata checks. No detector simulation, native build,
geometry validation or engineering acceptance is claimed.

## Changes and revision links

Changed-file inventory is in the paired JSON: inventory page/data/checker/tests;
README links; AGENTS.md, PR template, CI and Makefile upkeep hooks; paired session
and selected interaction input evidence. ADR-003/004/008 are governing references,
not modified decisions. Source catalogue changes: none; no detector facts or
new external design parameters were introduced. Existing repository receipts,
source pins and PR references provide software provenance.

No worker commit exists; Git history will locate the host-published enclosing
commit. The task branch and input revision remain unchanged during preparation.

## Token accounting

No exact completed-turn counters, stable client thread/turn IDs or reported
execution models were exposed for parent or child. `usage` remains empty;
observed input/output for this task are **unknown**, not zero. No token recovery
or per-PR allocation was attempted. The canonical summary had 257 sessions,
171 with usage and 86 without observations, covering 438 historical turns;
its observed input/output totals were 2,113,297,698 / 9,790,364. These are existing
project observations, not this task's consumption. No historical counters were
copied, split, moved or counted again.

## Follow-up

Human review should inspect component scope/provenance and the maintenance
policy/checker. The host must commit/push this branch, create the required draft
PR with issue124 and actual validation/limits, capture and validate that PR's
individual interaction record, and retain its verified URL in task state/results.
Publication is still pending, not a worker-completed PR outcome. The missing
historical project-record object must be available before full `make check`
can pass; normal CI already has a historical-evidence fetch step. No design
sign-off is requested or recorded. Future software changes update the inventory
in the same PR; automatic matching fingerprints do not replace semantic review.
