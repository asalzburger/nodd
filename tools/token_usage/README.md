# Token usage dashboard

The 2026-10-12 human request replaces the former project-progress dashboard with
a GitHub Pages view of cumulative observed token usage. No external chart library,
package install, private client-store access or TDR submodule checkout is needed.

```sh
python3 -B tools/session_logging/session_log.py validate
python3 -B tools/token_usage/build.py validate
python3 -B -m unittest discover -s tools/token_usage -p 'test_*.py' -v
node tools/token_usage/test_app.js
python3 -B tools/token_usage/build.py build --output _site/pages
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site/pages
```

Only validated `logs/codex` and `logs/design` turn entries contribute to totals.
Thread/turn ownership must be unique. `logs/usage` inventories supply exact
closed-turn end times and corroborating counters, never additional usage. Repeated
inventory snapshots cannot inflate totals; conflicting counters/timestamps stop
the build. Untimed observations remain in the headline subtotal but outside the
curve. Session creation, import and commit dates are never substituted for usage
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

The [Pages workflow](../../.github/workflows/token-usage.yml) builds preview
artifacts for PRs and publishes only from main through GitHub Actions artifact
deployment. It never pushes a generated site to a Git branch. Existing Pages
settings continue to use the GitHub Actions source. The former dashboard workflow,
renderer and browser assets are removed; scientific record checks and prototype
regressions remain in the separate [validation workflow](../../.github/workflows/validation.yml).

The builder records source HEAD, dirty state and UTC build time. `--built-at`
accepts a fixed UTC time for reproducible previews. Output is restricted to five
allowlisted static files; inside the repository it must be under `_site/`.
Repository records, private PDFs and raw recovery inventories are not packaged.
The JSON download contains aggregates, feature markers and source metadata.

The dashboard rebuilds checked-in observations; it is not live client telemetry.
The October 12 backfill demonstrates recovery from desktop chats at a parent
workspace through explicit thread selection. For subsequent tasks, recover and
attribute previously closed project turns with the [authorized logging workflow](../../logs/README.md#authorized-local-historical-recovery).
A turn still active during closeout cannot yet supply final counters. Capture it
in a later task after its boundary closes, preserving earlier counting exclusions.
