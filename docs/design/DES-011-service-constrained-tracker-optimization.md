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

## Working baseline selected on 2026-09-30

**SO-C19 — NODD DESIGN CHOICE, selected by explicit human instruction:** use
`p190-s680-b1-l1287.33-front_loaded-original-pockets` as the new tracker working baseline for subsequent
support, service and layout studies. The user confirmed the recommendation:

> Ok, we take the recommendation as the new baseline, record that and update the PR accordingly.

The [decision record](../../logs/codex/SESSION-2026-09-30-baseline-selection.md)
retains the instruction and its scope. This selects a working baseline; DES-011
remains DRAFT/PROTOTYPE and does not gain formal engineering sign-off or production
integration authorization. The historical PR #24 layout remains unapproved;
this explicit choice supplies the new baseline for future studies.

The exact selected geometry is the [retained original-pocket layout](../validation/DES-011-optimization/cases/p190-s680-b1-l1287.33-front_loaded-original-pockets/layout.json.gz)
at evidence revision `17ae47f6d18e132eb539f30ef8323114963f8588`, produced with numerical
source `ac61f766b34f9bb60748e8fc4258a41037ca1e33`. Its compressed-file SHA-256 is
`89ce39dae6af7e1e69d40582a6c49e6e7f26dbcd6ce1dd3cc061e41e75419cbd`.
The historical case name remains unchanged for reproducibility.

| Selected feature | Pixels / short strips / long strips, unless stated otherwise |
| --- | --- |
| Barrel radii, mm | 34/60/106/182; 260/340/480/660; 840/1060 |
| Long-strip barrel | 23 rows, inherited 112.6666667 mm pitch, central row retained; nominal half-length 1287.3333333 mm |
| Disc schedule | Front-loaded, with positive first-disc centres 611.7 / 1295.5 / 1403.65 mm |
| Constant service trunks, mm | 44 / 73 / 25 |
| Original routing-pocket floors, mm | Barrel: 50 / 80 / 90; disc: 50 / 90 / 90; actual envelopes remain those in the retained geometry |
| Final-disc routing | Tested downstream bypass retained, with complete downstream inventory |
| Module placements | Inherited sensor families, staggering and local tilts; no inclined barrel section; existing 12-degree long-strip local module tilt retained |

Rationale: with silicon area no longer a driving concern, retain service space
and measured local coverage for only a 0.64% mean-station reduction relative to
the compact coverage candidate. The selected case has 197.250 m² physical silicon,
9.0182 mean usable stations and a 1009.57 mm worst-mode p95 maximum inter-station
gap. It has no increased zero-hit fractions in the measured structured/random
eta bins relative to PR #25. These are sampled results, not continuum hermeticity
or tracking-resolution guarantees. See the [comparison](../validation/DES-011-service-constrained-optimization.md).

Next work prioritizes connector/bend envelopes, support/cooling interfaces,
service material, vessel access and local coverage weaknesses. Conservative/stress
capacity scenarios remain failures. Removing the final-disc bypass is a separate
simplification study requiring matched dense/native validation before adoption;
its training-only comparison does not change this selected baseline. The
numerical studies and their frozen training rankings remain unchanged.

## Requirements and numerical classification

Study settings below are **NODD DESIGN CHOICE** unless explicitly classified
**INFERENCE** for a derived geometric bound. Reviewer-directed constraints
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
retaining the inner two pixel radii and the outermost tracking radius. Its seed
must pass physical constraints, subsystem means and the strict central guard;
it may still fail another angular stratum. Radius exploration can repair such a
seam. The seed is not a finalist: all final roles require the complete SO-C16
guard. This distinction was frozen after the 1300 mm development probe exposed
a fully blind straight eta=-0.5, vertex-z=+150 mm stratum in unshifted barrels.

**SO-C12 — NODD DESIGN CHOICE, proposed:** derive the constant trunk, barrel-turn,
collector and joining-pocket dimensions from each repopulated inventory, using
the reference packing architecture with a demand factor of 1.1 and dimensions
rounded upwards to whole millimetres. Retain all adverse budget outcomes.
The compact-pocket study uses a 10 mm floor for barrel and disc routing pockets;
this is an **unqualified space hypothesis**, not a sourced bend radius or proof
that connectors fit. Compare the winning geometry with the original DES-010
50/80/90 mm barrel and 50/90/90 mm disc pocket floors. The common rear collector and radial-exit inlet may
start at r=1040 mm within the existing proposed bore envelope; its 1220 mm outer
bore limit and the 3555–3645 mm exit window remain fixed. The downstream radial
handoff still extends to r=1680 mm within the conditional vessel opening. No new global allocation
is made. Every enlarged overlap is shown and checked explicitly.

**SO-C13 — NODD DESIGN CHOICE, proposed:** train on 17×8 angular grid points at
three luminous z positions, a 9×4 grid at all luminous corners, and 256 random
directions (seed 202609291), separately for straight and both charged modes.
Rank only physically feasible candidates that do not lower any subsystem's mean
station count in any mode relative to the PR #25 control and pass SO-C16. Retain separate best
tested coverage, inter-station spacing and active-area candidates. Coverage rank
first maximizes the worst-mode mean station count; it does not claim a continuum
minimum or detector resolution optimum.

