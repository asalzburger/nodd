# SESSION-2026-10-21-pr91-token-accounting — PR91 exact token accounting and merge readiness

## Scope and request

The user asked to add token accounting to PR91 so they can merge it, and will
follow up with ACTS themselves. Update the existing PR; do not merge it or
implement the proposed ACTS initialization change. Starting source is
d11e8bb43aa5b4473974f234da08092cc5934705 with a clean worktree.

## Recovery and attribution

Followed the authorized local usage-only workflow in logs/README.md. Explicitly
selected this desktop chat and its two recorded specialist children using
read-only SQLite metadata. No conversation items or private model state were
queried. Only numeric token-count events are decoded by the existing tool.
Parent/child edges and exact agent paths match the journal's bounded assignments;
all specialist turns belong to the original parent profiling turn. The two
completed user-visible explanation turns also belong to the PR91 work.

The retained inventory documents eight closed turns and267 requests, ten
repeated snapshots ignored and no outside-turn events. Each cumulative increase
matches its own last-request observation; streams reconcile separately from
zero, avoiding parent/child aggregation. All eight entries have one canonical
owner, SESSION-2026-10-21-material-profile. Dry-run/import/replay adds eight,
then zero. Current active accounting usage remains excluded.

## Outcome and boundaries

Recovered 41,308,128 input + 205,567 output = 41,513,695 observed tokens.
Cached input 40,301,824 and reasoning output 100,184 are subsets. Input includes
cached/repeated context; these observations are not billing or unique-text
counts. Original unknown-usage narrative is preserved with a dated correction.
Model/client version and complete other-device history remain unknown.

This is maintenance within PR91, with no scientific-progress task, detector
change, design sign-off or ACTS implementation. Tests, final revision and
published PR state are recorded below and in the paired JSON. Exact counters
for this active accounting turn can be recovered only after it closes.

## Checks and closeout

Local validation passes: 194 paired records, 233 disjoint dated turns; 33 logging/recovery/document tests; 10 token-dashboard tests; JavaScript chart/keyboard controls; token-site build; and 70 task/39 document/21 review validation. The observed project subtotal is 733,830,533 tokens; PR91's 41,513,695 is included once. This maintenance adds no scientific-progress entries. Main remains an ancestor, and the worktree began clean. The metadata commit and PR body are published under the user's explicit request; no merge is performed. Hosted CI for the new head is checked separately after this journal closeout.
