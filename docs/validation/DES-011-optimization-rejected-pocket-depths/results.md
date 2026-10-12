# DES-011 generated placement results

PROTOTYPE. Best tested candidates; no global optimum or engineering approval.

Selection was frozen on training rays before dense validation. The dense grids
share some training angles; the separately reported random cohort is independent.

Source revision: `10203d9a3f41d82cb467a7deb75e8293b0f1cc95`; tracked source dirty: False.

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
| pr25 | 177.303 | 172.971 | 8.2146 | 1379.26 | 17.638% |
| p170-s680-b1-l1287.33-front_loaded | 199.964 | 195.090 | 8.8503 | 1099.81 | 12.348% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | 196.473 | 191.680 | 9.0677 | 1008.30 | 11.103% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | 197.250 | 192.435 | 9.0090 | 1009.94 | 11.002% |
| p190-s720-b1-l1287.33-uniform | 187.365 | 182.703 | 8.8224 | 936.09 | 12.712% |

## Per-mode and subsystem dense validation

Fixed-reference missing fractions refer to the original cobe ideal layers,
including when a candidate moved or refilled them. Candidate-local missing
fractions remain separately available under `coverage` in each summary JSON.

| Candidate | Mode | Subsystem | Mean sensor hits | Mean usable stations | Fixed-reference missing | p95 maximum inter-station gap, mm | p95 boundary gap, mm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| pr25 | straight | total | 12.415 | 8.217 | 17.645% | 1379.263 | 1407.670 |
| pr25 | straight | long_strip | 2.338 | 0.906 | 24.852% | 424.636 | 3327.090 |
| pr25 | straight | pixel | 6.349 | 4.450 | 15.017% | 363.069 | 2855.970 |
| pr25 | straight | short_strip | 3.728 | 2.861 | 19.085% | 514.398 | 3302.215 |
| pr25 | positive | total | 12.297 | 8.232 | 17.449% | 1378.659 | 1406.887 |
| pr25 | positive | long_strip | 2.297 | 0.869 | 26.794% | 424.636 | 3329.620 |
| pr25 | positive | pixel | 6.360 | 4.475 | 14.603% | 389.379 | 2860.541 |
| pr25 | positive | short_strip | 3.639 | 2.887 | 18.517% | 514.398 | 3302.215 |
| pr25 | negative | total | 12.070 | 8.195 | 17.819% | 1378.782 | 1406.466 |
| pr25 | negative | long_strip | 2.102 | 0.839 | 29.367% | 424.636 | 3329.326 |
| pr25 | negative | pixel | 6.325 | 4.469 | 14.745% | 372.762 | 2865.088 |
| pr25 | negative | short_strip | 3.642 | 2.887 | 18.490% | 514.398 | 3302.215 |
| p170-s680-b1-l1287.33-front_loaded | straight | total | 13.773 | 8.840 | 12.311% | 1099.807 | 1103.138 |
| p170-s680-b1-l1287.33-front_loaded | straight | long_strip | 2.592 | 0.975 | 24.880% | 460.792 | 3323.812 |
| p170-s680-b1-l1287.33-front_loaded | straight | pixel | 6.493 | 4.558 | 12.961% | 381.653 | 2850.304 |
| p170-s680-b1-l1287.33-front_loaded | straight | short_strip | 4.688 | 3.306 | 7.133% | 450.959 | 3256.391 |
| p170-s680-b1-l1287.33-front_loaded | positive | total | 13.748 | 8.875 | 12.176% | 1011.762 | 1101.011 |
| p170-s680-b1-l1287.33-front_loaded | positive | long_strip | 2.706 | 0.971 | 26.330% | 461.421 | 3324.496 |
| p170-s680-b1-l1287.33-front_loaded | positive | pixel | 6.504 | 4.585 | 12.514% | 384.043 | 2857.048 |
| p170-s680-b1-l1287.33-front_loaded | positive | short_strip | 4.539 | 3.318 | 6.975% | 451.555 | 3256.167 |
| p170-s680-b1-l1287.33-front_loaded | negative | total | 13.549 | 8.837 | 12.557% | 1012.051 | 1101.011 |
| p170-s680-b1-l1287.33-front_loaded | negative | long_strip | 2.516 | 0.942 | 28.888% | 461.522 | 3324.496 |
| p170-s680-b1-l1287.33-front_loaded | negative | pixel | 6.461 | 4.577 | 12.671% | 382.842 | 2858.299 |
| p170-s680-b1-l1287.33-front_loaded | negative | short_strip | 4.572 | 3.318 | 6.961% | 450.956 | 3256.167 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | total | 13.685 | 9.031 | 11.325% | 1008.305 | 1104.623 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | long_strip | 2.571 | 0.975 | 24.852% | 461.026 | 3319.955 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | pixel | 7.083 | 4.857 | 8.783% | 384.341 | 2721.813 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | short_strip | 4.031 | 3.199 | 10.513% | 452.616 | 3260.829 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | total | 14.015 | 9.100 | 10.846% | 1006.640 | 1043.007 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | long_strip | 2.758 | 0.995 | 24.322% | 460.595 | 3324.496 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | 7.163 | 4.891 | 8.211% | 384.359 | 2779.275 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | short_strip | 4.093 | 3.214 | 10.232% | 451.555 | 3259.057 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | total | 13.760 | 9.072 | 11.137% | 1006.640 | 1043.007 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | long_strip | 2.573 | 0.969 | 26.536% | 461.522 | 3324.496 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | pixel | 7.128 | 4.891 | 8.206% | 385.217 | 2791.836 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | short_strip | 4.058 | 3.212 | 10.321% | 451.555 | 3260.237 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | total | 13.736 | 9.004 | 11.052% | 1009.942 | 1101.948 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | long_strip | 2.653 | 0.979 | 23.009% | 442.926 | 3319.474 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | pixel | 7.024 | 4.841 | 8.666% | 384.167 | 2714.729 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | short_strip | 4.060 | 3.185 | 10.539% | 447.668 | 3260.829 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | total | 13.898 | 9.036 | 10.733% | 1007.467 | 1048.774 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | long_strip | 2.674 | 0.970 | 23.061% | 441.659 | 3324.496 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | pixel | 7.175 | 4.871 | 8.163% | 384.483 | 2788.485 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | short_strip | 4.050 | 3.195 | 10.405% | 447.668 | 3259.057 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | total | 13.507 | 8.987 | 11.222% | 1008.038 | 1048.774 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | long_strip | 2.478 | 0.941 | 25.542% | 442.098 | 3324.496 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | pixel | 7.014 | 4.849 | 8.565% | 385.495 | 2797.878 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | short_strip | 4.014 | 3.196 | 10.361% | 447.419 | 3260.237 |
| p190-s720-b1-l1287.33-uniform | straight | total | 13.354 | 8.821 | 12.661% | 936.093 | 1068.292 |
| p190-s720-b1-l1287.33-uniform | straight | long_strip | 2.289 | 0.905 | 27.714% | 410.566 | 3324.496 |
| p190-s720-b1-l1287.33-uniform | straight | pixel | 6.631 | 4.654 | 11.699% | 345.998 | 2713.737 |
| p190-s720-b1-l1287.33-uniform | straight | short_strip | 4.434 | 3.261 | 9.015% | 394.267 | 3260.829 |
| p190-s720-b1-l1287.33-uniform | positive | total | 13.515 | 8.850 | 12.466% | 888.846 | 1062.650 |
| p190-s720-b1-l1287.33-uniform | positive | long_strip | 2.329 | 0.892 | 28.760% | 420.162 | 3327.090 |
| p190-s720-b1-l1287.33-uniform | positive | pixel | 6.798 | 4.685 | 11.172% | 360.995 | 2778.424 |
| p190-s720-b1-l1287.33-uniform | positive | short_strip | 4.388 | 3.274 | 8.949% | 394.827 | 3259.057 |
| p190-s720-b1-l1287.33-uniform | negative | total | 13.180 | 8.796 | 13.009% | 934.733 | 1064.176 |
| p190-s720-b1-l1287.33-uniform | negative | long_strip | 2.172 | 0.861 | 31.326% | 419.517 | 3326.437 |
| p190-s720-b1-l1287.33-uniform | negative | pixel | 6.646 | 4.664 | 11.578% | 368.801 | 2790.260 |
| p190-s720-b1-l1287.33-uniform | negative | short_strip | 4.363 | 3.271 | 9.021% | 394.827 | 3260.237 |

