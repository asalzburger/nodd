# SESSION-2026-09-29-restore-workflow-branches — Preserve workflow branches

## Request and scope

After finishing the tracker service PR, the user asked to identify local branches
that had been deleted remotely and restore them for future workflow reuse.
[PR #25](https://github.com/asalzburger/nodd/pull/25) was completed at
`2a3dbfb741f7ea27e77cca3de81690fa800e4567`; its final hosted build passed at
[the retained run](https://github.com/asalzburger/nodd/actions/runs/36553957116).
This subsequent task changes remote references and records their provenance only.
It does not merge or approve any design, update detector files, or delete branches.

Read AGENTS.md, PROJECT.md, ADR-004 and the logging workflow. The main worktree
remains on `study/tracker-service-corridors`, preserving its four unrelated
untracked usage files. Created isolated worktree `/tmp/nodd-restore-workflow-branches`
on `infrastructure/restore-workflow-branches` from main
`1aa2aafd381fc37a9da3368686f2ca34d9f4dd0a` for this paired journal. Infrastructure
maintenance is excluded from scientific dashboard progress tracking.

## Audit and restoration

Compared `git for-each-ref` local heads/upstreams with the live paginated GitHub
branch API and merged PR head revisions. Local remote-tracking refs were stale:
ordinary fetch had not pruned them, so their presence did not prove a remote
branch still existed. Found twelve deleted branch names among the eighteen local
heads that existed before creating the maintenance branch. Every target was a
locally available commit and an ancestor of current main.

Rechecked absence immediately before an ordinary atomic push using explicit
`SHA:refs/heads/name` refspecs. No force push, history rewrite, pruning, local
branch movement or existing-remote update was performed. The push reported twelve
new branches. A fresh live branch listing then verified every restored hash,
all ten previously existing remote heads, and the unchanged local heads.

| Restored branch | Verified remote commit | Latest relevant merged PR |
| --- | --- | --- |
| `adr-004` | `03fcba5f4e7071513a1fd3d83119fbf303323135` | [#1](https://github.com/asalzburger/nodd/pull/1) |
| `chore/agent-roles-signoff` | `9a4bf3d5e638ff596a71f3d66f240dcfdcfddad1` | [#10](https://github.com/asalzburger/nodd/pull/10) |
| `design/global-envelopes` | `cb654ee91457b22d899a898faf2c8bf6e0fc275e` | [#4](https://github.com/asalzburger/nodd/pull/4) |
| `design/tracker-system-plan` | `075d8a3515406a1393224c5cf105153380c75517` | [#12](https://github.com/asalzburger/nodd/pull/12) |
| `infrastructure/acts-local-workflow` | `c41056328e16a0dc53f5c898b56c85c45c1b7e95` | [#23](https://github.com/asalzburger/nodd/pull/23) |
| `infrastructure/local-token-accounting` | `747d3ff11f3dbbd0189db529fc4ccac0cd9257a6` | [#18](https://github.com/asalzburger/nodd/pull/18) |
| `m0/reference-reading-pilot` | `c7fb95f91a39ef078b7806a264c04daa543fd064` | [#2](https://github.com/asalzburger/nodd/pull/2) |
| `planning/full-detector-roadmap` | `ef821572ede07e8349d10e5ba3cb8af23af018a7` | [#3](https://github.com/asalzburger/nodd/pull/3) |
| `software/acts-spack-skill` | `01c5a28459f3d72136e9f961426eedbfcc7b1433` | [#16](https://github.com/asalzburger/nodd/pull/16) |
| `study/cobe-pint-module-coverage` | `b97010c6135a562d5be38f410ae3600976303231` | [#24](https://github.com/asalzburger/nodd/pull/24) |
| `study/pyacts-gen3-bindings` | `53f3088e92e22c32bb074fe8426695594f2019af` | [#14](https://github.com/asalzburger/nodd/pull/14) |
| `study/tracker-first-layouts` | `412fa0f37a1e0cf284e07ce2db39bfcc7041dd55` | [#13](https://github.com/asalzburger/nodd/pull/13) |

Eleven restored tips match the corresponding local branch tip. For
`study/tracker-first-layouts`, local `243b138ffd78844c020604e103f5c2a6e893d988` and
stale tracking ref `f57e26e83b826867c2720edcd702e808fe946854` precede the published
rebase. Restored PR #13's final `412fa0f37a1e0cf284e07ce2db39bfcc7041dd55`, already
retained in main, to preserve the latest published workflow. The older local head
was not moved. Existing remote `archive/pr13-before-rebase-2026-09-25` remains at
`f57e26e83b826867c2720edcd702e808fe946854` for the earlier history.

## Commands and checks

- `git for-each-ref --format=... refs/heads` and `refs/remotes/origin`.
- `gh api --paginate 'repos/asalzburger/nodd/branches?per_page=100'` before and after.
- `gh pr list --repo asalzburger/nodd --state all --limit 100 --json number,headRefName,headRefOid,state,url`.
- `git cat-file -e SHA^{commit}` and `git merge-base --is-ancestor SHA origin/main` for each target.
- `git push --atomic origin SHA:refs/heads/NAME ...` for the twelve listed targets.
- Exact post-push remote/local comparison: PASS, twelve restored heads and ten
  existing remote heads verified; no local target branch changed.

No detector or workflow source was altered, so no physics rerun is applicable.
The paired journal validator and successful dashboard build are recorded below.
Branch restoration is complete; future deletion-prevention policy was not changed.

## Usage and limitations

No exact client-reported counters are exposed for this bounded task. `usage` is
empty, not zero. No private client state was inspected and no earlier counters
were copied into this record. The restored commits preserve their original
limitations and approval states; branch availability does not certify workflow
compatibility with today's dependencies.

## Journal validation

The isolated main-based checkout validates 56 paired records; dashboard validation
covers 31 tasks, 10 documents and 11 review rounds. Dashboard build succeeded at
`/tmp/nodd-branch-restore-dashboard`. No infrastructure progress item was added.
The journal summary retains historical observed input 134,594,309 and output
674,111 over 79 turns in 42/56 sessions; these partial sums are not this task's
usage. This checkout excludes PR #25's pending journal and the unrelated local
usage-summary pair, explaining the different session denominator.
