# MAG-05 — Inner solenoid with air-core barrel/endcap toroids

**2026-09-22 amendment:** the inner main solenoid now has an explicit finite
homogeneous winding pack. The [expert-review response](../inputs/DES-004-magnet-expert-review.md)
defines its bounds, pack-average current, derivation and checks. Historical
thin-sheet numbers below remain reference controls. Enclosure adequacy and
complete physical field solutions remain unverified; MAG-06 is withdrawn.

- Date: 2026-09-17; status: DRAFT; no approving humans.
- Governing [candidate](../DES-004-magnetic-configurations.md); [muon assessment](../inputs/DES-004-muon.md).
- **NODD DESIGN CHOICE — recommendation:** retain as the preferred topology to investigate for genuinely unconstrained standalone muons, conditional on a credible coil/station/service layout. Compare directly with MAG-02/04; this is a research priority, not a demonstrated performance winner.

## Technical case and precedent

**INFERENCE:** deliberate bending among separated muon stations can supply momentum information without an inner-track or interaction-point prior. Toroidal field orientation can help forward trajectories that run nearly along an axial solenoidal field. An air-core design avoids mandatory bulk return iron, but coil conductors, cryostats, supports and calorimeter steel still contribute material and alter fields. Combined fits remain useful and must be reported separately.

**FACT — SRC-ATLAS-JINST-2008, §6.1/printed164/PDF194 and Figs.6.1–6.2/PDF195:** ATLAS's barrel stations lie approximately at radii 5, 7.5 and 10 m, with chambers arranged around toroid coils and explicit service gaps. **INFERENCE:** this is an engineered topology precedent, not a scalable resolution guarantee. The nODD reference barrel host r=4.350–6.762 m is only 2.412 m thick before coils/supports consume space; copying the ATLAS stations is impossible within that host. The global radius or station arrangement may need amendment.

## Coupled subsystem consequences

The inner solenoid retains pre-ECal material and the finite-length tracker-field question up to η=4. Muon magnets cannot be assumed irrelevant to tracking: calculate the superposed vector field, including calorimeter/support ferromagnetism. Preserve calorimeter assembly and service exits rather than allocating toroid coils through them. In the forward region, central endcap supports, toroid end structures, chamber services and shielding compete for the same space.

**INFERENCE:** the η=3/3.5 objectives constrain chamber inner edges and the available bending region, not merely the overall mother volume. At the inherited first-station centre |z|=7.580 m, prompt straight-ray radii are 0.7566/0.4582 m respectively (`r=z/sinhη`; [aperture derivation](../inputs/DES-003-muon-review-1.md)). These small radii must coexist with beamline/shielding and coil return legs. They do not establish a realizable toroid aperture or active efficiency. Detached forward calorimetry cannot filter hadrons before these stations.

## Decision limits

**Conditional showstoppers:** within a fixed outer envelope, the candidate fails if coil/cryostat/support sectors leave inadequate independent measurements or bending in required angular regions. If adequate leverage requires a larger envelope, it needs an explicit architecture decision. An ideal axisymmetric toroid does not close either condition. No such failure or successful fit has been demonstrated.

**Missing studies:** discrete coil geometry/current, inter-coil and coil-centre fields, barrel/endcap transition, signed bending and displacement response, force/energy scales, alignment references, routes and material inventory. Sample the union of all candidate sector boundaries; favorable azimuths alone cannot establish coverage. No field magnitude, coil count, chamber resolution or production station position is selected here.

**Next comparison:** first draw coils, usable station regions and service sectors jointly. Then evaluate three-dimensional field/trajectory information for prompt and displaced muons, with unconstrained standalone, vertex-constrained and combined results separated. Add material and realistic measurement uncertainties before claiming resolution. Request extra absorber only after leakage/punch-through evidence, not as an automatic accompaniment to an air-core spectrometer.

Verification: reviewed existing source-located inputs and current allocations; no toroid model, solver or performance calculation run. Source IDs are registered in the [catalogue](../../../reference/manifest.yaml).

**Current host request:** barrel r=4.35–9 m, |z|≤9 m;
stepped endcap: upstream r=0.4–4.2 m, |z|=6.35–9 m;
wide r=0.4–9 m, |z|=9–10.9 m.
[Budget](../inputs/DES-004-muon-envelope-amendments.md),
[PNG](../figures/DES-004-mag-05-muon-envelope-rz.png) /
[SVG](../figures/DES-004-mag-05-muon-envelope-rz.svg). Unsigned; baseline issue after selection.
