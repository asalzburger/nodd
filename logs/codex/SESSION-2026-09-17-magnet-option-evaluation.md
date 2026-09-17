# Team evaluation of six magnetic layouts

## User request

Evaluate all magnetic options as a team, discuss the choices, write one page per
layout and a two-page summary, and flag showstoppers. Continue PR #6 with an
updated executive summary. Starting branch `research/magnetic-configurations`
was clean at `8dc8330`.

## Outcome and team discussion

Six option proposals contain roughly 500–540 words each; the synthesis is about
1050 words, a two-page reading equivalent rather than renderer-specific pagination.
The architect authored MAG-01/03; the muon engineer MAG-02/05; the calorimeter
engineer MAG-04/06. Physics independently reviewed all six; software reviewed
concrete tool paths; the tracker engineer reviewed forward tracking and the
synthesis. The coordinator/publication office reconciled and edited the reports.

Actual challenges changed the proposals. Physics rejected treating the 2.86 T
flux-area screen as a saturation proof and challenged assumed radial expansion;
the calorimeter author revised MAG-04 to separate the proven old-host conflict
from possible remedies. MAG-06 now labels the zero-thickness 7.79 m estimate and
adds the 8.06 m estimate for an annulus starting at 4.95 m. Tracker review removed
an unearned MAG-03 field-advantage claim. The final priorities are research
priorities, with no claimed performance winner. Some direct review messages hit
agent concurrency limits; the coordinator relayed and integrated them. Pending
redundant author-review turns were stopped after integration to avoid late edits.

## Evidence and tools

Added an isolated PROTOTYPE arithmetic screen, reusing existing coil/layout inputs:
flat-field flux, available return area, diagnostic return-field trials, uniform
winding-bore energy proxies and active-return radii. The JSON retains formulae,
assumptions, provenance and actual values. These are neither nonlinear magnetic
solutions nor rigorous energy/space bounds. No new ACTS, Geant4 or FEM run occurred.

Registered SRC-FOURTH-CONCEPT-2007: primary public dual-solenoid proposal, with
PDF/version/section verification and SHA-256. The local PDF remains ignored.
Also registered official Elmer nonlinear benchmark and NGSolve coil tutorial;
these show available workflows, not a locally validated nonlinear field solution.

## Blockers and recommendation

No intrinsic topology showstopper demonstrated. The outer coil conflicts with the
unchanged muon host. Outer iron return and the selected active-return screen have
conditional space warnings; actual flux/return geometry must be solved. Unknown
station/material/measurement requirements prevent a defensible resolution ranking.
Prioritize MAG-05 and MAG-02 for standalone research, preserve MAG-01/03 controls
and combined alternatives, retain MAG-04 as a conditional resource comparison,
and give MAG-06 a bounded finite-coil screen. Human priorities and any envelope
amendment remain review decisions. Production geometry is unchanged.

## Checks and accounting

The arithmetic screen ran successfully; independent agent arithmetic agreed.
Documentation/logging tests passed; dashboard validation and preview build passed.
The paired JSON records commands and outcomes. Exact token counts and client
thread/version were unavailable; no counts are invented. No human sign-off is
recorded. This closes only the bounded written-evaluation increment.
