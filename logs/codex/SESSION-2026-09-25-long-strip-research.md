# SESSION-2026-09-25-long-strip-research — Stereo long-strip module investigation

## Scope and evidence

Contemporaneous curated record of the user's long-strip follow-up to PR21.
Started from `58136c8adad0d10bb046bef3a574e181b7e1463c` on main; work branch
`research/long-strip-modules`. The pre-existing untracked
`tools/tracker_layout/__pycache__/covariance_control.cpython-314.pyc` was preserved.
Actual conversation start time is unknown. No subagents were used.

Read root instructions, PROJECT, DES-005 and TrackTech input, ADR-006, logging
and tracking workflows. Inspected PR21 at
`17d84a4c92916a49929db3c5e75684e51bf613b7` and its linked issue20, with its
DES-007, source guide, code and tests. This branch stays independent of the
unmerged short-strip PR; convex geometry helpers carry their pinned attribution.

## Selected conversation

User request, paraphrased: repeat the short-strip exercise for long-strip modules,
which are stereo sandwiches; study a good geometry and flag stereo rotation,
gap, mounting, local support and cooling interactions. Earlier explicit permission
to commit, push and make a PR remains part of the session context. This authorizes
publication of the study, not detector design approval.

Assistant outcomes: require both hits in the same module; distinguish ODD
sandwiches, ITk common cooled supports and CMS momentum-trigger pairs; expose
plane separation, inactive row seams and occupied support space from the start.
No raw conversations, private model state or chain-of-thought are retained.

## Decisions and outcomes

Added DRAFT DES-008 and a NumPy analytical PROTOTYPE. Compared seven layouts in
a provisional 700–1100 mm annulus, at 40 mrad relative stereo and 5 mm sensor
mid-plane separation. Three continuous-strip six-ring candidates have zero
sampled pair gaps and zero intersecting trial bodies on two grids and three
straight-ray vertex fixtures. The 402-pair 96 mm square is a conditional geometric
working candidate; 358-pair wedges use six outline types and about 2.6% less
silicon. This does not qualify ~96–100 mm strip electronics or occupancy.

Retained failures: split-square row seams; twelve-ring shorter modules;
fourteen-ring mounting conflicts; five-ring square coverage losses. The gap
scan distinguishes internal cooling-stack failure at 1.8/4 mm from occupied
body collisions at 6.6/10 mm with fixed 8 mm stagger spacing. PR21's 3 mm spacing
and enlarged mounting tabs are explicit collision controls. Neither projection
coverage nor two unassociated sensor hits establishes a usable stereo pair.

Kept all geometry isolated. No production XML, reconstruction, material mixture,
geometry envelope, accepted evidence or human approval was changed. Updated
TRK-LSTRIP as active with next actions, DES-008 and its evidence; other ongoing
work stays unchanged. Source facts are pinned ODD and locally hash-verified
ATLAS/CMS TDR passages with precise locators, separated from unsigned choices.
Live CDS records returned a challenge; local/public byte equality is not claimed.

## Commands and validation

Relevant reads: `gh pr view 21`, `gh issue view 20`, `git fetch origin main
research/short-strip-modules`, and `git show` at the pinned short-strip revision.
Local TDR selected text and SHA-256 were read with the existing reference venv;
no ACTS Spack runtime or installed DD4hep/Geant4 source was used.

The retained JSON supplies full inputs, code hashes, starting revision/dirty
state, numerical epsilon and package versions. The initial exploratory run used
250×720 samples; final evidence repeats at 500×1440 and retains all failing
candidate classes. Coarse 100×360 parameter scans alias narrow row seams;
no convergence of seam inefficiency or continuous coverage proof is claimed.

Actual checks: 9 long-strip tests, 27 dashboard tests, 32 logging tests and 14
JavaScript assertions passed. Dashboard validation and build passed. Dashboard
unit tests ran unchanged in a temporary full-history clone with the curated
working files overlaid, avoiding the ignored large reference cache. Source/input
hashes match the report; both SVGs parse and the ring overview was visually
inspected. The first figure run warned about font-cache paths but exited zero;
the retained final command sets both temporary Matplotlib and XDG cache paths.
The first staged whitespace check found a trailing blank line in the copied
geometry helper; it was removed and the study rerun to keep its source hash
accurate. The paired JSON contains commands and results. Detector runtime, curved-track,
material, electronics, thermal and mechanical validation were not run.

## Changes and revision links

See the paired JSON changed-file inventory: DES-008, report/JSON, two figures,
`tools/long_strip/`, source manifest and reading guides, docs index, tracking
register and this session pair. Result commits and PR link are added after they
exist. PR21/DES-007 is a comparison reference, not a dependency merged here.

## Token accounting

No exact completed-turn usage is exposed for this active task. `usage: []` means
unknown, not zero. No estimate, cumulative total, duplicated observation or
private client archive was entered. This task does not redo the earlier historical
recovery. The observed repository summary at this point contains 98,045,726 input
and 477,200 output tokens from 67 earlier turns in 38 records; 5 of 43 records
have no observations, including this task. Those historical totals are not
attributed to this task. Its missing turn usage can be imported later when exact disjoint
completed-turn counters are available.

## Follow-up

Human review is needed for sensor/readout length, pitch, noise and occupancy;
engineered supports, cooling routes, bond and mounting clearances; subsystem
interfaces and barrel reuse; converged mask/edge studies and pair ambiguity.
DES-008 remains DRAFT and TRK-LSTRIP remains active. A PR merge must not be
interpreted as design sign-off or scientific acceptance.
