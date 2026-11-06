# SESSION-2026-11-06-pr123-framework-install — Install original calorimeter digitization framework for PR123

## Scope and evidence

State collection method, available context, limitations, related IDs and starting
revision. Identify uncommitted user changes present before work.

## Selected conversation

Attribute requests to the user and outcomes to the assistant. Mark exact quotes
and paraphrases explicitly. Include corrections and changes in direction.
Exclude private model state, confidential content, and irrelevant system context.

## Decisions and outcomes

State rationale, alternatives, consequences and what remains unresolved. Never
convert implementation authorization into human design sign-off.

## Commands and validation

Record relevant commands, actual exits/results, failed attempts and remedies.
Distinguish structural checks from detector acceptance.

## Changes and revision links

List changed files or refer to the paired JSON inventory. Result commits are
recorded only once they exist; Git history locates this record's enclosing commit.

## Token accounting

Record the client-provided per-turn usage source and import command, or state why
exact counters are unavailable. Report observed input/output sums and missing
coverage from `session_log.py summary`; empty usage means unknown, not zero.
Never copy raw client archives or private model state. Do not duplicate turns
across tasks or add cached/reasoning subsets to the input/output totals.

## Follow-up

List remaining work, missing measurements and any human review needed.

## Specialist assignment

Assignment PR123-SOFTENG-DEPENDENCIES uses the explicit SoftEng fallback role,
input revision `0b26fd3c5199602ff92241d11fd4240d0b44cf65`, read-only. Inputs:
`docs/design/DES-044-calorimeter-digitization.md`,
`software/analysis/calorimeter_digitization/reference.md`, and pinned external
RecCaloDigi/k4FWCore sources. No writable paths. Deliverable: minimal dependency
closure and runtime validation plan for the original Gaudi processor, including
macOS/Spack constraints. Completion: bounded findings with exact source pins;
no physics acceptance or nested delegation.

Assignment PR123-SOFTENG-SMOKE uses the same explicit SoftEng fallback role and
input revision, write mode owning only `software/env/key4hep_smoke.py`. Deliverable:
a deterministic nonempty-plus-empty EDM4hep event smoke test that invokes the
original Gaudi processor through k4run, then checks persisted IDs, energy, links
and EventHeader/SimHit retention. Main agent owns integration and execution.
Completion: script syntax checked; actual runtime evidence reported separately.

## Scope and evidence

New bounded follow-up to PR #123 on its branch, starting at
`0b26fd3c5199602ff92241d11fd4240d0b44cf65`; initial worktree clean.
The parent workspace contains many unrelated worktrees; they were preserved.
Related: issue #117, PR #118, DES-044 and ADR-008. The public PR comment was
read through the GitHub connector, with only its login/body/URL retained.

## Selected conversation

- User, exact request: “There's a comment on PR #123, can you address and answer:
  - if it's possible
  - if so, add the necessary software as git submodules and install versus the local spack environment”.
- `trahxam`, public comment, exact: “Why can you not install the necessary frameworks exactly?”
  Source: https://github.com/asalzburger/nodd/pull/123#issuecomment-6684945961
- Assistant, paraphrase: the earlier task established absence, not technical
  impossibility; investigate and install a separate pinned runtime over Spack.

## Commands and validation

- Skill preflight returned 2 for changed setup/Spack lock fingerprints; warning
  reported before dependent work. The installed acts-spack workflow was read.
- `software/env/run.sh python3 software/env/doctor.py` passed: DD4hep/DDG4
  imports, Geant4 11.4.3 and twelve dataset presence checks. Setup/lock hashes
  match the prior report. `sysctl`/`ps` sandbox denials remain visible setup
  warnings; dependency paths and runtime were independently checked.
- Spack inventory: DD4hep1.38, Geant4 11.4.3, ROOT6.40.04, EDM4hep1.1.1,
  podio1.8, CLHEP2.4.7.2, GSL2.8, nlohmann/json3.12.0 present.
- Initial Gaudi v39r4 configuration failed because it requests boost_system,
  removed in installed Boost1.90. The selected v41r0 supports Boost1.90; its
  required Python/fiber/thread/log components are absent from Spack's build.
  Add a local same-release Boost build plus range-v3 and Microsoft GSL headers.
- Source acquisition is explicitly authorized by this task. Local `git fetch`
  first failed sandbox DNS; authorized network acquisition then succeeded.
  No shared Spack installation, lockfile, setup or registry is edited.

## Token accounting

Exact client per-turn input/output counters and stable thread IDs are unavailable
for this task, including its explicit SoftEng assignments. Usage remains empty;
no estimates, fabricated IDs or overlapping parent/child totals are recorded.

## Decisions and outcomes

