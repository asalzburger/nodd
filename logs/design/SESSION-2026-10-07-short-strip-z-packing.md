# SESSION-2026-10-07-short-strip-z-packing — PR49 longitudinal packing review

## Scope and evidence

Contemporaneous bounded review response on `codex/short-strip-barrel`, starting
from clean0f1ac4c622546535396d95c145d11fccf8b01755. The existing barrel checkout
belongs to PR50; a separate worktree `nodd-short-strip-z-packing` reuses PR49's
branch and preserves both later prototype branches. DES-020 stays DRAFT.

## Selected conversation

User, exact: “PR #49 has a comment to address”. The public
[comment](https://github.com/asalzburger/nodd/pull/49#issuecomment-6030478624)
asks for “information (and a drawing) about the packing along z for the prototypes”.
The requested deliverable is documentation/drawing of the current layouts.

## Decisions and outcomes

Derive both axial schedules from pinned inputs, frozen row placements and fresh
compact export; measure passive occupied bounds rather than drawing just active
rectangles. Both prototypes share28 rows,85⅓mm pitch,10⅔mm active projected
overlap,1.5mm alternating local-normal lifts,0.5mm front-stack gap and64mm
pickups with1⅚mm neighbouring-body axial clearance. Active union2400mm versus
2688mm summed length gives288mm duplicated,10.7143% of summed axial length,
not a whole-barrel overlap-area or track-hermeticity fraction.

The figure compares complete schedules and details z=0 and the occupied
barrel-end ledger, including independent cooling returns, all nine bearings,
5mm support-to-board gap,11.5mm front-body-to-board gap and the old1295.5mm disc
inside the collector. Normal scale/projection and ledger conventions are explicit.
Source/native hashes, layouts/IDs, engineering/coverage failures and unsigned
prototype lifecycle are preserved. New inference SB-I04 records provenance.

## Commands and validation

The paired JSON retains commands and actual results. Read applicable AGENTS.md,
PROJECT.md, logs/README.md, DES-020, tool/tracking workflows and linked issue20.
The first network sandbox read failed, then authorized GitHub reading succeeded.
The first new bounds calculation exhausted a generator; materializing it fixed
the helper. Visual inspection found that layer-cylinder rings use global w,
not stave-local v; correcting this produced all nine actual bearing stations.
Initial preservation check included the intentionally amended README; the
corrected check excludes only that file. These attempts are retained, not
scientific failures or changed native geometry.

The existing ten barrel controls passed. New report compares every frozen axial
row/identity/lift/axis in both prototypes, checks repeated schedules and equal
axial quantities, and records exact input/layout/producer/factory/compact/figure
hashes. New PNG renderings were visually inspected, with the final active
silicon drawn visibly above peripheral guards in projection. Native/Geant4
runtime was not used; no native/coverage rerun is claimed.

## Changes and revision links

Design SB-I04, new z-packing report/JSON, SVG/PNG, reproduction helper/README,
tracking evidence and this session pair. Existing historical reports, source
producers and drawings are byte-preserved. Publication/result commits are added
only after they exist; actual new drawing execution remains dirty0f1ac4c plus
the recorded exact hashes. No external review comment or Slack message is sent.

## Token accounting

This new implementation turn is active; final disjoint client counters and exact
turn boundaries are not available yet. Usage stays empty, not zero; no partial
import, estimates, duplicated older observations or new accounting automation.
Execution model/client version remain unknown. Logger summary reports only
previous observations; older project coverage remains partial and no total
includes this active turn or establishes all-project completeness.

## Follow-up

Review the axial description/drawing in PR49. Existing end-boundary coverage,
collector mean-fill and adverse thermal/data/service gates remain unresolved;
mechanical/CTE, seating/joints and connected services need qualification before
integration. No human approval or sign-off is inferred.

Pre-publication logger validated115 records; summary observes90 older turns in53
of115 sessions (input217035315, output1272392, total218307707). This is partial
coverage and excludes this active turn. Dashboard47 tasks/26 documents/19
review rounds validated/built. Working-tree and full start/main-relative diff
checks passed.
