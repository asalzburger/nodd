# DES-042 — Strixel pitch, truth tracking and service savings

**PROTOTYPE.** The baseline detector is unchanged. This study varies local-v
segmentation from 0.5 to 1/1.5/2 mm at fixed 75 µm fine pitch in both strixel
systems: barrel z and endcap radial direction. EC counts include both ends.

## Channel count and single-cell estimate

| Local-v pitch | Binary σv | Barrel channels | EC channels | Total channels | Reduction |
|---|---:|---:|---:|---:|---:|
| 0.5 mm | 144.3 µm | 990,904,320 | 530,841,600 | 1,521,745,920 | 0.0% |
| 1 mm | 288.7 µm | 495,452,160 | 265,420,800 | 760,872,960 | 50.0% |
| 1.5 mm | 433.0 µm | 330,301,440 | 176,947,200 | 507,248,640 | 66.7% |
| 2 mm | 577.4 µm | 247,726,080 | 132,710,400 | 380,436,480 | 75.0% |

Fine single-cell σu stays 21.65 µm. These pitch/√12 numbers are analytical
controls. The native geometric digitizer clusters multiple cells, so its
actual centroid response and covariance need not have single-cell widths.

## Native tracking sample and controls

PR104 balanced DD4hep → ACTS geometry, unchanged role-transported effective
material map, constant 3 T field, one origin muon/event, random charge,
uniform eta [-4,4], full phi, pT 1/10/100 GeV. Each pitch/momentum case has
20,000 generated events: **240,000 events across twelve cases**. This is
Fatras plus native geometric digitization and a truth-associated Kalman fit.
It uses pitch-derived clustered covariance with no old 0.5 mm calibration.
Truth association/seeds exclude pattern-recognition and occupancy tests.

All four variants at each momentum have identical generated truth and exact
all/primary simulated-hit payload hashes. Balanced sensitive inventory is
6,794 pixel barrel, 2,808 per pixel endcap, 8,064 strixel barrel, 4,320
strixel endcap, 13,968 long-strip barrel faces and 7,488 endcap faces.
Geometry/material comparisons pass for every native case.

| pT [GeV] | Pitch [mm] | Finite fits / generated | Native matched / generated | Finite fits failing 5×5 covariance checks | Wrong charge / finite fits |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.5 | 19,995/20,000 | 19,995/20,000 | 0 | 0/19,995 |
| 1 | 1 | 19,995/20,000 | 19,995/20,000 | 0 | 0/19,995 |
| 1 | 1.5 | 19,995/20,000 | 19,995/20,000 | 0 | 0/19,995 |
| 1 | 2 | 19,995/20,000 | 19,995/20,000 | 0 | 0/19,995 |
| 10 | 0.5 | 20,000/20,000 | 20,000/20,000 | 0 | 0/20,000 |
| 10 | 1 | 20,000/20,000 | 20,000/20,000 | 0 | 0/20,000 |
| 10 | 1.5 | 20,000/20,000 | 20,000/20,000 | 0 | 0/20,000 |
| 10 | 2 | 20,000/20,000 | 20,000/20,000 | 0 | 0/20,000 |
| 100 | 0.5 | 20,000/20,000 | 20,000/20,000 | 0 | 438/20,000 |
| 100 | 1 | 20,000/20,000 | 20,000/20,000 | 0 | 438/20,000 |
| 100 | 1.5 | 20,000/20,000 | 20,000/20,000 | 0 | 438/20,000 |
| 100 | 2 | 20,000/20,000 | 20,000/20,000 | 0 | 438/20,000 |

The covariance column counts finite fits lacking a valid covariance; native
audit counters and all failure flags remain in the retained event data.

## Measured track-resolution ratios