## Local coverage guards

Central eta=0 / vertex z=0 must preserve each subsystem's mean and zero-hit fraction.
Other eta-band / vertex-plane strata must not become entirely blind. Smaller local
regressions are retained explicitly; passing is not pointwise or continuum hermeticity.

| Candidate | Mode | Central guard | No new blind stratum | Strata/subsystem regressions |
| --- | --- | --- | --- | ---: |
| p170-s680-b1-l1287.33-front_loaded | straight | True | True | 24 |
| p170-s680-b1-l1287.33-front_loaded | positive | True | True | 20 |
| p170-s680-b1-l1287.33-front_loaded | negative | True | True | 20 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | True | True | 50 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | True | True | 38 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | True | True | 38 |
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
| pr25 | 8.1595 | 18.995% | 1379.50 |
| p170-s680-b1-l1287.33-front_loaded | 8.8547 | 13.261% | 1009.35 |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | 9.0229 | 12.383% | 1005.87 |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | 8.9836 | 12.139% | 1006.69 |
| p190-s720-b1-l1287.33-uniform | 8.8527 | 13.268% | 886.34 |

## Search and constraints

Evaluated 219 bounded candidates; 111 passed geometry/capacity constraints.
Every parameter set and rejection reason is retained in `study.json`.
Adverse service-budget failures remain in each case summary. Compact pockets,
connector bends, materials, cooling hydraulics and vessel access remain unqualified.
