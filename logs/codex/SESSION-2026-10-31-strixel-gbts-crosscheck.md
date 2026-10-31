# SESSION-2026-10-31-strixel-gbts-crosscheck — GBTS single-particle reconstruction versus strixel length

## Scope and selected request

Contemporaneous local prototype extends DES-042 using DES-041 reconstruction.
User: “Now cross-check GBTS reconstruction for the single particle cases with the different strixel lengths.”
Start revision `4ea4af17727020bac2ba8f5e2f6172378711c15a`; clean source tree,
with task session pair created before execution. The branch was already two local
commits ahead of its remote. Previous external PR publication was rejected by
automatic approval review; no publication is authorized by this new request.

## Protocol and assignments

The governing DES-042 amendment was saved before implementation. It declares a
PROTOTYPE, complete 80-case matrix, 1,000 generated events/case, frozen Gaussian
response with only strixel local-v sigma scaled, existing pixel-only GBTS,
all-system CKF, fixed geometry/material/3T and hypotheses/cuts. No retuning.
Statistical uncertainty and response-model limitations are required outputs.

Explicit role fallback through repository workflow; native profile loading is
not claimed. Assignments use the full initial revision and pinned Git inputs:

- `STRIXEL-GBTS-SoftEng-01`, child `/root/strixel_gbts_softeng`: runtime/campaign,
  four new owned files, native smoke; [assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/softeng-01-assignment.json).
- `STRIXEL-GBTS-PhysVal-01`, child `/root/strixel_gbts_physval`: separate read-only
  protocol assessment; [assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/physval-01-assignment.json).
- `STRIXEL-GBTS-SoftEng-02`, child `/root/strixel_gbts_analysis`: analysis,
  retention and plots, three disjoint owned files;
  [assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/analysis-01-assignment.json).

Children may not delegate, publish, modify shared dependencies or frozen helpers.
Coordinator owns scientific integration, project tracking and final evidence.
Separate final review must target an exact committed evidence revision.

## Commands and checks

- Node preflight returned exit2: setup script/Spack lock fingerprints differ.
  User warned; shared dependencies were not changed.
- Fresh runtime `source software/env/truth_tracking.sh`, imports `sys, ROOT,
  acts, acts.examples, dd4hep` passed (Python3.14.5, ROOT6.40.04).
- `workflow.py prepare` passed for all three bounded assignments.

## Results and revisions

Protocol assessment completed: [PhysVal-01](SESSION-2026-10-31-strixel-gbts-crosscheck/PhysVal-01-result.md) supports the qualified scan, with pairing/precision/model gates. Execution in progress. No detector or accepted baseline change.

## Token accounting

Exact disjoint client-reported counters are not exposed in this client/tool
surface. Usage stays empty; no estimates or private client state are collected.
The current coordinator turn is incomplete. Final session validation and summary
remain to be run; observed sums are unknown, not zero.


### Coordinator regression checks

The pre-existing DES042 suite passed22 tests. Analysis runtime imports passed
NumPy2.4.6, uproot5.7.7, Matplotlib3.11.2 and unrooted. ACTS supplier checkout
remains clean at355ea68493b326956756c9386d2fd9eaf9328568. Token dashboard validation
passed309 disjoint observed turns; these pre-existing totals are not task usage.
Initial project/session validation failed due to new record fields (`in_progress`
instead of `active`, incomplete activity schema); corrected records then passed
81tasks/42documents/23reviews and217session records. No check was weakened.


### Native implementation and bridge pilot

[SoftEng-01](SESSION-2026-10-31-strixel-gbts-crosscheck/SoftEng-01-result.md)
reports9focused tests and8completed2-event smokes. Coordinator independently
ran the unchanged classifier and [bridge](../../software/analysis/strixel_reconstruction/bridge.py)
for the three0.5mm smoke populations (Fatrasmuon/electron, Geant4electron):
every original portable observable and NaN mask matches the same two retained
reference events exactly. [Bridge pilot evidence](SESSION-2026-10-31-strixel-gbts-crosscheck/smoke-baseline-bridge.json).
Two adversarial bridge tests pass. Native [smoke summary](SESSION-2026-10-31-strixel-gbts-crosscheck/native-smoke-summary.json)
is a development check with dirty-source hashes; full campaign must run at the
new committed source freeze. Physical hit/pixel/seed pairing is separately audited.


