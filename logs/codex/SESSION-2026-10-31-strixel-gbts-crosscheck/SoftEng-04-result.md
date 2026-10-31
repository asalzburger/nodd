# STRIXEL-GBTS-SoftEng-04 — bounded portable retention

Child `/root/strixel_gbts_analysis` applied the explicit SoftEng mandate fallback
against native source revision `8c45136098d1e4d407c4d2f96e3590bb78eb6b75`,
plus the explicitly hashed parent statistical amendments. Only `analyze.py` and
`test_analyze.py` changed. No native launch, commit, shared dependency change,
publication or further delegation. No native profile loading or human sign-off
is claimed. Exact client usage is unavailable.

Added optional `--jobs N` (default 1) with spawned per-case workers, bounded
outstanding submissions, deterministic inventory order, import/launch/worker/close
source guards and failure cancellation. Completed partial case artifacts remain
on failure; no complete inventory is then written. Statistical reduction and
the frozen DES041 classifier are unchanged. Parent zero-discordance and net-count
amendments are preserved.

Final analyzer SHA256:
`6d4643aea8236370b7d549764e84989d589cb16b7335dd803290de1b835836dc`.
Final analyzer-test SHA256:
`9f39497da81e1cba06feafb73f8219104a82b699023ee9765af5fa6bddf4fde4`.
Frozen classifier remains
`972a4ebea1c402a2d5d22d07c90508b6f1a722628d3886a70e9d896a8c2339ab`.

All 46 reconstruction tests pass, including nine new adverse orchestration/source
cases. The actual three-worker Fatras electron100GeV four-pitch × 1000-event
pilot matches the serial reference: all 316 arrays (dtype, shape, values and NaN
masks), summaries, configurations, inventory case entries, all point statistics
and 400-bootstrap groups, plus Markdown. Standalone `--verify --jobs 1` exited 0.
[Comparison record](serial-parallel-comparison.json) retains hashes. Exposed
wall/user/system times are 178.92/324.13/8.69 seconds. The timing wrapper itself
exited1 after blocked `sysctl kern.clockrate`; peak RSS is unknown. This is not
reported as an analyzer failure or a memory-performance measurement.

Coordinator independently repeated all 46 tests (3.115 seconds), every 316-array
comparison, summaries/configurations, profile groups and report text: all pass.
Session217 and project81-task/42-document/23-review checks pass. Final full-matrix
scientific review remains separate. Native HEAD and runtime/campaign bytes remain
fixed while the production queue runs.
