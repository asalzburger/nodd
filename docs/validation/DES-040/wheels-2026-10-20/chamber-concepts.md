# W-M1 MuonTech — unselected endcap-wheel concepts

Input revision: `5674a7688319d6dd5179c04cd381cb59f48d36bb`. Read-only contribution; no repository edits, detector choices, engineering sign-off or new coverage/OBJ results. Inputs were read with `git show REV:path`; exact source hashes and all inventory dimensions are in `chamber-concepts.json`.

## Feasibility conclusion

A 500 mm full-bore front wheel outside the fixed ECT cannot fit behind the fixed HCAL. The HCAL endcap ends at |z|=6.4412 m and the warm ECT front starts at6.55 m: the available axial interval is only108.8 mm. The inherited coil clearance is50 mm, so a front wheel centre must be at most6.25 m; even with **zero HCAL clearance**, avoiding HCAL requires centre at least6.6912 m. There is no solution. Adding a **provisional, newly proposed**50 mm HCAL margin raises that lower bound to6.7412 m. This HCAL margin is distinct from the existing50 mm coil/support clearances.

A radially displaced front annulus can avoid HCAL only by losing the small bore. The conservative all-azimuth HCAL corner bound is4.229264124 m; zero HCAL margin requires inner apothem above that value, and the provisional50 mm margin requires at least4.279264124 m. A test-only4.30 m bore gives70.736 mm radial separation from that circumscribed bound. At z=6.25 m the corresponding nominal forward edge is |eta|≈1.173, so this fallback cannot preserve forward three-station coverage. It is not an equivalent replacement for the0.70 m bore.

The original inner-wheel outer bound5.45 m avoids the inner carrier hoop/spokes radially. If “full wheel” instead means outer bound8.45 m, the front carrier at |z|=6.30 m, occupied6.15–6.45 m, is another obstruction: a500 mm wheel plus50 mm separation must centre at or before5.85 m. It still conflicts with HCAL at small radius.

A full rear wheel of outer radius8.45 m can sit behind the rear carrier. Its spoke/inner-hoop material ends at12.45 m;500 mm depth and50 mm support separation require centre at least12.75 m. A test-only12.80 m centre leaves100 mm axial separation. This extends beyond the current field map |z|≤12.5 m and requires a new map-domain/navigation-world study with unchanged magnetic sources. It also changes the station span; the old3 m axial-span response must not be inherited.

## Sector phase and chamber interpretation

For twelve front sectors, put **seams** at the BT coil planes0°+30°k, hence sector centres15°+30°k. Phase0 puts BT inner legs through chamber centres. With the straight warm BT leg tangent half-width0.30 m, the inherited50 mm coil clearance requires each adjacent chamber side to remain at least0.35 m from the seam in its normal direction: at least0.70 m total physical corridor. This is much larger than the current20 mm intermodule gap. A test-only0.36 m side offset gives0.72 m total corridor and10 mm additional margin beyond the clearance envelope.

A full-bore trapezoid whose sides use the same constant offset cannot retain positive inner bases: minimum inner apothem is0.35/sin(15°)=1.352 m for12 sectors, or0.35/sin(7.5°)=2.681 m for24 sectors. Angularly narrower trapezoids can retain the0.70 m bore but leave broad angular gaps. None of these phase choices solves the HCAL axial conflict.

Twenty-four front sectors with seams at0°+15°k add unnecessary broad gaps at the non-BT seams if the same offset is applied everywhere. Alternating wide BT/narrow intermediate seams can avoid that extra loss, but needs asymmetric/reflected footprints or displaced sector axes; it gives no new space at HCAL. Twelve is the simpler front-sector geometry if a large-bore fallback were ever selected.

Beyond all coils/carriers, the rear wheel has no magnetic phase restriction. Twenty-four sectors give smaller outer widths than twelve and preserve the existing endcap angular inventory; twelve reduces part count. Test-only whole rear footprints with0.70 m inner apothem,8.45 m outer vertex-radius bound,500 mm depth and20 mm perpendicular seam gap are:

| Sectors | Distance between parallel bases [m] | Inner base [m] | Outer base [m] |
|---|---:|---:|---:|
|12|7.462073232|0.354423346|4.353336339|
|24|7.677709079|0.164140917|2.185720069|

These are **large sector-envelope/cassette concepts**, not qualified single MDT chambers. The existing design caps ordinary radial module spans at1.5 m. ATLAS JINST Table6.4 gives regular endcap radial chamber lengths about1.096–1.937 m, assembled in2–6 radial chambers per row. A7.5–7.7 m sector therefore requires a new explicit envelope assumption; existing chamber precision, mounts, service routing and sag/alignment performance do not follow from its outline.

