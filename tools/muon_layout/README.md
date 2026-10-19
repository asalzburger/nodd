# Modular muon chamber and warm-frame prototype (DES040)

Isolated DRAFT proposal on fixed PR87 commit
`fe372194038ed2af9617c27defffba09ae6d683f`. No DD4hep integration or engineering
acceptance. [Governing choices](../../docs/design/DES-040-muon-chambers-frame.md),
[results](../../docs/validation/DES-040/results.md),
[source classifications](../../docs/validation/DES-040/sources.json).

`design.json` supplies all chamber choices and points to the retained support
proposal. `layout.py` packs whole rectangular/trapezoidal prisms, splitting
compartments around obstacles within fixed size bounds. It does not cut arbitrary
holes into chamber shapes. `geometry.py` uses convex SAT and conservative
full-volume distance bounds; unresolved cells reject a module. `support.py`
retains hollow material walls, finite case contacts, ground connectivity and
joint-union self-mass separately from gross stock.

`coverage.py` counts distinct station identities for full-sphere straight IP
rays. Measurement-plane footprints and complete-depth traversal are different
geometric proxies. Warm-coil reservations and actual support-wall paths tag
material routes; they do not veto counts or predict efficiency. Every ray uses
actual panel-plane distances. Headline solid-angle fractions use an independent
seeded iid integral, since periodic image grids alias narrow module gaps.

Run from the repository root with Python >=3.12 and NumPy (the retained run used
Python 3.14.6 / NumPy 2.5.1; CI pins the controls environment to NumPy 2.5.3):

```sh
python3 -B tools/muon_layout/study.py
python3 -B -m unittest tools.muon_layout.test_geometry tools.muon_layout.test_layout tools.muon_layout.test_support
python3 -B tools/muon_layout/study.py --check
```

The study writes only DES040. It verifies the inherited magnetic result/map
SHA-256 before use. Its results retain input and artifact hashes, source versions,
grid sensitivity, independent integration errors and support mass refinement.
`chamber-outlines.obj` contains only the twelve edges per chamber envelope.
`geometry.json` retains full transforms, IDs and support graph; `coverage.npz`
contains numeric arrays readable with `allow_pickle=False`.

Render using Matplotlib >=3.8 (retained version 3.11.2):

```sh
python3 -B -m tools.muon_layout.draw --geometry docs/validation/DES-040/geometry.json --coverage docs/validation/DES-040/coverage.npz --output docs/validation/DES-040
```

XY/RZ figures use exact convex-prism plane intersections for chambers/material
walls; coil occupancy is a labelled finite-resolution display of the unchanged
exact mask. Three-dimensional views are explicitly cut away for visibility.
No plotted projection is used as a physical collision test.

No magnet dimensions/currents, field solve, MDT resolution or inherited response
model is changed here. Frame stiffness, magnetic forces, cold force closure,
case walls, chamber mounts/services/deadloads, forward technology and installed
HCAL B–H remain engineering inputs for future proposals.

The separate [ACTS propagation prototype](acts/README.md) constructs native chamber envelopes, propagates in the retained joint map, and audits large-face segment proxies versus local entrance momentum. It retains its own native controls and failure denominators; the original straight-ray artifacts above remain historical geometry evidence.

The [coloured OBJ export](../../docs/validation/DES-040/obj/README.md) contains the
current native chamber envelopes in blue and the fixed toroid warm envelopes in
grey, with a portable companion MTL and ZIP bundle. It changes no geometry or
propagation evidence.
