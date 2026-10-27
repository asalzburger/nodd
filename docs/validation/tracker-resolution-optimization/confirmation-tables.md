# Confirmation tables

All entries are observed native Fatras results, conditional on a valid fit for residuals. Coverage uses every generated muon. Each case has10,000 events. Width means the central68.27% half-width. Ratios below one improve. Brackets are pointwise95% paired event-bootstrap intervals (400 replicates), without multiplicity or systematic corrections. No noninferiority margin was registered.

## Primary geometric, seed52042

Data: [confirmation-geometric](confirmation-geometric.json.gz). Native launch identities and hashes: [reports](native-confirmation-geometric-reports.json.gz). Analysis source: `9873280239728ebaceb1f72387b70484a2382f5e`.

| Candidate | pT [GeV] | d0 ratio [95%] | z0 ratio [95%] | relative pT ratio [95%] | signed q/pT ratio [95%] |
| --- | ---: | --- | --- | --- | --- |
| mild-donor2 | 1 | 0.9665 [0.9470, 0.9904] | 0.9626 [0.9354, 0.9848] | 1.0147 [0.9827, 1.0440] | 1.0046 [0.9711, 1.0361] |
| mild-donor2 | 10 | 0.9489 [0.9281, 0.9771] | 0.9353 [0.9079, 0.9617] | 1.0094 [0.9800, 1.0410] | 1.0082 [0.9744, 1.0354] |
| mild-donor2 | 100 | 0.9762 [0.9501, 1.0014] | 0.9546 [0.9273, 0.9932] | 0.9558 [0.9060, 0.9959] | 0.9599 [0.9125, 1.0057] |
| balanced | 1 | 0.9537 [0.9302, 0.9753] | 0.9651 [0.9363, 0.9915] | 1.0561 [1.0246, 1.0893] | 1.0491 [1.0132, 1.0748] |
| balanced | 10 | 0.9315 [0.9112, 0.9567] | 0.9548 [0.9209, 0.9840] | 1.0249 [0.9898, 1.0578] | 1.0218 [0.9856, 1.0540] |
| balanced | 100 | 0.9471 [0.9197, 0.9733] | 0.9062 [0.8737, 0.9438] | 0.9879 [0.9338, 1.0327] | 1.0026 [0.9538, 1.0456] |

| Case | ≥10 hits [%] | Valid fits / generated | Wrong charge | d0 width [µm] | z0 width [µm] | relative pT width [%] | Full relative pT SD [%] | Full signed q/pT SD [%] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-pt1 | 88.09 | 9995 / 10000 | 0 | 101.291 | 402.935 | 1.869 | 3.654 | 4.950 |
| baseline-pt10 | 87.73 | 10000 / 10000 | 0 | 22.250 | 84.666 | 2.456 | 5.978 | 5.857 |
| baseline-pt100 | 87.74 | 9999 / 10000 | 200 | 10.589 | 22.755 | 6.323 | 1176.932 | 42.270 |
| mild-donor2-pt1 | 96.53 | 9996 / 10000 | 0 | 97.899 | 387.855 | 1.896 | 3.751 | 5.419 |
| mild-donor2-pt10 | 96.65 | 10000 / 10000 | 0 | 21.113 | 79.184 | 2.479 | 5.518 | 5.492 |
| mild-donor2-pt100 | 96.83 | 10000 / 10000 | 176 | 10.337 | 21.722 | 6.044 | 2652.095 | 39.565 |
| balanced-pt1 | 98.20 | 9996 / 10000 | 0 | 96.598 | 388.864 | 1.974 | 3.830 | 4.522 |
| balanced-pt10 | 98.28 | 10000 / 10000 | 0 | 20.725 | 80.835 | 2.517 | 5.863 | 5.602 |
| balanced-pt100 | 98.18 | 10000 / 10000 | 202 | 10.029 | 20.620 | 6.247 | 665.920 | 37.339 |

