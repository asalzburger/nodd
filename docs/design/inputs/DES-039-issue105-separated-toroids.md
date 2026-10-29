# DES-039 amendment — separated toroids and schematic muon stations

- Status: DRAFT
- Date: 2026-10-29
- Scope: isolated PROTOTYPE for [issue105](https://github.com/asalzburger/nodd/issues/105); no production integration or human sign-off.
- Parent designs: [DES-039](../DES-039-twelvefold-toroid.md), [DES-040](../DES-040-muon-chambers-frame.md), [DES-004](../DES-004-magnetic-configurations.md), [ADR-006](../../decisions/ADR-006-global-envelope-and-field-hypotheses.md).
- Source geometry: PR90 merge `cae3a72f3b1c98edaf9bc28a84d019142606ba25`, `docs/validation/DES-040/sketched-stagger-2026-10-20/candidate/geometry.json`.
- Approving humans: none. Expert feedback is attributed to `mgtmentink` as quoted in issue105; its exact reviewed commit is unknown.

## Review response and provenance

**FACT F01, review direction:** SRC-NODD-TOROID-REVIEW-20261029, issue body,
requests shorter barrel coils, longer endcap coils, no barrel/endcap interleaving,
and an ATLAS-like useful field. The quoted expert gives approximately 4 T at NbTi
windings and typically 0.5–1 T between coils. This is a technology screening
constraint, not a universal critical field or an approval of a particular current.
The expert regards the central 3 T solenoid as reasonable; this amendment preserves it.

**FACT F02, public model:** SRC-MENTINK-ATLAS-MAGNET-MODEL-2024, p1 §§1–2,
models all superconducting families and nonlinear iron using warm ideal symmetric
geometry, with explicit approximations. Page5 §5 compares 1.54 GJ calculated
energy with 1.56 GJ inferred from operation. Page6 Fig6 has a 4025.010 mT
maximum on its colourbar. These are ATLAS model facts, not nODD predictions.
The attachment does not supply nODD conductor, load line or structural calculations.
Source metadata, hash and precise locators are in the [manifest](../../../reference/manifest.yaml).

**FACT F03, repository inputs:** the active PR90 geometry contains barrel
centreline bounds |z|≤11.8 m and endcap bounds 7.3–11.7 m. Their 0.50 m
normal warm sweeps overlap axially. The older `toroid_prototype/design.json`
contains a different historical endcap front at 6.8 m and is not substituted for
the active input. The exact old chamber shapes, fields, supports and results
remain retained, with no assertion that their validation survives this amendment.

## Proposed coil geometry and operating screen

All following parameters are **NODD DESIGN CHOICE, proposed; human approval
pending**. Preserve twelve meridional racetracks per family, a homogeneous
0.12×0.18 m current pack, and the current rounded paths and radial dimensions.
The path and warm dimensions are inherited; the thinner pack is an explicit new
choice to permit the lower current and the review-directed energy/cold-volume
closure simultaneously. This is not an optimized cable or vessel design.

| Item | Barrel | Each endcap |
| --- | --- | --- |
| Centreline radial bounds [m] | 4.60–8.80 | 0.70–7.60 |
| Centreline axial bounds [m] | −6.00–6.00 | abs(z)=7.30–13.30 |
| Full axial length [m] | 12.00 | 6.00 |
| Corner radius [m] | 1.00 | 0.60 |
| Azimuthal phase | 0° | 15° |
| Warm sweep normal × tangent [m] | 0.50×0.60 | 0.50×0.60 |

**INFERENCE I01:** the complete warm envelopes end at |z|=6.25 m and begin
at |z|=7.05 m, providing **0.80 m axial separation at every azimuth**. The new
barrel is 12.0 m rather than 23.6 m long; each endcap is 6.0 m rather than
the active 4.4 m. Different families therefore occupy separate axial volumes.
They still interact magnetically; this is no force-balance or assembly proof.

**NODD DESIGN CHOICE C01:** target 0.60 T of signed Bphi at an ordinary barrel
intercoil point (R=6.7 m, z=0, phi=15°) and an endcap intercoil point
(R=4 m, z=10.3 m, phi=0°). Solve both family currents together. Reduce both
currents, keeping their ratio and the solenoid fixed, if a sampled total
exterior field exceeds 3.5 T. The 0.5 T difference from the review's approximate
4 T limit is an explicit study allowance, not a certified safety margin.
Do not normalize current to recover the old 1.6 T sagitta response.

The engineering requirement is **max |Btotal|≤4 T throughout the toroid
windings**, including their self-field, other coils, solenoid and installed iron.
The existing quadrature-filament solver cannot certify an interior peak: exterior
probes and order refinement are a screening diagnostic only. Final current
selection requires a resolved continuous-pack/conductor calculation, operating
temperature, NbTi critical surface, mechanical strain and quench/protection input.
The complete central-field cap remains 5 T under DES-004.

## Proposed schematic station arrangement

**NODD DESIGN CHOICE C02:** three independent station IDs S1–S3, each with a
barrel shell and a wheel on each end. A barrel/wheel pair supplies one station,
even if a ray intersects both. Chamber depth is the inherited 0.50 m whole-cassette
reservation, with 0.05 m minimum local warm-coil clearance. These are clipped
continuous schematic surfaces; the old 936 panels and 484 supports are not moved
or claimed valid. Actual finite panels, borders, seams and supports need repacking.

| Station | Barrel centre radius [m] | Barrel half-length [m] | Wheel abs(z) [m] | Wheel inner/outer radius [m] |
| --- | ---: | ---: | ---: | --- |
| S1 | 5.20 | 6.4456 | 6.7456 | 0.40 / 6.10 |
| S2 | 6.70 | 10.0000 | 10.3000 | 0.40 / 7.50 |
| S3 | 8.20 | 13.8000 | 14.1000 | 0.40 / 9.00 |

S1 lies between HCAL and ECT; S2 lies between the endcap coils; S3 lies beyond
the ECT rear. The outer barrel stations extend past the short barrel magnet
to close transition acceptance. These extensions do not imply useful bending
throughout their length. Coil-following exclusions remove local chamber portions
around both magnet families and their rounded ends.

**INFERENCE I02:** S1 front/back are 6.4956/6.9956 m. With the LAYOUT-001
HCAL back at 6.4412 m and ECT warm front at 7.05 m, it has 54.4 mm axial
clearance to each. Its wheel has 245.6 mm clearance beyond the BT warm end.
S3's front at 13.85 m is 0.30 m beyond the ECT warm rear. The barrel-to-wheel
gap is 0.05 m for every station. These are nominal shape gaps, with no
installation, alignment or service-capacity qualification.

**INFERENCE I03:** for half-depth h=0.25 m, barrel radius R and half-length L,
wheel centre Z and outer radius Ro, full-depth straight-ray handoff requires
`L/(R+h) >= (Z+h)/Ro`. The selected wheel outer radii meet this condition.
Each inner wheel also stops below the next barrel's inner radial face, avoiding
intersection of the orthogonal host volumes. The 0.40 m aperture limits the
first wheel to `asinh((6.7456−0.25)/0.40)≈3.48`; full 3.5 stretch coverage is
therefore not claimed, even without coils. Geometry below eta3 closes before
azimuthal hardware cuts. All dimensions remain conditional on actual panel shapes.

**C03, explicit vessel assumption:** S2 requires a coil-following/shared-sleeve
ECT vessel with an accessible intercoil measurement region. A filled annular
ATLAS-like vessel would exclude this middle wheel. That alternative needs a
different station concept and acceptance study; no free measurement volume
inside a real cryostat is assumed proven here.

## Reproducible evidence and interpretation

[Study inputs](../../../tools/toroid_redesign/design.json),
[code and reproduction](../../../tools/toroid_redesign/README.md),
[retained results](../../validation/DES-039/issue105/README.md).
The joint vacuum field is freshly evaluated; old field maps and coupling matrices
are not rescaled after changing source geometry. All-space energy includes every
finite-pack self and mutual term, with refinement, using the existing validated
J·A integrator. The 30 MJ/m³ cold-volume policy is reported explicitly; cold sweep dimensions close the global vacuum energy/volume relation while
containing the pack. This is not installed-detector sizing compliance.
Installed nonlinear HCAL response and applicable per-family cold allocation remain open.

Coverage counts ≥1/≥2/3 distinct stations, with full normal depth and warm-coil
cutouts. It compares short cylindrical chambers with the extended nested proposal
on the same deterministic direction bank. It reports flat eta/phi and integrated
solid-angle denominators, eta3 separately from 3–3.5 stretch, and a separate
conservative magnet-free interstation-path diagnostic. A muon crossing a warm
reservation is not automatically lost; material and transport are needed.
Coarse/fine grids expose sampling sensitivity. These are geometric availability
ceilings, not reconstructed efficiencies or MDT momentum-resolution predictions.

## Required review and subsequent implementation

- SysArch/MuonTech: qualify separate load paths, installation, warm/cold vessels,
  S2 access, new rear carrier and chamber/services routing; repack finite panels
  and recreate the frame. Current old panel/support certificates are historical.
- SysArch/Calorimeter: this proposal uses PR90/LAYOUT-001 HCAL. LAYOUT-002's
  longer HCAL conflicts with S1 and requires a separate amendment. Compact FCAL
  rear services and forward shielding require explicit interface checks.
- Magnet expert: resolve continuous-pack peak field and conductor operating
  margin; solve installed nonlinear fields/energy, force interaction and quench.
  Confirm applicable cold-volume allocation and vessel sizing; no inherited
  radial solenoid fit is applied blindly to non-solenoidal geometry.
- PhysVal/SoftEng: propagate a common muon bank through the new validated map
  and actual material/panels. Retain field/navigation failures in denominators;
  compare signed bending, station spacings, standalone and combined fits.
- Human design review remains necessary before production implementation.

No prior design is advanced to SIGNED OFF or ACCEPTED by this study.
