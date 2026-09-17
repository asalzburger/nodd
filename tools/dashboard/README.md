# Project dashboard

Build with Python 3.10 or newer and Git; no Python packages, JavaScript toolchain,
network calls or TDR submodule checkout are required.

```sh
python3 -B tools/dashboard/build.py validate
python3 -B -m unittest discover -s tools/dashboard -p 'test_*.py' -v
python3 -B tools/dashboard/build.py build
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Visit `http://127.0.0.1:8000/pages/`. Stop the server with Ctrl-C. All content
and detail links are rendered in HTML; JavaScript adds shareable filtering and
opens deep-linked task details. Empty review history is shown explicitly.
Assets and evidence URLs are relative so the output also works under a GitHub
Pages project URL prefix. Open `_site/pages/index.html` directly for an
offline view. Generated output is ignored by Git.

`--repo PATH` selects input records from another checkout; `--output PATH` sets
output. Within the repository, output must be inside `_site/`. Use a fresh output
directory when the evidence allowlist changes: the builder rejects unexpected or
stale output files rather than silently packaging them. `--built-at
2026-09-17T12:00:00Z` supplies fixed build metadata for reproducibility checks.
Normal builds record actual UTC build time, source HEAD and working-tree state.

See the [tracking workflow](../../project/README.md),
[proposal](../../docs/DASHBOARD_PLAN.md) and
[CI workflow](../../.github/workflows/dashboard.yml).
The workflow validates and builds every PR and uploads a preview artifact. A
successful push to `main` (or manual run on `main`) also packages `_site/pages/`
and deploys it through the `github-pages` environment. PRs and manual runs on other
branches never deploy. The build job has read-only repository permissions;
only the deployment job receives `pages: write` and `id-token: write`.
Main deployments are serialized; PR preview runs may be superseded.
The site target is `https://asalzburger.github.io/nodd/`.

Set repository Settings → Pages → Build and deployment → Source to **GitHub
Actions** (API `build_type: workflow`). The Pages environment should allow only
`main` deployments. This task prepares these settings when repository permissions
allow; actual setup results are recorded in the session log/PR. Merge the chore
PR to trigger the first publication; creating it does not merge or publish its
branch. No custom domain or TDR submodule is required.

For each non-chore project PR, update the tracking/review registers in that PR.
CI checks this from the PR title and changed paths. `chore: ...` and
`chore(scope): ...` titles exempt repository maintenance from progress tracking;
scientific/design/evidence changes cannot use the exemption. Chores still rebuild
the dashboard after merge. Review and merge snapshots are curated, not live API
polling; update them when known. See the repository instructions for the mandatory
maintenance rule.

Download and serve extracted preview artifacts with Python's HTTP server to
review them. If a deployment fails, the last published site remains available
with its source revision/build time; inspect the Project dashboard workflow and
rerun on `main` once the failure is resolved. Rebuilding does not alter accepted
evidence. To roll back, use a reviewed revert on `main` and let it deploy normally.

Actions configuration follows the official
[checkout](https://github.com/actions/checkout),
[setup-python](https://github.com/actions/setup-python) and
[upload-artifact](https://github.com/actions/upload-artifact),
[Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
and [deploy-pages](https://github.com/actions/deploy-pages) documentation
(accessed 2026-09-17). Hosted CI has not run merely because this workflow exists.

Optional interaction tests run with the Node runtime available on GitHub-hosted
runners:

```sh
node tools/dashboard/test_app.js
```

On macOS the same synthetic DOM tests can run without Node:

```sh
/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc tools/dashboard/test_app.js
```

JavaScriptCore uses a URL test shim because its shell lacks browser URL APIs;
Node uses native URL APIs. These checks exercise filtering, URL restoration,
empty states and deep links; they do not verify browser rendering.

Tests cover initialization, the actual PR #4 review history and approval scope,
formatted document statuses, merge metadata, revision changes, repeated and conditional reviews,
approval consistency, missing criteria, invalid dependencies, output allowlists,
escaping, deterministic builds and every generated local link/fragment. Browser
rendering, keyboard and mobile checks require a browser and should be completed
before publication. Schema validation and evidence consistency do not grant
human scientific approval.
