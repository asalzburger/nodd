# SESSION-2026-10-30-token-step-labels — Label recorded token graph steps

## Scope and evidence

Infrastructure follow-up starting from main at `e8bc28b5f8720edb1ca706605fc4a9ac851950b9`, on a clean checkout now using `codex/token-step-labels`. PR98 was already merged. Work is confined to the token dashboard and its curated task evidence. ADR-004 remains DRAFT; no scientific progress or design approval is recorded.

## Selected conversation

User request, exact: “I need another infrastructure work: the token counting graph has a few steps that are not labeled, it would be great if they could get labels to identify on what the tokens were spent.”

Assistant approach: label every recorded UTC-day step automatically from the canonical session that owns each counted turn. Keep merge milestones and observed work dates separate. A day spanning sessions names its leading session and explicitly indicates additional sessions; selecting the step expands all contributions and journal/PR evidence.

## Decisions and outcomes

Assistant outcome: added numbered, accessible graph links with work labels in hover/focus tooltips and a full Work behind each step list. The list has labels for all 28 observed days, newest first, and expandable daily input/output/combined subtotals by canonical session. Days spanning a session include only that day's turns. Shared PR references do not split or duplicate token counts. Existing seven merge markers remain as separate dated feature evidence.

Assistant implementation: the site derives session titles, source paths, turn counts and observed per-day subtotals from the same validated unique turn owners and closed UTC boundaries used by the curve. No new usage is collected or estimated. Current source accounting remains 309 disjoint turns and 1,306,633,934 observed input-plus-output tokens. Unknown counters remain null, undated observations receive no fabricated dates, and the JSON projection contains no raw client thread/turn IDs.

## Commands and validation

`python3 -B -m unittest discover -s tools/token_usage -p 'test_*.py' -v`: 20 tests passed, including five new work-attribution tests. Covers replayed inventories, same-session turns spanning days, shared PR scope, unknown/undated counters, escaped titles and real-data reconciliation for every counter and step.

`node tools/token_usage/test_app.js`: chart modes, keyboard labels, step selection, deep links and scrolled tooltip positioning pass. `python3 -B tools/token_usage/build.py build --output _site/token-step-labels-preview`: both tabs build with the unchanged observed subtotal.

Browser checks confirmed numbered point spacing, a focus tooltip identifying the October 26 truth-tracking work, and point selection expanding that day's six source sessions. Phone layout and closeout checks are recorded below when complete. The local-only HTTP server initially failed sandbox binding, then ran with approved escalation. No detector runtime or dependency installation was needed.

## Token accounting

Exact completed counters for this active task are unavailable; `usage` remains empty. The historical counters are only projected into labels and are unchanged. No token estimates, costs or inferred models are added.

## Specialist assignment TOKEN-STEPS-SoftEng-01

Prepared before dispatch against implementation `49613ee448850f28dd86f02eb508d20860879168`. A separate generic child receives the full explicit SoftEng mandate and read-only assignment in the session directory. It assesses attribution boundaries, escaping and interaction semantics, owns no files and may run pure local checks. No native profile loading or independent scientific/human approval is claimed. The coordinator retains QA and delivery.

## Review and final QA

PR108: https://github.com/asalzburger/nodd/pull/108. Separate SoftEng assessment found no actionable correctness findings at `49613ee448850f28dd86f02eb508d20860879168`, independently running all 20 site tests, Node checks and an exact parent/target accounting comparison. Its prepared mandate, input hashes and curated report are retained in the session directory.

Browser QA passed for all counter modes, focus descriptions, graph click/Enter selection and fragment reloads. At 390 × 844 the body width is 390 px; labels, disclosure panels and subtotals fit. A horizontally scrolled tooltip initially shrank to its minimum content width; explicit CSS width fixes it, verified in the phone browser. Disclosure glyphs became chevrons. These later CSS-only changes are coordinator work outside the reviewed source target. Temporary viewport override was reset.

All numeric daily/cumulative counters, dated boundaries, undated subtotals and feature markers equal the saved pre-change baseline. Session and project validators pass. The new PR's interaction ledger retains this prompt, outcome, assignment/result, named parties/roles, tool evidence and unobserved token account. Main-only Pages deployment remains unchanged; PR108 provides the reviewable change and preview build.
