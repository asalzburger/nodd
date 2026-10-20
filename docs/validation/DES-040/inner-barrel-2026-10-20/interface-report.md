# IB-A1 — Exact-revision inner-barrel physical interface assessment

Assignment: IB-A1. Role: SysArch, with the complete mandate explicitly supplied to a generic subagent; no native profile loading claimed. Mode: read-only repository assessment. Input revision: `56f12ef5b2a9bd410cb77e95ac3140557d92f1b2`. Governing design: DES-040/DES-039, both isolated unsigned PROTOTYPE work. Review request: PR90 human comment `6288294033`, as supplied in the bounded assignment; no external message was sent. Human engineering approval: none.

## Finding

Moving the existing 500 mm-deep coil-plane B1 chambers below the fixed BT inner legs cannot preserve the present HCAL. The conservative corner bound gives an empty chamber-apothem interval `[4.53946, 4.05] m`, a 489.46 mm deficit. The obstruction is also present in actual finite HCAL source-model material: all 48 moved coil-plane B1 panels at the limiting `R=4.05 m` intersect explicit Steel235 plates or aluminium rear-cover prisms. Thus it is not merely a failure of a filled corner-radius cylinder approximation.

The 888-panel candidate remains the input baseline: 696 barrel + 192 endcap, including 96 B1 panels, and all 484 support envelopes. No layout, magnetic map, OBJ, endcap, frame, chamber internals, material or response assumptions were changed. Scratch trial shapes are deliberately invalid counterfactuals, not a generated or selected candidate.

## Source identity and interpretation

All seven assigned source files were read with `git show 56f12ef...:path`; the large geometry artifact was parsed in full. The result JSON records SHA-256 and byte counts for every scientific input. The assigned hashes match the prompt. Further pinned evidence is `56f12ef...:docs/validation/MUON-001/hcal-material.json`, which explicitly identifies HCAL source revision `0e8530d56d171f38c9d53d3c60c8b48803680bbd` and source hashes. That commit is available in the local Git object database, and the sibling HCAL repository was also identified by the coordinator. Its AGENTS.md was read before inspecting its source.

The following additional exact HCAL blobs were read and independently SHA-256 matched against the pinned MUON-001 artifact:

| HCAL path at `0e8530d...` | SHA-256 |
| --- | --- |
| `tools/hcal_barrel/config.json` | `969f05111039de2686d9454a29fe348c56a91a5316716515fdfedafea5479d64` |
| `tools/hcal_barrel/design.py` | `14692cff976bef5bdb19aa5d9897b5fd89297ecc9f9bb2e89cc1a69928a9d3e6` |
| `docs/validation/DES-037/summary.json` | `68c4aa00a43b4e813d6c88552e000caf67cdb178e668b223c21f377b88117753` |

The older `56f12ef...:tools/calorimeter_hardware/assemblies.json` is the earlier smaller assembly and does not represent this HCAL; it was not substituted. Its different 3.83275 m corner is not an applicable clearance input.

Recorded dimensions are **NODD DESIGN CHOICES**, not independently measured detector facts. The geometric bounds, intersections and numerical values below are **INFERENCES** from those exact source choices. Warm envelopes and current-pack sweeps remain source-model reservations/current allocations, not an engineered case/conductor material description. HCAL Steel235 and aluminium witnesses refer to finite material parts in the pinned prototype, not installed-detector qualification.

Relevant precise code locators:

- `56f12ef...:tools/toroid_prototype/geometry.py:36,49`: exact rounded-centreline distance and finite tangential-slab sweep mask.
- `56f12ef...:tools/muon_layout/layout.py:26`: actual tangential/z barrel-prism frame.
- `56f12ef...:tools/muon_layout/geometry.py:125,145`: source SAT and adaptive full-volume coil-clearance conventions.
- `56f12ef...:tools/muon_layout/barrel_overlap.py:48,323`: full-depth/border angular definition and conservative HCAL corner-bound check.
- `0e8530d...:tools/hcal_barrel/design.py:43,94,99,141,164`: sector frame, usable axial extent, finite steel plate radial bands, rear cover, nominal corner derivation.

## Hard radial bounds

Use `u` radially outward in a BT coil's meridional plane, `t` tangent, `z` along the beam; metres and right-handed Cartesian frames. B1 half-depth `h=0.25 m` and coil clearance `c=0.05 m` remain fixed.

The BT inner straight leg centre is `6.7−2.1=4.60 m`. The warm inner face is `4.60−0.25=4.35 m`. Therefore a whole rectangular chamber below the leg must satisfy

`R+h+c <= 4.35`, hence `R <= 4.05 m`.

The current kernel treats contact with a conservatively expanded obstacle as conflict, so `4.05 m` is a limiting upper bound, not an accepted 50 mm certificate. An implementation would need a small strict guard below it. This cannot improve the HCAL obstruction.

The existing spherical/circular corner bound requires

`R−h >= 4.23946+0.05`, hence `R >= 4.53946 m`.

