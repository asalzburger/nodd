# SESSION-2026-10-19-odd-idres-comparison — Reproducible ODD tracker IdRes comparison

## Scope and evidence

Contemporaneous selected record, 2026-10-19. Started from main at
`33a607b70214532cd265623241b0c250ca0da361` in a new isolated worktree/branch
`codex/odd-idres-comparison`; no initial changes. Existing worktrees and their
unrelated changes were preserved. Related designs: DES006/013/018–023.

## Selected conversation

User requested IdRes SVGs for original ODD, extended ODD to |eta|<4, and the
extended detector with adapted outer pixel disc aperture: hits, material and
pitch/sqrt(12) momentum resolution vs eta; retain every required input/output
for future plotting and create a Documentation PR. The user clarified:
“Use the existing tracker prototype layouts.”

Assistant used the current maintained prototype JSONs, reducing them to ideal
cylinders/discs. Original ODD is the pinned c167363 study revision. Common
current prototype pitches and historical DES006 local-layer material allowances
are explicitly distinguished from original ODD digitization and detailed DD4hep
material. No new production geometry or design approval is introduced.

## Decisions and outcomes

- Seven SVGs and their plotting manifests; complete expanded geometry JSON and
  source extraction/hash map; all raw geom/res/hits/X0/log outputs retained.
- 9 nominal IdRes runs cover signed eta -4..4 step0.01, pT1/10/100GeV,
  vertices -150/0/+150mm and separate2/3/4T processes:64881 finite fit rows.
- 7209 independent technology hit/material profiles; every raw hit count and
  origin material sum agrees with the independent calculation at printed precision.
- 54 near-zero-material controls agree with independent SVD curvature covariance
  within half the printed1e-6GeV^-1 unit using the same0.3 conversion convention.
- Short strips are classified as pixel-like by IdRes because their coarse sigma
  is144um. Technology plots therefore use JSON metadata, preserving all raw counts.
- The DES018 aperture reduction leaves every sampled extended hit-ID list,
  material profile and resolution unchanged. At eta4/origin/100GeV/3T,
  sigma(1/pT) improves223.919->22.959TeV^-1 from original to extended, but the
  latter still gives pT*sigma(1/pT)>1. This is not a Gaussian relative-pT resolution.
- Material is only the explicit1/1.5/2%X0 per-layer fixture. No beam pipe,
  distributed services, detailed passive supports, reconstruction or finite-module
  transport result is claimed. Existing design states and accepted evidence stay unchanged.

## Commands and validation

Actual successful checks:

- Disposable IdRes build using `software/env/build_idres.py`, pinned unchanged
  source d54d0e3c465cc0308becb737b04364ce5c68ce16; Apple clang21/GSL2.8.
  Compiler warnings retained in docs/validation/ODD-idres/build.log.
- `python3 -B tools/odd_idres/prepare.py --extract-odd <pinned-ODD>`.
- `python -B tools/odd_idres/run.py --source <pinned-IdRes> --binary build/odd-idres-engine/bin/idres`.
- `python3 -B -m unittest discover -s tools/odd_idres -p 'test_*.py' -v`:8 passed.
- Existing tracker covariance controls:3 passed; existing IdRes adapter controls:4 passed.
- `python3 -B tools/odd_idres/verify.py`:all15 runs,64881 fits,7209 profiles,
  54 controls,7 SVGs, raw/source/producer hashes and CSV/JSON agreement passed.
- Re-prepared geometry JSON compared byte-for-byte with the committed input.
- All seven PNG previews visually inspected; captions/legends moved outside
  plotting axes to preserve data visibility.
- `python3 -B tools/project_records/validate.py`:67 tasks,36 documents,21 rounds validated.
- `python3 -B tools/session_logging/session_log.py validate`:184 records validated.
- `python3 -B tools/token_usage/build.py validate`:passed; historical totals are
  unrelated to this session's unavailable usage.
- `git diff --check`:passed.

An initial repeated-SVG byte check found only a Matplotlib clip-path ID difference
in the vertex figure. The producer now canonicalizes clip IDs; numeric data and
geometry were unchanged. The final repeated-plot check passed: all seven SVGs and the figure manifest regenerate byte-for-byte. A session-validator status spelling error was corrected to the required PASS enum before publication.
Initial sandboxed GitHub network access failed; the authorized network-enabled
fetch/auth checks succeeded. No credential data is retained here. Nonfatal
font-cache warnings were handled through the local writable plotting cache.

## Changes and revision links

Files are inventoried in the paired JSON. This task adds the study under
`docs/validation/ODD-idres/` and `tools/odd_idres/`, a CI verification step,
README link, source-catalogue observations and project task TASK-PUB-ODD-IDRES.
Scientific/documentation commit: `e777e84e6062e800db8a9fbe69a510a2ee6ae0dd`.
Opened and attached [Documentation PR89](https://github.com/asalzburger/nodd/pull/89),
base main; no merge performed. All local validation passed; hosted CI was pending
at the first PR snapshot. This closeout is recorded by ordinary follow-up commit.

## Token accounting

Exact client-reported counters for this active turn are unavailable. `usage`
remains empty; observed input/output totals for this session are unknown, not
zero. `session_log.py summary --format json` ran successfully; repository totals
cover other disjoint recorded turns and are not allocated to this task. No
private client store was inspected and no counters were estimated.

## Follow-up

Review the Documentation PR and the stated ideal-layer/material/response scope.
Physical DD4hep material comparison, source licence/access closure and full
reconstruction remain separate tasks. No sign-off is requested or inferred.
