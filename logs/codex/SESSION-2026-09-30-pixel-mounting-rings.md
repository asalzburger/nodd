# SESSION-2026-09-30-pixel-mounting-rings

- Date: 2026-09-30; contemporaneous curated record.
- Starting branch: `design/pixel-barrel-support`.
- Starting revision: `e35d8b79d84d7acc480cb9fc95ddb13c435cb1d0`.
- Related: DES-002, DES-010, DES-011, REVIEW-DES-002-1, PR #29.
- Four pre-existing untracked historical usage files were preserved unchanged.

## Selected request and review

The user asked to address the new PR comment. The human reviewer
`asalzburger-review` confirmed that the earlier x–y drawing matched the request,
then asked whether mounting rings were needed, how many and where, with updated
x–y and barrel |r|–z drawings:
https://github.com/asalzburger/nodd/pull/29#issuecomment-5910690174.

The review record targets the PR head observed at collection; the issue comment
itself did not specify a SHA. Approval of the requested drawing style is not
recorded as engineering approval, sign-off or acceptance of the geometry.

## Outcome and rationale

Added DES-002 PS-C13/C14 before implementing the isolated mounting overlay.
Propose six rings per barrel, 24 total: end mounting rings at z = ±546 mm and
intermediate stiffening rings at ±330 and ±110 mm. Their 8 mm axial width occupies
|z| = 542–550 mm at the ends, leaving 5 mm before the barrel service bay. The
maximum station pitch is 220 mm. This revises the earlier illustrative
±560/±336/±112 mm outward-A stations; the original evidence is preserved.

Ring radial depth remains the earlier proposed 1 mm. Inner radii sit 0.5 mm
beyond each stave assembly's largest corner radius. All 82 staves attach via
4 mm tangential by 8 mm axial foot envelopes of stagger-dependent height at each
station, giving 492 feet. One axial locating station is proposed at −546 mm;
the remaining guides permit longitudinal thermal movement. Fasteners, split-ring
joints, adhesive and global end mounts remain unresolved.

The rings tie the staves together but do not create independently grounded
short-span beam supports. Full cage/end-mount stiffness and thermal deformation
remain to be established; no short-span sag, minimum ring count or tracking
performance is claimed achieved. IBL section 7.3 provides a public support-ring
and central-foot precedent while also documenting remaining motion/distortion.

Generated four individual and one combined x–y section at z = +110 mm, plus a
combined |r|–z projection with a B4 end detail, all in PNG/PDF/SVG. The prior
z = +25 mm view remains valid between rings. No module/active-plane position or
production geometry changed. All six drawings were visually inspected; the
initial r–z subtitle was corrected from “inside” to “clear of” the service bays.

The nominal ring/foot overlay has zero reported intersections with module bodies,
stave boxes, other rings/feet, original support reservations and reserved routes.
B4's outer ring radius is 190.983 mm, beyond the projected 190 mm trunk boundary,
but its finite axial placement avoids the actual trunk beginning at |z| = 555 mm.
The 5 mm axial separation is not a tolerance or joint-installation qualification.
Rings contribute 217.69 g and solid CFRP foot envelopes 81.14 g, before joint and
global-mount hardware; material does not disappear into an unspecified support.

## Literature and provenance

Checked public arXiv HTML and the existing cached IBL production PDF, §7.3,
printed/PDF p. 75. Text extraction and rendered-page inspection agree. The web
PDF fetch exceeded the fetcher's size limit; public HTML and the existing
hash-catalogued local PDF supplied the source. Expanded the existing
SRC-ATLAS-IBL-PRODUCTION-2018 entry with PS-F07; no PDF committed. Ring dimensions,
counts, constraints and locations remain nODD design choices. Envelope/mass
calculations are PS-I07/I08 inferences, not literature measurements.

All original 12 inward hashes and 20 between-ring outward hashes still verify.
The new manifest verifies 25 producer/artifact hashes; all six SVGs parse.
The machine-readable report records the exact baseline, source hashes, command,
Python/NumPy/Matplotlib versions and numerical tolerances. No ACTS, DD4hep,
Geant4, FEA or hydraulic solver was invoked.

## Commands and actual checks

```sh
MPLCONFIGDIR=/tmp/nodd-des002-mpl python3 -B tools/pixel_support/mounting.py
python3 -B -m unittest discover -s tools/pixel_support -p 'test_*.py' -v
python3 -B tools/dashboard/build.py validate
python3 -B tools/dashboard/build.py build --output /tmp/nodd-des002-mounted-dashboard
python3 -B -m unittest discover -s tools/dashboard -p 'test_*.py' -k deterministic_escaped_build_and_all_internal_links -v
python3 tools/session_logging/session_log.py validate
python3 tools/session_logging/session_log.py summary --format json
```

All 12 support tests pass. Controls preserve the baseline and inventory, detect
a deliberately misplaced B4 ring in the service bay, reject old end locations
outside the stave and oversized feet, and compare curved-foot mass with independent
numerical integration. The dashboard/link/deterministic-build test passes;
33 tasks, 13 documents and 14 review rounds validate and the dashboard builds.
Final logging and publication outcomes are recorded in the paired JSON.

## Accounting and remaining review

Exact client-reported per-turn token counters are unavailable; usage is empty,
not zero. Historical observed project totals must not be attributed to this task.
One user request initiated this bounded review response; no subagents were used.

Human engineering review remains pending for ring count, constraint scheme,
complete cage stiffness, global mounting interfaces and joint material. The
updated drawing proposal does not grant production authorization.

The local accounting summary observes 134,594,309 input and 674,111 output tokens
over 79 historical turns in 42 sessions; 23 sessions lack usage measurements,
including this task. These incomplete project totals are not this task’s usage.

## Publication

Committed and pushed `9b916d7ad7dcfa013a8673f2c394069ebdedbdfd` to draft PR #29. Updated the PR description and
replied directly to the mounting-ring request with immutable drawing/report
links. The final staged whitespace check passes. No merge or sign-off.

Reply: https://github.com/asalzburger/nodd/pull/29#issuecomment-5911114398. Post-publication dashboard build and log validation/summary pass.
GitHub build was in progress when observed at the drawing commit; remote success
is not claimed. The reviewer’s acceptance of the response remains pending.
