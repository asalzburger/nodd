# SESSION-2026-09-25-long-strip-layout-compatibility — PR13 A/C1 interface correction

## Scope and selected request

User, exact quote: “Make sure the inner radius of the long strips is compatible
with the proposed 2 layouts of PR#13, adapt the number of rings if necessary”.
This is a new bounded follow-up to the initial DES-008 investigation. Branch
`research/long-strip-modules`, starting at
`68932692fc61bb25d21e55a915a12eb929b2b316`. The pre-existing untracked tracker-layout
bytecode was preserved. No subagents were used and no raw/private client state
was collected.

Read repository instructions, PROJECT, relevant design/report/test files, and the
PR13 A/C1 briefs, expert response and exact reviewed layouts. Fetched PR13 branch
and pinned its head `f57e26e83b826867c2720edcd702e808fe946854`; layout bytes equal
the reviewed evidence target `06275ecf55e4bb428ffbdb1d5beb72c9a7aca064`.

## Outcome and rationale

Both active A/C1 proposals use long-strip disks at r=710–1100 mm and
|z|=1430,1800,2120,2450,2730,3120 mm. Their long-strip barrels are at 840/1060 mm
with 1400 mm half-length; C1 tilts only short-strip barrel ends. Corrected the
DES-008 target from 700 to 710 mm and first-disk plane from 1320 to 1430 mm.
The old evidence remains in Git at the starting revision; no accepted evidence
or production geometry was overwritten or reinterpreted as approved.

Retained six square-module rings, recomputing centre radii and even azimuthal
counts: 404 pairs/disk, versus 402 before. Five rings lose pair coverage at the
first three disks (worst 1.0914%); six rings have no missed pairs on either grid
or in the direct inner/outer-boundary scans. A possible five-ring rear-disk
variant remains outside the selected common arrangement. The full seven-candidate
comparison was regenerated as well.

Compatibility has an explicit limit: the 710 mm target is at the reference plane,
while active outlines extend inward to 693.85 mm and trial bodies to 687.55 mm.
The nominal 10 mm radial service corridor is not clear. Using PR21's 11 mm
short-strip trial depth, the nearest short/long disk body envelopes retain
18.85 mm axial separation. The first disk has 14.35 mm to the ideal barrel end;
the last has 14.35 mm to the host end. Real shared carriers, barrel-end structures
and services remain unmodeled; no engineering clearance or sign-off is claimed.

## Validation and provenance

Executed 14 geometry/layout tests, 27 dashboard tests and 32 logging tests, all
passing. Dashboard validation and build passed. Dashboard tests used an unchanged
temporary full-history clone with the curated working tree overlaid to exclude
large ignored reference caches. The main study used 250×720 and 500×1440 polar
midpoint grids, three vertex fixtures and retained failed controls. Compatibility
also enumerated every module at 1440 azimuths directly on each target boundary:
all 18 disk/vertex cases have zero misses. Mirrored disk/stack/vertex ray factors
are identical and tested explicitly; no independent negative-side assembly is
assumed. Zero samples are not a continuous-coverage proof.

PR13's source-file hash and every curated signed layer field were verified against
Git. Both output files' input/code hashes match. The updated ring figure was
rendered and visually inspected. Precise commands/results are in the paired JSON.
The source catalogue's public detector facts are unchanged; this adds pinned
internal-design provenance in `pr13-layouts.json` and DES-008 C11. No full detector,
material, electrical, thermal or reconstruction test was run.

## Changed files and publication

Updated DES-008, its default inputs, comparison report/JSON/figure, README and
TRK-LSTRIP tracking. Added the pinned PR13 geometry extraction, compatibility
script/tests and report/JSON, and this session pair. The paired JSON contains the
exact changed-file inventory. The amendment belongs to existing
[PR22](https://github.com/asalzburger/nodd/pull/22); Git history locates its result
commit. PR13 itself and its human review state remain unchanged.

## Token accounting and follow-up

Exact completed-turn counters for this task are not exposed; `usage: []` means
unknown, not zero. The repository summary observes 98,045,726 input and 477,200
output tokens from 67 earlier turns in 38 records; 6 of 44 records have no
observations, including this task. These historical totals are not allocated to
this task. No token estimates, duplicates or cumulative counters were entered.

Human review remains necessary for strip readout/occupancy, actual support/service
clearances and barrel-end integration. DES-008 is DRAFT and TRK-LSTRIP remains
active; no approval follows from this compatibility check or a PR merge.
