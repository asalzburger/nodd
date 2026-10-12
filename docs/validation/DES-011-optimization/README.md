# Corrected DES-011 bounded follow-up

PROTOTYPE evidence; no design or engineering sign-off. See the
[coherent report](../DES-011-service-constrained-optimization.md) and
[generated full per-mode/subdetector results](results.md).

Source: `ac61f766b34f9bb60748e8fc4258a41037ca1e33`. Eight primary cases plus three
radius/pocket comparisons. All new routes pass reference capacity and known
individual-component fit. Coverage, area and original-pocket cases pass dense
coverage guards. The spacing candidate **fails** the dense long-strip mean
guard and is not recommended. All five cases pass 72 native ACTS trajectories
each. Adverse capacity scenarios still fail.

`study.json.gz` decodes to the original numerical study byte-for-byte; its decoded
SHA-256 is in `artifacts.json`. `full-run-artifacts.json` preserves the complete
original run manifest. Large per-track diagnostic arrays stay in the ignored run,
with hashes retained; regenerate them using the snapshotted inputs/seeds and
source revision. Selected geometries, summaries and native audits are retained.

Independent post-run audits and the paired bypass training control have their
own provenance. `supplemental-artifacts.json` hashes those plus the view manifest.
