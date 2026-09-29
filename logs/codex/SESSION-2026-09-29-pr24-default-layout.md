# SESSION-2026-09-29-pr24-default-layout — PR24 default layout and transverse views

## Request and starting state

The user asked to address the new comment on PR #24. The [expert comment](https://github.com/asalzburger/nodd/pull/24#issuecomment-5886458913)
requests a concrete default per-subdetector placement and x-y barrel/endcap views.
Start revision: `a382a72f304c44d4316a60e9117cc760c141dbb7`, branch
`study/cobe-pint-module-coverage`. Four untracked files from the separate usage
summary task remain untouched and excluded from this response's commits.

## Interpretation and design boundary

A draft DES-009 amendment precedes implementation. No tilt section is interpreted
as no pint inclined barrel ends, while retaining explicitly requested local module
tilts. The unnamed third barrel bullet is interpreted as long strips. An optional
clarification was requested. Cobe's complete cylindrical nominal layers avoid
removing pint end pieces while retaining its shortened cylinders.

Pixel phi staggering uses tangential staves at alternating radii, no z staggering
by default. Short strips stagger in phi and z; tangential alternating-radius staves
are the default, while a common-radius locally tilted option separates the two
phi-overlap mechanisms. Long strips use local phi tilt on constant-radius staves,
without z staggering. Endcaps retain clearance staggering pending engineering.
The two independent pixel-z and short-tilt switches form a 2x2 comparison.

No-z staves hold phi/radius/tilt fixed along their length, with a nonoverlapping
body-based longitudinal pitch. Full rows cover the nominal end extent without
cropping; inactive seams remain measured. Old variants and their retained evidence
remain unchanged. The new default is a working prototype, not detector sign-off.

## Delegation and runtime

Three existing, human-requested agents divide geometry, true section/endcap views,
and independent policy/report review. Root owns design, configuration, execution,
tracking, session records and PR response. The acts-spack preflight warns of
changed fingerprints; required ACTS capabilities were directly verified using
the preserved local installation and isolated PR6178 step-size overlay. No shared
ACTS source, build or install changes are needed. Two constructor mistakes in the
initial runtime probes were corrected and retained in the paired check history.

## Execution, results and revisions

Populated when measured. Exact per-turn counters are unavailable during this
active task and are not estimated or copied from the earlier usage inventory.
