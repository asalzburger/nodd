# DES-003 — Review round 2 disposition

- Date: 2026-09-17; status: DRAFT, human sign-off pending.
- Review: [PR #4](https://github.com/asalzburger/nodd/pull/4), comments 09:57–10:12 UTC and changes-requested summary at 10:14 UTC.
- Previous proposal: `9877ec14998280ef6f9cb4d13ae6b949d6c75d06` (E1-R1).
- Current proposal: **E1-R2**, [main document](DES-003-global-envelopes.md).

The remaining substantive review request is enough planning space for a **3 T
central solenoid**. The [space budget](inputs/DES-003-solenoid-space-budget.md)
provides a 400 mm radial reservation with explicit contents and end allowances.
The coordinator propagated it through neighbouring envelopes and regenerated the
drawing/report. Detailed magnetic-system and muon research remain the next tasks.
No full design sign-off is inferred from positive comments on individual items.

## New directions implemented

### Forward baseline

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4035455911) · [Team reply](https://github.com/asalzburger/nodd/pull/4#discussion_r4037106460). Detached forward calorimetry is now part of the working envelope baseline. Absorber and readout technology selection stays in later calorimeter design.

### 25 mm host

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4035461765) · [Team reply](https://github.com/asalzburger/nodd/pull/4#discussion_r4037106619). Retained 25 mm as the aggressive innermost tracker envelope. It remains a host boundary, not a selected sensor radius; pipe/module clearances will be resolved in tracker design.

### Outer-coil research

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4035471068) · [Team reply](https://github.com/asalzburger/nodd/pull/4#discussion_r4037106855). Recorded outer-solenoid bending, stray field and the need for a return yoke as a dedicated magnetic-system research question, outside the present envelope decision.

### Magnetic design next

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4035509315) · [Team reply](https://github.com/asalzburger/nodd/pull/4#discussion_r4037107019). Detailed magnetic-system design is explicitly deferred to the next research task. This revision changes only its space reservation and the neighbouring envelopes.

### 3 T space budget

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4035549705) · [Team reply](https://github.com/asalzburger/nodd/pull/4#discussion_r4037107204). Replaced the 200 mm shell with a 400 mm planning reservation, r=1.24–1.64 m and |z|≤3.55 m. The budget is 100 mm inner cryostat/interfaces + 150 mm cold assembly + 100 mm outer interfaces + 50 mm margin; 250 mm end allowances surround a cold assembly to |z|=3.30 m. Built NbTi benchmarks and explicit current/force scaling justify the scale. ECal/HCal move outward and downstream, and the muon barrel starts at 4.35 m, retaining nominal calorimeter depths and gaps. The regenerated allocation has no rectangle overlaps. This is a conservative planning allowance for 3 T centrally, not a certified safe magnet design; detailed magnetic research remains next.

### ACTS stack

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4035557609) · [Team reply](https://github.com/asalzburger/nodd/pull/4#discussion_r4037107423). Recorded ACTS installation as the next software-stack step for straight-line and full-field tracking. PROP-V01 retains the shared-field and convergence requirements. No installation or propagation is claimed in this envelope revision.

### Timing baseline

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4035583954) · [Team reply](https://github.com/asalzburger/nodd/pull/4#discussion_r4037107605). The outermost tracker layer is now the potential timing-layer baseline to investigate. Sensor/readout timing capability, forward coverage and service space will be resolved in tracker design; separate timing assemblies remain alternatives rather than the preferred baseline.

### Muon research

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4035589225) · [Team reply](https://github.com/asalzburger/nodd/pull/4#discussion_r4037107779). Recorded dedicated muon-setup research as the next task, including magnet alternatives and measurement requirements. No further muon design is required in this envelope round beyond its space allocation.

## Remaining comments acknowledged

The following comments confirm or defer existing baseline items; their evidence
and follow-up obligations remain in the proposal and study catalogue.

| Comment | Disposition |
| --- | --- |
| [4035448789](https://github.com/asalzburger/nodd/pull/4#discussion_r4035448789) — This looks good now. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035484210](https://github.com/asalzburger/nodd/pull/4#discussion_r4035484210) — Looks good, that will give us input for later refinement. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035512388](https://github.com/asalzburger/nodd/pull/4#discussion_r4035512388) — Ok, sounds good. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035515189](https://github.com/asalzburger/nodd/pull/4#discussion_r4035515189) — Agreed. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035519029](https://github.com/asalzburger/nodd/pull/4#discussion_r4035519029) — Good for further reference. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035520668](https://github.com/asalzburger/nodd/pull/4#discussion_r4035520668) — Good. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035524893](https://github.com/asalzburger/nodd/pull/4#discussion_r4035524893) — Correct, we will next tackle the magnetic field setup. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035529317](https://github.com/asalzburger/nodd/pull/4#discussion_r4035529317) — Ok. Probably not relevant for the current enevelope discussion. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035532636](https://github.com/asalzburger/nodd/pull/4#discussion_r4035532636) — Good - the new coverage is very much appreciated. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035538016](https://github.com/asalzburger/nodd/pull/4#discussion_r4035538016) — Ok. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035564715](https://github.com/asalzburger/nodd/pull/4#discussion_r4035564715) — Ok, can be revised later. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035568563](https://github.com/asalzburger/nodd/pull/4#discussion_r4035568563) — Good. | Acknowledged; retain the agreed baseline or explicitly deferred work. |
| [4035575745](https://github.com/asalzburger/nodd/pull/4#discussion_r4035575745) — I agree with this first baseline. | Acknowledged; retain the agreed baseline or explicitly deferred work. |

## Scope of the pending human decision

Review **the global envelope baseline and its explicit space allowances**, not a
completed magnet, detector technology or performance design. Confirming this
baseline can allow subsystem research to proceed under the existing design
workflow. Conductor/field/cryostat engineering, muon setup, timing implementation,
calorimeter technology and detailed supports/services remain subsequent tasks.
Any resulting change to the reviewed envelopes must be brought back as an amendment.
Only the human reviewer may sign off an exact revision and resolve review threads.
