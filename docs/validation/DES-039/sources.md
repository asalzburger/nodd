# DES-039 — Source evidence and pinned inputs

2026-10-16. **DRAFT / PROTOTYPE.** Prepared by the separate PhysVal context
against `e8108f997bb663670db745e57d61d66c2cea9437`. No design sign-off is
recorded. [Machine-readable evidence](sources.json) contains the source
locators, exact Git-object SHA-256 hashes and classification of each claim.

## Public engineering precedent

| Primary source | Locator and supported FACT |
| --- | --- |
| [ATLAS detector paper, JINST 3 S08003 (2008)](https://doi.org/10.1088/1748-0221/3/08/S08003) | Chapter 2, table 2.1 and §§2.1.2–2.1.3: eight coils in each toroid; barrel 120 turns at 20.5 kA and 1.08 GJ; each endcap 116 turns and 0.25 GJ. Peak winding fields 3.9/4.1 T. Figure 2.1 and §2.2.2 include calorimeter steel in the field model. |
| [Miele and ten Kate, Fusion Engineering and Design 58–59 (2001), 195–203](https://doi.org/10.1016/S0920-3796(01)00432-X) | Introduction and barrel/endcap sections: 22.5° relative rotation, individual barrel vessels and common endcap cold assemblies. |
| [Rey et al., IEEE TASC 16 (2006), 553–556](https://doi.org/10.1109/TASC.2006.870838) | Abstract and figure 1: approximately 25 × 5 × 0.4 m barrel coils; double-pancake windings in aluminium casings. |
| [ten Kate, Physica C 468 (2008), 2137–2142](https://doi.org/10.1016/j.physc.2008.05.146) | Table 1, figure 5 and §3: conductor envelopes and cryostat construction. The approximately 1.1 m barrel vessel diameter is distinct from cold-pack thickness. |
| [ATLAS MDT resolution, JINST 14 P09011 (2019), arXiv v2](https://arxiv.org/html/1906.12226v2) | Abstract and §8: 81.7 ± 2.2 μm single-hit resolution. Section 2: R–Z precision coordinate and three barrel/main endcap stations. |
| [ATLAS muon resolution, arXiv:1404.4562v1](https://arxiv.org/html/1404.4562v1) | Introduction: 35 μm chamber, 30 μm alignment and approximately 1.3 X₀ internal-material benchmarks. Section 2 specifies 30/40 μm barrel/endcap alignment design accuracies. Section 10.1, equation (3), separates resolution contributions. |

These references establish precedents, not nODD construction approval. The
ATLAS winding peak fields are different quantities from the mean spectrometer
field. Cold masses, complete cryostats and conductor volumes are also distinct.

**Hash limitation:** no article PDF was newly downloaded into this checkout.
The existing ATLAS-paper catalogue records SHA-256
`669a956b6e6f6af0e2ec14e1250cca4f8e9d97acb5454db5ffe50aa577524291`;
its local bytes were unavailable for rehashing. The CERN and publisher pages
were checked through public primary-source web results; some direct fetches
returned bot challenges or HTTP 403. The two arXiv HTML articles were read
directly. Article byte hashes remain explicitly null when unavailable; exact
Git-object hashes below are separately verified.

## Project source chain

The classification here is **FACT about recorded prototype inputs**. It does
not reclassify their unsigned component dimensions as experimental facts.

| Input | Exact source revision | Role in DES-039 |
| --- | --- | --- |
| [PR86, MUON-001](https://github.com/asalzburger/nodd/pull/86) | `e8108f997bb663670db745e57d61d66c2cea9437` | Compact-span target and MDT covariance benchmark; five file hashes retained. |
| [PR64, DES026](https://github.com/asalzburger/nodd/pull/64) | `4e44d7c650ac0a2931f7fc1637b5b3f2dfbe4c95` | Existing 3 T solenoid winding and vacuum sizing; three file hashes retained. |
| [PR81, DES036](https://github.com/asalzburger/nodd/pull/81) | `abd95bdc64b9d7971561d659bf953e71de4e7e99` | Common HCAL carrier and steel material recipe; three file hashes retained. |
| [PR84, DES037](https://github.com/asalzburger/nodd/pull/84) | `0e8530d56d171f38c9d53d3c60c8b48803680bbd` | HCAL barrel envelope and assembly; three file hashes retained. |
| [PR85, DES038](https://github.com/asalzburger/nodd/pull/85) | `c1f11013b03391a4f09d86b39dff57e6c3f58ab2` | HCAL endcap envelope and assembly; three file hashes retained. |

Read these files with `git show REV:path`; current branch files are not
substituted. The retained [solenoid input](../../../tools/toroid_prototype/solenoid-input.json)
copies two pinned JSON objects and records their hashes. The PR86 source tree
provides [compact-span results](../MUON-001/compact-span/results.md).

## Derived quantities and design choices

**INFERENCE:** twelvefold half-sector rotation is `360°/(2 × 12) = 15°`.
The ideal Ampère mean-field scale needs approximately 2.42 MA-turn per coil
for 1 T at radius 5.8 m. Neither calculation optimizes the finite geometry.

**INFERENCE:** PR86 combines 35 μm fitted chamber resolution with independent
30 μm alignment to obtain 46.0977 μm effective station uncertainty. The tube
error must not be added again. This is the central-barrel comparison;
extending 30 μm alignment to disks is an explicit assumption, while 40 μm
gives 53.1507 μm for an ATLAS endcap comparison. A disk/barrel mixture must
use the appropriate individual station variances.

**INFERENCE:** the pinned 3 m comparison needs 0.860806 T for 10% standalone
resolution at local 500 GeV with its assumed material. The tracker proxy alone
gives 6.75%, so the 10% combined target supplies no positive minimum field.
An actual toroid must use signed field integrals and the three actual station
crossings, including unequal mixed barrel/disk spacings.

**INFERENCE:** the inherited solenoid winding spans radii
1.3278–1.3792706602 m and length 7.2 m, with 18.363595673 MA-turn at central
3 T. Its 143.1737575 MJ energy and 4.7724586 m³ cold volume refer to the
isolated vacuum calculation.

**NODD DESIGN CHOICE:** twelve barrel coils, twelve per endcap and three
nested outline stations implement the human-requested topology. Final coil
dimensions, currents, cold supports and case clearances belong to the proposed
configuration. They are not ATLAS measurements. Approving humans: none.

**NODD DESIGN CHOICE:** the initial joint map assigns vacuum permeability to
the source calculation. HCAL steel remains part of the geometric input; its
magnetic grade and B–H curve are missing. Consequently the initial map cannot
certify the installed nonlinear field, stored energy or complete-system
30 MJ/m³ cold-volume requirement. Solenoid radial sizing rules cannot simply
be applied to an empty toroidal annulus. Approving humans: none.


Final chamber-envelope scale: **FACT**, ATLAS JINST chapter6, §6.3.1,
printedpp.172–174 (PDFpages202–204), Tables6.3–6.4: two multilayers
of3/4planes of30mm MDT tubes, with listed spacer heights6.5–317mm.
A1 read these selected pages from the additional JINST-hosted PDF acquisition
recorded in sources.json. **NODD DESIGN CHOICE:**500mm chamber-envelope depth;
this is not a claim of a specific ATLAS chamber's complete installed depth.