Central 68.27% half-width relative to the newly run 0.5 mm control;
1 means unchanged. Values below are conditional on finite fits in each
variant, with paired generated-event bootstrap standard errors (400 draws).
No residual/tail cuts are applied. Full SD/RMS, bias and pull diagnostics
remain in the CSV/JSON. The separately plotted common-success ratios test
survivor effects. Errors are statistical only.

| pT [GeV] | Absolute eta region | Pitch [mm] | z0 ratio | theta ratio | Relative-pT ratio |
|---:|---|---:|---:|---:|---:|
| 1 | 0–1 | 1 | 0.999 ± 0.001 | 1.000 ± 0.001 | 0.998 ± 0.006 |
| 1 | 1–2.5 | 1 | 1.001 ± 0.001 | 1.001 ± 0.001 | 1.002 ± 0.005 |
| 1 | 2.5–4 | 1 | 1.000 ± 0.000 | 1.000 ± 0.000 | 0.999 ± 0.002 |
| 1 | 0–1 | 1.5 | 1.000 ± 0.001 | 1.000 ± 0.001 | 1.011 ± 0.007 |
| 1 | 1–2.5 | 1.5 | 1.000 ± 0.001 | 1.001 ± 0.001 | 1.014 ± 0.005 |
| 1 | 2.5–4 | 1.5 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.003 |
| 1 | 0–1 | 2 | 1.000 ± 0.001 | 1.000 ± 0.001 | 1.004 ± 0.007 |
| 1 | 1–2.5 | 2 | 1.001 ± 0.001 | 1.000 ± 0.001 | 1.005 ± 0.005 |
| 1 | 2.5–4 | 2 | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.001 ± 0.003 |
| 10 | 0–1 | 1 | 0.994 ± 0.006 | 1.009 ± 0.006 | 1.001 ± 0.003 |
| 10 | 1–2.5 | 1 | 0.998 ± 0.002 | 1.000 ± 0.001 | 0.998 ± 0.004 |
| 10 | 2.5–4 | 1 | 1.000 ± 0.001 | 0.998 ± 0.002 | 1.001 ± 0.002 |
| 10 | 0–1 | 1.5 | 0.998 ± 0.005 | 1.002 ± 0.005 | 1.001 ± 0.002 |
| 10 | 1–2.5 | 1.5 | 0.999 ± 0.002 | 1.000 ± 0.002 | 1.002 ± 0.005 |
| 10 | 2.5–4 | 1.5 | 0.999 ± 0.002 | 0.998 ± 0.002 | 1.000 ± 0.002 |
| 10 | 0–1 | 2 | 0.994 ± 0.007 | 1.002 ± 0.006 | 1.000 ± 0.003 |
| 10 | 1–2.5 | 2 | 0.999 ± 0.002 | 1.000 ± 0.002 | 1.000 ± 0.005 |
| 10 | 2.5–4 | 2 | 1.000 ± 0.001 | 0.999 ± 0.002 | 1.003 ± 0.002 |
| 100 | 0–1 | 1 | 0.885 ± 0.017 | 0.927 ± 0.014 | 1.001 ± 0.004 |
| 100 | 1–2.5 | 1 | 1.007 ± 0.004 | 0.991 ± 0.005 | 1.007 ± 0.005 |
| 100 | 2.5–4 | 1 | 0.998 ± 0.002 | 1.002 ± 0.003 | 1.002 ± 0.001 |
| 100 | 0–1 | 1.5 | 0.819 ± 0.016 | 0.877 ± 0.016 | 1.000 ± 0.004 |
| 100 | 1–2.5 | 1.5 | 1.009 ± 0.005 | 0.991 ± 0.005 | 1.008 ± 0.005 |
| 100 | 2.5–4 | 1.5 | 0.999 ± 0.003 | 1.000 ± 0.003 | 1.001 ± 0.001 |
| 100 | 0–1 | 2 | 0.769 ± 0.014 | 0.837 ± 0.014 | 1.003 ± 0.004 |
| 100 | 1–2.5 | 2 | 1.006 ± 0.005 | 0.989 ± 0.005 | 1.011 ± 0.005 |
| 100 | 2.5–4 | 2 | 1.001 ± 0.003 | 1.001 ± 0.003 | 1.001 ± 0.001 |

