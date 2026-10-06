# SESSION-2026-10-06-pixel-disc-eta-trim — Eta-limited outer pixel-disc apertures

## Scope and selected conversation

Contemporaneous bounded follow-up to merged PR42. User request (exact):
“Given the tracker coverage to |eta|<4 and the luminous region the outer pixel
discs can drop some of the inner rings, optimize that.” User clarification
(exact): “Use pT ≥ 1 GeV”. Earlier authorization permits local ACTS execution,
follow-up PRs and ongoing curated resource logging. No design sign-off is inferred.

The clean task branch codex/pixel-disc-eta-trim starts at PR42 merge
f2af2714dadd30a722f5ece11d0fd04e92cbfd39, merged 2026-10-06T07:30:12Z into
codex/issue38-disc-overlap. PR41 is closed, not merged, and origin/main does not
contain PR42. This follow-up therefore targets that prototype branch. Primary
main remains at 7b559d0fbe0287848c46cb1e05c833e0579c43d8; pre-existing uncommitted
logs and all scientific files are preserved. The sister ACTS checkout remains
at 355ea68493b326956756c9386d2fd9eaf9328568 with its prior dirty files untouched.

## Contract, decisions and results

DRAFT DES018 was created before code, governing isolated whole-inner-ring removal
from both frozen DES017 layouts. Classifications distinguish PDG section 49.5.2,
page 8 equations 49.47–49.48 (FACT), the uniform-field chord bound (INFERENCE)
and the explicit geometric, momentum and 0.10 mm screening choices. Public source
SRC-PDG-KINEMATICS-2025 was catalogued; no PDF or private material was retained.

The proof uses each actual active chip plane, convex-rectangle corner maxima,
pT >= 1 GeV, the closed |eta| <= 4 boundary, luminous z +/-150 mm, conservative
transverse square +/-1 mm and uniform axial |B| <= 4 T. Its first-outward-half-turn
and first-host-exit domain is enforced. No low-pT, secondary, scattering, energy
loss, nonuniform-field or fitted-resolution guarantee is claimed.

On either end, keep all rings on discs 1–4; remove ring 1 on discs 5–6, rings 1–2
on disc 7 and rings 1–3 on discs 8–9. Both variants retain original survivor
transforms, IDs, local axes, module heights and exact disc datums. Ring 4 on the
last disc must remain: explicit 1 GeV witnesses of both signs reach it in 4 T.
This maximizes contiguous inner-prefix deletion within the frozen catalogue.
Straight/on-axis and all-pT controls are retained as distinct alternatives.

Both variants remove 424 single-chip modules across all 18 discs, 0.162816 m²
installed active-chip area and 1139.712 W nominal heat (1709.568 W at 1.5×).
Single-ring totals become 4904 modules/chips; mixed totals 2312 modules/5012 chips.
Cooling drops from 288 to 248 circuits and from 576 to 496 feed/return legs.
The common r27..188.5 mm, 6.3 mm sandwich and three mounting tongues stay intact;
empty pickup windows require engineering closeouts. No full plate mass saving
or enlarged support bore is claimed. Survivor support screens pass.

Services sum the actual heterogeneous first eight discs plus unchanged barrel;
inherited disc-9 bypass and an adverse all-nine-disc neck control are separate.
Fixed trunk r192..231.7 mm and neck outer radius 222 mm remain. Positive mixed
reference trunk improves 1.089→1.032× and neck 1.474→1.397×, still FAIL; every
reference/adverse scenario still fails. Baseline holes, guard and warm thermal
failures remain. Maximum selected silicon overlap remains below 20% on the
unchanged original annulus/full union. No engineering or coverage failure is
relabelled as acceptance.

## Execution and checks

acts-spack preflight --require-sources exited 2 for changed setup/lock fingerprints
and unstaged full sources; user warned before dependent work. Actual installed
ACTS runtime was independently verified: Python 3.14, NumPy 2.5.3, Shapely 2.1.2,
Matplotlib 3.11.2 and sensitive-surface bindings. Reused the existing isolated
Shapely target; no shared package installation, ACTS rebuild or sister edit.
Numerics used this_acts_withdeps.sh and the installed ACTS virtual environment;
native execution used the authorized acts_setup.sh / acts run acts-nodd workflow.

The screening run and native run completed with final verified artifacts.
Each variant preserves all exact hit IDs for 1906 analytic tracks (11547 single
or 11722 mixed hits) and 182 native in-scope tracks. Two out-of-scope controls
show intentional deleted hits; four exhaustive last-disc checks pass. ACTS
uses EigenStepper finite supporting-plane targets and real RectangleBounds;
neutral trajectories use analytic/equivalent charged zero-field controls.
No global navigation or passive/material transport is inferred from these audits.

All 9 focused tests, 7 inherited support controls and 31 dashboard tests passed.
A post-completion native process poll returned Unknown process id; the complete
passing native artifact was verified, and no audit was rerun to hide that tool
failure. Original process exit values were not retained and stay unknown.
The report was regenerated after visual label improvements and table escaping;
study/native hashes and old evidence remain unchanged. Updated figures inspected.
Actual check details and file inventory are in the paired JSON. Scientific source
execution is the dirty f2af2714 baseline plus exact producer/input hashes; later
result commits must never replace execution provenance.

## Token accounting and follow-up

