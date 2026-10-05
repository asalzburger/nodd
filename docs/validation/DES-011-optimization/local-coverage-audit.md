# DES-011 local coverage audit

Source: `ac61f766b34f9bb60748e8fc4258a41037ca1e33`.

PROTOTYPE follow-up with the individual service-object envelope floor. Passing sampled coverage and passage bounds is conditional evidence, not engineering sign-off. Training selection remained frozen before dense validation.

The comparisons use identical track hashes in each mode. Structured eta bands combine the central and luminous-boundary angular grids at one exact vertex plane. Random eta bands use the independent uniform random cohort with interior vertices; these are finite-sample diagnostics, not a measurement of continuous hole size.

## Hard guards

| Case | Mode | Central | No newly blind structured bin | Smaller local regressions (all scopes/cohorts) |
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

Dense overall subsystem-mean guard (separate from the local guards above):

- `p170-s680-b1-l1287.33-front_loaded`: True.
- `p190-s680-b1-l1287.33-front_loaded-barrel-10`: True.
- `p190-s680-b1-l1287.33-front_loaded-original-pockets`: True.
- `p190-s720-b1-l1287.33-uniform`: False.
  straight, long_strip: 0.9104774536 → 0.9090683024 stations/track.

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
| p190-s720-b1-l1287.33-uniform | straight | long_strip | zero-hit increase | [1, 1.5) | -150 | 160 | 1.7937 → 1.6375 | 0.00% → 3.75% |

## Worst random local regressions

For each candidate/subsystem, show the largest mean-station loss and largest increase in zero-station fraction across all three modes; ties are retained in the JSON. The two extrema can occur in different bins.

| Case | Mode | Subsystem | Criterion | Eta | Vertex z, mm | Tracks | Mean stations | Zero-station fraction |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | pixel | mean loss | [0.5, 1) | interior | 296 | 3.3750 → 3.3243 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | short_strip | mean loss | [-1, -0.5) | interior | 258 | 3.9767 → 3.9612 | 0.00% → 0.00% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | long_strip | mean loss | [-0.5, 0) | interior | 262 | 1.5802 → 1.5496 | 4.58% → 6.11% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | long_strip | zero-hit increase | [-0.5, 0) | interior | 262 | 1.5802 → 1.5496 | 4.58% → 6.11% |
| p190-s720-b1-l1287.33-uniform | negative | long_strip | mean loss | [1.5, 2) | interior | 266 | 2.0714 → 2.0451 | 1.50% → 0.00% |
| p190-s720-b1-l1287.33-uniform | straight | long_strip | zero-hit increase | [1.5, 2) | interior | 266 | 1.9962 → 2.0639 | 0.00% → 0.38% |

## Independent random cohort aggregate

