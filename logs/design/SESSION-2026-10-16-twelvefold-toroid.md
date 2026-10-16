# SESSION-2026-10-16-twelvefold-toroid

## Scope

User requests a12-fold ATLAS-like toroidal system based onPR86, serving3m
first-to-last chamber spans, three barrel chamber layers and three endcap disks
per side as outlines only, and a computed joint solenoid+toroid field map.
Base e8108f997bb663670db745e57d61d66c2cea9437 in isolated
codex/twelvefold-toroid-prototype. PR86 is open; no human engineering sign-off.
Proposed DES039 is a DRAFT/PROTOTYPE design, not production integration.

## Bounded assignments

A1 SysArch/MuonTech, read-only repository, write temporary proposal only under
/private/tmp. Read AGENTS, profiles and evidence skill. Samebase. Develop
barrel/endcap coil and3-layer chamber-outline envelopes around pinnedHCAL,
including transition mixed-station acceptance and physical clearances. Research
ATLAS public coil geometry as needed. No repo writes, external messages or
nested delegation. Return exact dimensions, assumptions, source locators and
collision/acceptance risks. Completion: usable parameter proposal and limits.

S1 SoftEng, write assignment only tools/toroid_prototype/field.py,
tools/toroid_prototype/field_backend.cpp and tools/toroid_prototype/test_field.py.
Samebase. Read AGENTS/profile and evidence skill. Implement generic finite
closed-coil BiotSavart field and vector-potential backend, uniform finite-pack
quadrature and polygon-loop construction; group-wise contributions for12-fold
barrel/endcap coils. Root owns geometryconfig, calculation/energy/map exporter,
figures and report. Do not choose detector dimensions. Return tests, API,
performance and tolerances; no external messages or nested delegation.

P1 PhysVal, read-only repo, temporary calculations only under/private/tmp.
Read profiles/review skill. Samebase. Independently assess field/energy methods,
ATLAS primary evidence, cold-volume policy applicability and map validations;
review later exact implementation. No repo edits, external messages or nested
delegation. Completion: numerical/physical review and explicit limits.

## Outcomes and validation

Pending. No installed-detector nonlinear-steel field or engineering acceptance
is inferred from a vacuum coil calculation.

## Token accounting

Exact per-turn root/child counters unavailable; usage unknown, not zero.

## Continued bounded assignments

After initial read-only proposals, A1 was explicitly granted ownership of
`tools/toroid_prototype/geometry.py` and `test_geometry.py`: implement coil
union masks, finite chamber outlines, mixed surface intersections, JSON/VTP
exports and unique cold-volume controls. Root retains configuration and reports.
A1 completed nine controls and the analytical/Monte Carlo union cross-check.

S1 ownership expanded to `energy.py`, `test_energy.py`, `energy_study.py` and
`docs/validation/DES-039/energy.json`. Question: complete all-space energy,
including finite-pack self and mutual terms, C12 reduction, convergence and
exact current rescaling. S1 completed six energy plus thirteen field controls,
retained eight convergence rows and the bidirectional solenoid mutual check.
The raw study fixes the 1T/1T reference; root owns the stronger operating point.

P1 ownership expanded to the source dossier, independent response/grid scripts
and JSON evidence, and `review.json`. P1 remains read-only for implementation.
Independent double-integration sagitta, scattering covariance and broad grid
checks challenged the initial coarse map. Formal implementation review is
against an explicit frozen commit; source-dossier authorship is disclosed.
These are explicit generic-agent role assignments, not verified native profile
loading. No external messages to other people were sent by these specialists.

## Design reconciliation

- Adopted twelve barrel plus twelve coils per end, 15 degree offset, finite
  rounded-racetrack packs and three nested capped measurement surfaces.
- Raised the endcap sagitta reference from 1T to1.6T after direct signed-field
  integration exposed barrel-return cancellation around eta1.6. Barrel remains
  1T. Complete coupling matrices are rescaled by each ordered current product.
- Replaced the initial 50mm graphical shell with a provisional 300mm whole
  chamber reservation and300mm barrel shortening. Measurement centres stay
  fixed. ATLAS tube-plane scales guide this choice; no full MDT depth or
  response qualification is inferred from an empty outline.
