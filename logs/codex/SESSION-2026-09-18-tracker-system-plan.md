# SESSION-2026-09-18-tracker-system-plan — Plan the whole tracker with architecture, technology, physics and software inputs

## Scope and evidence

Contemporaneous curated record of the whole-tracker planning task on 2026-09-18.
Starting revision: `9bc03865fa384dd4b19448b81bd9f86b29feb9f0`, branch `main`,
with a clean initial working tree. Work is on `design/tracker-system-plan`.
The user explicitly requested coordinated SysArch, TrackTech, PhysVal and SoftEng
work. The primary agent acted as SysArch; three independent agents wrote bounded
specialist inputs and then cross-reviewed the consolidated plan.

Related: DES-005, DES-003, ADR-001/003/006, existing pixel DES-001/PR #8/issue #7,
and magnetic DES-004/PR #6/issue #9. Pixel and magnetic branches are unmerged
dependencies inspected at exact revisions recorded in DES-005; they were not
copied into production. Exact token counts, client version, thread ID and actual
conversation start time are unavailable. Raw agent state is not collected.

## Selected conversation

- User request (paraphrase): plan the whole tracker inside the established envelope
  with fixed coverage to absolute eta 4; begin with ODD pixels, short strips/strixels
  and stereo outer long strips, allowing motivated timing alternatives. Coordinate
  the four roles, integrate the started pixel work, and stage parametric estimates,
  ACTS hermeticity/material/field studies and later DD4hep/Geant4 simulation.
- Assistant correction: the supplied pixel reference #9 is the muon field issue;
  verified pixel work is issue #7 / PR #8. The user was informed; both dependencies
  are correctly linked in the plan.
- Assistant outcome: DES-005, four argued role inputs, staged evidence gates,
  sixteen follow-on work packages, dashboard tracking and source-metadata updates.

## Decisions and outcomes

Keep the envelope fixed for initial studies and internal subsystem boundaries
variable. Coverage cannot be reduced by adopting an older exploratory option.
Beamspot stress tests enter early; the reviewed luminous distribution is required
before layer freeze and repeated in final detailed validation. Material and field
machinery start alongside layer screening; explicit estimate scenarios permit
progress while physical component budgets mature. Unknown material is not zero.

The pixel design's partial reference path is not a complete module/layer budget.
Separate strip, support, cooling and power/readout/service packages fill its
intentional exclusions. Audit ODD measurement/digitization conventions before
using stereo information. Compare timing hardware with and without time response
and against a no-timing control. Separate ideal estimates, truth fits, pattern
recognition and full transport evidence.

Cross-review requested and incorporated consistent operating/radiation states,
provisional source-extraction contracts, explicit field-domain failures, schema
versions/hashes, synthetic versus detailed material-map distinctions, fair
per-component material controls, electron/hadron validation beyond muon-like
controls, and design sign-off versus later physics acceptance.

SoftEng verified local ACTS imports and performed bounded read-only IdRes intake.
IdRes access succeeded; public availability, licensing and numerical validation
remain unresolved. No private endpoint/content is recorded here or used as a
normative detector source. The public analytic fallback permits planning to
proceed; optional tool intake remains a separate prerequisite for its adapter.

No tracker performance calculation, material scan, active-surface propagation,
new field solution or production detector implementation was performed. DES-005
is DRAFT. M0 and all human approval states remain unchanged. This task prepares
a plan; its dashboard completion refers only to the planning deliverable.

## Commands and validation

Inspected repository instructions, PROJECT, development plan, DES-003 allocation
and specialist inputs, ADRs, source catalogue, tracking/logging conventions and
relevant tests. `git fetch origin` initially failed on sandbox write access and
succeeded after escalation. GitHub reads initially hit sandbox network failures;
approved retries succeeded. `gh pr view 9` correctly reported no such PR;
`gh issue view 9`, PR #8, issue #7 and PR #6 established the dependency identities.
Read branch documents via `git show` without switching to their branches.

Created this pair with `python3 tools/session_logging/session_log.py new --id SESSION-2026-09-18-tracker-system-plan --title "Plan the whole tracker with architecture, technology, physics and software inputs" --milestone M1`;
created branch with `git switch -c design/tracker-system-plan`.

SoftEng's local inventory imported `acts` and `acts.examples` and verified
`pyacts` version 47.7.0. An initial distribution-name lookup for `acts` failed;
the corrected `pyacts` lookup succeeded. Presence/absence of named bindings is
an inventory only, not a numerical test. Public documentation locators were
checked and catalogued. The existing PR #6 propagation report was read, not rerun.

Two patch applications failed because their expected text did not match; corrected
patches fixed the parent link and integrated the review refinements. Final actual
check results are recorded in the paired JSON. Documentation and infrastructure
checks do not establish detector performance or scientific acceptance.

Final verification passed: 15 logging/documentation tests, 25 dashboard/update
tests, validation of 27 tasks / 8 documents / 3 review rounds, static dashboard
build and validation of all 32 session records. A focused audit of the five
DES-005 documents verified local link targets, whitespace, seven referenced
source IDs and absence of the private endpoint; all 51 catalogue IDs are unique.
`git diff --check` passed for tracked changes. No test or validation failure
remains unresolved.

## Changes and revision links

- DES-005 consolidated plan and SysArch/TrackTech/PhysVal/SoftEng inputs.
- Development-plan follow-up and documentation-index link.
- Tracking register: one completed planning deliverable, sixteen planned
  follow-on packages, affected workstream next actions and evidence.
- Source catalogue: existing ODD observation locators and ACTS official
  propagation/field/material documentation metadata; no new detector values.
- This session's paired record. Generated dashboard output stays ignored.

Exact paths are in the paired JSON. No commit or PR was requested or created.

## Follow-up

Review DES-005, assign technical/expert reviewers, complete the provisional
contracts and agree numerical physics criteria, luminous distribution, operating
and occupancy scenarios before selection. Then execute the bounded study tasks.
Module/field dependencies, physical budgets, backend readiness and applicable
human design sign-off remain explicit. No final layout decision is requested
without its evidence.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 7 disjoint turns: **7,752,206 input** and **39,477 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