The original EDM4hep-native Key4hep route is installed locally over Spack. Eight
new source gitlinks pin Gaudi, k4FWCore, k4RecCalorimeter, k4SimGeant4, Boost,
range-v3, Microsoft GSL and MarlinReco. The original RecCaloDigi algorithm bytes
and GeoSvc sources are unchanged; a narrow CMake wrapper omits unrelated
reconstruction/simulation packages. The shared Spack environment is unchanged.
The source/build/runtime recipe, compact runtime hashes and source catalogue
are reviewable in PR123. Current missing-runtime blocker is resolved; the ODD
comparison and physics gates remain open. No geometry, response parameter,
calibration, design sign-off or physics acceptance changes.

Explicit SoftEng fallback assignments produced a dependency-closure review and
the initial smoke script. The coordinator reconciled and executed it, corrected
activation/fixture issues and owns the final result. No native profile loading
or separate physics review is claimed. Their separately exposed exact token
counters were unavailable.

### Build and smoke corrections retained

- Boost CMake first returned1 because Python is opt-in; enable
  `BOOST_ENABLE_PYTHON=ON`. Boost then built and installed successfully.
- Gaudi v41 configure first returned1 because its optional ZSTD finder requires
  absent pkg-config; disable the unused optional Gaudi ZSTD feature. Spack's
  own zstd and ROOT/podio capabilities are unchanged.
- Gaudi compilation then returned1 with range-v3 0.12.0's nonportable standard
  forward declarations against current libc++. Pin upstream commit
  `5ba39112d2eafbb3c851a16a537f29b445022998`, which contains the compatibility
  correction; no local source patch. Reinstalled headers, then Gaudi built.
- `make key4hep JOBS=12` returned0, compiling/installing the full selected stack.
  Later k4FWCore/reference stages were reinstalled with explicit shared
  `GAUDI_INSTALL_PYTHONDIR=python` and `GAUDI_INSTALL_PLUGINDIR=lib` because
  downstream defaults differed from the existing Gaudi install layout.
- Smoke1: Make returned2, original command1, missing k4FWCore Python module.
  The explicit install layout above fixes that mismatch.
- Smoke2: original command1, DD4hep could not find the XML-reader factory.
  The protected macOS shell stripped DYLD_LIBRARY_PATH; restore Spack's paths
  from DD4HEP_LIBRARY_PATH inside the runtime shell before launching Python.
- A standalone DD4hep diagnostic reached material parsing, then aborted134;
  smoke3 with restored paths reached the same hand-written fixture-material
  failure (original command139, Make2). These failures did not involve a
  production detector or algorithm-source change.
- Replaced that hand-written material fixture with copied, hashed installed
  DD4hep element/material catalogues. Smoke4 stopped before processor execution
  because thisdd4hep.sh is not an executable discoverable by shutil.which; use
  the verified DD4hepINSTALL environment instead. Make returned2.
- Final actual command:
  `make key4hep-test KEY4HEP_TEST_WORK="$PWD/build/key4hep-smoke-5"` returned0.
  Two events, two input cells, one accepted, one rejected and one empty event.
  Accepted energy exactly2 MIP, residual0 against the predeclared2e-6 MIP
  tolerance; 64-bit ID, headers, retained inputs, truth links, position and
  earliest time all passed. Gaudi configured, initialized, processed, finalized
  and terminated successfully. Compact receipt in
  `docs/validation/issue117/pr123-runtime.json`; full ROOT/logs remain ignored.

## Changes and revision links

The paired JSON owns the complete changed-file inventory. Related records:
ADR-008, DES-044, issue117, PR118 and PR123. Six new build-support source
catalogue entries; existing MarlinReco/RecCaloDigi source identities unchanged.

## Follow-up

Run the deferred ODD original-framework same-hit comparison, then statistical
noise and muon/electron/photon response studies with the existing validation
plan. Resolve the independent endcap issue/PR split with the maintainer. No
physics campaign or upstream full test-suite pass is claimed by this install.

### Repository closeout checks

- Software gitlink/pin audit, project-record validation (101 tasks/54 documents/24
  reviews), Python syntax, zsh syntax and whitespace checks passed.
- Session validation passed after the activity-schema correction.
- Per-PR-only interaction sync left PR118 stale because this session references
  both PR118 and PR123. Synchronized all affected records; interaction
  validation then passed105 records. Canonical token counters unchanged.
- Token-site validation passed438 disjoint turns. First preview command failed1
  because repository output must be under `_site/`; corrected output to
  `_site/pr123-token-preview`, then build passed.
- `session_log.py summary --format json` passed. Repository-wide observed totals
  are2,113,297,698 input and9,790,364 output across438 recorded turns;89 sessions
  lack usage. These historical repository totals are not this task's usage.
  This task and its SoftEng turns have unavailable counters and empty usage.
- After installation, setup and Spack lock SHA-256 values were re-read and
  match the report exactly; shared configuration remains unchanged.
