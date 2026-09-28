# SESSION-2026-09-28-module-populated-layouts — Populate cobe and pint with finite modules and compare ACTS coverage

## Scope and evidence

Contemporaneous curated record. Started from clean nODD
`d23421175541651863de0e1f9077e81a5ade3832` after infrastructure PR #23 merged;
branch `study/cobe-pint-module-coverage`. Governing work is isolated DES-009,
continuing DES-005/006 and pinned draft inputs from PRs #8, #21 and #22.
The authorized ACTS sister checkout retained its pre-existing changes. Three
human-requested subagents owned geometry, independent intersections and native
ACTS validation, with subsequent independent report reviews.

## Selected conversation

User requests, paraphrased: populate cobe/pint using working pixel and strip
module models; compare staggering, tilts and flat staves; evaluate hits,
hermeticity and silicon for straight and 1 GeV tracks in 3 T over the specified
luminous region; divide work among subagents and recommend where support
complexity is beneficial. The user authorized creating a PR and Git/GitHub use.
Exact additional request: “Also, make this workflow repeatable, in case we have
future updates to the module/sensor shapes”. Earlier conditional authorization
requested an ACTS draft PR if needed functionality was missing.

The assistant asked an optional pT-versus-total-p clarification. No answer was
received; pT = 1 GeV was stated as the primary convention, then a separate
total-p = 1 GeV check was added so both interpretations are measured.

## Decisions and outcomes

The working models are explicit rectangular active masks, pixel chip islands,
and long-strip same-module stereo pairs. Pixel outlines/guards/services remain
conditional fixtures. New JSON dimensions and sampling controls drive a fresh
run directory; unsupported shapes fail explicitly. No production geometry,
reconstruction setting or human approval changed.

Four initial patterns exposed body clashes. Two mechanically motivated
clearance variants add pixel-endcap depth colours and account for barrel
curvature; all four cleared cobe/pint combinations pass trial-box and host checks.
The failed controls remain. Short-strip barrel staggering gives a clear coverage
gain. Long-strip staggering has substantial silicon/depth cost; pixel barrel
losses remain significant. Pint's full inclined modules overhang their ideal
segments, which is retained and reported.

The pooled grids showed phase-dependent charge asymmetries. An independent
4,096-direction sample confirms the support ranking without interpreting the
probe distribution as collider event efficiency. A separate 12,288-trajectory
rerun reproduced all numerical metrics exactly.

Native ACTS exposed two distinct issues. A single giant TryAll navigation leaf
misses curved-track candidate surfaces; the adverse control is retained and is
not described as validated global navigation. Target propagation also needed a
maximum step control unavailable in the Python options. A temporary native
guide-state method passed all 32 preliminary case audits. A separate isolated
ACTS worktree adds the small step-size binding and genuine propagation tests;
its compiled overlay leaves the shared installation/source/build untouched.
Final study runs use the preferred direct target propagation with that option.
Both methods distinguish finite-surface intersection checks from global navigation.

## Commands and validation

The paired JSON retains commands and actual checks. Preliminary numerical runs
covered 477,312 trajectories across 24 main/control cases, four independent
sample cases and four total-p cases; repeated straight controls count toward
that total. A separate exact rerun covered another 12,288 trajectories.
The final canonical-revision runs and exports are recorded below when complete.

The acts-spack preflight exited 2 for changed setup/lock fingerprints. Fresh
ACTS/ROOT/NumPy/Matplotlib capabilities were verified. Runtime setup warned about
sandboxed shell discovery and a missing Geant4 data path; actual required Python
imports and native executions passed. No Geant4 transport was attempted.
One delegated native benchmark waited on an escalation and was aborted before
execution; ordinary sandboxed runtime execution then worked.

Initial dashboard testing found two errors because a Python script was listed
as exportable curated evidence. The task deliverable was corrected to the
workflow README; no export policy/test was weakened. The subsequent dashboard
build passed. Final complete checks are retained in the paired JSON.

## Changes and revision links

See the paired JSON inventory. Principal changes are `tools/module_layout/`,
DES-009 design/report/evidence, the source manifest, tracking, README discovery
and this session pair. Result revisions and PR links are appended once they exist.

## Token accounting

Exact client-reported per-turn counters and stable client turn IDs were not
exposed for the parent or any of the three subagents. `usage` remains empty;
there are no observed input/output totals for this task. No counts were estimated
or copied from other sessions. The final logging summary reports historical
observations separately from this missing coverage.

## Follow-up

Human review is needed for pixel sensor boundaries/seams, stave depth and services,
beam-pipe clearance, long-strip electronics qualification, and a suitable full
ACTS navigation hierarchy. Finite sampling is not continuous hermeticity, and
trial occupied boxes are not support engineering. No design sign-off is recorded.