All native fit attempts produced tracks, and every fit has a finite positive6D covariance. The few missing fits are seven-hit selection losses, retained in coverage denominators. Charge mistakes and every finite residual tail remain included.

Half-unit absolute-eta regions with pointwise intervals entirely above one are listed exhaustively for the four objectives/diagnostics. These are diagnostics rather than familywise hypothesis tests.

| Candidate | pT [GeV] | absolute eta range | Quantity | Ratio [95%] |
| --- | ---: | --- | --- | --- |
| balanced | 1 | 3–3.5 | pt_relative | 1.1252 [1.0598, 1.1962] |
| balanced | 1 | 3–3.5 | q_over_pt_relative | 1.1441 [1.0729, 1.2057] |
| balanced | 1 | 3.5–4 | d0 | 1.1100 [1.0483, 1.1938] |

## Gaussian cross-check, seed52042

Data: [confirmation-gaussian](confirmation-gaussian.json.gz). Native launch identities and hashes: [reports](native-confirmation-gaussian-reports.json.gz). Analysis source: `9873280239728ebaceb1f72387b70484a2382f5e`.

| Candidate | pT [GeV] | d0 ratio [95%] | z0 ratio [95%] | relative pT ratio [95%] | signed q/pT ratio [95%] |
| --- | ---: | --- | --- | --- | --- |
| mild-donor2 | 1 | 0.9767 [0.9633, 0.9956] | 0.9645 [0.9420, 0.9914] | 1.0398 [1.0049, 1.0658] | 1.0272 [1.0004, 1.0536] |
| mild-donor2 | 10 | 0.9450 [0.9284, 0.9591] | 0.9767 [0.9478, 1.0063] | 0.9846 [0.9565, 1.0239] | 0.9886 [0.9556, 1.0263] |
| mild-donor2 | 100 | 0.9552 [0.9375, 0.9744] | 0.9727 [0.9467, 0.9911] | 0.9925 [0.9500, 1.0438] | 1.0005 [0.9574, 1.0472] |
| balanced | 1 | 0.9688 [0.9520, 0.9862] | 0.9813 [0.9577, 1.0069] | 1.0900 [1.0524, 1.1174] | 1.0516 [1.0264, 1.0780] |
| balanced | 10 | 0.9567 [0.9393, 0.9768] | 0.9686 [0.9405, 1.0000] | 1.0271 [1.0008, 1.0683] | 1.0404 [1.0079, 1.0782] |
| balanced | 100 | 0.9486 [0.9320, 0.9701] | 0.9418 [0.9169, 0.9636] | 0.9888 [0.9495, 1.0363] | 0.9990 [0.9489, 1.0404] |

| Case | ≥10 hits [%] | Valid fits / generated | Wrong charge | d0 width [µm] | z0 width [µm] | relative pT width [%] | Full relative pT SD [%] | Full signed q/pT SD [%] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-pt1 | 88.09 | 9995 / 10000 | 0 | 101.475 | 405.193 | 1.802 | 3.607 | 4.927 |
| baseline-pt10 | 87.73 | 10000 / 10000 | 0 | 21.673 | 96.477 | 2.449 | 5.912 | 5.675 |
| baseline-pt100 | 87.74 | 9999 / 10000 | 223 | 10.664 | 33.189 | 6.208 | 3813.450 | 41.050 |
| mild-donor2-pt1 | 96.53 | 9996 / 10000 | 0 | 99.109 | 390.813 | 1.874 | 3.732 | 5.398 |
| mild-donor2-pt10 | 96.65 | 10000 / 10000 | 0 | 20.481 | 94.227 | 2.411 | 5.662 | 5.535 |
| mild-donor2-pt100 | 96.83 | 10000 / 10000 | 200 | 10.186 | 32.282 | 6.161 | 788.423 | 37.941 |
| balanced-pt1 | 98.20 | 9996 / 10000 | 0 | 98.305 | 397.630 | 1.964 | 3.828 | 4.510 |
| balanced-pt10 | 98.28 | 10000 / 10000 | 0 | 20.736 | 93.452 | 2.515 | 5.672 | 5.671 |
| balanced-pt100 | 98.18 | 10000 / 10000 | 210 | 10.116 | 31.256 | 6.138 | 779.854 | 37.552 |

