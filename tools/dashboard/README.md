# Project dashboard

Build with Python 3.10 or newer and Git; no Python packages, JavaScript toolchain,
network calls or TDR submodule checkout are required.

```sh
python3 -B tools/dashboard/build.py validate
python3 -B -m unittest discover -s tools/dashboard -p 'test_*.py' -v
python3 -B tools/dashboard/build.py build
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Visit `http://127.0.0.1:8000/dashboard/`. Stop the server with Ctrl-C. All content
and detail links are rendered in HTML; JavaScript adds shareable filtering and
opens deep-linked task details. Empty review history is shown explicitly.
Assets and evidence URLs are relative so the output also works under a GitHub
Pages project URL prefix. Open `_site/dashboard/index.html` directly for an
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
The workflow validates and builds PR/main snapshots and uploads a preview
artifact. It has read-only repository permissions and no Pages deployment job.
Download and serve the extracted artifact with Python's HTTP server to review it.
A hosted publication is a separate next step after reviewing the working build.

Actions configuration follows the official
[checkout](https://github.com/actions/checkout),
[setup-python](https://github.com/actions/setup-python) and
[upload-artifact](https://github.com/actions/upload-artifact) documentation
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
