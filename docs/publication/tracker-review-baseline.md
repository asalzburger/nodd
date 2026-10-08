# Full tracker TDR review baseline — 2026-10-07

The existing Overleaf report now describes the selected pixel, short-strip and
long-strip barrels and endcaps together. This is an editorial baseline for human
technical review. DES019–023 remain DRAFT; publication does not record design
sign-off or imply an accepted integrated detector.

The new tracker overview states the ten barrel assemblies and 21 discs per end,
distinguishes modules, two-coordinate strixels and stereo sensor faces, and shows
the nominal r–z layout and fixed service reservations. It explains the luminous
region, eta/pT/field hypotheses, layer-dependent measurement frames, structural
load hierarchy and the need to replace duplicated standalone service cells once.
Standalone model masses are not summed as an integrated tracker material budget.

The short-strip section describes the selected +15° same-radius barrel, nine
bearing stations, module/ASIC fixture, half-stave U-loops, local buses, petal
serpentines, mounting frames and cumulative service limits. The long-strip
section describes true 1D stereo faces, the structural sandwich, +12° barrel,
potted/ring mounting, the minimum15/recommended17 anchor screen, six-loop petals,
fully wrapped dielectric and common routes. Both retain the first-disc shifts,
old-reference coverage losses and failed/unqualified engineering cases.

Eight new vector drawings and a generated disc-datum table use bundled hashed
snapshots. The long-barrel view is a true retained-solid cut at z166.50mm; the
short-barrel and disc plans project multiple depths and say so. Existing pixel
manuscript, snapshots and figure bytes are preserved. Public bibliography entries
remain separate from internal source, producer and native execution identities.

The full report entrypoint is `main.tex`; `tracker-review.tex` is a complete
tracker extract and `pixel-detector.tex` remains pixel-only. The review title and
date identify this edition. The house style retains continuous review line
numbers and matches the PDF1.7 assets. Page QA restored Tracker running heads
after the pixel bibliography and put the review table after its introduction.

The [publication inventory](tracker-review-baseline.json) records the actual
Overleaf revision, source/artifact hashes, compiler/PDF evidence and limitations.
It omits the private remote and client data. Deterministic extraction and figure
generation perform no new native execution or optimization.

Review priorities are coupled barrel/endcap acceptance, global/joint mechanics
and handling, real electronics/thermal/hydraulic models, cable turns and adverse
capacity, integrated material accounting, and response/alignment/reconstruction.
The existing coverage, guard, warm-thermal, service-packing and mechanical failures
remain comparison controls; fixed envelopes are not enlarged in this publication.

Scientific sources are pinned at nODD
`0d74f228a51bfbfeef93e19d21b2e58585772817`, the merged subsystem prototype branch.
The documentation PR is stacked on that branch; it does not separately integrate
strip compacts into production main. Source publication revisions never replace
the retained dirty native execution identities or exact input/plugin hashes.