### Frozen production launch

All28new tests passed; source freeze is
`8c45136098d1e4d407c4d2f96e3590bb78eb6b75`. On2026-10-31 at observed06:28:10UTC,
started `source software/env/truth_tracking.sh` then
`python -B software/analysis/strixel_reconstruction/campaign.py launch --output
build/strixel-gbts-production --jobs 3 --write-root`. Unified execution session21933.
Controller begins the costly Geant4electron100GeV cases first; each case uses
one native thread in a fresh subprocess. Keep HEAD fixed until all queued
native cases finish so every report identifies the same scientific source pin.
Mandatory full audit/hit ROOT and optional measurement/track ROOT are retained.

Separate PhysVal02 now reviews exact8c45136 source/development evidence through
[assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/physval-02-assignment.json).
No production-stopping bug found in initial review. An analysis-only refinement
will label zero-discordance paired-bootstrap intervals as degenerate and add an
exact finite-sample discordance/contrast bound; no native rerun is implicated.
SoftEng03 owns only a new offline ROOT persistence wrapper and focused tests
through [assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/softeng-03-assignment.json).
It composes the frozen auditor using temporary two-level views, with exact80
coverage and retained/native hash binding. No native runtime edits authorized.

SoftEng02 analysis implementation passed17scientific/provenance tests, actual
four-pitch2-event retention and exact bootstrap/report replay. Pilot8PNG/PDF
figures and six explicitly synthetic populated QA figures rendered and were
visually inspected. These are development checks, not production performance.
Root hit reader materializes one case at a time; prior5000-eventG4electron100
reference has794154hits, so current1000-eventcases are expected to remain
manageable. Memory usage is not a measured performance claim.


### Independent source review and analysis-only remediation

[PhysVal02](SESSION-2026-10-31-strixel-gbts-crosscheck/PhysVal-02-result.md)
reviewed exact8c45136 and independently repeated28tests, all eight smoke hashes,
all25hitROOTcolumns and three baseline bridges. No native-stopping issue.
It identified a medium zero-discordance bootstrap qualification and low net
measurementcount naming issue. Coordinator corrected both in offline analyzer
and added an adverse test:18analysis tests now pass. Native executing files and
HEAD are unchanged; final independent review must assess the correction at its
later committed evidence revision. The muon2-eventpilot had only pixels; electron
smokes directly checked system4/5scaled variances. Full native samples must
supply actual all-system sensitivity and statistical results.


Corrected offline analyzer replayed the retained4pitchpilot with400replicates;
exact--verify passed and8PNG/PDF figures rendered. This intentionally updates
pilot output to the corrected source hash; original PhysVal02 pilot hashes stay
in its review record as historical assessed evidence. HEAD/native source stays
8c45136. Zero-discordance contrast bounds are pointwise and not an equivalence
or simultaneous multiple-comparison claim.


### Offline persistence and repeatability checks ready

[SoftEng03](SESSION-2026-10-31-strixel-gbts-crosscheck/SoftEng-03-result.md)
adds isolated ROOT auditor composition and7adverse/synthetic tests, independently
rerun by coordinator. Fullnew suite now36tests passes; session217and project
81tasks/42documents/23reviews pass. Actual80caseROOTaudit remains pending.
README now documents fresh native runs with--write-root, portable retention,
400bootstrap replay, bridge, ROOTre-audit and unrootedplots. Requirements reuse
the existingglobal pinnedlock; no shared dependencies installed/changed.
Observed analysisPython3.11.15, NumPy2.4.6, uproot5.7.7, awkward2.14.0,
Matplotlib3.11.2, unrooted0.1.0rc1 at728465dce0c5cd5b876e67392e3858de6e982d05.
The ignored native plan is retained with originalSHAand collision-free logical
paths; actual environment snapshot is separate from stale node registry.