Freeze that selection before a denser 41×32 central / 21×16 luminous-corner grid
and 4096 independent random directions (revised seed 202609293). The holdout's grids share
some training angles; only its random cohort is statistically independent. Report
holdout performance without reranking, and use native ACTS on a seeded sample
plus adverse trajectories. Separately record candidate-local ideal misses and
fixed-original-layer misses; neither replaces actual reached-station counts.

**SO-C14 — NODD DESIGN CHOICE, proposed:** also compare long-strip barrel nominal
half-lengths 1287.3333333333333, 1300, 1350 and 1400 mm. The unchanged
endpoint-filling policy generates 23, 23, 24 and 25 rows, respectively.
The first preserves the original PR #25 retained barrel-row pitch: the original
25-row arrangement has pitch (2800−96)/24 = 112.6666667 mm; retaining 23 rows
at that pitch gives nominal half-length (22×pitch+96)/2 = 1287.3333333 mm.
It is a **NODD DESIGN CHOICE** to retain this derived-pitch control, avoiding
unnecessary shifts of existing longitudinal seams; it is not fitted to an eta
sample. The 1300 mm option stretches the same 23 rows to a larger extent. With 25 rows, the central row is assigned to the
positive end; 13 modules per positive half-stave exceed the inherited 12-module
harness ceiling and require two harnesses there. The 24-row option has 12 on
each end but leaves an active seam at z=0. The 23-row option retains the central
row with 12/11 modules per positive/negative half-stave, within the same harness
ceiling. This is an explicit geometry/electrical tradeoff, not a change to the
harness architecture or an omission of central modules. Compare all four under the
same finite-body clearance, exit-capacity and hit-coverage constraints.

**SO-C15 — NODD DESIGN CHOICE, proposed:** refill pixel endcaps down to a physical
body radius of 27 mm (25 mm host plus 2 mm allowance), compared with the original
29.7 mm body minimum. Refill long-strip endcaps up to a body radius of 1138 mm
(1140 mm host minus 2 mm). These are candidate body bounds, not redefinitions of
the original ideal-layer denominator or approved beam-pipe interfaces.

**SO-C16 — NODD DESIGN CHOICE, proposed after an observed failure:** the first
retained run at `6c882257c368927732315dbc756f1b89263d95af` selected 24-row long-strip
barrels. Dense validation exposed a central seam: all 96 straight rays with
eta=0 and vertex z=0 lost both long-strip stations despite improved global means.
Preserve that run as rejected evidence. Before the revised search, add the
23-row alternative and freeze a local guard: the central eta=0/vertex-z=0 cohort
must preserve each subsystem's mean stations and zero-station fraction in every
mode. Across 0.5-wide eta bands at each sampled vertex plane (-150/0/150 mm),
reject any newly completely blind subsystem stratum that was reached in the
baseline. Require identical paired track identities. Report all other local
mean/zero-hit regressions explicitly; this guard does not promise pointwise
non-regression. Bins and zero-loss central rule are diagnostic choices, not
sourced detector specifications. The repeated dense grids now serve regression
testing; use fresh random seed 202609293 for the revised independent cohort.
No sensor, staggering policy or harness limit is changed to repair the seam.
The native sample explicitly includes eight uniformly spread central-grid
azimuths per mode in addition to the seeded/adverse sample; the first run's
native sample contained no eta=0 tracks.

**SO-C17 — INFERENCE, derived necessary fit constraint:** an independent
post-selection audit found that aggregate annular area alone permits passages
thinner than individual round components already charged to the budget. With
the inherited 13.4 mm strip power cable, 12 mm return pipe and 2 mm allowance on
each boundary, the largest known strip item needs 17.4 mm total passage, rounded
to 18 mm. Pixel transport pipes have 4 mm diameter and require 8 mm before any
larger named floor. Values and their original classifications remain in
`services_budget_inputs.json`; the new inequality is a geometric derivation,
not a new cable technology choice or a qualified bend radius.

**SO-C18 — NODD DESIGN CHOICE, proposed enforcement and follow-up:** require
this bound in every routed cross-section and finite joining throat,
using the actual carried component inventory. Size passages to satisfy both
aggregate capacity and known component dimensions. Unknown pixel ancillary
bundle shapes, connector envelopes and bends remain explicitly unqualified.
The 10 mm named compact floor remains only a lower bound and cannot override
this physical bound. The full run at
`10203d9a3f41d82cb467a7deb75e8293b0f1cc95` predates this check: preserve its compact
finalists as rejected pocket-depth diagnostics, even where all coverage/native
checks pass. Its original larger-pocket control is assessed separately.

A fresh bounded engineering follow-up covers pixel trunk inner radii 170/190 mm,
short-strip 680/720 mm, final-disc bypass enabled, inherited-pitch 23-row barrels,
and front-loaded/uniform disc schedules (eight primary cases), plus the same
three radius/pocket comparisons. This declared subdomain follows the earlier
search; it is not a rerun of the entire 216-case scan or a global optimum.
Retain fresh random validation seed 202609294 and rerun geometry, inventory,
capacity, individual-item fit, coverage and native checks after the correction.
The default full-scan configuration also uses the corrected service builder for
future shape updates; only the bounded follow-up is newly executed here.

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
