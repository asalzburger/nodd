# SESSION-2026-10-01-pixel-z-coverage

## Selected request and authority

The user requested a new PR testing pixel-barrel refinement: orient RD53
wire-bond space in r-phi, minimise inactive z edges and attachment gaps, run
ACTS, and report for eventual approval. This authorizes an isolated prototype,
not production geometry changes or human engineering sign-off.

## Starting state and isolation

Started from origin/main c42bab1ce796ce10f188ae7b396fd88aa01fa547 in the separate
`/tmp/nodd-pixel-z-coverage` worktree, branch `study/pixel-z-coverage`. The user's
main checkout and palette/display edits were preserved. The frozen DES011
original-pocket layout and PR29 outward support inputs govern the study.

Read AGENTS.md, PROJECT.md, relevant designs, module/source model, validation
workflow, logging workflow and the acts-spack skill. The sister ACTS source
remains at 355ea68493b326956756c9386d2fd9eaf9328568 with its existing sensitivity
patch and other local changes; no sister source or dependency was edited.

## Outcome

Added DES013, six repeatable geometry hypotheses, matched coverage and total-p
sensitivity, paired regressions, a longitudinal seam scan, module vector
mockups, native ACTS audits and explicit ±1 µm edge probes. All unchanged
subdetector/region counts are identical for every matched primary track.
Recommend chip-centred 0.2 mm sensor edges plus 0.2 mm mechanical gaps for expert
review. Straight missing barrel opportunities fall from 16.54% to 3.87%; both
charge signs at pT=1 GeV give 3.86–4.01%. Added ASIC power is 1.5805 kW. The
quad stress cooling ceiling fails and is retained as a proposed flow/service
amendment, not silently repaired.

The symmetric packing retains a central quad seam. A 0.5 mm edge control has
an aligned four-barrel hole at z=−11 mm, eta=0, reproduced by native ACTS.
The 0.1 mm sensitivity offers less than one additional percentage point of gain.
No production compact, sensor response, materials or working baseline changed.

Added SRC-PLANAR-SLIM-2013 with exact section/page and explicit non-qualification
for RD53. A newer manual URL returned HTTP403 and was not used as normative
input; the inherited publicly catalogued approximate chip model is retained.

## Commands and actual verification

- Spack preflight returned 2: setup/lock fingerprints differ. Verified ACTS,
  sensitivity and step-size binding, NumPy and ROOT in the existing runtime.
- Initial sandbox runtime setup failed on permissions and a Matplotlib import;
  used authorized runtime activation. SVG reporting needs no Matplotlib.
- An initial native audit command overwrote PYTHONPATH and failed at provenance
  collection because ROOT was unavailable. Preserving the activated PYTHONPATH
  fixed this; all six complete audits were rerun successfully.
- `python3 tools/pixel_z_coverage/study.py --output docs/validation/DES-013-pixel-z/data`
  completed six cases: 7,312 primary tracks × 3 modes and 4,096 total-p tracks ×
  2 charges per case, 180,768 trajectory/layout evaluations in total.
- Native setup: source acts_setup.sh; `acts run acts-nodd`; activate installed
  acts-nodd/pyvenv; prepend `/tmp/acts-python-step-size-overlay/python` to existing
  PYTHONPATH. `study.py --native-only ... --acts-source ... --runtime-manifest ...`
  passed for all six cases, 92 tracks each. ROOT 6.40.04; overlay SHA retained.
- `native_seams.py --run ... --acts-source ...` passed 28 explicit controls for
  each complete geometry. 720 total native track audits, zero hit mismatches.
- 6 new layout tests, 15 analytic intersection tests, 3 native integration
  controls, and 27 dashboard tests passed. SVG XML syntax and retained native
  result assertions passed. No body/support conflicts in any case.
- `diagnostics.py --run ...` checks unchanged counts and paired denominators;
  28,896 additional straight eta=0 seam-scan evaluations, 1 mm z step.
- `report.py --run ... --output ...` reproduces report tables and module SVG.
- Dashboard validation initially found an invalid new state/role and missing
  not-yet-rendered evidence; corrected records and completed evidence pass.
- Session validator and dashboard validator/build pass; usage summary run.

## Files and evidence

Canonical new code is in tools/pixel_z_coverage; design is DES013; retained
artifacts, recommendation and drawings are in docs/validation/DES-013-pixel-z.
Updated source manifest and project tracking; reconciled observed PR32 merge
metadata. Exact changed-file inventory is in the paired JSON session record.

## Limits and accounting

Bulk coverage is an analytic finite-patch oracle cross-checked with native ACTS
supporting-plane propagation and native bounds; global navigator/reconstruction,
material transport, sensor response, FEA and new service/flow capacity are not
validated. The temporary binding overlay reuses existing libraries/build objects
and is not a clean rebuild of the dirty sister checkout. Source/extension hashes
and configuration are retained separately. Spack registry warnings remain.

Exact per-turn client token counters and thread/turn IDs were not exposed; usage
is empty, not zero. Repository-wide summary includes earlier observations only:
134,594,309 input and 674,111 output tokens across 79 recorded turns in 42 of 70
sessions at this checkout; it does not measure this task's token consumption.
No raw private client state or inferred token counts were collected.
