# Prepare PR137 and preserve the calibration for reuse

User request (2026-11-12): “Can you prepare the PR for merging, recording the calibration model for later usage ?”

Bounded follow-up on PR137, start d862d943600307a67a10a08c5644e7e4cf224007. Preserve existing coefficients, frozen numerical source, all plots/statistics and primary inputs. No new training, transport, geometry or sign-off. The request authorizes ready-for-review preparation of this PR, not merging it or its predecessors.

Used nodd-coordinate and nodd-review-validation. No native runtime use or shared dependency changes; existing NumPy Python only.

Initial public state: PR137 draft, mergeable into its existing PR136 base, two successful workflows, no reviews/comments/unresolved threads. Open stack PR133(main)→134→135→136→137 remains explicit. Prepare137only; do not approve/merge/retarget predecessors or rewrite history.

Recorded spline-v1(default) and linear-v1 IDs, domain, units, hashes, exact feature semantics and inference/fallback equations in frozen/manifest.json and reuse.md, keeping coefficients at SHA8595d8fd74d17edf2561d889e52910b3badbd358b446b951ca5083938c7ccdf1 and frozen source unchanged. Added highstat_inference API/CLI with hash/geometry/semantics guards, measured-only columns, output provenance/flags and no overwrites. Added7 meaningful reuse controls and CI coverage using the already pinned NumPy environment.

All16 NumPy controls pass (7new+6model+3analysis). Exact20k population replay reproduces all4linear/spline pre/post energy-ratio series bit-for-bit, all84zeros. An initial10k-vs20k bit check failed at batch-size floating-point matrix-product rounding; kept this failure, no model/reference/test tolerance changed. Ten-k chunked diagnostics measure maximum4.885e-15 ratio difference, no mean difference; full20k exact check passes. Compact reuse-verification JSON records this distinction; arrays remainlocalignored.