### High-momentum response diagnostic

At 100 GeV and |eta|<1, the native digital z0/theta core becomes narrower
with coarser cells. Every generated event in this region fits at every pitch, so survivor changes do not explain it.
The
uncut standard deviation changes less than the central width, and pull
standard deviations are well below one. This is an uncalibrated response
and fit-weighting sensitivity, not evidence that larger physical cells
improve a detector. The causal response assumption remains unqualified.

With the configured digital flag and merging enabled, the native merge
stage recomputes path-weighted cell centroids and both coordinate variances.
Both variances contain the same two-dimensional cell-weight concentration
factor. Coarsening local-v therefore also changes the reported fine-u
covariance. Source inspection and a small measurement-writing pilot verify
this coupling; they do not isolate the entire high-pT mechanism. See
[response-diagnostic.json](response-diagnostic.json) for source hashes.

| Pitch [mm] | z0 width68 [µm] | z0 uncut SD [µm] | z0 pull SD | theta width68 [µrad] | theta uncut SD [µrad] | theta pull SD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.5 | 4.021 | 5.214 | 0.543 | 43.08 | 52.14 | 0.681 |
| 1 | 3.556 | 5.105 | 0.492 | 39.94 | 51.75 | 0.601 |
| 1.5 | 3.295 | 5.029 | 0.474 | 37.79 | 50.78 | 0.572 |
| 2 | 3.093 | 4.898 | 0.458 | 36.05 | 49.45 | 0.554 |

At 1/10 GeV, longitudinal summary widths are close to the control.
Momentum-resolution summary changes stay at the percent scale in this
sample. This fixed-material truth-associated scan does not measure any
performance benefit from a hypothetical reduction of service material.

All six perigee/derived quantities and every signed-eta bin are available in
[summary.csv](summary.csv) and [profiles.json.gz](profiles.json.gz).
Figures: [fit fractions](figures/fit-fractions.png),
[1 GeV ratios](figures/ratio-pt1.png), [10 GeV ratios](figures/ratio-pt10.png),
[100 GeV ratios](figures/ratio-pt100.png). Absolute widths and
`common_ratio-pt*.png` controls are in the same figure directory.

## Separate Gaussian-response diagnostic

Four additional 5,000-event cases at 100 GeV use independent input
Gaussian widths equal to nominal pitch/√12 in every measured coordinate,
with merging disabled and one-coordinate long strips. Only the strixel-v
width changes within this control. The generated/transport samples are
paired across pitches. This adds 20,000 processed case-events, distinct
from the 240,000-event native geometric scan.

All-coordinate response replacement tests the overall model dependence;
it does not identify one causal mechanism or calibrate a physical sensor.
Native draws near sensor edges are bounded/retried, with at most 11
draw attempts. Retry counts are not exposed; zero lost measurements would not
prove zero retries. Exact stored variance checks and standardized local
residual diagnostics are retained in the control native reports.

| Pitch [mm] | Finite fits / generated | Native matched / generated | Wrong charge / finite fits | Simulated hits / measurements | Hits without measurement |
|---:|---:|---:|---:|---:|---:|
| 0.5 | 5,000/5,000 | 5,000/5,000 | 102/5,000 | 73,907/73,907 | 0 |
| 1 | 5,000/5,000 | 5,000/5,000 | 102/5,000 | 73,907/73,907 | 0 |
| 1.5 | 5,000/5,000 | 5,000/5,000 | 102/5,000 | 73,907/73,907 | 0 |
| 2 | 5,000/5,000 | 5,000/5,000 | 102/5,000 | 73,907/73,907 | 0 |

Central |eta|<1 absolute widths and pull checks:

| Pitch [mm] | z0 width68 [µm] | theta width68 [µrad] | z0 pull SD | theta pull SD | Relative-pT pull SD |
|---:|---:|---:|---:|---:|---:|
| 0.5 | 11.301 | 81.95 | 0.959 | 0.967 | 2.820 |
| 1 | 12.495 | 94.99 | 0.975 | 0.993 | 2.820 |
| 1.5 | 12.618 | 99.62 | 0.980 | 1.001 | 2.820 |
| 2 | 12.790 | 100.73 | 0.982 | 1.004 | 2.819 |

The central longitudinal pulls are much closer to unit width in this
control, while momentum pulls retain substantial tails/nonclosure.
This is a response-model sensitivity, not global fit calibration.

| Absolute eta region | Pitch [mm] | z0 ratio | theta ratio | Relative-pT ratio |
|---|---:|---:|---:|---:|
| 0–1 | 1 | 1.106 ± 0.019 | 1.159 ± 0.023 | 1.003 ± 0.003 |
| 1–2.5 | 1 | 1.043 ± 0.014 | 1.037 ± 0.015 | 1.004 ± 0.007 |
| 2.5–4 | 1 | 1.005 ± 0.005 | 1.002 ± 0.007 | 1.000 ± 0.001 |
| 0–1 | 1.5 | 1.117 ± 0.022 | 1.216 ± 0.028 | 1.000 ± 0.006 |
| 1–2.5 | 1.5 | 1.054 ± 0.016 | 1.078 ± 0.018 | 1.004 ± 0.009 |
| 2.5–4 | 1.5 | 1.005 ± 0.006 | 1.001 ± 0.008 | 1.000 ± 0.002 |
| 0–1 | 2 | 1.132 ± 0.024 | 1.229 ± 0.031 | 1.002 ± 0.006 |
| 1–2.5 | 2 | 1.061 ± 0.017 | 1.075 ± 0.018 | 1.003 ± 0.009 |
| 2.5–4 | 2 | 1.008 ± 0.006 | 0.998 ± 0.008 | 1.000 ± 0.002 |

Errors use the same paired-event bootstrap prescription, 400 draws.
[Gaussian ratios](gaussian-control/figures/gaussian-ratio-pt100.png),
[absolute widths](gaussian-control/figures/gaussian-absolute-pt100.png),
[full control data](gaussian-control/profiles.json.gz) and
[CSV](gaussian-control/summary.csv) retain all six quantities and eta bins.

## Conditional power estimate

The existing DES020/021 proxies are 7.8 W/module and
7.8 × 122,880/30,208 = 31.7288 W/module. The first is a complete CMS PS
service-load comparator; the second is its deliberately crude channel-density
scaling. **They are sensitivity normalizations, not physical bounds or
measurements of a compatible strixel ASIC.** Longer cells change capacitance
and do not guarantee equal power/channel.

Let f be the channel-dependent fraction of that load. The study assumes
`P(p)=P(0.5)[(1-f)+f×0.5/p]`. It keeps 2 W/module HV leakage (24.768 kW)
and 5 W/network boards (3.600 kW) fixed, and recomputes local 12 V rail I²R
loss. HV leakage is not added to LV current. External cable/converter losses
are unknown. The two baseline heat-load proxies are 125.354 and 427.772 kW.

| Pitch | Electronics saving, f=1 [kW] | Heat saving including local rail loss, f=1 [kW] | Heat saving, f=0.5 [kW] |
|---|---:|---:|---:|
| 1 mm | 48.3–196.5 | 48.6–201.3 | 24.3–101.1 |
| 1.5 mm | 64.4–262.0 | 64.7–267.7 | 32.4–134.6 |
| 2 mm | 72.4–294.7 | 72.8–300.8 | 36.5–151.3 |

If f=0, the modeled power saving is zero. These spans compare assumptions;
they are not confidence intervals. Reduced heat does not establish smaller
cooling pipes or a qualified thermal/hydraulic operating point.

