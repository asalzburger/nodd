# DES-011 generated placement results

PROTOTYPE. Best tested candidates; no global optimum or engineering approval.

Selection was frozen on training rays before dense validation. The dense grids
share some training angles; the separately reported random cohort is independent.

Source revision: `ac61f766b34f9bb60748e8fc4258a41037ca1e33`; tracked source dirty: False.

| Role | Candidate |
| --- | --- |
| coverage | p190-s680-b1-l1287.33-front_loaded-barrel-10 |
| spacing | p190-s720-b1-l1287.33-uniform |
| area | p170-s680-b1-l1287.33-front_loaded |
| Original-pocket control | p190-s680-b1-l1287.33-front_loaded-original-pockets |

All areas sum sensor/patch surfaces; overlaps are counted. Gaps are 3D path
distances between distinct usable stations, with complete same-module stereo pairs.

| Candidate | Physical silicon, m² | Summed active silicon, m² | Mean stations | Worst-mode p95 maximum inter-station gap, mm | Fixed-reference missed stations |
| --- | ---: | ---: | ---: | ---: | ---: |
| pr25 | 177.303 | 172.971 | 8.2284 | 1378.66 | 17.539% |
| p170-s680-b1-l1287.33-front_loaded | 199.964 | 195.090 | 8.8637 | 1099.18 | 12.240% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | 196.473 | 191.680 | 9.0758 | 1008.17 | 11.047% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | 197.250 | 192.435 | 9.0182 | 1009.57 | 10.938% |
| p190-s720-b1-l1287.33-uniform | 187.365 | 182.703 | 8.8281 | 936.09 | 12.680% |

## Per-mode and subsystem dense validation

Fixed-reference missing fractions refer to the original cobe ideal layers,
including when a candidate moved or refilled them. Candidate-local missing
fractions remain separately available under `coverage` in each summary JSON.

| Candidate | Mode | Subsystem | Mean sensor hits | Mean usable stations | Fixed-reference missing | p95 maximum inter-station gap, mm | p95 boundary gap, mm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| pr25 | straight | total | 12.436 | 8.232 | 17.566% | 1378.659 | 1407.670 |
| pr25 | straight | long_strip | 2.357 | 0.910 | 24.993% | 424.636 | 3326.112 |
| pr25 | straight | pixel | 6.337 | 4.453 | 14.901% | 366.775 | 2854.963 |
| pr25 | straight | short_strip | 3.742 | 2.868 | 18.967% | 514.398 | 3302.215 |
| pr25 | positive | total | 12.319 | 8.247 | 17.326% | 1378.659 | 1406.466 |
| pr25 | positive | long_strip | 2.318 | 0.876 | 26.599% | 424.636 | 3331.837 |
| pr25 | positive | pixel | 6.352 | 4.477 | 14.515% | 389.805 | 2859.329 |
| pr25 | positive | short_strip | 3.650 | 2.893 | 18.348% | 514.398 | 3302.215 |
| pr25 | negative | total | 12.074 | 8.207 | 17.724% | 1378.659 | 1406.466 |
| pr25 | negative | long_strip | 2.111 | 0.844 | 29.293% | 424.636 | 3331.582 |
| pr25 | negative | pixel | 6.316 | 4.468 | 14.696% | 377.988 | 2865.575 |
| pr25 | negative | short_strip | 3.648 | 2.895 | 18.298% | 514.368 | 3302.215 |
| p170-s680-b1-l1287.33-front_loaded | straight | total | 13.788 | 8.854 | 12.225% | 1099.178 | 1102.817 |
| p170-s680-b1-l1287.33-front_loaded | straight | long_strip | 2.605 | 0.980 | 24.938% | 460.778 | 3323.065 |
| p170-s680-b1-l1287.33-front_loaded | straight | pixel | 6.484 | 4.562 | 12.814% | 382.814 | 2850.385 |
| p170-s680-b1-l1287.33-front_loaded | straight | short_strip | 4.699 | 3.312 | 7.071% | 450.627 | 3258.743 |
| p170-s680-b1-l1287.33-front_loaded | positive | total | 13.775 | 8.888 | 12.055% | 1011.249 | 1101.011 |
| p170-s680-b1-l1287.33-front_loaded | positive | long_strip | 2.732 | 0.979 | 25.955% | 459.752 | 3324.496 |
| p170-s680-b1-l1287.33-front_loaded | positive | pixel | 6.495 | 4.588 | 12.402% | 384.043 | 2856.952 |
| p170-s680-b1-l1287.33-front_loaded | positive | short_strip | 4.548 | 3.320 | 6.903% | 451.555 | 3259.090 |
| p170-s680-b1-l1287.33-front_loaded | negative | total | 13.578 | 8.850 | 12.439% | 1011.598 | 1101.011 |
| p170-s680-b1-l1287.33-front_loaded | negative | long_strip | 2.542 | 0.948 | 28.656% | 460.778 | 3324.496 |
| p170-s680-b1-l1287.33-front_loaded | negative | pixel | 6.455 | 4.579 | 12.559% | 382.842 | 2859.253 |
| p170-s680-b1-l1287.33-front_loaded | negative | short_strip | 4.581 | 3.322 | 6.845% | 450.688 | 3258.743 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | total | 13.692 | 9.037 | 11.323% | 1008.168 | 1104.623 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | long_strip | 2.584 | 0.979 | 24.972% | 460.778 | 3320.286 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | pixel | 7.061 | 4.857 | 8.708% | 384.331 | 2726.901 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | short_strip | 4.047 | 3.201 | 10.551% | 452.616 | 3265.457 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | total | 14.056 | 9.108 | 10.772% | 1006.640 | 1043.007 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | long_strip | 2.794 | 1.003 | 23.909% | 459.782 | 3324.496 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | 7.152 | 4.889 | 8.174% | 384.359 | 2797.756 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | short_strip | 4.110 | 3.216 | 10.192% | 451.921 | 3265.011 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | total | 13.782 | 9.083 | 11.045% | 1006.095 | 1043.007 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | long_strip | 2.599 | 0.978 | 26.112% | 460.778 | 3324.496 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | pixel | 7.113 | 4.890 | 8.158% | 385.217 | 2815.602 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | short_strip | 4.071 | 3.215 | 10.243% | 451.849 | 3265.011 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | total | 13.745 | 9.015 | 11.000% | 1009.574 | 1101.948 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | long_strip | 2.663 | 0.982 | 23.076% | 442.926 | 3319.683 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | pixel | 7.010 | 4.844 | 8.537% | 384.167 | 2726.213 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | short_strip | 4.072 | 3.189 | 10.537% | 447.668 | 3265.457 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | total | 13.917 | 9.046 | 10.642% | 1007.738 | 1048.774 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | long_strip | 2.687 | 0.974 | 22.907% | 441.659 | 3324.496 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | pixel | 7.167 | 4.874 | 8.059% | 384.483 | 2795.934 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | short_strip | 4.063 | 3.198 | 10.331% | 447.552 | 3265.011 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | total | 13.510 | 8.993 | 11.171% | 1006.720 | 1048.774 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | long_strip | 2.488 | 0.943 | 25.650% | 441.659 | 3324.496 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | pixel | 7.003 | 4.850 | 8.483% | 385.495 | 2802.653 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | short_strip | 4.019 | 3.200 | 10.274% | 447.668 | 3265.011 |
| p190-s720-b1-l1287.33-uniform | straight | total | 13.368 | 8.830 | 12.636% | 936.093 | 1068.292 |
| p190-s720-b1-l1287.33-uniform | straight | long_strip | 2.306 | 0.909 | 27.833% | 410.251 | 3324.496 |
| p190-s720-b1-l1287.33-uniform | straight | pixel | 6.624 | 4.654 | 11.639% | 348.813 | 2725.474 |
| p190-s720-b1-l1287.33-uniform | straight | short_strip | 4.438 | 3.267 | 8.969% | 394.827 | 3265.457 |
| p190-s720-b1-l1287.33-uniform | positive | total | 13.530 | 8.854 | 12.437% | 889.088 | 1064.176 |
| p190-s720-b1-l1287.33-uniform | positive | long_strip | 2.340 | 0.897 | 28.568% | 419.442 | 3325.661 |
| p190-s720-b1-l1287.33-uniform | positive | pixel | 6.795 | 4.682 | 11.162% | 359.695 | 2793.604 |
| p190-s720-b1-l1287.33-uniform | positive | short_strip | 4.395 | 3.275 | 8.917% | 394.827 | 3265.011 |
| p190-s720-b1-l1287.33-uniform | negative | total | 13.170 | 8.800 | 12.967% | 934.889 | 1064.176 |
| p190-s720-b1-l1287.33-uniform | negative | long_strip | 2.178 | 0.864 | 31.353% | 422.111 | 3325.558 |
| p190-s720-b1-l1287.33-uniform | negative | pixel | 6.635 | 4.661 | 11.536% | 368.325 | 2802.676 |
| p190-s720-b1-l1287.33-uniform | negative | short_strip | 4.357 | 3.275 | 8.923% | 394.827 | 3265.011 |

