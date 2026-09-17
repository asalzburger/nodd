# DES-003 — PR #4 review round 1 disposition

- Date: 2026-09-17; status: DRAFT proposal responses, not human sign-off.
- Review: `asalzburger-review`, changes requested 2026-09-17 against `7bb7ff04a96b2038572d59904f8954a42777d7e6`.
- Scope: all 25 inline comments in the first review. Replies do not resolve threads on the reviewer's behalf.
- Coordinator synthesized the calorimeter, muon and physics specialists, followed by System Architect and Software Engineer reconciliation.
- Canonical outcome: [E1-R1 proposal](DES-003-global-envelopes.md), [ADR-006](../decisions/ADR-006-global-envelope-and-field-hypotheses.md), [study catalogue](../validation/DES-003-study-catalogue.md).

## Direction and proposals

The review sets 14 TeV HL-LHC investigation targets: tracker eta 4, calorimeter eta 5, muon eta 3 with 3.5 stretch. The later consolidated target supersedes the earlier calorimeter minimum of 4. Standalone-compatible/toroidal muon work is the baseline investigation; dedicated magnet decisions remain later. These directions do not approve the new numerical envelope choices. All new physics and engineering claims below are the FACT/INFERENCE/NODD DESIGN CHOICE entries with precise locators in the linked specialist evidence.

## Comment-by-comment response

### Forward coverage

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032889973) — **Adapted**.

E1-R1 adds a detached forward-calorimeter study volume at |z|=11.2–13.2 m, r=0.12–1.50 m. The later consolidated review target of |eta|<5 supersedes the earlier minimum of 4. ATLAS forward calorimetry covers 3.1–4.9; CMS operational literature reports HF to 5.19. The proposed volume has full axial traversal for prompt rays through eta 5, but edge response, beam aperture, shielding and total installed enclosure remain to be established.

[Evidence and follow-up](inputs/DES-003-calorimeter-review-1.md).

### Depth literature in design cycle

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032893034) — **Adapted**.

Added operational ATLAS electron/photon and CMS hadron-calorimeter calibration papers alongside the TDR precedents. CAL-V01/02 now require material scenarios and species/energy/angle leakage studies. Historical depth bands remain screening ranges, not automatic containment requirements; 14 TeV collisions do not imply 14 TeV single-particle tests.

[Evidence and follow-up](inputs/DES-003-physics-review-1.md).

### Calorimeter minimum coverage

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032897907) — **Adapted**.

Recorded the later consolidated target |eta|<5, which includes this requested minimum. A dedicated forward candidate is now drawn and tested geometrically; extension to 5.2 remains exploratory because its prompt entrance margin is only 3.57 mm.

[Evidence and follow-up](inputs/DES-003-calorimeter-review-1.md).

### Coil order with muon design

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032903479) — **Kept open**.

Kept coil ordering and return topology coupled to the muon-system study. E1-R1 still draws an inner-solenoid hypothesis; outer-solenoid, instrumented-return and air-core-toroid alternatives remain. This iteration does not force a dedicated muon magnet decision.

[Evidence and follow-up](inputs/DES-003-muon-review-1.md).

### Dense PCB inventory

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032905861) — **Deferred as requested**.

Moved detailed PCB/effective-material inventory behind envelope definition. It still must be included whenever inherited material depth is quoted; deferral is not permission to delete or double-count its mass.

[Evidence and follow-up](inputs/DES-003-calorimeter-review-1.md).

### Service exits

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032911679) — **Researched and adapted**.

Added ATLAS barrel/endcap-gap services (2008 detector paper §5.5, PDF166), CMS ECal end patch panels (§4.2, PDF119), and HGCAL outer-surface/rear-annular exits shared with timing/muons (TDR §4.5, PDF64–65). Proposed route topology: barrel bundles toward end patch regions, endcap bundles toward outer/rear handoffs, with named owners and phi sectors. Capacities and minimal path depth remain ENV-V03/CAL-V02 work.

[Evidence and follow-up](inputs/DES-003-calorimeter-review-1.md).

### Sufficient supports

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032914880) — **Adapted**.

The proposal now calls for minimal but sufficient supports with explicit footprints and material ownership. Forward support, readout and shielding may extend beyond the instrumented box; its bounds are not advertised as a complete installed enclosure.

