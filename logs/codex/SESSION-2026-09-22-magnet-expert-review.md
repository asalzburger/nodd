# SESSION-2026-09-22-magnet-expert-review — PR #6 magnetic-field expert response

## Scope and evidence

Contemporaneous curated record. Starting PR branch/head:
`research/magnetic-configurations`, `2530c5543da6b2c474ccadc6c67ce431d69d2e0f`.
The client initially had `main` checked out; switching preserved three unrelated
untracked bytecode files under `tools/tracker_layout/`. No raw private client
state, exact token counts or conversation start time was exposed/collected.

Related: DES-004, DES-003, ADR-006, ADR-003, PR #6 and issue #9.
The [expert comment](https://github.com/asalzburger/nodd/pull/6#issuecomment-5774198540)
by `mgtmentink` asks about enclosure scaling, homogeneous winding current and
removal of the active-solenoid configuration. It does not identify an exact
reviewed revision; the inspected head above is not attributed to the reviewer.

## Selected conversation

User request (exact): “There's a comment from the magnetic field expert reviwer
on PR#6, address it, update the PR description and answer as much as possible.”

Assistant outcomes: audited enclosure rationale, distinguished the existing
surface-current sheet from volume current, introduced finite homogeneous winding
packs and withdrew MAG-06 from the active comparison. Explained that vacuum-vessel
engineering cannot be inferred from the old cold-mass scaling argument.

## Decisions and outcomes

- Kept enclosure widths as explicitly unverified planning allowances; no vessel
  wall thickness, safety factor, material recipe or structural approval invented.
- Added isolated PROTOTYPE inner/outer rectangular winding packs, analytic
  normalization/axis integral, three-dimensional Biot–Savart quadrature and tests.
  Homogeneous pack averages are 25.9051 and 14.5181 A/mm² at +3 T in vacuum.
  The inner pack midpoint shifts 25 mm inward; the comparison records that change.
- Retained old sheet benchmark/atlas and archived MAG-06 inputs/card/evidence.
  Active drawings and host diagnostics cover MAG-01–05 with finite winding bounds.
- Updated candidate guidance, dashboard tracking/review context and the ATLAS
  source entry. The public ATLAS abstract/section I was re-read. Historical CMS
  facts remain sourced to prior repository verification; fresh PDF requests hit
  bot/403/access failures and are not represented as newly verified.
- Prepared a rewritten PR description and a direct three-part expert response.
  Publication evidence is added below after actual execution.
- No design sign-off, review closure, baseline/production change or new issue.

## Commands and validation

The paired JSON records commands and actual outcomes: 20 magnetic, 11 envelope,
25 dashboard and 15 session-logging tests passed; 12 field samples and five host
allocations passed; 14 JavaScript assertions passed with JavaScriptCore. Node
was absent (exit 127); no Node success claimed. Dashboard validation/build,
44-session validation, whitespace checks and baseline/TDR unchanged checks passed.
New axis and combined host drawings were visually inspected.

`git switch research/magnetic-configurations` initially failed because the
sandbox could not create the Git index lock; the approved escalated retry
succeeded. A subsequent GitHub head query failed in the sandbox and succeeded
with approved escalation. The historical plotting environment was absent;
installed Python 3.14.7, NumPy 2.4.3 and Matplotlib 3.11.0 were used, with actual
versions and file hashes recorded in generated reports. No dependency install.

## Changes and revision links

The paired JSON contains the complete changed-file inventory. Principal additions
are the expert-response memo, `windings.json`, `finite_winding.py`, its tests,
finite-winding numerical report and axis plot. Existing five-option figures,
host report, design guidance, source entry and dashboard records were updated.
Unrelated tracker caches remain untouched and unstaged.

## Follow-up

Expert assessment of the prototype assumptions remains pending. Actual vessel
sizing, conductor/thermal/protection engineering, nonlinear iron fields, discrete
toroid geometry and muon performance still require further work. No ACTS,
Geant4 or structural solver was run. Issue #9's previous MAG-06 scope is
superseded in the repository and PR; the issue itself was not edited in this task.

## Publication

Published implementation and response evidence at `e6a1ba796bb642f27cd3804519906d1f156422fd`.
Updated [PR #6](https://github.com/asalzburger/nodd/pull/6) description and posted
the [three-part expert reply](https://github.com/asalzburger/nodd/pull/6#issuecomment-5775404465). Both link
to the exact scientific revision. The tracking snapshot records that observed
head; a subsequent logging-only commit does not change the scientific target.

GitHub [build passed](https://github.com/asalzburger/nodd/actions/runs/35719994684/job/106720436356)
for the scientific revision; PR deployment was skipped as intended. Local session
and dashboard validation and the post-publication preview build passed. Task
closed after publication verification; expert approval remains pending.