### Full-size retention pilot and bounded parallel analysis

The serial 1,000-event/four-pitch Fatras electron100GeV group completed
retention and400-replicate statistics at observed07:11UTC, exit0. Native
controller21933 continues with fixed HEAD8c45136 and unchanged executing
runtime/campaign. Serial pilot lives in ignored
`build/strixel-gbts-production-pilot`; its analyzer SHA is
9c471fc0916f603fcf528041dfd23743843d549d631dafa173c9218ef053292f.
All8unrootedPNG/PDF pilot figures rendered; the longitudinal PNG was visually
inspected. The full matrix will populate the second momentum row absent from
this one-momentum development figure.

[SoftEng04 assignment](SESSION-2026-10-31-strixel-gbts-crosscheck/softeng-04-assignment.json)
owns only analyzer/test files for bounded per-case process retention, with
spawn, deterministic inventory, failure propagation and source-immutability
guards. ExplicitGO followed observed serial process exit0, never inferred from
artifact presence. It must show every scientific NPZarray, summary, configuration,
profile/bootstrap group and report text unchanged against the full-size serial
reference. This optimization changes no native reconstruction or statistical
kernel. New independent final review remains required.


[SoftEng04 result](SESSION-2026-10-31-strixel-gbts-crosscheck/SoftEng-04-result.md)
completed bounded retention. Coordinator independently repeated46tests and all
316arrays, group/bootstrap statistics, configurations/summaries and Markdown
comparisons against serial reference: exact. Standalone CLI verification exited0.
Native full campaign continues without source/HEAD changes. Current node disk
has188GiB available; actual peak memory remains unmeasured.


### High-energy Geant4 pilot and non-target-noise qualification

The complete four-pitch ×1000-event Geant4electron100GeV retention/analysis
finished exit0 in ignored `build/strixel-gbts-geant4-production-pilot`. Full
generated/transported JSON records, all persisted hit payloads and pixel/seed
inputs match across pitches. Fine-u strixel fingerprints differ in70/119/167
events at1/1.5/2mm; long-strip fingerprints differ in58/105/147 events. Counts
and primary measurement associations remain identical. Thus identical pixels
and seeds do not by themselves isolate the longitudinal response. This is
consistent with the documented bounded-Gaussian retry/RNG-consumption mechanism;
no native configuration or helper change is warranted.

Coordinator amended only offline reporting to flag the event union of changed
non-target physical inputs, broaden the attribution warning, and test the case
of identical pixels/seeds with changed strixel fine-u/long-strip measurements.
All47tests pass. This reporting amendment follows SoftEng04's exact6dsource
benchmark; [byte-exact source snapshots](SESSION-2026-10-31-strixel-gbts-crosscheck/analysis-review-sources/README.md)
preserve both development analyzer revisions and the parallel tests. Native
HEAD remains8c45136. The final exact-evidence review must inspect this amendment.

At100GeV, Geant4electron primary matching spans77.1–79.1%; wrong-charge fractions
span13.1–13.9% among matched primaries, and relative-pT errors beyond50% remain
about55%. These are existing frozen-baseline fit limitations, not an efficiency
validation or evidence that longer strixels cure momentum reconstruction.
The full matrix will retain fake/secondary, charge and residual/pull tails.


[Reporting amendment check](SESSION-2026-10-31-strixel-gbts-crosscheck/reporting-amendment-check.json)
replays both complete electron100GeV pilots without overwriting their historical
outputs. All point statistics and400-bootstrap results remain exact; all prior
fingerprint diagnostics remain exact. New non-target changed-event unions are
[0,10,25,38] for Fatras and[0,70,119,167] for Geant4. Current analyzer SHA503bd05a
adds reporting only; all native inputs, retention kernels and numerical statistics
are unchanged.


### Muon sensitivity and repeatability integration

