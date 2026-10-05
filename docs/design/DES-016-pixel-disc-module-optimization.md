# DES-016 — RD53 pixel disc module optimization

- Status: DRAFT — isolated PROTOTYPE study; no design sign-off or baseline replacement.
- Created: 2026-10-05.
- Review: [issue #38 overlap comment](https://github.com/asalzburger/nodd/issues/38#issuecomment-5981583892).
- Inputs: DES-001 RD53i matrix fixtures, DES-013 retained finite-module layout,
  DES-014 supports/services and DES-015 preliminary combined pixel prototype.

## Contract before the search

| ID | Classification | Requirement or choice |
| --- | --- | --- |
| DO-C01 | NODD DESIGN CHOICE, explicit user direction 2026-10-05 | Silicon overlap must be at most 10%. Report both repeated silicon area divided by the projected union and divided by the summed installed silicon area. Use the stricter former quantity for selection. Also report installed silicon outside the unchanged nominal annulus, so overhang cannot disappear into an overlap metric. |
| DO-C02 | NODD DESIGN CHOICE | Preserve the nominal active annulus r32.3..181.4550267061104 mm, nine discs per end and existing disc datums. The position amendment is a separate PR. Do not reduce the acceptance region or silently crop sensor outlines to achieve the target. |
| DO-C03 | NODD DESIGN CHOICE | Explore rectangular single-RD53i modules to reduce the severe inner-radius overlap of quads. Retain the 20.0 by 19.2 mm active matrix, 50 micrometre pitch, 0.15 mm sensor and inherited 1 mm occupied module thickness. Any narrower guard is an explicitly unqualified design choice, with the inherited 0.5 mm guard retained as a control. No new ASIC functionality or trapezoidal active pixels is assumed. |
| DO-C04 | NODD DESIGN CHOICE | Scan integer phi populations and radial ring spacing, plus mixed Cartesian/inner-ring tiling; explicitly screen actual active rectangles, physical sensor outlines and module bodies. Full projected annular coverage must be checked separately from area overlap. Preserve holes found in baseline controls. |
| DO-C05 | NODD DESIGN CHOICE | Finite z offsets and nonzero luminous vertices require their own straight/curved-track checks. Native ACTS target propagation validates finite sensitive-plane intersections and identifiers against the analytic oracle; it is not a claim of global ACTS navigation, material response or reconstruction. |
| DO-C06 | NODD DESIGN CHOICE | Recompute power chains, links, heat, half-ring circuit count, coolant feed/return and collector/trunk footprints with DES014/010 scenario inputs. Do not scale a quad count as though it were a single-chip module. Keep reference and adverse scenarios, packing failures and hydraulic/thermal qualification limits visible. |
| DO-C07 | NODD DESIGN CHOICE | Retain the full preliminary barrel and all original evidence as controls. Study outputs and proposed sensitive planes are isolated under tools/pixel_disc_optimization and docs/validation/DES-016. Baseline integration and a revised detailed support/thermal design need human review. |

All candidate dimensions, placement policies and numerical controls are recorded
in the executable study inputs. Public matrix/material facts remain those in
DES-001/014 and reference/manifest.yaml. This study adds choices and derived
geometry/service estimates, without new externally established design facts.


## Selected conditional proposal and engineering boundary

The reproducible study selects328 single modules per disc:18 inner polar modules
and310 Cartesian modules. It retains the original active matrices and nominal
annulus, with a0.1mm guard and20.4×21.4mm occupied body including ASIC periphery.
These slimmer guard/service allowances are **NODD DESIGN CHOICES, unqualified**;
the0.5mm inherited guard is retained as a failing control. The first-disc lattice
pitches19.55×18.75mm use0.45mm overlap reductions; farther discs scale that
reduction by615.2/abs(z), preserving the328 indices. Five1.2mm spaced levels,
body conflict colouring and on-axis vertex compensation are **NODD DESIGN
CHOICES**. All18 body/overlap screens and continuous straight coverage
certificates pass. Native ACTS is a finite supporting-plane audit, not global
navigation validation. [Results](../validation/DES-016/results.md) pin the actual
code, inputs and runtime.

The body radius grows to about212mm. The inherited r188.5mm support, local
service bands, r192mm trunk and thermal feet require a redesign. New module
count increases chains and command/data bundles despite reducing chips/heat.
All inherited shared-trunk packing scenarios fail; this is explicit evidence
for the next architecture review, not permission to integrate a broken service
model. No design sign-off or production replacement is recorded. Full DD4hep
implementation follows review of guard/ASIC assembly feasibility, new local
support/cooling/routing, readout aggregation, collector and last-disc adapter.

Provenance: matrix/pitch/sensor thickness and conditional heat proxy are inherited
from DES001/010; body/guard, tiling, levels, compensation, grouping and envelope
reserves are NODD DESIGN CHOICES. Areas, containment, counts, heat, tube/cable
cross-sections and packing failures are INFERENCES from those executable inputs.
Area tolerances, polygon resolution, colouring padding and subdivision limits
are numerical screening controls, not fabrication tolerances. No externally
qualified hardware performance is introduced by this proposal.