[Evidence and follow-up](inputs/DES-003-calorimeter-review-1.md).

### Polygon optional

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032917068) — **Adapted**.

Made polygon shape an optional later component choice. Circular maximum-enclosure bounds remain the planning convention. The 16-sided depth calculation is explicitly conditional, retained only to compare with ODD.

[Evidence and follow-up](inputs/DES-003-calorimeter-review-1.md).

### Toroidal baseline option

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032933147) — **Adapted**.

Replaced the identification-first preference with a standalone-compatible, potentially toroidal baseline investigation. All three architectures remain in the comparison. Reserving the muon host is not proof that toroid coils, supports and stations fit; dedicated magnet design remains deferred.

[Evidence and follow-up](inputs/DES-003-muon-review-1.md).

### Independent momentum baseline

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032955812) — **Adapted**.

Standalone-compatible muon measurement is now the baseline investigation rather than a mandatory finalized requirement. The catalogue separates tracker-combined, vertex-constrained muon-only and unconstrained standalone results, so an outer-coil combined fit cannot silently stand in for independent momentum measurement.

[Evidence and follow-up](inputs/DES-003-muon-review-1.md).

### Punch-through before extra steel; 14 TeV

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032964329) — **Adapted**.

Recorded 14 TeV HL-LHC as the study scenario. CAL-V03/MU-V05 require leakage and punch-through evidence before recommending extra absorber steel. None is added. The detached forward calorimeter is downstream of current muon stations, so smaller upstream endcap apertures are proposed to study filtering at eta 3–3.5; their adequate depth remains unproven.

[Evidence and follow-up](inputs/DES-003-muon-review-1.md).

### Consolidated coverage

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032974435) — **Adapted**.

Recorded tracker |eta|<4, calorimeter |eta|<5 with extension conditional, and muons |eta|<3 with 3.5 stretch. E1-R1 proposes ECal/HCal inner endcap radii 0.18/0.20 m, muon parent 0.40 m and detached forward calorimetry. These are new draft allocations, not achieved acceptance; actual station edges need a later layout.

[Evidence and follow-up](inputs/DES-003-muon-review-1.md).

### Study catalogue

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032977174) — **Added**.

Added docs/validation/DES-003-study-catalogue.md, including MU-V01–08: stations, independent measurements, vector-field bending, material/transport, punch-through, sensitive hits, reconstruction and systematic variations. Every item lists owners, dependencies, outputs and execution state.

[Evidence and follow-up](inputs/DES-003-muon-review-1.md).

### Historical choices versus operation

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032981759) — **Researched; limits retained**.

Added later operational calibration evidence. It supports the built scale and coverage but does not certify nODD containment: response corrections, material and leakage still matter. The cross-check also found a real documentation discrepancy: the 2008 CMS paper gives HF outer steel/sensitive radius 1.30 m, while the 2020 calibration paper §2 gives calorimeter radius 1.57 m. Its cause is unresolved and is not silently treated as an upgrade; nODD 1.50 m is an independent design proposal.

[Evidence and follow-up](inputs/DES-003-physics-review-1.md).

### Realistic solenoid field

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4032997182) — **Answered with screening estimate**.

Built NbTi examples support studying 2–4 T, but not claiming that 3 T fits a complete 200 mm coil/cryostat. For a finite current sheet R=1.34 m, L=6.70 m, 3 T centrally needs about 17.23 MA-turn; magnetic-pressure scale is 3.58 MPa and a uniform-bore energy proxy is 115.9 MJ. The same toy model gives only 1.82 T on axis at z=3.15 m. Winding, reinforcement, thermal/quench systems and return flux need a physical decomposition; these calculations are not a magnet feasibility certificate.

[Evidence and follow-up](inputs/DES-003-physics-review-1.md).

### Full propagation later

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033007673) — **Adapted**.

Added mandatory PROP-V01 after a field and material/active-surface model exist. It requires full charged-particle propagation, sensitive crossings, numerical convergence and the same field identity in transport and reconstruction. Straight rays remain only the present allocation screen.

[Evidence and follow-up](../validation/DES-003-study-catalogue.md).

### Architecture baseline

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033030983) — **Retained and extended**.

Retained E1 central dimensions as the negotiation baseline. E1-R1 changes endcap apertures and adds forward calorimetry in response to the coverage review. The initial proposal is preserved at commit 7bb7ff0; new dimensions remain draft choices.

