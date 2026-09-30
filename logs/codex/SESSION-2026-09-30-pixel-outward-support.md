# SESSION-2026-09-30-pixel-outward-support

- Date: 2026-09-30; contemporaneous curated record.
- Starting branch/revision: `design/pixel-barrel-support`, `f0ebdc4707aded2c0b774f73d2bf87409f1fce71`.
- Scope: DES-002, DES-010, DES-011; update draft PR #29.
- Four unrelated historical usage-summary files were present initially and remain untouched.

## Selected request

The user asked for candidate A with sensors facing inward and stave material
radially outward: an individual x–y drawing of each fully mounted barrel and a
combined view, motivated by tracking performance.

## Outcome and decisions

Added proposed PS-C11/C12 to DES-002 before implementing an isolated drawing
workflow. Generated B1/B2/B3/B4 and combined sections, each PNG/PDF/SVG. Used an
actual z = +25 mm cut with all 82 staves and 164 cooling tubes. Every module and
active-plane transform stays at its exact selected PR28-baseline value. The
1 mm module envelope is not an internally resolved sensor/ASIC stack; the
inward-facing sensor direction does not move the mathematical sensitive planes.

The drawing uses a true aspect ratio and inset stave details. Nominal radii are
dotted; B4/the combined view show the projected r = 190 mm trunk boundary dashed.
The trunk starts at |z| = 555 mm and does not occupy this cut. The section is between
bearing planes; global rings, frame, flex, end joints and connectors are not
represented as completed engineering. All five final PNGs were visually reviewed.
The first export footer overlapped the x-axis label; spacing was corrected and
all exports regenerated before publication.

No nominal support/body or support/support box intersections were found. The
minimum support-to-other-module gap is 1.070735 mm in B2. B4 reaches 189.482640 mm,
leaving 0.517360 mm radial headroom to the projected trunk. This is not a joint or
assembly tolerance allowance. Earlier inward annular reservations do not contain
this outward orientation. Its global bearings and service interface require
review; the earlier inward illustrative rib mass is not transferred.

The original inward evidence and all 12 producer/artifact hashes remain unchanged;
20 new hashes cover the outward artifacts and producers. Existing public
literature entries are reused; no new external source fact was introduced. The
new orientation and section convention are proposed design choices; clearance
values are PS-I06 inferences with explicit limits. No production geometry,
tracking simulation, thermal/hydraulic/FEA result or engineering approval added.

## Reproduction and checks

```sh
MPLCONFIGDIR=/tmp/nodd-des002-mpl python3 -B tools/pixel_support/outward.py
python3 -B -m unittest discover -s tools/pixel_support -p 'test_*.py' -v
python3 -B tools/dashboard/build.py validate
python3 -B tools/dashboard/build.py build --output /tmp/nodd-des002-outward-dashboard
python3 -B -m unittest discover -s tools/dashboard -p 'test_*.py' -v
python3 tools/session_logging/session_log.py validate
python3 tools/session_logging/session_log.py summary --format json
git diff --check
```

The focused support suite passes all 8 tests, including fixed inputs, correct
outward orientation, tube containment, invalid-cut and nonuniform-column
rejection, full-width collision control and analytic rotated-box distances.
Dashboard records validate (33 tasks / 13 documents / 13 review rounds) and build succeeds.
The paired JSON records actual outcomes, changed files and subsequent publication.

## Accounting and open review

Exact client-reported per-turn token counters are unavailable for this task;
`usage` is empty. Historical project totals are not attributed to this work.
One bounded drawing request was handled; this is not a reconstructed count of
all human/client interactions. No subagents were used for this task.

Human engineering review remains necessary for the outward envelope, global
load path, end fitting clearance and material/thermal/mechanical qualification.
Tracking benefit has not been quantified. The user direction is not recorded as
production sign-off.

## Check corrections

The dashboard suite ran 27 tests with one temporary-directory cleanup error
(macOS OSError 66, directory not empty), after the affected assertions. The
individual test passed, including cleanup, on a targeted rerun; no tests or
tolerances were changed. The first staged whitespace check exposed Matplotlib
SVG trailing spaces not visible to the earlier check of tracked files. The
generator now strips trailing spaces before hashing. Both artifact manifests
verify and all 5 normalized SVGs parse. Earlier inward evidence stays unchanged.

The local usage summary observes 134594309 input and 674111 output tokens over
79 historical turns in 42 sessions; 22 sessions lack observations, including this
task. These are incomplete historical project totals, not usage for this task.

## Publication

Committed and pushed `ce913fe503a2f83cc7f62aa0680806a7d7fa8b10` to draft [PR #29](https://github.com/asalzburger/nodd/pull/29). Updated its description and posted a summary with exact-revision drawing links. The final staged whitespace check passes. No merge or sign-off.

PR summary: https://github.com/asalzburger/nodd/pull/29#issuecomment-5910242885. Post-publication dashboard build and log validation/summary passed. GitHub build was in progress when observed at the drawing commit; no remote success is claimed.
