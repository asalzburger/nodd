# Material-preserving DD4hep LAr service routes

2026-11-14. **Isolated PROTOTYPE**, governed by
[DES032 routing input](../../design/inputs/DES-032-routing-dd4hep.md).
The user selected existing steel/N2 pipe materials with cable envelopes retained.
The maintained detector, its readout and its physical calorimeter components
are unchanged. This component is absent from production CMake/default exports.

## Model and material boundary

Separate `old` and `new` compacts instantiate32 representative passive pipes:
16 equally spaced azimuths at each signed end. This is an illustrative
multiplicity, not a supply/return/circuit bill. Each pipe uses the existing
20mm-OD/18mm-ID steel/N2 construction. The100mm jacket and cable lanes remain
explicit unmaterialised metadata, excluded from the material ledger. No invented
copper/insulation mixture or jacket-wall thickness is introduced.

Common endpoints retain the same4968.343720697463mm analytic path in both
variants. Arcs are replaced by bisector-mitered circular CutTube segments.
At5degree maximum chord angle, their total polyline length is4967.953085169159mm.
A common radius scale1.000039314768365 preserves steel and core volumes
separately, at unchanged densities/compositions. Adjusted outer/inner radii are
10.0003931477/9.0003538329mm. Maximum centreline sagitta is0.3807113673mm.
The10nm overlap tolerance applies to the constructed approximation; it is not
an agreement tolerance with an ideal toroidal bend.

Reference inventory per representative route:

| Constituent | Recipe/density | Volume | Mass |
| --- | --- | ---: | ---: |
| Steel | Fe0.7175/Cr0.19/Ni0.0925 by mass;7.84g/cm3 |296561.730536mm3 |2325.043967g |
| N2 core | Existing provisional nitrogen material;0.02g/cm3 |1264289.482810mm3 |25.285790g |

The nitrogen density is an inherited mass hypothesis, not a fluid-state or
hydraulic result. Conservation of volume/mass does not preserve directional
material budgets after rerouting or make the chordal shape an exact elbow.

## Validation and evidence

The final compact results and exact source/library/artifact bindings are retained
in `results.json`; native files and raw Geant4 step records stay local/ignored.
[Environment](environment.json) records the tested packages and registry warning.
The [recipe](reproduce.md) regenerates both compacts and native/smoke evidence.

The checks distinguish:

- DD4hep construction and native CutTube dimensions, normals, transforms,
  elemental mass fractions, density, volume and mass;
- all shared miter material points and boundary distances, wall/core disjointness
  and full standalone overlap/containment checks;
- converted Geant4 CutTubs counts/volumes and joint material navigation;
- saved native geantino primaries and actual steel/core step lengths through a
  transverse crossing and aimed core/wall miters;
- chord-resolution and invalid-configuration/source controls;
- occupancy witnesses sampled in an unchanged native LAr ECAL context.

The model has no sensitive detector. Its passive smoke therefore uses actual
Geant4 primary/step JSONL as event evidence; empty no-hit ROOT outputs are
diagnostics. No fake sensitivity is added to obtain an output collection.
Gun positions are explicit six-significant-digit smoke fixtures because the
current G4gun UI rounds them. Analytic versus requested vertices are recorded;
strict observed-input checks remain. The route geometry is not rounded this way.

## Integration status

**This is a usable standalone component, not a collision-free combined detector.**
The independent context diagnostic does not place these volumes into the ECAL.
It samples actual pipe centres/walls separately from100mm/20mm reservations,
reports existing cooling occupancy, bath displacement, closed structures and
cryostat vacuum interfaces, and retains bounded positive witnesses. Absence of
a sampled contact is not a clearance proof.

At matching azimuths the common upstream endpoint lies on existing N2 branches;
a naive overlay duplicates them. The old route also crosses barrel end closures;
the new route crosses radial vessel walls. Actual daughter ownership, sealed
ports, board/support repacking and full service circuits need further design.
The context contains ECAL only: tracker, magnet, HCAL, forward collar and fields
are absent. No400mm endcap shift, response improvement or engineering acceptance
is claimed.
