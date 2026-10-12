# Resolve PR #14 conflicts with main

- Session: `SESSION-2026-09-28-pr14-merge-main`
- Date: 2026-09-28
- Target branch: `study/pyacts-gen3-bindings`
- Starting revision: `0c8734540d3de12cf0c795aae65f71e8ac6e5099`
- Main revision: `0d90d75d6f998f732adaad2f0a49787b5cbc46fa`

## Selected request

“Please go through the open PRs and resolve conflcits if there were any.”
Commit and push were authorized. This record covers PR #14; the other four
conflicted PRs have separate bounded records without duplicated token usage.

## Outcome and resolution

Prepared an ordinary merge of main in a clean, isolated detached worktree of the
PR head. The original user checkout and its unrelated untracked bytecode file
were untouched. Initial changes above describe the clean worktree before the
merge; the log scaffold was created after conflict resolution.

Merged structured catalogues by stable IDs using the common ancestor, retaining
independent source facts, tasks, documents, evidence and PR entries. Preserved
all historical review objects exactly, including withdrawn/adverse states and
exact target revisions. Kept distinct session pairs and exact usage observations.
Updated the curated register date and PR #13's verified merged metadata from
`gh pr view 13 --json number,title,url,state,headRefOid,mergeCommit,mergedAt`.
PR #13 merged on 2026-09-25 at 13:41:56 UTC; its recorded final head is
`412fa0f37a1e0cf284e07ce2db39bfcc7041dd55`.

No new scientific parameter, source or human approval is introduced by this
resolution. Existing provenance from both parents is retained. The JSON inventory
includes main's imported changes and this session pair. The enclosing merge
commit provides the resulting revision without a self-referential hash.

## Commands and checks

- `git fetch origin`
- `git worktree add --detach <temporary-checkout> origin/study/pyacts-gen3-bindings`
- `git merge --no-commit --no-ff origin/main`
- Curated three-way JSON merge by stable IDs, with conflicting scalar values inspected explicitly.
- Dashboard, logging, tracker and applicable branch tests: actual results in the paired JSON.
- Source/review preservation audit: passed for both parents.

Validation and publication use ordinary commits and fast-forward pushes to the
existing PR branch. This task does not merge the PR into main or change design
approval. GitHub checks and mergeability are checked after publication.

## Limitations and next action

Exact client token counters are unavailable; `usage` remains empty. The summary
reports only retained observed totals and missing coverage, not a complete project
total. No physics simulation or binding-runtime regeneration was needed for this
conflict resolution. Existing design review/sign-off questions remain open.