The current503bd05a analyzer completed the Geant4muon100GeV four-pitch ×1000
pilot with jobs3, exit0. It exercises5805strixel measurements at each pitch.
For the central0≤|eta|<1 sample (269generated,267matched at every pitch), z0
central68.27 widths are12.323/13.501/13.739/14.177µm; theta widths
61.764/68.922/70.088/71.921µrad. Thus2mm ratios are1.1505 and1.1645. These are
preliminary point statistics; final full-matrix bootstrap uses its documented
group ordering. Whole-sample matching is987/989/989/989 of1000. Full transport
and pixel/seed pairing passes; non-target measurement changes affect0/3/9/15
events. No calibration or detector-choice conclusion is inferred.

Added a step to the existing pinned-unrooted CI job for47tests, portable full
statistics/bootstrap/report replay,20baseline bridge verification and40figure
regeneration. Actual native ROOTaudit requires local ignored outputs. Remote CI
has not been run or claimed; local full-matrix equivalents remain pending.


### Complete native matrix and offline source freeze

Native controller21933 exited0. At observed07:53:54UTC all80cases had completed
1000events each, all declaring source8c45136098d1e4d407c4d2f96e3590bb78eb6b75.
[Campaign check](../../docs/validation/DES-042/gbts/campaign-check.json)
revalidated every case identity and all recorded output SHA256values. No native
failure or retry. All47tests pass at the final offline source (3.140seconds);
project/session records and diff whitespace checks pass. Earlier DES042 native
point-statistic/source audit also passes:12cases,76032statistics,24servicecases.

Freeze offline analysis/reporting, ROOT wrapper, tests, CI integration and
development provenance in a new local commit before retaining the complete
matrix. Native and original scientific sources remain unchanged. No remote
publication is authorized or attempted.


Offline source freeze is `fcc74d72fc81a9f9e5f97056bac0ca84971671cb`, including
final analyzer SHA503bd05aa6fff1164dda466eba8a34dfa2852f3f6888db3e5c3b082cca7d4fd8.
At observed07:54:22UTC launched complete retention/statistics with analysisPython:
`analyze.py --source build/strixel-gbts-production --output
docs/validation/DES-042/gbts --replicates400 --jobs3`; unified session24764.
Native controller and its monitor both ended successfully at80/80. No source
edits are permitted during this executing offline analysis. Full baseline and
ROOTaudits can read the finalized inventory concurrently with immutable
statistical reduction once retention completes.

[Full-size bridge pilot](SESSION-2026-10-31-strixel-gbts-crosscheck/full-size-baseline-bridge-pilot.json)
independently compares all42 original observables/NaN masks in each of three
100GeV species/transport samples against identical1000eventIDs in frozen5000
references: all exact. Complete20-case bridge remains a separate final check.


### Full baseline bridge and byte-exact ROOT-audit remediation

All20 fresh0.5mm1000-event subsets reproduce812 original portable observables
(including NaN masks) against frozen5000-event references. Every Fatras-muon
historical1000-removal budget is provably nonlimiting.

First full ROOTaudit exited1 in the new wrapper's summary-binding check. The
wrapper re-serialized parsed JSON and re-sorted integer PDG keys as strings.
This changes order (numeric22 before211 versus lexical211 before22).
[Byte binding check](SESSION-2026-10-31-strixel-gbts-crosscheck/summary-byte-binding-check.json)
proves all80 exact decompressed serialized summaries match their original native
summary hashes after removing only the documented one trailing LF;44 parsed and
re-sorted forms differ. No numerical/native/retained source is changed.

The isolated new wrapper now hashes those exact serialized bytes, preserving the
original hash criterion. Added an actual integer-key-order regression and a
rebound-whitespace rejection test; all49tests pass in3.266seconds. Frozen original
auditor/analyzer and source503bd05a executing full statistics remain unchanged.
Freeze this audit-only correction locally before rerunning the full ROOTaudit;
independent final review must assess the correction and exact evidence.

PDF skill applied for read-only export inspection. Bundled pypdf verifies a
single-page Geant4electron pilot and Poppler renders its glyphs/labels/intervals
correctly; the unused second momentum row is the explicit one-momentum pilot.
Final20PDF/20PNG matrix QA remains pending. No dependency installation.


