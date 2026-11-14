# DES032/DES033 — material-preserving DD4hep service-route prototype

2026-11-14. **PROTOTYPE / user-authorized isolated implementation.**
Parent: [side-neck proposal](DES-032-side-rear-routing.md), draft PR142.
Drawing/source input: `3fca74b70709345a9440b17cf23acb40aab1f945`.
No production adoption or engineering acceptance is granted.

## Authorized scope and material reference

The user requested a DD4hep version of the old/new routing, allowing approximated
bends while keeping material. In clarification they selected: **reuse existing
pipe materials; retain cable envelopes**. This defines a physical cooling-pipe
prototype; unspecified cables and the100mm utility jacket do not acquire invented
material or wall thickness. They remain explicitly unmaterialised envelope
metadata/visual guides, excluded from the material inventory.

**FACT about the existing prototype:** barrel_services.py models a20mm-OD,
18mm-ID pipe wall in `lArCaloSteel` (density7.84g/cm3, mass fractions
Fe0.7175/Cr0.19/Ni0.0925), with `PrototypeNitrogenTwoPhase` core
(density0.02g/cm3, nitrogen). These provisional recipes are retained unchanged;
the nitrogen density remains a mass hypothesis, not a qualified fluid state.
Sources: barrel_geometry.py material_model(), barrel_services.py and services.json.
There is no pre-existing material-filled external cable network to preserve.

## Matched old/new routes and bend approximation

**NODD DESIGN CHOICES — isolated prototype:** use the drawing's R2735.3→3029mm
S-bend,400mm bend radius and old/new S-bend starts4170/3300mm. Complete the rear
turn from |z|5880mm to6280mm and radial handoff R4800mm. Use a common upstream
endpoint at |z|3000mm,R2735.3mm. Compare separate old/new compacts, at unchanged
detector-envelope coordinates. No400mm endcap shift is implemented.

**INFERENCE:** including the upstream straight makes the total centreline
length identical when the S-bend is translated along z: its added upstream
straight is exactly offset by the downstream straight. The common analytic
length per route is4968.343720697463mm. Its reference steel/core volumes are
296561.73053559044 /1264289.4828096223mm3. Replicated routes must declare their
side/azimuth count; they are not an engineered circuit/station bill.

**NODD DESIGN CHOICE — approximation:** approximate arcs by a polyline, initially
at no more than5degrees per chord, with bisecting miter planes at joins. Prefer
DD4hep CutTube pieces to retain circular pipe sections and matching faces.
Use a single per-route radius scale `sqrt(L_analytic/L_polyline)` for both inner
and outer radii so constituent volumes match the analytic circular reference,
while density/composition remain unchanged. Declare nominal versus adjusted
radii, sagitta and volume errors. Reject degenerate/reversing segments. Any
alternative solid construction must retain the same physical invariants and
be documented before acceptance of its checks.

No material-density scaling or arbitrary cable mixture is permitted. Adjacent
pieces must have coincident matching end planes without gaps or overlapping
solid material. Steel wall and nitrogen core must be disjoint. Empty cable
envelopes must not be silently filled with a proxy counted as real services.

## Integration boundary and validation gates

This is a standalone services component/factory and export, separate from the
maintained detector. Original LAr barrel/endcap solids, materials, readout and
placement hierarchy are unchanged. A diagnostic overlay onto that model must
identify occupied-space conflicts; it is not an accepted integrated layout.
Side-neck pressure/vacuum penetrations, board/support repacking, endcap rear
ports, complete circuits and the forward collar remain unresolved physical
interfaces. Do not cut/erase existing material or move calorimeter geometry
merely to make a drawing fit.

Before reporting a usable isolated component, require:

- deterministic export and bound source/configuration/material hashes;
- valid DD4hep construction, proper transforms and volume/placement inventory;
- native material recipe, density, constituent volume and mass readback;
- matched old/new inventories and bend-resolution controls;
- native containment/overlap checks at10nm and joint-focused navigation probes;
- DDG4/Geant4 conversion plus a saved small serial transport/navigation smoke;
- clear distinction between standalone checks and unresolved integrated fit.

Native ROOT/XML/events/logs stay ignored. Retain compact provenance/results and
reproduction commands, update scientific tracking/software inventory and create
a separate draft implementation PR stacked on the proposal branch. No approval
or production performance claim follows from these checks.
