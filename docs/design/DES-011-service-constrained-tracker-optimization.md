# DES-011 — Service-constrained tracker placement study

- Status: DRAFT
- Created: 2026-09-29
- Scope: **PROTOTYPE; no production geometry or design sign-off**
- Human owner and numerical approvers: unassigned
- Direction: [PR #25 expert comment](https://github.com/asalzburger/nodd/pull/25#issuecomment-5891018641)
  at observed head `9b5b7f2aa14ad38434480c29666187aa893b73d3`.
- Governing inputs: [DES-010](DES-010-tracker-service-corridors.md),
  [DES-009](DES-009-module-populated-layouts.md),
  [DES-006](DES-006-first-tracker-layouts.md),
  [ADR-006](../decisions/ADR-006-global-envelope-and-field-hypotheses.md).

## Authority and scope

The expert requests new placements and mockups under the following constraints.
This separate follow-up preserves PR #25's original service reservations and
evidence. PR #24 remains an unapproved working hypothesis. The comment directs
an exploration; it does not approve its numerical outcome, material model,
mechanical feasibility or full-detector integration.

## Requirements and numerical classification

Every new parameter below is **NODD DESIGN CHOICE**. Reviewer-directed constraints
are identified separately from algorithm choices proposed by Codex; neither
constitutes human sign-off of a resulting layout. Sensor facts and service-load
inputs retain the classifications and public sources in DES-009/010.

| ID | Constraint / method | Origin and consequence |
| --- | --- | --- |
| SO-C01 | Minimum 10 mm between the occupied barrel end and the first endcap; move the first disc as close as the service/support constraints permit | Explicit expert direction. Measure physical body/support extents, not nominal sensor-centre separation. A bundle that needs more space must retain it. |
| SO-C02 | Constant-width subsystem service corridors along the endcaps | Explicit expert direction for simpler mechanics. No progressive taper is introduced. Size against the maximum traffic actually carried by that route. |
| SO-C03 | Compare including the final endcap in its subsystem trunk with a separate downstream extraction | Expert suggestion, conditional on an explicit connected bypass. Final-disc power/data/cooling must still reach the common exit and remain in its downstream budget. |
| SO-C04 | Repopulate finite modules after changes to layer radii, disc positions or radial ranges | Explicit request to recover covered area. Preserve sensor/module shapes, placement policies and layer counts; report both active and physical silicon areas. Regenerated identifiers are candidate-local. |
| SO-C05 | Seek more reached stations and smaller gaps between successive measurements | Explicit expert objective. Evaluate physical path distances for straight tracks and both charges at pT=1 GeV in a constant 3 T field. Stereo faces of one module are not separate stations. |
| SO-C06 | Keep luminous x/y in [0,1] mm, z in [-150,150] mm and eta in [-4,4] | Retain the original study domain. Reuse identical samples across candidates, plus an independent holdout seed. These are sampled coverage estimates, not proofs of continuum hermeticity. |
| SO-C07 | Preserve host/interface limits, local supports, complete service inventory and finite route/throat checks | Retain DES-010 physical constraints. Reference capacity is a conditional architecture test; adverse scenarios must remain visible. No narrower passage is qualified solely by an area calculation. |
| SO-C08 | Use a bounded, deterministic candidate search and retain every candidate's parameters and rejection reason | Proposed repeatability policy. Report best tested candidates and tradeoffs, not a global optimum. Input/model/source hashes, seeds and commands accompany evidence. |
| SO-C09 | Keep the original cobe ideal layers as an additional fixed coverage denominator | Proposed anti-bias control. Moving or shrinking a layer must not erase the original missing-hit requirement. Also report candidate-local ideal coverage and actual reached hits. |
| SO-C10 | Report inter-station gaps together with origin/host-boundary gaps and hit counts | Proposed anti-bias control. Losing measurements must not improve a spacing score by dropping undefined gaps. Cases with fewer than two stations have no inter-station-gap statistic. |

The search configuration will state finite parameter ranges, sample sizes,
ranking and capacity margins before retained execution. These are reproducible
study settings, not sourced detector dimensions. First/last pixel radii and the
outer tracking lever arm must not be silently sacrificed for a scalar score.

## Bounded search protocol

**SO-C11 — NODD DESIGN CHOICE, proposed:** the
[configuration](../../tools/module_layout/optimization_config.json) scans pixel
trunk inner radii 170/190/210 mm and short-strip trunk inner radii 640/680/720 mm,
with the long-strip trunk starting at 1144 mm. The three disc schedules retain
the last disc positions and distribute intermediate discs using the inherited
fractions, equal intervals or a power-law exponent of 1.25. The first disc is
placed at the finite-body/service lower bound. Compare both final-disc routing
topologies. A second pass shifts four intermediate barrel radii by ±10 mm,
retaining the inner two pixel radii and the outermost tracking radius.

**SO-C12 — NODD DESIGN CHOICE, proposed:** derive the constant trunk, barrel-turn,
collector and joining-pocket dimensions from each repopulated inventory, using
the reference packing architecture with a demand factor of 1.1 and dimensions
rounded upwards to whole millimetres. Retain all adverse budget outcomes.
The compact-pocket study uses a 10 mm floor for barrel and disc routing pockets;
this is an **unqualified space hypothesis**, not a sourced bend radius or proof
that connectors fit. Compare the winning geometry with the original DES-010
50/80/90 mm barrel and 50/90/90 mm disc pocket floors. The final common exit may
start at r=1040 mm within the existing proposed bore envelope; outer radius
1220 mm and the 3555–3645 mm exit window remain fixed. No new global allocation
is made. Every enlarged overlap is shown and checked explicitly.

**SO-C13 — NODD DESIGN CHOICE, proposed:** train on 17×8 angular grid points at
three luminous z positions, a 9×4 grid at all luminous corners, and 256 random
directions (seed 202609291), separately for straight and both charged modes.
Rank only physically feasible candidates that do not lower any subsystem's mean
station count in any mode relative to the PR #25 control. Retain separate best
tested coverage, inter-station spacing and active-area candidates. Coverage rank
first maximizes the worst-mode mean station count; it does not claim a continuum
minimum or detector resolution optimum.

Freeze that selection before a denser 41×32 central / 21×16 luminous-corner grid
and 4096 independent random directions (seed 202609292). The holdout's grids share
some training angles; only its random cohort is statistically independent. Report
holdout performance without reranking, and use native ACTS on a seeded sample
plus adverse trajectories. Separately record candidate-local ideal misses and
fixed-original-layer misses; neither replaces actual reached-station counts.

**SO-C14 — NODD DESIGN CHOICE, proposed:** also compare long-strip barrel nominal
half-lengths 1350 and 1400 mm. The unchanged endpoint-filling policy generates
24 and 25 rows, respectively. With 25 rows, the central row is assigned to the
positive end; 13 modules per positive half-stave exceed the inherited 12-module
harness ceiling and require two harnesses there. The 24-row option has 12 on
each end. This is an explicit geometry/electrical tradeoff, not a change to the
harness architecture or an omission of central modules. Compare both under the
same finite-body clearance, exit-capacity and hit-coverage constraints.

**SO-C15 — NODD DESIGN CHOICE, proposed:** refill pixel endcaps down to a physical
body radius of 27 mm (25 mm host plus 2 mm allowance), compared with the original
29.7 mm body minimum. Refill long-strip endcaps up to a body radius of 1138 mm
(1140 mm host minus 2 mm). These are candidate body bounds, not redefinitions of
the original ideal-layer denominator or approved beam-pipe interfaces.

## Validation contract

Validate deterministic regeneration; full module/body/support clearance; tracker
host and conditional vessel-interface bounds; every declared service connection
and traffic partition; reference and adverse route/throat capacities; minimum
barrel/disc clearance; sensor area/counts; coverage and path gaps in total and by
subdetector. Validate selected changed layouts against the installed ACTS
finite-patch propagation workflow. Ideal-layer covariance tools, if used, remain
secondary diagnostics and cannot replace finite-module coverage.

Preserve original numerical/native evidence. Failed candidates and inaccessible
capabilities remain explicit. Report source/input/runtime versions, commands and
tolerances. New mockups show bodies, support reservations, service corridors and
conditional downstream paths at scale.

## Open engineering questions

Unqualified connector/bend footprints, cooling hydraulics, structural attachments,
electrical architecture, service material and vessel access from DES-010 remain
open. The search can demonstrate geometric and sampled-coverage tradeoffs under
those assumptions; it cannot confer engineering or performance acceptance.
