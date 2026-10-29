# Issue105 separated-toroid study

Isolated **PROTOTYPE**, based on the PR90 merge into PR87. This module makes
new design inputs and evidence; historical toroid fields, detailed chambers,
supports and DD4hep inputs remain separate.

```sh
python3 -B -m unittest tools.toroid_redesign.test_study -v
python3 -B -m tools.toroid_redesign.study
python3 -B -m tools.toroid_redesign.draw
rsvg-convert -o docs/validation/DES-039/issue105/schematic.png docs/validation/DES-039/issue105/schematic.svg
```

Python3.11+ and NumPy use the existing toroid tools. The field integrator uses
the local C++ backend when available. SVG rendering uses only the standard
library plus NumPy; the optional PNG uses the existing `rsvg-convert` executable.
No ACTS/DD4hep/Geant4 or Spack environment is required by this bounded study.

`design.json` contains metre/tesla/degree inputs. The ordinary gap field targets
are reduced together to meet a3.5T sampled exterior-field screen. This is no
conductor peak certification. A thinner uniform pack is required to close the
global30MJ/m³ vacuum energy/cold-volume relation at low current. The sizing root
never permits cold dimensions below the pack or above the warm reservation.
Finite source geometry changes always trigger a fresh self/mutual energy integral.

The energy refinement is an empirical numerical sensitivity, not an engineering
uncertainty. Cold dimensions have no qualified reinforcement, cooling or
per-family material decomposition. Installed nonlinear field, force interaction,
critical surface and quench remain open. In particular the exterior filament
quadrature diagnostic cannot bound the field inside a current pack.

`crossings` requires full-depth entry/exit within one schematic station, tests
the local normal extrusion and actual ray chord against warm sweeps, and counts
barrel/endcap alternatives once per station. A separate conservative interstation
path test distinguishes material traversal from missing chamber volume. Grids
use cell centres in one30° sector and exact solid-angle eta-bin weights; both
hemispheres follow the tested reflection symmetry. Eta3 and3.5 denominators
remain separate. The candidate has no finite panel tiling, borders or services:
its availability is a geometric ceiling, not detection efficiency.

[Design and source rationale](../../docs/design/inputs/DES-039-issue105-separated-toroids.md),
[results](../../docs/validation/DES-039/issue105/README.md).
