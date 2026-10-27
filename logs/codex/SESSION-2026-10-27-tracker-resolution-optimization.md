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
