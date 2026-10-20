# IB-M1 — MuonTech inner-barrel feasibility contribution

Input revision: `56f12ef5b2a9bd410cb77e95ac3140557d92f1b2`.
Assignment: explicitly supplied MuonTech fallback mandate; read-only repository.
Status: bounded DRAFT outline feasibility contribution. No design approval,
active-candidate adoption, chamber engineering or response qualification.

The requested move of the coil-plane B1 chambers below the BT inner legs cannot
retain the existing 500 mm chamber depth, fixed expanded HCAL and 50 mm margins.
The conditional R=5.75 m intercoil alternative clears the fixed hardware after
whole-rectangle packing, but increases B1 inventory and reduces the sampled
three-station full-depth geometric coverage. It remains **UNSELECTED**.

## Sources and ownership

All seven contract inputs were obtained with `git show REV:path`, with their
SHA-256 matching the dispatch. Additional pinned packing helpers come from
`tools/muon_layout/wheels.py` at the same revision. The eight execution inputs
and hashes are in `/private/tmp/pr90-IB-M1-source-manifest.json`.

Principal locators at the input revision:

- `docs/design/DES-040-muon-chambers-frame.md`, original bounded geometry and
  coverage definitions; reviewer-directed outer-barrel contract at lines 424–432.
- `docs/validation/DES-040/barrel-overlap-2026-10-20/candidate/geometry.json`,
  `configuration.chambers`, `magnetic_configuration`, `panels`, `supports` and
  `barrel_overlap_revision`. SHA-256
  `f4aebc7d5e1476d6f40f331d2aef0673fa6840ee1883015570089be6e79ad328`.
- `tools/muon_layout/barrel_overlap.py:48–72`, far-depth-face angular width
  derivation; `:89–207`, fresh source/radius/solid-keyed packing and seam merging.
- `tools/muon_layout/layout.py:21–30`, exact rectangular prisms and seed tiling;
  `:61–78`, existing subdivision and useful-size policy.
- `tools/muon_layout/geometry.py:78–100`, same-cassette full-depth crossings;
  `:125–183`, conservative finite-prism SAT and adaptive full-volume coil proof.
- `tools/muon_layout/wheels.py:193–206`, all-support-envelope certificates;
  `:256–263`, all-panel-pair AABB/SAT check.
- `tools/toroid_prototype/geometry.py:42–80`, exact rounded-racetrack distance
  and finite warm-sweep/slab union.

Working-tree AGENTS/PROJECT, role mandate, nodd-design-evidence and
nodd-review-validation skills, and pinned ADR-002/003/006 were read. The
coordinator's preconstruction DES040 addition was treated as workflow scope,
not substituted for the pinned numerical inputs. SysArch owns the actual HCAL
finite-solid source assessment under IB-A1. No new public-source technology
parameter is asserted here.

## Requested below-BT position

**FACT about the pinned prototype:** the BT inner straight centre is
`6.7−2.1=4.60 m`; the warm normal width is 0.50 m. Over the full B1 z span the
inner straight leg therefore has inner warm face at 4.35 m. Chamber radial
half-depth is 0.25 m and coil clearance is 0.05 m.

**INFERENCE:** an even coil-plane B1 prism below that leg must obey

`R_even + 0.25 + 0.05 <= 4.35`, hence `R_even <= 4.05 m`.
The exact upper value is a limiting bound: conservative expanded-obstacle
contact is rejected by the source kernel, so an accepted placement would need
a small strict guard below it. That worsens the HCAL fit.

The magnetic input's enclosing HCAL corner radius, 4.23946 m, would imply the
conservative sufficient exterior condition `R_even >= 4.53946 m`, leaving an
empty interval of 489.46 mm. That corner cylinder is an enclosing bound, **not
literal HCAL occupied material**; it is not used here to establish a collision.

