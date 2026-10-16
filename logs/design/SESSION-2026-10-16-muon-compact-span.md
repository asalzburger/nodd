# SESSION-2026-10-16-muon-compact-span

## Scope

User requested addressing the comment onPR86. Reviewer asalzburger-review asks
about reducing station span5m to3m and achieving10% combined resolution at500GeV,
given the3Ttracker and study material budgets. Comment:
https://github.com/asalzburger/nodd/pull/86#issuecomment-6210895219
Start fad762857944b8f39986365bed04274a73c813ec, clean branch
codex/muon-reach-field-study. No geometry adoption or sign-off inferred.

## Bounded assignments

C2 PhysVal/MuonTech, read-only, base revision above plus proposed compact-span
study. Read .codex/agents/PhysVal.toml and MuonTech.toml, nODD review skill.
No owned files. Independently derive3m/5m field requirements at500GeV, correct
combined-fit interpretation and material distinction; assess assumptions and
later exact changed files. No external messages, edits or nested delegation.

T2 TrackTech/SoftEng, read-only repository, same base. Read role profiles and
nODD evidence skill. Run direct pinnedIdRes at200/500/1000GeV for existing nominal
LAYOUT-001 proxy and3T. Temporary outputs only under/private/tmp. No shared
runtime/dependency modification. Return source script/results, exact input and
binary hashes, numerical table and limitations. No external messages or edits.

## Outcome and checks

Reran direct pinnedIdRes at100/200/500/1000GeV:48cases, including12overlapping
100GeV controls. All raw results match separate T2execution. Central500GeV is
6.75% from printedIdRes,6.74684% from independentGLS. The combined10% target
alone thus gives no positive field minimum. The additional standalone10% target
atlocal500GeV needs0.860806T across3m for uniform internal1.3X0. At1T, standalone
is8.608% and ideal independent combined is5.312%. Preserving0.5T/5m intrinsic
precision when compressed to3m requires1.389T. Material sensitivity is explicit.

Added compact_span.py, retained high-p evidence, report and plot; linked from
parent report and project task. Added numerical controls to CI. The old stopping
tables end at100GeV; no500GeVcalorimeter transport is used. Added upper-domain
rejection to prevent accidental extrapolation. An initial overly broad lower
range rejection also caught the existing approximate CSDA cutoff iteration;
restricted the new guard to unsupported upper-energy extrapolation, preserving
all existing tabulated transport results. Lower cutoff behavior is unchanged.

No chamber or magnet geometry has been implemented. Ideal curvature combination
omits mean-loss transport, straggling and cross-system covariance; tracker angle
and curvature are correlated and are not double counted. C2closure and final
checks/publication follow.

## Token accounting

Exact root/child per-turn counters unavailable; usage is unknown, not zero.

## Published response

Published source/evidence commit 679774e16b94e211652358e59dd67bcb634745ba and updated PR86's description.
Posted the [reviewer response](https://github.com/asalzburger/nodd/pull/86#issuecomment-6211025997)
with 3m/5m comparison, target distinction, material assumptions and the1T/1.4T
candidate comparisons. C2independent physics review passed with exact file hashes
in compact-span/review.json. Numerical controls,33document/session tests and
project/session validation passed. GitHubCI is running; no pass is claimed for
the new revision. No source/field topology adopted and no human sign-off inferred.
