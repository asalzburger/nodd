# DES-011 generated placement results

PROTOTYPE. Best tested candidates; no global optimum or engineering approval.

Selection was frozen on training rays before dense validation. The dense grids
share some training angles; the separately reported random cohort is independent.

Source revision: `6c882257c368927732315dbc756f1b89263d95af`; tracked source dirty: False.

| Role | Candidate |
| --- | --- |
| coverage | p190-s680-b1-l1350-front_loaded-barrel-10 |
| spacing | p190-s680-b1-l1350-front_loaded |
| area | p170-s680-b1-l1350-front_loaded |
| Original-pocket control | p190-s680-b1-l1350-front_loaded-original-pockets |

All areas sum sensor/patch surfaces; overlaps are counted. Gaps are 3D path
distances between distinct usable stations, with complete same-module stereo pairs.

| Candidate | Physical silicon, m² | Summed active silicon, m² | Mean stations | Worst-mode p95 maximum inter-station gap, mm | Fixed-reference missed stations |
| --- | ---: | ---: | ---: | ---: | ---: |
| pr25 | 177.303 | 172.971 | 8.2273 | 1379.34 | 17.593% |
| p170-s680-b1-l1350-front_loaded | 202.542 | 197.615 | 8.8604 | 1099.81 | 12.070% |
| p190-s680-b1-l1350-front_loaded | 199.828 | 194.961 | 9.0195 | 1007.16 | 11.080% |
| p190-s680-b1-l1350-front_loaded-barrel-10 | 199.032 | 194.186 | 9.0429 | 1007.42 | 11.181% |
| p190-s680-b1-l1350-front_loaded-original-pockets | 199.828 | 194.961 | 9.0151 | 1008.61 | 10.880% |

## Per-mode and subsystem dense validation

Fixed-reference missing fractions refer to the original cobe ideal layers,
including when a candidate moved or refilled them. Candidate-local missing
fractions remain separately available under `coverage` in each summary JSON.