### Complete portable evidence and export checks

All80cases retained; producer24764 exited0 with20paired groups. Full
`--verify` session22865 exited0 with exact point statistics, all400joint event
bootstrap results and Markdown. Corrected ROOTwrapper at6bc69e1 passes all80
cases and5406814persisted variance marginals; exact re-audit session51315
exited0. Baseline20bridge and exact bridge replay pass812original observables
including NaN masks. Native/frozen sources and numerical analyzer503bd05a
remained unchanged during all checks.

Sourceplot headings use ASCII hyphens for PDF export; no numerical change.
Actual unrooted fullmatrix produces40PNG/PDFfiles; a fresh-directory rerender
and fullmanifest match byte-for-byte. All20PDFs are single-page and render in
Poppler; inspected the20-panel contact sheet and detailed Geant4muoneta,
Fatrasmuonratios, Geant4electronwidths and pion efficiency: no clipping, overlap
or broken glyphs. Marker helper succeeded once immediately before creation,
expected20PDFs. Final49tests pass at current source in3.334seconds.

[Summary](../../docs/validation/DES-042/gbts/summary.md) gives all20four-pitch
efficiency rows, central100GeVmuon widths/pairedintervals, all-population100GeV
charge/momentum tails, exact pairing and retry-noise qualification. It uses
write-page editorial guidance at the repository's established destination.
[Verification record](../../docs/validation/DES-042/gbts/verification.json)
binds all source/data/export hashes and actual checks. No equivalence, physical
coarse calibration or sensor acceptance is inferred. Independent exact committed
evidence review remains the final scientific check.


### Independent final assessment and local closeout

[PhysVal-03](SESSION-2026-10-31-strixel-gbts-crosscheck/PhysVal-03-result.md)
independently assessed exact scientific evidence commit
`a9867564c4ebaeac774aa350e0f440f887916067`: zero unresolved material findings.
All105pinned objects and240caseartifacts bind;49tests and20baseline bridges
pass. The reviewer independently reconstructed1278653exactpointvalues, all80
Wilson/paired-efficiency intervals and first-principles selected400-resample
centralmuon z0/theta width/ratio intervals. Selected3actual100GeVROOTcases
pass303741marginals plus event/candidate/representative gates. All80ROOTrecord
bindings,40figurehashes and20single-pagePDFs checked;4figurefamilies rendered.
Reviewer did not repeat the entire bootstrap/export campaign or all80rawROOT
audits; coordinator's complete replays are separately retained. No scientific
source/data/figure change followed this exact-revision review.

Task TASK-TRACK-STRIXEL-GBTS is complete as a local isolated prototype. This
assessment grants no human design sign-off or acceptance. The result remains a
frozen Gaussian-response sensitivity scan with boundary-retry/noise coupling,
fixed material and substantial pre-existing high-pTmomentum failures. Physical
coarse calibration, occupancy and an explicit services/material redesign remain
conditions for later detector-selection claims. No remote publication attempted.

Local task commits are96748307ef5b0f5bee21051df91e56d8b2c4d99d,
8c45136098d1e4d407c4d2f96e3590bb78eb6b75,
fcc74d72fc81a9f9e5f97056bac0ca84971671cb,
6bc69e1c25310f20e3f04a53fcbae6d3104beee5 and
a9867564c4ebaeac774aa350e0f440f887916067. A subsequent metadata-only local
closeout commit records this review/assignment, session and task disposition;
its own hash cannot self-reference in its contents.

Session summary and token dashboard validate/build pass. The309observed turns
are historical project coverage: input1300427748/output6206186, combined
1306633934; these are not task counters. Current task usage remains empty and
unknown. No estimates, duplicate ownership or private client-state collection.
Observed scientific closeout clock is2026-10-31T08:37:32Z; actual task start is
unknown, and the active coordinator turn has no exposed final usage counter.


Final closeout validators pass:217sessionrecords,81tasks/42documents/23reviews,
eightroles/threeworkflow skills and Gitwhitespace check. Scientific source and
all retained evidence remain exactly at the independently assessed revision.
