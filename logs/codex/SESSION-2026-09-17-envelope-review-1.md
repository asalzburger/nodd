# SESSION-2026-09-17-envelope-review-1 — First envelope review

## Scope and selected conversation

2026-09-17, contemporaneous curated record. User requested that the team read
PR #4's first review comments, discuss options, answer where possible and adapt
the plan. Starting branch `design/global-envelopes`, clean at
`7bb7ff04a96b2038572d59904f8954a42777d7e6`. Exact conversation start, client
version and token counts are unavailable; no private agent state is collected.

Read all 25 inline comments and the changes-requested review. The canonical
[disposition register](../../docs/design/DES-003-review-1.md) links every comment
and retains its answer or deliberate deferral. Public reviewer attribution is
included only as design-direction evidence, not as sign-off.

## Team and outcomes

Calorimeter, muon and physics specialists researched the options and exchanged
interface findings. System Architect consolidated the proposal; Software Engineer
updated the isolated prototype and validation catalogue. Coordinator checked
sources, reconciled claims and prepared PR replies. A further tracker-agent
follow-up could not start because of the agent limit; tracker/timing/radius
questions were covered by the physics input and coordinator's source checks.

Review directions: 14 TeV HL-LHC; tracker eta 4, calorimeter eta 5, muon eta 3
with 3.5 stretch. The later coverage comment supersedes the earlier calo minimum
of eta 4. Standalone-compatible/toroidal muon work is the baseline investigation,
with dedicated magnets deferred. No numerical design approval was inferred.

E1-R1 adds a detached forward-calorimeter study volume and reduces upstream
endcap apertures. Original E1 remains in Git. Forward support/shielding/readout
may extend beyond the drawing; a downstream calorimeter cannot filter hadrons
before upstream muons. Extra absorber steel awaits punch-through evidence.

Added source-based timing, services, active-first-radius and finite-solenoid
screening. The finite-sheet 3 T central hypothesis gives about 1.82 T at the
tracker end, not a physical field-map prediction. Rechecked the arithmetic.
Historical-versus-operational HF papers give different outer radii (1.30 versus
1.57 m); preserved the unresolved boundary discrepancy and did not use it as an
unexplained nODD parameter. PCB details, polygons and layer design remain deferred.

## Sources and commands

- Read AGENTS, PROJECT, relevant DES/ADR, tests and branch status.
- `gh pr view 4 --json ...` and `gh api --paginate repos/asalzburger/nodd/pulls/4/comments` retrieved review evidence. API sandbox network failure was retried with explicit approved escalation; public comments were kept temporarily for thread mapping.
- Read selected local CMS/ATLAS timing, tracker and detector passages; public papers and primary documentation. Some CDS/arXiv browser routes returned bot/cache errors; local PDFs/direct public downloads supplied the cited evidence.
- Downloaded five public papers with `curl -fL` into ignored PDFs: ATLAS solenoid commissioning, IBL operation, CMS yoke cosmic-ray map, CMS field map and CMS HCAL calibration. Added six source records (including HTML ATLAS Run-2 calibration) and verified two existing timing-TDR identities. Local title dates/version discrepancies remain explicit.
- Extracted all five new PDFs using `reference/cache/venv/bin/python tools/reference_reading/read.py extract SOURCE_ID`; content-addressed caches remain ignored. An initial reader help call under system Python lacked PyMuPDF; corrected to the existing reader environment without installation.
- Ran the envelope study with the existing plotting environment and README command. Report retains exact script/input hashes and pre-commit provenance. Visually inspected the updated SVG/PNG output.
- Verified seven local source hashes, all design source identifiers, report input/script hashes and finite-solenoid arithmetic.

## Validation and limitations

11 envelope tests, 15 logging/documentation tests and 7 reference-reading tests
passed. The diagnostic samples 21 rays across ten allocations and finds no
positive-area rectangle overlaps. New full/partial/missed axial traversal labels
are allocation diagnostics only. At eta 4 the detached forward box is crossed
fully while upstream HCal is partial; eta 5/5.2 still intersect the tracker host,
which is not a claim of active tracking beyond the eta 4 target.

No detector construction, real magnetic-field solution, radiation/transport,
shower or reconstruction validation was run. Full propagation is a mandatory
later catalogue item. No production geometry or TDR submodule changed. Changed
files and actual final checks are in the paired JSON. Human reviewers retain
control of thread resolution and design sign-off.

## Publication and follow-up

Update PR #4 with the revised proposal, drawing and responses to all 25 threads.
Next review should address detached versus compact forward placement, beam-line
and shielding fit, timing/service partition and finite-field/muon tradeoffs.
Publication results and resulting commits are recorded once they exist.