- Refined the delivered joint field grid to62.5mm R/Z and0.625degree phi after
  independent broad probes exposed coarse-grid errors. Fine joint vector map
  and separate coarse source-component map are retained with explicit masks.
- Complete vacuum energy includes all self and mutual terms, not the finite
  map box. The DES00430MJ/m3 rule is applied globally to the complete coupled
  vacuum system; shared endcap cold overlap is subtracted. No local per-coil
  thermal/stress qualification or annular-solenoid gap formula is substituted.

## Physical limits

HCAL magnetic grade/B-H, real supports, shared endcap vessel/pressure boundary,
conductor/circuit choice and margins, forces and quench remain open. The
48.1A/mm2 barrel pack cannot adopt the cited ATLAS conductor unchanged. Results
are the complete joint COIL field in vacuum, not the installed nonlinear-steel
field. Chamber depths, clearance and straight-ray acceptance remain prototype
assumptions. The1.3X0 internal scattering model is borrowed, not derived from
empty chambers. MDT proxy observables use direct source evaluation; field-map
interpolation error is reported separately and not absorbed into that proxy.


## Final chamber-compatible geometry

A subsequent depth/interface check expanded the complete chamber reservation to
500mm, guided by ATLAS multilayer/spacer dimensions. Disk centres are now
|z|7.5/9.0/10.5m; barrel shortening500mm leaves250mm before disk front faces.
ECT centre|z|9m/half-length2.2m gives end turns at6.8/11.2m,700mm from the
first/last disk centres and150mm beyond halfwarm+halfchamber+clearance.
BT half-length11.8m clears the extended station caps. Geometry masks test
actual radial/axial extrusion with≤25mm samples+half-stepguard; they do not
inflate disk radial exclusions by axial chamber depth. Eleven geometry controls
include both full envelope faces and a false-isotropic-depth regression.

The new source geometry was recalculated, including all-space energy convergence:
raw1T/1T toroid energy3.071540457GJ; final1T/1.6T operating point3.827696716GJ,
complete3Tsolenoid+36coils3.970870474GJ. NI percoil2.885089/1.651317MAturn.
Global cold allocation132.362637m3 includes127.590178m3 unique toroid sleeves;
sharedECTcold overlap0.089653m3 perend is subtracted. Source packs remain
uniform0.20×0.30m; cold reservation~0.275745×0.402127m andwarm0.50×0.60m.
Final fine transition grid has2051/2511clear rays, Bsag min0.896511T andworst
500GeV standalone proxy8.79769%. This is a grid fraction/proxy, not efficiency
or continuum coverage. Narrowseam andforward aperture shadows remain visible.


P1 fixed-commit review found a raw-energy reference SHA captured before S1
finished its final metadata write. All five rescaled matrices agreed exactly
(0J difference); only the provenance link was stale. Root corrected the
operating-point reference SHA to the committed raw-energy file and froze a
follow-up revision. No field or energy recalculation was required.


Final P1 review at2457c6e4b87007794cf8c1b3b70b7c9a2c4acdc2 records no
outstanding tested-scope defect. It reconciles38immutable file hashes, all36
controls, independent sagitta/MS covariance, exact five-matrix energy rescaling,
2472serialized-grid probes and coarse-source decomposition. Catalogue/control
authorship is disclosed and human_approval=false. Broad map interpolation is
0.894mT RMS,9.75mT maximum and1.16%maximum relative norm at sampled points.
The review preserves the resolved energy-provenance finding and engineering
limits. Registry validation:67tasks,37documents,21reviewrounds PASS.


Published draft PR87 https://github.com/asalzburger/nodd/pull/87, stacked on
codex/muon-reach-field-study (PR86, head e8108f997bb663670db745e57d61d66c2cea9437).
Observed publication head b8e6c9ab2a753121207a0dec17a8c28fc134ad2b. PR attachment
added to this chat. GitHub Project validation and Token usage Pages were still
in progress at publication capture; no remote success is inferred here.
Final local registry/session checks and journal summary were run. No merge or
production integration was attempted. Root/child exact token counters remain
unavailable; usage is unknown, not zero.
