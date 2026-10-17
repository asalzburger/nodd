# DES039 forward calorimeter prototype

The [design](../../docs/design/DES-039-common-forward-calorimeter.md) and
[decision proposal](../../docs/decisions/ADR-010-common-forward-calorimeter.md)
define the common tungsten/fibre body, LAYOUT-002 EM collar and explicit bore /
service amendments. They remain DRAFT / PROTOTYPE.

Numerical inputs are in `inputs.json`. `layout-contexts.json` retains selected
scalars from exact independent 01/02 revisions, with their full Git SHA and
original path. It does not import or claim full construction of those components.

```sh
python3 -B -m unittest discover -s tools/forward_calorimeter -p 'test_*.py' -v
python3 -B tools/forward_calorimeter/study.py --model build/forward_calorimeter/model.json
python3 -B tools/forward_calorimeter/study.py --check
```

Retained floating results use twelve significant decimal digits for portability across C/Python math libraries; calculations/native tolerances retain full precision. The snapshot comparison remains exact, and counts/IDs/source hashes are not rounded.

The detailed model is an ignored export; the retained summary is
`docs/validation/DES-039/geometry.json`. Straight-ray paths intersect actual
finite cylindrical holes, buffered fibres and silica cores. Negative placements
use Rx(pi). Nuclear interaction length is distinct from pion interaction length
and from shower containment. Phi scans and aligned seam controls are separate.
The identifier screen is a proposed bit allocation, not DD4hep decoder evidence.

Generate the two full-detector context/forward-detail figures and package drawing
with a Python environment containing matplotlib:

```sh
MPLCONFIGDIR=/tmp/nodd-fcal-matplotlib python3 -B tools/forward_calorimeter/draw.py
```

The local execution used the existing ACTS Python environment for matplotlib
only; no ACTS build or runtime modification was needed. Figures are static
scientific SVG/PNG artifacts; their named input files retain source hashes.

For actual native construction, first run the established `acts-spack` skill's
preflight and verify runtime imports in the same shell. On this node the checked
activation was:

```sh
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
unset ACTS_SPACK_SETUP
setup_spack
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/thisdd4hep.sh
source /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/bin/geant4.sh
python3 -B tools/forward_calorimeter/native.py --help
```

Run `python3 -B tools/forward_calorimeter/native.py` without `--layout` to run both layouts in separate child
processes and retain `native.json`; exact executed commands and hashes are in
that report. This validates ROOT/TGeo construction, finite material navigation
and overlaps. It is not DD4hep construction, Geant4 transport, optics, a full
combined detector or engineering acceptance. Detailed optical fan-out, curved
collector/manifold connections, full electronics packaging and external load
frames are explicitly outside the native model; their planning bounds and
remaining gates stay visible in the design.
