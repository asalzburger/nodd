# Tracker resolution optimisation

Human authorizes barrel-radius and disk-z changes inside existing envelopes;
module types and stave general structures fixed, stave counts may change.
Hit coverage must stay high or improve, target at least10 hits throughout
acceptance; improve d0/z0 and keep or improve momentum resolution using Fatras
truth tracking and residuals. Pixel endcaps may exceptionally add a disk with
homogeneous material behind it, similar to existing disks, to avoid a new
material-mapping step for this addition.

PR101 merged at04b5ee2e408803eac836eee0b48a1635dcbbe201; new isolated branch
codex/tracker-resolution-optimization starts there, preserving local native
outputs and previous branch. Explicitly authorised PROTOTYPE study, no detector
design sign-off. Read AGENTS/PROJECT, DES025, related layout/optimisation records,
coordinate/design-evidence/review-validation and acts-spack instructions.
Preflight warns changed setup/lock fingerprints; actual runtime must be verified
before native execution, no shared dependency writes.

Optional digitization question pending: recommended geometric primary with
frozen cluster-size error table and Gaussian cross-check, retaining constant3T,
pT1/10/100GeV, |eta|<=4 inherited from PR101. Main continues independent
geometry/source/objective work while awaiting the reply.

Main owns integration, study design, candidate ranking/reduction and records.
Bounded read-only SoftEng checks native geometry/material/runtime mechanisms;
SysArch checks fixed envelopes/physical constraints and feasible placements;
PhysVal independently checks metrics and baseline hit coverage. Prepare all
assignments at exact merged source before dispatch.


## Initial assessments and experiment design

OPT-SoftEng-01, OPT-SysArch-01 and OPT-PhysVal-01 completed read-only against
04b5ee2e408803eac836eee0b48a1635dcbbe201. No native simulation or changes were
performed by these assignments. Full role instructions were supplied explicitly;
native client role loading was not claimed.

- SoftEng verified Python3.14.5/ROOT6.40.04, five unchanged factory hashes,
  adapter530080c/compiledACTS355ea684, and runtime minMaxRetries10. Candidate
  compact_file plus existing factories works without changing shared software.
  Native export/selection must be regenerated and materials joined by complete
  logical roles. Calibration volume keys likewise need physical-layer mapping.
- SysArch verified source-matched compact a27b807cbeda51c21b2994fdd5f5c60f96585ff54d788209f61a3a6bdc282ed3.
  Baseline pixel radii34/60/106/182, counts12/22/18/30; nine disks/end at
  615/795/1046/1333/1645/1977/2328/2692/3070mm. R1>=31.4782mm is a one-mm
  pipe-clearance screen, not qualified installation tolerance. Conservative
  disk+collector spacing77.636mm and current cage609..3136mm bound trials.
  All-box partial transverse screens do not replace full native overlap checks.
- PhysVal joined all generated events and native unique physical measurements.
  >=10 created-hit coverage is87.425/87.245/87.165% at1/10/100GeV. In
  |eta|3..3.5 it is52.47/51.54/51.05%; |eta|3.5..4 gives64.18/63.74/63.54%.
  The existing forward deficit cannot be solved by one extra plane alone.
  Preserve pT tails and wrong-charge rates; add signed q/pT as a diagnostic.
  Per-event created and incident record counts agree; incident unique sensor
  IDs are not separately retained. All reported coverage uses generated counts.

DES040 is written before implementation, remains DRAFT/PROTOTYPE, and governs
issue103. GitHub connector issue creation returned403; authenticated CLI
creation succeeded after network-enabled retry. No public comment was posted.
The optional digitisation preference has no reply; proceed with frozen geometric
primary and optional Gaussian sensitivity check, as previously stated.


## Implementation and exploratory evidence

DES040/issue103 govern isolated tools. Source implementatione793a30 supplies
compact/material/runtime plus task-local native ACTS slab mixing. No production
assembly, old PR101 analysis/native source or shared dependency changed. Full
prepared mandates OPT-SoftEng-02 and SysArch/PhysVal02 are committed. PhysVal02
found selected-row uniqueness, eta endpoint, zero-width bootstrap, inconsistent
pull sign and stage-count ambiguities; fixes are inb6c4abe/bc5b061 with regression
controls. Every observed measured marginal is audited; unsampled groups remain
explicit. Reference ROOT statistics and all old pull histograms reproduced.

SoftEng02 completed6native100-event smokes; all100fits/0invalidcov. No-op compact,
material and calibration are exact;31particle/99tracksummary/42measurement
branches match PR101 exactly. New17controls pass in activated native runtime;
portable analysis environment passes16 with1expected native-only skip.
Maximum native material inventory closure1.94e-7, donor2 homogeneous disks are
after all sensitive faces. Physical support/cable screens reject two compact
radii families; sourceconfigs/reasons retained. Full fixed original runtime
maps/profile scalings remain a declared approximation, with component/routing
and timing qualifications.

