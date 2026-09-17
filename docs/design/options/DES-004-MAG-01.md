# MAG-01 — Inner solenoid without a dedicated return yoke

- Date: 2026-09-17; status: DRAFT; human approval pending.
- Parent: [DES-004](../DES-004-magnetic-configurations.md); reference: E1-R2.
- Assessment: **retain as the simplest central-magnet control and a conditional combined-muon option; do not assume standalone capability.**

## Proposal and evidence

**NODD DESIGN CHOICE:** retain the reference magnet assembly at r=1.240–1.640 m,
|z|≤3.550 m. Its current-sheet diagnostic has R=1.415 m, half-length 3.300 m
and central Bz=+3 T. The [architect input](../inputs/DES-004-system-architecture.md),
§2, derives approximately 17.144 MA-turn. Turn count, operating current and
material decomposition remain unresolved; the 400 mm allocation is not a
demonstrated engineering envelope.

**FACT:** SRC-ATLAS-SOLENOID-2007, abstract/Table I, PDF1, documents a commissioned
2 T NbTi solenoid with a shared calorimeter cryostat. This supports the technology
class, not the complete nODD shell or operation without dedicated return iron.
Source identities are in the [catalogue](../../../reference/manifest.yaml).

## Technical assessment

**INFERENCE — tracker:** the retained [vacuum benchmark](../../validation/DES-004-solenoid-benchmark.json),
`results[candidate.id].checks`, gives MAG-01 Bz=1.766 T on axis at z=3.150 m,
versus 3 T centrally; at the outer tracker corner, (Br,Bz)=(0.871,1.967) T.
These are model outputs, not field measurements. Useful forward bending depends
on trajectory direction and the full vector field; neither sample predicts eta-4
resolution. The strong end variation is a research liability, not a demonstrated
failure of forward tracking.

**INFERENCE — calorimetry:** coil, cryostat and services precede ECal, introducing
conversion/shower and dead-material risks. Retaining the compact central layout
avoids MAG-03's outward muon-host amendment, but material accounting cannot be
skipped merely because the shell fits. Shared calorimeter cryogenics are not
assumed from the ATLAS precedent.

**INFERENCE — muons:** this option naturally supports a tracker-combined study.
Standalone momentum depends on measurable curvature between outer stations and
its separation from alignment/scattering uncertainties; fringe field alone is
not evidence of sufficiency. Distinguish unconstrained muon-only fits from fits
using a vertex or tracker constraint.

**INFERENCE — services/resources:** the compact bore limits the initial magnetic
volume, but chimneys, quench protection, cooling and load-bearing supports remain
unallocated. No dedicated yoke means neither zero return flux nor an iron-free
detector: inherited HCal steel (SRC-ODD-UPSTREAM, pinned revision in DES-004,
`xml/detectors/CalorimeterHCal.xml`) changes the physical solution. The vacuum
control cannot establish stray fields or installed energy and forces.

## Blocking conditions versus missing evidence

There is **no demonstrated intrinsic showstopper**. If unconstrained standalone
muon momentum is mandatory and outer bending is insufficient under agreed
measurement assumptions, MAG-01 fails that requirement. If the coil/material
assembly exceeds its reservation, an explicit amendment is required. Neither
condition has been demonstrated. Missing conductor margins, nonlinear steel
response, service paths and material-aware propagation prevent feasibility or
performance claims; missing evidence is not proof of failure.

## Next discriminating tests

**NODD DESIGN CHOICE:** prioritize common-surface ACTS vector-field propagation
against MAG-03, preserving failed/missing crossings; then evaluate signed bending
and momentum-information proxies for separate fit classes. Add a physical
calorimeter-steel field model and pre-ECal material scenarios. Check assembly
decomposition and service exits before optimizing field strength. Rank only after
comparing resource and material consequences, with criteria supplied independently
by Physics and Performance Validation. This note adds no simulation or sign-off.

**Current host request:** barrel r=4.35–6.762 m, |z|≤7.2 m;
endcap r=0.4–7 m, |z|=7.2–10.27 m.
[Budget](../inputs/DES-004-muon-envelope-amendments.md),
[PNG](../figures/DES-004-mag-01-muon-envelope-rz.png) /
[SVG](../figures/DES-004-mag-01-muon-envelope-rz.svg). Unsigned; baseline issue after selection.
