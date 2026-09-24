# SESSION-2026-09-16-tdr-submodule — Register TDR submodule

## Scope and selected conversation

2026-09-16. User (exact quote): “Change it to a submodule”.
Starting branch/commit and unrelated work are recorded in the paired JSON.
Read repository scope/instructions and inspected the clean TDR checkout.

## Changes and outcome

Registered existing docs/tdr with the user-provided Overleaf remote in .gitmodules.
The explicit instruction authorizes the remote configuration needed for the
submodule. No credentials were embedded. The parent index now records a gitlink
(mode 160000) to `7783ea3e3235c0fe9da641db3d303a6f211b3073`.
Moved nested Git metadata into .git/modules/docs/tdr with absorbgitdirs.
The TDR remains clean on main at the same revision, with its working files intact.
No TDR content was edited, no remote push occurred and no commit was created.
The .gitmodules and gitlink changes are staged by git submodule add; this session
pair remains unstaged. Unrelated user changes were preserved.

## Commands and validation

Both Git mutations initially failed under filesystem restrictions and succeeded
on explicitly approved retries. See the paired JSON for exits and commands.
Verified submodule status, index mode/revision, TDR branch and clean working tree,
and the relocated gitdir pointer. Staged and unstaged whitespace checks passed.
Session validation is recorded in the paired JSON. No LaTeX build or fresh network
clone was run. Exact token counts are unavailable.

## Follow-up

Other checkouts can initialize the pinned TDR with
`git submodule update --init docs/tdr` after these parent changes are committed.
Overleaf access is still required. Future report updates should commit in the TDR
repository and update the parent gitlink to the intended revision. Publication
and pushes remain separate actions. No design/ADR approval state changed.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **1,307,511 input** and **1,667 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
