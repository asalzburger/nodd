# SESSION-2026-11-18-lar-baseline-stack — ECAL baseline and stack

## Request and scope

User exact request: “Ok, make the last draft PRs stackable with token accounting
as well, the new LAr design becomes baseline for the EM calorimeter”.
Interpreted recent drafts as147(native drawing),148(restored LAr),149(updated
drawing), the only three recent draft ECAL PRs. PR145 is already ready and is
a separate historical findings report. Start:8f7a7c8bd86f4d9c67c11b37d91aea76790feee4
on clean PR148 worktree. No unrelated changes were present.

Explicit human working-baseline selection authorizes selecting the already
validated restored1.8mmPb/1248period barrel and650mm endcap for maintained ECAL
exports. Formal engineering sign-off/acceptance is not inferred. Preserve
Si-W as comparison and all original/dense/restored evidence. No new material
retuning, no new shower sample.

## Stack and records

Plan: main→147→148→149→baseline-selection draft. Use ordinary merges, no
rebase/force push. Merge147 cf4403cecf187c61f0f2835a6ecc31559e6639f3 into148,
then148 into149. Resolve shared project/inventory records by stable IDs and
additive content; regenerate the inventory page from combined source. Keep
distinct journal pairs and canonical token owners intact.

## Accounting boundaries

New bounded task journal. Refresh public discussions and exact visible sources
when accounting; import only disjoint completed observations. Active current
parent excluded. Historical owners and absent counters remain explicit.

## Validation and follow-up

Checks, actual source revisions, baseline implementation, physical-interface
assessment, independent scientific review and final draft links are appended
as they complete. No design lifecycle status is advanced by the agent.

### Stack merge execution

Merged PR147 into PR148 as5cf64bacde7de38d35cd23549c96b712db8566d8,
then PR148 into PR149 asd0c8afb0da080a44ce2ae9422dea6e96f857df2d.
Project and session/interaction validators passed after stable-ID reconciliation.
The second inventory merger rejected reordered additive evidence lists; the
command wrapper incorrectly continued and committed unresolved inventory markers.
This was detected before publication and corrected in an ordinary subsequent
commit, retaining both branches' evidence/PR/recipe contributions and rebuilding
the generated inventory page. Inventory check and conflict-marker audit now pass.
No geometry or accepted scientific evidence was altered by the correction.