Exact metadata-only recovery identifies implementation turn
01a11028-aa17-7a02-9f78-1e51445b27a1 in client thread
01a10c6a-664d-72b1-afad-926c2c57312b, start 2026-10-06T07:41:02Z and ordinal 3545.
Its persisted end boundary is still null. No active or partial counters are
imported. This canonical record owns that entire bounded implementation turn
once; no prior observation is moved, split or duplicated. Model and client
version are unknown. Older project coverage remains partial, so no complete
all-project or self-inclusive token total is claimed.

One bounded post-completion usage-only recovery will import this exact turn
through the logger after verifying its closed boundaries and request increments,
then synchronize only this canonical pair/new inventory to primary with byte
checks. Its own bookkeeping turn is separate and excluded. Human review of
DES018 field/material assumptions and unresolved service/mechanical/thermal
qualification is still needed; status remains DRAFT/PROTOTYPE.

First closeout logger validation exited 1: PASS requires an observed zero exit.
Scientific execution exits remain unknown; separate retained-artifact verification
and expected-ancestry assertions were run with observed exit zero and recorded
correctly. This fixes accounting semantics without rerunning scientific inputs.

The staged whitespace check exited 2 on Matplotlib SVG path lines. The report
producer strips only trailing SVG whitespace; regenerated DES018 figures and
manifest preserve all scientific screening/native/source inputs.

## Publication and primary log synchronization — 2026-10-06

Scientific deliverable b54899ade5054d2d9f98e792344ca58ef482b7c1 was normally
pushed and PR43 created at 2026-10-06T08:08:35Z, verified OPEN on
codex/pixel-disc-eta-trim with base codex/issue38-disc-overlap. Full parent and
origin/main-relative whitespace checks pass. PR body contains all nine disc
datums/counts/removals, scope, proof, witnesses, savings and unresolved failures;
figures/full report are linked. New PR attached to this chat. Curated PR snapshot
records the first published scientific head, without replacing execution hashes.

Primary pair creation used exclusive writes after confirming absence, original
main SHA and no tracked modifications. Only this task's pair was added; logger
validated 108 records. Saved ignored byte preimages allow a comparison before
subsequent task-record updates. All previous primary records stay untouched.
Initial hosted run37434150482/job112171724821 is in progress. Final metadata-head
hosted result will be verified before final response; exact conclusion/time and
metadata result commit will be added by the bounded post-turn accounting update.
No partial current-turn usage is recorded.

The first PR43 dashboard snapshot lacked its stable ID; validation rejected it.
Added PR-43 and reran strict validation/build. Scientific evidence unchanged.

## Completed-turn accounting correction — 2026-10-06

Authorized metadata-only recovery verified the exact implementation turn is
closed at 2026-10-06T08:20:16Z, persisted start/end ordinals3545/4233 and usage
ordinals3560..4232. All78 cumulative request increments reconcile with reported
last-request counters. Recovery read only thread/turn metadata and token_count
events; no conversation items or raw private state. The curated inventory is
`logs/usage/USAGE-2026-10-06-disc-eta-apertures.json`, with original recovery
source `build/issue38/eta-usage-only-20261006-0946.json`. Verified usage SHA256:
`2b8f992571f6a8931d75e5c178c53caaa5a153f9f1743cfd848df7ca9f8bffd2`.

Logger dry-run and import succeeded, adding this exact turn once to this owner:
input10497559, cached input10196608, output73762, reasoning output27589,
total10571321. Cached/reasoning counts are subsets. Reloaded JSON after import
before setting the actual completion time and closed task status. Model/client
version remain unknown. This separate bookkeeping turn is excluded, and older
project coverage remains partial; no self-inclusive or all-project total claim.

Final hosted run37434294081 succeeded on exact7c567f99888046e8500b177b820de1dcb3f397de:
build112172713912 completed2026-10-06T08:17:47Z, run updated08:17:48Z;
deploy112175059565 skipped. Initial scientific-head run37434150482 was cancelled
when the metadata push superseded it, not a scientific failure. Preserved earlier
failed local attempts and unchanged scientific/native execution hashes.
Result commits now include scientific b54899ad and metadata7c567f9, with the
full start-to-metadata changed-file inventory and new usage inventory.

PR43 is now MERGED, observed head7c567f9, merge7057861fa3c8c137833ecedddcae0856ebd91e4c
at2026-10-06T08:23:13Z. No push or PR modification is authorized for this closed
publication target; recovered validated logs will be retained locally. First
PR-state query hit a transient TLS timeout; retry succeeded. One read used a
wrong design filename, corrected from the repository inventory. No scientific
files, prior records, counters/attributions, PR descriptions or design status changed.
The accounting heartbeat was paused before recovery and will stay paused.

Post-import logger validate/summary passed102records, with observed coverage
46/102sessions and83turns; missing coverage is explicit. Dashboard validates
43tasks/24documents/19review rounds and builds under _site/eta-usage-recovery-20261006.
Working and full prototype-parent/main-relative diff checks passed.

Safely synchronized only the updated canonical pair and new curated inventory
to primary after immediate comparison against saved pre-update bytes. Primary
logger validates109records, remains original main7b559d0 with no tracked diff.
All earlier records and current DES019 logging copies are preserved. The
recovery is retained locally; PR43 is merged, so no log-only push is made.
