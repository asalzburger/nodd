# Issue #38: mounting, cooling and services review response

Status: review draft / PROTOTYPE. Date: 2026-10-15. Assignment: MECH-PUBDOC.
No design sign-off, mechanical qualification or publication is recorded here.

This package answers [Susanne Kuehn's forwarded comments](https://github.com/asalzburger/nodd/issues/38#issuecomment-6163716265)
and [Markus Elsing's strip-mounting question](https://github.com/asalzburger/nodd/issues/38#issuecomment-6163927822).
Coverage and material plots are a separate response. The text changes and
drawings below are concrete editorial corrections; the engineering gaps remain
explicit rather than being treated as resolved by a figure.

## Revision contract and review files

- Parent input: `5b4e5d9e563505aea17e9b792458708c3175ec4a`.
- Current TDR input: `7625cf6054f5761228be6d8d2de24d43f155bd19`.
  Its chapter blobs were read with `git show REV:path` from the existing
  `docs/tdr` checkout. `pixel-detector.tex` is a complete replacement of that
  current chapter, retaining its selected six-ring, trimmed mixed-module model.
- The originally reviewed issue attachment has SHA-256
  `667b709316c1aa1ab8c006985058017e8235f5548af343b77ab769cf9649ea94`.
  Its line/figure numbers refer to an older five-ring narrative. Those numbers
  must not be applied to the current manuscript as though they identify the
  same layout. The parent coordinator inspected that attachment; this author
  read its extracted text and the pinned current TDR source.
- [Corrected pixel chapter](pixel-detector.tex): terminology, radius/$z$
  headings, stave mounting and its incomplete cage, glue inventory, thermal
  assumptions, graphite feet/tongues and pigtail handoffs.
- [Strip-mounting insert](strip-mounting.tex): a compact comparison of all four
  barrel/endcap mounting paths and constraints. Insert after the long-strip
  chapter, before strip references, or integrate its paragraphs into the two
  corresponding chapters during editorial review.
- [Four-page figure booklet](figures/mechanics.pdf): barrel stack and mounting;
  endcap foot and tongues; pigtail handoffs; strip mount topology.
  [Contact sheet](figures/mechanics.png) provides a preview.
- Generator: [drawings.py](../../../tools/issue38_mechanics/drawings.py).
  Each drawing is schematic with independent display scales. Numerical labels
  describe the recorded prototype; dashed joints/routes identify concepts.

The endcap pickup sequence is checked against `trimmed_export.py`,
`support` pickup loop (lines 213--235 at the input revision): from plate
outward, cradle -> graphite -> insulation -> TIM -> bond -> module. The figure
shows the same sequence from module back toward the plate. TIM and bond are
separate geometric layers that both use the Epoxy material recipe.

The short-strip barrel ring is **inside** its stave: the actual exporter uses
`r_0-20` to `r_0-17 mm`, and the beveled shoe seats on its outer cylindrical
surface. This was checked against pinned
`tools/short_strip_barrel/inputs-phi-tilted.json` lines 42--44,
`export.py` lines 184--188 and `model.py:foot_profile` lines 82--96. The strip
insert and page 4 identify an inner bearing ring and an outward radial arrow.

The replacement chapter expects the existing TDR figures, `generated/` tables,
macros and bibliography. Copy `mechanics.pdf` to its `figures/` search path.
It references pages 1--3; the strip insert references page 4. This is review
source in the parent repository. The frozen DES-019 manuscript, TDR gitlink,
production geometry and Overleaf contents are not modified by this package.

The inherited `27 mm` passive pixel aperture belongs to standalone DES-019.
DES-025's combined BeamPipe+Tracker assembly opens affected passive annuli to
`28.8 mm`, giving `1 mm` radial clearance to the `27.8 mm` beam-pipe outer wall;
sensor transforms, guards, IDs and disc reference positions remain unchanged.
The chapter now names this distinction at the plate description and service
ledger, and the figure identifies the standalone plate. No inherited ledger
dimension is silently changed. Evidence: pinned DES-025, "Beam-pipe clearance
amendment for review", lines 54--73. This is an integration choice under review,
not mechanical sign-off.

## Point-by-point answers

| ID / reviewer point | Answer and concrete change | Evidence / remaining boundary |
| --- | --- | --- |
| SK-T01: What are graphite shims? | They are thermal contact spacers between each ASIC back and the module support-side envelope. The ASIC back is at local `w=0.245 mm`; a `0.255 mm` graphite layer reaches `w=0.500 mm`. The chapter defines the term at first use; figure page 1 shows its position relative to the epoxy interface. | DES-012 PB-C03/04; `tools/pixel_detector_dd4hep/trimmed_modules.py`, `module_xml`, `asic` and `contact_shim` records. This describes nominal material. Grain direction, ASIC bond and contact resistance are not qualified. |
| SK-T02: Slim barrel introduced too early. | The intended term is **slim longitudinal sensor edge**, not a separate barrel type. The replacement defines it beside the barrel packing: the selected inactive border is `0.20 mm` along `z`. Barrel and endcap body/guard dimensions stay separately tabulated. | Current TDR barrel layout and sensor-dimensions table; DES-012/013 and DES-019 PM-C03 govern the different module frames. Public slim-edge work motivates a small border but does not validate the selected nODD process/bias. |
| SK-T03: What are guards? | A guard here means inactive silicon excluded from the geometric active map. It is not a specified number or width of fabricated guard-ring implants. Added before the first use of the dimension table. Internal quad seams also remain passive silicon. | Current TDR sensor-dimensions table; original issue attachment lines 43--46 already made this distinction, but too late. No implant layout or radiation qualification is inferred. |
| SK-T04: Table datums should say radius and z. | Barrel column now says **Radius r**; disc caption says **reference z positions** and identifies the central support plane. Sensor positions include the separate mounting-face and height offsets. | Current TDR barrel and disc tables. A reference radius is not the radius of every staggered sensor. Values and generated table rows are unchanged. |
| SK-M01: How are staves mounted? Please draw structural body. | ASIC/module loads pass through the local support stack to the narrow CFRP/foam spine, discrete CFRP feet, surrounding bearing rings and finally a common cage/end support. Figure page 1 shows radial contact and all six `z` stations. The `z=-546 mm` station is the axial locator; other contacts propose sliding/compliance. | DES-002 PS-C01--06/10; DES-012 PB-C05; `tools/pixel_support/mounting.py` `make_mounts` and `check_mounts`. Rings and foot envelopes are represented. Cage/end connections, mount adhesive/inserts/preload and their stiffness are **open**. The dashed cage is a load-path requirement, not an added solid or invented wall thickness. |
| SK-M02: Calculate stiffness or state required stiffness/thickness. | Added the sourced displacement/modulus screens to the chapter. The supporting derivation and retained numerical example below state what `EI` would be required for a genuinely supported span and how skin thickness enters. This also explains why the ring pitch alone cannot select a cage wall. | DES-002 PS-I04/PS-C10, retained `screening.json`, and the explicit ungrounded-ring limitation in `mounting.py`. Actual composite section, core shear, ring/cage reactions, joints, service forces, thermal bow and modal loads remain **open**. No present-baseline sag or FEA result is invented. |
| SK-C01: Why -35 C barrel and -40 C endcaps? | These are separate screening assumptions, not an established plant requirement. The barrel uses -35 C with a prospective 15 K cm2/W thermal target. Endcaps use -40 C with a different narrow anisotropic contact path; their -35 C sensitivity fails in retained cases. Added this distinction beside the cooling table. | DES-002 PS-C07/08 and PS-I03; DES-014 EC-C09/12/16; DES-017 SV-C08 and results, thermal section. Mixed-disc worst stress temperatures are -16.857 C at -40 C coolant and -11.857 C at -35 C in the recorded screen. They are hypotheses, not measured bounds. Common operating temperature needs thermal/leakage/hydraulic closure; no set point is changed. |
| SK-C02: Raised graphite feed and tongues need pictures. | Corrected to **raised graphite support foot**: it is a solid `6 x 8 mm` thermal stem, `0` or `1.65 mm` high in the mixed baseline, and carries no coolant. The three tongues are `10 mm`-wide radial extensions of the sandwich into the mount sectors. Figure page 2 shows both separately. | DES-017 SV-C05/06/09; DES-019 PM-C04/05; DES-014 EC-C10/13. Four quad thermal contacts do not constitute four rigid alignment datums. Cone/slot/plane contacts, shell bond and end supports remain concepts pending joint/FEA/cold-cycle work. |
| SK-G01: Is stave glue missing relative to the endcap drawing? | The drawing was incomplete: the stave already contains `0.100 mm` explicit **Epoxy** at the module-support interface, `0.025 mm` electrical insulation and `0.080 mm`-equivalent internal glue. Module flex epoxy is a separate `0.025 mm` term. The revised chapter and page 1 show these. Endcap pickup TIM and adhesive are `0.025 mm` each. | DES-012 PB-C03/05; `tools/pixel_barrel_dd4hep/export.py` support-layer loop and `materials.py:core`. The core mixture adds glue in pore space while retaining the prescribed foam mass after tube bores; it is not a resolved skin-bond solid. Actual ASIC-to-shim and mounting-joint bonds remain omitted/unresolved inventory. No new glue mass was added to the simulation. |
| SK-S01: Show pigtail connections. | Figure page 3 and the service text now trace module flex pad -> pigtail/strain relief -> insulated longitudinal barrel bundle -> sector collector -> trunk. On discs, each tail drops beside its own foot to the same-face ring bus -> radial fan -> rim collector -> trunk/bypass. | DES-014 EC-C11/14; DES-012 PB-C06--08; DES-019 PM-C06. Endcap flex/fittings and remote service cells are material inventories. Connector pinouts/heads, termination details, exact slots, bend sweeps, strain relief and electrical continuity remain **open**; conceptual symbols do not claim manufactured connectivity. |
| ME-M01: Explain strip mounting. | Added `strip-mounting.tex` and figure page 4. Short strips use one-face graphite pickups and sandwich-to-ring webs (barrel), or three lugs to inner/outer frames (petal). Long strips use both faces of one sandwich, potted/keyed barrel mounts and three petal contacts with specified sliding directions. The text identifies the external cage/ring reactions and handling limitation. | DES-020 SB-C04/07/15; DES-021 SE-C04/06; DES-022 LS-C02--04; DES-023 LE-C02/03/07. Current TDR realizes 17 long-barrel stations, distinct from the minimum-count screen. Global frame stiffness, joints, cold glue stress and long-petal horizontal handling remain open. |

## Stiffness requirement and limits of a beam screen

The following is an **INFERENCE**, using the simply supported, uniform-load
Euler--Bernoulli equation already recorded as DES-002 PS-I04. For distributed
transverse load `q` in N/m, span `L` in m, and bending allocation `delta_b` in m:

```text
delta_b = 5 q L^4 / (384 EI)
EI_required >= 5 q L^4 / (384 delta_b)               [N m^2]
```

Here `q` includes the loaded stave mass, coolant and services under the selected
load factor. The inequality requires actual support reactions at the span ends.
It cannot be applied independently to each ring interval until a cage/ring/joint
model establishes those reactions. A shell that sags with the rings contributes
common displacement even when local stave bending is small.

For a sandwich whose core-shear stiffness is `S = kappa G A_core` in N, a useful
additional uniform-load term is `delta_s = q L^2/(8S)`. Allocate the complete
displacement first:

```text
delta_b = delta_allowed - delta_s - delta_joint - delta_cage - delta_other
EI_required >= 5 q L^4 / (384 delta_b), provided delta_b > 0.
```

`delta_other` must cover relevant thermal/pressure/service deformation; this is
an allocation equation, not a proof that these effects add as one known scalar.
If the available residual is nonpositive, adding skin bending rigidity alone
cannot satisfy the displacement requirement. DES-022 LS-I01 provides the
existing strip bending-plus-core-shear precedent; the pixel DES-002 calculation
omits shear and cannot qualify it.

For two equal thin skins, each width `b`, thickness `t`, separated between their
centroids by `h`, `I approximately b t h^2/2`; therefore
`t >= 2 EI_required / (E b h^2)` at fixed `h` is a first bending estimate.
The pixel stave has unequal skin widths. Its actual section must instead use
`I = sum(b_i t_i^3/12 + b_i t_i (y_i-ybar)^2)` and the laminate stiffnesses.
Orthotropy, foam shear, local indentation, torsion, adhesive strength, buckling,
joints and manufacturing constraints still govern. The dimensions recorded in
the chapter remain prototype choices; no cage thickness is selected here.

The retained DES-002 candidate-A arithmetic illustrates the span sensitivity:

| Historical fixture | I [mm4] | EI at E=100 GPa [N m2] | q [N/m] | Sag at 250 / 560 / 1120 mm [um] | EI needed at 250 / 560 / 1120 mm for 50 um bending only [N m2] |
| --- | ---: | ---: | ---: | --- | --- |
| Single, 47 modules, 23/10 mm upper/lower skins | 18.8928 | 1.88928 | 0.86983 | 23.42 / 589.56 / 9432.93 | 0.88483 / 22.2768 / 356.429 |
| Quad, 24 modules, 43.2/24 mm upper/lower skins | 41.8207 | 4.18207 | 1.76220 | 21.43 / 539.58 / 8633.24 | 1.79260 / 45.1310 / 722.096 |

These are **historical retained fixtures**, not recalculated current-baseline
predictions. Source: parent revision above,
`docs/validation/DES-002/screening.json`, `layers[0/2].candidates.A`;
the load is its full-liquid support plus its module payload times 9.80665 m/s2.
The current barrel population and slim module outline differ. Large-span linear
results are failure indicators; actual large displacement requires nonlinear
analysis. The table gives no qualification of cage stiffness or alignment.
DES-002 PS-C10's 50 um static and 5 um running-change values remain proposed
targets, with no approving human recorded.

To close SK-M02, an engineering owner must supply the cage/end-support section
and laminate, bearing/joint stiffness and preload, core shear data, complete
payload/service loads, gravity/orientation and handling cases, temperature/CTE
and pressure excursions, modal/excitation requirements and displacement
allocations. Coupled stave/ring/cage FEA and cold-load metrology must establish
that the selected thicknesses satisfy those requirements. This package makes
that missing design input visible; it does not replace it with an arbitrary wall.

## Source/claim audit

All nontrivial geometry/material values above are inherited **NODD DESIGN
CHOICES**, with approval pending in their DES records. Statements that the code
contains a volume, or that a retained report lists a number, are facts about
those pinned artifacts. They do not independently verify the cited public
literature or convert a screen into measured detector performance. No new
scientific source or material constant is introduced.

SHA-256 values below are for `git show <full-revision>:<path>` bytes.

| Revision / path | SHA-256 |
| --- | --- |
| TDR `chapters/pixel-detector.tex` | `eb3c619c54b91f8fd35298976f45912218e1bf4a954eea996a180e18b037f98a` |
| TDR `chapters/short-strip-detector.tex` | `a61395af5e60e41c7bbefe1117eda280daee6e237992488d9df92b9a4bdd90f2` |
| TDR `chapters/long-strip-detector.tex` | `8cb13ed8dd7ee431cf39a665680021528cd6f1fbab79dfdc267a947f8177cf28` |
| Parent `docs/design/DES-002-pixel-barrel-support-cooling.md` | `2e8d0b9bc48b5ff4cd2a30b9c3146d6e58869024ca5548f56d4b2b9637c72754` |
| Parent `docs/design/DES-012-dd4hep-pixel-barrels.md` | `a80a864563c2eab84e95362b44376ebdb0faba35c9d07e969de5c59af3e1e4a2` |
| Parent `docs/design/DES-014-pixel-endcap-support.md` | `eae67c13c87015280c0ec8891f717359e2783a29ed97ce47eb9035ef3bc54df3` |
| Parent `docs/design/DES-017-pixel-disc-support-variants.md` | `265eb7ab71bac736ef476b6e7f5cde4d5e3d541bc72256b7f0614fa7df5b36f0` |
| Parent `docs/design/DES-019-trimmed-mixed-pixel-dd4hep.md` | `c30cf43c9fcbcb30aa0e6ef8c9b41290046ad4d7af94b2d43bfdb96ca234e5dd` |
| Parent `docs/design/DES-020-short-strip-barrel.md` | `2958cffd82660a4596683019ed9c774f5c3dd36dd0603a33bc515697d10e97cd` |
| Parent `docs/design/DES-021-short-strip-endcap.md` | `a7bafba1ca4e2b828f59191cba35174cea1d869f4aa09c8c5fac4277e63e4d3f` |
| Parent `docs/design/DES-022-long-strip-barrel.md` | `13ad7f93b72a4d27741863cb04ea7fed08e8ab403eb83cca80793832c2f12eac` |
| Parent `docs/design/DES-023-long-strip-endcap.md` | `8817e70fa0c5068285a608bc92c49e244b968c4116f48a915f07a15b28941018` |
| Parent `docs/design/DES-025-tracker-dd4hep-gen3.md` | `0569e49038b25a4d983f68f45103e2d0287049bbfa2e995dc0131abc8bc0c6a5` |
| Parent `tools/pixel_barrel_dd4hep/materials.py` | `1d11107f7dda39420ccbb8c328d32a9087ac51d9da69f9aa492f29fc8f673ca6` |
| Parent `tools/pixel_barrel_dd4hep/export.py` | `d810922c23cc2351455c149118f3e62d80a13fbfe840d02a94e3e59da9b0711a` |
| Parent `tools/pixel_detector_dd4hep/trimmed_export.py` | `6b836801f01217d7323ec4e1b9af0b155954452db36d73c150be7a6d368d4c6f` |
| Parent `tools/pixel_support/mounting.py` | `fcb6eeacf826c0a7970b5696ce1a937d1897f57e7561c4ebcf93c2ce56f24f3c` |
| Parent `docs/validation/DES-002/screening.json` | `dfd32ac804287765b4147912c7eaddf0e10aeba80ccd9831fb78b8ba4ecad40a` |
| Parent `docs/validation/DES-017/results.md` | `8fc55f283e4e5db07ae643f0246318efa50a1b11541af9fd61bb9af73375afa4` |

## Reproduction and checks

The generator needs an existing Python with `reportlab`, `pypdfium2` and
`Pillow`; no DD4hep/Geant4 runtime is needed for these documentation changes.

```sh
python3 -B tools/issue38_mechanics/drawings.py
```

Checks actually run by MECH-PUBDOC:

- Python syntax parse; all four PDF pages and expected page-specific labels.
- Balanced LaTeX environments and unique labels in both edited source files.
- Every source-audit SHA-256 above checked against the exact pinned Git bytes.
- Historical beam equation independently recomputed against all retained
  single/quad fixture spans, agreeing to relative tolerance `1e-12`.
- Figure regeneration repeated with identical PDF/PNG hashes.
- Rendered contact sheet inspected; pickup order checked against the producer.
- Text/source whitespace check passed. A whole-tree `git diff --check` treats
  this small PDF as text and flags its valid fixed-width cross-reference rows;
  their required PDF whitespace is preserved.

The coordinator compiles the replacement within a temporary copy of the pinned
TDR and records the full build separately. Compilation and rendering do not
grant engineering approval. No new thermal, structural FEA, pressure, electrical
or mechanical qualification test is claimed.