All native fit attempts produced tracks, and every fit has a finite positive6D covariance. The few missing fits are seven-hit selection losses, retained in coverage denominators. Charge mistakes and every finite residual tail remain included.

Half-unit absolute-eta regions with pointwise intervals entirely above one are listed exhaustively for the four objectives/diagnostics. These are diagnostics rather than familywise hypothesis tests.

| Candidate | pT [GeV] | absolute eta range | Quantity | Ratio [95%] |
| --- | ---: | --- | --- | --- |
| mild-donor2 | 1 | 3.5–4 | d0 | 1.0739 [1.0279, 1.1319] |
| balanced | 1 | 2–2.5 | pt_relative | 1.0666 [1.0040, 1.1161] |
| balanced | 1 | 3–3.5 | pt_relative | 1.0980 [1.0449, 1.1762] |
| balanced | 1 | 3–3.5 | q_over_pt_relative | 1.1018 [1.0544, 1.1867] |
| balanced | 1 | 3.5–4 | d0 | 1.1109 [1.0381, 1.1725] |
| balanced | 1 | 3.5–4 | q_over_pt_relative | 1.0644 [1.0044, 1.1558] |
| balanced | 10 | 3–3.5 | pt_relative | 1.0852 [1.0213, 1.1714] |
| balanced | 10 | 3–3.5 | q_over_pt_relative | 1.1109 [1.0211, 1.1931] |

## Separate late-disk geometric control, seed62042

Data: [late-confirmation-geometric](late-confirmation-geometric.json.gz). Native launch identities and hashes: [reports](native-late-confirmation-geometric-reports.json.gz). Analysis source: `9873280239728ebaceb1f72387b70484a2382f5e`.

| Candidate | pT [GeV] | d0 ratio [95%] | z0 ratio [95%] | relative pT ratio [95%] | signed q/pT ratio [95%] |
| --- | ---: | --- | --- | --- | --- |
| late-disk | 1 | 0.9422 [0.9189, 0.9619] | 0.9544 [0.9206, 0.9845] | 1.0100 [0.9829, 1.0377] | 1.0000 [0.9789, 1.0289] |
| late-disk | 10 | 0.9674 [0.9388, 0.9946] | 0.9624 [0.9333, 0.9992] | 1.0026 [0.9630, 1.0381] | 0.9905 [0.9569, 1.0249] |
| late-disk | 100 | 0.9420 [0.9161, 0.9732] | 0.9479 [0.9120, 0.9824] | 0.9567 [0.9084, 1.0023] | 0.9462 [0.9054, 0.9980] |

| Case | ≥10 hits [%] | Valid fits / generated | Wrong charge | d0 width [µm] | z0 width [µm] | relative pT width [%] | Full relative pT SD [%] | Full signed q/pT SD [%] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-pt1 | 87.59 | 9999 / 10000 | 0 | 99.809 | 398.870 | 1.850 | 3.739 | 5.000 |
| baseline-pt10 | 87.04 | 10000 / 10000 | 0 | 21.982 | 86.455 | 2.475 | 5.968 | 5.640 |
| baseline-pt100 | 87.21 | 10000 / 10000 | 215 | 10.768 | 23.266 | 6.590 | 949.338 | 42.723 |
| late-disk-pt1 | 94.77 | 9999 / 10000 | 0 | 94.040 | 380.662 | 1.868 | 3.849 | 5.070 |
| late-disk-pt10 | 94.28 | 10000 / 10000 | 0 | 21.266 | 83.204 | 2.481 | 6.008 | 5.546 |
| late-disk-pt100 | 94.18 | 10000 / 10000 | 209 | 10.143 | 22.053 | 6.305 | 7697.737 | 38.333 |

