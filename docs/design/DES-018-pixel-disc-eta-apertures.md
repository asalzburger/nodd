# DES-018 — Eta-limited apertures for outer pixel discs

- Status: DRAFT — isolated PROTOTYPE; human design approval pending.
- Created: 2026-10-06.
- Human request: optimize inner-ring removal on outer pixel discs for tracker
  coverage |eta| < 4 and the luminous region, following merged PR42.
- Human clarification: use pT >= 1 GeV (2026-10-06, this session).
- Baseline: PR42 merge `f2af2714dadd30a722f5ece11d0fd04e92cbfd39`
  on `codex/issue38-disc-overlap`; it is not merged into main. The two layouts
  and all original evidence in [DES017](DES-017-pixel-disc-support-variants.md)
  remain frozen controls. This study changes only an isolated removal schedule.

## Contract recorded before implementation

| ID | Classification | Requirement and rationale |
| --- | --- | --- |
| EA-C01 | NODD DESIGN CHOICE, explicit human direction | Preserve primary coverage for \|eta\| <= 4, pT >= 1 GeV, charges 0 and +/-1. Use the closed eta boundary for conservative selection. No claim for lower-pT tracks or secondary/scattered trajectories. |
| EA-C02 | NODD DESIGN CHOICE, inherited scope | Luminous z spans [-150,150] mm. Use transverse x,y in [-1,1] mm, a conservative superset of DES013's [0,1] mm test box; the square's circumradius is sqrt(2) mm. This is a bounded geometric hypothesis, not a measured luminous distribution. |
| EA-C03 | NODD DESIGN CHOICE, inherited ADR006 hypotheses | Bound uniform axial fields by \|Bz\| <= 4 T; validate 0/2/3/4 T and both charge signs in the existing first-host-exit/first-half-turn vacuum convention. A physical nonuniform field and material transport require separate validation. |
| EA-C04 | NODD DESIGN CHOICE | Remove only complete innermost physical rings, disc by disc, from both DES017 variants. Preserve all retained module IDs, transforms, local axes, levels, support datums and outer service bounds. Never recolour a reduced conflict graph or renumber surviving sensors. |
| EA-C05 | INFERENCE | For a sensor plane at z, the smallest straight transverse arc is s=(\|z\|-150)/sinh(4). In a uniform axial field, the chord is 2 sin(k s/2)/k, where k=0.000299792458 \|qB\|/pT in mm^-1. Subtract sqrt(2) mm for the vertex box. On the first outward half-turn, chord increases with s and decreases with k, so eta=4, pT=1 GeV and \|B\|=4 T give a conservative continuous lower radius bound. Check the half-turn domain explicitly. |
| EA-C06 | NODD DESIGN CHOICE | A ring is removable only if every corner of every active chip lies at least 0.10 mm below the continuous lower bound at that chip's actual plane z. This retention buffer is a screening choice, not a qualified manufacturing tolerance. Retain signed z offsets and luminous xy compensation from the full baseline before filtering. |
| EA-C07 | NODD DESIGN CHOICE | Evaluate all physical rings; select the largest contiguous removable inner prefix. Keep unsafe next-ring evidence and straight/on-axis and all-pT half-turn controls. Ring removal is an optimization within this fixed-family, fixed-placement catalogue, not a global layout optimum. |
| EA-C08 | NODD DESIGN CHOICE | Compare exact sensitive patch IDs before/after with matched seeded off-grid and targeted boundary tracks, including transverse vertex corners, luminous z endpoints, neutral tracks and bent tracks. Demonstrate that no in-scope baseline hit is removed. Preserve baseline gaps and out-of-scope hit losses rather than relabeling removal as hermeticity. |
| EA-C09 | NODD DESIGN CHOICE | Retain the common r27..188.5 mm,6.3 mm support and surviving pickups/mounts. Remove cooling tracks/circuits associated with empty chip rows; recompute per-disc heat, links, chains, pipe legs and accumulated services from the heterogeneous schedule. Do not multiply one nominal disc by eight. Leave CAD closeouts, hydraulics, mechanical/thermal qualifications and inherited adverse failures visible. |
| EA-C10 | NODD DESIGN CHOICE | Retain frozen old hashes and record actual new source/input hashes, native runtime, deterministic seed and tolerances. Native ACTS finite-plane checks audit the analytic result; they do not establish full-detector reconstruction or design approval. |

All new choices have **human design approver: pending**. Execution settings and
the clarified pT threshold will be recorded in the new tool's input register.

## Public basis and derivation

**FACT — SRC-PDG-KINEMATICS-2025:** PDG *Kinematics*, section49.5.2,
printed/PDF page8, equations49.47–49.48 define pseudorapidity and
`sinh(eta)=cot(theta)`. Therefore straight transverse distance to a plane is
`delta_z/sinh(eta)`; pseudorapidity is used, not a mass-dependent rapidity proxy.
[Public PDF](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-kinematics.pdf)
was inspected2026-10-06; its source-catalogue entry accompanies this study.

**INFERENCE:** integrate a circular transverse trajectory with constant curvature
k and longitudinal displacement `s*sinh(eta)` to obtain the chord above.
For `0 <= k*s <= pi`, derivatives give monotonicity in s and k. The triangle
inequality subtracts the maximum transverse vertex radius. Maximal radius of an
active rectangle occurs at a corner, so testing all four corners gives a bound
over the entire active island, without filling quad seams. This proves exclusion
over a continuous domain under the stated uniform-field/vacuum hypotheses;
finite track samples are additional implementation controls, not the proof.

The source constant and helix convention agree with the retained analytic
oracle in `tools/module_layout/intersections.py` / `acts_validate.py`. The minimum
first-turn chord factor2/pi is retained as an all-pT alternative; it must not
be confused with the user-selected pT>=1 GeV result.

## Review boundaries

Eta-limited exclusion supersedes the original full-annulus demand only for this
new user-authorized removal study. DES017's original-annulus failures, narrow
guard hypothesis, warm-coolant failure, fixed service failures and unsigned
engineering remain in their original evidence. This optimization must report
preserved in-scope hits separately from achieved continuous hermeticity.
No production description, barrel geometry, disc z position, physical field map,
design lifecycle or prior PR description is changed.

## Results

The [retained DES018 report](../validation/DES-018/results.md) removes ring1 on
discs5–6, rings1–2 on disc7 and rings1–3 on discs8–9 on each end, for both variants.
All retained placements/IDs and disc datums are unchanged. The minimum selected
exclusion margin is1.574 mm before the0.10 mm retention buffer. The next ring has
reachable finite-patch witnesses, including both1 GeV charge signs in4 T.

The schedule saves424 single-chip modules/chips and1139.712 W nominal over all18
discs. The mixed totals become2312 modules/5012 chips. Cooling circuits become248
instead of288. For each variant,1906 analytic tracks retain exactly the same
hit-ID sets;182 native in-scope tracks do likewise, with two out-of-scope controls
and exhaustive last-disc before/after checks retained.

Mixed reference trunk demand improves1.089→1.032× fixed capacity and still fails;
neck, adverse bandwidth, original baseline gaps and inherited engineering/thermal
limitations remain unresolved. No lifecycle advancement or integration is granted.