## Barrel and transition implications

If a front wheel retains outer bound5.45 m, only B1 needs the direct barrel/disk seam change: a centre6.25 m with500 mm depth and50 mm physical separation limits B1 half-length to5.95 m, versus current7.70 m. If its outer radius reaches8.45 m, it intersects all three barrel radial layers and requires all three to stop before that front wheel; the additional front-carrier condition makes that bound still shorter. Do not silently delete the long B2/B3 transition coverage.

For illustration, shortening all barrel layers to half-length5.95 m ends nominal B3 coverage at |eta|≈0.674, whereas a rear wheel at12.75 m/Rmax8.45 m starts near1.200. This creates a large nominal transition gap. Even retaining current B3 half-length10.7 m gives nominal edge1.081, below the rear wheel's1.200 edge. Longer B3 outlines or another transition solution would need a separate whole-volume packing study around fixed BT returns. The middle station should remain unchanged until such a global choice is made.

## Exact current inventory and proposed presentation

The pinned layout has816 barrel rectangles and744 endcap trapezoids. Numerical family grouping is by dimension tuples rounded to1 nm to suppress floating-point noise; that is not a manufacturing tolerance. There are **6 barrel families and18 endcap families**; the barrel families are:

| Station | Tangential width [m] | Longitudinal length [m] | Copies |
|---|---:|---:|---:|
|B1|1.283359726|1.907500000|168|
|B2|1.678317219|1.822000000|216|
|B2|0.404579305|0.901000000|96|
|B3|2.073274712|1.927272727|240|
|B3|1.026637356|0.953636364|48|
|B3|0.503318678|0.953636364|48|

Every current chamber has500 mm depth. Endcap stations contain120/216/408 panels over both sides and3/6/9 unique footprints respectively. Preserve all six middle-station footprints and216 instances unless a chosen global layout requires otherwise.

Replacing both inner and outer endcap stations by N panels per wheel would conditionally give216+4N endcap instances and8 endcap shape families (six current middle families plus two new wheel families), **before any barrel repacking**. This is an inventory descriptor, not a feasible selected layout. For N12/N24 the conditional endcap counts are264/312; counting unchanged barrels would give1080/1128 total, but those totals must not be advertised after shortening/repacking barrels without recalculation.

For future review, use dimension-labelled blue local-footprint family catalogues, true XY wheel views with bores/seams labelled, and unrolled barrel(phi,z) layouts. OBJ exports should retain one group per chamber and separate barrel B1/B2/B3, endcap side, wheel station, frame and coil groups. Provide a combined chamber OBJ plus separate barrel/endcap/wheel files so a viewer can hide the barrel. This report creates no new selected-layout OBJ or acceptance plot.

## Actual checks and sources

- Parsed the exact pinned1,560-panel inventory and all source transforms; grouped dimension families independently.
- Ran the pinned full-volume coil distance-bound certificate and conservative panel/support SAT on the test-only widened-bore and rear concepts listed in the inventory JSON; no physical inputs were changed. Initial20 mm certificate resolution was unresolved for the10 mm extra seam margin, so the numerical certificate was refined to5 mm rather than declaring those boundary cells clear.
- Tested whole panel/panel non-overlap for each test wheel. HCAL clearance is an explicitly conservative circumscribed-radius/axial-envelope inference, not a detailed HCAL polygon certificate.
- Primary source inspected: `SRC-ATLAS-JINST-2008`, [ATLAS JINST3 S08003](https://jinst.sissa.it/LHC/ATLAS/2008_JINST_3_S08003.pdf), printed172–175, especially Table6.4 on174. Local PDF SHA256 `d0a522aae47997d889ab74f5ade000597e12cf7437568d3a37915613fe2269b2` matches the existing source record. Tube/MDT technology facts are context, not adopted internals.
- Repository locators at the exact input revision: `docs/design/DES-039-twelvefold-toroid.md` pinned envelopes/coil table; `docs/design/DES-040-muon-chambers-frame.md` bounded whole-prism/clearance choices; `tools/muon_layout/design.json` dimensions; `layout.py` `_disk`, `candidates`, `_children`; `geometry.py` full-volume certificate/SAT; `docs/validation/DES-040/{geometry,support-input}.json` actual geometry and carrier bounds.

The actionable human choice is to retain the fixed HCAL/magnet/depth inputs and relax the front-full-wheel request, or authorize a separate physical-envelope change for a small-bore front wheel. A widened-bore fallback is geometrically distinct and loses forward coverage. No option is selected here; no new detector acceptance, chamber response or engineering qualification is claimed.
