# DES042 PROTOTYPE - ttbar plus exactly 200 pileup interactions

Fatras qqbar-only ttbar; 100 paired generated events per length; fixed geometry/material, constant 3 T and common GBTS/CKF/ambiguity settings.

Efficiencies count unique charged generated particles with pT >=1 GeV, |eta| <=3, rho <=24 mm and |z| <=1 m, before hit requirements. Candidate fakes exclude matched out-of-scope generated particles and simulated secondaries. Duplicates overlap matched categories.

Guide selection is applied after frozen ambiguity resolution: reconstructed pT >=1 GeV, |eta| <=3, |loc0| <=4 mm, <=2 holes and <=2 outliers, in addition to frozen quality. It does not reproduce a different native reconstruction chain.

| Pitch [mm] | Selection | Stage | Inclusive efficiency | Hard scatter | Pileup | Fake candidates | Duplicate candidates | Fake events |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 0.5 | frozen | ckf | 77.37% [76.79, 78.03] (69123/89342) | 81.18% [79.66, 82.62] (3894/4797) | 77.15% [76.58, 77.79] (65229/84545) | 8.66% [8.26, 9.11] (12443/143680) | 24.12% [23.73, 24.54] (34659/143680) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 0.5 | frozen | ambi | 77.36% [76.77, 78.02] (69111/89342) | 81.11% [79.62, 82.58] (3891/4797) | 77.14% [76.57, 77.78] (65220/84545) | 3.46% [3.32, 3.61] (3459/99968) | 0.04% [0.03, 0.05] (36/99968) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 0.5 | guide | ckf | 76.20% [75.62, 76.85] (68081/89342) | 80.51% [78.93, 82.03] (3862/4797) | 75.96% [75.40, 76.59] (64219/84545) | 1.50% [1.05, 2.11] (1310/87075) | 18.88% [18.39, 19.44] (16443/87075) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 0.5 | guide | ambi | 76.05% [75.48, 76.69] (67947/89342) | 80.36% [78.77, 81.87] (3855/4797) | 75.81% [75.26, 76.44] (64092/84545) | 0.20% [0.16, 0.23] (135/69076) | 0.00% [0.00, 0.01] (2/69076) | 72.00% [63.00, 80.00] (72/100) |
| 1 | frozen | ckf | 77.40% [76.81, 78.05] (69149/89342) | 81.13% [79.62, 82.59] (3892/4797) | 77.19% [76.62, 77.82] (65257/84545) | 9.03% [8.61, 9.50] (13147/145600) | 24.59% [24.20, 25.01] (35805/145600) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 1 | frozen | ambi | 77.38% [76.79, 78.04] (69134/89342) | 81.09% [79.60, 82.53] (3890/4797) | 77.17% [76.60, 77.81] (65244/84545) | 3.65% [3.49, 3.79] (3655/100237) | 0.04% [0.03, 0.05] (37/100237) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 1 | guide | ckf | 76.26% [75.69, 76.89] (68134/89342) | 80.57% [79.06, 82.02] (3865/4797) | 76.02% [75.46, 76.63] (64269/84545) | 1.56% [1.06, 2.25] (1372/87809) | 19.41% [18.90, 19.96] (17040/87809) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 1 | guide | ambi | 76.10% [75.53, 76.73] (67991/89342) | 80.40% [78.88, 81.85] (3857/4797) | 75.86% [75.30, 76.47] (64134/84545) | 0.18% [0.15, 0.21] (125/69106) | 0.01% [0.00, 0.01] (4/69106) | 70.00% [61.00, 79.00] (70/100) |
| 1.5 | frozen | ckf | 77.40% [76.82, 78.06] (69154/89342) | 81.18% [79.66, 82.63] (3894/4797) | 77.19% [76.62, 77.83] (65260/84545) | 9.39% [8.96, 9.91] (13879/147835) | 25.21% [24.81, 25.63] (37264/147835) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 1.5 | frozen | ambi | 77.39% [76.81, 78.04] (69142/89342) | 81.13% [79.61, 82.61] (3892/4797) | 77.18% [76.61, 77.82] (65250/84545) | 3.94% [3.79, 4.10] (3967/100591) | 0.04% [0.03, 0.05] (38/100591) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 1.5 | guide | ckf | 76.31% [75.74, 76.95] (68180/89342) | 80.55% [78.99, 82.04] (3864/4797) | 76.07% [75.51, 76.70] (64316/84545) | 1.65% [1.12, 2.45] (1463/88756) | 20.08% [19.57, 20.63] (17821/88756) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 1.5 | guide | ambi | 76.14% [75.56, 76.78] (68024/89342) | 80.40% [78.87, 81.87] (3857/4797) | 75.90% [75.34, 76.53] (64167/84545) | 0.20% [0.17, 0.23] (141/69166) | 0.00% [0.00, 0.01] (3/69166) | 72.00% [63.00, 80.00] (72/100) |
| 2 | frozen | ckf | 77.43% [76.84, 78.08] (69177/89342) | 81.18% [79.66, 82.65] (3894/4797) | 77.22% [76.65, 77.86] (65283/84545) | 9.94% [9.49, 10.46] (14936/150284) | 25.69% [25.32, 26.10] (38612/150284) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 2 | frozen | ambi | 77.41% [76.82, 78.06] (69156/89342) | 81.11% [79.60, 82.60] (3891/4797) | 77.20% [76.62, 77.84] (65265/84545) | 4.24% [4.06, 4.40] (4275/100929) | 0.04% [0.03, 0.06] (44/100929) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 2 | guide | ckf | 76.34% [75.76, 76.98] (68203/89342) | 80.47% [78.91, 81.94] (3860/4797) | 76.11% [75.54, 76.74] (64343/84545) | 1.78% [1.24, 2.57] (1590/89564) | 20.59% [20.08, 21.13] (18441/89564) | 100.00% [100.00, 100.00] (100/100) (degenerate bootstrap) |
| 2 | guide | ambi | 76.15% [75.57, 76.79] (68030/89342) | 80.36% [78.81, 81.84] (3855/4797) | 75.91% [75.35, 76.54] (64175/84545) | 0.23% [0.19, 0.27] (159/69201) | 0.01% [0.00, 0.02] (7/69201) | 71.00% [62.00, 79.00] (71/100) |