Finite-patch screen:3000reference100GeV events,16000proposals with exact
subset/search seeds407042/408042; ledger retains every spacing rejection and
scored mutation. Screen selected865/1090/1180/1270/1355/1440/1977/2350/2465mm plus
1000mm donor2. Profiledonor2 chosen before performance because firstdisk normal
material0.1036X0 includes transition aggregate, versus0.03091X0 donor2.

All15geometric exploratory cases(5layouts×3pT×2000events) closed successfully at
4b009b2. Baseline>=10created fractions86.7/87.3/87.8%; coverage-candidate gives
99.2/99.2/98.95% but worsens forwardd0/curvature. This is an observed tradeoff,
not a successful full-objective optimum. No finite tails, failures or wrong
charges removed. Newly preregistered balanced configuration204ab5f preserves
first/farthest disk and all stavecounts, moves firstbarrel31.5mm and intermediate
disks; subsequent native trial uses same exploratory seed, never hold-out52042.

Full native ROOT overlap audit(1e-5mm): baseline0overlaps,PASS; first coverage
compact13486overlaps,FAIL (13378collectors,108railslot conflicts; noothertracker
conflicts). OPT-SoftEng-03 fixes complete disk-owned collector positions/clones
and rail cutouts under0e55431. All20disc subtrees match prior sensitive/local
structures exactly; trunks/reference density/envelopes preserved and service
capacity unqualified. Full corrected overlap audit and finalconfirmation are
pending. Original failed evidence retained compressed. Discovery/plot failures
were corrected: testfixturealias, sys.path discovery collision, and numerical
negative errorbar roundoff at100%coverage. No weakened scientific tolerances.

PriorPR101 merge-preparation turn closed:7645859observedtokens imported solely
into its original account, completed visible snapshot retained, publicdiscussion
recaptured/read and ledger synchronized. New optimisation account never copies
these prior tokens. Current coordinator turn01a17c93-3e49-7ac1-a25a-3b6fae03b727
remains active/excluded; child closed-turn accounting follows at closeout.


## Frozen confirmation and qualified outcome

The human answered: “Geometric primary; Gaussian cross-check.” This supersedes
the earlier pending-question notes without rewriting their historical state.
All24 exploratory cases completed(48,000events); this includes balanced-nine
and late-disk controls. All30 confirmation cases completed(300,000events):
52042baseline/mild/balanced and62042baseline/late, each both responses and
pT1/10/100GeV,10,000events/case. The62042schedule was registered before52042
residuals were reduced/read. No geometry was retuned using confirmation data.

Geometric primary mild(32mm firstpixel barrel; reference9disks+900mm donor2)
improves global d0 central-width2.4–5.1% and z03.7–6.5%, with ten-hit fractions
96.53/96.65/96.83% versus88.09/87.73/87.74%. Momentum core ratios at1/10GeV
are compatible within measured uncertainty;100GeV improves4.4%. This is not a
noninferiority proof. Gaussian1GeV momentum worsens4.0%[0.5%,6.6%], highest-eta
d0 also worsens; full nonlinear pT tails are severe. Balanced98.2%coverage
has primary1GeV momentum+5.6%[2.5%,8.9%] and highest-eta d0+11.0%. Late-control
global cores improve but forward regressions and94%coverage remain. No tested
layout meets every goal; preserve every adverse result and the full objective
as open. Mild is a geometric-primary follow-up candidate, not an accepted
baseline. Worst mild signed quarter-eta fractions81–85%, not ten hits everywhere.

Native sourcee80f982, reduction9873280, first primary evidence77070c9 and all
fourfinalmatrices/figures4c0910. All four offline native/source/output/count/
material/histogram checks pass(9+9+6+6cases). Portable ROOT-free plots/CSV
retain full counts, fitted/missing/charge states, all six bound-parameter pulls,
full SD/RMS/core widths, pointwise bootstrap intervals and joint eta/phi coverage.
No finite-tail/quality cuts; time prior dominated. Matplotlib full pull density
now autoscales so the8.075timepeak is visible. Primary figures visually inspected,
including coverage holes and time/tails. One final export wrapper used --data
instead of --input; reduction/audit had passed, only CSV/plot orchestration failed.
Corrected exports alone completed; no native jobs or reduction rerun for that typo.

Full ROOT overlaps/extrusions1e-5mm: baseline, corrected coverage, balanced, mild
and late all0,PASS. Initial13486-overlap failure retained. Collector/rail fix
moves complete attachments with disks, preserves global envelopes. Native
20/20currentcontrolsPASS,no skips in activated runtime; portable19PASS/1expected
native-helperSKIP. Initial restricted setup could not run ps/sysctl; scoped
native-environment execution succeeded without changing shared dependencies.
Project78tasks/40documents/21rounds,209sessions and eightroles/threeworkflow
skills validate. New CI audits all30 confirmation cases and replays primary data.