| Case | Mode | Subsystem | Tracks | Mean stations (baseline → candidate) | Zero-station fraction (baseline → candidate) |
| --- | --- | --- | ---: | ---: | ---: |
| p170-s680-b1-l1287.33-front_loaded | straight | pixel | 4096 | 4.3550 → 4.4978 | 0.098% → 0.098% |
| p170-s680-b1-l1287.33-front_loaded | straight | short_strip | 4096 | 2.9519 → 3.3994 | 22.583% → 16.455% |
| p170-s680-b1-l1287.33-front_loaded | straight | long_strip | 4096 | 0.8887 → 0.9866 | 48.950% → 46.997% |
| p170-s680-b1-l1287.33-front_loaded | positive | pixel | 4096 | 4.3562 → 4.4983 | 0.073% → 0.073% |
| p170-s680-b1-l1287.33-front_loaded | positive | short_strip | 4096 | 2.9573 → 3.4043 | 22.705% → 16.626% |
| p170-s680-b1-l1287.33-front_loaded | positive | long_strip | 4096 | 0.9148 → 1.0137 | 49.536% → 47.339% |
| p170-s680-b1-l1287.33-front_loaded | negative | pixel | 4096 | 4.3452 → 4.4922 | 0.073% → 0.073% |
| p170-s680-b1-l1287.33-front_loaded | negative | short_strip | 4096 | 2.9612 → 3.4070 | 22.632% → 16.577% |
| p170-s680-b1-l1287.33-front_loaded | negative | long_strip | 4096 | 0.8699 → 0.9700 | 50.220% → 47.949% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | pixel | 4096 | 4.3550 → 4.7583 | 0.098% → 0.000% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | short_strip | 4096 | 2.9519 → 3.2832 | 22.583% → 18.579% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | straight | long_strip | 4096 | 0.8887 → 0.9871 | 48.950% → 47.095% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | pixel | 4096 | 4.3562 → 4.7612 | 0.073% → 0.000% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | short_strip | 4096 | 2.9573 → 3.2954 | 22.705% → 18.652% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | positive | long_strip | 4096 | 0.9148 → 1.0188 | 49.536% → 47.046% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | pixel | 4096 | 4.3452 → 4.7546 | 0.073% → 0.000% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | short_strip | 4096 | 2.9612 → 3.2959 | 22.632% → 18.652% |
| p190-s680-b1-l1287.33-front_loaded-barrel-10 | negative | long_strip | 4096 | 0.8699 → 0.9749 | 50.220% → 48.120% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | pixel | 4096 | 4.3550 → 4.7417 | 0.098% → 0.073% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | short_strip | 4096 | 2.9519 → 3.2732 | 22.583% → 18.579% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | straight | long_strip | 4096 | 0.8887 → 0.9897 | 48.950% → 47.095% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | pixel | 4096 | 4.3562 → 4.7424 | 0.073% → 0.073% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | short_strip | 4096 | 2.9573 → 3.2839 | 22.705% → 18.652% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | positive | long_strip | 4096 | 0.9148 → 1.0144 | 49.536% → 47.363% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | pixel | 4096 | 4.3452 → 4.7334 | 0.073% → 0.049% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | short_strip | 4096 | 2.9612 → 3.2856 | 22.632% → 18.652% |
| p190-s680-b1-l1287.33-front_loaded-original-pockets | negative | long_strip | 4096 | 0.8699 → 0.9673 | 50.220% → 47.998% |
| p190-s720-b1-l1287.33-uniform | straight | pixel | 4096 | 4.3550 → 4.5837 | 0.098% → 0.073% |
| p190-s720-b1-l1287.33-uniform | straight | short_strip | 4096 | 2.9519 → 3.3574 | 22.583% → 18.579% |
| p190-s720-b1-l1287.33-uniform | straight | long_strip | 4096 | 0.8887 → 0.9270 | 48.950% → 48.193% |
| p190-s720-b1-l1287.33-uniform | positive | pixel | 4096 | 4.3562 → 4.5798 | 0.073% → 0.073% |
| p190-s720-b1-l1287.33-uniform | positive | short_strip | 4096 | 2.9573 → 3.3674 | 22.705% → 18.652% |
| p190-s720-b1-l1287.33-uniform | positive | long_strip | 4096 | 0.9148 → 0.9482 | 49.536% → 48.608% |
| p190-s720-b1-l1287.33-uniform | negative | pixel | 4096 | 4.3452 → 4.5786 | 0.073% → 0.049% |
| p190-s720-b1-l1287.33-uniform | negative | short_strip | 4096 | 2.9612 → 3.3699 | 22.632% → 18.652% |
| p190-s720-b1-l1287.33-uniform | negative | long_strip | 4096 | 0.8699 → 0.9011 | 50.220% → 49.243% |

No interval uncertainty, collision-data weighting or continuum hermeticity claim is implied. Dense structured angles were reused after the first failure; the fresh random seed provides the independent cohort. Counts are usable stations, so incomplete long-strip stereo pairs do not count as measurements.
