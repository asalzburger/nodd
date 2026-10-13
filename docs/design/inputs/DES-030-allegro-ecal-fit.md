# ALLEGRO-type LAr ECAL fit in the current nODD prototype

- Status: **DRAFT**; comparative space assessment, no technology adoption
- Date: 2026-10-13
- nODD source: `5664d16aea2df36222dc0099ba18594cf506304d`, [DES-029](../DES-029-calorimeter-assemblies.md)/[DES-030](../DES-030-ecal-edge-sensors.md)
- k4geo source: `e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb` (main observed 2026-10-13)
- Human question: would an ALLEGRO-like LAr ECAL fit in the current EM calorimeter volume?
- Engineering/technology sign-off: none; the existing Si–W choice is unchanged.

## Finding

**INFERENCE:** the LAr sampling stack fits the nominal depth, but the complete
current ALLEGRO allocation does not. A tailored barrel without ALLEGRO's outer
coil merits a concept study; endcaps need depth, radial and forward-aperture
redesign. Vessel gaps, insulation, supports, feedthroughs and electronics need
explicit space. The simplified cryostat model is not a construction-ready dewar.

## Current nODD reservation

**FACT — pinned nODD prototype inputs:** 48 layers with 1.9 mm absorber, 8.0 mm
cassette and 1 mm installation gap; 1700 mm barrel front apothem, 3900 mm
half-length, 3950 mm endcap front, 10 mm rear cover and 30 mm ECAL–HCAL interface
allocation. **INFERENCE:** sampling depth 523.2 mm; complete modeled package
533.2 mm. Barrel back-cover apothem is 2233.2 mm and HCAL front 2263.2 mm;
endcap package ends at 4483.2 mm and HCAL starts at 4513.2 mm. External services
are excluded from existing mass/geometry qualification. These are unsigned
prototype choices, not an accepted full-detector contract.

A circular cryostat contained between both unchanged 16-gon boundaries has
only `2233.2 - 1700/cos(pi/16) = 499.90 mm` radial span. This is a conservative
conditional geometric bound; reshaping the bore requires an interface study.
Apothems and cylinder radii must not be equated in a final clearance audit.

## ALLEGRO barrel: account for the outer solenoid

**FACT — SRC-ALLEGRO-K4GEO-2026:** latest ALLEGRO_o1_v04 and o2_v01 both include
the v03 ECAL files. DectDimensions.xml defines radial allocation 2100–2770 mm.
The barrel XML lines 25–55 give modeled cryostat 2149–2721 mm and sampling
2172.8–2578.3 mm. `SolenoidBarrel=70 mm` is included in the back-wall proxy.
The 49 mm margin on each side represents vessel-gap placeholders; warm and
cold walls are lumped into equivalent material. ALLEGRO's 2 T coil is outside
the ECAL; nODD's 3 T concept places its coil inside.

