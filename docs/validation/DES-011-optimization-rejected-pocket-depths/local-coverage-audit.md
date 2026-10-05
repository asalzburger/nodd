# DES-011 local coverage audit

Source: `10203d9a3f41d82cb467a7deb75e8293b0f1cc95`.

Retained as a rejected pocket-depth diagnostic: the compact strip passages cannot fit the declared round power cable plus corridor skins. Coverage improvements do not establish mechanical feasibility; the original-pocket case is a separate comparison control.

The comparisons use identical track hashes in each mode. Structured eta bands combine the central and luminous-boundary angular grids at one exact vertex plane. Random eta bands use the independent uniform random cohort with interior vertices; these are finite-sample diagnostics, not a measurement of continuous hole size.

## Hard guards

| Case | Mode | Central | No newly blind structured bin | Smaller local regressions (all scopes/cohorts) |
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

Dense overall subsystem-mean guard (separate from the local guards above):

- `p170-s680-b1-l1287.33-front_loaded`: True.
- `p190-s680-b1-l1287.33-front_loaded-barrel-10`: True.
- `p190-s680-b1-l1287.33-front_loaded-original-pockets`: True.
- `p190-s720-b1-l1287.33-uniform`: False.
  straight, long_strip: 0.9057526525 → 0.9050895225 stations/track.

## Exact central rays

| Case | Mode | Subsystem | Criterion | Eta | Vertex z, mm | Tracks | Mean stations | Zero-station fraction |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| p170-s680-b1-l1287.33-front_loaded | straight | long_strip | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | straight | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | straight | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | positive | long_strip | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | positive | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | positive | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | negative | long_strip | central | eta=0 | 0 | 96 | 1.9375 → 1.9375 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | negative | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | negative | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | long_strip | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | long_strip | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | long_strip | central | eta=0 | 0 | 96 | 1.9375 → 1.9583 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | long_strip | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | long_strip | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | long_strip | central | eta=0 | 0 | 96 | 1.9375 → 1.9375 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | straight | long_strip | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | straight | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | straight | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | positive | long_strip | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | positive | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | positive | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | negative | long_strip | central | eta=0 | 0 | 96 | 1.9375 → 1.9375 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | negative | pixel | central | eta=0 | 0 | 96 | 2.0000 → 2.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | negative | short_strip | central | eta=0 | 0 | 96 | 4.0000 → 4.0000 | 0.00% → 0.00% |

## Worst structured local regressions

For each candidate/subsystem, show the largest mean-station loss and largest increase in zero-station fraction across all three modes; ties are retained in the JSON. The two extrema can occur in different bins.

| Case | Mode | Subsystem | Criterion | Eta | Vertex z, mm | Tracks | Mean stations | Zero-station fraction |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| p170-s680-b1-l1287.33-front_loaded | negative | pixel | mean loss | [-2.5, -2) | 0 | 128 | 3.4531 → 3.3906 | 0.00% → 0.00% |
| p170-s680-b1-l1287.33-front_loaded | straight | long_strip | mean loss | [1.5, 2) | 150 | 128 | 2.4609 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | mean loss | [0.5, 1) | 150 | 128 | 3.6172 → 3.2500 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | zero-hit increase | [1.5, 2) | 150 | 128 | 2.6484 → 2.6953 | 0.00% → 3.12% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | long_strip | mean loss | [1.5, 2) | 150 | 128 | 2.4609 → 2.0000 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | long_strip | zero-hit increase | [-1, -0.5) | 0 | 160 | 1.7750 → 1.4375 | 3.12% → 9.38% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | pixel | mean loss | [-4, -3.5) | -150 | 224 | 7.3795 → 7.3080 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | long_strip | mean loss | [1.5, 2) | 150 | 128 | 2.4609 → 2.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | negative | pixel | mean loss | [-2.5, -2) | -150 | 128 | 3.7266 → 3.6875 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | straight | long_strip | mean loss | [-1.5, -1) | -150 | 128 | 2.0000 → 1.0000 | 0.00% → 0.00% |
| p190-s720-b1-l1287.33-uniform | negative | long_strip | zero-hit increase | [1, 1.5) | 150 | 160 | 1.7375 → 1.1438 | 0.00% → 1.88% |

## Worst random local regressions

For each candidate/subsystem, show the largest mean-station loss and largest increase in zero-station fraction across all three modes; ties are retained in the JSON. The two extrema can occur in different bins.

| Case | Mode | Subsystem | Criterion | Eta | Vertex z, mm | Tracks | Mean stations | Zero-station fraction |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | mean loss | [-0.5, 0) | interior | 252 | 3.1746 → 3.1468 | 0.40% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | zero-hit increase (2 ties) | [0.5, 1) | interior | 281 | 3.2811 → 3.3060 | 0.00% → 0.36% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | long_strip | mean loss | [0, 0.5) | interior | 233 | 1.6180 → 1.5794 | 3.00% → 3.43% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | long_strip | zero-hit increase | [0, 0.5) | interior | 233 | 1.7082 → 1.6781 | 0.86% → 3.00% |
| p190-s720-b1-l1287.33-uniform | positive | long_strip | mean loss | [-2, -1.5) | interior | 249 | 2.0843 → 2.0803 | 0.80% → 0.40% |
| p190-s720-b1-l1287.33-uniform | positive | long_strip | zero-hit increase | [1, 1.5) | interior | 262 | 1.6450 → 1.8702 | 0.00% → 0.38% |