The separately coordinated IB-A1 actual-source assessment identifies the clean
expanded HCAL at commit `0e8530d56d171f38c9d53d3c60c8b48803680bbd`, matching the
source hashes in pinned `docs/validation/MUON-001/hcal-material.json`. Its
finite last steel plate spans local normal coordinate 4.105–4.135 m and its
rear aluminium cover spans 4.148–4.158 m. The point `(4.12,0,1) m` lies in both
the steel plate and requested `B1/F00/Z02` at the maximum allowed R=4.05 m;
`(4.153,0,1) m` witnesses the rear cover. IB-A1 reports finite intersections for
all 48 moved coil-plane panels. Its true polygon/finite-width clearance bounds
require R at least 4.458 m for the 0/90 degree planes, or 4.530252500274383 m
for the 30/60 degree classes, versus the 4.05 m BT limit: deficits of
408–480.2525 mm. These actual-HCAL results are attributed to IB-A1, not claimed
as an independent MuonTech rerun.

Consequently this request needs a separately selected change to chamber depth,
HCAL or BT. The best flat-face gross HCAL-to-warm-BT space is only
`4.35−4.158=0.192 m`; after two 50 mm margins, only 92 mm remains, before the
stricter rotated finite-width condition. A thin reservation is not a validated
alternative MDT chamber. None of those hardware changes is selected here.

## Conditional fixed-hardware outward option

**UNSELECTED NODD DESIGN CHOICES supplied by the assignment:** keep twelve
coil-plane facets at R=5.20 m; move only twelve odd intercoil facets to R=5.75 m;
target 0.1 degree neighboring angular overlap with 30 mm border. Retain 500 mm
depth, half-z=6.4456 m, 4 m maximum seed, 20 mm seams/neighbor clearance,
50 mm coil/support margins, minimum z span 0.50 m, minimum area 0.25 m², and
subdivision depth six. All B2/B3/endcaps/frame/magnetic inputs stay fixed.

**INFERENCE from full depth:** with h=0.25 m, border b=0.03 m and adjacent
facet pitch 15 degrees,

`w_even=(5.20−h)*tan(7.5deg)−0.01 = 0.6416798630576094 m`

`a_even=atan((w_even−b)/(5.20+h)) = 6.403783462153276 deg`

`a_odd=15.1deg−a_even = 8.696216537846722 deg`

`w_odd=(5.75+h)*tan(a_odd)+b = 0.9477235414251715 m`.

Thus the odd full-width template is 1.895447082850343 m wide. Its outer corner
radius is 6.074387204564051 m. The neighboring even solid's projection onto the
odd radial normal gives a rigorous whole-template separating-plane gap of
69.625277306491 mm, exceeding the 20 mm requirement. The corresponding minimum
stagger from this supporting-plane test is 500.374722693509 mm; the assigned
550 mm stagger passes. All 24 adjacent full-z template pairs separately pass
the conservative expanded-prism SAT test at 20 mm.

B2's global inner radial bound is 6.45 m, giving at least 375.612795435949 mm
radial separation from every candidate B1 corner. Existing even B1 has at least
710.54 mm separation above the enclosing HCAL corner bound, so the outward
option is demonstrably HCAL-clear without treating that bound as material.

## Actual fresh packing and finite checks

Command:

```sh
python3 -B /private/tmp/pr90-IB-M1-check.py \
  --repo /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout \
  --revision 56f12ef5b2a9bd410cb77e95ac3140557d92f1b2 \
  --output /private/tmp/pr90-IB-M1-check.json \
  --outlines-output /private/tmp/pr90-IB-M1-unselected-B1-outlines.json
```

Final recorded execution: Python 3.14.6, NumPy 2.5.1, 17.090 s, exit zero.
No dependency installation or native framework/runtime was used.

