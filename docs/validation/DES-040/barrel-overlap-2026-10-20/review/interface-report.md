# BO-A1 — fixed-hardware interface assessment

DRAFT isolated PROTOTYPE, no engineering approval. Exact input revision: `e0fd6ad0e4cd8df96356c00ab35095446c3e9ce3`. Generic subagent using the explicitly supplied SysArch fallback mandate, not a verified native profile. Repository remained read-only; deliverables are scratch files.

## Outcome

Moving only the twelve inter-BT outer-barrel facets from apothem8.2m to8.75m permits azimuthal full-depth overlap without solid intersection. With the twelve BT-plane facets unchanged, an odd halfwidth1.3439920862902566m gives0.1° overlap after a30mm footprint border. The nearest actual solid distance is69.6252773065mm, exceeding20mm. This does not remove longitudinal hardware corridors or close all three stations' azimuthal cracks.

The widened odd B3 rectangles have a whole-z analytic50mm coil-clearance proof. Unchanged carrier spokes intersect their full-width columns around abs(z)=6.3m and12.3m. Longer cassettes must be split or reduced in tangent extent there. Existing192endcaps, station centres, and the middle-wheel eta3 obstruction remain unchanged.

## Evidence and classification

The numbers in the existing configuration are **FACTS about the pinned artefact**, representing the existing unsigned **NODD DESIGN CHOICES**; they are not independently established engineering requirements. New trial dimensions and the4m maximum seed are proposed NODD choices. All formulas and clearance/coverage results below are **INFERENCES** from those explicit outlines.

Primary repository evidence:

- `docs/validation/DES-040/refined-wheels-2026-10-20/candidate/geometry.json`: `configuration.chambers`, `magnetic_configuration`, all484 actual `supports.members`, all1248 actual `panels`.
- `tools/muon_layout/layout.py`:21–29 (`tiles`, `_barrel`),45–50 (nominal width and seeds),62–91 (`_children`).
- `tools/muon_layout/geometry.py`:48–69 (vertices/halfspaces),103–141 (ray clipping and convex SAT),145–183 (full-volume coil certificates).
- `tools/muon_layout/wheels.py`:193–253 (support certificates and fresh adaptive barrel packing).
- `tools/toroid_prototype/geometry.py`:35–81 (exact rounded-loop distance and finite tangential slab),232–253 in muon geometry (equivalent exact ray intervals).
- `tools/muon_layout/support.py`:54–141 (finite frame, spokes, lugs, feet); final actual members come from the pinned geometry, not reconstructed nominal assumptions.
- `tools/muon_layout/refined_validation.py`:135–138 (current chamber navigation world radius9.1m, half-z13.3m).
- `docs/design/DES-040-muon-chambers-frame.md`:202–235 (source width,24facets, seam/border/clearance conventions), selected wheel revision and refined wheel sections (fixed hardware/endcaps and open eta3 limitation).

No new external scientific source or private image URL was used. The existing ATLAS references provide context only; all new numeric results derive from the pinned repository input. SHA256s of every examined numerical source are in the portable check JSON.

## Exact neighbor bound and angular coverage

Use adjacent facet angleδ=15°, depth half-h=.25m, retained even apothemR=8.2m, and retained halfwidth

`a=(R−h)tan(δ/2)−.010=1.0366373558197968m`.

The odd radial axis separates the adjacent volumes whenever

`Rodd−h > (R+h)cosδ + a sinδ`.

Its gap is independent of odd width. ForRodd=8.75m the projected gap is.0696252773064927m. For a20mm lower bound, sufficient `Rodd >= 8.700374722693507m`. The even outer corner's orthogonal projection lies inside the widened odd inner face, so the actual minimum Euclidean distance equals this bound. Independent pair checks cover all276 pairs among the24 complete columns; no pair intersects after20mm conservative face expansion and the minimum true XY distance is.0696252773064905m. Any retained longitudinal/tangential fragment is a subset, so its separation cannot be smaller.

For an IP ray to cross both radial depth faces inside border t, the symmetric phi half-angle is

`β(R,a,t)=atan[(a−t)/(R+h)]`.

Thus closure needs `βeven+βodd>=δ`; with desired overlapε, choose

`b=t+(Rodd+h)tan[δ+ε−atan((a−t)/(R+h))]`.