OPT-SysArch-03 independently assessed77070c9 read-only: in-memory generated
mild/late compacts match auditedSHA86de9543/cccc962a exactly; all12corresponding
confirmationcompacts match. Unchanged readouts/world/pipe/strip XML,46,250unique
sensitiveIDs/logicaltuples. Added layer10 contributes302sensors/end; native clears
46,251sensor+pipe slabs then loads67materialkeys. Downstream carriers are±906.825
and±2906.825mm,1mmafter the last sensorfaces; donor2normalbudget0.0308203/0.0309096X0.
Each addedrailslot removes229.824mm³CFRP/end; clonedcollectoradds4,155,214.9569mm³
of existing effectivematerial/end. Zero intersections do not qualify cumulative
service connectivity/capacity, installation, mass or thermal design. No new
native job or tracked write by reviewer; no new physical blocker/signoff.


Display-only full symlog tick spacing refined at171cd0f8a7a3287d28262226f33fc0598336f43e;
all4figure sets regenerated from unchanged4c0910data. Main visually inspected
full pull PNG: zero/power labels no longer collide; timepeak and full tails
remain visible. No native/reduction/data changes. Documentation tables were
assembled directly from the retained final matrices; source CSV remains the
machine-readable numerical authority.


## Independent final assessment and accounting closeout

OPT-PhysVal-03 completed read-only: sourcebfa3c264/reduction9873280,
all4numericalmatrices/nativeinventories4c0910, figures171cd0f, finalclaims/tables
0a582d8, ACTSmaterialsemantics355ea684. Separate uproot/NumPy calculations check
54cases/348,000generated/347,964fitted, including30confirmationcases with300,000
/299,968.378nativeoutputhashes,8,714,319coordinatevariances,254,940scalarchecks
(maxdifference5.69e-14),714fullhistograms,3591profilerows and1512pairedbootstrap
intervals(378rows,maxdifference0) reproduce.16CSVfiles/31,638rows/240,702numeric
fields exact. All28PNGs visually inspected andhashmatched.18globalcomparison,
30case and17adverseregionalMarkdownrows/537numbers exact andregionalexceptions
exhaustive forstateddiagnostics. Noinvalid6Dcovariance/nativeFakes/outliers;
missingfits areselectionlosses. Gaussianreportsstate10retries/11maximumattempts,
withoutclaimingactualretrycounts.593carriers/76,950profilebins/476calibration
layers independentlychecked;closurewithin1.81e-7. No new simulation, tracked
write, installation orhumanapproval. No unresolved numerical/reporting blocker
withinassignment; no testedlayoutmeetscombinedobjectives. Mechanicalscopeclearly
separate. Full source/claim qualifications remain in validationREADME.

Nine exact completedOPTchildturns imported once: input53,086,127, cachedinput
51,768,192, output177,758, reasoningoutput74,758, total53,263,885. Cachedinput
andreasoning are subsets. New finalreviewevidence owns two newly finalized
turns(16,438,530PhysVal03;4,053,552SysArch03), not copied prior observations.
Rootcurrentturn01a17c93 remainsactiveandexcluded; models/clientversionunknown.
Curated completedchildvisibleoutputs/assignmentIDs and activecoordinator inputs/
responses retain only public text and operationmetadata, no hiddenreasoning,
rawrollouts, toolarguments/results orprivatepaths. PublicPR104discussionrefreshed:
no comments/reviewinputs present at capture. PRdescriptionupdatedwithactual
newlines, completedstatistics andfull-objectivefailure; draftretained.

PR101postmergeaccount reconciliation is separate andsolelyowns its newlyclosed
7,645,859tokens; oldbaseline/smearing/scienceunchanged. All affectedledgersare
synchronized. Local finalchecks anddashboardvalidate/build are performed before
publication. Hosted final-headstatus is an explicitly later external observation,
not invented in this prepublication snapshot. DraftPR104 remains a prototype
scientific report for human assessment; issue103/overalloptimisation remainopen.


## Accounting reconciliation — 2026-10-29

The original root optimisation and its two explicit recommendation followups
are now finalized. Exact visible prompts/turn IDs and usage-only counters are
retained in USAGE-2026-10-29-optimization-closed-root.json and PR104 turn records.
The three turns add40,161,171 tokens to the previously recorded53,263,885,
for93,425,056 across12closed turns. Counters remain in this original task owner;
the Oct29 balanced implementation account is separate and its active root is
excluded. The earlier coordinator mild preference remains historical; expert
review5701456683 selected balanced and current human direction authorizes its
maintained DD4hep/TDR integration. No performance result is rewritten.
