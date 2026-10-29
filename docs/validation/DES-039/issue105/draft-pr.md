# Magnet System: redesign separated toroids and schematic muon stations

The previous barrel toroid overlaps the endcap toroid span and its stronger field target lacks a credible NbTi winding margin. Refs [issue #105](https://github.com/asalzburger/nodd/issues/105).

This DRAFT design amendment shortens the barrel coils to **12 m**, lengthens each endcap to **6 m**, and provides **0.80 m between their complete warm axial envelopes**, retaining the **3 T central solenoid**. A thinner homogeneous pack and freshly solved currents give about **0.48 T at the two ordinary intercoil reference points**. The sampled exterior maximum rises from **3.50 T to 3.64 T** under higher-order checks; the approximately **4 T conductor limit remains an unresolved engineering requirement**, rather than a certified bound. Complete vacuum self/mutual energy and global 30 MJ/m³ cold-volume closure are recomputed.

Three nested schematic station pairs extend the outer chambers through the transition. On the same 134,400-direction bank they provide **84.06% three-station geometric availability by solid angle within |eta|<3** (83.80% within 3.5), versus **62.79%** (62.59%) for shortening every barrel chamber. This is a continuous-shell ceiling before finite panels, supports and services; eta3.5 stretch coverage remains unmet. The joint direct field, signed bending diagnostics and angular refinement are retained; no new interpolation map or production geometry is installed.

- [Design, source rationale and open interfaces](https://github.com/asalzburger/nodd/blob/codex/issue105-separated-toroids/docs/design/inputs/DES-039-issue105-separated-toroids.md)
- [Drawing, results, reproducibility and limits](https://github.com/asalzburger/nodd/blob/codex/issue105-separated-toroids/docs/validation/DES-039/issue105/README.md)
- [Separate physics assessment, adverse findings and fixes](https://github.com/asalzburger/nodd/blob/codex/issue105-separated-toroids/docs/validation/DES-039/issue105/physics-review.md)

**Validation:** 33 focused analytic/field/energy/sizing controls pass, including stationwise barrel-or-wheel counting and ray-batch invariance. Source hashes, project/session records and token-site validation/build pass. SysArch and MuonTech supplied separate interface/placement assessments; PhysVal independently checked the numerical claims and counting corrections.

Stacked on PR87's branch containing merged PR90. Earlier maps, 936 detailed panels, frames and DD4hep validation remain historical. Continuous-pack peak field, NbTi operating margin, tiny cold support allowance, nonlinear HCAL energy, forces/quench, an accessible middle-station cryostat volume and finite-panel/material transport require review. DES004/DES039/DES040 remain DRAFT; no human sign-off or production integration.
