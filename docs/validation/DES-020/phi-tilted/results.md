# DES-020 — Phi-tilted short-strip barrel alternative

Status: DRAFT isolated PROTOTYPE, 2026-10-06. Governing design: [DES-020](../../../design/DES-020-short-strip-barrel.md), SB-F03/F04 and SB-C14/C15. No production, pixel, identifier-remapping or sign-off change. The historical tangential proposal/reports are preserved byte-for-byte; their producers are located at scientific commit98a0fee7e6c554c5ea3a910d830329580ff998bb, rather than assumed to be today's amended files.

## Recommendation and layout

Use **+15° common phi tilt at one anchor radius per layer**, with the complete cold stave rotating as a unit. Retain28 rows,1.5 mm alternating row lifts,48×96 mm² active area and75µm×0.5mm readout. The fine coordinate U follows the tilted transverse direction; V stays along z. All sensors have the same angle relative to their stave anchor radial/tangential frame; raised centres move slightly in phi along N. No in-plane stereo is introduced.

| Layer | Anchor radius [mm] | Staves | Modules | Radial point-origin projected active overlap |
|---|---:|---:|---:|---:|
| L0 | 260 | 44 | 1232 | 19.34–19.76% |
| L1 | 340 | 56 | 1568 | 17.30–17.62% |
| L2 | 480 | 80 | 2240 | 18.41–18.64% |
| L3 | 660 | 108 | 3024 | 16.99–17.16% |

The count rule reserves8 mm of the active width before angular projection. These overlap fractions concern angular intervals of low/high-row sensors from the point origin, not total silicon area or curved-track hermeticity. Compared with44/56/78/106 tangential staves, the alternative adds4 staves/112 modules: **8,064 modules**, **990,904,320 channels**, **37.158912 m² active area**. The nominal radii and±1200 mm endpoints remain fixed.

The one-stave-step rotational covariance residual of all sensor centres/U/N is≤7.88e-13 (mm for centres, dimensionless for axes). The control's alternating lanes change radius every stave; the alternative removes this modulation. This establishes discrete local N-fold geometry only. Twelve service sectors, differing layer populations, same-handed tilt, field/charge effects and detector response are separate. No continuous or reflection symmetry or resolution-performance claim.

## Angle and hardware controls

The inherited full cold stack includes flex bridges and backside buses. Twelve degrees produces **602 native flex-to-neighbour-bus overlaps**, maximum penetration0.099805 mm, and fails. Fifteen and18 degrees give zero reported overlaps at1e−5 mm;18 degrees requires292 staves/8,176 modules. Fifteen is the smallest surveyed passing angle, not a continuous optimization or a qualified installation margin. ODD's locally inspected−0.15rad convention and ATLAS's11–13° angles motivate the arrangement; neither mandates our thicker hardware's angle.

Keep the core, skins, picks, module components, end boards, buses, flex and half-stave U-loops unchanged in their own local frame. Rotate them together. New2×8 mm beveled CFRP webs at u=+14.5 mm meet the bare back skin at w=−6.8 mm, on the3 mm land between the insulation and signal-bus edges with0.5 mm clearance each. Their inner face meets the circular ring tangent plane. The design gives the exact foot equation and positive-depth check. The contact is a line placeholder: web/bond strength, ring clamps and curved/machined seats, compliant/sliding joints, assembly clearances, off-centre torsion and thermal-cycle qualification remain required. No bolt-through-web assumption. A4 mm left-side shoe at u=−18 mm failed1908 overlaps against neighbouring cold plates; its exact model/export source preimages, input and failed native report are archived under off-bus-left-control/. This was rejected rather than pushing the foot through a neighbour or loading a bus.

Conservative cold-stack radial bounds are247.40..269.53,327.13..349.26,466.87..489.01 and646.70..668.83 mm. Bearing rings remain below each stave; L0 ring starts at240 mm, above the inherited231.7 mm pixel-service reference. End boards remain axially separate at|z|1215..1245 mm; unchanged sector collectors occupy|z|1245..1310 mm and trunksr710..783 mm. This isolated check is not full-detector integration clearance.

## Actual native and transport checks