| Odd layout | Halfwidth[m] | Full width[m] | Max radius[m] | No-border full-depth phi union |30mm-border union|
|---|---:|---:|---:|---:|---:|
| Existing sameR8.2 |1.0366373558|2.0732747116|8.5133493413|93.253870%|90.580722%|
|R8.75, source width formula only|1.1090462295|2.2180924590|9.0680749633|93.460217%|90.868945%|
|R8.75, exact bare closure|1.2658221705|2.5316443410|9.0885810646|100%|97.414315%|
|R8.75, exact bordered closure|1.3279533668|2.6559067335|9.0974425057|100%|100%|
|R8.75, bordered0.1° overlap|1.3439920863|2.6879841726|9.0997975103|100%|100%|

These are two-dimensional full-depth phi bounds before axial seams, hardware fragmentation and trajectory effects. The chosen trial has.4873962799° bare overlap and.1° bordered overlap between neighboring full facets. They are not three-station efficiencies or full-4pi fractions.

Simply widening the odd facet at the originalR8.2 causes solid collision. The checker constructs a strict common interior point `[8.219910139830349,.9263642840439446,0]`, with minimum face penetration.1102730718m into both original-radius boxes when odd halfwidth is1.3439920863m. This is a volume negative witness, not a coincident ray or corner claim.

The source nominal20mm tangent subtraction produces an actual same-radius nearest XY clearance19.8288972mm (projection bycos7.5°). The new staggered pair comfortably passes the explicit20mm physical bound; the historical nominal seam should not be re-described as an exact20mm Euclidean result.

## Fixed coils over the entire z span

The pinned warm BT sweep has normal halfwidth.25m, tangential halfwidth.30m, twelve planes0+30k°, and a rounded rectangle centredr6.7/z0, half extents2.1/11.8m, corner1m. The ECT planes are15+30k°, centre r4.15/abs(z)9.5m, half extents3.45/2.2m, corner.6m. Both use the same warm section.

For every point in an odd B3 box of radius8.75m, depth.5m and halfwidth1.3439920863m, the smallest absolute tangent to a BT plane is

`(8.75−.25)sin15°−b cos15°=.9017652168955415m`.

It exceeds the warm halfwidth plus50mm clearance `.30+.05=.35m` by.5517652169m, independent ofz. More distant BT planes have larger tangent bounds or irrelevant opposite radial coordinates. No rounded return can invalidate this slab exclusion.

Every ECT warm point has global cylindrical radius at most

`hypot(4.15+3.45+.25,.30)=7.855730392522392m`.

The odd box has minimum radius8.5m, giving at least.6442696075m radial separation, independently ofz and ECT-plane rotation. This exceeds50mm. Together these prove all odd B3 coil interfaces over−12.5<=z<=12.5m without corner sampling or an infinite annulus approximation.

The even B3 full-width column retains a hard BT return interruption: expanded50mm warm loop intersects it for abs(z)11.0598076211–12.0913171570m. These endpoints follow the inner/outer radii.7/1.3m of the rounded corner about(r,z)=(7.8,10.8)m and radial column interval7.95–8.45m. Tangential side strips can remain; this is not a claim that allphi in that z band is unavailable.

## Frame interfaces and longer-z cassettes

The independent checker builds halfspaces directly from every actual finite support prism. It expands every support face by50mm, a conservative enclosure of its Euclidean50mm neighborhood, then enumerates all possible vertices of the intersection with each full column. This checks full volumes including diagonal members; corners alone are insufficient. All484members and all24facets are evaluated separately, including asymmetric feet.

| Column | Full-width support interruption at abs(z)[m] | Actual member owners |
|---|---|---|
|B1 all facets|None|All484 members tested|
|B2 BT-plane/even|None|All484 members tested|
|B2 ECT-plane/odd|6.1–7.1|Front spoke6.1–6.5 and outer-radius ECT lug6.4–7.1|
|B3 BT-plane/even|None|All484 members tested|
|B3 inter-BT/odd, before or after radial move|6.1–6.5 and12.1–12.5|Front/rear carrier spokes, rear bound clipped bybarrel end|

These are intersections of a whole-width column with conservative support envelopes, not complete-width blind bands. Exact clipping can retain side strips, but a single full-width long cassette cannot bridge them. B2's ECT-front warm return around abs(z)=7.0–7.6m additionally constrains the current coil-plane chamber corridors; fresh generator certificates must decide the retained fragments.

