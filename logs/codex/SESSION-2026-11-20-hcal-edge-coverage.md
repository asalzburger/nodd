# SESSION-2026-11-20-hcal-edge-coverage — HCAL edge coverage and fixed-direction pion response

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

## User request and initial scope

Continue the standalone nODD HCAL prototype: minimize sector-edge scintillator
gaps with smaller modules, redo the eta and one-sector folded-phi response plots
including repeated outer windows, and run a dedicated optimal fixed barrel
direction sample with raw energy, raw fractional and sampling-corrected response.
Earlier hcal50 evidence remains an unchanged comparison baseline.

## Coordination

Applying nodd-coordinate, nodd-design-evidence and nodd-review-validation.
Explicit role-assignment fallback is used; native profile loading is not claimed.
Prepared assignment contracts and full prompts are in the same-stem directory.
HCAL-EDGE-CALO owns only DES046; HCAL-EDGE-PHYS owns only the prospective
new protocol; HCAL-EDGE-SOFT is initially read-only. Root owns integration.
Source b91b1d7969b94cccb4e0516e1c84246f4d2e2cd0, clean worktree at start.

## Environment

acts-spack registry preflight flagged changed setup/lock fingerprints. The
actual existing runtime was reverified: DD4hep1.38/3yd4hz3 and
Geant411.4.3/wfg55xi; DD4hep/DDG4 imports and all12dataset presence checks pass.
Sandbox sysctl/ps warnings persist; no shared dependencies were changed.

## Usage

Exact client per-turn counters are unavailable; usage remains empty, not zero.

HCAL-EDGE-SOFT-IMPLEMENT grants the same specialist the disjoint C++ factory,
C++ conversion/worker audit, transport, analysis and their existing tests/README.
The physical design and protocol must exist before their dependent edits.
Root retains model/export/edge-unit construction/native geometry/direction scan.

HCAL-EDGE-SYS delegates a separate read-only physical-interface assessment of
sector taper, edge guides, absorber ownership and retained service handoffs.

HCAL-EDGE-SYS-IMPLEMENT grants SysArch native.py and direction.py only, after
DES046 is written. This implementation is separate from its prior interface
assessment and is not independently reviewed by its own author.

HCAL-EDGE-CALO-REVIEW assesses physical implementation at2e516f04b1dcb51e2a374762060529de59511bf6; the reviewer
authored the governing design, not the implementation. No human sign-off.

## Implementation and development checks

Physical source2e516f04 passes8geometry tests. Both native C++ libraries
compiled. Backend source4a85b7fa passes13transport/statistics contracts.
SysArch's8finite-solid selector tests pass. Development native-v3 has379344
contexts,102distinct sensitive solids,88finite rays and zero overlaps. Its
complete native graph independently reproduces15material totals and
8831.375605tonnes. A failed earlier audit is retained locally:8unit0probes
lay exactly on CSG surfaces; explicit exact-surface native-leaf comparison
now accompanies independent analytic non-boundary controls, with unchanged
±1e-4mm boundary-neighbour probes and no relaxed physics/overlap tolerance.

CaloTech reviewed physical implementation2e516f04 (design author, not code
author): all100units' independent closed-form PSHost/Cu/Al/Ti/water volumes,
sparse channels and3heat/flow scenarios match; maximum arithmetic discrepancy
1.46e-10mm3. Local nominal heat2.125740MW and ideal water101.710kg/s do not
qualify a plant, routing or mechanical load path. The guide-only material
change is−50.074952tAl/+101.573222tsteel, before cassette repacking.

Development geometric scan found eta0/phi−0.75deg; its nine sampled neighbours
have minimum58/mean59.333active layers. This is a development diagnostic only;
the immutable final receipt must be regenerated at the frozen source before
showers. Source-bound ROOT checks match all nine layer sets and material paths.

## Pre-run independent scientific assessment

PhysVal review at a0b985be found a missing fail-closed link between the fixed
direction receipt and the geometry being sampled. No new showers had started.
Corrective sourceba946f56 requires selector/nativePASS, finite coordinates,
exact expected/export/source/execution bindings, copied-artifact revalidation
and runtime geometry-library identity. Fixed analysis also checks calibration
freeze chronology. All14transport/statistics tests pass, including negative
foreign/failed/NaN/corrupted/library/chronology cases. A new exact-commit
PhysVal guard assignment checks the correction before production.