No such R exists. However, this sufficient all-azimuth enclosure is not a literal filled HCAL cylinder.

The hash-matched HCAL has 16 sectors, 36 steel layers at 43 mm pitch, 30 mm steel per layer, 2.600 m inner apothem, 4.148–4.158 m rear cover, 1 mm sector half-seams, 20 mm plate edge strips, and steel/cover `|z| <= 4.4632 m` inside end flanges. These dimensions independently reproduce the nominal no-seam corner `4.239460035830188 m`. The actual finite seam-inset rear-cover corner is `4.239265058964133 m`.

For the actual B1 half-width `0.6416798630576094 m`, clipping each finite rear-cover quadrilateral to the chamber's tangent span and maximizing its `u` projection gives:

| BT coil planes | Actual cover maximum u | Necessary R outside cover with 50 mm margin | Empty interval deficit against R≤4.05 |
| --- | ---: | ---: | ---: |
| 0°, 90°, 180°, 270° | 4.158 m | 4.458 m | 408 mm |
| Remaining eight coil planes | 4.230252500274383 m | 4.530252500274383 m | 480.252500 mm |

These are finite-polyhedron interface bounds for unchanged full-width rectangular B1 chambers. Narrowing tangential width alone cannot recover a 500 mm chamber even at the aligned 0° central line, where only 192 mm gross radial space lies between HCAL cover and warm coil; the two 50 mm margins leave at most 92 mm depth.

## Actual occupied-volume witnesses

The source B1 panel `B1/F00/Z02` has tangent span ±0.641679863 m and `z=0.01..3.2178 m`. Shifting only its apothem to the limiting 4.05 m gives `u=3.80..4.30 m`.

- `(4.120, 0, 1.000) m` lies strictly inside that actual moved panel and HCAL sector 0 layer 35 Steel235 plate (`u=4.105..4.135 m`).
- `(4.153, 0, 1.000) m` lies strictly inside that panel and the actual aluminium rear cover (`u=4.148..4.158 m`).
- Raising the panel to the conservative HCAL-bound minimum `R=4.53946 m` makes `(4.600,0,1.000) m` an interior panel point inside both the exact warm BT sweep and finite uniform-current winding-pack allocation.

The witnesses deliberately avoid the actual B1 seam at z=0. Full-volume SAT checks, rather than the points alone, find actual finite HCAL material intersections for every one of the 48 moved coil-plane panels, including the outer z modules where they cross the barrel's finite end region.

## Separate angular and physical checks actually executed

The portable checker uses only Python's standard library, reads exact Git blobs and implements independent convex-prism SAT, polygon clipping, point containment and exact rounded-coil distance. It imports no repository code. Tolerance is 1e−10 m in normalized SAT projections; touching counts as conflict. All displaced panels discard their historical clearance certificates.

Actual results on Python 3.14.6, with final runtime approximately 0.50 seconds:

| Check | Actual result |
| --- | --- |
| 48 moved B1 panels × 592 finite HCAL prisms (36 steel + rear cover per sector) | 28,416 pair checks; all 48 panels have actual material conflicts |
| 48 moved panels × all 484 support envelopes, conservatively expanded 50 mm | 23,232 pair checks; 0 conflicts |
| All 96 counterfactual B1 chamber pairs | 4,560 pairs; 0 physical overlaps |
| 48 moved panels × 792 other retained chambers | 38,016 pairs; 0 overlaps |
| Duplicate, remote, occupied-steel, occupied-cover, coil-point and source-hash controls | All 10 asserted controls passed |

HCAL rails, end flanges, modules and services are omitted from the material-prism SAT set; including them cannot remove the identified plate/cover intersections. A clear result from this reduced HCAL set would not establish full HCAL clearance.

Projection must remain separate. At `R_even=4.05 m`, `R_odd=5.20 m`, retaining original widths produces 1.037810185° mid-plane angular overlap, but a 0.500144553° gap for the stricter full-depth proxy with the fixed 30 mm border. A purely mathematical widening of the intercoil full width to `1.399110255255650 m` would yield 0.1° of that stricter angular overlap. Fresh SAT finds 0 B1 pair conflicts and 0 widened-intercoil support conflicts (another 23,232 support pairs). This angular exercise still contains all 48 HCAL-intersecting inward panels and therefore is not a viable layout.

Within B1's entire axial span, the exact BT warm sweeps reduce to finite inner/outer straight-leg boxes: the rounded returns begin at |z|=10.8 m, well beyond |z|≤6.4456 m; the ECT warm front is 7.05 m. An independent 2,304-pair SAT check for this counterfactual finds 0 physical warm-coil intersections but 48 contacts with 50 mm expanded inner-leg boxes at the exact R=4.05 limit. This correctly exposes why the limiting value is a bound rather than a source-kernel clearance certificate. The original radius 5.2 m places the coil-plane inner chamber face at 4.95 m, 100 mm beyond the original straight warm outer face at 4.85 m.

## Physical alternatives and consequences

No alternative below is selected or approved.

