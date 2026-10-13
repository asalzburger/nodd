# DES029 companion — Endcap packing precedents

- Status: **DRAFT** research review; no geometry or technology change
- Date: 2026-10-13
- Parent: [DES029](DES-029-calorimeter-assemblies.md), PR69
- Question: How do FCC SiW concepts and CMS HGCal address endcap packing?

The relevant FCC-ee SiW comparison is **CLD**, drawing on ILD/CALICE. Other
FCC calorimeter concepts use different technologies. The physical precedent
common to CALICE and HGCal is a carrier holding many compact readout units,
with shared services. A fixed, independently framed large rectangle is not the
only repeated unit available to fill the endcap.

## Public hardware facts

The following observations are **FACT**, with their development scope retained.
They do not establish a nODD coverage percentage or qualify a copied design.

| Precedent | Packing and service architecture | Evidence and scope |
| --- | --- | --- |
| ILD/CALICE SiW | Quarter-endcap alveolar structures; layers assembled from 180 × 180 mm ASUs with four 90 × 90 mm sensors. ASICs embedded in the layer; multiple ASUs share compact slab-end readout. | SRC-CALICE-SIW-2022, PDF4 §3 and PDF6 §3.1. Architecture proposal plus technological prototype, not a completed collider endcap. |
| FCC-ee CLD | Assumes ILD/CALICE technology. Published concept explicitly requires cooling redesign for continuous operation; a 2026 overview still identifies electronics/cooling R&D. | SRC-FCC-CLD-2019-v3, PDF27–29 §5.5; SRC-FCC-CLD-2026, slide7. Simulation concept is not a complete hardware packing/service qualification. |
| CMS HGCal | Hexagonal full and partial modules tile broad cassettes: 60° CE-E and 30° CE-H. Copper plates contain cooling pipes; electronics/services occupy depth above the modules, including a stated 5.9 mm service space. | SRC-CMS-HGCAL-ENGINEERING-2025, PDF2 §§2.3–2.4. These are that publication's engineered cassette dimensions, not nODD requirements. |
| CMS partial silicon | Multi-geometry wafers include intended cut lines and internal HV protection/guard structures. The resulting manufactured partial sensors have dedicated boundary layouts. | SRC-CMS-HGCAL-PARTIAL-2025, §2 and Figs1–3. Evidence includes fabricated and irradiated partial sensors. |

Public sources:

- [CALICE SiW status paper](https://arxiv.org/pdf/2211.07457v1)
- [CLD detector concept, v3](https://arxiv.org/pdf/1911.12230v3)
- [CLD 2026 overview](https://indico.cern.ch/event/1588696/contributions/6871125/attachments/3208703/5714489/FCC_PW_CLD_2026.pdf)
- [HGCal engineering paper](https://doi.org/10.1051/epjconf/202532000066)
- [HGCal partial-sensor characterization, v4](https://arxiv.org/html/2510.17280v4#S2)

HGCal is a silicon sampling precedent; its electromagnetic absorber recipe
includes lead/copper/CuW rather than copying the nODD SiW sampling stack.
The transferable subject here is packing and services, not absorber selection.

## What the precedents imply

The following are **INFERENCE** from the architectures above and the unchanged
DES029 packing diagnosis:

- **Mechanical boundaries and readout-unit boundaries can differ.** A broad
  petal or quadrant can contain many smaller boards. Each board need not carry
  its own full perimeter frame and a large independent service strip.
- **Boundary adaptation must be physical.** A sensor/board family can fill
  aperture and perimeter remainders that full units cannot. A factory cannot
  simply clip an existing sensor's active rectangle and call that a qualified
  partial sensor: edge termination, biasing, manufacturing and readout change.
- **Services use both transverse placement and layer depth.** Moving shared
  interfaces to carrier ends, or placing electronics behind the sensitive face,
  can reduce wasted face area. Their material, heat, insulation, connector
  height and maintenance access still belong in the model.
- **Tessellation does not eliminate cracks.** Guards, board edges, tolerances,
  thermal motion, support seams and apertures remain. Assessment needs active
  layers versus eta/phi and material/transport checks, not only an area ratio.

No exact current HGCal global active-area fraction or inter-module seam size
is established by this review. We do not infer 100% coverage, universal gap
values or a current CMS seam-staggering specification from these sources.
Staggering/rotation is a nODD option to study after filling the large holes;
it cannot repair an uninstrumented inner annulus by itself.

## Proposed nODD sequence

These are unsigned **NODD DESIGN CHOICE proposals**, consistent with the
[existing repair proposal](DES-029-endcap-coverage-repair.md):

1. Keep SiW and the existing square silicon sensor baseline initially. Study
   carrier layouts containing single, 1×2 and 2×2 intact sensors with small
   custom boards. This isolates the packing repair from a sensor-technology
   redesign. Board families and margins still need qualification.
2. Compare broad mechanical petals/quadrants with the present sixteen narrow
   sectors. Preserve suitable logical sector IDs independently of mechanics.
   Review inner-ring/rib topology and structural/material consequences.
3. Share readout/power interfaces over a carrier and describe the local ASIC
   heat paths and cooling plate explicitly for continuous operation. Do not
   reuse ILC power-pulsing assumptions for this detector.
4. Optimize the aperture and outer remainders using the small board families.
   Introduce custom partial silicon only if the resulting coverage warrants
   its sensor-mask, dicing/edge-termination, PCB and qualification effort.
5. Publish each layer's active mask, aligned crack depths, eta/phi active-layer
   counts, mass/material, channel and continuous-power budgets. Compare optional
   seam offsets only after a credible complete layer exists.

The next concrete design remains one inner ECAL carrier and one inner HCAL
carrier. This research supplies architectural precedents, not an implemented
repair, signed-off sector count or promised detector efficiency.

## Evidence limits

CLD/CALICE PDFs and HGCal partial-sensor HTML were read through primary-source
web tools. HGCal engineering metadata and indexed primary PDF text were
available, while direct CDS/EPJ PDF access was challenged. The CLD 2026 slide7
observation comes from indexed primary PDF text; direct retrieval returned403.
No unverified full-PDF inspection or new native geometry run is claimed.