The checker automatically extracts all eight required inputs with `git show`
into a fresh temporary directory, verifies their pinned SHA-256 values, then
imports only that source tree. Extraction commands, source hashes and checker
hash are stored in the result JSON. It requires no pre-existing scratch source
directory. The portable-CLI-only rerun produced identical scientific fields,
all coverage/loss IDs and byte-identical 144 B1 outlines; see
`/private/tmp/pr90-IB-M1-portability-check.json`. The outline SHA-256 is
`e1e03932c3adda94c8e6338ca27cce2d9829e49a6083aecf0734ed62415c8fe1`.

- Fresh B1-only packing starts with 96 compartments, subdivides 144 times,
  accepts 144 whole prisms, and rejects 96 leaves for support clearance.
  Without support exclusions all 96 full seed prisms are coil-clear.
- Obstructing members include ECT front inner carrier-ring sectors, spokes and
  radius-5.8 m lugs near |z|=6.30 m. This is a real fixed-frame interface; no
  carrier or lug is moved. The subdivisions are conservative packing loss,
  not a statement that the entire rejected leaf is filled with material.
- Fresh C12 source proof cache: 32 unique certificates, 4,464 adaptive cells,
  actual radius/solid/config key, 0 historical coil certificates loaded.
- Every one of the 144 accepted B1 prisms additionally passes an uncached
  actual-orientation coil audit at 50 mm: 52,752 adaptive cells, zero unresolved
  cells accepted. This is a cache/orientation check with the same mathematical
  kernel, not an independent coil model.
- Every accepted B1 receives a fresh certificate against all 484 fixed support
  envelopes through conservative AABB selection and SAT at 50 mm.
- All 437,580 unordered pairs among the 936 conditional panels are freshly
  considered by AABB/SAT; zero panel-volume conflicts. The 792 B2/B3/endcap
  panels are retained value-equal. All 48 even B1 outlines retain their exact
  geometry. The complete magnetic configuration and support object remain
  unmutated; no field map is read or modified by this checker.
- IDs remain unique, all z spans >=0.50 m and all areas >=0.25 m²; minimum
  accepted area is 0.7379415409245391 m². No accepted tangential width is below
  0.50 m. No z-seam merge is attempted in this option.
- Adverse controls reject an occupied BT test solid and occupied support,
  detect a duplicate chamber, detect widening without radial staggering, and
  confirm that changing actual radius changes the coil-cache key.

The actual B1 inventory changes from one family/96 panels to four families/144
panels; the conditional whole-system total is 936, while the active baseline
remains 888.

| Tangential width (m) | z length (m) | Count | Interpretation |
| --- | --- | --- | --- |
| 0.937723541425 | 0.78695 | 48 | Odd split fragments near frame |
| 1.283359726115 | 3.2078 | 48 | Retained even panels |
| 1.895447082850 | 1.5939 | 24 | Odd full-width shortened panels |
| 1.895447082850 | 3.2078 | 24 | Odd full-width seed panels |

Per odd facet the outer accepted fragments stop at |z|=5.63865 m, below the
retained nominal 6.4456 m endpoint, because the unchanged front carrier crosses
the R=5.75 m templates. Seed/split seams remain explicit.

## Fresh geometric coverage and explained losses

The sole bank contains **65,536 iid directions over full 4pi**, uniform in
cos(theta) and full azimuth, NumPy default RNG seed 40087. Rays start at the IP
and remain straight. A panel passes only when both depth faces lie within the
same panel's footprint, optionally inset by 30 mm on all footprint edges.
For the three-station observable, all barrel and endcap panels with the same
station number are ORed, then the three station booleans are ANDed. These are
**three distinct stations, not necessarily three barrel stations**. The B1
barrel row counts only barrel-station-1 panels. No separate central bank and no
native ACTS, Geant4, response or reconstruction study was run.

| Full-depth observable | Baseline | Conditional option | Difference (percentage points) |
| --- | --- | --- | --- |
| B1 barrel, envelope | 64.21814% | 66.01563% | +1.79749 ±0.15123 sampling SE |
| Three stations, envelope | 65.61584% | 64.26697% | −1.34888 ±0.08884 sampling SE |
| B1 barrel, 30 mm border | 60.01740% | 63.92517% | +3.90778 ±0.16080 sampling SE |
| Three stations, 30 mm border | 57.44019% | 56.39801% | −1.04218 ±0.08586 sampling SE |