Pure measured-pixel seed coverage counts unique eligible generated particles with at least one seed whose links all associate with that particle and span at least three physical pixel groups. This control diagnoses an upstream stage; it does not prove the cause of downstream failures.

| Pitch [mm] | Seed stage | Inclusive coverage | Hard scatter | Pileup |
|---:|---|---:|---:|---:|
| 0.5 | seeds | 76.86% [76.26, 77.54] (68669/89342) | 81.22% [79.76, 82.61] (3896/4797) | 76.61% [76.01, 77.28] (64773/84545) |
| 0.5 | estimated_seeds | 76.85% [76.25, 77.53] (68663/89342) | 81.22% [79.76, 82.61] (3896/4797) | 76.61% [76.01, 77.27] (64767/84545) |
| 1 | seeds | 76.86% [76.26, 77.54] (68669/89342) | 81.22% [79.76, 82.61] (3896/4797) | 76.61% [76.01, 77.28] (64773/84545) |
| 1 | estimated_seeds | 76.85% [76.25, 77.53] (68663/89342) | 81.22% [79.76, 82.61] (3896/4797) | 76.61% [76.01, 77.27] (64767/84545) |
| 1.5 | seeds | 76.86% [76.26, 77.54] (68669/89342) | 81.22% [79.76, 82.61] (3896/4797) | 76.61% [76.01, 77.28] (64773/84545) |
| 1.5 | estimated_seeds | 76.85% [76.25, 77.53] (68663/89342) | 81.22% [79.76, 82.61] (3896/4797) | 76.61% [76.01, 77.27] (64767/84545) |
| 2 | seeds | 76.86% [76.26, 77.54] (68669/89342) | 81.22% [79.76, 82.61] (3896/4797) | 76.61% [76.01, 77.28] (64773/84545) |
| 2 | estimated_seeds | 76.85% [76.25, 77.53] (68663/89342) | 81.22% [79.76, 82.61] (3896/4797) | 76.61% [76.01, 77.27] (64767/84545) |

Intervals resample whole generated events jointly across all four pitches (2,000 deterministic event-block resamples in the production protocol). They are pointwise statistical intervals. Particles/tracks in one event are correlated. Zero fake-event bounds describe event incidence and do not bound candidate fake fractions. Degenerate paired bootstrap differences do not demonstrate equivalence.

The response scales only system 4/5 local-v Gaussian sigma relative to 0.5 mm. This is an uncalibrated coarse-response sensitivity with fixed material; Gaussian boundary retries can alter other realized smearing draws. Truth-binned efficiency and reco-binned fake/duplicate profiles, conditional denominators, exhaustive counts and paired differences are retained in profiles.json.gz.

Source particle/hit identity passed for all four configurations. Changed control-event counts:

| Pitch [mm] | Pixel inputs | Space points | Seeds | Estimated seeds | Non-target response |
|---:|---:|---:|---:|---:|---:|
| 0.5 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 | 0 | 100 |
| 1.5 | 0 | 0 | 0 | 0 | 100 |
| 2 | 0 | 0 | 0 | 0 | 100 |

The unchanged GBTS graph limit can truncate the graph. These are resource-limited chain results, not unconstrained detector/seeder performance.

| Pitch [mm] | Edge limit | Events reaching limit | Edges/event range | Edge links/event range |
|---:|---:|---:|---:|---:|
| 0.5 | 2000000 | 99/100 | 1921530–2000000 | 31205–49540 |
| 1 | 2000000 | 99/100 | 1921530–2000000 | 31205–49540 |
| 1.5 | 2000000 | 99/100 | 1921530–2000000 | 31205–49540 |
| 2 | 2000000 | 99/100 | 1921530–2000000 | 31205–49540 |
