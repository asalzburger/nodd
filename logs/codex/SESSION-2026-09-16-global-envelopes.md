# SESSION-2026-09-16-global-envelopes — Global detector envelope proposal

## Scope and evidence

Contemporaneous curated record, 2026-09-16. Starting main revision
`b5247808858e0391d600d66a970f83259a19b425`, initially clean; work branch
`design/global-envelopes`. Stage A had already been closed for progression by
the user. Stage B work here concerns global allocations and interfaces only.
Exact start time, client version, token counts and complete tool-call totals are
unavailable. No raw private agent state is recorded.

## Selected conversation

User request (paraphrase): coordinate subsystem envelope arguments through the
System Architect, obtain software validation-tool research and independent
physics input, and publish a first proposal PR with an r–z drawing and follow-up
questions. Web search and sandbox pip installation were explicitly authorized.

Assistant outcome: coordinated six specialist contributions (tracker,
calorimeter, muon, System Architect, Software Engineer, Physics and Performance
Validation) and assembled DES-003 / ADR-006 as drafts. Public primary sources and
local PDFs support the input memoranda. No agent grants human sign-off.

## Decisions and outcomes

- E1 retains ODD's inner-solenoid ordering with proposed tracker-service and
  magnet reservations, enlarged calorimeter allocations and an outward-shifted
  muon barrel start. Dimensions are draft choices, not engineering tolerances.
- ODD's polygon radius conventions differ between barrel and endcap factories;
  the proposal uses maximum enclosing radii and documents the conversion issue.
- Tracker investigation to |η|=4 and calorimeter entrance edges near |η|=3.1
  require an explicit coverage decision. Envelope crossings are not hit counts.
- Material screening uses explicitly labelled elemental approximations; the
  dense ODD HCal mixture needs physical accounting. No box is assigned a fictitious
  homogeneous material merely to produce a budget.
- External-coil and standalone-muon alternatives remain open; timing, return
  structures, support footprints and service routing are unresolved.
- The isolated PROTOTYPE diagnostic tool reads the draft JSON, tests rectangular
  allocations and prompt rays, and generates the r–z figure. It is not connected
  to production DD4hep geometry.

## Commands and validation

- Read repository instructions, project/plan/ADR documents, source catalogue,
  pinned ODD XML/factories and selected ATLAS/CMS PDF passages.
- Created branch with `git switch -c design/global-envelopes`; sandbox Git write
  restriction required an approved escalation.
- Created ignored plotting environment with
  `python3 -m venv reference/cache/envelope-venv`; installed Matplotlib through
  that environment's pip. Sandbox DNS failure was retried with approval.
  Exact dependencies and reproduction commands are in the envelope tool README.
- Downloaded the PDG 2025 passage-of-particles review into ignored local PDFs
  with `curl -fL`; sandbox DNS failure was retried with approval. Source metadata,
  access date and SHA-256 are retained in the manifest.
- Ran envelope diagnostics and rendered SVG/PNG; visually inspected the drawing.
  Initial tangent test exposed floating-point zero-path noise; added an explicit
  numerical ULP guard, distinct from any physical clearance tolerance.
- Logging test suite: 15 passed. Reference-download test suite: 4 passed.
  Additional final checks and their exact results are in the paired JSON.
- `gh pr list` initially could not reach GitHub in the sandbox; approved retry
  succeeded and found no open PRs before publication.
- The first staged whitespace check exposed trailing spaces from Matplotlib SVG
  output. The generator now normalizes line endings; figures/report were regenerated.
- No detector construction, runtime overlap check, material transport, shower,
  field, reconstruction, or TDR build was run. Such checks remain follow-up work.

## Changes and revision links

See the paired JSON inventory for changed files. Six input memoranda retain
source locators and role-specific recommendations; the main design consolidates
them. The manifest adds PDG evidence and verifies selected upgrade-TDR metadata.
Local PDFs, caches and the plotting environment are ignored. The TDR submodule
is unchanged. Git history identifies the enclosing commits.

## Follow-up

Review the first proposal on its PR: use cases and coverage, magnet ordering and
return field, timing allocation, muon requirements, material ownership and
transition/service corridors. Assign human reviewers before design sign-off.
Then define active surfaces/material scenarios and run the staged validation
programme. Merging this draft alone does not authorize production implementation.