All denominators remain 65,536. Errors are paired iid sampling standard errors,
not dimensional uncertainty or evidence of native-transport convergence.
The border three-station comparison has 1,245 gained and 1,928 lost directions.
All four independent sample quarters have negative three-station differences
(−0.8362, −1.2573, −0.9949, −1.0803 percentage points).

Fresh no-frame packing and continuous-full-z template controls partition all
1,928 border three-station losses without overlap:

| Loss class | Count | Sampled absolute eta range |
| --- | --- | --- |
| New fixed-frame packing exclusions | 565 | 0.77745–0.92702 |
| Retained z seed seams / same-cassette depth traversal | 1,034 | 0.50714–0.55508 |
| Finite B1 outer-z reach after outward move | 329 | 0.92631–0.99829 |

The result JSON retains direction IDs, phi/eta and before/after panel witnesses.
For example border direction 198 (eta −0.7923262, phi 278.672665 deg) loses
`B1/F19/Z00` through frame packing; direction 187 (eta 0.5542215,
phi 199.297416 deg) loses `B1/F13/Z02` through a z seam; direction 89
(eta −0.9912949, phi 229.419358 deg) loses `B1/F15/Z00` through finite end reach.

This is why a 0.1 degree full-width template overlap is not an all-direction
coverage gain. Moving a panel outward changes the eta image of its z seams and
endpoint. The large-face same-cassette requirement also rejects traversals
split across adjacent modules. The exact eta=0 ray lies in the retained common
20 mm central z seam; ideal transverse template angles are not a claim of
actual eta=0 coverage.

## Disposition, files and remaining assumptions

The requested inward option has a concrete physical blocker. The tested outward
option is geometrically admissible only with the exposed frame cuts, extra
families and poorer sampled three-station result; it remains unselected.
Keeping the active 888-panel candidate is a concrete available choice while a
human considers whether to authorize a different chamber/frame/coil/HCAL
interface. No further radius, z, depth or hardware optimization was undertaken.

Repository files changed by IB-M1: **none**. Scratch deliverables only:

- `/private/tmp/pr90-IB-M1-report.md` — this contribution;
- `/private/tmp/pr90-IB-M1-check.py` and `pr90-IB-M1-check.json` — executable
  bounded check and final actual results, including rejected leaves and losses;
- `/private/tmp/pr90-IB-M1-portability-check.json` — identical-result comparison
  after adding the portable CLI and automatic temporary source extraction;
- `/private/tmp/pr90-IB-M1-extract.py` and `pr90-IB-M1-source-manifest.json` —
  exact-revision extraction/hash validation;
- `/private/tmp/pr90-IB-M1-unselected-B1-outlines.json` — only conditional B1
  outlines, prominently labeled unselected; no full active-candidate export;
- `/private/tmp/pr90-IB-M1-src/` — pinned source extracts.

Reproduction uses an existing checkout containing the input Git objects and
existing NumPy. Run the checker command above with the desired checkout and
scratch output locations. `--outlines-output` may be omitted, in which case its
filename derives from `--output`; this bounded checker rejects a different
revision. The earlier extraction utility/manifests are supporting read evidence,
not prerequisites. The actual HCAL companion proof is preserved in
`/private/tmp/pr90-IB-A1-report.md`, `pr90-IB-A1-checker.py` and
`pr90-IB-A1-results.json`; those report exact HCAL blob identities independently.

Unresolved: chamber multilayer/tube construction, readout, local services and
mounting, sag and alignment, backgrounds, timing/spatial response, upstream
material transport, actual installed HCAL field and structural/cold-load
qualification. Geometry does not establish reconstructed efficiency or momentum
resolution. No human acceptance or DES/ADR status change is recorded.