Current actual counts are B1/B2/B3=168/360/528, total1056, with seven dimension families on the existing1nm inventory grid:

- B1:168 of(width,length,depth)=(1.283359726,1.824457143,.5)m.
- B2:192 of(1.678317219,1.822,.5),24 of(1.678317219,.901,.5),144 of(.404579305,.901,.5)m.
- B3:240 of(2.073274712,1.904615385,.5),96 of(1.026637356,.942307692,.5),192 of(.503318678,.942307692,.5)m.

With the same20mm axial gap and fixed half-spans6.4456/9.2/12.5m, a4m maximum seed gives4/5/7 seeds per facet, lengths3.2078/3.664/3.5542857143m, and nominal counts96/120/168=384, compared with720 original2m seeds. These are not accepted panel counts. Fewer/larger seeds can subdivide around the same hard hardware, change which leaves pass the.5m useful-span/.25m² area conditions, and generate more dimension families. The4m choice addresses avoidable2m tiling, not hardware fragmentation. The actual post-packing inventory and coverage must be reported, with no engineering qualification of long tubes, supports, sag, handling, alignment or services.

## Envelopes, field and interface register

The trial maximum corner9.0997975103m is below the assignment's9.4m chamber cap and fixed map radius9.5m, but only.2024897mm inside the current9.1m chamber-navigation world. A modestly larger world such as9.2m is possible within the stated cap and map; no magnetic solve follows from changing only chamber/world geometry while every magnetic source byte remains unchanged. Native world construction and strict interpolation masks still need validation by the coordinator.

The current ACTS world is a chamber-boundary vacuum navigation world. It does not contain the fixed frame: actual frame corners excludingfeet reach9.7833599049m; includingfeet they reach11.9084010514m. Do not imply that a world<=9.4m contains the entire material detector or that the9.5m field map covers the whole frame/feet. Those existing material/transport interfaces remain outside this chamber-outline study.

| Interface | Endpoint owners | Frame/convention | Bounds/validation | Open handoff |
|---|---|---|---|---|
|B3 neighboring chambers|MuonTech / MuonTech; SysArch coherence|Metres, right-handed xyz, zbeam; basis columns tangent,z,radial|24facets, depth.5m, above exact radial gap and276pair checks|Fresh final fragment pair checks and identifiers|
|B3/chamber–BT/ECT|MuonTech / SysArch magnets|Fixed warm sweep coordinates andfolds; unchanged sources|50mm whole-z analytic odd proof; even return fragmentation|Final full-volume certificates for all changed panels|
|B2/B3–carrier/lugs|MuonTech / SysArch commonframe|Actual484 finite member outlines; both ends independently|50mm conservative face expansion; complete polyhedral intersections|Retain interruptions, exact fragment validation; rails/services unqualified|
|Chambers–world/map|MuonTech / SoftEng, reconciled SysArch|SI coordinates; fixed field/mask conventions|Corners9.0997975103<9.4<map9.5; currentworld9.1|Choose explicit world margin; fresh native tests; no field solve needed|
|Endcaps/middle eta3|MuonTech / SysArch magnets; PhysVal claim review|192 outlines unchanged; fixedstationcentres|Preserve prior limitations and exact source identity|Uniform eta3 remains obstructed, no inferred repair|

Crossing materials/services are unchanged outline reservations; chamber internals, added services, supports for longer cassettes and installation qualifications are unresolved. No aggregate material or response improvement is claimed.

## Actual checks and reproduction

Run successfully (Python3 with NumPy, no native libraries):

```sh
python3 -B /private/tmp/pr90-BO-A1-check.py \
 --repo /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout \
 --revision e0fd6ad0e4cd8df96356c00ab35095446c3e9ce3 \
 --output /private/tmp/pr90-BO-A1-check.json
```

The portable script accepts any checkout path and explicit revision and reads blobs with `git show`; it never imports current dirty source. It checks SHA256s, authoritative counts/families, exact plane gap, Euclidean polygon distances, all276pair20mm expansion controls, a same-R collision witness, full-z odd coil bounds, and actual support-column intersections. The initial NumPy2 batched-solve argument shape failed and was corrected; the final invocation exits0. No ACTS/DD4hep/Geant4, field calculation, external message, dependency change, Git commit, or repository write occurred. Coordinator owns session-journal integration. Scratch files changed: checker, JSON result, this report, and pinned-source scratch copies/stdout.
