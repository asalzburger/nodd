# DES-013 — Pixel barrel longitudinal coverage

- Status: DRAFT; isolated **PROTOTYPE**, pending human approval.
- Created: 2026-10-01.
- Direction: human request to test transverse wire-bond routing and close z packing in a new PR with ACTS evidence.
- Governing inputs: [DES-011](DES-011-service-constrained-tracker-optimization.md), [DES-002](DES-002-pixel-barrel-support-cooling.md), [DES-012](DES-012-dd4hep-pixel-barrels.md); module issue [#7](https://github.com/asalzburger/nodd/issues/7).
- Approving humans: none for these numerical hypotheses. Production/default compact files remain unchanged.

## Parameter contract, before implementation

| ID | Classification | Requirement / rationale |
| --- | --- | --- |
| Z-C01 | NODD DESIGN CHOICE | Freeze the DES-011 original-pocket baseline and its four barrel radii, stave columns, radial staggering, outward support orientation, endcaps and strips. Replace only barrel modules in independent study artifacts. |
| Z-C02 | NODD DESIGN CHOICE | Rotate the inherited module chip matrix by 90 degrees in its sensor plane. Local u remains tangential, v remains z; transform chip offsets, bounds and asymmetric die-periphery offset. Keep each chip's active area, inter-chip dead seam, thickness and phi service allowance. Do not turn die periphery into active sensor. |
| Z-I01 | INFERENCE | The pinned DES001 approximate 20 × 21 mm chip and 20 × 19.2 mm matrix imply 1.8 mm periphery. Rotation moves this allowance to phi. This preserves the inherited approximate envelope; it is not a verified pad/bond-loop drawing or a choice of RD53 revision. |
| Z-C03 | NODD DESIGN CHOICE | Compare frozen baseline, rotation with inherited row centres, then close packing with (z guard per edge, mechanical body gap) of (0.5,0.2), (0.2,0.2), (0.1,0.1) mm. Remove the inherited 1 mm service allowance per z edge in the packed cases only. Keep 0.5 mm transverse guard and 1 mm transverse service allowance. The 0.5 mm case isolates removal of service space; 0.2 mm is a proposed slim-edge target; 0.1 mm is an aggressive sensitivity bound, not a qualified sensor. |
| Z-C04 | NODD DESIGN CHOICE | Bond/flex and fastening access is transverse or behind the sensor on the existing continuous outward support. No connector or end-to-end clamp occupies the proposed z gap. The mechanical gap must eventually include dicing, placement, adhesive, thermal motion and assembly tolerance; none is yet qualified. |
| Z-C05 | NODD DESIGN CHOICE | Use constant minimum pitch = occupied z length + mechanical gap, wholly inside |z| ≤ 550 mm. Retain residual space at ends rather than distributing it through the seams. Compare symmetric rows with a chip-centred phase: align one chip centre at z=0 and add all rows fitting the same envelope. No relative stave z staggering is introduced. Report end losses and central seams separately. |
| Z-C06 | NODD DESIGN CHOICE | Use matched seeded off-grid rays and independent angular/boundary grids for x,y ∈ [0,1] mm, z ∈ [-150,150] mm, |eta| ≤ 4. Test straight rays and both charges at pT=1 GeV in constant 3 T; add total-p=1 GeV sensitivity. Fractions are sampled geometric acceptance, not event efficiency. Keep ideal-layer denominators fixed. |
| Z-C07 | NODD DESIGN CHOICE | Preserve analytic finite-patch counting and audit selected tracks with native ACTS EigenStepper, supporting-plane targets and finite RectangleBounds. Include central and high-missing-hit tracks. Use inherited 0.002 mm trajectory tolerance and 10 mm maximum step. This is not full global navigator, material or reconstruction validation. |
| Z-C08 | NODD DESIGN CHOICE | Screen occupied bodies and outward support envelopes at inherited 1e-7 mm numerical overlap tolerance. Report chip/power changes with inherited 2.688 W/chip and 1.5 stress multiplier. Existing services are not recertified by area scaling. |

## Public evidence and approval boundary

**Z-F01 — FACT:** SRC-PLANAR-SLIM-2013, Weigell et al., arXiv:1210.7661v2, §3.2.1, PDF p4, reports 100–200 µm edge distances in dedicated FE-I3/FE-I4-compatible etched sensor developments. This motivates a sensitivity interval; it does not qualify these margins for nODD's RD53 modules, voltage, dose or production process. [Public paper](https://cds.cern.ch/record/1491076/files/1210.7661.pdf).

The existing module model remains the source of the chip dimensions (SRC-RD53-OVERVIEW-2023, slide 5; pinned DES001 in review_models.json). Exact die seal-ring width, bump map, bias structures, guard design, bonds and encapsulation remain engineering inputs. The approximate die width is no justification for a zero-edge module. Neither a successful intersection audit nor increased coverage grants sensor, mechanical, thermal or service approval.

## Deliverables and decision

Repeatable configuration, regenerated module/bounds geometry, matched coverage by layer and subsystem, off-grid and central diagnostics, body/support screens, silicon and power inventory, native ACTS audit, and a recommendation retained in `docs/validation/DES-013-pixel-z/`. No baseline change is automatic. Review the sensor edge, lateral services and assembly tolerance before a subsequent DD4hep implementation.

## Executed result and proposed amendment

The [results](../validation/DES-013-pixel-z/results.md) and [recommendation](../validation/DES-013-pixel-z/recommendation.md) retain all six hypotheses. Z-C03’s 0.2 mm edge/gap, chip-centred case is recommended for expert review, not adopted. Existing cooling fails the quad stress exit-quality ceiling; the recommendation proposes a new flow study without changing DES002. Added diagnostics are NODD DESIGN CHOICE: matched 1-unit eta and 100 mm z bands, straight eta=0 scans in 1 mm z steps at 16 phase-offset azimuths, and explicit native z-edge probes at ±1 µm (a numerical check, not an assembly tolerance).