## Conditional cable-space estimate

The existing 13.4 mm power + 3.6 mm fibre benchmark gives 1,584 sets across
both ends: 516.155 L gross power envelope and 37.254 L fibre envelope in
collectors/fans and downstream transport. Local buses/module flexes are
excluded from these volumes. Keeping the hardware unchanged recovers
**zero installed cable, cooling, tray or electronics-footprint space**.

A separate redesigned-harness hypothesis keeps the 13.4 mm benchmark OD
but assigns capacity equal to twelve baseline module loads, rounds within
each half-stave/petal including its 5 W board, and keeps fibres and cooling
fixed. Source cables have twelve independent LV and twelve HV circuits:
**the assumed reaggregation requires new conductors, fanouts, connectors and
HV/control topology. Aggregate power arithmetic does not qualify that cable.**

| Pitch | Power bundles, B / EC per network (f=1) | Gross power envelope removed, both ends | Effective Cu / PI / internal void removed | Worst-sector area-equivalent radial saving |
|---|---:|---:|---:|---:|
| 1 mm | 1 / 2 | 242.7 L | 48.5 / 72.8 / 121.4 L | 28.9 mm |
| 1.5 mm | 1 / 1 | 273.4 L | 54.7 / 82.0 / 136.7 L | 34.6 mm |
| 2 mm | 1 / 1 | 273.4 L | 54.7 / 82.0 / 136.7 L | 34.6 mm |

The Cu/PI/air entries use the existing effective 20%/30%/50% recipe, not
qualified electrical gauges. With f=0.5 all alternatives remove 242.7 L under
this same redesign hypothesis; with f=0 none do. The 1.5 and 2 mm f=1 cases
have equal cable-space benefit because bundle counts are discrete.

The fixed 56 pipe pairs/end and fibres give worst-sector area-equivalent
widths 75.590 mm baseline, 46.717 mm for 1/2 bundles per B/EC network,
and 41.000 mm for 1/1. These exact annular inversions use r=710 mm, 75%
azimuth and 50% packing, excluding walls/bends/connectors. They are routing
capacity screens, not proven narrower envelopes. Baseline native worst-sector
demand already exceeds the inherited 73 mm corridor packing budget.

Relative to the actual 73 mm allocation, the redesigned area-only demands
leave approximately 26.3 or 32.0 mm before wall/bend/connector reserves;
the larger equivalent savings in the table are relative to the baseline
75.590 mm demand, including its existing overcommitment.

If bundle outer diameters stay fixed, an alternative conductor-only scaling
could remove material but recovers zero external space; fixed HV/control
copper is unknown. Do not scale fibre traffic with channel count at fixed
particle flux. [Service tradeoff figure](figures/services-tradeoff.png).

## Reproduction, provenance and review

Commands and dependency/build arguments are in the
[repeatable workflow](../../../software/analysis/strixel_pitch_study/README.md).
Offline replay uses compact all-event NPZ arrays, native reports and exact
configuration/content hashes. Raw ROOT and full covariance remain in ignored
native output directories. Every stored residual/pull/flag was recomputed
from full truth/fitted/covariance arrays before compact retention.

Production ran the corrected source at
`8b7c147b3b0da4bd40dcd9ad06c98abcb2de58f9`. Native report preparation omitted
the imported metrics.py fingerprint; a separate launch/completion blob/hash
check and exact observable replay close this stated provenance gap. Initial
v1/v2 pilots had incorrect residual-sign metadata; v3 production and all
retained observables use fitted−truth consistently.

Scientific assumptions and service arithmetic received separate PhysVal and
SysArch assessments. Exact reviewed revisions, subsequent corrections,
executed checks and final evidence assessment are recorded in the
[session journal](../../../logs/codex/SESSION-2026-10-31-strixel-pitch-study.md).
No design sign-off or preferred pitch is inferred from these calculations.