- Updated default control: retained layout equality plus native counts, IDs and constituent mass/volume regression PASS; zero native overlaps. Original scientific reports, old drawing bytes and input are unchanged.
- DD4hep1.38, ROOT6.40.04: **8,064 sensitive sensors, 251,610 physical placements**, all entity/sensor transforms, materials and masses matched. **8,064 unique volume IDs / 40,320 anisotropic cell probes**;640×192 grid retained.
- Native overlap tolerance remains1e−5 mm; zero reported overlaps. Seventy-five sparse straight ROOT rays exercise all layers and material navigation; they do not establish coverage.
- Fresh-process ROOT import without factory loading: **8,064 sensors**, centres/solids/materials and all signed U/V/N axes PASS. Maximum axis residual0. Packed ID persistence is not claimed.
- Geant4 11.4.2, one10 GeV transverse mu−, seed42, FTFP_BERT, no field: **8 positive-energy saved hits in layers0–3**. Actual path lengths agree within the unchanged0.01 mm smoke tolerance with thickness/|N·gun| from the exact expected inventory. Tilted radial path is roughly0.2071 mm, not0.2000 mm.
- Total benchmark material inventory **1364.60 kg**, versus1340.82 kg for the control. Effective collectors/trunks dominate; this is not a manufactured cable/assembly BOM or a material-performance qualification.

## Coverage — unchanged denominator, failures retained

Refined sample:103,040 tracks per mode, eta161×phi128×5 origins, eta−4..4, same off-grid phase0.371, originsz=−150/0/+150 mm and the two off-axis±1 mm fixtures. Straight and both charges use the same finite-plane oracle, nominal-cylinder eligibility and1 GeV/4 T vacuum fixtures as the control. Coarser81×64×5 sample misses are70/86/76; refinement exposes additional boundary losses, not a convergence proof.

| Mode | Control missed crossings | Alternative missed crossings | Alternative eligible crossings | Misses >100 mm from nominal end |
|---|---:|---:|---:|---:|
| straight | 1311 | 225 | 183870 | 0 |
| positive | 1132 | 210 | 182446 | 0 |
| negative | 1135 | 174 | 182448 | 0 |

Full sampled hermeticity **FAILS** for every mode because boundary misses remain. Equal-radius shingling reduces the radial-lane seam displacement and sampled end losses; it does not close the barrel/endcap transition. Do not narrow eligibility or drop failing tracks. No continuum proof, energy loss, scattering in the coverage oracle, calibrated charge sharing, Lorentz drift, resolution or ACTS tracking-geometry conversion.

## Services and engineering gates

Recomputed counts:576 harnesses/end,288 cooling loops/end,44 manifold pairs/end, each module routed exactly once. Selected nominal trunk fill ratio0.7676 passes its screen; conservative1.7991 and channel-scaled2.9439 **FAIL**. Collector worst mean envelope fill51.54% exceeds50%: preserve the≥70 mm mean-volume recommendation and unresolved local manifold/bend/access packing. Cable diameters, material fractions and service bounds are unchanged. The collector still conflicts with the original1295.5 mm strip-disc datum.

The inherited−35°C comparator thermal case passes its simple screen;−25°C and channel-scaled load cases fail. Data bandwidth, electronics compatibility, two-phase pressure drop/dry-out and endcap service demand remain unqualified. The full-gravity beam screen gives47.08µm atE70 GPa/span300 mm; it is conservative for the normal load only and ignores in-plane bending, torsion, joints and installation loads. A field model does not by itself qualify hardware.

## Reproduction and provenance

Commands and runtime setup are in [the tool README](../../../../tools/short_strip_barrel/README.md). Inputs12/18° and failed/passing native reports are retained separately. The artifact manifest records actual dirty execution **c5472092c6da1ab073544fa75f0f00769ab2af9f**, exact input/producer/factory/library hashes, retained file hashes and versions. Result commits enclosing this report are publication provenance, never substituted for execution revision. Raw native ROOT/compact/inventory and DDSim logs/output remain ignored under `build/short-strip-barrel-phi/`; curated usage remains unknown while this turn is active.