1. Keep the coil-plane chambers above the BT and stagger/widen intercoil chambers outward. This preserves the HCAL and magnet interfaces but needs a separately bounded candidate, new all-coil/support/chamber proofs and actual coverage/lever-arm evaluation. IB-A1 does not certify that alternative; MuonTech/SoftEng are studying it separately.
2. Redesign the chamber depth/technology. Even at 0° the fixed space leaves an upper bound of 92 mm depth after both margins. With the retained 1.28336 m width, the other eight coil-plane rear-cover projections leave at most 19.7475 mm. The conservative corner enclosure leaves 10.54 mm. These are upper bounds, not a buildable chamber selection or response qualification; the proposed 500 mm envelope must not be silently compressed.
3. Move the BT inner legs outward. For unchanged HCAL/width/depth, the inner-leg radius would need to increase by at least 408–480.253 mm from actual cover constraints, or 489.46 mm under the conservative corner enclosure. These are necessary local bounds, not a working magnet design. Such a shift collides with or forces changes to the existing above-leg B1 region, changes the magnet window/source and field, and requires a new magnetic allocation, structural and chamber study.
4. Reduce/notch/reconfigure HCAL. At the 0° interface alone the outer material projection must shrink from 4.158 m to at most 3.750 m to fit 500 mm plus two margins under the fixed coil. This is at least 408 mm of lost radial HCAL envelope locally; other coil phases require more. Reducing steel/module depth or introducing notches changes calorimeter material, acceptance and containment. It requires an explicit CaloTech/ProRes/human physical decision, not an automatic envelope retune.
5. Restrict inward panels to special axial regions. This cannot implement a uniform inner-barrel stagger through the central HCAL. The barrel/endcap gross gap is only 400 mm (`4.4832..4.8832 m`), smaller than the retained 500 mm minimum longitudinal span even before clearances. Endcap and service interfaces would need their own exact source assessment; no central-barrel rescue follows from that gap.

## Interface register and limits

| Interface | Endpoint owners | Current convention and assessment |
| --- | --- | --- |
| B1 / BT warm allocation | MuonTech + SysArch (magnet); SoftEng representation | Actual origin/basis define tangent/z/radial prism; fixed 500 mm depth and 50 mm margin; inward R≤4.05 bound conflicts with HCAL |
| B1 / HCAL steel, cover and local routes | MuonTech + CaloTech, reconciled by SysArch | 12-fold B1 versus 16-fold HCAL; all frames right-handed; actual source plate/cover intrusion established; external collectors/services remain unqualified |
| B1 / shared frame and feet | MuonTech + SysArch (shared supports); SoftEng representation | All 484 unchanged outer envelopes checked, including case lugs, carriers, feet and braces; 50 mm expanded-envelope checks clear for the invalid radial trial |
| B1 / other chambers and angular footprint | MuonTech + PhysVal + SoftEng | 96 actual B1 modules retained as finite prisms; geometric overlap proxies differ; no chamber response or momentum-resolution claim |
| Magnet / HCAL field and material | SysArch + CaloTech + PhysVal | Existing joint vacuum map is unchanged; ferromagnetic HCAL, structural loads, cases and installed-field solution remain unresolved |

Checks establish the geometric obstruction in pinned prototypes. They do not certify chamber construction, HCAL performance, strength, alignment, gas/cooling/electronics routes, installed field, DD4hep/Geant4 navigation, ACTS transport or reconstructed efficiency. No native runtime, package installation, shared dependency, Git commit, nested agent or external message was used. No human approval or design-state advancement was recorded. Journal integration, session validation/summary and final coordinator reporting remain the coordinator's responsibility under the existing paired session record.

## Reproduction and deliverables

```sh
python3 -B /private/tmp/pr90-IB-A1-checker.py \
  --repo /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout \
  --revision 56f12ef5b2a9bd410cb77e95ac3140557d92f1b2 \
  --output /private/tmp/pr90-IB-A1-results.json
```

The checker accepts any writable `--output` path and requires the exact main and HCAL source commits in the supplied repository's Git object database. Missing sources cause an explicit failure; it never substitutes working-tree bytes or downloads anything. `pr90-IB-A1-results.json` contains full finite cover polygons, steel radial bands, frames, witnesses, all source identities, conflicts and commands for an honest XY drawing at z=1 m (the same solids occupy z=0.5 m). `pr90-IB-A1-sources.json` is the source manifest. `pr90-IB-A1-sources.tar.gz` preserves every read scientific input blob under its source commit/path; SHA-256 `cedd3ca686830f25cea867a2daa323bc27be173e794d516bfc6cd5c1396e61ce`.

Files changed: none in either repository. Deliverables are only `/private/tmp/pr90-IB-A1-checker.py`, `/private/tmp/pr90-IB-A1-report.md`, `/private/tmp/pr90-IB-A1-results.json`, `/private/tmp/pr90-IB-A1-sources.json`, `/private/tmp/pr90-IB-A1-sources.tar.gz`, plus scratch source extracts with the same assignment prefix.
