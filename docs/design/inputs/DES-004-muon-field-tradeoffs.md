# DES-004 — Muon return-field and dedicated-magnet tradeoffs

- Date: 2026-09-18; status: DRAFT, research follow-up; no sign-off.
- Physics/Performance agent assessment; no new simulation.
- Tracking: [issue #9](https://github.com/asalzburger/nodd/issues/9), requested in [PR #6](https://github.com/asalzburger/nodd/pull/6#discussion_r4040748306).

## Executive summary

Compare muon momentum measurement using the return field of an outer solenoid with a dedicated muon magnet. The physics assessment is that **an instrumented return field can provide an independent muon measurement if sufficient bending is sampled by independent muon measurements**. A separate excitation circuit is not required for measurement independence. Conversely, a large main-solenoid field does not establish standalone capability when the muon stations only measure an outgoing segment beyond it.

This is a **DRAFT research follow-up to PR #6 / DES-004**, not a baseline-update issue or topology selection. No nODD muon momentum resolution has been demonstrated. Human review must first agree which fit classes and performance criteria are required.

## Scope and evidence

The following tradeoffs are **INFERENCE**, grounded in the registered sources and measurement arguments in the [muon assessment](https://github.com/asalzburger/nodd/blob/research/magnetic-configurations/docs/design/inputs/DES-004-muon.md#public-evidence-and-next-gate) and [physics protocol](https://github.com/asalzburger/nodd/blob/research/magnetic-configurations/docs/design/inputs/DES-004-physics-validation.md#4-observables-and-fair-controls). Current allocations are the [stepped candidate envelopes](https://github.com/asalzburger/nodd/blob/research/magnetic-configurations/docs/design/DES-004-magnetic-configurations.md#candidate-specific-muon-envelopes), not the original fixed E1-R2 hosts.

| Candidate | Potential advantages | Costs / unresolved physics |
| --- | --- | --- |
| MAG-01: inner solenoid, no dedicated yoke | Compact central-magnet control; tracker information can support a combined fit. | Outer curvature may be weak or poorly observed. An outgoing segment alone cannot separate unknown incoming direction from momentum. Unconstrained standalone capability remains a question to calculate, not an assumed impossibility. |
| MAG-03: outer solenoid, no dedicated yoke | Main-field bending before outer measurements may help tracker-combined or vertex-constrained fits; avoids a dedicated massive yoke. | Unconfined fringe/return flux does not guarantee useful curvature between muon measurements. Stray field, forward orientation and the material of calorimeters, coil and supports remain relevant. |
| MAG-04: outer solenoid, instrumented iron return | Return flux can supply bending among muon measurements without a separate muon coil; CMS provides a built topology precedent. | Steel, air gaps and nonlinear response determine the field; scattering, energy loss and stopping compete with bending. Requires space, alignment, field calibration and end-return design. A stronger local field alone is not proof of a better fit. |
| MAG-05: inner solenoid plus air-core toroids | Intended bending within the muon spectrometer; field orientation can help forward trajectories. Avoids scattering in a dedicated return yoke; ATLAS provides a built topology precedent. | Additional coils, cryostats, supports and services; sector-dependent field and obstructions. Station lever arms, alignment and barrel/endcap transitions must work at nODD's scale. |
| MAG-06: outer main solenoid plus active return | An instrumented return annulus can combine distributed bending with less dedicated iron; external-field control is an explicit objective. | Trades iron for coupled coils, supports, cryogenics and protection. Finite ends, return-current choice, forward leverage and shared service space are unresolved. The fourth-concept precedent is a proposal, not operating evidence. |

MAG-02 (inner solenoid with an instrumented iron return) remains a useful companion control: it separates changing main-coil scale from adding an instrumented return. All options must include inherited calorimeter/support steel in their physical field model; “no dedicated yoke” does not mean an iron-free detector.

**FACT anchors already catalogued:** SRC-ATLAS-JINST-2008 §6.1, printed p.164/PDF194 and Figs.6.1–6.2/PDF195; SRC-CMS-YOKE-COSMICS-2010 §§1–2/PDF3–5; SRC-CMS-FIELD-MAP-2023 §§1–2/PDF2–3. SRC-FOURTH-CONCEPT-2007 §2.3/PDF5 and Fig.5/PDF6 supplies the active-return concept; its quoted angular reach corresponds to |eta|≈2.185 and does not establish the nODD |eta|<3 goal or 3.5 stretch. Source identities and public links: [manifest](https://github.com/asalzburger/nodd/blob/research/magnetic-configurations/reference/manifest.yaml). These precedents establish mechanisms and modeling obligations, not transferable nODD performance.

## Discriminating study and deliverables

**NODD DESIGN CHOICE — proposed study, human approval pending:** use the existing physics protocol and validation catalogue, with four separately reported fit classes:

1. Tracker-only.
2. Muon-only unconstrained standalone: no tracker hits or interaction-point prior.
3. Muon-only with an explicit vertex prior and uncertainty.
4. Tracker–muon combined: state any vertex prior separately.

- [ ] Physics + muon engineer: agree momentum, charge, eta/phi, prompt/displaced samples, measurement errors, alignment scenarios, required coverage and acceptance criteria before ranking candidates. Reuse the recorded diagnostic grid; do not invent performance thresholds from results.
- [ ] System architect + software: establish verified vector fields (finite coils first; nonlinear iron where applicable), domain/uncertainty policies and field-map/direct-evaluation agreement. For MAG-06, test finite dual coils and then end-return variants rather than treating flux-area arithmetic as a field solution.
- [ ] Muon engineer + software: place explicit independent measurement surfaces within the current stepped hosts; retain service/coil exclusions. Show both common diagnostic controls and physically candidate-specific station layouts, identifying their different resource costs.
- [ ] Physics + software: calculate crossings, signed vector bending and displacement response to q/p between measurements; examine which momentum information remains after fitting the unknown initial position/direction. Opposing bends may cancel net deflection while retaining measurable intermediate displacement. Neither an unsigned field integral nor host length is a resolution.
- [ ] Physics + software: move from vacuum controls to fixed-material comparisons and then physical candidate-dependent material/measurement fits. Report charge determination, momentum residuals/pulls, efficiency and failure fractions versus eta/phi/momentum; distinguish surviving-track precision from survival probability. Test field/alignment uncertainties and vertex-prior dependence, including displaced particles.
- [ ] Calorimeter + muon engineer: keep leakage/punch-through and background studies separate from momentum fits; do not add iron solely to obtain a desired performance curve.
- [ ] Publication office: record reproducible evidence, uncertainties and a pro/con recommendation in Git under DES-004, linked to FIELD-V01, PROP-V01 and MU-V01–08. If a layout is subsequently selected, open its separate baseline-amendment issue.

## Decision requested

Confirm the required standalone, vertex-constrained and combined objectives and their review criteria. The present recommendation is to **test return-field and dedicated-magnet options on equal measurement assumptions before selecting one**. The existing priority of MAG-05/MAG-02 is an investigation order, not a demonstrated performance ranking or rejection of MAG-04/MAG-06.
