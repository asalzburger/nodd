# DES-008 compatibility with the PR13 A and C1 layouts

- Date: 2026-09-25
- Status: **DRAFT / PROTOTYPE**, no detector or service-clearance approval
- Governing: [DES-008 C01/C11](../design/DES-008-long-strip-modules.md), DES-005 / TRK-LSTRIP
- Requested correction: [session record](../../logs/codex/SESSION-2026-09-25-long-strip-layout-compatibility.md)
- Source: [PR13 reviewed layouts](https://github.com/asalzburger/nodd/blob/f57e26e83b826867c2720edcd702e808fe946854/docs/design/DES-006-reviewed-layouts.json)
- [Curated exact geometry](../../tools/long_strip/pr13-layouts.json), [executed results](DES-008-layout-compatibility.json)

## Interface and decision

Both active layouts have the same outer long-strip geometry. C1's inclination
changes the short-strip barrel ends; it does not change the long-strip aperture.
These are **NODD DESIGN CHOICE — source proposals**, not engineering facts or
signed-off detector parameters.

| Quantity [mm] | PR13 A | PR13 C1 | DES-008 after correction |
| --- | --- | --- | --- |
| Long-strip disk target radii | 710–1100 | 710–1100 | 710–1100 |
| Positive long-strip disk z | 1430,1800,2120,2450,2730,3120 | same | all six checked |
| Negative disks | mirror of positive side | same | reflected complete module stack and vertex |
| Long-strip barrel radii / half-length | 840,1060 / 1400 | same | interface reference; barrel not tiled here |
| Short-strip disk target radii | 200–700 | 200–700 | nominal 10 mm band gap recorded |
| Tracker host maximum r / abs(z) | 1140 / 3150 | same | occupied envelope checked |

DES-008's initial 700 mm aperture and 1320 mm disk fixture matched neither
current long-strip proposal. They have been corrected to 710 mm and 1430 mm.
The previous inputs/results remain at
[`68932692fc61bb25d21e55a915a12eb929b2b316`](https://github.com/asalzburger/nodd/tree/68932692fc61bb25d21e55a915a12eb929b2b316/tools/long_strip).
This amendment does not edit PR13 or claim its whole-tracker performance losses
have been resolved.

**Retain six rings as the common working arrangement.** They require 404 square
sandwich modules per disk (previously 402), with centres and counts:

| Ring index | Centre radius [mm] | Module pairs |
| ---: | ---: | ---: |
| 0 | 742.0 | 56 |
| 1 | 807.2 | 60 |
| 2 | 872.4 | 66 |
| 3 | 937.6 | 70 |
| 4 | 1002.8 | 74 |
| 5 | 1068.0 | 78 |

Counts were recomputed from the unchanged sensor size, stereo rotation and overlap
rules, not copied after shifting the inner boundary. Total is 808 sensors and
969,600 nominal 80 µm strip channels per disk. The six-ring wedge now has 360
pairs; the full [candidate comparison](DES-008-ring-study.md) was regenerated.

## Five versus six rings at every disk position

Worst missing-pair area over both grids, normal projection and all three vertex
fixtures is shown below. Coverage requires both sensors of the **same** module.
The 338-pair five-ring alternative is retained as a reduction control.

| abs(z_disk) [mm] | Six rings: missing pair area | Five rings: missing pair area | Body conflicts, both candidates |
| ---: | ---: | ---: | ---: |
| 1430 | 0 sampled | 1.0914% | 0 |
| 1800 | 0 sampled | 0.2461% | 0 |
| 2120 | 0 sampled | 0.0412% | 0 |
| 2450 | 0 sampled | 0 sampled | 0 |
| 2730 | 0 sampled | 0 sampled | 0 |
| 3120 | 0 sampled | 0 sampled | 0 |

Five rings are therefore unsuitable as a common arrangement. A mixed scheme with
five rings on the last three disks could be studied separately for silicon versus
assembly complexity; it is not adopted here. Six rings preserve one arrangement
across A/C1 and all disks. Zero samples do not prove continuous hermeticity or
tracking efficiency.

## Physical extensions and mounting constraints

The aperture is a **coverage target at the disk reference plane**. It is not a
claim that every sensor or support stops at r=710 mm. With stereo, overlap and
parallax allowances, the square candidate has:

| Envelope or remaining allowance | Value [mm] | Interpretation |
| --- | ---: | --- |
| Rotated active sensor-outline radii | 693.85–1117.94 | Excludes outside guard/die extensions |
| Trial body radii, including guard/service boxes | 687.55–1123.68 | Extends 22.45 mm below the 710 mm target |
| Body residual to 1140 mm host | 16.32 | Shared services/support still omitted |
| Body overlap in r with 700 mm short-strip target | 12.45 | Nominal 10 mm radial service corridor is not clear |
| Four-level total normal depth | 31.3 | Existing DES-008 fixture, not a qualified assembly |
| Nearest short/long disk centre separation | 40 | PR13 signed planes, both A and C1 |
| Short/long trial axial-envelope separation | 18.85 | 40−31.3/2−11/2; PR21 short-strip depth fixture |
| First disk body to ideal long-strip barrel end | 14.35 | 1430−31.3/2−1400; barrel end structures unknown |
| Last disk body to host end | 14.35 | 3150−3120−31.3/2 |

The radial extensions do not imply a disk-to-disk collision because the checked
axial envelopes are disjoint. Conversely, this does **not** prove that shared
carriers, cooling bends, cabling or barrel-end mounts fit. Those missing volumes
could consume the quoted residuals. A/C1 compatibility is established for the
reference-plane annuli, sampled pair coverage and the listed trial envelopes;
a continuously empty 10 mm radial corridor is explicitly **not** established.
If such a corridor becomes a hard requirement, the module masks/placement and
coverage must be redesigned together rather than merely adding rings.

## Provenance, reproduction and checks

The source revision is PR13 head `f57e26e83b826867c2720edcd702e808fe946854`;
the reviewed geometry also equals the evidence target
`06275ecf55e4bb428ffbdb1d5beb72c9a7aca064`. Its original file SHA-256 and every
selected layer field were verified against Git. The curated extraction retains
both candidates and all signed long-strip disk IDs, short-strip disks and
long-strip barrels, without importing that unmerged branch.

```sh
python3 -B -m unittest discover -s tools/long_strip -p 'test_*.py' -v
reference/cache/envelope-venv/bin/python -B tools/long_strip/compatibility.py
```

Fourteen tests passed, including guards against the original 700 mm / 1320 mm
mismatch, independent A/C1 or negative-side drift, and reflection of disk,
module stack and vertex. The main seven-candidate study and figure were also
regenerated using its documented command. The full compatibility calculation
uses 250×720 and 500×1440 polar midpoint grids, vertices −150/0/+150 mm, 40 mrad
relative stereo and 5 mm sensor separation. There are no random samples. JSON
records the actual configuration, source hashes, Git revision/working tree,
Python/NumPy versions and numerical epsilon.

Mirroring uses `z -> -z`, module offsets `w -> -w`, and vertex `v -> -v`;
`(z+w-v)/(z-v)` is unchanged. The vertex set is symmetric, so one numerical case
per |z| applies to both signed sides and both identical A/C1 long-strip layouts.
Additionally, full module enumeration tests 1440 azimuthal samples directly on
each target boundary circle for every vertex and disk position: all 18 cases
have zero inner- or outer-boundary misses. This supplements the area-grid
midpoints without establishing a continuous-boundary proof.
No assumption of unrelated independently generated negative-side modules is made.
Manufacturing handedness, full reconstruction/material performance and engineering
qualification remain open. DES-008 remains DRAFT; no human approval is recorded.
