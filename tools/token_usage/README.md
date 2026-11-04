# Resource ledger: token usage and PR interactions

The 2026-10-12 human request replaces the former project-progress dashboard with
a GitHub Pages view of cumulative observed token usage. No external chart library,
package install, private client-store access or TDR submodule checkout is needed.

```sh
python3 -B tools/session_logging/session_log.py validate
python3 -B tools/token_usage/build.py validate
python3 -B -m unittest discover -s tools/token_usage -p 'test_*.py' -v
node tools/token_usage/test_app.js
node tools/token_usage/test_interactions.js
python3 -B tools/token_usage/build.py build --output _site/pages
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site/pages
```

Only validated `logs/codex` and `logs/design` turn entries contribute to totals.
Thread/turn ownership must be unique. `logs/usage` inventories supply exact
closed-turn end times and corroborating counters, never additional usage. Repeated
inventory snapshots cannot inflate totals. Older explicitly in-progress snapshots
with no closing boundary are checked as lower bounds; they supply neither final
counters nor dates. Conflicting finalized counters/timestamps and provisional
counters exceeding the recorded final counters stop the build. Untimed observations
remain in the headline subtotal but outside the curve. Session creation, import
and commit dates are never substituted for usage
dates. Days use UTC and observations are grouped by closed-turn end day.

Input plus output is the observed total. Cached input and reasoning output are
subsets, not additions. Missing fields and sessions remain unknown, not zero.
The site shows all-project observed coverage, without estimating cost or billing.
A dashed extension only carries the known subtotal after the last observation;
it does not claim no work occurred. Exact daily totals remain available in a table.

The selected labels on the time axis come from `project/token-milestones.json`.
Each retains an actual GitHub merge timestamp, full source revision and PR link.
Markers describe delivered features/prototypes, not human design sign-off. Update
this small curated list for major milestones; do not turn it into another task
tracker. Canonical usage changes rebuild the curve automatically.

Each observed daily step also has a numbered work label. Hovering or focusing a
step names its leading recorded session and daily increment; selecting it opens
the corresponding **Work behind each step** entry. Every day's full label is
visible in that list, newest first. It expands to all canonical session
contributions, exact observed input/output/combined subtotals and journal links.
PR links are references to the session's recorded scope, not allocations to each
PR. Merge milestones and recorded spending dates are independent evidence.

These labels derive automatically from the same unique turn owners and exact
UTC completion dates used for the curve. A session spanning days contributes
only that day's turns; repeated recovery inventories do not add work or tokens.
Titles describe the owning session, which may cover several tasks. Sessions are
ordered by observed combined tokens; missing counters remain unknown, and
undated observations receive no invented graph date. Adding accounting therefore
updates work labels without editing a second hand-maintained milestone list.

The [Pages workflow](../../.github/workflows/token-usage.yml) builds preview
artifacts for PRs and publishes only from main through GitHub Actions artifact
deployment. It never pushes a generated site to a Git branch. Existing Pages
settings continue to use the GitHub Actions source. The former dashboard workflow,
renderer and browser assets are removed; scientific record checks and prototype
regressions remain in the separate [validation workflow](../../.github/workflows/validation.yml).

The builder records source HEAD, dirty state and UTC build time. `--built-at`
accepts a fixed UTC time for reproducible previews. Inside the repository output
must be under `_site/`. The exact allowlist includes the two HTML pages, their
CSS/JS, `usage.json`, `interactions.json`, `.nojekyll` and one
`interactions/pr-NNNN.json` payload per validated PR. Unexpected files, stale PR
payloads and symlinks stop the build. Private PDFs and raw recovery inventories
are not packaged. The token JSON contains aggregates, feature markers, per-step
canonical-session subtotals/titles/source paths and source metadata. It does not
export raw client thread/turn IDs, tool arguments or recovery inventories.

The **Interactions** tab provides searchable PR navigation and human/agent
conversation cards. Links such as `interactions.html?pr=96&source=recorded` retain
the PR and source across browser history. An initial public index loads first;
individual PR payloads load on selection. `interactions.py` validates the
[canonical ledgers](../../interactions/README.md) and exports only selected text,
parties, roles, tool names, account references and safe source links. It neither
reads private client stores nor copies raw tool arguments or token counters.

Recorded visible messages, GitHub discussion and selected session notes appear
in separate views. Turn start times describe the turn, not individual messages;
upload references have no inferred timestamp. Journal excerpts may summarize
several inputs and are labeled accordingly. Unreported models and gaps in
historical coverage remain unknown. Shared token accounts link to the canonical
owner and do not become additive PR totals. Message text is rendered as plain
text, with long messages expandable and source links retained. Refreshing the
canonical interaction ledgers through the accounting workflow automatically
refreshes this tab in the next Pages build.

The dashboard rebuilds checked-in observations; it is not live client telemetry.
The October 12 backfill demonstrates recovery from desktop chats at a parent
workspace through explicit thread selection. For subsequent tasks, recover and
attribute previously closed project turns with the [authorized logging workflow](../../logs/README.md#authorized-local-historical-recovery).
A turn still active during closeout cannot yet supply final counters. Capture it
in a later task after its boundary closes, preserving earlier counting exclusions.
