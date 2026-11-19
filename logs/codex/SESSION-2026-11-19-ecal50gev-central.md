# SESSION-2026-11-19-ecal50gev-central — Dedicated central 50 GeV electron raw and sampling response

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

## Specialist assignments

Explicit fallback profiles, not claimed native loading. Before dispatch, read-only assignments at source077696b4da7556a31ad02d656dfa3c0141b07543: ECAL50-CaloTech-direction chooses a favourable fixed phi from geometry, no shower-output optimization; ECAL50-PhysVal-protocol independently assesses observable/calibration/uncertainty definitions. Inputs and completion contracts are retained in ignored build/ecal50gev/assignments/{CaloTech,PhysVal}.json; full prepared prompts supply role mandates. No owned write files or child delegation. Coordinator implements and executes.

ECAL50-SoftEng-analysis: explicit SoftEng fallback at077696b4da7556a31ad02d656dfa3c0141b07543; write ownership central_analyze.py/test_central_analyze.py only in isolated ../nodd-ecal50gev-analysis worktree. Implements compact statistics/replot and tests from exact new-run manifests, no simulation or detector changes. Main owns preparation/transport/protocol; full contract in ignored assignment JSON, prepared mandate supplied before dispatch.

## Prospective protocol decisions

Geometry-only CaloTech chooses eta0.1, phi+0.7degree; nearest sector seam10.55degree, minimum tangential active clearance16.797942mm,44/48layers crossed;4axialrow gaps remain. PhysVal preflight supports held-out effective visible-response fraction, with explicit SD/50 versus SD/mean labels and no claim constant scaling improvesCV. All four detector/population streams are independent: LAr calibration705020/evaluation705021; SiW calibration705030/evaluation705031. Pilots use705019/705029 and are excluded from inference. Composite event identity(detector,population,seed,event); identical primaryfourvectors are deliberate.2000calibration+10000evaluation/model, ECAL-onlyB0, origin50GeVtotal-energy electrons. All raw sensitive deposits and allzeros/tails retained. Runtime reverified after old setup/lock fingerprints changed: DD4hep1.38/Geant411.4.3/ROOT6.40.04;12datasets present and all3LAr libraries load successfully. Existing SiW/LAr libraries match original audited SHA256. No installation/shared environment change.
