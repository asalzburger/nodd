# PR conversation frontend contract

Work root: `/Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-interactions`.
Keep the existing token chart working. Parent handles Python generation and
all files except `tools/token_usage/interactions.js`, `interactions.css` and
`test_interactions.js`; these three are your only writable files.

## HTML

Both pages share existing `style.css` and new `interactions.css`. A normal
`nav.site-tabs[aria-label="Views"]` immediately below the header contains
`<a href="./">Token usage</a>` and `<a href="interactions.html">Interactions</a>`;
the active link has `aria-current="page"`. These are page navigation, not fake
ARIA widgets. The new page loads only interactions.js, not app.js.

The new page has `main.interaction-page`, intro h1 "PR conversations", then
`div.interaction-layout` containing `aside.pr-picker` and
`section#conversation-panel.conversation-panel[aria-labelledby="pr-title"]`.
Aside children: label for `#pr-search`, search input, `#pr-results` status,
and `div#pr-list.pr-list` (render navigation links/buttons here).
Panel children: `#interaction-status[role=status][aria-live=polite]` and
`div#pr-detail[hidden]`. Detail contains `.pr-heading` with `#pr-number` eyebrow,
`h2#pr-title`, `#pr-coverage`, and `a#pr-github`; then
`div#participants.participant-strip`; `.conversation-controls` with label and
`select#source-select`; `div#conversation[role=feed][aria-label="PR interaction messages"]`;
and `details.evidence-panel` with summary "Roles, tools & token references" and
`div#pr-evidence`.

## Data

Fetch `interactions.json` for index:

```json
{"schema_version":1,"metadata":{"source_commit":"SHA","built_at":"UTC"},"pull_requests":[{"number":98,"title":"Infrastructure: ...","state":"open","url":"https://github.com/asalzburger/nodd/pull/98","record_count":20,"parties":["Project user","Codex"],"captured_at":"UTC","sources":[{"id":"github","label":"GitHub discussion","count":1},{"id":"recorded","label":"Recorded messages","count":10},{"id":"notes","label":"Session notes","count":9}],"data":"interactions/pr-0098.json","missing_turns":0}]}
```

Index order: newest PR number first. Search number, title and parties. Preserve
number with `?pr=98`; source selection may use `&source=recorded`. Support direct
links and back/forward navigation. A new PR selection chooses recorded messages
if available, otherwise GitHub when it contains human actions, otherwise notes.
You may use a simpler consistently explained default if needed; do not merge
sources into a fabricated chronological transcript.

Each data URL has:

```json
{"number":98,"title":"Infrastructure: ...","url":"https://github.com/asalzburger/nodd/pull/98","state":"open","captured_at":"UTC","parties":[{"id":"human:x","name":"Project user (name unrecorded)","kind":"human"},{"id":"agent:x","name":"Codex","kind":"agent"},{"id":"github:asalzburger","name":"asalzburger","kind":"account"}],"agents":[{"id":"agent:x","name":"Codex","role":"primary coordinator","models":[]}],"tools":{"native_codex":[{"name":"exec_command","version":null,"source":"https://github.com/asalzburger/nodd/blob/SHA/file"}],"codex_installed":[],"instructed_software":[],"unresolved":[]},"accounts":[{"id":"SESSION-...","status":"unobserved","turn_count":0,"source":"https://github.com/asalzburger/nodd/blob/SHA/file"}],"coverage":{"missing_turns":2,"recovered_turns":5,"note":"Selected historical evidence; missing history and models remain unknown."},"groups":[{"id":"recorded","label":"Recorded messages","description":"User-visible messages in their recorded turns; not a complete history.","threads":[{"id":"turn:UUID","label":"Recorded turn","timestamp":"2026-10-24T09:00:00Z","messages":[{"id":"event:x","type":"prompt","direction":"action","actor":"human:x","text":"Original visible text","source_url":"https://github.com/asalzburger/nodd/blob/SHA/file","source_label":"Recorded message","reply_to":null,"model":null,"roles":[],"timestamp":null}]}]}]}
```

Groups only include nonempty sources; GitHub and notes have the same thread
structure. Timestamps can be null. Thread time is turn start, not a measured
message timestamp. The builder projects allowlisted data from validated ledgers;
private state, raw rollouts, numeric token counters and arbitrary source JSON are
not shipped. Account turn counts are source references, never per-message token
allocations or additive PR totals.

## Interaction and design

Create a polished, calm interface consistent with the existing dark teal/muted
teal dashboard: compact PR sidebar, generously spaced chat cards, human/agent
bubbles and initials/role badges, readable long messages. A publishing account
is labeled as such and not silently called a human or Codex. Clear source
selection avoids duplicate journal excerpts masquerading as transcript turns.
Display source descriptions and missing-history context. Every message has a
source link; unknown models need no repetitive warning per bubble but remain
clear in the evidence panel. Long text should have an accessible expandable
preview. Use textContent and safe DOM creation; do not execute Markdown/HTML.
Source links allow only http/https, no javascript/data schemes; do not turn
arbitrary text into HTML. Tool and account evidence can use native details.

Handle loading, fetch failure, no matching PRs, empty sources, missing actors,
malformed PR query numbers and race conditions during rapid navigation.
Responsive layout must work at 390px and desktop. Keyboard users can search,
select PR/source, follow evidence and expand text. Style nav globally through
.site-tabs only; scope remaining CSS to .interaction-page to avoid affecting
existing token charts. Do not use external libraries or fonts.

Tests should exercise real frontend logic where practical (factored pure
functions exported for Node are fine), including search, URL state, safe URL
handling, sender kinds, long text and rendering malicious source text literally.
Parent will perform the actual browser checks.
