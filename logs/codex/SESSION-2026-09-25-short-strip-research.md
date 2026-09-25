# SESSION-2026-09-25-short-strip-research — Short-strip sensor and reusable ring-module research

## Scope and evidence

Contemporaneous curated record of DES-007 / TRK-SSTRIP, issue #20. Started from
`58136c8adad0d10bb046bef3a574e181b7e1463c`, origin/main, in isolated worktree
`/tmp/nodd-short-strip`, branch `research/short-strip-modules`. Main contained
unrelated token-accounting/workflow edits and Python caches; these were preserved.
No production detector description was changed. Current-turn usage is unavailable.

## Selected conversation

- User request (paraphrase): open a short-strip sensor/module research area,
  retain roughly ODD strip feature sizes, compare ring-specific modules and
  reuse of the same module type; changing endcap ring count is allowed.
- User correction (exact): “ATLAS ITk + CMS Tracker I meant”.
- Assistant clarification: asked whether to preserve 0.5 mm cells or allow longer
  cells; no answer available when preparing this draft. Keep 0.5 mm provisional,
  report alternatives and flag electronics feasibility.

## Decisions and outcomes

Created DES-007 DRAFT with FACT/INFERENCE/NODD DESIGN CHOICE provenance, sensor and
functional module proposal, explicit unclosed material/readout/thermal accounts,
and numerical ring comparison. ATLAS ITk has 24.1 mm short strips; CMS PS-p
macropixels (100 µm × 1.467 mm) are the closer readout precedent. Neither source
establishes an ASIC for ODD's 75 µm × 0.5 mm segmentation.

Four candidates are retained: six-ring custom wedges (360 modules, six types),
six-ring 48 × 96 mm rectangles (414, one type), twelve-ring 48 mm squares (790,
one type), and six-ring 96 mm squares (206, one type). The five-ring rectangle is
an intentional failed coverage control. The working recommendation is the
repeated 48 × 96 rectangle, conditional on electronics and support feasibility;
wedges save about 14.7% active silicon relative to it. No human approval inferred.

Initial two-mm edge margins failed ray coverage under z staggering; preserved
inputs/results document this. The 4 mm revision is derived from the 2.69 mm
worst test projection shift plus polygon curvature allowance. Four revised
candidates have zero uncovered samples on both grids and all vertex fixtures;
this is not a proof of hermetic or curved-track coverage. Trial body collisions
are absent; real support/cooling and ASIC seams are not included.

ODD XML half-dimensions imply 156 mm endcap sensor length, not 78 mm. Ring ID
width must change for more than four rings. DES-006's 5 mm/√12 second-coordinate
fixture differs from the proposed 0.5 mm/√12 binary estimate; integration must
resolve this explicitly. A 48 × 96 rectangle has 122,880 channels and the study
has about 50.87 million channels per disk. Power/bandwidth remain unquantified.

## Commands and validation

- Read instructions, PROJECT, DES-005, source/tracking/log workflows; inspect
  open scientific branches/PRs and DES-006; allocate DES-007 without collision.
- `git fetch origin`; `git worktree add -b research/short-strip-modules /tmp/nodd-short-strip origin/main`.
- Public-source browser research encountered CDS bot challenges. Downloaded the
  existing catalogue acquisitions with `curl -L --fail`; PDFs remain ignored.
  ATLAS and CMS SHA-256 match manifest. Read selected `pdftotext -layout`
  excerpts and inspect rendered tables. Four GitLab ODD raw-file hashes match
  the pinned 2026-09-16 snapshot. Wrong guessed source/branch paths were corrected
  against repository listings; no findings were based on those failed reads.
- Six short-strip analytical tests pass; both full numerical runs succeed.
  Inspect the rendered candidate figure. No randomness used.
- Dashboard validation, 27 tests and local build pass. Logging/schema checks and
  diff whitespace check are recorded in the paired JSON after execution.
- Initial sandbox `gh issue create` failed to reach GitHub; permitted escalated
  retry created <https://github.com/asalzburger/nodd/issues/20>.
- No DD4hep/Geant4/ACTS or engineering qualification was run. No software
  installation or production deployment was attempted.

## Changes and revision links

See the paired JSON changed-file inventory. Deliverables include DES-007,
functional-module and ring figures, two retained numerical scans, comparison
report, isolated tool/inputs/tests, ATLAS reading guide and CMS guide extension,
source catalogue, tracking and documentation index. The Git history identifies
this record's enclosing commit; no self-referential commit hash is invented.

## Token accounting

No exact completed-turn input/output counters are exposed in this active turn;
`usage` is empty and means unknown, not zero. Do not import unrelated historical
usage or estimate a split. The pending main-worktree AGENTS rule explicitly says
that unavailable/pending counts do not exempt a PR and to leave the gate failing
until completed-turn evidence can be imported. Its checker is run from that
worktree against this committed branch; no unrelated workflow edits are copied.
The session summary reports missing coverage separately from historical totals.

## Follow-up

Human choice on cell length and module family; sensor/electronics and mechanical
reviewers; realistic ASIC tiling, budgets and services; DES-006 covariance,
envelope and identifier handoff. Import exact completed-turn token evidence
before merge. Scientific design sign-off and production implementation remain
separate future steps.
