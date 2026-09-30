# DES-012 — DD4hep pixel barrel implementation

- Status: DRAFT
- Implementation classification: standalone **PROTOTYPE**.
- Created: 2026-09-30.
- Human direction: use PR #29, even unmerged, as the new baseline and implement
  its pixel barrels in DD4hep. Configurable provisional cable material was
  explicitly authorized in the same session.
- Baseline: PR #29 at `c79c2194e23e99c4d2696ca2d6628a388b96f5e4`, with
  [human baseline confirmation](https://github.com/asalzburger/nodd/pull/29#issuecomment-5911774023).
- Governing designs: DES-001 (pinned module revision below),
  [DES-002](DES-002-pixel-barrel-support-cooling.md), DES-010, DES-011.
- Linked work: [pixel module issue #7](https://github.com/asalzburger/nodd/issues/7),
  PR #29 support/services baseline and dashboard TASK-SOFT-DD4HEP-PIXEL.
- Scope: four pixel barrels, their modules, outward local supports/cooling,
  mounting rings/feet, longitudinal cables and barrel extraction to |z|=605 mm.
  Endcaps, other subdetectors, global end brackets and full Geant4/ACTS integration
  are outside this implementation. No formal sign-off status is inferred.

## Plan and architecture

1. Verify the existing Spack DD4hep installation; build a repository-owned plugin.
2. Export the pinned numerical baseline into a compact XML plus independent
   expected placements/material inventories; reject stale source hashes.
3. Build reusable module, stave, mounting and effective-service components.
   A short assembly factory manages hierarchy, transforms and identifiers.
4. Construct the complete barrel in DD4hep; compare every sensitive transform,
   inventory, mass and ID. Run ROOT overlap checks and deterministic navigation
   and material rays. Exercise composition variations without changing geometry.
5. Retain commands, versions, fingerprints, hashes and results; propose changes
   in a separate implementation PR based on the unmerged PR #29 branch.

Code belongs in `detector/`; reproducible input export and validation in
`tools/pixel_barrel_dd4hep/`. The root CMake entry builds only this explicitly
named prototype. Generated compact data are reproducible build artifacts;
configuration and generator code are canonical, not copied hand-edited XML.

## Parameter and representation contract

All new numerical hypotheses below are **NODD DESIGN CHOICE**, pending expert
material/engineering review. The human authorized implementation and provisional
cable composition; this does not certify the particular numerical defaults.

| ID | Class | Implementation choice and rationale |
| --- | --- | --- |
| PB-C01 | NODD DESIGN CHOICE | Retain all PR29 module/sensitive transforms and its reference cable scenario. Preserve original module/patch IDs. Use local axes u=tangent, v=beam, w=radial outward. No new barrel tilt or row placement. |
| PB-C02 | NODD DESIGN CHOICE | DD4hep hierarchy detector → layer → stave → module → sensor substrate → active chip patch. Passive silicon substrate retains guards/seams, active daughters use identical silicon. One sensitive volume per original patch; 50 µm Cartesian readout with half-pitch offsets for the even 400 × 384 chip grid. No charge-sharing or seam-efficiency claim. |
| PB-C03 | NODD DESIGN CHOICE | Fill the module envelope with explicit 150 µm sensor, 150 µm ASIC, 50 µm polyimide flex (combined core/coverlay inventory), two 18 µm copper layers at provisional 50% area coverage, and 25 µm epoxy. These thicknesses come from pinned DES001 PM3-C02–05; patterned copper is homogenized, not full copper coverage. Keep the 20 µm bump standoff as unfilled space pending a bump inventory. Unknown bonds/passives/film stacks remain omitted inventory, not a zero-mass assertion. |
| PB-C04 | NODD DESIGN CHOICE | Graphite contact shims behind ASICs fill from their outward backs at w=0.245 mm to the PR29 body-back plane w=0.5 mm. This 0.255 mm derived interface refinement avoids a thermal air gap without moving sensors or the support stack. It is additional explicit material within the existing envelope. |
| PB-C05 | NODD DESIGN CHOICE | Keep PR29 support layers, pipe dimensions, ring/foot positions and densities. Bored foam, Ti walls and coolant are separate non-overlapping solids. Represent the earlier 0.08 mm equivalent internal glue inventory through an effective core mixture after subtracting pipe holes, preserving its specified volume without increasing stave depth. |
| PB-C06 | NODD DESIGN CHOICE | Cable outer-footprint composition defaults to Cu 10%, polyimide 40%, air 50% by volume. These are configurable placeholders, not cable specifications. Compare Cu 5% and 20% at fixed 40% polyimide. Remaining volume is air; packing void is separate. Convert volume fractions to mass fractions for DD4hep materials. |
| PB-C07 | NODD DESIGN CHOICE | Preserve the volume×length inventory of every PR29 longitudinal bundle. Export annular-sector solids, using effective materials normalized to their actual geometric volumes. |
| PB-C08 | NODD DESIGN CHOICE | Partition each end bay into non-overlapping radial bins in twelve phi sectors. Combine PR29 radial transport, axial handoff and collection-path inventories into these cells; normalize Cu/polyimide/Ti/CO2 volumes independently. This replaces overlapping illustrative turn envelopes with a simulation-effective representation; it does not add another copy of local cooling or longitudinal cables. Bends/manifold CAD is omitted. Keep source-to-cell assignments and conservation checks. |
| PB-C09 | NODD DESIGN CHOICE | Use inherited full-liquid CO2 density 1.0964 g/cm³ as the configurable material upper bound. The geometry does not imply liquid-only operating flow or qualify hydraulics. Provisional transport wall stays 0.15 mm. |
| PB-C10 | NODD DESIGN CHOICE | CFRP and foam use explicit carbon/epoxy effective compositions, with inherited bulk densities. Epoxy uses the public ODD C15H44O7 model at the inherited 2 g/cm³ density, as a placeholder for supplier resin/filler. Graphite is carbon; polyimide is C22H10N2O5. ROOT computes radiation/interaction lengths from composition: compare, do not overwrite, earlier scalar X0 screening assumptions. |
| PB-C11 | NODD DESIGN CHOICE | Propose numerical overlap tolerance 10⁻⁵ mm, transform tolerance 10⁻⁶ mm and analytical mass/volume relative tolerance 10⁻⁶ for this software check. These are numerical regression tolerances, not manufacturing allowances. No tolerance is relaxed to conceal an overlap. |
| PB-C12 | NODD DESIGN CHOICE | Use nominal pure-Si 2.329 g/cm³ and Cu 8.96 g/cm³, ODD air 0.0012 g/cm³ (N/O/Ar mass fractions 0.754/0.234/0.012), and the required but unused dilute-H vacuum recipe 10⁻¹² g/cm³. DD4hep selects Air for this test world. These software material defaults are centralized in `materials.py`; world medium is excluded from reported detector mass and material scans. They are not measured module/cable properties. |

**PB-F01 — FACT:** pinned DES001 at
`214747a3c83c140caa6c4ae9c3fb6486ac5cb825`,
`docs/design/DES-001-rd53-pixel-modules.md` PM3-C02–05, contains the adopted study
thicknesses and explicitly unresolved bump/bond/film inventory. A1 has a shifted
trial body centre relative to active silicon; use the actual pinned transforms.
This is a fact about the proposal, not a claim of manufactured thickness.

**PB-F02 — FACT:** SRC-DD4HEP-MANUALS, User Manual §2.8, defines material mixture
fractions by mass, or molecular composition by atom counts. The implementation
must convert configured volume inventories to mass fractions rather than pass
volume fractions directly to XML `fraction` tags.

**PB-I01 — INFERENCE:** density = Σ(volume_fraction × constituent_density);
mass_fraction_j = volume_fraction_j × density_j / density. For each effective
cell use actual constituent volumes divided by cell capacity, with remaining
space assigned air. Check 0≤Σconstituent_volume/cell_volume≤1, and conserve each
non-air constituent through export and DD4hep construction. Empty geometric
space is never counted as Cu, CFRP or liquid.

## Validation contract and limitations

Expected baseline counts: 4 layers, 82 staves, 2,750 modules, 6,206 sensitive
patches, 24 rings, 492 feet, 164 local cooling tubes. Global identifiers use
system/layer/stave/module/sensor fields; readout cell IDs add local x/y indices.
Geometry IDs are stable under cable material changes. Compare sensitive centres
and outward normals directly against the pinned layout, not regenerated ideals.

ROOT/DD4hep construction, overlap checks, physical-node counts, material masses,
identifier uniqueness, and straight navigation/material rays are required here.
Keep material composition sensitivity separate from geometry and heat balance.
Geant4 transport, digitization, thermal/pressure qualification, alignment/FEA,
endcap/global integration and ACTS conversion are explicitly future gates.
A runnable prototype does not resolve the omitted hardware inventory.

## Display convention (2026-09-30)

**PB-C13 — NODD DESIGN CHOICE:** assign volume display attributes by material
family using `detector/config/display.json`. Silicon is blue, carbon supports
and titanium grey, foam green, CO₂ cyan, copper/cables orange, polyimide yellow,
epoxy magenta and mixed end-bay services violet. Partial transparency exposes
nested components. These are visual labels, not material properties or changes
to dimensions, density, composition or sensitivity. Standard ROOT colours avoid
process-local custom colour IDs when exporting geometry. Validate RGB, colour
indices and transparency after reopening a ROOT export in a fresh process.
SRC-ROOT-TCOLOR documents the standard colour wheel; actual persistence is tested
against the installed DD4hep/ROOT versions. Existing numerical evidence remains
unchanged and is retained.
