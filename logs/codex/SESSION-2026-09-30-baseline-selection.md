# SESSION-2026-09-30-baseline-selection — Human-selected tracker working baseline

## Request and authority

On 2026-09-30 the user explicitly instructed:

> Ok, we take the recommendation as the new baseline, record that and update the PR accordingly.

This follows the [recommendation](../../logs/design/SESSION-2026-09-30-baseline-recommendation.md)
to select the original-pocket case from PR #28, with larger silicon area no longer
a driving concern. The instruction is recorded as a human choice of working
baseline. It does not provide formal engineering sign-off or production integration
authorization. No GitHub reviewer identity is inferred from the chat instruction.

## Outcome and scope

DES-011 SO-C19 records the exact selected case,
`p190-s680-b1-l1287.33-front_loaded-original-pockets`, at evidence revision
`17ae47f6d18e132eb539f30ef8323114963f8588`, numerical source
`ac61f766b34f9bb60748e8fc4258a41037ca1e33` and compressed geometry SHA-256
`89ce39dae6af7e1e69d40582a6c49e6e7f26dbcd6ce1dd3cc061e41e75419cbd`.
It retains the tested last-disc bypass, original larger pockets, constant trunks,
inherited23-row long-strip pitch and module placement policies. No inclined barrel
section is introduced; the existing12-degree local long-strip module tilt remains.

The design, report, workflow pointer and dashboard now identify this case as the
working baseline. Historical training roles, numerical artifacts, adverse capacity
results and earlier review decisions remain unchanged. A no-bypass alternative
requires matched validation before replacing the selected layout. DES-011 remains
DRAFT/PROTOTYPE, with service engineering and formal production sign-off outstanding.
The previous recommendation log pair is retained alongside this distinct decision
record. Four unrelated usage-summary files are preserved and excluded from staging.

## Validation and publication

Checks and actual publication details are recorded below and in the paired JSON.
This is a documentation/decision change; numerical simulations are not rerun.
Exact geometry identity and unchanged retained evidence are checked directly.

## Token accounting

Client-reported exact counters are unavailable for this task; usage remains empty.
The historical session summary is not this task's usage. No observations are copied
or inferred from earlier sessions.
