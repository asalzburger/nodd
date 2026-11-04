# CUMULATIVE-PhysVal-01 independent assessment

Read-only child `01a17838-6a10-7d90-97e4-72586f074dd1` reviewed exact source
**bffaba61f2d243ac2025de2476b34411437798fa** under the explicit PhysVal mandate.
No files changed, native rerun, rebuild, install or human acceptance.
**No blocking findings.** The five figures address the three observables in
[noemina's comment](https://github.com/asalzburger/nodd/pull/100#issuecomment-6415806657).

The physical definitions agree with the source: fractional homogeneous Geant4
pre/post steps versus thin ACTS interaction jumps; no second incidence correction.
Per-ray contributions precede means/SEM, preserving step correlations and zero
prefixes. Empty rays and interval boundaries have analytic controls. Checkpoint
holding is explicit; all retained final intervals equal the endpoint plateau,
so the displayed curves retain the full budget at their right edge.

Actual checks:

- Read seven pinned inputs with `git show` and verified source/data and five
  PNGs match the target. Concurrent dirty metadata was excluded.
- All 36 portable controls and the retained source/count/monotonicity/endpoint
  audit passed.
- Verified complete ROOT SHA-256 values and independently recomputed direct
  segment fractions and per-ray sums. Per sample, 38 representative checkpoint
  quantity comparisons and 18 all-slice endpoint comparisons match means within
  2.89e-15 and SEM squared within 8.15e-19. This is independent of the exporter's
  difference-array algorithm.
- All 32 CSV comparisons agree exactly with profile data. Counts reproduce
  100,000 rays per sample, 17,137,021 Geant4 steps and 1,417,441 ACTS interactions.
  Origins are zero; maximum off-ray position residual is below 0.000171 mm.
- All five PNGs are readable with correct labels/counts and endpoint plateaus.

The report correctly retains 0.36268 X0 at |z|=1330 mm, 1.5≤|eta|<2, about
15% of that slice's final Geant4 material, as a descriptive discrepancy.
Close final totals do not establish spatial agreement or isolate a unique cause.

Limits remain: fixed-map SEM, omitted training/systematic uncertainty, correlated
checkpoints, differing within-slice ray mixtures, phi=1, unknown original
geometry revision/seed, and origin straight rays only. No sensor-order or
tracking-performance acceptance is granted.
