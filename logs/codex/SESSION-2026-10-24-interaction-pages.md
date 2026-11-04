# SESSION-2026-10-24-interaction-pages — PR conversation navigator

## Scope

Extend the existing GitHub Pages resource ledger in PR98 on codex/pr-interaction-ledger, starting at `4cc9b95495593299c59377f2ffd171f9fb6d9dbd`. Preserve the token chart and canonical usage accounting. Main-only Pages deployment and PR preview artifacts remain under the established workflow.

## Selected conversation

User request, exact: “Great, can we add a second tab to the GitHub deployed pages that allow to navigate through the PRs and see the interactions - it could be nicely graphical (per PR) as a conversation between humans and agent(s)”

Assistant approach: add a PR Interactions tab with searchable PR navigation, sender-specific conversation cards, source-separated recorded messages/GitHub/session notes, and expandable role/tool/account evidence. Export only a validated allowlist of already-curated public interaction fields. Missing history, unreported models and shared account boundaries remain explicit.

## Specialist assignment INTERACTION-PAGES-SoftEng-01

Prepared before dispatch at `4cc9b95495593299c59377f2ffd171f9fb6d9dbd`; SoftEng explicitly assigned through generic child `/root/softeng_interaction_pages`. Parent owns export/build/HTML and QA; child owns three disjoint frontend files. Full contract, prepared prompt and curated result are retained in the session directory. No native profile loading or human approval is claimed.

## Outcomes

Assistant outcome: implemented an Interactions tab alongside Token usage, with search across 91 PRs, human/agent conversation cards, explicit publishing-account identity, source links, long-message expansion and expandable roles/tools/account references. PR and source selections have shareable URLs and support browser history. Recorded messages, GitHub discussion and selected journal excerpts remain separate source views with coverage limitations. Models and message times are only shown when evidenced.

Assistant implementation: the stdlib exporter validates canonical ledgers and publishes an allowlist to a small index plus lazily loaded per-PR JSON payloads. Site output accepts only its exact static files and PR payload names, rejecting unexpected or stale files and symlinks. Token arithmetic and ownership stay unchanged. No additional packages, external frontend services or scientific progress items were introduced. The existing Pages workflow builds PR previews and deploys from main; the new tab becomes public after merge.

Assistant validation: 15 Python token/site tests and both JavaScript suites pass. Browser checks covered tab navigation, PR search/selection, recorded and GitHub source views, browser back, long-message expansion and evidence disclosure. At 390 × 844 the page and long identities wrap without horizontal overflow (content and viewport both 390 px). The temporary viewport override was reset. A duplicate link arrow found during visual QA was removed. Session, project, interaction/accounting and usage validation pass; preview build retains 234 disjoint turns and 740,993,210 observed tokens. The current task and child have no exact completed token counters, so no usage is added.

## Execution and checks

Used the repository `nodd-coordinate` skill and explicit SoftEng assignment. Parent used native shell/patch tools, GitHub connector/CLI, Codex bundled runtime discovery and the CUA browser plugin. The local-only HTTP preview initially failed sandbox binding; the approved escalated server then served the preview. No detector runtime was needed. CUA startup was slow but the page loaded and interactive checks completed.

Commands included Python unittest discovery for `tools/token_usage`, both JavaScript suites, the session validator/summary, project validator, interaction validation against the starting revision, usage validation, site build and whitespace checks. CI includes the new navigation suite. Retained screenshots are preview artifacts, outside the generated Pages output allowlist.

## Usage

Exact completed parent and specialist usage counters are unavailable. No observations are imported or estimated.
