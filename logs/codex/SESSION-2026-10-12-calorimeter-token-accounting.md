# SESSION-2026-10-12-calorimeter-token-accounting — Calorimeter token-only PR

## Scope and selected request

The user requested accounting of the recent calorimeter software-chain work and
a PR that only updates its tokens. This isolated branch starts at main
`fdfa09a0fb58dd29af467054f9a7dc0b023e30f1` with no unrelated changes. No native software
runtime or new external dependency is needed for accounting.

## Findings and outcome

All eight relevant closed development turns were already counted via PR59.
Their exact subtotal is 27,882,303 input + 195,220 output = 28,077,523 tokens,
with cached input 27,035,136 and reasoning output 69,214 as subsets.
The PR gives them a [dedicated canonical record](SESSION-2026-10-10-calorimeter-software-chain.md), moving the complete
entries unchanged from the mixed desktop recovery owner. The old owner keeps
two material-tool turns; the recovery inventory remains byte-identical.
Fresh usage recovery confirms all eight counters, request hashes and boundaries.
The whole project remains at 183 disjoint turns / 552,937,331 observed tokens.

## Commands and validation

Read-only project/client usage inspection, main fetch, clean worktree creation,
and dry-run followed by validated import were performed. A first search used an
unmatched path/glob from the workspace parent; it was corrected to explicit
repository-relative paths. Final check results are in paired JSON.

## Token accounting and limitations

This active bookkeeping turn is excluded until its final client boundary closes.
The previously closed October 12 dashboard/accounting turns are not calorimeter
software development and are not imported into this subtotal. Old counting
exclusions and unrelated historical gaps are preserved. Exact model/client
version remains unknown; no estimate, cost or private model state is retained.

## Follow-up

Review this token-only PR. Detector/ACTS source, design status and dashboard
implementation are unaffected. The enclosing commit is located through Git
history; no self-referential result hash is recorded.