[Official barrel XML](https://github.com/key4hep/k4geo/blob/e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb/FCCee/ALLEGRO/compact/ALLEGRO_o1_v03/ECalBarrel_thetamodulemerged.xml#L25)

**INFERENCE**, retaining the stack and non-coil allowances:

| Radial budget | Thickness |
| --- | ---: |
| Sampling stack: absorber, electrode and LAr gaps | 405.5 mm |
| Front/rear equivalent walls without coil | 13.8 + 32.7 mm |
| Front/rear bath/service allowances | 10 + 40 mm |
| Simplified coilless shell/bath/stack lower bound | 502.0 mm |
| Two vessel-gap reservations | 49 + 49 mm |
| Coilless allocated total | **600.0 mm** |

The 502 mm lower bound leaves 31.2 mm against the nominal 533.2 mm package,
but the original vessel-gap reservations total 98 mm. Apparent fit does not
establish vacuum, structural, thermal, assembly or cable-space adequacy. It
also slightly exceeds the strict 499.90 mm circular-slot condition. Retaining
all non-coil allowances needs 66.8 mm extra radial space. Anchoring at 1700 mm
would give outer radius 2300 mm and HCAL front 2330 mm, preserving the 30 mm
interface allocation. Subtracting the 70 mm proxy is a repackaging hypothesis,
not a qualified cryostat design. Keep the existing inner magnet's material
and thermal ownership in the comparison.

ALLEGRO's 3100 mm half-length is shorter than nODD's 3900 mm. A full nODD
barrel needs extended/repeated electrodes and a longer engineered cryostat.

## Endcap and forward acceptance

**FACT — same pinned source:** the allocation is r = 350–2900 mm and
|z| = 3200–3850 mm. Nominal sampling occupies z = 3260–3710 mm: 450 mm sampling
plus 50/100 mm front/rear equivalent walls and 10/40 mm bath allowances gives
650 mm. The driver constructs the first wheel at 410 mm and extends blades
to 2790 mm; nominal XML sampling radii 400–2750 mm are not the full constructed
blade bounds.
[Endcap constants](https://github.com/key4hep/k4geo/blob/e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb/FCCee/ALLEGRO/compact/ALLEGRO_o1_v03/ECalEndcaps_Turbine_o1_v03.xml#L15),
[actual wheel construction](https://github.com/key4hep/k4geo/blob/e1ba7bc3e0d7291ebe3f6a02abfa784f879e36cb/detector/calorimeter/ECalEndcap_Turbine_o1_v03_geo.cpp#L784).

**INFERENCE:** moving the package front to 3950 mm places sampling at
4010–4460 mm and the package back at 4600 mm. This needs 116.8 mm extra axial
allocation and otherwise penetrates the present HCAL front by 86.8 mm. Preserve
the 30 mm interface gap. The 2900 mm outer radius also exceeds the current
ECAL endcap's 2223.2 mm outer apothem; a smaller turbine needs revised blade,
cell and gap calculations.

At the translated sampling front, eta = 4 reaches `4010/sinh(4) = 146.94 mm`,
far inside the 410 mm first wheel. Shrinking the cryostat aperture to 100 mm
while retaining the 50 mm inner-wall proxy and 10 mm wheel allowance still
gives 160 mm. The driver requires `tan(angle) >= depth/(2*ri)`: 450 mm at
49 degrees needs ri >= 195.59 mm; reaching 146.94 mm needs at least 56.85 degrees
in this construction. This is a geometric bound, not a qualified angle.
Inner wheels or a separate forward section need redesign. The nODD HCAL
aperture independently remains 300 mm.

## Performance and software limits

**FACT — SRC-ALLEGRO-CALOR-2025 and SRC-ALLEGRO-EPS-2025:** published barrel
studies describe approximately 40 cm sampling / 22 X0 and granular PCB
electrodes. Cryostat, support, cold electronics and complete particle-flow
integration remain development work. Published turbine parameters differ
from the pinned simulation, so their dimensions and performance must not be
mixed. **INFERENCE:** reducing radius changes inclined-plate spacing and LAr
gaps; uniform material scaling changes X0. An inner 3 T coil changes upstream
material and field conditions. No calorimetric resolution or particle-flow
performance follows from this dimensional comparison.

[Published geometry/performance paper](https://inspirehep.net/files/1a4ae9bc8730dd0bdd13c7922459e1d3),
[mechanics/readout/cryostat status](https://inspirehep.net/files/d3705f643a55e10919902f5d198bd618).

Existing DD4hep geometry/segmentation in k4geo is a possible later software
reference. No external package, factory or reconstruction framework was adopted.
A candidate study should agree cryostat/magnet/HCAL interfaces, model the full
hardware enclosure, audit native containment/mass/material and then compare
response with Si–W before a technology decision.

## Checks and evidence

The coordinator and read-only SysArch/PhysVal contributions inspected pinned
Git/XML/C++ and primary publications. A restricted standard-library arithmetic
parser evaluated named XML constants; the nODD inventory independently confirmed
the 533.2 mm package. [Scalar evidence](../../validation/DES-030/allegro-fit.json)
records hashes, formula outputs and conditional bounds. No LAr native construction,
overlap, thermal/mechanical calculation or transport was run. No engineering
or human sign-off is claimed.
