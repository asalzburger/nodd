# Tracker resolution optimisation

**DRAFT / PROTOTYPE, 2026-10-27.** Governed by
[DES040](../../design/DES-040-tracker-resolution-optimization.md) and
[issue103](https://github.com/asalzburger/nodd/issues/103). This is an isolated
study following merged PR101, with constant3T, origin muons at1/10/100GeV,
geometric primary digitisation and a frozen-error Gaussian crosscheck.

The constrained search preserves envelopes, module types and local stave
structures. Only barrel radii, disk z positions and permitted stave counts move;
one additional mirrored pixel disk pair uses a homogeneous material disk behind
the sensitive faces. [Configuration and execution](../../../software/analysis/tracker_optimization/README.md).

## Exploratory evidence

Five layouts have2000events per momentum in
[the first comparison](exploratory.json.gz); the balanced follow-up adds6000
events in [its comparison](balanced-exploratory.json.gz). These statistics were
used for selection, not confirmation. Initial compacts omitted moving disk
collectors; preserve that failed physical audit and use corrected source for
the independent comparison.

| Layout | Ten-hit fraction at1/10/100GeV | Observed tradeoff |
| --- | --- | --- |
| Reference |86.7 /87.3 /87.8%| Forward deficit inherited from PR101 |
| Inner32 |86.9 /87.5 /88.3%| Small impact-parameter gain; weak coverage change |
| Inner family |87.5 /88.0 /89.05%| More inward inner layers; outer lever arm fixed |
| Mild, donor2 |95.9 /96.7 /97.0%| Added900mm disk; modest resolution tradeoffs |
| Coverage candidate |99.2 /99.2 /98.95%| Rejected as a full solution: forward d0/curvature worsens |
| Balanced |98.35 /98.85 /98.75%| First/farthest disk fixed; momentum preservation needs confirmation |

The balanced layout uses pixel barrel radii31.5/57/96/182mm and unchanged
12/22/18/30 staves. Existing disk datums are615/865/1115/1333/1565/1780/2090/
2440/3070mm, plus one donor2 disk at950mm per end. Its exploratory global d0
width ratios are0.923/0.988/0.951, z0 ratios0.950/0.974/0.972 and relative-pT
ratios1.065/0.977/1.063. These are conditional empirical core widths, without
tail cuts; neither a global ratio nor higher coverage proves all objectives.

The finite-patch screen and full16000proposal ledger are retained separately:
[screen](finite-screen-donor2.json), [trials](finite-screen-donor2.trials.json.gz).
These ignore material/curvature and are not native performance measurements.

## Native mechanical and material checks

Full ROOT overlap tolerance is1e-5mm. Original reference: zero overlaps.
Initial coverage compact:13486 overlaps (collectors/rail cutouts), retained as
[failed evidence](coverage-native-overlaps.json.gz). Corrected collectors and
rail slots move with complete disk assemblies; the corrected coverage and
balanced compacts both have zero native overlaps. Service trunk inventories
remain frozen reference cells, with routing/capacity explicitly unqualified.

Each candidate rebuilds native material and calibration keys by logical roles.
Area/count Jacobians preserve integrated effective X0/L0/areal-mass inventories;
the extra disk adds a donor2 homogeneous slab after all sensitive faces. No
silicon/pipe slab is counted twice. This relocates aggregated mapped profiles;
component-resolved material and incidence-dependent errors need later validation.

Independent-seed confirmation and the Gaussian crosscheck are running. No
preferred production layout, momentum non-inferiority or detector sign-off is
claimed from the exploratory results.
