# Tracker TDR baseline refresh — 2026-11-24

## Scope and selected request

User request, exact: “Please make sure the Tracker TDR is up to date - don’t add too much text but make sure descriptions, plots and findings are representing the current baseline”.

Input parent: `78bef505c4e623739da204ce92e3aa7bc6f931c5`. Input TDR:
`80a6c998cb9002d0d116bd8c4a414193e904bbd2`, independently checked against
the fetched configured main. A new dedicated task worktree preserves the
unrelated `tools/agent_tasks/publish.py` change in the older main worktree.

## Outcome and evidence

The existing manuscript geometry already matched DES043: 46,682 planes,
54 signed groups, 2 mm strixels and the 703 mm sampled target. The stale parts
were completed integration/material checks still described as pending and the
absence of later current-geometry findings. All pinned geometry producer hashes
still match the current parent.

The review overlay adds three existing result plots (material, sensitive-volume
crossings and truth-fit ratios), updates stale descriptions and removes lengthy
future-integration prose. Five geometry figures use the fixed subsystem colors.
Pixel/long-strip geometry, original snapshots and historical receipts stay
unchanged. The report has 34 pages, versus 32; the extract has 30, versus 28.

Material and fit findings remain mixed: the complete-baseline radiation-length
average falls while interaction length rises. Truth-associated fitting is
distinct from pattern recognition. The approved GBTS/CKF reference keeps its
earlier 46,250-plane/Gaussian-response scope. Material locality, one-azimuth-bin
mapping, graphite CSG conversion and unqualified hardware remain explicit.
No new geometry, native simulation, engineering sign-off or acceptance occurred.

## Specialist assignments

Explicit fallback contracts were recorded before dispatch in the neighboring
`PubDoc-assignment.json` and `PhysVal-assignment.json`. Both use full input
parent revision above, read-only ownership and no nested delegation. The roles
were supplied through prepared prompts, without claiming native profile loading.

`/root/pubdoc_audit` checked every tracker figure/table fingerprint and current
producer hash. It identified stale future-integration language and the missing
current material report. `/root/physval_audit` independently reconciled DES043,
material, crossings, truth fits and the older approved reconstruction reference.
Its initial Fatras test attempt lacked analysis dependencies; the coordinator's
final isolated-environment run passes all eight tests. These are separate agent
assessments, not human expert approval.

## Validation and corrections

Commands, actual outcomes, compiler identity, PDF hashes and retained failures
are in `docs/publication/tracker-baseline-2026-11-24/validation.json` and the paired
session JSON. The exact overlay was assembled from the committed TDR and compiled
with the existing local TeX Live container, network disabled. All 34 final pages
were rendered and inspected; new findings and palette pages were also checked
at 1500 px. There is no clipping, overlap, overfull box or undefined reference.
Existing font substitutions and underfull table warnings remain.

The material retained-evidence suite passes 3 tests, crossings 2 and Fatras
analysis/native contracts 8. These do not rerun native transport. Snapshot,
overlay/source/evidence, software inventory, project records and session checks
pass. Standard Python lacked plotting/analysis packages, so the task installed
NumPy 2.4.6, Matplotlib 3.11.2, awkward and uproot in an ignored local venv.
Sandbox DNS failures were rerun with approved network access. The first project
record check needed a historical reviewed commit; fetching that exact commit
resolved it. Inventory initially rejected a documentation script as a code
family; it is now recorded as evidence of existing TDR tooling.

## Source delivery and publication boundary

`docs/publication/tracker-baseline-2026-11-24/` contains the compact readable
overlay, original/result hashes, evidence links, check/assembly recipe and QA
receipt. The exact compiled reports and page images remain local under ignored
`build/`. No full event, ROOT, geometry dump or large reference payload is added.

The locally edited `docs/tdr` is preserved; its parent gitlink is unchanged.
The TDR README explicitly says “Do not push.” Its deliberate Overleaf main
publication remains a separate authorization step after review of this concrete
result. This task prepares a draft PR under the parent's standing delivery rule.

## Token accounting

No exact completed-turn or child-turn token counters were exposed. `usage` is
empty, meaning unknown rather than zero. The required repository-wide summary
was run and retained locally; its historical observed totals are separate from
this task's missing coverage. No private client state or raw rollout was read.