[Evidence and follow-up](DES-003-global-envelopes.md).

### Timing placement and coverage

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033039653) — **Answered; allocation open**.

A separate outer barrel timing assembly plus forward disks is the strongest comparison, rather than assuming an ordinary outer strip layer gives precision timing. CMS MTD provides a 40 mm barrel precedent using LYSO/SiPM; ATLAS HGTD provides forward LGAD coverage 2.4–4 with a 125 mm vessel/moderator allocation. Full nODD timing to eta 4 would be a new combined ambition. Coverage needs active-area/vertex/curved-track association, ageing, inefficiency and timing-response studies (TIME-V01); shared service space is not yet partitioned.

[Evidence and follow-up](inputs/DES-003-physics-review-1.md).

### Project baseline

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033046322) — **Retained**.

Retained the overall ODD-like starting scale and documented E1-R1 as a review-driven iteration. This agreement to start is recorded as direction for the investigation, not technical sign-off of numerical dimensions.

[Evidence and follow-up](DES-003-global-envelopes.md).

### Dedicated muon magnets later

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033053336) — **Deferred as requested**.

Dedicated muon-magnet selection/design remains with the later muon-system work. The current plan preserves standalone-compatible space and interface questions while comparing toroidal, solenoidal/combined and instrumented-return options.

[Evidence and follow-up](inputs/DES-003-muon-review-1.md).

### Smallest inner radius

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033060406) — **Answered; minimum unresolved**.

There is no justified universal minimum from collision energy alone. CMS Phase-2 TDR starts active pixels near 29 mm; operating ATLAS IBL provides a 33 mm precedent. We propose screening active radii around 30–35 mm later. The existing 25 mm host boundary is not a sensor radius: the inherited 24.4 mm pipe leaves only 0.6 mm before support, motion and installation allowance. Beam optics/aperture, pipe stability, lifetime/rate and module/support assumptions must set the limit.

[Evidence and follow-up](inputs/DES-003-physics-review-1.md).

### Outer coil and need for iron

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033078996) — **Answered; architecture open**.

An outer solenoid can provide useful bending between tracker and muon segments, potentially replacing a separate magnet for a combined measurement. It does not automatically give tracker-independent momentum, particularly for displaced muons. Iron is not fundamentally required: flux can return through air or return coils, but the field/stray-field, energy and support problem changes. Compare signed bending integrals between measured surfaces, field maps, alignment and scattering; CMS operational yoke studies are now catalogued as evidence.

[Evidence and follow-up](inputs/DES-003-muon-review-1.md).

### Coverage follow-up

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033081125) — **Adapted**.

Replaced the open coverage question with the explicit 4/5/3 targets and 3.5 muon stretch. The follow-up now asks whether proposed apertures, transition depth, finite vertices and upstream filtering can deliver those objectives.

[Evidence and follow-up](DES-003-global-envelopes.md).

### Planning must expose space needs

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033083362) — **Adapted**.

Expanded the interface register with forward beam/support/shielding and timing ownership. Added literature-based service handoffs and a staged study catalogue. Unassigned space is now clearly a competing allocation to close, especially the timing/service band and forward support beyond the drawn instrumented box.

[Evidence and follow-up](DES-003-global-envelopes.md).

### Tracker layout after envelopes

[Review comment](https://github.com/asalzburger/nodd/pull/4#discussion_r4033086141) — **Deferred as requested**.

Kept layer/module/station design after envelope definition. The current pass sets coverage/aperture contracts and a first-radius comparison range only; it does not select or implement a tracker layout.

[Evidence and follow-up](DES-003-global-envelopes.md).

## Decisions still requiring review

1. Detached forward calorimetry versus a compact insert that would change muon station space; total support/readout/shielding boundaries remain open.
2. Smaller upstream calorimeter apertures and the muon stretch reservation versus beam-line, rate and shielding constraints.
3. Timing scope and the split of barrel/forward integration space with services.
4. Credible coil/cryostat decomposition, finite field and later standalone/combined muon performance tradeoffs.
5. Reconcile the two published CMS HF radial definitions before using either as a copied installed envelope.

No extra absorber steel, production geometry, actual tracker layout or human sign-off was added. Later simulation obligations are retained with owners and prerequisites.