All native fit attempts produced tracks, and every fit has a finite positive6D covariance. The few missing fits are seven-hit selection losses, retained in coverage denominators. Charge mistakes and every finite residual tail remain included.

Half-unit absolute-eta regions with pointwise intervals entirely above one are listed exhaustively for the four objectives/diagnostics. These are diagnostics rather than familywise hypothesis tests.

| Candidate | pT [GeV] | absolute eta range | Quantity | Ratio [95%] |
| --- | ---: | --- | --- | --- |
| late-disk | 1 | 3–3.5 | q_over_pt_relative | 1.0599 [1.0096, 1.1254] |
| late-disk | 1 | 3.5–4 | d0 | 1.0599 [1.0033, 1.1205] |

## Separate late-disk Gaussian cross-check, seed62042

Data: [late-confirmation-gaussian](late-confirmation-gaussian.json.gz). Native launch identities and hashes: [reports](native-late-confirmation-gaussian-reports.json.gz). Analysis source: `9873280239728ebaceb1f72387b70484a2382f5e`.

| Candidate | pT [GeV] | d0 ratio [95%] | z0 ratio [95%] | relative pT ratio [95%] | signed q/pT ratio [95%] |
| --- | ---: | --- | --- | --- | --- |
| late-disk | 1 | 0.9516 [0.9365, 0.9691] | 0.9644 [0.9329, 0.9935] | 1.0035 [0.9757, 1.0276] | 1.0080 [0.9829, 1.0314] |
| late-disk | 10 | 0.9603 [0.9416, 0.9755] | 0.9723 [0.9452, 1.0002] | 1.0293 [0.9989, 1.0657] | 1.0344 [1.0049, 1.0685] |
| late-disk | 100 | 0.9403 [0.9214, 0.9585] | 0.9380 [0.9004, 0.9594] | 0.9560 [0.9046, 1.0016] | 0.9472 [0.9080, 1.0033] |

| Case | ≥10 hits [%] | Valid fits / generated | Wrong charge | d0 width [µm] | z0 width [µm] | relative pT width [%] | Full relative pT SD [%] | Full signed q/pT SD [%] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-pt1 | 87.59 | 9999 / 10000 | 0 | 101.009 | 402.881 | 1.828 | 3.739 | 4.998 |
| baseline-pt10 | 87.04 | 10000 / 10000 | 0 | 21.690 | 98.390 | 2.409 | 6.332 | 5.759 |
| baseline-pt100 | 87.21 | 10000 / 10000 | 210 | 10.613 | 33.991 | 6.470 | 727.669 | 44.146 |
| late-disk-pt1 | 94.77 | 9999 / 10000 | 0 | 96.119 | 388.544 | 1.834 | 3.846 | 5.065 |
| late-disk-pt10 | 94.28 | 10000 / 10000 | 0 | 20.830 | 95.664 | 2.479 | 6.249 | 5.642 |
| late-disk-pt100 | 94.18 | 10000 / 10000 | 178 | 9.979 | 31.883 | 6.186 | 1759.335 | 39.040 |

All native fit attempts produced tracks, and every fit has a finite positive6D covariance. The few missing fits are seven-hit selection losses, retained in coverage denominators. Charge mistakes and every finite residual tail remain included.

Half-unit absolute-eta regions with pointwise intervals entirely above one are listed exhaustively for the four objectives/diagnostics. These are diagnostics rather than familywise hypothesis tests.

| Candidate | pT [GeV] | absolute eta range | Quantity | Ratio [95%] |
| --- | ---: | --- | --- | --- |
| late-disk | 1 | 2.5–3 | z0 | 1.0601 [1.0071, 1.1215] |
| late-disk | 1 | 3–3.5 | pt_relative | 1.0645 [1.0068, 1.1349] |
| late-disk | 1 | 3–3.5 | q_over_pt_relative | 1.0716 [1.0168, 1.1260] |
| late-disk | 1 | 3.5–4 | z0 | 1.0834 [1.0168, 1.1601] |
