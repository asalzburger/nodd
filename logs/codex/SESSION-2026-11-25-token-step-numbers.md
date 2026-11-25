# SESSION-2026-11-25-token-step-numbers — Remove milestone annotations from the token chart

## Scope and evidence

A separate infrastructure task/PR from clean merged main on dedicated branch
`codex/token-step-numbers`. The paired JSON records the exact starting revision;
main already includes PR159's statistics tab and human/agent message colors.
No detector, scientific tracking or approval record changes apply.

## Selected conversation

Human, exact: "One more infrastructure PR: for the token dashboard on the GitHub pages you can remove the milestone labeling again (this is the dedicated lines and labels for #3 #14 #28 …), the numbers is enough"

Assistant outcome: removed dedicated feature-milestone lines, dots and PR/date
labels from combined, input and output charts. Kept numbered daily usage steps,
hover/focus details, keyboard/deep links and the work/session breakdown.

## Decisions and outcomes

Removed unused annotation styles, their source-list dropdown and obsolete UI copy.
The chart uses a compact 1100 by 360 viewBox, and date bounds depend on observed
usage plus build time. Historical milestone dates no longer widen the chart.
The existing immutable catalogue remains validated in usage.json for provenance;
its records and all canonical token observations are preserved.

Updated the resource-site software inventory usage and generated page for numbered
usage-step charts. No dependency, installation, scientific milestone or sign-off
was introduced. The change will be published through its own draft Infrastructure
PR and the existing main-branch Pages deployment workflow.

## Commands and validation

- All 28 token-site Python tests passed. The updated regression proves milestone
  metadata is absent from the page and cannot change SVG output in any counter
  mode, while step numbers/links and historical metadata validation remain.
- Both existing Node suites passed: chart controls/deep links and conversations.
- Token validation and the full Pages build passed.
- XML inspection of the three real built chart modes found numbered steps,
  no milestone annotation classes, and the compact viewBox in each.
- Inventory refresh/check and whitespace checks passed; generated diffs reviewed.
- Final canonical validator passed for 307 session records; PR160 interaction
  validation and historical base-ledger preservation passed.
- No browser-rendering pass is claimed; the connected browser/computer surfaces
  were unavailable earlier in this session. Existing static/interaction checks
  provide the verification recorded here.

## Changes and revision links

The paired JSON lists renderer/styles, existing regression test, method guide,
software inventory and this paired session. Generated site outputs remain ignored.
Implementation commit: `3b155ceff3d30dfc4f34900156e0a69b7dd3dc00`.
Opened [draft PR160](https://github.com/asalzburger/nodd/pull/160). Connector reads
confirmed its open/draft state, main target and empty public discussion/review
timeline. The selected public snapshot and canonical session references are
retained in `interactions/pr-0160.json`.

## Token accounting

No exact finalized client-reported counters or accounting IDs were exposed for this
active task. Usage remains empty/unknown; no historical observation was copied.
The canonical summary retains 589 turns, 3,319,239,723 observed input and 13,881,824
output tokens. Coverage is 205/307 sessions; 102 lack observations, including this
new task. Cached/reasoning subsets are not added again.

## Follow-up

Review/merge the separate draft Infrastructure PR to publish the simplified token
chart. A successful infrastructure build creates no scientific approval.
