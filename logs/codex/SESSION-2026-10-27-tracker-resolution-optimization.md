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
