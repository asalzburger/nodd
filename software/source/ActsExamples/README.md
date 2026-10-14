# Local ActsExamples extensions

ACTS remains the event-processing framework. nODD algorithms, DD4hep-to-ACTS
adapters and external interfaces live in this directory. The CMake project hook
`cmake/Inject.cmake` appends local targets after upstream ACTS is configured.
No source patch, generated source, or local algorithm is written into a submodule.
ACTS remains CMake's top-level project, preserving its source revision metadata.

`Nodd` is migrated from acts-nodd HEAD555c66e71 plus its inspected uncommitted
tracker Gen3 adapter changes, including geometry reporting and navigation.
The existing local checkout is left intact. Steering lives in `../../running`.
The geometry definitions/configuration remain in the independent detectors tree.
Additional algorithms use ActsExamples::IAlgorithm and its whiteboard interfaces.

`make software` builds a separate ACTS tree with the pinned source and local
extension. It uses a build-owned Python environment created from the node's Spack
interpreter, with PYTHON override supported, and keeps its build/install products under nODD/build. `make
software-test` runs local adapter tests, tracker conversion audits and a one-event
Geant4 material recording smoke test. Make targets have explicit dependencies on
the detector build. An ACTS gitlink update can be followed by this same regression
sequence; the test does not modify the checkout to regain compatibility.