## Independent random cohort aggregate

| Case | Mode | Subsystem | Tracks | Mean stations (baseline → candidate) | Zero-station fraction (baseline → candidate) |
| --- | --- | --- | ---: | ---: | ---: |
| p170-s680-b1-l1287.33-front_loaded | straight | pixel | 4096 | 4.3464 → 4.4854 | 0.073% → 0.073% |
| p170-s680-b1-l1287.33-front_loaded | straight | short_strip | 4096 | 2.9304 → 3.3831 | 22.681% → 16.577% |
| p170-s680-b1-l1287.33-front_loaded | straight | long_strip | 4096 | 0.8748 → 0.9739 | 49.707% → 48.022% |
| p170-s680-b1-l1287.33-front_loaded | positive | pixel | 4096 | 4.3508 → 4.4893 | 0.073% → 0.073% |
| p170-s680-b1-l1287.33-front_loaded | positive | short_strip | 4096 | 2.9387 → 3.3977 | 22.900% → 16.675% |
| p170-s680-b1-l1287.33-front_loaded | positive | long_strip | 4096 | 0.8945 → 0.9966 | 50.098% → 48.340% |
| p170-s680-b1-l1287.33-front_loaded | negative | pixel | 4096 | 4.3489 → 4.4863 | 0.024% → 0.024% |
| p170-s680-b1-l1287.33-front_loaded | negative | short_strip | 4096 | 2.9382 → 3.3940 | 22.827% → 16.748% |
| p170-s680-b1-l1287.33-front_loaded | negative | long_strip | 4096 | 0.8557 → 0.9578 | 50.977% → 48.999% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | pixel | 4096 | 4.3464 → 4.7578 | 0.073% → 0.000% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | short_strip | 4096 | 2.9304 → 3.2776 | 22.681% → 18.872% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | long_strip | 4096 | 0.8748 → 0.9753 | 49.707% → 47.998% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | 4096 | 4.3508 → 4.7664 | 0.073% → 0.049% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | short_strip | 4096 | 2.9387 → 3.2905 | 22.900% → 18.823% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | long_strip | 4096 | 0.8945 → 0.9973 | 50.098% → 48.462% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | pixel | 4096 | 4.3489 → 4.7593 | 0.024% → 0.024% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | short_strip | 4096 | 2.9382 → 3.2869 | 22.827% → 18.921% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | long_strip | 4096 | 0.8557 → 0.9578 | 50.977% → 48.804% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | pixel | 4096 | 4.3464 → 4.7322 | 0.073% → 0.073% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | short_strip | 4096 | 2.9304 → 3.2622 | 22.681% → 18.872% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | long_strip | 4096 | 0.8748 → 0.9792 | 49.707% → 48.120% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | pixel | 4096 | 4.3508 → 4.7341 | 0.073% → 0.073% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | short_strip | 4096 | 2.9387 → 3.2749 | 22.900% → 18.823% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | long_strip | 4096 | 0.8945 → 1.0010 | 50.098% → 48.340% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | pixel | 4096 | 4.3489 → 4.7305 | 0.024% → 0.024% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | short_strip | 4096 | 2.9382 → 3.2739 | 22.827% → 18.921% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | long_strip | 4096 | 0.8557 → 0.9626 | 50.977% → 49.048% |
| p190-s720-b1-l1287.33-uniform | straight | pixel | 4096 | 4.3464 → 4.5857 | 0.073% → 0.073% |
| p190-s720-b1-l1287.33-uniform | straight | short_strip | 4096 | 2.9304 → 3.3406 | 22.681% → 18.872% |
| p190-s720-b1-l1287.33-uniform | straight | long_strip | 4096 | 0.8748 → 0.9102 | 49.707% → 49.097% |
| p190-s720-b1-l1287.33-uniform | positive | pixel | 4096 | 4.3508 → 4.5889 | 0.073% → 0.073% |
| p190-s720-b1-l1287.33-uniform | positive | short_strip | 4096 | 2.9387 → 3.3628 | 22.900% → 18.823% |
| p190-s720-b1-l1287.33-uniform | positive | long_strip | 4096 | 0.8945 → 0.9324 | 50.098% → 49.536% |
| p190-s720-b1-l1287.33-uniform | negative | pixel | 4096 | 4.3489 → 4.5874 | 0.024% → 0.024% |
| p190-s720-b1-l1287.33-uniform | negative | short_strip | 4096 | 2.9382 → 3.3586 | 22.827% → 18.921% |
| p190-s720-b1-l1287.33-uniform | negative | long_strip | 4096 | 0.8557 → 0.8916 | 50.977% → 50.122% |

No interval uncertainty, collision-data weighting or continuum hermeticity claim is implied. Dense structured angles were reused after the first failure; the fresh random seed provides the independent cohort. Counts are usable stations, so incomplete long-strip stereo pairs do not count as measurements.