| Candidate | Mode | Subsystem | Mean sensor hits | Mean usable stations | Fixed-reference missing | p95 maximum inter-station gap, mm | p95 boundary gap, mm |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| pr25 | straight | total | 12.411 | 8.227 | 17.620% | 1379.339 | 1407.670 |
| pr25 | straight | long_strip | 2.340 | 0.904 | 24.871% | 424.636 | 3330.363 |
| pr25 | straight | pixel | 6.330 | 4.443 | 14.969% | 363.782 | 2856.487 |
| pr25 | straight | short_strip | 3.740 | 2.880 | 19.063% | 514.398 | 3302.215 |
| pr25 | positive | total | 12.314 | 8.248 | 17.374% | 1378.659 | 1406.466 |
| pr25 | positive | long_strip | 2.296 | 0.871 | 26.573% | 424.636 | 3332.048 |
| pr25 | positive | pixel | 6.343 | 4.471 | 14.529% | 387.309 | 2860.727 |
| pr25 | positive | short_strip | 3.674 | 2.907 | 18.477% | 514.398 | 3302.215 |
| pr25 | negative | total | 12.077 | 8.206 | 17.786% | 1379.141 | 1406.466 |
| pr25 | negative | long_strip | 2.099 | 0.839 | 29.269% | 424.636 | 3333.383 |
| pr25 | negative | pixel | 6.314 | 4.461 | 14.699% | 371.844 | 2870.967 |
| pr25 | negative | short_strip | 3.665 | 2.907 | 18.487% | 514.398 | 3302.215 |
| p170-s680-b1-l1350-front_loaded | straight | total | 13.745 | 8.821 | 12.384% | 1099.807 | 1103.139 |
| p170-s680-b1-l1350-front_loaded | straight | long_strip | 2.552 | 0.939 | 26.101% | 445.901 | 3322.807 |
| p170-s680-b1-l1350-front_loaded | straight | pixel | 6.477 | 4.553 | 12.873% | 382.814 | 2853.302 |
| p170-s680-b1-l1350-front_loaded | straight | short_strip | 4.717 | 3.329 | 7.099% | 451.295 | 3264.733 |
| p170-s680-b1-l1350-front_loaded | positive | total | 13.764 | 8.900 | 11.713% | 1012.945 | 1101.011 |
| p170-s680-b1-l1350-front_loaded | positive | long_strip | 2.695 | 0.978 | 23.032% | 444.689 | 3324.496 |
| p170-s680-b1-l1350-front_loaded | positive | pixel | 6.493 | 4.580 | 12.437% | 384.016 | 2858.083 |
| p170-s680-b1-l1350-front_loaded | positive | short_strip | 4.576 | 3.341 | 6.927% | 451.461 | 3264.903 |
| p170-s680-b1-l1350-front_loaded | negative | total | 13.540 | 8.860 | 12.113% | 1013.252 | 1101.011 |
| p170-s680-b1-l1350-front_loaded | negative | long_strip | 2.493 | 0.947 | 25.758% | 444.689 | 3324.496 |
| p170-s680-b1-l1350-front_loaded | negative | pixel | 6.442 | 4.570 | 12.609% | 382.842 | 2861.725 |
| p170-s680-b1-l1350-front_loaded | negative | short_strip | 4.605 | 3.344 | 6.891% | 451.085 | 3264.733 |
| p190-s680-b1-l1350-front_loaded | straight | total | 13.656 | 8.982 | 11.375% | 1007.160 | 1104.623 |
| p190-s680-b1-l1350-front_loaded | straight | long_strip | 2.552 | 0.939 | 26.101% | 445.901 | 3322.807 |
| p190-s680-b1-l1350-front_loaded | straight | pixel | 7.022 | 4.838 | 8.534% | 384.452 | 2725.201 |
| p190-s680-b1-l1350-front_loaded | straight | short_strip | 4.082 | 3.205 | 10.602% | 452.297 | 3269.170 |
| p190-s680-b1-l1350-front_loaded | positive | total | 13.952 | 9.067 | 10.651% | 1006.409 | 1041.806 |
| p190-s680-b1-l1350-front_loaded | positive | long_strip | 2.695 | 0.978 | 23.032% | 444.689 | 3324.496 |
| p190-s680-b1-l1350-front_loaded | positive | pixel | 7.159 | 4.869 | 8.034% | 385.217 | 2794.563 |
| p190-s680-b1-l1350-front_loaded | positive | short_strip | 4.099 | 3.219 | 10.374% | 451.631 | 3269.170 |
| p190-s680-b1-l1350-front_loaded | negative | total | 13.549 | 9.010 | 11.215% | 1005.443 | 1041.806 |
| p190-s680-b1-l1350-front_loaded | negative | long_strip | 2.493 | 0.947 | 25.758% | 444.689 | 3324.496 |
| p190-s680-b1-l1350-front_loaded | negative | pixel | 7.000 | 4.845 | 8.452% | 386.444 | 2800.466 |
| p190-s680-b1-l1350-front_loaded | negative | short_strip | 4.056 | 3.218 | 10.436% | 451.834 | 3269.170 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | straight | total | 13.674 | 9.008 | 11.437% | 1007.417 | 1104.623 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | straight | long_strip | 2.546 | 0.944 | 25.668% | 445.901 | 3322.807 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | straight | pixel | 7.065 | 4.848 | 8.732% | 384.302 | 2726.892 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | straight | short_strip | 4.063 | 3.216 | 10.630% | 452.616 | 3269.170 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | positive | total | 13.932 | 9.073 | 10.919% | 1006.640 | 1041.806 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | positive | long_strip | 2.655 | 0.958 | 24.711% | 444.689 | 3324.496 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | positive | pixel | 7.149 | 4.884 | 8.180% | 384.318 | 2802.034 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | positive | short_strip | 4.128 | 3.231 | 10.355% | 452.003 | 3269.170 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | negative | total | 13.670 | 9.047 | 11.188% | 1005.464 | 1041.806 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | negative | long_strip | 2.463 | 0.931 | 27.062% | 444.689 | 3324.496 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | negative | pixel | 7.114 | 4.886 | 8.115% | 385.139 | 2804.179 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | negative | short_strip | 4.093 | 3.230 | 10.422% | 452.308 | 3269.170 |
| p190-s680-b1-l1350-front_loaded-original-pockets | straight | total | 13.734 | 8.994 | 11.047% | 1008.608 | 1101.948 |
| p190-s680-b1-l1350-front_loaded-original-pockets | straight | long_strip | 2.637 | 0.956 | 23.186% | 433.400 | 3322.545 |
| p190-s680-b1-l1350-front_loaded-original-pockets | straight | pixel | 7.011 | 4.836 | 8.554% | 384.167 | 2726.247 |
| p190-s680-b1-l1350-front_loaded-original-pockets | straight | short_strip | 4.086 | 3.202 | 10.628% | 447.668 | 3269.170 |
| p190-s680-b1-l1350-front_loaded-original-pockets | positive | total | 13.915 | 9.054 | 10.516% | 1006.717 | 1047.573 |
| p190-s680-b1-l1350-front_loaded-original-pockets | positive | long_strip | 2.668 | 0.971 | 21.566% | 427.501 | 3324.496 |
| p190-s680-b1-l1350-front_loaded-original-pockets | positive | pixel | 7.163 | 4.868 | 8.055% | 384.295 | 2798.803 |
| p190-s680-b1-l1350-front_loaded-original-pockets | positive | short_strip | 4.084 | 3.215 | 10.450% | 447.307 | 3269.170 |
| p190-s680-b1-l1350-front_loaded-original-pockets | negative | total | 13.511 | 8.997 | 11.076% | 1006.708 | 1047.573 |
| p190-s680-b1-l1350-front_loaded-original-pockets | negative | long_strip | 2.462 | 0.937 | 24.559% | 429.971 | 3324.496 |
| p190-s680-b1-l1350-front_loaded-original-pockets | negative | pixel | 7.000 | 4.845 | 8.463% | 385.495 | 2800.812 |
| p190-s680-b1-l1350-front_loaded-original-pockets | negative | short_strip | 4.049 | 3.216 | 10.429% | 447.667 | 3269.170 |

## Independent random cohort

| Candidate | Mean stations | Fixed-reference missed stations | Worst-mode p95 maximum inter-station gap, mm |
| --- | ---: | ---: | ---: |
| pr25 | 8.1967 | 18.861% | 1379.95 |
| p170-s680-b1-l1350-front_loaded | 8.9209 | 12.635% | 1009.70 |
| p190-s680-b1-l1350-front_loaded | 9.0370 | 11.990% | 1005.12 |
| p190-s680-b1-l1350-front_loaded-barrel-10 | 9.0726 | 11.938% | 1005.28 |
| p190-s680-b1-l1350-front_loaded-original-pockets | 9.0286 | 11.720% | 1006.07 |

## Search and constraints

Evaluated 111 bounded candidates; 39 passed geometry/capacity constraints.
Every parameter set and rejection reason is retained in `study.json`.
Adverse service-budget failures remain in each case summary. Compact pockets,
connector bends, materials, cooling hydraulics and vessel access remain unqualified.
