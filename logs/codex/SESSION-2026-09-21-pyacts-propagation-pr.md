# SESSION-2026-09-21-pyacts-propagation-pr — Propagation view and review PR

## Scope and selected request

User request (exact): “Please create a PR, if possible add x-y view of the intersection with the surfaces. This can be done using the Propagation example wit step writing enabled.”

Starting revision and branch are recorded in the paired JSON. Prior pyacts
assessment commit fb45621 is included in the requested PR. Existing untracked
tracker bytecode is preserved and excluded. No token measurements or exact
conversation start time are exposed; usage is unobserved, not zero.

## Decisions and outcomes

Used the release-pinned ACTS propagation-example sequence with the existing
module blueprint fixture, EigenStepper/Navigator and sterileLogger=False.
ROOT step writing is unavailable in this wheel, so the included OBJ step writer
provides real written positions/connectivity. No custom writer or ACTS rebuild
was required. Read-only GitHub source calls used the user's standing permission;
network failures were retried with authorized access.

The central x-y figure shows 48 negative muons from the origin in each synthetic
0/2 T field, eta=0, pT=0.1 GeV, seed42, maximum step2 mm. Barrel modules are drawn
as finite plane intersections; endcaps remain in the geometry but lie outside
the slice. Every generated track has a written path and reaches the boundary.
Independent straight/circular trajectories and finite-plane intersection sets
match all 96 propagations. There are 34/30 intersections and 2744/2959 steps.
OBJ lacks surface IDs; plotted markers are actual steps geometrically associated
with module planes, not fabricated segment intersections or simulated hits.

The writer's six-significant-digit coordinates motivate numerical tolerances
of 0.001 mm for planes/trajectories and 0.002 mm for intersection positions.
These do not set detector alignment or performance requirements. Constant field
and low momentum are visualization controls, not nODD design selections.

## Commands and validation

The paired JSON records actual commands, results, unavailable ROOT writer and
relevant checks. Raw OBJ/particle CSV stay in ignored cache; execution report
retains hashes, intersections, tool versions and settings. The figure was
visually inspected. Source/figure hashes and generated particle denominators
make the demonstration reproducible. The initial Matplotlib font-cache warnings
were resolved by using a writable local cache.

## Changed files and provenance

Added propagation runner, plot dependency pin, retained figure/report; updated
the assessment, reproduction guide, source catalogue and dashboard. This pair
records the bounded follow-up. SRC-PYACTS-4770-BINDINGS now includes pinned
propagation example, algorithm and OBJ-writer references. Git history locates
the eventual commits; no human approval or sign-off is recorded.

## Follow-up

Published [PR #14](https://github.com/asalzburger/nodd/pull/14) with an executive
summary, immutable embedded figure and review requested from asalzburger-review.
The exact evidence revision is d8f5dd69a0a4c3a74ef09239d186b79f5a5160c2; the
subsequent metadata commit only reconciles the project/session registers. All
40 local tests, dashboard build/validation, retained hashes and whitespace checks
passed. GitHub dashboard CI was queued at publication; no human approval is
implied. Initial staging/commit sandbox denials were retried with authorized Git
permissions before publishing the complete PR.

Physical
module conversion, field maps, material response, acceptance and reconstruction
remain open. The unrelated tracker-layout proposals in PR #13 remain on hold.
