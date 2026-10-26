# SESSION-2026-10-26-geantino-material-stacks — Geant4 material profile PR

## Scope and evidence

Package the existing 100,000-geantino analysis into nODD, following DES-024/025
and ADR-008. Fresh worktree codex/geantino-material-stacks starts at
f459df42a73c526c10acb0c6e73ddda5f408ea4c with no changes. Initial plotting is
summarized retrospectively from retained artifacts and visible conversation;
this packaging record is contemporaneous. Other checkouts and original scan/plots
remain intact. Exact token counters are unavailable.

## Selected conversation

- User request, paraphrased: find the Geant4 scan of 100,000 geantinos in storage;
  make stacked profile histograms with unrooted for beam pipe, pixel, short strip
  and long strip, each split into sensitive and non-sensitive material.
- Assistant outcome: processed all 100,000 tracks and 17,137,021 material steps;
  produced eta, |eta|, phi and subdetector panels, TProfiles, CSV and static/HTML.
- User follow-up, exact: “Can you make a OR with these changes ?”
- Assistant interpretation: “OR” means a pull request; package scripts, figures,
  compact profile data and validation for review.

## Decisions and outcomes

Use explicit compact and factory paths for native classification and the pinned
isolated unrooted environment for export/plotting. Retain compact means, variances,
counts and static figures in Git; keep recording, derived ROOT, HTML and caches
local. CI replays figures without native DD4hep. No geometry/design changes.

Positions are Geant4 step starts: locate half a step along the recorded direction.
Use DD4hep flags, preserving passive silicon ASICs, guards and seams. Fill every
track into every component including zeros; stack additive means and derive total
uncertainty from per-track totals with covariance.

The recording has no geometry revision, seed or original command. Retain local
geometry hashes and source checkout 530080cfe16c7513228bf60238b99d4b9938538a
separately. Density agreement supports association but cannot prove missing
recording identity or same-density material recipes. Six float32 boundary rescues
include two short-strip sensitive/guard ambiguities, allocated non-sensitive with
a full allocation bound: at most 1.46e-10 X0 and 2.99e-11 interaction lengths in
an eta-bin mean. Totals are unchanged. The finite cell grid is not a continuous proof.

## Commands and validation

- Original acts-spack preflight found changed setup/lock fingerprints. Direct
  verification succeeded: DD4hep 1.38, Geant4 11.4.3, ROOT 6.40.04. Sandbox system
  inspection restrictions required the authorized retry.
- Original 1,000-track control: zero unassigned/density-mismatched steps.
- First full pass: six precision-limited mismatches, two unassigned steps. A cell
  retry initially stopped on ambiguous sensitivity. Retain a conservative bound.
- Corrected full pass: all 100,000 tracks and 17,137,021 steps accounted for;
  zero unassigned/density-mismatched steps, three interior retries, six cell rescues.
- Portable export checks native counts, means and variances against independent
  per-track reductions. Compact-data replay passed and generated all 15 exports.
- Project validation: 72 tasks, 39 documents and 21 review rounds validated.
- Final portable native rerun, review and closeout checks are recorded below.

## Changes and revision links

Paired JSON lists scripts, retained profile data/figures, software documentation,
CI replay, tracking and this record. Result commits are entered only after creation.

## Token accounting

Exact client per-turn usage, actual model and client version are unavailable.
Usage stays empty: unknown, not zero. No estimates or cumulative totals are
attributed. Project observed coverage is reported at closeout, not as task usage.

## Follow-up

Complete portable native rerun and exact-revision assessment; open the requested
PR with its interaction record. Human PR review is separate from detector design
sign-off, which is not granted here.

## Specialist assignment GEANTINO-PhysVal-01

Explicit generic-agent PhysVal mandate, read-only, at 4008abf1c4c76bbfd5f7df64dcfd81ee5e62e768.
Contract: [PhysVal-01.assignment.json](SESSION-2026-10-26-geantino-material-stacks/PhysVal-01.assignment.json).
Assess normalization, sensitivity attribution, covariance, precision bounds and provenance.
No native simulations, file changes, installs, external services or further delegation.
This is a separate assessment; native profile loading and human approval are not claimed.

## Specialist follow-up GEANTINO-PhysVal-02

Read-only correction assessment at 7c0012184a6bb033eb4366d48db4f8699b22f8d5. Contract: [PhysVal-02.assignment.json](SESSION-2026-10-26-geantino-material-stacks/PhysVal-02.assignment.json). Check asymmetric float32 cells, the pure C++ regression and retained native provenance only.
