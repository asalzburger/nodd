# SESSION-2026-09-17-envelope-review-2 — Envelope closure details

## Scope and conversation

User requested addressing the new PR #4 review, expecting envelope sign-off soon.
Started on clean `design/global-envelopes` at
`9877ec14998280ef6f9cb4d13ae6b949d6c75d06`. Read 21 new inline comments and the
changes-requested summary: the remaining substantive item was enough space for
a 3 T solenoid. Exact start/client version/token counts are unavailable.

## Work and outcomes

Physics specialist supplied a bounded, sourced space estimate; System Architect
updated DES-003/ADR-006. Coordinator propagated dimensions, regenerated artifacts,
recorded baseline directions and prepared PR responses. Detailed magnet design
was expressly deferred by the reviewer and was not started.

E1-R2 reserves 400 mm radially for the magnet with explicit sub-allowances and
250 mm at each end of an illustrative cold assembly. Adjacent calorimeters move
outward/downstream, retaining nominal thicknesses/gaps; the muon barrel starts
at 4.35 m. The conditional polygon face-normal reduction is explicit. This is
planning space, not a certified safe magnet or complete remote service enclosure.

Recorded: detached forward calorimeter in the baseline, 25 mm aggressive inner
tracker host, outermost tracker layer as potential timing baseline, dedicated
magnetic/muon research next, ACTS installation planned for later propagation.
No human sign-off or production implementation was recorded. Positive comments
were acknowledged separately from approval of an exact final revision.

## Commands and checks

Read current instructions/project and relevant design/ADR; inspected Git state.
GitHub reads initially failed in the sandbox and succeeded on approved escalation.
Read public PR review threads with gh; no new scientific sources were required.
Existing ATLAS/CMS source catalogue entries gained explicit space-budget locators.

Ran the envelope generator using the existing plotting venv and README command:
10 allocations, 21 rays, zero positive-area rectangle overlaps. Verified report
input/script hashes and inspected the figure. Ran 11 envelope tests and 15
logging/documentation tests, all passed. Session validator checked 24 records.
No field solver, structural calculation beyond disclosed analytic scales,
DD4hep/Geant4/ACTS runtime or TDR build was executed. Local caches remain ignored.

## Traceability and follow-up

[Review round 2 disposition](../../docs/design/DES-003-review-2.md) records all
21 comments and the pending decision scope. The paired JSON lists changed files
and publication outcomes. Human review/sign-off of the envelope baseline remains
pending; detailed field and muon studies are the next work, not hidden prerequisites
claimed complete by this proposal.
