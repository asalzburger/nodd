# SESSION-2026-09-24-magnet-sizing-review — PR6 expert sizing

## Scope and evidence

Contemporaneous curated record. Inspected PR head `35047957ea565ea0fca53e57c32379d5f0e5fc91`; isolated detached worktree, target remote `research/magnetic-configurations`. Main workspace and unrelated untracked tracker bytecode preserved. Scaffold was created after resolving the merge; the JSON records the true pre-task revision and observed merge result. Missing start time and exact token usage remain unknown, not zero.

## Selected conversation

User, exact: “PR#6 has comments from the human expert reviewer, plesae address them (also fix the merge conflict in the tracking.json)”. Read mgtmentink's new 2026-09-24 comment and previous replies. Asked whether undefined RCM means RCMi; proceeded with a clearly provisional interpretation after time for an optional answer. No human confirmation was inferred.

## Decisions and outcomes

Merged origin/main normally, combining tracking tasks/PRs by stable ID and retaining both independent magnet and Spack records. Strict duplicate-key and parent-ID audit passes; no history rewrite. Merge conflict was expected and resolved, not treated as a design decision.

Implemented review-directed inner/outer gap relations, all-space vacuum energy/cold-volume closure and central 5 T cap. Persisted constraints in AGENTS, central policy, field/layout validators and CI. Kept explicit homogeneous winding J, retained provisional axial allowances, and documented the 2:1 radial winding/support closure. No pressure-vessel engineering or conductor approval is claimed.

Derived and implemented an axial-integrated current/vector-potential energy expression, including all vacuum field energy without a finite map cutoff. No SciPy needed; probing found it unavailable and no dependency was installed. Both roots meet energy/volume closure and quadrature refinement. At 3 T inner/outer energies are 132.576/3624.582 MJ and RVo 1.559419/5.400309 m. Outer muon hosts and nested budgets move +0.600309 m, preserving depths and 0.15 m interface gaps. No DES-003 baseline changes. MAG-06 remains withdrawn.

Added source catalogue entries for the public expert instructions and Fitzpatrick's vacuum-energy derivation, with locators. The expert's ATLAS/CMS scaling attribution is not presented as an independently reconstructed fit. Earlier finite-pack and sheet evidence remains historical; prior composite drawings/report remain in Git at the inspected head. New field/energy evidence uses separately named artifacts.

## Commands and validation

Paired JSON records actual commands/results. Reused the existing shared envelope Python environment under the main checkout's reference/cache; no shared environment modification. All 26 magnetic, 26 dashboard, 15 logging and 5 preflight tests pass; 14 JavaScript assertions pass. All twelve new field samples and five geometric allocations pass. The first layout regeneration caught stale auxiliary MAG-04 steel bands; corrected their radial translation and reran successfully. Initial default plotting emitted cache warnings; explicit temporary caches used thereafter. Figure inspected; input/code hashes match. Source derivation independently checked against a long-solenoid field-energy limit, analytic axial integral and scaling identities. Local success is not a full magnet field, pressure-vessel or performance validation.

## Changes and revision links

See paired inventory: sizing solver/policy/tests, CI and AGENTS rule, current winding/layout inputs and figures, DES-004 response and supersession notes, provenance/tracking and paired log. Result hashes only recorded once observed. Publication and fresh expert review target are added when available.

## Follow-up

Expert confirmation of RCMi interpretation, axial allowance, cold-volume convention and winding/support split; conductor margins (inner pack now about 49.6 A/mm²), support/closure design, complete nonlinear steel/toroid/coupled energy and field solutions. Future full configurations cannot claim the 5 T total central cap or complete energy sizing from an isolated vacuum control. Human final sign-off remains with asalzburger-review; no condition marked resolved on behalf of a reviewer.

## Publication and re-review

Published `2b8c032fb9c6e8aa2333ae5a4c88818cacecc645`; [response](https://github.com/asalzburger/nodd/pull/6#issuecomment-5812130449). Requested re-review from mgtmentink; original asalzburger-review request retained. GitHub reports MERGEABLE. [Hosted CI](https://github.com/asalzburger/nodd/actions/runs/35985506596) passed at that code revision, including the newly enforced magnetic tests. Following commit updates review/PR/log metadata only and records this exact evidence target.