## Dense coverage validation outcome

Training selections are not reranked using validation. A failed dense guard
withholds that candidate from a recommendation, even if native propagation agrees.

| Candidate | All dense coverage guards pass |
| --- | --- |
| p170-s680-b1-l1287.33-front_loaded | True |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | True |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | True |
| p190-s720-b1-l1287.33-uniform | False |

## Local coverage guards

Central eta=0 / vertex z=0 must preserve each subsystem's mean and zero-hit fraction.
Other eta-band / vertex-plane strata must not become entirely blind. Smaller local
regressions are retained explicitly; passing is not pointwise or continuum hermeticity.

| Candidate | Mode | Central guard | No new blind stratum | Strata/subsystem regressions |
| --- | --- | --- | --- | ---: |
| p170-s680-b1-l1287.33-front_loaded | straight | True | True | 24 |
| p170-s680-b1-l1287.33-front_loaded | positive | True | True | 21 |
| p170-s680-b1-l1287.33-front_loaded | negative | True | True | 21 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | True | True | 54 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | True | True | 35 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | True | True | 39 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | True | True | 10 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | True | True | 4 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | True | True | 6 |
| p190-s720-b1-l1287.33-uniform | straight | True | True | 19 |
| p190-s720-b1-l1287.33-uniform | positive | True | True | 11 |
| p190-s720-b1-l1287.33-uniform | negative | True | True | 13 |

Detailed local changes and paired track hashes are retained in `study.json` and case summaries.


## Independent random cohort

| Candidate | Mean stations | Fixed-reference missed stations | Worst-mode p95 maximum inter-station gap, mm |
| --- | ---: | ---: | ---: |
| pr25 | 8.2000 | 18.704% | 1378.78 |
| p170-s680-b1-l1287.33-front_loaded | 8.8897 | 12.990% | 1008.88 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | 9.0431 | 12.259% | 1005.08 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | 9.0106 | 11.948% | 1006.02 |
| p190-s720-b1-l1287.33-uniform | 8.8711 | 13.176% | 886.93 |

## Search and constraints

Evaluated 11 bounded candidates; 11 passed geometry/capacity constraints.
Every parameter set and rejection reason is retained in `study.json`.
Adverse service-budget failures remain in each case summary. Compact pockets,
connector bends, materials, cooling hydraulics and vessel access remain unqualified.
