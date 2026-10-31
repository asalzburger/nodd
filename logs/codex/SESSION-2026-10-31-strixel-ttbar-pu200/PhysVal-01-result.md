# TTBAR-PU200-PhysVal-01 — preproduction assessment

Independent read-only PhysVal child `/root/ttbar_physval` reviewed exact
`a734cf0d718846af84f919575725b9c7f0eee731`. All seven pinned inputs match their
hashes and working bytes. Explicit mandate/review-skill fallback; no native
profile loading or human acceptance claimed. No canonical files changed.

The protocol supports the requested fixed-response reconstruction comparison,
subject to implementation and distinct-seed smoke gates. It cannot establish
physical sensor occupancy performance or detector acceptance.

## High-severity implementation gates

1. Frozen SafeFatras reads `particles_generated`, whereas the guide transports
   `particles_generated_selected`. Preserve all generated truth separately and
   demonstrably feed the selected generator collection into transport. The
   proposed new task-owned collection split is structurally adequate but needs
   actual smoke proof.
2. ACTS355ea `EventGenerator.cpp` lines90–142 preserves generator order, but
   `HepMC3InputConverter.cpp` lines295–331 clusters primary vertices (default
   mergePrimaries=True,1nm), then assigns sequential barcode vertices at371–387.
   A vertexPrimary==1 assumption alone does not prove hard-scatter origin.
   Retain201producer origins and verify conversion mapping/rare mergers.
3. Frozen ReconstructionAudit omits generated initial position and assumes
   origin loc0/loc1. New audit must retain initial position/ct/origin for
   fiducial and hardscatter/pileup classification. Do not use origin truth
   coordinates for displaced-track residual claims.

## Required definitions and qualifications

Unique eligible matched generated particles / all eligible generated particles
is headline efficiency. Conditional>=9measurement and>=6sensor/3pixelgroup
denominators remain separate. Match every candidate against all truth, retaining
matched out-of-fiducial generated particles and simulated secondaries separately
from unmatched fakes. Additional matches are duplicates, overlapping matched
categories. Event-block paired ratio-of-sums uncertainty is required; efficiency
profiles use truth bins, candidate fractions use reconstructed-track bins.

The guide-defined hard process is qqbar-only ttbar, not the full qqbar+gg mixture.
Fatras pMin0.5GeV, approximate interactions and mixed-sample muon fit hypothesis
remain explicit. doMerge=False does not model physical cell sharing, merging,
electronics occupancy/saturation or service/material changes. Guide-like cuts
after frozen reconstruction are a selection comparison, not a reproduction of
the guide's differently configured native chain.

Pythia8ProcessGenerator scopes FPE monitoring off around upstream generation;
preserve Fatras/reconstruction monitoring and qualify any no-mask statement.
For100events, zero fake events gives one-sided95 event-incidence upper bound
2.9513%; this is not a candidate-fake upper bound. Flag degenerate bootstraps.

## Actual checks and remaining gates

Read governing AGENTS/PROJECT/DES041/042/ADR001/003/workflow/profile/skill;
verified seven input hashes, clean matching ACTS355ea source and inspected
guide, simulation, generator, merger/converter and selector implementation.
Node preflight exit0 with unverified fingerprints/full-source warnings, already
communicated. Independently calculated the zero-fake-event bound. No native
job, install, write, commit, publication or delegation.

Before production: freeze task-owned sources, close the three gates in smoke,
and verify exhaustive classification, complete payload replay, response
variance, CKF inputs/hypotheses and preselection ambiguity convergence. Final
exact committed evidence review remains required. Implementation peers were
notified of these gates; coordinator reconciles actual evidence separately.


Coordinator provenance correction: standalone node preflight subsequently
returned exit2, not0. The initial combined shell returned the finalcat exit0.
Unverified status/warnings were always present; runtime/source claims unchanged.
