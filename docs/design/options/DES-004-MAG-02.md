# MAG-02 — Inner solenoid with instrumented iron return

**2026-09-24 sizing amendment:** [Current constraints and dimensions](../inputs/DES-004-magnet-sizing-review.md)
supersede earlier winding/vessel and MAG-03/04 radial allocations below.
Earlier numerical results remain historical; complete-system engineering is open.

**2026-09-22 amendment:** the inner main solenoid now has an explicit finite
homogeneous winding pack. The [expert-review response](../inputs/DES-004-magnet-expert-review.md)
defines its bounds, pack-average current, derivation and checks. Historical
thin-sheet numbers below remain reference controls. Enclosure adequacy and
complete physical field solutions remain unverified; MAG-06 is withdrawn.

- Date: 2026-09-17; status: DRAFT; no approving humans.
- Governing [candidate](../DES-004-magnetic-configurations.md); [muon assessment](../inputs/DES-004-muon.md).
- **NODD DESIGN CHOICE — recommendation:** retain as a principal alternative to MAG-05 for independent muon momentum; request a coarse return-and-station layout before a nonlinear field solve. Do not select its steel inventory now.

## Technical case

**INFERENCE:** a return structure can place bending between muon measurements without a second superconducting magnet system. Its steel also introduces scattering, energy loss, stopping and structural/service constraints. The compact inner coil preserves the reference calorimeter ordering but retains upstream coil/cryostat material affecting electrons and photons. Instrumented calorimeter energy must remain distinct from energy absorbed in uninstrumented return plates.

**FACT — SRC-CMS-YOKE-COSMICS-2010, §§1–2/PDF3–5:** the operational CMS study distinguishes return-field standalone measurement, vertex-constrained fits and tracker-to-muon bending. **INFERENCE:** it demonstrates the measurement principle, not performance for nODD's much smaller inner coil. Tracker coverage to η=4 still depends on the changed vector field and actual forward measurements. Adding iron requires recomputing current and field; the MAG-01 vacuum normalization cannot simply be reused.

## Flux/space screen

**NODD DESIGN CHOICE — diagnostic assumptions only:** the [common option screen](../../validation/DES-004-option-screen.json) approximates the coil bore by a uniform axial 3 T disk of radius 1.415 m and directs all its flux through the muon-host cross-section. Trial average return flux densities 1.5 and 2 T are illustrative, not steel specifications or proof against saturation.

**INFERENCE — arithmetic:** `Φ=3π(1.415)²=18.87 Wb`; `A=Φ/B` gives 12.58 and 9.44 m² respectively. The full reference annulus r=4.350–6.762 m has area approximately **84.20 m²**. The equivalent return areas occupy about **14.9% and 11.2%** of that cross-section, before station gaps, supports or services. Elementary flux accounting therefore does not itself reject MAG-02. The much greater MAG-04 flux demand deserves a stronger space-pressure challenge, rather than treating both yoked candidates identically.

This is not a lower bound or a designed yoke: finite-solenoid flux is nonuniform, calorimeter steel can carry return flux, and actual plates, gaps, endcap bottlenecks, supports and penetrations redistribute it. Filling the host with steel is not a detector layout. The area screen supplies neither chamber locations nor field in their gaps. No absorber mass, steel grade or saturation limit is inferred.

## Decision limits

**Conditional showstoppers:** reject or enlarge this candidate if a physically solved return layout cannot provide sufficient independent bending between usable stations, or if plate/gap/support allocation cannot fit while preserving the required measurements and services. Material-driven stopping/scattering may invalidate a specified performance requirement. No such failure has yet been demonstrated; numerical performance requirements remain to be agreed.

**Missing studies:** nonlinear B–H/material scenarios including HCal; barrel/endcap flux continuity; stations and aligned measurement coordinates; forward η=3/3.5 apertures; cryogenic/electrical/gas routes; punch-through and material scans. Extra steel must not be justified solely by better rejection plots before calorimeter leakage is established. Forward calorimetry downstream of stations cannot filter their incoming hadrons.

**Next comparison:** separate unconstrained muon-only, vertex-constrained and combined fits with common uncertainties, then candidate-specific material. Report survival separately from precision. Compare the engineering burden of passive return structures with MAG-05's discrete coils, rather than ranking field strength alone.

Verification: flux arithmetic executed with Python; no finite-element field solution, propagation or material simulation. Existing source IDs resolve in the [catalogue](../../../reference/manifest.yaml); no new source or production parameter introduced.

**Current host request:** barrel r=4.35–7.5 m, |z|≤8 m;
stepped endcap: upstream r=0.4–4.2 m, |z|=6.35–8 m;
wide r=0.4–7.5 m, |z|=8–10.9 m.
[Budget](../inputs/DES-004-muon-envelope-amendments.md),
[PNG](../figures/DES-004-mag-02-muon-envelope-rz.png) /
[SVG](../figures/DES-004-mag-02-muon-envelope-rz.svg). Unsigned; baseline issue after selection.
