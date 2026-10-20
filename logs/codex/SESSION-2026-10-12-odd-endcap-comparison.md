# SESSION-2026-10-12-odd-endcap-comparison — Current ODD endcap coverage

2026-10-12. User exact request: “How does the current ODD looks like in this
respect?” Context: endcap active coverage and the DES029 repair drawing.
Starting revision4dd968356ec709e671aceaa4f3fcdd20fba10ecf, branch
codex/calorimeter-assemblies, clean. Bounded source review and documentation;
no geometry input changes or human design sign-off.

The public GitHub repository points development to CERN GitLab. Browser GitLab
access returned403; default-shell curl lacked DNS access. Approved network
access to the public GitLab API succeeded. Project121973 main is still
c167363f3d4ad1540a577af99071283caf54f3a6, committed2026-04-29. Four exact-revision
raw files matched the clean pinned cache byte for byte: Envelopes, ECal, HCal
and ODDPolyhedraEndcapCalorimeter factory. Current revision/file hashes are
recorded, distinct from latest tag metadata; no new software dependency adopted.

ODD uses16 trapezoidal sectors with full-footprint sensitive silicon or
polystyrene slices;5.1/30mm cells are logical segmentation. XML gap2.5mm reduces
each half-width, yielding4.904mm normal seam width. Polygon face-minus-seams
arithmetic gives98.5927%ECAL/99.3252%HCAL sensitive area outside the hole.
An independent trapezoid-area expression agrees. Inner apothems315/355mm and
fronts3200/3600mm imply front aperture near|eta|3 with polygonal phi variation.
These estimates are not efficiency or full-depth acceptance claims. There is no
fresh native ODD construction or transport validation in this task.

The nODD prototype's31.85%/38.82% plate fractions and first sensitive radial
edges908.9/1483.15mm come from finite rectangular packaging and its elementary
packer. Denominators and detector dimensions differ and are explicitly stated.
The engineering objective is near-contiguous physical modules on shaped
carriers with explicit guards/services, not adopting fictitious continuous
sensitive sheets. Requirements and mechanics still need human review.

A four-panel source/placement-derived figure compares both technologies at
each detector's own physical dimensions; PNG visually inspected successfully.
Reproduce arithmetic/figure using odd_endcap_comparison.py with the pinned ODD
source directory and optional --plot. It rejects revision/hash differences.
Companion review, reproducible record, source catalogue and task evidence added
to open PR69. Check commands/results and changed files are in the paired JSON.
A journal replacement patch used conflicting delete/add operations and was
rejected without changing that file; a direct text write completed the edit.

Exact client token counters are unavailable; usage remains empty/unknown, not
zero. Session summary preserves disjoint existing observations and missing
coverage. Repository summary/build retains209 disjoint observed turns and620812827
observed tokens, with no measurements for this task. This task copies no
previous token observations or private state.
